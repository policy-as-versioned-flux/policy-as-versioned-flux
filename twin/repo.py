"""The pinned model repository.

Git-versioned text is the source of truth; any store is a derived index rebuildable from it
(decision ticket 07, Q4). Reads go through a *tree object*, never the working tree, so the pin
describes exactly what was read — and a dirty tree is refused outright so that nobody is misled
into thinking an edit they can see took effect.

Reading by tree rather than by path is what lets the world layer and each overlay be separately
versioned units with independent refs (build ticket 04) while sharing one repository.
"""

from __future__ import annotations

import datetime
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

OBJECT_ID = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")

# The years git's date parser can actually compare against. Outside this window it does not fail
# — it falls back to `now`, so `--before=1968-06-01` returns the newest commit rather than none.
# Measured, not assumed: 1968 returns HEAD against a 2026 repository, 1970 onwards does not.
GIT_EPOCH_YEARS = (1970, 2099)

# Git reads configuration and environment that can change what it returns, and in two cases what
# it *executes*. A model repository can arrive as a directory rather than a clone, so its local
# config is not trusted: `core.fsmonitor` and a hooks path are commands, and `core.quotePath`
# silently changes the bytes of a listing. Command-line `-c` beats repository-local config.
_HARDEN = (
    "--no-pager",
    "-c", "core.fsmonitor=false",
    "-c", "core.hooksPath=/dev/null",
    "-c", "core.pager=cat",
    "-c", "core.quotePath=false",
)
# Anything that could point git at a different repository, index or object store.
_SCRUB = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CEILING_DIRECTORIES", "GIT_NAMESPACE",
)


class RepoError(RuntimeError):
    pass


class DirtyTreeError(RepoError):
    pass


class SafeLoader(yaml.SafeLoader):
    """`safe_load` plus a refusal of aliases.

    PyYAML shares an alias's object rather than copying it, so nesting anchors makes a few
    hundred bytes of model file expand to gigabytes when the document is serialised into an
    artefact. Nothing in a model repository needs an alias, so the cheapest fix is to not have
    them.
    """

    def compose_node(self, parent: Any, index: Any) -> Any:
        if self.check_event(yaml.events.AliasEvent):
            event = self.peek_event()
            raise yaml.constructor.ConstructorError(
                None, None, f"YAML aliases are not accepted here (*{event.anchor})", event.start_mark
            )
        return super().compose_node(parent, index)


def load_yaml(text: str) -> Any:
    return _normalise(yaml.load(text, Loader=SafeLoader))


def _normalise(node: Any) -> Any:
    """Dates and times become ISO strings.

    PyYAML auto-types an unquoted `2011-07-12` into a `date`, which is not JSON-serialisable —
    so whether a model file quotes its dates would otherwise decide between an artefact and a
    traceback. Normalising here makes the quoting irrelevant and the output identical either way.
    """
    if isinstance(node, dict):
        return {k: _normalise(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_normalise(v) for v in node]
    if isinstance(node, (datetime.datetime, datetime.date)):
        return node.isoformat()
    return node


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in _SCRUB}
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "LC_ALL": "C",
            "TZ": "UTC",
        }
    )
    return env


def _git_bytes(cwd: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", *_HARDEN, *args],
        cwd=str(cwd),
        env=_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", "replace").strip()
        raise RepoError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout


def _git_text(cwd: Path, *args: str) -> str:
    return _git_bytes(cwd, *args).decode("utf-8")


def _resolve(worktree: Path, spec: str) -> str:
    """Resolve an object spec, refusing anything git would read as an option.

    `git rev-parse` echoes an unrecognised dash-leading argument and exits 0, so without
    `--verify --end-of-options` a ref of `--output=...` becomes the pin *and* reaches the next
    git command as an option.
    """
    resolved = _git_text(worktree, "rev-parse", "--verify", "--end-of-options", spec).strip()
    if not OBJECT_ID.match(resolved):
        raise RepoError(f"{spec!r} did not resolve to an object id (got {resolved!r})")
    return resolved


def _join(root: str, rel: str) -> str:
    return f"{root}/{rel}" if root else rel


@dataclass(frozen=True)
class UnitRef:
    """A separately versioned unit inside the repository.

    `commit` is the last commit that touched this subtree, so the world layer and each overlay
    advance independently even when they share a repository. `tree` is the content pin —
    identical content gives an identical tree whatever the history.
    """

    path: str
    commit: str
    tree: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "commit": self.commit, "tree": self.tree}


@dataclass(frozen=True)
class Pin:
    """What was read, precisely enough to read it again."""

    root: str
    commit: str
    tree: str
    committed: str  # commit date of `commit`; from the pin, never from the wall clock

    def as_dict(self) -> dict[str, str]:
        return {"root": self.root, "commit": self.commit, "tree": self.tree, "committed": self.committed}


class ModelRepo:
    """A model repository opened at a ref. Every read is at that ref, or at a ref pinned by it."""

    def __init__(self, worktree: Path, pin: Pin) -> None:
        self.worktree = worktree
        self.pin = pin
        self.direction_checked = False  # set once the world/overlay direction rule has been enforced

    # -- opening -------------------------------------------------------------------------

    @classmethod
    def open(cls, path: str | Path, ref: str = "HEAD") -> "ModelRepo":
        model_root = Path(path).resolve()
        if not model_root.is_dir():
            raise RepoError(f"no model repository at {model_root}")
        worktree = Path(_git_text(model_root, "rev-parse", "--show-toplevel").strip()).resolve()
        root = model_root.relative_to(worktree).as_posix()
        root = "" if root == "." else root

        cls._refuse_dirty(worktree, model_root, root)

        commit = _resolve(worktree, f"{ref}^{{commit}}")
        try:
            tree = cls._tree_of(worktree, commit, root)
        except RepoError as exc:
            raise RepoError(f"model root {root or '.'!r} does not exist at ref {ref!r}") from exc
        committed = _git_text(worktree, "show", "-s", "--format=%cI", commit).strip()
        repo = cls(worktree, Pin(root=root, commit=commit, tree=tree, committed=committed))
        repo._refuse_gitlinks()
        return repo

    @staticmethod
    def parse_moment(at: str) -> datetime.datetime:
        """An ISO 8601 instant git can actually compare against, or a refusal.

        Separate from `open_at_time` because two callers need it: the opener, and any verb that
        was *handed* an already-open repository and has to check the time it was told. A guard
        that only one caller runs is a guard the other callers do not have.
        """
        stamp = str(at).strip()
        if not stamp:
            raise RepoError("a rewind needs a time; a rewind to no particular moment is not a rewind")
        try:
            moment = datetime.datetime.fromisoformat(stamp)
        except ValueError:
            raise RepoError(
                f"{stamp!r} is not an ISO 8601 time. git reads a date it cannot parse as `now` and "
                "returns the newest commit, so an unparseable time would answer a question about "
                "the past with today's model. Use `2026-06-01` or `2026-06-01T12:00:00+00:00`."
            ) from None
        if not GIT_EPOCH_YEARS[0] <= moment.year <= GIT_EPOCH_YEARS[1]:
            # The same silent fallback as an unparseable date, and less obvious: `fromisoformat`
            # happily accepts a year git cannot represent, git reads it as `now`, and the answer
            # comes back as the newest commit. Bounded here because a date this reader accepts
            # must be one git can actually compare against.
            raise RepoError(
                f"{stamp!r} is outside the years git can represent "
                f"({GIT_EPOCH_YEARS[0]}-{GIT_EPOCH_YEARS[1]}). Outside that window git falls back "
                "to `now` and returns the newest commit, so the answer would be today's model "
                "wearing a date from another century."
            )
        # A time with no offset is UTC, explicitly. This is the **second** of two mechanisms —
        # `_env()` already pins `TZ=UTC` for every git call, so deleting this line changes no
        # behaviour today, and a mutation test will report it as redundant. It stays because the
        # two guard different things: `TZ` guards what git does with the string, this guards what
        # *this* function means by it, and a future caller that formats the moment itself would
        # otherwise inherit the machine's clock.
        return moment if moment.tzinfo else moment.replace(tzinfo=datetime.timezone.utc)

    @classmethod
    def open_at_time(cls, path: str | Path, at: str) -> "ModelRepo":
        """The repository as it stood at `at` — the last commit at or before that moment.

        The git access for the rewind primitive (build ticket 35) lives here rather than in
        `twin/primitives.py`, so every command this system runs goes through the same hardened
        environment. What it *means* is documented there.

        Refuses a time before the first commit rather than opening an empty tree, and refuses a
        time it cannot parse rather than passing it to git. **That second refusal is not
        defensive tidying.** `git rev-list --before=not-a-date` exits 0 and returns HEAD, so a
        typo would silently hand back today's model as though it were the past — a confident
        wrong answer to a question about history, which is the failure this whole system is built
        to refuse.

        A time with no offset is read as UTC, explicitly, rather than left to git and the
        machine's clock. `--before` is inclusive, so one instant resolves to one commit
        everywhere.
        """
        root = Path(path).resolve()
        if not root.is_dir():
            raise RepoError(f"no model repository at {root}")
        stamp = str(at).strip()
        moment = cls.parse_moment(at)
        worktree = Path(_git_text(root, "rev-parse", "--show-toplevel").strip()).resolve()
        found = _git_text(worktree, "rev-list", "-1", f"--before={moment.isoformat()}", "HEAD").strip()
        if not found:
            roots = _git_text(worktree, "rev-list", "--max-parents=0", "HEAD").strip().splitlines()
            born = (
                _git_text(worktree, "show", "-s", "--format=%cI", roots[-1]).strip()
                if roots
                else "never — this repository has no commits"
            )
            raise RepoError(
                f"cannot read {root} at {stamp!r}: it did not exist yet, and its first commit is "
                f"dated {born}. An empty model is a claim that there was nothing in the "
                "organisation, which is a different answer from 'there was no model'."
            )
        return cls.open(root, ref=found)

    def _refuse_gitlinks(self) -> None:
        """A submodule under the model root would load as empty, silently. Refuse instead."""
        listing = _git_bytes(self.worktree, "ls-tree", "-r", "-z", self.pin.tree).decode("utf-8")
        links = [e.split("\t", 1)[-1] for e in listing.split("\0") if e.startswith("160000 ")]
        if links:
            raise RepoError(
                "the model root contains submodules, which this reader does not descend into: "
                + ", ".join(sorted(links))
            )

    @staticmethod
    def _refuse_dirty(worktree: Path, model_root: Path, root: str) -> None:
        args = ["status", "--porcelain", "--untracked-files=all"]
        if root:
            args += ["--", root]
        dirty = [line for line in _git_text(worktree, *args).splitlines() if line.strip()]
        if dirty:
            listed = "\n  ".join(dirty[:10])
            more = f"\n  ... and {len(dirty) - 10} more" if len(dirty) > 10 else ""
            raise DirtyTreeError(
                f"model repository at {model_root} has uncommitted changes; commit them first "
                f"so the pin describes what you are reading:\n  {listed}{more}"
            )

    @staticmethod
    def _tree_of(worktree: Path, commit: str, path: str) -> str:
        return _resolve(worktree, f"{commit}:{path}" if path else f"{commit}^{{tree}}")

    # -- reading by tree -----------------------------------------------------------------

    def read_blob(self, tree: str, rel: str) -> bytes:
        return _git_bytes(self.worktree, "cat-file", "blob", f"{tree}:{rel}")

    def read_yaml_at(self, tree: str, rel: str) -> dict[str, Any]:
        try:
            loaded = load_yaml(self.read_blob(tree, rel).decode("utf-8"))
        except yaml.YAMLError as exc:
            raise RepoError(f"{rel}: {exc}") from None
        if not isinstance(loaded, dict):
            raise RepoError(f"{rel}: expected a mapping, got {type(loaded).__name__}")
        return loaded

    def commits_touching(self, subpath: str) -> list[str]:
        """Every commit under the pin that touched this path, oldest first.

        How the history of an authored value is read back — the evidence-grade immutability check
        compares what a file said at each of these against the regrade record (build ticket 18).
        Renames are not followed, which is stated in `twin/evidence.py` rather than implied.
        """
        full = _join(self.pin.root, subpath)
        out = _git_text(self.worktree, "rev-list", "--reverse", self.pin.commit, "--", full)
        return [line.strip() for line in out.splitlines() if line.strip()]

    def list_tree(self, tree: str, prefix: str = "") -> list[str]:
        # `-z` because without it git C-quotes any path with a non-ASCII byte, and a quoted name
        # would silently fail the `.yaml` suffix test — the same pins loading a different model.
        out = _git_bytes(self.worktree, "ls-tree", "-r", "-z", "--name-only", tree)
        paths = sorted(p.decode("utf-8") for p in out.split(b"\0") if p)
        if prefix:
            head = prefix.rstrip("/") + "/"
            paths = [p for p in paths if p.startswith(head)]
        return paths

    def exists_at(self, tree: str, rel: str) -> bool:
        try:
            _git_bytes(self.worktree, "cat-file", "-e", f"{tree}:{rel}")
        except RepoError:
            return False
        return True

    # -- reading at the repository pin ---------------------------------------------------

    def read(self, rel: str) -> bytes:
        return self.read_blob(self.pin.tree, rel)

    def read_yaml(self, rel: str) -> dict[str, Any]:
        return self.read_yaml_at(self.pin.tree, rel)

    def list(self, prefix: str = "") -> list[str]:
        return self.list_tree(self.pin.tree, prefix)

    def exists(self, rel: str) -> bool:
        return self.exists_at(self.pin.tree, rel)

    # -- versioned units -----------------------------------------------------------------

    def unit_ref(self, subpath: str) -> UnitRef:
        """The independent ref of a versioned unit — `world`, `orgs/netflix`, and so on."""
        full = _join(self.pin.root, subpath)
        commit = _git_text(self.worktree, "rev-list", "-1", self.pin.commit, "--", full).strip()
        if not commit:
            raise RepoError(f"no commit touches {full} at {self.pin.commit[:12]}")
        return UnitRef(path=subpath, commit=commit, tree=self._tree_of(self.worktree, commit, full))

    def unit_ref_at(self, subpath: str, commit: str) -> UnitRef:
        """The same unit as pinned by some other commit — how an overlay resolves a moving world.

        The pin must be an object id. A branch or tag resolves to whatever it points at *now*,
        which would make identical model-repo pins produce different bytes on different days —
        the exact property the whole system rests on.
        """
        if not OBJECT_ID.match(commit.strip()):
            raise RepoError(
                f"{commit!r} is not an object id; a pinned ref must be a full commit sha, "
                "because a branch or tag moves and a pin that moves is not a pin"
            )
        full = _join(self.pin.root, subpath)
        resolved = _resolve(self.worktree, f"{commit.strip()}^{{commit}}")
        return UnitRef(path=subpath, commit=resolved, tree=self._tree_of(self.worktree, resolved, full))
