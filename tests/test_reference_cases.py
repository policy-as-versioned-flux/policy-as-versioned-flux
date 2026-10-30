"""TEST_ONLY case custody at admission and the existing evaluate/Stated seam."""
from __future__ import annotations

import hashlib
from typing import Any

import pytest

from twin.reference_cases import admit_reference, source_record
from twin.skills import Stated, evaluate
from twin import evolution_judge


def example() -> tuple[dict[str, Any], dict[str, Any]]:
    source = source_record(b'TEST_ONLY dated capability account', 'TEST_ONLY:account', 'test-v1')
    rights = source_record(b'TEST_ONLY permission for development research', 'TEST_ONLY:rights', 'test-v1')
    scope = {'purpose': 'development', 'claim': 'agent-reference-agreement',
             'metric': 'evolution-judge', 'domain': 'TEST_ONLY:mars',
             'capability': 'TEST_ONLY:flight', 'organisation': 'TEST_ONLY:NASA',
             'as_of': '2021-04-19', 'frame': 'capability in its operating environment'}
    witness = {'source': 'account', 'start': 0, 'end': source['bytes'], 'sha256': source['sha256']}
    payload = {'component': {'id': 'flight', 'name': 'TEST_ONLY Mars flight'},
               'evidence': [{'statement': 'First trial flight', 'date': '2021-04-19', 'source': 'TEST_ONLY:account'}]}
    expected = {'evolution_position': 0.125}
    case = {'id': 'TEST_ONLY-flight', 'sources': {'account': source, 'rights': rights},
            'context': scope.copy(), 'input': payload, 'expected': expected,
            'reference_kind': 'agent-authored', 'limitations': ['Not empirical calibration'],
            'group': 'TEST_ONLY:publisher', 'exposure': {'status': 'exposed', 'history': ['TEST_ONLY author saw labels']},
            'selection': {'decision': 'selected', 'reason': 'TEST_ONLY tracer'},
            'rights': {'statement': 'TEST_ONLY grant', 'uses': ['development'], 'evidence': ['rights'], 'covered_sources': ['account']},
            'field_support': {'evolution_position': {'sources': ['account'], 'meaning': 'Authored developmental coordinate', 'witnesses': [witness]}},
            'basis': {'facts': ['First trial flight'], 'source_hashes': {'account': source['sha256']}},
            'basis_binding': {}}
    # Bind the independently supplied basis to the declared input, labels and context.
    from twin.reference_cases import binding_for
    case['basis_binding'] = binding_for(case)
    return case, scope


def test_admitted_packet_is_immutable_and_projects_only_input_to_existing_evaluator() -> None:
    case, scope = example()
    admission = admit_reference(case, scope)
    assert admission.admitted, admission.reasons
    original = admission.packet_bytes
    case['expected']['evolution_position'] = 0.9
    case['input']['component']['name'] = 'changed after admission'
    assert admission.packet_bytes == original
    item = admission.evaluator_item()
    seen = []
    def test_only_candidate(payload):
        seen.append(payload)
        return Stated({'evolution_position': 0.125}, {'facts': ['First trial flight']})
    result = evaluate('evolution-judge', test_only_candidate, [item], scorer=evolution_judge.scorer,
                      basis_scorer=lambda actual, reference: actual['facts'] == reference['facts'])
    assert seen == [{'component': {'id': 'flight', 'name': 'TEST_ONLY Mars flight'},
                    'evidence': [{'statement': 'First trial flight', 'date': '2021-04-19', 'source': 'TEST_ONLY:account'}]}]
    assert result.items[0].verdict == 'right'
    assert result.outcome == 'not-measurable'
    assert result.measured_count == 1
    assert admission.input_projection() == seen[0]
    assert admission.packet_digest == hashlib.sha256(original).hexdigest()


def test_incomplete_causal_reference_is_held_with_missing_fields_conserved() -> None:
    case, scope = example()
    scope['metric'] = 'causal-claims'
    scope['claim'] = 'complete-causal-reference'
    case['context'] = scope.copy()
    case['expected'] = {'sign': None, 'lag_days': None, 'elasticity_mode': None, 'evidence_grade': None}
    from twin.reference_cases import binding_for
    case['basis_binding'] = binding_for(case)
    admission = admit_reference(case, scope)
    assert not admission.admitted
    assert 'missing-target:sign' in admission.reasons
    assert 'missing-target:lag_days' in admission.reasons
    assert 'missing-target:elasticity_mode' in admission.reasons
    assert 'missing-target:evidence_grade' in admission.reasons
    import json
    assert json.loads(admission.packet_bytes)['case']['expected'] == case['expected']
    import pytest
    with pytest.raises(ValueError, match='reference held'):
        admission.evaluator_item()


def test_rights_support_and_stale_source_bindings_are_refused() -> None:
    from copy import deepcopy
    from twin.reference_cases import binding_for
    case, scope = example()
    controls = []
    missing_rights = deepcopy(case)
    missing_rights.pop('rights')
    controls.append((missing_rights, 'missing-rights'))
    incomplete = deepcopy(case)
    incomplete['field_support'] = {}
    controls.append((incomplete, 'unsupported-target:evolution_position'))
    stale_basis = deepcopy(case)
    stale_basis['basis']['facts'] = ['Unbound replacement']
    controls.append((stale_basis, 'stale-basis-binding'))
    stale_source = deepcopy(case)
    stale_source['sources']['account'] = source_record(b'Replacement account', 'TEST_ONLY:account', 'test-v2')
    controls.append((stale_source, 'stale-source-basis:account'))
    changed_bytes = deepcopy(case)
    changed_bytes['sources']['account']['content_base64'] = 'Y2hhbmdlZA=='
    controls.append((changed_bytes, 'source-integrity:account'))
    foreign_rights = deepcopy(case)
    foreign_rights['rights']['evidence'] = ['absent-licence']
    controls.append((foreign_rights, 'unbound-rights'))
    wrong_use = deepcopy(case)
    wrong_use['rights']['uses'] = ['unrelated']
    controls.append((wrong_use, 'rights-scope-conflict'))
    silent_negative = deepcopy(case)
    silent_negative['context']['metric'] = 'gameplay-lens'
    silent_negative['expected'] = {'opportunities': []}
    silent_negative['field_support'] = {'opportunities': {'sources': ['account'], 'meaning': 'Absent mention'}}
    silent_negative['basis_binding'] = binding_for(silent_negative)
    controls.append((silent_negative, 'unsupported-negative-set'))
    for control, reason in controls:
        decision = admit_reference(control, control['context'])
        assert not decision.admitted, reason
        assert reason in decision.reasons


def test_context_conflicts_exposure_and_selection_cannot_promote_development_case() -> None:
    from copy import deepcopy
    from twin.reference_cases import binding_for
    case, scope = example()
    for key, value in [('domain', 'foreign'), ('frame', 'global aviation'), ('as_of', '2024-12-31'),
                       ('organisation', 'foreign'), ('capability', 'foreign')]:
        foreign = {**scope, key: value}
        assert 'scope-context-conflict' in admit_reference(case, foreign).reasons
    for key in ['as_of', 'frame', 'organisation', 'capability', 'claim', 'domain']:
        incomplete = {k: v for k, v in scope.items() if k != key}
        control = deepcopy(case)
        control['context'] = incomplete
        control['basis_binding'] = binding_for(control)
        assert 'missing-context:' + key in admit_reference(control, incomplete).reasons
    for key in ['group', 'exposure', 'selection', 'reference_kind', 'limitations']:
        control = deepcopy(case)
        control.pop(key)
        assert 'missing-' + key in admit_reference(control, scope).reasons
    held = deepcopy(case)
    held['selection'] = {'decision': 'held', 'reason': 'Prior unresolved disagreement'}
    assert 'selection-held' in admit_reference(held, scope).reasons
    qualification = {**scope, 'purpose': 'qualification'}
    assert 'qualification-requires-separately-admitted-population' in admit_reference(case, qualification).reasons


def test_malformed_targets_and_uncheckable_support_do_not_become_reference_authority() -> None:
    from copy import deepcopy
    from twin.reference_cases import binding_for
    case, scope = example()
    for value in ['0.125', True, 1.1, -0.1]:
        control = deepcopy(case)
        control['expected']['evolution_position'] = value
        control['basis_binding'] = binding_for(control)
        assert 'invalid-target:evolution_position' in admit_reference(control, scope).reasons
    control = deepcopy(case)
    control['reference_kind'] = 'reported-significance'
    assert 'reference-claim-conflict' in admit_reference(control, scope).reasons
    control = deepcopy(case)
    control['field_support']['evolution_position']['witnesses'] = [
        {'source': 'account', 'start': 0, 'end': 9, 'sha256': 'not-the-span'}]
    assert 'invalid-support-witness:evolution_position' in admit_reference(control, scope).reasons
    control = deepcopy(case)
    control['input']['expected'] = {'evolution_position': 0.125}
    control['basis_binding'] = binding_for(control)
    assert 'reference-fields-in-input' in admit_reference(control, scope).reasons


def test_field_support_requires_a_checked_span_not_only_a_source_name() -> None:
    case, scope = example()
    case['field_support']['evolution_position']['witnesses'] = []
    assert 'missing-support-witness:evolution_position' in admit_reference(case, scope).reasons


def test_missing_input_and_rights_for_a_different_source_remain_held() -> None:
    case, scope = example()
    case.pop('input')
    assert 'missing-input' in admit_reference(case, scope).reasons
    case, scope = example()
    case['rights']['covered_sources'] = ['rights']
    assert 'rights-do-not-cover-source:account' in admit_reference(case, scope).reasons


def test_witnesses_must_cover_declared_sources_and_bad_shapes_are_retained() -> None:
    from copy import deepcopy
    case, scope = example()
    unrelated = deepcopy(case)
    source = unrelated['sources']['rights']
    unrelated['field_support']['evolution_position']['witnesses'] = [
        {'source': 'rights', 'start': 0, 'end': source['bytes'], 'sha256': source['sha256']}]
    assert 'unbound-support-witness:evolution_position' in admit_reference(unrelated, scope).reasons
    for field in ['expected', 'sources', 'rights', 'basis', 'field_support', 'selection', 'exposure']:
        malformed = deepcopy(case)
        malformed[field] = ['bad object shape']
        decision = admit_reference(malformed, scope)
        assert not decision.admitted
        assert 'invalid-shape:' + field in decision.reasons


def test_existing_ethics_dpia_refusal_retains_explicit_null_ladder_stop() -> None:
    """The existing scorer distinguishes overall DPIA refusal from a failed ladder rung."""
    from copy import deepcopy
    from twin import ethics_gate
    from twin.reference_cases import binding_for
    case, scope = example()
    contract = next(row for row in ethics_gate.labelled_corpus()
                    if row['id'] == 'keystroke-monitoring-no-dpia')
    scope.update(metric='ethics-gate', claim='task-conformance')
    case.update(context=scope.copy(), input=contract['input'],
                expected={'admitted': False, 'stopped_at': None}, reference_kind='declared-constraints')
    support = case['field_support']['evolution_position']
    case['field_support'] = {field: deepcopy(support) for field in ('admitted', 'stopped_at')}
    case['basis']['contract'] = {'last_ladder_rung': 'proportionality',
                               'channels': ['keystroke'], 'complete': False}
    case['basis_binding'] = binding_for(case)
    decision = admit_reference(case, scope)
    assert decision.admitted, decision.reasons
    assert decision.evaluator_item()['expected'] == {'admitted': False, 'stopped_at': None}

    def basis_holds(actual, expected):
        return {'last_ladder_rung': actual['rung_checks'][-1]['rung'],
                'channels': actual['dpia_readings']['channels'],
                'complete': actual['dpia_readings']['complete']} == expected['contract']

    result = evaluate('ethics-gate', ethics_gate.admit_stated, [decision.evaluator_item()],
                      scorer=ethics_gate.scorer, basis_scorer=basis_holds)
    assert result.items[0].verdict == 'right'
    assert result.outcome == 'not-measurable'
    missing = deepcopy(case)
    missing['expected'].pop('stopped_at')
    missing['basis_binding'] = binding_for(missing)
    assert 'missing-target:stopped_at' in admit_reference(missing, scope).reasons


@pytest.mark.parametrize('witnesses', [None, ['bad'], {'source': 'account'},
                                       [{'source': ['unhashable']}], [{'source': None}]])
def test_malformed_support_witness_declarations_return_retained_holds(witnesses: Any) -> None:
    import json
    from copy import deepcopy
    case, scope = example()
    case['field_support']['evolution_position']['witnesses'] = deepcopy(witnesses)
    decision = admit_reference(case, scope)
    assert not decision.admitted
    assert 'invalid-shape:field-support-witnesses:evolution_position' in decision.reasons
    assert (json.loads(decision.packet_bytes)['case']['field_support']['evolution_position']['witnesses']
            == witnesses)
    with pytest.raises(ValueError, match='reference held'):
        decision.evaluator_item()


@pytest.mark.parametrize('section,field,value', [
    ('rights', 'uses', None), ('rights', 'uses', 'development'),
    ('rights', 'uses', {'development': True}), ('rights', 'uses', [None]),
    ('rights', 'evidence', None), ('rights', 'evidence', 'rights'),
    ('rights', 'evidence', [['unhashable']]),
    ('rights', 'covered_sources', None), ('rights', 'covered_sources', 'account'),
    ('rights', 'covered_sources', [{'source': 'account'}]),
    ('basis', 'source_hashes', None), ('basis', 'source_hashes', ['bad']),
    ('basis', 'source_hashes', 'bad'), ('basis', 'source_hashes', {'account': None}),
])
def test_malformed_nested_rights_and_basis_declarations_are_conserved_as_holds(
    section: str, field: str, value: Any,
) -> None:
    import json
    from copy import deepcopy
    case, scope = example()
    case[section][field] = deepcopy(value)
    decision = admit_reference(case, scope)
    assert not decision.admitted
    assert 'invalid-shape:' + section + '.' + field in decision.reasons
    assert json.loads(decision.packet_bytes)['case'][section][field] == value
    with pytest.raises(ValueError, match='reference held'):
        decision.evaluator_item()


@pytest.mark.parametrize('claim', [['bad'], {'bad': 'claim'}])
def test_malformed_requested_claim_is_held_before_reference_kind_lookup(claim: Any) -> None:
    import json
    from twin.reference_cases import binding_for
    case, scope = example()
    scope['claim'] = claim
    case['context'] = scope.copy()
    case['basis_binding'] = binding_for(case)
    decision = admit_reference(case, scope)
    assert not decision.admitted
    assert 'missing-context:claim' in decision.reasons
    assert json.loads(decision.packet_bytes)['requested_scope']['claim'] == claim
