"""Pure TEST_ONLY protocol controls. Never call ptrace/proc/native children."""
import copy
import pytest
from twin import source_native_observation as n


def test_public_trace_cannot_issue_an_actual_handle():
    store = n.new_native_observation_store(purpose='actual')
    with pytest.raises(ValueError, match='authority|host|purpose'):
        n.acquire_test_only_observation(store, {}, b'', {}, {})


def test_actual_without_independent_host_selection_holds_before_os():
    store = n.new_native_observation_store(purpose='actual')
    with pytest.raises(ValueError, match='host'):
        n.acquire_native_observation(store, {}, b'')


def fixture():
    import struct
    from twin import source_metadata as sm
    archive = {}
    def blob(raw):
        pin=sm.sha256(raw); archive[pin]=raw; return pin
    def elf(interpreter=None):
        raw=bytearray(64+56+(len(interpreter)+1 if interpreter else 0))
        raw[:7]=b'\x7fELF\x02\x01\x01'
        struct.pack_into('<HHIQQQIHHHHHH',raw,16,2,62,1,0x400000,64,0,0,64,56,1 if interpreter else 0,0,0,0)
        if interpreter:
            struct.pack_into('<IIQQQQQQ',raw,64,3,4,120,0,0,len(interpreter)+1,len(interpreter)+1,1)
            raw[120:]=interpreter.encode()+b'\0'
        return bytes(raw)
    files={}
    for i,(path,raw) in enumerate([('/bin/tool',elf('/lib/loader')),('/lib/loader',elf()),('/data',b'ABCDEF')]):
        files[path]={'path':path,'sha256':blob(raw),'bytes':len(raw),'identity':[1,10+i,0o100444,1000,1000,1,len(raw),1,1]}
    maps=[{'start':0x400000,'end':0x401000,'prot':5,'offset':0,'path':'/bin/tool','identity':[1,10]},
          {'start':0x500000,'end':0x501000,'prot':5,'offset':0,'path':'/lib/loader','identity':[1,11]}]
    spec={'schema':'twin.native-observation-spec/v1','purpose':'TEST_ONLY','profile':'pdf-text-xpdf/1',
          'plan_sha256':'a'*64,'argv':['/bin/tool','-cfg','/work/native-config','-enc','UTF-8','-eol','unix','-nopgbrk','/work/input','-'],
          'environment':{'LC_ALL':'C','LANG':'C','TZ':'UTC'},'cwd':'/work',
          'limits':{'input_bytes':256*1048576,'wall_seconds':120,'stdout_bytes':128*1048576,'stderr_bytes':4*1048576,'syntax_bytes':64*1048576,'termination_grace_seconds':2},
          'candidates':[{k:v for k,v in row.items() if k!='identity'} for row in files.values()]}
    events=[]
    def event(kind,data): events.append({'seq':len(events),'at_ns':len(events)*1000,'kind':kind,'data':data})
    fds=[{'fd':i,'identity':[2,20+i],'kind':kind} for i,kind in enumerate(['stdin','stdout','stderr'])]
    event('start',{'pid':100,'starttime':123,'ppid':99,'uid':1000,'gid':1000,'fds':fds})
    event('enter',{'nr':59,'args':[0]*6,'detail':{'path':'/bin/tool','argv':spec['argv'],'environment':spec['environment'],'cwd':'/work'}})
    event('exec',{'maps':maps,'executable':'/bin/tool','credentials':[1000,1000],'interpreter':'/lib/loader','interpreter_route':{'path':'/lib/loader'}})
    event('leave',{'result':0,'detail':{}})
    event('enter',{'nr':1,'args':[1,0,6,0,0,0],'detail':{'buffer_sha256':blob(b'hello\n')}})
    event('leave',{'result':6,'detail':{}})
    event('enter',{'nr':231,'args':[0]*6,'detail':{}})
    event('exit-stop',{'status':0,'maps':maps,'fds':fds,'pid':100,'starttime':123})
    event('terminal',{'returncode':0,'stdout_sha256':blob(b'hello\n'),'stderr_sha256':blob(b''),'sidecars':{},'eof':['stdout','stderr'],'reaped':[100],'cleanup':'owned-workspace-removed','custody':{'schema':'twin.native-custody/v1','leader_pid':100,'reservation':'traced-owned-lifetime','signals':[],'direct_child_reaped':True,'absence_verified':True,'absence_probe':'absent','descendants':[],'reaped':[100],'grace_deadline':122.0,'cleanup_ended':120.0}})
    return {'schema':'twin.native-file-observation/v1','scope':n.SCOPE,'purpose':'TEST_ONLY',
            'spec':spec,'files':files,'events':events,'platform':{'system':'Linux','machine':'x86_64','release':'TEST_ONLY-kernel','version':'TEST_ONLY-build'},'host_policy_sha256':None},archive


def test_replay_accounts_for_exact_short_lived_exec_and_streams():
    obs,archive=fixture()
    result=n.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    assert result['used_paths']==['/bin/tool','/lib/loader']
    assert result['stdout_bytes']==6


@pytest.mark.parametrize('mutation', ['sequence','missing-exec','abi','unknown','fork','second-exec','wrong-output','vdso-file'])
def test_trace_mutations_never_become_complete(mutation):
    obs,archive=fixture()
    if mutation=='sequence': obs['events'][2]['seq']=3
    if mutation=='missing-exec': obs['events'][2]['kind']='leave'
    if mutation in ('abi','unknown','fork'): obs['events'][4]['data']['nr']={'abi':0x40000001,'unknown':99999,'fork':56}[mutation]
    if mutation=='second-exec': obs['events'][4]['data']=copy.deepcopy(obs['events'][1]['data'])
    if mutation=='wrong-output': obs['events'][-1]['data']['stdout_sha256']=obs['events'][-1]['data']['stderr_sha256']
    if mutation=='vdso-file': obs['files']['[vdso]']=obs['files']['/data']
    with pytest.raises(ValueError): n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_private_test_only_acquisition_is_store_local_and_rechecks_held_bytes():
    obs,archive=fixture(); store=n.new_native_observation_store(purpose='TEST_ONLY')
    handle=n.acquire_test_only_observation(store,{},b'',obs,archive)
    assert n.resolve_native_observation(store,handle)['status']=='TEST_ONLY-observed'
    with pytest.raises(ValueError): n.resolve_native_observation(n.new_native_observation_store(purpose='TEST_ONLY'),handle)
    with pytest.raises(ValueError): n.resolve_native_observation(store,copy.deepcopy(handle))
    exported=n.resolve_native_observation(store,handle); exported['observation']['scope']='all-input-reproducibility'
    assert n.resolve_native_observation(store,handle)['observation']['scope']==n.SCOPE


def test_host_context_requires_independently_selected_exact_policy_and_evidence():
    from twin import source_metadata as sm
    policy={'schema':'twin.native-host-policy/v1','scope':n.SCOPE,'custodian':'public-test',
            'not_before':'2026-10-30T00:00:00+00:00','not_after':'2026-10-31T00:00:00+00:00',
            'roots':['/bin','/lib'],'writer_control':'trusted-administrator-controlled-interval',
            'evidence_sha256s':[sm.sha256(b'public independent selection')]}
    with pytest.raises(ValueError): n.freeze_native_host_context(policy,{},sm.sha256(sm.canonical(policy)))
    with pytest.raises(ValueError): n.freeze_native_host_context(policy,{sm.sha256(b'public independent selection'):b'public independent selection'},'0'*64)


def test_kernel_syscall_info_has_typed_arch_length_and_stop_checks():
    import struct
    raw=bytearray(128);raw[0]=1;struct.pack_into('<I',raw,4,0xc000003e);struct.pack_into('<Q6Q',raw,24,1,1,2,3,0,0,0)
    assert n.decode_syscall_info(bytes(raw),80)=={'op':'enter','nr':1,'args':[1,2,3,0,0,0]}
    for length in (0,33,79,129):
        with pytest.raises(ValueError): n.decode_syscall_info(bytes(raw),length)
    raw[4:8]=b'\x03\x00\x00\x40'
    with pytest.raises(ValueError): n.decode_syscall_info(bytes(raw),80)


def splice(obs, pairs):
    events=[]
    for kind,data in pairs: events.append({'seq':0,'at_ns':0,'kind':kind,'data':data})
    obs['events'][4:4]=events
    for i,event in enumerate(obs['events']): event['seq']=i;event['at_ns']=i*1000


def call(nr,args,entry=None,result=0,detail=None):
    if nr in (0,17,19): detail={**(detail or {}),'buffer_bytes':max(0,result)}
    return [('enter',{'nr':nr,'args':args+[0]*(6-len(args)),'detail':({'buffer_bytes':36} if nr==16 and entry is None else entry or {})}),
            ('leave',{'result':result,'detail':detail or {}})]


def blob(archive,raw):
    from twin import source_metadata as sm
    pin=sm.sha256(raw);archive[pin]=raw;return pin


def resource_run():
    obs,archive=fixture();identity=obs['files']['/data']['identity']
    pairs=call(2,[0,0x80000],{'path':'/data'},3,{'kind':'file','identity':identity})
    pairs+=call(0,[3,0,3],result=3,detail={'buffer_sha256':blob(archive,b'ABC')})
    pairs+=call(72,[3,0,0],result=4)
    pairs+=call(0,[4,0,3],result=3,detail={'buffer_sha256':blob(archive,b'DEF')})
    maps=copy.deepcopy(obs['events'][2]['data']['maps'])
    mapped=maps+[{'start':0x600000,'end':0x601000,'prot':1,'offset':0,'path':'/data','identity':identity[:2]}]
    pairs+=call(9,[0,4096,1,2,4,0],result=0x600000,detail={'maps':mapped})
    pairs+=call(3,[3])+call(3,[4])
    pairs+=call(11,[0x600000,4096],detail={'maps':maps})
    splice(obs,pairs)
    return obs,archive


def test_fd_aliases_share_read_offset_and_mappings_outlive_closed_fd():
    obs,archive=resource_run()
    assert n.verify_native_observation(obs,archive,purpose='TEST_ONLY')['used_paths']==['/bin/tool','/data','/lib/loader']


@pytest.mark.parametrize('mutation',['wrong-read','wrong-offset','unknown-fd','identity','unretained','unexplained-map','anonymous-exec','shared-write','unknown-flag','missing-lookup-buffer'])
def test_resource_coverage_rejects_nearby_mutations(mutation):
    obs,archive=resource_run()
    if mutation=='wrong-read':obs['events'][7]['data']['detail']['buffer_sha256']=blob(archive,b'DEF')
    if mutation=='wrong-offset':obs['events'][11]['data']['detail']['buffer_sha256']=blob(archive,b'ABC')
    if mutation=='unknown-fd':obs['events'][10]['data']['args'][0]=99
    if mutation=='identity':
        obs['events'][5]['data']['detail']['identity']=list(obs['events'][5]['data']['detail']['identity']);obs['events'][5]['data']['detail']['identity'][1]=999
    if mutation=='unretained':obs['spec']['candidates']=obs['spec']['candidates'][:2]
    if mutation=='unexplained-map':obs['events'][-2]['data']['maps'][0]['path']='/data'
    if mutation=='anonymous-exec':obs['events'][12]['data']['args'][3]=0x22;obs['events'][12]['data']['args'][2]=5
    if mutation=='shared-write':obs['events'][12]['data']['args'][3]=1;obs['events'][12]['data']['args'][2]=3
    if mutation=='unknown-flag':obs['events'][4]['data']['args'][1]|=0x40
    if mutation=='missing-lookup-buffer':splice(obs,call(4,[0,0],{'path':'/data'}))
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def sidecar_run():
    from twin import source_metadata_migration as m
    obs,archive=fixture();obs['spec']['profile']='utf8-identity/1';obs['spec']['limits']=copy.deepcopy(m.PROFILES['utf8-identity/1'])
    argv=['/bin/tool','-I','-S','-B','-X','pycache_prefix=/work/pycache','/work/helper.py','--run','/work/input','/work/config','/work/syntax','/work/runtime']
    obs['spec']['argv']=argv;obs['events'][1]['data']['detail']['argv']=argv
    pairs=[];sidecars={}
    for index,(path,raw) in enumerate([('/work/runtime',b'{}'),('/work/syntax',b'')]):
        identity=[3,30+index,0o100600,1000,1000,1,0,1,1]
        pairs+=call(2,[0,0x800c1,0o600],{'path':path},3,{'kind':'sidecar','identity':identity})
        if raw:pairs+=call(1,[3,0,len(raw)],{'buffer_sha256':blob(archive,raw)},len(raw))
        pairs+=call(3,[3]);identity=list(identity);identity[6]=len(raw)
        sidecars[path]={'sha256':blob(archive,raw),'identity':identity}
    splice(obs,pairs);obs['events'][-1]['data']['sidecars']=sidecars
    return obs,archive


def test_two_fixed_exclusive_outputs_replay_to_exact_final_bytes():
    obs,archive=sidecar_run()
    assert n.verify_native_observation(obs,archive,purpose='TEST_ONLY')['stdout_bytes']==6


@pytest.mark.parametrize('mutation',['missing-excl','wrong-mode','preexisting-size','duplicate-create','read-output','map-output','wrong-final','wrong-inode','aliased-link','unclosed-output','extra-write','partial-result'])
def test_fixed_sidecar_protocol_rejects_every_nearby_write_escape(mutation):
    obs,archive=sidecar_run()
    if mutation=='missing-excl':obs['events'][4]['data']['args'][1]&=~0x80
    if mutation=='wrong-mode':obs['events'][4]['data']['args'][2]=0o644
    if mutation=='preexisting-size':obs['events'][5]['data']['detail']['identity'][6]=2
    if mutation=='duplicate-create':obs['events'][10]['data']['detail']['path']='/work/runtime'
    if mutation=='read-output':obs['events'][6]['data']={'nr':0,'args':[3,0,2,0,0,0],'detail':{}}
    if mutation=='map-output':obs['events'][6]['data']={'nr':9,'args':[0,4096,1,2,3,0],'detail':{}}
    if mutation=='wrong-final':obs['events'][-1]['data']['sidecars']['/work/runtime']['sha256']=blob(archive,b'xx')
    if mutation=='wrong-inode':obs['events'][-1]['data']['sidecars']['/work/runtime']['identity'][1]=99
    if mutation=='aliased-link':obs['events'][5]['data']['detail']['identity'][5]=2
    if mutation=='unclosed-output':obs['events'][9]['data']['result']=1
    if mutation=='extra-write':obs['events'][6]['data']['args'][0]=0
    if mutation=='partial-result':obs['events'][7]['data']['result']=1
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('fd,result,ioctl_request',[(0,-25,0x5401),(1,-25,0x5401),(2,-25,0x5401),(0,0,0x5401),(1,-22,0x5401),(3,-25,0x5401),(1,-25,0x1234)])
def test_only_exact_owned_nonterminal_stdio_failed_probe_is_accepted(fd,result,ioctl_request):
    obs,archive=fixture();splice(obs,call(16,[fd,ioctl_request,4096],result=result))
    if fd in (0,1,2) and result==-25 and ioctl_request==0x5401:
        assert n.verify_native_observation(obs,archive,purpose='TEST_ONLY')['stdout_bytes']==6
    else:
        with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('nr',[41,56,57,58,101,165,257+10000,298,319,322,425,435])
def test_unsupported_access_classes_have_no_fallthrough(nr):
    obs,archive=fixture();obs['events'][4]['data']['nr']=nr
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('mutation',['no-start','no-exit','no-eof','no-reap','cleanup','deadline','stderr','profile-limit','argv','actual-relabel','complete-flag'])
def test_incomplete_or_relabelled_records_cannot_supply_success(mutation):
    obs,archive=fixture()
    if mutation=='no-start':obs['events'][0]['kind']='enter'
    if mutation=='no-exit':obs['events'][-2]['kind']='exec'
    if mutation=='no-eof':obs['events'][-1]['data']['eof']=[]
    if mutation=='no-reap':obs['events'][-1]['data']['reaped']=[]
    if mutation=='cleanup':obs['events'][-1]['data']['cleanup']='uncertain'
    if mutation=='deadline':obs['events'][-1]['at_ns']=121*10**9
    if mutation=='stderr':obs['events'][-1]['data']['stderr_sha256']=blob(archive,b'lost diagnostic')
    if mutation=='profile-limit':obs['spec']['limits']['wall_seconds']=900
    if mutation=='argv':obs['spec']['argv'][1]='-q'
    if mutation=='actual-relabel':obs['purpose']='actual';obs['spec']['purpose']='actual'
    if mutation=='complete-flag':obs['complete']=True
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_source_guard_rejects_live_dispatch_and_core_guard_drift(monkeypatch):
    obs,archive=fixture();store=n.new_native_observation_store(purpose='TEST_ONLY')
    def substituted(*args):return 'write'
    monkeypatch.setattr(n,'_admit',substituted)
    with pytest.raises(ValueError):n.acquire_test_only_observation(store,{},b'',obs,archive)


def test_pure_html_replay_preserves_data_lf_and_marks_only_emitted_syntax():
    from twin import source_metadata_migration as m
    output,ranges=m._pure_observed_output('html-text-utf8/1',b'<p>A\n&amp;B</p><br/>',m.PROFILES['html-text-utf8/1'])
    assert output==b'\nA\n&B\n\n'
    assert [(r['start_byte'],r['end_byte'],r['event_kind']) for r in ranges]==[(0,1,'start'),(5,6,'end'),(6,7,'startend')]


def test_observed_loader_symlink_route_is_retained_and_replayed():
    obs,archive=resource_run()
    obs['events'][4]['data']['detail']={'path':'/data','requested_path':'/alias/data','route':[{'path':'/alias','target':'/'}]}
    assert '/data' in n.verify_native_observation(obs,archive,purpose='TEST_ONLY')['used_paths']
    obs['events'][4]['data']['detail']['route'][0]['target']='/elsewhere'
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_unknown_open_and_inherited_descriptors_cannot_hide_in_a_trace():
    obs,archive=fixture();identity=obs['files']['/data']['identity']
    splice(obs,call(2,[0,0x80000],{'path':'/missing'},3,{'kind':'file','identity':identity}))
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    obs,archive=fixture();obs['events'][0]['data']['fds'].append({'fd':3,'kind':'file','identity':[1,99]})
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_fd_reuse_and_aliases_cannot_gain_the_original_stdio_probe_exception():
    obs,archive=fixture();identity=obs['files']['/data']['identity']
    pairs=call(3,[0])+call(2,[0,0x80000],{'path':'/data'},0,{'kind':'file','identity':identity})+call(16,[0,0x5401,4096],result=-25)
    splice(obs,pairs)
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    obs,archive=fixture();splice(obs,call(32,[1],result=3)+call(16,[3,0x5401,4096],result=-25))
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_vector_buffers_and_premature_eof_have_exact_extent_checks():
    obs,archive=resource_run()
    obs['events'][6]['data']={'nr':19,'args':[3,4096,2,0,0,0],'detail':{'iovecs':[[8192,1],[12288,2]]}}
    assert n.verify_native_observation(obs,archive,purpose='TEST_ONLY')['stdout_bytes']==6
    obs['events'][6]['data']['detail']['iovecs']=[[8192,1]]
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    obs,archive=resource_run();obs['events'][7]['data']={'result':0,'detail':{'buffer_sha256':blob(archive,b''),'buffer_bytes':0}}
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_public_event_and_path_caps_are_holds(monkeypatch):
    obs,archive=fixture();monkeypatch.setattr(n,'MAX_EVENTS',4)
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_core_inventory_guard_cannot_return_a_forged_success(monkeypatch):
    from twin import source_metadata as sm
    obs,archive=fixture();store=n.new_native_observation_store(purpose='TEST_ONLY')
    monkeypatch.setattr(sm,'_runtime_helper_inventory',lambda modules: ([],()))
    with pytest.raises(ValueError):n.acquire_test_only_observation(store,{},b'',obs,archive)


def test_privately_held_result_tampering_does_not_resolve():
    obs,archive=fixture();store=n.new_native_observation_store(purpose='TEST_ONLY')
    handle=n.acquire_test_only_observation(store,{},b'',obs,archive)
    store._entries[id(handle)][1]['observation']['scope']='forged'
    with pytest.raises(ValueError):n.resolve_native_observation(store,handle)


def test_syscall_restart_is_explicitly_unsupported():
    import struct
    raw=bytearray(128);raw[0]=2;struct.pack_into('<I',raw,4,0xc000003e);struct.pack_into('<q',raw,24,-512);raw[32]=1
    with pytest.raises(ValueError):n.decode_syscall_info(bytes(raw),33)


def test_raw_ptrace_binding_can_be_exercised_only_with_a_pure_os_stub(monkeypatch):
    calls=[]
    class Fn:
        def __call__(self,*args):calls.append(args);return 7
    class Lib:ptrace=Fn()
    monkeypatch.setattr(n.ctypes,'CDLL',lambda *a,**kw:Lib())
    assert n._ptrace(0x420e,123,128,4096)==7
    assert calls==[(0x420e,123,128,4096)]


def test_candidate_bytes_are_a_permitted_superset_and_never_execution_authority():
    from twin import source_metadata as sm
    from twin import source_metadata_migration as m
    obs,archive=fixture();version=b'public declared tool version; no execution'
    version_pin=sm.sha256(version)
    rows=obs['spec']['candidates']
    retained={row['path']:archive[row['sha256']] for row in rows};retained[version_pin]=version
    process={'schema':'twin.source-extraction-native-tool-files/v1','executable':'/bin/tool',
             'files':[rows[0]],'version':'public-fixture-candidate','version_observation_sha256':version_pin}
    plan=n.prepare_native_candidate_plan('pdf-text-xpdf/1',b'public PDF-shaped bytes',predecessor_sha256='b'*64,
        member_id='public-candidate',process_files=process,retained_files=retained,native_configuration=b'')
    config,closure=n.validate_native_candidate_plan(plan,b'public PDF-shaped bytes')
    assert closure['scope']=='native-candidate-file-set/v1' and closure['platform_closure']=='OBSERVATION-REQUIRED'
    with pytest.raises(ValueError,match='host'):
        m.execute_new_extraction(plan,b'public PDF-shaped bytes')
    with pytest.raises(ValueError):m._validate_plan(plan,b'public PDF-shaped bytes')
    wrong=copy.deepcopy(plan);wrong['archive'][rows[0]['sha256']]=b'changed native candidate'
    with pytest.raises(ValueError):n.validate_native_candidate_plan(wrong,b'public PDF-shaped bytes')


def test_helper_runtime_and_syntax_share_the_fixed_exclusive_creation_protocol():
    import ast
    from pathlib import Path
    from twin import source_metadata_migration as m
    tree=ast.parse(Path(m.CHILD).read_text())
    calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='os' and node.func.attr=='open']
    assert len(calls)==2
    for node in calls:
        flags={part.attr for part in ast.walk(node.args[1]) if isinstance(part,ast.Attribute)}
        assert flags=={'O_WRONLY','O_CREAT','O_EXCL','O_CLOEXEC'}
        assert node.args[2].value==0o600
    assert not any(isinstance(node,ast.Attribute) and node.attr=='write_bytes' for node in ast.walk(tree))


def test_failed_stdio_probe_requires_the_fixed_validated_memory_extent():
    obs,archive=fixture();splice(obs,call(16,[1,0x5401,4096],{'buffer_bytes':35},-25))
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_public_success_records_and_serialized_handles_have_no_adoption_constructor():
    store=n.new_native_observation_store(purpose='TEST_ONLY')
    for value in ({'token':'invented'},'0'*64,object()):
        with pytest.raises(ValueError):n.resolve_native_observation(store,value)
    with pytest.raises(TypeError):n.NativeObservationStore('actual',None,None,{})
    with pytest.raises(TypeError):n.ObservedExtraction(object())


def test_exact_plan_binding_rejects_public_cross_pin_substitution_without_any_execution():
    from twin import source_metadata as sm
    obs,archive=fixture();version=b'public static candidate identity'
    vp=sm.sha256(version);rows=obs['spec']['candidates']
    retained={r['path']:archive[r['sha256']] for r in rows};retained[vp]=version
    pf={'schema':'twin.source-extraction-native-tool-files/v1','executable':'/bin/tool','files':[rows[0]],'version':'public-candidate','version_observation_sha256':vp}
    parent=b'public raw'
    plan=n.prepare_native_candidate_plan('pdf-text-xpdf/1',parent,predecessor_sha256='b'*64,member_id='public',process_files=pf,retained_files=retained,native_configuration=b'')
    config,closure=n.validate_native_candidate_plan(plan,parent)
    obs['spec']['purpose']='actual';obs['purpose']='actual'
    obs['spec']['plan_sha256']=sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'}))
    wanted=closure['process_files']['files']+closure['platform_files']+closure['driver_files']
    wanted+=[{'path':'/work/input','sha256':sm.sha256(parent),'bytes':len(parent)},
             {'path':'/work/config','sha256':plan['configuration_sha256'],'bytes':len(plan['archive'][plan['configuration_sha256']])},
             {'path':'/work/native-config','sha256':sm.sha256(b''),'bytes':0}]
    obs['spec']['candidates']=wanted
    invocation={'schema':'twin.source-extraction-invocation/v1','argv':obs['spec']['argv'],'cwd':'/work','environment':obs['spec']['environment'],'stdin':'OWNED-EOF-PIPE'}
    n.validate_observation_binding(obs,plan,parent,invocation)
    changed=copy.deepcopy(obs);changed['spec']['plan_sha256']='c'*64
    with pytest.raises(ValueError):n.validate_observation_binding(changed,plan,parent,invocation)
    changed=copy.deepcopy(obs);changed['spec']['candidates'].pop()
    with pytest.raises(ValueError):n.validate_observation_binding(changed,plan,parent,invocation)
    # A binding check has no side effect, handle, index enrolment, or actual store grant.
    with pytest.raises(ValueError):n.acquire_test_only_observation(n.new_native_observation_store(purpose='TEST_ONLY'),plan,parent,obs,archive)


def test_interpreter_alias_route_cannot_replace_the_retained_elf_requested_path():
    obs,archive=fixture();obs['events'][2]['data']['interpreter_route']={'path':'/lib/loader','requested_path':'/different','route':[{'path':'/different','target':'/lib/loader'}]}
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_failed_observation_schema_is_never_a_complete_success():
    obs,archive=fixture();obs['schema']='twin.native-file-observation-failure/v1';obs['failure']={'reaped':[100]}
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('where',['exit','returncode','map-protection','fd-number'])
def test_boolean_claims_are_not_kernel_integer_observations(where):
    obs,archive=fixture()
    if where=='exit':obs['events'][-2]['data']['status']=False
    if where=='returncode':obs['events'][-1]['data']['returncode']=False
    if where=='map-protection':obs['events'][2]['data']['maps'][0]['prot']=True
    if where=='fd-number':obs['events'][0]['data']['fds'][0]['fd']=False
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_requested_sidecar_write_is_bounded_before_any_io_dispatch(monkeypatch):
    obs,archive=sidecar_run();monkeypatch.setattr(n,'RUNTIME_BYTES',1)
    with pytest.raises(ValueError,match='write buffer limit'):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_native_formatting_remains_unestablished_independently_of_dependency_replay():
    from twin import source_metadata as sm
    from twin import source_metadata_migration as m
    raw=b'publisher-looking text'
    syntax={'schema':'twin.source-extraction-generated-syntax/v1','profile':'pdf-text-xpdf/1',
        'parent_sha256':'a'*64,'output_sha256':sm.sha256(raw),'output_bytes':len(raw),'ranges':[],
        'coverage':'complete-generated-syntax'}
    with pytest.raises(ValueError):m._syntax_check(syntax,'pdf-text-xpdf/1','a'*64,raw)


def test_migration_freezes_native_module_and_only_independent_json_index_pins(monkeypatch):
    from twin import source_metadata as sm
    from twin import source_metadata_migration as m
    policy={'purpose':'TEST_ONLY','allowed_transforms':[],'reviewer_id':'public','reviewer_role':'source-test'}
    indexes=['a'*64]
    authority=m.freeze_migration_authority('public','public','1',sm.sha256(sm.canonical(policy)),policy=policy,
        layout_config={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None},
        execution_contract={'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY','index_sha256s':indexes})
    indexes.append('b'*64)
    authority.verify()
    held=authority.source_checker.__kwdefaults__['execution_contract']
    assert held['index_sha256s']==['a'*64]
    assert [row['module'] for row in sm._json(authority.description)['runtime_helper_bindings']['modules']]==['twin.source_metadata_migration','twin.source_native_observation','twin.pdf_output_origin','twin.pdf_native_bridge']
    monkeypatch.setitem(n.SYSCALLS,'56','clone')
    with pytest.raises(ValueError):authority.verify()


def test_retained_buffer_budget_is_bounded_without_invoking_any_os_interface():
    archive={};budget={'bytes':0,'limit':3}
    assert n._runtime_blob(archive,b'ABC',budget)
    assert n._runtime_blob(archive,b'ABC',budget)
    with pytest.raises(ValueError):n._runtime_blob(archive,b'D',budget)
    assert list(archive.values())==[b'ABC']
