"""Portable TEST_ONLY controls. No privileged/kernel/runtime operation is executed."""
import importlib.util
from pathlib import Path
import pytest


def control():
    source = Path(__file__).parents[1]/'bench/pinned-candidate/linux_lease_control.py'
    spec = importlib.util.spec_from_file_location('TEST_ONLY_linux_lease_control', source)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_control_descriptor_is_separate_from_every_production_profile():
    module = control()
    descriptor = module.validate_descriptor({'schema':'TEST_ONLY-linux-lease-control/v1',
                                              'scenario':'baseline'})
    assert descriptor == {'schema':'TEST_ONLY-linux-lease-control/v1','scenario':'baseline'}
    from twin.linux_candidate import validate_profile
    with pytest.raises(ValueError):validate_profile(descriptor)
    with pytest.raises(ValueError):module._guardian().validate_reviewed_profile(descriptor)
    source=Path(__file__).parents[1]/'bench/pinned-candidate/qwen_backend.py'
    spec=importlib.util.spec_from_file_location('TEST_ONLY_production_child',source)
    assert spec and spec.loader
    backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
    with pytest.raises(ValueError):backend.validate_runtime_profile(descriptor)
    with pytest.raises(ValueError,match='fixed scenario'):
        module.validate_descriptor(dict(descriptor,scenario='/bin/sh'))
    with pytest.raises(ValueError,match='closed descriptor'):
        module.validate_descriptor(dict(descriptor,uid=1001))


def test_guardian_loss_cleanup_does_not_fabricate_a_production_receipt():
    m=control()
    evidence={'executed':True,'scenario':'guardian-loss','started':100.0,'finished':120.0,
        'guardian_terminal':None,'outer':{'empty':True,'dead':True,'reaped':True,'removed':True},
        'sentinel':{'before':{'pid':701,'start':'91'},'after':{'pid':701,'start':'91'},'alive':True},
        'checks':{'raw-clone':True,'attached':True,'dropped':True,'armed':True,'ready':True,
                  'descendants':True},'error':None}
    import copy
    evidence['attempts']=[dict(copy.deepcopy(evidence),case=stage,
        started=100.0+index*3,finished=103.0+index*3,checks={stage:True})
        for index,stage in enumerate(('raw-clone','attached','dropped','armed','ready','descendants'))]
    result=m.verify_result(evidence)
    assert result['control_passed'] is True
    assert result['production_capture_accepted'] is False
    assert result['guardian_terminal_missing'] is True
    for altered in ({'executed':False},{'outer':dict(evidence['outer'],reaped=False)},
                    {'sentinel':dict(evidence['sentinel'],alive=False)},
                    {'checks':dict(evidence['checks'],dropped=False)},
                    {'finished':1001.0},{'guardian_terminal':{'empty':True,'reaped':True}},
                    {'outer':{'empty':1,'dead':1,'reaped':1,'removed':1}}):
        value=copy.deepcopy(evidence);value.update(altered)
        with pytest.raises(ValueError):m.verify_result(value)


def test_existing_nobody_requires_distinct_unaliased_unused_credentials():
    m=control()
    facts={'name':'nobody','uid':65534,'gid':65534,'caller_uid':1001,'caller_gid':1001,
           'uid_names':['nobody'],'gid_names':['nogroup'],'primary_names':['nobody'],
           'supplementary_names':[],'active':False,'home_exposed':False}
    assert m.validate_principal(facts)==(65534,65534)
    for change in ({'uid':0},{'uid':1001},{'active':True},{'home_exposed':True},
                   {'uid_names':['nobody','other']},{'primary_names':['nobody','other']},
                   {'supplementary_names':['runner']},{'uid':True}):
        with pytest.raises(ValueError):m.validate_principal(dict(facts,**change))


def test_closure_refuses_missing_elf_loader_ambiguous_needed_and_unbounded_files():
    m=control()
    rows=[{'source':'/TEST_ONLY/python','target':'/usr/bin/python3.12','bytes':4096,'sha256':'1'*64,
           'elf':{'interpreter':'/lib/ld-test.so','needed':['libc-test.so']}},
          {'source':'/TEST_ONLY/loader','target':'/lib/ld-test.so','bytes':4096,'sha256':'2'*64,
           'elf':{'interpreter':None,'needed':[]}},
          {'source':'/TEST_ONLY/libc','target':'/lib/libc-test.so','bytes':4096,'sha256':'3'*64,
           'elf':{'interpreter':None,'needed':[]}}]
    assert m.validate_closure(rows)['bytes']==12288
    for bad in (rows[:1],rows+[dict(rows[-1],source='/TEST_ONLY/other',target='/other/libc-test.so')],
                [dict(rows[0],bytes=268435457),*rows[1:]],
                [dict(rows[0],target='/app/../bad'),*rows[1:]]):
        with pytest.raises(ValueError):m.validate_closure(bad)


def test_trusted_handoff_rejects_unknown_stage_and_private_control_eof(monkeypatch):
    m=control();g=m._guardian()
    class PinnedSupervisor:
        def verify(self):pass
    class PinnedChild:
        pid=300;start='88'
        def verify(self):pass
    output=[]
    monkeypatch.setattr(g.os,'write',lambda fd,raw:output.append(raw) or len(raw))
    monkeypatch.setattr(g.os,'read',lambda fd,count:b'')
    monkeypatch.setattr(g.select,'select',lambda read,write,error,timeout:(read,write,[]))
    monkeypatch.setattr(g.time,'monotonic',lambda:1.0)
    h=g.TrustedHandoff(0,1,g.Wire('TEST_ONLY'),30.0,PinnedSupervisor())
    with pytest.raises(ValueError,match='fixed trusted handoff'):h.reach('arbitrary-command',PinnedChild())
    with pytest.raises(ValueError,match='handoff control lost'):h.reach('raw-clone',PinnedChild())
    assert b'raw-clone' in output[0]


def test_control_initialization_cannot_reset_deadline_or_enter_production(monkeypatch):
    m=control();g=m._guardian()
    monkeypatch.setattr(g.time,'monotonic',lambda:100.0)
    guardian=m.control_guardian(g,{'deadline_monotonic':140.0}, {},
        {'config':{'schema':m.SCHEMA,'scenario':'baseline'}},None)
    assert guardian.deadline==140.0
    assert guardian.work_deadline==130.0
    assert guardian.anchor==m.ANCHOR
    with pytest.raises(ValueError):g.Guardian({'deadline_monotonic':140.0},{},
        {'config':{'schema':m.SCHEMA,'scenario':'baseline'}},None)


def test_network_evidence_requires_eight_actual_errno_denials_and_kernel_state():
    m=control()
    valid={'state':{'NoNewPrivs':'1','Seccomp':'2'},'probes':[
        {'errno':1,'probe':name} for name in ('ipv4/tcp','ipv4/udp','ipv6/tcp','ipv6/udp',
            'socket-syscall','io-uring','pidfd-getfd','unix-socketpair')]}
    assert m.network_ok(valid)
    assert not m.network_ok(dict(valid,probes=valid['probes'][:7]))
    assert not m.network_ok(dict(valid,probes=[{'errno':13,'blocked':True}]*8))
    assert not m.network_ok(dict(valid,state={'NoNewPrivs':'0','Seccomp':'2'}))
    assert not m.network_ok(dict(valid,probes=[valid['probes'][0]]*8))


def test_boundary_assessment_does_not_accept_success_or_missing_denial_evidence():
    m=control()
    denial={'denied':True,'errno':1}
    result={'writes':[dict(denial,path=path) for path in m.WRITE_PATHS],
        'privilege':{key:denial for key in ('setuid','setgid','setgroups','capset','death-signal')},
        'isolation':{key:denial for key in ('mount','unshare','setns')},
        'process':{key:denial for key in ('ptrace','process_vm_writev','pidfd_getfd')},
        'host_proc_absent':{'101':True,'102':True,'103':True}}
    assert m.boundary_checks(result,[101,102,103])=={'writes':True,'privilege':True,'isolation':True,'process':True}
    import copy
    forged=copy.deepcopy(result);forged['writes'][0]['denied']=False
    assert not m.boundary_checks(forged,[101,102,103])['writes']
    forged=copy.deepcopy(result);forged['host_proc_absent']['103']=False
    assert not m.boundary_checks(forged,[101,102,103])['process']
    forged=copy.deepcopy(result);forged['privilege']['capset']={'denied':True,'errno':2}
    assert not m.boundary_checks(forged,[101,102,103])['privilege']


def test_parent_cannot_aggregate_success_over_missing_or_failed_actual_attempts():
    m=control()
    result={'executed':True,'scenario':'guardian-loss','started':100.,'finished':200.,'error':None,
        'guardian_terminal':None,'outer':{'empty':True,'dead':True,'reaped':True,'removed':True},
        'sentinel':{'before':{'pid':701,'start':'91'},'after':{'pid':701,'start':'91'},'alive':True},
        'checks':dict.fromkeys(m.HANDOFFS,True),
        'attempts':[{'case':'raw-clone','started':100.,'finished':110.,'error':None,
            'checks':{'raw-clone':False},'outer':{'empty':True,'dead':True,'reaped':True,'removed':True}}]}
    with pytest.raises(ValueError,match='attempt'):
        m.verify_result(result)


@pytest.mark.parametrize('stage',['raw-clone','dropped','armed'])
def test_guardian_death_before_any_bootstrap_release_never_releases_child(monkeypatch,stage):
    m=control();g=m._guardian()
    class Exit(BaseException):pass
    writes=[]
    monkeypatch.setattr(g.select,'select',lambda read,write,error,timeout:([99],[],[]))
    monkeypatch.setattr(g.os,'_exit',lambda code:(_ for _ in ()).throw(Exit(code)))
    monkeypatch.setattr(g.os,'write',lambda fd,raw:writes.append((fd,raw)))
    with pytest.raises(Exit):g.child_handoff(stage,10,11,99)
    assert writes==[]


def test_actual_elf_reader_retains_loader_and_needed_and_refuses_out_of_file_segments():
    import struct
    m=control()
    raw=bytearray(1024)
    raw[:16]=b'\x7fELF\x02\x01\x01'+b'\0'*9
    struct.pack_into('<HHIQQQIHHHHHH',raw,16,3,62,1,0,64,0,0,64,56,3,0,0,0)
    struct.pack_into('<IIQQQQQQ',raw,64,1,4,0,0x400000,0,1024,1024,4096)
    loader=b'/lib/ld-fixture.so\0'
    struct.pack_into('<IIQQQQQQ',raw,120,3,4,300,0,0,len(loader),len(loader),1)
    raw[300:300+len(loader)]=loader
    struct.pack_into('<IIQQQQQQ',raw,176,2,4,400,0,0,64,64,8)
    struct.pack_into('<qQqQqQqQ',raw,400,1,0,5,0x400200,10,14,0,0)
    raw[512:526]=b'libfixture.so\0'
    assert m.elf_dependencies(bytes(raw))=={'interpreter':'/lib/ld-fixture.so','needed':['libfixture.so']}
    with pytest.raises(ValueError):m.elf_dependencies(bytes(raw[:450]))
    raw[5]=2
    with pytest.raises(ValueError):m.elf_dependencies(bytes(raw))


def test_child_success_alone_cannot_supply_actual_kernel_limits_or_both_phases():
    m=control()
    fake=[{'event':'frame','phase':'generate','body':{'type':'control','case':'standard',
        'result':{'network':{},'claimed_limits':{'memory.max':'12884901888'}}}}]
    verdict=m.assess_attempt('baseline','standard',fake,
        {'receipts':[],'host_pids':[1,2,3],'source_unchanged':True},{'cpus':[0,1]})
    assert verdict=={'paired':False,'limits':False,'network':False,'sources':False}


@pytest.mark.parametrize('scenario',('baseline','boundaries','resources','supervisor-loss','guardian-loss','invalid-evidence'))
def test_missing_actual_scenario_events_are_never_success(scenario):
    m=control()
    case=m.CASES[scenario][0]
    assert any(value is False for value in m.assess_attempt(scenario,case,[],
        {'receipts':[],'host_pids':[1,2,3]},{'cpus':[0,1]}).values())


def test_guardian_loss_between_early_check_and_release_still_exits_without_release(monkeypatch):
    g=control()._guardian()
    class Exit(BaseException):pass
    calls=iter([([],[],[]),([99],[],[])])
    monkeypatch.setattr(g.select,'select',lambda *args:next(calls))
    monkeypatch.setattr(g.os,'_exit',lambda code:(_ for _ in ()).throw(Exit(code)))
    written=[]
    monkeypatch.setattr(g.os,'write',lambda fd,raw:written.append((fd,raw)) or len(raw))
    monkeypatch.setattr(g.os,'read',lambda *args:pytest.fail('dead guardian must not consume a release'))
    with pytest.raises(Exit):g.child_handoff('dropped',10,11,99)
    assert written==[(10,b'dropped\n')]
