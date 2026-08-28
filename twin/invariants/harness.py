"""The suite runner and the checks that guard the suite itself."""

from __future__ import annotations

import datetime
import io
import os
import re
import signal
import subprocess
import tempfile
import threading
from contextlib import contextmanager, redirect_stderr
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml

from .. import PACKAGE_DIR, REPO_DIR, fixtures
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


@harness_check("disparate_impact_audit_channel_is_sealed_and_role_gated")
def _disparate_impact_audit_channel_is_sealed_and_role_gated(ctx: Context) -> str:
    """The sealed audit channel decision ticket 15 Q3b finding 4 asks for (build ticket 61):
    "Disparate impact needs no protected field to occur, but does need one to be measured. Needs a
    sealed audit channel, or an explicit admission that the system cannot be checked for it."

    A guard on the suite rather than an invariant, the same shape
    `a_challenge_to_a_constituent_survives_an_unrelated_resolution` is: this asserts a **semantic
    property of a module's contract**, not one of the constitution's sixteen fixed names.

    Two legs. First, sealed: `raise_audit()` runs the identical `refuse_special_category` refusal
    the model repository itself carries — a finding that names the protected characteristic
    (rather than describing the disparity it produced) is refused, exactly as a component or claim
    naming one already is. Second, role-gated: `respond()` refuses a response naming any role but
    `disparate-impact-respondent`, even when the role supplied is itself registered — a channel any
    registered role could close is not answerable to a *defined* respondent.
    """
    import json

    from .. import disparate_impact as di_mod

    try:
        di_mod.raise_audit(
            "disparity by race across cohorts", "guard-planted audit", ["twin", "disparate-impact-audit"]
        )
    except di_mod.DisparateImpactError:
        pass
    else:
        raise Violated("an audit finding naming a protected characteristic was not refused")

    clean = di_mod.raise_audit(
        "cohort A receives systematically worse trade-off ranges than cohort B", "guard-planted audit",
        ["twin", "disparate-impact-audit"],
    )
    audit_doc = json.loads(clean.to_bytes())
    audit_sha = clean.digest()

    for wrong_role in ("model-steward", "challenge-resolver", "constraint-owner"):
        try:
            di_mod.respond(audit_doc, audit_sha, "response text", wrong_role, ["twin", "disparate-impact-respond"])
        except di_mod.DisparateImpactError:
            continue
        raise Violated(f"a response from registered role {wrong_role!r} (not the respondent) was not refused")

    ok = di_mod.respond(
        audit_doc, audit_sha, "response text", di_mod.RESPONDENT_ROLE, ["twin", "disparate-impact-respond"]
    )
    if ok.body["responded_by_role"] != di_mod.RESPONDENT_ROLE:
        raise Violated("a response from the registered respondent did not record its own role")

    return (
        "a finding naming a protected characteristic is refused; a response from any role but "
        f"{di_mod.RESPONDENT_ROLE!r} is refused (checked against three registered roles); the "
        "defined respondent, structurally checked, succeeds"
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


@harness_check("honest_build_inventory_matches_files_and_owning_tickets")
def _honest_build_inventory_matches_files_and_owning_tickets(ctx: Context) -> str:
    """`honest-build`'s AC 2 and AC 4 (build ticket 90, decision ticket 20): the capability
    inventory and the skill-owning-ticket map are computed claims, not typed prose, so this checks
    them the way every other computed claim in the suite is checked — against real files, not
    trusted from the module that declares them.

    `twin/honest_build.py`'s own `validate_inventory()`/`validate_owning_tickets()` do the actual
    work; this guard exists so a `CAPABILITY_INVENTORY` entry that quietly drifted from the files
    it cites (a renamed module, a threshold dropped from skill-thresholds.yaml, a kind that
    contradicts its own `reproducible_from_pins` flag) fails the standing suite rather than only a
    test a future ticket might not think to run.
    """
    from .. import honest_build

    honest_build.validate_inventory()
    honest_build.validate_owning_tickets()
    kinds = honest_build.inventory_summary()
    return (
        f"{len(honest_build.CAPABILITY_INVENTORY)} capabilities classified "
        f"({len(kinds['code'])} code, {len(kinds['inherited'])} inherited, {len(kinds['skill'])} "
        f"skill); {len(honest_build.SKILL_OWNING_TICKET)} skill(s) each resolve to a real "
        "decision ticket under .scratch/twin/issues/"
    )


def _score_log_history(root: Path) -> list[str]:
    """Commits that changed the score-over-time log, newest first — the same shape
    `_manifest_history` gives the invariant manifest."""
    from .. import skills as skills_mod

    rel = skills_mod.SCORES_PATH.relative_to(root).as_posix()
    out = _git(root, "log", "--format=%H", "--", rel)
    return [line for line in (out or "").splitlines() if line]


def _score_log_at(root: Path, ref: str) -> list[str] | None:
    """Every non-blank line the score-over-time log carried at `ref`, or `None` if it did not
    exist there yet."""
    from .. import skills as skills_mod

    rel = skills_mod.SCORES_PATH.relative_to(root).as_posix()
    out = _git(root, "show", f"{ref}:{rel}")
    if out is None:
        return None
    return [line for line in out.splitlines() if line.strip()]


@harness_check("skill_score_log_is_append_only", may_skip=True)
def _skill_score_log_is_append_only(ctx: Context) -> str:
    """`twin/skills.py`'s own `record_score()` docstring names this guard as already asserting
    the log's append-only discipline against git history, the identical shape
    `hash_changes_are_authorised` already gives the invariant manifest. Build ticket 56's
    coherence audit found the guard itself had never actually been built — invisible while
    `twin/skill-scores.jsonl` stayed empty, and a real gap the moment this same ticket gave the
    log its first genuine entries (`twin/record_skill_scores.py`): nothing stopped a later edit
    from silently rewriting or deleting a recorded score.

    Same two-branch shape as `hash_changes_are_authorised`: an uncommitted change is compared
    against the committed baseline directly, because in CI the checkout *is* HEAD and only the
    file's own git history — the previous committed version against the one just landed — can
    catch a violation the last commit itself made.
    """
    from .. import skills as skills_mod

    current = (
        [line for line in skills_mod.SCORES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
        if skills_mod.SCORES_PATH.is_file()
        else []
    )
    head = _score_log_at(REPO_DIR, "HEAD")

    if head is not None and head != current:
        baseline, source = head, "the committed log (uncommitted change)"
    else:
        history = _score_log_history(REPO_DIR)
        if len(history) < 2:
            raise Skip("the score-over-time log has fewer than two committed versions; nothing to compare yet")
        earlier = _score_log_at(REPO_DIR, history[1])
        if earlier is None:
            raise Skip(f"could not read the log at {history[1][:12]}")
        baseline, source = earlier, f"the previous version ({history[1][:12]})"

    if current[: len(baseline)] != baseline:
        raise Violated(
            f"a previously-committed skill-score entry was edited, reordered or removed against {source} "
            "— the log must only ever grow"
        )
    return f"{len(baseline)} line(s) against {source} unchanged; {len(current) - len(baseline)} new"


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


@harness_check("substrate_generator_is_mundane_by_default_and_records_measurability_winning")
def _substrate_generator_is_mundane_by_default(ctx: Context) -> str:
    """`substrate-generator` (build ticket 49, decision ticket 12 Q1/Q4): the fifth of the six
    skills seam 3 exists to evaluate — regeneration from a pinned recipe is reproducible
    (ticket 48's own mechanics, reused rather than reinvented), the output stays mostly mundane
    even at its plant-count ceiling, and the believability/measurability conflict the ticket's own
    checklist names is resolved in the artefact rather than only in prose.

    A guard on the suite rather than an invariant, the same shape
    `gameplay_lens_is_grade_5_and_reports_no_recommendation` is: this asserts **structural
    properties of a module's contract**, not one of the constitution's sixteen fixed names.

    Four legs. First, regenerating a batch from the identical recipe reproduces byte-for-byte —
    `generate()` draws no entropy `random.Random(recipe.seed)` and `generate_deterministic`
    (ticket 48) do not already pin. Second, a batch scheduling one plant per channel — the
    structural ceiling `SubstrateGeneratorError` enforces — still clears `MIN_MUNDANE_FRACTION`.
    Third, the recorded `resolution` names measurability winning over believability, checked
    against real output rather than trusted from the module docstring. Fourth, the real labelled
    corpus (the same three recipes `tests/test_substrate_generator.py` evaluates against, built
    fresh here) passes end to end and a generator that emits nothing fails the threshold — a
    harness with no subject proves nothing.
    """
    from .. import skills as skills_mod
    from .. import substrate_generator as sg
    from ..substrate import SubstrateRecipe

    recipe = SubstrateRecipe(
        id="guard-recipe", seed=99,
        templates=(
            "Lunch order chat in #ops.", "A long thread about the staging environment.",
            "Expense report chasing.", "Sprint planning grumbling.",
        ),
        model_version="toy-model-v1",
        planted_signals=("a", "b", "c", "d"),
    )
    first = sg.generate(recipe)
    second = sg.generate(recipe)
    if first != second:
        raise Violated("regenerating from the identical recipe did not reproduce byte-for-byte")

    if len(first["plants"]) != len(sg.CHANNELS):
        raise Violated(f"a plant-per-channel recipe scheduled {len(first['plants'])} plant(s), not {len(sg.CHANNELS)}")
    if sg.mundane_fraction(first) < sg.MIN_MUNDANE_FRACTION:
        raise Violated(
            f"a batch at the plant-count ceiling scored mundane_fraction={sg.mundane_fraction(first)}, "
            f"below the floor {sg.MIN_MUNDANE_FRACTION}"
        )

    resolution = first["resolution"].lower()
    if "measurability" not in resolution or "believ" not in resolution:
        raise Violated(f"the recorded resolution does not name measurability winning over believability: {first['resolution']!r}")

    corpus = sg.labelled_corpus()
    good = skills_mod.evaluate(sg.SKILL, sg.generate_from_recipe_yaml, corpus, scorer=sg.scorer)
    if not good.passed:
        raise Violated("substrate-generator failed its own labelled corpus running correctly — the harness has no subject")
    bad = skills_mod.evaluate(
        sg.SKILL, lambda text: {"channels": {}, "plants": [], "resolution": ""}, corpus, scorer=sg.scorer,
    )
    if bad.passed:
        raise Violated("a generator that emits nothing still passed — the threshold is not gating anything")

    return (
        "regenerating from the identical recipe reproduces byte-for-byte; a plant-per-channel "
        f"batch still clears mundane_fraction >= {sg.MIN_MUNDANE_FRACTION}; the resolution names "
        f"measurability winning; the real {len(corpus)}-item labelled corpus passes and a silent "
        "generator fails its threshold"
    )


@harness_check("ingest_runs_unattended_with_provenance_and_measured_throughput")
def _ingest_runs_unattended_with_provenance_and_measured_throughput(ctx: Context) -> str:
    """`twin/ingest.py` (build ticket 53, decision ticket 11 Q2): binding runs fully automated
    *at throughput* — no human gate at entry, every item provenanced, and the throughput actually
    achieved is measured rather than assumed. The same two-leg shape
    `signal_classify_is_grade_5_by_construction` uses, applied to the pipeline that calls the
    skill at volume rather than to the skill alone.

    Two legs. Structural: `ingest_run`'s own source calls `signal_classify.classify` directly, in
    a loop, with nothing resembling a confirmation, review or approval step in its call graph —
    checked against the source text itself, the same discipline
    `skill_eval_harness_is_agnostic_and_thresholds_are_guarded` uses to keep a harness honest
    about what it does not call. Live: a real run against the default fixture's `netflix`
    overlay, at a declared volume, actually classifies every item — each carrying `provenance`
    naming the substrate blob, the recipe and its own index — stays grade 5 throughout (the
    downstream gate this ticket's "no gate at entry" argument rests on), and reports a measured
    `items_per_second` computed from wall-clock elapsed time rather than a hardcoded figure.
    """
    import inspect

    from .. import ingest as ingest_mod
    from ..repo import ModelRepo
    from ..substrate import SubstrateRecipe

    source = inspect.getsource(ingest_mod.ingest_run)
    for banned in ("input(", "approve", "review", "sign.human", "confirm"):
        if banned in source:
            raise Violated(f"ingest_run's own source contains {banned!r} — a human gate may exist at entry")

    recipe = SubstrateRecipe(
        id="harness-guard-recipe",
        seed=11,
        templates=(
            "A trading update describes deteriorating margins in the core business.",
            "An industry report flags rising input costs across the sector.",
        ),
        model_version="toy-model-v1",
    )
    repo = ModelRepo.open(ctx.repo_dir)
    declared_count = 60
    artefact = ingest_mod.ingest_run(repo, ctx.caps, "netflix", recipe, declared_count, ["twin", "ingest"])
    body = artefact.body

    accounted_for = len(body["items"]) + len(body["failures"])
    if accounted_for != declared_count:
        raise Violated(f"declared {declared_count} item(s), accounted for {accounted_for}")
    if not body["items"]:
        raise Violated("no item was actually classified — the pipeline has no subject")
    for item in body["items"]:
        if item["claim"]["evidence_grade"] != 5:
            raise Violated(f"an ingested item carries evidence_grade {item['claim']['evidence_grade']!r}, not 5")
        provenance = item.get("provenance", {})
        if not {"substrate", "recipe", "index"} <= provenance.keys():
            raise Violated(f"an ingested item carries incomplete provenance: {provenance}")

    throughput = body["throughput"]
    if throughput["elapsed_seconds"] <= 0 or not throughput["items_per_second"]:
        raise Violated(f"throughput was not actually measured: {throughput}")

    return (
        "ingest_run's own source calls no confirmation/review/approval step; "
        f"{len(body['items'])} of {declared_count} declared item(s) classified at grade 5, each "
        f"carrying full provenance, measured at {throughput['items_per_second']:.1f} items/sec"
    )


@harness_check("unbound_pool_retains_a_decayed_signal_rather_than_dropping_it")
def _unbound_pool_retains_decayed_signals(ctx: Context) -> str:
    """`twin/unbound_pool.py` (build ticket 54, decision ticket 11 Q3): a signal the graph cannot
    yet interpret is retained with decay, never discarded — plain decay-to-zero would be
    indistinguishable from the deletion Q3 explicitly rejects unless a decayed-out signal stays
    visible in the pool's own report rather than quietly ceasing to be listed.

    Two legs, both against the default fixture's `netflix` overlay (its own signal collection is
    mutated in memory only — nothing here is committed, the same throwaway-input shape
    `signal_classify_is_grade_5_by_construction` uses for its synthetic sample). Live: a signal
    planted ten years before the declared time — comfortably past the published threshold at any
    sane half-life — is still present in `pool()`'s own output, `decayed: true`, carrying a
    computed `decayed_on` date: not absent, not silently dropped. Structural: the observable
    `pool_size`/`age_distribution` a reader actually watches excludes it, so "recorded" and
    "still counted as live" are demonstrably two different properties rather than one field doing
    both jobs.
    """
    from .. import unbound_pool
    from ..model import Overlay
    from ..repo import ModelRepo

    overlay = Overlay.load(ModelRepo.open(ctx.repo_dir), "netflix")
    ancient_id = "harness-guard-ancient-signal"
    overlay.signals[ancient_id] = {
        "id": ancient_id,
        "date": "2000-01-01",
        "steep": "technological",
        "source": "harness guard",
        "statement": "planted directly, never committed — a decayed-out signal must not vanish",
        "provenance": {},
    }

    entries = unbound_pool.pool(overlay, "2026-01-01")
    planted = next((e for e in entries if e["id"] == ancient_id), None)
    if planted is None:
        raise Violated("a decayed-out signal is absent from pool()'s own report — silently dropped")
    if not planted["decayed"]:
        raise Violated(f"a signal aged {planted['age_days']} days did not cross the decay threshold")
    if not planted.get("decayed_on"):
        raise Violated("a decayed signal carries no decayed_on date")

    live_count = sum(1 for e in entries if not e["decayed"])
    reported = unbound_pool.age_distribution(entries)
    if sum(reported.values()) != live_count:
        raise Violated("age_distribution counts do not match the live (non-decayed) pool")
    if planted["id"] in {e["id"] for e in entries if not e["decayed"]}:
        raise Violated("a decayed signal is still counted as live")

    return (
        f"a signal {planted['age_days']} days old stays in the pool report (decayed: true, "
        f"decayed_on {planted['decayed_on']}) rather than being dropped, and is excluded from "
        "the observable live pool_size/age_distribution rather than double-counted"
    )


@harness_check("retrospective_sweep_rescues_a_decayed_signal_when_a_model_change_binds_it")
def _retrospective_sweep_rescues_a_decayed_signal(ctx: Context) -> str:
    """`twin/retrospective_sweep.py` (build ticket 55, decision ticket 11 Q3): a model change — a
    new component sharing the signal's own vocabulary, standing in for "adding a component,
    dependency or causal edge" — rescues a signal out of the unbound pool even after it has
    decayed. That is the whole point of the rescue path: plain decay alone would preferentially
    delete the longest-lead-time signals, exactly the ones a rescue mechanism exists to catch.

    Two legs, both against the default fixture's `netflix` overlay (mutated in memory only, the
    same throwaway-input shape `unbound_pool_retains_a_decayed_signal_rather_than_dropping_it`
    uses). Before: a signal planted 1000 days before the declared time — comfortably past
    `twin/decay.yaml`'s own threshold — whose statement shares no vocabulary with any of the
    seven netflix/world candidates, sweeps to `still_unbound`. After: the identical signal, swept
    against an overlay that also carries one new component sharing its own vocabulary, sweeps to
    `rebound` — `had_decayed_before_rescue` true and `lead_time_to_recognition_days` equal to its
    full age — proving decay is recorded on the way through, never a barrier to rescue.
    """
    from .. import retrospective_sweep
    from ..model import Overlay
    from ..repo import ModelRepo

    signal_id = "harness-guard-quantum-signal"
    signal_date = "2023-06-01"
    at = "2026-01-01"
    signal_doc = {
        "id": signal_id,
        "date": signal_date,
        "steep": "technological",
        "source": "harness guard: an obscure materials-science preprint",
        "statement": "planted directly, never committed — a graphene-composite radiation shielding advance nothing yet reads",
        "provenance": {},
    }

    before = Overlay.load(ModelRepo.open(ctx.repo_dir), "netflix")
    before.signals[signal_id] = signal_doc
    before_result = retrospective_sweep.sweep(before, at)
    if signal_id not in {e["id"] for e in before_result["still_unbound"]}:
        raise Violated("a signal with no matching component did not sweep to still_unbound")
    if signal_id in {e["id"] for e in before_result["rebound"]}:
        raise Violated("a signal with no matching component in the graph rebound anyway")

    after = Overlay.load(ModelRepo.open(ctx.repo_dir), "netflix")
    after.signals[signal_id] = signal_doc
    after.components["graphene-composite-shielding"] = {
        "id": "graphene-composite-shielding",
        "name": "Graphene-composite radiation shielding",
        "kind": "capability",
    }
    after_result = retrospective_sweep.sweep(after, at)
    rebound = {e["id"]: e for e in after_result["rebound"]}
    if signal_id not in rebound:
        raise Violated("adding a matching component did not rescue the signal")
    entry = rebound[signal_id]
    if not entry["had_decayed_before_rescue"]:
        raise Violated("the harness guard's own planted signal was not actually decayed before rescue")
    if entry["lead_time_to_recognition_days"] <= 0:
        raise Violated(f"lead_time_to_recognition_days was not positive: {entry['lead_time_to_recognition_days']}")
    if entry["component"] != "graphene-composite-shielding":
        raise Violated(f"rescued onto the wrong component: {entry['component']!r}")

    return (
        f"a signal {entry['lead_time_to_recognition_days']} days old (decayed before rescue: true) "
        "stays still_unbound with no matching component, and rebinds the moment a model change adds one"
    )


@harness_check("substrate_reconciles_with_the_spine_and_the_diff_attack_finds_no_plants")
def _substrate_reconciles_with_the_spine_and_the_diff_attack_finds_no_plants(ctx: Context) -> str:
    """Spine anchoring and free-running (build ticket 50, decision ticket 12 Q3): the substrate
    must never contradict a dated public fact, but is free wherever the record is silent — and the
    concrete danger decision ticket 12 names is over-anchoring: a substrate derived entirely from
    the spine except for its plants would let a diff against the spine locate every one.

    A guard on the suite rather than an invariant, the same shape
    `substrate_generator_is_mundane_by_default_and_records_measurability_winning` is: this asserts
    a **structural property of a module's contract**, not one of the constitution's sixteen fixed
    names.

    Four legs, on the real Carillion answer key (build ticket 38) rather than an invented spine —
    `Spine.from_overlay` reads the org's own 8 real, dated, cited signals directly. First, a
    substrate batch missing the spine's facts fails `reconcile()`, naming what is absent. Second,
    once `anchor()` has inserted them, `reconcile_at_every_checkpoint()` — one reconciliation per
    distinct spine date, not only the last — passes at every one of the 8. Third, knowability
    dates genuinely gate through `twin/regimes.py`'s own machinery: a malformed checkpoint fails
    with `regimes.RegimeError`, the identical exception every other regime-gated read raises, not
    a parallel parser that happens to agree with it today. Fourth, the diff attack itself: a
    substrate batch carrying one planted signal, anchored against the real spine, still leaves the
    plant inside a `free_running` residual dozens of lines wide — the diff alone does not single
    it out — while a batch built the forbidden way (nothing free-running but the plant) leaves the
    plant as the *entire* residual, so the guard is proven to measure a real property rather than
    passing on every input.
    """
    from .. import fixtures
    from ..model import Overlay
    from ..regimes import RegimeError, cutoff
    from ..repo import ModelRepo
    from ..spine import Spine, SpineError, anchor, diff_against_spine, reconcile, reconcile_at_every_checkpoint
    from ..substrate import SubstrateRecipe
    from ..substrate_generator import generate

    carillion_dir = ctx.tmp / "carillion-repo"
    if not carillion_dir.exists():
        fixtures.build_carillion_org(carillion_dir)
    overlay = Overlay.load(ModelRepo.open(carillion_dir), fixtures.CARILLION_ORG)
    spine = Spine.from_overlay(overlay)
    if len(spine.facts) < 3:
        raise Violated(f"the Carillion spine carries only {len(spine.facts)} fact(s) — too thin to guard with")

    recipe = SubstrateRecipe(
        id="spine-guard-recipe", seed=13,
        templates=(
            "Lunch order chat in #ops.", "A long thread about the staging environment.",
            "Expense report chasing.", "Sprint planning grumbling.",
        ),
        model_version="toy-model-v1",
        planted_signals=("a director's calendar clears for three unexplained days",),
    )
    batch = generate(recipe)
    checkpoint = max(f.date for f in spine.facts)

    try:
        reconcile(batch, spine, checkpoint)
    except SpineError:
        pass
    else:
        raise Violated("reconcile() passed on a batch that never had the spine anchored into it")

    anchored_batch = anchor(batch, spine, checkpoint)
    reports = reconcile_at_every_checkpoint(anchored_batch, spine)
    if [r["checkpoint"] for r in reports] != sorted({f.date for f in spine.facts}):
        raise Violated("reconcile_at_every_checkpoint did not run once per distinct spine date, in order")
    if reports[-1]["reconciled"] != sorted(f.id for f in spine.facts):
        raise Violated("the final checkpoint did not reconcile every spine fact")

    try:
        cutoff("2018-01-15T00:00:00Z")
    except RegimeError:
        pass
    else:
        raise Violated("cutoff() accepted a non-YYYY-MM-DD checkpoint")
    try:
        spine.at("2018-01-15T00:00:00Z")
    except RegimeError:
        pass
    else:
        raise Violated("Spine.at() did not route its checkpoint through regimes.cutoff()")

    plant_line = f"[{batch['focus_entity']}] {batch['plants'][0]['signal']}"
    diff = diff_against_spine(anchored_batch, spine)
    if plant_line not in diff["free_running"]:
        raise Violated("the planted signal did not survive as free-running content")
    decoys = len(diff["free_running"]) - 1
    if decoys < 10:
        raise Violated(f"only {decoys} non-plant decoy(s) sit beside the plant in free_running — the diff attack would work")

    over_anchored = {"channels": {"events": [f.statement for f in spine.facts] + [plant_line]}}
    rigged = diff_against_spine(over_anchored, spine)
    if rigged["free_running"] != [plant_line]:
        raise Violated("the over-anchored negative control did not expose the plant as the sole residual — this guard proves nothing")

    return (
        f"a batch missing the {len(spine.facts)}-fact real Carillion spine fails reconcile(); once "
        "anchored it reconciles at every one of the spine's own dated checkpoints; a malformed "
        "checkpoint fails through regimes.RegimeError, not a parallel parser; the diff attack "
        f"leaves the plant beside {decoys} non-plant decoy(s), while an over-anchored control "
        "exposes it as the sole residual"
    )


@harness_check("substrate_fidelity_is_measured_and_tuning_closes_a_real_gap")
def _substrate_fidelity_is_measured_and_tuning_closes_a_real_gap(ctx: Context) -> str:
    """The substrate fidelity eval suite (build tickets 51, 87; decision ticket 12): fidelity is
    *defined and tuned by measurement*, not asserted in prose — seven declared, targeted
    dimensions (signal-to-noise, plant difficulty, plant-difficulty spread, spine consistency,
    reporting asymmetry, mundanity, contamination), a real tuning loop that closes a genuine gap
    rather than one built to pass on the first call, and negativity bias measured as the same
    property as reporting asymmetry (decision ticket 12 Q3c, spec story 60).

    A guard on the suite rather than an invariant, the same shape
    `substrate_reconciles_with_the_spine_and_the_diff_attack_finds_no_plants` is: this asserts
    **structural and live properties of a module's contract**, not one of the constitution's
    sixteen fixed names.

    Five legs, on the real Carillion spine (build ticket 38) `spine.py`'s own guard already
    builds from. First, `evaluate_fidelity()` returns exactly the declared dimensions named in
    `TARGETS`, each carrying its own declared target band — checked against real output, not
    trusted from the module docstring. Second, the real gap `tune()` exists to close: a balanced
    (50/50) template mix genuinely misses the `reporting_asymmetry` target — not a strawman built
    to fail. Third, `tune()` converges over more than one iteration to a batch that clears every
    band at once — a real loop, not a single call that happens to pass. Fourth, the converged
    batch's own `reporting_asymmetry` sits above 0.5: the negativity bias is *produced*, matching
    the record's real skew, not merely inside an arbitrary band centred on balance. Fifth, the
    suite has teeth: a degraded batch (balanced polarity, un-camouflaged plant wording) fails
    `passes()` on more than one dimension — a harness with no subject proves nothing.
    """
    from .. import fixtures
    from ..model import Overlay
    from ..repo import ModelRepo
    from ..spine import Spine
    from .. import substrate_eval as se

    carillion_dir = ctx.tmp / "carillion-repo"
    if not carillion_dir.exists():
        fixtures.build_carillion_org(carillion_dir)
    overlay = Overlay.load(ModelRepo.open(carillion_dir), fixtures.CARILLION_ORG)
    spine = Spine.from_overlay(overlay)
    checkpoint = max(f.date for f in spine.facts)

    tuned_batch = se.generate(se._recipe_for(0.6, se.PLANTED_SIGNALS, seed=42))
    metrics = se.evaluate_fidelity(tuned_batch, spine, checkpoint)
    if {m.name for m in metrics} != set(se.TARGETS):
        raise Violated(f"evaluate_fidelity() did not return exactly the {len(se.TARGETS)} declared dimensions: {[m.name for m in metrics]}")

    balanced_batch = se.generate(se._recipe_for(0.5, se.PLANTED_SIGNALS, seed=42))
    balanced_metrics = {m.name: m for m in se.evaluate_fidelity(balanced_batch, spine, checkpoint)}
    if balanced_metrics["reporting_asymmetry"].within_target:
        raise Violated("a balanced 50/50 template mix passed reporting_asymmetry — the tuning loop has no real gap to close")

    result = se.tune(spine, checkpoint)
    if not result.converged:
        raise Violated(f"tune() did not converge within its own default budget: {result.iterations} iteration(s)")
    if result.iterations <= 1:
        raise Violated("tune() converged on its first step — not a loop closing a real gap")
    if not se.passes(result.final.metrics):
        raise Violated(f"tune() reported converged but its final step does not pass: {[m.as_dict() for m in result.final.metrics]}")

    final_asymmetry = next(m.value for m in result.final.metrics if m.name == "reporting_asymmetry")
    if final_asymmetry <= 0.5:
        raise Violated(f"the tuned batch's reporting_asymmetry ({final_asymmetry}) does not skew negative — the bias was not produced")

    degraded = se.generate(se._recipe_for(0.5, se.UNCAMOUFLAGED_PLANTED_SIGNALS, seed=42))
    degraded_metrics = se.evaluate_fidelity(degraded, spine, checkpoint)
    if se.passes(degraded_metrics):
        raise Violated("a degraded (balanced, un-camouflaged) batch passed the full suite — it is not gating anything")
    failing = {m.name for m in degraded_metrics if not m.within_target}
    if len(failing) < 2:
        raise Violated(f"the degraded batch failed only {failing} — expected more than one dimension to catch it")

    return (
        f"evaluate_fidelity() returns exactly the {len(se.TARGETS)} declared dimensions; a balanced 50/50 mix "
        f"genuinely misses reporting_asymmetry; tune() converges in {result.iterations} iteration(s) "
        f"to a batch passing every band, with reporting_asymmetry={final_asymmetry} skewing negative; "
        f"a degraded batch fails {len(failing)} dimension(s) at once ({', '.join(sorted(failing))})"
    )


@harness_check("planter_detector_scorer_are_structurally_separated_and_late_detection_scores_near_zero")
def _planter_detector_scorer_are_structurally_separated(ctx: Context) -> str:
    """The planter/detector/scorer split (build ticket 52, decision ticket 12 AC 4, Q2, Q3b):
    "a planter agent holds ground truth in a sealed artefact; a detector agent runs with no access
    to it and no shared context; a scorer reads both" — and every plant carries an actionability
    horizon so a late detection scores as the near-zero option value it actually is.

    A guard on the suite rather than an invariant, the same shape the other three substrate-chain
    guards are: this asserts structural and behavioural properties of three modules' contracts,
    not one of the constitution's sixteen fixed names.

    Five legs. First, `twin/detector.py` imports nothing naming `planter` — an AST scan of its own
    real source, not a promise in a docstring. Second, `detector.detect()` is behaviourally blind
    to ground truth, not merely unwired to it: called on the planter's real public view and on an
    identical dict with a decoy `plants` key spliced in (the exact key `planter.PlantedWorld.public`
    never carries), it returns byte-identical output either way — it does not even look. Third, a
    plant detected on or before its own actionability horizon scores `TIMELY_SCORE`. Fourth, the
    identical plant detected one day after its own horizon scores `LATE_SCORE` — near zero, not
    zero — and the reason string names the horizon and says why. Fifth, every `ScoreResult` carries
    the shared-prior limitation verbatim, the limit decision ticket 12 Q2 records rather than
    papers over: a synthetic result evidences detection mechanics only, never anticipation of the
    world.
    """
    import ast
    import inspect

    from .. import detector as detector_mod
    from .. import planter as planter_mod
    from .. import scorer as scorer_mod
    from ..substrate import SubstrateRecipe

    detector_source = inspect.getsource(detector_mod)
    tree = ast.parse(detector_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""] + [a.name for a in node.names]
        else:
            continue
        if any("planter" in n for n in names):
            raise Violated(f"twin/detector.py imports something naming 'planter': {names}")

    signal = "an unusual incident review opens after hours, examining finance access"
    recipe = SubstrateRecipe(
        id="pds-guard-recipe", seed=7,
        templates=(
            "Lunch order chat in #ops.", "A long thread about the staging environment.",
            "Expense report chasing.", "Sprint planning grumbling.",
        ),
        model_version="toy-model-v1", planted_signals=(signal,),
    )
    world = planter_mod.plant(recipe, horizons={signal: "2018-06-01"}, strengths={signal: 0.6})
    if "plants" in world.public:
        raise Violated("PlantedWorld.public still carries the 'plants' key — ground truth leaked to the detector")

    honest = detector_mod.detect(world.public)
    decoy_public = {
        **world.public,
        "plants": [{"channel": "events", "index": 0, "signal": "not the real ground truth"}],
    }
    tampered = detector_mod.detect(decoy_public)
    if honest != tampered:
        raise Violated(
            "detect() produced different output when a decoy 'plants' key was present — it is "
            "reading ground truth it should never see"
        )

    p = world.ground_truth[0]
    on_target_detection = (detector_mod.Detection(channel=p.channel, index=p.index, line=p.signal, outlier_score=0.0),)

    timely = scorer_mod.score(world.ground_truth, on_target_detection, detected_at="2018-05-01")
    if timely.plant_scores[0].score != scorer_mod.TIMELY_SCORE or not timely.plant_scores[0].timely:
        raise Violated("a detection before the actionability horizon did not score as timely")

    late = scorer_mod.score(world.ground_truth, on_target_detection, detected_at="2018-06-02")
    late_ps = late.plant_scores[0]
    if late_ps.timely is not False or late_ps.score != scorer_mod.LATE_SCORE or late_ps.score >= 0.1:
        raise Violated(f"a detection after the actionability horizon did not score near zero: {late_ps}")
    if "2018-06-01" not in late_ps.reason or "horizon" not in late_ps.reason.lower():
        raise Violated(f"the late score's reason does not name the horizon it missed: {late_ps.reason!r}")

    missed = scorer_mod.score(world.ground_truth, (), detected_at="2018-05-01")
    if missed.plant_scores[0].score != scorer_mod.MISSED_SCORE or missed.plant_scores[0].detected:
        raise Violated("an undetected plant did not score as missed")

    for result in (timely, late, missed):
        if result.limitation != planter_mod.SHARED_PRIOR_LIMITATION:
            raise Violated("a ScoreResult did not carry the shared-prior limitation verbatim")

    return (
        "twin/detector.py imports nothing naming 'planter'; detect() returns identical output "
        "with and without a decoy ground-truth key present; a plant detected before its "
        f"actionability horizon scores {scorer_mod.TIMELY_SCORE}, the identical plant detected "
        f"after it scores {late_ps.score} with the horizon named in the reason, and a missed plant "
        f"scores {scorer_mod.MISSED_SCORE}; every result carries the shared-prior limitation verbatim"
    )


@harness_check("netflix_substrate_is_free_running_and_every_plant_carries_a_horizon")
def _netflix_substrate_is_free_running_and_every_plant_carries_a_horizon(ctx: Context) -> str:
    """The Netflix substrate as a whole (build ticket 73, decision ticket 12 Q3, Q3b): the
    committed recipe against the committed spine, on the real subject rather than a guard-local
    stand-in.

    A guard on the suite rather than an invariant, the same shape the other four substrate-chain
    guards are. It differs from them in what it runs on: they assert module contracts against
    recipes they build themselves, and this one asserts that the **committed content** — a real
    recipe and a real six-filing spine, both in git — actually holds those contracts. A mechanism
    that works on its own fixtures and fails on the subject it shipped for is the failure this
    guard exists to catch.

    Five legs. First, free-running: not one generated line restates a spine fact, so the diff
    against the spine has no anchored residual to subtract and the plants stay buried among
    dozens of decoys (decision ticket 12 Q3). Second, every plant carries a declared actionability
    horizon and a reason, read from the committed `twin/plant-horizons.yaml` — `plant()` refuses
    the recipe otherwise, so this leg is what stops that refusal from being the shipped state.
    Third, drift between the two committed documents is refused in the direction `plant()` does
    not cover: a horizons file naming a signal the recipe never plants is a stale seal, and it
    fails rather than reads as covering a plant that is gone. Fourth, every fidelity dimension
    lands inside its declared band on the real subject. Fifth, the report is emitted, reproduces
    byte-for-byte from identical pins, and carries a row for **every** plant including the ones
    nothing detected — a report that dropped its misses would publish a hit rate over a
    denominator it had quietly shrunk.
    """
    from .. import planter as planter_mod, substrate_report
    from ..model import Overlay
    from ..planter import PlanterError
    from ..repo import ModelRepo
    from ..spine import Spine, diff_against_spine
    from ..substrate import SubstrateRecipe
    from ..substrate_eval import evaluate_fidelity
    from ..substrate_generator import generate
    from ..verbs import command_for

    checkpoint = "2011-10-24"
    recipe_path = PACKAGE_DIR / "netflix-substrate-recipe.yaml"
    recipe = SubstrateRecipe.from_yaml(recipe_path.read_text(encoding="utf-8"))

    netflix_dir = ctx.tmp / "netflix-repo"
    if not netflix_dir.exists():
        fixtures.build_netflix_org(netflix_dir)
    overlay = Overlay.load(ModelRepo.open(netflix_dir), "netflix")
    spine = Spine.from_overlay(overlay)

    batch = generate(recipe)
    split = diff_against_spine(batch, spine)
    if split["anchored"]:
        raise Violated(
            f"{len(split['anchored'])} generated line(s) restate a spine fact — the substrate is "
            "anchored where it should be free-running, and a diff against the spine narrows the "
            "search for the plants"
        )

    dates, reasons, strengths = planter_mod.horizons_for(recipe)
    missing = [
        s for s in recipe.planted_signals if s not in dates or not reasons.get(s) or s not in strengths
    ]
    if missing:
        raise Violated(f"{len(missing)} committed plant(s) carry no declared horizon, reason or strength: {missing}")

    drifted = ctx.tmp / "drifted-horizons.yaml"
    drifted.write_text(
        "schema: twin.plant-horizons/v1\nrecipes:\n"
        f"  {recipe.id}:\n    - signal: a signal this recipe never plants\n"
        "      horizon: '2011-09-30'\n      reason: a stale seal\n",
        encoding="utf-8",
    )
    try:
        planter_mod.horizons_for(recipe, path=drifted)
    except PlanterError:
        pass
    else:
        raise Violated("a horizons document naming a signal the recipe never plants was accepted")

    metrics = evaluate_fidelity(batch, spine, checkpoint)
    outside = [m.name for m in metrics if not m.within_target]
    if outside:
        raise Violated(f"the committed Netflix substrate falls outside its declared band(s): {outside}")

    command = command_for(
        "substrate", org="netflix", checkpoint=checkpoint, detected_at=checkpoint,
        recipe=recipe_path.name,
    )
    first = substrate_report.report(
        ModelRepo.open(netflix_dir), ctx.caps, "netflix", recipe_path, checkpoint, checkpoint, command
    )
    second = substrate_report.report(
        ModelRepo.open(netflix_dir), ctx.caps, "netflix", recipe_path, checkpoint, checkpoint, command
    )
    if first.to_bytes() != second.to_bytes():
        raise Violated("two substrate reports from identical pins are not byte-identical")

    reported = first.body["detection"]["plants"]
    if len(reported) != len(recipe.planted_signals):
        raise Violated(
            f"the report carries {len(reported)} plant row(s) for {len(recipe.planted_signals)} "
            "planted signal(s) — a miss was dropped rather than scored"
        )
    if not any(not row["detected"] for row in reported):
        raise Violated(
            "no plant is reported as missed; this guard is asserted against a report that keeps "
            "its misses, and one with none proves nothing about whether it would"
        )
    if first.body["detection"]["limitation"] != planter_mod.SHARED_PRIOR_LIMITATION:
        raise Violated("the report does not carry the shared-prior limitation verbatim")

    hit_rate = first.body["detection"]["hit_rate"]
    return (
        f"the committed Netflix recipe restates none of the spine's {len(spine.facts)} facts; all "
        f"{len(recipe.planted_signals)} plants carry a declared horizon and reason, and a horizons "
        "file drifted from the recipe is refused; every fidelity dimension is inside its band at "
        f"{checkpoint}; the report reproduces byte-for-byte and scores every plant, misses "
        f"included, at a hit rate of {hit_rate}"
    )


@harness_check("netflix_runs_both_paths_and_the_curve_keeps_the_disagreement")
def _netflix_runs_both_paths_and_the_curve_keeps_the_disagreement(ctx: Context) -> str:
    """The whole-engine beat, on the committed subject (build ticket 74, decision ticket 22).

    A guard on the suite rather than an invariant, and the sibling of build ticket 73's
    `netflix_substrate_is_free_running_and_every_plant_carries_a_horizon`: that one asserts the
    committed *content* holds the substrate contracts, this one asserts the committed content
    actually drives the engine.

    **Black-box at seam 1, deliberately, with one seam-2 exception named below.** Adversarial
    review of the first draft found it drove `verbs.run`/`verbs.price`/`verbs.trade_off` directly
    — a call sequence, which the constitution scopes to seam 2 ("numerical and structural
    properties only, never call sequences") and its own sibling guard,
    `a_scored_forecast_is_never_silently_dropped`, already gets right. Every leg below drives
    `cli.main` and reads the artefact it wrote, the same way `twin/beat-netflix.sh` does, so
    renaming or reordering an internal verb function cannot leave this green while the CLI itself
    is broken.

    **One dated state, two directions, independently resolved.** `twin backtest --at` and `twin
    rewind --at` are two separate CLI invocations, each resolving 2011-08-01 on its own — the same
    shape the beat script's own steps 1 and 2 are. The first draft instead opened one rewound repo
    once and handed it to both paths, so the pin comparison it ran could only ever agree with
    itself; here the two resolutions are genuinely independent and are asserted against each
    other, which would catch `cmd_backtest`'s internal rewind ever diverging from `cmd_rewind`'s.

    **The cut is real, not narrated.** At 2011-08-01, `twin options` for `the-operator` fails —
    the perspective rests on a filing that did not exist yet — and the rewound state's own
    `rollups.causal_edges` is zero. Both read from artefacts the CLI emits, not from an `Overlay`
    reached into directly.

    **The comparison is cross-domain, direction-named, and the refusal survives it.** The lever
    (`hold-the-bundled-price-for-one-quarter`) earns mitigation credit; the control
    (`ship-one-bill-and-one-sign-in-across-the-two-plans`) is refused credit with a reason, never
    given a zero. Named by id rather than "some response earned nothing", so swapping the two
    responses' evidence grades — inverting the beat's own argument — fails here rather than
    passing because *a* refusal still exists.

    **The curve keeps the disagreement, and the refused option's own figure never moves.** The
    three accounts disagree about which response is cheapest — asserted on `cheapest_by_account`,
    so a re-authored cost that preserves the flip still passes and one that collapses it does not
    — and the control's `net_cost_of_risk.range` is zero across all three, because nothing here
    ever credits it regardless of which account is asked.

    **No account is privileged — asserted directly on the propagation maths, not through the CLI.**
    This is the one deliberate seam-2 leg: `tradeoff.curve()` called on one hoisted overlay, the
    same function `tests/test_tradeoff.py` already exercises. Three extra `twin trade-off`
    invocations here would pay ~1.6s to re-derive an overlay that has not changed in order to
    re-check a property that is purely about `net_cost_of_risk` arithmetic, never about CLI
    wiring — exactly the "numerical and structural properties only" seam 2 exists for, so this leg
    stays there rather than moving to seam 1 for uniformity's own sake.

    **Versioned enactment is proposed, on the lever, through the channel it is not code.**
    `twin propose --channel record` on the lever, not the control — the beat found and fixed a
    defect where its own script proposed the code control through the not-code channel.

    **The shared-prior limitation is paired with the capability, over every artefact the beat
    actually emits.** Ticket 73 asserted one report carries it; this asserts the pairing over all
    eight — backtest, rewind, gameplay-sweep, options, price, trade-off, propose and substrate —
    not the three the first draft happened to have already built for other reasons. Adversarial
    review proved the gap by adding `synthetic-substrate` to `CAPS_PRICE` and watching the old,
    narrower walk pass anyway.
    """
    import json

    from ..cli import main as cli_main

    org, at, checkpoint = "netflix", "2011-08-01", "2011-10-24"
    origin, perspective_id = "dvd-by-mail", "the-operator"
    lever_id = "hold-the-bundled-price-for-one-quarter"
    control_id = "ship-one-bill-and-one-sign-in-across-the-two-plans"
    accounts = [
        "the-shock-stayed-on-the-dvd-side",
        "the-shock-crossed-to-the-streaming-side",
        "the-damage-was-mostly-the-rebrand",
    ]

    # Deliberately its own directory name, `netflix-repo-corroborated` rather than the plain
    # `netflix-repo` build ticket 73's sibling guard
    # (`netflix_substrate_is_free_running_and_every_plant_carries_a_horizon`) already caches at —
    # both guards share one `ctx.tmp` for the whole suite run, and that guard's own spine-fidelity
    # assertions need the org build ticket 86 must NOT touch, so the two builds cannot share a
    # cache key now that one of them means something different from the other.
    netflix_dir = ctx.tmp / "netflix-repo-corroborated"
    if not netflix_dir.exists():
        # `build_and_corroborate_netflix_org`, not `build_netflix_org`: the lever needs
        # corroborated enactment to keep earning mitigation credit under the new gate (build
        # ticket 86) — the same wrapper `twin fixture --name netflix` registers.
        fixtures.build_and_corroborate_netflix_org(netflix_dir)
    out = ctx.tmp / "netflix-engine-guard"
    out.mkdir(exist_ok=True)

    def run(args: list[str], outfile: str) -> dict:
        path = out / outfile
        rc = cli_main([*args, "--out", str(path)])
        if rc != 0:
            raise Violated(f"`twin {' '.join(args)}` exited {rc}")
        return json.loads(path.read_bytes())

    # -- one dated state, two directions, independently resolved --------------------------------
    threat = run(
        ["backtest", "--repo", str(netflix_dir), "--org", org,
         "--scenario", "would-the-twin-have-flagged-it", "--regime", "as-consumed", "--at", at],
        "threat.json",
    )
    rewound = run(["rewind", "--repo", str(netflix_dir), "--org", org, "--at", at], "rewind.json")
    threat_commit = threat["envelope"]["pins"]["model_repo"]["commit"]
    resolved_commit = rewound["body"]["resolved"]["commit"]
    if threat_commit != resolved_commit:
        raise Violated(
            "`twin backtest` and `twin rewind` resolved 2011-08-01 to two different commits — "
            "the threat path and the opportunity path would be reading different states while "
            "the beat narrates one"
        )

    forecasts = threat["body"]["forecasts"]
    if len(forecasts) < 2:
        raise Violated(
            f"the threat path emits {len(forecasts)} forecast(s) at {at}; an ensemble beat with "
            "nothing to spread is the plurality refusal satisfied trivially rather than shown"
        )
    distinct = len({f["probability"] for f in forecasts})
    if distinct < 2:
        raise Violated(
            f"the threat path emits {len(forecasts)} forecast(s) at {at} but only {distinct} "
            "distinct probability among them — an ensemble that agrees with itself demonstrates "
            "nothing about plurality"
        )

    swept = run(
        ["gameplay-sweep", "--repo", str(netflix_dir), "--ref", resolved_commit],
        "sweep.json",
    )
    if not swept["body"]["opportunities"]:
        raise Violated(
            f"the opportunity path pulls nothing at {at} — the seize half of the beat has no "
            "content, so only the threat half is being demonstrated"
        )
    if swept["envelope"]["pins"]["repos"][0]["commit"] != resolved_commit:
        raise Violated("the opportunity sweep did not run on the commit `twin rewind` resolved")

    # -- the cut is real, checked through the CLI rather than a direct Overlay reach-in ----------
    options_past_rc = cli_main([
        "options", "--repo", str(netflix_dir), "--ref", resolved_commit, "--org", org,
        "--perspective", perspective_id, "--out", str(out / "options-past.json"),
    ])
    if options_past_rc == 0:
        raise Violated(
            f"`twin options` succeeded for {perspective_id!r} at the commit {at} resolves to; "
            "the pricing layer rests on filings dated after that day and the perspective should "
            "not exist yet — a commit was back-dated"
        )
    if rewound["body"]["rollups"]["causal_edges"] != 0:
        raise Violated(
            f"the rewound state at {at} already carries a causal edge; back-dating the pricing "
            "layer would defeat the point of running the threat path from before it existed"
        )

    options_head = run(
        ["options", "--repo", str(netflix_dir), "--org", org, "--perspective", perspective_id],
        "options-head.json",
    )
    admitted = set(options_head["body"]["prefilter"]["admitted"])
    if not {lever_id, control_id} <= admitted:
        raise Violated(
            f"expected {lever_id!r} and {control_id!r} admitted by the pre-filter at HEAD, got "
            f"{sorted(admitted)}"
        )

    # -- the cross-domain comparison, direction-named, and the refusal that survives it ---------
    price_doc = run(
        ["price", "--repo", str(netflix_dir), "--org", org, "--origin", origin], "price.json"
    )
    priced = price_doc["body"]
    eye = next(e for e in priced["perspectives"] if e["perspective"] == perspective_id)
    mitigations = {r["option"]: r["mitigation"] for r in eye["responses"]["priced"]}
    if lever_id not in mitigations or control_id not in mitigations:
        raise Violated(
            f"expected {lever_id!r} and {control_id!r} both priced under {perspective_id!r}, got "
            f"{sorted(mitigations)} — a lever cannot be compared against a control without both "
            "of them on the page"
        )
    if "credit" not in mitigations[lever_id]:
        raise Violated(f"{lever_id!r} earned no mitigation credit; the lever with the evidence "
                       "should price")
    if "credit" in mitigations[control_id]:
        raise Violated(f"{control_id!r} earned mitigation credit; its claim is graded outside "
                       "the pricing threshold and should be refused a figure, not given one")
    if "reason" not in mitigations[control_id]:
        raise Violated(f"{control_id!r} earned no credit and carries no reason it earned none")

    # -- the curve keeps the disagreement, and the refused option's own figure never moves -------
    account_args = [arg for a in accounts for arg in ("--account", a)]
    curve_doc = run(
        ["trade-off", "--repo", str(netflix_dir), "--org", org, "--origin", origin,
         "--perspective", perspective_id, *account_args],
        "curve.json",
    )
    curve = curve_doc["body"]
    agreement = curve["agreement"]
    if agreement["unanimous"] or len(set(agreement["cheapest_by_account"].values())) < 2:
        raise Violated(
            "the named accounts agree on the cheapest response, so the one committed fixture in "
            "this repository that makes an ensemble disagreement visible no longer does"
        )
    control_row = next(p for p in curve["curve"] if p["option"] == control_id)
    if control_row["net_cost_of_risk"]["range"] != 0:
        raise Violated(
            f"{control_id!r} earns no credit under any named account, so its own net cost of "
            f"risk should not move across the ensemble; the reported range is "
            f"{control_row['net_cost_of_risk']['range']}"
        )
    if sorted(control_row["uncredited_by"]) != sorted(accounts):
        raise Violated(f"{control_id!r} should be uncredited by every named account")

    # -- no account is privileged (seam 2, deliberately: see docstring) -------------------------
    from .. import tradeoff as tradeoff_mod
    from ..model import Overlay
    from ..repo import ModelRepo

    overlay = Overlay.load(ModelRepo.open(netflix_dir), org)
    perspective = overlay.perspectives[perspective_id]
    for dropped in accounts:
        kept = [a for a in accounts if a != dropped]
        without = tradeoff_mod.curve(overlay, perspective, origin, overlay.responses, kept)
        for account in kept:
            before = {p["option"]: p["net_cost_of_risk"]["by_account"][account] for p in curve["curve"]}
            after = {p["option"]: p["net_cost_of_risk"]["by_account"][account] for p in without["curve"]}
            if before != after:
                raise Violated(
                    f"dropping {dropped} moved {account}'s own net cost of risk — an account is "
                    "being computed from the company it keeps rather than from its own graph alone"
                )

    # -- versioned enactment, proposed on the lever, through the not-code channel ----------------
    proposal = run(
        ["propose", "--repo", str(netflix_dir), "--org", org, "--response", lever_id,
         "--channel", "record"],
        "proposal.json",
    )
    if proposal["body"]["response"]["id"] != lever_id:
        raise Violated(
            f"the enactment proposal names {proposal['body']['response']['id']!r}, not "
            f"{lever_id!r} — the beat's own defect (proposing the code control through the "
            "not-code channel) would reproduce silently if this drifted back"
        )

    # -- the limitation is paired with the capability, over every artefact the beat emits --------
    from .. import planter as planter_mod

    substrate = run(
        ["substrate", "--repo", str(netflix_dir), "--org", org,
         "--recipe", str(PACKAGE_DIR / "netflix-substrate-recipe.yaml"),
         "--checkpoint", checkpoint],
        "substrate.json",
    )
    emitted = [threat, rewound, swept, options_head, price_doc, curve_doc, proposal, substrate]
    claimed = 0
    for artefact in emitted:
        if "synthetic-substrate" not in artefact["envelope"]["depth"]["capabilities"]:
            continue
        claimed += 1
        if planter_mod.SHARED_PRIOR_LIMITATION not in json.dumps(artefact["body"]):
            raise Violated(
                f"a {artefact['envelope']['kind']} artefact declares the synthetic-substrate "
                "capability and carries no shared-prior limitation; a synthetic result "
                "travelling without it reads as evidence about the world"
            )
    if not claimed:
        raise Violated("no emitted artefact claimed the synthetic-substrate capability, so the "
                       "pairing above was asserted over nothing")

    cheapest = ", ".join(f"{a}->{o}" for a, o in sorted(agreement["cheapest_by_account"].items()))
    return (
        f"`twin backtest` and `twin rewind` independently resolved {at} to the same commit; "
        f"{len(forecasts)} rival forecasts ({distinct} distinct) and "
        f"{len(swept['body']['opportunities'])} opportunity pulled from it, with `twin options` "
        f"refusing the perspective and 0 causal edges at that commit; {lever_id!r} priced with "
        f"credit and {control_id!r} refused with a reason, its own net cost of risk unmoved "
        f"across every account; the accounts disagree ({cheapest}) and dropping any one leaves "
        f"the rest untouched; enactment proposed on the lever through `record`; "
        f"{claimed}/{len(emitted)} emitted artefacts claim synthetic-substrate and all carry the "
        "limitation"
    )


@harness_check("intel_forecast_is_pinned_signed_and_names_its_own_unscoreability")
def _intel_forecast_is_pinned_signed_and_names_its_own_unscoreability(ctx: Context) -> str:
    """The live, unresolved, pinned forecast (build ticket 75, decision tickets 06, 22).

    **Emitted through the scheduled production line, not hand-made (AC 4).** `twin sweep` is
    "the normal scheduled production line" `twin/schedule.py`'s own docstring names: no human
    names a scenario, in contrast to `twin run --scenario X`. This guard drives `cli.main` for
    `sweep`, never `run`, for the artefact it presents as the forecast — and then separately
    drives `run` on the identical scenario purely to obtain a standalone `forecast-bundle` file to
    feed `score`'s file-based interface, asserting the two are byte-identical
    (`digest_of_file`, the same check `identical_pins_identical_bytes` makes elsewhere). A
    hand-authored forecast could not reproduce this: the number the demo shows is exactly the
    number the scheduler would have produced with nobody watching.

    **Explicitly unscoreable, and the artefact says so (AC 2) — never a side channel.** Adversarial
    review of build ticket 74 found prose that explained a caveat only in a script's own `echo`
    lines, never reaching the artefact itself; this guard asserts the unscoreable statement and
    the resolution window are read back out of the *emitted forecast bundle's own body*
    (`scenario.question`), not merely present in the fixture source. It also asserts the absence
    is structural, not narrated: the `intel` overlay carries zero outcomes, checked directly
    against `Overlay.load`, and `twin score` against any outcome id refuses and names the same
    absence build ticket 74 already demonstrated for Netflix — for a different, stated reason
    (that story is over; this one has not happened yet).

    **The resolution date is published in the artefact too (AC 3), held to the identical
    standard.** Checked against `execution["body"]["scenario"]["horizon"]` — the emitted bundle —
    never against `Overlay.proposition(...)["resolves_on"]`, which is the source a reader holding
    only the artefact cannot see.

    **Pinned and signed before any resolution (AC 1).** Both emitted artefacts are derived, carry
    pins, and their attestation sidecars report `agent-signed`, never `unsigned` and never a human
    signature — `derived_never_human_signed` already asserts the mechanism globally; this checks
    it actually fires on this org's own artefacts rather than trusting it by inference.

    **The depth grade travels with the artefact, computed rather than typed (AC 6).** Read back
    from the sweep artefact's own `envelope.depth`, never asserted separately in this guard.
    """
    import json

    from ..artefact import digest_of_file
    from ..attest import SUFFIX as ATTEST_SUFFIX
    from ..cli import main as cli_main
    from ..model import Overlay
    from ..repo import ModelRepo

    org = "intel"
    scenario_id = "does-the-14a-bet-land-a-named-customer"

    intel_dir = ctx.tmp / "intel-repo"
    if not intel_dir.exists():
        fixtures.build_intel_org(intel_dir)
    out = ctx.tmp / "intel-forecast-guard"
    out.mkdir(exist_ok=True)

    # No answer key exists, structurally, before anything else runs — the permanent half of AC 2.
    overlay = Overlay.load(ModelRepo.open(intel_dir), org)
    if overlay.outcomes:
        raise Violated(
            f"the intel overlay carries {len(overlay.outcomes)} outcome(s); this fixture's own "
            "contract is that none is ever authored, because the proposition has not resolved"
        )

    old_key = os.environ.get("TWIN_SIGNING_KEY")
    os.environ["TWIN_SIGNING_KEY"] = "invariant-suite-key"
    try:
        def run_cli(args: list[str], outfile: str) -> dict:
            path = out / outfile
            rc = cli_main([*args, "--out", str(path)])
            if rc != 0:
                raise Violated(f"`twin {' '.join(args)}` exited {rc}")
            return json.loads(path.read_bytes())

        def signed(outfile: str) -> None:
            sidecar = json.loads((out / f"{outfile}{ATTEST_SUFFIX}").read_bytes())
            # `signature_status` is `None` exactly when a signing key produced an agent signature
            # (`attest.build`); a truthy value there names why it did *not* sign — see
            # `twin/attest.py`'s own `None if material else UNSIGNED`.
            status = sidecar.get("signature_status")
            if status is not None or not sidecar.get("agent_signature"):
                raise Violated(f"{outfile}: expected an agent-signed sidecar, got status={status!r}")
            if sidecar.get("human_involvement", {}).get("present"):
                raise Violated(f"{outfile}: carries human involvement on a derived artefact")

        # -- the scheduled production line, and nothing hand-made behind it -----------------------
        # Two clean executions, not one: build ticket 88 adds the real opportunity scenario
        # (decision ticket 13 AC 7) beside this fear scenario in the identical overlay, and the
        # standing library (tier 1) sweeps every scenario in it unconditionally.
        swept = run_cli(["sweep", "--repo", str(intel_dir)], "sweep.json")
        signed("sweep.json")
        executions = swept["body"]["executions"]
        if len(executions) != 2 or swept["body"]["failures"]:
            raise Violated(
                f"expected exactly two clean executions sweeping the intel repository (fear + "
                f"opportunity), got {len(executions)} execution(s) and "
                f"{len(swept['body']['failures'])} failure(s)"
            )
        by_scenario = {e["scenario"]: e for e in executions if e["org"] == org}
        if scenario_id not in by_scenario:
            raise Violated(f"sweep never ran {org}/{scenario_id}: got {sorted(by_scenario)}")
        execution = by_scenario[scenario_id]

        standalone = run_cli(
            ["run", "--repo", str(intel_dir), "--org", org, "--scenario", scenario_id,
             "--regime", "as-consumed"],
            "run.json",
        )
        signed("run.json")
        standalone_digest = digest_of_file(out / "run.json")
        if execution["forecast_bundle"]["sha256"] != standalone_digest:
            raise Violated(
                "the sweep-embedded forecast bundle is not byte-identical to a standalone `twin "
                "run` on the same scenario — the scheduled forecast and an independently "
                "reproduced one disagree, so it is not provably the same computation"
            )

        forecasts = standalone["body"]["forecasts"]
        if len(forecasts) < 2 or len({f["probability"] for f in forecasts}) < 2:
            raise Violated(
                f"expected plural, distinct forecasts on an ensemble with genuine disagreement, "
                f"got {[f['probability'] for f in forecasts]}"
            )

        # -- the resolution date is published IN THE ARTEFACT, not only in the fixture source ------
        # (AC 3). Held to the identical standard as the unscoreability check just below: read back
        # from the emitted body's own `scenario.horizon` — which `verbs.run` already copies from
        # the scenario's `horizon` field for every fixture in this file, unmodified by this ticket
        # — never from `Overlay.proposition(...)["resolves_on"]`, which is the *source*, not what a
        # reader holding only the artefact would see.
        if execution["body"]["scenario"]["horizon"] != "2027-06-30":
            raise Violated(
                f"the emitted forecast bundle's own scenario.horizon is "
                f"{execution['body']['scenario']['horizon']!r}, not the declared resolution date"
            )

        # -- explicitly unscoreable, published in the artefact's own body, not a side channel -----
        question = execution["body"]["scenario"]["question"].lower()
        for needle in ("unscoreable", "second half of 2026", "first half of 2027", "twin score"):
            if needle not in question:
                raise Violated(
                    f"the emitted forecast bundle's own scenario.question does not mention "
                    f"{needle!r} — the resolution window and checking procedure must be published "
                    "with the artefact, not only in the fixture source or a script's own prose"
                )

        # -- and the refusal is real, not narrated -------------------------------------------------
        score_out = out / "score.json"
        rc = cli_main([
            "score", "--repo", str(intel_dir), "--org", org, "--forecast", str(out / "run.json"),
            "--outcome", "any-outcome-at-all", "--out", str(score_out),
        ])
        if rc == 0:
            raise Violated("`twin score` succeeded against an overlay that carries no outcome")
        if score_out.exists():
            raise Violated("`twin score` wrote an artefact despite refusing")
    finally:
        if old_key is None:
            os.environ.pop("TWIN_SIGNING_KEY", None)
        else:
            os.environ["TWIN_SIGNING_KEY"] = old_key

    return (
        f"`twin sweep` and a standalone `twin run` agree byte-for-byte on {scenario_id!r} "
        f"({len(forecasts)} distinct forecasts); both artefacts are pinned and agent-signed; the "
        "emitted body names its own unscoreability, resolution window and checking procedure; "
        "the intel overlay carries zero outcomes and `twin score` refuses against it"
    )


@harness_check("benchmark_selection_is_mechanical_and_quarantine_catches_a_planted_breach")
def _benchmark_selection_is_mechanical_and_quarantine_catches_a_planted_breach(ctx: Context) -> str:
    """Benchmark question selection and ingestion quarantine (build ticket 57, decision ticket
    21 Q1(b)/Q2): the committed selection rule is mechanical and reproducible, the selected set
    spans the full confidence range, and a quarantine breach planted in ingestion provenance is
    actually caught — the same structural-plus-live shape
    `signal_classify_is_grade_5_by_construction` uses, extended here to a selection-plus-audit
    pair rather than a single function.

    Four legs, against the real committed rule (`twin/benchmark-selection-rule.yaml`), never a
    hand-typed stand-in. First, reproducibility: the identical rule against an identical pool
    selects the identical set twice. Second, the selected set spans every bin the rule declares —
    checked against `spans_full_confidence_range()`'s own computed answer. Third, the negative
    leg: auditing ingestion-provenance records that never mention a quarantined id reports clean.
    Fourth, the AC this ticket names directly: a quarantined question's id planted in a nested
    provenance field — a recipe id, a free-text note — is caught by `audit_quarantine`, at both an
    old and a since-elapsed record, because nothing in the audit reads a timestamp to filter by.
    """
    from .. import benchmark as bm

    rule = bm.SelectionRule.load()
    midpoints = [lo + (hi - lo) / 2 for lo, hi in rule.confidence_bins for _ in range(3)]
    pool = [
        {
            "id": f"guard-q-{i:02d}",
            "category": rule.categories[i % len(rule.categories)],
            "liquidity": rule.min_liquidity * 2,
            "horizon_days": (rule.min_horizon_days + rule.max_horizon_days) // 2,
            "implied_probability": p,
        }
        for i, p in enumerate(midpoints)
    ]

    first = bm.select_questions(rule, pool)
    second = bm.select_questions(rule, pool)
    if first != second:
        raise Violated("select_questions() against the identical rule and pool did not reproduce identically")
    if not first.spans_full_confidence_range():
        raise Violated(f"the selected set does not span every declared confidence bin: {first.distribution}")

    clean_records: list[tuple[str, dict[str, Any]]] = [
        ("ingest-run#1", {"provenance": {"substrate": "sha256:aa:1", "recipe": "unrelated-recipe", "index": 0}}),
        ("ingest-run#2", {"provenance": {"substrate": "sha256:bb:1", "recipe": "another-recipe", "index": 1}}),
    ]
    clean = bm.audit_quarantine(first, clean_records)
    if clean:
        raise Violated(f"a quarantine audit against records naming no quarantined id reported a breach: {clean}")

    planted_id = next(iter(first.ids))
    breached_records = [
        *clean_records,
        # "at any lag": an old record and one long since elapsed both carry the planted breach,
        # buried in a nested field rather than a single obviously-checked one.
        (
            "ingest-run#0-old",
            {"provenance": {"substrate": "sha256:cc:1", "recipe": f"derived-from-{planted_id}", "index": 0}},
        ),
        (
            "ingest-run#99-elapsed",
            {"provenance": {"substrate": "sha256:dd:1", "recipe": "unrelated", "note": f"see also {planted_id}"}},
        ),
    ]
    breaches = bm.audit_quarantine(first, breached_records)
    caught = {b.where for b in breaches}
    if "ingest-run#0-old" not in caught or "ingest-run#99-elapsed" not in caught:
        raise Violated(f"a planted quarantine breach was not caught at both lags: caught {caught}")
    if any(b.question_id != planted_id for b in breaches):
        raise Violated(f"a breach was reported against the wrong question id: {breaches}")

    return (
        "select_questions() reproduces byte-identically against the committed rule; the selected "
        f"{len(first.questions)}-question set spans all {len(first.distribution)} declared "
        "confidence bins; a clean provenance audit reports no breach; a quarantined id planted in "
        "a nested field of an old and a since-elapsed record is caught at both"
    )


@harness_check("forecast_book_is_blind_by_construction_and_observe_only")
def _forecast_book_is_blind_by_construction_and_observe_only(ctx: Context) -> str:
    """Blind pinned emission, resolution scoring, and the narrow claim (build ticket 58, decision
    ticket 21 Q1(c)/Q4/Q5): temporal separation is refused structurally rather than reviewed, the
    module's public surface cannot place a position, resolution scoring reuses `twin/scoring.py`
    rather than re-implementing it, and the narrow claim scope travels with every emitted result —
    the same structural-plus-live shape
    `benchmark_selection_is_mechanical_and_quarantine_catches_a_planted_breach` uses, extended here
    to a module-surface allow-list rather than a single function pair.

    Four legs. First, structural refusal: an emission timed at the resolution window's own open
    and one timed past it are both refused, and the identical inputs a month earlier succeed — a
    gate, not a wall. Second, observe-only: `twin/forecast_book.py`'s exposed function surface is
    asserted as an **allow-list**, the same discipline `prefilter_precedes_pricing` uses on
    `twin/options.py`, so a differently-named position-placing function would still be caught, not
    only one matching an obvious keyword. Third, scoring: `score_resolution`'s own source calls
    `scoring.score(`, and its output matches `twin/scoring.py`'s own `brier`/`log_loss` bit for
    bit rather than a second implementation drifting from it. Fourth, the claim scope: both
    artefacts this module emits carry `claim_scope`, and its `does_not_evidence` names Wardley
    propagation, the causal elasticities, £ pricing and the org overlay explicitly, checked
    against the emitted body rather than asserted in prose.
    """
    import inspect

    from .. import forecast_book as fb
    from .. import scoring

    question = {"id": "guard-q-1", "resolution_window_opens_at": "2026-09-01T00:00:00Z"}
    command = ["twin", "forecast-emit"]

    for late in ("2026-09-01T00:00:00Z", "2026-09-02T00:00:00Z"):
        try:
            fb.emit(ctx.caps, question, "twin-default", 0.3, late, command)
        except fb.ForecastBookError:
            continue
        raise Violated(f"an emission timed at or after the resolution window ({late}) was not refused")

    emission = fb.emit(ctx.caps, question, "twin-default", 0.3, "2026-08-01T00:00:00Z", command)
    if emission.body["position_placed"] is not False or emission.body["observe_only"] is not True:
        raise Violated(f"a blind emission did not record observe-only/no-position: {emission.body}")
    if not fb.is_blind(emission.body["emitted_at"], emission.body["resolution_window_opens_at"]):
        raise Violated(
            "is_blind() disagrees with the artefact it just built, against that artefact's own "
            "recorded body"
        )

    allowed = {"emit", "score_resolution", "is_blind"}
    banned_verbs = ("place", "stake", "bet", "buy", "sell", "trade", "order", "wager", "hedge", "position")
    public = {
        name
        for name, value in vars(fb).items()
        if not name.startswith("_") and inspect.isfunction(value) and getattr(value, "__module__", "") == fb.__name__
    }
    if public != allowed:
        raise Violated(
            f"twin/forecast_book.py exposes {', '.join(sorted(public)) or 'nothing'} at module "
            f"level; this guard admits exactly {', '.join(sorted(allowed))} — observe-only is "
            "structural, so a new callable here needs a deliberate decision, not a keyword scan"
        )
    for name in public:
        hit = [v for v in banned_verbs if v in name.lower()]
        if hit:
            raise Violated(f"{name} contains a position-shaped verb ({', '.join(hit)}) despite passing the allow-list")

    source = inspect.getsource(fb.score_resolution)
    if "scoring.score(" not in source:
        raise Violated(
            "score_resolution() does not call twin/scoring.py's score() — a second scoring "
            "implementation may have crept in"
        )
    resolved = fb.score_resolution(ctx.caps, emission.envelope(), emission.digest(), True, ["twin", "forecast-score"])
    expected = scoring.score(0.3, True)
    if (resolved.body["brier"], resolved.body["log_loss"]) != (expected["brier"], expected["log_loss"]):
        raise Violated(f"score_resolution() did not reproduce twin/scoring.py's own score: {resolved.body} vs {expected}")

    for artefact in (emission, resolved):
        scope = artefact.body.get("claim_scope") or {}
        does_not = " ".join(str(s) for s in scope.get("does_not_evidence", [])).lower()
        missing = [
            phrase
            for phrase in ("wardley propagation", "causal elasticities", "£ pricing", "org")
            if phrase not in does_not
        ]
        if missing:
            raise Violated(f"{artefact.kind}'s claim_scope does not name {missing}: {scope}")

    return (
        "an emission at or after its resolution window is refused (checked at the boundary and "
        "past it); a blind emission records observe_only/position_placed correctly and is_blind() "
        f"agrees with its own recorded body; the module's public surface is exactly "
        f"{', '.join(sorted(allowed))}, none position-shaped; score_resolution() calls "
        "scoring.score() and reproduces its output bit for bit; both the emission and the "
        "resolution score carry a claim_scope naming what the gate does not evidence"
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
    # The primary missed-opportunity case (build ticket 71, decision tickets 19/22): the same
    # dated-and-cited contract, holding even though the proposition is a missed opportunity
    # rather than a collapse — the table has no opinion on which direction a proposition names,
    # only that it is dated, cited and resolved honestly.
    ("royal-mail", fixtures.build_royal_mail_org, "royal-mail-concedes-the-automation-shortfall-2019",
     "ipc.be", "low"),
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


@harness_check("a_scored_forecast_is_never_silently_dropped")
def _a_scored_forecast_is_never_silently_dropped(ctx: Context) -> str:
    """The falsifiability beat's own refusal (build ticket 72, decision ticket 22).

    The beat's thesis is *"we can prove when we're wrong"*, and its Royal Mail result is red: the
    market consensus at flotation put the shortfall at 0.05 and it happened, so the brier is worse
    than a coin flip. The thesis survives that and does not survive hiding it, so the ways it
    could be hidden are the thing to guard.

    Three legs, black-box rather than by reading a comment. **Nothing is dropped between the
    bundle and the card**: every forecast the execution emitted is either scored or named in
    `unscoreable` with a reason, so a poor forecast cannot leave by the same door a genuinely
    unresolvable one uses. **Nothing is dropped between the card and the screen**: `twin score`'s
    own stdout names every world model the card scored, so the surface a viewer watches cannot
    report a subset of what the artefact holds. **The red result is not tuned away**: the worst
    forecast on this key stays worse than a flat 0.5. That last one is asserted on the *worst*
    score rather than a fixed figure, so adding a world model that gets it right — which is the
    whole point of an ensemble — passes, and quietly re-authoring the losing belief does not.
    """
    import contextlib
    import io
    import json

    from ..cli import main as cli_main

    org, scenario = "royal-mail", "would-the-twin-have-flagged-it"
    key = "royal-mail-concedes-the-automation-shortfall-2019"

    # The same scratch paths the other answer-key guards use, so one suite run builds one
    # Carillion rather than two (`carillion-repo` is this file's existing name for it).
    repos: dict[str, Path] = {}
    for name, dirname in ((org, org), ("carillion", "carillion-repo"), ("enron", "enron")):
        repo_dir = ctx.tmp / dirname
        if not repo_dir.exists():
            fixtures.BUILDERS[name](repo_dir)
        repos[name] = repo_dir

    out = ctx.tmp / "beat"
    bundle = out / "forecast-bundle.json"
    if cli_main([
        "backtest", "--repo", str(repos[org]), "--org", org, "--scenario", scenario,
        "--regime", "as-consumed", "--at", "2018-06-01", "--out", str(bundle),
    ]) != 0:
        raise Violated("the beat's rewind-and-project leg exited non-zero")

    legs: dict[str, Path] = {}
    for name, outcome in (("carillion", "carillion-collapse-resolved"), ("enron", "enron-bankruptcy-resolved")):
        leg_bundle, leg_card = out / f"{name}-bundle.json", out / f"{name}-card.json"
        rc1 = cli_main([
            "run", "--repo", str(repos[name]), "--org", name, "--scenario", scenario,
            "--regime", "as-consumed", "--out", str(leg_bundle),
        ])
        rc2 = cli_main([
            "score", "--repo", str(repos[name]), "--org", name, "--forecast", str(leg_bundle),
            "--outcome", outcome, "--out", str(leg_card),
        ])
        if rc1 != 0 or rc2 != 0:
            raise Violated(f"the {name} discount leg exited non-zero (run={rc1}, score={rc2})")
        legs[name] = leg_card

    card = out / "score-card.json"
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        rc = cli_main([
            "score", "--repo", str(repos[org]), "--org", org, "--forecast", str(bundle),
            "--outcome", key, "--discount-enron", str(legs["enron"]),
            "--discount-obscure", str(legs["carillion"]), "--out", str(card),
        ])
    if rc != 0:
        raise Violated("the beat's scoring leg exited non-zero")

    emitted = json.loads(bundle.read_bytes())["body"]["forecasts"]
    body = json.loads(card.read_bytes())["body"]
    if not body["scores"]:
        raise Violated("the beat scored nothing, so it demonstrates no falsifiability at all")

    # The partition is checked on two cards, because on the beat's own card it cannot fail: this
    # key carries one world model and nothing unscoreable, so `scores + unscoreable == emitted`
    # reduces to "one score exists", which the line above already says. The second card is the
    # fixture org run under `with-hindsight` — every forecast is then ineligible, so the
    # `unscoreable` list is the populated one and the arithmetic has both halves to get wrong.
    # A leg that cannot fail is not a guard, it is a sentence.
    # A third card for the same reason, and it is also the only one that can exercise the ordering
    # leg below: the beat's key carries one world model, so "the worst is printed first" is true of
    # a list of one however it is sorted. The fixture org carries three.
    spread: dict[str, tuple[Path, Path, str]] = {}
    for regime in ("with-hindsight", "as-consumed"):
        spread_bundle = out / f"{regime}-bundle.json"
        spread_card = out / f"{regime}-card.json"
        rc1 = cli_main([
            "run", "--repo", str(ctx.repo_dir), "--org", "netflix", "--scenario", "dvd-decline-2011",
            "--regime", regime, "--out", str(spread_bundle),
        ])
        spread_printed = io.StringIO()
        with contextlib.redirect_stdout(spread_printed):
            rc2 = cli_main([
                "score", "--repo", str(ctx.repo_dir), "--org", "netflix",
                "--forecast", str(spread_bundle), "--outcome", "dvd-decline-2011-resolved",
                "--out", str(spread_card),
            ])
        if rc1 != 0 or rc2 != 0:
            raise Violated(f"the {regime} card could not be built (run={rc1}, score={rc2})")
        spread[regime] = (spread_bundle, spread_card, spread_printed.getvalue())

    hindsight_bundle, hindsight_card, _ = spread["with-hindsight"]
    partitions = [(bundle, card), (hindsight_bundle, hindsight_card), spread["as-consumed"][:2]]
    for bundle_path, card_path in partitions:
        forecasts = json.loads(bundle_path.read_bytes())["body"]["forecasts"]
        scored = json.loads(card_path.read_bytes())["body"]
        reported = len(scored["scores"]) + len(scored["unscoreable"])
        if reported != len(forecasts):
            raise Violated(
                f"{card_path.name}: {len(forecasts)} forecast(s) emitted, {reported} reported — a "
                "forecast left without being scored and without being named unscoreable"
            )
    hindsight = json.loads(hindsight_card.read_bytes())["body"]
    if not hindsight["unscoreable"] or hindsight["scores"]:
        raise Violated(
            "the with-hindsight card scored something or named nothing unscoreable, so the "
            "partition check has no populated `unscoreable` side to exercise"
        )

    worst = max(body["scores"], key=lambda s: s["brier"])
    if worst["brier"] <= 0.25:
        raise Violated(
            f"the worst forecast on this key scores {worst['brier']}, better than a flat 0.5 — the "
            "beat's red result has been tuned away, and a falsifiability demo that only passes "
            "proves nothing"
        )

    # The **figure**, not merely the world model's name: a surface that printed the names and
    # dropped the numbers would satisfy a name-only check while showing nothing of the result,
    # and this leg's whole claim is that the red result reaches the screen. And the worst one is
    # required to be the first score printed, because "reported" and "reported where somebody
    # reads it" are the difference between an honest surface and a technically-complete one.
    for label, scored_body, on_screen in (
        ("the beat's card", body, printed.getvalue()),
        ("the three-model card", json.loads(spread["as-consumed"][1].read_bytes())["body"],
         spread["as-consumed"][2]),
    ):
        entries = scored_body["scores"]
        lines = [line for line in on_screen.splitlines()
                 if any(s["world_model"] in line for s in entries)]
        for entry in entries:
            shown = [line for line in lines if entry["world_model"] in line]
            if not shown or f"{entry['brier']:.4f}" not in shown[0]:
                raise Violated(
                    f"{label}: `twin score` did not print {entry['world_model']}'s own score "
                    f"({entry['brier']}) — a scored forecast reached the card and not the screen"
                )
        poorest = max(entries, key=lambda s: s["brier"])
        if not lines or poorest["world_model"] not in lines[0]:
            raise Violated(
                f"{label}: the worst forecast ({poorest['world_model']}, brier {poorest['brier']}) "
                "is not the first score printed — the bad news sits below better news, on a "
                "lower-is-better rule"
            )

    discount = body["contamination_discount"]
    if discount is None:
        raise Violated("the beat's card carries no contamination discount despite both legs being supplied")
    # Keyed off the measured rule rather than assuming brier, because `--discount-rule` accepts
    # log_loss. A discount of exactly zero is a legitimate measurement — `scoring.measure_discount`
    # declines to clamp the sign precisely so that "no memorisation advantage" can be reported —
    # so the raw and adjusted figures being equal is checked as presence, never as difference.
    if f"adjusted_{discount['rule']}" not in worst:
        raise Violated(
            f"the discounted card reports no adjusted_{discount['rule']} beside the raw figure"
        )

    return (
        f"the partition holds on both a scoring card ({len(emitted)} emitted, "
        f"{len(body['scores'])} scored) and an all-unscoreable one "
        f"({len(hindsight['unscoreable'])} named, 0 scored); every scored forecast's own figure "
        f"reaches stdout; the worst is brier {worst['brier']} and is printed first, worse than a "
        "coin flip and still the headline"
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


@harness_check("flux_coverage_floor_is_still_reachable")
def _flux_coverage_floor_is_still_reachable(ctx: Context) -> str:
    """The pre-registered coverage floor can still be reached at the declared cadence (ticket 70).

    **What was missing was never the news that the probe was behind. It was the deadline.** Build
    ticket 70's audit first wrote this guard up as "two tickets, each green, composing into a
    measurement that cannot be read", and review showed that framing was false. Both tickets were
    honest about the shortfall in their own files:

    - Build ticket 64 reads `Status: instrumented, **NOT MEASURING**` and its AC 2 is open, in its
      own words *"What remains is the schedule — no crontab entry exists"*.
    - Build ticket 65 reads `Status: pre-registered, **VERDICT PENDING**` and records the figure
      itself: *"9% elapsed at 1% coverage"*.

    So the early-detection design caught the silence, twice, and said so. **What no ticket, guard or
    artefact carried was that the shortfall had an expiry.** Unsampled hours do not come back, so a
    floor stops being reachable at a computable moment, and after it the continuous-state branch
    closes `unmeasured` whatever the probe does. "We are behind" and "there are ten hours left" are
    different facts and only the first was ever computed. That is what this guard adds: not the
    shortfall, the irreversibility of it.

    **It does not go quiet when the window closes.** An earlier draft returned a pass there, on the
    reasoning that the fact was settled and `twin verdict` would report it. Review caught that:
    `flux_verdict_is_pre_registered_and_derived` passes on a branch reading `unmeasured`, so the
    suite would have gone fully green on 2026-11-06 over a measurement that produced no result —
    silence reading as stability, which is the failure the whole drift instrument exists to refuse.
    A closed window simply offers no remaining slots, so the same arithmetic answers "was it
    reached" and the guard is red on exactly the case the verdict cannot read.
    """
    from .. import drift
    from ..verdict import Protocol

    window, floor = drift.Window.load(), Protocol.load().minimum_coverage
    samples = drift.load_samples()
    # Wall-clock, for the same reason the liveness guard's is: the whole property is whether time
    # is still available, and a pinned clock would make this green forever at the moment it was
    # written — which is precisely how the gap it guards went unseen.
    now = datetime.datetime.now(datetime.timezone.utc)
    opens, closes = drift._day(window.opens), drift._day(window.closes)
    if now < opens:
        return f"window {window.opens}..{window.closes} has not opened; the full floor is still available"

    # Stringified because `floor_reachable` takes the moment as a parameter in the log's own format,
    # the same way `coverage` does — the wall clock stops here and the arithmetic below it stays a
    # function of its inputs.
    reach = drift.floor_reachable(window, samples, now.strftime("%Y-%m-%dT%H:%M:%SZ"), floor)
    taken = f"{reach['samples_reachable']}/{reach['samples_needed']} sample(s)"
    # A closed window offers no remaining slots, so `ceiling` collapses to the coverage actually
    # achieved and `reachable` becomes exactly the gate `verdict.decide` applies. One expression
    # answers both questions, and the guard is red on exactly the case the verdict cannot read.
    closed = now > closes
    if not reach["reachable"]:
        raise Violated(
            (
                f"the window closed {window.closes} at {reach['ceiling']:.1%} coverage, under its "
                f"pre-registered floor of {floor:.0%} ({taken}). The measurement produced no "
                "readable result and never will"
                if closed
                else (
                    f"the pre-registered coverage floor of {floor:.0%} can no longer be reached: "
                    f"{taken}, only {closes - now} of window left to take them in, a ceiling of "
                    f"{reach['ceiling']:.1%}"
                )
            )
            + f". The continuous-state branch closes `unmeasured`, so {drift.VERDICT_TICKET}'s "
            "primary falsifier is unanswerable and the residual branch cannot be concluded either. "
            f"{window.owner} owns the probe; window.yaml's `operation.crontab` is the line that was "
            "never installed. **This guard staying red is the finding, not a defect in it** — see "
            "build ticket 70's finding 1. It goes green only if the floor is actually reached"
        )
    if closed:
        return f"window closed {window.closes} at {reach['ceiling']:.1%}, above its {floor:.0%} floor"
    if reach["latest_start"] is None:
        # Already banked. There is no deadline for something no further action is needed for, and
        # printing one would read as a countdown on a floor that is met.
        return f"floor {floor:.0%} already met on samples taken: {taken}"
    return (
        f"floor {floor:.0%} still reachable (ceiling {reach['ceiling']:.1%}); {taken}, "
        f"start sampling by {reach['latest_start']} or it is gone"
    )


def _first_commit_date(root: Path, path: Path) -> datetime.datetime | None:
    """When a file first entered git history, or `None` if it never has.

    A file under `.estate-clone/<unit>/` lives in that unit's own repository, not the hub's, so
    its history is read there. The hub committed the same file at `estate/<unit>/...` before the
    six-org split (mo-12); that earlier date counts too, so the earliest of the two is returned.
    Reading only the hub's log made invariants 42 and 45 report "never committed" for files that
    had been committed for weeks.
    """
    candidates: list[tuple[Path, str]] = []
    try:
        candidates.append((root, path.relative_to(root).as_posix()))
    except ValueError:
        pass
    from .. import ESTATE_CLONE_DIR

    if path.is_relative_to(ESTATE_CLONE_DIR):
        inner = path.relative_to(ESTATE_CLONE_DIR)  # <unit>/<rest>
        unit_root = ESTATE_CLONE_DIR / inner.parts[0]
        candidates.append((unit_root, Path(*inner.parts[1:]).as_posix()))
        candidates.append((root, (Path("estate") / inner).as_posix()))
    found: list[datetime.datetime] = []
    for repo, rel in candidates:
        out = _git(repo, "log", "--diff-filter=A", "--format=%cI", "--", rel)
        stamps = [line for line in (out or "").splitlines() if line.strip()]
        if stamps:
            found.append(
                datetime.datetime.fromisoformat(stamps[-1].strip().replace("Z", "+00:00"))
            )
    return min(found) if found else None


@harness_check("forced_campaign_pre_registered_and_walled_off")
def _forced_campaign_pre_registered_and_walled_off(ctx: Context) -> str:
    """The forced-drift latency campaign predates its data and never leaks into the organic log
    (build ticket 78).

    Same shape as `drift_window_was_declared_before_it_was_measured`, for the same reason: a
    campaign whose pre-registration could be edited after seeing an inconvenient result is not a
    pre-registration. `ForcedCampaign.load` already refuses a file that omits any of the four
    named trials, an undo step for each, or the explicit "not organic-drift evidence" statement
    citing build ticket 65 — what only git history and the real logs can add is that the file
    predates the data, and that none of its samples have actually landed in build ticket 64's
    organic log. A forced mechanism event inside build ticket 65's verdict would be a bug, not a
    result, and this is the guard that would catch it.
    """
    from .. import drift

    campaign = drift.ForcedCampaign.load()  # refuses a file missing any required declaration
    forced_samples = drift.load_samples(campaign.samples_path)
    organic = drift.load_samples()

    # Independent of the timestamp checks below, and checked first: `FORCED_DRIFT_MARKER` is only
    # ever written by the campaign's own configmap-edit trial, so its presence anywhere in the
    # organic log is unmistakable contamination — including the failure a timestamp intersection
    # alone would miss, a misrouted `DRIFT_SAMPLES` override that sent a forced sample straight to
    # `samples.jsonl` and so left no matching entry in the campaign's own log to intersect against.
    marked = [s["ts"] for s in organic if drift.FORCED_DRIFT_MARKER in str(s.get("subjects", {}))]
    if marked:
        raise Violated(
            f"build ticket 64's organic samples.jsonl carries the forced-campaign marker "
            f"{drift.FORCED_DRIFT_MARKER!r} at {len(marked)} timestamp(s), earliest {min(marked)} "
            "— a forced sample reached the organic log, whether or not it also reached the "
            "campaign's own"
        )

    declared = _first_commit_date(REPO_DIR, drift.FORCED_CAMPAIGN_PATH)
    if declared is None:
        if forced_samples:
            raise Violated(
                f"{len(forced_samples)} forced-campaign sample(s) exist and forced-campaign.yaml "
                "has never been committed, so nothing establishes it was declared before the data"
            )
        return f"{len(campaign.trials)} trial(s) declared, uncommitted and unrun"

    early = [s["ts"] for s in forced_samples if drift._moment(s["ts"]) < declared]
    if early:
        raise Violated(
            f"{len(early)} forced-campaign sample(s) predate forced-campaign.yaml's first commit "
            f"({declared.isoformat()}), earliest {min(early)}"
        )

    leaked = {s["ts"] for s in forced_samples} & {s["ts"] for s in organic}
    if leaked:
        raise Violated(
            f"{len(leaked)} timestamp(s) appear in both the forced-campaign log and build ticket "
            "64's organic samples.jsonl — the wall between mechanism evidence and organic "
            "evidence has been crossed"
        )
    return (
        f"{len(campaign.trials)} trial(s) declared, committed {declared.date().isoformat()}, "
        f"{len(forced_samples)} forced sample(s), none earlier, none leaked into the organic log, "
        "no marker contamination"
    )


@harness_check("flux_verdict_is_pre_registered_and_derived")
def _flux_verdict_is_pre_registered_and_derived(ctx: Context) -> str:
    """The verdict's decision rule predates its data, and the elimination path stays closed
    (build ticket 65).

    Two guards in one, because they fail as one thing. `verdict.yaml` declares the risk basis, the
    coverage floor, the three branches and the spec amendment for the failing case — and a decision
    rule written once the data is in view is not a decision rule, so its first commit is read out
    of git the same way `drift_window_was_declared_before_it_was_measured` reads the window's.

    The second half is the one that actually bites, and it bites on live data every run: a null
    state-drift result must never produce a verdict concluding the residual `point-in-time` branch,
    because build ticket 64's window cannot see the third branch at all. `Protocol.load` refuses a
    two-branch protocol and `decide` refuses to resolve the residual while any branch is unmeasured,
    but both are code somebody could relax; this asserts the property against the real files, so
    relaxing either shows up here rather than in a durable artefact six months from now.
    """
    from .. import drift, verdict

    protocol = verdict.Protocol.load()  # refuses a missing branch, a missing amendment, a lone product
    window = drift.Window.load()
    decided = verdict.decide(protocol, window, drift.load_samples(), datetime.datetime.now(datetime.timezone.utc).isoformat())

    declared = _first_commit_date(REPO_DIR, verdict.PROTOCOL_PATH)
    closes = drift._day(window.closes)
    if declared is None:
        if datetime.datetime.now(datetime.timezone.utc) > closes:
            raise Violated(
                f"the measurement window closed {window.closes} and verdict.yaml has never been "
                "committed, so nothing establishes the decision rule was fixed before the result"
            )
    elif declared > closes:
        raise Violated(
            f"verdict.yaml was first committed {declared.date().isoformat()}, after the window "
            f"closed {window.closes} — the decision rule was written with the data in view"
        )

    residual = decided["branches"][verdict.RESIDUAL]
    action = decided["branches"][verdict.ACTION]
    if residual["state"] != verdict.PENDING and action["state"] == verdict.UNMEASURED:
        raise Violated(
            f"the residual point-in-time branch reads {residual['state']!r} while the "
            "action-boundary branch is unmeasured — a verdict reached by elimination against an "
            "incomplete set, which is the exact false dichotomy build ticket 65 exists to refuse"
        )
    if decided["verdict"] and action["state"] == verdict.UNMEASURED:
        if decided["branches"][verdict.STATE]["state"] != verdict.HELD:
            raise Violated(
                f"a verdict was emitted ({decided['verdict']!r}) with the action-boundary branch "
                "unmeasured and the state branch not held — no branch earned it"
            )
    return (
        f"{len(protocol.branches)} branches, floor {protocol.minimum_coverage:.0%}, amendment "
        f"drafted; state={decided['branches'][verdict.STATE]['state']}, "
        f"residual={residual['state']}, action={action['state']}, verdict="
        f"{decided['verdict'] or 'none yet'}"
    )


@harness_check("enactment_is_propose_only_at_both_layers")
def _enactment_is_propose_only_at_both_layers(ctx: Context) -> str:
    """The twin proposes and never disposes, asserted at both layers (build ticket 66).

    A guard on the suite rather than an invariant, for the reason the drift window and the pocket
    worksheet are: the constitution names sixteen invariants and may not grow a seventeenth without
    the constitution changing first.

    **Layer 1 is asserted as an allow-list, not as a name screen.** A free function that merges
    reopens the question whatever it is called, and `land` or `ship` gives nothing away to a
    keyword match — so the assertion is that `twin/enact.py`'s public surface is *exactly* these
    functions, and a new one forces a deliberate decision.

    **Layer 2 is asserted on the three composition paths build ticket 66 names** — a shell tool, an
    MCP GitHub server, a subagent with `gh` — because layer 1 holds unchanged through every one of
    them and the guarantee does not. The positive leg is asserted with them: opening a pull request
    is admitted, so this is a gate and not a wall.

    **The registration is asserted too, and that is the half that will actually rot.** Layer 2's
    named failure mode is a forgotten call site, so the check reads `.claude/settings.json` back and
    fails if the hook has gone. Nothing else in this repository would notice.
    """
    import inspect
    import json

    from .. import attest, verbs
    from .. import enact as enact_mod
    from .. import enact_guard
    from ..artefact import DERIVED
    from ..repo import ModelRepo

    # -- layer 1: the structural absence -----------------------------------------------------
    ALLOWED = {"dependency_pins", "propose"}
    public = {
        name
        for name, value in vars(enact_mod).items()
        if not name.startswith("_") and inspect.isfunction(value)
        and getattr(value, "__module__", "") == enact_mod.__name__
    }
    if public != ALLOWED:
        raise Violated(
            f"twin/enact.py exposes {', '.join(sorted(public)) or 'nothing'} at module level; this "
            f"guard admits exactly {', '.join(sorted(ALLOWED))}. A callable that disposes reopens "
            "propose-only whatever it is named, so adding one needs an authorising decision ticket."
        )

    # -- layer 2: the tool-call boundary, on the paths that defeat layer 1 --------------------
    composed = (
        ("a shell tool", "Bash", {"command": "gh pr merge 42 --squash"}),
        ("a shell tool", "Bash", {"command": "gh api --method PUT repos/o/r/pulls/42/merge"}),
        ("a shell tool, auto-merge", "Bash", {"command": "cd /tmp/work && gh pr merge --auto 7"}),
        ("an MCP GitHub server", "mcp__github__merge_pull_request", {"pullNumber": 42}),
        ("an MCP server naming the act differently", "mcp__forge__squash_pull_request", {"n": 42}),
    )
    # A subagent is deliberately absent from this table. Its calls reach `decide` only if the
    # runtime routes a subagent's tool calls through its hooks, which is the runtime's property and
    # not this repository's to assert — a row here would read as an assertion nothing checks.
    #
    # `decide` is now MODE-gated (twin/enact_guard.py's "Mode" section, 2026-08-25): the checked-in
    # default is `development`, permissive, for hands-on building. This invariant tests the
    # capability itself, not the ambient default, so it forces `operations` for its own calls —
    # restored in `finally` regardless of how the check exits.
    _prior_mode = os.environ.get("TWIN_ENACT_MODE")
    os.environ["TWIN_ENACT_MODE"] = "operations"
    try:
        for path, tool, payload in composed:
            if enact_guard.decide(tool, payload) is None:
                raise Violated(
                    f"the tool-call boundary admits a merge through {path} ({tool}: {payload}) — layer 1 "
                    "holds unchanged through that composition, so this is the layer that has to refuse it"
                )
        admitted = (
            ("Bash", {"command": "gh pr create --title 'propose: raise the CDN pin' --body ..."}),
            ("Bash", {"command": "git commit -m 'propose'"}),
            ("Read", {"file_path": "twin/enact.py"}),
        )
        for tool, payload in admitted:
            refused = enact_guard.decide(tool, payload)
            if refused is not None:
                raise Violated(
                    f"the tool-call boundary refuses {tool} {payload} ({refused}) — proposing is the "
                    "one thing the twin is for, and a guard that refuses it is a wall rather than a gate"
                )
    finally:
        if _prior_mode is None:
            os.environ.pop("TWIN_ENACT_MODE", None)
        else:
            os.environ["TWIN_ENACT_MODE"] = _prior_mode

    # -- layer 2's own failure mode: the call site, read back out of the registration ---------
    settings_path = REPO_DIR / ".claude" / "settings.json"
    if not settings_path.is_file():
        raise Violated(f"{settings_path} is missing, so layer 2 is registered nowhere")
    hooks = json.loads(settings_path.read_text(encoding="utf-8")).get("hooks", {})
    matchers = [
        str(group.get("matcher", ""))
        for group in hooks.get("PreToolUse", [])
        if any("enact_guard.py" in str(e.get("command", "")) for e in group.get("hooks", []))
    ]
    if not matchers:
        raise Violated(
            "no PreToolUse hook in .claude/settings.json runs twin/enact_guard.py — layer 2's "
            "named failure mode is a forgotten call site, and this is it happening"
        )
    # The registration must not itself be a name screen. `decide` can only refuse a call the
    # runtime routes to it, so a matcher reading `.*merge.*` would put the exact defect layer 1's
    # allow-list exists to avoid one level further out: a tool named `land_pull_request` would
    # never reach the guard at all, and every assertion above would still pass.
    UNREVEALING = ("land_pull_request", "shortcuts_execute", "Bash")
    for name in UNREVEALING:
        if not any(re.fullmatch(m, name) for m in matchers):
            raise Violated(
                f"the PreToolUse matcher(s) {matchers} do not route {name!r} to the guard. A "
                "matcher that screens for merge-shaped names is the same mistake as a merge-shaped "
                "name screen on layer 1, moved one level out where nothing else would catch it."
            )

    # -- the proposal itself: derived, so no endorsement can be attached to it ----------------
    repo = ModelRepo.open(ctx.repo_dir)
    proposal = enact_mod.propose(
        repo, ctx.caps, "netflix", "expand-the-delivery-network", enact_mod.POLICY,
        verbs.command_for("propose", org="netflix", response="expand-the-delivery-network", channel=enact_mod.POLICY),
    )
    if proposal.mark != DERIVED:
        raise Violated(
            "an enactment proposal is not marked derived, so derived_never_human_signed no longer "
            "refuses a human signature on it and a proposal could carry an endorsement"
        )
    material = b"invariant-suite-key"
    try:
        attest.build(proposal, [{"identity": "someone@example.invalid", "asserts": "accountability"}], material=material)
    except attest.AttestationError:
        pass
    else:
        raise Violated("a human signature attached to an enactment proposal — that is an endorsement")

    body = proposal.body
    layers = body["layers"]
    if len(layers) != 2 or any(not (layer.get("holds") and layer.get("fails_when")) for layer in layers):
        raise Violated(
            "the proposal does not state both layers with the failure mode of each; a proposal "
            "silent about how its own guarantee fails will be read as not having one"
        )
    if not body["dependency"]["pins"] or not body["dependency"]["limits"]:
        raise Violated(
            "the proposal names no real consumed dependency pin, or names them with no stated "
            "limit — 'signed, pinned, consumed by real separate repositories' is a claim about "
            "files, and a tag pin with its commit line commented out is not the pin it reads as"
        )
    try:
        enact_mod.propose(
            repo, ctx.caps, "netflix", "expand-the-delivery-network", "whatever-is-convenient",
            verbs.command_for("propose", org="netflix"),
        )
    except enact_mod.EnactError:
        pass
    else:
        raise Violated("an unnamed enactment channel was admitted, so the narrowing is decorative")

    dependency = body["dependency"]
    return (
        f"layer 1 exposes exactly {', '.join(sorted(ALLOWED))}; layer 2 refuses {len(composed)} "
        f"disposition shape(s) and admits {len(admitted)} proposing one(s), routed by a matcher "
        f"that admits a tool name revealing nothing about merging; the proposal is derived and "
        f"refuses a human signature; {dependency['cross_repository_pins']} cross-repository pin(s) "
        f"across {len(dependency['consumer_repositories'])} consumers "
        f"({dependency['self_sync_pins']} self-sync, counted apart), {len(dependency['limits'])} "
        "limit(s) stated"
    )


@harness_check("enforcement_is_a_spectrum_and_never_prices_a_rung")
def _enforcement_is_a_spectrum_and_never_prices_a_rung(ctx: Context) -> str:
    """Consequence is a spectrum, a rung buys no credit, and posture-as-identity is computed (67).

    A guard on the suite rather than an invariant, for the same reason build ticket 66's is: the
    constitution names sixteen invariants and may not grow a seventeenth without the constitution
    changing first.

    **The leg that matters is the one about money.** Decision ticket 18 Q4 admitted graded
    enforcement on the basis that it needs *no special status* — a control that modifies a FAIR
    factor by degree, priced by the £ engine's existing partial-mitigation path. A rung that
    carried a number would quietly turn that into a free multiplier: tighten the rung, earn more
    credit, with nothing evidencing it. So the assertion is that a rung is **invisible to
    pricing** — the same control at the loosest and the tightest rung produces an identical
    `Option`, which is the only thing that reaches the pre-filter and therefore the only thing
    that can reach a price.

    **Posture-as-identity is asserted as computed rather than declarable.** The prior estate's
    version was a philosophy an author could assert; here it is derived from two declared facts,
    and the fixture carries a control on each side of the line.
    """
    from .. import attest, enforcement, options, verbs
    from ..artefact import AUTHORED
    from ..model import Overlay
    from ..repo import ModelRepo
    from ..schema import SchemaError, validate

    # -- the ladder is a spectrum, and every rung is occupiable -------------------------------
    rungs = enforcement.grades()
    if len(rungs) < 3 or enforcement.changes_the_outcome(rungs[0]) or not enforcement.changes_the_outcome(rungs[-1]):
        raise Violated(
            f"the ladder runs {rungs}: a cliff edge with extra steps, not a spectrum. The bottom "
            "rung must change the outcome and the top one must not, or grading buys nothing"
        )
    intervening = [g for g in rungs if enforcement.changes_the_outcome(g)]
    if len(intervening) < 2:
        raise Violated(
            f"only {intervening} changes the outcome, so {rungs[-1]!r} is the mechanism rather than "
            "the bottom rung — which is the cliff edge this ticket exists to remove"
        )
    for rung in rungs:
        validate(
            "response",
            {
                "id": "a-control", "name": "A control", "addresses": "foundry-services",
                "cost": {"min": 1, "mode": 2, "max": 3},
                "enforcement": {"grade": rung, "point": "somewhere a decision is taken"},
            },
            f"occupancy check at {rung!r}",
        )

    # -- a rung carries no number, and cannot reach a price -----------------------------------
    priced_rung = dict(enforcement.ladder())
    priced_rung["grades"] = [{**dict(enforcement.ladder()["grades"][0]), "reduction": 0.4}]
    scratch = ctx.tmp / "priced-rung.yaml"
    scratch.write_text(yaml.safe_dump(priced_rung), encoding="utf-8")
    try:
        enforcement.ladder(scratch)
    except enforcement.EnforcementError:
        pass
    else:
        raise Violated(
            "a rung carrying a reduction was admitted. A number on a rung is credit nobody "
            "evidenced: tighten the rung, earn more. The £ comes from the control's own graded "
            "mitigation claim and from nowhere else."
        )
    for banned in ({"reduction": {"min": 0, "mode": 0.5, "max": 1}}, {"cost": 5}, {"posture_as_identity": True}):
        try:
            validate(
                "response",
                {
                    "id": "a-control", "name": "A control", "addresses": "foundry-services",
                    "cost": {"min": 1, "mode": 2, "max": 3},
                    "enforcement": {"grade": rungs[-1], "point": "an enforcement point", **banned},
                },
                "planted",
            )
        except SchemaError:
            continue
        raise Violated(
            f"a control declared {sorted(banned)} inside its enforcement block. A price there is a "
            "rung that buys credit; a declared posture-as-identity is the philosophy decision "
            "ticket 18 Q4 refused, asserted by the party it flatters"
        )

    repo = ModelRepo.open(ctx.repo_dir)
    intel = Overlay.load(repo, "intel")
    control = dict(intel.responses["pin-the-tooling-image-set"])
    at_loosest = dict(control, enforcement={**control["enforcement"], "grade": rungs[0]})
    if options.Option.of(control) != options.Option.of(at_loosest):
        raise Violated(
            "the same control produces a different Option at a different rung, so the rung reaches "
            "the pre-filter and therefore the price. Graded enforcement would then be a multiplier "
            "the £ engine never agreed to."
        )

    # -- posture-as-identity: computed from two facts, and excluded by name otherwise ----------
    admitted = enforcement.posture_as_identity(control)
    if not admitted["admitted"]:
        raise Violated(
            f"the fixture's machine-enforceable control is excluded as {admitted['excluded_as']!r}, "
            "so the supported case is asserted nowhere and the narrowing is a refusal of everything"
        )
    unstamped = dict(control, enforcement={k: v for k, v in control["enforcement"].items() if k != "stamped_by"})
    observing = dict(intel.responses["report-node-schedule-variance"])
    lever = dict(intel.responses["report-node-schedule-variance"])
    lever.pop("enforcement")
    for subject, expected in ((unstamped, 2), (observing, 1), (lever, 0)):
        verdict = enforcement.posture_as_identity(subject)
        if verdict["admitted"] or verdict["excluded_as"] != enforcement.POSTURE_EXCLUSIONS[expected]["case"]:
            raise Violated(
                f"a control that should be excluded as "
                f"{enforcement.POSTURE_EXCLUSIONS[expected]['case']!r} came back as {verdict}. "
                "Posture-as-identity survives only where the evidence supports it, and each "
                "unsupported case is named rather than silently admitted"
            )

    # -- a rung moves only with a record, and the record is git-versioned ----------------------
    moved = ctx.tmp / "moved-repo"
    if not moved.exists():
        fixtures.build(moved)
        fixtures.plant_unrecorded_enforcement_move(moved)
    moved_repo = ModelRepo.open(moved)
    moved_overlay = Overlay.load(moved_repo, "intel")
    found = enforcement.history_violations(
        moved_repo, moved_overlay.ref.path, moved_overlay.ref.tree, moved_overlay.enforcement_moves
    )
    if not found:
        raise Violated(
            "a control was tightened to the bottom rung in a commit with no move event covering "
            "it, and nothing noticed. The chain check cannot see this, so the git history is the "
            "only thing that can"
        )

    # -- the published posture is authored, so somebody is accountable for where a control sits --
    posture = enforcement.artefact(repo, "intel", verbs.command_for("enforcement", org="intel"))
    if posture.mark != AUTHORED:
        raise Violated(
            "the enforcement posture is not authored, so nothing requires a human signature on it "
            "— and 'moving a control between grades is a signed change' has nobody behind it"
        )
    problems = attest.check(attest.build(posture, []), posture.to_bytes(), material=b"invariant-suite-key")
    if not any("no human signature" in problem for problem in problems):
        raise Violated(
            f"an unsigned authored posture raised {problems or 'nothing'} — an authored artefact "
            "with no human signature has nobody accountable for it, and the sidecar must say so"
        )

    return (
        f"{len(rungs)} rungs, {len(intervening)} of them changing the outcome; a priced rung and a "
        f"priced enforcement block are both refused; the same control is one Option at {rungs[0]!r} "
        f"and at {rungs[-1]!r}; posture-as-identity admitted for 1 control and excluded by name for "
        f"3, of {len(enforcement.POSTURE_EXCLUSIONS)} named cases; {len(found)} unrecorded move(s) "
        "caught in git history; the posture is authored and unsigned reads as unsigned"
    )


@harness_check("enactment_is_sensed_and_corroboration_sets_the_grade")
def _enactment_is_sensed_and_corroboration_sets_the_grade(ctx: Context) -> str:
    """Enactment reaches the model through the ordinary sensing path, and no channel prices alone (68).

    A guard on the suite rather than an invariant, for the reason build tickets 66 and 67's are:
    the constitution names sixteen invariants and may not grow a seventeenth without the
    constitution changing first.

    **The leg that matters is the one about self-corroboration.** Decision ticket 18 Q3 admits
    declarations as sensor inputs precisely because corroboration is what sets the weight, and the
    incentive that produces — be verifiable rather than be watched — survives only while a subject
    cannot corroborate itself. So the assertion is that a claim set made entirely of the subject's
    own channels never reaches a price-eligible grade, however many channels it uses and however
    many times each one speaks.

    **"No enactment-specific pipeline" is asserted structurally, not by a name screen.** The
    assertion is that the same `sense()` call emits the same artefact kind for a signal that binds
    to a component and for one that binds to a response, and that the enactment lives in the
    overlay's ordinary `signals` and `claims` collections. A parallel pipeline would have to show
    up as a second verb, a second artefact kind or a second collection, and there is none.
    """
    import copy

    from .. import corroboration, evidence, verbs
    from ..model import Overlay
    from ..repo import ModelRepo
    from ..schema import SchemaError, validate

    CORROBORATED, SELF_DECLARED = "pin-the-tooling-image-set", "report-node-schedule-variance"
    DECLARED_SIGNAL, COMPONENT_SIGNAL = "tooling-pins-declared-in-place", "foundry-segment-loss-disclosed"

    # -- no channel prices alone, and a table where one does is refused ----------------------
    channels = corroboration.channel_ids()
    pricing_alone = sorted(c for c in channels if evidence.may_price(corroboration.alone_grade(c)))
    if pricing_alone:
        raise Violated(
            f"channel(s) {', '.join(pricing_alone)} price alone. Every channel observes a proxy "
            "for 'this response was enacted', and the step from proxy to enactment is unevidenced "
            "in any single instance — a channel that skips corroboration makes the rule decorative"
        )
    scratch = ctx.tmp / "enactment-channels"
    scratch.mkdir(parents=True, exist_ok=True)
    for index, mutate in enumerate((
        lambda d: d["channels"][1].update(alone=evidence.threshold()),
        lambda d: d["channels"][0].update(required_for_price=True),
        lambda d: next(c for c in d["channels"] if c["observes_people"]).pop("admission"),
    )):
        doc = copy.deepcopy(corroboration.table())
        mutate(doc)
        path = scratch / f"mutated-{index}.yaml"
        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        try:
            corroboration.table(path)
        except corroboration.CorroborationError:
            continue
        raise Violated(
            f"the channel table admitted mutation {index}: a channel that prices alone, a channel "
            "carrying a field that could privilege it, or a channel that observes people and walks "
            "no admission ladder. Each one is a rule this table exists to hold."
        )

    # -- a subject cannot corroborate itself, however many of its own channels it uses --------
    doubled = copy.deepcopy(corroboration.table())
    twin_channel = copy.deepcopy(next(c for c in doubled["channels"] if c["declared_by_subject"]))
    twin_channel["channel"] = "self-declaration-elsewhere"
    doubled["channels"].append(twin_channel)
    doubled_path = scratch / "two-subject-channels.yaml"
    doubled_path.write_text(yaml.safe_dump(doubled, sort_keys=False), encoding="utf-8")
    self_only = corroboration.corroborate(
        [
            {"id": "one", "channel": "self-declaration"},
            {"id": "two", "channel": "self-declaration"},
            {"id": "three", "channel": "self-declaration-elsewhere"},
        ],
        doubled_path,
    )
    if self_only["independent_channels"] != 1 or self_only["may_price"]:
        raise Violated(
            f"three of the subject's own claims across two of its own channels reached "
            f"{self_only['independent_channels']} independent channel(s) at grade "
            f"{self_only['evidence_grade']}. A subject that can corroborate itself makes the "
            "cheapest route to credit 'say it again', which inverts the whole incentive"
        )

    # -- reconciliation state is one channel among several ------------------------------------
    machine = [c for c in channels if not corroboration.channel(c)["declared_by_subject"]]
    if "reconciliation-state" not in machine or len(machine) < 2:
        raise Violated(
            "reconciliation state is not among the independent channels, or it is the only one — "
            "either way build ticket 65's open verdict has been decided here by fiat"
        )
    def pair(other: str) -> int:
        """The grade a declaration plus one machine channel reaches."""
        graded = corroboration.corroborate(
            [{"id": "a", "channel": "self-declaration"}, {"id": "b", "channel": other}]
        )
        return int(graded["evidence_grade"])

    reconciled = pair("reconciliation-state")
    differing = sorted(c for c in machine if c != "reconciliation-state" and pair(c) != reconciled)
    if differing:
        raise Violated(
            f"swapping the reconciler for {', '.join(differing)} changes the grade, so "
            "reconciliation state is privileged after all — before the verdict that would justify it"
        )

    # -- the fixture's two cases: corroborated prices, self-declared does not ------------------
    repo = ModelRepo.open(ctx.repo_dir)
    intel = Overlay.load(repo, "intel")
    corroborated = corroboration.state(intel, CORROBORATED)
    declared = corroboration.state(intel, SELF_DECLARED)
    if not corroborated["may_price"] or corroborated["evidence_grade"] >= corroborated["strongest_alone"]:
        raise Violated(
            f"a response observed by {corroborated['independent_channels']} independent channel(s) "
            f"grades {corroborated['evidence_grade']} against a strongest-alone of "
            f"{corroborated['strongest_alone']} — corroboration buys nothing, so the channels are "
            "a taxonomy rather than a mechanism"
        )
    if declared["may_price"]:
        raise Violated(
            "an uncorroborated self-declaration reached a price-eligible grade, so declaring that "
            "you acted earns the same credit as being seen to"
        )

    # -- the grade is computed: no claim may name its own --------------------------------------
    planted = {
        "id": "an-enactment", "kind": "enactment", "signal": "a-signal", "response": "a-response",
        "channel": "self-declaration", "evidence_grade": evidence.threshold(),
        "claimed_by": "model-steward", "evidence": "They said so.",
    }
    try:
        validate("claim", planted, "planted")
    except SchemaError:
        pass
    else:
        raise Violated(
            "a self-declaration typed itself at a price-eligible grade. A claim free to name its "
            "own rung makes the corroboration rule advisory"
        )

    # -- one verb, one artefact kind, one set of collections -----------------------------------
    emitted = {
        signal: verbs.sense(repo, ctx.caps, "intel", signal, verbs.command_for("sense", signal=signal))
        for signal in (DECLARED_SIGNAL, COMPONENT_SIGNAL)
    }
    kinds = {artefact.kind for artefact in emitted.values()}
    if kinds != {verbs.KIND_BOUND_SIGNAL}:
        raise Violated(
            f"sensing a component binding and an enactment produced {sorted(kinds)}. A second "
            "artefact kind is a second pipeline wearing the first one's name"
        )
    for claim in corroboration.claims_for(intel, CORROBORATED):
        if claim["id"] not in intel.claims or str(claim["signal"]) not in intel.signals:
            raise Violated(
                f"enactment claim {claim['id']!r} or its signal lives outside the overlay's "
                "ordinary claims and signals collections — which is the parallel record type "
                "decision ticket 18 Q3 refused"
            )
    if not emitted[DECLARED_SIGNAL].body["action_state"] or emitted[COMPONENT_SIGNAL].body["action_state"]:
        raise Violated(
            "the action state is emitted for the wrong signal: a component binding reports one, or "
            "an enactment reports none. The loop's read side is the whole point of the ticket"
        )

    return (
        f"{len(channels)} channels, none pricing alone ({len(machine)} independent of the "
        f"subject); a table that prices alone, one carrying a privileging field and a "
        f"people-observing channel with no admission ladder are all refused; three self-declared "
        f"claims across two of the subject's own channels stay at 1 independent channel and grade "
        f"{self_only['evidence_grade']}; the reconciler is interchangeable with "
        f"{len(machine) - 1} other machine channel(s); the fixture's corroborated response grades "
        f"{corroborated['evidence_grade']} from a strongest-alone of {corroborated['strongest_alone']} "
        f"and prices, its self-declared one grades {declared['evidence_grade']} and does not; a "
        f"claim naming its own grade is refused; both signal kinds sense to {verbs.KIND_BOUND_SIGNAL}"
    )


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


@harness_check("substrate_regeneration_is_not_deterministic_so_it_is_authored")
def _substrate_regeneration_is_not_deterministic_so_it_is_authored(ctx: Context) -> str:
    """The authored-or-derived spike (build ticket 48, decision tickets 12 and 14): regenerated
    substrate is classified `authored`, and the reasons this holds are checked, not narrated.

    A guard on the suite rather than an invariant, the same shape `causal_accounts_have_no_privileged_default`
    is: this asserts a **semantic property of the spike's own finding**, not one of the
    constitution's fixed sixteen.

    Four legs. First, the toy demonstration of what "derived" would require: a pure, seeded
    generator with no external entropy reproduces byte-for-byte from the identical recipe, every
    time. Second, the tension the ticket names: a stand-in for a live model call — drawing on
    entropy the recipe cannot pin, the one honest thing an API call actually is — does **not**
    reproduce from the identical recipe, which is why `identical_pins_identical_bytes` cannot be
    asserted for real substrate generation. Third, the boundary made explicit: an artefact carrying
    substrate content itself, marked `authored`, accepts a human signature, while a derived
    artefact that only references the substrate by content hash still refuses one —
    `derived_never_human_signed` (build ticket 11) checked against this new case, not merely
    unchanged by omission. Fourth, the "twin verify attempt": a `sense` artefact pinning a real,
    non-empty substrate reference reproduces cleanly from its pins alone, without the substrate
    bytes ever being written anywhere `twin` can read them — the reference participates in
    derivation, the bytes behind it never do.
    """
    import tempfile

    from .. import attest, cli, sign, verbs
    from ..artefact import AUTHORED, DERIVED, Artefact
    from ..attest import AttestationError
    from ..blob import BlobRef
    from ..reproduce import reproduce
    from ..repo import ModelRepo
    from ..substrate import SubstrateRecipe, generate_deterministic, generate_non_reproducible

    recipe = SubstrateRecipe(
        id="guard-recipe", seed=11, templates=("a mundane line", "another mundane line"),
        model_version="toy-model-v1",
    )
    if generate_deterministic(recipe) != generate_deterministic(recipe):
        raise Violated("the pure, seeded generator did not reproduce from the identical recipe")
    if generate_non_reproducible(recipe) == generate_non_reproducible(recipe):
        raise Violated(
            "the stand-in live-model generator reproduced from the identical recipe twice in a "
            "row — the tension this spike exists to demonstrate has gone missing"
        )

    payload = generate_deterministic(recipe)
    ref = BlobRef.of(payload)
    batch = Artefact(
        kind="substrate-batch", mark=AUTHORED, command=["twin", "substrate"],
        pins={"recipe_id": recipe.id}, depth={}, body={"substrate": str(ref)},
    )
    attest.build(batch, [sign.human("model-steward", batch.digest(), b"guard-key")])

    referencing = Artefact(
        kind="bound-signal", mark=DERIVED, command=["twin", "sense"],
        pins={"substrate": str(ref)}, depth={}, body={},
    )
    try:
        attest.build(referencing, [sign.human("model-steward", referencing.digest(), b"guard-key")])
    except AttestationError:
        pass
    else:
        raise Violated("a derived artefact referencing substrate by hash accepted a human signature")

    signal_dir = ctx.tmp / "substrate-guard-repo"
    if not signal_dir.exists():
        fixtures.build(signal_dir)
        (signal_dir / "orgs" / "intel" / "signals" / "toy-substrate-signal.yaml").write_text(
            f"id: toy-substrate-signal\ndate: '2024-08-02'\nsteep: economic\n"
            f"source: toy substrate spike\nstatement: A planted signal inside the toy substrate.\n"
            f"substrate: {ref}\nprovenance:\n  observed_by: fixture\n"
            f"  url: https://example.invalid/fixture/toy-substrate\n",
            encoding="utf-8",
        )
        (signal_dir / "orgs" / "intel" / "claims" / "bind-toy-substrate-signal.yaml").write_text(
            "id: bind-toy-substrate-signal\nkind: binding\nsignal: toy-substrate-signal\n"
            "component: foundry-services\nevidence_grade: 5\n"
            "claimed_by: fixture-author (human)\nevidence: Reading of the toy substrate.\n",
            encoding="utf-8",
        )
        fixtures.git(signal_dir, "add", "-A")
        fixtures.git(signal_dir, "commit", "-q", "-m", "toy substrate signal")

    with tempfile.TemporaryDirectory(prefix="twin-substrate-guard-") as scratch:
        out = Path(scratch) / "bound-signal.json"
        rc = cli.main(
            ["sense", "--repo", str(signal_dir), "--org", "intel",
             "--signal", "toy-substrate-signal", "--out", str(out)]
        )
        if rc != 0:
            raise Violated("emitting the substrate-referencing sense artefact failed")
        report = reproduce(str(signal_dir), str(out))
        if not report.reproduces:
            raise Violated(f"the substrate-referencing artefact did not reproduce from its pins: {report.diff}")

    return (
        "the pure seeded generator reproduces from an identical recipe; the stand-in live-model "
        "generator does not; an authored substrate batch accepts a human signature and a derived "
        "reference to it still refuses one; a substrate-referencing sense artefact reproduces from "
        "its pins with the substrate bytes never written anywhere twin can read them"
    )


@harness_check("twin_self_reference_is_cut_not_recursed")
def _twin_self_reference_is_cut_not_recursed(ctx: Context) -> str:
    """The twin inside the twin (build ticket 63, decision ticket 10, Q1): "self-modelling
    terminates at depth 1 — the twin appears as components and its risks are priced, but it does
    not model 'the twin modelling the twin' as a further layer. Graph traversal detects and cuts
    self-referential cycles."

    A guard on the suite rather than an invariant, the same shape `causal_accounts_have_no_privileged_default`
    and `drift_window_was_declared_before_it_was_measured` are: this asserts a **semantic property
    of the twin's own fixture**, not one of the constitution's fixed sixteen.

    Two legs. First, the structural half: a component's schema carries no field by which a further
    nested "twin modelling this twin" layer could even be attached — the schemas are closed, so a
    planted field for one does not load, the identical mechanism `no_special_category_slot` uses
    for a different absence. Second, the traversal half, on the twin's own fixture
    (`fixtures.build_twin_self_org`): `the-twin-model` and `the-twin-adoption` close a genuine
    two-node causal cycle (accuracy earns adoption; adoption sustains the model), and propagating
    from either origin reaches the other exactly once — the return leg, a depth-2 attempt, is cut
    by `twin/propagate.py`'s existing simple-path rule (build ticket 21) rather than recursed, and
    the cut is disclosed (`truncated: true`, the cycle named in `known_limits`) rather than silent.
    """
    from .. import fixtures
    from ..model import Overlay
    from ..propagate import propagate
    from ..repo import ModelRepo
    from ..schema import SchemaError, validate

    base = {"id": "the-twin-model", "name": "The twin's own engine", "kind": "capability"}
    for planted in ("models_graph", "nested_twin", "twin_of"):
        try:
            validate("component", {**base, planted: "x"}, "planted")
        except SchemaError:
            pass
        else:
            raise Violated(f"a component carrying a planted {planted!r} field validated")

    repo_dir = ctx.tmp / "twin-self"
    if not repo_dir.exists():
        fixtures.build_twin_self_org(repo_dir)
    overlay = Overlay.load(ModelRepo.open(repo_dir), fixtures.TWIN_SELF_ORG)
    graph = overlay.graph()

    for origin, expect in (("the-twin-model", "the-twin-adoption"), ("the-twin-adoption", "the-twin-model")):
        body = propagate(graph, origin)
        reached = [r["component"] for r in body["reached"]]
        if reached != [expect]:
            raise Violated(f"propagating from {origin!r} reached {reached}, expected [{expect!r}]")
        if body["traversal"]["truncated"] is not True:
            raise Violated(
                f"propagating from {origin!r} through the twin's own self-referential cycle did "
                "not report truncated — a depth-2 attempt recursed instead of being cut"
            )
        if not any("cyclic" in limit for limit in body["traversal"]["known_limits"]):
            raise Violated(
                f"propagating from {origin!r} was truncated but the cycle is not named in "
                f"known_limits: {body['traversal']['known_limits']}"
            )

    return (
        "a component carrying a planted models_graph/nested_twin/twin_of field is refused at "
        "load; propagating the twin's own fixture from either side of its self-referential cycle "
        "reaches the other component exactly once and the return leg is cut, disclosed, not silent"
    )


@harness_check("ethics_gate_ladder_stops_early_and_fast_improvement_is_never_an_automatic_finding")
def _ethics_gate_ladder_stops_early_and_fast_improvement_is_never_an_automatic_finding(ctx: Context) -> str:
    """`ethics-gate` (build ticket 47, decision ticket 15 Q1/Q2): the sensor admission ladder
    stops at its first failing rung rather than evaluating the rest, and a fast-improvement flag
    can never become an adverse finding without a human's own adjudication, attached to a
    registered role — the same structural-plus-live shape the other five skill guards use.

    Five legs. First, the ladder genuinely stops: a necessity/proportionality payload that would
    raise if ever read (empty dicts, missing the keys `_check_necessity`/`_check_proportionality`
    require) sits behind a failing purpose rung, and `walk_ladder()` does not raise — proving the
    later rungs were never called, not merely that the reported result happens to be right.
    Second, the positive leg of the same property: a fully-passing walk carries a non-empty
    `justification` on every evaluated rung, so "recorded justification per rung" is checked
    against real output. Third, `flag_fast_improvement()`'s own output carries no action- or
    verdict-shaped field or phrase — the identical banned-word/phrase scan
    `no_recommended_action_field` runs, re-asserted against a fourth artefact
    (`trade_off_curve_reports_disagreement_never_a_scalar` was the second,
    `gameplay_lens_is_grade_5_and_reports_no_recommendation` the third). Fourth,
    `adjudicate_fast_improvement()` refuses to run against a flag that was never raised and
    refuses an unregistered role, checked against the real role register
    (`twin/roles.yaml`) rather than trusted from a docstring. Fifth, the real labelled corpus (the
    same five sensor proposals `tests/test_ethics_gate.py` evaluates against, built fresh here)
    passes its threshold and a skill that admits everything fails it — a harness with no subject
    proves nothing.
    """
    from . import NO_ACTION_BANNED_KEYS, NO_ACTION_BANNED_PHRASES
    from .. import ethics_gate as eg
    from .. import skills as skills_mod
    from ..canon import walk_keys, walk_values
    from ..sign import role_ids

    poison: dict[str, Any] = {}
    stopped = eg.walk_ladder(
        {"purpose": {"scenario": "", "will_act": False}, "necessity": poison, "proportionality": poison}
    )
    if stopped["admitted"] or stopped["stopped_at"] != "purpose" or len(stopped["rungs"]) != 1:
        raise Violated(f"the ladder did not stop cleanly at the first failing rung: {stopped}")

    passing = eg.walk_ladder(
        {
            "purpose": {"scenario": "s", "will_act": True},
            "necessity": {"kind": "structural", "level": "aggregate", "alternatives": []},
            "proportionality": {"intrusion_cost": 10.0, "value_illuminated": 1000.0},
        }
    )
    if not passing["admitted"] or not all(r["justification"] for r in passing["rungs"]):
        raise Violated(f"a fully-passing ladder walk is missing a justification somewhere: {passing}")

    flag = eg.flag_fast_improvement({"sensor": {"id": "guard-sensor"}, "baseline": 10.0, "current": 30.0})
    if not flag["flagged"]:
        raise Violated("a 200% improvement did not flag at the default threshold — this leg needs a raised flag")
    for key in walk_keys(flag):
        if any(word in key.lower() for word in NO_ACTION_BANNED_KEYS):
            raise Violated(f"flag_fast_improvement()'s own output carries an action/verdict-shaped field ({key})")
    for key, value in walk_values(flag):
        if isinstance(value, str) and any(phrase in value.lower() for phrase in NO_ACTION_BANNED_PHRASES):
            raise Violated(f"flag_fast_improvement() states an action in prose at {key}: {value!r}")

    try:
        eg.adjudicate_fast_improvement({"sensor": "guard-sensor", "flagged": False}, "model-steward", "clear", "reviewed")
    except eg.EthicsGateError:
        pass
    else:
        raise Violated("adjudicate_fast_improvement() ran against a clear (unflagged) input")
    try:
        eg.adjudicate_fast_improvement(flag, "nobody-in-the-register", "genuine improvement", "reviewed")
    except eg.EthicsGateError:
        pass
    else:
        raise Violated("adjudicate_fast_improvement() accepted a claimed_by not in the role register")
    adjudicated = eg.adjudicate_fast_improvement(flag, "model-steward", "genuine improvement", "reviewed the underlying data")
    if adjudicated["claimed_by"] not in role_ids():
        raise Violated("the adjudication's own claimed_by is not in the role register")

    corpus = eg.labelled_corpus()
    good = skills_mod.evaluate(eg.SKILL, eg.admit, corpus, scorer=eg.scorer)
    if not good.passed:
        raise Violated("ethics-gate failed its own labelled corpus running correctly — the harness has no subject")
    bad = skills_mod.evaluate(
        eg.SKILL, lambda payload: {"admitted": True, "ladder": {"stopped_at": None}}, corpus, scorer=eg.scorer,
    )
    if bad.passed:
        raise Violated("a skill that admits everything still passed — the threshold is not gating anything")

    return (
        "the ladder stops at its first failing rung without touching the rest; a fully-passing "
        "walk carries a justification on every rung; flag_fast_improvement() carries no "
        "action/verdict-shaped field or phrase; adjudication refuses an unflagged input and an "
        f"unregistered role; the real {len(corpus)}-item labelled corpus passes and a skill that "
        "admits everything fails its threshold"
    )


@harness_check("does_not_do_register_is_generated_never_typed")
def _does_not_do_register_is_generated_never_typed(ctx: Context) -> str:
    """The does-not-do register turns decision ticket 15's published-scope-exclusions device on
    the demo itself (build ticket 77, decision tickets 15 and 22): what a viewer is shown must
    never silently drift from what the depth-grade checklists actually say.

    One leg, checked by mutation rather than by reading the module's source for the absence of a
    file constant: checking one criterion off in a capability's own checklist has to remove
    exactly its entry from the register. A cached or hand-maintained list that happened to agree
    with the checklists today would pass every other check in this suite and still fail this one
    the moment a checklist changed under it.
    """
    import dataclasses

    from ..canon import digest_of
    from ..does_not_do import register
    from ..grades import Capabilities

    caps = ctx.caps
    before = register(caps)
    graded = next((g for g in caps if g.unchecked), None)
    if graded is None:
        raise Skip("every loaded capability is already `full`; there is nothing left to check off")
    target = graded.unchecked[0]
    ticked = dataclasses.replace(target, checked=True, evidence="guard-plant", ticked_by="guard")
    patched_criteria = tuple(ticked if c.index == target.index else c for c in graded.criteria)
    patched_grade = dataclasses.replace(graded, criteria=patched_criteria)
    patched = {
        g.capability: (patched_grade if g.capability == graded.capability else g) for g in caps
    }
    # Recomputed, not `caps.digest` carried over: that digest is `digest_of` the *unpatched*
    # summaries (`grades.py`'s own `Capabilities.load`), and reusing it here would hand back a
    # `Capabilities` instance whose own digest lies about the criteria it actually holds.
    patched_digest = digest_of({name: g.summary() for name, g in sorted(patched.items())})
    after = register(Capabilities(patched, patched_digest))

    if len(before) - len(after) != 1:
        raise Violated(
            f"checking off {graded.capability} AC {target.index} changed the register by "
            f"{len(before) - len(after)} entries, not 1 — it is not tracking the checklist live"
        )
    survivor = f"{graded.capability}-{target.index}"
    if any(e["id"] == survivor for e in after):
        raise Violated(f"{survivor} survived in the register after its criterion was checked off")
    return f"{len(before)} unchecked criteria registered; checking one off removed exactly it"


@harness_check("the_demo_sequence_earns_credibility_before_it_spends_it")
def _the_demo_sequence_earns_credibility_before_it_spends_it(ctx: Context) -> str:
    """Decision ticket 22's resolved thesis order — falsifiability (b), then versioned governance
    (c), concluding in the one-currency comparison (a) — made structural rather than narrated
    (build ticket 77): "the order IS the argument." CI step ordering drifted from this once
    already (royal-mail, netflix, intel priced the second beat, not the third), so this is checked
    against the beats' own source rather than trusted to stay narrated correctly.

    Three legs, all read off literal text — the same trade-off build ticket 78's own
    orchestrator-consistency checks made, because no bash parser exists here to do better.
    `beat-sequence.sh` names the three beats in the declared order; neither `beat-royal-mail.sh`
    nor `beat-intel.sh` calls a pricing verb, so £ cannot leak into either falsifiability beat; and
    inside `beat-netflix.sh`, `twin propose` (versioned governance, (c)) is called before both
    `twin price` and `twin trade-off` (the one-currency comparison, (a), which labels both steps),
    so the comparison concludes the beat rather than opening it.

    `tests/test_beat_sequence.py` exercises this exact function through `invariants.run(only=[...])`
    rather than re-implementing the same regex checks a second time — one definition, run from
    both `twin verify` and `pytest -q`.
    """
    sequence = (PACKAGE_DIR / "beat-sequence.sh").read_text(encoding="utf-8")
    names = re.findall(r"beat-(royal-mail|intel|netflix)\.sh", sequence)
    first_seen = list(dict.fromkeys(names))
    if first_seen != ["royal-mail", "intel", "netflix"]:
        raise Violated(
            f"beat-sequence.sh names the beats in order {first_seen}, not the declared "
            "royal-mail, intel, netflix — falsifiability before governance before the comparison"
        )
    for name in ("beat-royal-mail.sh", "beat-intel.sh"):
        text = (PACKAGE_DIR / name).read_text(encoding="utf-8")
        if re.search(r'"\$TWIN"\s+(price|trade-off)\b', text):
            raise Violated(f"{name} calls a pricing verb — £ must not appear before the third beat")
    netflix = (PACKAGE_DIR / "beat-netflix.sh").read_text(encoding="utf-8")
    propose_at = netflix.find('"$TWIN" propose')
    price_at = netflix.find('"$TWIN" price')
    trade_off_at = netflix.find('"$TWIN" trade-off')
    if -1 in (propose_at, price_at, trade_off_at):
        raise Violated("beat-netflix.sh no longer calls all three of propose, price and trade-off")
    if propose_at > price_at or propose_at > trade_off_at:
        raise Violated(
            "beat-netflix.sh prices or trades off before it proposes — (a) is not sequenced after (c)"
        )
    return (
        "royal-mail, intel, netflix in that order; £ absent from the first two beats; propose "
        "precedes both price and trade-off in the third"
    )


@harness_check("mitigation_credit_is_gated_on_corroborated_enactment_not_just_claimed_evidence")
def _mitigation_credit_is_gated_on_corroborated_enactment_not_just_claimed_evidence(
    ctx: Context,
) -> str:
    """The action-state feedback path that closes decision ticket 08's conditional-forecast loop
    (build ticket 86, decision ticket 18 AC 5).

    A guard on the suite rather than an invariant, for the reason build tickets 66, 67 and 68's
    are: the constitution names sixteen invariants and may not grow a seventeenth without the
    constitution changing first.

    Build ticket 68 built the read side: `corroboration.state(overlay, response)` answers whether
    a recommendation was actually acted upon, and how well evidenced that is. Nothing consumed it
    — `pricing._credit()` computed mitigation credit purely from the response's own `mitigates`
    claim and its own evidence grade. **The leg that matters is that the two causal claims are
    checked separately**: a response can be evidenced well enough to price and still earn nothing,
    because "this removes part of the impact" and "this was actually done" are different
    assertions and only one of them used to be gated. The assertion is that an identical claim
    scores differently depending only on the option's own corroborated enactment state, and that
    this holds through the live artefact path (`verbs.price`), not only inside the unit function.
    """
    from .. import fixtures, pricing, verbs
    from ..model import Overlay
    from ..repo import ModelRepo

    # -- the same claim, credited or refused purely on the option's own enactment state -------
    repo = ModelRepo.open(ctx.repo_dir)
    intel = Overlay.load(repo, "intel")
    claim = {
        "component": "a-component", "reduction": {"min": 0.1, "mode": 0.2, "max": 0.3},
        "evidence_grade": 2, "basis": "identical claim, planted for the harness guard",
    }
    priced = [{"component": "a-component",
               "price": {"attenuated": {"min": 100.0, "mode": 200.0, "max": 300.0}}}]
    corroborated = pricing._credit({"option": "pin-the-tooling-image-set"}, claim, priced, intel)
    self_declared = pricing._credit(
        {"option": "report-node-schedule-variance"}, claim, priced, intel
    )
    if "credit" not in corroborated or self_declared.get("reason") != pricing.NOT_ENACTED:
        raise Violated(
            f"the identical claim produced {corroborated} against a corroborated option and "
            f"{self_declared} against an uncorroborated one — the gate is not distinguishing them"
        )
    if self_declared.get("reason") == pricing.CLAIM_TOO_WEAK:
        raise Violated(
            "an uncorroborated option's refusal read as the claim's own grade being too weak. "
            "It is grade 2, well inside the pricing threshold — conflating the two reasons would "
            "make a corroborated claim indistinguishable from an unevidenced one in the artefact"
        )

    # -- the live artefact path threads the same gate, not just the unit function -------------
    def _mitigation(body: dict, option: str, perspective: str) -> dict:
        entry = next(e for e in body["perspectives"] if e["perspective"] == perspective)
        return next(o for o in entry["responses"]["priced"] if o["option"] == option)["mitigation"]

    pocket = ctx.tmp / "pocket-with-enactment"
    if not pocket.exists():
        fixtures.build_pocket_org(pocket)
    live = verbs.price(
        ModelRepo.open(pocket), ctx.caps, "pocket", "order-service", None,
        verbs.command_for("price", org="pocket", origin="order-service"),
    ).body
    if "credit" not in _mitigation(live, "retrain-the-on-call-rota", "the-operator"):
        raise Violated(
            "retrain-the-on-call-rota earns no credit against its own fixture, which carries "
            "corroborated enactment for it — either the gate or the fixture regressed"
        )

    # -- strip the corroborating enactment claims, and the same response is refused -----------
    scratch = ctx.tmp / "pocket-no-enactment"
    if not scratch.exists():
        fixtures.build_pocket_org(scratch)
        for stray in (
            "orgs/pocket/claims/enacted-rota-retrained-declared.yaml",
            "orgs/pocket/claims/enacted-rota-runbook-merged.yaml",
        ):
            (scratch / stray).unlink()
        fixtures.git(scratch, "add", "-A")
        fixtures.git(
            scratch, "commit", "-q", "-m", "strip corroborating enactment for the harness guard"
        )
    stripped = verbs.price(
        ModelRepo.open(scratch), ctx.caps, "pocket", "order-service", None,
        verbs.command_for("price", org="pocket", origin="order-service"),
    ).body
    stripped_mitigation = _mitigation(stripped, "retrain-the-on-call-rota", "the-operator")
    if stripped_mitigation.get("reason") != pricing.NOT_ENACTED:
        raise Violated(
            f"stripping retrain-the-on-call-rota's two corroborating enactment claims left the "
            f"mitigation at {stripped_mitigation}, not refused as NOT_ENACTED — the same claim, "
            "the same fixture, the only thing removed was the evidence that it happened"
        )

    return (
        "an identical claim credits against a corroborated option and refuses as "
        "NOT_ENACTED (never CLAIM_TOO_WEAK) against an uncorroborated one; the live price "
        "artefact credits retrain-the-on-call-rota against its own fixture's corroborated "
        "enactment and refuses it the moment that corroboration is stripped from the same fixture"
    )


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
        # A check's own stderr is noise unless the check fails: several guards drive `twin`
        # verbs that are *meant* to refuse, and their `VerbError:` lines read as an uncaught
        # crash in a green run (Appendix E of the 2026-08-27 drift review). Keep the tail for the
        # FAIL detail; drop it on PASS. A check that runs past CHECK_TIMEOUT seconds is a FAIL,
        # never a silent hang.
        err = io.StringIO()
        try:
            with redirect_stderr(err), _deadline(name):
                detail = fn(ctx)
        except Skip as exc:
            return Result(number, name, SKIP, str(exc), is_invariant)
        except Violated as exc:
            return Result(number, name, FAIL, f"{exc}{_stderr_tail(err)}", is_invariant)
        except Exception as exc:  # a check that errors is a check that did not assert
            return Result(
                number, name, FAIL, f"{type(exc).__name__}: {exc}{_stderr_tail(err)}", is_invariant
            )
        return Result(number, name, PASS, detail, is_invariant)


CHECK_TIMEOUT = int(os.environ.get("TWIN_CHECK_TIMEOUT", "600"))


class TimedOut(Exception):
    pass


@contextmanager
def _deadline(name: str) -> Iterator[None]:
    """Fail a check that overruns CHECK_TIMEOUT. SIGALRM only: main thread, POSIX."""
    if CHECK_TIMEOUT <= 0 or threading.current_thread() is not threading.main_thread():
        yield
        return

    def _fire(signum: int, frame: Any) -> None:
        raise TimedOut(f"{name} ran past {CHECK_TIMEOUT}s")

    previous = signal.signal(signal.SIGALRM, _fire)
    signal.alarm(CHECK_TIMEOUT)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _stderr_tail(buf: io.StringIO, lines: int = 5) -> str:
    tail = [line for line in buf.getvalue().splitlines() if line.strip()][-lines:]
    return ("\n    stderr: " + "\n    stderr: ".join(tail)) if tail else ""


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
