"""TEST_ONLY source/protocol controls, never Linux/model execution evidence."""
import pytest
import copy
import base64
import hashlib
import json


def profile():
    return {'profile': 'signal-linux-bf16-v1', 'max_input_tokens': 4096, 'max_new_tokens': 512,
        'timeout_seconds': 900, 'threads': 2, 'interop_threads': 1,
        'backend': {'script': '/TEST_ONLY/qwen_backend.py', 'sha256': '1'*64,
                    'python': '/TEST_ONLY/python', 'python_sha256': '2'*64},
        'runtime_contract': {'TEST_ONLY': 'not an acquired runtime'},
        'linux_profile': {'model_id': 'Qwen/Qwen3-4B-Instruct-2507',
            'revision': 'cdbee75f17c01a7cc42f958dc650907174af0554',
            'model_manifest_sha256': '409410d7d41d7e62aafb27c18f049fe3c62d66383b3a5b89d5fadfd3b773fd7e',
            'runtime_manifest_sha256': '3'*64,
            'chat_template_sha256': '64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326',
            'dtype': 'torch.bfloat16', 'device': 'cpu', 'attention': 'eager',
            'do_sample': False, 'num_beams': 1, 'num_return_sequences': 1,
            'seed': 0, 'use_cache': True, 'cache_implementation': 'dynamic',
            'eos_token_ids': [151645, 151643], 'pad_token_id': 151643}}


def test_profile_preserves_exact_reviewed_bounds_without_borrowing_another_actor():
    from twin.linux_candidate import validate_profile
    value = profile()
    frozen = validate_profile(value)
    value['linux_profile']['eos_token_ids'].clear()
    assert frozen['linux_profile']['eos_token_ids'] == [151645, 151643]
    other = profile()
    other.update({'max_new_tokens': 2048, 'timeout_seconds': 600})
    with pytest.raises(ValueError, match='reviewed Linux profile'):
        validate_profile(other)


def test_model_named_authority_cannot_supply_a_registered_linux_host():
    from twin.linux_candidate import invoke_pair
    with pytest.raises(ValueError, match='protected host authority'):
        invoke_pair({'input': 'TEST_ONLY input', 'prompt_utf8': 'TEST_ONLY prompt'},
                    {'profile': 'signal-linux-bf16-v1', 'authority': {'uid': 0, 'root': '/run'}})


def test_explicit_generator_profile_keeps_its_own_caps_and_shared_deadline():
    from twin.linux_candidate import validate_profile
    value = profile()
    value.update({'profile': 'substrate-linux-bf16-v1', 'max_new_tokens': 2048,
        'timeout_seconds': 600, 'context_tokens': 8192, 'raw_output_max_bytes': 131072})
    assert validate_profile(value)['timeout_seconds'] == 600
    value['profile'] = 'signal-linux-bf16-v1'
    with pytest.raises(ValueError, match='reviewed Linux profile'):
        validate_profile(value)


def wire_control():
    from twin.qualification import canonical
    request = {'input': 'TEST_ONLY YAML: value', 'prompt_utf8': 'TEST_ONLY frozen prompt'}
    config = profile()
    binding = {'input_sha256': hashlib.sha256(canonical(request['input'])).hexdigest(),
        'prompt_sha256': hashlib.sha256(request['prompt_utf8'].encode()).hexdigest(),
        'rendered_chat_sha256': '4'*64, 'input_ids': [12, 34],
        'input_ids_sha256': hashlib.sha256(canonical([12, 34])).hexdigest()}
    lease = 'a'*48
    def event(kind, **fields): return {'event': kind, 'lease': lease, **fields}
    raw = b'{"TEST_ONLY":"retained actual bytes"}<|im_end|>'
    packets = [event('lease', authority='5'*64, profile_sha256=hashlib.sha256(canonical(config)).hexdigest()),
        event('phase_start', phase='preflight', pid=100, start='1000'),
        event('frame', phase='preflight', body={'type': 'preflight', 'binding': binding}),
        event('phase_end', phase='preflight', returncode=0, empty=True, reaped=True),
        event('phase_start', phase='generate', pid=101, start='1001'),
        event('frame', phase='generate', body={'type': 'input', 'binding': binding}),
        event('frame', phase='generate', body={'type': 'token', 'index': 0, 'id': 151645,
            'raw_base64': base64.b64encode(raw).decode()}),
        event('frame', phase='generate', body={'type': 'end'}),
        event('frame', phase='generate', body={'type': 'complete', 'output_ids': [151645],
            'raw_base64': base64.b64encode(raw).decode(), 'stop_reason': 'eos',
            'observed_runtime': config['runtime_contract']}),
        event('phase_end', phase='generate', returncode=0, empty=True, reaped=True),
        event('done', empty=True, reaped=True, removed=True)]
    return request, config, packets, raw


def test_paired_journal_conserves_both_phase_bindings_and_actual_raw_bytes():
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    journal = PairJournal(request, config, '5'*64)
    for packet in packets:
        journal.accept(packet)
    result = journal.result()
    assert result.failure is None and result.raw == raw
    assert result.observations['input_ids'] == [12, 34]
    assert result.observations['output_ids'] == [151645]
    assert result.observations['phase_identities'] == [[100, '1000'], [101, '1001']]


def test_generation_cannot_skip_its_actual_tokenizer_binding_and_borrow_preflight():
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    journal = PairJournal(request, config, '5'*64)
    with pytest.raises(ValueError, match='generation.*binding'):
        for packet in packets[:5] + packets[6:]:
            journal.accept(packet)


@pytest.mark.parametrize('change', ['foreign lease', 'different tokenization', 'same process',
                                  'not reaped', 'no teardown', 'wrong runtime'])
def test_paired_evidence_refuses_foreign_or_incomplete_captures(change):
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    if change == 'foreign lease': packets[4]['lease'] = 'b'*48
    elif change == 'different tokenization':
        packets[5]['body']['binding'] = copy.deepcopy(packets[5]['body']['binding'])
        packets[5]['body']['binding']['rendered_chat_sha256'] = 'different'
    elif change == 'same process': packets[4].update({'pid': 100, 'start': '1000'})
    elif change == 'not reaped': packets[3]['reaped'] = False
    elif change == 'no teardown': packets[-1]['empty'] = False
    else: packets[8]['body']['observed_runtime'] = {'TEST_ONLY': 'a different actual build'}
    journal = PairJournal(request, config, '5'*64)
    with pytest.raises(ValueError):
        for packet in packets: journal.accept(packet)


def test_partial_actual_tokens_survive_failure_without_a_completed_answer():
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    journal = PairJournal(request, config, '5'*64)
    for packet in packets[:7]: journal.accept(packet)
    result = journal.result('TEST_ONLY timeout before end')
    assert result.raw == raw and result.failure and result.observations['partial']
    assert result.observations['output_ids'] == [151645]


def test_separate_token_and_chunked_raw_frames_conserve_actual_bytes_and_ids():
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    token = packets[6]['body']
    del token['raw_base64']
    chunk = copy.deepcopy(packets[6])
    chunk['body'] = {'type': 'raw', 'count': 1, 'offset': 0, 'total': len(raw),
        'raw_base64': base64.b64encode(raw).decode()}
    packets.insert(7, chunk)
    journal = PairJournal(request, config, '5'*64)
    for packet in packets: journal.accept(packet)
    assert journal.result().raw == raw and journal.result().failure is None


def test_incomplete_raw_snapshot_is_retained_as_partial_not_completed_answer():
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    del packets[6]['body']['raw_base64']
    journal = PairJournal(request, config, '5'*64)
    for packet in packets[:7]: journal.accept(packet)
    frame = copy.deepcopy(packets[6])
    frame['body'] = {'type': 'raw', 'count': 1, 'offset': 0, 'total': 100000,
        'raw_base64': base64.b64encode(b'X'*32768).decode()}
    journal.accept(frame)
    result = journal.result('TEST_ONLY interruption within raw snapshot')
    assert result.raw == b'X'*32768 and result.observations['output_ids'] == [151645]
    with pytest.raises(ValueError, match='raw'):
        for packet in packets[7:]: journal.accept(packet)


def test_failed_real_child_protocol_retains_observations_and_verified_teardown():
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    journal = PairJournal(request, config, '5'*64)
    for packet in packets[:7]: journal.accept(packet)
    observed = copy.deepcopy(packets[6])
    observed['body'] = {'type': 'observation', 'facts': {'TEST_ONLY actual loaded dtype': 'foreign'}}
    journal.accept(observed)
    failed = copy.deepcopy(observed)
    failed['body'] = {'type': 'failure', 'error': 'TEST_ONLY actual runtime mismatch'}
    journal.accept(failed)
    end = copy.deepcopy(packets[-2]); end['returncode'] = 1
    journal.accept(end)
    terminal = copy.deepcopy(packets[-1]); terminal['event'] = 'aborted'
    journal.accept(terminal)
    result = journal.result()
    assert result.failure and 'runtime mismatch' in result.failure and result.raw == raw
    assert result.observations['child_observations'] == [{'TEST_ONLY actual loaded dtype': 'foreign'}]
    assert result.observations['teardown_verified'] is True


def test_incremental_parent_reader_keeps_partial_raw_stderr_and_nonzero_exit(tmp_path):
    from twin.linux_candidate import read_pair
    from twin.qualification import canonical
    import subprocess
    import sys
    import time
    request, config, packets, raw = wire_control()
    script = tmp_path/'TEST_ONLY_pair.py'
    script.write_text('import sys,json\nsys.stdin.buffer.readline()\n'
        'packets=json.loads('+repr(json.dumps(packets[:7]))+')\n'
        'for p in packets: print(json.dumps(p),flush=True)\n'
        'sys.stderr.buffer.write(b"TEST_ONLY actual child OOM detail")\n'
        'sys.stderr.flush()\nsys.exit(7)\n')
    child = subprocess.Popen([sys.executable, str(script)], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = read_pair(child, request, config, '5'*64, canonical({'TEST_ONLY': 'control'}), time.monotonic()+13)
    assert child.returncode == 7 and result.failure and result.raw == raw
    assert result.observations['output_ids'] == [151645]
    assert 'OOM detail' in result.observations['guardian_stderr']
    assert not result.observations['teardown_verified']


def test_host_failure_and_bad_resource_facts_survive_without_becoming_child_authority():
    from twin.linux_candidate import PairJournal
    request, config, packets, raw = wire_control()
    journal = PairJournal(request, config, '5'*64)
    journal.accept(packets[0])
    bad = {'event': 'resources', 'lease': 'a'*48, 'phase': None,
        'facts': {'TEST_ONLY': 'actual OOM counter', 'memory.events': {'oom_kill': 1}}}
    journal.accept(bad)
    journal.accept({'event':'failure','lease':'a'*48,'error':'TEST_ONLY actual resource refusal'})
    journal.accept({'event':'aborted','lease':'a'*48,'empty':True,'reaped':True,'removed':True})
    result = journal.result()
    assert result.failure and 'resource refusal' in result.failure
    assert bad in result.observations['guardian_events']
    assert result.observations['teardown_verified'] is True


def test_complete_model_stream_cannot_borrow_absent_host_kernel_proof():
    from twin.linux_candidate import HostCapture, HostAuthority, PairJournal
    request, config, packets, raw = wire_control()
    journal = PairJournal(request, config, '5'*64)
    for packet in packets: journal.accept(packet)
    capture = HostCapture(HostAuthority(b'{"TEST_ONLY":"no OS authority"}'),
        {'candidate_uid': 65534, 'candidate_gid': 65534, 'cpus': [3, 4]},
        {'config': config, 'readonly_mounts': []}, 100,
        {'pid': 99, 'start': '1000', 'uids': [501]*4}, 2000.)
    with pytest.raises(ValueError, match='host lease|kernel proof'):
        capture.finish(journal)


def test_matching_hash_and_root_looking_json_cannot_replace_os_owned_host_authority(tmp_path):
    from twin.linux_candidate import protected_bytes
    path = tmp_path/'run'/'policy-as-versioned-flux-candidate'/'host.json'
    path.parent.mkdir(parents=True)
    raw = b'{"uid":0,"issuer":"protected host","TEST_ONLY":"candidate-writable"}'
    path.write_bytes(raw)
    with pytest.raises(ValueError, match='owner|foreign|protected'):
        protected_bytes(path, hashlib.sha256(raw).hexdigest())


@pytest.mark.parametrize('name', [None, [], {}, 'unknown-linux-profile', 'linux-qwen-bf16/v1'])
def test_unknown_or_omitted_profile_identity_never_borrows_an_approved_actor(name):
    from twin.linux_candidate import validate_profile
    value = profile()
    value['profile'] = name
    with pytest.raises(ValueError, match='reviewed Linux profile'):
        validate_profile(value)
