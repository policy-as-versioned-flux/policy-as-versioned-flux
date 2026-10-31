"""TEST_ONLY review regressions; all target actions are explicit OS models."""
import json
import stat
from types import SimpleNamespace
import pytest
from test_xpdf_linux_discovery_model import whole_model
from test_xpdf_linux_discovery_model import reseal
from test_xpdf_linux_discovery import module


def test_wrong_tool_gnu_banner_stops_before_dependent_query(monkeypatch, tmp_path):
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path,
        outputs={2: b'GNU ld (GNU Binutils) 2.42\n'})
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA'
    assert len(calls) == 3
    assert result['commands'][-1]['stdout']['sha256'] == module._sha(b'GNU ld (GNU Binutils) 2.42\n')


def test_stable_empty_module_directory_is_part_of_complete_snapshot(monkeypatch, tmp_path):
    selected, root, calls, _, _, mapped = whole_model(monkeypatch, tmp_path)
    parent = mapped('/usr/share/cmake-3.28/Modules')
    parent.chmod(0o755)
    (parent / 'TEST_ONLY-empty').mkdir(mode=0o555)
    parent.chmod(0o555)
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'COMPLETE_DATA', result['faults']
    assert len(calls) == 15
    assert any(item['path'].endswith('/TEST_ONLY-empty') for item in result['directory_snapshots'])
    bundle = {path.relative_to(root / 'export').as_posix(): path.read_bytes() for path in (root / 'export').rglob('*') if path.is_file()}
    assert module.check_discovery_bundle(bundle, result['selection_sha256'])['inventory_state'] == 'COMPLETE_DATA'


def test_clock_before_original_parent_start_refuses_before_acquisition(monkeypatch, tmp_path):
    selected, root, calls, clock, _, _ = whole_model(monkeypatch, tmp_path)
    clock.now = -2
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'NOT_STARTED'
    assert result['original_started'] == 0 and result['entered'] is None
    assert calls == [] and not root.exists()
    assert result['faults'][0]['at'] < result['original_started']


@pytest.mark.parametrize('index,raw', [
    (1, b'GNU Make 04.3\n'), (2, b'gcc (Clang) 13.3.0\n'),
    (2, b'gcc (GNU) 13.3.0\nGNU Make 4.3\n'),
    (2, b'gcc (GNU) 13.3.0\nNOT A GNU TOOL\n'),
    (3, b'g++ (GNU) 13.3.0\ng++ (GNU) 13.3.0\n'),
    (4, b'GNU ld (GNU Binutils) 2.42\n'), (5, b'GNU ld (GNU Binutils) 2.42\n'),
    (6, b'GNU Make 4.3\n'), (7, b'GNU ld (GNU Binutils) 2.42\n'),
    (8, b'GNU ld (GNU Binutils) 2.42\n'), (9, b'GNU ld (GNU Binutils) 2.42\n'),
])
def test_unsupported_version_role_or_whole_data_stops_fixed_prefix(monkeypatch, tmp_path, index, raw):
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path, outputs={index: raw})
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA' and len(calls) == index + 1
    query = result['commands'][-1]
    assert query['stdout']['sha256'] == module._sha(raw)
    assert (root / 'export' / f'journal/{index:03}-stdout.log').read_bytes() == raw


def test_ubuntu_compiler_and_supported_notice_syntax_is_data_only(monkeypatch, tmp_path):
    notice = (b'Copyright (C) 2023 Free Software Foundation, Inc.\n'
        b'This is free software; see the source for copying conditions.  There is NO\n'
        b'warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\n')
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path, outputs={
        2: b'gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0\n' + notice,
        3: b'g++ (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0\n' + notice})
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'COMPLETE_DATA' and len(calls) == 15
    assert result['build_complete'] is False and result['native_execution'] is False


@pytest.mark.parametrize('mutation', ['missing_empty', 'orphan', 'unknown_child', 'cycle', 'unsafe_kind', 'unlisted_file', 'unrooted_nonempty', 'conflicting_kind'])
def test_empty_module_graph_rejects_missing_or_unrooted_rehashed_data(monkeypatch, tmp_path, mutation):
    selected, root, _, _, _, mapped = whole_model(monkeypatch, tmp_path)
    parent = mapped('/usr/share/cmake-3.28/Modules')
    parent.chmod(0o755)
    (parent / 'TEST_ONLY-empty').mkdir(mode=0o555)
    parent.chmod(0o555)
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'COMPLETE_DATA', result['faults']
    bundle = {p.relative_to(root / 'export').as_posix(): p.read_bytes() for p in (root / 'export').rglob('*') if p.is_file()}
    empty = next(item for item in result['directory_snapshots'] if item['path'].endswith('/TEST_ONLY-empty'))
    artifact = next(name for name, raw in bundle.items() if name.startswith('directories/') and json.loads(raw)['path'] == empty['path'])
    data = json.loads(bundle[artifact])
    if mutation in ('unlisted_file', 'unrooted_nonempty'):
        directory = next(item for item in result['directory_snapshots'] if item['path'] == result['module_root'])
        parent_artifact = next(name for name, raw in bundle.items() if name.startswith('directories/') and json.loads(raw)['path'] == directory['path'])
        parent_data = json.loads(bundle[parent_artifact])
        omitted = 'FindTEST_ONLY.cmake' if mutation == 'unlisted_file' else 'subdir'
        parent_data['before_names'].remove(omitted)
        parent_data['after_names'].remove(omitted)
        directory['child_names_sha256'] = module._sha(module._json(parent_data['before_names']))
        bundle[parent_artifact] = module._json(parent_data)
    elif mutation == 'conflicting_kind':
        from copy import deepcopy
        directory = deepcopy(empty)
        directory['path'] = result['modules'][0]['path']
        result['directory_snapshots'].append(directory)
        result['directory_snapshots'].sort(key=lambda item: item['path'])
        bundle['directories/TEST_ONLY-conflicting.json'] = module._json(dict(path=directory['path'], before_names=[], after_names=[]))
    elif mutation == 'missing_empty':
        result['directory_snapshots'].remove(empty)
        del bundle[artifact]
    elif mutation == 'orphan': empty['path'] = data['path'] = empty['path'] + '-unrooted'
    elif mutation == 'unsafe_kind':
        empty['before'][2] = empty['after'][2] = stat.S_IFLNK | 0o777
    else:
        data['before_names'] = data['after_names'] = ['..' if mutation == 'cycle' else 'TEST_ONLY-missing-child']
        empty['child_names_sha256'] = module._sha(module._json(data['before_names']))
    if mutation != 'missing_empty': bundle[artifact] = module._json(data)
    with pytest.raises(ValueError): module.check_discovery_bundle(reseal(bundle, result), result['selection_sha256'])


@pytest.mark.parametrize('at,accepted', [(10, True), (9.99999, False), (None, False)])
def test_original_start_boundary_has_no_public_clock_reset(monkeypatch, tmp_path, at, accepted):
    from test_xpdf_linux_discovery import selection
    result = module._new_result(selection())
    result.update(original_started=10, deadline=70)
    monkeypatch.setattr(module, 'time', SimpleNamespace(monotonic=lambda: at))
    collection = module._Collection(result, tmp_path)
    if accepted:
        collection.add('TEST_ONLY.json', b'{}', 'metadata')
        assert collection.payload['TEST_ONLY.json'][0] == b'{}'
    else:
        with pytest.raises(module.DiscoveryHold): collection.add('TEST_ONLY.json', b'{}', 'metadata')
        assert collection.payload == {}


def test_full_original_clock_rejection_keeps_exact_invalid_observation(monkeypatch, tmp_path):
    selected, root, calls, clock, _, _ = whole_model(monkeypatch, tmp_path)
    module._DISCOVERY_APPOINTMENT.update(original_started=10, deadline=70)
    clock.now = 9
    result = module.discover_linux_tools(selected, root)
    assert result['faults'][0]['at'] == pytest.approx(9.0001)
    assert result['finished'] == pytest.approx(9.0002)
    assert result['original_started'] == 10 and result['entered'] is None
    assert not root.exists() and calls == []


@pytest.mark.parametrize('operation', ['read', 'write'])
@pytest.mark.parametrize('first', ['body_interrupt', 'close_error'])
def test_owned_file_closes_once_preserve_first_and_bounded_secondary(monkeypatch, tmp_path, operation, first):
    from test_xpdf_linux_discovery import selection
    original = KeyboardInterrupt('TEST_ONLY first body interruption')
    close_error = OSError('TEST_ONLY first close uncertainty')
    later = SystemExit('TEST_ONLY secondary parent close uncertainty')
    calls = []
    info = SimpleNamespace(st_dev=1, st_ino=1, st_mode=stat.S_IFREG | 0o444, st_uid=0, st_gid=0,
        st_size=1, st_mtime_ns=1, st_ctime_ns=1, st_nlink=1)
    def read(fd, count):
        if first == 'body_interrupt': raise original
        return b'x'
    def write(fd, raw):
        if first == 'body_interrupt': raise original
        return len(raw)
    def close(fd):
        calls.append(fd)
        raise close_error if fd == 11 else later
    host = SimpleNamespace(O_RDONLY=0, O_WRONLY=1, O_CREAT=2, O_EXCL=4, O_NOFOLLOW=8,
        open=lambda *args, **kwargs: 11, close=close, fstat=lambda fd: info,
        read=read, write=write, stat=lambda *args, **kwargs: info)
    monkeypatch.setattr(module, 'os', host)
    monkeypatch.setattr(module, '_directory_fd', lambda path: 10)
    monkeypatch.setattr(module, 'time', SimpleNamespace(monotonic=lambda: 1))
    result = module._new_result(selection())
    result.update(original_started=0, deadline=60)
    expected = original if first == 'body_interrupt' else close_error
    # A successful one-byte read reaches EOF before the first close fails.
    if operation == 'read' and first == 'close_error':
        chunks = iter([b'x', b''])
        host.read = lambda *args: next(chunks)
    with pytest.raises(type(expected)) as caught:
        if operation == 'read': module._Collection(result, tmp_path).read('/TEST_ONLY/file', 1)
        else: module._write(tmp_path, 'TEST_ONLY.bin', b'x')
    assert caught.value is expected and calls == [11, 10]
    module._fault(result, 'snapshot' if operation == 'read' else 'export', 'TEST_ONLY', caught.value, 1)
    assert result['faults'][0]['error_type'] == type(expected).__name__
    assert result['faults'][-1]['error_type'] == 'SystemExit' and result['faults'][-1]['at'] is None
    assert 'unestablished' in result['faults'][-1]['message']
    assert result['custody']['known_terminal'] is False


def test_collector_retains_original_file_cancellation_before_close_uncertainty(monkeypatch, tmp_path):
    selected, root, calls, _, host, _ = whole_model(monkeypatch, tmp_path)
    original = KeyboardInterrupt('TEST_ONLY bootstrap read first')
    read, close = host.read, host.close
    failed = []
    def interrupted(fd, count):
        if host.descriptors.get(fd) == '/usr/bin/python3.12':
            failed.append(fd)
            raise original
        return read(fd, count)
    def uncertain(fd):
        selected_descriptor = fd in failed and host.descriptors.get(fd) == '/usr/bin/python3.12'
        close(fd)  # Own fixture descriptor disposal; the modeled result remains unknown.
        if selected_descriptor: raise OSError('TEST_ONLY modeled close uncertainty')
    monkeypatch.setattr(host, 'read', interrupted)
    monkeypatch.setattr(host, 'close', uncertain)
    with pytest.raises(KeyboardInterrupt) as caught: module.discover_linux_tools(selected, root)
    assert caught.value is original and calls == [] and root.exists()
    result = json.loads((root / 'export/RESULT.json').read_bytes())
    assert result['inventory_state'] == 'PARTIAL_DATA'
    assert result['faults'][0]['error_type'] == 'KeyboardInterrupt'
    assert result['faults'][1]['error_type'] == 'OSError' and result['faults'][1]['at'] is None
    assert result['custody']['known_terminal'] is False
