"""The suite runner and the checks that guard the suite itself."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import yaml

from .. import REPO_DIR
from ..grades import Capabilities
from . import (
    FAIL,
    MANIFEST_PATH,
    PASS,
    SKIP,
    SKIPPABLE,
    Result,
    Skip,
    Violated,
    body_hash,
    harness_check,
    harness_registry,
    registry,
)

BUILD_TICKETS_DIR = REPO_DIR / ".scratch" / "twin" / "build"
CONSTITUTION = BUILD_TICKETS_DIR / "00-constitution.md"
CLOSED_STATUSES = {"done", "closed", "resolved", "complete", "completed"}

LIVE, PENDING = "live", "pending"


@dataclass(frozen=True)
class Entry:
    name: str
    activating_ticket: str
    state: str
    asserts: str
    body_sha256: str | None = None
    authorised_by: str | None = None
    note: str | None = None
    # Field names this invariant refuses to let into an artefact. Declared here rather than read
    # back out of the code, so deleting one from `artefact.FORBIDDEN_KEYS` fails the check
    # instead of quietly shrinking what it asserts.
    refuses_keys: tuple[str, ...] = ()


def manifest_doc(path: Path | None = None) -> dict[str, object]:
    loaded = yaml.safe_load((path or MANIFEST_PATH).read_text(encoding="utf-8"))
    return dict(loaded)


def load_manifest(path: Path | None = None) -> list[Entry]:
    raw = yaml.safe_load((path or MANIFEST_PATH).read_text(encoding="utf-8"))
    return [
        Entry(
            name=str(e["name"]),
            activating_ticket=str(e["activating_ticket"]),
            state=str(e["state"]),
            asserts=str(e.get("asserts", "")),
            body_sha256=e.get("body_sha256"),
            authorised_by=e.get("authorised_by"),
            note=e.get("note"),
            refuses_keys=tuple(e.get("refuses_keys", []) or []),
        )
        for e in raw["invariants"]
    ]


def constitution_invariants() -> list[str]:
    """The invariant names as the constitution lists them — the yardstick for the manifest."""
    if not CONSTITUTION.is_file():
        # Not a skip: without the yardstick this guard is not "unable to run", it is absent.
        raise Violated(f"the constitution is missing from {CONSTITUTION} — the yardstick is gone")
    text = CONSTITUTION.read_text(encoding="utf-8")
    section = text.split("## The invariants", 1)[-1].split("\n##", 1)[0]
    # Snake_case identifiers only: an underscore is required, so backticked prose does not count.
    return sorted(set(re.findall(r"`([a-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+)`", section)))


def build_ticket_status(number: str) -> str | None:
    matches = sorted(BUILD_TICKETS_DIR.glob(f"{number}-*.md"))
    if not matches:
        return None
    found = re.search(r"^\*\*Status:\*\*\s*(.+)$", matches[0].read_text(encoding="utf-8"), re.M)
    return found.group(1).strip().lower() if found else None


def ticket_is_closed(status: str | None) -> bool:
    """Statuses carry a date — `done (2026-08-05)` — so compare the leading word, not the line."""
    return bool(status) and status.split()[0].strip(":;,.") in CLOSED_STATUSES  # type: ignore[union-attr]


@dataclass
class Context:
    tmp: Path
    repo_dir: Path
    caps: Capabilities
    ci_matrix: bool


# -- checks on the suite itself ------------------------------------------------------------


@harness_check("manifest_names_every_invariant")
def _manifest_complete(ctx: Context) -> str:
    """Every invariant the constitution names has a manifest entry, and vice versa."""
    listed = set(constitution_invariants())
    manifest = {e.name for e in load_manifest()}
    missing = sorted(listed - manifest)
    extra = sorted(manifest - listed)
    if missing:
        raise Violated(f"constitution names invariants absent from the manifest: {', '.join(missing)}")
    if extra:
        raise Violated(f"manifest names invariants the constitution does not: {', '.join(extra)}")
    return f"{len(listed)} invariants, manifest and constitution agree"


@harness_check("live_invariants_have_checks")
def _live_have_checks(ctx: Context) -> str:
    entries = load_manifest()
    registered = set(registry())
    live = {e.name for e in entries if e.state == LIVE}
    pending = {e.name for e in entries if e.state == PENDING}
    if live - registered:
        raise Violated(f"live but unimplemented: {', '.join(sorted(live - registered))}")
    if registered - live:
        raise Violated(
            "implemented but not marked live in the manifest: "
            f"{', '.join(sorted(registered - live))} — an unlisted check is an unguarded one"
        )
    if pending & registered:
        raise Violated(f"marked pending but implemented: {', '.join(sorted(pending & registered))}")
    return f"{len(live)} live, {len(pending)} pending"


@harness_check("no_invariant_pending_past_its_ticket")
def _pending_past_ticket(ctx: Context) -> str:
    """An invariant still pending after its activating ticket closed is a silent weakening."""
    if not BUILD_TICKETS_DIR.is_dir():
        raise Violated(f"build tickets missing from {BUILD_TICKETS_DIR} — this guard cannot see anything")
    overdue = []
    unknown = []
    for entry in load_manifest():
        if entry.state != PENDING:
            continue
        status = build_ticket_status(entry.activating_ticket)
        if status is None:
            unknown.append(f"{entry.name} (ticket {entry.activating_ticket})")
        elif ticket_is_closed(status):
            overdue.append(f"{entry.name} (ticket {entry.activating_ticket} is {status!r})")
    if overdue:
        raise Violated("pending past a closed ticket: " + "; ".join(overdue))
    if unknown:
        raise Violated("activating ticket not found for: " + "; ".join(unknown))
    return "every pending invariant names an open activating ticket"


@harness_check("invariant_bodies_match_manifest_hashes")
def _bodies_match(ctx: Context) -> str:
    from .checks import module_hash

    checks = registry()
    drifted = []
    for entry in load_manifest():
        if entry.state != LIVE:
            continue
        actual = body_hash(checks[entry.name])
        if entry.body_sha256 != actual:
            drifted.append(f"{entry.name} (manifest {str(entry.body_sha256)[:12]}, actual {actual[:12]})")
    pinned_module = manifest_doc().get("checks_module_sha256")
    if pinned_module != module_hash():
        drifted.append(
            f"the checks module itself (manifest {str(pinned_module)[:12]}, actual {module_hash()[:12]})"
        )
    if drifted:
        raise Violated(
            "invariant test bodies changed without the manifest being re-blessed: "
            + "; ".join(drifted)
            + ". Re-bless with `twin verify --rehash --authorise \"decision ticket NN — reason\"`."
        )
    return f"{len(checks)} live test bodies match their pinned hashes"


@harness_check("hash_changes_are_authorised", may_skip=True)
def _hash_changes_authorised(ctx: Context) -> str:
    """A body hash that moved must carry an authorising citation.

    The baseline is the working tree's own last change to the manifest, not `HEAD`: in CI the
    checkout *is* HEAD, so comparing against it can only ever see uncommitted edits and the guard
    would be green for every commit that weakens a refusal and re-pins its hash in the same diff.
    """
    current = load_manifest()
    doc = manifest_doc()
    head = _manifest_at(REPO_DIR, "HEAD")

    if head is not None and _hashes(head[0], head[1]) != _hashes(current, doc):
        baseline, source = head, "the committed manifest (uncommitted change)"
    else:
        history = _manifest_history(REPO_DIR)
        if len(history) < 2:
            raise Skip("the manifest has only one committed version; no earlier one to compare against")
        earlier = _manifest_at(REPO_DIR, history[1])
        if earlier is None:
            raise Skip(f"could not read the manifest at {history[1][:12]}")
        baseline, source = earlier, f"the previous version ({history[1][:12]})"

    before = {e.name: e for e in baseline[0]}
    changed = [
        entry.name
        for entry in current
        if (was := before.get(entry.name)) is not None
        # A hash appearing for the first time is an invariant being *activated*, which the
        # constitution asks for. Only a hash that moves from one value to another is a change.
        and was.body_sha256 is not None
        and (was.body_sha256, was.refuses_keys) != (entry.body_sha256, entry.refuses_keys)
        and not _cites_decision_ticket(entry.authorised_by)
    ]
    module_before = baseline[1].get("checks_module_sha256")
    if module_before != doc.get("checks_module_sha256") and not _cites_decision_ticket(
        str(doc.get("checks_module_authorised_by") or "")
    ):
        changed.append("checks_module_sha256")

    if changed:
        raise Violated(
            "hash changed with no authorising decision ticket cited in `authorised_by`: "
            + ", ".join(sorted(changed))
        )
    return f"no unauthorised hash changes against {source}"


def _hashes(entries: list[Entry], doc: dict[str, object]) -> dict[str, object]:
    """What must not move without a citation: the pinned bodies and the declared refusals."""
    out: dict[str, object] = {e.name: (e.body_sha256, e.refuses_keys) for e in entries}
    out["checks_module_sha256"] = doc.get("checks_module_sha256")
    return out


@harness_check("cross_architecture_determinism", may_skip=True)
def _cross_arch(ctx: Context) -> str:
    """The identical-bytes claim across architectures. Proven by CI, never locally."""
    if not ctx.ci_matrix:
        raise Skip(
            "requires the CI matrix (set TWIN_CI_ARCH_MATRIX=1); "
            "the same-machine leg is asserted by identical_pins_identical_bytes"
        )
    from .checks import golden_digests, recompute_digests

    golden = golden_digests()
    if not golden:
        raise Violated("no committed golden digests to compare this architecture against")
    actual = recompute_digests(ctx)
    differing = sorted(k for k in golden if golden[k] != actual.get(k))
    if differing:
        raise Violated(
            f"artefact bytes differ on {os.uname().machine} for: {', '.join(differing)} — "
            "seeded identity does not survive this platform's maths"
        )
    return f"{len(golden)} artefacts byte-identical on {os.uname().machine}"


def _git(root: Path, *args: str) -> str | None:
    proc = subprocess.run(
        ["git", *args], cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    return None if proc.returncode != 0 else proc.stdout.decode("utf-8")


def _manifest_history(root: Path) -> list[str]:
    """Commits that changed the manifest, newest first."""
    rel = MANIFEST_PATH.relative_to(root).as_posix()
    out = _git(root, "log", "--format=%H", "--", rel)
    return [line for line in (out or "").splitlines() if line]


def _manifest_at(root: Path, ref: str) -> tuple[list[Entry], dict[str, object]] | None:
    rel = MANIFEST_PATH.relative_to(root).as_posix()
    out = _git(root, "show", f"{ref}:{rel}")
    if out is None:
        return None
    raw = yaml.safe_load(out)
    entries = [
        Entry(
            name=str(e["name"]),
            activating_ticket=str(e["activating_ticket"]),
            state=str(e["state"]),
            asserts=str(e.get("asserts", "")),
            body_sha256=e.get("body_sha256"),
            authorised_by=e.get("authorised_by"),
            refuses_keys=tuple(e.get("refuses_keys", []) or []),
        )
        for e in raw["invariants"]
    ]
    return entries, dict(raw)


def _cites_decision_ticket(text: str | None) -> bool:
    return bool(text and re.search(r"decision ticket\s+\d{1,2}", text, re.I))


# -- the runner ----------------------------------------------------------------------------


class Suite:
    def __init__(self, manifest: list[Entry] | None = None) -> None:
        self.manifest = manifest or load_manifest()

    def plan(self) -> list[tuple[str, bool]]:
        """Ordered (name, is_invariant) pairs. Harness checks first: they guard the rest."""
        plan: list[tuple[str, bool]] = [(n, False) for n in harness_registry()]
        plan += [(e.name, True) for e in self.manifest]
        return plan

    def run(self, ctx: Context, only: list[str] | None = None) -> list[Result]:
        results = []
        for number, (name, is_invariant) in enumerate(self.plan(), start=1):
            if only and name not in only and str(number) not in only:
                continue
            results.append(self._one(ctx, number, name, is_invariant))
        return results

    def _one(self, ctx: Context, number: int, name: str, is_invariant: bool) -> Result:
        entry = next((e for e in self.manifest if e.name == name), None)
        if is_invariant and entry is not None and entry.state == PENDING:
            return Result(
                number,
                name,
                SKIP,
                f"pending — activates at build ticket {entry.activating_ticket}",
                True,
            )
        fn = registry().get(name) if is_invariant else harness_registry().get(name)
        if fn is None:
            return Result(number, name, FAIL, "no check registered", is_invariant)
        try:
            detail = fn(ctx)
        except Skip as exc:
            return Result(number, name, SKIP, str(exc), is_invariant)
        except Violated as exc:
            return Result(number, name, FAIL, str(exc), is_invariant)
        except Exception as exc:  # a check that errors is a check that did not assert
            return Result(number, name, FAIL, f"{type(exc).__name__}: {exc}", is_invariant)
        return Result(number, name, PASS, detail, is_invariant)


def context(tmp: Path) -> Context:
    from .. import fixtures

    repo_dir = tmp / "fixture-model-repo"
    if not repo_dir.exists():
        fixtures.build(repo_dir)
    return Context(
        tmp=tmp,
        repo_dir=repo_dir,
        caps=Capabilities.load(),
        ci_matrix=os.environ.get("TWIN_CI_ARCH_MATRIX") == "1",
    )


def may_skip(name: str, is_invariant: bool, live: set[str]) -> bool:
    """Who is allowed to decline to assert: pending invariants, and declared-skippable guards."""
    return name in SKIPPABLE if not is_invariant else name not in live


def run(only: list[str] | None = None, tmp: Path | None = None) -> tuple[list[Result], bool]:
    """Run the suite. Returns (results, ok).

    A *live* invariant that skips counts as a failure, and so does a harness guard that skips
    without declaring `may_skip`. "Pending" is the only honest way to not assert something, and it
    has to be declared in the manifest where it can be seen.
    """
    with _scratch(tmp) as scratch:
        suite = Suite()
        results = suite.run(context(scratch), only)
    live = {e.name for e in Suite().manifest if e.state == LIVE}
    ok = all(
        r.status == PASS or (r.status == SKIP and may_skip(r.name, r.invariant, live))
        for r in results
    )
    return results, ok


@contextmanager
def _scratch(tmp: Path | None) -> Iterator[Path]:
    if tmp is not None:
        tmp.mkdir(parents=True, exist_ok=True)
        yield tmp
    else:
        with tempfile.TemporaryDirectory(prefix="twin-verify-") as handle:
            yield Path(handle)
