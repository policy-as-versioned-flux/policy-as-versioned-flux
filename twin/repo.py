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
