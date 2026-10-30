"""TEST_ONLY task history/import/dispatch controls through public interfaces."""
import copy

import pytest

from twin import qualification as q
from twin.task_contracts import TaskContract
from twin.task_sessions import ATTEMPT_FIELDS
from test_task_sessions import genuine_task_material, TASK_CALLS
from test_task_inputs import protected_request


def test_task_document_dispatch_cannot_drop_counted_refusals_on_local_clock(monkeypatch):
    for marker in ('GITHUB_ACTIONS', 'GITHUB_RUN_ID', 'GITHUB_WORKFLOW'):
        monkeypatch.delenv(marker, raising=False)
    inputs = q.HostInputs.freeze(({'subject': 'TEST_ONLY-unresolved', 'issuer': 'TEST_ONLY',
        'input': {}, 'context': {}, 'source': {}},), ('TEST_ONLY',))
    resolver = q.Resolver(); session = resolver.host_session(inputs)
    job = {'task': 'evolution', 'task_contract_sha256': TaskContract.freeze('evolution').digest,
        'model_version': 'actor-' + '1' * 64, 'organisation': 'driftwood', 'subjects': ['TEST_ONLY-unresolved']}
    session.bind_task_job(job); session.decline_task_run(tuple(job['subjects']), 'TEST_ONLY preflight refusal; human required')
    state = session.task_snapshot()
    document = {'schema': 'twin.headline-claim/v1', 'org': 'driftwood', 'source_pins': [], 'derived_from': [], 'claims': [],
        'run': {'host_session': session.identity, 'task_contract_sha256': job['task_contract_sha256'],
            'model_version': job['model_version'], 'clock': 'local', 'operator_role': 'TEST_ONLY', 'headless': False,
            'declined': state['declines'], 'attempts': [{key: row[key] for key in ATTEMPT_FIELDS} for row in state['attempts']],
            'action_authority': False, 'merge_authority': False, 'override_authority': False, 'price_eligible': False}}
    assert session.check_task_document(document) == []
    assert resolver.check_claim_document(document, 'local') == []
    forged = copy.deepcopy(document); forged['run']['declined'] = []; forged['run']['attempts'] = []
    assert session.check_task_document(forged)
    assert resolver.check_claim_document(forged, 'local')
    assert session.check_document(forged)


def test_pending_task_archive_rejects_rewritten_attempts_events_and_counts(protected_request, tmp_path):
    import json
    material = genuine_task_material(protected_request, tmp_path)
    session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
    before = len(TASK_CALLS)
    result = session.judge('evolution-judge', material['actor'].model_version, material['job']['subjects'][0])
    assert result.receipt is None and len(session.pending_reviews) == 1 and len(TASK_CALLS) == before + 1
    original = json.loads(session.archive())
    restored = q.HostSession.restore(q.canonical(original), material['resolver'], task_policy=material['host_policy'])
    assert restored.archive() == session.archive()
    mutations = [
        lambda doc: doc['task_job'].update(organisation='TEST_ONLY-foreign-adopter'),
        lambda doc: doc['task_attempts'][0].update(input_sha256='0' * 64),
        lambda doc: doc['task_attempts'][0].update(target_sha256='0' * 64),
        lambda doc: doc['task_attempts'][0].update(capture_sha256='0' * 64),
        lambda doc: doc['task_attempts'][0].update(metrics=[]),
        lambda doc: doc['task_attempts'][0].update(assessment_outcomes={'evolution-judge': 'pass'}),
        lambda doc: doc['task_attempts'].clear(),
        lambda doc: doc['task_events'].clear(),
        lambda doc: doc['task_events'][0].update(reason='TEST_ONLY rewritten event'),
        lambda doc: doc['declines'].clear(),
        lambda doc: doc['pending_reviews'].clear(),
    ]
    for mutate in mutations:
        forged = copy.deepcopy(original); mutate(forged)
        with pytest.raises(ValueError):
            q.HostSession.restore(q.canonical(forged), material['resolver'], task_policy=material['host_policy'])
    # A registered metric still owns the task boundary after every optional
    # public task marker is erased and a generic request checksum is recomputed.
    forged = copy.deepcopy(original)
    for name in ('task_job', 'task_attempts', 'task_events', 'task_reviews'):
        forged.pop(name)
    saved = next(iter(forged['pending_reviews'].values()))
    generic = {key: saved[key] for key in ('subject', 'metric', 'model_version', 'selection', 'context', 'output', 'attempt')}
    selected = material['selections'][0]
    row = material['inputs'].resolve(generic['subject'])
    request = {'schema': 'twin.basis-request/v1', 'policy': selected.assessment_policy.digest,
        'actor_digest': selected.actor.digest, 'population_digest': selected.population.digest,
        'selection_digest': selected.digest, 'capture_digest': q.digest(generic),
        'rows': [{'id': generic['subject'], 'input': row['input'], 'context': row['context'],
                  'sources': {'input': row['source']}, 'output': generic['output']}]}
    forged['pending_reviews'] = {q.digest(request): generic}
    with pytest.raises(ValueError):
        q.HostSession.restore(q.canonical(forged), material['resolver'], task_policy=material['host_policy'])
    assert len(TASK_CALLS) == before + 1
