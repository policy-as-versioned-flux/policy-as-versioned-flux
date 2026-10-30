"""TEST_ONLY parent controls; no operational permission or actual model competence."""
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


def test_protected_caller_clock_and_role_are_not_chosen_by_the_document(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
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
    missing_review = json.loads(bundle)
    missing_review['review_store'] = {'path': 'missing-review.json', 'sha256': '0' * 64}
    missing_raw = q.canonical(missing_review)
    (tmp_path / 'job.json').write_bytes(missing_raw)
    missing_registry = json.loads(registry)
    missing_registry['task_jobs']['evolution']['driftwood']['sha256'] = hashlib.sha256(missing_raw).hexdigest()
    catalogue.write_bytes(q.canonical(missing_registry))
    unavailable = parent.run_registered('evolution', 'driftwood', tmp_path / 'unavailable-review', resolver=host)
    assert len(unavailable['attempts']) == len(unavailable['declined']) == 1
    assert unavailable['attempts'][0]['capture_sha256'] is None and unavailable['accepted'] is False
    assert (tmp_path / 'unavailable-review' / 'host-session.json').is_file()
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
@pytest.mark.parametrize(('requested_clock', 'github_actions', 'expected_clock'), [
    ('local', False, 'local'), ('human', False, 'human'), ('local', True, 'github'),
])
def test_public_validator_requires_the_actual_task_session_for_every_clock(
        task, monkeypatch, requested_clock, github_actions, expected_clock):
    if github_actions:
        monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    else:
        monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    from pathlib import Path
    from twin.qualified_signals import _validator
    validator = _validator()
    root = str(Path(q.__file__).resolve().parents[1])
    kinds, roles = validator.twin_facts(root)
    job, state = snapshot(task)
    document = parent.document_from_snapshot(job, state, role='model-steward', clock=requested_clock)
    calls = []
    def deny(doc, resolver, clock):
        calls.append((doc, resolver, clock))
        return ['TEST_ONLY protected session denial']
    monkeypatch.setattr(parent, 'validate_document', deny)
    host = q.Resolver()
    derive, check, lookup = validator.permission_rules(root, host)
    bad = validator.validate(document, kinds, roles, clock=derive(requested_clock)[0], permission=(check, lookup))
    assert calls == [(document, host, expected_clock)]
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


def restore_task_material(material, session, path):
    """Import independently pinned TEST_ONLY qualification and host archives through public APIs."""
    path.mkdir()
    if material['group']:
        bundle = material['group'].archive(material['core'], material['assessments'])
    else:
        selected = material['selections'][0]
        metric = selected.population.metric
        bundle = selected.archive(material['captures'][metric], material['assessments'][metric])
    raw = session.archive()
    (path / 'qualification.json').write_bytes(bundle)
    (path / 'session.json').write_bytes(raw)
    registry = q.canonical({'schema': 'twin.qualification-registry/v1',
        'entries': [{'bundle': 'qualification.json', 'sha256': hashlib.sha256(bundle).hexdigest()}],
        'sessions': [{'bundle': 'session.json', 'sha256': hashlib.sha256(raw).hexdigest()}]})
    catalogue = path / 'registry.json'; catalogue.write_bytes(registry)
    host = q.Resolver.from_catalogue(catalogue, hashlib.sha256(registry).hexdigest(), material['scores'],
        allow_test_only=True, task_policies={policy.digest: policy for policy in (material['policy'], material['host_policy'])})
    return host, host.task_session(session.task_snapshot()['identity'])


def test_actual_evolution_parent_reviews_restores_and_publicly_checks_complete_original_pins(protected_request, tmp_path, monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    from pathlib import Path
    from test_task_sessions import genuine_task_material, task_review_store, TASK_CALLS
    from twin.qualified_signals import _validator
    material = genuine_task_material(protected_request, tmp_path)
    selected = material['selections'][0]
    before = len(TASK_CALLS)
    run = parent.TaskParent(material['resolver'], clock='local').start(material['job'], material['inputs'])
    pending_state = run.session.task_snapshot()
    assert len(TASK_CALLS) == before + 1 and len(pending_state['pending_reviews']) == 1
    pending_summary = run.save(tmp_path / 'pending-parent')
    assert pending_summary['accepted'] is False and len(pending_summary['declined']) == 1
    assert pending_summary['attempts'][0]['raw_available'] is True
    host, restored = restore_task_material(material, run.session, tmp_path / 'pending-import')
    resumed = parent.TaskParent(host, clock='local').resume(material['job'], restored)
    pending = restored.task_snapshot()['pending_reviews'][0]
    store = task_review_store(tmp_path / 'accepted-review', selected.assessment_policy, q.canonical(pending['request']))
    assert len(resumed.review_pending(store)) == 1
    assert len(TASK_CALLS) == before + 1 and resumed.validate() == []
    document = resumed.document()
    state = restored.task_snapshot()
    assert document['derived_from'] == [] and document['source_pins'] == state['source_pins']
    assert document['claims'][0]['source_pins'] == state['attempts'][0]['source_pins']
    assert len(document['source_pins']) > 2 and 'signal' not in document['claims'][0]
    validator = _validator()
    root = str(Path(q.__file__).resolve().parents[1])
    kinds, roles = validator.twin_facts(root)
    _, check, lookup = validator.permission_rules(root, host)
    assert validator.validate(document, kinds, roles, clock='local', permission=(check, lookup)) == []
    for forgery in ('top pin', 'claim pin', 'basis', 'receipt', 'attempt', 'clock'):
        changed = copy.deepcopy(document)
        if forgery == 'top pin': changed['source_pins'].pop()
        elif forgery == 'claim pin': changed['claims'][0]['source_pins'].pop()
        elif forgery == 'basis': changed['claims'][0]['evidence'] = 'TEST_ONLY fabricated reasoning'
        elif forgery == 'receipt': changed['claims'][0]['host_receipt'] = 'TEST_ONLY-forged'
        elif forgery == 'attempt': changed['run']['attempts'].clear()
        else: changed['run']['clock'] = 'github'
        assert validator.validate(changed, kinds, roles, clock='local', permission=(check, lookup)), forgery
    accepted = resumed.save(tmp_path / 'accepted-parent')
    assert accepted['accepted'] is True and len(accepted['declined']) == 1
    assert json.loads((tmp_path / 'accepted-parent' / 'claim.json').read_bytes()) == document
    final_host, final_session = restore_task_material(material, restored, tmp_path / 'accepted-import')
    assert parent.TaskParent(final_host, clock='local').resume(material['job'], final_session).validate() == []
    assert len(TASK_CALLS) == before + 1
    registered = tmp_path / 'registered-resume'; registered.mkdir()
    (registered / 'inputs.json').write_bytes(material['inputs'].description)
    bundle = {'schema': 'twin.protected-task-job/v1', 'execution': material['job'],
        'task_policy_sha256': material['host_policy'].digest, 'resume_session': final_session.identity,
        'inputs': {'path': 'inputs.json', 'sha256': hashlib.sha256(material['inputs'].description).hexdigest()},
        'review_store': {'path': 'missing-review.json', 'sha256': '0' * 64}}
    def install_bundle():
        raw = q.canonical(bundle); (registered / 'job.json').write_bytes(raw)
        catalogue = registered / 'registry.json'
        catalogue.write_bytes(q.canonical({'schema': 'twin.qualification-registry/v1', 'entries': [],
            'task_jobs': {'evolution': {'driftwood': {'path': 'job.json', 'sha256': hashlib.sha256(raw).hexdigest()}}}}))
        monkeypatch.setattr(parent, 'CATALOGUE', catalogue)
    install_bundle()
    missing = parent.run_registered('evolution', 'driftwood', tmp_path / 'resume-missing-review', 'local', resolver=final_host)
    assert missing['accepted'] is False and missing['attempts'] == final_session.task_snapshot()['attempts']
    assert (tmp_path / 'resume-missing-review' / 'host-session.json').read_bytes() == final_session.archive()
    other = material['resolved'][3].host_record
    other_inputs = q.HostInputs.freeze((other,), (other['issuer'],), task_policy=material['policy'])
    (registered / 'inputs.json').write_bytes(other_inputs.description)
    del bundle['review_store']
    bundle['task_policy_sha256'] = material['policy'].digest
    bundle['inputs']['sha256'] = hashlib.sha256(other_inputs.description).hexdigest()
    install_bundle()
    mismatched = parent.run_registered('evolution', 'driftwood', tmp_path / 'resume-different-inputs', 'local', resolver=final_host)
    assert mismatched['accepted'] is False and any('original inputs' in reason for reason in mismatched['reasons'])
    assert mismatched['attempts'] == final_session.task_snapshot()['attempts']
    assert len(TASK_CALLS) == before + 1
    for decision in ('fail', 'held'):
        refused = parent.TaskParent(material['resolver'], clock='local').start(material['job'], material['inputs'])
        request = refused.session.task_snapshot()['pending_reviews'][0]
        store = task_review_store(tmp_path / ('review-' + decision), selected.assessment_policy,
            q.canonical(request['request']), decision=decision)
        refused.review_pending(store)
        state = refused.session.task_snapshot()
        assert state['pending_reviews'] == []
        assert state['attempts'][0]['disposition'] == ('held-review' if decision == 'held' else 'failed-review')
        calls = len(TASK_CALLS)
        assert refused.review_pending(store) == [] and len(TASK_CALLS) == calls
        summary = refused.save(tmp_path / (decision + '-parent'))
        assert summary['accepted'] is False and summary['attempts'][0]['raw_available'] is True
        reloaded = q.HostSession.restore(refused.session.archive(), material['resolver'], task_policy=material['host_policy'])
        assert reloaded.archive() == refused.session.archive() and len(TASK_CALLS) == calls


def task_group_review_store(material, requests, path, *, first_decision='pass'):
    """Combine independently retained TEST_ONLY assessments into one protected acquisition store."""
    from test_task_sessions import task_review_store
    from twin.basis_assessment import ReviewStore
    path.mkdir()
    entries = []
    for index, pending in enumerate(requests):
        selected = next(item for item in material['selections'] if item.assessment_policy.digest == pending['request']['policy'])
        name = selected.population.metric
        task_review_store(path / name, selected.assessment_policy, q.canonical(pending['request']),
                          decision=first_decision if index == 0 else 'pass')
        entry = json.loads((path / name / 'store.json').read_bytes())['entries'][0]
        entries.append({**entry, 'record': name + '/' + entry['record']})
    raw = q.canonical({'schema': 'twin.semantic-review-store/v1', 'entries': entries})
    target = path / 'store.json'; target.write_bytes(raw)
    return ReviewStore(target, hashlib.sha256(raw).hexdigest())


def test_actual_causal_parent_uses_one_capture_both_permissions_and_complete_proposal(protected_request, tmp_path):
    from pathlib import Path
    from test_task_sessions import genuine_task_material, TASK_CALLS
    from twin.qualified_signals import _validator
    material = genuine_task_material(protected_request, tmp_path, task='causal')
    assert all(material['resolver'].permission(metric, material['actor'].model_version).granted
               for metric in TaskContract.freeze('causal').metrics)
    before = len(TASK_CALLS)
    run = parent.TaskParent(material['resolver'], clock='local').start(material['job'], material['inputs'])
    state = run.session.task_snapshot()
    assert len(TASK_CALLS) == before + 1 and len(state['attempts']) == 1 and len(state['pending_reviews']) == 2
    assert len({q.digest(item['request']['rows'][0]['output']) for item in state['pending_reviews']}) == 1
    pending_summary = run.save(tmp_path / 'causal-pending')
    assert pending_summary['accepted'] is False and len(pending_summary['declined']) == 1
    host, session = restore_task_material(material, run.session, tmp_path / 'causal-pending-import')
    resumed = parent.TaskParent(host, clock='local').resume(material['job'], session)
    store = task_group_review_store(material, session.task_snapshot()['pending_reviews'], tmp_path / 'causal-reviews')
    results = resumed.review_pending(store)
    assert len(results) == 2 and results[0].receipt is None and results[1].receipt
    assert len(TASK_CALLS) == before + 1 and resumed.validate() == []
    document = resumed.document()
    validate('ProposalDocument', document)
    attempt = session.task_snapshot()['attempts'][0]
    assert document['judgements'][0]['answer'] == attempt['output']['answer']
    assert document['judgements'][0]['basis'] == attempt['output']['basis']
    assert document['judgements'][0]['actual_output_sha256'] == attempt['capture_sha256']
    assert set(attempt['assessment_outcomes'].values()) == {'pass'}
    validator = _validator(); root = str(Path(q.__file__).resolve().parents[1])
    kinds, roles = validator.twin_facts(root)
    _, check, lookup = validator.permission_rules(root, host)
    assert validator.validate(document, kinds, roles, clock='local', permission=(check, lookup)) == []
    changed = copy.deepcopy(document)
    changed['judgements'][0]['answer']['edge']['lag_days'] += 1
    assert validator.validate(changed, kinds, roles, clock='local', permission=(check, lookup))
    accepted = resumed.save(tmp_path / 'causal-accepted')
    assert accepted['accepted'] is True and accepted['sensor_activation'] is False
    assert json.loads((tmp_path / 'causal-accepted' / 'proposal.json').read_bytes()) == document
    final_host, final_session = restore_task_material(material, session, tmp_path / 'causal-accepted-import')
    assert parent.TaskParent(final_host, clock='local').resume(material['job'], final_session).validate() == []
    assert len(TASK_CALLS) == before + 1
    for decision in ('fail', 'held'):
        refused = parent.TaskParent(material['resolver'], clock='local').start(material['job'], material['inputs'])
        store = task_group_review_store(material, refused.session.task_snapshot()['pending_reviews'],
            tmp_path / ('causal-' + decision), first_decision=decision)
        results = refused.review_pending(store)
        assert len(results) == 1 and results[0].receipt is None
        state = refused.session.task_snapshot()
        assert state['pending_reviews'] == [] and state['attempts'][0]['receipt'] is None
        assert state['attempts'][0]['raw_available'] is True
        calls = len(TASK_CALLS)
        assert refused.review_pending(store) == [] and len(TASK_CALLS) == calls
        assert refused.save(tmp_path / ('causal-' + decision + '-saved'))['accepted'] is False


def test_unreadable_protected_inputs_are_counted_before_any_actor(tmp_path):
    job, state = snapshot('evolution')
    resolver = RefusalResolver(state['inputs'])
    class Inputs:
        @property
        def records(self):
            raise OSError('TEST_ONLY protected source unavailable')
    run = parent.TaskParent(resolver).start(job, Inputs())
    summary = run.save(tmp_path / 'unreadable')
    assert len(summary['declined']) == len(summary['attempts']) == 1
    assert summary['attempts'][0]['capture_sha256'] is None
    assert 'protected source unavailable' in summary['declined'][0]['reason']


@pytest.mark.parametrize('task', ['gameplay', 'ethics'])
def test_actual_remaining_parent_preserves_empty_gameplay_and_independent_denied_gate(task, protected_request, tmp_path):
    from pathlib import Path
    from test_task_sessions import genuine_task_material, task_review_store, TASK_CALLS
    from twin.qualified_signals import _validator
    material = genuine_task_material(protected_request, tmp_path, task=task)
    selected = material['selections'][0]
    assert material['resolver'].permission(selected.population.metric, material['actor'].model_version).granted
    before = len(TASK_CALLS)
    run = parent.TaskParent(material['resolver'], clock='local').start(material['job'], material['inputs'])
    state = run.session.task_snapshot()
    assert len(TASK_CALLS) == before + 1 and len(state['pending_reviews']) == 1
    attempt = state['attempts'][0]
    if task == 'gameplay':
        assert attempt['output']['answer']['opportunities'] == []
        assert attempt['mandatory_gate'] is None
    else:
        assert attempt['output']['answer']['admitted'] is True
        assert attempt['mandatory_gate']['admitted'] is False
    pending = run.save(tmp_path / (task + '-pending'))
    assert pending['accepted'] is False and pending['sensor_activation'] is False
    request = state['pending_reviews'][0]
    store = task_review_store(tmp_path / (task + '-review'), selected.assessment_policy, q.canonical(request['request']))
    assert run.review_pending(store)[0].receipt
    document = run.document()
    validate('ProposalDocument', document)
    assert run.validate() == [] and len(TASK_CALLS) == before + 1
    judgement = document['judgements'][0]
    assert judgement['answer'] == attempt['output']['answer'] and judgement['basis'] == attempt['output']['basis']
    assert judgement['actual_output_sha256'] == attempt['capture_sha256']
    validator = _validator(); root = str(Path(q.__file__).resolve().parents[1])
    kinds, roles = validator.twin_facts(root)
    _, check, lookup = validator.permission_rules(root, material['resolver'])
    assert validator.validate(document, kinds, roles, clock='local', permission=(check, lookup)) == []
    changed = copy.deepcopy(document)
    if task == 'ethics': changed['judgements'][0]['mandatory_gate']['admitted'] = True
    else: changed['judgements'][0]['basis']['checks'][0]['present'] = not changed['judgements'][0]['basis']['checks'][0]['present']
    assert validator.validate(changed, kinds, roles, clock='local', permission=(check, lookup))
    summary = run.save(tmp_path / (task + '-accepted'))
    assert summary['accepted'] is True and summary['sensor_activation'] is False
    assert summary['action_authority'] is False and summary['merge_authority'] is False
    assert summary['mandatory_gate_blocked'] == (material['job']['subjects'] if task == 'ethics' else [])
    assert json.loads((tmp_path / (task + '-accepted') / 'proposal.json').read_bytes()) == document
    host, session = restore_task_material(material, run.session, tmp_path / (task + '-import'))
    assert parent.TaskParent(host, clock='local').resume(material['job'], session).validate() == []
    assert len(TASK_CALLS) == before + 1
