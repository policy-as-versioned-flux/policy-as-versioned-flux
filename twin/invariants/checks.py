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
from .. import attest, fixtures, index, verbs
from ..artefact import AUTHORED, DERIVED, Artefact, ArtefactError
from ..canon import canonical_json, sha256_hex, walk_keys
from ..grades import Capabilities, GradeError
from ..model import check_direction
from ..repo import ModelRepo
from . import Violated, invariant


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


# -- shared subjects -----------------------------------------------------------------------


def emit_all(ctx: "Context", into: str = "artefacts") -> dict[str, tuple[Artefact, Path]]:
    """One of each artefact kind, from the fixture repository. The subjects every check asserts on."""
    repo = ModelRepo.open(ctx.repo_dir)
    out_dir = ctx.tmp / into
    out_dir.mkdir(parents=True, exist_ok=True)

    bound = verbs.sense(
        repo, ctx.caps, NETFLIX, SIGNAL, verbs.command_for("sense", org=NETFLIX, signal=SIGNAL)
    )
    bound_path = bound.write(out_dir / "bound-signal.json")

    bundle = verbs.run(
        repo, ctx.caps, NETFLIX, SCENARIO, verbs.command_for("run", org=NETFLIX, scenario=SCENARIO)
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

    return {
        bound.kind: (bound, bound_path),
        bundle.kind: (bundle, bundle_path),
        card.kind: (card, card_path),
        graph.kind: (graph, graph_path),
    }


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
    """Any derived index can be dropped and rebuilt from the repository alone."""
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
    return f"index dropped and rebuilt from git alone, identically ({first[:12]})"


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
         "--org", NETFLIX, "--scenario", SCENARIO, "--out", str(out)],
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
    """A capability with no depth grade fails to load, and no grade may be typed."""
    used = sorted(set(verbs.CAPS_SENSE) | set(verbs.CAPS_RUN) | set(verbs.CAPS_SCORE))
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
    """An execution emits multiple forecasts and nothing collapses them."""
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

    from .. import cli  # imported here: the CLI imports the suite, so the suite must not import it early

    for module in (verbs, cli):
        source = inspect.getsource(module)
        for needle in ("--collapse", "--single", "--consensus", "--point-estimate", "def collapse", "def consensus"):
            if needle in source:
                raise Violated(f"{module.__name__} offers a collapse affordance ({needle!r})")
    return f"{len(forecasts)} forecasts emitted, no collapse affordance anywhere"


@invariant("no_recommended_action_field")
def _no_recommended_action_field(ctx: "Context") -> str:
    """Output is a map to be argued with, never a verdict that ends the argument."""
    for _, (_, path) in sorted(emit_all(ctx).items()):
        _refusals_hold("no_recommended_action_field", json.loads(path.read_bytes()))
    return "no recommendation field in any artefact; every declared one is refused at emission"


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
    """For a derived artefact, human involvement is a defect, not a warrant."""
    signature = {"identity": "someone@example.invalid", "asserts": "accountability"}
    for kind, (art, _) in sorted(emit_all(ctx).items()):
        doc = attest.build(art)
        if doc["mark"] != DERIVED:
            raise Violated(f"{kind} is not marked derived")
        if attest.human_signed(doc):
            raise Violated(f"{kind} attestation claims human involvement")
        try:
            attest.build(art, [signature])
        except attest.AttestationError:
            continue
        raise Violated(f"a human signature attached to derived {kind} without refusal")

    authored = Artefact(kind="constraint-set", mark=AUTHORED, command=["twin"], pins={}, depth={}, body={})
    if not attest.human_signed(attest.build(authored, [signature])):
        raise Violated("an authored artefact could not carry the human signature that gives it accountability")
    return "derived artefacts refuse human signatures; authored artefacts require them"


def _keys(node: Any) -> set[str]:
    return set(walk_keys(node))


def _pairs(node: Any) -> list[tuple[str, Any]]:
    from ..canon import walk_values

    return walk_values(node)
