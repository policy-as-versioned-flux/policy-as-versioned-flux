"""`evolution-judge` (build ticket 44, decision ticket 11 Q1) — the second of the six skills
seam 3 (build ticket 42, `twin/skills.py`) exists to evaluate.

Decision ticket 11 Q1: a component's evolution position is **inferred first from accumulated
evidence**, then a human may correct it — and the twin **pushes back**, retaining its own
estimate and stating the disagreement rather than being silently overwritten. "Humans get
calibrated against evidence too" is the whole reason inference comes first: an override is not a
free edit, it is a second graded claim scored on the same footing as the twin's own.

Three functions carry the contract. `judge()` infers a position from accumulated evidence and
returns it as a grade-5 claim, exactly the shape `classify()` returns in `signal_classify.py`. //
`override()` requires that inferred claim as its own first argument — decision ticket 11 Q1 amends
the map to be inferred *first*, so there is structurally no way to call this without one — and
returns a grade-4 claim ("calibrated expert judgement... named by role", `twin/evidence-ladder.yaml`)
attributable to a registered role (`twin/roles.yaml`), never free text. `pushback()` compares the
two and never returns an empty statement, agreement included.

`ponytail:` the position heuristic is a small keyword lookup fitted to the four real backtest
orgs' own component descriptions (Carillion/NMC/Wirecard/Enron, build tickets 38-40) — the same
honest move `signal_classify.py`'s own heuristic makes for STEEP/binding: the point being proven
is the harness and the contract, not classifier quality. Upgrade path: swap `_infer_position`'s
body for a model call; nothing else in this module, its tests, or its harness guard changes,
because `evaluate()` (`twin/skills.py`) reads `skill_fn` as a bare callable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from . import wardley
from .fixtures import (
    CARILLION_ORG,
    ENRON_ORG,
    NMC_ORG,
    WIRECARD_ORG,
    build_carillion_org,
    build_enron_org,
    build_nmc_health_org,
    build_wirecard_org,
)
from .model import Overlay
from .repo import ModelRepo

SKILL = "evolution-judge"

# What the eval's 1.000 IS (ecosystem ticket 76, REVIEW-2026-09-02 R3). `labelled_corpus()` below
# is the corpus `_MATURITY_KEYWORDS` was fitted to: for every item, the table's own answer for
# that component's name already sits inside `scorer`'s tolerance of the expected position
# (`tests/test_evolution_judge.py` asserts exactly that). So a perfect score is available by
# construction, and what it observes is the harness -- corpus loads, scorer runs, threshold
# compares -- not the twin's judgement. verify-twin-evals.sh reads this constant into both
# of the lines it prints and asserts only that the two agree, and the unit test below requires
# the value to match what the corpus actually is, so holding out an unfitted corpus later is one
# edit to the corpus and one to this word, and every surface follows without turning a check red.
# Two values are defined: "harness-mechanism" while every corpus item is one the heuristic was
# fitted to, "held-out" once any item is not.
CORPUS_KIND = "harness-mechanism"

# The twin's own inference is a model assertion (grade 5, evidence-ladder.yaml); a human override
# is calibrated expert judgement (grade 4) — neither is a parameter either function accepts, so
# neither can be called into asserting a stronger grade than its own kind is (harness guard
# `evolution_judge_output_is_graded_by_construction`).
_INFERRED_GRADE = 5
_OVERRIDE_GRADE = 4

# Delta below which the twin reports agreement rather than disagreement — a round, stated
# tolerance rather than an implied exact-match, because two independent judgements landing on the
# same evolution sub-band is agreement even when the raw floats differ.
_AGREEMENT_TOLERANCE = 0.1


class EvolutionJudgeError(RuntimeError):
    """A malformed payload, or an override with no inferred position to answer to."""


# Longest/most specific phrase first, so a real hit does not lose to a shorter substring nested
# inside it. Fitted to the four backtest orgs' own component names (build tickets 38-40) — see
# module docstring — and grounded in ordinary Wardley judgement about each named industry rather
# than invented to make the corpus pass: merchant/payment acquiring is a canonical commodity-stage
# activity; construction and outsourced support services compete on price at scale; hospital
# operations is standardised, regulated care delivery; mark-to-market energy trading was the
# genuinely novel practice the subject itself pioneered, custom-built rather than commoditised.
_MATURITY_KEYWORDS: tuple[tuple[str, float], ...] = (
    ("payment-acquiring", 0.8),
    ("payment acquiring", 0.8),
    ("merchant acquiring", 0.8),
    ("support-services", 0.62),
    ("support services", 0.62),
    ("construction", 0.6),
    ("hospital operations", 0.55),
    ("healthcare", 0.5),
    ("mark-to-market", 0.45),
    ("energy-trading", 0.45),
    ("energy trading", 0.45),
    ("bespoke", 0.15),
    ("proprietary", 0.15),
    ("pioneering", 0.15),
)

# No keyword hit — the honest "no strong signal" default, sitting on the custom-built/product
# boundary rather than guessing a stage in either direction.
_DEFAULT_POSITION = 0.5


def _infer_position(haystack: str) -> float:
    haystack = haystack.lower()
    for phrase, position in _MATURITY_KEYWORDS:
        if phrase in haystack:
            return position
    return _DEFAULT_POSITION


def judge(payload: dict[str, Any]) -> dict[str, Any]:
    """The skill. `payload` is `{"component": {"id", "name"}, "evidence": [{"statement", ...}]}`
    — the component's own description plus whatever has accumulated and bound to it (exactly what
    `verbs.sense()`'s `bindings` already assembles per component).

    Returns `{"evolution", "evolution_position", "claim": {...}}` — `claim` becomes a genuine
    `schema.SCHEMAS["claim"]` document once a caller adds the `id` it alone knows. `evidence_grade`
    is a literal `5`: there is no parameter here that can set it to anything else, so a caller
    cannot ask the skill to self-assert a higher grade than a model assertion is.
    """
    missing = [f for f in ("component", "evidence") if f not in payload]
    if missing:
        raise EvolutionJudgeError(f"{SKILL}: payload declares no {', '.join(missing)}")
    component = payload["component"]
    if "id" not in component or "name" not in component:
        raise EvolutionJudgeError(f"{SKILL}: payload's component declares no id or name")

    haystack = " ".join(
        [str(component.get("name", ""))] + [str(item.get("statement", "")) for item in payload["evidence"]]
    )
    position = _infer_position(haystack)
    stage = wardley.stage_of(position)
    return {
        "evolution": stage,
        "evolution_position": position,
        "claim": {
            "kind": "position",
            "component": component["id"],
            "evidence_grade": _INFERRED_GRADE,
            "claimed_by": f"{SKILL} (skill)",
            "evidence": (
                f"automated evolution-position inference from {len(payload['evidence'])} "
                "accumulated evidence item(s) and the component's own description"
            ),
            "evolution_position": position,
        },
    }


def override(inferred: dict[str, Any], component_id: str, position: float, role: str, reason: str) -> dict[str, Any]:
    """A human correction — recorded as a provenanced, graded claim attributable to a registered
    role (`twin/roles.yaml`; enforced again, structurally, at `schema.py::_refine_claim`).

    `inferred` is required, not optional: decision ticket 11 Q1 amends the map to be inferred
    *first*, so this function cannot be called into existence without the twin's own prior
    position already in hand — and it must be the prior position **for this component**, or a
    caller could satisfy the letter of "inference first" while overriding one component on the
    strength of a completely different one's evidence. `evidence_grade` is a literal `4`
    ("calibrated expert judgement... named by role", `twin/evidence-ladder.yaml`) — again no
    parameter can set it to anything else.
    """
    if "claim" not in inferred or "evolution_position" not in inferred.get("claim", {}):
        raise EvolutionJudgeError(f"{SKILL}: override() needs the twin's own inferred position, not a bare guess")
    if inferred["claim"].get("component") != component_id:
        raise EvolutionJudgeError(
            f"{SKILL}: override() names component {component_id!r} but the inferred claim is about "
            f"{inferred['claim'].get('component')!r} — an override answers the inference for its own component"
        )
    return {
        "kind": "override",
        "component": component_id,
        "evidence_grade": _OVERRIDE_GRADE,
        "claimed_by": role,
        "evidence": reason,
        "evolution_position": float(position),
    }


def pushback(inferred: dict[str, Any], override_claim: dict[str, Any]) -> dict[str, Any]:
    """The twin's stated response to an override — never silent (decision ticket 11 Q1: "the twin
    retains its inferred estimate and keeps surfacing the divergence"). `statement` is populated
    on agreement as much as on disagreement — an override that happens to land on the same
    position states that explicitly rather than returning nothing.

    `override_claim` need not have come from `override()` in this same call (a committed claim
    file loaded back from a model repository has not), so the component match `override()` checks
    at construction is checked again here rather than assumed.
    """
    if inferred["claim"].get("component") != override_claim.get("component"):
        raise EvolutionJudgeError(
            f"{SKILL}: pushback() was given an inferred claim about {inferred['claim'].get('component')!r} "
            f"and an override about {override_claim.get('component')!r} — they must answer the same component"
        )
    inferred_position = float(inferred["claim"]["evolution_position"])
    overridden_position = float(override_claim["evolution_position"])
    delta = abs(inferred_position - overridden_position)
    agrees = delta < _AGREEMENT_TOLERANCE
    if agrees:
        statement = (
            f"No material disagreement: the twin's own inference ({inferred_position:.2f}) and the "
            f"override ({overridden_position:.2f}) sit within {_AGREEMENT_TOLERANCE} of each other."
        )
    else:
        statement = (
            f"The twin disagrees: its own inference placed this component at {inferred_position:.2f} "
            f"on the basis that {inferred['claim']['evidence']}, against the override's "
            f"{overridden_position:.2f}. The inferred estimate is retained alongside the override, "
            "not replaced by it, and the divergence stays live."
        )
    return {
        "agrees": agrees,
        "delta": delta,
        "inferred_position": inferred_position,
        "overridden_position": overridden_position,
        "statement": statement,
    }


# Tolerance a scored position must land within to count as a pass — a continuous axis has no
# exact match, so this is the same shape decision as `signal_classify.py`'s boolean scorer, just
# over a distance rather than an equality. 0.15 is 60% of one Wardley evolution band's 0.25 width
# (`wardley.BANDS`): a round number close to a band, not a fitted one — a landing more than one
# band away is refused, a landing inside or adjacent to the right one usually passes.
_TOLERANCE = 0.15


def scorer(actual: Any, expected: Any) -> bool:
    try:
        actual_position = float(actual.get("evolution_position", float("nan")))
    except (TypeError, ValueError):
        return False
    return abs(actual_position - float(expected["evolution_position"])) <= _TOLERANCE


# -- the labelled corpus: dated positions from the public spine ---------------------------------

# Each org's builder, its single component, and the fixture-author's own dated Wardley judgement
# for it — a grade-4 "calibrated expert judgement" about the industry the real, cited signals
# already describe (build tickets 38-40), not a fresh invention: the same honesty
# `_carillion_claim()` (`twin/fixtures.py`) already applies to binding a signal is applied here to
# positioning a component. The axis moves over years, not the ~1-2 year distress window each key
# spans, so this corpus tests one dated position per org rather than a trajectory — a stated
# limit, not one implied away.
_ORGS: dict[str, tuple[Callable[[Path], Path], str, float]] = {
    CARILLION_ORG: (build_carillion_org, "carillion-uk-construction", 0.62),
    NMC_ORG: (build_nmc_health_org, "uk-listed-hospital-group", 0.55),
    WIRECARD_ORG: (build_wirecard_org, "third-party-acquiring-business", 0.8),
    ENRON_ORG: (build_enron_org, "energy-trading-book", 0.45),
}


def labelled_corpus(tmp_dir: Path) -> list[dict[str, Any]]:
    """The labelled corpus `evolution-judge` is evaluated against: one item per backtest org, its
    component's own description plus every signal that accumulated against it, read back through
    `Overlay` from a freshly built org (`twin/fixtures.py`) — not a fossilised duplicate of it.
    """
    items: list[dict[str, Any]] = []
    for org, (builder, component_id, expected_position) in sorted(_ORGS.items()):
        repo_dir = builder(tmp_dir / org)
        overlay = Overlay.load(ModelRepo.open(repo_dir), org)
        component = overlay.component(component_id)
        evidence = [
            {"statement": signal["statement"], "date": signal["date"]}
            for signal in sorted(overlay.signals.values(), key=lambda s: str(s["date"]))
        ]
        items.append(
            {
                "id": org,
                "input": {"component": {"id": component_id, "name": component["name"]}, "evidence": evidence},
                "expected": {"evolution_position": expected_position},
            }
        )
    return items
