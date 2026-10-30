"""Portable TEST_ONLY source controls; no Linux/proc/root/helper/runtime execution."""
import importlib.util
from pathlib import Path
import sys
import pytest


def ci():
    source=Path(__file__).parents[1]/'bench/pinned-candidate/linux_lease_control_ci.py'
    spec=importlib.util.spec_from_file_location('TEST_ONLY_lease_ci',source)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def test_suite_deadline_survives_install_and_every_scenario_without_renewal():
    m=ci()
    receipt={'schema':'TEST_ONLY-ci-start/v1','pid':201,'start':'77','started':100.,
             'deadline':1000.,'source_manifest_sha256':'1'*64}
    budget=m.SuiteBudget.admit(receipt,pid=201,start='77',manifest='1'*64,now=180.)
    assert budget.deadline==1000.
    assert budget.attempt_deadline(200.,'standard')==260.
    assert budget.attempt_deadline(500.,'deadline')==530.
    assert budget.attempt_deadline(970.,'standard')==1000.
    for changed in ({'pid':202},{'start':'78'},{'started':True},{'deadline':1001.},
                    {'deadline':float('nan')},{'source_manifest_sha256':'2'*64}):
        with pytest.raises(ValueError):
            m.SuiteBudget.admit(dict(receipt,**changed),pid=201,start='77',manifest='1'*64,now=180.)
    with pytest.raises(ValueError):budget.attempt_deadline(991.,'standard')


def test_literal_manifest_pin_is_required_before_any_source_can_be_installed():
    import hashlib,json
    m=ci()
    data={'schema':'TEST_ONLY-ci-sources/v1','files':{name:{'sha256':'1'*64,'bytes':12} for name in m.MEMBERS}}
    raw=json.dumps(data).encode();pin=hashlib.sha256(raw).hexdigest()
    assert set(m.source_manifest(raw,pin))==set(m.MEMBERS)
    with pytest.raises(ValueError,match='reviewed'):
        m.source_manifest(raw,'0'*64)
    for mutation in ('../root.py','unknown.py'):
        changed=json.loads(raw);changed['files'][mutation]=changed['files'].pop('linux_guardian.py')
        altered=json.dumps(changed).encode()
        with pytest.raises(ValueError):m.source_manifest(altered,hashlib.sha256(altered).hexdigest())
    with pytest.raises(ValueError):m.check_member(data['files'],'linux_guardian.py',b'changed bytes')


def test_export_requires_exact_complete_bytes_and_never_treats_skip_as_pass():
    import json
    m=ci()
    outcome={'schema':'TEST_ONLY-ci-suite/v1','status':'SKIP','executed':False,
        'control_passed':False,'production_capture_accepted':False,'reason':'TEST_ONLY missing capacity'}
    stream=b''.join(m.export_frames({'suite/result.json':json.dumps(outcome).encode()},outcome))
    received=m.receive_export(stream)
    assert received['outcome']['status']=='SKIP'
    assert received['outcome']['control_passed'] is False
    assert set(received['files'])=={'suite/result.json'}
    for wrong in (stream.rsplit(b'\n',2)[0]+b'\n',stream.replace(b'c3RhdHVz',b'Z3RhdHVz',1)):
        if wrong!=stream:
            with pytest.raises(ValueError):m.receive_export(wrong)
    with pytest.raises(ValueError):list(m.export_frames({'../../etc/shadow':b'forbidden'},outcome))
    with pytest.raises(ValueError):list(m.export_frames({'suite/result.json':b'x'*(16*1024**2+1)},outcome))


def test_suite_admission_requires_every_serialized_subcase_inside_original_budget():
    import copy
    from test_linux_lease_control_admission import receipt
    from test_linux_lease_control import control
    m=ci();c=control();scenarios=[];clock=120.
    for name in ('baseline','boundaries','resources','supervisor-loss','guardian-loss','invalid-evidence'):
        row=receipt(name);shift=clock-100.
        row['started']+=shift;row['finished']+=shift
        for attempt in row['attempts']:
            attempt['started']+=shift;attempt['finished']+=shift
        scenarios.append(row);clock=row['finished']
    suite={'schema':'TEST_ONLY-ci-suite/v1','status':'PASS','executed':True,
        'control_passed':True,'production_capture_accepted':False,
        'started':100.,'deadline':1000.,'finished':clock,'scenarios':scenarios,'error':None}
    assert m.verify_suite(suite,c)['control_passed'] is True
    for mutation in ('missing','unremoved','reset','overlap','skip','late'):
        bad=copy.deepcopy(suite)
        if mutation=='missing':bad['scenarios'].pop()
        if mutation=='unremoved':bad['scenarios'][0]['attempts'][0]['outer']['removed']=False
        if mutation=='reset':bad['deadline']=1001.
        if mutation=='overlap':bad['scenarios'][1]['started']=120.
        if mutation=='skip':bad['scenarios'][0]['executed']=False
        if mutation=='late':bad['finished']=1001.
        with pytest.raises(ValueError):m.verify_suite(bad,c)
    forged=dict(suite,status='SKIP',executed=False,control_passed=False)
    with pytest.raises(ValueError):m.receive_export(b''.join(m.export_frames({'suite/result.json':m.canonical(suite)},forged)))


def test_existing_os_closure_must_cover_actual_loader_needed_and_loaded_aliases():
    m=ci()
    rows=[{'source':'/usr/bin/python3.12','target':'/usr/bin/python3.12','bytes':4096,'sha256':'1'*64,
           'elf':{'interpreter':'/lib/TEST_ONLY-ld.so','needed':['TEST_ONLY-libc.so']}},
          {'source':'/usr/lib/TEST_ONLY-ld.so','target':'/lib/TEST_ONLY-ld.so','bytes':4096,'sha256':'2'*64,
           'elf':{'interpreter':None,'needed':[]}},
          {'source':'/usr/lib/TEST_ONLY-libc.so','target':'/usr/lib/TEST_ONLY-libc.so','bytes':4096,'sha256':'3'*64,
           'elf':{'interpreter':None,'needed':[]}}]
    from test_linux_lease_control import control
    c=control()
    assert m.validate_os_closure(rows,{'/usr/bin/python3.12','/usr/lib/TEST_ONLY-libc.so'},c)['files']==3
    for bad,loaded in ((rows[:2],{'/usr/bin/python3.12'}),(rows,{'/home/runner/toolcache/python'}),
                       ([dict(rows[0],source='/home/runner/python'),*rows[1:]],{'/usr/bin/python3.12'}),
                       ([dict(rows[0],bytes=268435457),*rows[1:]],{'/usr/bin/python3.12'})):
        with pytest.raises(ValueError):m.validate_os_closure(bad,loaded,c)


def test_claimed_pass_export_cannot_replace_scenario_or_source_evidence():
    m=ci()
    fake={'schema':'TEST_ONLY-ci-suite/v1','status':'PASS','executed':True,'control_passed':True,
        'production_capture_accepted':False,'started':100.,'deadline':1000.,'finished':200.,'error':None,
        'scenarios':[]}
    stream=b''.join(m.export_frames({'suite/result.json':m.canonical(fake)},fake))
    with pytest.raises(ValueError,match='PASS|source|scenario'):m.receive_export(stream)


def test_workflow_root_payload_is_literal_pinned_and_has_no_checkout_execution():
    import ast,hashlib,json,yaml
    root=Path(__file__).parents[1];workflow=yaml.safe_load((root/'.github/workflows/twin.yml').read_text())
    steps=workflow['jobs']['determinism']['steps']
    step=next(row for row in steps if row.get('name')=='native tiny lease controls; no model')
    script=step['run'];payload=script.split("<<'FIXED_ROOT_BOOTSTRAP'\n",1)[1].split('\nFIXED_ROOT_BOOTSTRAP',1)[0]
    tree=ast.parse(payload);constants={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            try:constants[node.targets[0].id]=ast.literal_eval(node.value)
            except (ValueError,TypeError):pass
    raw=(root/'bench/pinned-candidate/linux_lease_control_ci_sources.json').read_bytes()
    assert constants['REVIEWED_MANIFEST']==hashlib.sha256(raw).hexdigest()
    m=ci();manifest=m.source_manifest(raw,constants['REVIEWED_MANIFEST'])
    for name in m.MEMBERS:m.check_member(manifest,name,(root/'bench/pinned-candidate'/name).read_bytes())
    assert "os.execve(STORE+'/source/linux_lease_control_ci_entry'" in payload
    assert "sudo -n -- /usr/bin/env -i" in script
    assert 'subtree_control' not in payload and 'os.system' not in payload and 'subprocess' not in payload
    assert step['if']=="runner.os == 'Linux'" and step['timeout-minutes']==17
    upload=next(row for row in steps if row.get('name')=='retain native tiny lease evidence')
    assert upload['timeout-minutes']==5 and upload['if']=="always() && runner.os == 'Linux'"
    assert upload['with']['if-no-files-found']=='error'
    assert set(workflow['jobs']['determinism']['strategy']['matrix']['include'][0])=={'os','arch'}


def test_ci_root_parent_is_fixed_and_does_not_change_legacy_or_production(monkeypatch):
    """Construction only, with explicit TEST_ONLY OS facts; no kernel proof."""
    import hashlib,json,struct
    from types import SimpleNamespace
    from test_linux_lease_control import control
    c=control();m=ci();raw=bytearray(64);raw[:16]=b'\x7fELF\x02\x01\x01'+b'\0'*9
    struct.pack_into('<HHIQQQIHHHHHH',raw,16,3,62,1,0,64,0,0,64,56,0,0,0,0)
    python=bytes(raw);data={m.STORE+'/source/'+name:b'TEST_ONLY source' for name in m.MEMBERS}
    data['/usr/bin/python3.12']=python
    rows=[{'source':name,'target':'/app/'+Path(name).name if name.startswith(m.STORE) else name,
        'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest(),'elf':c.elf_dependencies(value)} for name,value in data.items()]
    anchor=json.dumps({'schema':c.SCHEMA,'files':rows}).encode()
    paths=[]
    def metadata(name,regular=False):
        paths.append(name)
        return SimpleNamespace(st_dev=7,st_ino=sorted(data).index(name)+1 if name in data else 99)
    caller=SimpleNamespace(pid=201,start='77',uid=[1001]*4,verify=lambda:None)
    g=SimpleNamespace(protected_read=lambda name,*args,**kwargs:anchor if name==c.ANCHOR else data[name],
        protected_path=metadata,parse_set=lambda value:{2,3},parse_status=lambda value:{'Gid':'1001 1001 1001 1001'},
        candidate_unused=lambda uid,gid:None,storage_paths=lambda *args:('/var/lib',),
        reserve=lambda *args:{'host_memory_available':20000000000},observe_ancestors=lambda parent:[],
        effective_memory=lambda *args:20000000000,validate_reserve=lambda *args:None,
        verify_guardian_closure=lambda *args:None,digest=lambda value:hashlib.sha256(value).hexdigest(),MEMORY=12884901888,RESERVE=2147483648)
    nobody=SimpleNamespace(pw_name='nobody',pw_uid=65534,pw_gid=65534,pw_dir='/TEST_ONLY-no-home')
    monkeypatch.setattr(c.pwd,'getpwnam',lambda name:nobody);monkeypatch.setattr(c.pwd,'getpwall',lambda:[nobody])
    monkeypatch.setattr(c.grp,'getgrall',lambda:[SimpleNamespace(gr_name='nogroup',gr_gid=65534,gr_mem=[])])
    monkeypatch.setattr(c.os,'sched_getaffinity',lambda pid:{2,3},raising=False)
    monkeypatch.setattr(Path,'read_text',lambda path,*args,**kwargs:'memory cpu cpuset pids' if path.name=='cgroup.subtree_control' else '2-3')
    monkeypatch.setattr(Path,'exists',lambda path:False)
    monkeypatch.setattr(c,'__file__',m.STORE+'/source/linux_lease_control.py')
    monkeypatch.setattr(c.sys,'executable','/usr/bin/python3.12')
    host,profile,_=c.load_ci_control_host(g,'baseline',caller)
    assert host['cgroup_parent']=='/sys/fs/cgroup' and host['candidate_uid']==65534
    legacy,oldprofile,_=c.load_control_host(g,'baseline',caller)
    assert legacy['cgroup_parent']=='/sys/fs/cgroup/policy-as-versioned-flux-linux-control'
    assert oldprofile==profile
    with pytest.raises(ValueError):c.load_ci_control_host(g,'/arbitrary/cgroup',caller)
    from twin.linux_candidate import validate_profile
    with pytest.raises(ValueError):validate_profile(profile['config'])


def test_actual_discovery_closes_native_interpreter_dependencies_and_refuses_foreign_sources(monkeypatch):
    """Actual discovery algorithm, OS read facts are explicitly TEST_ONLY."""
    import struct
    from types import SimpleNamespace
    from test_linux_lease_control import control
    m=ci();c=control();python=bytearray(1024)
    python[:16]=b'\x7fELF\x02\x01\x01'+b'\0'*9
    struct.pack_into('<HHIQQQIHHHHHH',python,16,3,62,1,0,64,0,0,64,56,3,0,0,0)
    struct.pack_into('<IIQQQQQQ',python,64,1,4,0,0x400000,0,1024,1024,4096)
    loader=b'/lib/ld-fixture.so\0'
    struct.pack_into('<IIQQQQQQ',python,120,3,4,300,0,0,len(loader),len(loader),1);python[300:300+len(loader)]=loader
    struct.pack_into('<IIQQQQQQ',python,176,2,4,400,0,0,64,64,8)
    struct.pack_into('<qQqQqQqQ',python,400,1,0,5,0x400200,10,14,0,0);python[512:526]=b'libfixture.so\0'
    data={m.STORE+'/source/'+name:b'TEST_ONLY source' for name in m.MEMBERS}
    data.update({'/usr/bin/python3.12':bytes(python),'/usr/lib/ld-fixture.so':b'TEST_ONLY loader',
        '/usr/lib/libfixture.so':b'TEST_ONLY libc','/usr/lib/python3.12/test_only.py':b'TEST_ONLY stdlib'})
    observed=[SimpleNamespace(__file__='/usr/lib/python3.12/test_only.py')]
    class Modules(dict):
        def values(self):return observed
    import os,time
    monkeypatch.setattr(sys,'modules',Modules(sys.modules))
    maps=['/usr/bin/python3.12','/usr/lib/ld-fixture.so','/usr/lib/libfixture.so']
    monkeypatch.setattr(Path,'read_text',lambda path,*args,**kwargs:'\n'.join('00-01 r-xp 0 0 0 '+name for name in maps))
    monkeypatch.setattr(os.path,'realpath',lambda path:'/usr/lib/ld-fixture.so' if path=='/lib/ld-fixture.so' else path)
    monkeypatch.setattr(time,'monotonic',lambda:150.)
    g=SimpleNamespace(protected_path=lambda path,*args:SimpleNamespace(st_dev=8,st_ino=sorted(data).index(path)+1,st_size=len(data[path])),
        protected_read=lambda path,**kwargs:data[path])
    rows,facts=m.discover_closure(g,c,m.SuiteBudget(100.,1000.))
    assert next(row for row in rows if row['source']=='/usr/lib/ld-fixture.so')['target']=='/lib/ld-fixture.so'
    assert facts['files']==13 and facts['loaded_sources']==sorted(maps+['/usr/lib/python3.12/test_only.py'])
    data['/home/runner/toolcache/untrusted.py']=b'TEST_ONLY forbidden'
    observed.append(SimpleNamespace(__file__='/home/runner/toolcache/untrusted.py'))
    with pytest.raises(ValueError,match='OS/source'):m.discover_closure(g,c,m.SuiteBudget(100.,1000.))
    observed.pop();maps.append('/usr/lib/other/libfixture.so');data[maps[-1]]=b'TEST_ONLY ambiguous'
    with pytest.raises(ValueError,match='ambiguous'):m.discover_closure(g,c,m.SuiteBudget(100.,1000.))


def test_coordinator_serializes_all_twenty_and_aborts_before_next_leaf_on_failed_removal(monkeypatch,tmp_path):
    """TEST_ONLY kernel transport; checks orchestration, never kernel efficacy."""
    from types import SimpleNamespace
    from test_linux_lease_control import control
    from test_linux_lease_control_admission import receipt
    import time
    m=ci();c=control();clock=[120.];calls=[]
    monkeypatch.setattr(time,'monotonic',lambda:clock[0])
    def run(g,host,profile,caller,case,deadline,directory):
        scenario=profile['config']['scenario'];calls.append((scenario,case,deadline))
        row=next(row for row in receipt(scenario)['attempts'] if row['case']==case)
        row['started']=clock[0];clock[0]+=10.;row['finished']=clock[0]
        return row
    transport=SimpleNamespace(SCENARIOS=c.SCENARIOS,CASES=c.CASES,verify_result=c.verify_result,
        load_ci_control_host=lambda g,scenario,caller:({}, {'config':{'scenario':scenario}}, {'TEST_ONLY':True}),run_attempt=run)
    caller=SimpleNamespace(verify=lambda:None)
    result=m.execute_suite(None,transport,caller,m.SuiteBudget(100.,1000.),tmp_path)
    assert result['status']=='PASS' and result['production_capture_accepted'] is False
    assert len(calls)==20 and {row[2] for row in calls}=={1000.}
    assert calls[:5]==[('baseline','standard',1000.),('boundaries','standard',1000.),
        ('resources','standard',1000.),('resources','oom',1000.),('resources','pids',1000.)]
    failure_dir=tmp_path/'failure';failure_dir.mkdir();calls.clear();clock[0]=120.
    def unremoved(*args):
        row=run(*args);row['outer']['removed']=False;return row
    transport.run_attempt=unremoved
    failed=m.execute_suite(None,transport,caller,m.SuiteBudget(100.,1000.),failure_dir)
    assert failed['status']=='FAIL' and failed['control_passed'] is False and failed['executed'] is True
    assert calls==[('baseline','standard',1000.)]
    assert (failure_dir/'baseline-standard.json').is_file()


def test_pass_artifact_requires_every_original_journal_and_attempt_record():
    from test_linux_lease_control import control
    from test_linux_lease_control_admission import receipt
    m=ci();c=control();root=Path(__file__).parents[1];files={};rows=[];clock=120.
    for scenario in c.SCENARIOS:
        row=receipt(scenario);shift=clock-100.;row['started']+=shift;row['finished']+=shift
        for attempt in row['attempts']:
            attempt['started']+=shift;attempt['finished']+=shift
            files[f"cases/{scenario}/{attempt['case']}.json"]=m.canonical(attempt)
            files[f"cases/{scenario}/{attempt['case']}.jsonl"]=b'{"TEST_ONLY":"synthetic transport, no kernel credit"}\n'
        rows.append(row);clock=row['finished']
    outcome={'schema':'TEST_ONLY-ci-suite/v1','status':'PASS','executed':True,'control_passed':True,
        'production_capture_accepted':False,'started':100.,'deadline':1000.,'finished':clock,'error':None,'scenarios':rows}
    raw=(root/'bench/pinned-candidate/linux_lease_control_ci_sources.json').read_bytes()
    files.update({'suite/start.json':m.canonical({'started':100.,'deadline':1000.,'source_manifest_sha256':m.sha(raw)}),
        'suite/sources.json':raw,'suite/installation.json':b'{"TEST_ONLY":true}',
        'suite/host.json':b'{"TEST_ONLY":true}','suite/result.json':m.canonical(outcome)})
    for name in m.MEMBERS:files['source/'+name]=(root/'bench/pinned-candidate'/name).read_bytes()
    assert m.receive_export(b''.join(m.export_frames(files,outcome)))['production_capture_accepted'] is False
    files.pop('cases/resources/oom.jsonl')
    with pytest.raises(ValueError,match='journal|attempt'):m.receive_export(b''.join(m.export_frames(files,outcome)))


def test_transport_exit_cannot_leave_a_pass_or_convert_failure_to_skip():
    m=ci();passed={'status':'PASS','executed':True,'control_passed':True,'production_capture_accepted':False}
    assert m.native_disposition(passed,0,0)==passed
    for exitcode,receiver in ((1,0),(124,0),(0,1),(77,0)):
        result=m.native_disposition(passed,exitcode,receiver)
        assert result['control_passed'] is False and result['status']=='UNVERIFIED'
    skipped={'status':'SKIP','executed':False,'control_passed':False,'production_capture_accepted':False}
    assert m.native_disposition(skipped,77,0)==skipped
    failure={'status':'FAIL','executed':True,'control_passed':False,'production_capture_accepted':False}
    assert m.native_disposition(failure,1,1)==failure
    assert m.native_disposition(None,77,1)['status']=='UNVERIFIED'
    assert m.native_disposition(passed,False,0)['control_passed'] is False


def test_result_evidence_can_exceed_one_frame_without_truncating_actual_bytes():
    m=ci();outcome={'schema':'TEST_ONLY-ci-suite/v1','status':'FAIL','executed':True,
        'control_passed':False,'production_capture_accepted':False,
        'scenarios':[{'TEST_ONLY_original_evidence':'x'*70000}]}
    original=m.canonical(outcome)
    stream=b''.join(m.export_frames({'suite/result.json':original},outcome))
    assert m.receive_export(stream)['files']['suite/result.json']==original
    assert max(map(len,stream.splitlines()))<65536


def test_nonroot_local_export_cannot_outlive_original_whole_control_deadline(monkeypatch,tmp_path):
    import io,os,time
    from types import SimpleNamespace
    m=ci();outcome={'schema':'TEST_ONLY-ci-suite/v1','status':'SKIP','executed':False,
        'control_passed':False,'production_capture_accepted':False,'started':100.,'deadline':1000.,'finished':200.}
    stream=b''.join(m.export_frames({'suite/result.json':m.canonical(outcome)},outcome))
    monkeypatch.setattr(os,'geteuid',lambda:1001);monkeypatch.setattr(sys,'stdin',SimpleNamespace(buffer=io.BytesIO(stream)))
    monkeypatch.setattr(time,'monotonic',lambda:1001.);monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError,match='original|ceiling|deadline'):m.receiver_main()
    assert not (tmp_path/'native-outcome.json').exists()
