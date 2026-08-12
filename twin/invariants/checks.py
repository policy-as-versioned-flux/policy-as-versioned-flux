"""The live invariant checks.

Each asserts on external behaviour at a boundary — an emitted artefact, a validated claim, a
score — never on internal structure. A test coupled to internals becomes the sunk cost that
resists the rewrite, which is one of the three named failure modes.

Whole-module source is hashed into the manifest alongside each check body, so a helper cannot be
weakened to make a check pass without the manifest noticing.
"""

from __future__ import annotations

import inspect
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .. import REPO_DIR
from .. import artefact as artefact_mod
from .. import attest, fixtures, index, sign, verbs
from .. import constraints as constraints_mod
from ..artefact import AUTHORED, DERIVED, Artefact, ArtefactError
from ..canon import canonical_json, sha256_hex, walk_keys
from ..grades import Capabilities, GradeError
from ..model import Overlay, check_direction
from .. import schema as schema_mod
from ..repo import ModelRepo
from . import NO_ACTION_BANNED_KEYS, NO_ACTION_BANNED_PHRASES, Violated, invariant


def load_manifest():  # noqa: ANN201 - re-exported lazily to avoid a circular import at module load
    from .harness import load_manifest as _load

    return _load()

if TYPE_CHECKING:  # pragma: no cover
    from .harness import Context

GOLDEN_PATH = Path(__file__).resolve().parent / "golden-digests.json"

NETFLIX = "netflix"
SIGNAL = "price-separation-announced"
SCENARIO = "dvd-decline-2011"
OUTCOME = "dvd-decline-2011-resolved"
# The regime the shared subjects run under (build ticket 36). Named rather than omitted, because
# there is no default: `only_as_consumed_scores` needs a scoring-eligible bundle, so this is the
# one that produces one, and the regimes that do not are exercised where that is the point.
REGIME = "as-consumed"
# The blast-radius subject (build ticket 19). From the delivery network, one component is
# reachable through a fully-graded causal path and one is reachable only through a grade-5 model
# assertion — so the fixture exercises the gate in both directions rather than one.
BLAST_ORIGIN = "content-delivery-network"
GRADE_5_ONLY = "brand-goodwill"
# The propagation subject (build ticket 20). Same origin as the blast radius on purpose: the two
# artefacts then describe the same shock, and the difference between what composes and what is
# merely downstream is readable by putting them side by side.
PROPAGATE_ORIGIN = "content-delivery-network"
# The priced impact (build ticket 30). Same origin again, so the propagation, the blast radius and
# the price all describe one shock and a reader can lay them side by side. It is also the origin
# that reaches `brand-goodwill` through a grade-5 assertion and `streaming-experience` through a
# graded path, so the £ gate is exercised in both directions in one artefact.
PRICE_ORIGIN = "content-delivery-network"
# The choice set and its two removals (build ticket 28). One crosses the universal floor and one
# crosses this perspective's own ruin boundary, so both tiers are exercised.
# The subject of the do/observe pair (build ticket 22). It has a cause above it and an effect
# below it, so both operations reach the same components downstream and differ only upstream —
# which is the distinction, with nothing else moving.
QUERY_COMPONENT = "streaming-experience"
# The rewind subject (build ticket 35). Every fixture commit carries one fixed date, so any later
# instant resolves to HEAD on every machine and the emitted state is byte-stable. The dated-change
# case — where rewind reads a number that was later overwritten — is `tests/test_primitives.py`,
# because it needs a second commit at a second date and the fixture is deliberately single-dated.
REWIND_AT = "2026-06-01T00:00:00+00:00"
PERSPECTIVE = "the-operator"
OTHER_PERSPECTIVE = "the-staff-council"
RUIN_CLASS_OPTION = "stake-the-quarter-on-one-title"
FLOOR_OPTION = "instrument-viewers-without-telling-them"


# -- shared subjects -----------------------------------------------------------------------


def emit_all(ctx: "Context", into: str = "artefacts") -> dict[str, tuple[Artefact, Path]]:
    """One of each artefact kind, from the fixture repository. The subjects every check asserts on.

    Memoised per (context, directory). Fifteen checks ask for these and the set is deterministic
    by construction — that is the property half of them are asserting — so re-deriving it fifteen
    times only buys wall-clock. Build ticket 21 made that expensive enough to notice: three more
    artefacts, two of which run a full 2000-draw propagation.

    The determinism legs that *need* a second derivation ask for one by name, with `into` set to
    a different directory, so they still get one.
    """
    cached = ctx.emitted.get(into)
    if cached is not None:
        return cached
    repo = ModelRepo.open(ctx.repo_dir)
    out_dir = ctx.tmp / into
    out_dir.mkdir(parents=True, exist_ok=True)

    bound = verbs.sense(
        repo, ctx.caps, NETFLIX, SIGNAL, verbs.command_for("sense", org=NETFLIX, signal=SIGNAL)
    )
    bound_path = bound.write(out_dir / "bound-signal.json")

    bundle = verbs.run(
        repo, ctx.caps, NETFLIX, SCENARIO, REGIME,
        verbs.command_for("run", org=NETFLIX, scenario=SCENARIO, regime=REGIME),
    )
    bundle_path = bundle.write(out_dir / "forecast-bundle.json")

    card = verbs.score(
        repo,
        ctx.caps,
        NETFLIX,
        bundle_path,
        OUTCOME,
        verbs.command_for("score", org=NETFLIX, outcome=OUTCOME, forecast_sha256=bundle.digest()),
    )
    card_path = card.write(out_dir / "score-card.json")

    graph = verbs.graph(repo, ctx.caps, NETFLIX, verbs.command_for("graph", org=NETFLIX))
    graph_path = graph.write(out_dir / "graph.json")

    radius = verbs.blast(
        repo, ctx.caps, NETFLIX, BLAST_ORIGIN,
        verbs.command_for("blast", org=NETFLIX, origin=BLAST_ORIGIN),
    )
    radius_path = radius.write(out_dir / "blast-radius.json")

    exposed = verbs.exposure(
        repo, ctx.caps, NETFLIX, SCENARIO, None,
        verbs.command_for("exposure", org=NETFLIX, scenario=SCENARIO),
    )
    exposed_path = exposed.write(out_dir / "scenario-exposure.json")

    moved = verbs.propagate(
        repo, ctx.caps, NETFLIX, PROPAGATE_ORIGIN,
        verbs.command_for("propagate", org=NETFLIX, origin=PROPAGATE_ORIGIN),
    )
    moved_path = moved.write(out_dir / "propagation.json")

    choices = verbs.options(
        repo, ctx.caps, NETFLIX, PERSPECTIVE,
        verbs.command_for("options", org=NETFLIX, perspective=PERSPECTIVE),
    )
    choices_path = choices.write(out_dir / "priced-option-set.json")

    valued = verbs.price(
        repo, ctx.caps, NETFLIX, PRICE_ORIGIN, None,
        verbs.command_for("price", org=NETFLIX, origin=PRICE_ORIGIN),
    )
    valued_path = valued.write(out_dir / "priced-impact.json")

    acted = verbs.intervene(
        repo, ctx.caps, NETFLIX, QUERY_COMPONENT,
        verbs.command_for("intervene", org=NETFLIX, component=QUERY_COMPONENT),
    )
    acted_path = acted.write(out_dir / "intervention.json")

    learned = verbs.observe(
        repo, ctx.caps, NETFLIX, QUERY_COMPONENT,
        verbs.command_for("observe", org=NETFLIX, component=QUERY_COMPONENT),
    )
    learned_path = learned.write(out_dir / "observation.json")

    from ..primitives import rewind

    past = verbs.rewind(
        rewind(ctx.repo_dir, REWIND_AT), ctx.caps, NETFLIX, REWIND_AT,
        verbs.command_for("rewind", org=NETFLIX, at=REWIND_AT),
    )
    past_path = past.write(out_dir / "rewound-model.json")

    emitted = {
        bound.kind: (bound, bound_path),
        bundle.kind: (bundle, bundle_path),
        card.kind: (card, card_path),
        graph.kind: (graph, graph_path),
        radius.kind: (radius, radius_path),
        exposed.kind: (exposed, exposed_path),
        moved.kind: (moved, moved_path),
        choices.kind: (choices, choices_path),
        valued.kind: (valued, valued_path),
        acted.kind: (acted, acted_path),
        learned.kind: (learned, learned_path),
        past.kind: (past, past_path),
    }
    ctx.emitted[into] = emitted
    return emitted


def recompute_digests(ctx: "Context") -> dict[str, str]:
    return {kind: art.digest() for kind, (art, _) in sorted(emit_all(ctx).items())}


def golden_digests() -> dict[str, str]:
    if not GOLDEN_PATH.is_file():
        return {}
    loaded: dict[str, str] = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))["digests"]
    return loaded


def module_hash() -> str:
    """Whole-module hash, so a weakened helper cannot make a check pass unnoticed."""
    lines = [line.rstrip() for line in Path(__file__).read_text(encoding="utf-8").splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return sha256_hex("\n".join(lines).encode("utf-8"))


# -- the invariants ------------------------------------------------------------------------


@invariant("store_rebuildable_from_git")
def _store_rebuildable_from_git(ctx: "Context") -> str:
    """Any derived index can be dropped and rebuilt from the repository alone.

    Extended at build ticket 13 to the aggregates: a roll-up is computed from its constituents on
    read and has **no authored and no stored form**, which is what makes "an aggregate can never
    drift from its constituents" structural rather than a discipline. There is no second copy to
    drift.
    """
    repo = ModelRepo.open(ctx.repo_dir)
    out = ctx.tmp / "derived-index"

    index.write(repo, out)
    first = index.read_digest(out)
    shutil.rmtree(out)
    if out.exists():
        raise Violated("the derived index survived deletion")

    index.write(repo, out)
    second = index.read_digest(out)
    if first != second:
        raise Violated(f"rebuilt index differs: {first[:12]} then {second[:12]}")
    if not (out / "world.json").is_file():
        raise Violated("rebuild produced no world index")

    from ..schema import ROLLUP_FIELDS, SCHEMAS, SchemaError, validate

    for name, schema in SCHEMAS.items():
        declared = (set(schema.required) | set(schema.optional)) & set(ROLLUP_FIELDS)
        if declared:
            raise Violated(f"schema {name!r} declares a slot for an authored aggregate: {', '.join(sorted(declared))}")
    for field in ROLLUP_FIELDS:
        try:
            validate(
                "signal",
                {"id": "planted", "date": "2011-07-12", "steep": "economic", "source": "s",
                 "statement": "t", "provenance": {"observed_by": "x", field: 1}},
                "planted",
            )
        except SchemaError:
            continue
        raise Violated(f"an authored {field!r} validated inside a free-form mapping")

    for path in sorted(out.rglob("*.json")):
        stored = set(_keys(json.loads(path.read_bytes()))) & set(ROLLUP_FIELDS)
        if stored:
            raise Violated(f"the derived index stores an aggregate ({', '.join(sorted(stored))})")

    # And the roll-up follows its constituents with no separate step: the same graph, read twice,
    # with one constituent added in between.
    graph = verbs.graph(repo, ctx.caps, NETFLIX, verbs.command_for("graph", org=NETFLIX))
    body = json.loads(graph.to_bytes())["body"]
    if body["rollups"]["components"] != len(body["components"]):
        raise Violated("a roll-up disagrees with the constituents it was computed from")
    if body["rollups"]["edges"] != len(body["edges"]):
        raise Violated("the edge roll-up disagrees with the edges beside it")
    return (
        f"index dropped and rebuilt from git alone, identically ({first[:12]}); "
        f"{len(ROLLUP_FIELDS)} aggregate field names have no authored or stored form"
    )


@invariant("identical_pins_identical_bytes")
def _identical_pins_identical_bytes(ctx: "Context") -> str:
    """Same pins, same bytes — the property attestation rests on.

    Three legs. In-process repetition catches the obvious. **Separate processes under different
    hash seeds** catch iteration order leaking into output, which an in-process comparison
    structurally cannot see. The committed goldens catch drift over time and are what a second
    architecture compares against.
    """
    first = recompute_digests(ctx)
    second = {
        kind: art.digest() for kind, (art, _) in sorted(emit_all(ctx, into="artefacts-second").items())
    }
    differing = sorted(k for k in first if first[k] != second.get(k))
    if differing:
        raise Violated(f"a second run against the same ref produced different bytes for: {', '.join(differing)}")

    seeds = [subprocess_digest(ctx, seed) for seed in ("0", "1", "524287")]
    if len(set(seeds)) != 1:
        raise Violated(
            f"the forecast bundle differs between processes under different hash seeds: {sorted(set(seeds))} "
            "— iteration order is reaching the output"
        )
    if seeds[0] != first[verbs.KIND_FORECAST_BUNDLE]:
        raise Violated("the CLI and the library produce different bytes for the same pins")

    # The operational form of the same property: an artefact recomputed from its own pins,
    # through the same path an auditor would use, including the chain a score card carries.
    from ..reproduce import reproduce

    card_path = emit_all(ctx)[verbs.KIND_SCORE_CARD][1]
    report = reproduce(ctx.repo_dir, card_path)
    if not report.reproduces:
        raise Violated(f"a freshly emitted score card did not reproduce from its pins: {report.diff[:400]}")
    if [link.kind for link in report.chain] != [verbs.KIND_FORECAST_BUNDLE]:
        raise Violated("reproducing a score card did not recompute the forecast bundle it scored")

    nudged = ctx.tmp / "nudged-card.json"
    doc = json.loads(card_path.read_bytes())
    doc["body"]["scores"][0]["brier"] = 0.0
    nudged.write_bytes(canonical_json(doc))
    if reproduce(ctx.repo_dir, nudged).reproduces:
        raise Violated("a hand-edited score card reproduced anyway; verify is not comparing anything")

    golden = golden_digests()
    if not golden:
        raise Violated(
            "no committed golden digests — the cross-architecture leg has nothing to compare "
            "against. Re-record with `twin verify --bless-goldens`."
        )
    drifted = sorted(k for k in golden if golden[k] != first.get(k))
    if drifted:
        raise Violated(f"artefact bytes differ from the committed golden digests for: {', '.join(drifted)}")
    if set(golden) != set(first):
        raise Violated(f"the goldens cover {sorted(golden)}; this run emitted {sorted(first)}")
    return (
        f"{len(first)} artefacts identical across runs, processes, hash seeds and the committed "
        "goldens; a score card reproduces from its pins and a hand-edited one does not"
    )


def subprocess_digest(ctx: "Context", hash_seed: str) -> str:
    """Emit a forecast bundle in a fresh interpreter and return its digest."""
    out = ctx.tmp / f"seed-{hash_seed}" / "forecast-bundle.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONHASHSEED": hash_seed, "PYTHONPATH": str(REPO_DIR)}
    proc = subprocess.run(
        [sys.executable, "-P", "-m", "twin", "run", "--repo", str(ctx.repo_dir),
         "--org", NETFLIX, "--scenario", SCENARIO, "--regime", REGIME, "--out", str(out)],
        env=env, cwd=str(REPO_DIR), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise Violated(f"the CLI failed under PYTHONHASHSEED={hash_seed}: {proc.stderr.decode()[:400]}")
    return sha256_hex(out.read_bytes())


@invariant("every_artefact_marked")
def _every_artefact_marked(ctx: "Context") -> str:
    """Every artefact is marked authored or derived, and the marking is enforced, not conventional."""
    for kind, (art, path) in sorted(emit_all(ctx).items()):
        mark = json.loads(path.read_bytes())["envelope"]["mark"]
        if mark not in artefact_mod.MARKS:
            raise Violated(f"{kind} carries mark {mark!r}")
        if mark != art.mark:
            raise Violated(f"{kind} mark differs between object and emitted bytes")

    unmarked = Artefact(kind="probe", mark="", command=["twin"], pins={}, depth={}, body={})
    try:
        unmarked.to_bytes()
    except ArtefactError:
        pass
    else:
        raise Violated("an artefact with no mark serialised anyway")
    return "all emitted artefacts marked; an unmarked artefact refuses to serialise"


@invariant("every_capability_depth_graded")
def _every_capability_depth_graded(ctx: "Context") -> str:
    """A capability with no depth grade fails to load, and no grade may be typed.

    The list is every capability any verb declares, so a verb added later without a graded
    capability behind it fails here rather than emitting an artefact that grades nothing.
    """
    used = sorted(
        set(verbs.CAPS_SENSE) | set(verbs.CAPS_RUN) | set(verbs.CAPS_SCORE)
        | set(verbs.CAPS_GRAPH) | set(verbs.CAPS_BLAST) | set(verbs.CAPS_EXPOSURE)
        | set(verbs.CAPS_PROPAGATE) | set(verbs.CAPS_OPTIONS)
        | set(verbs.CAPS_QUERY) | set(verbs.CAPS_REWIND)
    )
    for name in used:
        ctx.caps.require(name)

    try:
        ctx.caps.require("a-capability-nobody-graded")
    except GradeError:
        pass
    else:
        raise Violated("an ungraded capability resolved instead of failing")

    typed = ctx.tmp / "typed-grade"
    typed.mkdir(parents=True, exist_ok=True)
    source = next(iter(Capabilities.load()))  # any real capability
    (typed / "typed.yaml").write_text(
        "capability: typed-probe\n"
        f"owning_ticket: '{source.owning_ticket}'\n"
        "grade: full\n"
        "criteria:\n"
        + "".join(f"  - index: {c.index}\n    text: {json.dumps(c.text)}\n    checked: false\n" for c in source.criteria),
        encoding="utf-8",
    )
    try:
        Capabilities.load(directory=typed)
    except GradeError as exc:
        if "unchecked criteria" not in str(exc):
            raise Violated(f"a typed grade was rejected without naming the unchecked criteria: {exc}") from None
    else:
        raise Violated("a hand-typed `grade: full` loaded instead of being rejected")

    for kind, (_, path) in sorted(emit_all(ctx).items()):
        depth = json.loads(path.read_bytes())["envelope"]["depth"]
        if not depth.get("capabilities"):
            raise Violated(f"{kind} carries no capability depth grades")
        for name, summary in depth["capabilities"].items():
            if summary["grade"] not in ("stub", "partial", "full"):
                raise Violated(f"{kind}: capability {name} has grade {summary['grade']!r}")
    return f"{len(used)} capabilities graded by computed checklist; typed grades refused"


@invariant("only_as_consumed_scores")
def _only_as_consumed_scores(ctx: "Context") -> str:
    """The honest number is never contaminated by what we know now."""
    from ..canon import canonical_json

    repo = ModelRepo.open(ctx.repo_dir)
    _, bundle_path = emit_all(ctx)[verbs.KIND_FORECAST_BUNDLE]
    card = json.loads(emit_all(ctx)[verbs.KIND_SCORE_CARD][1].read_bytes())["body"]

    if not card["scores"]:
        raise Violated("the as-consumed fixture produced no scores at all")
    tags = {s.get("regime") for s in card["scores"]}
    if tags != {verbs.SCORING_REGIME}:
        raise Violated(f"scores carry regimes {sorted(map(str, tags))}; only as-consumed may score")

    # A bundle executed under any other regime must produce an explicit unscoreable result and
    # never a number — a zero would read as a confident forecast that was wrong.
    for regime in ("as-knowable", "with-hindsight"):
        doc = json.loads(bundle_path.read_bytes())
        doc["body"]["regime"]["declared"] = regime
        for forecast in doc["body"]["forecasts"]:
            forecast["regime"] = regime
        tampered = ctx.tmp / f"bundle-{regime}.json"
        tampered.write_bytes(canonical_json(doc))

        artefact = verbs.score(
            repo, ctx.caps, NETFLIX, tampered, OUTCOME,
            verbs.command_for("score", org=NETFLIX, outcome=OUTCOME, forecast_sha256="tampered"),
        )
        body = json.loads(artefact.to_bytes())["body"]
        if body["scores"]:
            raise Violated(f"a {regime!r} execution produced {len(body['scores'])} score(s)")
        reasons = {u["reason"] for u in body["unscoreable"]}
        if reasons != {"regime-not-as-consumed"}:
            raise Violated(f"a {regime!r} execution was refused for {sorted(reasons)}, not its regime")
        if any(isinstance(v, (int, float)) and not isinstance(v, bool) for _, v in _pairs(body["unscoreable"])):
            raise Violated("an unscoreable forecast still carried a number")
    return f"{len(card['scores'])} as-consumed scores; as-knowable and with-hindsight refused explicitly"


@invariant("as_consumed_admits_no_post_T_fact")
def _as_consumed_admits_no_post_t_fact(ctx: "Context") -> str:
    """An as-consumed execution cannot reference a fact dated after T, by construction (ticket 36).

    "By construction" is the load-bearing word, so the check asserts the *construction* rather
    than the outcome. Four legs, and the first two are what make it structural:

    * **No default.** `verbs.run` takes the regime as a parameter with no default value, and
      omitting it is a refusal. A default would make the gate bypassable by leaving a flag off,
      and the value a default would pick is the one whose forecasts score. The scenario schema
      carries no regime field either, for the same reason: an authored one is a default wearing
      a different hat.
    * **Absence, not screening.** The facts a regime withholds are missing from the overlay the
      execution reads, so there is no post-T fact available to reference.
    * **The planted fact fails the run.** A fact dated after T and committed *before* it is the
      one shape the rewind cannot remove; bound to a component the scenario forecasts, it is a
      refusal rather than a silent redaction.
    * **A gate, not a wall.** The same fixture still runs under as-consumed without the plant,
      and still emits forecasts — a gate that refused everything would pass every refusal in this
      check while making the regime useless.
    """
    import inspect

    from .. import regimes as regimes_mod
    from ..regimes import RegimeError
    from ..schema import DATED_FACTS, REGIMES, SchemaError, validate

    signature = inspect.signature(verbs.run)
    if signature.parameters["regime"].default is not inspect.Parameter.empty:
        raise Violated("verbs.run defaults its regime; the one a default would pick is the one that scores")
    try:
        verbs.run(ModelRepo.open(ctx.repo_dir), ctx.caps, NETFLIX, SCENARIO, None, ["twin", "run"])
    except RegimeError:
        pass
    else:
        raise Violated("an execution with no declared regime ran; the regime has a default somewhere")
    try:
        validate(
            "scenario",
            {"id": "planted", "question": "q", "proposition": "p", "at": "2011-07-12",
             "components": ["c"], "world_models": ["m"], "regime": verbs.SCORING_REGIME},
            "planted",
        )
    except SchemaError:
        pass
    else:
        raise Violated(
            "a scenario declaring its own regime validated. An authored regime is a default: an "
            "execution that omitted the flag would inherit whatever the file happened to say"
        )

    clean = ctx.tmp / "regime-org"
    if not clean.exists():
        fixtures.build_regime_org(clean)
    repo = ModelRepo.open(clean)
    scenario, org, at = "did-it-land-2011", fixtures.REGIME_ORG, fixtures.REGIME_T

    bundles = {}
    for regime in REGIMES:
        artefact = verbs.run(
            repo, ctx.caps, org, scenario, regime,
            verbs.command_for("run", org=org, scenario=scenario, regime=regime),
        )
        bundles[regime] = json.loads(artefact.to_bytes())["body"]
    consumed = bundles[verbs.SCORING_REGIME]
    if not consumed["forecasts"]:
        raise Violated("the as-consumed execution emitted no forecast, so the gate is a wall")
    if not consumed["regime"]["gated"] or not consumed["regime"]["scoring_eligible"]:
        raise Violated("the as-consumed bundle does not declare itself gated and scoring-eligible")

    # Absence, not screening: what this regime admitted is a strict subset of what the loosest one
    # did, and the difference is named rather than counted.
    admitted = {
        regime: {f"{c}/{i}" for c, ids in body["regime"]["gate"]["admitted"].items() for i in ids}
        for regime, body in bundles.items()
    }
    if not admitted[regimes_mod.WITH_HINDSIGHT] - admitted[verbs.SCORING_REGIME]:
        raise Violated(
            "as-consumed and with-hindsight admitted the same facts in this fixture, so the gate "
            "is asserted where nothing could go wrong"
        )
    for collection, field in sorted(DATED_FACTS.items()):
        late = [
            ident
            for ident in admitted[verbs.SCORING_REGIME]
            if ident.startswith(f"{collection}/")
        ]
        for ident in late:
            doc = getattr(regimes_mod.Overlay.load(repo, org), collection)[ident.split("/", 1)[1]]
            if str(doc[field]) > at:
                raise Violated(f"as-consumed admitted {ident}, dated {doc[field]} — after {at}")

    # The planted fact. Committed before T so the rewind keeps it; dated after T so only the date
    # filter can catch it; bound to the forecast subject so silence would be the wrong answer.
    planted = ctx.tmp / "regime-org-planted"
    if not planted.exists():
        fixtures.build_regime_org(planted, planted=True)
    planted_repo = ModelRepo.open(planted)
    try:
        verbs.run(
            planted_repo, ctx.caps, org, scenario, verbs.SCORING_REGIME,
            verbs.command_for("run", org=org, scenario=scenario, regime=verbs.SCORING_REGIME),
        )
    except RegimeError as exc:
        if "planted-post-t" not in str(exc):
            raise Violated(f"the as-consumed run refused, but not for the planted fact: {exc}") from None
    else:
        raise Violated(
            "a fact dated after T and committed before it was quietly withheld rather than "
            "refusing the run, so an as-consumed forecast was produced about a redacted subject"
        )
    # And it is the *regime* that refuses, not the repository: the same plant runs with hindsight.
    loose = verbs.run(
        planted_repo, ctx.caps, org, scenario, regimes_mod.WITH_HINDSIGHT,
        verbs.command_for("run", org=org, scenario=scenario, regime=regimes_mod.WITH_HINDSIGHT),
    )
    if not json.loads(loose.to_bytes())["body"]["forecasts"]:
        raise Violated("the planted fixture emits nothing under any regime, so the refusal proves nothing")
    return (
        f"regime has no default and no schema slot; as-consumed admits "
        f"{len(admitted[verbs.SCORING_REGIME])} of {len(admitted[regimes_mod.WITH_HINDSIGHT])} facts "
        "and still forecasts; a post-T fact bound to the subject refuses the run"
    )


@invariant("no_special_category_slot")
def _no_special_category_slot(ctx: "Context") -> str:
    """Article 9 compliance is an impossibility of representation, not a rule someone could relax."""
    from ..model import BehaviouralOverlay, Overlay
    from ..schema import SPECIAL_CATEGORY, SchemaError, SpecialCategoryError, validate

    declared = next(e.refuses_keys for e in load_manifest() if e.name == "no_special_category_slot")
    if not declared:
        raise Violated("no_special_category_slot declares no Article 9 categories in the manifest")
    missing = [k for k in declared if k not in SPECIAL_CATEGORY]
    if missing:
        raise Violated(
            f"the schema no longer names {', '.join(missing)} as special category — a category was "
            "removed from twin/schema.py while the manifest still declares it"
        )

    # There is no slot: the schemas are closed, so an Article 9 field cannot even be spelled.
    for category in declared:
        try:
            validate("person", {"id": "someone", category: "any value at all"}, "planted")
        except SpecialCategoryError:
            continue
        except SchemaError as exc:
            raise Violated(f"{category!r} was refused as an unknown field rather than as Article 9: {exc}") from None
        raise Violated(f"a person carrying {category!r} validated; there is a slot after all")

    # And nowhere to hide one, at any depth, inside a free-form container.
    try:
        validate(
            "signal",
            {
                "id": "planted", "date": "2011-07-12", "steep": "economic", "source": "s",
                "statement": "t", "provenance": {"observed_by": "x", "notes": [{"health": "poor"}]},
            },
            "planted",
        )
    except SpecialCategoryError:
        pass
    else:
        raise Violated("Article 9 data nested inside a free-form mapping validated")

    # The closure is what makes the data unrepresentable; the name list only improves the message.
    try:
        validate("person", {"id": "someone", "morale": 0.4}, "planted")
    except SchemaError as exc:
        if "schema is closed" not in str(exc):
            raise Violated(f"an undeclared field was refused for the wrong reason: {exc}") from None
    else:
        raise Violated("an undeclared field validated; the schemas are not closed")

    # And by value, not only by key: a cohort or a metric can name a category just as well.
    for probe in ({"cohort": "staff-on-long-term-sickness"}, {"metric": "religion"}):
        try:
            validate(
                "observation",
                {"id": "planted", "cohort": "a-cohort", "metric": "a-metric", "value": 0.5,
                 "observed_on": "2024-01-01", **probe},
                "planted",
            )
        except SpecialCategoryError:
            continue
        raise Violated(f"an observation naming Article 9 data in a value validated: {probe}")

    repo = ModelRepo.open(ctx.repo_dir)
    if hasattr(Overlay.load(repo, NETFLIX), "observations"):
        raise Violated("loading an overlay reached the behavioural unit")
    surfaces = [Overlay.load(repo, org).graph().as_dict() for org in ("netflix", "intel")]
    surfaces.append(BehaviouralOverlay.load(repo, "netflix").observations)
    surfaces += [json.loads(path.read_bytes()) for _, (_, path) in sorted(emit_all(ctx).items())]
    for surface in surfaces:
        present = set(declared) & _keys(surface)
        if present:
            raise Violated(f"a loaded or emitted surface carries {', '.join(sorted(present))}")
    return f"{len(declared)} Article 9 categories with no representation, at any depth"


@invariant("world_never_references_overlay")
def _world_never_references_overlay(ctx: "Context") -> str:
    """An overlay may reference the world layer; the world layer may never reference an overlay."""
    clean = ModelRepo.open(ctx.repo_dir)
    violations = check_direction(clean)
    if violations:
        raise Violated("the clean fixture already violates the direction rule: " + "; ".join(violations))

    planted_dir = ctx.tmp / "planted-direction-violation"
    if not planted_dir.exists():
        fixtures.build(planted_dir)
        fixtures.plant_world_violation(planted_dir)
    planted = ModelRepo.open(planted_dir)
    found = check_direction(planted)
    if not found:
        raise Violated("a world-layer file referencing an overlay was not caught")
    return f"clean fixture is clean; planted violation caught ({found[0]})"


@invariant("no_collapse_mechanism")
def _no_collapse_mechanism(ctx: "Context") -> str:
    """An execution emits multiple forecasts and nothing collapses them.

    **Extended at build ticket 21**, which introduced the first aggregate in this system that
    could plausibly stand in for the things it aggregates. A component reached by several causal
    paths now carries a combined `joint` figure, and the risk that creates is precisely the one
    this invariant exists for: a single number that ends the conversation. So the combined figure
    is asserted to be an **addition** to the paths and never a replacement — every path is still
    reported individually beside it, with its own composed, attenuated and sampled triples.
    """
    _, path = emit_all(ctx)[verbs.KIND_FORECAST_BUNDLE]
    body = json.loads(path.read_bytes())["body"]
    forecasts = body.get("forecasts")
    if not isinstance(forecasts, list):
        raise Violated(f"forecasts is a {type(forecasts).__name__}, not a list")
    if len(forecasts) < 2:
        raise Violated("the fixture scenario names rival world models but emitted one forecast")
    if len({f["world_model"] for f in forecasts}) != len(forecasts):
        raise Violated("forecasts were merged by world model")

    _refusals_hold("no_collapse_mechanism", json.loads(path.read_bytes()))

    moved = json.loads(emit_all(ctx)[verbs.KIND_PROPAGATION][1].read_bytes())["body"]
    combined = 0
    for reached in moved["reached"]:
        if "joint" not in reached:
            continue
        combined += 1
        joint, paths = reached["joint"], reached["paths"]
        if not paths:
            raise Violated(f"{reached['component']}: a combined figure with no paths beside it")
        if joint["paths_combined"] + joint["paths_directional"] != len(paths):
            raise Violated(
                f"{reached['component']}: the combined figure covers "
                f"{joint['paths_combined']} + {joint['paths_directional']} of {len(paths)} paths — "
                "a path that is neither combined nor named as directional has been absorbed"
            )
        for entry in paths:
            if entry["directional_only"]:
                continue
            if not all(k in entry for k in ("composed", "attenuated", "sampled")):
                raise Violated(
                    f"{reached['component']}: a path lost its own figures once a combined one "
                    "existed. The combined figure is an addition, never a replacement."
                )
        # The reference the discount is from. Without it the correction is unfalsifiable, which is
        # the same failure as an attenuated number with no un-attenuated one beside it.
        if "if_independent" not in joint:
            raise Violated(f"{reached['component']}: a combined figure with nothing to compare it against")
    if not combined:
        raise Violated("no component carries a combined figure, so this leg asserts nothing")

    from .. import cli  # imported here: the CLI imports the suite, so the suite must not import it early

    for module in (verbs, cli):
        source = inspect.getsource(module)
        for needle in ("--collapse", "--single", "--consensus", "--point-estimate", "def collapse", "def consensus"):
            if needle in source:
                raise Violated(f"{module.__name__} offers a collapse affordance ({needle!r})")
    return (
        f"{len(forecasts)} forecasts emitted, no collapse affordance anywhere; "
        f"{combined} combined propagation figures, each beside every path it combines"
    )


@invariant("no_recommended_action_field")
def _no_recommended_action_field(ctx: "Context") -> str:
    """Output is a map to be argued with, never a verdict that ends the argument.

    Extended at build ticket 14, where the Wardley maths was inherited from arckit. arckit
    publishes each of D, K and R alongside an **action band** — "must invest", "strong candidate
    for outsourcing". The number is inherited; the band is a recommended action under another
    name and is not. The reader draws the action; the artefact never states it.
    """
    for _, (_, path) in sorted(emit_all(ctx).items()):
        _refusals_hold("no_recommended_action_field", json.loads(path.read_bytes()))

    graph = json.loads(emit_all(ctx)[verbs.KIND_GRAPH][1].read_bytes())["body"]
    wardley = graph.get("wardley")
    if not wardley or not wardley["positions"]:
        raise Violated("the graph carries no map, so this check asserts nothing about it")
    if wardley["axis"].get("action_bands_inherited") is not False:
        raise Violated("the map claims to have inherited arckit's action bands")

    # Scanned over the map's content, not over `axis`, which is provenance about the inheritance
    # and is where the refusal itself is declared.
    content = {k: v for k, v in wardley.items() if k != "axis"}
    for key, value in _pairs(content):
        if any(word in key.lower() for word in NO_ACTION_BANNED_KEYS):
            raise Violated(f"the map carries an action-shaped field ({key})")
        if isinstance(value, str) and any(phrase in value.lower() for phrase in NO_ACTION_BANNED_PHRASES):
            raise Violated(f"the map states an action in prose at {key}")
    for entry in wardley["positions"]:
        for field in ("differentiation_pressure", "commodity_leverage"):
            if not isinstance(entry[field], (int, float)):
                raise Violated(f"{entry['component']}: {field} is not a number — a band would be")
    return (
        "no recommendation field in any artefact; every declared one is refused at emission; "
        f"{len(wardley['positions'])} map positions carry numbers and no inherited action band"
    )


def _refusals_hold(invariant_name: str, doc: dict[str, Any]) -> None:
    """Assert the field names the manifest says this invariant refuses.

    Read from the manifest rather than from `artefact.FORBIDDEN_KEYS`, because a check that
    derives its expectation from the thing it is checking is a tautology: deleting a key would
    shrink the assertion and the suite would stay green. This is the shape the constitution warns
    about — a removed refusal does not show up in a diff.
    """
    from .harness import load_manifest

    declared = next(e.refuses_keys for e in load_manifest() if e.name == invariant_name)
    if not declared:
        raise Violated(f"{invariant_name} declares no refused field names in the manifest")

    missing = [k for k in declared if artefact_mod.FORBIDDEN_KEYS.get(k) != invariant_name]
    if missing:
        raise Violated(
            f"{invariant_name} no longer refuses {', '.join(missing)} at emission — the refusal was "
            "removed from twin/artefact.py while the manifest still declares it"
        )
    present = set(declared) & _keys(doc)
    if present:
        raise Violated(f"artefact carries {', '.join(sorted(present))}")
    for key in declared:
        try:
            artefact_mod.refuse_forbidden_keys({"body": {"nested": [{key: "planted"}]}})
        except ArtefactError:
            continue
        raise Violated(f"a planted {key!r} field was emitted rather than refused")


@invariant("derived_never_human_signed")
def _derived_never_human_signed(ctx: "Context") -> str:
    """For a derived artefact, human involvement is a defect, not a warrant.

    Two depths. **Structural**: a human signature cannot be attached at emission. **Cryptographic**
    (build ticket 11): a sidecar edited afterwards to carry one is *detected* when it is read
    back, which is what turns a convention breach into an anomaly.
    """
    material = b"invariant-suite-key"
    planted = {"identity": "someone@example.invalid", "asserts": "accountability"}

    for kind, (art, path) in sorted(emit_all(ctx).items()):
        doc = attest.build(art, material=material)
        if doc["mark"] != DERIVED:
            raise Violated(f"{kind} is not marked derived")
        if attest.human_signed(doc):
            raise Violated(f"{kind} attestation claims human involvement")
        if attest.check(doc, path.read_bytes(), material):
            raise Violated(f"a freshly emitted {kind} sidecar does not verify: {attest.check(doc, path.read_bytes(), material)}")
        try:
            attest.build(art, [planted], material=material)
        except attest.AttestationError:
            pass
        else:
            raise Violated(f"a human signature attached to derived {kind} without refusal")

        # Emission refused it, so plant it the only way left: edit the sidecar afterwards.
        tampered = {**doc, "human_involvement": {"present": True, "signatures": [planted]}}
        if not any("derived_never_human_signed" in p for p in attest.check(tampered, path.read_bytes(), material)):
            raise Violated(f"a hand-edited {kind} sidecar claiming human involvement was not detected")

    # The two signature types are not interchangeable, in either direction.
    subject = sha256_hex(b"a subject")
    human = sign.human("model-steward", subject, material)
    agent = sign.agent(subject, {"python": "3.12"}, material)
    if set(sign.AGENT_ASSERTS_NOTHING_ABOUT) - set(agent["asserts_nothing_about"]):
        raise Violated("an agent signature no longer declares what it does not assert")
    for signature, wrong in ((human, sign.AGENT), (agent, sign.HUMAN)):
        try:
            sign.verify(signature, wrong, subject, material)
        except sign.SignatureError:
            continue
        raise Violated(f"a {signature['type']} signature verified as a {wrong} one")
    if "role" not in human or set(human) & set(sign.PERSONAL_FIELDS):
        raise Violated("a human signature names an individual rather than a role")

    authored = Artefact(kind="constraint-set", mark=AUTHORED, command=["twin"], pins={}, depth={}, body={})
    signed = attest.build(authored, [sign.human("model-steward", authored.digest(), material)], material=material)
    if not attest.human_signed(signed):
        raise Violated("an authored artefact could not carry the human signature that gives it accountability")
    if attest.check(signed, authored.to_bytes(), material):
        raise Violated(f"a signed authored artefact did not verify: {attest.check(signed, authored.to_bytes(), material)}")
    if not attest.check(attest.build(authored, material=material), authored.to_bytes(), material):
        raise Violated("an unsigned authored artefact verified; nobody is accountable for it")
    return (
        "derived artefacts refuse human signatures and a planted one is detected on read; "
        "authored artefacts require one; the two signature types never substitute"
    )


@invariant("grade_5_only_path_never_prices")
def _grade_5_only_path_never_prices(ctx: "Context") -> str:
    """A path evidenced only by a model assertion emits a blast radius, never a price.

    Grade 5 is where parametric contamination hides: an edge a model asserted from training data
    looks exactly like a well-evidenced one unless the schema forces the distinction. So the gate
    is checked at four depths — the ladder that defines it, the traversal that applies it, the
    **scenario** whose valuation it gates, and the bodies that have nowhere to put a price even if
    somebody wanted one there.

    The scenario leg is the one that matters most. A traversal emits no money at all, so a gate
    asserted only there would be asserted only where nothing could go wrong; the scenario exposure
    is where a figure actually appears, and that is where a grade-5 claim must fail to become one.

    The positive leg matters as much as the negative one. A gate that admits nothing is a wall,
    and a wall would pass every refusal test in this check while making the system useless, so a
    well-evidenced path must still be admitted.
    """
    from .. import blast, evidence, verbs as verbs_mod
    from ..blast import BELOW_THRESHOLD
    from ..schema import CAUSAL_EDGE, EVIDENCE_GRADES, SchemaError, validate

    threshold = evidence.threshold()
    admits = [g for g in EVIDENCE_GRADES if evidence.may_price(g)]
    if admits != [1, 2] or evidence.may_price(5):
        raise Violated(
            f"the published ladder admits grades {admits} to pricing; only 1-2 may price a scored "
            "forecast, and grade 5 never may"
        )
    for grade in EVIDENCE_GRADES:
        if not str(evidence.rung(grade).get("admits", "")).strip():
            raise Violated(f"grade {grade} has no written admission criterion, so it admits anything")

    body = json.loads(emit_all(ctx)[verbs_mod.KIND_BLAST_RADIUS][1].read_bytes())["body"]
    admitted = {e["component"]: e for e in body["admitted_to_pricing"]}
    unpriced = {e["component"]: e for e in body["unpriced"]}
    if not admitted:
        raise Violated(
            "the fixture admits nothing to pricing, so this check cannot tell a gate from a wall"
        )
    for name, entry in sorted(admitted.items()):
        if int(entry["worst_evidence_grade"]) > threshold:
            raise Violated(f"{name} was admitted on a path whose weakest hop is grade {entry['worst_evidence_grade']}")
        if any(hop["hop"] != CAUSAL_EDGE for hop in entry["path"]):
            raise Violated(f"{name} was admitted on a path with a structural hop, where no mechanism is claimed")

    entry = unpriced.get(GRADE_5_ONLY)
    if entry is None:
        raise Violated(
            f"the fixture no longer reaches {GRADE_5_ONLY!r}, whose only causal path runs through a "
            "grade-5 model assertion — this invariant has lost its subject"
        )
    if GRADE_5_ONLY in admitted:
        raise Violated(f"{GRADE_5_ONLY} was admitted to pricing through a grade-5 model assertion")
    if int(entry["worst_evidence_grade"]) != 5 or entry["reason"] != BELOW_THRESHOLD:
        raise Violated(
            f"{GRADE_5_ONLY} is unpriced for {entry['reason']!r} at grade "
            f"{entry['worst_evidence_grade']}, not as a grade-5 path"
        )

    # A distinct artefact type, not a price with a null field: the body is closed and there is no
    # price-shaped name in the set of keys it may carry, at any depth.
    price_shaped = {"price", "prices", "priced", "cost", "costs", "gbp", "amount", "loss",
                    "expected_loss", "severity", "delta", "monetary_value", "declared_value"}
    present = sorted(price_shaped & blast.BODY_KEYS)
    if present:
        raise Violated(f"the blast-radius body declares a slot for {', '.join(present)}")
    stray = sorted(_keys(body) - blast.BODY_KEYS)
    if stray:
        raise Violated(f"an emitted blast radius carries undeclared field(s) {', '.join(stray)}")
    try:
        blast.refuse_undeclared_keys({**body, "price": 1})
    except ArtefactError:
        pass
    else:
        raise Violated("a planted price field serialised into a blast radius rather than being refused")

    # The scenario leg. The traversal above emits no money; this is where a figure appears, so
    # this is where a grade-5 claim has to fail to become one.
    exposure = json.loads(emit_all(ctx)[verbs_mod.KIND_SCENARIO_EXPOSURE][1].read_bytes())["body"]
    if GRADE_5_ONLY not in exposure["scenario"]["components"]:
        raise Violated(
            f"the fixture scenario no longer names {GRADE_5_ONLY!r}, so no perspective is even "
            "offered the chance to price a grade-5 claim and this leg asserts nothing"
        )
    for entry in exposure["perspectives"]:
        priced = {e["component"] for e in entry["admitted"]}
        if GRADE_5_ONLY in priced:
            raise Violated(f"perspective {entry['id']!r} priced {GRADE_5_ONLY} at a gated grade")
        if not priced:
            raise Violated(f"perspective {entry['id']!r} admitted nothing, so the gate is a wall here")
        held = {e["component"]: e for e in entry["register"]}
        if GRADE_5_ONLY not in held:
            raise Violated(
                f"perspective {entry['id']!r} neither priced nor registered {GRADE_5_ONLY}; a "
                "weakly-evidenced valuation is a register entry, never a silent omission"
            )
        if evidence.may_price(int(held[GRADE_5_ONLY]["evidence_grade"])):
            raise Violated(f"perspective {entry['id']!r} registered a valuation that may price")
        for name, figures in ((e["component"], e) for e in entry["register"]):
            numbers = [v for _, v in _pairs(figures) if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if [n for n in numbers if n != figures["evidence_grade"]]:
                raise Violated(f"a register entry for {name} carries a figure beside its grade")
    if any(row["declared_value"][e["id"]] is not None
           for row in exposure["attribution"] if row["component"] == GRADE_5_ONLY
           for e in exposure["perspectives"]):
        raise Violated(f"{GRADE_5_ONLY} carries an attributed figure despite never being admitted")

    # The **priced impact** (build ticket 30). This is now the place where the largest figures in
    # the system appear — a valuation multiplied by a propagated influence — so a gate asserted
    # only on the exposure would be asserted only where the smaller numbers are.
    # Named `impact_body` rather than `priced`: the scenario leg above binds `priced` to a set of
    # component names, and reusing the name would shadow one meaning with another.
    impact_body = json.loads(emit_all(ctx)[verbs_mod.KIND_PRICED_IMPACT][1].read_bytes())["body"]
    for entry in impact_body["perspectives"]:
        named = {i["component"] for i in entry["impacts"]}
        if not named:
            raise Violated(
                f"perspective {entry['perspective']!r} priced nothing at all, so the £ gate is a "
                "wall here and this leg asserts nothing"
            )
        if GRADE_5_ONLY in named:
            raise Violated(f"{GRADE_5_ONLY} was priced through a grade-5 model assertion")
        for impact in entry["impacts"]:
            if int(impact["worst_evidence_grade"]) > threshold:
                raise Violated(
                    f"{impact['component']} was priced on a path whose weakest hop is grade "
                    f"{impact['worst_evidence_grade']}"
                )
            if not evidence.may_price(int(impact["valuation"]["evidence_grade"])):
                raise Violated(f"{impact['component']} was priced from a gated valuation")
        held = {r["component"]: r for r in entry["register"]}
        if GRADE_5_ONLY not in held:
            raise Violated(
                f"perspective {entry['perspective']!r} neither priced nor registered "
                f"{GRADE_5_ONLY}; a refused impact is a register entry, never a silent omission"
            )
        # A refusal carries no money. Not a zero — zero is a price, and it is the wrong one.
        for record in entry["register"]:
            figures = [
                f"{k}={v}" for k, v in _pairs(record)
                if isinstance(v, (int, float)) and not isinstance(v, bool)
                and k not in ("depth", "worst_evidence_grade", "evidence_grade")
            ]
            if figures:
                raise Violated(
                    f"the register entry for {record['component']} carries {', '.join(figures)}; a "
                    "refused impact carries no figure, and a zero is a price rather than a refusal"
                )
        # Mitigation credit is the same gate on a different claim: an unevidenced counterfactual
        # earns nothing rather than a discount.
        for option in entry["responses"]["priced"]:
            claim = option["mitigation"]
            if "credit" in claim and not evidence.may_price(int(claim["evidence_grade"])):
                raise Violated(
                    f"{option['option']} earned mitigation credit on a grade "
                    f"{claim['evidence_grade']} claim; 'the incident did not happen because of our "
                    "control' is a causal claim and is gated like one"
                )
            if "credit" not in claim and "reason" not in claim:
                raise Violated(f"{option['option']} neither earned credit nor said why not")
    # The **positive** leg of the mitigation gate lives in the pocket-org worksheet rather than
    # here, because this fixture authors no mitigation claim at all: worksheet line 73 pins a real
    # credit of 40000 and lines 75-76 pin the two refusals. A gate that credited nothing would
    # pass every refusal above while making the credit useless, and that is where it fails.

    # And the schema refuses the figure at the source, so the artefact is not the only guard.
    try:
        validate(
            "perspective",
            {"id": "planted", "name": "Planted", "party": "employer", "pays": "somebody",
             "ruin": {"insolvency": "a boundary"},
             "values": {"a-component": {"amount": 1, "evidence_grade": 5, "basis": "asserted"}}},
            "planted",
        )
    except SchemaError:
        pass
    else:
        raise Violated("a grade-5 valuation carrying an amount validated; the gate is not at the source")

    # The threshold is a published parameter, pinned where the gate was applied — so moving it
    # moves the digest every gating artefact records, and cannot be done quietly.
    if body["gating"]["pin"] != evidence.pin():
        raise Violated("the emitted blast radius does not pin the ladder it gated against")
    loosened = ctx.tmp / "loosened-ladder" / "evidence-ladder.yaml"
    loosened.parent.mkdir(parents=True, exist_ok=True)
    loosened.write_text(
        evidence.LADDER_PATH.read_text(encoding="utf-8")
        .replace("pricing_threshold: 2", "pricing_threshold: 5")
        .replace("may_price: false", "may_price: true"),
        encoding="utf-8",
    )
    if evidence.pin(loosened)["digest"] == evidence.pin()["digest"]:
        raise Violated("a ladder with a different threshold has the same digest; the pin says nothing")
    if not evidence.may_price(5, loosened):
        raise Violated("the threshold is not what decides admission; something else is gating")
    return (
        f"grades {admits} price and 5 never does; {len(admitted)} admitted on fully-graded paths and "
        f"{GRADE_5_ONLY} unpriced at grade 5; every perspective registers it without a figure in "
        "both the exposure and the priced impact, and the schema refuses one; mitigation credit is "
        "gated on the same rule; the blast body is closed with no price slot; the threshold is "
        "pinned in the artefact and moving it moves the digest"
    )


@invariant("ruin_class_absent_not_priced")
def _ruin_class_absent_not_priced(ctx: "Context") -> str:
    """An excluded option is absent from the choice set, never present with a large number.

    A very large penalty still asserts that a price exists, and with enough upside an optimiser
    finds it. So this is checked where a number would appear: the option is not in `priced`, its
    removal record carries no figure at any depth, and no magnitude brings it back.

    The magnitude leg is the one that matters. Both fixture options are costed at almost nothing,
    so a filter that secretly read a cost would let the cheap ones through; the check then re-runs
    the pre-filter with the cost driven to zero and to an absurd number and demands the same
    verdict, because the cost is not an input to the decision at all.

    The positive leg matters as much. A pre-filter that removed everything would pass every
    refusal here while making the tool useless, and ruin is perspective-relative — so an option
    removed under one eye must still survive under another that declares a different boundary.
    """
    from .. import options as options_mod
    from ..model import Overlay

    body = json.loads(emit_all(ctx)[verbs.KIND_PRICED_OPTIONS][1].read_bytes())["body"]
    priced = {entry["option"] for entry in body["priced"]}
    removed = {entry["option"]: entry for entry in body["prefilter"]["removed"]}

    if not priced:
        raise Violated("the fixture prices nothing, so this check cannot tell a filter from a wall")
    for name in (RUIN_CLASS_OPTION, FLOOR_OPTION):
        if name not in removed:
            raise Violated(
                f"{name!r} is no longer removed by the pre-filter — this invariant has lost the "
                "subject that proves an excluded option never reaches a number"
            )
        if name in priced:
            raise Violated(f"{name!r} was excluded and priced anyway")
    if removed[RUIN_CLASS_OPTION]["class"] != constraints_mod.RUIN:
        raise Violated(f"{RUIN_CLASS_OPTION!r} is removed as {removed[RUIN_CLASS_OPTION]['class']!r}, not ruin")
    if removed[FLOOR_OPTION]["tier"] != "universal":
        raise Violated(f"{FLOOR_OPTION!r} is not removed by the universal floor")

    for name, record in sorted(removed.items()):
        numbers = [f"{k}={v}" for k, v in _pairs(record) if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if numbers:
            raise Violated(f"the removal record for {name} carries {', '.join(numbers)}")

    # No magnitude brings it back. The pre-filter never reads a cost, so driving one to zero and
    # one to an absurd number must change nothing.
    repo = ModelRepo.open(ctx.repo_dir)
    overlay = Overlay.load(repo, NETFLIX)
    perspective = overlay.perspectives[PERSPECTIVE]
    for cost in ({"min": 0, "mode": 0, "max": 0}, {"min": 1e12, "mode": 1e15, "max": 1e18}):
        nudged = {
            ident: ({**doc, "cost": cost} if ident == RUIN_CLASS_OPTION else doc)
            for ident, doc in overlay.responses.items()
        }
        again = options_mod.prefilter(perspective, nudged).priced()
        if RUIN_CLASS_OPTION in {e["option"] for e in again["priced"]}:
            raise Violated(f"{RUIN_CLASS_OPTION!r} reappeared in the priced set at cost {cost}")

    # The gate is a gate. Ruin is perspective-relative, so the same option survives under an eye
    # that declares a different boundary — and that is correct modelling, not a leak.
    other = options_mod.prefilter(overlay.perspectives[OTHER_PERSPECTIVE], overlay.responses).priced()
    if RUIN_CLASS_OPTION not in {e["option"] for e in other["priced"]}:
        raise Violated(
            f"{RUIN_CLASS_OPTION!r} is removed under {OTHER_PERSPECTIVE!r} too, which declares no "
            "such boundary — the pre-filter is holding a list of its own rather than reading the "
            "constraint set each perspective resolves"
        )
    if FLOOR_OPTION in {e["option"] for e in other["priced"]}:
        raise Violated(f"{FLOOR_OPTION!r} survived a perspective; the universal floor is negotiable")

    # And the body is closed, so an excluded option has nowhere to put a number even if somebody
    # later wanted one there.
    stray = sorted(_keys(body) - options_mod.BODY_KEYS)
    if stray:
        raise Violated(f"an emitted priced option set carries undeclared field(s) {', '.join(stray)}")
    try:
        options_mod.refuse_priced_removals(
            {**body, "prefilter": {**body["prefilter"],
                                   "removed": [{**removed[RUIN_CLASS_OPTION], "cost": 1}]}}
        )
    except ArtefactError:
        pass
    else:
        raise Violated("a planted cost on a removal record serialised rather than being refused")
    return (
        f"{len(removed)} options removed before pricing at both tiers, carrying no figure; neither "
        f"a zero nor an absurd cost brings one back; {len(priced)} priced, and the ruin-class one "
        "still survives the perspective that declares no such boundary"
    )


@invariant("prefilter_precedes_pricing")
def _prefilter_precedes_pricing(ctx: "Context") -> str:
    """The pre-filter runs before pricing, asserted structurally rather than by ordering.

    An ordering convention is a comment: it holds until somebody calls the functions the other way
    round. So the property is built out of two locks and this check asserts both of them.

    First, pricing is a **method on the pre-filter's product**. There is no free function in
    `twin/options.py` that takes an option and returns a number, so there is nothing to call in
    the wrong order.

    Second, that product refuses to be built any other way. Without this the first lock would be
    bypassed by constructing the object directly and pricing whatever you liked.
    """
    import inspect as inspect_mod

    from .. import options as options_mod
    from ..constraints import ConstraintError
    from ..model import Overlay

    # An allow-list, not a name filter. A free function that prices an unfiltered option would
    # reopen the ordering whatever it was called, and `tally` or `summarise` gives away nothing —
    # so the assertion is that the module's public surface is exactly these three, and anything
    # new forces a deliberate decision rather than slipping past a keyword match.
    #
    # Only what this module defines: an imported helper is somebody else's surface.
    ALLOWED = {"prefilter", "refuse_undeclared_keys", "refuse_priced_removals"}
    public = {
        name
        for name, value in vars(options_mod).items()
        if not name.startswith("_") and inspect_mod.isfunction(value)
        and getattr(value, "__module__", "") == options_mod.__name__
    }
    if public != ALLOWED:
        raise Violated(
            f"twin/options.py exposes {', '.join(sorted(public)) or 'nothing'} at module level; "
            f"this invariant admits exactly {', '.join(sorted(ALLOWED))}. Pricing is a method on "
            "the pre-filter's product precisely so that no callable can be handed unfiltered "
            "options, and a new free function is how that gets reopened. Adding one needs an "
            "authorising decision ticket."
        )
    if not callable(getattr(options_mod.Admitted, "priced", None)):
        raise Violated("Admitted no longer carries the pricing method, so the seam has moved")

    # Build ticket 30 gave response pricing a **second** module, and a lock asserted on one module
    # while a sibling prices freely is not a lock. So the same allow-list runs on `twin/pricing.py`,
    # and the thing it is really asserting is that nothing there takes a raw response: `price`
    # reaches the choice set only through `options.prefilter(...)`, so an excluded option is absent
    # at any magnitude here exactly as it is in `twin options`.
    from .. import pricing as pricing_mod

    PRICING_ALLOWED = {"impacts", "price", "refuse_undeclared_keys", "refuse_unpriced_figures",
                       "spread"}
    pricing_public = {
        name
        for name, value in vars(pricing_mod).items()
        if not name.startswith("_") and inspect_mod.isfunction(value)
        and getattr(value, "__module__", "") == pricing_mod.__name__
    }
    if pricing_public != PRICING_ALLOWED:
        raise Violated(
            f"twin/pricing.py exposes {', '.join(sorted(pricing_public)) or 'nothing'} at module "
            f"level; this invariant admits exactly {', '.join(sorted(PRICING_ALLOWED))}. Adding a "
            "callable here is how response pricing stops going through the pre-filter."
        )
    source = inspect_mod.getsource(pricing_mod.price)
    if "options_mod.prefilter(" not in source:
        raise Violated(
            "twin/pricing.py no longer reaches the choice set through the pre-filter, so an "
            "excluded option could be priced here while remaining absent from `twin options`"
        )

    repo = ModelRepo.open(ctx.repo_dir)
    overlay = Overlay.load(repo, NETFLIX)
    perspective = overlay.perspectives[PERSPECTIVE]

    try:
        options_mod.Admitted(
            perspective=PERSPECTIVE, options=(), removed=(), considered=(), constraint_set={}
        )
    except ConstraintError:
        pass
    else:
        raise Violated(
            "an Admitted set was constructed without the pre-filter, so anything at all could be "
            "priced and `prefilter_precedes_pricing` would be an ordering convention"
        )

    admitted = options_mod.prefilter(perspective, overlay.responses)
    body = admitted.priced()
    if not body["prefilter"]["ran_before_pricing"]:
        raise Violated("the emitted choice set does not record that the pre-filter ran first")
    considered, survived = set(body["prefilter"]["considered"]), set(body["prefilter"]["admitted"])
    excluded = {entry["option"] for entry in body["prefilter"]["removed"]}
    if not survived <= considered or not excluded <= considered:
        raise Violated("the choice set prices or removes an option nobody considered")
    if survived & excluded:
        raise Violated(f"{', '.join(sorted(survived & excluded))} is both removed and admitted")
    if {e["option"] for e in body["priced"]} != survived:
        raise Violated("the priced list and the pre-filter's survivors disagree")

    # The pre-filter reads the published constraint set and holds no list of its own: the ids it
    # filtered on are exactly the ids the resolved set publishes.
    in_force = {str(c["id"]) for c in body["prefilter"]["constraint_set"]["constraints"]}
    filtered_on = {entry["constraint"] for entry in body["prefilter"]["removed"]}
    if not filtered_on <= in_force:
        raise Violated(
            f"the pre-filter removed options on {', '.join(sorted(filtered_on - in_force))}, which "
            "the published constraint set does not contain"
        )
    if not constraints_mod.floor_ids() <= in_force:
        raise Violated("the resolved constraint set does not contain the whole universal floor")
    return (
        f"pricing is a method on the pre-filter's product and no free pricing function exists; a "
        f"hand-built Admitted set is refused; {len(considered)} options considered, {len(excluded)} "
        f"removed on published constraints and {len(survived)} priced"
    )


@invariant("standing_library_covers_committed_classes")
def _standing_library_covers_committed_classes(ctx: "Context") -> str:
    """The committed set (build ticket 69; decision ticket 13, spec story 43) is code, not prose.

    A class silently dropped from the library — a deleted scenario file, a typo in `class` — is a
    load-time refusal at the source first (`schema.py`'s closed enum on `scenario.class`) and a
    suite failure here second, rather than a gap nobody notices until asked. Built fresh under
    `ctx.tmp` rather than reused from the shared default fixture, the same way the pocket-org
    worksheet guard builds its own subject: this property is about the library, not the flagships.
    """
    library_dir = ctx.tmp / "standing-library-classes"
    if not library_dir.exists():
        fixtures.build_library_org(library_dir)
    overlay = Overlay.load(ModelRepo.open(library_dir), fixtures.LIBRARY_ORG)
    present = {str(s["class"]) for s in overlay.scenarios.values() if s.get("class")}
    committed = set(schema_mod.COMMITTED_SCENARIO_CLASSES)
    missing = sorted(committed - present)
    if missing:
        raise Violated(
            "the standing library is missing an executable scenario for: " + ", ".join(missing)
        )
    return f"the standing library covers all {len(committed)} committed classes: {', '.join(sorted(present))}"


def _keys(node: Any) -> set[str]:
    return set(walk_keys(node))


def _pairs(node: Any) -> list[tuple[str, Any]]:
    from ..canon import walk_values

    return walk_values(node)
