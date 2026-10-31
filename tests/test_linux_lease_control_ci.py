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
    irc=SimpleNamespace(pw_name='irc',pw_uid=39,pw_gid=39,pw_dir='/TEST_ONLY-no-irc-home')
    monkeypatch.setattr(c.pwd,'getpwnam',lambda name:irc if name=='irc' else nobody);monkeypatch.setattr(c.pwd,'getpwall',lambda:[nobody,irc])
    monkeypatch.setattr(c.grp,'getgrall',lambda:[SimpleNamespace(gr_name='nogroup',gr_gid=65534,gr_mem=[]),SimpleNamespace(gr_name='irc',gr_gid=39,gr_mem=[])])
    monkeypatch.setattr(c.os,'sched_getaffinity',lambda pid:{2,3},raising=False)
    monkeypatch.setattr(Path,'read_text',lambda path,*args,**kwargs:'memory cpu cpuset pids' if path.name=='cgroup.subtree_control' else '2-3')
    monkeypatch.setattr(Path,'exists',lambda path:False)
    monkeypatch.setattr(c,'__file__',m.STORE+'/source/linux_lease_control.py')
    monkeypatch.setattr(c.sys,'executable','/usr/bin/python3.12')
    host,profile,_=c.load_ci_control_host(g,'baseline',caller)
    assert host['cgroup_parent']=='/sys/fs/cgroup' and host['candidate_uid']==39 and host['candidate_gid']==39
    legacy,oldprofile,_=c.load_control_host(g,'baseline',caller)
    assert legacy['cgroup_parent']=='/sys/fs/cgroup/policy-as-versioned-flux-linux-control' and legacy['candidate_uid']==65534
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
    transport=SimpleNamespace(SCENARIOS=c.SCENARIOS,CASES=c.CASES,verify_result=c.verify_result,verify_attempt=c.verify_attempt,CiPrerequisiteUnavailable=c.CiPrerequisiteUnavailable,
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


def bootstrap_namespace():
    """Definitions only from reviewed literal; never execute privileged payload."""
    import ast,hashlib,json,os,stat,time,yaml
    workflow=yaml.safe_load((Path(__file__).parents[1]/'.github/workflows/twin.yml').read_text())
    script=next(row['run'] for row in workflow['jobs']['determinism']['steps'] if row.get('name')=='native tiny lease controls; no model')
    payload=script.split("<<'FIXED_ROOT_BOOTSTRAP'\n",1)[1].split('\nFIXED_ROOT_BOOTSTRAP',1)[0]
    tree=ast.parse(payload);scope={'os':os,'stat':stat,'time':time,'hashlib':hashlib,'json':json,'deadline':time.monotonic()+900}
    exec(compile(ast.Module(body=[node for node in tree.body if isinstance(node,ast.FunctionDef)],type_ignores=[]),'<TEST_ONLY-bootstrap-definitions>','exec'),scope)
    return scope,payload


def test_bootstrap_fifo_is_refused_without_waiting_for_a_writer(tmp_path):
    import os,subprocess
    scope,payload=bootstrap_namespace();os.mkfifo(tmp_path/'fifo')
    program='import ast,os,stat,time\ndeadline=time.monotonic()+900\nsource='+repr(payload)+'\n'
    program+="tree=ast.parse(source);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'TEST_ONLY','exec'))\n"
    program+='directory=os.open('+repr(str(tmp_path))+',os.O_RDONLY|os.O_DIRECTORY)\n'
    program+="try:readat(directory,'fifo')\nexcept ValueError:print('REFUSED_NONREGULAR')\nelse:raise AssertionError('FIFO accepted')\nfinally:os.close(directory)\n"
    result=subprocess.run([sys.executable,'-B','-I','-S','-c',program],capture_output=True,text=True,timeout=1)
    assert result.returncode==0 and result.stdout.strip()=='REFUSED_NONREGULAR'


def test_initial_source_integrity_failure_is_not_a_neutral_skip():
    import ast
    from types import SimpleNamespace
    m=ci();tree=ast.parse((Path(__file__).parents[1]/'bench/pinned-candidate/linux_lease_control_ci.py').read_text())
    main=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='suite_main')
    stage=next(node for node in main.body if isinstance(node,ast.Try) and any(
        isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='installed_module' for call in ast.walk(node)))
    class MissingNative(ValueError):pass
    control=SimpleNamespace(ci_principal_facts=lambda *args:None,CiPrerequisiteUnavailable=MissingNative,CiPrincipalRejected=type("PrincipalRejected",(ValueError,),{}))
    def namespace(error):
        def refused(*args):raise error
        return {'time':SimpleNamespace(monotonic=lambda:150.),'budget':m.SuiteBudget(100.,1000.),
            'control':control,'g':None,'caller':None,'installed_module':refused,'manifest':{},'base':{},'outcome':None,
            'PrerequisiteUnavailable':m.PrerequisiteUnavailable,'persist_observation':lambda *args:None,
            'Path':Path,'STORE':m.STORE,'canonical':m.canonical}
    code=compile(ast.Module(body=[stage],type_ignores=[]),'TEST_ONLY-initial-stage','exec')
    for error in (ValueError('actual source member bytes differ from reviewed manifest'),
                  PermissionError('protected source discretionary ACL'),KeyError('required source pin')):
        with pytest.raises(type(error)):exec(code,namespace(error))
    scope=namespace(m.PrerequisiteUnavailable('four controllers not already enabled'))
    exec(code,scope)
    assert scope['outcome']['status']=='SKIP' and scope['outcome']['control_passed'] is False


def test_bootstrap_alarm_uses_remaining_original_clock_without_installing_a_timer():
    from types import SimpleNamespace
    scope,payload=bootstrap_namespace();calls=[]
    scope.update(deadline=1000.,time=SimpleNamespace(monotonic=lambda:700.),
        signal=SimpleNamespace(SIGALRM=14,SIG_DFL=0,ITIMER_REAL=0,SIG_UNBLOCK=1,
            signal=lambda *args:calls.append(args),pthread_sigmask=lambda *args:calls.append(args),setitimer=lambda *args:calls.append(args)))
    scope['arm_budget']()
    assert calls==[(14,0),(1,{14}),(0,300.)]
    scope['time']=SimpleNamespace(monotonic=lambda:991.)
    with pytest.raises(ValueError,match='original900'):scope['arm_budget']()
    assert payload.index('\narm_budget()')<payload.index("manifest_raw=readat(")


def test_observed_prerequisites_are_persisted_before_export_and_survive_later_failure(monkeypatch,tmp_path):
    import hashlib
    from types import SimpleNamespace
    m=ci();monkeypatch.setattr(m,'STORE',str(tmp_path));base={};reads=[]
    def protected(path,pin,maximum):
        raw=Path(path).read_bytes();reads.append(path)
        assert hashlib.sha256(raw).hexdigest()==pin and len(raw)<=maximum
        return raw
    g=SimpleNamespace(protected_path=lambda *args:None,protected_read=protected)
    record={'TEST_ONLY':True,'native_maps_sha256':'1'*64,'caller':{'pid':201,'start':'77'}}
    m.persist_observation(g,base,'suite/installation.json',record)
    original=(tmp_path/'ci-evidence/installation.json').read_bytes()
    assert original==m.canonical(record)+b'\n' and base['suite/installation.json']==original and len(reads)==1
    try:raise RuntimeError('TEST_ONLY later export failure')
    except RuntimeError:pass
    assert (tmp_path/'ci-evidence/installation.json').read_bytes()==original
    with pytest.raises(ValueError):m.persist_observation(g,base,'../../private.json',record)
    with pytest.raises(FileExistsError):m.persist_observation(g,base,'suite/installation.json',record)


def test_missing_required_terminal_aborts_before_the_next_subcase(monkeypatch,tmp_path):
    from types import SimpleNamespace
    from test_linux_lease_control import control
    from test_linux_lease_control_admission import receipt
    import time
    m=ci();c=control();calls=[];clock=[120.]
    monkeypatch.setattr(time,'monotonic',lambda:clock[0])
    def run(g,host,profile,caller,case,deadline,directory):
        calls.append(case);row=next(row for row in receipt('invalid-evidence')['attempts'] if row['case']==case)
        row['started']=clock[0];clock[0]+=10.;row['finished']=clock[0]
        if case=='eof':row['guardian_terminal']=None
        return row
    transport=SimpleNamespace(SCENARIOS=('invalid-evidence',),CASES=c.CASES,verify_result=c.verify_result,CiPrerequisiteUnavailable=c.CiPrerequisiteUnavailable,
        load_ci_control_host=lambda *args:({}, {'config':{'scenario':'invalid-evidence'}}, {}),run_attempt=run)
    if hasattr(c,'verify_attempt'):transport.verify_attempt=c.verify_attempt
    result=m.execute_suite(None,transport,SimpleNamespace(verify=lambda:None),m.SuiteBudget(100.,1000.),tmp_path)
    assert result['status']=='FAIL' and calls==['eof']
    assert 'terminal' in result['error'] and (tmp_path/'invalid-evidence-eof.json').is_file()


def test_bootstrap_reads_back_protected_manifest_and_every_copy_before_first_exec(tmp_path):
    import hashlib,json
    scope,payload=bootstrap_namespace();m=ci();sources={name:b'TEST_ONLY '+name.encode() for name in m.MEMBERS}
    raw=m.canonical({'schema':'TEST_ONLY-ci-sources/v1','files':{name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in sources.items()}})+b'\n'
    (tmp_path/'source').mkdir();(tmp_path/'source-manifest.json').write_bytes(raw)
    for name,data in sources.items():(tmp_path/'source'/name).write_bytes(data)
    scope.update(STORE=str(tmp_path),NAMES=m.MEMBERS,REVIEWED_MANIFEST=hashlib.sha256(raw).hexdigest(),safe=lambda *args:None)
    scope['verify_installed'](raw,sources)
    (tmp_path/'source/linux_lease_control_ci_entry').write_bytes(b'TEST_ONLY changed installed entry')
    with pytest.raises(ValueError,match='installed|copy|bytes'):scope['verify_installed'](raw,sources)
    assert payload.rindex('verify_installed(manifest_raw,sources)')<payload.index('os.execve(')


def test_public_ci_context_is_bound_annotation_and_never_an_authority_or_path_selector():
    m=ci();context={'schema':'TEST_ONLY-ci-context/v1','source_manifest_sha256':'1'*64,
        'workflow_run':{'repository':'TEST_ONLY/repository','workflow':'twin','job':'determinism','run_id':'123',
            'attempt':'2','source_commit':'a'*40,'event':'pull_request','arch':'x86_64-linux','runner_label':'ubuntu-24.04'}}
    assert m.workflow_context(m.canonical(context),'1'*64)==context
    for bad in (dict(context,source_manifest_sha256='2'*64),dict(context,root_path='/root'),
                dict(context,workflow_run=dict(context['workflow_run'],job='unreviewed-job'))):
        with pytest.raises(ValueError):m.workflow_context(m.canonical(bad),'1'*64)


def test_initial_stage_keeps_observed_kernel_and_principal_when_later_discovery_fails(monkeypatch,tmp_path):
    import ast,hashlib
    from types import SimpleNamespace
    m=ci();monkeypatch.setattr(m,'STORE',str(tmp_path));base={}
    def protected(path,pin,maximum):
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('protected original changed')
        return raw
    g=SimpleNamespace(protected_path=lambda *args:None,protected_read=protected)
    tree=ast.parse((Path(__file__).parents[1]/'bench/pinned-candidate/linux_lease_control_ci.py').read_text())
    main=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='suite_main')
    stage=next(node for node in main.body if isinstance(node,ast.Try) and any(
        isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='installed_module' for call in ast.walk(node)))
    class MissingNative(ValueError):pass
    def refused(*args):raise ValueError('TEST_ONLY later native mapping integrity refusal')
    scope={'time':SimpleNamespace(monotonic=lambda:150.),'budget':m.SuiteBudget(100.,1000.),'g':g,'caller':None,
        'control':SimpleNamespace(ci_principal_facts=lambda *args:{'TEST_ONLY_principal':65534},CiPrerequisiteUnavailable=MissingNative,CiPrincipalRejected=type("PrincipalRejected",(ValueError,),{})),
        'installed_module':lambda *args:None,'manifest':{},'base':base,'outcome':None,
        'PrerequisiteUnavailable':m.PrerequisiteUnavailable,'persist_observation':m.persist_observation,
        'admit_ci_root':lambda *args:{'TEST_ONLY_controllers':['memory','cpu','cpuset','pids']},
        'discover_closure':refused,'Path':Path,'STORE':str(tmp_path),'canonical':m.canonical}
    with pytest.raises(ValueError,match='mapping integrity'):exec(compile(ast.Module(body=[stage],type_ignores=[]),'TEST_ONLY-stage','exec'),scope)
    assert set(base)=={'suite/principal.json','suite/kernel.json'}
    assert (tmp_path/'ci-evidence/kernel.json').read_bytes()==base['suite/kernel.json']
    (tmp_path/'ci-evidence/kernel.json').chmod(0o600);(tmp_path/'ci-evidence/kernel.json').write_bytes(b'TEST_ONLY tampered original')
    with pytest.raises(ValueError,match='changed'):m.owned_exports(g,base,None,{'status':'FAIL'},m.SuiteBudget(100.,1000.))


def test_initial_missing_fixed_cgroup_root_is_typed_absence_but_unsafe_root_is_failure():
    import errno
    from types import SimpleNamespace
    m=ci()
    def absent(path,*args):
        assert path=='/sys/fs/cgroup'
        raise FileNotFoundError(errno.ENOENT,'TEST_ONLY fixed root absent',path)
    with pytest.raises(m.PrerequisiteUnavailable) as caught:m.admit_ci_root(SimpleNamespace(protected_path=absent))
    assert caught.value.facts['path']=='/sys/fs/cgroup'
    assert caught.value.facts['error_type']=='FileNotFoundError' and caught.value.facts['errno']==errno.ENOENT
    def unsafe(path,*args):raise PermissionError(errno.EACCES,'TEST_ONLY unsafe root ACL',path)
    with pytest.raises(PermissionError):m.admit_ci_root(SimpleNamespace(protected_path=unsafe))


def test_initial_missing_fixed_ci_account_is_typed_without_converting_later_identity_or_integrity_errors(monkeypatch):
    from types import SimpleNamespace
    from test_linux_lease_control import control
    c=control()
    def absent(name):
        assert name in ('irc','nobody')
        raise KeyError('TEST_ONLY existing nobody absent')
    monkeypatch.setattr(c.pwd,'getpwnam',absent)
    with pytest.raises(c.CiPrerequisiteUnavailable) as caught:c.ci_principal_facts(None,None)
    assert caught.value.facts['name']=='irc' and caught.value.facts['args']==['TEST_ONLY existing nobody absent']
    with pytest.raises(KeyError):c.principal_facts(None,None)
    monkeypatch.setattr(c.pwd,'getpwnam',lambda name:SimpleNamespace(pw_uid=65534,pw_gid=65534))
    monkeypatch.setattr(c.pwd,'getpwall',lambda:[]);monkeypatch.setattr(c.grp,'getgrall',lambda:[])
    monkeypatch.setattr(Path,'read_text',lambda *args,**kwargs:'TEST_ONLY caller metadata')
    for error in (ValueError('TEST_ONLY active/shared principal'),KeyError('TEST_ONLY malformed later identity fact')):
        def failed(*args):raise error
        g=SimpleNamespace(parse_status=lambda value:{'Gid':'1001'},candidate_unused=failed)
        with pytest.raises(type(error)):c.ci_principal_facts(g,SimpleNamespace(pid=201,uid=[1001]*4))


def test_poststart_capacity_failure_retains_current_raw_admission_facts_before_export(monkeypatch,tmp_path):
    import copy,hashlib,json,time
    from types import SimpleNamespace
    from test_linux_lease_control import control
    from test_linux_lease_control_admission import receipt
    m=ci();c=control();monkeypatch.setattr(m,'STORE',str(tmp_path));clock=[120.];calls=[]
    monkeypatch.setattr(time,'monotonic',lambda:clock[0])
    facts={'TEST_ONLY':True,'memory_available':123,'disk_free':456,
        'ancestors':[{'TEST_ONLY_raw':'current-low-admission'}],'raw_marker':'TEST_ONLY-original-failed-current-capacity'}
    expected=copy.deepcopy(facts)
    def load(g,scenario,caller):
        calls.append(scenario)
        if scenario=='boundaries':raise c.CiPrerequisiteUnavailable('TEST_ONLY current capacity lost',facts)
        return {},{'config':{'scenario':scenario}},{}
    def run(*args):
        row=receipt('baseline')['attempts'][0];row['started']=120.;row['finished']=130.;clock[0]=130.;return row
    def protected(path,pin=None,maximum=16*1024**2):
        raw=Path(path).read_bytes()
        if pin is not None and hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('original capacity bytes changed')
        return raw
    g=SimpleNamespace(protected_path=lambda *args:None,protected_read=protected)
    transport=SimpleNamespace(SCENARIOS=('baseline','boundaries'),CASES=c.CASES,CiPrerequisiteUnavailable=c.CiPrerequisiteUnavailable,
        load_ci_control_host=load,run_attempt=run,verify_attempt=c.verify_attempt,verify_result=c.verify_result)
    directory=tmp_path/'attempts';directory.mkdir()
    outcome=m.execute_suite(g,transport,SimpleNamespace(verify=lambda:None),m.SuiteBudget(100.,1000.),directory)
    assert outcome['status']=='FAIL' and outcome['executed'] is True and calls==['baseline','boundaries']
    reference=outcome['admission_failure'];raw=(tmp_path/'ci-evidence/admission-failure.json').read_bytes();saved=json.loads(raw)
    assert saved['facts']==expected and saved['scenario']=='boundaries' and saved['phase']=='host-admission'
    assert saved['started']==100. and saved['deadline']==1000. and saved['observed_monotonic']==130.
    assert reference=={'name':'suite/admission-failure.json','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    facts['raw_marker']='TEST_ONLY later mutation';assert json.loads(raw)['facts']==expected
    files=m.owned_exports(g,{},directory,outcome,m.SuiteBudget(100.,1000.))
    assert files['suite/admission-failure.json']==raw
    assert m.receive_export(b''.join(m.export_frames(files,outcome)))['outcome']['status']=='FAIL'
    files.pop('suite/admission-failure.json')
    with pytest.raises(ValueError,match='admission|original'):m.receive_export(b''.join(m.export_frames(files,outcome)))


@pytest.mark.parametrize('absent',('root','nobody'))
def test_initial_literal_absence_is_neutral_skip_with_original_absence_record(monkeypatch,tmp_path,absent):
    import ast,errno,hashlib,time
    from types import SimpleNamespace
    from test_linux_lease_control import control
    m=ci();c=control();monkeypatch.setattr(m,'STORE',str(tmp_path));monkeypatch.setattr(time,'monotonic',lambda:150.);base={}
    def metadata(path,*args):
        if path=='/sys/fs/cgroup':raise FileNotFoundError(errno.ENOENT,'TEST_ONLY fixed root absent',path)
    def protected(path,pin,maximum):
        raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin;return raw
    g=SimpleNamespace(protected_path=metadata,protected_read=protected)
    if absent=='root':monkeypatch.setattr(c,'ci_principal_facts',lambda *args:{'TEST_ONLY_principal':65534})
    else:
        def missing(name):
            assert name in ('irc','nobody')
            raise KeyError('TEST_ONLY nobody genuinely absent')
        monkeypatch.setattr(c.pwd,'getpwnam',missing)
    tree=ast.parse((Path(__file__).parents[1]/'bench/pinned-candidate/linux_lease_control_ci.py').read_text())
    main=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='suite_main')
    stage=next(node for node in main.body if isinstance(node,ast.Try) and any(
        isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='installed_module' for call in ast.walk(node)))
    scope={'time':time,'budget':m.SuiteBudget(100.,1000.),'g':g,'caller':None,'control':c,'installed_module':lambda *args:None,
        'manifest':{},'base':base,'outcome':None,'PrerequisiteUnavailable':m.PrerequisiteUnavailable,
        'persist_observation':m.persist_observation,'admit_ci_root':m.admit_ci_root}
    exec(compile(ast.Module(body=[stage],type_ignores=[]),'TEST_ONLY-initial-absence-stage','exec'),scope)
    assert scope['outcome']['status']=='SKIP' and scope['outcome']['executed'] is False
    assert scope['outcome']['control_passed'] is False and scope['outcome']['deadline']==1000.
    import json
    original=(tmp_path/'ci-evidence/availability.json').read_bytes()
    facts=json.loads(original);assert base['suite/availability.json']==original
    assert facts['error_type']==('FileNotFoundError' if absent=='root' else 'KeyError')
    assert facts.get('path',facts.get('name'))==('/sys/fs/cgroup' if absent=='root' else 'irc')
