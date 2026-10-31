"""Independent R21 fault/record controls; all target operations are modeled."""
import copy
from typing import Any
import pytest
from test_pdf_remap_driver import full_driver_models,DriverGuard,execute_model,_EXEC_MODEL
from twin import source_metadata as sm,pdf_remap_driver as d,pdf_comparison_capture as c

def ready_capture(monkeypatch,side,index=0):
    original,model,clock,flow,entry,packet,left,right,contexts=full_driver_models(monkeypatch,index)
    completed=copy.deepcopy(entry['patched']._completed)
    original._awaiting_comparison=False
    if side=='baseline':
        original._next=36+2*index;original._used_hosts={sm.sha256(str(i).encode())for i in range(original._next)}
        entry.update(phase='NOT_STARTED',baseline=None,patched=None,baseline_data=None,patched_data=None)
    else:
        original._next=37+2*index;original._used_hosts.remove(sm.sha256(contexts[1]._policy));entry.update(phase='BASELINE_DONE',patched=None)
    store=object.__new__(d.n.NativeObservationStore)
    for key,value in {'_purpose':'actual','_host_context':contexts[1],'_guard':DriverGuard(),'_entries':{}}.items():setattr(store,key,value)
    return original,model,clock,flow,entry,packet,left,right,contexts,store,completed

@pytest.mark.parametrize('side',('baseline','patched'))
@pytest.mark.parametrize('fault',('clock','source'))
def test_real_capture_prologue_fault_permanently_stops_original(monkeypatch,side,fault):
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,side)
    before=clock[0]
    if fault=='clock':clock[0]=float('nan')
    else:
        def refuse():raise ValueError('PURE reached source changed')
        monkeypatch.setattr(flow.guard,'verify',refuse)
    with pytest.raises(ValueError):
        if side=='baseline':d._capture_next_remap_baseline(original,contexts[0])
        else:d._capture_next_remap_patched(original,store,right['plan'])
    assert original._stopped, 'Original remains resumable after a clock/source refusal in capture prologue'

def test_unconsumed_genuine_next_context_positive_neighbor(monkeypatch):
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,'baseline')
    selected=d._selected(original,(36,38,40));authority=d._freeze(original,contexts[0],packet,entry)
    assert selected[0]is flow and authority._session is original and original._next==36 and not original._stopped

@pytest.mark.parametrize('side',('baseline','patched'))
def test_recovered_clock_cannot_resume_original_after_unknown_clock(monkeypatch,side):
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,side)
    before=clock[0];clock[0]=float('nan')
    with pytest.raises(ValueError):
        if side=='baseline':d._capture_next_remap_baseline(original,contexts[0])
        else:d._capture_next_remap_patched(original,store,right['plan'])
    clock[0]=before+1
    with pytest.raises(ValueError):d._selected(original,(36,38,40)if side=='baseline'else(37,39,41))

@pytest.mark.parametrize('kind',(KeyboardInterrupt,SystemExit))
def test_prologue_clock_cancellation_preserves_identity_and_stops(monkeypatch,kind):
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,'baseline')
    error=kind('PURE original clock interruption')
    def interrupted():raise error
    monkeypatch.setattr(d.time,'monotonic',interrupted)
    with pytest.raises(kind)as caught:d._capture_next_remap_baseline(original,contexts[0])
    assert caught.value is error and original._stopped and flow.failure_raw is not None

def failed_patched_disposition(monkeypatch,wait_known):
    _EXEC_MODEL.clear();_EXEC_MODEL.update(completed=[],calls=[])
    monkeypatch.setattr(d.migration,'_execute_prepared_extraction',execute_model)
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,'patched')
    result,observation=completed
    terminal=observation['events'][-1]['data'];wait={'kind':'exited','raw_status':256,'exit_code':1,'observed_at_ns':terminal['wait']['observed_at_ns']}
    observation['failure']={'wait':wait if wait_known else None};raw=sm.canonical(observation);result['archive'][sm.sha256(raw)]=raw
    dossier=sm._json(result['receipts'][result['dossier_sha256']]);dossier.update(native_observation_sha256=sm.sha256(raw),disposition='failure',failure='PURE failed observation',standard_receipt_sha256=None)
    raw=sm.canonical(dossier);result['receipts'][sm.sha256(raw)]=raw;result['dossier_sha256']=sm.sha256(raw);result['status']='failure'
    _EXEC_MODEL['completed'].append((result,observation))
    d._capture_next_remap_patched(original,store,right['plan'])
    record=copy.deepcopy(entry['disposition'])
    archive={**left['archive'],**entry['patched']._completed[0]['archive'],**entry['patched']._completed[0]['receipts'],**flow.records}
    assert d.check_remap_disposition(record,archive,packet)=={'qualification':'NONE','stop_suite':True}
    return original,entry,packet,record,archive

@pytest.mark.parametrize('wait_known',(False,True))
def test_failed_patched_wait_cannot_disagree_with_retained_original_observation(monkeypatch,wait_known):
    original,entry,packet,record,archive=failed_patched_disposition(monkeypatch,wait_known)
    def put(value):raw=sm.canonical(value);archive[sm.sha256(raw)]=raw;return sm.sha256(raw)
    baseline=sm._json(archive[record['baseline_data_sha256']]);patched=sm._json(archive[record['patched_data_sha256']])
    observation=sm._json(archive[patched['native_observation_sha256']]);at=observation['events'][-1]['data']['wait']['observed_at_ns']
    patched['terminal_wait']={'kind':'exited','raw_status':512,'exit_code':2,'observed_at_ns':at,'provenance':'natural_terminal'}
    record['patched_data_sha256']=put(patched)
    journal=sm._json(archive[record['gate_journal_sha256']]);gate=sm._json(archive[journal[0]]);gate['patched_data_sha256']=record['patched_data_sha256'];journal[0]=put(gate);record['gate_journal_sha256']=put(journal)
    record['pair_comparison_sha256']=put(c._compare_data(packet['pair_plan'],baseline,archive,patched,archive,actual_origin_confirmed=False))
    with pytest.raises(ValueError):d.check_remap_disposition(record,archive,packet)

@pytest.mark.parametrize('index',(0,1,2))
def test_failed_patched_attempt_records_its_actual_original_slot(monkeypatch,index):
    _EXEC_MODEL.clear();_EXEC_MODEL.update(completed=[],calls=[],mode='nonreturn')
    monkeypatch.setattr(d.migration,'_execute_prepared_extraction',execute_model)
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,'patched',index)
    expected_slot=37+2*index
    with pytest.raises(RuntimeError):d._capture_next_remap_patched(original,store,right['plan'])
    assert original._stopped and original._active_slot==expected_slot and not original._target_custody_known
    assert entry['attempts'][-1]['slot']==expected_slot
    assert flow.failure['original_slot']==expected_slot, 'Patched failure mislabeled with its baseline partner slot'


class UnknownInterruption(BaseException):
    pass


@pytest.mark.parametrize('side',('baseline','patched'))
@pytest.mark.parametrize('location',('original-source','H-source','authority'))
@pytest.mark.parametrize('kind',(ValueError,KeyboardInterrupt,SystemExit,UnknownInterruption))
def test_bound_preflight_fault_keeps_first_identity_attempt_and_custody(monkeypatch,side,location,kind):
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,side)
    expected=36 if side=='baseline' else 37;error=kind('PURE first preflight fault')
    def refuse(*args,**kwargs):raise error
    if location=='original-source':target=original._guard;attribute='verify'
    elif location=='H-source':target=contexts[0 if side=='baseline' else 1]._guard;attribute='verify'
    else:target=d;attribute='_freeze'
    saved=getattr(target,attribute);monkeypatch.setattr(target,attribute,refuse)
    def capture():
        if side=='baseline':return d._capture_next_remap_baseline(original,contexts[0])
        return d._capture_next_remap_patched(original,store,right['plan'])
    with pytest.raises(kind) as caught:capture()
    assert caught.value is error and original._stopped and flow.phase=='STOPPED'
    assert original._next==expected and original._active_slot is None and original._target_custody_known
    assert flow.failure['original_slot']==expected and flow.failure['exception_type']==kind.__name__
    assert entry['attempts']==[{'slot':expected,'plan':None,'H':None}]
    first=flow.failure_raw;monkeypatch.setattr(target,attribute,saved)
    with pytest.raises(ValueError):capture()
    assert first is not None and flow.failure_raw==first and len(entry['attempts'])==1


@pytest.mark.parametrize('side',('baseline','patched'))
def test_preflight_stop_does_not_promote_preexisting_unknown_target_custody(monkeypatch,side):
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,side)
    prior=original._next-1;original._active_slot=prior;original._target_custody_known=False
    with pytest.raises(ValueError):
        if side=='baseline':d._capture_next_remap_baseline(original,contexts[0])
        else:d._capture_next_remap_patched(original,store,right['plan'])
    assert original._stopped and original._active_slot==prior and original._target_custody_known is False
    assert flow.failure['target_custody']=='UNKNOWN' and flow.failure['observations_complete'] is False
    assert entry['attempts'][0]['slot']==prior+1


@pytest.mark.parametrize('kind',(KeyboardInterrupt,SystemExit,UnknownInterruption))
def test_preflight_primary_exception_survives_secondary_first_record_failure(monkeypatch,kind):
    original,model,clock,flow,entry,packet,left,right,contexts,store,completed=ready_capture(monkeypatch,'baseline');error=kind('PURE primary')
    def primary(*args):raise error
    def secondary(*args):raise OSError('PURE metadata serialization unavailable')
    monkeypatch.setattr(d,'_freeze',primary);monkeypatch.setattr(d,'_encoded',secondary)
    with pytest.raises(kind) as caught:d._capture_next_remap_baseline(original,contexts[0])
    assert caught.value is error and original._stopped and flow.failure['exception_type']==kind.__name__
    assert flow.failure['original_slot']==36 and flow.failure_raw is None and entry['attempts'][0]['slot']==36


@pytest.mark.parametrize('wait_known',(False,True))
@pytest.mark.parametrize('replacement',('same','null','exit0','exit2','signal9'))
def test_failed_wait_positive_null_exit_and_signal_neighbors(monkeypatch,wait_known,replacement):
    original,entry,packet,record,archive=failed_patched_disposition(monkeypatch,wait_known)
    def put(value):raw=sm.canonical(value);archive[sm.sha256(raw)]=raw;return sm.sha256(raw)
    baseline=sm._json(archive[record['baseline_data_sha256']]);patched=sm._json(archive[record['patched_data_sha256']])
    observation=sm._json(archive[patched['native_observation_sha256']]);at=observation['events'][-1]['data']['wait']['observed_at_ns']
    if replacement=='null':patched['terminal_wait']=None
    if replacement.startswith('exit'):
        exit_code=int(replacement[4:]);patched['terminal_wait']={'kind':'exited','raw_status':exit_code*256,'exit_code':exit_code,'observed_at_ns':at,'provenance':'natural_terminal'}
    if replacement=='signal9':patched['terminal_wait']={'kind':'signaled','raw_status':9,'signal':9,'core_dumped':False,'observed_at_ns':at,'provenance':'natural_terminal'}
    record['patched_data_sha256']=put(patched);journal=sm._json(archive[record['gate_journal_sha256']]);gate=sm._json(archive[journal[0]]);gate['patched_data_sha256']=record['patched_data_sha256'];journal[0]=put(gate);record['gate_journal_sha256']=put(journal)
    record['pair_comparison_sha256']=put(c._compare_data(packet['pair_plan'],baseline,archive,patched,archive,actual_origin_confirmed=False))
    if replacement=='same' or replacement=='null' and not wait_known:
        assert d.check_remap_disposition(record,archive,packet)=={'qualification':'NONE','stop_suite':True}
    else:
        with pytest.raises(ValueError):d.check_remap_disposition(record,archive,packet)
    assert original._stopped and original._active_slot is None and original._target_custody_known
