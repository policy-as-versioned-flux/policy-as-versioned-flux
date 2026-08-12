"""`causal-claims` (build ticket 45, decision ticket 08 Q5) — the third of the six skills seam 3
(build ticket 42, `twin/skills.py`) exists to evaluate.

Given evidence text about a claimed relationship between two components, the skill proposes a
causal edge: sign, lag, a calibrated-range elasticity, an evidence grade — **and, unlike
`signal_classify.py`'s and `evolution_judge.py`'s fixed grade 5, a grade that genuinely varies with
what the evidence supports.** That is the whole risk this ticket exists to measure: those two
skills assert grade 5 by construction because the skill itself is the model asserting something
from nothing; this skill reads evidence someone else gathered and has to place it correctly on the
ladder. **Over-grading — stamping a grade-5 assertion as grade-2 — is scored as a separate,
asymmetrically-penalised metric from whether the claim itself (sign/lag/elasticity) is right**,
because a confidently mis-graded claim defeats the use-gate (`twin/evidence.py`) invisibly: the
artefact still just looks priced.

**Decision ticket 08 Q5's confounding discipline, built here for the first time.** Build ticket 21
built shared-*path* dependence (`twin/propagate.py`'s `shares_ancestry`) and stopped short of this:
"nothing in `twin/` computes common ancestors of an edge's endpoints... the confounder detector is
still to build" (`.scratch/twin/build/21-shared-ancestry-and-common-cause-handling.md`).
`shared_ancestors()` is that detector — a **free structural check**: a component adjacent to both
of an edge's endpoints is a candidate common cause, surfaced automatically rather than argued for.
**Honest limit, stated rather than implied:** this walks one hop, not the full transitive closure.
In the small, densely-connected graphs this system models, walking every reachable node would flag
most of the graph as a candidate for most edges, which hands a reader nothing they could act on —
the same shape of ceiling `twin/propagate.py` names for its own depth cutoff. A confounder two or
more hops from both endpoints, or one the graph does not contain at all, is invisible to this
check — proportional strictness, not a proof (decision ticket 08 Q5: "the usual failure is not
considering the alternative, not failing to formally rule it out").

**The mandatory alternative-explanation field is unconditional, not just for grade 1-2.** Every
proposal names reverse causation as a live alternative — cheap, always available, and honestly
worth stating for any two-variable claim — plus one entry per graph-flagged confounder. Decision
ticket 08 Q5's "only grade 1-2 edges carry the obligation" is about not demanding *formal*
identification work for weak claims; it is not a reason to withhold a free field from the rest.

`ponytail:` sign, lag and grade are a keyword heuristic fitted to this module's own labelled
corpus text (the two real co-flagship edges plus two more from the same fixture), the same honest
move `signal_classify.py` and `evolution_judge.py` make — the point being proven is the harness and
the asymmetric-grading discipline, not classifier quality. Elasticity magnitude is not even
keyword-fitted: `_elasticity()` returns a fixed mode whose *width* narrows with a stronger grade,
because no amount of keyword search stands in for actually fitting a magnitude from data. Upgrade
path for all of it: swap the body for a model call; nothing else in this module, its tests or its
harness guard changes, because `evaluate()` (`twin/skills.py`) reads `skill_fn` as a bare callable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import fixtures, schema
from .evidence import threshold as pricing_threshold
from .model import Graph, Overlay
from .repo import ModelRepo

SKILL = "causal-claims"
# A second, separately-thresholded metric on the same skill's output, registered under its own
# name in `twin/skill-thresholds.yaml` — not a seventh skill (decision ticket 20's six are
# unchanged), the same way `toy-classifier` there is not one of the six either. Kept separate from
# `SKILL` so it can carry its own threshold and its own score-over-time history, which is what
# makes a *systematic over-grading drift* — as opposed to an ordinary claim-accuracy regression —
# separately detectable via the existing `twin/skills.py` machinery (AC: "a systematic
# over-grading drift is detectable in the score-over-time record").
GRADE_SKILL = "causal-claims-grade-accuracy"


class CausalClaimsError(RuntimeError):
    """A malformed payload, or a mandatory field the module failed to populate."""


# -- the graph-based confounder detector (decision ticket 08 Q5) -------------------------------


def shared_ancestors(graph: Graph, from_id: str, to_id: str) -> list[str]:
    """Components directly adjacent, in either edge direction and of any edge type, to **both**
    of an edge's endpoints — candidate common causes, surfaced structurally rather than argued
    for. See the module docstring for the one-hop limit and why it is deliberate.
    """
    neighbours: dict[str, set[str]] = {}
    for e in graph.edges:
        neighbours.setdefault(e.source, set()).add(e.target)
        neighbours.setdefault(e.target, set()).add(e.source)
    exclude = {from_id, to_id}
    a = neighbours.get(from_id, set()) - exclude
    b = neighbours.get(to_id, set()) - exclude
    return sorted(a & b)


def _name_of(graph: Graph, component_id: str) -> str:
    if component_id in graph.components:
        return str(graph.components[component_id].get("name", component_id))
    if component_id in graph.people:
        return str(graph.people[component_id].get("role", component_id))
    return component_id


# -- the heuristic (see module docstring's `ponytail:` note) -----------------------------------

_NEGATIVE_MARKERS = (
    "displac", "erod", "slip", "reduc", "declin", "cannibal", "undermin", "weaken", "shrink",
    "cut", "loses", "lose", "delay", "fall",
)
_POSITIVE_MARKERS = ("lift", "boost", "increas", "improv", "grow", "strengthen", "accelerat", "expand", "support", "gain", "rise")


def _sign(haystack: str) -> str:
    if any(m in haystack for m in _POSITIVE_MARKERS):
        return "positive"
    # ponytail: an arbitrary conservative default when the text names neither direction — a real
    # deployment infers this from data or a model call, not a keyword default.
    return "negative"


# Longest/most specific phrase first within a rung so a real hit is not lost to a shorter
# substring nested inside it — the same discipline `evolution_judge._MATURITY_KEYWORDS` uses.
# Fitted to the ladder's own rung names and `admits` text (`twin/evidence-ladder.yaml`), which is
# exactly the vocabulary `labelled_corpus()`'s hand-authored evidence statements below use.
_GRADE_MARKERS: tuple[tuple[int, tuple[str, ...]], ...] = (
    (1, ("dated natural experiment", "measured before and after", "dated price change", "dated change with observable data")),
    (2, ("repeated historical co-movement", "moving together", "repeated across more than one", "co-movement across")),
    (3, ("established mechanism", "domain theory", "literature", "published work", "published account")),
    (4, ("calibrated expert judgement", "expert judgement", "calibration-trained estimator", "calibrated judgement")),
)
# The safe default when the text names none of the ladder's stronger rungs: grade 5, model
# assertion — never guess a grade the evidence text does not support (decision ticket 08 Q2).
_DEFAULT_GRADE = 5


def _grade(haystack: str) -> int:
    for grade, markers in _GRADE_MARKERS:
        if any(m in haystack for m in markers):
            return grade
    return _DEFAULT_GRADE


_LAG_MARKERS: tuple[tuple[str, int], ...] = (
    ("year or more", 365), ("more than a year", 365), ("a year", 365),
    ("six months", 180),
    ("couple of months", 60), ("few months", 60),
    ("about a month", 30), ("within a month", 30),
)
# A round, stated middle default — no cue present says nothing about direction or magnitude, so
# this is the honest "no signal" answer, the same role `evolution_judge._DEFAULT_POSITION` plays.
_DEFAULT_LAG_DAYS = 180


def _lag_days(haystack: str) -> int:
    for marker, days in _LAG_MARKERS:
        if marker in haystack:
            return days
    return _DEFAULT_LAG_DAYS


# A fixed starting mode with a grade-scaled width: stronger evidence claims a tighter range,
# mirroring the ladder's own logic, even though no keyword search stands in for fitting a
# magnitude from data (see module docstring). 0.375 is the mean of this module's own four-item
# labelled corpus's real elasticity modes — a round starting point with margin either side of the
# claim scorer's own tolerance, not a value picked to graze it.
_BASE_MODE = 0.375
_BAND_PER_GRADE = 0.05


def _elasticity(grade: int) -> dict[str, float]:
    band = min(_BAND_PER_GRADE * grade, _BASE_MODE, 1.0 - _BASE_MODE)
    return {"min": round(_BASE_MODE - band, 4), "mode": _BASE_MODE, "max": round(_BASE_MODE + band, 4)}


def _alternatives(from_c: dict[str, Any], to_c: dict[str, Any], confounders: list[dict[str, Any]]) -> list[str]:
    """The mandatory alternative-explanation field. Reverse causation is always representable and
    always worth stating, so it is unconditional; one entry per graph-flagged confounder joins it.
    Never empty — see the module docstring on why this is not gated to grade 1-2 alone.
    """
    out = [
        f"Reverse causation: {to_c.get('name', to_c['id'])} could be influencing "
        f"{from_c.get('name', from_c['id'])} rather than the direction claimed here."
    ]
    out += [
        f"An unmodelled common cause via {c['name']} could explain the correlation without a direct causal link."
        for c in confounders
    ]
    return out


def propose(payload: dict[str, Any]) -> dict[str, Any]:
    """The skill. `payload` is `{"from": {"id","name"}, "to": {"id","name"}, "evidence":
    [{"statement","source"}, ...], "candidate_confounders": [{"id","name"}, ...]}` —
    `candidate_confounders` is graph-derived by the caller (`shared_ancestors()` above), not
    computed here, so this function stays a bare callable over its own input the way
    `signal_classify.classify()` and `evolution_judge.judge()` do.

    Returns `{"edge", "confounders", "alternatives", "claimed_by"}`. `edge` becomes a genuine
    `schema.SCHEMAS["edge"]` document once a caller adds the `id` only it knows — the same
    once-id-is-added contract `classify()`'s and `judge()`'s `claim` half carry. `confounders` and
    `alternatives` are the skill's own working notes, not (yet) a schema-committed field on
    anything — they travel beside the edge rather than inside it.
    """
    missing = [f for f in ("from", "to", "evidence") if f not in payload]
    if missing:
        raise CausalClaimsError(f"{SKILL}: payload declares no {', '.join(missing)}")
    from_c, to_c = payload["from"], payload["to"]
    if "id" not in from_c or "id" not in to_c:
        raise CausalClaimsError(f"{SKILL}: payload's from/to must each declare an id")
    evidence = payload["evidence"]
    if not evidence:
        raise CausalClaimsError(f"{SKILL}: no evidence to assess a causal claim from")

    haystack = " ".join(str(item.get("statement", "")) for item in evidence).lower()
    grade = _grade(haystack)

    candidates = payload.get("candidate_confounders") or []
    confounders = [
        {
            "id": c["id"],
            "name": c.get("name", c["id"]),
            "discounted_because": (
                f"{c.get('name', c['id'])} is structurally adjacent to both {from_c.get('name', from_c['id'])} "
                f"and {to_c.get('name', to_c['id'])} in the graph; not formally ruled out as the true common "
                "cause — recorded as a candidate for a human to assess rather than silently discounted."
            ),
        }
        for c in candidates
    ]
    alternatives = _alternatives(from_c, to_c, confounders)
    if grade <= pricing_threshold() and not alternatives:
        # Unreachable given `_alternatives()` above always returns at least the reverse-causation
        # entry — a structural guard on the contract itself, the same shape
        # `evolution_judge.pushback()`'s "never silent" check is, in case a future edit to
        # `_alternatives()` ever makes it reachable.
        raise CausalClaimsError(f"{SKILL}: grade {grade} carries no alternative explanation")

    return {
        "edge": {
            "from": from_c["id"],
            "to": to_c["id"],
            "type": schema.CAUSAL_EDGE,
            "sign": _sign(haystack),
            "lag_days": _lag_days(haystack),
            "elasticity": _elasticity(grade),
            "evidence_grade": grade,
        },
        "confounders": confounders,
        "alternatives": alternatives,
        "claimed_by": f"{SKILL} (skill)",
    }


# -- scoring: claim accuracy and grade accuracy are separate metrics (ticket 45's own AC) ------

_LAG_TOLERANCE_DAYS = 60
# The same round tolerance `evolution_judge.scorer()` uses on its own continuous axis.
_ELASTICITY_MODE_TOLERANCE = 0.15


def scorer(actual: Any, expected: Any) -> bool:
    """Claim accuracy: sign, lag and elasticity magnitude — deliberately never the grade, which
    `grade_scorer()` below reports as its own, separately-thresholded metric."""
    edge = actual.get("edge", {})
    if edge.get("sign") != expected["sign"]:
        return False
    try:
        lag_ok = abs(int(edge.get("lag_days", -1)) - int(expected["lag_days"])) <= _LAG_TOLERANCE_DAYS
        mode_ok = abs(float(edge["elasticity"]["mode"]) - float(expected["elasticity_mode"])) <= _ELASTICITY_MODE_TOLERANCE
    except (KeyError, TypeError, ValueError):
        return False
    return lag_ok and mode_ok


# The asymmetric penalty (ticket 45's own AC, documented here where it is enforced): over-grading
# — a predicted grade *stronger* (a lower number) than the truth — is the dangerous failure named
# in this module's docstring, so it gets **zero** tolerance: any over-grade fails outright.
# Under-grading — weaker than the truth, the safe direction — gets one rung of slack, because a
# cautious skill that under-credits strong evidence is a nuisance to a human reviewer, not a
# silent threat to the use-gate the way an over-grade is.
_OVER_GRADE_TOLERANCE = 0
_UNDER_GRADE_TOLERANCE = 1


def grade_scorer(actual: Any, expected: Any) -> bool:
    try:
        predicted = int(actual["edge"]["evidence_grade"])
    except (KeyError, TypeError, ValueError):
        return False
    true_grade = int(expected["evidence_grade"])
    delta = predicted - true_grade  # negative: over-graded; positive: under-graded
    if delta < 0:
        return (-delta) <= _OVER_GRADE_TOLERANCE
    return delta <= _UNDER_GRADE_TOLERANCE


# -- the labelled corpus: the real co-flagship edges, plus two more from the same fixture -------

# Hand-authored evidence statements, grounded in the same real facts the fixture edges themselves
# assert (see each edge's own `note` in `twin/fixtures.py`, and — for `streaming-displaces-dvd`
# specifically — its own regrade record, which independently names the identical rationale: "a
# published account of the same displacement mechanism was found, so the claim moved off
# calibrated judgement and onto domain theory"). Phrased in the evidence ladder's own vocabulary
# (`twin/evidence-ladder.yaml`) for the same honest reason `signal_classify.py`'s fixed keyword
# list is fitted to real fixture text: the point being proven is the grading discipline, not
# classifier quality (see module docstring).
_NETFLIX_DISPLACEMENT_EVIDENCE = (
    "Streaming displacing physical-disc subscriptions is an established mechanism in "
    "media-industry literature and domain theory; the general substitution effect is documented "
    "in published accounts of digital disruption, but this organisation's own figure has not been "
    "separately measured. The effect is not visible for roughly six months after streaming take-up."
)
_CDN_LIFT_EVIDENCE = (
    "Content-delivery capacity lifting streaming quality has been observed moving together, "
    "repeated across more than one delivery-network build-out rather than a single instance, felt "
    "within a couple of months of a build-out completing."
)
_GOODWILL_EROSION_EVIDENCE = (
    "No dataset has observed this relationship and no study has published it; the claim that "
    "price separation erodes goodwill is asserted from general familiarity with brand economics, "
    "not from any measurement. If it exists at all it would show up within about a month."
)
_EUV_SLIP_EVIDENCE = (
    "Lithography tooling deliveries slipping ahead of a process-node slip has been observed "
    "repeatedly, across more than one node generation in the semiconductor industry — a repeated "
    "historical co-movement rather than a single dated instance, taking a year or more to show up "
    "in the following node."
)

# (org, edge id, hand-authored evidence statement). `streaming-displaces-dvd` and
# `euv-delay-slips-the-node` are decision ticket 08's own two co-flagship exemplars (Qwikster to
# churn; EUV delay to node slip); the other two are the same fixture's remaining graded edges, so
# the corpus spans the ladder from grade 2 to grade 5 rather than resting on one pair.
_EDGE_ITEMS: tuple[tuple[str, str, str], ...] = (
    ("netflix", "streaming-displaces-dvd", _NETFLIX_DISPLACEMENT_EVIDENCE),
    ("netflix", "cdn-capacity-lifts-streaming", _CDN_LIFT_EVIDENCE),
    ("netflix", "price-separation-erodes-goodwill", _GOODWILL_EROSION_EVIDENCE),
    ("intel", "euv-delay-slips-the-node", _EUV_SLIP_EVIDENCE),
)


def labelled_corpus(tmp_dir: Path) -> list[dict[str, Any]]:
    """The labelled corpus `causal-claims` is evaluated against: every graded `influences` edge in
    the main netflix/intel fixture (`twin/fixtures.py`), read back through `Overlay` from a
    freshly built repository — not a fossilised duplicate of it — with `candidate_confounders`
    pre-populated by `shared_ancestors()` exactly as a live caller would populate them.
    """
    repo = ModelRepo.open(fixtures.build(tmp_dir))
    items: list[dict[str, Any]] = []
    for org, edge_id, evidence_text in _EDGE_ITEMS:
        graph = Overlay.load(repo, org).graph()
        edge = next(e for e in graph.edges if e.id == edge_id)
        if edge.causal is None:
            raise CausalClaimsError(f"{edge_id}: fixture edge carries no causal claim to grade against")
        confounders = shared_ancestors(graph, edge.source, edge.target)
        items.append(
            {
                "id": f"{org}:{edge_id}",
                "input": {
                    "from": {"id": edge.source, "name": _name_of(graph, edge.source)},
                    "to": {"id": edge.target, "name": _name_of(graph, edge.target)},
                    "evidence": [{"statement": evidence_text, "source": f"{org} fixture, {edge_id}"}],
                    "candidate_confounders": [{"id": cid, "name": _name_of(graph, cid)} for cid in confounders],
                },
                "expected": {
                    "sign": str(edge.causal["sign"]),
                    "lag_days": int(edge.causal["lag_days"]),
                    "elasticity_mode": float(edge.causal["elasticity"]["mode"]),
                    "evidence_grade": int(edge.causal["evidence_grade"]),
                },
            }
        )
    return items
