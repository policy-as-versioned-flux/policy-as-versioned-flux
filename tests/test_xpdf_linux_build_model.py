"""TEST_ONLY whole fixed driver with modeled OS/tool results; never execute any child."""
from collections import deque
from copy import deepcopy
import io
import os
from pathlib import Path
import re
import stat
import struct
from types import SimpleNamespace

import pytest

from test_xpdf_linux_build import module, held_bundle, encoded, sha


def apply_reviewed_patch_as_test_data(directory):
    """Minimal fixture serializer, not a production patch route or tool invocation."""
    lines = (module.PACKAGE / 'xpdf-4.06-origin.patch').read_bytes().splitlines(keepends=True)
    index = 0
    while index < len(lines):
        if not lines[index].startswith(b'--- a/'):
            index += 1
            continue
        name = lines[index + 1].split(b'\t')[0].strip()[6:].decode()
        source = (directory / name).read_bytes().splitlines(keepends=True)
        output = []
        cursor = 0
        index += 2
        while index < len(lines) and not lines[index].startswith(b'--- a/'):
            match = re.match(rb'@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@', lines[index])
            if match is None:
                index += 1
                continue
            offset = int(match[1]) if match[2] == b'0' else int(match[1]) - 1
            output.extend(source[cursor:offset])
            cursor = offset
            index += 1
            while index < len(lines) and lines[index][:1] in (b' ', b'+', b'-') and not lines[index].startswith(b'--- a/'):
                kind, value = lines[index][:1], lines[index][1:]
                if kind in (b' ', b'-'):
                    assert source[cursor] == value
                    cursor += 1
                if kind in (b' ', b'+'):
                    output.append(value)
                index += 1
        output.extend(source[cursor:])
        (directory / name).write_bytes(b''.join(output))


def fake_binary():
    interpreter = b'/lib64/ld-linux-x86-64.so.2\0'
    header = struct.pack('<16sHHIQQQIHHHHHH', b'\x7fELF\x02\x01\x01' + bytes(9), 3, 62, 1, 0, 64, 0, 0, 64, 56, 1, 0, 0, 0)
    program = struct.pack('<IIQQQQQQ', 3, 4, 120, 0, 0, len(interpreter), len(interpreter), 1)
    return header + program + interpreter


def whole_model(monkeypatch, tmp_path, archive, *, fail_stage=None, source_extra=False):
    selection = __import__('json').loads(held_bundle()[0]['SELECTION.json'])
    selection.update(driver_sha256=sha(module.SCRIPT.read_bytes()) if hasattr(module, 'SCRIPT') else sha(Path(module.__file__).read_bytes()),
                     preparer_sha256=sha((module.PACKAGE / 'prepare_source.py').read_bytes()))
    fixtures = tmp_path / 'TEST_ONLY-model-inputs'
    fixtures.mkdir()
    workflow = fixtures / 'workflow.data'
    workflow.write_bytes(b'TEST_ONLY workflow source; no actual CI selection')
    selection['workflow_sha256'] = sha(workflow.read_bytes())
    interpreter = fixtures / 'python3.12'
    interpreter.write_bytes(b'\x7fELFTEST_ONLY Python bootstrap fixture, never executable')
    module_data = fixtures / 'cmake-module.data'
    module_data.write_bytes(b'TEST_ONLY source module observation model, no real Linux assurance')
    ca = fixtures / 'CA.data'
    ca.write_bytes(b'TEST_ONLY SSL bytes; never used by a network request')
    bootstrap = {'files': {str(workflow): sha(workflow.read_bytes()), str(interpreter): sha(interpreter.read_bytes())}, 'review_sha256': 'b' * 64}
    os_release = fixtures / 'os-release.data'
    os_release.write_bytes(b'# TEST_ONLY OS-release fixture, not an observed Linux host\nID=ubuntu\nVERSION_ID="24.04"\n')
    bootstrap['files'][str(os_release)] = sha(os_release.read_bytes())
    modules = {'files': {str(module_data): sha(module_data.read_bytes())}, 'review_sha256': 'c' * 64}
    selection['bootstrap_selection_sha256'] = sha(encoded(bootstrap))
    selection['tool_module_review_sha256'] = sha(encoded(modules))
    tools = {}
    tool_paths = {}
    fixed = module._load_json((module.PACKAGE / 'build-contract/LIMITS-AND-RECIPE.json').read_bytes())['tools']['fixed_selectors']
    for index, name in enumerate(fixed + ['/usr/lib/gcc/TEST_ONLY/cc1', '/usr/lib/gcc/TEST_ONLY/cc1plus', '/usr/lib/gcc/TEST_ONLY/collect2', '/lib64/ld-linux-x86-64.so.2']):
        actual = fixtures / f'tool-{index:02}.data'
        actual.write_bytes(b'\x7fELFTEST_ONLY existing-tool identity ' + name.encode())
        tool_paths[name] = actual
        tools[name] = {'sha256': sha(actual.read_bytes()), 'resolved': str(actual), 'links': []}
    modules['files'].update({str(path): sha(path.read_bytes()) for path in tool_paths.values()})
    selection['tool_module_review_sha256'] = sha(encoded(modules))
    appointed = {'selection_sha256': sha(encoded(selection)), 'bootstrap': bootstrap, 'modules': modules, 'tools': tools,
                 'capacity': {'acceptance_sha256': 'd' * 64, 'minimum_free_bytes': 1},
                 'source_transport': {'selection_sha256': 'e' * 64, 'ssl_files': {str(ca): sha(ca.read_bytes())}, 'ca_file': str(ca)},
                 'run': {'id': 1, 'attempt': 1, 'runner_temp': str(tmp_path), 'workflow_sha256': selection['workflow_sha256']},
                 'linux_release': 'TEST_ONLY-6.8.0'}
    monkeypatch.setattr(module, '_APPOINTED_EXECUTION', appointed)
    monkeypatch.setattr(module, 'sys', SimpleNamespace(flags=SimpleNamespace(isolated=True, no_site=True), dont_write_bytecode=True, executable=str(interpreter), version_info=(3, 12, 0), version='3.12.0 TEST_ONLY model; no actual Linux bootstrap'))
    original_resolve, original_stat, original_lstat = Path.resolve, Path.stat, Path.lstat
    monkeypatch.setattr(Path, 'resolve', lambda self, *a, **k: os_release if str(self) == '/etc/os-release' else tool_paths[str(self)] if str(self) in tool_paths else original_resolve(self, *a, **k))
    monkeypatch.setattr(module.os, 'uname', lambda: module.os.uname_result(('Linux', 'TEST_ONLY', 'TEST_ONLY-6.8.0', 'TEST_ONLY', 'x86_64')))
    def modeled_stat(path, *args, **kwargs):
        result = original_stat(path, *args, **kwargs)
        if path in tool_paths.values():
            values = {key: getattr(result, key) for key in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')}
            return SimpleNamespace(**values, st_uid=0, st_mode=stat.S_IFREG | 0o555)
        return result
    monkeypatch.setattr(Path, 'stat', modeled_stat)
    monkeypatch.setattr(Path, 'lstat', lambda self, *a, **k: SimpleNamespace(st_uid=0, st_mode=stat.S_IFREG | 0o555) if str(self) in tool_paths else original_lstat(self, *a, **k))
    monkeypatch.setattr(module.os, 'statvfs', lambda *a: SimpleNamespace(f_bavail=2**30, f_frsize=4096))
    clock = [0.0]
    def monotonic():
        clock[0] += 0.02
        return clock[0]
    monkeypatch.setattr(module.time, 'monotonic', monotonic)
    calls, streams, children = [], {}, {}
    class Stream:
        def __init__(self, fd): self.fd = fd
        def fileno(self): return self.fd
        def close(self): pass
    class Selector:
        def __init__(self): self.keys = {}
        def register(self, stream, events, name): self.keys[stream.fd] = SimpleNamespace(fd=stream.fd, fileobj=stream, data=name)
        def unregister(self, stream): self.keys.pop(stream.fd)
        def select(self, timeout): return [(key, 1) for key in list(self.keys.values())]
        def close(self): pass
    def popen(argv, **kwargs):
        assert kwargs['start_new_session'] and kwargs['close_fds']
        assert kwargs['env'] == {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC', 'HOME': str(tmp_path / 'A-1-1/home'), 'TMPDIR': str(tmp_path / 'A-1-1/tmp'), 'CMAKE_BUILD_PARALLEL_LEVEL': '2'}
        calls.append(argv)
        stdout, stderr = b'GNU TEST_ONLY 1.0\n', b''
        if argv[0] == '/usr/bin/cmake' and argv[1] == '--version': stdout = b'cmake version 3.28.3\n'
        elif argv[-1] == '--internal-fetch': stdout = archive
        elif argv[0] == '/usr/bin/patch' and len(argv) > 2:
            apply_reviewed_patch_as_test_data(Path(kwargs['cwd']))
            stdout = b'patching file TEST_ONLY\n'
        elif argv[0] == '/usr/bin/cmake':
            build = Path(kwargs['cwd'])
            cache = ''.join(argument[2:].split('=', 1)[0] + ':UNINITIALIZED=' + argument[2:].split('=', 1)[1] + '\n' for argument in argv[4:])
            (build / 'CMakeCache.txt').write_text(cache)
            (build / 'compile_commands.json').write_bytes(b'[]\n')
        elif argv[0] == '/usr/bin/make' and len(argv) > 2:
            build = Path(kwargs['cwd'])
            (build / 'xpdf').mkdir()
            (build / 'xpdf/pdftotext').write_bytes(fake_binary())
            (build / 'TEST_ONLY.o').write_bytes(b'TEST_ONLY object bytes, never executed')
            (build / 'TEST_ONLY.a').write_bytes(b'TEST_ONLY archive bytes, never linked')
            stdout = b'/lib64/ld-linux-x86-64.so.2\n'
            if source_extra and 'instrumented-build' in str(build):
                (build.parent / 'instrumented-source/TEST_ONLY-extra').write_bytes(b'unaccepted source path')
        elif argv[1].startswith('-print-prog-name='): stdout = ('/usr/lib/gcc/TEST_ONLY/' + argv[1].split('=')[1] + '\n').encode()
        elif argv[1] == '-dumpmachine': stdout = b'x86_64-linux-gnu\n'
        elif argv[1] == '-dumpspecs': stdout = b'TEST_ONLY GCC specs; no actual compiler invocation\n'
        pid = 123 + len(calls)
        children[pid] = 256 if fail_stage and fail_stage in argv[0] and '--version' not in argv else 0
        out_fd, err_fd = 10000 + pid * 2, 10001 + pid * 2
        streams[out_fd], streams[err_fd] = io.BytesIO(stdout), io.BytesIO(stderr)
        return SimpleNamespace(pid=pid, stdout=Stream(out_fd), stderr=Stream(err_fd), returncode=None)
    original_read = module.os.read
    monkeypatch.setattr(module.os, 'read', lambda fd, maximum: streams[fd].read(maximum) if fd in streams else original_read(fd, maximum))
    monkeypatch.setattr(module.os, 'set_blocking', lambda *a: None)
    monkeypatch.setattr(module.subprocess, 'Popen', popen)
    monkeypatch.setattr(module.selectors, 'DefaultSelector', Selector)
    monkeypatch.setattr(module.os, 'waitid', lambda mode, pid, flags: SimpleNamespace(si_pid=pid))
    monkeypatch.setattr(module.os, 'waitpid', lambda pid, flags: (pid, children[pid]))
    def kill(pid, number):
        assert pid in children
        if number == 0: raise ProcessLookupError()
    monkeypatch.setattr(module.os, 'killpg', kill)
    return selection, tmp_path / 'A-1-1', calls


def retained_archive():
    supplied = os.environ.get('TWIN_XPDF_BUILD_TEST_ARCHIVE')
    if not supplied:
        pytest.skip('explicit data-only retained archive not supplied; no fetch or execution')
    raw = Path(supplied).read_bytes()
    assert len(raw) == 999317 and sha(raw) == '1c38f527c46caee0f712386d42a885b96a31ed9ce11904e872559859894d137e'
    return raw


def test_full_fixed_driver_and_checker_with_only_os_models(monkeypatch, tmp_path):
    selection, root, calls = whole_model(monkeypatch, tmp_path, retained_archive())
    result = module.build_linux_pair(selection, root)
    assert result['status'] == 'COMPLETE_BUILD_PAIR', result['first_failure']
    bundle = {path.relative_to(root / 'export').as_posix(): path.read_bytes() for path in (root / 'export').rglob('*') if path.is_file()}
    summary = module.check_build_bundle(bundle, sha(encoded(selection)))
    assert summary['build_complete'] and not summary['native_permission']
    assert [c[0] for c in calls if c[0] == '/usr/bin/make' and len(c) > 2] == ['/usr/bin/make', '/usr/bin/make']
    assert result['runtime_access_closure'] == 'UNESTABLISHED' and result['native_N01_N08'] == 'UNRUN'


def test_first_modeled_configure_failure_stops_before_any_build(monkeypatch, tmp_path):
    selection, root, calls = whole_model(monkeypatch, tmp_path, retained_archive(), fail_stage='cmake')
    result = module.build_linux_pair(selection, root)
    assert result['status'] == 'HELD'
    assert not any(argv[0] == '/usr/bin/make' and len(argv) > 2 for argv in calls)
    assert root.exists() and (root / 'FIRST-FAILURE.json').is_file()
    assert result['first_failure']['command_id'] == result['commands'][-1]['id']


def test_source_added_by_a_modeled_build_cannot_export_complete(monkeypatch, tmp_path):
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive(), source_extra=True)
    result = module.build_linux_pair(selection, root)
    assert result['status'] == 'HELD' and result['hold_codes'] == ['H_SOURCE_CONSERVATION']
    assert not (root / 'export/RESULT.json').exists()


@pytest.mark.parametrize('missing,code', [('bootstrap', 'H_BOOTSTRAP'), ('modules', 'H_PROBE_EXECUTION_UNESTABLISHED'), ('tools', 'H_TOOLS'), ('capacity', 'H_CAPACITY'), ('source_transport', 'H_SOURCE_TRANSPORT')])
def test_missing_actual_prerequisites_hold_before_a_child(monkeypatch, tmp_path, missing, code):
    selection, root, calls = whole_model(monkeypatch, tmp_path, retained_archive())
    module._APPOINTED_EXECUTION[missing] = None
    result = module.build_linux_pair(selection, root)
    assert result['status'] == 'HELD' and result['hold_codes'] == [code]
    assert calls == [] and not root.exists()


def reseal_complete(bundle, result):
    old = __import__('json').loads(bundle['FILES.json'])
    roles = {entry['path']: entry['role'] for entry in old['files']}
    payload = {key: value for key, value in bundle.items() if key not in {'FILES.json', 'RESULT.json'}}
    entries = [{'path': name, 'bytes': len(raw), 'sha256': sha(raw), 'role': roles.get(name, 'metadata')} for name, raw in sorted(payload.items())]
    payload['FILES.json'] = encoded({'schema': 'twin.xpdf-linux-build-files/v1', 'files': entries, 'logical_bytes': sum(e['bytes'] for e in entries), 'self_included': False})
    result['files_manifest_sha256'] = sha(payload['FILES.json'])
    payload['RESULT.json'] = encoded(result)
    return payload


def test_complete_data_mutations_cannot_self_repair_with_new_public_hashes(monkeypatch, tmp_path):
    import json
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive())
    original = module.build_linux_pair(selection, root)
    assert original['status'] == 'COMPLETE_BUILD_PAIR', original['first_failure']
    source = {path.relative_to(root / 'export').as_posix(): path.read_bytes() for path in (root / 'export').rglob('*') if path.is_file()}
    for mutation in ('late_query', 'missing_tool_bytes', 'stage_renewal', 'wrong_variant', 'missing_raw_cache', 'different_recipe', 'bad_config_guard', 'false_native', 'stream_lower_bound', 'wrong_binary'):
        bundle, result = dict(source), deepcopy(original)
        if mutation == 'late_query':
            command = deepcopy(result['commands'][0])
            command['id'] = 'TEST_ONLY late query'
            context = {'schema': 'twin.xpdf-build-custody-binding/v1', 'selection_sha256': result['selection_sha256'], 'command_id': command['id'], 'phase': command['phase'], 'argv': command['argv'], 'environment_sha256': command['environment_sha256'], 'command_started': command['started'], 'command_deadline': command['deadline'], 'checkpoint_started': result['clock']['started'], 'checkpoint_deadline': result['clock']['deadline'], 'leader_pid': command['custody']['leader_pid']}
            command['custody']['command_binding_sha256'] = sha(encoded(context).rstrip(b'\n'))
            result['commands'].append(command)
        elif mutation == 'missing_tool_bytes':
            # The selected CMake tool bytes occur in inputs/tools, not in loader candidates.
            tool = json.loads(bundle['TOOL-MANIFEST.json'])['/usr/bin/cmake']['sha256']
            for name in list(bundle):
                if sha(bundle[name]) == tool:
                    del bundle[name]
        elif mutation == 'stage_renewal':
            stages = json.loads(bundle['STAGES.json'])
            stages['pristine']['deadline'] += 1
            bundle['STAGES.json'] = encoded(stages)
        elif mutation == 'wrong_variant': result['variants'][1]['variant'] = 'pristine'
        elif mutation == 'missing_raw_cache': del bundle['pristine/build/CMakeCache.txt']
        elif mutation == 'different_recipe': result['variants'][1]['recipe_sha256'] = result['variants'][1]['configuration_manifest_sha256']
        elif mutation == 'bad_config_guard':
            config = json.loads(bundle['instrumented/CONFIGURATION.json'])
            config['logical_cache']['NO_FONTCONFIG']['value'] = 'OFF'
            bundle['instrumented/CONFIGURATION.json'] = encoded(config)
            result['variants'][1]['configuration_manifest_sha256'] = sha(bundle['instrumented/CONFIGURATION.json'])
        elif mutation == 'false_native': result['runtime_access_closure'] = 'COMPLETE'
        elif mutation == 'stream_lower_bound': result['commands'][0]['stdout']['observed_bytes_lower_bound'] = 0
        else: result['variants'][1]['binary_sha256'] = result['variants'][1]['source_manifest_sha256']
        with pytest.raises(ValueError, match='.'):
            module.check_build_bundle(reseal_complete(bundle, result), sha(encoded(selection)))
