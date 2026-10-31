"""Invented Linux trace/bundle models only. Never invoke a child/native backend."""
import copy
import os
from pathlib import Path
import pytest
from twin import source_native_observation as n, source_metadata as sm
from test_source_native_observation import fixture, splice, call, blob

PROFILE='pdf-text-xpdf-origin/2'


def native_fixture():
    observation,archive=fixture();spec=observation['spec']
    output=b'AB';wire=(Path(__file__).parent/'fixtures/TEST_ONLY-pdf-output-origin/TEST_ONLY-contiguous-fragment.jsonl').read_bytes()
    observation['schema']='twin.native-file-observation/v2';spec['schema']='twin.native-observation-spec/v2';spec['profile']=PROFILE
    spec['argv']=['/bin/tool','-cfg','/work/native-config','-enc','UTF-8','-eol','unix','-nopgbrk','-twin-origin-fd','3','/work/input','-']
    observation['events'][1]['data']['detail']['argv']=spec['argv']
    fd={'fd':3,'kind':'pdf-origin','identity':[2,23],'generation':0,'access_mode':'write-only','file_type':'pipe','inheritable':True}
    initial=observation['events'][0]['data']['fds'];initial.append(fd)
    observation['events'][2]['data']['fds']=copy.deepcopy(initial)
    observation['events'][4]['data']['args'][2]=len(output);observation['events'][4]['data']['detail']['buffer_sha256']=blob(archive,output)
    observation['events'][5]['data']['result']=len(output)
    splice(observation,call(1,[3,4096,len(wire)],{'buffer_sha256':blob(archive,wire)},len(wire)))
    observation['events'][-2]['data']['fds']=[{k:r[k] for k in ('fd','kind','identity')} for r in initial]
    terminal=observation['events'][-1]['data'];terminal.update(stdout_sha256=blob(archive,output),origin_sha256=blob(archive,wire),origin_bytes=len(wire),eof=['stdout','stderr','origin'])
    terminal['wait']={'kind':'exited','raw_status':0,'exit_code':0,'observed_at_ns':14000}
    terminal['custody'].update(grace_deadline=3.000025,cleanup_ended=1.000029)
    eof=[]
    for name,fdno,raw in [('stdout',1,output),('stderr',2,b''),('origin',3,wire)]:
        eof.append({'kind':'pipe-eof','data':{'channel':name,'fd':fdno,'generation':0,'identity':initial[fdno]['identity'],'request_bytes':65536,'result':0,'captured_bytes':len(raw)}})
    observation['events'][-1:-1]=eof
    for i,event in enumerate(observation['events']):event['seq']=i;event['at_ns']=i*1000
    observation['events'][-1]['at_ns']=30000
    run={'started_at':'2026-10-31T00:00:00+00:00','ended_at':'2026-10-31T00:00:00.000030+00:00','monotonic_start_ns':1000000000,'elapsed_ns':30000,'wall_deadline_ns':121000000000,'cleanup_started_ns':1000025000,'cleanup_deadline_ns':3000025000}
    process={key:observation['events'][0]['data'][key] for key in ('pid','starttime','ppid','uid','gid')}
    invocation={'schema':'twin.source-extraction-invocation/v1','argv':spec['argv'],'cwd':spec['cwd'],'environment':spec['environment'],'stdin':'OWNED-EOF-PIPE'}
    seed={'plan_sha256':spec['plan_sha256'],'invocation_sha256':sm.sha256(sm.canonical(invocation)),'started_at':run['started_at'],'monotonic_start_ns':run['monotonic_start_ns'],'process':process}
    run['run_id']=sm.sha256(sm.canonical(seed));observation['run']=run
    return observation,archive


def test_profile2_native_replay_preserves_three_original_channels_without_issuing_authority():
    obs,archive=native_fixture()
    result=n.verify_native_observation(obs,archive,purpose='TEST_ONLY')
    assert result['origin_bytes']==len(archive[obs['events'][-1]['data']['origin_sha256']])
    assert result['stdout_bytes']==2
    with pytest.raises(ValueError):
        n.acquire_test_only_observation(n.new_native_observation_store(purpose='TEST_ONLY'),{},b'',obs,archive)


@pytest.mark.parametrize('nr,args,detail',[(0,[3,4096,1],{}),(17,[3,4096,1,0],{}),(19,[3,4096,1],{'iovecs':[[8192,1]]}),(3,[3],{}),(5,[3,4096],{}),(72,[3,1],{}),(16,[3,0x5401,4096],{'buffer_bytes':36}),(32,[3],{}),(33,[1,3],{}),(8,[3,0,0],{}),(9,[0,4096,1,2,3,0],{})])
def test_fd3_unsupported_uses_refuse_at_syscall_entry(nr,args,detail):
    obs,archive=native_fixture();splice(obs,call(nr,args,detail))
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('mutation',['missing-eof','zero-read-eof','eof-identity','generation','access','inherit','exec-channel','signal','raw-wait','origin-length','stdout','unknown-field','deadline','cleanup','profile'])
def test_native_v2_nearby_mutations_never_become_completed(mutation):
    obs,archive=native_fixture();terminal=obs['events'][-1]['data'];row=obs['events'][0]['data']['fds'][3]
    eof=next(e['data'] for e in obs['events'] if e['kind']=='pipe-eof')
    if mutation=='missing-eof':obs['events']=[e for e in obs['events'] if not(e['kind']=='pipe-eof' and e['data']['channel']=='origin')]
    if mutation=='zero-read-eof':eof['request_bytes']=0
    if mutation=='eof-identity':eof['identity']=[2,999]
    if mutation=='generation':row['generation']=1
    if mutation=='access':row['access_mode']='read-write'
    if mutation=='inherit':row['inheritable']=False
    if mutation=='exec-channel':obs['events'][2]['data']['fds'][3]['identity']=[2,999]
    if mutation=='signal':terminal['wait']={'kind':'signaled','raw_status':9,'signal':9,'core_dumped':False,'observed_at_ns':14000}
    if mutation=='raw-wait':terminal['wait']['raw_status']=256
    if mutation=='origin-length':terminal['origin_bytes']+=1
    if mutation=='stdout':terminal['stdout_sha256']=blob(archive,b'ABX')
    if mutation=='unknown-field':obs['approved']=True
    if mutation=='deadline':obs['run']['cleanup_deadline_ns']+=2000000000
    if mutation=='cleanup':terminal['custody']['absence_verified']=False
    if mutation=='profile':obs['spec']['profile']='pdf-text-xpdf-origin/999'
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_origin_writev_partial_prefixes_replay_exactly():
    obs,archive=native_fixture();entry=next(e for e in obs['events'] if e['kind']=='enter' and e['data']['args'][0]==3 and e['data']['nr']==1)
    at=obs['events'].index(entry);raw=archive[entry['data']['detail']['buffer_sha256']]
    entry['data']['nr']=20;entry['data']['args']=[3,4096,2,0,0,0];entry['data']['detail']['iovecs']=[[8192,10],[12288,len(raw)-10]]
    obs['events'][at+1]['data']['result']=15
    pairs=call(1,[3,8192,len(raw)-15],{'buffer_sha256':blob(archive,raw[15:])},len(raw)-15)
    obs['events'][at+2:at+2]=[{'kind':kind,'data':data} for kind,data in pairs]
    for i,e in enumerate(obs['events']):e.update(seq=i,at_ns=i*1000)
    obs['events'][-1]['at_ns']=30000
    assert n.verify_native_observation(obs,archive,purpose='TEST_ONLY')['origin_bytes']==len(raw)


def bundle_fixture():
    """Real retained source bytes plus explicitly synthetic compiler/binary association."""
    from twin import pdf_native_bridge as b, pdf_output_origin as p, source_metadata_migration as m
    obs,archive=native_fixture();root=Path(m.__file__).resolve().parents[1]
    supplied=os.environ.get('TWIN_XPDF_SOURCE_ARCHIVE')
    if not supplied: pytest.skip('fixed official archive not explicitly supplied; no download/build')
    retained=Path(supplied)
    blob(archive,retained.read_bytes())
    package=(root/'bench/pinned-candidate/xpdf-origin/SOURCE-PINS.json').read_bytes();assert blob(archive,package)==b.PACKAGE_SHA256
    patch=(root/'bench/pinned-candidate/xpdf-origin/xpdf-4.06-origin.patch').read_bytes();assert blob(archive,patch)==b.PATCH_SHA256
    inventory=b._driver_inventory();drivers=[]
    for path in sorted({str(Path(mod.__file__).resolve()) for mod in b._modules()}|{str(Path(sm.__file__).resolve()),str(sm.SCHEMA_PATH.resolve())}):
        raw=Path(path).read_bytes();drivers.append({'path':path,'sha256':blob(archive,raw),'bytes':len(raw)})
    files=[{k:v for k,v in row.items() if k!='identity'} for row in obs['files'].values()]
    version=blob(archive,b'TEST_ONLY synthetic tool version')
    closure={'schema':'twin.source-extraction-closure/v1','purpose':'TEST_ONLY','scope':'native-candidate-file-set/v1','platform_closure':'OBSERVATION-REQUIRED',
        'process_files':{'schema':'twin.source-extraction-native-tool-files/v1','executable':'/bin/tool','files':files,'version':'TEST_ONLY synthetic','version_observation_sha256':version},'platform_files':[],'driver_files':drivers,'driver_inventory':inventory}
    build={'schema':'twin.native-build-identity/v1','source_archive_sha256':b.ARCHIVE_SHA256,'source_package_sha256':b.PACKAGE_SHA256,'patch_sha256':b.PATCH_SHA256,
        **{key:blob(archive,('TEST_ONLY synthetic '+key).encode()) for key in ('prepared_tree_sha256','build_configuration_sha256','toolchain_sha256','build_log_sha256')},
        'executable_sha256':files[0]['sha256'],'executable_bytes':files[0]['bytes'],'target':{'system':'Linux','machine':'x86_64','elf_class':64}}
    verifier={'schema':'twin.pdf-origin-verifier-identity/v1','module':'twin.pdf_output_origin','source_sha256':blob(archive,Path(p.__file__).read_bytes()),'helper_inventory_sha256':blob(archive,sm.canonical(inventory)),
        'protocol_sha256':p.PROTOCOL_SHA256,'event_schema_sha256':p.SCHEMA_SHA256}
    config={'schema':'twin.source-extraction-config/v2','profile':PROFILE,'purpose':'TEST_ONLY','limits':m.PROFILES[PROFILE],'environment':m.ENVIRONMENT,'diagnostic_policy':'accept-bounded-on-zero','test_only_behavior':'normal',
        'native_config_sha256':blob(archive,b'TEST_ONLY fixed native config'),'pdf_origin':{'protocol_sha256':p.PROTOCOL_SHA256,'event_schema_sha256':p.SCHEMA_SHA256,'verifier_artifact_sha256':blob(archive,sm.canonical(verifier)),
        'build_identity_sha256':blob(archive,sm.canonical(build)),'origin_bytes':b.ORIGIN_BYTES,'origin_record_bytes':b.ORIGIN_RECORD_BYTES,'origin_events':b.ORIGIN_EVENTS}}
    parent=b'TEST_ONLY synthetic raw parent'
    plan={'schema':'twin.source-extraction-plan/v1','purpose':'TEST_ONLY','profile':PROFILE,'parent_sha256':blob(archive,parent),'parent_bytes':len(parent),'member_id':'derived','predecessor_sha256':'b'*64,
        'implementation_artifact_sha256':blob(archive,sm.canonical(closure)),'configuration_sha256':blob(archive,sm.canonical(config)),'archive':archive}
    wanted={r['path']:r for r in files+drivers}
    for name,raw in [('input',parent),('config',sm.canonical(config)),('native-config',archive[config['native_config_sha256']])]:
        wanted['/work/'+name]={'path':'/work/'+name,'sha256':blob(archive,raw),'bytes':len(raw)}
    obs['spec']['candidates']=list(wanted.values());obs['spec']['plan_sha256']=sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'}))
    for i,row in enumerate(wanted.values()):
        if row['path'] not in obs['files']:obs['files'][row['path']]={**row,'identity':[9,100+i,0o100444,1000,1000,1,row['bytes'],1,1]}
    process={k:obs['events'][0]['data'][k] for k in ('pid','starttime','ppid','uid','gid')}
    invocation={'schema':'twin.source-extraction-invocation/v1','argv':obs['spec']['argv'],'cwd':'/work','environment':m.ENVIRONMENT,'stdin':'OWNED-EOF-PIPE'}
    obs['run']['run_id']=sm.sha256(sm.canonical({'plan_sha256':obs['spec']['plan_sha256'],'invocation_sha256':sm.sha256(sm.canonical(invocation)),'started_at':obs['run']['started_at'],'monotonic_start_ns':obs['run']['monotonic_start_ns'],'process':process}))
    return plan,parent,obs,archive


def test_complete_test_only_bundle_cross_binding_is_not_actual_build_or_acquisition():
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=bundle_fixture()
    result=b._complete_pdf_extraction(plan,parent,obs,archive)
    b.verify_pdf_extraction_bundle(plan,parent,result)
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);assert dossier['schema']=='twin.source-extraction-execution/v3'
    assert 'generated_syntax_sha256' not in dossier
    assert len(sm._json(result['receipts'][result['index_sha256']]))==5
    assert len(sm._json(result['receipts'][result['member']['transform']['execution_receipt_artifact_sha256']]))==9
    with pytest.raises(ValueError):n.acquire_test_only_observation(n.new_native_observation_store(purpose='TEST_ONLY'),plan,parent,obs,archive)


@pytest.mark.parametrize('field',['plan_sha256','profile','purpose','run_id','parent_sha256','parent_bytes','configuration_sha256','implementation_artifact_sha256','executable','build_identity_sha256','verifier_artifact_sha256','invocation_sha256','host_policy_sha256','native_observation_sha256','process','streams','wait','interval','native_custody_sha256','workspace_cleanup','pdf_origin_map_sha256','errors'])
def test_each_host_envelope_substitution_with_rehashed_dossier_is_refused(field):
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=bundle_fixture();result=b._complete_pdf_extraction(plan,parent,obs,archive)
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);envelope=sm._json(result['receipts'][dossier['pdf_origin_observation_sha256']])
    value=envelope[field]
    envelope[field]=value+1 if type(value) is int else 'substituted' if type(value) is str else {'substituted':True}
    dossier['pdf_origin_observation_sha256']=blob(result['receipts'],sm.canonical(envelope))
    result['dossier_sha256']=blob(result['receipts'],sm.canonical(dossier))
    index=sm._json(result['receipts'][result['index_sha256']]);index['dossier_sha256']=result['dossier_sha256'];result['index_sha256']=blob(result['receipts'],sm.canonical(index))
    with pytest.raises(ValueError):b.verify_pdf_extraction_bundle(plan,parent,result)


@pytest.mark.parametrize('field',['standard_receipt_sha256','pdf_origin_map_sha256','pdf_origin_observation_sha256','native_observation_sha256','predecessor_sha256','origin','output_sha256','process_group','ended_at','workspace_cleanup','failure','generated_syntax_sha256'])
def test_rehashed_dossier_or_index_cannot_select_itself(field):
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=bundle_fixture();result=b._complete_pdf_extraction(plan,parent,obs,archive)
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);dossier[field]='c'*64
    result['dossier_sha256']=blob(result['receipts'],sm.canonical(dossier))
    index=sm._json(result['receipts'][result['index_sha256']]);index['dossier_sha256']=result['dossier_sha256'];result['index_sha256']=blob(result['receipts'],sm.canonical(index))
    with pytest.raises(ValueError):b.verify_pdf_extraction_bundle(plan,parent,result)


@pytest.mark.parametrize('mutation',['native-null-actual','test-only-host-hash','mixed-purpose','fatal','nonzero','post-footer-origin','post-footer-stdout','missing-reap','missing-exit-fd3','replaced-exit-fd3','zero-progress','write-error','excess-result','unknown-config','extra-env'])
def test_complete_builder_rejects_adjacent_terminal_transport_and_purpose_histories(mutation):
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=bundle_fixture();terminal=obs['events'][-1]['data']
    if mutation=='native-null-actual':obs['purpose']='actual';obs['spec']['purpose']='actual'
    if mutation=='test-only-host-hash':obs['host_policy_sha256']=blob(archive,b'TEST_ONLY public policy cannot select itself')
    if mutation=='mixed-purpose':plan['purpose']='actual'
    if mutation=='fatal':terminal['wait']={'kind':'signaled','raw_status':139,'signal':11,'core_dumped':True,'observed_at_ns':14000};terminal['returncode']=-11
    if mutation=='nonzero':terminal['wait'].update(raw_status=256,exit_code=1);terminal['returncode']=1
    if mutation=='post-footer-origin':terminal['origin_sha256']=blob(archive,archive[terminal['origin_sha256']]+b'{}\n');terminal['origin_bytes']+=3
    if mutation=='post-footer-stdout':terminal['stdout_sha256']=blob(archive,b'ABX')
    if mutation=='missing-reap':terminal['custody']['reaped']=[]
    if mutation=='missing-exit-fd3':obs['events'][next(i for i,e in enumerate(obs['events']) if e['kind']=='exit-stop')]['data']['fds'].pop()
    if mutation=='replaced-exit-fd3':next(e for e in obs['events'] if e['kind']=='exit-stop')['data']['fds'][-1]['identity']=[2,999]
    if mutation in ('zero-progress','write-error','excess-result'):
        i=next(i for i,e in enumerate(obs['events']) if e['kind']=='enter' and e['data']['nr']==1 and e['data']['args'][0]==3)
        obs['events'][i+1]['data']['result']={'zero-progress':0,'write-error':-5,'excess-result':obs['events'][i]['data']['args'][2]+1}[mutation]
    if mutation=='unknown-config':
        c=sm._json(archive[plan['configuration_sha256']]);c['approved']=True;plan['configuration_sha256']=blob(archive,sm.canonical(c))
    if mutation=='extra-env':obs['spec']['environment']={**obs['spec']['environment'],'HOST_PIN':'x'}
    with pytest.raises(ValueError):b._complete_pdf_extraction(plan,parent,obs,archive)


def test_blank_output_failure_never_issues_receipt_index_or_member():
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=bundle_fixture();run={'failure':'empty-output','stdout':b'','stderr':b'','origin':b'','observed_bytes_lower_bound':dict.fromkeys(('stdout','stderr','origin'),0),
        'process_group':obs['events'][-1]['data']['custody'],'started_at':obs['run']['started_at'],'ended_at':obs['run']['ended_at'],'exit_code':0,'elapsed_seconds':0.1,'streams_complete':True}
    result=b._failed_pdf_extraction(plan,parent,run,obs,archive,'preserved-unverified-group')
    assert result['status']=='failure' and 'member' not in result and 'index_sha256' not in result
    dossier=sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['schema']=='twin.source-extraction-execution/v3'
    assert dossier['standard_receipt_sha256'] is dossier['pdf_origin_map_sha256'] is dossier['pdf_origin_observation_sha256'] is None


def actual_shaped_fixture():
    """Public invented H/H facts only; this never creates actual observation state."""
    plan,parent,obs,archive=bundle_fixture()
    c=sm._json(archive[plan['configuration_sha256']]);c['purpose']='actual';plan['configuration_sha256']=blob(archive,sm.canonical(c))
    closure=sm._json(archive[plan['implementation_artifact_sha256']]);closure['purpose']='actual';closure['process_files']['version']='synthetic declared association, never built';plan['implementation_artifact_sha256']=blob(archive,sm.canonical(closure));plan['purpose']='actual'
    policy={'schema':'twin.native-host-policy/v1','scope':n.SCOPE,'custodian':'TEST_ONLY public hypothetical independent custodian',
        'not_before':'2026-10-31T00:00:00+00:00','not_after':'2026-10-31T01:00:00+00:00','roots':['/bin','/lib','/data',str(Path(__file__).resolve().parents[1])],
        'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':[plan['configuration_sha256'],c['pdf_origin']['build_identity_sha256']]}
    obs['host_policy_sha256']=blob(archive,sm.canonical(policy));obs['purpose']='actual';obs['spec']['purpose']='actual'
    wanted={r['path']:r for r in obs['spec']['candidates']};wanted['/work/config']={'path':'/work/config','sha256':plan['configuration_sha256'],'bytes':len(archive[plan['configuration_sha256']])}
    obs['spec']['candidates']=list(wanted.values());obs['files']['/work/config'].update(wanted['/work/config'])
    obs['files']['/work/config']['identity'][6]=wanted['/work/config']['bytes']
    obs['spec']['plan_sha256']=sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'}))
    obs['run']['run_id']=n._run_identity(obs['spec'],obs['run'],obs['events'][0]['data'])
    return plan,parent,obs,archive


def test_actual_shaped_h_h_consistency_does_not_acquire_and_null_actual_is_never_exception():
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=actual_shaped_fixture()
    result=b._complete_pdf_extraction(plan,parent,obs,archive);b.verify_pdf_extraction_bundle(plan,parent,result)
    with pytest.raises(ValueError):n.acquire_native_observation(n.new_native_observation_store(purpose='actual'),plan,parent)
    obs['host_policy_sha256']=None
    with pytest.raises(ValueError):b._complete_pdf_extraction(plan,parent,obs,archive)


def test_actual_missing_preselected_build_association_holds_before_os(monkeypatch):
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=actual_shaped_fixture();policy=sm._json(archive[obs['host_policy_sha256']]);policy['evidence_sha256s']=[blob(archive,b'public unrelated operating evidence')]
    import datetime
    now=datetime.datetime.now(datetime.timezone.utc)
    policy.update(not_before=(now-datetime.timedelta(minutes=1)).isoformat(),not_after=(now+datetime.timedelta(minutes=1)).isoformat())
    context=n.freeze_native_host_context(policy,{pin:archive[pin] for pin in policy['evidence_sha256s']},sm.sha256(sm.canonical(policy)))
    store=n.new_native_observation_store(purpose='actual',host_context=context)
    monkeypatch.setattr(n.platform,'system',lambda: (_ for _ in ()).throw(AssertionError('no OS availability probe')))
    with pytest.raises(ValueError,match='association'):b._require_actual_selection(store,plan)
    assert not store._entries


@pytest.mark.parametrize('nr,args,detail',[(32,[3],{}),(33,[3,8],{}),(292,[3,8,0],{}),(72,[3,0,8],{}),(33,[8,3],{}),(257,[-100,0,0,0],{'path':'/proc/self/fd/3'}),(2,[0,0,0],{'path':'/dev/fd/3'})])
def test_output_aliases_or_reopens_refused_before_dispatch(nr,args,detail):
    obs,archive=native_fixture();splice(obs,call(nr,args,detail))
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


@pytest.mark.parametrize('mutation',['missing','duplicate','wrong-channel','wrong-count','wrong-fd'])
def test_positive_capacity_eof_is_unique_and_exact(mutation):
    obs,archive=native_fixture();i=next(i for i,e in enumerate(obs['events']) if e['kind']=='pipe-eof' and e['data']['channel']=='origin')
    if mutation=='missing':obs['events'].pop(i)
    if mutation=='duplicate':obs['events'].insert(i,copy.deepcopy(obs['events'][i]))
    if mutation=='wrong-channel':obs['events'][i]['data']['channel']='hup'
    if mutation=='wrong-count':obs['events'][i]['data']['captured_bytes']-=1
    if mutation=='wrong-fd':obs['events'][i]['data']['fd']=99
    for j,e in enumerate(obs['events']):e['seq']=j
    with pytest.raises(ValueError):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_origin_requested_record_and_event_bounds_checked_before_dispatch():
    with pytest.raises(ValueError):n._origin_transport_prefix(b'',b'x'*65536)
    with pytest.raises(ValueError):n._origin_transport_prefix(b'',b'\n'*1000003)


def test_source_inventory_covers_bridge_builder_and_migration_helpers(monkeypatch):
    from twin import pdf_native_bridge as b, source_metadata_migration as m
    store=n.new_native_observation_store(purpose='actual')
    assert {row['module'] for row in b._driver_inventory()}=={'twin.source_native_observation','twin.source_metadata_migration','twin.pdf_output_origin','twin.pdf_native_bridge'}
    monkeypatch.setattr(b,'_complete_pdf_extraction',lambda *args:{'status':'success'})
    with pytest.raises(ValueError):store._guard.verify()
    with pytest.raises(ValueError):n.resolve_native_observation(store,object())


def test_replay_retained_buffer_budget_is_independent_of_child_requested_flags(monkeypatch):
    # Lower only the pure validator's named budget to exercise accounting cheaply.
    obs,archive=native_fixture()
    from twin import pdf_native_bridge as b
    monkeypatch.setattr(b,'BUFFER_BYTES',1)
    with pytest.raises(ValueError,match='buffer'):n.verify_native_observation(obs,archive,purpose='TEST_ONLY')


def test_failure_after_final_native_cleanup_keeps_native_evidence_and_no_final_handle(monkeypatch):
    # Exercise only finalizer with invented completed facts and a pure clock model.
    obs,archive=native_fixture();obs['purpose']='actual';obs['spec']['purpose']='actual'
    terminal=obs['events'].pop()['data']
    run={'native_observation':obs,'native_artifacts':archive,'failure':None,'_monotonic_start':1.0,'_native_terminal':terminal,'_buffer_budget':{'bytes':0,'limit':456*1048576},
        'process_group':terminal['custody'],'stdout':b'AB','stderr':b'','origin':archive[terminal['origin_sha256']],
        'observed_bytes_lower_bound':{'stdout':2,'stderr':0,'origin':terminal['origin_bytes']},'_native_eof':['stdout','stderr','origin'],'exit_code':0,'_native_wait':terminal['wait']}
    monkeypatch.setattr(n.time,'monotonic',lambda:1.000030)
    failed,retained=n._finalize_pdf_native_run(run,'preserved-unverified-group')
    assert failed['schema']=='twin.native-file-observation-failure/v2'
    assert failed['failure']['reason']=='native-workspace-cleanup-uncertain'
    assert run['ended_at']==failed['run']['ended_at'] and retained==archive


def test_source_final_flow_has_one_builder_before_deposit_and_resolve_only_verifies():
    import ast,inspect,textwrap
    from twin import source_metadata_migration as m, pdf_native_bridge as b
    def calls(fn):
        tree=ast.parse(textwrap.dedent(inspect.getsource(fn)))
        return [node.func.attr for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute)]
    assert calls(m._execute_prepared_extraction).count('_complete_pdf_extraction')==1
    assert '_complete_pdf_extraction' not in calls(n.resolve_native_observation)
    assert '_complete_pdf_extraction' not in calls(b.verify_pdf_extraction_bundle)
    source=inspect.getsource(m._execute_prepared_extraction)
    assert source.index('_cleanup_workspace')<source.index('_finalize_pdf_native_run')<source.index('_complete_pdf_extraction')
    assert source.index('_complete_pdf_extraction')<source.index('pdf_native_bridge.verify_pdf_extraction_bundle')
    assert '_deposit(' not in source and '_deposit(' not in inspect.getsource(b)


def replace_origin_wire(obs,archive,wire):
    event=next(e for e in obs['events'] if e['kind']=='enter' and e['data']['nr']==1 and e['data']['args'][0]==3);i=obs['events'].index(event)
    event['data']['args'][2]=len(wire);event['data']['detail']['buffer_sha256']=blob(archive,wire);obs['events'][i+1]['data']['result']=len(wire)
    obs['events'][-1]['data'].update(origin_sha256=blob(archive,wire),origin_bytes=len(wire))
    next(e for e in obs['events'] if e['kind']=='pipe-eof' and e['data']['channel']=='origin')['data']['captured_bytes']=len(wire)


@pytest.mark.parametrize('role',['observation','statement','excerpt','alias'])
def test_migration_gates_every_publisher_path_and_alias_before_stock(role,monkeypatch):
    from twin import source_metadata_migration as m, pdf_native_bridge as b
    stock=[];monkeypatch.setattr(sm,'retained_source_checker',lambda *args:stock.append(args))
    plan,parent,obs,archive=actual_shaped_fixture()
    wire=(Path(__file__).parent/'fixtures/TEST_ONLY-pdf-output-origin/TEST_ONLY-deleted-hyphen.jsonl').read_bytes();replace_origin_wire(obs,archive,wire)
    result=b._complete_pdf_extraction(plan,parent,obs,archive);member=result['member']
    manifest={'members':{'derived':member,'original':{'id':'original','role':'original','sha256':plan['parent_sha256'],'bytes':len(parent)}},'observations':{},'statement':{'origin_role':'analyst'},'visible_excerpts':[]}
    witness={'member_id':'derived','member_sha256':member['sha256'],'start_byte':0,'end_byte':2,'text_utf8':'AB'}
    if role=='observation':manifest['observations']['o']={'witness':witness}
    if role=='statement':manifest['statement']={'origin_role':'publisher-quotation','witness':witness}
    if role=='excerpt':manifest['visible_excerpts']=[{'origin_role':'publisher-quotation','witness':witness}]
    if role=='alias':
        manifest['members']['alias']={'id':'alias','role':'source-document','parent':{'member_id':'derived','sha256':member['sha256']},'sha256':member['sha256'],'bytes':2};witness['member_id']='alias';manifest['observations']['o']={'witness':witness}
    policy={'purpose':'actual','allowed_transforms':[{key:member['transform'][key] for key in ('identity','version','implementation_artifact_sha256','configuration_sha256')}]}
    contract={'schema':'twin.source-migration-execution-contract/v1','purpose':'actual','index_sha256s':[result['index_sha256']]}
    with pytest.raises(ValueError):m.migration_source_checker(manifest,result['archive'],result['receipts'],policy,execution_contract=contract)
    assert not stock


def test_supported_endpoint_reaches_unchanged_stock_and_missing_independent_index_holds(monkeypatch):
    from twin import source_metadata_migration as m, pdf_native_bridge as b
    stock=[];monkeypatch.setattr(sm,'retained_source_checker',lambda *args:stock.append(args))
    plan,parent,obs,archive=actual_shaped_fixture();result=b._complete_pdf_extraction(plan,parent,obs,archive);member=result['member']
    manifest={'members':{'derived':member,'original':{'id':'original','role':'original','sha256':plan['parent_sha256'],'bytes':len(parent)}},
        'observations':{'o':{'witness':{'member_id':'derived','member_sha256':member['sha256'],'start_byte':0,'end_byte':1,'text_utf8':'A'}}},'statement':{'origin_role':'analyst'},'visible_excerpts':[]}
    policy={'purpose':'actual','allowed_transforms':[{key:member['transform'][key] for key in ('identity','version','implementation_artifact_sha256','configuration_sha256')}]}
    contract={'schema':'twin.source-migration-execution-contract/v1','purpose':'actual','index_sha256s':[]}
    with pytest.raises(ValueError,match='independently'):m.migration_source_checker(manifest,result['archive'],result['receipts'],policy,execution_contract=contract)
    contract['index_sha256s']=[result['index_sha256']]
    m.migration_source_checker(manifest,result['archive'],result['receipts'],policy,execution_contract=contract)
    assert len(stock)==1
    assert all(a is c for a,c in zip(stock[0],(manifest,result['archive'],result['receipts'],policy)))


@pytest.mark.parametrize('field',['source_archive_sha256','source_package_sha256','patch_sha256','executable_sha256','executable_bytes','target'])
def test_fixed_selected_build_fields_cannot_be_relabelled(field):
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=bundle_fixture();c=sm._json(archive[plan['configuration_sha256']]);build=sm._json(archive[c['pdf_origin']['build_identity_sha256']])
    build[field]=7 if field=='executable_bytes' else {'system':'Darwin','machine':'arm64','elf_class':64} if field=='target' else blob(archive,b'TEST_ONLY different source/build association')
    c['pdf_origin']['build_identity_sha256']=blob(archive,sm.canonical(build));plan['configuration_sha256']=blob(archive,sm.canonical(c))
    with pytest.raises(ValueError):b._validate_plan(plan,parent)


@pytest.mark.parametrize('field',['source_sha256','helper_inventory_sha256','protocol_sha256','event_schema_sha256','module'])
def test_selected_verifier_cross_binding_cannot_be_relabelled(field):
    from twin import pdf_native_bridge as b
    plan,parent,obs,archive=bundle_fixture();c=sm._json(archive[plan['configuration_sha256']]);v=sm._json(archive[c['pdf_origin']['verifier_artifact_sha256']]);v[field]='wrong'
    c['pdf_origin']['verifier_artifact_sha256']=blob(archive,sm.canonical(v));plan['configuration_sha256']=blob(archive,sm.canonical(c))
    with pytest.raises(ValueError):b._validate_plan(plan,parent)


def test_recomputed_consistent_public_result_cannot_replace_separately_held_native_record():
    from twin import pdf_native_bridge as b
    plan,parent,held,archive=bundle_fixture();changed=copy.deepcopy(held)
    changed['events'][0]['data'].update(pid=101,starttime=124)
    exitstop=next(e for e in changed['events'] if e['kind']=='exit-stop')['data'];exitstop.update(pid=101,starttime=124)
    terminal=changed['events'][-1]['data'];terminal['reaped']=[101];terminal['custody'].update(leader_pid=101,reaped=[101])
    changed['run']['run_id']=n._run_identity(changed['spec'],changed['run'],changed['events'][0]['data'])
    result=b._complete_pdf_extraction(plan,parent,changed,archive);b.verify_pdf_extraction_bundle(plan,parent,result)
    with pytest.raises(ValueError,match='actual completed native record'):n._completed_pdf_result((result,held))
    actual_result,actual_record=n._completed_pdf_result((result,changed))
    assert actual_result is result and actual_record is changed
    with pytest.raises(ValueError):n._completed_pdf_result([result,changed])


@pytest.mark.parametrize('elapsed,success',[(0.000030,True),(121.0,False)])
def test_finalizer_captures_after_cleanup_with_original_deadline_only(elapsed,success,monkeypatch):
    import datetime
    plan,parent,obs,archive=actual_shaped_fixture();terminal=obs['events'].pop()['data']
    run={'native_observation':obs,'native_artifacts':archive,'failure':None,'_monotonic_start':1.0,'_native_terminal':terminal,'_buffer_budget':{'bytes':0,'limit':456*1048576},
        'process_group':terminal['custody'],'stdout':b'AB','stderr':b'','origin':archive[terminal['origin_sha256']],
        'observed_bytes_lower_bound':{'stdout':2,'stderr':0,'origin':terminal['origin_bytes']},'_native_eof':['stdout','stderr','origin'],'exit_code':0,'_native_wait':terminal['wait']}
    fixed=datetime.datetime(2026,10,31,tzinfo=datetime.timezone.utc)+datetime.timedelta(seconds=elapsed)
    class Clock(datetime.datetime):
        @classmethod
        def now(cls,tz=None):return fixed
    monkeypatch.setattr(n.time,'monotonic',lambda:1.0+elapsed);monkeypatch.setattr(n.datetime,'datetime',Clock)
    completed,_=n._finalize_pdf_native_run(run,'removed')
    assert completed['run']['ended_at']==fixed.isoformat()
    assert (completed['schema']=='twin.native-file-observation/v2') is success
    if success:
        assert completed['events'][-1]['at_ns']==completed['run']['elapsed_ns']
        assert completed['events'][-1]['data']['custody']['cleanup_ended']<=1.0+elapsed
    else:assert run['failure']=='native-deadline-or-terminal-incomplete'


def test_absent_explicit_archive_is_a_disclosed_resource_hold(monkeypatch):
    monkeypatch.delenv('TWIN_XPDF_SOURCE_ARCHIVE',raising=False)
    with pytest.raises(pytest.skip.Exception,match='not explicitly supplied'):bundle_fixture()


def test_incremental_event_budget_counts_start_and_eof_before_continuation(monkeypatch):
    events=[];budget={'bytes':2};limits={'wall_seconds':120};monkeypatch.setattr(n.time,'monotonic',lambda:1.0)
    n._append(events,'start',{},1.0,limits,budget=budget)
    assert budget['bytes']==len(sm.canonical(events))
    monkeypatch.setattr(n,'MAX_EVENT_BYTES',budget['bytes']+1)
    with pytest.raises(ValueError,match='event limit'):n._append(events,'pipe-eof',{},1.0,limits,budget=budget)
    assert len(events)==1


def test_failed_capture_retention_shares_original_buffer_cap(monkeypatch):
    obs,_=native_fixture();terminal=obs['events'].pop()['data'];archive={sm.sha256(b'123456'):b'123456'}
    run={'native_observation':obs,'native_artifacts':archive,'failure':'buffer-overflow','_monotonic_start':1.0,'_native_terminal':None,
        '_buffer_budget':{'bytes':6,'limit':7},'process_group':terminal['custody'],'stdout':b'AB','stderr':b'','origin':b'XYZ',
        'observed_bytes_lower_bound':{'stdout':2,'stderr':0,'origin':3},'_native_eof':[],'exit_code':None,'_native_wait':None}
    monkeypatch.setattr(n.time,'monotonic',lambda:1.000030)
    failed,artifacts=n._finalize_pdf_native_run(run,'preserved-unverified-group')
    assert sum(map(len,artifacts.values()))<=7
    assert failed['failure']['streams']['stdout']['observed_bytes_lower_bound']==2
    assert failed['failure']['streams']['stdout']['truncated'] is True
    assert failed['failure']['streams']['origin']['truncated'] is True
