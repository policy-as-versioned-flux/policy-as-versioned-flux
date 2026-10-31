"""TEST_ONLY whole collector using explicit filesystem/process/clock OS models."""
import io
import json
import os
from pathlib import Path
import stat
from types import SimpleNamespace
import pytest

from test_xpdf_linux_discovery import module, selection


def whole_model(monkeypatch, tmp_path, *, outputs=None, raw_waits=None, query_delay=0):
    real_os = os
    virtual = tmp_path / 'TEST_ONLY-virtual-host'
    virtual.mkdir()
    def mapped(name):
        name = str(name)
        return virtual / name.lstrip('/') if name == '/' or name.startswith(('/usr/', '/usr', '/bin/', '/bin')) else Path(name)
    def data(name, raw):
        path = mapped(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod(0o555)
    profile = json.loads((module.PACKAGE / 'discovery-contract/QUERY-PROFILE.json').read_bytes())
    for name in profile['selectors']:
        data(name, b'\x7fELFTEST_ONLY never executed ' + name.encode())
    for name in ['cc1', 'cc1plus', 'collect2']:
        data('/usr/lib/gcc/x86_64-linux-gnu/13/' + name, b'\x7fELFTEST_ONLY DATA-only internal ' + name.encode())
    data('/usr/bin/python3.12', b'\x7fELFTEST_ONLY never executed interpreter')
    data('/usr/lib/python3.12/os.py', b'# TEST_ONLY already-loaded candidate DATA\n')
    data('/usr/share/cmake-3.28/Modules/FindTEST_ONLY.cmake', b'# TEST_ONLY never execute CMake\n')
    data('/usr/share/cmake-3.28/Modules/subdir/TEST_ONLY.cmake', b'# TEST_ONLY nested candidate DATA\n')
    for path in virtual.rglob('*'):
        if path.is_dir():
            path.chmod(0o555)
    virtual.chmod(0o555)

    descriptors, streams, children, calls = {}, {}, {}, []
    class OS:
        def __getattr__(self, name): return getattr(real_os, name)
        def logical(self, path, dir_fd=None):
            value = str(path)
            return os.path.normpath(os.path.join(descriptors[dir_fd], value)) if dir_fd is not None and not value.startswith('/') else value
        def info(self, info, logical):
            if mapped(logical).is_relative_to(virtual):
                values = {name: getattr(info, name) for name in ('st_dev', 'st_ino', 'st_mode', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_nlink')}
                return SimpleNamespace(**values, st_uid=0, st_gid=0)
            return info
        def open(self, path, flags, mode=0o777, dir_fd=None):
            if dir_fd is not None and dir_fd not in descriptors:
                return real_os.open(path, flags, mode, dir_fd=dir_fd)
            logical = self.logical(path, dir_fd)
            fd = real_os.open(mapped(logical), flags, mode)
            descriptors[fd] = logical
            return fd
        def close(self, fd):
            descriptors.pop(fd, None)
            real_os.close(fd)
        def fstat(self, fd): return self.info(real_os.fstat(fd), descriptors[fd]) if fd in descriptors else real_os.fstat(fd)
        def lstat(self, path): return self.info(real_os.lstat(mapped(path)), str(path))
        def stat(self, path, dir_fd=None, follow_symlinks=True):
            if dir_fd is not None and dir_fd not in descriptors:
                return real_os.stat(path, dir_fd=dir_fd, follow_symlinks=follow_symlinks)
            logical = self.logical(path, dir_fd)
            return self.info(real_os.stat(mapped(logical), follow_symlinks=follow_symlinks), logical)
        def readlink(self, path): return real_os.readlink(mapped(path))
        def scandir(self, path): return real_os.scandir(path if isinstance(path, int) else mapped(path))
        def mkdir(self, path, mode=0o777, dir_fd=None): return real_os.mkdir(mapped(self.logical(path, dir_fd)), mode)
        def read(self, fd, maximum): return streams[fd].read(maximum) if fd in streams else real_os.read(fd, maximum)
        def set_blocking(self, *args): pass
        def waitid(self, mode, pid, flags): return SimpleNamespace(si_pid=pid)
        def waitpid(self, pid, flags): return pid, children[pid]
        def killpg(self, pid, number):
            assert pid in children
            if number == 0: raise ProcessLookupError()
        def statvfs(self, path): return SimpleNamespace(f_bavail=2**30, f_frsize=4096)
        def uname(self): return real_os.uname_result(('Linux', 'TEST_ONLY', 'TEST_ONLY-6.8', 'TEST_ONLY', 'x86_64'))
    host = OS()
    host.descriptors = descriptors
    class Clock:
        now = 1.0
        def monotonic(self):
            self.now += 0.0001
            return self.now
    clock = Clock()
    class Stream:
        def __init__(self, fd): self.fd = fd
        def fileno(self): return self.fd
        def close(self): pass
    class Selector:
        def __init__(self): self.keys = {}
        def register(self, stream, events, name): self.keys[stream.fd] = SimpleNamespace(fd=stream.fd, fileobj=stream, data=name)
        def unregister(self, stream): self.keys.pop(stream.fd)
        def select(self, timeout):
            clock.now += timeout
            return [(key, 1) for key in list(self.keys.values())]
        def close(self): pass
    def popen(argv, **kwargs):
        assert argv == profile['ordered_query_argv'][len(calls)]
        assert kwargs['stdin'] == module._build.subprocess.DEVNULL and kwargs['close_fds'] and kwargs['start_new_session']
        calls.append(list(argv))
        output = b'GNU TEST_ONLY existing tool version DATA\n'
        if argv == ['/usr/bin/cmake', '--version']: output = b'cmake version 3.28.3\n'
        elif argv[-1] == '-dumpmachine': output = b'x86_64-linux-gnu\n'
        elif argv[-1] == '-dumpspecs': output = b'TEST_ONLY opaque GCC specs DATA\n'
        elif argv[-1].startswith('-print-prog-name='): output = ('/usr/lib/gcc/x86_64-linux-gnu/13/' + argv[-1].split('=')[1] + '\n').encode()
        output = (outputs or {}).get(len(calls) - 1, output)
        clock.now += query_delay
        pid = 100 + len(calls)
        children[pid] = (raw_waits or {}).get(len(calls) - 1, 0)
        out_fd, err_fd = 100000 + pid * 2, 100001 + pid * 2
        streams[out_fd], streams[err_fd] = io.BytesIO(output), io.BytesIO(b'')
        return SimpleNamespace(pid=pid, stdout=Stream(out_fd), stderr=Stream(err_fd), returncode=None)

    monkeypatch.setattr(module, 'os', host)
    monkeypatch.setattr(module._build, 'os', host)
    monkeypatch.setattr(module, 'time', clock)
    monkeypatch.setattr(module._build, 'time', clock)
    monkeypatch.setattr(module._build.subprocess, 'Popen', popen)
    monkeypatch.setattr(module._build.selectors, 'DefaultSelector', Selector)
    monkeypatch.setattr(module, 'sys', SimpleNamespace(executable='/usr/bin/python3.12', version_info=(3, 12, 8),
        flags=SimpleNamespace(isolated=1, no_site=1), dont_write_bytecode=True,
        modules={'TEST_ONLY_loaded': SimpleNamespace(__file__='/usr/lib/python3.12/os.py')}))
    selected = selection()
    selected['driver_sha256'] = module._sha(Path(module.__file__).read_bytes())
    workflow = tmp_path / 'TEST_ONLY-workflow.data'
    workflow.write_bytes(b'TEST_ONLY source data, no workflow execution')
    selected['workflow_sha256'] = module._sha(workflow.read_bytes())
    bootstrap_paths = ['/usr/bin/python3.12', '/usr/lib/python3.12/os.py']
    bootstrap = dict(schema='twin.xpdf-discovery-parent-bootstrap/v1', interpreter=bootstrap_paths[0], roots=['/usr/bin', '/usr/lib/python3.12'],
        loaded_files=bootstrap_paths[1:], files={path: module._sha(mapped(path).read_bytes()) for path in bootstrap_paths},
        startup_provenance_sha256='a' * 64, writer_control_sha256='b' * 64)
    selected['bootstrap_selection_sha256'] = module._sha(module._json(bootstrap))
    def candidate(path):
        info = host.lstat(path)
        identity = [getattr(info, 'st_' + key) for key in ('dev', 'ino', 'mode', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns', 'nlink')]
        raw = mapped(path).read_bytes()
        return dict(role='selector', path=path, resolved=path, links=[], before=identity, after=list(identity), bytes=len(raw), sha256=module._sha(raw))
    root = tmp_path / 'D-1-1'
    closure = [Path(module.__file__), module.PACKAGE / 'build_linux_pair.py', module.PACKAGE / 'prepare_source.py', workflow]
    closure += [module.PACKAGE / 'build-contract' / name for name in module._build._CONTRACT_PINS]
    closure += [module.PACKAGE / 'discovery-contract' / name for name in module._PINS]
    appointment = dict(selection_sha256=module._sha(module._json(selected)), source_commit=selected['source_commit'], source_tree=selected['source_tree'],
        workflow_source=str(workflow), source_files={str(path): module._sha(path.read_bytes()) for path in closure},
        run_identity=dict(repository='TEST_ONLY/repo', workflow_path='.github/workflows/TEST_ONLY.yml', run_id=1, run_attempt=1, job='tiny',
            row=selected['expected_row'], source_commit=selected['source_commit']), owned_parent=str(root), original_started=0, a_deadline=1800, deadline=60,
        bootstrap_selection=bootstrap, query_acceptance=dict(selectors={path: candidate(path) for path in profile['selectors']}, review_sha256='c' * 64, writer_control_sha256='d' * 64),
        capacity=dict(review_sha256='e' * 64, minimum_free_bytes=1))
    monkeypatch.setattr(module, '_DISCOVERY_APPOINTMENT', appointment)
    return selected, root, calls, clock, host, mapped


def test_complete_discovery_body_and_pure_checker_with_only_os_models(monkeypatch, tmp_path):
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path)
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'COMPLETE_DATA', result['faults']
    bundle = {p.relative_to(root / 'export').as_posix(): p.read_bytes() for p in (root / 'export').rglob('*') if p.is_file()}
    assert module.check_discovery_bundle(bundle, module._sha(module._json(selected))) == dict(inventory_state='COMPLETE_DATA',
        build_hold='H_PROBE_EXECUTION_UNESTABLISHED', build_complete=False, native_execution=False)
    assert len(calls) == 15 and all(argv[0] != '/bin/sh' for argv in calls)
    assert [Path(c['path']).name for c in result['gcc_internals']] == ['cc1', 'cc1plus', 'collect2']


def test_late_supervisor_clock_cannot_consume_the_terminal_reserve(monkeypatch, tmp_path):
    selected, root, calls, clock, _, _ = whole_model(monkeypatch, tmp_path)
    class SchedulingGap:
        fired = False
        def monotonic(self):
            if not self.fired:
                clock.now = 46.0  # Shared time advances after outer admission, before actual dispatch.
                self.fired = True
            return clock.monotonic()
    monkeypatch.setattr(module._build, 'time', SchedulingGap())
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA'
    assert calls == [], 'the actual five-second admission must preserve ten seconds before creating a child'
    query = result['commands'][0]
    assert query['deadline'] is None and query['command_binding_sha256'] is None
    assert query['custody']['command_binding_sha256'] is None and query['custody']['leader_pid'] is None
    bundle = {p.relative_to(root / 'export').as_posix(): p.read_bytes() for p in (root / 'export').rglob('*') if p.is_file()}
    assert module.check_discovery_bundle(bundle, result['selection_sha256'])['inventory_state'] == 'PARTIAL_DATA'


def complete_bundle(monkeypatch, tmp_path):
    selected, root, calls, clock, host, mapped = whole_model(monkeypatch, tmp_path)
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'COMPLETE_DATA', result['faults']
    bundle = {p.relative_to(root / 'export').as_posix(): p.read_bytes() for p in (root / 'export').rglob('*') if p.is_file()}
    return selected, result, bundle


def reseal(bundle, result, role_change=None):
    roles = {entry['path']: entry['role'] for entry in json.loads(bundle['FILES.json'])['entries']}
    if role_change is not None:
        roles[role_change] = 'TEST_ONLY-wrong-role'
    output = {name: raw for name, raw in bundle.items() if name not in ('RESULT.json', 'FILES.json')}
    entries = [dict(path=name, sha256=module._sha(raw), bytes=len(raw), role=roles.get(name, 'metadata')) for name, raw in sorted(output.items())]
    output['FILES.json'] = module._json(dict(schema='twin.xpdf-linux-discovery-files/v1', entries=entries))
    result['files_manifest_sha256'] = module._sha(output['FILES.json'])
    output['RESULT.json'] = module._json(result)
    return output


@pytest.mark.parametrize('mutation', ['unsafe_route', 'artifact_role', 'partial_run_extra', 'partial_bootstrap_literal',
    'partial_directory_extra', 'partial_future_gcc', 'partial_unsupported_then_later', 'partial_module_fallback'])
def test_closed_data_and_partial_facts_do_not_bypass_association_checks(monkeypatch, tmp_path, mutation):
    selected, result, bundle = complete_bundle(monkeypatch, tmp_path)
    role_change = None
    if mutation.startswith('partial_'):
        result['inventory_state'] = 'PARTIAL_DATA'
        result['custody']['known_terminal'] = False
    if mutation == 'unsafe_route':
        item = result['tools'][0]
        info = list(item['before'])
        info[2] = stat.S_IFLNK | 0o777
        item['links'] = [dict(path=item['path'], target='/TEST_ONLY/unselected-target', identity=info)]
        parent = json.loads(bundle['PARENT.json'])
        parent['query_acceptance']['selectors'][item['path']] = item
        bundle['PARENT.json'] = module._json(parent)
    elif mutation == 'artifact_role':
        role_change = next(entry['path'] for entry in json.loads(bundle['FILES.json'])['entries'] if entry['role'] == 'cmake-module')
    elif mutation == 'partial_run_extra': result['run_identity']['approved'] = True
    elif mutation == 'partial_bootstrap_literal': result['bootstrap'] = 'not-a-digest'
    elif mutation == 'partial_directory_extra': result['directory_snapshots'][0]['approved'] = True
    elif mutation == 'partial_future_gcc': result['commands'] = result['commands'][:1]
    elif mutation == 'partial_module_fallback': result['module_root'] = '/TEST_ONLY/fallback/Modules'
    elif mutation == 'partial_unsupported_then_later':
        output = b'cmake version 0.0.0\n'
        q = result['commands'][0]
        q['stdout'].update(sha256=module._sha(output), bytes=len(output), observed_bytes_lower_bound=len(output))
        bundle['journal/000-stdout.log'] = output
    with pytest.raises(ValueError):
        module.check_discovery_bundle(reseal(bundle, result, role_change), module._sha(module._json(selected)))


@pytest.mark.parametrize('reserve,started,launched', [(0, 46.0, True), (10, 45.0, True), (10, 45.00001, False)])
def test_actual_supervisor_default_and_fixed_reserve_boundaries(monkeypatch, tmp_path, reserve, started, launched):
    selected, root, calls, clock, _, _ = whole_model(monkeypatch, tmp_path)
    class BoundaryClock:
        first = True
        def monotonic(self):
            if self.first:
                self.first = False
                clock.now = started
                return started
            return clock.monotonic()
    monkeypatch.setattr(module._build, 'time', BoundaryClock())
    environment = module._build._fresh_environment(root)
    context = dict(selection_sha256=module._sha(module._json(selected)), clock=dict(started=0, deadline=60), commands=[],
        environment_manifest_sha256=module._sha(module._build._json(environment)))
    if launched:
        command = module._build._supervise(context, 'bootstrap-input-tools', ['/usr/bin/cmake', '--version'], root, environment, 5, {}, terminal_reserve=reserve)
        assert command['started'] == started and command['deadline'] == started + 5
        assert len(calls) == 1
    else:
        with pytest.raises(module._build.BuildHold):
            module._build._supervise(context, 'bootstrap-input-tools', ['/usr/bin/cmake', '--version'], root, environment, 5, {}, terminal_reserve=reserve)
        assert calls == []
        assert context['commands'][0]['started'] == started and context['commands'][0]['deadline'] is None


@pytest.mark.parametrize('reserve', [True, False, 1, 9, 10.0, None, '10'])
def test_invalid_private_reserve_never_reaches_clock_or_child(monkeypatch, tmp_path, reserve):
    with pytest.raises(ValueError):
        module._build._supervise({}, 'bootstrap-input-tools', [], tmp_path, {}, 5, {}, terminal_reserve=reserve)


def test_impossible_raw_terminal_status_stops_before_another_query(monkeypatch, tmp_path):
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path, raw_waits={0: 128})
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA'
    assert len(calls) == 1
    assert result['commands'][0]['raw_wait_status'] == 128
    assert (root / 'FIRST-FAILURE.json').exists()


@pytest.mark.parametrize('index,output', [(0, b'cmake version 03.28.3\n'), (0, b'cmake version 3.23.0\n'),
    (0, b'cmake version 3.28.3\ncmake version 3.29.0\n'), (1, b'TEST_ONLY unsupported tool\n'),
    (12, b'/TEST_ONLY/unselected/cc1\n'), (12, b'/usr/lib/gcc/x86_64-linux-gnu/013/cc1\n')])
def test_unsupported_raw_reply_stops_without_search_or_reply_execution(monkeypatch, tmp_path, index, output):
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path, outputs={index: output})
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA'
    assert len(calls) == index + 1
    assert all(argv[0] not in ('/bin/sh', '/TEST_ONLY/unselected/cc1') for argv in calls)
    assert result['commands'][-1]['stdout']['sha256'] == module._sha(output)


def test_slow_queries_preserve_a_successful_prefix_without_renewed_time(monkeypatch, tmp_path):
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path, query_delay=2.5)
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA' and 0 < len(calls) < 15
    assert result['original_started'] == 0 and result['deadline'] == 60
    assert all(q['deadline'] == q['started'] + 5 and q['deadline'] + 10 <= 60 for q in result['commands'])
    bundle = {p.relative_to(root / 'export').as_posix(): p.read_bytes() for p in (root / 'export').rglob('*') if p.is_file()}
    assert result['files_manifest_sha256'] == module._sha(bundle['FILES.json'])
    assert json.loads(bundle['RESULT.json']) == result and result['faults']
    assert module.check_discovery_bundle(bundle, result['selection_sha256'])['inventory_state'] == 'PARTIAL_DATA'


def test_late_parent_entry_keeps_actual_clock_and_creates_nothing(monkeypatch, tmp_path):
    selected, root, calls, clock, _, _ = whole_model(monkeypatch, tmp_path)
    clock.now = 61
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'NOT_STARTED' and result['entered'] is None
    assert result['original_started'] == 0 and result['deadline'] == 60 and result['finished'] > 61
    assert calls == [] and not root.exists()


def test_source_closure_drift_cannot_launch_queries(monkeypatch, tmp_path):
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path)
    module._DISCOVERY_APPOINTMENT['source_files'][str(module.PACKAGE / 'build_linux_pair.py')] = '0' * 64
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'NOT_STARTED' and calls == [] and not root.exists()


@pytest.mark.parametrize('unsafe', ['selector_owner', 'module_symlink', 'bootstrap_startup'])
def test_unestablished_candidate_or_startup_facts_hold(monkeypatch, tmp_path, unsafe):
    selected, root, calls, _, host, mapped = whole_model(monkeypatch, tmp_path)
    if unsafe == 'selector_owner':
        lstat = host.lstat
        def wrong_owner(path):
            info = lstat(path)
            if str(path) == '/usr/bin/cmake':
                info.st_uid = 501
            return info
        monkeypatch.setattr(host, 'lstat', wrong_owner)
    elif unsafe == 'module_symlink':
        parent = mapped('/usr/share/cmake-3.28/Modules')
        parent.chmod(0o755)
        (parent / 'TEST_ONLY-link.cmake').symlink_to('FindTEST_ONLY.cmake')
    else:
        module.sys.flags.no_site = 0
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA'
    assert len(calls) == (1 if unsafe == 'module_symlink' else 0)
    bundle = {p.relative_to(root / 'export').as_posix(): p.read_bytes() for p in (root / 'export').rglob('*') if p.is_file()}
    assert json.loads(bundle['RESULT.json']) == result and result['faults']
    assert module.check_discovery_bundle(bundle, result['selection_sha256'])['inventory_state'] == 'PARTIAL_DATA'


def test_known_terminal_partial_inventory_retains_its_actual_data_bundle(monkeypatch, tmp_path):
    output = b'cmake version 3.23.0\n'
    selected, root, calls, _, _, _ = whole_model(monkeypatch, tmp_path, outputs={0: output})
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA' and len(calls) == 1
    bundle = {p.relative_to(root / 'export').as_posix(): p.read_bytes() for p in (root / 'export').rglob('*') if p.is_file()}
    assert bundle['journal/000-stdout.log'] == output
    summary = module.check_discovery_bundle(bundle, module._sha(module._json(selected)))
    assert summary['inventory_state'] == 'PARTIAL_DATA' and summary['build_complete'] is False
    assert result['files_manifest_sha256'] == module._sha(bundle['FILES.json'])
    assert len(result['tools']) == 11 and result['bootstrap'] is not None


@pytest.mark.parametrize('mutation', ['outer_binding', 'context_clock', 'environment_newline', 'equal_ordinal', 'signal_after_reap', 'omitted_module', 'unknown_clock', 'file_changed'])
def test_independent_checker_rejects_rehashed_context_custody_and_snapshot_mutations(monkeypatch, tmp_path, mutation):
    selected, result, bundle = complete_bundle(monkeypatch, tmp_path)
    query = result['commands'][0]
    if mutation == 'outer_binding': query['command_binding_sha256'] = '0' * 64
    elif mutation == 'context_clock': result['original_started'] = -1
    elif mutation == 'environment_newline': bundle['ENVIRONMENT.json'] = bundle['ENVIRONMENT.json'].rstrip(b'\n')
    elif mutation == 'unknown_clock': query['started'] = None
    elif mutation == 'omitted_module': result['modules'].pop()
    elif mutation == 'file_changed': result['tools'][0]['after'][5] += 1
    elif mutation == 'equal_ordinal':
        observations = query['custody']['observations']
        observations[-1]['ordinal'] = observations[0]['ordinal']
    else:
        observations = query['custody']['observations']
        signal = next(event for event in observations if event['kind'] == 'signal-attempt')
        observations.remove(signal)
        reaping = next(i for i, event in enumerate(observations) if event['kind'] == 'reaping-start')
        observations.insert(reaping + 1, signal)
        at = query['custody']['cleanup_started']
        for i, event in enumerate(observations): event.update(ordinal=i, at=at)
        query['custody']['cleanup_ended'] = at
        query['custody']['signals'] = [dict(event['detail'], at=at) for event in observations if event['kind'] == 'signal-attempt']
    with pytest.raises(ValueError):
        module.check_discovery_bundle(reseal(bundle, result), module._sha(module._json(selected)))


def test_interrupted_query_stops_all_later_actions_and_preserves_first_fault(monkeypatch, tmp_path):
    selected, root, calls, _, host, _ = whole_model(monkeypatch, tmp_path)
    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt('TEST_ONLY original cancellation')
    monkeypatch.setattr(module._build.subprocess, 'Popen', interrupted)
    with pytest.raises(KeyboardInterrupt, match='TEST_ONLY original cancellation'):
        module.discover_linux_tools(selected, root)
    assert calls == [] and root.exists()
    failure = json.loads((root / 'FIRST-FAILURE.json').read_bytes())
    assert failure['faults'][0]['error_type'] == 'KeyboardInterrupt'
    assert failure['commands'][0]['custody']['reservation'] == 'UNESTABLISHED'
    assert failure['build_complete'] is False and failure['native_execution'] is False


def test_capacity_and_metadata_limits_refuse_without_acquisition(monkeypatch, tmp_path):
    result = module._new_result(selection())
    result['deadline'] = 60
    monkeypatch.setattr(module, 'time', SimpleNamespace(monotonic=lambda: 1))
    collection = module._Collection(result, tmp_path)
    with pytest.raises(module.DiscoveryHold): collection.room(module.DATA_LIMIT + 1)
    with pytest.raises(module.DiscoveryHold): collection.room(files=8191)
    with pytest.raises(module.DiscoveryHold): collection.add('metadata.json', b'x' * (module.MAX_METADATA + 1), 'metadata')
    assert collection.payload == {}


def test_directory_enumeration_stops_at_its_finite_input_bound(monkeypatch, tmp_path):
    _, root, _, _, host, _ = whole_model(monkeypatch, tmp_path)
    result = module._new_result(selection())
    result['deadline'] = 60
    collection = module._Collection(result, root)
    consumed = []
    class Entries:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def __iter__(self):
            for index in range(9000):
                consumed.append(index)
                yield SimpleNamespace(name=f'TEST_ONLY-{index:05}')
    monkeypatch.setattr(host, 'scandir', lambda fd: Entries())
    with pytest.raises(ValueError): collection.directory('/usr')
    assert len(consumed) == 8193


def test_unknown_clock_after_modeled_launch_never_becomes_complete_or_renews_work(monkeypatch, tmp_path):
    selected, root, calls, clock, _, _ = whole_model(monkeypatch, tmp_path)
    monotonic = clock.monotonic
    def unavailable():
        if calls: raise OSError('TEST_ONLY clock unavailable after launch')
        return monotonic()
    monkeypatch.setattr(clock, 'monotonic', unavailable)
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'PARTIAL_DATA' and len(calls) == 1
    assert result['finished'] is None and result['files_manifest_sha256'] is None
    assert result['commands'][0]['finished'] is None
    assert result['custody']['known_terminal'] is False and root.exists()
    assert json.loads((root / 'FIRST-FAILURE.json').read_bytes()) == result


def test_late_export_keeps_original_bound_and_invalidates_complete_state(monkeypatch, tmp_path):
    selected, root, calls, clock, host, _ = whole_model(monkeypatch, tmp_path)
    write = host.write
    def delayed(fd, raw):
        count = write(fd, raw)
        clock.now = 61
        return count
    monkeypatch.setattr(host, 'write', delayed)
    result = module.discover_linux_tools(selected, root)
    assert len(calls) == 15 and result['inventory_state'] == 'PARTIAL_DATA'
    assert result['deadline'] == 60 and result['finished'] > 61 and result['files_manifest_sha256'] is None
    assert not (root / 'export/RESULT.json').exists() and (root / 'FIRST-FAILURE.json').exists()


def test_bounded_fault_prefix_preserves_first_observation():
    result = module._new_result(selection())
    for index in range(30): module._fault(result, 'query', 'TEST_ONLY', OSError(str(index) + 'é' * 3000), None)
    assert len(result['faults']) == 16 and result['faults'][0]['message'].startswith('0é')
    assert all(len(fault['message'].encode()) <= 2048 and fault['at'] is None for fault in result['faults'])


def test_stable_selected_relative_symlink_route_is_data_not_an_extra_query(monkeypatch, tmp_path):
    selected, root, calls, _, _, mapped = whole_model(monkeypatch, tmp_path)
    mapped('/bin').chmod(0o755)
    mapped('/usr/bin').chmod(0o755)
    raw = mapped('/bin/sh').read_bytes()
    mapped('/bin/sh').unlink()
    mapped('/usr/bin/sh').write_bytes(raw)
    mapped('/usr/bin/sh').chmod(0o555)
    mapped('/bin/sh').symlink_to('../usr/bin/sh')
    probe_result = module._new_result(selected)
    probe_result['deadline'] = 60
    candidate = module._Collection(probe_result, root).snapshot('/bin/sh', 'selector')
    module._DISCOVERY_APPOINTMENT['query_acceptance']['selectors']['/bin/sh'] = candidate
    result = module.discover_linux_tools(selected, root)
    assert result['inventory_state'] == 'COMPLETE_DATA', result['faults']
    observed = next(item for item in result['tools'] if item['path'] == '/bin/sh')
    assert observed['resolved'] == '/usr/bin/sh' and observed['links'][0]['target'] == '../usr/bin/sh'
    assert len(calls) == 15 and all(argv[0] != '/bin/sh' for argv in calls)


def test_failed_near_cap_export_has_precharged_all_emergency_regular_files(monkeypatch, tmp_path):
    result = module._new_result(selection())
    result['deadline'] = 60
    monkeypatch.setattr(module, 'time', SimpleNamespace(monotonic=lambda: 1))
    collection = module._Collection(result, tmp_path)
    # 8159 normal payload files + FILES + interrupted RESULT + 31 failure
    # prefixes + FIRST-FAILURE would be8193. Refuse before accumulating this state.
    collection.payload = {f'files/{index:05}.bin': (b'', 'selector') for index in range(8159)}
    with pytest.raises(module.DiscoveryHold): collection.room()


def test_exact_neighbor_reserves_every_failure_prefix_and_metadata_file(monkeypatch, tmp_path):
    result = module._new_result(selection())
    result['deadline'] = 60
    monkeypatch.setattr(module, 'time', SimpleNamespace(monotonic=lambda: 1))
    (tmp_path / 'journal').mkdir()
    collection = module._Collection(result, tmp_path)
    collection.payload = {f'files/{index:05}.bin': (b'', 'selector') for index in range(8127)}
    for index in range(30): collection.payload[f'journal/{index:03}.log'] = (b'', 'raw-log')
    collection.payload['journal/partial-file.bin'] = (b'', 'failure-prefix')
    collection.room()
    module._retain_failure(collection)
    emergency = [path for path in tmp_path.rglob('*') if path.is_file()]
    assert len(collection.payload) == 8158 and len(emergency) == 32
    assert len(collection.payload) + 2 + len(emergency) == 8192
    assert json.loads((tmp_path / 'FIRST-FAILURE.json').read_bytes())['files_manifest_sha256'] is None
