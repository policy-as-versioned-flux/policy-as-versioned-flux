"""Public synthetic repair controls; no native/backend/proc operation is invoked."""
import copy
import types
import pytest
from twin import source_native_observation as n, source_metadata as sm
from test_source_native_observation import fixture, splice, call, blob


def test_resolver_rejects_substitute_store_and_reference_before_reading_attributes():
    observation,archive=fixture()
    raw=b'TEST_ONLY independent policy evidence; no native execution'
    evidence={sm.sha256(raw):raw}
    policy={'schema':'twin.native-host-policy/v1','scope':n.SCOPE,'custodian':'TEST_ONLY-source-review',
        'not_before':'2026-10-30T00:00:00+00:00','not_after':'2026-10-30T01:00:00+00:00',
        'roots':['/bin','/lib'],'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':list(evidence)}
    context=n.freeze_native_host_context(policy,evidence,sm.sha256(sm.canonical(policy)))
    genuine=n.new_native_observation_store(purpose='actual',host_context=context)
    observation['purpose']=observation['spec']['purpose']='actual'
    observation['host_policy_sha256']=sm.sha256(sm.canonical(policy))
    archive.update(evidence);archive[observation['host_policy_sha256']]=sm.canonical(policy)
    reference=object();result={'status':'success','archive':archive,'receipts':{}}
    substitute=types.SimpleNamespace(_guard=genuine._guard,_purpose='actual',_host_context=context,
        _entries={id(reference):(reference,result,n._result_digest(result),observation)})
    for store,ref in ((substitute,reference),(types.SimpleNamespace(),reference),(genuine,reference)):
        with pytest.raises(ValueError,match='store|reference'):
            n.resolve_native_observation(store,ref)
    assert genuine._entries=={}


@pytest.mark.parametrize('variant',['readlink-count','readlink-exe','stat-empty','stat-identity','stat-status','getcwd','dirent','failed-buffer'])
def test_metadata_replay_rejects_impossible_result_buffers(variant):
    observation,archive=fixture()
    if variant=='readlink-count':
        request=call(89,[4096,8192,1],{'path':'/proc/self/exe'},200,{'buffer_sha256':blob(archive,b'/TEST_ONLY-wrong-executable')})
    elif variant=='readlink-exe':
        wrong=b'/bad/tool';request=call(89,[4096,8192,32],{'path':'/proc/self/exe'},len(wrong),{'buffer_sha256':blob(archive,wrong)})
    elif variant=='getcwd':
        request=call(79,[8192,32],result=7,detail={'buffer_sha256':blob(archive,b'/other\0')})
    elif variant=='dirent':
        identity=[1,123,0o40555,1000,1000,1,0,1,1]
        request=call(2,[0,0x90000],{'path':'/'},3,{'kind':'directory','identity':identity})
        request+=call(217,[3,8192,32],result=8,detail={'buffer_sha256':blob(archive,b'badentry')})+call(3,[3])
    else:
        raw=stat_buffer(observation['files']['/data']['identity'])
        if variant=='stat-empty':raw=b''
        if variant=='stat-identity':raw=stat_buffer([1,999,0o100444,1000,1000,1,6,1,1])
        request=call(4,[4096,8192],{'path':'/data'},1 if variant=='stat-status' else -2 if variant=='failed-buffer' else 0,{'buffer_sha256':blob(archive,raw)})
    splice(observation,request)
    with pytest.raises(ValueError):n.verify_native_observation(observation,archive,purpose='TEST_ONLY')


def stat_buffer(identity):
    import struct
    dev,ino,mode,uid,gid,nlink,size,mtime,ctime=identity
    raw=bytearray(144)
    struct.pack_into('<QQQIII',raw,0,dev,ino,nlink,mode,uid,gid)
    struct.pack_into('<q',raw,48,size)
    struct.pack_into('<qqqq',raw,88,mtime//10**9,mtime%10**9,ctime//10**9,ctime%10**9)
    return bytes(raw)


def test_metadata_replay_accepts_exact_stat_and_proc_exe_truncation():
    observation,archive=fixture()
    requests=call(4,[4096,8192],{'path':'/data'},0,{'buffer_sha256':blob(archive,stat_buffer(observation['files']['/data']['identity']))})
    requests+=call(89,[4096,8192,1],{'path':'/proc/self/exe'},1,{'buffer_sha256':blob(archive,b'/')})
    requests+=call(79,[8192,32],result=6,detail={'buffer_sha256':blob(archive,b'/work\0')})
    splice(observation,requests)
    assert n.verify_native_observation(observation,archive,purpose='TEST_ONLY')['stdout_bytes']==6


def test_executable_mprotect_is_refused_at_admission_without_file_provenance():
    observation,_=fixture()
    with pytest.raises(ValueError,match='mapping|provenance'):
        n._admit(10,[0x600000,4096,5,0,0,0],{},observation['spec'],{},set(),True)


def test_executable_mprotect_requires_full_acquired_interval_before_dispatch():
    observation,_=fixture();maps=observation['events'][2]['data']['maps']
    assert n._admit(10,[0x400000,4096,5,0,0,0],{},observation['spec'],{},set(),True,maps=maps)=='mprotect'
    for start,length in ((0x3ff000,8192),(0x400000,8192),(0x600000,4096)):
        with pytest.raises(ValueError):
            n._admit(10,[start,length,5,0,0,0],{},observation['spec'],{},set(),True,maps=maps)


def test_post_mapping_reconciliation_holds_before_userspace_can_resume():
    observation,_=fixture();maps=observation['events'][2]['data']['maps']
    assert n._reconcile_maps('mprotect',[0x400000,4096,1,0,0,0],0,maps,[{**maps[0],'prot':1},maps[1]],observation['files'],None)[0]['prot']==1
    anonymous={'start':0x600000,'end':0x601000,'prot':5,'offset':0,'path':None,'identity':[0,0]}
    with pytest.raises(ValueError):
        n._reconcile_maps('mprotect',[0x400000,4096,1,0,0,0],0,maps,maps+[anonymous],observation['files'],None)


def test_native_teardown_uses_one_shared_grace_for_leader_and_descendants(monkeypatch):
    import ast,signal
    from pathlib import Path
    clock={'now':120.0};signals=[];reaped=[]
    fake_os=types.SimpleNamespace(killpg=lambda pid,sig:signals.append(('group',pid,int(sig),clock['now'])),
        kill=lambda pid,sig:signals.append(('pid',pid,int(sig),clock['now'])),
        waitpid=lambda *args:(0,0),WNOHANG=1,WUNTRACED=2,
        WIFEXITED=lambda status:False,WIFSIGNALED=lambda status:False,
        waitstatus_to_exitcode=lambda status:0,close=lambda fd:None)
    fake_time=types.SimpleNamespace(monotonic=lambda:clock['now'],sleep=lambda seconds:clock.update(now=clock['now']+.25))
    monkeypatch.setattr(n,'os',fake_os);monkeypatch.setattr(n,'time',fake_time)
    monkeypatch.setattr(n,'_ptrace',lambda *args:None)
    if hasattr(n,'_finish_native_custody'):
        custody,_=n._finish_native_custody(100,{101,102},reaped,None,deadline=122.0)
    else:
        # The independent source-only probe, retained here to establish the old
        # renewed-budget behavior before the narrow cleanup helper is written.
        tree=ast.parse(Path(n.__file__).read_text())
        function=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='_linux_run')
        cleanup=next(node.finalbody for node in ast.walk(function) if isinstance(node,ast.Try)
            and any(isinstance(item,ast.For) and isinstance(item.target,ast.Name) and item.target.id=='child_pid' for item in node.finalbody))
        namespace={'pid':100,'reaped':reaped,'descendants':{101,102},'held':{},'acquired':[],
            'pipes':[],'mem':-1,'procfd':-1,'os':fake_os,'time':fake_time,'signal':signal,
            '_ptrace':lambda *args:None,'failure':'already-at-original-wall','returncode':None}
        module=ast.Module(body=cleanup,type_ignores=[]);ast.fix_missing_locations(module)
        exec(compile(module,'TEST_ONLY-extracted-cleanup','exec'),namespace)
        custody={'absence_verified':False}
    assert clock['now']<=122.0,'cleanup renewed the original shared grace'
    assert not custody['absence_verified']
    assert not reaped
    assert all(event[3]<=122.0 for event in signals)


def test_native_uncertain_custody_preserves_workspace_even_with_true_public_booleans():
    from twin import source_metadata_migration as m
    observation,_=fixture();custody=copy.deepcopy(observation['events'][-1]['data']['custody'])
    custody['absence_probe']='not-observed'
    state={'cleaned':False,'detached':False}
    directory=types.SimpleNamespace(_finalizer=types.SimpleNamespace(detach=lambda:state.update(detached=True)),
        cleanup=lambda:state.update(cleaned=True))
    run={'native_observation':observation,'process_group':custody}
    assert m._cleanup_workspace(directory,run,run_started=True)=='preserved-unverified-group'
    assert state=={'cleaned':False,'detached':True}


def test_native_reaped_lifetime_is_never_signalled_and_requires_absent_group(monkeypatch):
    calls=[]
    def absent_group(pid,sig):
        calls.append((pid,sig));assert sig==0
        raise ProcessLookupError('TEST_ONLY absent group')
    monkeypatch.setattr(n,'os',types.SimpleNamespace(killpg=absent_group))
    monkeypatch.setattr(n,'time',types.SimpleNamespace(monotonic=lambda:120.0))
    custody,status=n._finish_native_custody(100,set(),[100],0,deadline=122.0)
    n.validate_native_custody(custody,pid=100,reaped=[100])
    assert status==0 and calls==[(100,0)] and custody['signals']==[]


def test_metadata_unsupported_extents_hold_before_dispatch_or_memory_capture(monkeypatch):
    observation,_=fixture()
    with pytest.raises(ValueError):
        n._admit(89,[4096,8192,n.MAX_PATH+1,0,0,0],{'path':'/proc/self/exe'},observation['spec'],{},set(),True)
    def forbidden(*args):raise AssertionError('impossible result was read from target memory')
    monkeypatch.setattr(n,'_memory',forbidden)
    with pytest.raises(ValueError):
        n._result_buffer({'name':'readlink','args':[4096,8192,1,0,0,0]},200,123)


def test_rejected_stopped_native_target_is_never_resumed_during_teardown(monkeypatch):
    clock={'now':120.0};resumed=[]
    fake_os=types.SimpleNamespace(killpg=lambda *args:None,kill=lambda *args:None,
        waitpid=lambda pid,*args:(pid,1),WNOHANG=1,WUNTRACED=2,
        WIFEXITED=lambda status:False,WIFSIGNALED=lambda status:False)
    monkeypatch.setattr(n,'os',fake_os)
    monkeypatch.setattr(n,'time',types.SimpleNamespace(monotonic=lambda:clock['now'],sleep=lambda seconds:clock.update(now=clock['now']+.25)))
    monkeypatch.setattr(n,'_ptrace',lambda *args:resumed.append(args))
    custody,_=n._finish_native_custody(100,set(),[],None,deadline=122.0)
    assert not resumed,'cleanup released a target stopped at a rejected syscall'
    assert not custody['absence_verified'] and not custody['direct_child_reaped']
