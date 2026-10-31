"""Fixed private remap v2 comparison flow; no selector, issuer or activation API.

All public records are DATA. Real source/root/H appointments remain absent. Tests
use fabricated private objects and explicit models, never actual target actions.
"""
from __future__ import annotations
import copy
import dataclasses
import json
import math
from pathlib import Path
import sys
import shutil
import time
from typing import Any, cast
from . import source_metadata as sm
from . import pdf_comparison_capture as c
from . import pdf_remap_resources as r
from . import source_native_observation as n
from . import source_metadata_migration as migration
from . import pdf_native_bridge as bridge
from . import pdf_output_origin as origin

# A later reviewed trusted source must appoint the original suite and this root.
# No setter, env/CLI reader, callback, context factory or JSON importer exists.
_SOURCE_ROOT: str|None=None
MIB=1048576
METADATA_BYTES=4*MIB
GATE_KEYS={'schema','pair_plan_sha256','control','stage_record_sha256','baseline_data_sha256','patched_data_sha256','baseline_observation_sha256','patched_observation_sha256','status','summary_sha256','first_failure_sha256'}
DISPOSITION_KEYS={'schema','qualification','pair_plan_sha256','control','baseline_slot','patched_slot','baseline_data_sha256','patched_data_sha256','gate_journal_sha256','pair_comparison_sha256','first_failure_sha256','stop_suite','technical_state_sha256'}
FAILURE_KEYS={'schema','phase','code','original_slot','exception_type','available_facts_sha256','observations_complete','target_custody','technical_state_sha256','root_removal_known'}


@dataclasses.dataclass(eq=False,frozen=True,init=False,repr=False)
class _BaselineCompletion(c._PrivateCapability):
    def __new__(cls,*args:Any,**kwargs:Any)->Any:raise ValueError('private v2 baseline completion required')
    _record:bytes
    _held_record:bytes
    _archive:dict
    _packet:dict
    _guard:Any
    _context:n.NativeHostContext
    _original:c.OriginalComparisonSuite


@dataclasses.dataclass(eq=False,frozen=True,init=False,repr=False)
class _PatchedCompletion(c._PrivateCapability):
    def __new__(cls,*args:Any,**kwargs:Any)->Any:raise ValueError('private v2 patched completion required')
    _completed:tuple
    _plan:dict
    _pair:bytes
    _guard:Any
    _context:n.NativeHostContext
    _original:c.OriginalComparisonSuite


def _state(original:c.OriginalComparisonSuite)->r._StageState:
    c._check_original_suite(original);state=original._technical_state
    if type(state) is not r._StageState or state._original_owner is not original:raise ValueError('exact original-owned technical state required')
    return cast(r._StageState,state)


def _bound_flow(original:c.OriginalComparisonSuite)->r._RemapFlow:
    """Bind existing private ownership only; never validate/appoint fresh source.

    This check precedes fallible source validation so revocation and emergency
    facts remain possible even when that validation itself raises or cancels.
    """
    if type(original) is not c.OriginalComparisonSuite:raise ValueError('private original suite required')
    state=getattr(original,'_technical_state',None)
    if (type(state) is not r._StageState or state._original_owner is not original
            or type(state._remap_flow) is not r._RemapFlow or state._remap_flow.owner is not original):raise ValueError('existing exact original-owned remap flow required')
    return state._remap_flow


def _preflight_attempt(original:c.OriginalComparisonSuite,flow:r._RemapFlow,slots:tuple[int,...])->dict|None:
    if original._stopped:raise ValueError('original remap suite permanently stopped')
    slot=original._next
    if type(slot) is not int or slot not in slots or len(flow.entries)!=3:return None
    entry=flow.entries[(slot-36)//2]
    if entry['slot']!=slot-slot%2:raise ValueError('fixed original remap entry differs')
    if len(entry['attempts'])>=2:raise ValueError('finite original pair attempts exhausted')
    entry['attempts'].append({'slot':slot,'plan':None,'H':None})
    return entry


def _raw_flow(original:c.OriginalComparisonSuite)->r._RemapFlow:
    state=_state(original)
    if (type(state) is not r._StageState or state._original_owner is not original
            or type(state._remap_flow) is not r._RemapFlow or state._remap_flow.owner is not original):raise ValueError('exact original-owned remap flow required')
    return state._remap_flow


def _flow(original:c.OriginalComparisonSuite)->r._RemapFlow:
    flow=_raw_flow(original)
    if not flow.reserved or flow.guard is None or len(flow.packets)!=3 or len(flow.entries)!=3:raise ValueError('private remap preparation incomplete')
    flow.guard.verify()
    return flow


def _encoded(value:Any)->bytes:
    encoder=json.JSONEncoder(sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    parts=[];size=0
    for part in encoder.iterencode(value):
        raw=part.encode('utf-8');size+=len(raw)
        if size>MIB:raise ValueError('bounded canonical remap driver record required')
        parts.append(raw)
    return b''.join(parts)


def _put(flow:r._RemapFlow,value:Any)->str:
    raw=_encoded(value);pin=sm.sha256(raw)
    if not flow.reserved or flow.metadata_bytes+ (0 if pin in flow.records else len(raw))>METADATA_BYTES:raise ValueError('original reserved remap metadata exhausted')
    if pin not in flow.records:flow.records[pin]=raw;flow.metadata_bytes+=len(raw)
    return pin


def _driver_inventory()->list[dict]:
    paths={row['path'] for row in c._driver_inventory()}|{str(Path(__file__).resolve()),str(Path(r.__file__).resolve())}
    return [{'path':path,'sha256':sm.sha256(Path(path).read_bytes()),'bytes':len(Path(path).read_bytes())} for path in sorted(paths)]


def _check_drivers(packet:dict)->None:
    plan=packet['comparison_plan'];archive=packet['archive']
    rows=sm._json(c._raw(archive,plan['recorder_inventory_sha256']))
    if rows!=_driver_inventory():raise ValueError('fixed remap reached-source inventory differs')
    for row in rows:
        if Path(row['path']).read_bytes()!=c._raw(archive,row['sha256']):raise ValueError('retained remap source bytes differ')


def _time(original:c.OriginalComparisonSuite,deadline:float)->None:
    state=_state(original)
    r._tick(state,deadline)


def _stop(original:c.OriginalComparisonSuite,phase:str,code:str,error:BaseException|None,entry:dict|None=None)->None:
    # Failure slots are bounded placeholder memory inside the original fixed16MiB
    # failure reserve; even a failed normal4MiB charge cannot erase the first fact.
    try:
        flow=_bound_flow(original);original._stopped=True;flow.phase='STOPPED'
        if entry is not None:entry['phase']='STOPPED'
        if flow.failure is None:
            state=cast(r._StageState,original._technical_state)
            attempts=entry['attempts'] if entry is not None else []
            slot=attempts[-1]['slot'] if attempts else None
            if type(slot) is not int or not 0<=slot<52:slot=None
            flow.failure={'schema':'TEST_ONLY-pdf-remap-first-failure/v1','phase':phase,'code':code,
                'original_slot':slot,'exception_type':type(error).__name__[:80] if error else None,
                'available_facts_sha256':None,'observations_complete':False,
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN',
                'technical_state_sha256':None,'root_removal_known':state.root_removal_known}
            flow.failure_raw=_encoded(flow.failure)
        elif len(flow.secondary)<32:flow.secondary.append({'phase':phase,'code':code,'exception_type':type(error).__name__[:80] if error else None})
    except BaseException:
        # Never replace the original pending cancellation with emergency evidence.
        pass


def _prepare_remap_route(original:c.OriginalComparisonSuite,fixed_build_and_fixture_bytes:dict)->None:
    c._check_original_suite(original)
    if _SOURCE_ROOT is None:raise ValueError('trusted fixed source/root appointment absent')
    if original._technical_state is not None:raise ValueError('original remap preparation is once only')
    c._closed(fixed_build_and_fixture_bytes,{'ordinary_plan','archive'})
    plan=fixed_build_and_fixture_bytes['ordinary_plan'];archive=fixed_build_and_fixture_bytes['archive']
    pair=c._plan(plan,archive)
    if pair['schedule_index']!=0 or pair['resource'] is not None or pair['suite_selection_sha256']!=original._selection or c._raw(archive,original._selection)!=original._selection_raw:raise ValueError('original selected first-fixture build inputs required')
    try:
        stage=r._stage_for_remap_driver(original,_SOURCE_ROOT)
        flow=_raw_flow(original);flow.guard=_state(original).guard;flow.phase='PREPARING'
        stage_pin=_put(flow,stage)
        selected=dict(archive);drivers=_driver_inventory()
        for row in drivers:selected[row['sha256']]=Path(row['path']).read_bytes()
        packets=r.make_remap_plans(_SOURCE_ROOT,stage['identities'],plan,selected)
        for packet in packets:
            raw=sm.canonical(drivers);packet['archive'][sm.sha256(raw)]=raw
            packet['comparison_plan']['recorder_inventory_sha256']=sm.sha256(raw)
            r.check_remap_plan(packet);_check_drivers(packet)
        source={'schema':'TEST_ONLY-pdf-remap-driver-source/v1','files':drivers,'helper_inventory_sha256':sm.sha256(flow.guard.description)}
        # The frozen helper description is earlier source DATA, never H approval.
        flow.records[sm.sha256(flow.guard.description)]=flow.guard.description;flow.metadata_bytes+=len(flow.guard.description)
        if flow.metadata_bytes>METADATA_BYTES:raise ValueError('original remap source metadata exhausted')
        source_pin=_put(flow,source)
        flow.packets=tuple(copy.deepcopy(packets))
        flow.entries=[{'slot':36+2*i,'phase':'NOT_STARTED','baseline':None,'patched':None,'baseline_data':None,'patched_data':None,
            'baseline_archive':None,'patched_archive':None,'baseline_run':None,'gate_spent':False,'journal':[],
            'stage_pin':stage_pin,'source_pin':source_pin,'disposition':None,'attempts':[]} for i in range(3)]
        _time(original,min(original._started+60,original._started+c.B_SECONDS));flow.phase='READY'
    except BaseException as error:
        _stop(original,'PREPARE','SELECTION_REFUSED',error)
        raise


def _selected(original:c.OriginalComparisonSuite,slots:tuple[int,...])->tuple[r._RemapFlow,dict,dict]:
    flow=_flow(original);state=_state(original)
    if (original._stopped or flow.phase!='READY' or original._next not in slots or original._active_slot is not None
            or original._target_custody_known is not True or original._awaiting_comparison or state.phase!='COMPLETE_STAGE'):
        raise ValueError('fixed next remap slot/stage/custody required')
    i=(original._next-36)//2;entry=flow.entries[i];packet=flow.packets[i]
    r.check_remap_plan(packet);_check_drivers(packet)
    resource=packet['pair_plan']['resource'];stage=sm._json(flow.records[entry['stage_pin']])
    if (stage['phase']!='COMPLETE_STAGE' or stage['root']!=_SOURCE_ROOT or stage['identities'][resource['control']]!=resource['identity']
            or state.identities!=stage['identities'] or state.root!=stage['root']):raise ValueError('held actual stage/public resource association differs')
    _time(original,original._started+c.B_SECONDS)
    return flow,entry,packet


def _freeze(original:c.OriginalComparisonSuite,context:n.NativeHostContext,packet:dict,entry:dict)->c.ComparisonCaptureAuthority:
    flow=_flow(original)
    if type(context) is not n.NativeHostContext:raise ValueError('genuine independently held actual H required')
    context._guard.verify();policy=n._host_window(context)
    if (sm._instant(policy['not_after'])-sm._instant(policy['not_before'])).total_seconds()>300:raise ValueError('original remap H exceeds300')
    pair=packet['pair_plan'];required=[original._selection,pair['build_pair']['pristine_build_sha256'],pair['build_pair']['patched_build_sha256'],entry['source_pin']]
    evidence={**packet['archive'],**flow.records}
    for pin in required:
        if pin not in policy['evidence_sha256s'] or c._raw(context._evidence,pin)!=c._raw(evidence,pin):raise ValueError('independent original/build/source H evidence absent')
    if sm.sha256(context._policy) in original._used_hosts:raise ValueError('remap H already spent')
    r.check_remap_host_evidence(packet,policy,context._evidence)
    for row in _driver_inventory():
        if not n._inside(row['path'],policy['roots']):raise ValueError('remap source outside independently controlled H roots')
    c.admit_slot(elapsed_ns=int((time.monotonic()-original._started)*10**9),slots_used=original._next,retained_bytes=original._retained,reserve_bytes=original._reserve)
    _time(original,original._started+c.B_SECONDS);authority=object.__new__(c.ComparisonCaptureAuthority)
    for key,value in {'_context':context,'_guard':flow.guard,'_pair':sm.canonical(pair),'_archive':dict(packet['archive']),
        '_selected_at':_state(original).last_time,'_spent':False,'_suite_started':original._started,'_slots_used':original._next,
        '_retained_bytes':original._retained,'_reserve_bytes':original._reserve,'_plan':sm.canonical(packet['comparison_plan']),
        '_session':original,'_slot':original._next}.items():object.__setattr__(authority,key,value)
    return authority


def check_remap_capture_data(record:dict,archive:dict,expected_packet:dict)->dict:
    r.check_remap_plan(expected_packet)
    result=c._check_capture_data(record,archive,expected_packet['comparison_plan'],expected_packet['pair_plan'])
    if record['observation_mode']=='actual':
        policy=c._json(archive,record['host_policy_sha256']);r.check_remap_host_evidence(expected_packet,policy,archive)
    return result


def _baseline_completion(authority:c.ComparisonCaptureAuthority,packet:dict,data:dict,archive:dict)->_BaselineCompletion:
    check_remap_capture_data(data,archive,packet);value=object.__new__(_BaselineCompletion);raw=sm.canonical(data)
    for key,item in {'_record':raw,'_held_record':bytes(bytearray(raw)),'_archive':dict(archive),'_packet':copy.deepcopy(packet),
        '_guard':authority._guard,'_context':authority._context,'_original':authority._session}.items():object.__setattr__(value,key,item)
    c._retain_completion(authority,archive,failed=data['status']!='COMPLETE_EXIT0_DATA',patched=False)
    return value


def _baseline_view(value:_BaselineCompletion,original:c.OriginalComparisonSuite,packet:dict)->tuple[dict,dict]:
    if type(value) is not _BaselineCompletion or value._original is not original:raise ValueError('same private original v2 baseline completion required')
    value._guard.verify();value._context._guard.verify()
    if value._record!=value._held_record or value._packet['pair_plan']!=packet['pair_plan'] or value._packet['comparison_plan']!=packet['comparison_plan']:raise ValueError('private original baseline record/plan changed')
    data=sm._json(value._record);check_remap_capture_data(data,value._archive,packet)
    if data['observation_mode']!='actual' or data['host_policy_sha256']!=sm.sha256(value._context._policy):raise ValueError('actual original H/capture required')
    return data,value._archive


def _failed_data(authority:c.ComparisonCaptureAuthority,packet:dict,archive:dict,error:BaseException,workdir:Path|None,workspace_cleanup:str)->dict:
    empty={'sha256':c._put(archive,b''),'bytes':0}
    stream=lambda fd:{'captured':dict(empty),'observed_bytes_lower_bound':0,'complete':False,'original_descriptor':fd,'generation':0,'identity':None,'eof_event_seq':None}
    policy=c._put(archive,authority._context._policy);archive.update(authority._context._evidence)
    data={'schema':'TEST_ONLY-pdf-baseline-capture-data/v1','purpose':'TEST_ONLY','observation_mode':'actual',
        'plan_sha256':sm.sha256(sm.canonical(packet['comparison_plan'])),'pair_plan_sha256':packet['comparison_plan']['pair_plan_sha256'],
        'host_policy_sha256':policy,'host_evidence_sha256':c._record(archive,{'schema':'TEST_ONLY-comparison-host-evidence-index/v1','sha256s':sorted(sm._json(authority._context._policy)['evidence_sha256s'])}),
        'run_id':None,'invocation_sha256':None,'process_sha256':None,'run_clock_sha256':None,'native_events_sha256':None,'dependency_observation_sha256':None,
        'stdout':stream(1),'stderr':stream(2),'terminal_wait':None,'custody_sha256':None,'cleanup':workspace_cleanup if workspace_cleanup in ('removed','failed') else 'preserved-uncertain' if workdir else 'not-created',
        'intervention':'none','status':'FAILED_DATA','failure':{'stage':'prepare','code':'CAPTURE_REFUSED','original_exception_type':type(error).__name__[:80],'facts_sha256':None}}
    data['failure']['facts_sha256']=c._failure_facts(data,archive,'collector returned no verified complete DATA',type(error).__name__[:80],str(workdir) if workdir else None)
    return data


def _capture_next_remap_baseline(original:c.OriginalComparisonSuite,context:n.NativeHostContext)->_BaselineCompletion:
    bound=_bound_flow(original);preflight_entry=None
    try:
        preflight_entry=_preflight_attempt(original,bound,(36,38,40))
        flow,entry,packet=_selected(original,(36,38,40))
        if entry['phase']!='NOT_STARTED':raise ValueError('remap baseline already attempted')
        authority=_freeze(original,context,packet,entry);entry['phase']='BASELINE_RUNNING'
        entry['attempts'][-1].update(plan=authority._plan,H=context._policy)
        archive=dict(authority._archive);archive.update(context._evidence);archive[sm.sha256(context._policy)]=context._policy
        entry['baseline_archive']=archive
        workdir=None;cleanup='preserved-uncertain';run=None;interruption=None
        try:
            c._consume(authority,patched=False);object.__setattr__(authority,'_spent',True)
            workdir=Path(c.tempfile.mkdtemp(prefix='TEST_ONLY-pdf-remap-comparison-'));c.os.chmod(workdir,0o700)
            for name,blob in [('input',packet['pair_plan']['fixture']),('native-config',packet['pair_plan']['config'])]:migration._write_owned(workdir/name,c._blob(blob,archive,256*MIB))
            plan=packet['comparison_plan'];candidates=c._candidate_rows(plan,archive,str(workdir))
            spec={'schema':'twin.native-observation-spec/v1','purpose':'actual','profile':'pdf-text-xpdf/1','plan_sha256':sm.sha256(sm.canonical(plan)),
                'argv':migration._pdf_command(plan['executable_path'],str(workdir)),'cwd':str(workdir),'environment':dict(migration.ENVIRONMENT),'limits':dict(c.LIMITS),'candidates':candidates}
            run=c._linux_run_comparison(authority,spec,archive);entry['baseline_run']=run
            interruption=run.get('_interruption')
            try:n.validate_native_custody(run['process_group'])
            except (ValueError,KeyError,TypeError):pass
            else:
                object.__setattr__(original,'_target_custody_known',True);object.__setattr__(original,'_active_slot',None)
                try:shutil.rmtree(workdir);cleanup='removed'
                except OSError:cleanup='failed'
            try:n._host_window(context);flow.guard.verify();_check_drivers(packet)
            except (ValueError,OSError,TypeError):run['failure']=run['failure'] or 'post-run-host-or-source-refused'
            data=c._finalize_capture(plan,run,archive,workspace_cleanup=cleanup);entry['baseline_data']=data
            value=_baseline_completion(authority,packet,data,archive);entry['baseline']=value
            if data['status']!='COMPLETE_EXIT0_DATA':
                _stop(original,'BASELINE','CAPTURE_FAILED',None,entry);_retain_adverse(original,flow,entry,packet)
            else:entry['phase']='BASELINE_DONE'
            if run['_interruption'] is not None:raise run['_interruption']
            _time(original,original._started+c.B_SECONDS)
            return value
        except BaseException as error:
            if isinstance(interruption,BaseException) and not isinstance(interruption,Exception):error=interruption
            _stop(original,'BASELINE','CANCELLED' if not isinstance(error,Exception) else 'CAPTURE_MISSING',error,entry)
            if entry['baseline'] is None:
                try:
                    data=_failed_data(authority,packet,archive,error,workdir if cleanup!='removed' else None,cleanup);entry['baseline_data']=data
                    entry['baseline']=_baseline_completion(authority,packet,data,archive)
                except BaseException as secondary:
                    if len(flow.secondary)<32:flow.secondary.append(r._fault(secondary))
            _retain_adverse(original,flow,entry,packet)
            if not isinstance(error,Exception):raise error
            if entry['baseline'] is not None:return entry['baseline']
            raise
    except BaseException as error:
        _stop(original,'BASELINE','CANCELLED' if not isinstance(error,Exception) else 'SELECTION_REFUSED',error,preflight_entry)
        raise


def _failure_wait(observation:dict)->dict|None:
    wait=copy.deepcopy(observation.get('failure',{}).get('wait'))
    if wait is not None:wait['provenance']='natural_terminal';c._wait(wait)
    return wait


def _patched_view(value:_PatchedCompletion,original:c.OriginalComparisonSuite,packet:dict)->tuple[dict,dict,dict]:
    if type(value) is not _PatchedCompletion or value._original is not original:raise ValueError('same private original v2 patched completion required')
    value._guard.verify();value._context._guard.verify()
    if value._pair!=sm.canonical(packet['pair_plan']):raise ValueError('private patched remap pair changed')
    result,observation=n._completed_pdf_result(value._completed)
    if observation['host_policy_sha256']!=sm.sha256(value._context._policy):raise ValueError('original patched actual H changed')
    plan=copy.deepcopy(value._plan);plan['archive']=result['archive'];parent=c._blob(packet['pair_plan']['fixture'],packet['archive'],256*MIB)
    config,closure=bridge._validate_plan(plan,parent)
    if config['native_config_sha256']!=packet['pair_plan']['config']['sha256'] or config['pdf_origin']['build_identity_sha256']!=packet['pair_plan']['build_pair']['patched_build_sha256']:raise ValueError('private patched config/build association changed')
    complete=result['status']=='success';archive=result['archive'];dossier=sm._json(c._raw(result['receipts'],result['dossier_sha256']))
    if complete:
        bridge.verify_pdf_extraction_bundle(plan,parent,result)
        wait=copy.deepcopy(observation['events'][-1]['data']['wait'])
    elif result['status']=='failure':wait=_failure_wait(observation)
    else:raise ValueError('private patched completion status differs')
    if wait is not None:wait['provenance']='natural_terminal';c._wait(wait)
    data={'schema':'TEST_ONLY-pdf-patched-comparison-data/v1','purpose':'TEST_ONLY','observation_mode':'actual','pair_plan_sha256':sm.sha256(sm.canonical(packet['pair_plan'])),
        'stdout':{'captured':dossier['stdout'],'complete':complete},'stderr':{'captured':dossier['stderr'],'complete':complete},'terminal_wait':wait,
        'status':'COMPLETE_EXIT0_DATA' if complete else 'FAILED_DATA','origin_effect_confirmed':complete,
        'host_policy_sha256':observation['host_policy_sha256'],'native_observation_sha256':sm.sha256(sm.canonical(observation))}
    for channel in ('stdout','stderr'):c._blob(data[channel]['captured'],archive,c.LIMITS[channel+'_bytes'])
    return data,archive,{'observation':observation,'archive':archive,'plan':plan}


def _capture_next_remap_patched(original:c.OriginalComparisonSuite,store:n.NativeObservationStore,native_plan:dict)->_PatchedCompletion:
    bound=_bound_flow(original);preflight_entry=None
    try:
        preflight_entry=_preflight_attempt(original,bound,(37,39,41))
        flow,entry,packet=_selected(original,(37,39,41))
        if entry['phase']!='BASELINE_DONE':raise ValueError('complete private remap baseline required')
        baseline,_=_baseline_view(entry['baseline'],original,packet)
        if baseline['status']!='COMPLETE_EXIT0_DATA':raise ValueError('failed baseline cannot launch partner')
        if type(store) is not n.NativeObservationStore or store._purpose!='actual' or type(store._host_context) is not n.NativeHostContext:raise ValueError('genuine actual patched store/context required')
        store._guard.verify();context=store._host_context;authority=_freeze(original,context,packet,entry)
        frozen=copy.deepcopy(native_plan);parent=c._blob(packet['pair_plan']['fixture'],packet['archive'],256*MIB)
        config,closure=n.validate_native_candidate_plan(frozen,parent)
        if frozen['purpose']!='actual' or frozen['profile']!=bridge.PROFILE:raise ValueError('fixed actual profile2 patched plan required')
        bridge._require_actual_selection(store,frozen)
        policy=n._host_window(context);closure_pin=frozen['implementation_artifact_sha256']
        if closure_pin not in policy['evidence_sha256s'] or c._raw(context._evidence,closure_pin)!=c._raw(frozen['archive'],closure_pin):raise ValueError('earlier independently selected patched candidate closure absent')
        pair=packet['pair_plan'];resource=pair['resource']
        if (config['native_config_sha256']!=pair['config']['sha256'] or config['pdf_origin']['build_identity_sha256']!=pair['build_pair']['patched_build_sha256']
                or c._raw(frozen['archive'],config['native_config_sha256'])!=c._blob(pair['config'],packet['archive'],8192)
                or c._raw(frozen['archive'],pair['build_pair']['patched_build_sha256'])!=c._raw(packet['archive'],pair['build_pair']['patched_build_sha256'])
                or [row for row in closure['platform_files'] if row['path']==resource['path']]!=[{'path':resource['path'],**resource['blob']}]):raise ValueError('patched remap selection/resource differs')
        r.check_remap_host_evidence(packet,policy,context._evidence,c._raw(frozen['archive'],frozen['configuration_sha256']))
        if time.monotonic()-authority._selected_at>60:raise ValueError('original remap preparation deadline')
        entry['phase']='PATCHED_RUNNING';entry['attempts'][-1].update(plan=sm.canonical({k:v for k,v in frozen.items() if k!='archive'}),H=context._policy)
        try:
            c._consume(authority,patched=True);object.__setattr__(authority,'_spent',True)
            completed=migration._execute_prepared_extraction(frozen,parent,observation_store=store,preparation_deadline=min(authority._selected_at+60,original._started+c.B_SECONDS))
            entry['patched_return']=completed  # Hold the first actual return before validation.
            result,actual_record=n._completed_pdf_result(completed);entry['patched_archive']=result['archive']
            dossier=sm._json(c._raw(result['receipts'],result['dossier_sha256']))
            try:n.validate_native_custody(dossier['process_group'])
            except (ValueError,KeyError,TypeError):original._stopped=True
            else:object.__setattr__(original,'_target_custody_known',True);object.__setattr__(original,'_active_slot',None)
            if actual_record['host_policy_sha256']!=sm.sha256(context._policy):raise ValueError('patched actual recorder/H mismatch')
            if result['status']=='success':n.verify_native_observation(actual_record,result['archive'],purpose='actual');bridge.verify_pdf_extraction_bundle(frozen,parent,result)
            elif result['status']!='failure':raise ValueError('patched result status differs')
            store._guard.verify();flow.guard.verify();n._host_window(context);_check_drivers(packet)
            value=object.__new__(_PatchedCompletion)
            for key,item in {'_completed':(copy.deepcopy(result),copy.deepcopy(actual_record)),'_plan':{k:copy.deepcopy(v) for k,v in frozen.items() if k!='archive'},
                '_pair':sm.canonical(pair),'_guard':flow.guard,'_context':context,'_original':original}.items():object.__setattr__(value,key,item)
            entry['patched']=value
            c._retain_completion(authority,result['archive'],failed=result['status']!='success',patched=True)
            if result['status']!='success' or original._stopped:
                entry['patched_data']=_patched_view(value,original,packet)[0]
                _stop(original,'PATCHED','CAPTURE_FAILED',None,entry);_retain_adverse(original,flow,entry,packet)
            else:entry['phase']='GATE_PENDING'
            _time(original,original._started+c.B_SECONDS)
            return value
        except BaseException as error:
            _stop(original,'PATCHED','CANCELLED' if not isinstance(error,Exception) else 'CAPTURE_MISSING',error,entry)
            _retain_adverse(original,flow,entry,packet)
            raise
    except BaseException as error:
        _stop(original,'PATCHED','CANCELLED' if not isinstance(error,Exception) else 'SELECTION_REFUSED',error,preflight_entry)
        raise


def _failure_pin(flow:r._RemapFlow)->str|None:
    return sm.sha256(flow.failure_raw) if flow.failure_raw is not None else None


def _gate_record(packet:dict,entry:dict,status:str,baseline:dict|None,patched:dict|None,summary:str|None,failure:str|None)->dict:
    return {'schema':'TEST_ONLY-pdf-remap-gate/v1','pair_plan_sha256':sm.sha256(sm.canonical(packet['pair_plan'])),'control':packet['pair_plan']['resource']['control'],
        'stage_record_sha256':entry['stage_pin'],'baseline_data_sha256':sm.sha256(sm.canonical(baseline)) if baseline else None,
        'patched_data_sha256':sm.sha256(sm.canonical(patched)) if patched else None,
        'baseline_observation_sha256':baseline['native_events_sha256'] if baseline else None,'patched_observation_sha256':patched['native_observation_sha256'] if patched else None,
        'status':status,'summary_sha256':summary,'first_failure_sha256':failure}


def _retain_adverse(original:c.OriginalComparisonSuite,flow:r._RemapFlow,entry:dict,packet:dict)->None:
    """One stopped disposition from available capture facts; never a gate retry."""
    if not flow.reserved or entry['disposition'] is not None:return
    if entry['gate_spent'] and (len(entry['journal'])!=2 or sm._json(flow.records[entry['journal'][-1]])['status']!='REFUSED'):return
    if not entry['gate_spent'] and entry['journal']:return
    try:
        baseline=entry['baseline_data'];patched=entry['patched_data']
        for data in (baseline,patched):
            if data is not None:_put(flow,data)
        first=_failure_pin(flow)
        if first is None:raise ValueError('adverse disposition needs first failure')
        if flow.failure is not None:_put(flow,flow.failure)
        if not entry['gate_spent']:entry['journal'].append(_put(flow,_gate_record(packet,entry,'NOT_RUN',baseline,patched,None,first)))
        comparison=c._compare_data(packet['pair_plan'],baseline,entry['baseline_archive'] or {},patched,entry['patched_archive'] or {},actual_origin_confirmed=False)
        comparison_pin=_put(flow,comparison);technical=_put(flow,r._held_stage_data(original))
        record={'schema':'TEST_ONLY-pdf-remap-pair-disposition/v1','qualification':'NONE','pair_plan_sha256':sm.sha256(sm.canonical(packet['pair_plan'])),
            'control':packet['pair_plan']['resource']['control'],'baseline_slot':entry['slot'],'patched_slot':entry['slot']+1,
            'baseline_data_sha256':sm.sha256(sm.canonical(baseline)) if baseline else None,'patched_data_sha256':sm.sha256(sm.canonical(patched)) if patched else None,
            'gate_journal_sha256':_put(flow,entry['journal']),'pair_comparison_sha256':comparison_pin,'first_failure_sha256':first,'stop_suite':True,'technical_state_sha256':technical}
        _put(flow,record);entry['disposition']=record
    except BaseException as secondary:
        if len(flow.secondary)<32:flow.secondary.append(r._fault(secondary))


def _compare_remap_pair(original:c.OriginalComparisonSuite)->dict:
    flow=_flow(original)
    if original._next not in (38,40,42):raise ValueError('fixed completed remap pair required')
    entry=flow.entries[(original._next-38)//2];packet=flow.packets[(original._next-38)//2]
    if entry['gate_spent'] or entry['phase']!='GATE_PENDING' or original._stopped or not original._awaiting_comparison or original._active_slot is not None or not original._target_custody_known:raise ValueError('private pending gate/custody required')
    entry['gate_spent']=True;entry['phase']='GATE_RUNNING'
    baseline=None;patched=None
    try:
        # STARTED is retained before any private view extraction or pure checker.
        start=_gate_record(packet,entry,'STARTED',None,None,None,None);entry['journal'].append(_put(flow,start))
        baseline,left_archive=_baseline_view(entry['baseline'],original,packet)
        patched,right_archive,right_bundle=_patched_view(entry['patched'],original,packet)
        entry['baseline_data']=baseline;entry['patched_data']=patched
        _put(flow,baseline);_put(flow,patched)
        if baseline['status']!='COMPLETE_EXIT0_DATA' or patched['status']!='COMPLETE_EXIT0_DATA':raise ValueError('incomplete capture cannot pass remap gate')
        observation=c._json(left_archive,baseline['native_events_sha256'])
        summary=r.check_remap_control(packet,{'observation':observation,'archive':left_archive,'plan':packet['comparison_plan']},right_bundle)
        summary_pin=_put(flow,summary)
        result=c._compare_data(packet['pair_plan'],baseline,left_archive,patched,right_archive,actual_origin_confirmed=True)
        if result['status']!='MATCH' or result['stop_suite']:raise ValueError('adverse remap comparison')
        comparison_pin=_put(flow,result)
        pass_pin=_put(flow,_gate_record(packet,entry,'PASS',baseline,patched,summary_pin,None))
        stage_pin=_put(flow,r._held_stage_data(original));journal_pin=_put(flow,entry['journal']+[pass_pin])
        disposition={'schema':'TEST_ONLY-pdf-remap-pair-disposition/v1','qualification':'NONE','pair_plan_sha256':sm.sha256(sm.canonical(packet['pair_plan'])),
            'control':packet['pair_plan']['resource']['control'],'baseline_slot':entry['slot'],'patched_slot':entry['slot']+1,
            'baseline_data_sha256':sm.sha256(sm.canonical(baseline)),'patched_data_sha256':sm.sha256(sm.canonical(patched)),
            'gate_journal_sha256':journal_pin,'pair_comparison_sha256':comparison_pin,'first_failure_sha256':None,'stop_suite':False,'technical_state_sha256':stage_pin}
        _put(flow,disposition);returned=copy.deepcopy(disposition)
        flow.guard.verify();_check_drivers(packet)
        for completion in (entry['baseline'],entry['patched']):
            completion._context._guard.verify();n._host_window(completion._context)
        _time(original,original._started+c.B_SECONDS)
        entry['journal'].append(pass_pin);entry['disposition']=disposition;entry['phase']='MATCH_RETAINED';original._awaiting_comparison=False
        return returned
    except BaseException as error:
        _stop(original,'GATE','CANCELLED' if not isinstance(error,Exception) else 'GATE_REFUSED',error,entry)
        try:
            if len(entry['journal'])==1:entry['journal'].append(_put(flow,_gate_record(packet,entry,'REFUSED',entry['baseline_data'],entry['patched_data'],None,_failure_pin(flow))))
            result=c._compare_data(packet['pair_plan'],entry['baseline_data'],entry['baseline_archive'] or {},entry['patched_data'],entry['patched_archive'] or {},actual_origin_confirmed=False)
            _put(flow,result)
            _retain_adverse(original,flow,entry,packet)
        except BaseException as secondary:
            if len(flow.secondary)<32:flow.secondary.append(r._fault(secondary))
        raise


def _finish_remap_route(original:c.OriginalComparisonSuite)->dict:
    flow=_raw_flow(original);original._stopped=True
    try:
        result=r._cleanup_remap_resources(original)
        if flow.phase!='STOPPED':flow.phase='FINISHED'
        return result
    except BaseException as error:
        _stop(original,'CLEANUP','CUSTODY_UNKNOWN',error)
        raise


def _held_remap_data(original:c.OriginalComparisonSuite)->dict:
    flow=_raw_flow(original)
    records=dict(flow.records)
    if flow.failure_raw is not None:records[sm.sha256(flow.failure_raw)]=flow.failure_raw
    return {'schema':'TEST_ONLY-pdf-remap-driver-held-data/v1','qualification':'NONE','phase':flow.phase,
        'records':records,'failure':copy.deepcopy(flow.failure),'secondary':copy.deepcopy(flow.secondary),
        'captures':[{'baseline_data':copy.deepcopy(e['baseline_data']),'patched_data':copy.deepcopy(e['patched_data']),
            'baseline_archive':dict(e['baseline_archive']) if e['baseline_archive'] is not None else None,
            'patched_archive':dict(e['patched_archive']) if e['patched_archive'] is not None else None,
            'patched_return':copy.deepcopy(e.get('patched_return')),
            'baseline_run':_run_data(e.get('baseline_run'))} for e in flow.entries],
        'entries':[{'slot':e['slot'],'phase':e['phase'],'gate_spent':e['gate_spent'],'journal':list(e['journal']),
            'has_baseline':e['baseline'] is not None,'has_patched':e['patched'] is not None,'disposition':copy.deepcopy(e['disposition'])} for e in flow.entries]}


def _run_data(run:dict|None)->dict|None:
    if run is None:return None
    # The collector's bytes/observation are already in its held archive. Keep the
    # raw returned custody/wait/failure facts even when finalization failed.
    return {key:copy.deepcopy(value) for key,value in run.items() if key!='_interruption'}


def _stage_snapshot(value:dict,pair:dict,*,complete:bool)->None:
    c._closed(value,{'schema','qualification','phase','root','stage_deadline','final_cleanup_deadline','uncertain_ownership','open_fds','created_files','identities','facts','failure','root_removal_known','clock_observation'})
    resource=pair['resource']
    if value['schema']!='TEST_ONLY-pdf-remap-technical-custody/v1' or value['qualification']!='NONE' or type(value['root_removal_known']) is not bool or type(value['uncertain_ownership']) is not bool:raise ValueError('closed technical snapshot differs')
    if complete:
        c._closed(value['identities'],{row[0] for row in r.RECIPES})
        for control,name,raw in r.RECIPES:r._identity(value['identities'][control],len(raw))
        fds=value['open_fds'];clock=value['clock_observation'];c._closed(clock,{'at','deadline','status'})
        if (type(fds) is not list or len(fds)!=2 or any(type(fd) is not int or fd<0 for fd in fds) or len(set(fds))!=2
                or value['created_files']!=sorted(row[1] for row in r.RECIPES) or value['failure'] is not None
                or clock['status']!='ONTIME' or any(type(clock[k]) not in (int,float) or not math.isfinite(clock[k]) for k in ('at','deadline')) or clock['at']>=clock['deadline']):raise ValueError('complete finite technical custody required')
    if complete and (value['phase']!='COMPLETE_STAGE' or value['root_removal_known'] or value['uncertain_ownership'] or value['identities'].get(resource['control'])!=resource['identity'] or value['root']!=resource['path'].rsplit('/',1)[0]):raise ValueError('complete bound stage snapshot required')


def _first_failure(value:dict)->None:
    c._closed(value,FAILURE_KEYS)
    if (value['schema']!='TEST_ONLY-pdf-remap-first-failure/v1' or value['phase'] not in ('PREPARE','STAGE','HOST','BASELINE','PATCHED','GATE','RETENTION','CLEANUP','RETURN_CLOCK')
            or value['code'] not in ('SELECTION_REFUSED','CAPTURE_FAILED','CAPTURE_MISSING','GATE_REFUSED','RECORD_UNRETAINED','CAPACITY_HELD','CLOCK_HELD','SOURCE_HELD','CUSTODY_UNKNOWN','CANCELLED')
            or value['original_slot'] is not None and (type(value['original_slot']) is not int or not 0<=value['original_slot']<52)
            or value['exception_type'] is not None and (type(value['exception_type']) is not str or not 1<=len(value['exception_type'])<=80)
            or type(value['observations_complete']) is not bool or value['target_custody'] not in ('NOT_CREATED','KNOWN_TERMINAL','UNKNOWN') or type(value['root_removal_known']) is not bool):raise ValueError('closed first failure differs')


def check_remap_disposition(record:dict,archive:dict,expected_packet:dict)->dict:
    """Closed exported DATA only; cannot advance, import or restore a private flow.

    The archive includes retained capture archives as well as the small driver
    metadata. Replaying this DATA never supplies a private completion or actual H.
    """
    r.check_remap_plan(expected_packet);c._closed(record,DISPOSITION_KEYS);pair=expected_packet['pair_plan']
    if (record['schema']!='TEST_ONLY-pdf-remap-pair-disposition/v1' or record['qualification']!='NONE' or record['pair_plan_sha256']!=sm.sha256(sm.canonical(pair))
            or record['control']!=pair['resource']['control'] or type(record['baseline_slot']) is not int or record['baseline_slot']!=pair['schedule_index']*2
            or type(record['patched_slot']) is not int or record['patched_slot']!=record['baseline_slot']+1 or type(record['stop_suite']) is not bool):raise ValueError('closed fixed remap disposition differs')
    baseline=c._json(archive,record['baseline_data_sha256']) if record['baseline_data_sha256'] is not None else None
    patched=c._json(archive,record['patched_data_sha256']) if record['patched_data_sha256'] is not None else None
    if baseline is not None:check_remap_capture_data(baseline,archive,expected_packet)
    if patched is not None:
        c._closed(patched,{'schema','purpose','observation_mode','pair_plan_sha256','stdout','stderr','terminal_wait','status','origin_effect_confirmed','host_policy_sha256','native_observation_sha256'})
        if patched['schema']!='TEST_ONLY-pdf-patched-comparison-data/v1' or patched['purpose']!='TEST_ONLY' or patched['observation_mode']!='actual' or patched['pair_plan_sha256']!=record['pair_plan_sha256'] or patched['status'] not in ('COMPLETE_EXIT0_DATA','FAILED_DATA') or type(patched['origin_effect_confirmed']) is not bool:raise ValueError('closed patched DATA differs')
        for channel in ('stdout','stderr'):
            c._closed(patched[channel],{'captured','complete'});c._blob(patched[channel]['captured'],archive,c.LIMITS[channel+'_bytes'])
            if type(patched[channel]['complete']) is not bool or patched[channel]['complete']!=(patched['status']=='COMPLETE_EXIT0_DATA'):raise ValueError('patched stream completeness differs')
        if patched['terminal_wait'] is not None:c._wait(patched['terminal_wait'])
        observation=sm._json(c._raw(archive,patched['native_observation_sha256']))
        if observation['host_policy_sha256']!=patched['host_policy_sha256'] or patched['origin_effect_confirmed']!=(patched['status']=='COMPLETE_EXIT0_DATA'):raise ValueError('patched observation/H/effect differs')
        if patched['status']=='FAILED_DATA' and sm.canonical(patched['terminal_wait'])!=sm.canonical(_failure_wait(observation)):raise ValueError('failed wait differs from retained original observation')
        if patched['status']=='COMPLETE_EXIT0_DATA':
            n.verify_native_observation(observation,archive,purpose='actual');terminal=observation['events'][-1]['data']
            if patched['terminal_wait']!={**terminal['wait'],'provenance':'natural_terminal'} or any(patched[channel]['captured']!={'sha256':terminal[channel+'_sha256'],'bytes':len(c._raw(archive,terminal[channel+'_sha256']))} for channel in ('stdout','stderr')):raise ValueError('patched original terminal streams/wait differ')
    journal=sm._json(c._raw(archive,record['gate_journal_sha256']))
    if type(journal) is not list or len(journal) not in (1,2):raise ValueError('finite gate journal required')
    gates=[c._json(archive,pin) for pin in journal]
    for gate in gates:c._closed(gate,GATE_KEYS)
    if len(gates)==2 and (gates[0]['status']!='STARTED' or gates[1]['status'] not in ('PASS','REFUSED')) or len(gates)==1 and gates[0]['status']!='NOT_RUN':raise ValueError('consumed gate journal ordering differs')
    stage_pin=None
    for gate in gates:
        c._closed(gate,GATE_KEYS)
        if gate['schema']!='TEST_ONLY-pdf-remap-gate/v1' or gate['pair_plan_sha256']!=record['pair_plan_sha256'] or gate['control']!=record['control']:raise ValueError('gate/pair binding differs')
        stage=c._json(archive,gate['stage_record_sha256']);_stage_snapshot(stage,pair,complete=True)
        if stage_pin is not None and stage_pin!=gate['stage_record_sha256']:raise ValueError('gate stage changed')
        stage_pin=gate['stage_record_sha256']
        if gate['status']=='STARTED':
            if any(gate[k] is not None for k in ('baseline_data_sha256','patched_data_sha256','baseline_observation_sha256','patched_observation_sha256','summary_sha256','first_failure_sha256')):raise ValueError('STARTED cannot claim views or result')
        else:
            for name,data,key in (('baseline',baseline,'native_events_sha256'),('patched',patched,'native_observation_sha256')):
                if gate[name+'_data_sha256']!=record[name+'_data_sha256'] or gate[name+'_observation_sha256']!=(data[key] if data is not None else None):raise ValueError('gate original capture/observation differs')
            if gate['first_failure_sha256']!=record['first_failure_sha256'] or (gate['summary_sha256'] is None)!=(gate['status']!='PASS'):raise ValueError('gate terminal refs differ')
    if record['first_failure_sha256'] is not None:
        failure=c._json(archive,record['first_failure_sha256']);_first_failure(failure)
        for key in ('available_facts_sha256','technical_state_sha256'):
            if failure[key] is not None:c._json(archive,failure[key])
    comparison=c._json(archive,record['pair_comparison_sha256'])
    expected=c._compare_data(pair,baseline,archive,patched,archive,actual_origin_confirmed=not record['stop_suite'])
    if sm.canonical(comparison)!=sm.canonical(expected):raise ValueError('original closed comparison DATA differs')
    technical=c._json(archive,record['technical_state_sha256']);_stage_snapshot(technical,pair,complete=not record['stop_suite'])
    if not record['stop_suite']:
        if (gates[-1]['status']!='PASS' or record['first_failure_sha256'] is not None or comparison['status']!='MATCH' or comparison['stop_suite'] or baseline is None or patched is None):raise ValueError('retained complete gate MATCH required')
        summary=c._json(archive,gates[-1]['summary_sha256'])
        c._closed(summary,{'schema','qualification','scope','control','pair_plan_sha256','association_sha256','baseline_observation_sha256','patched_observation_sha256','intended_reads','input_a_items','stream_exit_equality','origin_map_sha256'})
        if (summary['schema']!='TEST_ONLY-pdf-remap-read-effect-data/v1' or summary['qualification']!='NONE' or summary['scope']!='DATA-only-no-native-authority' or summary['control']!=record['control']
                or summary['pair_plan_sha256']!=record['pair_plan_sha256'] or summary['association_sha256']!=pair['resource']['association_sha256']
                or summary['baseline_observation_sha256']!=baseline['native_events_sha256'] or summary['patched_observation_sha256']!=patched['native_observation_sha256']
                or type(summary['input_a_items']) is not int or summary['input_a_items']<1 or sm.canonical(summary['stream_exit_equality'])!=sm.canonical({'stdout':True,'stderr':True,'exit':True})):raise ValueError('gate summary binding differs')
        observation=sm._json(c._raw(archive,patched['native_observation_sha256']));terminal=observation['events'][-1]['data']
        wire=c._raw(archive,terminal['origin_sha256']);mapping=origin.check_pdf_origin_events(c._raw(archive,terminal['stdout_sha256']),wire)
        rows=[json.loads(line) for line in wire.splitlines()];items=[row for row in rows if row.get('record')=='item' and row['input_scalars']==[65]]
        expected_effect={'identity':([65],'none'),'a-to-b':([66],'unicode-remap'),'a-to-ab':([65,66],'unicode-remap')}[record['control']]
        if (summary['origin_map_sha256']!=sm.sha256(mapping.description) or c._raw(archive,summary['origin_map_sha256'])!=mapping.description
                or summary['input_a_items']!=len(items) or any((item['scalars'],item['taint'])!=expected_effect for item in items)):raise ValueError('summary origin/effect differs')
        if type(summary['intended_reads']) is not list or len(summary['intended_reads'])!=2:raise ValueError('two original intended read sets required')
        for facts,data in zip(summary['intended_reads'],(baseline,patched)):
            observation=sm._json(c._raw(archive,data['native_events_sha256'] if data is baseline else data['native_observation_sha256']))
            wanted={path:observation['files'][path] for path in (pair['resource']['path'],observation['spec']['cwd']+'/native-config')}
            if facts!=r._full_original_reads(observation,archive,wanted):raise ValueError('summary original read facts differ')
    elif record['first_failure_sha256'] is None or gates[-1]['status'] not in ('NOT_RUN','REFUSED'):raise ValueError('stopped disposition needs first failure and adverse gate')
    return {'qualification':'NONE','stop_suite':record['stop_suite']}
