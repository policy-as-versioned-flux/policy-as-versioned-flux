"""TEST_ONLY attribution mechanics, not independent real-world labels or model permission.

Literal expectations describe small worked rule examples. They are never added to the fitted
corpora, scored population or committed score history. The actual generic evaluator is the seam.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

import pytest

from twin import record_skill_scores as rss
from twin import signal_classify as sc
from twin.skills import Stated, evaluate


def test_actual_signal_basis_can_be_checked_without_claiming_a_measurable_population() -> None:
    payload = {"statement": "Atlas liquidation", "source": "test-only notice A",
               "candidates": [{"id": "atlas", "name": "Atlas"}, {"id": "other", "name": "Other"}]}
    basis = {
        "method": "signal-keywords-and-overlap/v1",
        "signal": {"statement": "Atlas liquidation", "source": "test-only notice A"},
        "steep_keywords": ["liquidation"],
        "steep_default": "economic", "steep_default_used": False,
        "claim_grade_rule": {"kind": "fixed model assertion", "value": 5},
        "candidate_overlaps": [{"id": "atlas", "name": "Atlas", "tokens": ["atlas"]},
                               {"id": "other", "name": "Other", "tokens": []}],
        "binding_rule": "first maximum token overlap",
    }
    # Before the implementation this is the real raw function, giving UNSCOREABLE. The new
    # entrypoint must reach the SAME computation, with its own decision witnesses attached.
    fn = getattr(sc, "classify_stated", sc.classify)
    result = evaluate(sc.SKILL, fn, [{"id": "TEST_ONLY-signal", "input": payload,
        "expected": {"steep": "political", "component": "atlas"}, "basis": basis}], scorer=sc.scorer)
    assert result.items[0].verdict == "right"
    assert result.outcome == "not-measurable"


def test_actual_evolution_basis_discloses_the_rule_and_its_dated_sources() -> None:
    from twin import evolution_judge as ej
    payload = {"component": {"id": "build", "name": "Construction"},
               "evidence": [{"statement": "A dated account", "source": "TEST_ONLY record B", "observed_at": "2026-01-02"}]}
    basis = {"method": "maturity-keywords/v1", "component": {"id": "build", "name": "Construction"},
             "evidence": [{"statement": "A dated account", "source": "TEST_ONLY record B", "observed_at": "2026-01-02"}],
             "matched_phrase": "construction", "rule_position": 0.6}
    result = evaluate(ej.SKILL, getattr(ej, "judge_stated", ej.judge), [
        {"id": "TEST_ONLY-evolution", "input": payload, "expected": {"evolution_position": 0.6}, "basis": basis}
    ], scorer=ej.scorer)
    assert result.items[0].verdict == "right"
    assert result.outcome == "not-measurable"


def test_actual_causal_basis_covers_both_metrics_and_discloses_constant_magnitude() -> None:
    from twin import causal_claims as cc
    payload = {"from": {"id": "a", "name": "A"}, "to": {"id": "b", "name": "B"},
               "evidence": [{"statement": "Established mechanism: support within a month", "source": "TEST_ONLY record C"}]}
    basis = {"method": "causal-keywords/v1", "from": {"id": "a", "name": "A"}, "to": {"id": "b", "name": "B"},
        "evidence": [{"statement": "Established mechanism: support within a month", "source": "TEST_ONLY record C"}],
        "grade_marker": "established mechanism", "sign_marker": "support", "lag_marker": "within a month",
        "defaults": {"evidence_grade": 5, "sign": "negative", "lag_days": 180},
        "defaults_used": {"evidence_grade": False, "sign": False, "lag_days": False},
        "elasticity_rule": {"method": "fixed fitted mode with grade-scaled width", "mode": 0.375, "band_per_grade": 0.05},
        "candidate_confounders": [], "alternative_rule": "reverse causation plus declared candidate common causes"}
    for metric, scorer in [(cc.SKILL, cc.scorer), (cc.GRADE_SKILL, cc.grade_scorer)]:
        result = evaluate(metric, getattr(cc, "propose_stated", cc.propose), [{"id": "TEST_ONLY-causal", "input": payload,
            "expected": {"sign": "positive", "lag_days": 30, "elasticity_mode": 0.375, "evidence_grade": 3}, "basis": basis}], scorer=scorer)
        assert result.items[0].verdict == "right"
        assert result.outcome == "not-measurable"


def test_actual_gameplay_basis_cites_graph_witnesses_and_unchecked_incumbency() -> None:
    from twin import gameplay_lens as gl
    payload = {"positions": [{"component": "base", "stage": "product", "evolution": 0.65}],
               "edges": [{"type": "needs", "from": "base", "to": "adjacent"},
                         {"type": "owns", "from": "org", "to": "adjacent"}], "org_components": ["base"]}
    # Independently authored TEST_ONLY graph expectation; no output is used to construct it.
    basis = {"method": "graph-play-preconditions/v1",
        "positions": {"base": {"stage": "product", "evolution": 0.65}},
        "needs_out": {"base": ["adjacent"]}, "needs_in": {"adjacent": ["base"]}, "held_by": {"adjacent": ["org"]},
        "org_components": ["base"], "land_grab_min_position": 0.6, "young_stages": ["genesis", "custom-built"],
        "checks": [{"component": "base", "play": "exploit-commoditisation", "witness": None},
                   {"component": "base", "play": "land-grab", "witness": {"stage": "product", "evolution_position": 0.65,
                     "adjacent_component_held": "adjacent", "held_by": ["org"], "incumbency_checked": False}}]}
    result = evaluate(gl.SKILL, getattr(gl, "propose_stated", gl.propose), [{"id": "TEST_ONLY-gameplay", "input": payload,
        "expected": {"opportunities": [["land-grab", "base"]]}, "basis": basis}], scorer=gl.scorer)
    assert result.items[0].verdict == "right"
    assert result.outcome == "not-measurable"


def test_actual_substrate_basis_states_recipe_and_generation_witnesses_only() -> None:
    from twin import substrate_generator as sg
    text = ('schema: twin.substrate-recipe/v1\nid: TEST_ONLY-recipe\nseed: 1\nmodel_version: TEST_ONLY-model\n'
            'templates: [Event, Message, HR, Telemetry]\nplanted_signals: [TEST_ONLY-plant]\n')
    basis = {"method": "deterministic-recipe-generation/v1",
        "recipe": {"id": "TEST_ONLY-recipe", "seed": 1, "model_version": "TEST_ONLY-model",
                   "templates": ["Event", "Message", "HR", "Telemetry"], "planted_signals": ["TEST_ONLY-plant"]},
        "focus_rule": "seeded choice from declared focus pool", "focus_pool": ["project-atlas", "project-kestrel", "the-migration", "project-lighthouse", "the-onboarding-flow", "project-harbour"],
        "focus_entity": "project-kestrel", "lines_per_channel": 6,
        "channel_recipes": [{"channel": "events", "seed": 1, "templates": ["Event"], "plant_index": 3},
                            {"channel": "communications", "seed": 2, "templates": ["Message"], "plant_index": None},
                            {"channel": "hr", "seed": 3, "templates": ["HR"], "plant_index": None},
                            {"channel": "telemetry", "seed": 4, "templates": ["Telemetry"], "plant_index": None}]}
    result = evaluate(sg.SKILL, getattr(sg, "generate_from_recipe_yaml_stated", sg.generate_from_recipe_yaml), [
        {"id": "TEST_ONLY-substrate", "input": text, "expected": {"channels": ["events", "communications", "hr", "telemetry"],
         "planted_signals": ["TEST_ONLY-plant"], "min_mundane_fraction": 0.7}, "basis": basis}], scorer=sg.scorer)
    assert result.items[0].verdict == "right"
    assert result.outcome == "not-measurable"


def test_actual_ethics_basis_records_only_walked_rungs_and_real_policy_sources() -> None:
    from twin import ethics_gate as eg
    payload = {"sensor": {"id": "mood-sensor-no-scenario"}, "purpose": {"scenario": "", "will_act": False},
               "necessity": {}, "proportionality": {}, "dpia": {"channels": [], "complete": False}}
    basis = {"rung_checks": [{"rung": "purpose", "readings": {"scenario": "", "will_act": False}}],
             "sensor_schema": "twin.sensors/v1", "sensor_version": 1,
             "sensor_id": "mood-sensor-no-scenario", "dpia_channels": []}

    def check_basis(actual, expected):
        return {"rung_checks": actual["rung_checks"], "sensor_schema": actual["sensor_table"]["schema"],
                "sensor_version": actual["sensor_table"]["version"], "sensor_id": actual["sensor_table"]["row"]["sensor"],
                "dpia_channels": actual["dpia_readings"]["channels"]} == expected

    result = evaluate(eg.SKILL, getattr(eg, "admit_stated", eg.admit), [{"id": "TEST_ONLY-ethics", "input": payload,
        "expected": {"admitted": False, "stopped_at": "purpose"}, "basis": basis}], scorer=eg.scorer, basis_scorer=check_basis)
    assert result.items[0].verdict == "right"
    assert result.outcome == "not-measurable"


def test_recorder_selects_stated_evaluation_without_changing_raw_baselines() -> None:
    from twin import record_skill_scores as rss
    payload = {"statement": "Atlas liquidation", "source": "TEST_ONLY registry notice", "candidates": [{"id": "atlas", "name": "Atlas"}]}
    # This independent checker tests the actual selected rule and source, never expected labels
    # copied into input. A single checked item still cannot promote the model.
    def basis_holds(actual, expected):
        return actual["steep_keywords"] == expected["keywords"] and actual["signal"]["source"] == expected["source"]
    fn = getattr(rss, "evaluation_skill", lambda name: sc.classify)(sc.SKILL)
    result = evaluate(sc.SKILL, fn, [{"id": "TEST_ONLY-registry", "input": payload,
        "expected": {"steep": "political", "component": "atlas"},
        "basis": {"keywords": ["liquidation"], "source": "TEST_ONLY registry notice"}}], scorer=sc.scorer, basis_scorer=basis_holds)
    assert result.items[0].verdict == "right"
    assert result.outcome == "not-measurable"


# These seven metric cases are deliberately small TEST_ONLY software examples, not a labelled
# population. Their checkers inspect source/rule facts; no expected answer constructs a basis.
def _example(metric: str) -> tuple[Any, dict[str, Any], dict[str, Any], dict[str, Any]]:
    if metric == "signal-classify":
        return ({"statement": "Atlas liquidation", "source": "TEST_ONLY notice A", "candidates": [{"id": "atlas", "name": "Atlas"}]},
                {"steep": "political", "component": "atlas"}, {"steep": "political", "component": "foreign"},
                {"method": "signal-keywords-and-overlap/v1", "witness": ["TEST_ONLY notice A", ["liquidation"]]})
    if metric == "evolution-judge":
        return ({"component": {"id": "build", "name": "Construction"}, "evidence": [{"statement": "A dated account", "source": "TEST_ONLY record B"}]},
                {"evolution_position": 0.6}, {"evolution_position": 0.0},
                {"method": "maturity-keywords/v1", "witness": ["TEST_ONLY record B", "construction"]})
    if metric in ("causal-claims", "causal-claims-grade-accuracy"):
        return ({"from": {"id": "a"}, "to": {"id": "b"}, "evidence": [{"statement": "Established mechanism: support within a month", "source": "TEST_ONLY record C"}]},
                {"sign": "positive", "lag_days": 30, "elasticity_mode": 0.375, "evidence_grade": 3},
                {"sign": "negative", "lag_days": 365, "elasticity_mode": 0.0, "evidence_grade": 1},
                {"method": "causal-keywords/v1", "witness": ["TEST_ONLY record C", "established mechanism", "support", "within a month"]})
    if metric == "gameplay-lens":
        return ({"positions": [{"component": "base", "stage": "product", "evolution": 0.65}],
                 "edges": [{"type": "needs", "from": "base", "to": "adjacent"}, {"type": "owns", "from": "org", "to": "adjacent"}], "org_components": ["base"]},
                {"opportunities": [["land-grab", "base"]]}, {"opportunities": []},
                {"method": "graph-play-preconditions/v1", "witness": ["product", 0.65, ["org"]]})
    if metric == "substrate-generator":
        return ('schema: twin.substrate-recipe/v1\nid: TEST_ONLY-recipe\nseed: 1\nmodel_version: TEST_ONLY-model\ntemplates: [Event, Message, HR, Telemetry]\nplanted_signals: [TEST_ONLY-plant]\n',
                {"channels": ["events", "communications", "hr", "telemetry"], "planted_signals": ["TEST_ONLY-plant"], "min_mundane_fraction": 0.7},
                {"channels": ["events"], "planted_signals": [], "min_mundane_fraction": 1.0},
                {"method": "deterministic-recipe-generation/v1", "witness": [1, "TEST_ONLY-model", ["Event", "Message", "HR", "Telemetry"]]})
    assert metric == "ethics-gate"
    return ({"sensor": {"id": "mood-sensor-no-scenario"}, "purpose": {"scenario": "", "will_act": False}, "necessity": {}, "proportionality": {}, "dpia": {"channels": []}},
            {"admitted": False, "stopped_at": "purpose"}, {"admitted": True, "stopped_at": None},
            {"method": "sensor-ladder-and-dpia/v1", "witness": ["mood-sensor-no-scenario", {"scenario": "", "will_act": False}]})


def _checked_witness(basis: dict[str, Any]) -> dict[str, Any]:
    method = basis["method"]
    if method == "signal-keywords-and-overlap/v1":
        witness = [basis["signal"]["source"], basis["steep_keywords"]]
    elif method == "maturity-keywords/v1":
        witness = [basis["evidence"][0]["source"], basis["matched_phrase"]]
    elif method == "causal-keywords/v1":
        witness = [basis["evidence"][0]["source"], basis["grade_marker"], basis["sign_marker"], basis["lag_marker"]]
    elif method == "graph-play-preconditions/v1":
        witness = [basis["positions"]["base"]["stage"], basis["positions"]["base"]["evolution"], basis["held_by"]["adjacent"]]
    elif method == "deterministic-recipe-generation/v1":
        witness = [basis["recipe"]["seed"], basis["recipe"]["model_version"], basis["recipe"]["templates"]]
    else:
        assert method == "sensor-ladder-and-dpia/v1"
        witness = [basis["sensor_table"]["row"]["sensor"], basis["rung_checks"][0]["readings"]]
    return {"method": method, "witness": witness}


def _metric_scorer(metric: str) -> Callable[[Any, Any], bool]:
    from twin import causal_claims as cc, evolution_judge as ej, gameplay_lens as gl, substrate_generator as sg, ethics_gate as eg
    return {sc.SKILL: sc.scorer, ej.SKILL: ej.scorer, cc.SKILL: cc.scorer,
            cc.GRADE_SKILL: cc.grade_scorer, gl.SKILL: gl.scorer, sg.SKILL: sg.scorer, eg.SKILL: eg.scorer}[metric]


@pytest.mark.parametrize("metric", rss.METRICS)
def test_all_actual_metric_entrypoints_keep_negative_basis_controls(metric: str) -> None:
    payload, expected, wrong, basis = _example(metric)
    actual_fn = rss.evaluation_skill(metric)
    actual = actual_fn(payload)
    assert isinstance(actual, Stated)
    assert actual.answer == rss.raw_skill(metric)(payload)
    assert _checked_witness(actual.basis) == basis
    # Use each production metric scorer, unchanged. The fixture's checker is independent of
    # the answer and inspects a cited rule/source witness rather than answer equality.
    scorer = _metric_scorer(metric)

    def run(fn, answer_label, basis_label):
        item = {"id": "TEST_ONLY-negative-controls", "input": payload, "expected": answer_label}
        if basis_label is not None:
            item["basis"] = basis_label
        return evaluate(metric, fn, [item], scorer=scorer, basis_scorer=lambda a, b: _checked_witness(a) == b)

    assert run(actual_fn, expected, basis).items[0].verdict == "right"
    assert run(actual_fn, expected, {"method": basis["method"], "witness": ["FOREIGN source/rule"]}).items[0].verdict == "wrong-basis"
    assert run(actual_fn, expected, None).items[0].verdict == "unscoreable"
    # Disclosed negative adapter REMOVES a real basis; it is never a production entrypoint.
    assert run(lambda x: Stated(actual_fn(x).answer, None), expected, basis).items[0].verdict == "unscoreable"
    assert run(actual_fn, wrong, basis).items[0].verdict == "wrong"
    assert run(actual_fn, expected, basis).outcome == "not-measurable"


@pytest.mark.parametrize("metric", rss.METRICS)
def test_hidden_input_labels_cannot_select_an_actual_answer_or_basis(metric: str) -> None:
    payload, _, _, _ = _example(metric)
    fn = rss.evaluation_skill(metric)
    original = fn(payload)
    poisoned = deepcopy(payload)
    if isinstance(poisoned, str):
        poisoned += 'expected: foreign-label\nbasis: foreign-basis\n'
    else:
        poisoned.update(expected="foreign-label", basis="foreign-basis")
        for key in ("component", "from", "to", "sensor"):
            if key in poisoned:
                poisoned[key].update(expected="foreign-label", basis="foreign-basis")
        for key in ("evidence", "positions", "candidates"):
            for row in poisoned.get(key, []):
                row.update(expected="foreign-label", basis="foreign-basis")
    assert fn(poisoned) == original


@pytest.mark.parametrize("metric", rss.METRICS)
def test_a_changed_source_witness_cannot_reuse_the_old_checked_basis(metric: str) -> None:
    payload, expected, _, old_basis = _example(metric)
    changed = deepcopy(payload)
    if metric == "signal-classify":
        changed["source"] = "FOREIGN notice"
    elif metric in ("evolution-judge", "causal-claims", "causal-claims-grade-accuracy"):
        changed["evidence"][0]["source"] = "FOREIGN record"
    elif metric == "gameplay-lens":
        changed["edges"][1]["from"] = "FOREIGN holder"
    elif metric == "substrate-generator":
        changed = changed.replace("seed: 1\n", "seed: 2\n")
    else:
        changed["purpose"]["will_act"] = True
    scorer = _metric_scorer(metric)
    result = evaluate(metric, rss.evaluation_skill(metric), [{"id": "TEST_ONLY-foreign-source", "input": changed,
        "expected": expected, "basis": old_basis}], scorer=scorer, basis_scorer=lambda a, b: _checked_witness(a) == b)
    assert result.items[0].verdict == "wrong-basis"
    assert result.outcome == "not-measurable"


def test_gameplay_does_not_start_requiring_unread_fields_on_out_of_scope_positions() -> None:
    from twin import gameplay_lens as gl
    # The existing API indexes component IDs but never reads an out-of-scope position. Trace
    # capture must preserve that boundary, rather than imposing new validation on the raw API.
    payload = {"positions": [{"component": "out-of-scope"}], "edges": [], "org_components": []}
    assert gl.propose(payload) == {"opportunities": []}
    assert gl.propose_stated(payload).answer == {"opportunities": []}


def test_signal_fallback_and_fixed_grade_are_checked_as_rules_not_inferred_from_the_answer() -> None:
    payload = {"statement": "Atlas ordinary update", "source": "TEST_ONLY default notice", "candidates": [{"id": "atlas", "name": "Atlas"}]}
    expected_basis: dict[str, Any] = {"source": "TEST_ONLY default notice", "default": "economic", "used": True,
                      "grade": {"kind": "fixed model assertion", "value": 5}}

    def basis_holds(actual, expected):
        return {"source": actual["signal"]["source"], "default": actual.get("steep_default"),
                "used": actual.get("steep_default_used"), "grade": actual.get("claim_grade_rule")} == expected

    item = {"id": "TEST_ONLY-signal-fallback", "input": payload, "expected": {"steep": "economic", "component": "atlas"}, "basis": expected_basis}
    correct = evaluate(sc.SKILL, rss.evaluation_skill(sc.SKILL), [item], scorer=sc.scorer, basis_scorer=basis_holds)
    assert correct.items[0].verdict == "right"
    assert correct.outcome == "not-measurable"
    for wrong_basis in [{**expected_basis, "default": "political"},
                        {**expected_basis, "grade": {"kind": "fixed model assertion", "value": 1}},
                        {**expected_basis, "used": False}]:
        wrong = evaluate(sc.SKILL, rss.evaluation_skill(sc.SKILL), [{**item, "basis": wrong_basis}], scorer=sc.scorer, basis_scorer=basis_holds)
        assert wrong.items[0].verdict == "wrong-basis"


@pytest.mark.parametrize("metric", ["causal-claims", "causal-claims-grade-accuracy"])
def test_causal_fallback_values_and_rules_are_checked_even_when_every_marker_is_absent(metric: str) -> None:
    from twin import causal_claims as cc
    payload = {"from": {"id": "a"}, "to": {"id": "b"}, "evidence": [{"statement": "An ordinary account", "source": "TEST_ONLY default record"}]}
    expected_basis: dict[str, Any] = {"source": "TEST_ONLY default record", "markers": [None, None, None],
        "defaults": {"evidence_grade": 5, "sign": "negative", "lag_days": 180},
        "used": {"evidence_grade": True, "sign": True, "lag_days": True}}

    def basis_holds(actual, expected):
        return {"source": actual["evidence"][0]["source"], "markers": [actual["grade_marker"], actual["sign_marker"], actual["lag_marker"]],
                "defaults": actual.get("defaults"), "used": actual.get("defaults_used")} == expected

    scorer = cc.scorer if metric == cc.SKILL else cc.grade_scorer
    item = {"id": "TEST_ONLY-causal-fallback", "input": payload, "expected": {"sign": "negative", "lag_days": 180, "elasticity_mode": 0.375, "evidence_grade": 5}, "basis": expected_basis}
    correct = evaluate(metric, rss.evaluation_skill(metric), [item], scorer=scorer, basis_scorer=basis_holds)
    assert correct.items[0].verdict == "right"
    assert correct.outcome == "not-measurable"
    for field, value in [("evidence_grade", 1), ("sign", "positive"), ("lag_days", 0)]:
        wrong_basis = {**expected_basis, "defaults": {**expected_basis["defaults"], field: value}}
        wrong = evaluate(metric, rss.evaluation_skill(metric), [{**item, "basis": wrong_basis}], scorer=scorer, basis_scorer=basis_holds)
        assert wrong.items[0].verdict == "wrong-basis"
