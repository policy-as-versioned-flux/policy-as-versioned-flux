"""TEST_ONLY returned-byte retention after source consistency revocation."""
import json
from pathlib import Path

import pytest

from twin import qualification as q
from bench.qualification_controls import population, parse_position, basis_holds
from test_capture_group import causal_pair, mechanical_causal, parse_causal

CALLS = []


def mutating_position(payload, config):
    CALLS.append('position')
    Path(config['support']).write_bytes(b'TEST_ONLY changed during invocation')
    return q.RuntimeResult(q.canonical({'position': payload['position'], 'evidence': payload['evidence']}),
                           {'purpose': 'TEST_ONLY'}, {'retained': 'TEST_ONLY actual runner observation'})


def mutating_causal(payload, config):
    CALLS.append('causal')
    raw = mechanical_causal(payload, config)
    Path(config['support']).write_bytes(b'TEST_ONLY changed during invocation')
    return q.RuntimeResult(raw, {'purpose': 'TEST_ONLY'}, {'retained': 'TEST_ONLY actual runner observation'})


def actor_with_support(tmp_path, runner, parser):
    support = tmp_path / 'TEST_ONLY-support.txt'; support.write_bytes(b'TEST_ONLY original')
    return q.Actor.freeze(runner, parser, {'purpose': 'TEST_ONLY', 'support': str(support),
        'runtime_contract': {'purpose': 'TEST_ONLY'}}, support=(support,))


def test_postcapture_identity_refusal_returns_actual_raw_runtime_and_no_stated_answer(tmp_path):
    actor = actor_with_support(tmp_path, mutating_position, parse_position)
    payload = {'position': .5, 'evidence': 'TEST_ONLY retained evidence'}
    output = actor.invoke(payload)
    packet = json.loads(output.packet)
    assert output.raw == q.canonical(payload)
    assert packet['raw_available'] is True and 'source changed' in output.failure
    assert packet['observed_runtime'] == {'purpose': 'TEST_ONLY'}
    assert packet['observations'] == {'retained': 'TEST_ONLY actual runner observation'}
    assert output.stated.answer is None and output.stated.basis is None
    with pytest.raises(ValueError, match='source changed'):
        actor.invoke(payload)


def test_selection_returns_all_counted_rows_and_actual_first_raw_after_revocation(tmp_path):
    actor = actor_with_support(tmp_path, mutating_position, parse_position)
    pop = population(count=3)
    selected = q.Selection.freeze(actor, pop, basis_holds, test_only=q.TEST_ONLY_MECHANICS)
    before = len(CALLS)
    captured = selected.capture()
    rows = json.loads(captured.packet)['rows']
    assert len(rows) == 3 and len(CALLS) == before + 1
    assert q.Output(q.canonical(rows[0]['output'])).raw == q.canonical(pop.corpus[0]['input'])
    assert rows[0]['output']['raw_available'] is True
    assert all(row['output']['failure'] and row['output']['answer'] is None for row in rows)
    assert all(row['output']['raw_available'] is False for row in rows[1:])
    with pytest.raises(ValueError, match='source changed'):
        selected.evaluate(captured)
    with pytest.raises(ValueError, match='source changed'):
        selected.archive(captured)


def test_group_returns_one_raw_core_without_invoking_remaining_subjects_after_revocation(tmp_path):
    original = causal_pair()
    actor = actor_with_support(tmp_path, mutating_causal, parse_causal)
    pair = tuple(q.Selection.freeze(actor, item.population, basis_holds, review=item.review,
                                   test_only=q.TEST_ONLY_MECHANICS) for item in original)
    group = q.CaptureGroup.freeze(pair)
    before = len(CALLS)
    core = group.capture()
    rows = json.loads(core.packet)['rows']
    assert len(rows) == 3 and len(CALLS) == before + 1
    assert rows[0]['output']['raw_available'] is True
    assert q.Output(q.canonical(rows[0]['output'])).raw
    assert all(row['output']['failure'] and row['output']['answer'] is None for row in rows)
    with pytest.raises(ValueError, match='source changed'):
        group.view(pair[0], core)
    with pytest.raises(ValueError, match='source changed'):
        group.archive(core)


def task_runner_that_revokes_support_after_returned_bytes_are_computed(payload, config):
    from test_task_sessions import task_mechanical_runner
    raw = task_mechanical_runner(payload, config)
    if Path(config['TEST_ONLY_arm']).exists():
        Path(config['TEST_ONLY_support']).write_bytes(b'TEST_ONLY source revoked during live call')
    return q.RuntimeResult(raw, {'purpose': 'TEST_ONLY'}, {'retained': 'TEST_ONLY actual task callback observation'})


def test_registered_task_keeps_actual_raw_failed_capture_but_refuses_stale_authority(protected_request, tmp_path):
    from test_task_sessions import genuine_task_material, TASK_CALLS
    support = tmp_path / 'TEST_ONLY-task-support.txt'; support.write_bytes(b'TEST_ONLY original task support')
    arm = tmp_path / 'TEST_ONLY-arm'
    material = genuine_task_material(protected_request, tmp_path,
        runner=task_runner_that_revokes_support_after_returned_bytes_are_computed,
        actor_config={'TEST_ONLY_support': str(support), 'TEST_ONLY_arm': str(arm),
                      'runtime_contract': {'purpose': 'TEST_ONLY'}}, support=(support,))
    assert material['resolver'].permission('evolution-judge', material['actor'].model_version).granted
    session = material['resolver'].host_session(material['inputs']); session.bind_task_job(material['job'])
    arm.write_bytes(b'TEST_ONLY arm one openly authored fault control')
    before = len(TASK_CALLS)
    result = session.judge('evolution-judge', material['actor'].model_version, material['job']['subjects'][0])
    assert result.receipt is None and len(TASK_CALLS) == before + 1 and session.pending_reviews == []
    assert result.output and result.output.raw and 'source changed' in result.output.failure
    actual = json.loads(result.output.raw)
    assert actual['answer'] == {'evolution_position': 0.0}
    attempt = session.task_snapshot()['attempts'][0]
    assert attempt['disposition'] == 'failed' and attempt['raw_available'] is True
    assert attempt['output']['observed_runtime'] == {'purpose': 'TEST_ONLY'}
    assert attempt['output']['observations'] == {'retained': 'TEST_ONLY actual task callback observation'}
    saved = json.loads(session.archive())
    assert saved['failed_outputs'][0]['output'] == json.loads(result.output.packet) == attempt['output']
    assert not material['resolver'].permission('evolution-judge', material['actor'].model_version).granted
    with pytest.raises(ValueError, match='source changed'):
        q.HostSession.restore(session.archive(), material['resolver'], task_policy=material['host_policy'])
    assert len(TASK_CALLS) == before + 1

from test_task_inputs import protected_request
