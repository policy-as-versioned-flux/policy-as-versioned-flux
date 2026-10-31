"""BUILD_ONLY production interfaces with synthetic data/OS models; no child or network."""
import importlib.util
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest


SCRIPT = Path(__file__).parents[1] / 'bench/pinned-candidate/xpdf-origin/build_linux_pair.py'
spec = importlib.util.spec_from_file_location('xpdf_build_pair', SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_public_selection_cannot_enable_execution_or_touch_workspace(tmp_path):
    with patch('subprocess.Popen', side_effect=AssertionError('no child')), patch('urllib.request.urlopen', side_effect=AssertionError('no network')):
        result = module.build_linux_pair({'approved': True, 'scope': 'BUILD_ONLY'}, tmp_path / 'new')
    assert result['status'] == 'HELD'
    assert result['hold_codes'] == ['H_EXECUTION_SELECTION']
    assert result['commands'] == []
    assert result['native_H'] is None
    assert not (tmp_path / 'new').exists()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def held_bundle():
    selection = {
        'schema': 'twin.xpdf-linux-build-selection/v1', 'scope': 'BUILD_ONLY',
        'source_commit': '1' * 40, 'source_tree': '2' * 40,
        'workflow_sha256': '3' * 64, 'driver_sha256': '4' * 64, 'preparer_sha256': '5' * 64,
        'source_package_sha256': '37b3903b671b49c2d75efa7e2ab0694e64dde6affd0df7208df176aa86152adc',
        'bootstrap_selection_sha256': '6' * 64, 'tool_module_review_sha256': '7' * 64,
        'limits_profile': 'checkpoint-A-1800/v1',
        'expected_row': {'os': 'ubuntu-24.04', 'arch': 'x86_64-linux'},
        'official_archive': {'url': 'https://dl.xpdfreader.com/xpdf-4.06.tar.gz', 'bytes': 999317,
                             'sha256': '1c38f527c46caee0f712386d42a885b96a31ed9ce11904e872559859894d137e'},
    }
    bundle = {'SELECTION.json': encoded(selection), 'ENVIRONMENT.json': encoded({})}
    result = {
        'schema': 'twin.xpdf-linux-build-result/v2', 'scope': 'BUILD_DATA_ONLY',
        'selection_sha256': sha(bundle['SELECTION.json']), 'status': 'HELD',
        'hold_codes': ['H_EXECUTION_SELECTION'],
        'first_failure': {'phase': 'bootstrap-input-tools', 'command_id': None, 'reason': 'TEST_ONLY unappointed'},
        'clock': {'original_seconds': 1800, 'started': 0, 'deadline': 1800, 'ended': 1},
        'environment_manifest_sha256': sha(bundle['ENVIRONMENT.json']), 'tool_manifest_sha256': None,
        'source_conservation_sha256': None, 'variants': [], 'commands': [], 'files_manifest_sha256': None,
        'runtime_access_closure': 'UNESTABLISHED', 'native_H': None, 'private_native_handle': None,
        'native_N01_N08': 'UNRUN', 'actual_converter_invocations': 0, 'execution_or_publication_grant': 'NONE',
    }
    return reseal(bundle, result), result


def reseal(bundle, result):
    bundle = {key: value for key, value in bundle.items() if key not in {'RESULT.json', 'FILES.json'}}
    files = [{'path': key, 'bytes': len(raw), 'sha256': sha(raw), 'role': 'metadata'} for key, raw in sorted(bundle.items())]
    bundle['FILES.json'] = encoded({'schema': 'twin.xpdf-linux-build-files/v1', 'files': files,
                                   'logical_bytes': sum(f['bytes'] for f in files), 'self_included': False})
    result['files_manifest_sha256'] = sha(bundle['FILES.json'])
    bundle['RESULT.json'] = encoded(result)
    return bundle


def test_pure_checker_retains_held_unknowns_without_authority():
    bundle, result = held_bundle()
    with patch('subprocess.Popen', side_effect=AssertionError('no child')):
        summary = module.check_build_bundle(bundle, result['selection_sha256'])
    assert summary == {'status': 'HELD', 'build_complete': False, 'runtime_access_closure': 'UNESTABLISHED', 'native_permission': False}


@pytest.mark.parametrize('mutation', ['extra', 'unsafe', 'hash', 'authority'])
def test_checker_refuses_unbound_bytes_paths_and_authority(mutation):
    bundle, result = held_bundle()
    if mutation == 'extra':
        bundle['undeclared.txt'] = b'unbound'
    elif mutation == 'unsafe':
        bundle['../escape'] = b'outside'
        bundle = reseal(bundle, result)
    elif mutation == 'hash':
        bundle['ENVIRONMENT.json'] = b'changed'
    else:
        result['native_H'] = {'approved': True}
        bundle = reseal(bundle, result)
    with pytest.raises(ValueError):
        module.check_build_bundle(bundle, result['selection_sha256'])


def custody_bundle(history='valid_order'):
    bundle, result = held_bundle()
    proof = json.loads((Path(__file__).parent / 'fixtures/TEST_ONLY-xpdf-build/custody-projections.json').read_bytes())
    custody = deepcopy(proof['histories'][history])
    command = {
        'id': 'TEST_ONLY/pristine/1', 'phase': 'pristine',
        'argv': proof['binding_context']['argv'], 'environment_sha256': result['environment_manifest_sha256'],
        'started': 90, 'deadline': 100, 'ended': 100,
        'stdout': {'sha256': sha(b''), 'retained_bytes': 0, 'observed_bytes_lower_bound': 0, 'state': 'COMPLETE'},
        'stderr': {'sha256': sha(b''), 'retained_bytes': 0, 'observed_bytes_lower_bound': 0, 'state': 'COMPLETE'},
        'custody': custody, 'disposition': 'HELD' if history == 'unknown_prefix_held_only' else 'EXIT0_COMPLETE',
    }
    context = dict(proof['binding_context'], selection_sha256=result['selection_sha256'], environment_sha256=command['environment_sha256'])
    if custody['command_binding_sha256'] is not None:
        custody['command_binding_sha256'] = sha(encoded(context).rstrip(b'\n'))
    result['commands'] = [command]
    result['clock']['ended'] = 100
    bundle['logs/empty.log'] = b''
    return reseal(bundle, result), result


@pytest.mark.parametrize('history', ['valid_order', 'equal_tick_valid', 'unknown_prefix_held_only'])
def test_checker_conserves_known_and_unknown_synthetic_custody(history):
    bundle, result = custody_bundle(history)
    assert module.check_build_bundle(bundle, result['selection_sha256'])['status'] == 'HELD'


@pytest.mark.parametrize('history', ['post_first_reaping_signal', 'renewed_cleanup', 'equal_tick_post_reaping_signal'])
def test_checker_distinguishes_the_review_histories(history):
    bundle, result = custody_bundle(history)
    with pytest.raises(ValueError):
        module.check_build_bundle(bundle, result['selection_sha256'])


@pytest.mark.parametrize('mutation', ['ordinal', 'projection', 'pid', 'binding', 'duplicate', 'absence_before_reap', 'post_wait_absent', 'late_cleanup', 'past_command_end', 'unknown_success_end', 'next_after_unknown'])
def test_checker_refuses_custody_order_projection_and_unknown_success(mutation):
    bundle, result = custody_bundle('unknown_prefix_held_only' if mutation == 'next_after_unknown' else 'valid_order')
    command = result['commands'][0]
    events = command['custody']['observations']
    if mutation == 'ordinal': events[1]['ordinal'] = 0
    elif mutation == 'projection': command['custody']['signals'] = []
    elif mutation == 'pid': events[1]['detail']['pid'] = 124
    elif mutation == 'binding': command['custody']['command_binding_sha256'] = '0' * 64
    elif mutation == 'duplicate': events[1] = dict(events[0], ordinal=1)
    elif mutation == 'absence_before_reap': events[3], events[4] = events[4], events[3]
    elif mutation == 'post_wait_absent':
        events[1], events[2] = events[2], events[1]
        for i, e in enumerate(events): e['ordinal'], e['at'] = i, 99
        events[2]['detail']['outcome'] = 'ABSENT'
    elif mutation == 'late_cleanup': events[-1]['at'] = command['custody']['cleanup_ended'] = 101
    elif mutation == 'past_command_end': command['ended'] = 95
    elif mutation == 'unknown_success_end': command['ended'] = None
    else: result['commands'].append(deepcopy(command))
    bundle = reseal(bundle, result)
    with pytest.raises(ValueError):
        module.check_build_bundle(bundle, result['selection_sha256'])


class ModelClock:
    def __init__(self):
        self.now = 90.0
        self.cleanup_entry_error = False

    def __call__(self):
        if self.cleanup_entry_error:
            self.cleanup_entry_error = False
            raise SystemExit('TEST_ONLY secondary cleanup-entry failure')
        self.now += 0.01
        return self.now


def model_supervisor(monkeypatch, tmp_path, *, wait_unknown=False, body_cancel=False, entry_error=False, term_cancel=False, group_present=False, output=b'', allowance=5):
    """Model only OS/clock/stream edges of the source-appointed private execution seam."""
    clock = ModelClock()
    calls = []
    class Stream:
        def __init__(self, fd): self.fd = fd
        def fileno(self): return self.fd
        def close(self): calls.append(('close', self.fd))
    child = SimpleNamespace(pid=123, stdout=Stream(111), stderr=Stream(112), returncode=None)
    class Selector:
        def __init__(self): self.keys = {}
        def register(self, stream, event, name): self.keys[stream.fd] = SimpleNamespace(data=name, fd=stream.fd, fileobj=stream)
        def unregister(self, stream): self.keys.pop(stream.fd)
        def select(self, timeout): return [(key, 1) for key in list(self.keys.values())]
        def close(self): pass
    buffers = {111: [output, b''] if output else [b''], 112: [b'']}
    real_read = module.os.read
    def read(fd, count):
        if fd not in buffers: return real_read(fd, count)
        value = buffers[fd].pop(0)
        if len(value) > count:
            buffers[fd].insert(0, value[count:])
        return value[:count]
    def peek(*args):
        if body_cancel:
            if entry_error: clock.cleanup_entry_error = True
            raise KeyboardInterrupt('TEST_ONLY original body cancellation')
        return SimpleNamespace(si_pid=123)
    def kill(pid, number):
        assert pid == 123
        calls.append(('signal', number))
        if term_cancel and number == 15:
            raise KeyboardInterrupt('TEST_ONLY cleanup signal cancellation')
        if number == 0 and not group_present:
            raise ProcessLookupError()
    def wait(pid, flags):
        calls.append(('wait', pid))
        return (0, 0) if wait_unknown else (123, 0)
    monkeypatch.setattr(module.time, 'monotonic', clock)
    monkeypatch.setattr(module.subprocess, 'Popen', lambda *a, **k: child)
    monkeypatch.setattr(module.selectors, 'DefaultSelector', Selector)
    monkeypatch.setattr(module.os, 'set_blocking', lambda *a: None)
    monkeypatch.setattr(module.os, 'read', read)
    monkeypatch.setattr(module.os, 'waitid', peek)
    monkeypatch.setattr(module.os, 'waitpid', wait)
    monkeypatch.setattr(module.os, 'killpg', kill)
    bundle, result = held_bundle()
    result['clock']['ended'] = None
    environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC',
                   'HOME': str(tmp_path / 'home'), 'TMPDIR': str(tmp_path / 'tmp'), 'CMAKE_BUILD_PARALLEL_LEVEL': '2'}
    bundle['ENVIRONMENT.json'] = encoded(environment)
    result['environment_manifest_sha256'] = sha(bundle['ENVIRONMENT.json'])
    payload = {}
    def run():
        return module._supervise(result, 'pristine', ['/usr/bin/make', '-C', str(tmp_path), '-j2', 'VERBOSE=1', 'SHELL=/bin/sh', 'pdftotext'], tmp_path, environment, allowance, payload)
    return run, result, calls, clock, payload, bundle


@pytest.mark.parametrize('group_present', [False, True])
def test_modeled_leader_success_still_settles_owned_group_before_reaping(monkeypatch, tmp_path, group_present):
    run, result, calls, clock, payload, bundle = model_supervisor(monkeypatch, tmp_path, group_present=group_present)
    if group_present:
        with pytest.raises(module.BuildHold, match='cleanup'): run()
    else:
        assert run()['disposition'] == 'EXIT0_COMPLETE'
    assert calls.index(('signal', 9)) < next(i for i, c in enumerate(calls) if c[0] == 'wait')
    assert not any(c[0] == 'signal' and c[1] in (9, 15) for c in calls[next(i for i, c in enumerate(calls) if c[0] == 'wait'):])
    result['clock']['ended'] = clock()
    bundle.update({name: value[0] for name, value in payload.items()})
    assert module.check_build_bundle(reseal(bundle, result), result['selection_sha256'])['status'] == 'HELD'


def test_cleanup_entry_failure_conserves_original_cancellation_and_workspace(monkeypatch, tmp_path):
    import gc
    run, result, calls, _, _, _ = model_supervisor(monkeypatch, tmp_path, body_cancel=True, entry_error=True)
    evidence = tmp_path / 'original.txt'
    evidence.write_bytes(b'TEST_ONLY original')
    with pytest.raises(KeyboardInterrupt, match='original body'): run()
    gc.collect()
    custody = result['commands'][0]['custody']
    assert custody['cleanup_started'] is None and custody['direct_reap'] == 'UNOBSERVED'
    assert custody['workspace'] == 'RETAINED' and evidence.read_bytes() == b'TEST_ONLY original'
    assert not any(c[0] == 'wait' for c in calls)


def test_cancelled_cleanup_signal_uses_same_budget_for_best_effort_owned_kill(monkeypatch, tmp_path):
    run, result, calls, _, _, _ = model_supervisor(monkeypatch, tmp_path, term_cancel=True)
    with pytest.raises(KeyboardInterrupt, match='cleanup signal'): run()
    assert ('signal', 9) in calls
    custody = result['commands'][0]['custody']
    assert custody['cleanup_deadline'] == pytest.approx(custody['cleanup_started'] + 2)
    assert result['commands'][0]['disposition'] != 'EXIT0_COMPLETE'


@pytest.mark.parametrize('argv', [
    ['/usr/bin/make', '-C', 'TEST_ONLY_BUILD', '-j2', 'VERBOSE=1', 'SHELL=/bin/sh', 'all'],
    ['/usr/bin/make', '-C', 'TEST_ONLY_BUILD', '-j3', 'VERBOSE=1', 'SHELL=/bin/sh', 'pdftotext'],
    ['/tmp/TEST_ONLY/pdftotext', '-v'],
    ['/usr/bin/ctest'],
])
def test_even_held_data_cannot_normalize_a_forbidden_dispatch(argv):
    bundle, result = custody_bundle()
    command = result['commands'][0]
    command['argv'] = argv
    context = {'schema': 'twin.xpdf-build-custody-binding/v1', 'selection_sha256': result['selection_sha256'],
               'command_id': command['id'], 'phase': command['phase'], 'argv': argv,
               'environment_sha256': command['environment_sha256'], 'command_started': command['started'],
               'command_deadline': command['deadline'], 'checkpoint_started': result['clock']['started'],
               'checkpoint_deadline': result['clock']['deadline'], 'leader_pid': 123}
    command['custody']['command_binding_sha256'] = sha(encoded(context).rstrip(b'\n'))
    with pytest.raises(ValueError):
        module.check_build_bundle(reseal(bundle, result), result['selection_sha256'])


def test_command_start_clock_failure_retains_unknowns_before_any_launch(monkeypatch, tmp_path):
    _, result = held_bundle()
    def failed_clock(): raise SystemExit('TEST_ONLY original start-clock failure')
    monkeypatch.setattr(module.time, 'monotonic', failed_clock)
    monkeypatch.setattr(module.subprocess, 'Popen', lambda *a, **k: pytest.fail('no launch'))
    with pytest.raises(SystemExit, match='original start-clock'):
        module._supervise(result, 'pristine', ['/usr/bin/make', '-C', str(tmp_path), '-j2', 'VERBOSE=1', 'SHELL=/bin/sh', 'pdftotext'], tmp_path, {}, 5, {})
    assert len(result['commands']) == 1
    command = result['commands'][0]
    assert command['started'] is None and command['deadline'] is None
    assert command['custody']['reservation'] == 'NO_CHILD_CREATED'


def test_missing_actual_module_review_has_no_valid_v1_build_selection_shape():
    bundle, result = held_bundle()
    selection = json.loads(bundle['SELECTION.json'])
    selection['tool_module_review_sha256'] = None
    bundle['SELECTION.json'] = encoded(selection)
    result['selection_sha256'] = sha(bundle['SELECTION.json'])
    with pytest.raises(ValueError, match='schema'):
        module.check_build_bundle(reseal(bundle, result), result['selection_sha256'])


def test_fixed_contract_data_drift_cannot_raise_limits(monkeypatch, tmp_path):
    source = tmp_path / 'build-contract'
    source.mkdir()
    for name in module._CONTRACT_PINS:
        (source / name).write_bytes((module.PACKAGE / 'build-contract' / name).read_bytes())
    limits = json.loads((source / 'LIMITS-AND-RECIPE.json').read_bytes())
    limits['supervision']['compiler_workers_max'] = 3
    (source / 'LIMITS-AND-RECIPE.json').write_bytes(encoded(limits))
    monkeypatch.setattr(module, 'PACKAGE', tmp_path)
    bundle, result = held_bundle()
    with pytest.raises(ValueError, match='contract drifted'):
        module.check_build_bundle(bundle, result['selection_sha256'])


def test_supervisor_overflow_retains_exact_prefix_and_stops(monkeypatch, tmp_path):
    run, result, _, _, payload, _ = model_supervisor(monkeypatch, tmp_path, output=b'A' * (16 * 1024 * 1024 + 1), allowance=30)
    with pytest.raises(module.BuildHold, match='stream overflow'): run()
    stream = result['commands'][0]['stdout']
    assert stream['state'] == 'PREFIX_ONLY' and stream['retained_bytes'] == 16 * 1024 * 1024
    assert stream['observed_bytes_lower_bound'] == 16 * 1024 * 1024 + 1
    assert len(payload['journal/000-stdout.log'][0]) == 16 * 1024 * 1024


def test_unknown_reaping_holds_workspace_without_any_later_signal(monkeypatch, tmp_path):
    run, result, calls, _, _, _ = model_supervisor(monkeypatch, tmp_path, wait_unknown=True)
    with pytest.raises(module.BuildHold, match='cleanup'): run()
    custody = result['commands'][0]['custody']
    assert custody['direct_reap'] == custody['group_absence'] == 'UNOBSERVED'
    assert custody['workspace'] == 'RETAINED'
    first = next(i for i, call in enumerate(calls) if call[0] == 'wait')
    assert not any(call[0] == 'signal' for call in calls[first:])
