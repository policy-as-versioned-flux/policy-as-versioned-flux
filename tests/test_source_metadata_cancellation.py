"""Pure OS cancellation models at public extraction/preflight seams; no child spawned."""
import gc
import os
from pathlib import Path
import shutil
import signal

import pytest

from twin import source_metadata as sm
from twin import source_metadata_migration as migration


@pytest.mark.parametrize('route,site,exception_type', [
    (route,site,KeyboardInterrupt)
    for route in ('extraction','preflight')
    for site in ('first-signal','repeated-signal','wait','body','evidence-io')
] + [('extraction','first-signal',SystemExit)]
  + [(route,'cleanup-entry',KeyboardInterrupt) for route in ('extraction','preflight')])
def test_interrupted_owned_custody_preserves_workspace_and_original_cancellation(
        tmp_path, monkeypatch, route, site, exception_type):
    tool = tmp_path / 'TEST_ONLY-never-executed-converter'
    tool.write_bytes(b'TEST_ONLY retained executable fixture; never run')
    tool.chmod(0o700)
    plan = migration.prepare_pdf_extraction_plan(b'TEST_ONLY input', purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY predecessor'), member_id='TEST_ONLY-new',
        executable=str(tool), configuration=b'TEST_ONLY config', tool_version='TEST_ONLY-mock',
        version_observation=b'TEST_ONLY retained version', retained_files={str(tool):tool.read_bytes()})
    original = exception_type('TEST_ONLY original cancellation')
    state = {'workspace':None, 'wait_started':False, 'reaped':False,
             'group_alive':True, 'signals':[], 'wait_calls':0, 'read_calls':0,
             'secondary_raised':False, 'pipes':[]}
    class FakeChild:
        def __init__(self, argv, **kwargs):
            self.pid = 123456789
            self.returncode = None
            state['workspace'] = kwargs['cwd']
            for name, data in [('stdout',b'A'),('stderr',b'')]:
                read,write = os.pipe()
                os.write(write,data);os.close(write)
                stream = os.fdopen(read,'rb',buffering=0)
                setattr(self,name,stream)
                state['pipes'].append(stream)
        def wait(self, timeout):
            state['wait_started'] = True
            state['wait_calls'] += 1
            if site == 'wait':
                raise original
            state['reaped'] = True
            self.returncode = 0
            return 0
    def signal_group(pid, sig):
        assert pid == 123456789
        if sig:
            assert not state['wait_started'], 'destructive signal after solewait began'
            state['signals'].append(int(sig))
            if site in ('first-signal','repeated-signal','evidence-io') and sig == signal.SIGTERM:
                raise original
            if site == 'repeated-signal' and sig == signal.SIGKILL:
                raise SystemExit('TEST_ONLY secondary interruption')
            if sig == signal.SIGKILL:
                state['group_alive'] = False
        elif not state['group_alive']:
            raise ProcessLookupError('TEST_ONLY absent own group')
        else:
            # No actual group observation or signals occur in this pure model.
            raise PermissionError('TEST_ONLY live group membership unverified')
    def waitid(*args):
        assert not state['wait_started']
        return object()
    actual_read = os.read
    def interrupted_read(fd,count):
        state['read_calls'] += 1
        if site in ('body','cleanup-entry') and state['read_calls'] == 1:
            raise original
        return actual_read(fd,count)
    actual_monotonic = migration.time.monotonic
    def interrupted_cleanup_entry_clock():
        if site == 'cleanup-entry' and state['read_calls'] and not state['secondary_raised']:
            state['secondary_raised'] = True
            raise SystemExit('TEST_ONLY secondary cleanup-entry interruption')
        return actual_monotonic()
    monkeypatch.setattr(migration.time,'monotonic',interrupted_cleanup_entry_clock)
    actual_open = os.open
    def interrupted_evidence_open(path,*args,**kwargs):
        if site == 'evidence-io' and Path(path).name.startswith('interrupted-'):
            raise SystemExit('TEST_ONLY evidence write interrupted')
        return actual_open(path,*args,**kwargs)
    monkeypatch.setattr(migration.os,'open',interrupted_evidence_open)
    monkeypatch.setattr(migration.subprocess,'Popen',FakeChild)
    monkeypatch.setattr(migration.os,'killpg',signal_group)
    monkeypatch.setattr(migration.os,'waitid',waitid)
    monkeypatch.setattr(migration.os,'read',interrupted_read)
    try:
        with pytest.raises(exception_type) as caught:
            if route == 'extraction':
                migration.execute_new_extraction(plan,b'TEST_ONLY input')
            else:
                migration.prepare_extraction_plan('utf8-identity/1',b'TEST_ONLY input',
                    purpose='TEST_ONLY', predecessor_sha256=sm.sha256(b'TEST_ONLY old'),
                    member_id='TEST_ONLY-new')
        assert caught.value is original
        gc.collect()
        workdir = Path(state['workspace'])
        assert workdir.exists(), 'unknown launched custody deleted its workspace/finalizer'
        if route == 'extraction':
            assert (workdir/'input').read_bytes() == b'TEST_ONLY input'
            assert (workdir/'config').is_file()
        if site == 'evidence-io':
            assert not (workdir/'interrupted-execution.json').exists()
        else:
            observation = sm._json((workdir/'interrupted-execution.json').read_bytes())
            assert observation['disposition'] == 'interrupted'
            assert observation['cancellation_type'] == exception_type.__name__
            assert observation['process_group']['direct_child_reaped'] == state['reaped']
            assert not observation['success']
        assert state['wait_calls'] <= 1
        if site == 'cleanup-entry':
            assert state['secondary_raised'] and not state['signals']
            assert not state['wait_calls'] and not state['reaped']
        else:
            assert state['signals'] == [signal.SIGTERM,signal.SIGKILL]
        if site == 'repeated-signal':
            assert state['group_alive'] and not state['reaped']
    finally:
        # The child/group are entirely mocked; close fixture pipes and owned files.
        for pipe in state['pipes']:
            pipe.close()
        if state['workspace'] and Path(state['workspace']).exists():
            shutil.rmtree(state['workspace'])
