"""Public candidate adapter controls, using only explicit TEST_ONLY responses."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import pytest

from twin import task_candidate
from twin.task_contracts import TaskContract
from twin.qualification import RuntimeResult
from twin.task_inputs import resolve_task_input
from test_signal_inputs import protected_request
from test_task_inputs import task_request


def test_evolution_preserves_the_complete_answer_and_actual_basis():
    config = {'task': 'evolution', 'task_contract_digest': TaskContract.freeze('evolution').digest}
    basis = {'reason': 'TEST_ONLY declared capability and frame support this estimate',
        'witnesses': [{'path': ['task', 'evidence', 0, 'text'], 'quote': 'TEST_ONLY evidence'}],
        'calculations': []}
    raw = json.dumps({'schema': 'twin.evolution-response/v1',
        'answer': {'evolution_position': 0.4}, 'basis': basis}).encode()
    stated = task_candidate.parse(raw, config)
    assert stated.answer == {'evolution_position': 0.4}
    assert stated.basis == basis


def test_declared_terminal_token_retains_the_actual_decline():
    config = {'task': 'evolution', 'task_contract_digest': TaskContract.freeze('evolution').digest,
        'terminal_token': '<|im_end|>'}
    stated = task_candidate.parse(b'{"decline":"TEST_ONLY source cannot support the frame"}<|im_end|>', config)
    assert stated.answer is None
    assert stated.basis == {'decline': 'TEST_ONLY source cannot support the frame'}


def test_whitespace_cannot_be_a_factual_decline():
    config = {'task': 'evolution', 'task_contract_digest': TaskContract.freeze('evolution').digest}
    with pytest.raises(ValueError):
        task_candidate.parse(b'{"decline":"   "}', config)


def config_for(task):
    return {'task': task, 'task_contract_digest': TaskContract.freeze(task).digest}


def basis():
    return {'reason': 'TEST_ONLY actual source statement',
        'witnesses': [{'path': ['task', 'evidence', 0, 'statement'], 'quote': 'TEST_ONLY'}],
        'calculations': []}


def causal_answer():
    return {'edge': {'from': 'TEST_ONLY-dosage', 'to': 'TEST_ONLY-response',
        'type': 'influences', 'sign': 'positive', 'lag_days': 30,
        'elasticity': {'min': 0.1, 'mode': 0.3, 'max': 0.6}, 'evidence_grade': 4},
        'confounders': [{'id': 'TEST_ONLY-season', 'reason': 'TEST_ONLY not excluded', 'status': 'not-ruled-out'}],
        'alternatives': ['TEST_ONLY shared seasonal effect'],
        'units': {'from': 'TEST_ONLY mg/day', 'to': 'TEST_ONLY score', 'lag': 'days',
            'elasticity_definition': 'TEST_ONLY proportional response per proportional dosage'}}


def response(task, answer, actual_basis=None):
    return json.dumps({'schema': f'twin.{task}-response/v1', 'answer': answer,
        'basis': basis() if actual_basis is None else actual_basis}, allow_nan=False).encode()


def test_complete_causal_response_is_preserved_without_inventing_units_or_grade():
    actual = causal_answer()
    stated = task_candidate.parse(response('causal', actual), config_for('causal'))
    assert stated.answer == actual
    assert stated.basis == basis()


def test_overbound_raw_response_refuses_instead_of_hiding_bytes_with_whitespace():
    raw = b'{"decline":"TEST_ONLY"}' + b' ' * 131072
    with pytest.raises(ValueError):
        task_candidate.parse(raw, config_for('evolution'))


def profile_for(task):
    root = Path(__file__).resolve().parents[1]
    declared = json.loads((root / 'twin/task_contract/profiles.json').read_bytes())
    limits = declared['profiles'][task + '-linux-bf16-v1']
    model = dict(declared['model'])
    model['model_id'] = model.pop('id')
    model.pop('runtime_build_and_host_authority')
    model['runtime_manifest_sha256'] = '0' * 64  # TEST_ONLY, explicitly not acquired authority.
    # Existing source bytes, deliberately not an acquired operational backend.
    script = root / 'bench/pinned-candidate/smoke.py'
    python = Path(sys.executable).resolve()
    prompt = json.loads((root / 'twin/task_contract/prompts.json').read_bytes())
    return {**config_for(task), 'profile': task + '-linux-bf16-v1',
        **{key: limits[key] for key in ('max_input_tokens', 'max_new_tokens', 'context_tokens',
            'raw_output_max_bytes', 'timeout_seconds', 'threads', 'interop_threads')},
        'linux_profile': model, 'runtime_contract': {'purpose': 'TEST_ONLY-unacquired'},
        'backend': {'script': str(script), 'sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
            'python': str(python), 'python_sha256': hashlib.sha256(python.read_bytes()).hexdigest()},
        'prompt_sha256': next(row['sha256'] for row in prompt['prompts'] if row['task'] == task)}


@pytest.mark.parametrize('task', ['evolution', 'causal', 'gameplay', 'ethics'])
def test_unacquired_task_profile_cannot_freeze_an_operational_actor_or_launch(monkeypatch, task):
    def forbidden(*args, **kwargs):
        pytest.fail('source-only actor freeze attempted a process launch')
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    with pytest.raises(ValueError):
        task_candidate.freeze_actor(task, profile_for(task))


def test_profile_for_a_different_task_refuses_before_any_input_or_backend_work():
    config = profile_for('evolution')
    config['profile'] = 'causal-linux-bf16-v1'
    with pytest.raises(ValueError):
        task_candidate.render_prompt({}, config)


def test_empty_gameplay_preserves_negative_checks_in_the_actual_basis():
    actual_basis = {**basis(), 'checks': [{'play': 'land-grab', 'component': 'TEST_ONLY-own',
        'present': False, 'reason': 'TEST_ONLY position is outside this play',
        'witnesses': [{'path': ['task', 'org_components', 0], 'value': 'TEST_ONLY-own'}],
        'incumbency_checked': False}]}
    stated = task_candidate.parse(response('gameplay', {'opportunities': []}, actual_basis), config_for('gameplay'))
    assert stated.answer == {'opportunities': []}
    assert stated.basis == actual_basis


def test_denied_ethics_with_no_failed_rung_preserves_the_dpia_blocked_form():
    actual = {'admitted': False, 'ladder': {'stopped_at': None, 'rungs': [
        {'rung': 'purpose', 'passed': True, 'justification': 'TEST_ONLY bounded purpose'},
        {'rung': 'necessity', 'passed': True, 'justification': 'TEST_ONLY necessary granularity'},
        {'rung': 'proportionality', 'passed': True, 'justification': 'TEST_ONLY bounded impact'}]}}
    actual_basis = {**basis(), 'witnesses': [{'path': ['task', 'dpia', 'complete'], 'value': False}]}
    stated = task_candidate.parse(response('ethics', actual, actual_basis), config_for('ethics'))
    assert stated.answer == actual
    assert stated.basis == actual_basis


@pytest.mark.parametrize('raw', [
    b'{"decline":"TEST_ONLY","decline":"replaced"}',
    b'{"decline":"TEST_ONLY","permission":true}',
    b'{"decline":"TEST_ONLY"} {}', b'```json\n{"decline":"TEST_ONLY"}\n```',
    b'\xff', b'{"decline":false}', b'{"decline":""}',
    b'{"decline":"TEST_ONLY"}<|im_end|><|im_end|>',
    b'{"decline":"TEST_ONLY"}<|endoftext|>',
    b'{"schema":"twin.evolution-response/v1","answer":{"evolution_position":true},"basis":{}}',
    b'{"schema":"twin.evolution-response/v1","answer":{"evolution_position":NaN},"basis":{}}',
])
def test_ambiguous_or_non_json_responses_never_become_answers(raw):
    config = {**config_for('evolution'), 'terminal_token': '<|im_end|>'}
    with pytest.raises(ValueError):
        task_candidate.parse(raw, config)


@pytest.mark.parametrize('replacement', [True, float('inf'), -0.1, 1.1])
def test_evolution_position_requires_a_finite_genuine_unit_interval_number(replacement):
    raw = json.dumps({'schema': 'twin.evolution-response/v1',
        'answer': {'evolution_position': replacement}, 'basis': basis()}).encode()
    with pytest.raises(ValueError):
        task_candidate.parse(raw, config_for('evolution'))


def test_nested_value_witness_cannot_hide_nonfinite_json():
    actual_basis = {**basis(), 'witnesses': [{'path': ['task'], 'value': {'nested': [float('inf')]}}]}
    raw = json.dumps({'schema': 'twin.evolution-response/v1',
        'answer': {'evolution_position': 0.5}, 'basis': actual_basis}).encode()
    with pytest.raises(ValueError):
        task_candidate.parse(raw, config_for('evolution'))


def test_render_keeps_the_complete_acquired_public_input_and_exact_template(protected_request):
    payload = resolve_task_input(**task_request(protected_request)).payload
    before = json.loads(json.dumps(payload))
    config = profile_for('evolution')
    rendered = task_candidate.render_prompt(payload, config)
    template = Path(__file__).resolve().parents[1].joinpath('twin/task_prompts/evolution.txt').read_bytes()
    expected_input = json.dumps(payload, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode()
    assert rendered == template.replace(b'{{INPUT_JSON}}', expected_input)
    assert payload == before
    assert payload['context']['metadata']['primary']['publication']['precision'] == 'month'


def test_run_retains_original_capture_when_actual_basis_witness_is_false(monkeypatch, protected_request):
    payload = resolve_task_input(**task_request(protected_request)).payload
    actual_basis = {**basis(), 'witnesses': [{'path': ['task', 'component', 'name'],
        'quote': 'TEST_ONLY quotation absent from supplied component'}]}
    raw = response('evolution', {'evolution_position': 0.4}, actual_basis)
    original = RuntimeResult(raw, {'purpose': 'TEST_ONLY'}, {'capture': 'TEST_ONLY original observations'})
    calls = []
    def pair(request, config):
        calls.append(request)
        return original
    # Explicit TEST_ONLY public transport boundary, never an acquired Linux host.
    monkeypatch.setitem(sys.modules, 'twin.linux_candidate', SimpleNamespace(
        validate_profile=lambda config: config, invoke_pair=pair))
    result = task_candidate.run(payload, profile_for('evolution'))
    assert len(calls) == 1
    assert calls[0]['input'] == payload
    assert result.raw == raw
    assert result.observed_runtime == original.observed_runtime
    assert result.observations == original.observations
    assert result.failure


def causal_payload(protected_request):
    args = task_request(protected_request, task='causal')
    job = args['protected_job']
    packet = json.loads(job['source_packet'])
    target = {'kind': 'edge', 'from': 'test-only-local-service', 'to': 'test-only-local-standing'}
    packet['target'] = target
    packet['task']['measurement'] = {'from_unit': 'TEST_ONLY mg/day', 'to_unit': 'TEST_ONLY score',
        'lag_unit': 'days', 'elasticity_definition': 'TEST_ONLY proportional response per proportional dosage',
        'temporal_interpretation': 'TEST_ONLY declared thirty day interval'}
    job['target'] = target
    job['source_packet'] = json.dumps(packet, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    job['source_pin'] = hashlib.sha256(job['source_packet']).hexdigest()
    return resolve_task_input(**args).payload


@pytest.mark.parametrize('defect', [None, 'unordered-pert', 'self-edge', 'duplicate-confounder', 'units', 'missing-confounder'])
def test_full_causal_capture_checks_actual_ordered_pair_units_and_complete_confounders(monkeypatch, protected_request, defect):
    payload = causal_payload(protected_request)
    assert [item['id'] for item in payload['task']['candidate_confounders']] == ['test-only-cloud']
    answer = causal_answer()
    answer['edge'].update({'from': payload['target']['from'], 'to': payload['target']['to']})
    answer['confounders'][0]['id'] = 'test-only-cloud'
    actual_basis = {**basis(), 'witnesses': [{'path': ['task', 'from', 'name'],
        'quote': payload['task']['from']['name']}]}
    if defect == 'unordered-pert':
        answer['edge']['elasticity']['mode'] = 0.8
    elif defect == 'self-edge':
        answer['edge']['to'] = answer['edge']['from']
    elif defect == 'duplicate-confounder':
        answer['confounders'].append({**answer['confounders'][0], 'reason': 'TEST_ONLY different reason'})
    elif defect == 'units':
        answer['units']['from'] = 'TEST_ONLY silently converted grams/day'
    elif defect == 'missing-confounder':
        answer['confounders'] = []
    raw = response('causal', answer, actual_basis)
    original = RuntimeResult(raw, {'purpose': 'TEST_ONLY'}, {'capture': 'TEST_ONLY causal original'})
    calls = []
    def pair(request, config):
        calls.append(request)
        return original
    monkeypatch.setitem(sys.modules, 'twin.linux_candidate', SimpleNamespace(
        validate_profile=lambda config: config, invoke_pair=pair))
    result = task_candidate.run(payload, profile_for('causal'))
    assert len(calls) == 1
    assert result.raw == raw
    assert result.observations == original.observations
    assert bool(result.failure) is (defect is not None)


def test_wrong_prompt_identity_refuses_before_paired_transport(monkeypatch, protected_request):
    payload = resolve_task_input(**task_request(protected_request)).payload
    config = profile_for('evolution')
    config['prompt_sha256'] = '0' * 64
    def forbidden(*args, **kwargs):
        pytest.fail('changed prompt reached paired transport')
    monkeypatch.setitem(sys.modules, 'twin.linux_candidate', SimpleNamespace(
        validate_profile=lambda config: config, invoke_pair=forbidden))
    with pytest.raises(ValueError, match='prompt identity'):
        task_candidate.run(payload, config)


def test_gameplay_full_twenty_definition_input_and_reported_pairs_are_never_filtered(monkeypatch, protected_request):
    args = task_request(protected_request, task='gameplay')
    job = args['protected_job']
    packet = json.loads(job['source_packet'])
    target = {'kind': 'map', 'organisation': 'driftwood'}
    packet.update(target=target, task={})
    job['target'] = target
    job['source_packet'] = json.dumps(packet, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    job['source_pin'] = hashlib.sha256(job['source_packet']).hexdigest()
    payload = resolve_task_input(**args).payload
    assert len(payload['task']['components']) == len(payload['task']['positions']) == 20
    own = payload['task']['org_components']
    checks = [{'play': play, 'component': component, 'present': (play == 'land-grab' and index == 0),
        'reason': 'TEST_ONLY actual stated check, not an expected play label',
        'witnesses': [{'path': ['task', 'org_components', index], 'value': component}],
        'incumbency_checked': False} for play in payload['task']['catalogue']
        for index, component in enumerate(own)]
    answer = {'opportunities': [{'play': 'land-grab', 'component': own[0],
        'reason': 'TEST_ONLY preserve this reported opportunity even when semantic review may disagree'}]}
    actual_basis = {**basis(), 'witnesses': [{'path': ['task', 'org_components'], 'value': own}], 'checks': checks}
    raw = response('gameplay', answer, actual_basis)
    original = RuntimeResult(raw, {'purpose': 'TEST_ONLY'}, {'capture': 'TEST_ONLY complete map'})
    calls = []
    def pair(request, config):
        calls.append(request)
        return original
    monkeypatch.setitem(sys.modules, 'twin.linux_candidate', SimpleNamespace(
        validate_profile=lambda config: config, invoke_pair=pair))
    config = profile_for('gameplay')
    result = task_candidate.run(payload, config)
    assert result == original and not result.failure
    assert len(calls) == 1 and calls[0]['input'] == payload
    assert len(json.loads(calls[0]['prompt_utf8'].split('INPUT:\n', 1)[1])['task']['components']) == 20
    assert task_candidate.parse(result.raw, config).answer == answer
