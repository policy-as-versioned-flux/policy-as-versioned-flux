"""`evolution-judge` (build ticket 44): infer a component's evolution position from accumulated
evidence, then let a human override it with the twin pushing back — the second of the six skills
seam 3 (build ticket 42) exists to evaluate.
"""

from __future__ import annotations

import inspect

import pytest

from twin.evolution_judge import (
    SKILL,
    EvolutionJudgeError,
    judge,
    labelled_corpus,
    override,
    pushback,
    scorer,
)
from twin import schema
from twin.schema import SchemaError
from twin.sign import role_ids
from twin.skills import evaluate, threshold_for


@pytest.fixture(scope="session")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> list[dict]:
    return labelled_corpus(tmp_path_factory.mktemp("evolution-judge-corpus"))


# -- judge() -------------------------------------------------------------------------------


def test_judge_produces_a_grade_5_claim_shaped_dict() -> None:
    result = judge({"component": {"id": "some-component", "name": "A construction business"}, "evidence": []})
    assert 0.0 <= result["evolution_position"] <= 1.0
    assert result["evolution"] in ("genesis", "custom-built", "product", "commodity")
    claim = result["claim"]
    assert claim["kind"] == "position"
    assert claim["component"] == "some-component"
    assert claim["evidence_grade"] == 5
    assert SKILL in claim["claimed_by"]
    assert claim["evidence"]
    assert claim["evolution_position"] == result["evolution_position"]


def test_the_claim_conforms_to_the_claim_schema_once_id_is_added() -> None:
    """`judge()` cannot know a claim's own id — only the caller committing it does — so the claim
    is genuinely a `schema.SCHEMAS["claim"]` document, refinement included, only once that is
    added. Unlike a 'binding' claim, a 'position' claim needs no `signal`."""
    result = judge({"component": {"id": "some-component", "name": "A business"}, "evidence": []})
    doc = {**result["claim"], "id": "position-some-component"}
    schema.validate("claim", doc, "test")  # raises SchemaError if the shape or refinement is wrong


def test_a_position_claim_missing_evolution_position_is_refused() -> None:
    doc = {
        "id": "position-some-component", "kind": "position", "component": "some-component",
        "evidence_grade": 5, "claimed_by": "evolution-judge (skill)", "evidence": "inferred",
    }
    with pytest.raises(SchemaError, match="must declare the evolution_position"):
        schema.validate("claim", doc, "test")


def test_a_position_claim_carrying_a_signal_is_refused() -> None:
    """A 'position' claim asserts a value from accumulated evidence, not one signal — carrying
    both fields would read as a binding wearing a position's kind (build ticket 44 review)."""
    doc = {
        "id": "position-some-component", "kind": "position", "component": "some-component",
        "evidence_grade": 5, "claimed_by": "evolution-judge (skill)", "evidence": "inferred",
        "evolution_position": 0.5, "signal": "some-signal",
    }
    with pytest.raises(SchemaError, match="only a 'binding' claim asserts"):
        schema.validate("claim", doc, "test")


def test_a_binding_claim_carrying_an_evolution_position_is_refused() -> None:
    doc = {
        "id": "bind-some-signal", "kind": "binding", "component": "some-component", "signal": "some-signal",
        "evidence_grade": 5, "claimed_by": "some-skill (skill)", "evidence": "automated binding",
        "evolution_position": 0.5,
    }
    with pytest.raises(SchemaError, match="only a 'position' or 'override' claim asserts"):
        schema.validate("claim", doc, "test")


def test_judge_has_no_parameter_that_can_set_a_different_grade() -> None:
    params = inspect.signature(judge).parameters
    assert "grade" not in params
    assert "evidence_grade" not in params
    assert list(params) == ["payload"]


def test_judge_refuses_a_payload_missing_a_field() -> None:
    with pytest.raises(EvolutionJudgeError, match="declares no"):
        judge({"component": {"id": "x", "name": "y"}})


def test_judge_refuses_a_component_with_no_id_or_name() -> None:
    with pytest.raises(EvolutionJudgeError, match="component declares no"):
        judge({"component": {}, "evidence": []})


def test_judge_reads_maturity_signal_from_the_component_name() -> None:
    commodity = judge({"component": {"id": "c", "name": "A merchant acquiring business"}, "evidence": []})
    genesis_leaning = judge({"component": {"id": "g", "name": "A bespoke, proprietary trading system"}, "evidence": []})
    assert commodity["evolution_position"] > genesis_leaning["evolution_position"]


# -- override() and pushback() --------------------------------------------------------------


def test_override_requires_the_inferred_position_first() -> None:
    """Decision ticket 11 Q1: inference before any human input is accepted — structurally, not by
    convention. `override()` refuses a bare dict that is not a real `judge()` output."""
    with pytest.raises(EvolutionJudgeError, match="needs the twin's own inferred position"):
        override({}, "x", 0.5, "model-steward", "a guess")


def test_override_has_inferred_as_its_first_parameter() -> None:
    assert list(inspect.signature(override).parameters)[0] == "inferred"


def test_override_produces_a_grade_4_claim_attributable_to_a_registered_role() -> None:
    inferred = judge({"component": {"id": "x", "name": "A construction business"}, "evidence": []})
    correction = override(inferred, "x", 0.9, "model-steward", "a review found stronger commoditisation")
    assert correction["kind"] == "override"
    assert correction["evidence_grade"] == 4
    assert correction["claimed_by"] == "model-steward"
    assert correction["claimed_by"] in role_ids()
    assert correction["evolution_position"] == 0.9


def test_the_override_conforms_to_the_claim_schema_once_id_is_added() -> None:
    inferred = judge({"component": {"id": "some-component", "name": "A business"}, "evidence": []})
    correction = override(inferred, "some-component", 0.7, "model-steward", "reviewed")
    doc = {**correction, "id": "override-some-component"}
    schema.validate("claim", doc, "test")


def test_an_override_claimed_by_an_unregistered_role_is_refused() -> None:
    inferred = judge({"component": {"id": "some-component", "name": "A business"}, "evidence": []})
    correction = override(inferred, "some-component", 0.7, "nobody-in-the-register", "reviewed")
    doc = {**correction, "id": "override-some-component"}
    with pytest.raises(SchemaError, match="not in the role register"):
        schema.validate("claim", doc, "test")


def test_override_has_no_parameter_that_can_set_a_different_grade() -> None:
    params = inspect.signature(override).parameters
    assert "grade" not in params
    assert "evidence_grade" not in params


def test_override_refuses_a_component_that_does_not_match_the_inferred_claim() -> None:
    """An override answers the inference for *its own* component — a caller cannot satisfy the
    letter of 'inference first' by pointing at some other component's inferred position."""
    inferred = judge({"component": {"id": "some-component", "name": "A business"}, "evidence": []})
    with pytest.raises(EvolutionJudgeError, match="answers the inference for its own component"):
        override(inferred, "a-different-component", 0.5, "model-steward", "reviewed")


def test_pushback_states_disagreement_and_its_basis() -> None:
    inferred = judge({"component": {"id": "x", "name": "A construction business"}, "evidence": []})
    correction = override(inferred, "x", 0.95, "model-steward", "later evidence")
    result = pushback(inferred, correction)
    assert result["agrees"] is False
    assert result["statement"]
    assert f"{inferred['claim']['evolution_position']:.2f}" in result["statement"]
    assert inferred["claim"]["evidence"] in result["statement"]


def test_pushback_is_not_silent_on_agreement() -> None:
    """Silence is not an option — an override that lands on the twin's own estimate still gets a
    stated response, not an empty one."""
    inferred = judge({"component": {"id": "x", "name": "A construction business"}, "evidence": []})
    correction = override(inferred, "x", inferred["claim"]["evolution_position"], "model-steward", "confirmed")
    result = pushback(inferred, correction)
    assert result["agrees"] is True
    assert result["statement"]


def test_pushback_refuses_an_override_for_a_different_component() -> None:
    """Defence in depth: `override()` already refuses this at construction, but `pushback()`
    checks again rather than trusting a claim pair that did not come through `override()` — a
    claim loaded back from a committed model repository, say."""
    inferred = judge({"component": {"id": "some-component", "name": "A business"}, "evidence": []})
    unrelated_override = {
        "kind": "override", "component": "a-different-component", "evidence_grade": 4,
        "claimed_by": "model-steward", "evidence": "reviewed", "evolution_position": 0.5,
    }
    with pytest.raises(EvolutionJudgeError, match="must answer the same component"):
        pushback(inferred, unrelated_override)


# -- the labelled corpus: dated positions from the public spine ----------------------------


def test_the_labelled_corpus_covers_all_four_backtest_keys(corpus: list[dict]) -> None:
    assert len(corpus) == 4
    assert {item["id"] for item in corpus} == {"carillion", "nmc", "wirecard", "enron"}


def test_every_corpus_item_carries_the_fields_evaluate_requires(corpus: list[dict]) -> None:
    for item in corpus:
        assert {"id", "input", "expected"} <= item.keys()
        assert {"component", "evidence"} <= item["input"].keys()
        assert "evolution_position" in item["expected"]


def test_evolution_judge_passes_its_own_labelled_corpus(corpus: list[dict]) -> None:
    result = evaluate(SKILL, judge, corpus, scorer=scorer)
    assert result.passed, f"scored {result.score}, threshold {result.threshold}: {result.as_dict()}"
    assert result.threshold == threshold_for(SKILL)


def test_a_degraded_judge_fails_the_threshold(corpus: list[dict]) -> None:
    def always_wrong(payload: dict) -> dict:
        return {"evolution_position": 0.999}

    result = evaluate(SKILL, always_wrong, corpus, scorer=scorer)
    assert result.score == 0.0
    assert not result.passed


def test_override_accuracy_is_scored_on_the_same_footing_as_the_twins_own_inference(corpus: list[dict]) -> None:
    """AC: 'Override accuracy is scored over time on the same footing as the twin's inference.'
    A human override that names the same expected positions goes through the identical
    `evaluate()` call, corpus and threshold the twin's own `judge()` does — no separate scoring
    path exists for a human's number."""
    expected_by_component = {
        item["input"]["component"]["id"]: item["expected"]["evolution_position"] for item in corpus
    }

    def perfect_human_override(payload: dict) -> dict:
        return {"evolution_position": expected_by_component[payload["component"]["id"]]}

    result = evaluate(SKILL, perfect_human_override, corpus, scorer=scorer)
    assert result.passed
    assert result.threshold == threshold_for(SKILL)

    def careless_human_override(payload: dict) -> dict:
        return {"evolution_position": 0.0}

    bad = evaluate(SKILL, careless_human_override, corpus, scorer=scorer)
    assert not bad.passed
