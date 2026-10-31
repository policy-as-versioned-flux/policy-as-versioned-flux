"""TEST_ONLY policy identity and consumed-review permission-loss controls."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import pytest

from twin import qualification as q
from twin.basis_assessment import ReviewStore
from twin.task_inputs import TaskPolicy, resolve_task_input, support_sources
from test_task_inputs import protected_request, task_request
from test_task_sessions import genuine_task_material, task_review_store, TASK_CALLS


def test_changed_actual_metadata_policy_requires_new_actor_and_rejects_cross_policy_reuse(protected_request, tmp_path):
    first = genuine_task_material(protected_request, tmp_path / 'version-one', count=3)
    second = genuine_task_material(protected_request, tmp_path / 'version-two', count=3,
                                   metadata_policy_version='TEST_ONLY-policy-version-two')
    assert first['policy'].digest != second['policy'].digest
    assert json.loads(first['policy'].description)['contexts']['driftwood']['input_constructor_sha256'] != json.loads(second['policy'].description)['contexts']['driftwood']['input_constructor_sha256']
    for material in (first, second):
        material['selections'][0].verify()
    assert first['actor'].model_version != second['actor'].model_version
    assert json.loads(first['actor'].description)['config']['task_policy_digest'] == first['policy'].digest
    # Additional real source-packet rows do not change the per-adopter protected policy.
    args = task_request(protected_request)
    packet = json.loads(args['protected_job']['source_packet'])
    packet['subject'] = args['protected_job']['subject'] = 'TEST_ONLY-distinct-source-case'
    packet['as_of'] = args['protected_job']['as_of'] = '2026-10-29'
    args['protected_job']['source_packet'] = q.canonical(packet)
    args['protected_job']['source_pin'] = q.digest(packet)
    extra = resolve_task_input(**args)
    same_policy = TaskPolicy.freeze(first['policy'].contract, (*first['resolved'], extra))
    assert same_policy.digest == first['policy'].digest
    wrong_handle = replace(first['selections'][0], _task_policy=second['policy'])
    before = len(TASK_CALLS)
    with pytest.raises(ValueError, match='policy'):
        wrong_handle.verify()
    with pytest.raises(ValueError, match='policy'):
        wrong_handle.verify_input(first['resolved'][0].host_record)
    assert len(TASK_CALLS) == before
    # Even a protected catalogue pin cannot repair an actor frozen for another policy.
    selected = first['selections'][0]
    bundle = json.loads(selected.archive(first['captures']['evolution-judge'], first['assessments']['evolution-judge']))
    bundle['selection']['task_policy'] = json.loads(second['policy'].description)
    (tmp_path / 'cross-policy.json').write_bytes(q.canonical(bundle))
    catalogue = {'schema': 'twin.qualification-registry/v1', 'entries': [
        {'bundle': 'cross-policy.json', 'sha256': q.digest(bundle)}]}
    path = tmp_path / 'cross-policy-catalogue.json'; path.write_bytes(q.canonical(catalogue))
    with pytest.raises(ValueError, match='policy'):
        q.Resolver.from_catalogue(path, q.digest(catalogue), allow_test_only=True,
            task_policies={item.digest: item for item in (first['policy'], second['policy'])})
    assert len(TASK_CALLS) == before
    selected = second['selections'][0]
    with pytest.raises(ValueError, match='policy'):
        q.Selection.freeze(first['actor'], selected.population, selected.basis_checker, review=selected.review,
            assessment_policy=selected.assessment_policy, task_contract=second['policy'].contract, task_policy=second['policy'])
    config = json.loads(first['actor'].description)['config']
    for claimed in (None, '0' * 64):
        forged = dict(config)
        if claimed is None:
            forged.pop('task_policy_digest', None)
        else:
            forged['task_policy_digest'] = claimed
        actor = q.Actor.freeze(first['actor'].runner, first['actor'].parser, forged, support=support_sources())
        selected = first['selections'][0]
        with pytest.raises(ValueError, match='policy'):
            q.Selection.freeze(actor, selected.population, selected.basis_checker, review=selected.review,
                assessment_policy=selected.assessment_policy, task_contract=first['policy'].contract, task_policy=first['policy'])
    # Even a correct public digest cannot replace the independently supplied handle.
    with pytest.raises(ValueError, match='protected task'):
        q.Selection.freeze(first['actor'], selected.population, selected.basis_checker, review=selected.review,
            assessment_policy=selected.assessment_policy, task_contract=first['policy'].contract)


class WithdrawMetricAfterAcquiredReview(ReviewStore):
    """Real retained review acquisition, followed by TEST_ONLY host score withdrawal."""
    def withdraw_after_acquisition(self, scores, metric):
        self.scores, self.metric = scores, metric
        return self

    def assess(self, policy, request):
        assessment = super().assess(policy, request)
        retained = self.scores.read_bytes().splitlines(keepends=True)
        self.scores.write_bytes(b''.join(line for line in retained if json.loads(line)['skill'] != self.metric))
        return assessment


def withdrawing_store(path, policy, request, scores, metric):
    task_review_store(path, policy, request)
    raw = (path / 'store.json').read_bytes()
    return WithdrawMetricAfterAcquiredReview(path / 'store.json', q.hashlib.sha256(raw).hexdigest()).withdraw_after_acquisition(scores, metric)


def import_session(path, material, session):
    path.mkdir()
    if material['group']:
        bundle = material['group'].archive(material['core'], material['assessments'])
    else:
        selected = material['selections'][0]; metric = selected.population.metric
        bundle = selected.archive(material['captures'][metric], material['assessments'][metric])
    (path / 'group.json').write_bytes(bundle)
    archive = session.archive(); (path / 'session.json').write_bytes(archive)
    catalogue = {'schema': 'twin.qualification-registry/v1', 'entries': [{'bundle': 'group.json', 'sha256': q.hashlib.sha256(bundle).hexdigest()}],
                 'sessions': [{'bundle': 'session.json', 'sha256': q.hashlib.sha256(archive).hexdigest()}]}
    raw = q.canonical(catalogue); (path / 'catalogue.json').write_bytes(raw)
    resolver = q.Resolver.from_catalogue(path / 'catalogue.json', q.hashlib.sha256(raw).hexdigest(), material['scores'],
        allow_test_only=True, task_policies={item.digest: item for item in (material['policy'], material['host_policy'])})
    return resolver.task_session(session.identity)


def assert_terminal_tamper_refuses(material, archive, previous_refusal=None):
    original = json.loads(archive)
    attempt_id = original['task_attempts'][0]['attempt_id']
    def changed_reason(value):
        value['task_attempts'][0]['reason'] = 'TEST_ONLY claimed authority refusal'
        value['task_events'][-1]['reason'] = value['declines'][-1]['reason'] = value['task_attempts'][0]['reason']
    def changed_receipt(value):
        receipt = value['task_refusals'][attempt_id]
        receipt['record']['bindings']['output_sha256'] = '0' * 64
        receipt['digest'] = q.digest(receipt['record'])
    def changed_event(value):
        value['task_events'][0]['reason'] = value['declines'][0]['reason'] = 'TEST_ONLY rewritten original event'
    mutations = [lambda value: value.pop('task_refusals'), changed_reason, changed_receipt, changed_event,
                 lambda value: value['task_reviews'][attempt_id].pop(next(iter(value['task_reviews'][attempt_id])))]
    if previous_refusal is not None:
        mutations.append(lambda value: value['task_refusals'].update({attempt_id: previous_refusal}))
    for mutate in mutations:
        forged = copy.deepcopy(original); mutate(forged)
        with pytest.raises(ValueError):
            q.HostSession.restore(q.canonical(forged), material['resolver'], task_policy=material['host_policy'])
    # Erasing all task markers must not erase history already known privately.
    forged = {key: value for key, value in original.items() if not key.startswith('task_')}
    forged.update(records={}, pending_reviews={}, reviewed_outputs=[], declines=[], failed_outputs=[])
    with pytest.raises(ValueError, match='erase an original consumed refusal'):
        q.HostSession.restore(q.canonical(forged), material['resolver'], task_policy=material['host_policy'])


def public_acceptance_cannot_replace_known_consumed_refusal(material, archive):
    forged = json.loads(archive)
    attempt = forged['task_attempts'][0]; identity = attempt['attempt_id']
    reviews = forged['task_reviews'][identity]
    record = {**next(iter(reviews.values()))['record'],
              'assessments': {metric: value['assessment'] for metric, value in reviews.items()},
              'assessment_digests': {metric: value['digest'] for metric, value in reviews.items()}}
    token = 'TEST_ONLY-invented-accepted-receipt'
    forged.pop('task_refusals')
    attempt.update(disposition='accepted', status='accepted', receipt=token, reason='TEST_ONLY claimed later acceptance')
    forged['task_events'][-1].update(disposition='accepted', receipt=token, reason=attempt['reason'])
    forged['declines'].pop()
    forged['records'] = {token: record}
    with pytest.raises(ValueError):
        q.HostSession.restore(q.canonical(forged), material['resolver'], task_policy=material['host_policy'])


def import_in_fresh_process(path, material, model_root, identity):
    """Reconstruct private TEST_ONLY source handles; import only a protected pin."""
    config = {'catalogue': str(path / 'catalogue.json'), 'sha256': q.hashlib.sha256((path / 'catalogue.json').read_bytes()).hexdigest(),
        'scores': str(material['scores']), 'model_root': str(model_root), 'session': identity,
        'task': material['policy'].contract.task}
    script = r'''
from pathlib import Path
import json,sys,yaml
sys.path.insert(0,str(Path.cwd()/'tests'))
from twin import qualification as q
from twin.repo import ModelRepo
from twin.model import Overlay
from twin.task_inputs import TaskPolicy,resolve_task_input
from twin.task_contracts import TaskContract
from test_task_inputs import task_request
from test_task_sessions import TASK_CALLS
config=json.loads(sys.argv[1]);repo=ModelRepo.open(config['model_root'])
def protected_request(org):
    party=yaml.safe_dump({'id':org,'appetite':{'pricing_threshold':3}}).encode()
    overlay=Overlay.load(repo,org,pricing_threshold=3)
    return {'repo':repo,'party_bytes':party,'party_pin':q.hashlib.sha256(party).hexdigest(),
        'policy':{'issuer':'TEST_ONLY-protected-resolver','domain':'TEST_ONLY-source-task',
        'capability':'TEST_ONLY-primary-subject','frame':'TEST_ONLY-current-model-relevance','model_as_of':'2026-10-30',
        'model_pins':{'model_repo':repo.pin.as_dict(),'overlay':overlay.ref.as_dict(),'world':overlay.world.ref.as_dict()}}}
rows=tuple(resolve_task_input(**task_request(protected_request,config['task'],org)) for org in ('driftwood','tuppence','ludlow'))
contract=TaskContract.freeze(config['task']);full=TaskPolicy.freeze(contract,rows);host=TaskPolicy.freeze(contract,(rows[0],))
resolver=q.Resolver.from_catalogue(Path(config['catalogue']),config['sha256'],Path(config['scores']),allow_test_only=True,
    task_policies={policy.digest:policy for policy in (full,host)})
session=resolver.task_session(config['session'])
print(json.dumps({'raw_calls':len(TASK_CALLS),'pending':len(session.pending_reviews),
    'disposition':session.task_snapshot()['attempts'][0]['disposition'],'archive_sha256':q.hashlib.sha256(session.archive()).hexdigest()}))
'''
    result = subprocess.run([sys.executable, '-c', script, json.dumps(config)], cwd=Path(__file__).resolve().parents[1],
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_both_real_permission_loss_directions_after_consumed_review_are_terminal_and_durable(protected_request, tmp_path):
    material = genuine_task_material(protected_request, tmp_path / 'material', task='causal')
    actor = material['actor'].model_version
    original_scores = material['scores'].read_bytes()
    previous_refusal = None
    for blocked in ('causal-claims', 'causal-claims-grade-accuracy'):
        material['scores'].write_bytes(original_scores)
        assert all(material['resolver'].permission(metric, actor).granted for metric in ('causal-claims', 'causal-claims-grade-accuracy'))
        session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
        before = len(TASK_CALLS)
        assert session.judge_group(actor, material['job']['subjects'][0]).receipt is None
        assert len(TASK_CALLS) == before + 1
        first = session.pending_reviews[0]
        policy = next(item.assessment_policy for item in material['selections'] if item.assessment_policy.digest == first['request']['policy'])
        store = task_review_store(tmp_path / (blocked + '-first'), policy, q.canonical(first['request']))
        assert session.review_pending(first['request_digest'], store).receipt is None
        partial = q.HostSession.restore(session.archive(), material['resolver'], task_policy=material['host_policy'])
        assert partial.archive() == session.archive()
        last = partial.pending_reviews[0]
        policy = next(item.assessment_policy for item in material['selections'] if item.assessment_policy.digest == last['request']['policy'])
        store = withdrawing_store(tmp_path / (blocked + '-last'), policy, q.canonical(last['request']), material['scores'], blocked)
        result = partial.review_pending(last['request_digest'], store)
        assert result.receipt is None and 'human required' in result.reason
        assert not material['resolver'].permission(blocked, actor).granted
        other = 'causal-claims-grade-accuracy' if blocked == 'causal-claims' else 'causal-claims'
        assert material['resolver'].permission(other, actor).granted
        assert partial.pending_reviews == [] and len(TASK_CALLS) == before + 1
        attempt = partial.task_snapshot()['attempts'][0]
        assert set(attempt['assessment_outcomes'].values()) == {'pass'}
        assert attempt['disposition'] == 'failed-review' and attempt['receipt'] is None
        assert attempt['output']['raw_available'] is True
        archive = partial.archive()
        assert_terminal_tamper_refuses(material, archive, previous_refusal)
        previous_refusal = next(iter(json.loads(archive)['task_refusals'].values()))
        restored = q.HostSession.restore(archive, material['resolver'], task_policy=material['host_policy'])
        assert restored.archive() == archive and len(TASK_CALLS) == before + 1
        imported = import_session(tmp_path / (blocked + '-catalogue'), material, restored)
        assert imported.archive() == archive and len(TASK_CALLS) == before + 1
        child = import_in_fresh_process(tmp_path / (blocked + '-catalogue'), material,
                                        protected_request()['repo'].model_root, restored.identity)
        assert child == {'raw_calls': 0, 'pending': 0, 'disposition': 'failed-review',
                         'archive_sha256': q.hashlib.sha256(archive).hexdigest()}
        material['scores'].write_bytes(original_scores)
        assert material['resolver'].permission(blocked, actor).granted
        public_acceptance_cannot_replace_known_consumed_refusal(material, archive)
        assert restored.review_pending(last['request_digest'], store).receipt is None
        assert restored.archive() == archive and len(TASK_CALLS) == before + 1
        # Restoring current permission never converts a consumed failure into acceptance.
        imported_again = import_session(tmp_path / (blocked + '-current-again'), material, restored)
        assert imported_again.archive() == archive and imported_again.pending_reviews == []
    # Independent fresh operation still uses one invocation and accepts only after both reviews.
    fresh = material['resolver'].host_session(material['inputs']); fresh.bind_task_job(material['job'])
    before = len(TASK_CALLS)
    fresh.judge_group(actor, material['job']['subjects'][0])
    for ordinal, pending in enumerate(fresh.pending_reviews):
        policy = next(item.assessment_policy for item in material['selections'] if item.assessment_policy.digest == pending['request']['policy'])
        store = task_review_store(tmp_path / ('fresh-' + str(ordinal)), policy, q.canonical(pending['request']))
        result = fresh.review_pending(pending['request_digest'], store)
        assert (result.receipt is not None) is (ordinal == 1)
    assert len(TASK_CALLS) == before + 1
    restored = import_session(tmp_path / 'fresh-catalogue', material, fresh)
    assert restored.archive() == fresh.archive() and len(TASK_CALLS) == before + 1
