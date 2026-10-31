"""Pure comparison DATA controls: never launches a target or observes a real host."""
import copy
from typing import Any, cast
import pytest
from twin import source_metadata as sm
from twin import pdf_comparison_capture as c


def test_copied_public_packets_are_never_actual_capture_authority():
    with pytest.raises(ValueError, match='private'):
        c.capture_baseline(cast(Any,{}), {}, {})


def test_original_budgets_are_checked_before_any_launch():
    c.admit_slot(elapsed_ns=0, slots_used=0, retained_bytes=0, reserve_bytes=1024)
    invalid: list[dict[str, Any]]=[dict(elapsed_ns=10700*10**9),dict(slots_used=52),dict(retained_bytes=8*1024**3),dict(elapsed_ns=True)]
    for args in invalid:
        values=dict(elapsed_ns=0,slots_used=0,retained_bytes=0,reserve_bytes=1024);values.update(args)
        with pytest.raises(ValueError): c.admit_slot(**values)


def event_fixture():
    from test_source_native_observation import fixture
    obs,archive=fixture();events=obs['events'];events[-1]['at_ns']=12000
    for fd,name in [(1,'stdout'),(2,'stderr')]:
        events.insert(-1,{'seq':0,'at_ns':9000+fd*1000,'kind':'pipe-eof','data':{'channel':name,'fd':fd,'generation':0,'identity':[2,20+fd],'request_bytes':65536,'result':0,'captured_bytes':6 if fd==1 else 0}})
    for i,row in enumerate(events):row['seq']=i
    events[2]['data']['fds']=copy.deepcopy(events[0]['data']['fds'])
    terminal=events[-1]['data'];terminal['wait']={'kind':'exited','raw_status':0,'exit_code':0,'observed_at_ns':9000}
    terminal['custody']['grace_deadline']=102.00001;terminal['custody']['cleanup_ended']=100.000011
    obs['schema']='TEST_ONLY-pdf-baseline-events/v1';obs['scope']=c.DATA_SCOPE
    obs['spec']['schema']='TEST_ONLY-pdf-baseline-spec/v1';obs['spec']['profile']=c.DATA_SCOPE
    obs['run']={'started_at':'2026-10-31T00:00:00+00:00','ended_at':'2026-10-31T00:00:00.000012+00:00','monotonic_start_ns':100000000000,'elapsed_ns':12000,'wall_deadline_ns':220000000000,'cleanup_started_ns':100000010000,'cleanup_deadline_ns':102000010000}
    return obs,archive


def test_simulated_data_checks_two_eof_wait_custody_without_creating_a_native_handle():
    obs,archive=event_fixture()
    result=c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')
    assert result['stdout_bytes']==6 and result['stderr_bytes']==0
    assert result['qualification']=='NONE'


@pytest.mark.parametrize('mutation',['origin','unknown-field','missing-eof','zero-read','wrong-pipe','wrong-generation','early-eof','early-wait','late-wait','raw-wait','no-reap','deadline','alias','wrong-write'])
def test_comparison_nearby_invalid_histories_are_refused(mutation):
    obs,archive=event_fixture();events=obs['events']
    if mutation=='origin':events[0]['data']['fds'].append({'fd':3,'kind':'pdf-origin','identity':[2,23]})
    if mutation=='unknown-field':obs['origin_sha256']='a'*64
    if mutation=='missing-eof':events.pop(-2)
    if mutation=='zero-read':events[-2]['data']['request_bytes']=0
    if mutation=='wrong-pipe':events[-2]['data']['identity']=[2,999]
    if mutation=='wrong-generation':events[-2]['data']['generation']=1
    if mutation=='early-eof':events.insert(4,events.pop(-2))
    if mutation=='early-wait':events[-1]['data']['wait']['observed_at_ns']=0
    if mutation=='late-wait':events[-1]['data']['wait']['observed_at_ns']=11000
    if mutation=='raw-wait':events[-1]['data']['wait']['raw_status']=256
    if mutation=='no-reap':events[-1]['data']['custody']['direct_child_reaped']=False
    if mutation=='deadline':obs['run']['wall_deadline_ns']+=1
    if mutation=='alias':events[4]['data']={'nr':33,'args':[1,3,0,0,0,0],'detail':{}}
    if mutation=='wrong-write':events[5]['data']['result']=5
    for i,row in enumerate(events):row['seq']=i
    with pytest.raises(ValueError):c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')


PDF01_B64='JVBERi0xLjcKJSBURVNUX09OTFkgaW52ZW50ZWQgc3ludGhldGljIHRlY2huaWNhbCBmaXh0dXJlCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvQ291bnQgMSAvS2lkcyBbNSAwIFJdID4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyA+PgplbmRvYmoKNCAwIG9iago8PCAvTGVuZ3RoIDQyID4+CnN0cmVhbQpCVCAvRjEgMTIgVGYgMSAwIDAgMSA3MiAyNDAgVG0gKEFCKSBUaiBFVAoKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgMzAwIDMwMF0gL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgMyAwIFIgPj4gPj4gL0NvbnRlbnRzIDQgMCBSID4+CmVuZG9iago2IDAgb2JqCjw8IC9UaXRsZSAoVEVTVF9PTkxZIDAxLW9uZS1mcmFnbWVudCkgL1Byb2R1Y2VyIChURVNUX09OTFkgb3duIGRldGVybWluaXN0aWMgc2VyaWFsaXplcikgL1N1YmplY3QgKEludmVudGVkIHRlY2huaWNhbCBmaXh0dXJlOyBubyBwdWJsaWNhdGlvbiBjbGFpbSkgPj4KZW5kb2JqCnhyZWYKMCA3CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTA3IDAwMDAwIG4gCjAwMDAwMDAxNjQgMDAwMDAgbiAKMDAwMDAwMDI2MSAwMDAwMCBuIAowMDAwMDAwMzUzIDAwMDAwIG4gCjAwMDAwMDA0NzkgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA3IC9Sb290IDEgMCBSIC9JbmZvIDYgMCBSID4+CnN0YXJ0eHJlZgo2NDYKJSVFT0YK'


def prepared_fixture():
    import base64
    from test_source_native_observation import fixture
    obs,archive=fixture()
    def blob(raw):
        pin=sm.sha256(raw);archive[pin]=raw;return {'sha256':pin,'bytes':len(raw)}
    def record(value):return blob(sm.canonical(value))['sha256']
    config=blob(b'');pdf=blob(base64.b64decode(PDF01_B64));recipe=blob(b'TEST_ONLY identical frozen toolchain and flags')['sha256']
    configuration=blob(b'TEST_ONLY frozen build configuration')['sha256'];exe={k:obs['files']['/bin/tool'][k] for k in ('sha256','bytes')}
    rows=obs['spec']['candidates'];inventory=blob(sm.canonical(rows))['sha256']
    left={'schema':'TEST_ONLY-pdf-comparison-build-selection/v1','variant':'pristine','source_archive_sha256':c.ARCHIVE,'patch_sha256':None,'prepared_tree_sha256':'c'*64,'toolchain_recipe_sha256':recipe,'configuration_recipe_sha256':configuration,'executable':exe,'dependency_inventory_sha256':inventory}
    right={'schema':'twin.native-build-identity/v1','source_archive_sha256':c.ARCHIVE,'source_package_sha256':blob(b'TEST_ONLY package')['sha256'],'patch_sha256':c.PATCH,'prepared_tree_sha256':blob(b'TEST_ONLY tree')['sha256'],'build_configuration_sha256':configuration,'toolchain_sha256':recipe,'build_log_sha256':blob(b'TEST_ONLY never built')['sha256'],'executable_sha256':exe['sha256'],'executable_bytes':exe['bytes'],'target':{'system':'Linux','machine':'x86_64','elf_class':64}}
    pair={'schema':'TEST_ONLY-pdf-pair-plan/v1','purpose':'TEST_ONLY','fixture_id':c.FIXTURES[0][0],'fixture':pdf,'config':config,'resource':None,'archive_sha256':c.ARCHIVE,'patch_sha256':c.PATCH,'build_pair':{'pristine_build_sha256':record(left),'patched_build_sha256':record(right),'pristine_executable':exe,'patched_executable':exe,'same_toolchain_recipe_sha256':recipe,'accepted_differences_sha256':blob(b'TEST_ONLY reviewed fixed differences')['sha256']},'schedule_index':0,'suite_selection_sha256':blob(b'TEST_ONLY suite selection')['sha256']}
    prepared=c.prepare_comparison_plan(pair,base64.b64decode(PDF01_B64),archive,executable_path='/bin/tool',candidate_inventory=rows,recorder_inventory=rows)
    return pair,prepared['plan'],prepared['archive']


def complete_data_fixture():
    pair,plan,archive=prepared_fixture();obs,trace_archive=event_fixture();archive.update(trace_archive)
    obs['spec']['plan_sha256']=sm.sha256(sm.canonical(plan))
    obs['spec']['candidates']=c._candidate_rows(plan,archive,'/work')
    def put(value):raw=sm.canonical(value);pin=sm.sha256(raw);archive[pin]=raw;return pin
    initial=obs['events'][0]['data'];clock=obs['run'];terminal=obs['events'][-1]['data']
    invocation={'schema':'twin.source-extraction-invocation/v1','argv':obs['spec']['argv'],'cwd':'/work','environment':dict(c.migration.ENVIRONMENT),'stdin':'OWNED-EOF-PIPE'}
    invocation_pin=put(invocation)
    run_id=sm.sha256(sm.canonical({'plan_sha256':sm.sha256(sm.canonical(plan)),'invocation_sha256':invocation_pin,'started_at':clock['started_at'],'monotonic_start_ns':clock['monotonic_start_ns'],'process':{k:initial[k] for k in ('pid','starttime','ppid','uid','gid')}}))
    data={'schema':'TEST_ONLY-pdf-baseline-capture-data/v1','purpose':'TEST_ONLY','observation_mode':'SIMULATED_DATA','plan_sha256':sm.sha256(sm.canonical(plan)),'pair_plan_sha256':plan['pair_plan_sha256'],'host_policy_sha256':None,'host_evidence_sha256':None,'run_id':run_id,'invocation_sha256':invocation_pin,'process_sha256':put(initial),'run_clock_sha256':put(clock),'native_events_sha256':put(obs),'dependency_observation_sha256':put(obs['files']),'stdout':{'captured':{'sha256':terminal['stdout_sha256'],'bytes':6},'observed_bytes_lower_bound':6,'complete':True,'original_descriptor':1,'generation':0,'identity':[2,21],'eof_event_seq':8},'stderr':{'captured':{'sha256':terminal['stderr_sha256'],'bytes':0},'observed_bytes_lower_bound':0,'complete':True,'original_descriptor':2,'generation':0,'identity':[2,22],'eof_event_seq':9},'terminal_wait':{**terminal['wait'],'provenance':'natural_terminal'},'custody_sha256':put(terminal['custody']),'cleanup':'removed','intervention':'none','status':'COMPLETE_EXIT0_DATA','failure':None}
    return pair,plan,data,archive


def test_complete_simulated_pair_is_data_and_keeps_actual_suite_stopped():
    pair,plan,data,archive=complete_data_fixture()
    assert c.check_comparison_capture(data,archive,expected_plan=plan)['qualification']=='NONE'
    result=c.compare_simulated_pair(pair,data,archive,plan,copy.deepcopy(data),archive,plan)
    assert (result['stdout_equal'],result['stderr_equal'],result['exit_equal'])==(True,True,True)
    assert result['status']=='MATCH' and result['stop_suite'] is True and result['qualification']=='NONE'
    with pytest.raises(ValueError,match='private'):c.compare_pair(pair,data)


@pytest.mark.parametrize('field',['fixture_id','fixture','config','resource','archive_sha256','patch_sha256','build_pair','schedule_index','suite_selection_sha256'])
def test_substituted_or_unknown_pair_selection_never_changes_the_frozen_plan(field):
    pair,plan,archive=prepared_fixture();changed=copy.deepcopy(plan)
    mutated=copy.deepcopy(pair);mutated[field]={} if field=='resource' else None
    raw=sm.canonical(mutated);pin=sm.sha256(raw);archive[pin]=raw;changed['pair_plan_sha256']=pin
    rows=sm._json(archive[plan['candidate_inventory_sha256']])
    with pytest.raises((ValueError,TypeError)):c.prepare_comparison_plan(mutated,archive[pair['fixture']['sha256']],archive,executable_path='/bin/tool',candidate_inventory=rows,recorder_inventory=rows)


@pytest.mark.parametrize('field',['purpose','plan_sha256','pair_plan_sha256','host_policy_sha256','run_id','process_sha256','run_clock_sha256','invocation_sha256','native_events_sha256','dependency_observation_sha256','custody_sha256','cleanup','intervention','terminal_wait'])
def test_complete_data_cannot_replace_independently_bound_run_facts(field):
    pair,plan,data,archive=complete_data_fixture();data[field]='a'*64 if field=='host_policy_sha256' else None
    with pytest.raises((ValueError,TypeError)):c.check_comparison_capture(data,archive,expected_plan=plan)


def test_invalid_public_comparison_inputs_do_not_call_a_native_target(monkeypatch):
    calls=[]
    monkeypatch.setattr(c,'_linux_run_comparison',lambda *a,**k:calls.append('BAD'))
    monkeypatch.setattr(c.migration,'_execute_prepared_extraction',lambda *a,**k:calls.append('BAD'))
    for fake in ({},None,object()):
        with pytest.raises(ValueError):c.capture_baseline(cast(Any,fake),{}, {})
        with pytest.raises(ValueError):c.capture_patched_comparison(cast(Any,fake),cast(Any,{}),cast(Any,fake),{},b'')
    assert calls==[]


class GuardModel:
    def verify(self):pass


def test_fixed_native_collector_with_fully_mocked_kernel_retains_both_actual_shaped_channels(monkeypatch):
    """No child, proc access, signal, descriptor or kernel operation is performed."""
    import types
    from test_source_native_observation import fixture
    obs,archive=fixture();initial=obs['events'][0]['data'];maps=obs['events'][2]['data']['maps']
    facts=obs['files'];clock=[100.0];waits=[0];reads={12:[b'hello\n',b''],14:[b'']};ptrace=[]
    def tick():clock[0]+=.0001;return clock[0]
    policy={'schema':'twin.native-host-policy/v1','scope':c.n.SCOPE,'custodian':'PURE MOCK, NO HOST SELECTED','not_before':'2026-10-31T00:00:00+00:00','not_after':'2026-10-31T00:05:00+00:00','roots':['/bin','/lib','/data'],'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':[sm.sha256(b'PURE MOCK evidence')]}
    archive[sm.sha256(b'PURE MOCK evidence')]=b'PURE MOCK evidence'
    context=object.__new__(c.n.NativeHostContext)
    for key,value in {'_policy':sm.canonical(policy),'_evidence':{sm.sha256(b'PURE MOCK evidence'):b'PURE MOCK evidence'},'_guard':GuardModel()}.items():object.__setattr__(context,key,value)
    authority=object.__new__(c.ComparisonCaptureAuthority)
    for key,value in {'_context':context,'_guard':GuardModel(),'_selected_at':100.0,'_suite_started':100.0}.items():object.__setattr__(authority,key,value)
    fdrows={20:'/bin/tool',21:'/lib/loader',22:'/data'}
    def info(path):
        if '/fd/' in path:
            fd=int(path.rsplit('/',1)[1]);values=[2,20+fd,0o100600,1000,1000,1,0,1,1]
        else:values=facts[path]['identity']
        return types.SimpleNamespace(**dict(zip(('st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_mtime_ns','st_ctime_ns'),values)))
    class FakePath:
        def __init__(self,value):self.value=str(value)
        def __truediv__(self,part):return FakePath(self.value+'/'+str(part))
        def __str__(self):return self.value
        def __fspath__(self):return self.value
        def stat(self):return info(self.value)
        def iterdir(self):return [FakePath('PURE MOCK thread')]
    class SelectorModel:
        def __init__(self):self.items={}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def register(self,fd,event,data):self.items[fd]=types.SimpleNamespace(fd=fd,data=data)
        def unregister(self,fd):del self.items[fd]
        def get_map(self):return self.items
        def select(self,timeout):
            if waits[0]>=8:return [(key,None) for key in list(self.items.values())]
            if waits[0]>=6 and len(reads[12])==2 and 12 in self.items:return [(self.items[12],None)]
            return []
    statuses=[(100,19<<8|127),(100,133<<8|127),(100,4<<16|5<<8|127),(100,133<<8|127),(100,133<<8|127),(100,133<<8|127),(100,133<<8|127),(100,6<<16|5<<8|127),(100,0)]
    calls=[{'op':'enter','nr':59,'args':[0]*6},{'op':'leave','result':0},{'op':'enter','nr':1,'args':[1,0,6,0,0,0]},{'op':'leave','result':6},{'op':'enter','nr':231,'args':[0]*6}]
    def waitpid(*args):value=statuses[waits[0]];waits[0]+=1;return value
    def detail(stop,*args):return copy.deepcopy(obs['events'][1 if stop['nr']==59 else 4 if stop['nr']==1 else 6]['data']['detail'])
    pipes=iter([(10,11),(12,13),(14,15)])
    with monkeypatch.context() as patch:
        patch.setattr(c.os,'WIFSTOPPED',lambda status:status&255==127);patch.setattr(c.os,'WSTOPSIG',lambda status:status>>8&255);patch.setattr(c.signal,'SIGSTOP',19);patch.setattr(c,'Path',FakePath);patch.setattr(c.platform,'system',lambda:'Linux');patch.setattr(c.platform,'machine',lambda:'x86_64')
        patch.setattr(c.time,'monotonic',tick);patch.setattr(c.time,'sleep',lambda *_:None)
        patch.setattr(c.selectors,'DefaultSelector',SelectorModel)
        for name,value in {'pipe2':lambda *_:next(pipes),'close':lambda *_:None,'fork':lambda:100,'set_blocking':lambda *_:None,'waitpid':waitpid,'getpid':lambda:99,'getuid':lambda:1000,'getgid':lambda:1000,'open':lambda *_:90,'fstat':lambda fd:info(fdrows[fd]),'read':lambda fd,*_:reads[fd].pop(0)}.items():patch.setattr(c.os,name,value,raising=False)
        patch.setattr(c.os.path,'realpath',lambda *_:'/bin/tool')
        patch.setattr(c.n,'_host_window',lambda *a,**k:copy.deepcopy(policy))
        patch.setattr(c.n,'_acquire_candidates',lambda *a,**k:({fdrows[k]:k for k in fdrows},copy.deepcopy(facts)))
        patch.setattr(c.n,'_lifetime',lambda *_:{k:initial[k] for k in ('pid','starttime','ppid','uid','gid')})
        patch.setattr(c.n,'_ptrace',lambda *args:ptrace.append(args))
        patch.setattr(c.n,'_syscall_stop',lambda *_:calls.pop(0));patch.setattr(c.n,'_entry_detail',detail)
        patch.setattr(c.n,'_maps',lambda *_:copy.deepcopy(maps));patch.setattr(c.n,'_observe_open_route',lambda value:(value,[]))
        patch.setattr(c.n,'_fd_snapshot',lambda *_:copy.deepcopy(initial['fds']))
        patch.setattr(c,'_comparison_snapshot',lambda *_:copy.deepcopy(initial['fds']))
        patch.setattr(c.n,'_read_fd',lambda fd,*_:archive[facts[fdrows[fd]]['sha256']])
        patch.setattr(c.n,'_finish_native_custody',lambda pid,desc,reaped,code,deadline:({'schema':'twin.native-custody/v1','leader_pid':100,'reservation':'traced-owned-lifetime','signals':[],'direct_child_reaped':True,'absence_verified':True,'absence_probe':'absent','descendants':[],'reaped':[100],'grace_deadline':deadline,'cleanup_ended':clock[0]},code))
        run=c._linux_run_comparison(authority,copy.deepcopy(obs['spec']),archive)
    assert run['failure'] is None
    assert run['stdout']==b'hello\n' and run['stderr']==b''
    assert run['_eof']==['stdout','stderr'] and run['_wait']['raw_status']==0
    assert run['native_observation']['schema']=='TEST_ONLY-pdf-baseline-events/v1'
    assert [row['data']['channel'] for row in run['native_observation']['events'] if row['kind']=='pipe-eof']==['stdout','stderr']
    assert len([row for row in ptrace if row[0]==24])==8


def authority_model(plan,archive,*,slot=0):
    """Explicitly fabricated private-shaped objects for pure source controls only."""
    import time
    session=object.__new__(c.ComparisonSession)
    for key,value in {'_selection':'a'*64,'_started':time.monotonic(),'_next':slot,'_retained':0,'_reserve':1024,'_stopped':False,'_awaiting_comparison':False,'_used_hosts':set(),'_guard':GuardModel()}.items():setattr(session,key,value)
    pair=sm._json(archive[plan['pair_plan_sha256']]);evidence={pin:archive[pin] for pin in (plan['build_identity_sha256'],pair['build_pair']['patched_build_sha256'],plan['config']['sha256'],pair['suite_selection_sha256'])}
    policy={'schema':'twin.native-host-policy/v1','scope':c.n.SCOPE,'custodian':'PURE MODEL, NOT AN ACTUAL SELECTED HOST','not_before':'2026-10-31T00:00:00+00:00','not_after':'2026-10-31T00:05:00+00:00','roots':['/bin','/lib','/data'],'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':sorted(evidence)}
    context=object.__new__(c.n.NativeHostContext)
    for key,value in {'_policy':sm.canonical(policy),'_evidence':evidence,'_guard':GuardModel()}.items():object.__setattr__(context,key,value)
    authority=object.__new__(c.ComparisonCaptureAuthority)
    for key,value in {'_context':context,'_guard':GuardModel(),'_pair':sm.canonical(pair),'_archive':dict(archive),'_plan':sm.canonical(plan),'_selected_at':time.monotonic(),'_spent':False,'_suite_started':session._started,'_slots_used':slot,'_retained_bytes':0,'_reserve_bytes':1024,'_session':session,'_slot':slot}.items():object.__setattr__(authority,key,value)
    return authority


def test_collector_pre_return_error_retains_failed_data_and_stops_the_original_session(monkeypatch,tmp_path):
    pair,plan,archive=prepared_fixture();authority=authority_model(plan,archive)
    monkeypatch.setattr(c,'_check_drivers',lambda *a:None)
    monkeypatch.setattr(c.n,'_host_window',lambda *a,**k:sm._json(authority._context._policy))
    monkeypatch.setattr(c,'_linux_run_comparison',lambda *a:(_ for _ in ()).throw(ValueError('PURE MODEL pre-return refusal')))
    monkeypatch.setattr(c.tempfile,'mkdtemp',lambda **k:str(tmp_path))
    completed=c.capture_baseline(authority,plan,archive)
    data=sm._json(completed._record)
    assert data['status']=='FAILED_DATA' and data['cleanup']=='preserved-uncertain'
    assert data['terminal_wait'] is None and data['stdout']['complete'] is False
    assert authority._session._stopped is True and authority._spent is True
    assert (tmp_path/'comparison-failed-data.json').read_bytes()==completed._record
    assert c.compare_pair(pair,completed)['status']=='NOT_COMPARABLE'


def test_consistently_rehashed_candidate_substitution_does_not_change_the_selected_input(monkeypatch):
    pair,plan,data,archive=complete_data_fixture()
    obs=sm._json(archive[data['native_events_sha256']])
    obs['spec']['candidates']=[row for row in obs['spec']['candidates'] if row['path']!='/work/input']
    raw=sm.canonical(obs);data['native_events_sha256']=sm.sha256(raw);archive[data['native_events_sha256']]=raw
    with pytest.raises(ValueError,match='candidate'):c.check_comparison_capture(data,archive,expected_plan=plan)


def patched_gate_fixture(monkeypatch):
    """All private-shaped host objects here are invented pure models, not selections."""
    import time
    pair,plan,data,archive=complete_data_fixture();authority=authority_model(plan,archive,slot=1)
    session=authority._session
    context=authority._context;policy_pin=sm.sha256(context._policy);archive[policy_pin]=context._policy;archive.update(context._evidence)
    obs=sm._json(archive[data['native_events_sha256']]);obs['host_policy_sha256']=policy_pin
    obsraw=sm.canonical(obs);data['native_events_sha256']=sm.sha256(obsraw);archive[data['native_events_sha256']]=obsraw
    data['observation_mode']='actual';data['host_policy_sha256']=policy_pin
    evidence=sm.canonical({'schema':'TEST_ONLY-comparison-host-evidence-index/v1','sha256s':sorted(context._evidence)})
    data['host_evidence_sha256']=sm.sha256(evidence);archive[data['host_evidence_sha256']]=evidence
    baseline=object.__new__(c.ComparisonCompletion)
    for key,value in {'_record':sm.canonical(data),'_held_record':sm.canonical(data),'_archive':dict(archive),'_plan':sm.canonical(plan),'_pair':sm.canonical(pair),'_guard':GuardModel(),'_session':session}.items():object.__setattr__(baseline,key,value)
    wrapper_config={'native_config_sha256':pair['config']['sha256'],'pdf_origin':{'build_identity_sha256':pair['build_pair']['patched_build_sha256']}}
    raw=sm.canonical(wrapper_config);configpin=sm.sha256(raw);archive[configpin]=raw
    new_evidence=dict(context._evidence);new_evidence[configpin]=raw
    policy=sm._json(context._policy);policy['evidence_sha256s']=sorted(new_evidence)
    newcontext=object.__new__(c.n.NativeHostContext)
    for key,value in {'_policy':sm.canonical(policy),'_evidence':new_evidence,'_guard':GuardModel()}.items():object.__setattr__(newcontext,key,value)
    object.__setattr__(authority,'_context',newcontext)
    store=object.__new__(c.n.NativeObservationStore)
    for key,value in {'_purpose':'actual','_host_context':newcontext,'_guard':GuardModel(),'_entries':{}}.items():setattr(store,key,value)
    frozen={'purpose':'actual','profile':c.bridge.PROFILE,'parent_sha256':pair['fixture']['sha256'],'parent_bytes':pair['fixture']['bytes'],'configuration_sha256':configpin,'archive':archive}
    parent=archive[pair['fixture']['sha256']];calls=[]
    monkeypatch.setattr(c.n,'_host_window',lambda ctx,**k:sm._json(ctx._policy))
    monkeypatch.setattr(c.n,'validate_native_candidate_plan',lambda p,raw:calls.append(('validate',p is not frozen,raw==parent)))
    failure_observation={'schema':'twin.native-file-observation-failure/v2','host_policy_sha256':sm.sha256(newcontext._policy),'failure':{'wait':{'kind':'exited','raw_status':256,'exit_code':1,'observed_at_ns':9000}}}
    archive[sm.sha256(newcontext._policy)]=newcontext._policy;archive.update(new_evidence)
    obsbytes=sm.canonical(failure_observation);op=sm.sha256(obsbytes);archive[op]=obsbytes
    empty={'sha256':sm.sha256(b''),'bytes':0};archive[empty['sha256']]=b''
    dossier={'native_observation_sha256':op,'stdout':empty,'stderr':empty}
    dr=sm.canonical(dossier);dp=sm.sha256(dr)
    result={'status':'failure','archive':archive,'receipts':{dp:dr},'dossier_sha256':dp}
    def execute(p,raw,observation_store,preparation_deadline):
        assert preparation_deadline<=authority._selected_at+60
        calls.append(('execute',observation_store is store,p is not frozen))
        return copy.deepcopy(result),copy.deepcopy(failure_observation)
    monkeypatch.setattr(c.migration,'_execute_prepared_extraction',execute)
    return pair,authority,baseline,store,frozen,parent,calls,result


def test_private_patched_route_consumes_one_actual_shaped_completed_pair_and_retains_failure(monkeypatch):
    pair,authority,baseline,store,plan,parent,calls,result=patched_gate_fixture(monkeypatch)
    completed=c.capture_patched_comparison(authority,baseline,store,plan,parent)
    assert type(completed) is c.PatchedComparisonCompletion
    assert calls==[('validate',True,True),('execute',True,True)]
    assert completed._completed[0]['status']=='failure' and completed._completed[1]['failure']['wait']['exit_code']==1
    assert completed._completed[0] is not result
    assert authority._session._stopped is True and authority._spent is True
    assert store._entries=={}


@pytest.mark.parametrize('mutation',['public-store','test-only-store','missing-context','forged-context','different-context','store-guard','source-guard','host-window','plan-validation','selection','public-failure','tuple-substitute','different-session'])
def test_patched_route_missing_private_gates_never_executes_or_adopts_a_failure(monkeypatch,mutation):
    pair,authority,baseline,store,plan,parent,calls,result=patched_gate_fixture(monkeypatch)
    class RefuseGuard:
        def verify(self):raise ValueError('PURE MODEL source guard refused')
    if mutation=='public-store':store={}
    if mutation=='test-only-store':store._purpose='TEST_ONLY'
    if mutation=='missing-context':store._host_context=None
    if mutation=='forged-context':store._host_context={}
    if mutation=='different-context':store._host_context=object.__new__(c.n.NativeHostContext)
    if mutation=='store-guard':store._guard=RefuseGuard()
    if mutation=='source-guard':object.__setattr__(authority,'_guard',RefuseGuard())
    if mutation=='host-window':monkeypatch.setattr(c.n,'_host_window',lambda *a,**k:(_ for _ in ()).throw(ValueError('unselected/expired H')))
    if mutation=='plan-validation':monkeypatch.setattr(c.n,'validate_native_candidate_plan',lambda *a:(_ for _ in ()).throw(ValueError('invalid frozen native plan')))
    if mutation=='selection':object.__setattr__(authority._context,'_evidence',{})
    if mutation=='public-failure':monkeypatch.setattr(c.migration,'_execute_prepared_extraction',lambda *a,**k:copy.deepcopy(result))
    if mutation=='tuple-substitute':monkeypatch.setattr(c.migration,'_execute_prepared_extraction',lambda *a,**k:(copy.deepcopy(result),{}))
    if mutation=='different-session':object.__setattr__(baseline,'_session',object())
    with pytest.raises(ValueError):c.capture_patched_comparison(authority,baseline,store,plan,parent)
    assert not any(call[0]=='execute' for call in calls)
    if mutation in ('public-failure','tuple-substitute'):assert authority._session._stopped is True
    if type(store) is c.n.NativeObservationStore:assert store._entries=={}


@pytest.mark.parametrize('mutation',['stopped','out-of-order','same-H','awaiting-comparison','deadline','capacity'])
def test_private_original_session_cannot_renew_duplicate_or_continue_after_uncertain_outcomes(mutation):
    pair,plan,archive=prepared_fixture();authority=authority_model(plan,archive)
    session=authority._session
    if mutation=='stopped':session._stopped=True
    if mutation=='out-of-order':session._next=1
    if mutation=='same-H':session._used_hosts.add(sm.sha256(authority._context._policy))
    if mutation=='awaiting-comparison':session._awaiting_comparison=True
    if mutation=='deadline':session._started-=10700
    if mutation=='capacity':session._retained=c.MAX_SUITE_BYTES
    with pytest.raises(ValueError):c._consume(authority,patched=False)
    assert authority._spent is False


def failed_data_fixture(wait=None):
    pair,plan,data,archive=complete_data_fixture();data['status']='FAILED_DATA';data['terminal_wait']=wait
    for name in ('stdout','stderr'):data[name]['complete']=False
    facts={'schema':'TEST_ONLY-comparison-failure-facts/v1','reason':'PURE MODEL failed outcome','exception_type':None,'workspace':None,'stdout':copy.deepcopy(data['stdout']),'stderr':copy.deepcopy(data['stderr']),'terminal_wait':copy.deepcopy(wait),'custody_sha256':data['custody_sha256'],'cleanup':data['cleanup'],'intervention':data['intervention']}
    raw=sm.canonical(facts);pin=sm.sha256(raw);archive[pin]=raw
    data['failure']={'stage':'terminal','code':'CAPTURE_REFUSED','original_exception_type':None,'facts_sha256':pin}
    return pair,plan,data,archive


def test_failed_natural_wait_substitution_cannot_replace_retained_failure_facts():
    pair,plan,data,archive=failed_data_fixture({'kind':'exited','raw_status':256,'exit_code':1,'observed_at_ns':9000,'provenance':'natural_terminal'})
    c.check_comparison_capture(data,archive,expected_plan=plan)
    data['terminal_wait']={'kind':'exited','raw_status':0,'exit_code':0,'observed_at_ns':9000,'provenance':'natural_terminal'}
    with pytest.raises(ValueError,match='failure facts'):c.check_comparison_capture(data,archive,expected_plan=plan)


def test_failed_incomplete_comparisons_preserve_natural_nonzero_and_never_treat_cleanup_as_converter_exit():
    one={'kind':'exited','raw_status':256,'exit_code':1,'observed_at_ns':9000,'provenance':'natural_terminal'}
    zero={'kind':'exited','raw_status':0,'exit_code':0,'observed_at_ns':9000,'provenance':'natural_terminal'}
    pair,plan,left,a=failed_data_fixture(one);_,rightplan,right,b=failed_data_fixture(zero)
    result=c.compare_simulated_pair(pair,left,a,plan,right,b,rightplan)
    assert result['stdout_equal'] is None and result['stderr_equal'] is None
    assert result['exit_equal'] is False and result['status']=='MISMATCH' and result['stop_suite']
    right['terminal_wait']['provenance']='cleanup_intervention'
    facts=sm._json(b[right['failure']['facts_sha256']]);facts['terminal_wait']['provenance']='cleanup_intervention'
    raw=sm.canonical(facts);pin=sm.sha256(raw);b[pin]=raw;right['failure']['facts_sha256']=pin
    result=c.compare_simulated_pair(pair,left,a,plan,right,b,rightplan)
    assert result['exit_equal'] is None and result['status']=='NOT_COMPARABLE' and result['stop_suite']


def retime(obs):
    import datetime
    events=obs['events']
    for i,event in enumerate(events):event['seq']=i;event['at_ns']=i*1000
    clock=obs['run'];elapsed=(len(events)+3)*1000;cleanup=(len(events)+2)*1000
    events[-1]['at_ns']=elapsed;clock['elapsed_ns']=elapsed;clock['cleanup_started_ns']=clock['monotonic_start_ns']+cleanup
    clock['cleanup_deadline_ns']=clock['cleanup_started_ns']+2*10**9
    clock['ended_at']=(datetime.datetime.fromisoformat(clock['started_at'])+datetime.timedelta(microseconds=elapsed/1000)).isoformat()
    events[-1]['data']['wait']['observed_at_ns']=cleanup
    custody=events[-1]['data']['custody'];custody['grace_deadline']=clock['cleanup_deadline_ns']/10**9;custody['cleanup_ended']=(clock['monotonic_start_ns']+elapsed)/10**9


def test_descriptor_three_is_an_ordinary_checked_dependency_and_never_an_origin_channel():
    obs,archive=event_fixture();events=obs['events'];raw=b'ABC';pin=sm.sha256(raw);archive[pin]=raw
    calls=[('enter',{'nr':2,'args':[0,0x80000,0,0,0,0],'detail':{'path':'/data'}}),('leave',{'result':3,'detail':{'kind':'file','identity':obs['files']['/data']['identity']}}),('enter',{'nr':0,'args':[3,4096,3,0,0,0],'detail':{}}),('leave',{'result':3,'detail':{'buffer_sha256':pin,'buffer_bytes':3}}),('enter',{'nr':3,'args':[3,0,0,0,0,0],'detail':{}}),('leave',{'result':0,'detail':{}})]
    events[4:4]=[{'seq':0,'at_ns':0,'kind':kind,'data':data} for kind,data in calls];retime(obs)
    assert c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')['stdout_bytes']==6


@pytest.mark.parametrize('close_succeeds',[True,False])
def test_eof_during_original_close_may_interleave_with_an_already_closed_channel(close_succeeds):
    obs,archive=event_fixture();events=obs['events'];stdout_eof=copy.deepcopy(events[-3]);stderr_eof=copy.deepcopy(events[-2])
    close=lambda fd:{'nr':3,'args':[fd,0,0,0,0,0],'detail':{}}
    sequence=[{'kind':'enter','data':close(2)},{'kind':'leave','data':{'result':0,'detail':{}}},{'kind':'enter','data':close(1)},stderr_eof,stdout_eof,{'kind':'leave','data':{'result':0 if close_succeeds else -9,'detail':{}}}]
    events[6:6]=sequence
    events[:]=[row for row in events if row is not events[-3] and row is not events[-2]]
    exit_stop=next(e for e in events if e['kind']=='exit-stop');exit_stop['data']['fds']=exit_stop['data']['fds'][:1]
    retime(obs)
    if close_succeeds:assert c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')['qualification']=='NONE'
    else:
        with pytest.raises(ValueError):c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')


@pytest.mark.parametrize('at,valid',[(7000,True),(10000,True),(6999,False),(10001,False)])
def test_exact_wait_exit_cleanup_clock_boundaries(at,valid):
    obs,archive=event_fixture();obs['events'][-1]['data']['wait']['observed_at_ns']=at
    if valid:assert c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')['qualification']=='NONE'
    else:
        with pytest.raises(ValueError):c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')


@pytest.mark.parametrize('replacement',[True,120.0,-1])
def test_profile_limits_require_exact_integers(replacement):
    obs,archive=event_fixture();obs['spec']['limits']['wall_seconds']=replacement
    with pytest.raises(ValueError):c.check_comparison_events(obs,archive,observation_mode='SIMULATED_DATA')


def test_full_bytes_are_compared_without_substrings_normalization_or_warning_removal():
    pair,plan,left,a=complete_data_fixture();_,rightplan,right,b=complete_data_fixture()
    obs=sm._json(b[right['native_events_sha256']]);raw=b'HELLO\n';pin=sm.sha256(raw);b[pin]=raw
    obs['events'][4]['data']['detail']['buffer_sha256']=pin;obs['events'][-1]['data']['stdout_sha256']=pin
    wire=sm.canonical(obs);op=sm.sha256(wire);b[op]=wire;right['native_events_sha256']=op;right['stdout']['captured']['sha256']=pin
    result=c.compare_simulated_pair(pair,left,a,plan,right,b,rightplan)
    assert result['stdout_equal'] is False and result['stderr_equal'] is True and result['exit_equal'] is True
    assert result['status']=='MISMATCH' and result['stop_suite'] is True


def test_copied_private_completion_and_changed_helper_are_not_public_adoption_routes(monkeypatch):
    guard=c._guard()
    original=c._comparison_admit
    monkeypatch.setattr(c,'_comparison_admit',lambda *a,**k:'write')
    with pytest.raises(ValueError):guard.verify()
    monkeypatch.setattr(c,'_comparison_admit',original)
    for public in ({},b'{}',object()):
        with pytest.raises(ValueError):c.compare_pair({},cast(Any,public))


def test_authority_freeze_requires_real_private_types_and_matching_independent_evidence(monkeypatch):
    pair,plan,archive=prepared_fixture();model=authority_model(plan,archive);session=model._session
    session._selection=pair['suite_selection_sha256']
    monkeypatch.setattr(c.n,'_host_window',lambda context,**kw:sm._json(context._policy))
    with pytest.raises(ValueError,match='private'):c.freeze_comparison_authority(cast(Any,{}),plan,archive,session=session)
    with pytest.raises(ValueError,match='private'):c.freeze_comparison_authority(model._context,plan,archive,session=cast(Any,{}))
    frozen=c.freeze_comparison_authority(model._context,plan,archive,session=session)
    assert type(frozen) is c.ComparisonCaptureAuthority and frozen._spent is False
    object.__setattr__(model._context,'_evidence',{})
    with pytest.raises(ValueError):c.freeze_comparison_authority(model._context,plan,archive,session=session)


def test_original_session_selection_cannot_start_from_a_public_record_or_larger_budget(monkeypatch):
    pair,plan,archive=prepared_fixture();authority=authority_model(plan,archive)
    with pytest.raises(ValueError,match='private'):c.new_comparison_session(cast(Any,{}),'a'*64)
    selection={'schema':'TEST_ONLY-pdf-comparison-suite-selection/v1','original_started_monotonic_ns':int(authority._suite_started*10**9),'original_seconds':10800,'max_invocations':52,'slot_seconds':182,'preparation_seconds':60,'target_seconds':120,'failed_cleanup_seconds':2,'transport_seconds':300,'storage_bytes':c.MAX_SUITE_BYTES,'reserve_bytes':1024}
    def select(value):
        raw=sm.canonical(value);pin=sm.sha256(raw)
        context=authority._context;policy=sm._json(context._policy);policy['evidence_sha256s']=[pin]
        object.__setattr__(context,'_policy',sm.canonical(policy));object.__setattr__(context,'_evidence',{pin:raw})
        return context,pin
    monkeypatch.setattr(c.n,'_host_window',lambda context,**k:sm._json(context._policy))
    context,pin=select(selection);session=c.new_comparison_session(context,pin)
    assert session._next==0 and session._stopped is False
    selection['original_seconds']=10801;context,pin=select(selection)
    with pytest.raises(ValueError):c.new_comparison_session(context,pin)


@pytest.mark.parametrize('deadline',[True,float('nan'),float('inf'),float('-inf')])
def test_optional_native_preparation_deadline_rejects_invalid_values_without_os(monkeypatch,deadline):
    touched=[]
    monkeypatch.setattr(c.n,'_host_window',lambda *_:touched.append('BAD'))
    with pytest.raises(ValueError):c.n._acquire_candidates({'candidates':[]},{},cast(Any,object()),preparation_deadline=deadline)
    assert touched==[]


@pytest.mark.parametrize('deadline,read_finishes,allowed',[(99.0,100.0,False),(160.0,160.0,True),(160.0,160.000001,False),(1000.0,161.0,False),(None,161.0,True)])
def test_candidate_read_uses_original_pre_setup_bound_and_later_deadline_never_renews_local_sixty(monkeypatch,deadline,read_finishes,allowed):
    import types,errno
    now=[100.0];closed=[];touched=[]
    info=types.SimpleNamespace(st_dev=1,st_ino=2,st_mode=0o100444,st_uid=1000,st_gid=1000,st_nlink=1,st_size=1,st_mtime_ns=1,st_ctime_ns=1)
    raw=b'x';pin=sm.sha256(raw);spec={'cwd':'/work','candidates':[{'path':'/safe/file','sha256':pin,'bytes':1}]}
    def read(*a):now[0]=read_finishes;return raw
    with monkeypatch.context() as patch:
        patch.setattr(c.n.time,'monotonic',lambda:now[0]);patch.setattr(c.n,'_host_window',lambda *a,**k:{'roots':['/safe']})
        patch.setattr(c.n,'_observe_open_route',lambda path:(path,[]));patch.setattr(c.n.os,'open',lambda *a:touched.append('open') or 999)
        patch.setattr(c.n.os,'close',lambda fd:closed.append(fd));patch.setattr(c.n.os,'fstat',lambda *_:info)
        patch.setattr(c.n.os,'getxattr',lambda *a:(_ for _ in ()).throw(OSError(errno.ENODATA,'PURE MODEL no capability')),raising=False)
        patch.setattr(c.n,'_read_fd',read)
        if allowed:
            held,facts=c.n._acquire_candidates(spec,{pin:raw},cast(Any,object()),preparation_deadline=deadline)
            assert held=={'/safe/file':999} and facts['/safe/file']['sha256']==pin
        else:
            with pytest.raises(ValueError):c.n._acquire_candidates(spec,{pin:raw},cast(Any,object()),preparation_deadline=deadline)
    if not allowed and touched:assert closed==[999]
    if deadline==99.0:assert touched==[]


@pytest.mark.parametrize('interval',[('2026-10-31T00:00:01+00:00','2026-10-31T00:05:00+00:00'),('2026-10-31T00:00:00+00:00','2026-10-31T00:00:00.000012+00:00'),('2026-10-31T00:00:00+00:00','2026-10-31T00:05:01+00:00')])
def test_actual_shaped_data_cannot_move_or_extend_the_independently_held_host_interval(monkeypatch,interval):
    pair,authority,baseline,store,plan,parent,calls,result=patched_gate_fixture(monkeypatch)
    data=sm._json(baseline._record);archive=dict(baseline._archive);obs=sm._json(archive[data['native_events_sha256']])
    policy=sm._json(archive[obs['host_policy_sha256']]);policy['not_before'],policy['not_after']=interval
    raw=sm.canonical(policy);pin=sm.sha256(raw);archive[pin]=raw;obs['host_policy_sha256']=pin;data['host_policy_sha256']=pin
    raw=sm.canonical(obs);op=sm.sha256(raw);archive[op]=raw;data['native_events_sha256']=op
    with pytest.raises(ValueError,match='interval'):c.check_comparison_capture(data,archive,expected_plan=sm._json(baseline._plan))
