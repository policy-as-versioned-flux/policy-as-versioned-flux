"""Invented DATA and explicitly fabricated private capabilities/OS models only."""
import copy
from typing import Any, cast
import pytest
from twin import source_metadata as sm, pdf_comparison_capture as c, pdf_remap_resources as r
from twin import pdf_remap_driver as d
from test_pdf_remap_resources import stage_model,full_control_fixture,prepared,OSModel
from test_pdf_comparison_capture import GuardModel,authority_model,prepared_fixture


@pytest.mark.parametrize('substitute',[{},object(),'a'*64,None])
def test_passive_records_cannot_prepare_capture_compare_or_finish(monkeypatch,substitute):
    def forbidden(*a,**k):raise AssertionError('OS reached from public DATA')
    monkeypatch.setattr(d.time,'monotonic',forbidden)
    for call in (lambda:d._prepare_remap_route(substitute,{}),lambda:d._capture_next_remap_baseline(substitute,cast(Any,{})),lambda:d._capture_next_remap_patched(substitute,cast(Any,{}),{}),lambda:d._compare_remap_pair(substitute),lambda:d._finish_remap_route(substitute)):
        with pytest.raises(ValueError):call()


def actual_control_fixture(index=0):
    """Public invented actual-shaped replay; never selects H or runs a converter."""
    packet,left,right=full_control_fixture(index);archive=right['archive'];plan=right['plan'];plan['archive']=archive
    config=sm._json(archive[plan['configuration_sha256']]);config['purpose']='actual'
    raw=sm.canonical(config);archive[sm.sha256(raw)]=raw;plan['configuration_sha256']=sm.sha256(raw)
    closure=sm._json(archive[plan['implementation_artifact_sha256']]);closure['purpose']='actual';closure['process_files']['version']='PURE_MODEL synthetic never built'
    raw=sm.canonical(closure);archive[sm.sha256(raw)]=raw;plan['implementation_artifact_sha256']=sm.sha256(raw);plan['purpose']='actual'
    obs=right['observation'];obs['purpose']='actual';obs['spec']['purpose']='actual'
    row=obs['files']['/work/config'];row.update(sha256=plan['configuration_sha256'],bytes=len(archive[plan['configuration_sha256']]))
    row['identity'][6]=row['bytes']
    for candidate in obs['spec']['candidates']:
        if candidate['path']=='/work/config':candidate.update({k:row[k] for k in ('sha256','bytes')})
    obs['spec']['plan_sha256']=sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'}))
    obs['run']['run_id']=d.n._run_identity(obs['spec'],obs['run'],obs['events'][0]['data'])
    wrapper=archive[plan['configuration_sha256']]
    for name,bundle in [('baseline',left),('patched',right)]:
        evidence=r.remap_native_projection(packet,wrapper if name=='patched' else None)['evidence']
        evidence.update({key:packet['archive'][key] for key in (packet['pair_plan']['suite_selection_sha256'],packet['pair_plan']['build_pair']['pristine_build_sha256'],packet['pair_plan']['build_pair']['patched_build_sha256'])})
        bundle['archive'].update(evidence)
        policy={'schema':'twin.native-host-policy/v1','scope':d.n.SCOPE,'custodian':'PURE_MODEL '+name,'not_before':'2026-10-31T00:00:00+00:00','not_after':'2026-10-31T00:05:00+00:00','roots':['/bin','/lib','/data','/work','/TEST_ONLY-remap-controls',str(__import__('pathlib').Path(d.__file__).resolve().parents[1])],'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':sorted(evidence)}
        raw=sm.canonical(policy);bundle['archive'][sm.sha256(raw)]=raw;bundle['observation']['host_policy_sha256']=sm.sha256(raw)
    return packet,left,right


def test_actual_comparative_purpose_is_separate_from_actual_observation_mode():
    packet,left,right=actual_control_fixture()
    c.check_comparison_events(left['observation'],left['archive'],observation_mode='actual')
    d.n.verify_native_observation(right['observation'],right['archive'],purpose='actual')
    assert r.check_remap_control(packet,left,right)['qualification']=='NONE'


class DriverGuard(GuardModel):
    description=b'{"purpose":"PURE_MODEL_SOURCE_GUARD_ONLY"}'


def prepared_driver(monkeypatch):
    original,model,clock=stage_model(monkeypatch)
    monkeypatch.setattr(r,'_source_guard',lambda:DriverGuard())
    monkeypatch.setattr(d,'_SOURCE_ROOT','/TEST_ONLY/resources')
    pair,plan,archive=prepared_fixture()
    d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
    return original,model,clock


def test_flow_owner_and_placeholders_precede_both_original_charges(monkeypatch):
    original,model,clock=stage_model(monkeypatch);monkeypatch.setattr(d,'_SOURCE_ROOT','/TEST_ONLY/resources');monkeypatch.setattr(r,'_source_guard',lambda:DriverGuard())
    pair,plan,archive=prepared_fixture();charge=c._charge_technical_bytes;seen=[]
    def checked(owner,count):
        state=owner._technical_state
        assert state._original_owner is owner and state._remap_flow.owner is owner
        assert state.deadline is None
        seen.append(count);charge(owner,count)
    monkeypatch.setattr(c,'_charge_technical_bytes',checked)
    d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
    flow=d._flow(original)
    assert seen==[4*1048576,2*1048576] and original._retained==6*1048576
    assert flow.phase=='READY' and [p['pair_plan']['schedule_index'] for p in flow.packets]==[18,19,20]
    assert [p['comparison_plan']['schedule_index'] for p in flow.packets]==[36,38,40]
    assert original._next==0 and not original._stopped and len(model.fds)==2
    with pytest.raises(ValueError):d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
    with pytest.raises(ValueError):copy.deepcopy(flow)


@pytest.mark.parametrize('kind',['missing-root','wrong-owner','copied-record','bad-clock','capacity','partial-stage'])
def test_private_preparation_and_owner_neighbor_refusals(monkeypatch,kind):
    if kind in ('wrong-owner','copied-record'):
        original,model,clock=prepared_driver(monkeypatch);other,_,_=stage_model(monkeypatch)
        other._technical_state=original._technical_state if kind=='wrong-owner' else r._held_stage_data(original)
        with pytest.raises(ValueError):d._held_remap_data(other)
        return
    original,model,clock=stage_model(monkeypatch);monkeypatch.setattr(r,'_source_guard',lambda:DriverGuard());monkeypatch.setattr(d,'_SOURCE_ROOT',None if kind=='missing-root' else '/TEST_ONLY/resources')
    if kind=='bad-clock':clock[0]=float('nan')
    if kind=='capacity':original._retained=c.MAX_SUITE_BYTES
    if kind=='partial-stage':model.fail='write'
    _,plan,archive=prepared_fixture()
    with pytest.raises((ValueError,OSError)):d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
    if kind=='missing-root':assert model.log==[] and original._technical_state is None
    else:assert original._technical_state is not None and original._stopped


@pytest.mark.parametrize('index',[0,1,2])
def test_ordinary_public_v1_routes_still_refuse_each_v2_packet(index):
    packet=prepared()[index]
    with pytest.raises(ValueError):c._plan(packet['comparison_plan'],packet['archive'])
    with pytest.raises(ValueError):c.compare_pair(packet['pair_plan'],cast(Any,{}))


def full_driver_models(monkeypatch,index=0,host_window=None):
    """Complete pure actual-shaped private completion model. No acquisition occurs."""
    from pathlib import Path
    monkeypatch.setattr(d.n,'_host_window',host_window if host_window is not None else lambda context,**kwargs:sm._json(context._policy))
    old_packet,left,right=actual_control_fixture(index)
    original,model,clock=stage_model(monkeypatch);monkeypatch.setattr(r,'_source_guard',lambda:DriverGuard());monkeypatch.setattr(d,'_SOURCE_ROOT','/TEST_ONLY/resources')
    archive=old_packet['archive'];pair=copy.deepcopy(old_packet['pair_plan']);pair.update(schema='TEST_ONLY-pdf-pair-plan/v1',schedule_index=0,resource=None,config={'sha256':sm.sha256(b''),'bytes':0});archive[sm.sha256(b'')]=b''
    raw=sm.canonical(pair);archive[sm.sha256(raw)]=raw
    ordinary=copy.deepcopy(old_packet['comparison_plan']);ordinary.update(schema='TEST_ONLY-pdf-baseline-plan/v1',schedule_index=0,resource=None,config=pair['config'],pair_plan_sha256=sm.sha256(raw))
    rows=sm._json(archive[ordinary['candidate_inventory_sha256']]);rows=[row for row in rows if row['path']!=old_packet['pair_plan']['resource']['path']];raw=sm.canonical(rows);archive[sm.sha256(raw)]=raw;ordinary['candidate_inventory_sha256']=sm.sha256(raw)
    d._prepare_remap_route(original,{'ordinary_plan':ordinary,'archive':archive});flow=d._flow(original);packet=flow.packets[index];entry=flow.entries[index];resource=packet['pair_plan']['resource']
    right_archive=right['archive'];right_archive.update(packet['archive']);native=right['plan'];native['archive']=right_archive
    config=sm._json(right_archive[native['configuration_sha256']]);config['native_config_sha256']=packet['pair_plan']['config']['sha256'];raw=sm.canonical(config);right_archive[sm.sha256(raw)]=raw;native['configuration_sha256']=sm.sha256(raw)
    closure=sm._json(right_archive[native['implementation_artifact_sha256']]);closure['platform_files']=[{'path':resource['path'],**resource['blob']}];raw=sm.canonical(closure);right_archive[sm.sha256(raw)]=raw;native['implementation_artifact_sha256']=sm.sha256(raw)
    contexts=[]
    for side,bundle in enumerate((left,right)):
        held=bundle['archive'];held.update(packet['archive']);held.update(flow.records);obs=bundle['observation']
        candidates=({row['path']:row for row in closure['process_files']['files']+closure['platform_files']+closure['driver_files']} if side else {row['path']:row for row in c._candidate_rows(packet['comparison_plan'],packet['archive'],'/work')})
        if side:
            for name,pin in [('input',packet['pair_plan']['fixture']['sha256']),('native-config',packet['pair_plan']['config']['sha256']),('config',native['configuration_sha256'])]:candidates['/work/'+name]={'path':'/work/'+name,'sha256':pin,'bytes':len(held[pin])}
        obs['spec']['candidates']=list(candidates.values());obs['files']={}
        for j,(path,row) in enumerate(candidates.items()):obs['files'][path]={**row,'identity':copy.deepcopy(resource['identity']) if path==resource['path'] else [9,100+j,0o100444,1000,1000,1,row['bytes'],1,1]}
        for event in obs['events']:
            for row in event['data'].get('maps',[]):row['identity']=obs['files'][row['path']]['identity'][:2]
        pending=None
        for event in obs['events']:
            data=event['data']
            if event['kind']=='enter':
                if data['nr']==2:
                    path=data['detail']['path'];data['detail']['path']=resource['path'] if path.endswith('-remap.txt') else path;pending=data['detail']['path']
                elif data['nr']==0 and pending in obs['files']:data['args'][2]=obs['files'][pending]['bytes']+1
            elif event['kind']=='leave' and pending in obs['files']:
                row=obs['files'][pending]
                if 'kind' in data['detail']:data['detail']['identity']=copy.deepcopy(row['identity'])
                elif 'buffer_bytes' in data['detail']:data['result']=row['bytes'];data['detail'].update(buffer_bytes=row['bytes'],buffer_sha256=row['sha256'])
                elif data['result']==0:pending=None
        wrapper=right_archive[native['configuration_sha256']]
        evidence=r.remap_native_projection(packet,wrapper if side else None)['evidence'];evidence.update(flow.records)
        for pin in (original._selection,packet['pair_plan']['build_pair']['pristine_build_sha256'],packet['pair_plan']['build_pair']['patched_build_sha256']):evidence[pin]=packet['archive'][pin]
        if side:evidence[native['implementation_artifact_sha256']]=held[native['implementation_artifact_sha256']]
        policy={'schema':'twin.native-host-policy/v1','scope':d.n.SCOPE,'custodian':'PURE_MODEL_driver_'+str(index)+'_'+str(side),'not_before':'2026-10-31T00:00:00+00:00','not_after':'2026-10-31T00:05:00+00:00','roots':['/bin','/lib','/data','/work','/TEST_ONLY',str(Path(d.__file__).resolve().parents[1])],'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':sorted(evidence)}
        held.update(evidence);raw=sm.canonical(policy);held[sm.sha256(raw)]=raw;obs['host_policy_sha256']=sm.sha256(raw)
        obs['spec']['plan_sha256']=sm.sha256(sm.canonical({k:v for k,v in native.items() if k!='archive'})) if side else sm.sha256(sm.canonical(packet['comparison_plan']))
        if side:obs['run']['run_id']=d.n._run_identity(obs['spec'],obs['run'],obs['events'][0]['data'])
        context=object.__new__(d.n.NativeHostContext)
        for key,value in {'_policy':raw,'_evidence':evidence,'_guard':DriverGuard()}.items():object.__setattr__(context,key,value)
        contexts.append(context)
    left['plan']=packet['comparison_plan']
    def put(value):raw=sm.canonical(value);left['archive'][sm.sha256(raw)]=raw;return sm.sha256(raw)
    obs=left['observation'];terminal=obs['events'][-1]['data'];initial=obs['events'][0]['data'];invocation={'schema':'twin.source-extraction-invocation/v1','argv':obs['spec']['argv'],'cwd':'/work','environment':dict(c.migration.ENVIRONMENT),'stdin':'OWNED-EOF-PIPE'};invpin=put(invocation)
    data={'schema':'TEST_ONLY-pdf-baseline-capture-data/v1','purpose':'TEST_ONLY','observation_mode':'actual','plan_sha256':obs['spec']['plan_sha256'],'pair_plan_sha256':packet['comparison_plan']['pair_plan_sha256'],
        'host_policy_sha256':obs['host_policy_sha256'],'host_evidence_sha256':put({'schema':'TEST_ONLY-comparison-host-evidence-index/v1','sha256s':sorted(sm._json(contexts[0]._policy)['evidence_sha256s'])}),
        'run_id':sm.sha256(sm.canonical({'plan_sha256':obs['spec']['plan_sha256'],'invocation_sha256':invpin,'started_at':obs['run']['started_at'],'monotonic_start_ns':obs['run']['monotonic_start_ns'],'process':{k:initial[k] for k in ('pid','starttime','ppid','uid','gid')}})),
        'invocation_sha256':invpin,'process_sha256':put(initial),'run_clock_sha256':put(obs['run']),'native_events_sha256':put(obs),'dependency_observation_sha256':put(obs['files']),
        'stdout':None,'stderr':None,'terminal_wait':{**terminal['wait'],'provenance':'natural_terminal'},'custody_sha256':put(terminal['custody']),'cleanup':'removed','intervention':'none','status':'COMPLETE_EXIT0_DATA','failure':None}
    for channel,fd in [('stdout',1),('stderr',2)]:
        pin=terminal[channel+'_sha256'];data[channel]={'captured':{'sha256':pin,'bytes':len(left['archive'][pin])},'observed_bytes_lower_bound':len(left['archive'][pin]),'complete':True,'original_descriptor':fd,'generation':0,'identity':initial['fds'][fd]['identity'],'eof_event_seq':next(e['seq'] for e in obs['events'] if e['kind']=='pipe-eof' and e['data']['channel']==channel)}
    d.check_remap_capture_data(data,left['archive'],packet)
    base=object.__new__(d._BaselineCompletion);raw=sm.canonical(data)
    for key,value in {'_record':raw,'_held_record':bytes(bytearray(raw)),'_archive':left['archive'],'_packet':copy.deepcopy(packet),'_guard':DriverGuard(),'_context':contexts[0],'_original':original}.items():object.__setattr__(base,key,value)
    result=d.bridge._complete_pdf_extraction(native,right['archive'][native['parent_sha256']],right['observation'],right['archive'])
    patched=object.__new__(d._PatchedCompletion)
    for key,value in {'_completed':(result,copy.deepcopy(right['observation'])),'_plan':{k:v for k,v in native.items() if k!='archive'},'_pair':sm.canonical(packet['pair_plan']),'_guard':DriverGuard(),'_context':contexts[1],'_original':original}.items():object.__setattr__(patched,key,value)
    original._next=38+2*index;original._used_hosts={sm.sha256(('PURE_prior_'+str(j)).encode()) for j in range(original._next-2)}|{sm.sha256(ctx._policy) for ctx in contexts};original._awaiting_comparison=True
    for earlier in flow.entries[:index]:earlier['phase']='MATCH_RETAINED'
    entry.update(phase='GATE_PENDING',baseline=base,patched=patched,baseline_data=data,baseline_archive=left['archive'],patched_archive=result['archive'])
    return original,model,clock,flow,entry,packet,left,right,contexts


@pytest.mark.parametrize('index',[0,1,2])
def test_real_pure_replayers_private_views_and_once_gate_advance_only_retained_match(monkeypatch,index):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch,index)
    result=d._compare_remap_pair(original)
    assert result['stop_suite'] is False and result['control']==['identity','a-to-b','a-to-ab'][index]
    assert entry['gate_spent'] and entry['phase']=='MATCH_RETAINED' and original._awaiting_comparison is False
    assert [sm._json(flow.records[pin])['status'] for pin in entry['journal']]==['STARTED','PASS']
    assert d.check_remap_disposition(result,{**left['archive'],**entry['patched']._completed[0]['archive'],**entry['patched']._completed[0]['receipts'],**flow.records},packet)=={'qualification':'NONE','stop_suite':False}
    before=(len(flow.records),flow.metadata_bytes,original._next)
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert before==(len(flow.records),flow.metadata_bytes,original._next)


@pytest.mark.parametrize('failure',['view','started-retention','summary-retention','record-retention','actual-record','different-original','baseline-copy'])
def test_gate_consumes_before_validation_and_retains_first_failure_without_retry(monkeypatch,failure):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    baseline=entry['baseline'];patched=entry['patched'];seen=[];put=d._put
    if failure=='view':
        def refuse(*args):
            assert entry['phase']=='GATE_RUNNING' and entry['gate_spent']
            assert sm._json(flow.records[entry['journal'][0]])['status']=='STARTED'
            seen.append('view');raise ValueError('PURE view refusal')
        monkeypatch.setattr(d,'_baseline_view',refuse)
    if failure in ('started-retention','summary-retention','record-retention'):
        schema={'started-retention':'TEST_ONLY-pdf-remap-gate/v1','summary-retention':'TEST_ONLY-pdf-remap-read-effect-data/v1','record-retention':'TEST_ONLY-pdf-remap-pair-disposition/v1'}[failure]
        def refuse_put(owner,value):
            if type(value) is dict and value.get('schema')==schema:seen.append(schema);raise ValueError('PURE retention refusal')
            return put(owner,value)
        monkeypatch.setattr(d,'_put',refuse_put)
    if failure=='actual-record':patched._completed[1]['platform']['release']='substituted'
    if failure=='different-original':object.__setattr__(patched,'_original',object())
    if failure=='baseline-copy':object.__setattr__(baseline,'_record',b'{}')
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert original._stopped and original._awaiting_comparison and entry['gate_spent']
    assert entry['baseline'] is baseline and entry['patched'] is patched and flow.failure is not None
    first=flow.failure_raw;before=len(seen)
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert first==flow.failure_raw and before==len(seen)


@pytest.mark.parametrize('exception',[KeyboardInterrupt,SystemExit])
def test_gate_cancellation_survives_secondary_evidence_failure(monkeypatch,exception):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch);error=exception('PURE first cancellation')
    def cancel(*args):raise error
    monkeypatch.setattr(d,'_baseline_view',cancel)
    with pytest.raises(exception) as seen:d._compare_remap_pair(original)
    assert seen.value is error and original._stopped and flow.failure['exception_type']==exception.__name__
    assert entry['journal'] and entry['gate_spent'] and original._awaiting_comparison


@pytest.mark.parametrize('mutation',['source','stage','slot','active','awaiting','stopped','H-type','H-evidence','H-reused','H-window'])
def test_fixed_private_freeze_neighbor_refusals_before_kernel(monkeypatch,mutation):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    original._next=36;original._used_hosts={sm.sha256(('prior'+str(i)).encode()) for i in range(36)};original._awaiting_comparison=False;entry['phase']='NOT_STARTED';context:Any=contexts[0]
    if mutation=='source':flow.records[entry['source_pin']]=b'changed'
    if mutation=='stage':original._technical_state.identities['identity'][1]+=1
    if mutation=='slot':original._next=42;original._used_hosts={sm.sha256(str(i).encode()) for i in range(42)}
    if mutation=='active':original._active_slot=35;original._target_custody_known=False
    if mutation=='awaiting':original._awaiting_comparison=True
    if mutation=='stopped':original._stopped=True
    if mutation=='H-type':context={}
    if mutation=='H-evidence':context._evidence.pop(entry['source_pin'])
    if mutation=='H-reused':original._used_hosts.pop();original._used_hosts.add(sm.sha256(context._policy))
    if mutation=='H-window':monkeypatch.setattr(d.n,'_host_window',lambda *a,**k:(_ for _ in ()).throw(ValueError('expired')))
    if mutation in ('H-type','H-evidence','H-reused','H-window','source'):
        with pytest.raises(ValueError):d._freeze(original,context,packet,entry)
    else:
        with pytest.raises(ValueError):d._selected(original,(36,38,40))
    assert original._next in (36,42) and entry['attempts']==[]


def test_genuine_unconsumed_next_H_freezes_without_reset_or_slot_consumption(monkeypatch):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    original._next=36;original._used_hosts={sm.sha256(str(i).encode()) for i in range(36)};original._awaiting_comparison=False;entry['phase']='NOT_STARTED'
    authority=d._freeze(original,contexts[0],packet,entry)
    assert authority._session is original and authority._slot==36 and not authority._spent
    assert original._next==36 and original._technical_state._remap_flow is flow


_EXEC_MODEL:dict[str,Any]={}

def execute_model(plan,parent,observation_store,preparation_deadline):
    _EXEC_MODEL['calls'].append((plan,parent,observation_store,preparation_deadline))
    if _EXEC_MODEL.get('mode')=='nonreturn':raise RuntimeError('PURE no return')
    value=copy.deepcopy(_EXEC_MODEL['completed'][0])
    if _EXEC_MODEL.get('mode')=='actual-record':value[1]['platform']['release']='forged'
    return value


@pytest.mark.parametrize('index',[0,1,2])
def test_patched_fixed_prologue_uses_existing_completed_pair_once_then_real_gate(monkeypatch,index):
    completed:list[Any]=[];calls:list[Any]=[]
    _EXEC_MODEL.clear();_EXEC_MODEL.update(completed=completed,calls=calls)
    monkeypatch.setattr(d.migration,'_execute_prepared_extraction',execute_model)
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch,index)
    completed.append(entry['patched']._completed)
    original._next=37+2*index;original._used_hosts.remove(sm.sha256(contexts[1]._policy));original._awaiting_comparison=False;entry['phase']='BASELINE_DONE';entry['patched']=None
    store:Any=object.__new__(d.n.NativeObservationStore)
    for key,value in {'_purpose':'actual','_host_context':contexts[1],'_guard':DriverGuard(),'_entries':{}}.items():setattr(store,key,value)
    value=d._capture_next_remap_patched(original,store,right['plan'])
    assert type(value) is d._PatchedCompletion and len(calls)==1 and calls[0][2] is store
    assert original._next==38+2*index and original._awaiting_comparison and original._active_slot is None and original._target_custody_known
    assert store._entries=={} and entry['phase']=='GATE_PENDING'
    assert d._compare_remap_pair(original)['stop_suite'] is False


@pytest.mark.parametrize('mutation',['public-store','missing-context','test-only','configuration','closure','actual-record','nonreturn'])
def test_patched_refusals_never_adopt_data_or_forge_terminal_custody(monkeypatch,mutation):
    completed:list[Any]=[];calls:list[Any]=[]
    _EXEC_MODEL.clear();_EXEC_MODEL.update(completed=completed,calls=calls,mode=mutation)
    monkeypatch.setattr(d.migration,'_execute_prepared_extraction',execute_model)
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    completed.append(entry['patched']._completed);original._next=37;original._used_hosts.remove(sm.sha256(contexts[1]._policy));original._awaiting_comparison=False;entry['phase']='BASELINE_DONE';entry['patched']=None
    store:Any=object.__new__(d.n.NativeObservationStore)
    for key,value in {'_purpose':'actual','_host_context':contexts[1],'_guard':DriverGuard(),'_entries':{}}.items():setattr(store,key,value)
    if mutation=='public-store':store={}
    if mutation=='missing-context':store._host_context=None
    if mutation=='test-only':store._purpose='TEST_ONLY'
    if mutation=='configuration':contexts[1]._evidence.pop(right['plan']['configuration_sha256'])
    if mutation=='closure':contexts[1]._evidence.pop(right['plan']['implementation_artifact_sha256'])
    with pytest.raises((ValueError,RuntimeError)):d._capture_next_remap_patched(original,store,right['plan'])
    if mutation in ('actual-record','nonreturn'):
        assert len(calls)==1 and original._stopped and original._active_slot==37 and original._target_custody_known is False
    else:assert calls==[] and original._next==37


@pytest.mark.parametrize('mode',['complete','no-return','cancel','finalize-error','returned-cancel-finalize-error'])
def test_v2_baseline_prologue_shares_kernel_mechanics_and_preserves_unknown_return(monkeypatch,mode):
    from types import SimpleNamespace
    cell:list[Any]=[];calls:list[Any]=[]
    def kernel(authority,spec,archive):
        calls.append('kernel')
        if mode=='no-return':raise RuntimeError('PURE no collector return')
        if mode=='cancel':raise KeyboardInterrupt('PURE cancellation')
        archive.update(cell[1]);return cell[0]
    monkeypatch.setattr(c,'_linux_run_comparison',kernel)
    monkeypatch.setattr(c,'tempfile',SimpleNamespace(mkdtemp=lambda **k:'/work'))
    monkeypatch.setattr(c,'os',SimpleNamespace(chmod=lambda *a:None))
    monkeypatch.setattr(d,'shutil',SimpleNamespace(rmtree=lambda *a:calls.append('remove')))
    monkeypatch.setattr(d.migration,'_write_owned',lambda *a:None)
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    original._next=36;original._used_hosts={sm.sha256(str(i).encode()) for i in range(36)};original._awaiting_comparison=False;entry['phase']='NOT_STARTED';original_data=copy.deepcopy(entry['baseline_data']);entry['baseline']=None;entry['patched']=None;entry['baseline_data']=None;entry['patched_data']=None;entry['patched_archive']=None
    cell.extend([{'process_group':left['observation']['events'][-1]['data']['custody'],'failure':None,'_interruption':KeyboardInterrupt('PURE returned cancellation') if mode=='returned-cancel-finalize-error' else None},left['archive']])
    def finalize(plan,run,archive,workspace_cleanup):
        if mode in ('finalize-error','returned-cancel-finalize-error'):raise ValueError('PURE finalization failed')
        return copy.deepcopy(original_data)
    monkeypatch.setattr(c,'_finalize_capture',finalize)
    if mode in ('cancel','returned-cancel-finalize-error'):
        with pytest.raises(KeyboardInterrupt) as seen:d._capture_next_remap_baseline(original,contexts[0])
        if mode=='returned-cancel-finalize-error':assert seen.value is cell[0]['_interruption']
    else:
        value=d._capture_next_remap_baseline(original,contexts[0]);assert type(value) is d._BaselineCompletion
    assert calls[0]=='kernel' and original._next==37
    if mode=='complete':assert calls==['kernel','remove'] and not original._stopped and entry['phase']=='BASELINE_DONE'
    elif mode in ('finalize-error','returned-cancel-finalize-error'):
        assert calls==['kernel','remove'] and original._stopped and original._active_slot is None and original._target_custody_known
        assert entry['baseline_data']['cleanup']=='removed'
        held=d._held_remap_data(original)['captures'][0]['baseline_run']
        assert held['process_group']==cell[0]['process_group'] and '_interruption' not in held
    else:
        assert calls==['kernel'] and original._stopped and original._active_slot==36 and original._target_custody_known is False
        assert [sm._json(flow.records[pin])['status'] for pin in entry['journal']]==['NOT_RUN']
        assert entry['disposition']['stop_suite'] is True


def test_gate_final_retention_failure_has_one_terminal_journal_not_pass_then_refusal(monkeypatch):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch);put=d._put
    def fail(owner,value):
        if type(value) is dict and value.get('schema')=='TEST_ONLY-pdf-remap-pair-disposition/v1':raise ValueError('final retention unavailable')
        return put(owner,value)
    monkeypatch.setattr(d,'_put',fail)
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert [sm._json(flow.records[pin])['status'] for pin in entry['journal']]==['STARTED','REFUSED']
    assert original._stopped and original._awaiting_comparison and entry['disposition'] is None


@pytest.mark.parametrize('mutation',['gate-stage','gate-capture','gate-observation','summary-pair','summary-association','comparison-extra','summary-extra','technical-removed','comparison-bool','summary-bool','summary-map','summary-count'])
def test_public_disposition_refuses_consistently_rehashed_cross_record_substitutions(monkeypatch,mutation):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    record=d._compare_remap_pair(original);archive={**left['archive'],**entry['patched']._completed[0]['archive'],**entry['patched']._completed[0]['receipts'],**flow.records}
    assert d.check_remap_disposition(record,archive,packet)['stop_suite'] is False
    def put(value):raw=sm.canonical(value);archive[sm.sha256(raw)]=raw;return sm.sha256(raw)
    journal=sm._json(archive[record['gate_journal_sha256']]);gate=sm._json(archive[journal[-1]])
    if mutation=='gate-stage':gate['stage_record_sha256']=record['pair_plan_sha256']
    if mutation=='gate-capture':gate['baseline_data_sha256']=record['patched_data_sha256']
    if mutation=='gate-observation':gate['patched_observation_sha256']=gate['baseline_observation_sha256']
    if mutation.startswith('summary-'):
        summary=sm._json(archive[gate['summary_sha256']])
        if mutation=='summary-pair':summary['pair_plan_sha256']='a'*64
        if mutation=='summary-association':summary['association_sha256']='b'*64
        if mutation=='summary-extra':summary['authority']=True
        if mutation=='summary-bool':summary['stream_exit_equality']['stdout']=1
        if mutation=='summary-map':summary['origin_map_sha256']='e'*64
        if mutation=='summary-count':summary['input_a_items']+=1
        gate['summary_sha256']=put(summary)
    if mutation in ('comparison-extra','comparison-bool'):
        comparison=sm._json(archive[record['pair_comparison_sha256']])
        if mutation=='comparison-extra':comparison['authority']=True
        else:comparison['stdout_equal']=1
        record['pair_comparison_sha256']=put(comparison)
    if mutation=='technical-removed':
        stage=sm._json(archive[record['technical_state_sha256']]);stage.update(phase='REMOVED_HELD',root_removal_known=True);record['technical_state_sha256']=put(stage)
    journal[-1]=put(gate);record['gate_journal_sha256']=put(journal)
    with pytest.raises(ValueError):d.check_remap_disposition(record,archive,packet)
    assert not original._stopped and not original._awaiting_comparison


@pytest.mark.parametrize('late',[10800.25,float('nan')])
def test_post_last_retention_clock_cannot_commit_pass(monkeypatch,late):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch);put=d._put
    def advance(owner,value):
        pin=put(owner,value)
        if type(value) is dict and value.get('schema')=='TEST_ONLY-pdf-remap-pair-disposition/v1':clock[0]=original._started+late
        return pin
    monkeypatch.setattr(d,'_put',advance)
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert original._stopped and original._awaiting_comparison and entry['disposition']['stop_suite'] is True
    assert [sm._json(flow.records[p])['status'] for p in entry['journal']]==['STARTED','REFUSED']
    assert original._technical_state.clock_observation['status'] in ('LATE','UNKNOWN')


@pytest.mark.parametrize('state',['active','unknown','complete','late-remove','partial'])
def test_final_cleanup_conserves_target_custody_once_windows_and_known_removal(monkeypatch,state):
    original,model,clock=prepared_driver(monkeypatch);technical=original._technical_state
    if state=='active':original._next=1;original._used_hosts={'a'*64};original._active_slot=0;original._target_custody_known=False
    if state=='unknown':original._next=1;original._used_hosts={'b'*64};original._active_slot=0;original._target_custody_known=False
    if state=='partial':technical.phase='PRESERVED'
    if state=='late-remove':
        remove=model.rmdir
        def delayed(*a,**k):remove(*a,**k);clock[0]+=2.25
        monkeypatch.setattr(r.os,'rmdir',delayed)
    if state=='complete':
        result=d._finish_remap_route(original)
        assert result['phase']=='REMOVED' and result['root_removal_known'] and '/TEST_ONLY/resources' not in model.nodes
    else:
        with pytest.raises(ValueError):d._finish_remap_route(original)
        if state=='late-remove':assert technical.phase=='REMOVED_HELD' and technical.root_removal_known and '/TEST_ONLY/resources' not in model.nodes
        else:assert '/TEST_ONLY/resources' in model.nodes and technical.final_deadline is None
    assert original._stopped
    before=list(model.log)
    with pytest.raises(ValueError):d._finish_remap_route(original)
    assert model.log==before


@pytest.mark.parametrize('kind',['record','aggregate','original'])
def test_new_metadata_and_original_capacity_never_reset_or_grow(monkeypatch,kind):
    if kind=='original':
        original,model,clock=stage_model(monkeypatch);monkeypatch.setattr(d,'_SOURCE_ROOT','/TEST_ONLY/resources')
        original._retained=c.MAX_SUITE_BYTES-c.FAILURE_RESERVE-original._reserve
        pair,plan,archive=prepared_fixture();before=original._retained
        with pytest.raises(ValueError):d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
        assert original._stopped and original._retained==before and model.log==[]
        assert original._technical_state._remap_flow.failure is not None
        with pytest.raises(ValueError):d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
    else:
        original,model,clock=prepared_driver(monkeypatch);flow=d._flow(original)
        if kind=='record':value:Any='x'*d.MIB
        else:flow.metadata_bytes=d.METADATA_BYTES;value={'new':'record'}
        before=(flow.metadata_bytes,len(flow.records),original._retained)
        with pytest.raises(ValueError):d._put(flow,value)
        assert before==(flow.metadata_bytes,len(flow.records),original._retained)


def replace_baseline_data(entry,left,packet):
    data=copy.deepcopy(entry['baseline_data']);obs=left['observation'];archive=left['archive']
    raw=sm.canonical(obs);archive[sm.sha256(raw)]=raw;data['native_events_sha256']=sm.sha256(raw)
    for name in ('stdout','stderr'):
        stream=data[name];pin=obs['events'][-1]['data'][name+'_sha256'];stream['captured']={'sha256':pin,'bytes':len(archive[pin])};stream['observed_bytes_lower_bound']=len(archive[pin]);stream['eof_event_seq']=next(e['seq'] for e in obs['events'] if e['kind']=='pipe-eof' and e['data']['channel']==name)
    d.check_remap_capture_data(data,archive,packet)
    raw=sm.canonical(data);object.__setattr__(entry['baseline'],'_record',raw);object.__setattr__(entry['baseline'],'_held_record',bytes(bytearray(raw)));entry['baseline_data']=data


@pytest.mark.parametrize('mutation',['unused','partial-read','stdout','missing-input-A'])
def test_private_gate_stops_valid_replay_without_selected_read_effect_or_equality(monkeypatch,mutation):
    from test_pdf_remap_resources import replace_stream,origin_wire
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch,1)
    if mutation in ('unused','partial-read'):
        events=left['observation']['events']
        if mutation=='unused':
            del events[4:10]
            for seq,event in enumerate(events):event['seq']=seq
        else:
            data=next(e['data'] for e in events if e['kind']=='leave' and 'buffer_bytes' in e['data']['detail']);data['result']-=1;data['detail']['buffer_bytes']-=1
            raw=left['archive'][data['detail']['buffer_sha256']][:-1];left['archive'][sm.sha256(raw)]=raw;data['detail']['buffer_sha256']=sm.sha256(raw)
        replace_baseline_data(entry,left,packet)
    elif mutation=='stdout':
        replace_stream(left['observation'],left['archive'],1,b'full original mismatch');replace_baseline_data(entry,left,packet)
    else:
        import json
        output,wire=origin_wire('a-to-b');rows=[json.loads(line) for line in wire.splitlines()];rows[2]['input_scalars']=[88]
        prefix=b''.join(sm.canonical(row)+b'\n' for row in rows[:-1]);rows[-1].update(event_prefix_sha256=sm.sha256(prefix),event_prefix_bytes=len(prefix));wire=prefix+sm.canonical(rows[-1])+b'\n'
        d.origin.check_pdf_origin_events(output,wire);replace_stream(right['observation'],right['archive'],3,wire)
        result=d.bridge._complete_pdf_extraction(right['plan'],right['archive'][right['plan']['parent_sha256']],right['observation'],right['archive'])
        object.__setattr__(entry['patched'],'_completed',(result,copy.deepcopy(right['observation'])));entry['patched_archive']=result['archive']
        d._patched_view(entry['patched'],original,packet)
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert original._stopped and original._awaiting_comparison and entry['gate_spent']
    assert [sm._json(flow.records[p])['status'] for p in entry['journal']]==['STARTED','REFUSED']
    held=d._held_remap_data(original)
    assert held['captures'][1]['baseline_archive'] is not None and held['captures'][1]['patched_archive'] is not None
    assert flow.failure['phase']=='GATE' and flow.failure['code']=='GATE_REFUSED'
    if mutation=='stdout':assert any(sm._json(raw).get('stdout_equal') is False for raw in flow.records.values() if raw.startswith(b'{') and b'TEST_ONLY-pdf-pair-comparison/v1' in raw)


@pytest.mark.parametrize('wait_known',[True,False])
def test_failed_patched_private_return_retains_typed_wait_and_not_run_gate(monkeypatch,wait_known):
    completed:list[Any]=[];calls:list[Any]=[];_EXEC_MODEL.clear();_EXEC_MODEL.update(completed=completed,calls=calls)
    monkeypatch.setattr(d.migration,'_execute_prepared_extraction',execute_model)
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    result,observation=copy.deepcopy(entry['patched']._completed);terminal=observation['events'][-1]['data']
    wait={'kind':'exited','raw_status':256,'exit_code':1,'observed_at_ns':terminal['wait']['observed_at_ns']}
    observation['failure']={'wait':wait if wait_known else None};raw=sm.canonical(observation);result['archive'][sm.sha256(raw)]=raw
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);dossier.update(native_observation_sha256=sm.sha256(raw),disposition='failure',failure='PURE failed observation',standard_receipt_sha256=None)
    raw=sm.canonical(dossier);result['receipts'][sm.sha256(raw)]=raw;result['dossier_sha256']=sm.sha256(raw);result['status']='failure';completed.append((result,observation))
    original._next=37;original._used_hosts.remove(sm.sha256(contexts[1]._policy));original._awaiting_comparison=False;entry['phase']='BASELINE_DONE';entry['patched']=None
    store:Any=object.__new__(d.n.NativeObservationStore)
    for key,value in {'_purpose':'actual','_host_context':contexts[1],'_guard':DriverGuard(),'_entries':{}}.items():setattr(store,key,value)
    value=d._capture_next_remap_patched(original,store,right['plan']);data=d._patched_view(value,original,packet)[0]
    assert data['status']=='FAILED_DATA' and not data['stdout']['complete'] and not data['origin_effect_confirmed']
    assert data['terminal_wait']==({**wait,'provenance':'natural_terminal'} if wait_known else None)
    assert original._stopped and original._target_custody_known and original._active_slot is None and len(calls)==1
    assert [sm._json(flow.records[p])['status'] for p in entry['journal']]==['NOT_RUN']
    assert entry['disposition']['stop_suite'] and d._held_remap_data(original)['captures'][0]['patched_return'][0]['status']=='failure'


@pytest.mark.parametrize('slot',[0,35,42,43,50,51,52])
def test_driver_cannot_select_ordinary_early_or_held_fault_slots(monkeypatch,slot):
    original,model,clock=prepared_driver(monkeypatch);original._next=slot;original._used_hosts={sm.sha256(str(i).encode()) for i in range(slot)}
    with pytest.raises(ValueError):d._selected(original,(36,38,40))
    with pytest.raises(ValueError):d._selected(original,(37,39,41))
    assert original._next==slot and all(e['attempts']==[] for e in d._raw_flow(original).entries)


@pytest.mark.parametrize('kind',['clock','capacity'])
def test_preparation_uncertainty_keeps_original_placeholder_first_failure_no_retry(monkeypatch,kind):
    original,model,clock=stage_model(monkeypatch);monkeypatch.setattr(d,'_SOURCE_ROOT','/TEST_ONLY/resources')
    if kind=='clock':clock[0]=float('nan')
    else:original._retained=c.MAX_SUITE_BYTES-original._reserve-c.FAILURE_RESERVE
    pair,plan,archive=prepared_fixture()
    with pytest.raises(ValueError):d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
    state=original._technical_state;flow=state._remap_flow;first=flow.failure_raw;deadline=state.deadline;log=list(model.log)
    assert state._original_owner is original and flow.owner is original and original._stopped and flow.phase=='STOPPED'
    assert flow.failure['code']=='SELECTION_REFUSED' and first is not None
    with pytest.raises(ValueError):d._prepare_remap_route(original,{'ordinary_plan':plan,'archive':archive})
    assert original._technical_state is state and state.deadline==deadline and flow.failure_raw==first and model.log==log


@pytest.mark.parametrize('cls',[d._BaselineCompletion,d._PatchedCompletion,r._RemapFlow])
def test_private_driver_types_have_no_construction_copy_or_serialization_route(cls):
    with pytest.raises(ValueError):cls()
    with pytest.raises(ValueError):cls({'status':'PASS'})


def test_gate_refusal_exports_closed_stop_disposition_with_available_originals(monkeypatch):
    from test_pdf_remap_resources import replace_stream
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch)
    replace_stream(left['observation'],left['archive'],1,b'raw adverse output');replace_baseline_data(entry,left,packet)
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert entry['disposition'] is not None and entry['disposition']['stop_suite'] is True
    archive={**left['archive'],**entry['patched']._completed[0]['archive'],**flow.records}
    assert d.check_remap_disposition(entry['disposition'],archive,packet)=={'qualification':'NONE','stop_suite':True}


_HOST_MODEL:dict[str,Any]={}

def host_window_model(context,**kwargs):
    if _HOST_MODEL.get('expired'):raise ValueError('PURE H expired after last retention')
    return sm._json(context._policy)

def test_last_retention_H_expiry_cannot_commit_match(monkeypatch):
    _HOST_MODEL.clear()
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch,host_window=host_window_model);put=d._put
    def expire(owner,value):
        pin=put(owner,value)
        if type(value) is dict and value.get('schema')=='TEST_ONLY-pdf-remap-pair-disposition/v1':_HOST_MODEL['expired']=True
        return pin
    monkeypatch.setattr(d,'_put',expire)
    with pytest.raises(ValueError):d._compare_remap_pair(original)
    assert _HOST_MODEL['expired'] and original._stopped and original._awaiting_comparison
    assert entry['disposition']['stop_suite'] and [sm._json(flow.records[p])['status'] for p in entry['journal']]==['STARTED','REFUSED']
