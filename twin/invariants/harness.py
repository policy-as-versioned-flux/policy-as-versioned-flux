"""The suite runner and the checks that guard the suite itself."""

from __future__ import annotations

import datetime
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import yaml

from .. import REPO_DIR
from ..artefact import Artefact
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
    # `emit_all`'s memo, keyed by output directory. Held on the context rather than in a module
    # global so it dies with the scratch directory it describes, and so two suite runs in one
    # process cannot hand each other stale artefacts.
    emitted: dict[str, dict[str, tuple[Artefact, Path]]] = field(default_factory=dict)


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


@harness_check("worksheet_matches_the_pocket_org")
def _worksheet_matches(ctx: Context) -> str:
    """The continuous coherence mechanism (build ticket 15).

    A guard on the suite rather than an invariant, because the worksheet is a **second yardstick**
    alongside the constitution: it is what catches the degenerate system a refusal test cannot
    see — a triple that is present but garbage, an elasticity nobody recalibrated three tickets
    later. Both stay green under every refusal test and both fail here.
    """
    from .. import fixtures, worksheet
    from ..repo import ModelRepo

    pocket = ctx.tmp / "pocket-org"
    if not pocket.exists():
        fixtures.build_pocket_org(pocket)
    results = worksheet.check(worksheet.bodies_for(ModelRepo.open(pocket), ctx.caps))
    differing = [
        f"line {r.line.index} ({r.line.key}): worksheet {r.line.expected}, artefact {r.actual}"
        for r in results
        if not r.pending and not r.ok
    ]
    if differing:
        raise Violated("the pocket org no longer matches its hand-computed worksheet: " + "; ".join(differing))
    late = worksheet.overdue(results)
    if late:
        raise Violated("a worksheet line is pending past its build ticket: " + "; ".join(late))
    pending = sum(1 for r in results if r.pending)
    return f"{len(results) - pending} hand-computed lines match, {pending} pending on open tickets"


@harness_check("graded_edge_fixture_holds_its_contract")
def _graded_edge_contract(ctx: Context) -> str:
    """The boundary contract the £ and skills tracks build against (build ticket 17).

    Generated rather than committed, so it cannot fossilise — and asserted here, so a track that
    depends on it finds out at this seam rather than three tickets downstream.
    """
    import json

    from .. import verbs
    from ..model import Overlay
    from ..repo import ModelRepo
    from ..schema import CAUSAL_EDGE, SchemaError, validate

    repo = ModelRepo.open(ctx.repo_dir)
    graded = []
    for org in sorted({"netflix", "intel"}):
        artefact = verbs.graph(repo, ctx.caps, org, verbs.command_for("graph", org=org))
        for edge in json.loads(artefact.to_bytes())["body"]["edges"]:
            if edge["type"] != CAUSAL_EDGE:
                if any(f in edge for f in ("sign", "lag_days", "elasticity", "evidence_grade")):
                    raise Violated(f"a {edge['type']!r} edge asserts a quantity it cannot measure")
                continue
            missing = [f for f in ("sign", "lag_days", "elasticity", "evidence_grade") if f not in edge]
            if missing:
                raise Violated(f"causal edge {edge['id']!r} asserts no {', '.join(missing)}")
            if set(edge["elasticity"]) != {"min", "mode", "max"}:
                raise Violated(f"causal edge {edge['id']!r} carries an elasticity that is not a triple")
            if "degenerate_elasticity" not in edge:
                raise Violated(f"causal edge {edge['id']!r} does not say whether its triple has width")
            graded.append(edge)

    if not graded:
        raise Violated("the fixture emits no graded causal edge, so downstream tracks have no contract")
    if not any(e["degenerate_elasticity"] for e in graded):
        raise Violated("no degenerate triple in the fixture, so the false-precision flag is never exercised")
    if not any(not e["degenerate_elasticity"] for e in graded):
        raise Violated("every triple in the fixture is degenerate, so a real range is never exercised")

    # And the refusal itself: a causal edge that drops one of its assertions does not load.
    stripped = {k: v for k, v in graded[0].items() if k not in ("elasticity", "degenerate_elasticity")}
    try:
        validate("edge", {**stripped, "from": "comp-a", "to": "comp-b"}, "planted")
    except SchemaError:
        pass
    else:
        raise Violated("a causal edge with no elasticity validated; propagation would run on hand-waving")
    if not Overlay.load(repo, "netflix").edges:
        raise Violated("the fixture overlay carries no first-class edges at all")
    return f"{len(graded)} graded causal edges, one degenerate and flagged; a stripped one is refused"


@harness_check("drift_window_was_declared_before_it_was_measured")
def _drift_window_declared_up_front(ctx: Context) -> str:
    """The Flux measurement's window was pre-registered (build ticket 64).

    A guard on the suite rather than an invariant, for the same reason the pocket-org worksheet is
    one: the constitution names sixteen invariants and may not grow a seventeenth without the
    constitution changing first, and this guards a **yardstick** — the pre-registration — rather
    than an absence in the system.

    The claim "the window was stated up front, not chosen after seeing results" is otherwise
    something a reader has to take on trust. Here it is read out of git: the window file's first
    commit must predate every sample in the probe log. Retuning the window once the data looked
    inconvenient would fail this, and rewriting the history to hide that is a different act from
    editing a file.

    The window also has to name what would falsify the spec, and `Window.load` refuses one that
    does not — a measurement that can only come back one way is a demonstration.
    """
    from .. import drift

    window = drift.Window.load()  # refuses a window with no falsifier and no named owner
    samples = drift.load_samples()

    declared = _first_commit_date(REPO_DIR, drift.WINDOW_PATH)
    if declared is None:
        if samples:
            raise Violated(
                f"{len(samples)} probe sample(s) exist and the window has never been committed, so "
                "nothing establishes that it was declared before the data arrived"
            )
        return (
            f"window {window.opens}..{window.closes} declared with {len(window.falsifiers)} "
            "falsifier(s), uncommitted and unmeasured — the state at the start of a measurement"
        )

    early = [s["ts"] for s in samples if drift._moment(s["ts"]) < declared]
    if early:
        raise Violated(
            f"{len(early)} probe sample(s) predate the window's first commit ({declared.isoformat()}), "
            f"earliest {min(early)} — the window was not declared before it was measured"
        )
    return (
        f"window {window.opens}..{window.closes} committed {declared.date().isoformat()}, "
        f"{len(window.falsifiers)} declared falsifier(s), {len(samples)} sample(s), none earlier"
    )


@harness_check("drift_window_is_actually_being_sampled")
def _drift_window_is_being_sampled(ctx: Context) -> str:
    """An open measurement window is receiving samples (build ticket 64).

    **This guard exists because its absence cost three days of a ninety-one-day window.** On
    2026-08-10 the probe was found never to have run: no `samples.jsonl`, no crontab entry, the
    cluster up and `probe.sh` executable. Ticket 64 had said "measuring" since 2026-08-07.

    `drift_window_was_declared_before_it_was_measured` was green throughout, and correctly so — it
    proves the window predates the data, and it is vacuously satisfied by no data at all. Nothing
    proved any data existed. A pre-registration guard and a liveness guard are different guards,
    and the plan had built only the first.

    `window.yaml` predicted this in its own words — *"a probe nobody owns stops running and nobody
    notices, and a stopped probe is what produces a confident 'no drift'"* — and it happened anyway,
    which is the argument for a mechanism over a warning.

    The check is deliberately weak on cadence and strict on silence. A gap wider than the declared
    cadence is a coverage hole that `reduce.py` reports as one, and coverage is ticket 65's problem.
    Total silence inside an open window is this guard's problem, because it is the failure that
    reads as a result.
    """
    from .. import drift

    window = drift.Window.load()
    samples = drift.load_samples()
    # Wall-clock, deliberately. Liveness is the one property that cannot be asserted from pinned
    # inputs: the whole question is whether anything has happened *lately*, and a pinned clock
    # would make this guard green forever at the moment it was written.
    today = datetime.datetime.now(datetime.timezone.utc)

    opens, closes = drift._day(window.opens), drift._day(window.closes)
    if today < opens:
        return f"window {window.opens}..{window.closes} has not opened; nothing owed yet"
    if not samples:
        elapsed = (min(today, closes) - opens).days
        raise Violated(
            f"the window opened {window.opens} and holds no sample after {elapsed} day(s). "
            "An unsampled window is not a measurement, and a silent instrument reads as a stable "
            f"estate — schedule the probe ({window.owner} owns it) before {window.closes}"
        )

    latest = max(drift._moment(s["ts"]) for s in samples)
    stale_for = today - latest
    horizon = datetime.timedelta(days=1)
    if today <= closes and stale_for > horizon:
        raise Violated(
            f"the window is open and the newest sample is {stale_for.days} day(s) old "
            f"({latest.isoformat()}). The probe has stopped, and a stopped probe writes no "
            "`unreachable` sample either — the silence is indistinguishable from stability"
        )
    return (
        f"{len(samples)} sample(s) in an open window, newest {latest.date().isoformat()}, "
        f"{(closes - today).days} day(s) left"
    )


def _first_commit_date(root: Path, path: Path) -> datetime.datetime | None:
    """When a file first entered git history, or `None` if it never has."""
    rel = path.relative_to(root).as_posix()
    out = _git(root, "log", "--diff-filter=A", "--format=%cI", "--", rel)
    stamps = [line for line in (out or "").splitlines() if line.strip()]
    if not stamps:
        return None
    return datetime.datetime.fromisoformat(stamps[-1].strip().replace("Z", "+00:00"))


@harness_check("scheduled_emission_ignores_signal_presence")
def _sweep_is_not_event_gated(ctx: Context) -> str:
    """A scheduled sweep emits the same volume twice running, nothing having changed (build ticket 09).

    A guard on the suite rather than an invariant, for the same reason the pocket-org worksheet and
    the drift window are: the constitution names sixteen invariants and may not grow a seventeenth
    without the constitution changing first, and this guards a **property of the scheduler**, not an
    absence in the emitted artefact shape.

    `twin/schedule.py` carries no staleness check by design — decision ticket 11 Q5's whole point is
    that a twin which only re-forecasts on change would score beautifully and mean nothing, because
    the boring "no material change expected" days are exactly what a reliability diagram needs to
    see. Two sweeps back to back over the same, unchanged repository, with no signal added between
    them, are asserted to emit the **same** forecast count — not zero the second time, which is what
    a hash-staleness skip (the very thing arckit's inherited `--refresh` machinery does, and the
    thing this ticket explicitly declines to inherit) would produce.

    The positive leg matters as much as the equality: a sweep that executed nothing both times would
    pass the equality trivially while asserting nothing about emission at all.
    """
    from .. import schedule
    from ..repo import ModelRepo

    repo = ModelRepo.open(ctx.repo_dir)
    first = schedule.sweep([repo], ctx.caps, ["twin", "sweep"])
    second = schedule.sweep([repo], ctx.caps, ["twin", "sweep"])

    first_counts, second_counts = first.body["counts"], second.body["counts"]
    if first_counts["executed"] == 0:
        raise Violated("the sweep executed no scenario at all, so 'unconditional emission' asserts nothing")
    if first_counts["failed"] or second_counts["failed"]:
        raise Violated(f"the sweep failed on a fixture scenario: {first.body['failures'] + second.body['failures']}")
    if first_counts["forecasts"] != second_counts["forecasts"]:
        raise Violated(
            f"two sweeps over the same unchanged repository emitted different forecast counts "
            f"({first_counts['forecasts']} then {second_counts['forecasts']}) — emission is gated on "
            "something other than the standing scenario set"
        )
    return (
        f"{first_counts['executed']} scenario(s) across {first_counts['repos']} repo(s) emitted "
        f"{first_counts['forecasts']} forecast(s) on both of two consecutive, unconditional sweeps"
    )


@harness_check("an_intervention_never_reaches_upstream")
def _intervention_never_reaches_upstream(ctx: Context) -> str:
    """`do()` propagates downstream only (build ticket 22).

    A guard rather than an invariant, because the constitution's sixteen invariants are the named
    *absences* and this is a semantic property of one verb — the same kind of thing the graded-edge
    fixture's contract is. It belongs in the suite regardless: a system that lets an intervention
    back-propagate concludes that taking an action changed the past, and that conclusion would
    read as an ordinary number in an ordinary artefact.

    Three legs. The emitted pair must differ upstream and agree downstream; the refusal must bite
    on a planted violation; and the fixture must actually have something upstream to update, or
    the first leg is vacuous.

    **The downstream-identity leg is a property of this implementation, not of causal inference.**
    Conditioning and intervening give the same downstream answer only because nothing here models
    a backdoor path — which is exactly the identification discipline decision ticket 08 AC 4 is
    still holding open. When that lands, `observe()` will legitimately differ downstream and this
    leg must be narrowed rather than defended. Named here so the guard cannot quietly become the
    reason the AC-4 work is not done: the constitution calls that skeleton-as-ceiling.
    """
    import json

    from ..artefact import ArtefactError
    from ..primitives import refuse_upstream_under_intervention
    from ..verbs import KIND_INTERVENTION, KIND_OBSERVATION
    from .checks import emit_all

    emitted = emit_all(ctx)
    doing = json.loads(emitted[KIND_INTERVENTION][1].read_bytes())["body"]
    learning = json.loads(emitted[KIND_OBSERVATION][1].read_bytes())["body"]

    if not learning["upstream"]:
        raise Violated(
            "the observed component has no causal ancestor in the fixture, so 'do() updates "
            "nothing upstream' is true of a component nothing could update"
        )
    if doing["upstream"]:
        named = ", ".join(str(e.get("component")) for e in doing["upstream"])
        raise Violated(f"an intervention updated belief about {named}; acting did not change the past")
    if not doing["severed"]:
        raise Violated("the intervened component has no incoming edge to sever, so nothing is asserted")
    if doing["downstream"] != learning["downstream"]:
        raise Violated(
            "doing and learning produced different downstream halves. The difference between them "
            "lives above the causal composition; a difference inside it is a second implementation"
        )
    # And the refusal itself, on a planted violation — the leg that proves the guard is a guard.
    try:
        refuse_upstream_under_intervention({**doing, "upstream": [{"component": "planted"}]})
    except ArtefactError:
        pass
    else:
        raise Violated("a planted upstream belief update survived an intervention's emission")

    # The guard has to be *wired*, not merely present. Nothing reachable through the public API
    # can violate it today — the intervention branch hardcodes an empty upstream — so deleting the
    # call would leave every test green while removing the protection that matters the moment
    # somebody changes that branch. Asserted on the emitting function's source, the same way
    # `no_collapse_mechanism` asserts the absence of a collapse affordance.
    import inspect

    from .. import verbs

    if "refuse_upstream_under_intervention" not in inspect.getsource(verbs._query):
        raise Violated(
            "the emitting function no longer calls refuse_upstream_under_intervention. The guard "
            "cannot bite through the public API today, which is exactly why its removal has to "
            "fail here rather than wait for the branch that would need it."
        )
    return (
        f"do({doing['component']}) severs {len(doing['severed'])} edge(s) and updates nothing "
        f"upstream; observe() updates {len(learning['upstream'])}; the downstream halves are identical"
    )


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
