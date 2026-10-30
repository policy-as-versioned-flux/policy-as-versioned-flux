"""Explicit private TEST_ONLY capture mechanics, never operational causal permission."""
import json

from twin import qualification as q
from twin.reference_cases import admit_reference, binding_for
from twin.skills import Stated
from bench.qualification_controls import reference, envelope, basis_holds

CALLS = []


def mechanical_causal(payload, config):
    CALLS.append(payload['ordinal'])
    return q.canonical({'edge': {'from': 'TEST_ONLY-a', 'to': 'TEST_ONLY-b', 'type': 'influences',
        'sign': 'positive' if payload['ordinal'] % 2 == 0 else 'negative',
        'lag_days': 10 + payload['ordinal'] * 80, 'elasticity': {'min': .1, 'mode': .2 + payload['ordinal'] * .2, 'max': .9},
        'evidence_grade': 3}, 'confounders': [], 'alternatives': ['TEST_ONLY retained alternative']})


def parse_causal(raw, config):
    return Stated(json.loads(raw), 'TEST_ONLY shared actual basis')


def causal_pair():
    actor = q.Actor.freeze(mechanical_causal, parse_causal, {'purpose': 'TEST_ONLY'})
    selections = []
    for metric in ('causal-claims', 'causal-claims-grade-accuracy'):
        admissions = []
        for index in range(3):
            packet = json.loads(reference(case_id=f'TEST_ONLY-causal-{index}', org=('driftwood', 'tuppence', 'ludlow')[index]).packet_bytes)
            case, scope = packet['case'], packet['requested_scope']
            scope['metric'] = metric
            case['context'] = scope
            case['input'] = {'ordinal': index, 'statement': 'TEST_ONLY shared source request'}
            case['expected'] = {'evidence_grade': 3}
            if metric == 'causal-claims':
                case['expected'].update(sign='positive' if index % 2 == 0 else 'negative', lag_days=10 + index * 80,
                                        elasticity_mode=.2 + index * .2)
            support = next(iter(case['field_support'].values()))
            case['field_support'] = {name: support for name in case['expected']}
            case['basis']['witness'] = 'TEST_ONLY shared actual basis'
            case['basis_binding'] = binding_for(case)
            admitted = admit_reference(case, scope)
            assert admitted.admitted, admitted.reasons
            admissions.append(admitted)
        population = q.Population.freeze(metric, tuple(admissions), envelope(),
            {'status': 'development', 'history': ['TEST_ONLY openly authored'], 'training_provenance': 'unknown'})
        selections.append(q.Selection.freeze(actor, population, basis_holds,
            review=q.PopulationReview.test_only(population), test_only=q.TEST_ONLY_MECHANICS))
    return tuple(selections)


def test_two_metric_views_share_one_authenticated_actual_invocation_per_subject():
    quantity, grade = causal_pair()
    group = q.CaptureGroup.freeze((quantity, grade))
    before = len(CALLS)
    capture = group.capture()
    quantity_view, grade_view = group.view(quantity, capture), group.view(grade, capture)
    assert CALLS[before:] == [0, 1, 2]
    assert quantity.captured_outputs(quantity_view) == grade.captured_outputs(grade_view)
    assert quantity.evaluate(quantity_view).attributable_rate == 1.0
    assert grade.evaluate(grade_view).attributable_rate == 1.0
    assert len(CALLS) == before + 3


def test_group_durable_import_preserves_core_and_independent_metric_bindings(tmp_path):
    import hashlib
    from pathlib import Path
    quantity, grade = causal_pair()
    group = q.CaptureGroup.freeze((quantity, grade))
    core = group.capture()
    before = len(CALLS)
    raw = group.archive(core)
    packet = json.loads(raw)
    assert 'rows' not in packet['members'][0]['capture']
    assert 'rows' not in packet['members'][1]['capture']
    path = tmp_path / 'group.json'
    path.write_bytes(raw)
    registry = {'schema': 'twin.qualification-registry/v1', 'entries': [
        {'bundle': path.name, 'sha256': hashlib.sha256(raw).hexdigest()}]}
    catalogue = tmp_path / 'registry.json'
    catalogue.write_bytes(q.canonical(registry))
    restored = q.Resolver.from_catalogue(catalogue, q.digest(registry), allow_test_only=True)
    for metric in ('causal-claims', 'causal-claims-grade-accuracy'):
        selected, view = restored._bindings[(metric, quantity.actor.model_version)]
        assert selected.evaluate(view).attributable_rate == 1.0
    assert len(CALLS) == before


def test_group_views_cannot_swap_raw_core_membership_or_rows():
    from dataclasses import replace
    import pytest
    quantity, grade = causal_pair()
    group = q.CaptureGroup.freeze((quantity, grade))
    core, foreign = group.capture(), group.capture()
    view = group.view(quantity, core)
    before = len(CALLS)
    for forged in (replace(view, _core=foreign), replace(view, packet=q.canonical({
            **json.loads(view.packet), 'row_refs': [{'id': 'TEST_ONLY-causal-0', 'index': 1}]})),
            replace(view, _group=None), replace(view, authentication=b'child supplied')):
        with pytest.raises(ValueError):
            quantity.captured_outputs(forged)
    with pytest.raises(ValueError):
        grade.captured_outputs(view)
    with pytest.raises(ValueError):
        group.view(quantity, replace(core, packet=q.canonical({**json.loads(core.packet), 'rows': []})))
    assert len(CALLS) == before


def test_independent_metric_baseline_and_variance_are_not_inherited():
    quantity, grade = causal_pair()
    group = q.CaptureGroup.freeze((quantity, grade))
    core = group.capture()
    before = len(CALLS)
    quantities = quantity.facts(group.view(quantity, core))
    grades = grade.facts(group.view(grade, core))
    assert grades['baseline'].score == 1.0
    assert quantities['baseline'].score < grades['baseline'].score
    assert max(quantities['variance'].values()) == 3
    assert set(grades['variance'].values()) == {1}
    assert quantities['population_digest'] != grades['population_digest']
    assert len(CALLS) == before
