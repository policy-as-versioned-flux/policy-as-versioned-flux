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
from typing import Any, Callable, Iterator

import yaml

from .. import REPO_DIR, fixtures
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


@harness_check("position_deltas_have_no_privileged_default")
def _position_deltas_have_no_privileged_default(ctx: Context) -> str:
    """No world model — including the org's own believed map — is required (build ticket 16).

    A guard on the suite rather than an invariant, for the same reason the pocket-org worksheet
    and the drift window are: the constitution's sixteen are named *absences*, and this asserts a
    **semantic property of a module's contract** instead — the same kind of thing
    `an_intervention_never_reaches_upstream` guards.

    Three legs. Dropping any one of the netflix fixture's three world models — including
    `netflix-believed`, the org's own map, and `twin-default`, the twin's own default reference —
    still computes, and the survivors' own scores against revealed truth do not move. And the
    artefact body carries no field named `actual`: the only way a privileged position could creep
    back in is a schema slot for one, and there is none to plant.
    """
    from ..model import Overlay
    from ..positions import deltas
    from ..repo import ModelRepo

    proposition = "dvd-rental-revenue-falls-faster-than-streaming-adds"
    all_models = ["twin-default", "rival-fast-commoditisation", "netflix-believed"]
    overlay = Overlay.load(ModelRepo.open(ctx.repo_dir), "netflix")

    full = deltas(overlay, proposition, all_models)
    if "actual" in full:
        raise Violated("the artefact carries a field named 'actual' — a privileged position exists")
    full_scores = {row["id"]: row["brier"] for row in full["against_revealed"]}

    for dropped in all_models:
        remaining = [m for m in all_models if m != dropped]
        body = deltas(overlay, proposition, remaining)
        if {p["id"] for p in body["positions"]} != set(remaining):
            raise Violated(f"dropping {dropped!r} changed which positions the remainder computed")
        for row in body["against_revealed"]:
            if row["brier"] != full_scores[row["id"]]:
                raise Violated(
                    f"dropping {dropped!r} moved {row['id']!r}'s own score against revealed truth "
                    "— a position's arithmetic depended on who else was in the room"
                )
    return f"{len(all_models)} positions, each dispensable, none privileged; scores stay put when any one is dropped"


@harness_check("credibility_blend_falls_back_to_the_world_prior_alone")
def _credibility_blend_has_no_hidden_default(ctx: Context) -> str:
    """A subject with no own-data prices from the world-layer prior alone, and says so
    (build ticket 31, AC 2) — and a subject that *has* own-data actually moves off it.

    Two legs, both on the pocket-org fixture: `payment-fraud-loss` carries a world prior and no
    `own_data` file, so its blend must equal the prior exactly with `n=0` declared. Rebuilds the
    fixture once per suite run, memoised the same way the pocket-org worksheet guard is.
    """
    from .. import fixtures, verbs
    from ..grades import Capabilities
    from ..model import Overlay
    from ..repo import ModelRepo

    pocket = ctx.tmp / "pocket-org"
    if not pocket.exists():
        fixtures.build_pocket_org(pocket)
    repo = ModelRepo.open(pocket)
    overlay = Overlay.load(repo, "pocket")

    unpriced = verbs.credibility(
        repo, ctx.caps, "pocket", "payment-fraud-loss",
        verbs.command_for("credibility", org="pocket", subject="payment-fraud-loss"),
    ).body
    if unpriced["own_data"]["n"] != 0:
        raise Violated("payment-fraud-loss carries an own_data file in the fixture; this guard needs none")
    prior = overlay.prior("payment-fraud-loss")["industry"]
    if unpriced["blended"] != {"min": float(prior["min"]), "mode": float(prior["mode"]), "max": float(prior["max"])}:
        raise Violated("a subject with no own-data did not blend to exactly its world-layer prior")

    priced = verbs.credibility(
        repo, ctx.caps, "pocket", "identity-store-incident-cost",
        verbs.command_for("credibility", org="pocket", subject="identity-store-incident-cost"),
    ).body
    if priced["own_data"]["n"] == 0:
        raise Violated("identity-store-incident-cost carries no own_data in the fixture; this guard needs some")
    if priced["blended"] == priced["world_prior"]:
        raise Violated("own-data present and the blend did not move off the world-layer prior at all")
    return (
        f"payment-fraud-loss (n=0) blends to exactly its prior; identity-store-incident-cost "
        f"(n={priced['own_data']['n']}) moves off it — z={priced['credibility']['z']}"
    )


@harness_check("a_var_shaped_summary_hides_what_tvar_surfaces")
def _var_shaped_summary_hides_the_tail(ctx: Context) -> str:
    """TVaR over VaR, asserted as a permanent property rather than left as a one-off test
    (build ticket 24, decision ticket 09's TVaR-over-VaR commitment).

    A guard on the suite rather than a seventeenth invariant, for the same reason
    `position_deltas_have_no_privileged_default` and `credibility_blend_falls_back_to_the_world_prior_alone`
    are: the constitution names sixteen invariants and may not grow a seventeenth without the
    constitution changing first, and this asserts a **semantic property of a module's contract**.

    Two legs. First, the demonstration the ticket asks for: two severities sharing a lognormal
    body, threshold and GPD scale, differing only in tail shape, carry an *identical* VaR at the
    threshold's own exceedance probability — a report carrying VaR alone could not tell a light
    tail from a heavy one apart at that point — while TVaR, the average of what actually lies
    beyond it, differs sharply. Second, the shape-parameter boundary: past `xi == 1` a GPD's mean
    does not exist, and TVaR must refuse there rather than silently dividing by a `(1 - xi)` that
    has gone to zero or negative.
    """
    import math

    from ..severity import Severity, SeverityError

    body = {"mu": 10.0, "sigma": 1.5, "threshold": 100_000.0, "beta": 80_000.0}
    light = Severity(**body, xi=0.1)
    heavy = Severity(**body, xi=0.7)
    if light.tail_probability != heavy.tail_probability:
        raise Violated(
            "two severities sharing a body and threshold disagree on tail_probability — it is "
            "meant to be derived from the body alone, not from the tail that follows it"
        )
    alpha = 1.0 - light.tail_probability
    light_var, heavy_var = light.var(alpha), heavy.var(alpha)
    if abs(light_var - heavy_var) > 1e-6 * max(light_var, heavy_var):
        raise Violated(
            f"VaR differs between a light tail ({light_var}) and a heavy one ({heavy_var}) at the "
            "threshold's own exceedance probability, where the two distributions are identical "
            "below the splice — this leg has lost its subject"
        )
    light_tvar, heavy_tvar = light.tvar(alpha), heavy.tvar(alpha)
    if heavy_tvar <= light_var:
        raise Violated("the heavy tail's TVaR did not even clear the shared VaR; the tail carries no mass")
    if heavy_tvar < light_tvar * 1.5:
        raise Violated(
            f"a heavy tail's TVaR ({heavy_tvar}) is not materially larger than a light tail's "
            f"({light_tvar}) despite identical VaR — TVaR is not surfacing what VaR hides"
        )

    for xi in (1.0, 1.5, 4.0):
        boundary = Severity(**body, xi=xi)
        boundary_alpha = 1.0 - boundary.tail_probability + 0.01
        try:
            boundary.tvar(boundary_alpha)
        except SeverityError as exc:
            if "does not exist" not in str(exc):
                raise Violated(f"xi={xi} was refused, but not for the shape boundary: {exc}") from None
        else:
            raise Violated(f"xi={xi} computed a TVaR; a GPD shape at or past 1 has no mean to average")

    # And the positive leg of that boundary: refusing is not a wall that bites below it too.
    if not math.isfinite(Severity(**body, xi=0.99).tvar(1.0 - Severity(**body, xi=0.99).tail_probability + 0.01)):
        raise Violated("a shape just below the boundary failed to produce a finite TVaR")

    return (
        f"identical VaR ({light_var:.2f}) at alpha={alpha:.4f} for xi=0.1 and xi=0.7; TVaR "
        f"diverges ({light_tvar:.2f} vs {heavy_tvar:.2f}); xi>=1 refuses at the shape boundary "
        "and xi=0.99 still computes"
    )


@harness_check("a_constraint_removal_with_no_computed_attractiveness_is_rejected")
def _a_constraint_removal_with_no_computed_attractiveness_is_rejected(ctx: Context) -> str:
    """Removing a constraint requires logging the excluded option's computed attractiveness —
    computed, not stated (build ticket 62, decision ticket 15's carried-forward item).

    A guard on the suite rather than an invariant, the same shape `causal_accounts_have_no_privileged_default`
    is: this asserts a **semantic property of a module's contract**, not one of the constitution's
    sixteen fixed names.

    Three legs, on the netflix fixture's `the-operator` perspective and `stake-the-quarter-on-one-title`
    (which crosses `insolvency`, a constraint that perspective declares itself). First,
    `compute_attractiveness` returns a real, nonzero figure re-derived from `options.prefilter()`
    — not a stand-in. Second, `log_removal`'s own signature carries no float parameter a caller
    could hand it instead of letting the figure be computed — checked against the signature, not
    merely by calling it correctly. Third, `verify_removals` refuses a removal with no matching
    log entry, and accepts the identical removal once one exists.
    """
    from .. import misuse as misuse_mod
    from ..model import Overlay
    from ..repo import ModelRepo

    repo = ModelRepo.open(ctx.repo_dir)
    overlay = Overlay.load(repo, "netflix")
    perspective = overlay.perspectives["the-operator"]
    option, constraint = "stake-the-quarter-on-one-title", "insolvency"

    figure = misuse_mod.compute_attractiveness(perspective, overlay.responses, option, constraint)
    if not figure.get("mode"):
        raise Violated(f"compute_attractiveness returned no real figure: {figure}")

    import inspect

    for name, param in inspect.signature(misuse_mod.log_removal).parameters.items():
        if param.annotation in (float, "float"):
            raise Violated(f"log_removal accepts a raw float parameter {name!r} — attractiveness could be stated")

    after = {**perspective, "ruin": {}}
    unlogged = misuse_mod.verify_removals(perspective, after, [])
    if not unlogged:
        raise Violated("an unlogged removal of a perspective's own declared constraint verified clean")

    log_entry = misuse_mod.log_removal(
        perspective, overlay.responses, option, constraint, "constraint-owner",
        "guard-planted removal", "2026-08-10", path=ctx.tmp / "guard-removal-log.jsonl",
    )
    logged = misuse_mod.verify_removals(perspective, after, [log_entry])
    if logged:
        raise Violated(f"the identical removal, now logged with a computed figure, still failed verification: {logged}")

    return (
        f"attractiveness computed as mode={figure['mode']} (not stated); log_removal accepts no "
        "raw float; an unlogged removal is rejected and the same removal logged clean verifies"
    )


@harness_check("a_challenge_to_a_constituent_survives_an_unrelated_resolution")
def _a_challenge_to_a_constituent_survives_an_unrelated_resolution(ctx: Context) -> str:
    """Contestability is a primary workflow, and a challenge to one claim cannot be closed by a
    resolution to another (build ticket 60, decision tickets 07/15).

    A guard on the suite rather than an invariant, the same shape `position_deltas_have_no_privileged_default`
    is: this asserts a **semantic property of a module's contract**, not one of the constitution's
    sixteen fixed names.

    Two legs on the fixture graph. First, `resolve()` can only ever build a resolution whose
    `claim_path` equals its challenge's — proven by round-tripping a real challenge through it and
    checking the two agree, not merely by reading the function's signature. Second, the refusal:
    `refuse_answering_a_different_claim` bites on a hand-built resolution that names a different
    path, and `for_artefact` still reports the original challenge as open when the only resolution
    on file is for that unrelated path — a challenge to a constituent is not answered by a
    resolution to an aggregate that happens to share the artefact.
    """
    import json

    from .. import challenges as challenges_mod
    from ..artefact import ArtefactError, digest_of_file, load as load_artefact
    from ..grades import Capabilities
    from ..repo import ModelRepo
    from ..verbs import graph as graph_verb

    repo = ModelRepo.open(ctx.repo_dir)
    artefact = graph_verb(repo, ctx.caps, "netflix", ["twin", "graph"])
    graph_path = ctx.tmp / "guard-graph.json"
    artefact.write(graph_path)
    doc = load_artefact(graph_path)
    sha = digest_of_file(graph_path)

    challenge = challenges_mod.raise_challenge(
        doc, sha, "components[1].evolution", "guard-planted dispute", ["twin", "challenge"]
    )
    challenge_doc = json.loads(challenge.to_bytes())
    resolution = challenges_mod.resolve(challenge_doc, challenge.digest(), "guard response", ["twin", "resolve-challenge"])
    if resolution.body["claim_path"] != challenge.body["claim_path"]:
        raise Violated("resolve() produced a resolution whose claim_path differs from its challenge's")

    unrelated = {
        "envelope": {"kind": challenges_mod.KIND_RESOLUTION},
        "body": {
            "challenge_sha256": "not-this-challenge", "claim_path": "components[0].evolution",
            "response": "unrelated",
        },
    }
    try:
        challenges_mod.refuse_answering_a_different_claim(challenge_doc, unrelated)
    except ArtefactError:
        pass
    else:
        raise Violated("a resolution naming a different claim_path was not refused")

    report = challenges_mod.for_artefact(sha, [challenge_doc], [unrelated])
    if not report["has_unresolved_challenges"]:
        raise Violated("an unrelated resolution on the same artefact closed a constituent's challenge")
    if report["open"][0]["claim_path"] != "components[1].evolution":
        raise Violated("the open challenge reported does not name the claim that was actually challenged")

    return (
        "resolve() reproduces its challenge's own claim_path; a hand-built resolution naming a "
        "different one is refused; an unrelated resolution on the same artefact leaves the "
        "original challenge reported open, not silently closed"
    )


@harness_check("skill_eval_harness_is_agnostic_and_thresholds_are_guarded")
def _skill_eval_harness_is_agnostic_and_thresholds_are_guarded(ctx: Context) -> str:
    """Seam 3: the skill-eval harness is skill-agnostic, its thresholds are versioned, and a
    lowered threshold needs a citation the way a moved invariant hash does (build ticket 42,
    decision ticket 20).

    A guard on the suite rather than an invariant, for the same reason `prefilter_precedes_pricing`
    inspects `twin/options.py`'s public surface: this asserts **structural properties of a module's
    contract**, checked against its source and against git history, not trusted from a docstring.

    Three legs. First, none of `twin/skills.py`'s harness functions hardcode one of the six real
    skills' names — checked against each function's own source, the same way
    `test_skills.py::test_the_harness_is_skill_agnostic` is, so the suite catches it even if that
    test is ever deleted. Second, a fixture skill (`toy-classifier`) actually runs end to end and
    a degraded one fails its threshold — proving the harness does something, not merely that it
    imports. Third, a threshold that decreased since the manifest's last committed version needs
    an `authorised_by` citing a decision ticket — the same `hash_changes_are_authorised` pattern,
    applied to a second file.
    """
    import inspect

    from .. import skills as skills_mod

    real_skills = (
        "signal-classify", "causal-claims", "evolution-judge", "substrate-generator",
        "gameplay-lens", "ethics-gate",
    )
    for fn in (
        skills_mod.evaluate, skills_mod.threshold_for, skills_mod.load_thresholds,
        skills_mod.record_score, skills_mod.load_scores, skills_mod.detect_regression,
    ):
        body = inspect.getsource(fn)
        hit = [s for s in real_skills if s in body]
        if hit:
            raise Violated(f"{fn.__name__} names {', '.join(hit)} — the harness is not skill-agnostic")

    good = skills_mod.evaluate("toy-classifier", skills_mod.toy_classifier, skills_mod.TOY_SKILL_CORPUS)
    if not good.passed:
        raise Violated("the fixture skill failed its own corpus running correctly — the harness has no subject")
    bad = skills_mod.evaluate("toy-classifier", lambda x: "wrong", skills_mod.TOY_SKILL_CORPUS)
    if bad.passed:
        raise Violated("a skill that gets every item wrong still passed — the threshold is not gating anything")

    current = skills_mod.load_thresholds()
    head = _thresholds_at(REPO_DIR, "HEAD")
    if head is None:
        return (
            f"{len(real_skills)} real skill names absent from every harness function; the fixture "
            "skill passes and a degraded one fails; no committed threshold history to compare yet"
        )
    lowered = [
        name
        for name, entry in current["thresholds"].items()
        if name in head["thresholds"]
        and float(entry["threshold"]) < float(head["thresholds"][name]["threshold"])
        and not _cites_decision_ticket(str(entry.get("authorised_by") or ""))
    ]
    if lowered:
        raise Violated(
            "threshold(s) lowered with no authorising decision ticket cited in `authorised_by`: "
            + ", ".join(sorted(lowered))
        )
    return (
        f"{len(real_skills)} real skill names absent from every harness function; the fixture "
        "skill passes and a degraded one fails; no threshold lowered since HEAD without a citation"
    )


@harness_check("signal_classify_is_grade_5_by_construction")
def _signal_classify_is_grade_5_by_construction(ctx: Context) -> str:
    """`signal-classify` (build ticket 43, decision ticket 11 Q2): an automated binding claim is
    grade 5 by construction, and nothing about calling the skill can produce a different grade —
    checked against its own source (no grade-shaped parameter exists to call it with) and against
    its actual output, the same two-leg shape `skill_eval_harness_is_agnostic_and_thresholds_are_guarded`
    uses for the harness itself.

    Also runs the skill end to end against its real labelled corpus (the pooled
    Carillion/NMC/Wirecard/Enron signals `tests/test_signal_classify.py` also evaluates against,
    built fresh here in `ctx.tmp` the same way `carillion_answer_key_is_dated_and_adversarial`
    builds its own fixture) and proves a degraded classifier fails the threshold — a harness with
    no subject running proves nothing.
    """
    import inspect

    from .. import signal_classify as sc
    from .. import skills as skills_mod

    params = inspect.signature(sc.classify).parameters
    if "grade" in params or "evidence_grade" in params:
        raise Violated("signal_classify.classify() accepts a grade-shaped parameter — grade 5 is no longer by construction")

    sample = {
        "statement": "A trading update on financial performance.",
        "source": "Company announcement",
        "candidates": [{"id": "x", "name": "y"}],
    }
    grade = sc.classify(sample)["claim"].get("evidence_grade")
    if grade != 5:
        raise Violated(f"signal_classify.classify() emitted evidence_grade {grade!r}, not 5")

    corpus = sc.labelled_corpus(ctx.tmp / "signal-classify-corpus")
    good = skills_mod.evaluate(sc.SKILL, sc.classify, corpus, scorer=sc.scorer)
    if not good.passed:
        raise Violated("signal-classify failed its own labelled corpus running correctly — the harness has no subject")
    bad = skills_mod.evaluate(
        sc.SKILL,
        lambda payload: {"steep": "environmental", "claim": {"component": "not-a-real-component"}},
        corpus, scorer=sc.scorer,
    )
    if bad.passed:
        raise Violated("a classifier that gets every item wrong still passed — the threshold is not gating anything")

    return (
        "no grade-shaped parameter exists on classify(); every call returns evidence_grade 5; "
        f"the real {len(corpus)}-item labelled corpus passes and a degraded classifier fails its threshold"
    )


@harness_check("evolution_judge_output_is_graded_by_construction_and_never_silent")
def _evolution_judge_output_is_graded_by_construction_and_never_silent(ctx: Context) -> str:
    """`evolution-judge` (build ticket 44, decision ticket 11 Q1): the twin's own inference is
    grade 5 by construction, an override is grade 4 and attributable to a registered role, an
    override cannot be constructed without the twin's own prior inference, and the twin's pushback
    is never empty — the same structural-plus-live two-leg shape
    `signal_classify_is_grade_5_by_construction` uses, extended to the override half ticket 43 did
    not need.

    Also runs the skill end to end against its real labelled corpus (the four backtest orgs'
    dated positions `tests/test_evolution_judge.py` also evaluates against, built fresh here in
    `ctx.tmp`) and proves a degraded judge fails the threshold.
    """
    import inspect

    from .. import evolution_judge as ej
    from .. import skills as skills_mod

    judge_params = inspect.signature(ej.judge).parameters
    if "grade" in judge_params or "evidence_grade" in judge_params:
        raise Violated("evolution_judge.judge() accepts a grade-shaped parameter — grade 5 is no longer by construction")

    override_params = inspect.signature(ej.override).parameters
    if "grade" in override_params or "evidence_grade" in override_params:
        raise Violated("evolution_judge.override() accepts a grade-shaped parameter — grade 4 is no longer by construction")
    if list(override_params)[0] != "inferred":
        raise Violated(
            "evolution_judge.override()'s first parameter is not 'inferred' — decision ticket 11 Q1 requires "
            "inference before any human input is accepted, structurally, not by convention"
        )

    sample = {"component": {"id": "x", "name": "A trading business."}, "evidence": []}
    inferred = ej.judge(sample)
    if inferred["claim"].get("evidence_grade") != 5:
        raise Violated(f"evolution_judge.judge() emitted evidence_grade {inferred['claim'].get('evidence_grade')!r}, not 5")

    correction = ej.override(inferred, "x", 0.9, "model-steward", "a review found stronger commoditisation")
    if correction.get("evidence_grade") != 4:
        raise Violated(f"evolution_judge.override() emitted evidence_grade {correction.get('evidence_grade')!r}, not 4")

    from ..sign import role_ids

    if correction["claimed_by"] not in role_ids():
        raise Violated("evolution_judge.override() accepted a claimed_by not in the role register")

    disagreeing = ej.pushback(inferred, correction)
    agreeing = ej.pushback(inferred, ej.override(inferred, "x", inferred["claim"]["evolution_position"], "model-steward", "confirmed"))
    if not disagreeing.get("statement") or not agreeing.get("statement"):
        raise Violated("evolution_judge.pushback() returned an empty statement — silence is not an option, agreement included")

    corpus = ej.labelled_corpus(ctx.tmp / "evolution-judge-corpus")
    good = skills_mod.evaluate(ej.SKILL, ej.judge, corpus, scorer=ej.scorer)
    if not good.passed:
        raise Violated("evolution-judge failed its own labelled corpus running correctly — the harness has no subject")
    bad = skills_mod.evaluate(
        ej.SKILL, lambda payload: {"evolution_position": 0.999}, corpus, scorer=ej.scorer,
    )
    if bad.passed:
        raise Violated("a judge that gets every item wrong still passed — the threshold is not gating anything")

    return (
        "no grade-shaped parameter exists on judge() or override(); judge() always emits grade 5, "
        "override() always emits grade 4 and refuses an unregistered role, override() cannot run "
        "without an inferred claim first, pushback() is never silent on agreement or disagreement; "
        f"the real {len(corpus)}-item labelled corpus passes and a degraded judge fails its threshold"
    )


@harness_check("causal_claims_over_grading_is_penalised_and_alternatives_are_mandatory")
def _causal_claims_over_grading_is_penalised_and_alternatives_are_mandatory(ctx: Context) -> str:
    """`causal-claims` (build ticket 45, decision ticket 08 Q5): unlike `signal-classify` and
    `evolution-judge`, this skill's own evidence grade genuinely varies with its input rather than
    being fixed by construction — so the property to guard is not "always grade N" but **the
    asymmetric penalty and the mandatory alternative-explanation field survive contact with a
    proposer that cheats in the dangerous direction.**

    Three legs. First, a proposer that gets every claim's sign/lag/elasticity right but stamps
    every grade to the strongest rung (1) passes the claim metric and fails the grade metric at
    0.0 — the precise failure this ticket exists to catch, run here against the real labelled
    corpus rather than trusted from a docstring. Second, `propose()`'s own `alternatives` field is
    never empty, checked directly against its output with no candidate confounders supplied at
    all, so the mandatory field cannot silently become optional. Third, `shared_ancestors()`
    genuinely finds the real, fixture-authored shared dependency on both co-flagship edges
    (`content-delivery-network` for netflix's `streaming-displaces-dvd`, `foundry-services` for
    intel's `euv-delay-slips-the-node`) — a confounder detector that never fires on real data
    proves nothing by existing.
    """
    from .. import causal_claims as cc
    from .. import skills as skills_mod
    from ..model import Overlay
    from ..repo import ModelRepo

    corpus = cc.labelled_corpus(ctx.tmp / "causal-claims-corpus")

    def over_grades_everything(payload: dict[str, Any]) -> dict[str, Any]:
        honest = cc.propose(payload)
        honest["edge"]["evidence_grade"] = 1
        return honest

    claim_result = skills_mod.evaluate(cc.SKILL, over_grades_everything, corpus, scorer=cc.scorer)
    if not claim_result.passed:
        raise Violated("a proposer with the right sign/lag/elasticity but the wrong grade should still pass the claim metric")
    grade_result = skills_mod.evaluate(cc.GRADE_SKILL, over_grades_everything, corpus, scorer=cc.grade_scorer)
    if grade_result.passed or grade_result.score != 0.0:
        raise Violated(
            f"a proposer that over-grades every item to the strongest rung scored {grade_result.score} on the "
            "grade metric and passed — the asymmetric penalty is not gating the dangerous direction"
        )

    no_confounders = cc.propose(
        {
            "from": {"id": "x", "name": "X"}, "to": {"id": "y", "name": "Y"},
            "evidence": [{"statement": "A model assertion.", "source": "s"}],
            "candidate_confounders": [],
        }
    )
    if not no_confounders["alternatives"]:
        raise Violated("propose() returned an empty alternatives field — the mandatory alternative-explanation field is not mandatory")

    repo = ModelRepo.open(ctx.repo_dir)
    netflix_graph = Overlay.load(repo, "netflix").graph()
    netflix_confounders = cc.shared_ancestors(netflix_graph, "streaming-experience", "dvd-by-mail")
    if "content-delivery-network" not in netflix_confounders:
        raise Violated("shared_ancestors() did not find the real shared dependency on the netflix co-flagship edge")
    intel_graph = Overlay.load(repo, "intel").graph()
    intel_confounders = cc.shared_ancestors(intel_graph, "euv-lithography", "leading-edge-process-node")
    if "foundry-services" not in intel_confounders:
        raise Violated("shared_ancestors() did not find the real shared dependency on the intel co-flagship edge")

    return (
        "over-grading every item to grade 1 passes the claim metric and fails the grade metric at "
        "0.0; propose() never returns an empty alternatives field; shared_ancestors() finds the "
        "real shared dependency on both co-flagship edges"
    )


@harness_check("gameplay_lens_is_grade_5_and_reports_no_recommendation")
def _gameplay_lens_is_grade_5_and_reports_no_recommendation(ctx: Context) -> str:
    """`gameplay-lens` (build ticket 46, decision ticket 13 Q3): a proposed play is grade 5 by
    construction — checked against `propose()`'s own source and against its actual output, the
    same two-leg shape `signal_classify_is_grade_5_by_construction` uses — and the scheduled sweep
    that pulls opportunity candidates forward carries no recommended-action field, re-asserting
    `no_recommended_action_field`'s own banned-word scan against a third artefact
    (`trade_off_curve_reports_disagreement_never_a_scalar` was the second) rather than growing the
    constitution's fixed sixteen.

    Three legs. First, structural-plus-live grade-5: no grade-shaped parameter on `propose()`, and
    a real call emits `evidence_grade: 5`. Second, the real labelled corpus (the same three org
    maps `tests/test_gameplay_lens.py` evaluates against, built fresh here in `ctx.tmp`) passes and
    a skill that proposes nothing fails the threshold — a harness with no subject proves nothing.
    Third, `sweep()`'s own artefact on the netflix/intel fixture carries both an opportunity count
    and a signal count side by side — the AC this ticket's checklist names, "opportunity output
    volume is reported alongside threat output volume" — and the identical banned-word/phrase scan
    `no_recommended_action_field` runs finds nothing in it.
    """
    import inspect

    from . import NO_ACTION_BANNED_KEYS, NO_ACTION_BANNED_PHRASES
    from .. import gameplay_lens as gl
    from .. import skills as skills_mod
    from ..canon import walk_keys, walk_values
    from ..repo import ModelRepo

    params = inspect.signature(gl.propose).parameters
    if "grade" in params or "evidence_grade" in params:
        raise Violated("gameplay_lens.propose() accepts a grade-shaped parameter — grade 5 is no longer by construction")

    sample = {
        "positions": [
            {"component": "c", "stage": "product", "evolution": 0.65, "visibility": 0.5},
            {"component": "adj", "stage": "commodity", "evolution": 0.9, "visibility": 0.2},
        ],
        "edges": [
            {"id": "e1", "type": "needs", "from": "c", "to": "adj"},
            {"id": "e2", "type": "knows", "from": "person", "to": "adj"},
        ],
        "org_components": ["c"],
    }
    hits = gl.propose(sample)["opportunities"]
    if not hits or any(o["claim"].get("evidence_grade") != 5 for o in hits):
        raise Violated(f"gameplay_lens.propose() emitted a non-grade-5 claim: {hits}")

    corpus = gl.labelled_corpus(ctx.tmp / "gameplay-lens-corpus")
    good = skills_mod.evaluate(gl.SKILL, gl.propose, corpus, scorer=gl.scorer)
    if not good.passed:
        raise Violated("gameplay-lens failed its own labelled corpus running correctly — the harness has no subject")
    bad = skills_mod.evaluate(gl.SKILL, lambda payload: {"opportunities": []}, corpus, scorer=gl.scorer)
    if bad.passed:
        raise Violated("a skill that proposes nothing still passed — the threshold is not gating anything")

    repo = ModelRepo.open(ctx.repo_dir)
    swept = gl.sweep([repo], ctx.caps, ["twin", "gameplay-sweep"])
    counts = swept.body["counts"]
    if not (counts.get("opportunities", 0) > 0 and counts.get("signals", 0) > 0):
        raise Violated(
            f"the sweep did not report both a positive opportunity count and a positive signal "
            f"count side by side: {counts}"
        )

    for key in walk_keys(swept.body):
        if any(word in key.lower() for word in NO_ACTION_BANNED_KEYS):
            raise Violated(f"the gameplay sweep carries an action-shaped field ({key})")
    for key, value in walk_values(swept.body):
        if isinstance(value, str) and any(phrase in value.lower() for phrase in NO_ACTION_BANNED_PHRASES):
            raise Violated(f"the gameplay sweep states an action in prose at {key}: {value!r}")

    return (
        "no grade-shaped parameter exists on propose(); every opportunity carries evidence_grade "
        f"5; the real {len(corpus)}-item labelled corpus passes and a skill that proposes nothing "
        f"fails its threshold; the sweep reports {counts['opportunities']} opportunity candidate(s) "
        f"beside {counts['signals']} signal(s), and no action-shaped field found in it"
    )


def _thresholds_at(root: Path, ref: str) -> dict[str, Any] | None:
    rel = (REPO_DIR / "twin" / "skill-thresholds.yaml").relative_to(root).as_posix()
    out = _git(root, "show", f"{ref}:{rel}")
    if out is None:
        return None
    return dict(yaml.safe_load(out))


@harness_check("carillion_answer_key_is_dated_and_adversarial")
def _carillion_answer_key_is_dated_and_adversarial(ctx: Context) -> str:
    """The primary backtest key names contemporaneous, adversarial sources and a real rewind can
    read its own history (build ticket 38, decision ticket 19's evidence-asymmetry argument).

    A guard on the suite rather than an invariant, for the same reason `graded_edge_fixture_holds_its_contract`
    is: this asserts a **property of a fixture's contract downstream tickets (39-41, 71-77) will
    build against**, not an absence the constitution names.

    Four legs. Every signal carries a dated fact and a non-placeholder citation. No signal cites
    HC 769 (the post-collapse inquiry report) — that would be hindsight leaking into what is
    supposed to be contemporaneous ground truth, and the outcome is where that citation belongs.
    The commit history is monotonically dated, which is what makes `ingestion_history` a real
    rewind here rather than the date-filter-only fallback the main netflix/intel fixture is
    limited to. And the world layer names no tenant, the same direction rule every fixture holds.
    """
    import subprocess

    from .. import fixtures
    from ..model import Overlay, check_direction
    from ..repo import ModelRepo

    carillion_dir = ctx.tmp / "carillion-repo"
    if not carillion_dir.exists():
        fixtures.build_carillion_org(carillion_dir)
    repo = ModelRepo.open(carillion_dir)
    overlay = Overlay.load(repo, fixtures.CARILLION_ORG)

    if len(overlay.signals) < 3:
        raise Violated(f"the Carillion key carries only {len(overlay.signals)} signal(s)")
    for signal_id, signal in overlay.signals.items():
        url = signal.get("provenance", {}).get("url", "")
        if not url.startswith("https://"):
            raise Violated(f"signal {signal_id!r} carries no https citation")
        if "example.invalid" in url:
            raise Violated(f"signal {signal_id!r} carries a placeholder citation, not a real one")
        if "769" in url:
            raise Violated(f"signal {signal_id!r} cites HC 769 — a post-collapse inquiry report is hindsight")
        if not str(signal.get("date", "")).count("-") == 2:
            raise Violated(f"signal {signal_id!r} carries no dated fact")

    outcome = overlay.outcomes.get("carillion-collapse-resolved")
    if outcome is None:
        raise Violated("the Carillion overlay carries no resolved outcome")
    if outcome.get("contamination") != "low":
        raise Violated(f"the answer key declares contamination={outcome.get('contamination')!r}, not 'low'")
    if "769" not in str(outcome.get("source", "")):
        raise Violated("the answer key's own source does not cite HC 769 — the adversarial post-mortem is unnamed")

    proc = subprocess.run(
        ["git", "log", "--format=%cI", "--reverse"], cwd=str(carillion_dir),
        stdout=subprocess.PIPE, check=True,
    )
    from datetime import datetime as _dt

    dates = [_dt.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
    if dates != sorted(dates):
        raise Violated("the Carillion fixture's commit history is not monotonically dated")

    violations = check_direction(repo)
    if violations:
        raise Violated(f"the world layer references the carillion tenant: {'; '.join(violations)}")

    return (
        f"{len(overlay.signals)} dated signal(s), each citing a live https source and none citing "
        "the post-collapse HC 769; the answer key itself does; commit history spans "
        f"{dates[0].date()}..{dates[-1].date()} monotonically; the world layer names no tenant"
    )


# One fixture builder, one hindsight source, one declared contamination class per row — the
# table a new answer-key fixture adds a row to rather than a new copy of the whole check (build
# ticket 39, extended at build ticket 40). The builder travels with its row rather than being
# re-derived from the org string, so a further key is one line here and needs no branch anywhere
# in the check body. Enron's row differs from NMC/Wirecard's only in its declared class
# (`contamination: control`, not `low`/`high`) — the table already had no opinion on which values
# are valid, so it needed no widening to take it.
_FurtherAnswerKey = tuple[str, Callable[[Path], Path], str, str, str]
_FURTHER_ANSWER_KEYS: tuple[_FurtherAnswerKey, ...] = (
    ("nmc", fixtures.build_nmc_health_org, "nmc-administration-resolved", "healthcareandprotection.com", "low"),
    ("wirecard", fixtures.build_wirecard_org, "wirecard-insolvency-resolved", "bundestag.de", "high"),
    ("enron", fixtures.build_enron_org, "enron-bankruptcy-resolved", "powers.report", "control"),
)


@harness_check("further_answer_keys_are_dated_and_evidenced")
def _further_answer_keys_are_dated_and_evidenced(ctx: Context) -> str:
    """The further answer keys (build ticket 39, extended at build ticket 40; decision ticket 19)
    hold the same contract `carillion_answer_key_is_dated_and_adversarial` checks for the primary
    one: every signal is dated and cites a live https source, no signal cites the post-collapse
    adversarial finding that belongs on the outcome alone, the outcome declares a `contamination`
    class from the schema's enum, and the fixture's own commit history is monotonically dated.

    One loop over `_FURTHER_ANSWER_KEYS`, rather than a near-duplicate check per fixture — the row
    is what a further key adds, whether it is another low-notoriety case or (Enron) the
    contamination control itself.
    """
    from ..model import Overlay, check_direction
    from ..repo import ModelRepo

    reports: list[str] = []
    for org, builder, outcome_id, hindsight_domain, expected_contamination in _FURTHER_ANSWER_KEYS:
        repo_dir = ctx.tmp / org
        if not repo_dir.exists():
            builder(repo_dir)
        repo = ModelRepo.open(repo_dir)
        overlay = Overlay.load(repo, org)

        if len(overlay.signals) < 3:
            raise Violated(f"the {org} key carries only {len(overlay.signals)} signal(s)")
        for signal_id, signal in overlay.signals.items():
            url = signal.get("provenance", {}).get("url", "")
            if not url.startswith("https://"):
                raise Violated(f"{org} signal {signal_id!r} carries no https citation")
            if "example.invalid" in url:
                raise Violated(f"{org} signal {signal_id!r} carries a placeholder citation, not a real one")
            if hindsight_domain in url:
                raise Violated(f"{org} signal {signal_id!r} cites the post-collapse adversarial finding")
            if not str(signal.get("date", "")).count("-") == 2:
                raise Violated(f"{org} signal {signal_id!r} carries no dated fact")

        outcome = overlay.outcomes.get(outcome_id)
        if outcome is None:
            raise Violated(f"the {org} overlay carries no resolved outcome {outcome_id!r}")
        if outcome.get("contamination") != expected_contamination:
            raise Violated(
                f"the {org} answer key declares contamination={outcome.get('contamination')!r}, "
                f"not {expected_contamination!r} — the ticket 39 notoriety assessment"
            )
        if hindsight_domain not in str(outcome.get("source", "")):
            raise Violated(f"the {org} answer key's own source does not cite the adversarial finding")
        if not str(outcome.get("note", "")).strip():
            raise Violated(f"the {org} answer key carries no notoriety-assessment note")

        violations = check_direction(repo)
        if violations:
            raise Violated(f"the world layer references the {org} tenant: {'; '.join(violations)}")

        proc = subprocess.run(
            ["git", "log", "--format=%cI", "--reverse"], cwd=str(repo_dir),
            stdout=subprocess.PIPE, check=True,
        )
        commit_dates = [datetime.datetime.fromisoformat(line) for line in proc.stdout.decode().splitlines()]
        if commit_dates != sorted(commit_dates):
            raise Violated(f"the {org} fixture's commit history is not monotonically dated")

        reports.append(f"{org}: {len(overlay.signals)} signal(s), contamination={expected_contamination}")

    return "; ".join(reports)


@harness_check("measure_discount_is_computed_not_hardcoded")
def _measure_discount_is_computed_not_hardcoded(ctx: Context) -> str:
    """The memorisation-leakage discount is genuinely a measurement, not a constant wearing a
    function's clothes (build ticket 40, decision ticket 19).

    The fixture side of ticket 40 (dated signals, no hindsight leak, `contamination: control`,
    world-layer direction, monotonic commit history) is Enron's row in `_FURTHER_ANSWER_KEYS`,
    checked by `further_answer_keys_are_dated_and_evidenced` above — repeating it here would be
    exactly the near-duplicate check that table exists to avoid. This guard covers only what that
    one cannot: that `scoring.measure_discount` produces a different number when the underlying
    scores change — proof, run at CI time rather than trusted from a comment, that nothing
    hardcoded the figure.
    """
    from ..scoring import measure_discount, score

    low = [score(0.05, True), score(0.1, True)]
    high = [score(0.4, True), score(0.6, True)]
    a = measure_discount(low, high, rule="brier")
    b = measure_discount(high, low, rule="brier")
    if a["discount"] == b["discount"]:
        raise Violated("measure_discount produced the same figure for two different score populations")

    return (
        f"measure_discount({low!r}, {high!r})={a['discount']} != "
        f"measure_discount({high!r}, {low!r})={b['discount']}"
    )


@harness_check("hindsight_resistance_cases_score_a_memorising_system_worse")
def _hindsight_resistance_cases_score_a_memorising_system_worse(ctx: Context) -> str:
    """Both hindsight-resistance cases hold the dated-and-cited contract, declare the trap
    explicitly on the outcome, and demonstrate the thing they exist to demonstrate: a world model
    that recites the canonical story scores worse than one that reasons from the contemporaneous
    record (build ticket 41, decision ticket 19).

    A guard on the suite rather than an invariant, the same shape the answer-key guards above are.
    Table-driven over the two cases (AstraZeneca, Sanofi) rather than duplicated, the same
    discipline `further_answer_keys_are_dated_and_evidenced` holds — each row differs only in
    which world model is expected to win, because the two cases are an inverse pair.
    """
    from .. import fixtures, verbs
    from ..model import Overlay, check_direction
    from ..repo import ModelRepo
    from ..scoring import measure_discount

    cases = (
        (fixtures.build_astrazeneca_org, fixtures.ASTRAZENECA_ORG, "az-market-verdict-resolved", "az"),
        (fixtures.build_sanofi_org, fixtures.SANOFI_ORG, "sanofi-market-verdict-resolved", "sanofi"),
    )
    scenario_id = "would-the-twin-recite-the-ending"
    reports: list[str] = []
    honest_scores: dict[str, dict] = {}
    memorising_scores: dict[str, dict] = {}

    for builder, org, outcome_id, tag in cases:
        repo_dir = ctx.tmp / tag
        if not repo_dir.exists():
            builder(repo_dir)
        repo = ModelRepo.open(repo_dir)
        overlay = Overlay.load(repo, org)

        outcome = overlay.outcomes.get(outcome_id)
        if outcome is None:
            raise Violated(f"the {tag} overlay carries no resolved outcome {outcome_id!r}")
        if outcome.get("hindsight_trap") is not True:
            raise Violated(f"the {tag} answer key does not declare hindsight_trap: true")

        scenario = overlay.scenarios.get(scenario_id)
        if scenario is None:
            raise Violated(f"the {tag} overlay carries no scenario {scenario_id!r}")
        if set(scenario.get("world_models", [])) != {"contemporaneous-consensus", "canonical-hindsight-consensus"}:
            raise Violated(f"the {tag} scenario does not name both hindsight world models")

        violations = check_direction(repo)
        if violations:
            raise Violated(f"the world layer references the {tag} tenant: {'; '.join(violations)}")

        bundle_artefact = verbs.run(
            repo, ctx.caps, org, scenario_id, "as-consumed",
            ["twin", "run", "--org", org, "--scenario", scenario_id, "--regime", "as-consumed"],
        )
        with tempfile.TemporaryDirectory(prefix="twin-hindsight-guard-") as scratch:
            bundle_path = Path(scratch) / "bundle.json"
            bundle_path.write_bytes(bundle_artefact.to_bytes())
            card = verbs.score(
                repo, ctx.caps, org, bundle_path, outcome_id,
                ["twin", "score", "--org", org, "--outcome", outcome_id],
            )
        by_model = {entry["world_model"]: entry for entry in card.body["scores"]}
        if set(by_model) != {"contemporaneous-consensus", "canonical-hindsight-consensus"}:
            raise Violated(f"the {tag} score card does not carry both world models' scores")
        honest, memorising = by_model["contemporaneous-consensus"], by_model["canonical-hindsight-consensus"]
        if memorising["brier"] <= honest["brier"]:
            raise Violated(
                f"the {tag} canonical-hindsight world model did not score worse than the honest "
                f"one (memorising brier={memorising['brier']}, honest brier={honest['brier']})"
            )
        honest_scores[tag], memorising_scores[tag] = honest, memorising
        reports.append(f"{tag}: memorising brier={memorising['brier']} > honest brier={honest['brier']}")

    # The results feed the same discount ticket 40 measures, rather than sitting beside it.
    enron_stub = [{"brier": 0.9409, "log_loss": 2.813}]
    obscure_stub = [{"brier": 0.9025, "log_loss": 2.708}]
    without = measure_discount(enron_stub, obscure_stub, rule="brier")
    with_hindsight = measure_discount(
        enron_stub, obscure_stub, rule="brier",
        hindsight_memorising=list(memorising_scores.values()), hindsight_honest=list(honest_scores.values()),
    )
    if with_hindsight["discount"] == without["discount"]:
        raise Violated("folding the hindsight-resistance scores into measure_discount changed nothing")

    return "; ".join(reports) + (
        f"; discount without hindsight={without['discount']}, with hindsight={with_hindsight['discount']}"
    )


@harness_check("backtest_is_a_pure_composition")
def _backtest_is_a_pure_composition(ctx: Context) -> str:
    """`twin backtest` is rewind plus projection, with no backtest-specific code path
    (build ticket 37, decision ticket 13 Q2: "the backtest is not a special mode and needs no
    separate harness").

    A guard on the suite rather than an invariant, the same shape `an_intervention_never_reaches_upstream`
    is: the constitution's sixteen are fixed, and this asserts a **structural property of the CLI
    command itself** — checked against its source, not merely claimed by its docstring, for the
    reason `prefilter_precedes_pricing` inspects `twin/options.py`'s public surface rather than
    trusting a comment: a property that only holds by convention is a property that erodes the
    first time somebody is in a hurry.

    Two legs. First, the source: `cmd_backtest` calls `rewind(` and `verbs.run(` and references no
    propagation, intervention or scoring machinery of its own — a second implementation hiding
    behind the same name would still pass a black-box output check, so this reads the function
    body directly. Second, the composition actually computes the same thing `run()` computes on
    its own: rewinding explicitly first and then calling `run()` at the same time produces a
    forecast identical to calling `run()` directly at that time, save for which command is
    recorded as having produced it — proving the explicit rewind adds no second derivation, only
    an explicit statement of what `run()`'s own regime gate already does internally.
    """
    import inspect

    from .. import cli, verbs

    source = inspect.getsource(cli.cmd_backtest)
    if "rewind(" not in source or "verbs.run(" not in source:
        raise Violated("cmd_backtest no longer calls both rewind( and verbs.run( — the composition changed")
    forbidden = ("propagate", "Do(", "Observe(", "scoring.")
    hit = [f for f in forbidden if f in source]
    if hit:
        raise Violated(f"cmd_backtest references {', '.join(hit)} — a second code path beside rewind+run")

    from ..cli import main as cli_main

    at = "2026-01-01"
    backtest_out, run_out = ctx.tmp / "guard-backtest.json", ctx.tmp / "guard-run.json"
    rc1 = cli_main([
        "backtest", "--repo", str(ctx.repo_dir), "--org", "netflix", "--scenario", "dvd-decline-2011",
        "--regime", "as-consumed", "--at", at, "--out", str(backtest_out),
    ])
    rc2 = cli_main([
        "run", "--repo", str(ctx.repo_dir), "--org", "netflix", "--scenario", "dvd-decline-2011",
        "--regime", "as-consumed", "--at", at, "--out", str(run_out),
    ])
    if rc1 != 0 or rc2 != 0:
        raise Violated(f"backtest or run exited non-zero (backtest={rc1}, run={rc2})")

    import json

    def strip(body: dict) -> dict:
        return {**body, "forecasts": [
            {k: v for k, v in f.items() if k not in ("id", "pins")} for f in body["forecasts"]
        ]}

    backtest_body = strip(json.loads(backtest_out.read_bytes())["body"])
    run_body = strip(json.loads(run_out.read_bytes())["body"])
    if backtest_body != run_body:
        raise Violated(
            "an explicit rewind followed by run() computed a different forecast than run() alone "
            "at the same time — backtest is not the same primitives run() already composes internally"
        )
    return (
        "cmd_backtest's source calls exactly rewind( and verbs.run(, references no propagation, "
        "intervention or scoring machinery; an explicit rewind+run and run() alone compute the "
        "identical forecast at the same time, differing only in which command produced it"
    )


@harness_check("causal_accounts_have_no_privileged_default")
def _causal_accounts_have_no_privileged_default(ctx: Context) -> str:
    """No causal account — including this overlay's own `edges` collection — is required
    (build ticket 32, decision tickets 07/08).

    A guard on the suite rather than an invariant, the same shape
    `position_deltas_have_no_privileged_default` is for world models: the constitution's sixteen
    are fixed, and this asserts a **semantic property of a module's contract**.

    Three legs, on the netflix fixture's three rival accounts (`netflix-base-case`,
    `rival-aggressive-cannibalisation`, `rival-conservative-view`) all overriding the same edge.
    First, dropping any one of the three still computes and the survivors' own spread figures do
    not move — the same "no privileged position" property `positions.py` established, carried
    into the causal layer. Second, `Overlay.causal_graph` reads a named account and this overlay's
    own `edges` collection through the *same call*: propagating the graph a named account builds
    and propagating `overlay.graph()` directly reach the same components, proving there is no
    special code path for "the primary one". Third, the schema itself: a `causal-account` document
    carrying a planted `author`/`created_at`/`priority` field does not load — adjudication by
    authorship or recency has no field to attach to, not merely a convention against reading one.
    """
    from .. import causal_accounts as causal_accounts_mod
    from ..model import Overlay
    from ..propagate import propagate
    from ..repo import ModelRepo
    from ..schema import SchemaError, validate

    repo = ModelRepo.open(ctx.repo_dir)
    overlay = Overlay.load(repo, "netflix")
    all_accounts = ["netflix-base-case", "rival-aggressive-cannibalisation", "rival-conservative-view"]
    origin = "streaming-experience"

    full = causal_accounts_mod.ensemble_spread(overlay, all_accounts, origin)
    full_by_component = {r["component"]: r["by_account"] for r in full["spread"]}
    for dropped in all_accounts:
        remaining = [a for a in all_accounts if a != dropped]
        narrowed = causal_accounts_mod.ensemble_spread(overlay, remaining, origin)
        if {a["account"] for a in narrowed["accounts"]} != set(remaining):
            raise Violated(f"dropping {dropped!r} changed which accounts the remainder computed")
        for row in narrowed["spread"]:
            for account_id, value in row["by_account"].items():
                if value != full_by_component[row["component"]][account_id]:
                    raise Violated(
                        f"dropping {dropped!r} moved {account_id!r}'s own figure for "
                        f"{row['component']!r} — an account's arithmetic depended on who else was named"
                    )

    via_account = propagate(overlay.causal_graph("netflix-base-case"), origin)
    via_overlay = propagate(overlay.graph(), origin)
    if {e["component"] for e in via_account["reached"]} != {e["component"] for e in via_overlay["reached"]}:
        raise Violated(
            "propagating a named account's graph and propagating overlay.graph() directly reach "
            "different components — there is a code path privileging one over the other"
        )

    base_doc = {
        "id": "planted", "name": "planted",
        "edges": {"e": {"from": "streaming-experience", "to": "dvd-by-mail", "sign": "negative",
                         "lag_days": 1, "elasticity": {"min": 0.1, "mode": 0.2, "max": 0.3},
                         "evidence_grade": 3}},
    }
    for field_name in ("author", "authored_by", "created_at", "priority"):
        try:
            validate("causal-account", {**base_doc, field_name: "x"}, "planted")
        except SchemaError:
            pass
        else:
            raise Violated(f"a causal-account document carrying {field_name!r} validated")

    return (
        f"{len(all_accounts)} accounts, each dispensable, none privileged; dropping any one "
        "leaves the rest's own figures unmoved; a named account and overlay.graph() reach the "
        "same components; a planted author/date field on a causal-account is refused"
    )


@harness_check("trade_off_curve_reports_disagreement_never_a_scalar")
def _trade_off_curve_reports_disagreement_never_a_scalar(ctx: Context) -> str:
    """The trade-off curve across the ensemble surfaces disagreement rather than averaging it
    away, and carries no recommended-action field (build ticket 33, decision tickets 09/13).

    A guard on the suite rather than an invariant, the same shape `causal_accounts_have_no_privileged_default`
    and `position_deltas_have_no_privileged_default` are: this asserts a **semantic property of a
    module's contract**, not one of the constitution's fixed sixteen — and it re-asserts
    `no_recommended_action_field`'s own banned-word scan against this richer output, per build
    ticket 33's own checklist, rather than growing the constitution's fixed set.

    Two legs, on the netflix fixture's `netflix-base-case` / `rival-cdn-headwind` accounts — the
    pair that actually disagrees about a component graded well enough to price.
    `streaming-displaces-dvd`, the edge build ticket 32's other three accounts share, is graded 3
    and never clears the published pricing threshold (2), so a curve built only from those would
    have nowhere for a response's own net figure to move, however much the accounts disagree about
    the elasticity. First, the disagreement is real and reported **per account** rather than
    averaged: `expand-the-delivery-network`'s own net cost of risk differs between the two named
    accounts by a strictly positive `range`, and both accounts' own figures are present in
    `by_account` — not folded into a mean before it reaches the artefact. Second, the same
    banned-word scan `no_recommended_action_field` runs against the Wardley map runs here too, and
    finds nothing: no key or prose value in the curve names an action, a verdict or advice, and the
    `default` it does carry names its own `basis` rather than asserting an answer.
    """
    from .. import tradeoff as tradeoff_mod
    from . import NO_ACTION_BANNED_KEYS, NO_ACTION_BANNED_PHRASES
    from ..canon import walk_keys, walk_values
    from ..model import Overlay
    from ..repo import ModelRepo

    repo = ModelRepo.open(ctx.repo_dir)
    overlay = Overlay.load(repo, "netflix")
    perspective = overlay.perspectives["the-operator"]
    accounts = ["netflix-base-case", "rival-cdn-headwind"]

    body = tradeoff_mod.curve(overlay, perspective, "content-delivery-network", overlay.responses, accounts)

    point = next((p for p in body["curve"] if p["option"] == "expand-the-delivery-network"), None)
    if point is None:
        raise Violated("the curve carries no entry for expand-the-delivery-network")
    by_account = point["net_cost_of_risk"]["by_account"]
    if set(by_account) != set(accounts):
        raise Violated(f"the curve does not report a net figure for every named account: {by_account}")
    if len(set(by_account.values())) < 2:
        raise Violated(
            "two accounts that genuinely disagree about the cdn edge's elasticity produced the "
            f"identical net figure under both: {by_account} — the disagreement did not reach the curve"
        )
    if point["net_cost_of_risk"]["range"] <= 0:
        raise Violated(f"a nonzero spread in by_account did not produce a positive range: {point}")

    # Imported, not re-typed: `no_recommended_action_field` (checks.py) and this guard now read
    # the identical tuple, so one cannot be edited to close a blind spot while the other quietly
    # stays behind. `ranking` is deliberately not in it: `not_a_ranking` is a field this very
    # artefact carries (embedded from `pricing.price()`) to say the opposite.
    for key in walk_keys(body):
        if any(word in key.lower() for word in NO_ACTION_BANNED_KEYS):
            raise Violated(f"the trade-off curve carries an action-shaped field ({key})")
    for key, value in walk_values(body):
        if isinstance(value, str) and any(phrase in value.lower() for phrase in NO_ACTION_BANNED_PHRASES):
            raise Violated(f"the trade-off curve states an action in prose at {key}: {value!r}")

    if "basis" not in body["default"]:
        raise Violated("the default carries no basis — a default with no reason is a verdict wearing a hat")

    return (
        f"expand-the-delivery-network's net cost of risk ranges {point['net_cost_of_risk']['range']:,.0f} "
        f"across {len(accounts)} accounts ({by_account}), reported per account rather than "
        "averaged; no action-shaped field found; the default names its own basis"
    )


@harness_check("unanchored_severity_parameters_are_marked_not_assumed")
def _unanchored_severity_parameters_are_marked(ctx: Context) -> str:
    """An anchored severity subject names which of its parameters are defensible and which are
    illustrative (build ticket 25, decision ticket 09's TVaR-over-VaR commitment deepened).

    A guard on the suite rather than an invariant, for the same reason
    `a_var_shaped_summary_hides_what_tvar_surfaces` is: the constitution's sixteen may not grow a
    seventeenth without the constitution changing first, and this asserts a **semantic property of
    a module's contract** — every anchored parameter carries a citation method, every unanchored
    one carries a reason, and the two are never conflated by the loader.

    Two legs. First, the committed anchor file: at least one parameter is genuinely anchored
    (cited or fit from cited quantiles) and at least one is genuinely not, on the committed subject
    — a file that anchored nothing would make "marked, not assumed" vacuous, and a file that left
    nothing unanchored would never exercise the honest-gap path at all. Second, the refusal itself:
    an anchor file that flips a parameter to `anchored: true` with no `method`, or to
    `anchored: false` with no `reason`, does not load — checked directly against
    `twin/anchoring.py`'s loader rather than trusted to hold because the schema was written the
    right way round.
    """
    import copy

    from .. import anchoring

    doc = anchoring.load()
    subject = doc["subjects"][0]
    params = subject["parameters"]
    anchored_names = [n for n, p in params.items() if p.get("anchored")]
    unanchored_names = [n for n, p in params.items() if not p.get("anchored")]
    if not anchored_names:
        raise Violated(f"subject {subject['id']!r} anchors nothing; 'marked, not assumed' has no positive leg here")
    if not unanchored_names:
        raise Violated(
            f"subject {subject['id']!r} leaves nothing unanchored; the honest-gap path this guard "
            "exists for is never exercised"
        )
    result = anchoring.anchored(str(subject["id"]))
    for p in result.parameters:
        if p.anchored and not p.method:
            raise Violated(f"parameter {p.name!r} is anchored but carries no method in the loaded result")
        if not p.anchored and not p.note:
            raise Violated(f"parameter {p.name!r} is unanchored but carries no reason in the loaded result")

    # The refusal, on a planted violation of each shape.
    import tempfile
    from pathlib import Path

    import yaml

    for planted_name, planted_entry, expect in (
        ("xi", {"anchored": False}, "no reason"),
        ("beta", {"anchored": True}, "no method"),
    ):
        broken = copy.deepcopy(doc)
        broken["subjects"][0]["parameters"][planted_name] = planted_entry
        with tempfile.TemporaryDirectory(prefix="twin-anchor-guard-") as scratch:
            path = Path(scratch) / "broken.yaml"
            path.write_text(yaml.safe_dump(broken), encoding="utf-8")
            try:
                anchoring.load.__wrapped__(path)  # bypass the lru_cache: a fresh path each time anyway
            except anchoring.AnchoringError as exc:
                if expect not in str(exc):
                    raise Violated(f"planting {planted_name}={planted_entry} was refused, but not for {expect!r}: {exc}") from None
            else:
                raise Violated(f"planting {planted_name}={planted_entry} loaded without refusal")

    return (
        f"subject {subject['id']!r}: {len(anchored_names)} anchored ({', '.join(sorted(anchored_names))}), "
        f"{len(unanchored_names)} unanchored ({', '.join(sorted(unanchored_names))}); a planted "
        "anchored-with-no-method or unanchored-with-no-reason is refused"
    )


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
