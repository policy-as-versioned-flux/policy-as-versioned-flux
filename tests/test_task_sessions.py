"""TEST_ONLY protected task history; no actual model or permission grant."""
from twin import qualification as q
from twin.task_contracts import TaskContract


def test_preflight_refusal_retains_a_public_snapshot_even_with_invalid_inputs():
    row = {'subject': 'TEST_ONLY-missing', 'issuer': 'TEST_ONLY', 'input': {'schema': 'twin.evolution-input/v2'},
           'context': {}, 'source': {}}
    inputs = q.HostInputs.freeze((row,), ('TEST_ONLY',))
    session = q.Resolver().host_session(inputs)
    job = {'task': 'evolution', 'task_contract_sha256': TaskContract.freeze('evolution').digest,
           'model_version': 'actor-' + '1' * 64, 'organisation': 'driftwood', 'subjects': ['TEST_ONLY-missing']}
    session.bind_task_job(job)
    session.decline_task_run(('TEST_ONLY-missing',), 'TEST_ONLY invalid input, human required')
    snapshot = session.task_snapshot()
    assert snapshot['job'] == job
    assert snapshot['inputs'] == [row]
    assert len(snapshot['attempts']) == len(snapshot['declines']) == 1
    attempt = snapshot['attempts'][0]
    assert attempt['actor_sha256'] == '1' * 64
    assert attempt['capture_sha256'] is None and attempt['raw_available'] is False
    assert attempt['disposition'] == 'refused-before-invocation'
    assert attempt['reason'] == 'TEST_ONLY invalid input, human required'
