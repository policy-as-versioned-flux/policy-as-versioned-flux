"""Bounded TEST_ONLY own-group regression probes; no native converter or /proc."""
import json
import os
from pathlib import Path
import signal
import shutil
import sys
import time

import pytest

from twin import source_metadata as sm
from twin import source_metadata_migration as migration


def owned_descendant_run(tmp_path, monkeypatch, mode):
    """Public fake-converter route; fixture descendants have a five-second backstop."""
    info = tmp_path / 'TEST_ONLY-owned-pids.json'
    tool = tmp_path / 'TEST_ONLY-converter'
    tool.write_text('#!' + sys.executable + '\n' + '''import os,signal,time,json
from pathlib import Path
info=Path(''' + repr(str(info)) + ''')
mode=''' + repr(mode) + '''
pid=os.fork()
if pid==0:
    signal.signal(signal.SIGTERM,signal.SIG_IGN)
    if mode=='success':
        os.close(1);os.close(2)
    info.write_text(json.dumps({'leader':os.getppid(),'descendant':os.getpid(),'group':os.getpgrp()}))
    time.sleep(5)
    os._exit(0)
while not info.exists(): time.sleep(.001)
if mode=='success':
    os.write(1,b'A');os._exit(0)
if mode=='overflow': os.write(2,b'X'*4096)
time.sleep(5)
''')
    tool.chmod(0o700)
    limits = dict(migration.PROFILES['pdf-text-xpdf/1'], wall_seconds=.8,
                  termination_grace_seconds=.2, stderr_bytes=1024)
    monkeypatch.setitem(migration.PROFILES, 'pdf-text-xpdf/1', limits)
    plan = migration.prepare_pdf_extraction_plan(b'TEST_ONLY raw', purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY predecessor'), member_id='TEST_ONLY-new',
        executable=str(tool), tool_version='TEST_ONLY-fake-converter',
        version_observation=b'TEST_ONLY retained fixture version',
        configuration=b'TEST_ONLY config', retained_files={str(tool.resolve()):tool.read_bytes()})
    result = None
    try:
        result = migration.execute_new_extraction(plan, b'TEST_ONLY raw')
        owned = json.loads(info.read_text())
        deadline = time.monotonic() + .5
        alive = True
        while time.monotonic() < deadline:
            try:
                os.kill(owned['descendant'], 0)
            except ProcessLookupError:
                alive = False
                break
            time.sleep(.005)
        return result, owned, alive
    finally:
        # Explicit narrow cleanup also runs on RED. Never attach to another group.
        if info.exists():
            owned = json.loads(info.read_text())
            try:
                if os.getpgid(owned['descendant']) == owned['group']:
                    os.killpg(owned['group'], signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_timeout_leader_term_exit_cannot_leave_term_ignoring_descendant(tmp_path, monkeypatch):
    result, owned, alive = owned_descendant_run(tmp_path, monkeypatch, 'timeout')
    assert not alive, 'owned descendant survived timeout cleanup'
    assert result['status'] == 'failure' and 'index_sha256' not in result
    dossier = sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['failure'] == 'timeout'
    assert dossier['elapsed_seconds'] < 1.1
    assert dossier['process_group']['direct_child_reaped'] is True
    assert dossier['process_group']['absence_verified'] is True
    assert dossier['process_group']['leader_pid'] == owned['group'] == owned['leader']
    assert not Path(sm._json(result['archive'][dossier['invocation_sha256']])['cwd']).exists()


def test_zero_exit_closed_pipes_do_not_establish_group_completion(tmp_path, monkeypatch):
    result, owned, alive = owned_descendant_run(tmp_path, monkeypatch, 'success')
    assert not alive, 'owned descendant survived apparent leader success'
    dossier = sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['process_group']['direct_child_reaped'] is True
    assert dossier['process_group']['absence_verified'] is True
    assert dossier['process_group']['leader_pid'] == owned['group']
    assert dossier['workspace_cleanup'] == 'removed'
    assert dossier['elapsed_seconds'] < .8
    assert result['archive'][sm.sha256(b'A')] == b'A'
    assert any(row == {'signal':int(signal.SIGKILL),'outcome':'sent'}
               for row in dossier['process_group']['signals'])


def test_stream_overflow_kills_group_even_when_leader_exits_on_term(tmp_path, monkeypatch):
    result, _, alive = owned_descendant_run(tmp_path, monkeypatch, 'overflow')
    assert not alive, 'owned descendant survived stream-overflow cleanup'
    dossier = sm._json(result['receipts'][result['dossier_sha256']])
    assert result['status'] == 'failure' and result['failure'] == 'stderr-overflow'
    assert 'index_sha256' not in result and dossier['standard_receipt_sha256'] is None
    assert dossier['stderr']['bytes'] == 1024
    assert dossier['observed_bytes_lower_bound']['stderr'] > 1024
    assert dossier['process_group']['absence_verified'] is True
    assert dossier['process_group']['direct_child_reaped'] is True
    assert dossier['elapsed_seconds'] < .8


def test_unverified_group_holds_preserves_workspace_and_never_signals_after_reap(monkeypatch):
    plan = migration.prepare_extraction_plan('utf8-identity/1', b'A', purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY predecessor'), member_id='TEST_ONLY-new')
    actual_popen, actual_killpg = migration.subprocess.Popen, os.killpg
    processes = []
    class ObservedChild:
        def __init__(self, *args, **kwargs):
            self.process = actual_popen(*args, **kwargs)
            self.reaped = False
            processes.append(self)
        def __getattr__(self, name):
            return getattr(self.process, name)
        def wait(self, timeout):
            code = self.process.wait(timeout=timeout)
            self.reaped = True
            return code
    def uncertain_group(pid, sig):
        child = processes[-1]
        assert pid == child.pid
        if child.reaped:
            assert sig == 0, 'destructive signal after PID reservation released'
            raise PermissionError('TEST_ONLY absence observation unavailable')
        return actual_killpg(pid, sig)
    monkeypatch.setattr(migration.subprocess, 'Popen', ObservedChild)
    monkeypatch.setattr(migration.os, 'killpg', uncertain_group)
    result = migration.execute_new_extraction(plan, b'A')
    dossier = sm._json(result['receipts'][result['dossier_sha256']])
    workdir = Path(sm._json(result['archive'][dossier['invocation_sha256']])['cwd'])
    try:
        assert result['status'] == 'failure' and result['failure'] == 'owned-group-unverified'
        assert 'index_sha256' not in result and dossier['standard_receipt_sha256'] is None
        assert dossier['process_group']['direct_child_reaped'] is True
        assert dossier['process_group']['absence_verified'] is False
        assert dossier['workspace_cleanup'] == 'preserved-unverified-group'
        assert (workdir / 'input').read_bytes() == b'A'
        assert result['archive'][sm.sha256(b'A')] == b'A'
        assert dossier['elapsed_seconds'] <= migration.PROFILES['utf8-identity/1']['wall_seconds']
    finally:
        # The TEST_ONLY injected observation failed; the real direct child is reaped.
        monkeypatch.setattr(migration.os, 'killpg', actual_killpg)
        with pytest.raises(ProcessLookupError):
            actual_killpg(processes[-1].pid, 0)
        shutil.rmtree(workdir)


@pytest.mark.parametrize('uncertainty', ['reservation', 'reap'])
def test_uncertain_child_ownership_or_reap_holds_without_claiming_cleanup(monkeypatch, uncertainty):
    plan = migration.prepare_extraction_plan('utf8-identity/1', b'A', purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY predecessor'), member_id='TEST_ONLY-new')
    signals, instances = [], []
    class FakeChild:
        def __init__(self, *args, **kwargs):
            self.pid = 123456789
            self.returncode = None
            self.wait_called = False
            for name, data in [('stdout', b'A'), ('stderr', b'')]:
                read, write = os.pipe()
                os.write(write, data)
                os.close(write)
                setattr(self, name, os.fdopen(read, 'rb', buffering=0))
            instances.append(self)
        def wait(self, timeout):
            self.wait_called = True
            raise migration.subprocess.TimeoutExpired('TEST_ONLY unreapable child', timeout)
    def waitid(*args):
        if uncertainty == 'reservation':
            raise ChildProcessError('TEST_ONLY no retained child reservation')
        return object()
    def signal_group(pid, sig):
        assert pid == instances[0].pid
        assert not instances[0].wait_called, 'group signal after reservation release'
        if sig:
            signals.append(int(sig))
    monkeypatch.setattr(migration.subprocess, 'Popen', FakeChild)
    monkeypatch.setattr(migration.os, 'waitid', waitid)
    monkeypatch.setattr(migration.os, 'killpg', signal_group)
    result = migration.execute_new_extraction(plan, b'A')
    dossier = sm._json(result['receipts'][result['dossier_sha256']])
    workdir = Path(sm._json(result['archive'][dossier['invocation_sha256']])['cwd'])
    try:
        assert result['status'] == 'failure' and 'index_sha256' not in result
        assert result['failure'] == 'direct-child-' + uncertainty + '-unverified'
        assert dossier['process_group']['direct_child_reaped'] is False
        assert dossier['process_group']['absence_verified'] is False
        assert dossier['workspace_cleanup'] == 'preserved-unverified-group'
        assert (workdir / 'input').read_bytes() == b'A'
        assert all(getattr(instances[0], name).closed for name in ('stdout', 'stderr'))
        if uncertainty == 'reservation':
            assert not signals and not instances[0].wait_called
        else:
            assert signals == [signal.SIGTERM, signal.SIGKILL]
    finally:
        # Pure OS mock: there is no actual child or process group to clean.
        shutil.rmtree(workdir)


@pytest.mark.parametrize('claim', ['direct_child_reaped', 'absence_verified', 'workspace_cleanup'])
def test_pinned_execution_with_unestablished_cleanup_cannot_enter_store(claim):
    from test_source_metadata_migration import migrated_fixture
    manifest, archive, receipts, old, result, _ = migrated_fixture()
    index = sm._json(receipts[result['index_sha256']])
    dossier = sm._json(receipts[index['dossier_sha256']])
    if claim == 'workspace_cleanup':
        dossier[claim] = 'preserved-unverified-group'
    else:
        dossier['process_group'][claim] = False
    raw = sm.canonical(dossier)
    index['dossier_sha256'] = sm.sha256(raw)
    receipts[sm.sha256(raw)] = raw
    raw = sm.canonical(index)
    pin = sm.sha256(raw)
    receipts[pin] = raw
    policy = sm._json(old.description)['policy']
    authority = migration.freeze_migration_authority('TEST_ONLY-parent', 'TEST_ONLY-cleanup', '1',
        sm.sha256(sm.canonical(policy)), policy=policy,
        layout_config={'schema':'twin.source-legacy-layout/v1', 'purpose':'TEST_ONLY',
                       'transport_contract_sha256':None},
        execution_contract={'schema':'twin.source-migration-execution-contract/v1',
                            'purpose':'TEST_ONLY', 'index_sha256s':[pin]})
    raw = sm.canonical(manifest)
    with pytest.raises(ValueError, match='group cleanup'):
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-unverified', raw, archive,
            receipts, sm.sha256(raw), authority)
