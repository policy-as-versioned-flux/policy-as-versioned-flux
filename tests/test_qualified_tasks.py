"""TEST_ONLY parent serialization controls, never earned task permissions."""
import base64
import copy

import pytest

from twin import qualification as q, qualified_tasks as parent
from twin.task_contracts import TaskContract, validate


def snapshot(task):
    contract = TaskContract.freeze(task)
    target = {'causal': {'kind': 'edge', 'from': 'test-only-a', 'to': 'test-only-b'},
        'gameplay': {'kind': 'map', 'organisation': 'driftwood'},
        'ethics': {'kind': 'sensor', 'sensor': 'test-only-sensor', 'policy_sha256': 'b' * 64},
        'evolution': {'kind': 'component', 'component': 'test-only-a'}}[task]
    basis = {'reason': 'TEST_ONLY literal reasoning, not adjudicated support',
        'witnesses': [{'path': ['context', 'metadata', 'test-only-source', 'statement', 'text'], 'quote': 'TEST_ONLY text'}],
        'calculations': ['TEST_ONLY explicit calculation']}
    if task == 'gameplay':
        basis['checks'] = [{'play': play, 'component': 'test-only-a', 'present': False,
            'reason': 'TEST_ONLY negative', 'witnesses': copy.deepcopy(basis['witnesses']), 'incumbency_checked': False}
            for play in ('land-grab', 'exploit-commoditisation')]
    answer = {'evolution': {'evolution_position': .4}, 'causal': {
        'edge': {'from': 'test-only-a', 'to': 'test-only-b', 'type': 'influences', 'sign': 'negative',
            'lag_days': 7, 'elasticity': {'min': .1, 'mode': .2, 'max': .3}, 'evidence_grade': 3},
        'confounders': [], 'alternatives': ['TEST_ONLY rival explanation'],
        'units': {'from': 'TEST_ONLY units', 'to': 'TEST_ONLY units', 'lag': 'days', 'elasticity_definition': 'TEST_ONLY ratio'}},
        'gameplay': {'opportunities': []}, 'ethics': {'admitted': False, 'ladder': {'stopped_at': 'purpose',
            'rungs': [{'rung': 'purpose', 'passed': False, 'justification': 'TEST_ONLY no purpose'}]}}}[task]
    raw = q.canonical({'schema': f'twin.{task}-response/v1', 'answer': answer, 'basis': basis})
    output = {'raw': base64.b64encode(raw).decode(), 'raw_available': True, 'answer': answer,
        'basis': basis, 'actor_digest': 'a' * 64, 'input_digest': 'c' * 64, 'failure': None}
    pins = [{'identity': 'TEST_ONLY original source', 'version': 'v1', 'sha256': 'd' * 64},
        {'identity': 'TEST_ONLY original policy', 'version': 'v2', 'sha256': 'e' * 64}]
    attempt = {'attempt_id': 'TEST_ONLY-attempt', 'subject': 'TEST_ONLY-subject', 'task': task,
        'metrics': list(contract.metrics), 'target': target, 'context': {'organisation': 'driftwood'},
        'status': 'accepted', 'receipt': 'TEST_ONLY-receipt', 'output': output,
        'assessment_outcomes': {metric: 'pass' for metric in contract.metrics}, 'source_pins': pins,
        'mandatory_gate': {'admitted': False, 'source_sha256': 'f' * 64, 'result_sha256': '1' * 64} if task == 'ethics' else None}
    job = {'task': task, 'task_contract_sha256': contract.digest, 'model_version': 'actor-' + 'a' * 64,
        'organisation': 'driftwood', 'subjects': ['TEST_ONLY-subject']}
    state = {'schema': 'twin.task-session-snapshot/v1', 'identity': 'TEST_ONLY-session',
        'inputs': [{'subject': 'TEST_ONLY-subject', 'input': {'TEST_ONLY': 'original input'},
                    'context': {'target': target}}], 'attempts': [attempt], 'declines': [],
        'pending_reviews': [], 'source_pins': pins}
    state['job'] = copy.deepcopy(job)
    output['input_digest'] = q.digest(state['inputs'][0]['input'])
    attempt.update({'input_sha256': output['input_digest'], 'target_sha256': q.digest(target),
        'actor_sha256': output['actor_digest'], 'capture_sha256': q.digest(output),
        'raw_available': True, 'disposition': 'accepted', 'reason': 'TEST_ONLY accepted mechanical snapshot'})
    return job, state


@pytest.mark.parametrize('task', ['causal', 'gameplay', 'ethics'])
def test_complete_proposal_is_lossless_and_conforms_to_the_accepted_schema(task):
    job, state = snapshot(task)
    document = parent.document_from_snapshot(job, state, role='model-steward', clock='local')
    validate('ProposalDocument', document)
    actual = state['attempts'][0]
    assert document['judgements'][0]['answer'] == actual['output']['answer']
    assert document['judgements'][0]['basis'] == actual['output']['basis']
    assert document['judgements'][0]['mandatory_gate'] == actual['mandatory_gate']
    assert document['source_pins'] == state['source_pins']
    assert document['judgements'][0]['actual_output_sha256'] == q.digest(actual['output'])
    assert document['run']['action_authority'] is False
    if task == 'gameplay': assert document['judgements'][0]['answer']['opportunities'] == []


def test_evolution_keeps_all_actual_source_pins_without_inventing_a_signal():
    job, state = snapshot('evolution')
    document = parent.document_from_snapshot(job, state, role='model-steward', clock='human')
    claim = document['claims'][0]
    assert claim['kind'] == 'position' and claim['evidence_grade'] == 5 and claim['price_eligible'] is False
    assert claim['source_pins'] == document['source_pins'] == state['source_pins']
    assert document['derived_from'] == [] and 'signal' not in claim
    assert claim['evidence'] == q.canonical(state['attempts'][0]['output']['basis']).decode()


@pytest.mark.parametrize('change', ['missing basis', 'partial answer', 'wrong target', 'one causal metric', 'missing receipt', 'extra answer'])
def test_serializer_cannot_fill_or_relabel_an_incomplete_protected_capture(change):
    job, state = snapshot('causal')
    actual = state['attempts'][0]
    if change == 'missing basis': actual['output']['basis'] = None
    elif change == 'partial answer': del actual['output']['answer']['edge']['elasticity']
    elif change == 'wrong target': actual['target'] = {'kind': 'map', 'organisation': 'driftwood'}
    elif change == 'one causal metric': actual['metrics'].pop()
    elif change == 'missing receipt': actual['receipt'] = None
    else: actual['output']['answer']['invented'] = 'TEST_ONLY repair'
    actual['capture_sha256'] = q.digest(actual['output'])
    actual['target_sha256'] = q.digest(actual['target'])
    with pytest.raises(ValueError): parent.document_from_snapshot(job, state, role='model-steward', clock='local')


def test_environment_derived_github_clock_overrides_local_document_declaration(monkeypatch):
    job, state = snapshot('gameplay')
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    document = parent.document_from_snapshot(job, state, role='model-steward', clock='local')
    assert document['run']['clock'] == 'github'


def test_snapshot_job_cannot_be_relabelled_by_the_document_caller():
    job, state = snapshot('evolution')
    job['organisation'] = 'tuppence'
    with pytest.raises(ValueError): parent.document_from_snapshot(job, state, role='model-steward', clock='human')
