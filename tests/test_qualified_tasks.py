"""TEST_ONLY parent serialization controls, never earned task permissions."""
import base64
import copy
import hashlib
import json

import pytest

from twin import qualification as q, qualified_tasks as parent
from twin.task_contracts import TaskContract, validate
from test_signal_inputs import protected_request


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


def test_a_well_shaped_serialized_snapshot_cannot_create_a_protected_receipt():
    job, state = snapshot('causal')
    document = parent.document_from_snapshot(job, state, role='model-steward', clock='local')
    reasons = parent.validate_document(document, q.Resolver(), clock='local')
    assert reasons and any('session' in reason for reason in reasons)


def test_protected_caller_clock_and_role_are_not_chosen_by_the_document():
    job, state = snapshot('gameplay')
    document = parent.document_from_snapshot(job, state, role='TEST_ONLY-nonrole', clock='local')
    reasons = parent.validate_document(document, q.Resolver(), clock='github')
    assert any('clock' in reason for reason in reasons)
    assert any('role' in reason for reason in reasons)


def test_fixed_default_registered_route_has_no_job_or_permission(tmp_path):
    result = parent.run_registered('causal', 'driftwood', tmp_path / 'unregistered')
    assert result['accepted'] is False and result['human_required'] is True
    assert 'no registered task job' in result['reasons'][0]
    assert (tmp_path / 'unregistered' / 'summary.json').is_file()


class RefusalSession:
    """TEST_ONLY preflight adapter: it has no permission or inference implementation."""
    identity = 'TEST_ONLY-refused-session'

    def __init__(self, rows):
        self.rows, self.job, self.declines = rows, None, []

    def bind_task_job(self, job):
        self.job = copy.deepcopy(job)

    def decline_task_run(self, subjects, reason):
        self.declines.extend({'subject': subject, 'reason': reason} for subject in subjects)

    def judge(self, *args):
        raise AssertionError('unsupported run must never reach judge')

    def judge_group(self, *args):
        raise AssertionError('unsupported run must never reach paired judge')

    def task_snapshot(self):
        attempts = []
        by_subject = {row['subject']: row for row in self.rows}
        for index, declined in enumerate(self.declines):
            row = by_subject[declined['subject']]
            attempts.append({'attempt_id': f'TEST_ONLY-refused-{index}', 'subject': declined['subject'],
                'task': self.job['task'], 'metrics': list(TaskContract.freeze(self.job['task']).metrics),
                'input_sha256': q.digest(row['input']), 'target_sha256': q.digest(None),
                'actor_sha256': self.job['model_version'][6:], 'capture_sha256': None,
                'raw_available': False, 'disposition': 'refused-before-invocation', 'reason': declined['reason'],
                'status': 'declined', 'receipt': None, 'output': None, 'mandatory_gate': None, 'source_pins': []})
        return {'schema': 'twin.task-session-snapshot/v1', 'identity': self.identity, 'job': self.job,
            'inputs': self.rows, 'attempts': attempts,
            'declines': self.declines, 'pending_reviews': [], 'events': [], 'source_pins': []}

    def archive(self):
        return q.canonical(self.task_snapshot())


class RefusalResolver:
    def __init__(self, rows):
        self.session = RefusalSession(rows)

    def host_session(self, inputs):
        return self.session


def test_mixed_scope_is_counted_before_any_judge_even_without_a_granted_adapter(tmp_path):
    job, _ = snapshot('causal')
    job['subjects'] = ['TEST_ONLY-a', 'TEST_ONLY-b']
    rows = [{'subject': subject, 'input': {}, 'context': {'organisation': org}}
        for subject, org in zip(job['subjects'], ('driftwood', 'tuppence'))]
    resolver = RefusalResolver(rows)
    class Inputs:
        records = tuple(rows)
    run = parent.TaskParent(resolver).start(job, Inputs())
    assert [item['subject'] for item in resolver.session.declines] == job['subjects']
    summary = run.save(tmp_path / 'mixed-refusal')
    assert summary['accepted'] is False and summary['human_required'] is True
    assert len(summary['declined']) == 2
    assert summary['reasons'] == ['no accepted task judgement; human-required fallback remains']
    assert (tmp_path / 'mixed-refusal' / 'host-session.json').is_file()


def test_actual_foundation_missing_selection_keeps_counted_raw_free_fallback(protected_request, tmp_path, monkeypatch):
    from test_task_inputs import task_request
    from twin.task_inputs import resolve_task_input, TaskPolicy
    args = task_request(protected_request)
    resolved = resolve_task_input(**args)
    policy = TaskPolicy.freeze(args['contract'], (resolved,))
    job = {'task': 'evolution', 'task_contract_sha256': args['contract'].digest,
        'model_version': 'actor-' + '1' * 64, 'organisation': 'driftwood', 'subjects': ['TEST_ONLY-task-subject']}
    calls = []
    def forbidden(*values):
        calls.append(values)
        raise AssertionError('no unregistered task inference')
    monkeypatch.setattr(q.Actor, 'invoke', forbidden)
    resolver = q.Resolver()
    run = parent.TaskParent(resolver).start(job, resolved.host_inputs())
    state = run.session.task_snapshot()
    assert calls == [] and len(state['attempts']) == len(state['declines']) == 1
    assert state['attempts'][0]['raw_available'] is False and state['attempts'][0]['capture_sha256'] is None
    assert 'no protected registered task selection' in state['declines'][0]['reason']
    result = run.save(tmp_path / 'real-foundation-refusal')
    assert result['accepted'] is False and result['human_required'] is True
    restored = q.HostSession.restore(run.session.archive(), resolver, task_policy=policy)
    resumed = parent.TaskParent(resolver).resume(job, restored)
    assert resumed.session.task_snapshot() == state
    assert resumed.save(tmp_path / 'restored-refusal')['declined'] == state['declines']
    assert calls == []


def test_actual_foundation_mixed_adopter_preflight_counts_all_original_requests(protected_request, tmp_path, monkeypatch):
    from test_task_inputs import task_request
    from twin.task_inputs import resolve_task_input, TaskPolicy
    contract = TaskContract.freeze('evolution')
    resolved = []
    for index, org in enumerate(('driftwood', 'tuppence')):
        args = task_request(protected_request, org=org)
        packet = json.loads(args['protected_job']['source_packet'])
        packet['subject'] += str(index)
        args['protected_job']['subject'] = packet['subject']
        args['protected_job']['source_packet'] = q.canonical(packet)
        args['protected_job']['source_pin'] = hashlib.sha256(q.canonical(packet)).hexdigest()
        resolved.append(resolve_task_input(**args))
    policy = TaskPolicy.freeze(contract, tuple(resolved))
    rows = tuple(item.host_record for item in resolved)
    inputs = q.HostInputs.freeze(rows, tuple({row['issuer'] for row in rows}), task_policy=policy)
    job = {'task': 'evolution', 'task_contract_sha256': contract.digest,
        'model_version': 'actor-' + '1' * 64, 'organisation': 'driftwood', 'subjects': [row['subject'] for row in rows]}
    def forbidden(*values):
        raise AssertionError('mixed task run must never reach judge')
    monkeypatch.setattr(q.HostSession, 'judge', forbidden)
    run = parent.TaskParent(q.Resolver()).start(job, inputs)
    state = run.session.task_snapshot()
    assert [item['subject'] for item in state['attempts']] == job['subjects']
    assert len(state['declines']) == 2 and all(item['capture_sha256'] is None for item in state['attempts'])
    assert run.save(tmp_path / 'actual-mixed')['accepted'] is False


def test_registered_job_restores_only_with_actual_original_private_policy(protected_request, tmp_path, monkeypatch):
    from test_task_inputs import task_request
    from twin.task_inputs import resolve_task_input, TaskPolicy
    args = task_request(protected_request)
    resolved = resolve_task_input(**args)
    policy = TaskPolicy.freeze(args['contract'], (resolved,))
    inputs_raw = resolved.host_inputs().description
    (tmp_path / 'inputs.json').write_bytes(inputs_raw)
    job = {'task': 'evolution', 'task_contract_sha256': args['contract'].digest,
        'model_version': 'actor-' + '1' * 64, 'organisation': 'driftwood', 'subjects': ['TEST_ONLY-task-subject']}
    bundle = q.canonical({'schema': 'twin.protected-task-job/v1', 'execution': job,
        'task_policy_sha256': policy.digest,
        'inputs': {'path': 'inputs.json', 'sha256': hashlib.sha256(inputs_raw).hexdigest()}})
    (tmp_path / 'job.json').write_bytes(bundle)
    registry = q.canonical({'schema': 'twin.qualification-registry/v1', 'entries': [],
        'task_jobs': {'evolution': {'driftwood': {'path': 'job.json', 'sha256': hashlib.sha256(bundle).hexdigest()}}}})
    catalogue = tmp_path / 'registry.json'
    catalogue.write_bytes(registry)
    host = q.Resolver.from_catalogue(catalogue, hashlib.sha256(registry).hexdigest(),
        task_policies={policy.digest: policy})
    monkeypatch.setattr(parent, 'CATALOGUE', catalogue)
    outcome = parent.run_registered('evolution', 'driftwood', tmp_path / 'with-handles', resolver=host)
    assert outcome['accepted'] is False and outcome['human_required'] is True
    assert len(outcome['attempts']) == 1 and len(outcome['declined']) == 1
    assert (tmp_path / 'with-handles' / 'host-session.json').is_file()
    stale_bundle = json.loads(bundle)
    stale_bundle['execution']['task_contract_sha256'] = '0' * 64
    stale_raw = q.canonical(stale_bundle)
    (tmp_path / 'job.json').write_bytes(stale_raw)
    stale_registry = json.loads(registry)
    stale_registry['task_jobs']['evolution']['driftwood']['sha256'] = hashlib.sha256(stale_raw).hexdigest()
    catalogue.write_bytes(q.canonical(stale_registry))
    stale = parent.run_registered('evolution', 'driftwood', tmp_path / 'stale-contract', resolver=host)
    assert len(stale['attempts']) == len(stale['declined']) == 1
    assert stale['attempts'][0]['capture_sha256'] is None and stale['accepted'] is False
    assert (tmp_path / 'stale-contract' / 'host-session.json').is_file()
    (tmp_path / 'job.json').write_bytes(bundle)
    catalogue.write_bytes(registry)
    without = parent.run_registered('evolution', 'driftwood', tmp_path / 'without-handles', resolver=q.Resolver())
    assert without['accepted'] is False and without['attempts'] == []
    assert 'policy' in without['reasons'][0]
    alias = tmp_path / 'symlink-registry.json'
    alias.symlink_to(catalogue)
    monkeypatch.setattr(parent, 'CATALOGUE', alias)
    linked = parent.run_registered('evolution', 'driftwood', tmp_path / 'symlink-catalogue', resolver=host)
    assert linked['accepted'] is False and linked['attempts'] == []
    assert 'symlink' in linked['reasons'][0]


@pytest.mark.parametrize('task', ['evolution', 'causal', 'gameplay', 'ethics'])
def test_public_validator_requires_the_actual_task_session_for_every_clock(task, monkeypatch):
    from pathlib import Path
    from twin.qualified_signals import _validator
    validator = _validator()
    root = str(Path(q.__file__).resolve().parents[1])
    kinds, roles = validator.twin_facts(root)
    job, state = snapshot(task)
    document = parent.document_from_snapshot(job, state, role='model-steward', clock='local')
    calls = []
    def deny(doc, resolver, clock):
        calls.append((doc, resolver, clock))
        return ['TEST_ONLY protected session denial']
    monkeypatch.setattr(parent, 'validate_document', deny)
    host = q.Resolver()
    derive, check, lookup = validator.permission_rules(root, host)
    bad = validator.validate(document, kinds, roles, clock=derive('local')[0], permission=(check, lookup))
    assert calls == [(document, host, 'local')]
    assert bad == ['TEST_ONLY protected session denial']
    assert validator.validate(document, kinds, roles)


def test_public_task_route_cannot_mint_a_receipt_from_a_well_shaped_snapshot():
    from pathlib import Path
    from twin.qualified_signals import _validator
    validator = _validator()
    root = str(Path(q.__file__).resolve().parents[1])
    kinds, roles = validator.twin_facts(root)
    job, state = snapshot('evolution')
    document = parent.document_from_snapshot(job, state, role='model-steward', clock='local')
    derive, check, lookup = validator.permission_rules(root, q.Resolver())
    bad = validator.validate(document, kinds, roles, clock=derive('local')[0], permission=(check, lookup))
    assert any('protected' in reason and 'session' in reason for reason in bad)
    assert not any('derived_from is empty' in reason for reason in bad)


def test_public_registered_task_command_has_no_default_job_or_permission(tmp_path):
    from twin.qualified_signals import _validator
    output = tmp_path / 'public-default'
    assert _validator().main(['--run-registered-task', 'evolution', 'driftwood', '--output', str(output)]) == 2
    summary = json.loads((output / 'summary.json').read_bytes())
    assert summary['accepted'] is False and summary['human_required'] is True
    assert summary['attempts'] == [] and summary['actual_permission_grant'] is False
