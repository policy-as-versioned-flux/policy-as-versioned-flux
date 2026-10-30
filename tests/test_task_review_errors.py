"""TEST_ONLY actual permission-reader failure after acquired review consumption."""
import copy
import json

import pytest

from twin import qualification as q
from twin.basis_assessment import ReviewStore
from test_task_inputs import protected_request
from test_task_sessions import genuine_task_material, task_review_store, TASK_CALLS
from test_task_policy_transactions import (import_session, import_in_fresh_process,
    assert_terminal_tamper_refuses, public_acceptance_cannot_replace_known_consumed_refusal)


class CorruptScoresAfterAcquiredReview(ReviewStore):
    def corrupt_after_acquisition(self, scores):
        self.scores = scores
        return self

    def assess(self, policy, request):
        acquired = super().assess(policy, request)
        self.scores.write_bytes(b'TEST_ONLY malformed local score row\n')
        return acquired


def test_consumed_review_reader_error_is_authenticated_terminal_and_durable(protected_request, tmp_path):
    material = genuine_task_material(protected_request, tmp_path / 'material')
    actor = material['actor'].model_version
    assert material['resolver'].permission('evolution-judge', actor).granted
    scores = material['scores'].read_bytes()
    session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
    before = len(TASK_CALLS)
    session.judge('evolution-judge', actor, material['job']['subjects'][0])
    assert len(TASK_CALLS) == before + 1
    pending = session.pending_reviews[0]
    policy = material['selections'][0].assessment_policy
    path = tmp_path / 'actual-acquired-review'
    task_review_store(path, policy, q.canonical(pending['request']))
    store = CorruptScoresAfterAcquiredReview(path / 'store.json', q.hashlib.sha256((path / 'store.json').read_bytes()).hexdigest()).corrupt_after_acquisition(material['scores'])
    result = session.review_pending(pending['request_digest'], store)
    attempt = session.task_snapshot()['attempts'][0]
    assert result.receipt is None and 'not a JSON object' in result.reason
    assert session.pending_reviews == [] and len(TASK_CALLS) == before + 1
    assert attempt['assessment_outcomes'] == {'evolution-judge': 'pass'}
    assert attempt['disposition'] == 'failed-review' and attempt['receipt'] is None
    assert attempt['output']['raw_available'] is True
    archive = session.archive()
    fact = next(iter(json.loads(archive)['task_refusals'].values()))['record']
    assert fact['failure']['kind'] == 'post-consumption-verification-error'
    assert fact['failure']['exception_type'] == 'twin.skills.SkillError'
    assert 'not a JSON object' in fact['failure']['message']
    assert fact['permissions_after_acquisition'] is None
    assert_terminal_tamper_refuses(material, archive)
    for failure in ({'kind': 'current-permission-refused'},
                    {**fact['failure'], 'message': 'TEST_ONLY invented error'}):
        forged = copy.deepcopy(json.loads(archive))
        value = next(iter(forged['task_refusals'].values()))
        value['record']['failure'] = failure
        value['digest'] = q.digest(value['record'])
        with pytest.raises(ValueError):
            q.HostSession.restore(q.canonical(forged), material['resolver'], task_policy=material['host_policy'])
    restored = q.HostSession.restore(archive, material['resolver'], task_policy=material['host_policy'])
    assert restored.archive() == archive
    catalogue = tmp_path / 'error-catalogue'
    assert import_session(catalogue, material, restored).archive() == archive
    assert import_in_fresh_process(catalogue, material, protected_request()['repo'].model_root, restored.identity) == {
        'raw_calls': 0, 'pending': 0, 'disposition': 'failed-review', 'archive_sha256': q.hashlib.sha256(archive).hexdigest()}
    material['scores'].write_bytes(scores)
    assert material['resolver'].permission('evolution-judge', actor).granted
    public_acceptance_cannot_replace_known_consumed_refusal(material, archive)
    assert restored.review_pending(pending['request_digest'], store).receipt is None
    assert restored.archive() == archive and len(TASK_CALLS) == before + 1
    assert import_session(tmp_path / 'repaired-catalogue', material, restored).archive() == archive
