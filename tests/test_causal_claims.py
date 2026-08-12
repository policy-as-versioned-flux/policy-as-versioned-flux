"""`causal-claims` (build ticket 45): propose causal edges with sign, lag, elasticity and an
evidence grade, flag confounders and offer alternative explanations — the third of the six skills
seam 3 (build ticket 42) exists to evaluate, and the first scored on grade accuracy as its own,
separately-thresholded metric.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin.causal_claims import (
    GRADE_SKILL,
    SKILL,
    CausalClaimsError,
    grade_scorer,
    labelled_corpus,
    propose,
    scorer,
    shared_ancestors,
)
from twin.evidence import threshold as pricing_threshold
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.schema import SCHEMAS
from twin.skills import detect_regression, evaluate, record_score, threshold_for


@pytest.fixture(scope="session")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> list[dict]:
    return labelled_corpus(tmp_path_factory.mktemp("causal-claims-corpus"))


_PAYLOAD = {
    "from": {"id": "some-component", "name": "Some business"},
    "to": {"id": "other-component", "name": "Other business"},
    "evidence": [{"statement": "A model assertion. Nothing observed it, nothing published it.", "source": "x"}],
}


# -- propose() -------------------------------------------------------------------------------


def test_propose_produces_an_edge_shaped_dict_with_confounders_and_alternatives() -> None:
    result = propose(_PAYLOAD)
    edge = result["edge"]
    assert edge["from"] == "some-component"
    assert edge["to"] == "other-component"
    assert edge["type"] == "influences"
    assert edge["sign"] in ("positive", "negative")
    assert isinstance(edge["lag_days"], int)
    assert set(edge["elasticity"]) == {"min", "mode", "max"}
    assert edge["evidence_grade"] in (1, 2, 3, 4, 5)
    assert SKILL in result["claimed_by"]
    assert isinstance(result["confounders"], list)
    assert result["alternatives"], "the alternative-explanation field is mandatory, never empty"


def test_the_edge_conforms_to_the_edge_schema_once_id_is_added() -> None:
    """`propose()` cannot know an edge's own id — only the caller committing it does — so `edge`
    is genuinely `schema.SCHEMAS["edge"]`-shaped only once that is added, the same once-id-added
    contract `signal_classify.classify()`'s and `evolution_judge.judge()`'s `claim` half carry."""
    result = propose(_PAYLOAD)
    doc = {**result["edge"], "id": "proposed-some-other"}
    SCHEMAS["edge"].validate(doc, "test")  # raises SchemaError if the shape is wrong


def test_propose_refuses_a_payload_missing_a_field() -> None:
    with pytest.raises(CausalClaimsError, match="declares no"):
        propose({"from": {"id": "a"}, "to": {"id": "b"}})


def test_propose_refuses_a_from_or_to_with_no_id() -> None:
    with pytest.raises(CausalClaimsError, match="must each declare an id"):
        propose({"from": {"name": "a"}, "to": {"id": "b"}, "evidence": [{"statement": "x"}]})


def test_propose_refuses_empty_evidence() -> None:
    with pytest.raises(CausalClaimsError, match="no evidence"):
        propose({**_PAYLOAD, "evidence": []})


def test_alternatives_is_never_empty_even_with_no_candidate_confounders() -> None:
    result = propose({**_PAYLOAD, "candidate_confounders": []})
    assert result["alternatives"]
    assert result["confounders"] == []


def test_alternatives_names_reverse_causation_by_name() -> None:
    result = propose(_PAYLOAD)
    assert "Reverse causation" in result["alternatives"][0]
    assert "Some business" in result["alternatives"][0]
    assert "Other business" in result["alternatives"][0]


def test_confounders_carry_a_discount_rationale() -> None:
    result = propose(
        {**_PAYLOAD, "candidate_confounders": [{"id": "shared-thing", "name": "Shared thing"}]}
    )
    assert len(result["confounders"]) == 1
    confounder = result["confounders"][0]
    assert confounder["id"] == "shared-thing"
    assert confounder["discounted_because"]
    assert "Shared thing" in confounder["discounted_because"]
    # A confounder earns its own alternative-explanation entry too.
    assert any("Shared thing" in a for a in result["alternatives"])


def test_grade_reads_the_ladders_own_vocabulary_from_the_evidence_text() -> None:
    dated = propose(
        {
            **_PAYLOAD,
            "evidence": [{"statement": "Repeated historical co-movement across several instances.", "source": "x"}],
        }
    )
    assert dated["edge"]["evidence_grade"] == 2

    literature = propose(
        {**_PAYLOAD, "evidence": [{"statement": "An established mechanism from the literature.", "source": "x"}]}
    )
    assert literature["edge"]["evidence_grade"] == 3

    judgement = propose(
        {**_PAYLOAD, "evidence": [{"statement": "A calibrated expert judgement, recorded as such.", "source": "x"}]}
    )
    assert judgement["edge"]["evidence_grade"] == 4

    default_assertion = propose(
        {**_PAYLOAD, "evidence": [{"statement": "Nothing in particular is said about how we know this.", "source": "x"}]}
    )
    assert default_assertion["edge"]["evidence_grade"] == 5, "no ladder language present is the safe grade-5 default"


def test_sign_is_read_from_directional_language() -> None:
    lifts = propose({**_PAYLOAD, "evidence": [{"statement": "This lifts and boosts the other component.", "source": "x"}]})
    assert lifts["edge"]["sign"] == "positive"
    erodes = propose({**_PAYLOAD, "evidence": [{"statement": "This erodes and undermines the other component.", "source": "x"}]})
    assert erodes["edge"]["sign"] == "negative"


# -- shared_ancestors(): the graph-based confounder detector (decision ticket 08 Q5) ----------


@pytest.fixture()
def netflix(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "netflix")


@pytest.fixture()
def intel(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, "intel")


def test_shared_ancestors_finds_the_real_confounder_on_the_netflix_co_flagship_edge(netflix: Overlay) -> None:
    """`streaming-experience` and `dvd-by-mail` both `needs: content-delivery-network` — a real,
    fixture-authored shared dependency, not a planted one."""
    graph = netflix.graph()
    found = shared_ancestors(graph, "streaming-experience", "dvd-by-mail")
    assert "content-delivery-network" in found


def test_shared_ancestors_finds_the_real_confounder_on_the_intel_co_flagship_edge(intel: Overlay) -> None:
    """`foundry-services` needs both `euv-lithography` and `leading-edge-process-node` — a real
    shared dependent of the EUV-delay edge's two endpoints."""
    graph = intel.graph()
    found = shared_ancestors(graph, "euv-lithography", "leading-edge-process-node")
    assert "foundry-services" in found


def test_shared_ancestors_is_honestly_empty_with_no_shared_neighbour(netflix: Overlay) -> None:
    """`brand-goodwill` has no edge but the one from `dvd-by-mail` itself — nothing forces a
    confounder to be manufactured where the graph has none."""
    graph = netflix.graph()
    assert shared_ancestors(graph, "dvd-by-mail", "brand-goodwill") == []


def test_shared_ancestors_excludes_the_endpoints_themselves(netflix: Overlay) -> None:
    graph = netflix.graph()
    found = shared_ancestors(graph, "streaming-experience", "dvd-by-mail")
    assert "streaming-experience" not in found
    assert "dvd-by-mail" not in found


# -- scorer() and grade_scorer(): two separate metrics (ticket 45's own AC) -------------------


def test_scorer_ignores_the_grade_entirely() -> None:
    """Claim accuracy and grade accuracy are separate metrics: a claim with the right
    sign/lag/elasticity but a wildly wrong grade still passes the claim scorer."""
    actual = {"edge": {"sign": "negative", "lag_days": 180, "elasticity": {"mode": 0.45}, "evidence_grade": 5}}
    expected = {"sign": "negative", "lag_days": 180, "elasticity_mode": 0.45, "evidence_grade": 1}
    assert scorer(actual, expected)
    assert not grade_scorer(actual, expected)


def test_scorer_fails_on_a_wrong_sign() -> None:
    actual = {"edge": {"sign": "positive", "lag_days": 180, "elasticity": {"mode": 0.45}}}
    expected = {"sign": "negative", "lag_days": 180, "elasticity_mode": 0.45}
    assert not scorer(actual, expected)


def test_grade_scorer_is_asymmetric_over_grading_fails_under_grading_survives() -> None:
    """The asymmetric penalty, directly: over-grading by one rung fails outright; under-grading
    by one rung passes; under-grading by two fails too (the tolerance is one rung, not unlimited)."""
    expected = {"evidence_grade": 3}
    over_by_one = {"edge": {"evidence_grade": 2}}
    under_by_one = {"edge": {"evidence_grade": 4}}
    under_by_two = {"edge": {"evidence_grade": 5}}
    exact = {"edge": {"evidence_grade": 3}}

    assert not grade_scorer(over_by_one, expected), "over-grading must never be forgiven"
    assert grade_scorer(under_by_one, expected), "one rung of under-grading is tolerated"
    assert not grade_scorer(under_by_two, expected), "the tolerance is one rung, not unlimited"
    assert grade_scorer(exact, expected)


def test_grade_scorer_handles_a_malformed_actual() -> None:
    assert not grade_scorer({"edge": {}}, {"evidence_grade": 3})
    assert not grade_scorer({}, {"evidence_grade": 3})


# -- the labelled corpus: the real co-flagship edges, plus two more from the same fixture ------


def test_the_labelled_corpus_covers_the_co_flagship_edges_and_two_more(corpus: list[dict]) -> None:
    assert len(corpus) == 4
    assert {item["id"] for item in corpus} == {
        "netflix:streaming-displaces-dvd",
        "netflix:cdn-capacity-lifts-streaming",
        "netflix:price-separation-erodes-goodwill",
        "intel:euv-delay-slips-the-node",
    }


def test_every_corpus_item_carries_the_fields_evaluate_requires(corpus: list[dict]) -> None:
    for item in corpus:
        assert {"id", "input", "expected"} <= item.keys()
        assert {"from", "to", "evidence", "candidate_confounders"} <= item["input"].keys()
        assert {"sign", "lag_days", "elasticity_mode", "evidence_grade"} <= item["expected"].keys()


def test_causal_claims_passes_its_own_labelled_corpus_on_both_metrics(corpus: list[dict]) -> None:
    claim_result = evaluate(SKILL, propose, corpus, scorer=scorer)
    assert claim_result.passed, f"claim accuracy scored {claim_result.score}: {claim_result.as_dict()}"
    assert claim_result.threshold == threshold_for(SKILL)

    grade_result = evaluate(GRADE_SKILL, propose, corpus, scorer=grade_scorer)
    assert grade_result.passed, f"grade accuracy scored {grade_result.score}: {grade_result.as_dict()}"
    assert grade_result.threshold == threshold_for(GRADE_SKILL)


def test_a_degraded_proposer_fails_both_thresholds(corpus: list[dict]) -> None:
    def always_wrong(payload: dict) -> dict:
        return {"edge": {"sign": "positive", "lag_days": 1, "elasticity": {"mode": 0.999}, "evidence_grade": 5}}

    claim_result = evaluate(SKILL, always_wrong, corpus, scorer=scorer)
    assert not claim_result.passed

    grade_result = evaluate(GRADE_SKILL, always_wrong, corpus, scorer=grade_scorer)
    assert not grade_result.passed


def test_a_systematically_over_grading_proposer_fails_the_grade_threshold_but_not_necessarily_the_claim_one(
    corpus: list[dict],
) -> None:
    """The precise failure this ticket exists to catch: a proposer that gets sign/lag/elasticity
    right but always claims the strongest possible grade — confidently stamping every claim as
    grade 1, exactly the over-grading decision ticket 08's own text calls the dangerous failure."""

    def over_grades_everything(payload: dict) -> dict:
        honest = propose(payload)
        honest["edge"]["evidence_grade"] = 1
        return honest

    claim_result = evaluate(SKILL, over_grades_everything, corpus, scorer=scorer)
    assert claim_result.passed, "the claim itself (sign/lag/elasticity) is unaffected by the grade change"

    grade_result = evaluate(GRADE_SKILL, over_grades_everything, corpus, scorer=grade_scorer)
    assert not grade_result.passed, "over-grading every item to the strongest rung must fail the grade metric"
    assert grade_result.score == 0.0, "every item in this corpus has a true grade above 1, so every one is an over-grade"


# -- AC: a systematic over-grading drift is detectable in the score-over-time record -----------


def test_a_systematic_over_grading_drift_is_detectable_as_a_regression(tmp_path: Path, corpus: list[dict]) -> None:
    log = tmp_path / "scores.jsonl"

    def over_grades_everything(payload: dict) -> dict:
        honest = propose(payload)
        honest["edge"]["evidence_grade"] = 1
        return honest

    good = evaluate(GRADE_SKILL, propose, corpus, scorer=grade_scorer)
    bad = evaluate(GRADE_SKILL, over_grades_everything, corpus, scorer=grade_scorer)
    record_score(good, "model-a", "2026-08-01T00:00:00Z", path=log)
    record_score(bad, "model-b", "2026-08-08T00:00:00Z", path=log)

    report = detect_regression(GRADE_SKILL, path=log)
    assert report["computed"] is True
    assert report["regressed"] is True
    assert report["delta"] < 0


def test_pricing_threshold_two_matches_the_mandatory_alternatives_boundary_this_module_cites() -> None:
    """The module cites the live pricing threshold rather than a hardcoded `2` — this pins the
    value the rest of the suite already assumes, so a future ladder change is felt here too."""
    assert pricing_threshold() == 2
