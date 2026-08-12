"""`ethics-gate` (build ticket 47): the sensor admission ladder, DPIA triage, gameability marking
and the fast-improvement backstop — the sixth and last of the six skills seam 3 (build ticket 42)
exists to evaluate.
"""

from __future__ import annotations

import inspect

import pytest

from twin.ethics_gate import (
    GOODHART_PROOF,
    MARKED,
    SKILL,
    EthicsGateError,
    admit,
    adjudicate_fast_improvement,
    classify_gameability,
    dpia_triage,
    flag_fast_improvement,
    labelled_corpus,
    prefer,
    scorer,
    walk_ladder,
)
from twin.invariants import NO_ACTION_BANNED_KEYS, NO_ACTION_BANNED_PHRASES
from twin.canon import walk_keys, walk_values
from twin.sign import role_ids
from twin.skills import evaluate, threshold_for


@pytest.fixture(scope="session")
def corpus() -> list[dict]:
    return labelled_corpus()


# -- walk_ladder() --------------------------------------------------------------------------

_PASSING_PURPOSE = {"scenario": "key-person-succession-planning", "will_act": True}
_PASSING_NECESSITY = {"kind": "structural", "level": "aggregate", "alternatives": []}
_PASSING_PROPORTIONALITY = {"intrusion_cost": 100.0, "value_illuminated": 10000.0}


def test_walk_ladder_admits_when_every_rung_passes() -> None:
    result = walk_ladder(
        {"purpose": _PASSING_PURPOSE, "necessity": _PASSING_NECESSITY, "proportionality": _PASSING_PROPORTIONALITY}
    )
    assert result["admitted"] is True
    assert result["stopped_at"] is None
    assert [r["rung"] for r in result["rungs"]] == ["purpose", "necessity", "proportionality"]
    assert all(r["justification"] for r in result["rungs"])


def test_walk_ladder_refuses_a_payload_missing_a_rung() -> None:
    with pytest.raises(EthicsGateError, match="declares no"):
        walk_ladder({"purpose": _PASSING_PURPOSE, "necessity": _PASSING_NECESSITY})


def test_walk_ladder_stops_at_purpose_and_never_evaluates_the_rest() -> None:
    """A malformed necessity/proportionality payload that would raise if ever read proves the
    later rungs were never touched, not merely that the result happened to come out right."""
    result = walk_ladder(
        {"purpose": {"scenario": "", "will_act": False}, "necessity": {}, "proportionality": {}}
    )
    assert result["admitted"] is False
    assert result["stopped_at"] == "purpose"
    assert len(result["rungs"]) == 1


def test_walk_ladder_stops_at_necessity_when_a_less_intrusive_alternative_exists() -> None:
    result = walk_ladder(
        {
            "purpose": _PASSING_PURPOSE,
            "necessity": {
                "kind": "behavioural", "level": "individual",
                "alternatives": [{"kind": "structural", "level": "aggregate"}],
            },
            "proportionality": {},
        }
    )
    assert result["admitted"] is False
    assert result["stopped_at"] == "necessity"
    assert len(result["rungs"]) == 2


def test_walk_ladder_stops_at_proportionality_when_intrusion_outweighs_value() -> None:
    result = walk_ladder(
        {
            "purpose": _PASSING_PURPOSE,
            "necessity": _PASSING_NECESSITY,
            "proportionality": {"intrusion_cost": 100000.0, "value_illuminated": 10.0},
        }
    )
    assert result["admitted"] is False
    assert result["stopped_at"] == "proportionality"
    assert len(result["rungs"]) == 3


def test_walk_ladder_necessity_refuses_an_unknown_kind_or_level() -> None:
    with pytest.raises(EthicsGateError, match="unknown sensor kind"):
        walk_ladder(
            {
                "purpose": _PASSING_PURPOSE,
                "necessity": {"kind": "telepathic", "level": "aggregate", "alternatives": []},
                "proportionality": _PASSING_PROPORTIONALITY,
            }
        )


# -- dpia_triage() --------------------------------------------------------------------------


def test_dpia_triage_flags_keystroke_monitoring_as_mandatory() -> None:
    result = dpia_triage({"channels": ["keystroke"], "profiling": False, "financial_loss_risk": False})
    assert result["mandatory"] is True
    assert "keystroke" in result["triggers"]
    assert result["citation"]


def test_dpia_triage_flags_profiling_as_mandatory_with_no_channel() -> None:
    result = dpia_triage({"channels": [], "profiling": True, "financial_loss_risk": False})
    assert result["mandatory"] is True
    assert result["triggers"] == ["profiling"]


def test_dpia_triage_is_not_mandatory_when_nothing_triggers_it() -> None:
    result = dpia_triage({"channels": ["structural-commit-graph"], "profiling": False, "financial_loss_risk": False})
    assert result["mandatory"] is False
    assert result["triggers"] == []


# -- admit() --------------------------------------------------------------------------------


def _payload(**dpia_overrides: object) -> dict:
    dpia = {"channels": [], "profiling": False, "financial_loss_risk": False, "complete": False}
    dpia.update(dpia_overrides)
    return {
        "sensor": {"id": "s", "name": "A sensor"},
        "purpose": _PASSING_PURPOSE,
        "necessity": _PASSING_NECESSITY,
        "proportionality": _PASSING_PROPORTIONALITY,
        "dpia": dpia,
    }


def test_admit_passes_when_ladder_and_dpia_both_clear() -> None:
    result = admit(_payload())
    assert result["admitted"] is True
    assert result["ladder"]["admitted"] is True
    assert result["dpia"]["satisfied"] is True


def test_admit_refuses_when_dpia_mandatory_and_not_complete_even_though_ladder_passes() -> None:
    result = admit(_payload(channels=["keystroke"], complete=False))
    assert result["admitted"] is False
    assert result["ladder"]["admitted"] is True  # the ladder itself passed
    assert result["dpia"]["mandatory"] is True
    assert result["dpia"]["satisfied"] is False


def test_admit_passes_when_dpia_mandatory_and_recorded_complete() -> None:
    result = admit(_payload(channels=["keystroke"], complete=True))
    assert result["admitted"] is True


def test_admit_refuses_a_payload_missing_a_field() -> None:
    with pytest.raises(EthicsGateError, match="declares no"):
        admit({"sensor": {"id": "s"}})


def test_admit_produces_a_grade_5_claim_shaped_dict() -> None:
    result = admit(_payload())
    claim = result["claim"]
    assert claim["kind"] == "sensor-admission"
    assert claim["component"] == "s"
    assert claim["evidence_grade"] == 5
    assert SKILL in claim["claimed_by"]
    assert claim["evidence"]


def test_admit_has_no_parameter_that_can_set_a_different_grade() -> None:
    params = inspect.signature(admit).parameters
    assert "grade" not in params
    assert "evidence_grade" not in params
    assert list(params) == ["payload"]


# -- classify_gameability() and prefer() -----------------------------------------------------


def test_classify_gameability_marks_a_bus_factor_metric_as_goodhart_proof() -> None:
    result = classify_gameability(
        {"sensor": {"id": "bf"}, "metric_description": "Bus-factor score from commit-structure spread"}
    )
    assert result["gameability"] == GOODHART_PROOF
    assert result["reason"]


def test_classify_gameability_marks_a_commit_count_metric_as_marked_by_default() -> None:
    """Decision ticket 15 Q2's own named examples of cheaply-gamed sensors — commit counts,
    message sentiment, hours-online — carry no goodhart-proof keyword, so they fall to the safe
    default rather than being preferred."""
    result = classify_gameability({"sensor": {"id": "cc"}, "metric_description": "Raw commit count per engineer"})
    assert result["gameability"] == MARKED


def test_classify_gameability_refuses_a_payload_missing_a_field() -> None:
    with pytest.raises(EthicsGateError, match="declares no"):
        classify_gameability({"sensor": {"id": "s"}})


def test_prefer_prefers_the_goodhart_proof_candidate_among_several() -> None:
    result = prefer(
        [
            {"sensor": {"id": "commit-count"}, "metric_description": "Raw commit count"},
            {"sensor": {"id": "bus-factor"}, "metric_description": "Bus-factor from commit structure"},
        ]
    )
    assert result["preferred"] == ["bus-factor"]
    assert "bus-factor" in result["reason"]
    assert len(result["candidates"]) == 2


def test_prefer_names_no_preference_when_no_candidate_is_goodhart_proof() -> None:
    result = prefer(
        [
            {"sensor": {"id": "commit-count"}, "metric_description": "Raw commit count"},
            {"sensor": {"id": "hours-online"}, "metric_description": "Hours online per day"},
        ]
    )
    assert result["preferred"] == []
    assert "no candidate is goodhart-proof" in result["reason"]


def test_prefer_refuses_an_empty_candidate_list() -> None:
    with pytest.raises(EthicsGateError, match="at least one candidate"):
        prefer([])


# -- flag_fast_improvement() and adjudicate_fast_improvement() ------------------------------


def test_flag_fast_improvement_flags_a_rate_at_or_above_threshold() -> None:
    result = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 30.0})
    assert result["flagged"] is True
    assert result["requires_human_adjudication"] is True
    assert result["rate"] == pytest.approx(2.0)
    assert result["statement"]


def test_flag_fast_improvement_does_not_flag_a_rate_below_threshold() -> None:
    result = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 11.0})
    assert result["flagged"] is False
    assert result["requires_human_adjudication"] is False


def test_flag_fast_improvement_respects_a_custom_threshold() -> None:
    result = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 12.0, "rate_threshold": 0.1})
    assert result["flagged"] is True


def test_flag_fast_improvement_handles_a_zero_baseline_without_dividing_by_zero() -> None:
    result = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 0.0, "current": 5.0})
    assert result["rate"] == float("inf")
    assert result["flagged"] is True


def test_flag_fast_improvement_output_carries_no_action_or_verdict_shaped_field() -> None:
    """The structural half of 'never an automatic adverse finding': the flag's own output has
    nowhere to put one — checked against the same banned-word/phrase lists
    `no_recommended_action_field` runs, not merely by field-name convention."""
    result = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 30.0})
    for key in walk_keys(result):
        assert not any(word in key.lower() for word in NO_ACTION_BANNED_KEYS), key
    for key, value in walk_values(result):
        if isinstance(value, str):
            assert not any(phrase in value.lower() for phrase in NO_ACTION_BANNED_PHRASES), (key, value)


def test_adjudicate_fast_improvement_requires_a_raised_flag() -> None:
    clear = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 10.5})
    with pytest.raises(EthicsGateError, match="needs a raised flag"):
        adjudicate_fast_improvement(clear, "model-steward", "genuine improvement", "reviewed the data")


def test_adjudicate_fast_improvement_requires_a_registered_role() -> None:
    flag = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 30.0})
    with pytest.raises(EthicsGateError, match="not in the role register"):
        adjudicate_fast_improvement(flag, "nobody-in-the-register", "genuine improvement", "reviewed")


def test_adjudicate_fast_improvement_requires_a_nonempty_finding() -> None:
    flag = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 30.0})
    with pytest.raises(EthicsGateError, match="not an adjudication"):
        adjudicate_fast_improvement(flag, "model-steward", "   ", "reviewed")


def test_adjudicate_fast_improvement_produces_a_grade_4_claim_attributable_to_a_registered_role() -> None:
    flag = flag_fast_improvement({"sensor": {"id": "s"}, "baseline": 10.0, "current": 30.0})
    result = adjudicate_fast_improvement(flag, "model-steward", "genuine improvement, not gaming", "reviewed the underlying data")
    assert result["kind"] == "fast-improvement-adjudication"
    assert result["evidence_grade"] == 4
    assert result["claimed_by"] == "model-steward"
    assert result["claimed_by"] in role_ids()
    assert result["finding"] == "genuine improvement, not gaming"


# -- the labelled corpus ----------------------------------------------------------------------


def test_the_labelled_corpus_spans_every_ladder_outcome(corpus: list[dict]) -> None:
    assert len(corpus) == 5
    outcomes = {(item["expected"]["admitted"], item["expected"]["stopped_at"]) for item in corpus}
    assert outcomes == {
        (True, None),
        (False, "purpose"),
        (False, "necessity"),
        (False, "proportionality"),
        (False, None),  # DPIA-gated: the ladder itself passed
    }


def test_every_corpus_item_carries_the_fields_evaluate_requires(corpus: list[dict]) -> None:
    for item in corpus:
        assert {"id", "input", "expected"} <= item.keys()
        assert {"sensor", "purpose", "necessity", "proportionality", "dpia"} <= item["input"].keys()
        assert {"admitted", "stopped_at"} <= item["expected"].keys()


def test_ethics_gate_passes_its_own_labelled_corpus(corpus: list[dict]) -> None:
    result = evaluate(SKILL, admit, corpus, scorer=scorer)
    assert result.passed, f"scored {result.score}, threshold {result.threshold}: {result.as_dict()}"
    assert result.threshold == threshold_for(SKILL)


def test_a_degraded_gate_fails_the_threshold(corpus: list[dict]) -> None:
    def admits_everything(payload: dict) -> dict:
        return {"admitted": True, "ladder": {"stopped_at": None}}

    result = evaluate(SKILL, admits_everything, corpus, scorer=scorer)
    assert result.score < 1.0
    assert not result.passed
