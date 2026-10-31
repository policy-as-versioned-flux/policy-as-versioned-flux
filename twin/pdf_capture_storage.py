"""C1 fixed private logical storage ledger; no genesis or collector integration.

Source guards/readbacks and all reached allocation enforcement require C2/C3.
No96MiB runtime enforcement, physical quota, fit or native qualification is issued.
"""
from __future__ import annotations
import dataclasses
from pathlib import Path
import re
from typing import Any, cast
from . import source_metadata as sm,pdf_comparison_capture as c,pdf_remap_resources as r

MIB=1048576
RESERVE=7040*MIB
CAPTURE=96*MIB
NONCAPTURE=2048*MIB
TECHNICAL=8*MIB
LEDGER=8*MIB
MAX_PERMITS=256
MAX_JOURNAL=32768
OPERATIONS=('INITIALIZE','NONCAPTURE','RESERVE_RETAINED','RESERVE_SCRATCH','RETAIN','SCRATCH','CAPTURE','CLOSE_CAPTURE')
SOURCE_FILES=tuple(sorted(('twin/pdf_capture_storage.py','twin/pdf_comparison_capture.py','twin/pdf_remap_resources.py','twin/source_metadata.py','twin/source_metadata.schema.json','twin/source_native_observation.py','twin/qualification.py')))
SELECTION_KEYS={'schema','original_selection_sha256','retained_inventory_sha256','source_inventory_sha256','reserve_bytes','capture_count','capture_bytes','noncapture_bytes','failure_bytes','technical_bytes','unspendable_slack_bytes'}

class StorageHold(ValueError):
    pass

class _Private(c._PrivateCapability):
    def __new__(cls,*args:Any,**kwargs:Any)->Any:raise StorageHold('private source-held storage object required')

@dataclasses.dataclass(eq=False,frozen=True,init=False,repr=False)
class _Selection(_Private):
    _original:c.OriginalComparisonSuite
    _original_raw:bytes
    _record:bytes
    _archive:dict[str,bytes]
    _guard:Any

class _Cell(_Private):
    def __setattr__(self,name:str,value:Any)->None:
        if name in ('_original','_stage','_selection','_selection_raw','_guard','_allocations') and hasattr(self,name):raise StorageHold('immutable C1 ownership/source association')
        object.__setattr__(self,name,value)
    _original:c.OriginalComparisonSuite
    _stage:r._StageState
    _selection:_Selection
    _selection_raw:bytes
    phase:str
    journal:list[dict]
    first_failure:dict|None
    first_exception:BaseException|None
    _guard:Any
    busy:bool
    technical_phase:str
    _allocations:tuple[_Allocation,...]
    _owners:list[_OwnedBytes]

class _Allocation(_Private):
    def __setattr__(self,name:str,value:Any)->None:
        if name.startswith('_') and hasattr(self,name):raise StorageHold('immutable allocation association')
        object.__setattr__(self,name,value)
    _cell:_Cell
    _index:int
    _limit:int
    _context:Any
    _host_pin:str|None
    phase:str
    issued:int
    retained:int
    permits:list[_Permit]

class _Permit(_Private):
    def __setattr__(self,name:str,value:Any)->None:
        if name.startswith('_') and hasattr(self,name):raise StorageHold('immutable permit association')
        object.__setattr__(self,name,value)
    _allocation:_Allocation
    _maximum:int
    _kind:str
    _ordinal:int
    _entry:dict
    phase:str

class _OwnedBytes(_Private):
    def __setattr__(self,name:str,value:Any)->None:
        if name.startswith('_') and hasattr(self,name):raise StorageHold('immutable retained ownership')
        object.__setattr__(self,name,value)
    _permit:_Permit
    _payload:bytes
    _entry:dict
    phase:str
    transferred:bool

# A future trusted original genesis must already hold this exact private birth
# object. No source factory, setter, context/hash importer or actual appointment.
_APPOINTED_STORAGE:_Selection|None=None


def _source_material()->tuple[dict,dict[str,bytes]]:
    root=Path(__file__).resolve().parents[1];rows=[];archive={}
    for name in SOURCE_FILES:
        with (root/name).open('rb') as handle:raw=handle.read(MIB+1)
        if len(raw)>MIB:raise StorageHold('bounded fixed source material required')
        pin=sm.sha256(raw);archive[pin]=raw;rows.append({'path':name,'sha256':pin,'bytes':len(raw)})
    return {'schema':'TEST_ONLY-pdf-storage-source-inventory/v1','files':rows},archive


def check_storage_selection(record:dict,archive:dict)->dict:
    """Pure closed DATA only; cannot construct a suite, cell, permit or H."""
    c._closed(record,SELECTION_KEYS)
    expected={'schema':'TEST_ONLY-pdf-capture-storage-selection/v1','original_selection_sha256':record['original_selection_sha256'],'retained_inventory_sha256':record['retained_inventory_sha256'],'source_inventory_sha256':record['source_inventory_sha256'],'reserve_bytes':RESERVE,'capture_count':52,'capture_bytes':CAPTURE,'noncapture_bytes':NONCAPTURE,'failure_bytes':16*MIB,'technical_bytes':TECHNICAL,'unspendable_slack_bytes':1128*MIB}
    if sm.canonical(record)!=sm.canonical(expected):raise StorageHold('fixed C1 selection differs')
    original=c._raw(archive,record['original_selection_sha256']);selection=c._original_selection(original)
    if selection['reserve_bytes']!=RESERVE:raise StorageHold('original reserve was not preselected7040MiB')
    inventory=c._json(archive,record['retained_inventory_sha256']);c._closed(inventory,{'schema','original_selection_sha256','owners'})
    if inventory['schema']!='TEST_ONLY-pdf-retained-inventory/v1' or inventory['original_selection_sha256']!=record['original_selection_sha256'] or type(inventory['owners']) is not list or not 1<=len(inventory['owners'])<=256:raise StorageHold('earlier retained inventory required')
    names=[];total=0
    for row in inventory['owners']:
        c._closed(row,{'owner','maximum_bytes'})
        if type(row['owner']) is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,64}',row['owner']):raise StorageHold('closed retained owner name required')
        count=c._uint(row['maximum_bytes'],NONCAPTURE)
        if count==0:raise StorageHold('positive retained owner bound required')
        names.append(row['owner']);total+=count
    if len(set(names))!=len(names) or total!=NONCAPTURE or {'owner':'c1-ledger','maximum_bytes':LEDGER} not in inventory['owners']:raise StorageHold('complete fixed noncapture DATA budget required')
    sources=c._json(archive,record['source_inventory_sha256']);c._closed(sources,{'schema','files'})
    if sources['schema']!='TEST_ONLY-pdf-storage-source-inventory/v1' or type(sources['files']) is not list or len(sources['files'])!=len(SOURCE_FILES):raise StorageHold('fixed earlier storage source inventory required')
    for row,path in zip(sources['files'],SOURCE_FILES):
        c._closed(row,{'path','sha256','bytes'})
        if row['path']!=path:raise StorageHold('fixed storage source path differs')
        c._blob({'sha256':row['sha256'],'bytes':row['bytes']},archive,MIB)
    return {'qualification':'NONE','reserve_bytes':RESERVE,'capture_bytes':CAPTURE,'capture_count':52,'source_complete':False}


def _bound_cell(original:c.OriginalComparisonSuite)->_Cell:
    if type(original) is not c.OriginalComparisonSuite:raise StorageHold('exact existing original required')
    state=getattr(original,'_technical_state',None)
    if type(state) is not r._StageState or state._original_owner is not original:raise StorageHold('same original-owned stage required')
    cell=state._capture_storage
    if type(cell) is not _Cell or cell._original is not original or cell._stage is not state:raise StorageHold('same original/stage storage cell required')
    return cast(_Cell,cell)


def _source_guard()->Any:
    import sys
    from . import source_native_observation as n
    policy={'purpose':'TEST_ONLY','allowed_transforms':[],'reviewer_id':'C1-fixed-storage-source','reviewer_role':'source-binding-only'}
    return sm.MetadataAuthority.freeze('C1-storage-source','C1-source-bindings','1',sm.sha256(sm.canonical(policy)),_guard_callback,_guard_callback,policy=policy,helper_modules=(sys.modules[__name__],c,r,n))


def _guard_callback(*args:Any)->None:
    pass


def _allocate_selected_stage(original:c.OriginalComparisonSuite)->r._StageState:
    selected=_APPOINTED_STORAGE
    if (type(original) is not c.OriginalComparisonSuite or type(selected) is not _Selection
            or selected._original is not original or getattr(original,'_capture_storage_selection',None) is not selected):raise StorageHold('earlier exact private birth selection absent')
    if (original._technical_state is not None or original._next!=0 or original._retained!=0 or original._stopped
            or original._active_slot is not None or not original._target_custody_known or original._awaiting_comparison or original._used_hosts):raise StorageHold('cannot migrate an existing/started original')
    state=r._stage_placeholder(original);cell=object.__new__(_Cell)
    cell._original=original;cell._stage=state;cell._selection=selected;cell._selection_raw=selected._record;cell.phase='INITIALIZING'
    cell.journal=[{'operation':'INITIALIZE','status':'PENDING','slot':None}];cell.first_failure=None;cell.first_exception=None;cell.busy=True;cell._guard=None;cell.technical_phase='NOT_CHARGED'
    state._capture_storage=cell;original._technical_state=state
    try:
        c._check_original_suite(original)
        _original_window(original,60)
        guard=selected._guard;object.__setattr__(cell,'_guard',guard);guard.verify()
        _check_birth(cell)
        if original._reserve!=RESERVE:raise StorageHold('initial frozen reserve differs')
        allocations=[]
        for index in range(53):
            allocation=object.__new__(_Allocation)
            allocation._cell=cell;allocation._index=index;allocation._limit=NONCAPTURE if index==52 else CAPTURE
            allocation._context=None;allocation._host_pin=None
            allocation.phase='OPEN' if index==52 else 'UNOPENED';allocation.issued=LEDGER if index==52 else 0;allocation.retained=0;allocation.permits=[]
            allocations.append(allocation)
        cell._allocations=tuple(allocations);cell._owners=[]
        cell.technical_phase='PENDING';c._charge_technical_bytes(original,TECHNICAL);cell.technical_phase='CHARGED'
        cell.phase='READY';_check_cell(cell);_original_window(original,60);cell.journal[0]['status']='APPLIED';cell.busy=False
        return state
    except BaseException as error:
        _fail(cell,error,'INITIALIZE');raise


def _fail(cell:_Cell,error:BaseException,operation:str)->None:
    try:
        original=cell._original
        if _bound_cell(original) is not cell:return
        original._stopped=True;cell.phase='STOPPED'
        if cell.first_failure is None:
            cell.first_exception=error
            cell.first_failure={'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':operation if operation in OPERATIONS else 'INVALID','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'}
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
    except BaseException:
        pass  # Never mask the original pending exception/cancellation.


def _check_birth(cell:_Cell)->None:
    original=cell._original;selected=cell._selection
    if (_APPOINTED_STORAGE is not selected or getattr(original,'_capture_storage_selection',None) is not selected
            or selected._original is not original or selected._original_raw!=original._selection_raw or selected._record!=cell._selection_raw):raise StorageHold('earlier exact birth storage binding differs')
    if type(selected._record) is not bytes or len(selected._record)>MIB:raise StorageHold('bounded earlier storage selection required')
    record=sm._json(selected._record)
    if sm.canonical(record)!=selected._record or record['original_selection_sha256']!=original._selection:raise StorageHold('original/storage bytes differ')
    check_storage_selection(record,selected._archive)
    sources,current=_source_material();earlier=c._json(selected._archive,record['source_inventory_sha256'])
    if sources!=earlier or any(c._raw(selected._archive,pin)!=raw for pin,raw in current.items()):raise StorageHold('earlier fixed source material changed')


def _check_cell(cell:_Cell)->None:
    original=cell._original
    c._check_original_suite(original);cell._guard.verify();_check_birth(cell)
    if original._stopped or cell.phase!='READY' or _bound_cell(original) is not cell:raise StorageHold('storage original stopped or binding changed')
    transferred=sum(len(owner._payload) for owner in cell._owners if owner.transferred)
    if original._reserve!=RESERVE-transferred or original._retained!=TECHNICAL+transferred:raise StorageHold('original storage totals differ from genuine ownership')
    if len(cell._allocations)!=53:raise StorageHold('fixed bucket count differs')
    for index,allocation in enumerate(cell._allocations):
        if type(allocation) is not _Allocation or allocation._cell is not cell or allocation._index!=index or allocation._limit!=(NONCAPTURE if index==52 else CAPTURE):raise StorageHold('fixed bucket association differs')
        c._uint(allocation.issued,allocation._limit);c._uint(allocation.retained,allocation.issued)
        if index<52 and allocation.phase=='OPEN' and _host_evidence(cell,allocation._context)!=allocation._host_pin:raise StorageHold('capture H binding changed')
    _original_window(original,10800)


def _original_window(original:c.OriginalComparisonSuite,seconds:int)->None:
    elapsed=c.time.monotonic()-original._started
    if not 0<=elapsed<=seconds:raise StorageHold('original storage deadline unavailable')


def _begin(original:c.OriginalComparisonSuite,operation:str)->_Cell:
    cell=_bound_cell(original)
    try:
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage transition stopped or reentered')
        cell.busy=True
        if operation not in OPERATIONS:raise StorageHold('closed storage operation required')
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':operation,'status':'PENDING','slot':original._next})
        _check_cell(cell)
        return cell
    except BaseException as error:_fail(cell,error,operation);raise


def _end(cell:_Cell)->None:
    _check_cell(cell)
    cell.journal[-1]['status']='APPLIED';cell.busy=False


def _noncapture(original:c.OriginalComparisonSuite)->_Allocation:
    cell=_begin(original,'NONCAPTURE')
    try:
        allocation=cell._allocations[52];_end(cell);return allocation
    except BaseException as error:_fail(cell,error,'NONCAPTURE');raise


def _allocation_cell(allocation:_Allocation)->_Cell:
    if type(allocation) is not _Allocation:raise StorageHold('exact private allocation required')
    cell=_bound_cell(allocation._cell._original)
    if allocation._cell is not cell or not 0<=allocation._index<53 or cell._allocations[allocation._index] is not allocation:raise StorageHold('owned fixed allocation required')
    return cell


def _reserve(allocation:_Allocation,count:int,kind:str)->_Permit:
    cell=_allocation_cell(allocation);_begin(cell._original,'RESERVE_'+kind if kind in ('RETAINED','SCRATCH') else 'INVALID')
    try:
        c._uint(count,allocation._limit)
        if count==0 or allocation.phase!='OPEN' or allocation.issued+count>allocation._limit or len(allocation.permits)>=MAX_PERMITS:raise StorageHold('fixed prospective bucket exhausted')
        if allocation._index<52 and cell._original._next not in (allocation._index,allocation._index+1):raise StorageHold('stale capture allocation')
        permit=object.__new__(_Permit);permit._allocation=allocation;permit._maximum=count;permit._kind=kind;permit._ordinal=len(allocation.permits);permit._entry=cell.journal[-1];permit.phase='ISSUED'
        allocation.permits.append(permit);allocation.issued+=count
        _end(cell);return permit
    except BaseException as error:_fail(cell,error,'RESERVE_'+kind);raise


def _reserve_retained(allocation:_Allocation,count:int)->_Permit:
    return _reserve(allocation,count,'RETAINED')


def _reserve_scratch(allocation:_Allocation,count:int)->_Permit:
    return _reserve(allocation,count,'SCRATCH')


def _spend_scratch(original:c.OriginalComparisonSuite,permit:_Permit)->None:
    cell=_begin(original,'SCRATCH')
    try:
        _permit(cell,permit,'SCRATCH');permit.phase='SPENT';_end(cell)
    except BaseException as error:_fail(cell,error,'SCRATCH');raise


def _permit(cell:_Cell,permit:_Permit,kind:str)->_Allocation:
    if type(permit) is not _Permit or type(permit._allocation) is not _Allocation:raise StorageHold('exact private permit required')
    allocation=permit._allocation
    if _allocation_cell(allocation) is not cell or permit._kind!=kind or permit.phase!='ISSUED' or not 0<=permit._ordinal<len(allocation.permits) or allocation.permits[permit._ordinal] is not permit or allocation.phase!='OPEN':raise StorageHold('wrong owner, spent or closed permit')
    if allocation._index<52 and cell._original._next not in (allocation._index,allocation._index+1):raise StorageHold('stale capture permit')
    return allocation


def _retain(original:c.OriginalComparisonSuite,permit:_Permit,payload:bytes)->_OwnedBytes:
    cell=_begin(original,'RETAIN')
    try:
        allocation=_permit(cell,permit,'RETAINED')
        if type(payload) is not bytes or not 0<len(payload)<=permit._maximum or any(owner._payload is payload for owner in cell._owners):raise StorageHold('new immutable genuinely held payload required')
        owner=object.__new__(_OwnedBytes);owner._permit=permit;owner._payload=payload;owner._entry=cell.journal[-1];owner.phase='PENDING';owner.transferred=False
        cell._owners.append(owner);permit.phase='TRANSFER_PENDING'
        # Ownership/journal precede the irreversible exact-original transfer.
        count=len(payload);original._reserve-=count;original._retained+=count;owner.transferred=True;allocation.retained+=count
        _end(cell);owner.phase='COMMITTED';permit.phase='COMMITTED';return owner
    except BaseException as error:_fail(cell,error,'RETAIN');raise


def _host_evidence(cell:_Cell,context:Any)->str:
    from . import source_native_observation as n
    if type(context) is not n.NativeHostContext:raise StorageHold('separate earlier private H required')
    context._guard.verify();policy=n._host_window(context)
    if policy.get('schema')!='twin.native-host-policy/v1' or policy.get('scope')!=n.SCOPE:raise StorageHold('held native host policy required')
    selected=cell._selection;record=sm._json(selected._record)
    required=[selected._original_raw,selected._record,cell._guard.description,
              c._raw(selected._archive,record['retained_inventory_sha256']),c._raw(selected._archive,record['source_inventory_sha256'])]
    index=c._json(selected._archive,record['source_inventory_sha256'])
    root=Path(__file__).resolve().parents[1]
    for row in index['files']:
        required.append(c._raw(selected._archive,row['sha256']))
        if not n._inside(str(root/row['path']),policy['roots']):raise StorageHold('fixed source outside held H roots')
    for raw in required:
        pin=sm.sha256(raw)
        if pin not in policy['evidence_sha256s'] or c._raw(context._evidence,pin)!=raw:raise StorageHold('storage/source/retained inventory must precede H')
    return sm.sha256(context._policy)


def _capture_allocation(original:c.OriginalComparisonSuite,context:Any)->_Allocation:
    cell=_begin(original,'CAPTURE')
    try:
        if original._next>=52 or original._active_slot is not None or not original._target_custody_known or original._awaiting_comparison:raise StorageHold('next known-terminal original slot required')
        if any(a.phase=='OPEN' for a in cell._allocations[:52]):raise StorageHold('previous capture bucket not closed')
        allocation=cell._allocations[original._next]
        if allocation.phase!='UNOPENED':raise StorageHold('fixed capture bucket already opened')
        pin=_host_evidence(cell,context)
        if pin in original._used_hosts:raise StorageHold('held H already consumed')
        c.admit_slot(elapsed_ns=int((c.time.monotonic()-original._started)*10**9),slots_used=original._next,retained_bytes=original._retained,reserve_bytes=original._reserve)
        object.__setattr__(allocation,'_context',context);object.__setattr__(allocation,'_host_pin',pin);allocation.phase='OPEN'
        _end(cell);return allocation
    except BaseException as error:_fail(cell,error,'CAPTURE');raise


def _close_capture(allocation:_Allocation)->None:
    cell=_allocation_cell(allocation);original=cell._original;_begin(original,'CLOSE_CAPTURE')
    try:
        if allocation._index>=52 or allocation.phase!='OPEN' or original._next!=allocation._index+1 or original._active_slot is not None or original._target_custody_known is not True or allocation._host_pin not in original._used_hosts:raise StorageHold('independently known completed slot required')
        if _host_evidence(cell,allocation._context)!=allocation._host_pin:raise StorageHold('capture H binding changed')
        allocation.phase='CLOSED';_end(cell)
    except BaseException as error:_fail(cell,error,'CLOSE_CAPTURE');raise
