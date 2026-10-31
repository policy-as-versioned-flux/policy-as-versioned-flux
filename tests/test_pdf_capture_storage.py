"""C1 logical ledger models; no genesis, native/OS collector or actual fit proof."""
import copy
import pickle
from typing import Any
import pytest
from twin import source_metadata as sm,pdf_comparison_capture as c,pdf_remap_resources as r
from twin import pdf_capture_storage as s
from test_pdf_comparison_capture import prepared_fixture,authority_model,GuardModel

MIB=1048576

def data_model():
    _,plan,archive=prepared_fixture();original=authority_model(plan,archive)._session
    selected=sm._json(original._selection_raw);selected['reserve_bytes']=7040*MIB;raw=sm.canonical(selected)
    object.__setattr__(original,'_selection_raw',raw);object.__setattr__(original,'_selection',sm.sha256(raw));original._reserve=7040*MIB
    inventory={'schema':'TEST_ONLY-pdf-retained-inventory/v1','original_selection_sha256':original._selection,'owners':[{'owner':'c1-ledger','maximum_bytes':8*MIB},{'owner':'TEST_ONLY-all-other-noncapture','maximum_bytes':2040*MIB}]}
    source_index,source_archive=s._source_material()
    archive=dict(source_archive)
    def put(value):raw=sm.canonical(value);archive[sm.sha256(raw)]=raw;return sm.sha256(raw)
    archive[original._selection]=original._selection_raw
    record={'schema':'TEST_ONLY-pdf-capture-storage-selection/v1','original_selection_sha256':original._selection,'retained_inventory_sha256':put(inventory),'source_inventory_sha256':put(source_index),'reserve_bytes':7040*MIB,'capture_count':52,'capture_bytes':96*MIB,'noncapture_bytes':2048*MIB,'failure_bytes':16*MIB,'technical_bytes':8*MIB,'unspendable_slack_bytes':1128*MIB}
    return original,record,archive


def test_selected_storage_never_appoints_original_from_bytes(monkeypatch):
    original,record,archive=data_model()
    assert s.check_storage_selection(record,archive)=={'qualification':'NONE','reserve_bytes':7381975040,'capture_bytes':100663296,'capture_count':52,'source_complete':False}
    assert s._APPOINTED_STORAGE is None
    value:Any
    for value in ({},record,original):
        with pytest.raises(ValueError):s._allocate_selected_stage(value)
    for cls in (s._Selection,s._Cell,s._Allocation,s._Permit):
        with pytest.raises(ValueError):cls()
    assert original._technical_state is None and not original._stopped


class BudgetGuard(GuardModel):
    description=b'{"purpose":"TEST_ONLY_C1_MODEL_GUARD"}'


def born(monkeypatch,*,allocate=True,real_guard=False):
    original,record,archive=data_model();raw=sm.canonical(record);archive[sm.sha256(raw)]=raw
    monkeypatch.setattr(c.time,'monotonic',lambda:original._started+1)
    selected=object.__new__(s._Selection)
    for name,value in {'_original':original,'_original_raw':original._selection_raw,'_record':raw,'_archive':archive}.items():object.__setattr__(selected,name,value)
    # Explicit pure fixture shape, never a source genesis or chronology proof.
    monkeypatch.setattr(s,'_APPOINTED_STORAGE',selected)
    guard=s._source_guard() if real_guard else BudgetGuard()
    object.__setattr__(selected,'_guard',guard)
    object.__setattr__(original,'_capture_storage_selection',selected)
    if not allocate:return original,selected
    state=s._allocate_selected_stage(original)
    return original,state,state._capture_storage,selected


def test_storage_owner_is_same_original_and_same_stage(monkeypatch):
    original,state,cell,selected=born(monkeypatch)
    assert original._technical_state is state and state._original_owner is original and state._remap_flow.owner is original
    assert cell._original is original and cell._stage is state and cell._selection is selected
    for item in (cell,selected):
        for operation in (copy.copy,copy.deepcopy,pickle.dumps):
            with pytest.raises(ValueError):operation(item)
    for field,value in (('_original',object()),('_stage',object()),('_selection',object())):
        with pytest.raises(ValueError):setattr(cell,field,value)
    with pytest.raises(ValueError):state._capture_storage=None
    other,_,_=data_model();other._technical_state=state
    with pytest.raises(ValueError):s._bound_cell(other)
    with pytest.raises(ValueError):original._capture_storage_selection=selected
    _,plan,archive=prepared_fixture();default=authority_model(plan,archive)._session
    ordinary=r._allocate_stage(default)
    assert ordinary._capture_storage is None
    with pytest.raises(ValueError):ordinary._capture_storage=cell


@pytest.mark.parametrize('location',('guard','charge'))
@pytest.mark.parametrize('kind',(ValueError,KeyboardInterrupt,SystemExit))
def test_storage_placeholder_survives_first_charge_and_guard_cancel(monkeypatch,location,kind):
    original,selected=born(monkeypatch,allocate=False);error=kind('PURE first allocation uncertainty');calls=[]
    def uncertain(*args):
        calls.append(location);state=original._technical_state;cell=state._capture_storage
        assert state._original_owner is original and state._remap_flow.owner is original
        assert cell._original is original and cell._stage is state and cell.journal[0]['status']=='PENDING'
        raise error
    if location=='guard':monkeypatch.setattr(selected._guard,'verify',uncertain)
    else:monkeypatch.setattr(c,'_charge_technical_bytes',uncertain)
    with pytest.raises(kind) as caught:s._allocate_selected_stage(original)
    assert caught.value is error and original._stopped and calls==[location]
    state=original._technical_state;cell=state._capture_storage
    assert cell.phase=='STOPPED' and cell.first_exception is error and cell.first_failure['exception_type']==kind.__name__
    assert original._active_slot is None and original._target_custody_known
    with pytest.raises(ValueError):s._allocate_selected_stage(original)
    assert original._technical_state is state and cell.first_exception is error and calls==[location]


@pytest.mark.parametrize('mutation',('reserve','record','raw','later-birth','started','default-stage'))
def test_selected_reserve_matches_frozen_original(monkeypatch,mutation):
    original,selected=born(monkeypatch,allocate=False);raw=original._selection_raw;guard=original._guard;start=original._started
    if mutation=='reserve':original._reserve-=MIB
    if mutation=='record':
        record=sm._json(selected._record);record['noncapture_bytes']-=1;object.__setattr__(selected,'_record',sm.canonical(record))
    if mutation=='raw':object.__setattr__(selected,'_original_raw',b'not the earlier original')
    if mutation=='later-birth':
        object.__delattr__(original,'_capture_storage_selection')
        with pytest.raises(ValueError):original._capture_storage_selection=selected
    if mutation=='started':original._next=1;original._used_hosts={'1'*64}
    if mutation=='default-stage':r._allocate_stage(original)
    before=original._technical_state
    with pytest.raises(ValueError):s._allocate_selected_stage(original)
    assert original._selection_raw is raw and original._guard is guard and original._started==start
    if mutation in ('later-birth','started','default-stage'):assert original._technical_state is before
    else:assert original._stopped and original._technical_state._capture_storage.phase=='STOPPED'


def test_reserved_to_retained_once_conserves_total(monkeypatch):
    original,state,cell,selected=born(monkeypatch);allocation=s._noncapture(original)
    total=original._retained+original._reserve;raw=bytes(bytearray(b'abc'));permit=s._reserve_retained(allocation,3)
    owned=s._retain(original,permit,raw)
    assert owned._payload is raw and owned.phase=='COMMITTED' and permit.phase=='COMMITTED'
    assert original._retained==8*MIB+3 and original._reserve==7040*MIB-3 and original._retained+original._reserve==total
    assert allocation.issued==8*MIB+3 and allocation.retained==3
    before=(original._retained,original._reserve,allocation.issued,allocation.retained)
    with pytest.raises(ValueError):s._retain(original,permit,raw)
    assert before==(original._retained,original._reserve,allocation.issued,allocation.retained) and original._stopped


def test_pending_scratch_permit_is_not_refund_or_evidence(monkeypatch):
    original,_,cell,_=born(monkeypatch);allocation=s._noncapture(original)
    permit=s._reserve_scratch(allocation,17);total=(original._retained,original._reserve)
    assert allocation.issued==8*MIB+17 and permit.phase=='ISSUED'
    s._spend_scratch(original,permit)
    assert permit.phase=='SPENT' and (original._retained,original._reserve)==total and not cell._owners
    with pytest.raises(ValueError):s._retain(original,permit,b'a')
    assert (original._retained,original._reserve)==total and allocation.issued==8*MIB+17 and original._stopped


@pytest.mark.parametrize('bad',(0,-1,True,2048*MIB+1))
def test_retention_count_neighbors_refuse_before_transfer(monkeypatch,bad):
    original,_,cell,_=born(monkeypatch);allocation=s._noncapture(original);before=(original._retained,original._reserve,allocation.issued)
    with pytest.raises(ValueError):s._reserve_retained(allocation,bad)
    assert before==(original._retained,original._reserve,allocation.issued) and original._stopped and not cell._owners


@pytest.mark.parametrize('failure',('wrong-owner','short-permit','reentry','post-guard-cancel'))
def test_retention_owner_reentry_and_partial_neighbors(monkeypatch,failure):
    original,_,cell,selected=born(monkeypatch);allocation=s._noncapture(original);permit=s._reserve_retained(allocation,3)
    before=(original._retained,original._reserve)
    if failure=='wrong-owner':
        other,_,_,_=born(monkeypatch)
        with pytest.raises(ValueError):s._retain(other,permit,b'abc')
        assert (original._retained,original._reserve)==before and other._stopped
        return
    if failure=='reentry':cell.busy=True
    if failure=='post-guard-cancel':
        error=KeyboardInterrupt('PURE after transfer');calls=[]
        def guard():
            calls.append(1)
            if len(calls)==2:raise error
        monkeypatch.setattr(selected._guard,'verify',guard)
        with pytest.raises(KeyboardInterrupt) as caught:s._retain(original,permit,b'abc')
        assert caught.value is error and cell.first_exception is error and original._stopped
        assert cell._owners[0]._payload==b'abc' and cell._owners[0].transferred and cell._owners[0].phase=='PENDING'
        assert original._retained+original._reserve==sum(before) and permit.phase=='TRANSFER_PENDING'
        return
    with pytest.raises(ValueError):s._retain(original,permit,b'abcd' if failure=='short-permit' else b'abc')
    assert (original._retained,original._reserve)==before and original._stopped


def host_model(monkeypatch,original,selected,*,slot=0):
    from pathlib import Path
    context=object.__new__(c.n.NativeHostContext)
    evidence=dict(selected._archive);evidence[sm.sha256(selected._record)]=selected._record;evidence[sm.sha256(selected._guard.description)]=selected._guard.description
    policy={'schema':'twin.native-host-policy/v1','scope':c.n.SCOPE,'custodian':'PURE C1 SHAPE, NO ACTUAL HOST '+str(slot),'not_before':'2026-10-31T00:00:00+00:00','not_after':'2026-10-31T00:05:00+00:00','roots':[str(Path(s.__file__).resolve().parents[1])],'writer_control':'trusted-administrator-controlled-interval','evidence_sha256s':sorted(evidence)}
    for name,value in {'_policy':sm.canonical(policy),'_evidence':evidence,'_guard':BudgetGuard()}.items():object.__setattr__(context,name,value)
    # No real clock or host query: exact pure elapsed/window models.
    monkeypatch.setattr(c.time,'monotonic',lambda:original._started+1)
    monkeypatch.setattr(c.n,'_host_window',lambda ctx,**kw:sm._json(ctx._policy))
    return context


def model_terminal(original,index,context):
    # Explicit trusted-return shape for pure ledger tests, not custody proof.
    original._used_hosts.add(sm.sha256(context._policy));original._next=index+1


def test_no_cross_slot_or_noncapture_borrow(monkeypatch):
    original,_,cell,selected=born(monkeypatch);context=host_model(monkeypatch,original,selected)
    allocation=s._capture_allocation(original,context)
    assert allocation is cell._allocations[0] and allocation._limit==96*MIB
    permit=s._reserve_scratch(allocation,96*MIB);s._spend_scratch(original,permit)
    model_terminal(original,0,context);s._close_capture(allocation)
    context2=host_model(monkeypatch,original,selected,slot=1);next_allocation=s._capture_allocation(original,context2)
    assert next_allocation._index==1 and next_allocation.issued==0 and cell._allocations[2].phase=='UNOPENED'
    before=(original._retained,original._reserve)
    with pytest.raises(ValueError):s._reserve_retained(allocation,1)
    assert original._stopped and next_allocation.issued==0 and before==(original._retained,original._reserve)
    assert cell._allocations[52].issued==8*MIB and all(a.issued==0 for a in cell._allocations[2:52])


def test_existing_admit_slot_double_count_neighbor(monkeypatch):
    original,_,cell,selected=born(monkeypatch);context=host_model(monkeypatch,original,selected)
    assert original._retained+original._reserve+c.FAILURE_RESERVE+c.MAX_CAPTURE_BYTES==8088*MIB
    c.admit_slot(elapsed_ns=0,slots_used=0,retained_bytes=original._retained,reserve_bytes=original._reserve)
    allocation=s._capture_allocation(original,context);s._reserve_scratch(allocation,96*MIB)
    c.admit_slot(elapsed_ns=0,slots_used=0,retained_bytes=original._retained,reserve_bytes=original._reserve)
    with pytest.raises(ValueError):s._reserve_scratch(allocation,1)
    assert allocation.issued==96*MIB and original._stopped


@pytest.mark.parametrize('charge',('exact','short','extra'))
def test_technical_metadata_charged_outside_7040(monkeypatch,charge):
    original,selected=born(monkeypatch,allocate=False);real=c._charge_technical_bytes;seen=[]
    def charged(owner,count):
        seen.append(count);real(owner,count+({'exact':0,'short':-1,'extra':1}[charge]))
    monkeypatch.setattr(c,'_charge_technical_bytes',charged)
    if charge!='exact':
        with pytest.raises(ValueError):s._allocate_selected_stage(original)
        assert original._stopped and original._technical_state._capture_storage.first_exception is not None
        return
    state=s._allocate_selected_stage(original);cell:Any=state._capture_storage
    assert seen==[8*MIB] and original._retained==8*MIB and original._reserve==7040*MIB
    assert sum(a._limit for a in cell._allocations)==7040*MIB and sum(a.issued for a in cell._allocations)==8*MIB
    assert all(a.retained==0 for a in cell._allocations) and not cell._owners
    assert 8192-7040-16-8==1128
    with pytest.raises(ValueError):s._allocate_selected_stage(original)
    assert seen==[8*MIB] and original._technical_state is state


@pytest.mark.parametrize('kind',(KeyboardInterrupt,SystemExit,ValueError))
def test_first_failure_under_source_revocation(monkeypatch,kind):
    original,state,cell,selected=born(monkeypatch)
    original._next=1;original._used_hosts={'a'*64};original._active_slot=0;original._target_custody_known=False
    error=kind('PURE source revoked');calls=[]
    def revoked():calls.append(1);raise error
    monkeypatch.setattr(selected._guard,'verify',revoked)
    with pytest.raises(kind) as caught:s._noncapture(original)
    assert caught.value is error and cell.first_exception is error and original._stopped
    assert cell.first_failure['target_custody']=='UNKNOWN' and original._active_slot==0 and original._target_custody_known is False
    first=cell.first_failure
    with pytest.raises(ValueError):s._noncapture(original)
    assert cell.first_failure is first and cell.first_exception is error and calls==[1]
    assert state._capture_storage is cell and cell.journal[-1]['status']=='HELD'


@pytest.mark.parametrize('mutation',('function','defaults','global','selection','source-bytes','during'))
def test_selected_guard_inventory_covers_storage_helpers(monkeypatch,mutation):
    original,_,cell,selected=born(monkeypatch,real_guard=True);allocation=s._noncapture(original);permit=s._reserve_retained(allocation,3)
    before=(original._retained,original._reserve);real=s._retain
    if mutation=='function':monkeypatch.setattr(s,'_guard_callback',lambda *args:None)
    if mutation=='defaults':monkeypatch.setattr(s._reserve_retained,'__defaults__',(4,))
    if mutation=='global':monkeypatch.setattr(s,'CAPTURE',97*MIB)
    if mutation=='selection':monkeypatch.setattr(s,'_APPOINTED_STORAGE',None)
    if mutation=='source-bytes':
        record=sm._json(selected._record);index=c._json(selected._archive,record['source_inventory_sha256']);selected._archive[index['files'][0]['sha256']]=b'different earlier material'
    if mutation=='during':
        verify=selected._guard.verify;calls=[]
        def revoke_after_transfer():
            calls.append(1)
            if len(calls)==2:monkeypatch.setattr(s,'CAPTURE',97*MIB)
            verify()
        # Pure fault hook around the held verifier, not a public construction API.
        object.__setattr__(selected._guard,'verify',revoke_after_transfer)
    with pytest.raises(ValueError):real(original,permit,b'abc')
    assert original._stopped and cell.first_exception is not None
    if mutation!='during':assert (original._retained,original._reserve)==before and not cell._owners
    else:assert original._retained+original._reserve==sum(before) and cell._owners[0]._payload==b'abc'


@pytest.mark.parametrize('missing',('none','selection','retained','source-index','source-file','guard','roots','public'))
def test_storage_selection_and_inventory_precede_H(monkeypatch,missing):
    original,_,cell,selected=born(monkeypatch);context=host_model(monkeypatch,original,selected)
    record=sm._json(selected._record);pin=None
    if missing=='selection':pin=sm.sha256(selected._record)
    if missing=='retained':pin=record['retained_inventory_sha256']
    if missing=='source-index':pin=record['source_inventory_sha256']
    if missing=='source-file':pin=c._json(selected._archive,record['source_inventory_sha256'])['files'][0]['sha256']
    if missing=='guard':pin=sm.sha256(selected._guard.description)
    if pin is not None:context._evidence.pop(pin)
    if missing=='roots':
        policy=sm._json(context._policy);policy['roots']=['/elsewhere'];object.__setattr__(context,'_policy',sm.canonical(policy))
    if missing=='public':context=sm._json(context._policy)
    if missing=='none':
        allocation=s._capture_allocation(original,context)
        assert allocation._context is context and allocation._host_pin==sm.sha256(context._policy) and original._next==0 and not original._used_hosts
    else:
        with pytest.raises(ValueError):s._capture_allocation(original,context)
        assert original._stopped and original._next==0 and not original._used_hosts and not cell._owners


@pytest.mark.parametrize('case',('expired','negative-time','slots52','awaiting','unknown','already-open','stale-permit','stale-reserve','reused-H'))
def test_capture_admission_neighbors_preserve_original_constraints(monkeypatch,case):
    original,_,cell,selected=born(monkeypatch);context=host_model(monkeypatch,original,selected)
    allocation:Any=None
    if case in ('already-open','stale-permit','stale-reserve'):
        allocation=s._capture_allocation(original,context)
        if case=='stale-permit':permit=s._reserve_retained(allocation,1)
        if case!='already-open':original._next=2;original._used_hosts={'1'*64,'2'*64}
    if case=='expired':monkeypatch.setattr(c.time,'monotonic',lambda:original._started+10019)
    if case=='negative-time':monkeypatch.setattr(c.time,'monotonic',lambda:original._started-1)
    if case=='slots52':original._next=52;original._used_hosts={sm.sha256(str(i).encode()) for i in range(52)}
    if case=='awaiting':original._awaiting_comparison=True
    if case=='unknown':original._next=1;original._used_hosts={'1'*64};original._active_slot=0;original._target_custody_known=False
    if case=='reused-H':original._next=1;original._used_hosts={sm.sha256(context._policy)}
    before=(original._retained,original._reserve)
    with pytest.raises(ValueError):
        if case=='stale-permit':s._retain(original,permit,b'a')
        elif case=='stale-reserve':s._reserve_retained(allocation,1)
        else:s._capture_allocation(original,context)
    assert original._stopped and before==(original._retained,original._reserve)
    if case=='unknown':assert original._active_slot==0 and not original._target_custody_known


@pytest.mark.parametrize('case',('partial-return','unknown','H-drift'))
def test_capture_close_cannot_manufacture_terminal_custody(monkeypatch,case):
    original,_,cell,selected=born(monkeypatch);context=host_model(monkeypatch,original,selected)
    allocation=s._capture_allocation(original,context)
    if case=='unknown':original._next=1;original._used_hosts={sm.sha256(context._policy)};original._active_slot=0;original._target_custody_known=False
    if case=='H-drift':model_terminal(original,0,context);object.__setattr__(context,'_policy',b'{}')
    with pytest.raises(ValueError):s._close_capture(allocation)
    assert original._stopped and allocation.phase=='OPEN'
    if case=='unknown':assert original._active_slot==0 and not original._target_custody_known


@pytest.mark.parametrize('elapsed',(60,60.000001,-0.000001))
def test_selected_initialization_uses_original_preparation_window(monkeypatch,elapsed):
    original,selected=born(monkeypatch,allocate=False)
    monkeypatch.setattr(c.time,'monotonic',lambda:original._started+elapsed)
    if elapsed==60:
        state=s._allocate_selected_stage(original);cell:Any=state._capture_storage;assert cell.phase=='READY'
    else:
        with pytest.raises(ValueError):s._allocate_selected_stage(original)
        assert original._stopped and original._technical_state._capture_storage.phase=='STOPPED'


@pytest.mark.parametrize('case',('zero','bool','missing-key','extra-key','duplicate-owner','partial-inventory','source-order','wrong-size'))
def test_closed_storage_DATA_neighbors_do_not_select(monkeypatch,case):
    original,record,archive=data_model()
    if case=='zero':record['capture_bytes']=0
    if case=='bool':record['capture_count']=True
    if case=='missing-key':record.pop('failure_bytes')
    if case=='extra-key':record['qualification']='actual'
    if case in ('duplicate-owner','partial-inventory'):
        inventory=c._json(archive,record['retained_inventory_sha256'])
        if case=='duplicate-owner':inventory['owners'][1]['owner']='c1-ledger'
        else:inventory['owners'].pop()
        raw=sm.canonical(inventory);pin=sm.sha256(raw);archive[pin]=raw;record['retained_inventory_sha256']=pin
    if case in ('source-order','wrong-size'):
        index=c._json(archive,record['source_inventory_sha256'])
        if case=='source-order':index['files'].reverse()
        else:index['files'][0]['bytes']+=1
        raw=sm.canonical(index);pin=sm.sha256(raw);archive[pin]=raw;record['source_inventory_sha256']=pin
    with pytest.raises(ValueError):s.check_storage_selection(record,archive)
    assert s._APPOINTED_STORAGE is None and original._technical_state is None and not original._stopped


@pytest.mark.parametrize('case',('count','journal','scratch-replay','wrong-kind','forged-permit','duplicate-payload'))
def test_finite_permit_and_ownership_neighbors(monkeypatch,case):
    original,_,cell,_=born(monkeypatch);allocation=s._noncapture(original)
    if case=='count':
        for _ in range(s.MAX_PERMITS):s._reserve_scratch(allocation,1)
    if case=='journal':cell.journal=[{'operation':'NONCAPTURE','status':'APPLIED','slot':0}]*s.MAX_JOURNAL
    if case=='scratch-replay':permit=s._reserve_scratch(allocation,1);s._spend_scratch(original,permit)
    if case=='forged-permit':
        real=s._reserve_retained(allocation,1);permit=object.__new__(s._Permit)
        for key in ('_allocation','_maximum','_kind','_ordinal','phase'):setattr(permit,key,getattr(real,key))
    if case=='duplicate-payload':
        raw=bytes(bytearray(b'x'));s._retain(original,s._reserve_retained(allocation,1),raw);permit=s._reserve_retained(allocation,1)
    before=(original._retained,original._reserve,allocation.issued)
    with pytest.raises(ValueError):
        if case=='scratch-replay':s._spend_scratch(original,permit)
        elif case=='wrong-kind':s._reserve(allocation,1,'X'*1000)
        elif case=='forged-permit':s._retain(original,permit,b'x')
        elif case=='duplicate-payload':s._retain(original,permit,raw)
        else:s._reserve_scratch(allocation,1)
    assert (original._retained,original._reserve,allocation.issued)==before and original._stopped


def test_allocation_permit_and_owner_are_noncopyable(monkeypatch):
    original,_,_,_=born(monkeypatch);allocation=s._noncapture(original);permit=s._reserve_retained(allocation,1);owner=s._retain(original,permit,b'x')
    for value in (allocation,permit,owner):
        for operation in (copy.copy,copy.deepcopy,pickle.dumps):
            with pytest.raises(ValueError):operation(value)
    with pytest.raises(ValueError):allocation._limit+=1
    with pytest.raises(ValueError):permit._maximum+=1
    with pytest.raises(ValueError):owner._payload=b'other'


def test_retained_owner_and_scratch_have_exact_pending_journal_links(monkeypatch):
    original,_,cell,_=born(monkeypatch);allocation=s._noncapture(original)
    retained=s._reserve_retained(allocation,1);issued=cell.journal[-1]
    assert retained._entry is issued and issued['status']=='APPLIED'
    owner=s._retain(original,retained,b'x')
    assert owner._entry is cell.journal[-1] and owner._entry['operation']=='RETAIN' and owner._entry['status']=='APPLIED'
    scratch=s._reserve_scratch(allocation,1);s._spend_scratch(original,scratch)
    assert scratch._entry in cell.journal and scratch.phase=='SPENT' and scratch._entry['operation']=='RESERVE_SCRATCH'
