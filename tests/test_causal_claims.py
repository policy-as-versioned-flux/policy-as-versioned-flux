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
    propose_stated,
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


@pytest.mark.parametrize("statement", [
    "expert judgement",
    "An ordinary expert judgement, with no calibration support.",
    "An uncalibrated expert judgement.",
    "An uncalibrated judgement.",
    "A miscalibrated expert judgement.",
    "This is not calibrated expert judgement.",
    "This is not a calibrated judgement.",
    "There is no evidence of calibrated expert judgement.",
    "The author never provided calibrated judgement.",
    "The claim is offered without calibrated expert judgement.",
    "The author is not a calibration-trained estimator.",
    "The author isn't a calibration-trained estimator.",
    "The author is a calibration-untrained estimator.",
])
def test_unsupported_calibration_authority_stays_a_model_assertion(statement: str) -> None:
    """Decision 08 Q2 requires affirmative calibration, not ordinary expert authority."""
    payload = {**_PAYLOAD, "evidence": [{"statement": statement}]}
    stated = propose_stated(payload)
    assert stated.answer == propose(payload)
    assert stated.answer["edge"]["evidence_grade"] == 5
    assert grade_scorer(stated.answer, {"evidence_grade": 5})
    assert stated.basis["evidence"] == payload["evidence"]
    assert stated.basis["grade_marker"] is None
    assert stated.basis["defaults_used"]["evidence_grade"] is True


@pytest.mark.parametrize("statement", [
    "A calibrated expert judgement, explicitly recorded as judgement.",
    "A calibration-trained estimator records this judgement.",
    "The estimator supplies calibrated judgement.",
    "CALIBRATED EXPERT JUDGEMENT, explicitly recorded as judgement.",
])
def test_affirmative_calibration_support_is_retained(statement: str) -> None:
    payload = {**_PAYLOAD, "evidence": [{"statement": statement}]}
    stated = propose_stated(payload)
    assert stated.answer == propose(payload)
    assert stated.answer["edge"]["evidence_grade"] == 4
    assert grade_scorer(stated.answer, {"evidence_grade": 4})
    assert stated.basis["grade_marker"] is not None
    assert stated.basis["defaults_used"]["evidence_grade"] is False


@pytest.mark.parametrize("evidence", [
    [{"statement": "Reviewer A is not a calibration-trained estimator"},
     {"statement": "Reviewer B is a calibration-trained estimator"}],
    [{"statement": "Reviewer A is not a calibration-trained estimator. Reviewer B is a calibration-trained estimator."}],
    [{"statement": "Reviewer A is not a calibration-trained estimator; reviewer B supplies calibrated judgement."}],
    [{"statement": "Reviewer A is not a calibration-trained estimator, but reviewer B supplies calibrated judgement."}],
])
def test_unqualified_opinion_does_not_veto_an_independent_calibrated_source(evidence: list[dict]) -> None:
    payload = {**_PAYLOAD, "evidence": evidence}
    stated = propose_stated(payload)
    assert stated.answer == propose(payload)
    assert stated.answer["edge"]["evidence_grade"] == 4
    assert grade_scorer(stated.answer, {"evidence_grade": 4})
    assert stated.basis["grade_marker"] is not None
    assert stated.basis["defaults_used"]["evidence_grade"] is False


@pytest.mark.parametrize("statement, expected_grade", [
    ("A dated natural experiment, measured before and after the intervention.", 1),
    ("Repeated historical co-movement across several organizations.", 2),
    ("An established mechanism in published domain theory.", 3),
])
def test_independent_stronger_evidence_keeps_its_grade(statement: str, expected_grade: int) -> None:
    payload = {**_PAYLOAD, "evidence": [
        {"statement": "The first opinion is uncalibrated expert judgement."},
        {"statement": statement},
    ]}
    stated = propose_stated(payload)
    assert stated.answer == propose(payload)
    assert stated.answer["edge"]["evidence_grade"] == expected_grade
    assert grade_scorer(stated.answer, {"evidence_grade": expected_grade})


@pytest.mark.parametrize("cue, grade", [
    ("dated natural experiment", 1),
    ("measured before and after", 1),
    ("dated price change", 1),
    ("dated change with observable data", 1),
    ("repeated historical co-movement", 2),
    ("moving together", 2),
    ("repeated across more than one", 2),
    ("co-movement across", 2),
    ("established mechanism", 3),
    ("domain theory", 3),
    ("literature", 3),
    ("published work", 3),
    ("published account", 3),
])
def test_denied_stronger_evidence_is_not_a_supported_source(cue: str, grade: int) -> None:
    """Naming an absent source is not evidence, at any rung of the same ladder."""
    affirmative = {**_PAYLOAD, "evidence": [{"statement": f"Evidence supplied: {cue}."}]}
    denied = {**_PAYLOAD, "evidence": [{"statement": f"There is no support from {cue}."}]}
    good, unsupported = propose_stated(affirmative), propose_stated(denied)
    assert good.answer == propose(affirmative)
    assert good.answer["edge"]["evidence_grade"] == grade
    assert grade_scorer(good.answer, {"evidence_grade": grade})
    assert unsupported.answer == propose(denied)
    assert unsupported.answer["edge"]["evidence_grade"] == 5
    assert grade_scorer(unsupported.answer, {"evidence_grade": 5})
    assert unsupported.basis["grade_marker"] is None
    assert unsupported.basis["defaults_used"]["evidence_grade"] is True


@pytest.mark.parametrize("statement", [
    "A dated natural experiment did not occur.",
    "Repeated historical co-movement was not observed.",
    "Published work does not support this claim.",
])
def test_a_source_denied_after_its_name_cannot_strengthen_the_grade(statement: str) -> None:
    payload = {**_PAYLOAD, "evidence": [{"statement": statement}]}
    stated = propose_stated(payload)
    assert stated.answer == propose(payload)
    assert stated.answer["edge"]["evidence_grade"] == 5
    assert grade_scorer(stated.answer, {"evidence_grade": 5})
    assert stated.basis["grade_marker"] is None
    assert stated.basis["defaults_used"]["evidence_grade"] is True


@pytest.mark.parametrize("cue, expected_grade", [
    ("dated natural experiment", 1),
    ("repeated historical co-movement", 2),
    ("published work", 3),
])
def test_distinct_valid_evidence_is_not_vetoed_by_a_denied_source(cue: str, expected_grade: int) -> None:
    denied = f"There is no support from {cue}"
    affirmative = f"Another source supplies {cue}"
    groups = [[{"statement": denied}, {"statement": affirmative}]]
    groups += [[{"statement": denied + boundary + affirmative}] for boundary in [". ", "; ", ", but "]]
    for evidence in groups:
        payload = {**_PAYLOAD, "evidence": evidence}
        stated = propose_stated(payload)
        assert stated.answer == propose(payload)
        assert stated.answer["edge"]["evidence_grade"] == expected_grade
        assert grade_scorer(stated.answer, {"evidence_grade": expected_grade})
        assert stated.basis["grade_marker"] == cue
        assert stated.basis["defaults_used"]["evidence_grade"] is False


@pytest.mark.parametrize("support, expected_grade", [
    ("Repeated historical co-movement across multiple organizations.", 2),
    ("An established mechanism in published work.", 3),
    ("A calibrated expert judgement recorded as judgement.", 4),
])
def test_denied_strongest_rung_does_not_defeat_valid_weaker_support(support: str, expected_grade: int) -> None:
    payload = {**_PAYLOAD, "evidence": [
        {"statement": "No dated natural experiment occurred."},
        {"statement": support},
    ]}
    stated = propose_stated(payload)
    assert stated.answer == propose(payload)
    assert stated.answer["edge"]["evidence_grade"] == expected_grade
    assert grade_scorer(stated.answer, {"evidence_grade": expected_grade})


def test_a_theory_source_need_not_be_a_local_observation() -> None:
    payload = {**_PAYLOAD, "evidence": [{"statement": "An established mechanism, not observed here."}]}
    assert propose(payload)["edge"]["evidence_grade"] == 3


@pytest.mark.parametrize("apostrophe", ["'", "’"])
@pytest.mark.parametrize("subject, auxiliary, predicate, grade", [
    ("A dated natural experiment", "did", "occur", 1),
    ("Published work", "does", "support this claim", 3),
    ("The cited instances measured before and after", "do", "support this claim", 1),
    ("Published work", "is", "available", 3),
    ("The cited instances measured before and after", "are", "available", 1),
    ("Repeated historical co-movement", "was", "observed", 2),
    ("A calibrated expert judgement", "was", "provided", 4),
    ("The cited instances measured before and after", "were", "provided", 1),
    ("A calibrated expert judgement", "has", "been provided", 4),
    ("The cited instances measured before and after", "have", "been provided", 1),
    ("Published work", "had", "been provided", 3),
])
def test_contracting_an_immediate_denial_does_not_change_its_grade(
    subject: str, auxiliary: str, predicate: str, grade: int, apostrophe: str,
) -> None:
    """An apostrophe cannot turn denial of the same source into affirmative evidence."""
    affirmative = f"{subject} {auxiliary} {predicate}."
    expanded = f"{subject} {auxiliary} not {predicate}."
    contracted = f"{subject} {auxiliary}n{apostrophe}t {predicate}."
    for statement, expected_grade in [(affirmative, grade), (expanded, 5), (contracted, 5)]:
        payload = {**_PAYLOAD, "evidence": [{"statement": statement}]}
        stated = propose_stated(payload)
        assert stated.answer == propose(payload)
        assert stated.answer["edge"]["evidence_grade"] == expected_grade
        assert grade_scorer(stated.answer, {"evidence_grade": expected_grade})
        assert (stated.basis["grade_marker"] is None) == (expected_grade == 5)
        assert stated.basis["defaults_used"]["evidence_grade"] == (expected_grade == 5)


@pytest.mark.parametrize("affirmative, denied, grade", [
    ("A dated natural experiment occurred.", "A dated natural experiment never occurred.", 1),
    ("Repeated historical co-movement was observed.", "Repeated historical co-movement was never observed.", 2),
    ("Published work supports this claim.", "Published work never supports this claim.", 3),
    ("A calibrated expert judgement was provided.", "A calibrated expert judgement was never provided.", 4),
])
def test_direct_never_denial_is_not_positive_evidence(affirmative: str, denied: str, grade: int) -> None:
    for statement, expected_grade in [(affirmative, grade), (denied, 5)]:
        payload = {**_PAYLOAD, "evidence": [{"statement": statement}]}
        stated = propose_stated(payload)
        assert stated.answer == propose(payload)
        assert stated.answer["edge"]["evidence_grade"] == expected_grade
        assert grade_scorer(stated.answer, {"evidence_grade": expected_grade})


@pytest.mark.parametrize("denied, affirmative, grade", [
    ("A dated natural experiment didn't occur", "Another dated natural experiment occurred", 1),
    ("Repeated historical co-movement wasn't observed", "Repeated historical co-movement was observed", 2),
    ("Published work doesn’t support this claim", "Another published work supports this claim", 3),
    ("A calibrated expert judgement wasn’t provided", "Another calibrated expert judgement was provided", 4),
])
def test_independent_support_after_contracted_denial_remains_usable(denied: str, affirmative: str, grade: int) -> None:
    groups = [[{"statement": denied}, {"statement": affirmative}]]
    groups += [[{"statement": denied + separator + affirmative}] for separator in [". ", "; ", ", but "]]
    for evidence in groups:
        payload = {**_PAYLOAD, "evidence": evidence}
        stated = propose_stated(payload)
        assert stated.answer == propose(payload)
        assert stated.answer["edge"]["evidence_grade"] == grade
        assert grade_scorer(stated.answer, {"evidence_grade": grade})


@pytest.mark.parametrize("singular, plural, grade", [
    ("dated natural experiment", "dated natural experiments", 1),
    ("dated price change", "dated price changes", 1),
    ("dated change with observable data", "dated changes with observable data", 1),
    ("repeated historical co-movement", "repeated historical co-movements", 2),
    ("co-movement across", "co-movements across", 2),
    ("established mechanism", "established mechanisms", 3),
    ("domain theory", "domain theories", 3),
    ("published work", "published works", 3),
    ("published account", "published accounts", 3),
    ("calibrated expert judgement", "calibrated expert judgements", 4),
    ("calibration-trained estimator", "calibration-trained estimators", 4),
    ("calibrated judgement", "calibrated judgements", 4),
])
def test_ordinary_noun_inflections_preserve_supported_rungs_and_actual_trace(
    singular: str, plural: str, grade: int,
) -> None:
    """More than one source is not absence of the same kind of source."""
    for form in (singular, plural):
        statement = f"Evidence supplied: {form}."
        payload = {**_PAYLOAD, "evidence": [{"statement": statement}]}
        stated = propose_stated(payload)
        assert stated.answer == propose(payload)
        assert stated.answer["edge"]["evidence_grade"] == grade
        assert grade_scorer(stated.answer, {"evidence_grade": grade})
        assert stated.basis["evidence"] == payload["evidence"]
        assert stated.basis["grade_marker"] == form
        assert stated.basis["defaults_used"]["evidence_grade"] is False
        denied = {**_PAYLOAD, "evidence": [{"statement": f"There is no support from {form}."}]}
        unsupported = propose_stated(denied)
        assert unsupported.answer == propose(denied)
        assert unsupported.answer["edge"]["evidence_grade"] == 5
        assert grade_scorer(unsupported.answer, {"evidence_grade": 5})
        assert unsupported.basis["grade_marker"] is None


@pytest.mark.parametrize("statement", [
    "Published workshops are available.",
    "Published accountancy is available.",
    "An established mechanistic argument is offered.",
    "Domain theoretical speculation is offered.",
    "A calibrated judgemental tone is present.",
])
def test_noun_inflection_support_keeps_real_word_boundaries(statement: str) -> None:
    payload = {**_PAYLOAD, "evidence": [{"statement": statement}]}
    assert propose(payload)["edge"]["evidence_grade"] == 5


def test_plural_denial_does_not_veto_independent_plural_support() -> None:
    denied = "Repeated historical co-movements weren't observed"
    affirmative = "Repeated historical co-movements were observed"
    groups = [[{"statement": denied}, {"statement": affirmative}]]
    groups += [[{"statement": denied + separator + affirmative}] for separator in [". ", "; ", ", but "]]
    for evidence in groups:
        payload = {**_PAYLOAD, "evidence": evidence}
        stated = propose_stated(payload)
        assert stated.answer == propose(payload)
        assert stated.answer["edge"]["evidence_grade"] == 2
        assert grade_scorer(stated.answer, {"evidence_grade": 2})
        assert stated.basis["grade_marker"] == "repeated historical co-movements"


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
    assert claim_result.clears_threshold, f"claim accuracy scored {claim_result.score}: {claim_result.as_dict()}"
    assert claim_result.threshold == threshold_for(SKILL)

    grade_result = evaluate(GRADE_SKILL, propose, corpus, scorer=grade_scorer)
    assert grade_result.clears_threshold, f"grade accuracy scored {grade_result.score}: {grade_result.as_dict()}"
    assert grade_result.threshold == threshold_for(GRADE_SKILL)


def test_a_degraded_proposer_fails_both_thresholds(corpus: list[dict]) -> None:
    def always_wrong(payload: dict) -> dict:
        return {"edge": {"sign": "positive", "lag_days": 1, "elasticity": {"mode": 0.999}, "evidence_grade": 5}}

    claim_result = evaluate(SKILL, always_wrong, corpus, scorer=scorer)
    assert not claim_result.clears_threshold

    grade_result = evaluate(GRADE_SKILL, always_wrong, corpus, scorer=grade_scorer)
    assert not grade_result.clears_threshold


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
    assert claim_result.clears_threshold, "the claim itself (sign/lag/elasticity) is unaffected by the grade change"

    grade_result = evaluate(GRADE_SKILL, over_grades_everything, corpus, scorer=grade_scorer)
    assert not grade_result.clears_threshold, "over-grading every item to the strongest rung must fail the grade metric"
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
