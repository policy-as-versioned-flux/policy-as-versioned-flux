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
    _initial_cell:_Cell

class _Cell(_Private):
    def __setattr__(self,name:str,value:Any)->None:
        if name in ('_original','_stage','_selection','_selection_raw','_guard','_anchor','_allocations') and hasattr(self,name):raise StorageHold('immutable C1 ownership/source association')
        object.__setattr__(self,name,value)
    _original:c.OriginalComparisonSuite
    _stage:r._StageState|None
    _selection:_Selection
    _selection_raw:bytes
    phase:str
    journal:list[dict]
    first_failure:dict|None
    first_exception:BaseException|None
    _guard:Any
    _anchor:Any
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


@dataclasses.dataclass(eq=False,frozen=True,init=False,repr=False)
class _Guard(_Private):
    _core:Any
    _methods:tuple
    description:bytes

    def verify(self)->None:
        self._core.verify()
        current=_method_dispatch()
        if len(current)!=len(self._methods):raise StorageHold('fixed C1 method set differs')
        for (name,method),(held_name,held,code,defaults,kwdefaults) in zip(current,self._methods):
            if (name!=held_name or method is not held or method.__code__ is not code
                    or method.__defaults__ is not defaults or method.__kwdefaults__ is not kwdefaults):raise StorageHold('fixed C1 method dispatch/code/defaults changed')


# Core MetadataAuthority keeps its class-identity policy. These fixed local
# enforcement methods additionally need actual dispatch/code/default custody.
def _method_dispatch()->tuple:
    return (('private-new',_Private.__new__),('selection-set',_Selection.__setattr__),('selection-delete',_Selection.__delattr__),
            ('cell-set',_Cell.__setattr__),('allocation-set',_Allocation.__setattr__),
            ('permit-set',_Permit.__setattr__),('owned-set',_OwnedBytes.__setattr__),
            ('guard-set',_Guard.__setattr__),('guard-delete',_Guard.__delattr__),('guard-verify',_Guard.verify),
            ('stage-set',r._StageState.__setattr__),('original-set',c.OriginalComparisonSuite.__setattr__),
            ('private-copy',c._PrivateCapability.__copy__),('private-deepcopy',c._PrivateCapability.__deepcopy__),
            ('private-reduce',c._PrivateCapability.__reduce_ex__))


_GUARD_VERIFY=_Guard.verify


def _verify_guard(guard:Any)->None:
    if type(guard) is _Guard:
        # Entries already authenticated this inner function through the held
        # core. Keep the local15-method guard; model transports are checked by
        # that same entry anchor and _end, without duplicate fault callbacks.
        guard._core.verify()
        if type(guard).verify is not _GUARD_VERIFY:raise StorageHold('fixed C1 verifier dispatch changed')
        guard.verify()

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
    selected=getattr(original,'_capture_storage_selection',None)
    cell=getattr(selected,'_initial_cell',None)
    if type(selected) is not _Selection or selected._original is not original or type(cell) is not _Cell or cell._original is not original or cell._selection is not selected:raise StorageHold('same original birth initialization cell required')
    state=getattr(original,'_technical_state',None)
    if state is None and cell._stage is None:return cell
    if type(state) is not r._StageState or state._original_owner is not original:raise StorageHold('same original-owned stage required')
    if state._capture_storage is not cell or cell._stage is not state:raise StorageHold('same original/stage storage cell required')
    return cast(_Cell,cell)


def _source_guard()->Any:
    import sys
    from . import source_native_observation as n
    policy={'purpose':'TEST_ONLY','allowed_transforms':[],'reviewer_id':'C1-fixed-storage-source','reviewer_role':'source-binding-only'}
    methods=[]
    for name,method in _method_dispatch():
        if method.__defaults__ is not None or method.__kwdefaults__ is not None:raise StorageHold('fixed C1 method defaults unavailable')
        methods.append((name,method,method.__code__,None,None))
    core=sm.MetadataAuthority.freeze('C1-storage-source','C1-source-bindings','1',sm.sha256(sm.canonical(policy)),_guard_callback,_guard_callback,policy=policy,helper_modules=(sys.modules[__name__],c,r,n))
    guard=object.__new__(_Guard)
    object.__setattr__(guard,'_core',core);object.__setattr__(guard,'_methods',tuple(methods));object.__setattr__(guard,'description',core.description)
    return guard


def _guard_callback(*args:Any)->None:
    pass


def _allocate_selected_stage(original:c.OriginalComparisonSuite)->r._StageState:
    selected=_APPOINTED_STORAGE
    if (type(original) is not c.OriginalComparisonSuite or type(selected) is not _Selection
            or selected._original is not original or getattr(original,'_capture_storage_selection',None) is not selected):raise StorageHold('earlier exact private birth selection absent')
    if (original._technical_state is not None or original._next!=0 or original._retained!=0 or original._stopped
            or original._active_slot is not None or not original._target_custody_known or original._awaiting_comparison or original._used_hosts or getattr(selected,'_initial_cell',None) is not None):raise StorageHold('cannot migrate an existing/started original')
    # Raw passive ownership only: no reached custom setter/helper before its
    # earlier source guard. This one attempt survives even no StageState return.
    cell=object.__new__(_Cell)
    for name,value in {'_original':original,'_stage':None,'_selection':selected,'_selection_raw':selected._record,'phase':'INITIALIZING',
                       'journal':[{'operation':'INITIALIZE','status':'PENDING','slot':None}],'first_failure':None,'first_exception':None,
                       'busy':True,'_guard':selected._guard,'_anchor':getattr(selected._guard,'_core',selected._guard),'technical_phase':'NOT_CHARGED'}.items():object.__setattr__(cell,name,value)
    object.__setattr__(selected,'_initial_cell',cell)
    try:
        cell._anchor.verify()
        _verify_guard(cell._guard)
        cell._anchor.verify()
        state=r._stage_placeholder(original)
        object.__setattr__(cell,'_stage',state)
        state._capture_storage=cell;original._technical_state=state
        cell._anchor.verify()
        c._check_original_suite(original)
        cell._anchor.verify()
        _original_window(original,60)
        cell._anchor.verify()
        guard=selected._guard;_verify_guard(guard)
        cell._anchor.verify()
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
        cell._anchor.verify()
        cell.technical_phase='PENDING';c._charge_technical_bytes(original,TECHNICAL);cell.technical_phase='CHARGED'
        cell.phase='READY';cell._anchor.verify();_check_cell(cell)
        cell._anchor.verify();_original_window(original,60)
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=60:raise StorageHold('original preparation deadline unavailable after authentication')
        cell.journal[0]['status']='APPLIED';object.__setattr__(cell,'busy',False)
        return state
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'INITIALIZE','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise


def _fail(cell:_Cell,error:BaseException,operation:str)->None:
    try:
        original=cell._original
        # Emergency custody does not invoke any revocable helper or setter.
        selected=cell._selection
        if (type(original) is not c.OriginalComparisonSuite or type(selected) is not _Selection or selected._original is not original
                or getattr(original,'_capture_storage_selection',None) is not selected or getattr(selected,'_initial_cell',None) is not cell):return
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':operation if operation in OPERATIONS else 'INVALID','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
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
    c._check_original_suite(original);_verify_guard(cell._guard);_check_birth(cell)
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
    # Only a fixed held entry can open the row before its direct core check.
    cell=_bound_cell(original)
    try:
        if (not cell.busy or cell.phase!='READY' or original._stopped or operation not in OPERATIONS or not cell.journal
                or cell.journal[-1]!={'operation':operation,'status':'PENDING','slot':original._next}):raise StorageHold('authenticated pending entry required')
        _check_cell(cell)
        return cell
    except BaseException as error:_fail(cell,error,operation);raise


def _end(cell:_Cell)->None:
    cell._anchor.verify()
    _check_cell(cell)


def _noncapture(original:c.OriginalComparisonSuite)->_Allocation:
    if type(original) is not c.OriginalComparisonSuite:raise StorageHold('exact original entry required')
    selected=getattr(original,'_capture_storage_selection',None);cell=getattr(selected,'_initial_cell',None)
    if (type(selected) is not _Selection or type(cell) is not _Cell or selected._original is not original or cell._original is not original
            or cell._selection is not selected):raise StorageHold('exact held entry association required')
    try:
        # Caller holds this entry/code. Authenticate the earlier protected core
        # directly before any mutable C1 inner helper; reuse this pending row.
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage entry stopped or reentered')
        object.__setattr__(cell,'busy',True)
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':'NONCAPTURE','status':'PENDING','slot':original._next})
        cell._anchor.verify()
        _begin(original,'NONCAPTURE')
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        allocation=cell._allocations[52]
        cell._anchor.verify()
        _end(cell)
        # Independent caller-held postcheck, even if the inner finalizer changed.
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable after authentication')
        cell.journal[-1]['status']='APPLIED';object.__setattr__(cell,'busy',False)
        return allocation
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'NONCAPTURE','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise


def _allocation_cell(allocation:_Allocation)->_Cell:
    if type(allocation) is not _Allocation:raise StorageHold('exact private allocation required')
    cell=_bound_cell(allocation._cell._original)
    if allocation._cell is not cell or not 0<=allocation._index<53 or cell._allocations[allocation._index] is not allocation:raise StorageHold('owned fixed allocation required')
    return cell


def _reserve(allocation:_Allocation,count:int,kind:str)->_Permit:
    cell=_allocation_cell(allocation)
    try:
        if (kind not in ('RETAINED','SCRATCH') or not cell.busy or not cell.journal
                or cell.journal[-1]!={'operation':'RESERVE_'+kind,'status':'PENDING','slot':cell._original._next}):raise StorageHold('fixed authenticated reserve entry required')
        c._uint(count,allocation._limit)
        if count==0 or allocation.phase!='OPEN' or allocation.issued+count>allocation._limit or len(allocation.permits)>=MAX_PERMITS:raise StorageHold('fixed prospective bucket exhausted')
        if allocation._index<52 and cell._original._next not in (allocation._index,allocation._index+1):raise StorageHold('stale capture allocation')
        permit=object.__new__(_Permit);permit._allocation=allocation;permit._maximum=count;permit._kind=kind;permit._ordinal=len(allocation.permits);permit._entry=cell.journal[-1];permit.phase='ISSUED'
        allocation.permits.append(permit);allocation.issued+=count
        return permit
    except BaseException as error:_fail(cell,error,'RESERVE_'+kind);raise


def _reserve_retained(allocation:_Allocation,count:int)->_Permit:
    if type(allocation) is not _Allocation:raise StorageHold('exact allocation entry required')
    cell=allocation._cell;original=cell._original;selected=cell._selection
    if (type(cell) is not _Cell or type(original) is not c.OriginalComparisonSuite or type(selected) is not _Selection
            or selected._original is not original or cell._selection is not selected or getattr(selected,'_initial_cell',None) is not cell
            or getattr(original,'_capture_storage_selection',None) is not selected):raise StorageHold('exact held entry association required')
    try:
        # Caller holds this entry/code. Authenticate the earlier protected core
        # directly before any mutable C1 inner helper; reuse this pending row.
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage entry stopped or reentered')
        object.__setattr__(cell,'busy',True)
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':'RESERVE_RETAINED','status':'PENDING','slot':original._next})
        cell._anchor.verify()
        _begin(original,'RESERVE_RETAINED')
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        permit=_reserve(allocation,count,'RETAINED')
        cell._anchor.verify()
        _end(cell)
        # Independent caller-held postcheck, even if the inner finalizer changed.
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable after authentication')
        cell.journal[-1]['status']='APPLIED';object.__setattr__(cell,'busy',False)
        return permit
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'RESERVE_RETAINED','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise


def _reserve_scratch(allocation:_Allocation,count:int)->_Permit:
    if type(allocation) is not _Allocation:raise StorageHold('exact allocation entry required')
    cell=allocation._cell;original=cell._original;selected=cell._selection
    if (type(cell) is not _Cell or type(original) is not c.OriginalComparisonSuite or type(selected) is not _Selection
            or selected._original is not original or cell._selection is not selected or getattr(selected,'_initial_cell',None) is not cell
            or getattr(original,'_capture_storage_selection',None) is not selected):raise StorageHold('exact held entry association required')
    try:
        # Caller holds this entry/code. Authenticate the earlier protected core
        # directly before any mutable C1 inner helper; reuse this pending row.
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage entry stopped or reentered')
        object.__setattr__(cell,'busy',True)
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':'RESERVE_SCRATCH','status':'PENDING','slot':original._next})
        cell._anchor.verify()
        _begin(original,'RESERVE_SCRATCH')
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        permit=_reserve(allocation,count,'SCRATCH')
        cell._anchor.verify()
        _end(cell)
        # Independent caller-held postcheck, even if the inner finalizer changed.
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable after authentication')
        cell.journal[-1]['status']='APPLIED';object.__setattr__(cell,'busy',False)
        return permit
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'RESERVE_SCRATCH','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise


def _spend_scratch(original:c.OriginalComparisonSuite,permit:_Permit)->None:
    if type(original) is not c.OriginalComparisonSuite:raise StorageHold('exact original entry required')
    selected=getattr(original,'_capture_storage_selection',None);cell=getattr(selected,'_initial_cell',None)
    if (type(selected) is not _Selection or type(cell) is not _Cell or selected._original is not original or cell._original is not original
            or cell._selection is not selected):raise StorageHold('exact held entry association required')
    try:
        # Caller holds this entry/code. Authenticate the earlier protected core
        # directly before any mutable C1 inner helper; reuse this pending row.
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage entry stopped or reentered')
        object.__setattr__(cell,'busy',True)
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':'SCRATCH','status':'PENDING','slot':original._next})
        cell._anchor.verify()
        _begin(original,'SCRATCH')
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        _permit(cell,permit,'SCRATCH');permit.phase='SPENT'
        cell._anchor.verify()
        _end(cell)
        # Independent caller-held postcheck, even if the inner finalizer changed.
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable after authentication')
        cell.journal[-1]['status']='APPLIED';object.__setattr__(cell,'busy',False)
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'SCRATCH','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise


def _permit(cell:_Cell,permit:_Permit,kind:str)->_Allocation:
    if type(permit) is not _Permit or type(permit._allocation) is not _Allocation:raise StorageHold('exact private permit required')
    allocation=permit._allocation
    if _allocation_cell(allocation) is not cell or permit._kind!=kind or permit.phase!='ISSUED' or not 0<=permit._ordinal<len(allocation.permits) or allocation.permits[permit._ordinal] is not permit or allocation.phase!='OPEN':raise StorageHold('wrong owner, spent or closed permit')
    if allocation._index<52 and cell._original._next not in (allocation._index,allocation._index+1):raise StorageHold('stale capture permit')
    return allocation


def _retain(original:c.OriginalComparisonSuite,permit:_Permit,payload:bytes)->_OwnedBytes:
    if type(original) is not c.OriginalComparisonSuite:raise StorageHold('exact original entry required')
    selected=getattr(original,'_capture_storage_selection',None);cell=getattr(selected,'_initial_cell',None)
    if (type(selected) is not _Selection or type(cell) is not _Cell or selected._original is not original or cell._original is not original
            or cell._selection is not selected):raise StorageHold('exact held entry association required')
    try:
        # Caller holds this entry/code. Authenticate the earlier protected core
        # directly before any mutable C1 inner helper; reuse this pending row.
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage entry stopped or reentered')
        object.__setattr__(cell,'busy',True)
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':'RETAIN','status':'PENDING','slot':original._next})
        cell._anchor.verify()
        _begin(original,'RETAIN')
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        allocation=_permit(cell,permit,'RETAINED')
        if type(payload) is not bytes or not 0<len(payload)<=permit._maximum or any(owner._payload is payload for owner in cell._owners):raise StorageHold('new immutable genuinely held payload required')
        owner=object.__new__(_OwnedBytes);owner._permit=permit;owner._payload=payload;owner._entry=cell.journal[-1];owner.phase='PENDING';owner.transferred=False
        cell._owners.append(owner);permit.phase='TRANSFER_PENDING'
        # Ownership/journal precede the irreversible exact-original transfer.
        count=len(payload);original._reserve-=count;original._retained+=count;owner.transferred=True;allocation.retained+=count
        cell._anchor.verify()
        _end(cell)
        # Independent caller-held postcheck, even if the inner finalizer changed.
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable after authentication')
        object.__setattr__(owner,'phase','COMMITTED');object.__setattr__(permit,'phase','COMMITTED')
        cell.journal[-1]['status']='APPLIED';object.__setattr__(cell,'busy',False)
        return owner
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'RETAIN','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise


def _host_evidence(cell:_Cell,context:Any)->str:
    from . import source_native_observation as n
    if type(context) is not n.NativeHostContext:raise StorageHold('separate earlier private H required')
    context._guard.verify()
    cell._anchor.verify()
    if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
    policy=n._host_window(context)
    # Held H observations can revoke dispatch before this helper resumes.
    cell._anchor.verify()
    if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
    if policy.get('schema')!='twin.native-host-policy/v1' or policy.get('scope')!=n.SCOPE:raise StorageHold('held native host policy required')
    selected=cell._selection;record=sm._json(selected._record)
    required=[selected._original_raw,selected._record,cell._guard.description,
              c._raw(selected._archive,record['retained_inventory_sha256']),c._raw(selected._archive,record['source_inventory_sha256'])]
    index=c._json(selected._archive,record['source_inventory_sha256'])
    root=Path(__file__).resolve().parents[1]
    cell._anchor.verify()
    if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
    for row in index['files']:
        required.append(c._raw(selected._archive,row['sha256']))
        inside=n._inside(str(root/row['path']),policy['roots'])
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        if not inside:raise StorageHold('fixed source outside held H roots')
    for raw in required:
        pin=sm.sha256(raw)
        if pin not in policy['evidence_sha256s'] or c._raw(context._evidence,pin)!=raw:raise StorageHold('storage/source/retained inventory must precede H')
    return sm.sha256(context._policy)


def _capture_allocation(original:c.OriginalComparisonSuite,context:Any)->_Allocation:
    if type(original) is not c.OriginalComparisonSuite:raise StorageHold('exact original entry required')
    selected=getattr(original,'_capture_storage_selection',None);cell=getattr(selected,'_initial_cell',None)
    if (type(selected) is not _Selection or type(cell) is not _Cell or selected._original is not original or cell._original is not original
            or cell._selection is not selected):raise StorageHold('exact held entry association required')
    try:
        # Caller holds this entry/code. Authenticate the earlier protected core
        # directly before any mutable C1 inner helper; reuse this pending row.
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage entry stopped or reentered')
        object.__setattr__(cell,'busy',True)
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':'CAPTURE','status':'PENDING','slot':original._next})
        cell._anchor.verify()
        _begin(original,'CAPTURE')
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        if original._next>=52 or original._active_slot is not None or not original._target_custody_known or original._awaiting_comparison:raise StorageHold('next known-terminal original slot required')
        if any(a.phase=='OPEN' for a in cell._allocations[:52]):raise StorageHold('previous capture bucket not closed')
        allocation=cell._allocations[original._next]
        if allocation.phase!='UNOPENED':raise StorageHold('fixed capture bucket already opened')
        pin=_host_evidence(cell,context)
        elapsed_ns=int((c.time.monotonic()-original._started)*10**9)
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        if pin in original._used_hosts:raise StorageHold('held H already consumed')
        c.admit_slot(elapsed_ns=elapsed_ns,slots_used=original._next,retained_bytes=original._retained,reserve_bytes=original._reserve)
        object.__setattr__(allocation,'_context',context);object.__setattr__(allocation,'_host_pin',pin);allocation.phase='OPEN'
        cell._anchor.verify()
        _end(cell)
        # Independent caller-held postcheck, even if the inner finalizer changed.
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable after authentication')
        cell.journal[-1]['status']='APPLIED';object.__setattr__(cell,'busy',False)
        return allocation
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'CAPTURE','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise


def _close_capture(allocation:_Allocation)->None:
    if type(allocation) is not _Allocation:raise StorageHold('exact allocation entry required')
    cell=allocation._cell;original=cell._original;selected=cell._selection
    if (type(cell) is not _Cell or type(original) is not c.OriginalComparisonSuite or type(selected) is not _Selection
            or selected._original is not original or cell._selection is not selected or getattr(selected,'_initial_cell',None) is not cell
            or getattr(original,'_capture_storage_selection',None) is not selected):raise StorageHold('exact held entry association required')
    try:
        # Caller holds this entry/code. Authenticate the earlier protected core
        # directly before any mutable C1 inner helper; reuse this pending row.
        if cell.busy or cell.phase!='READY' or original._stopped:raise StorageHold('storage entry stopped or reentered')
        object.__setattr__(cell,'busy',True)
        if len(cell.journal)>=MAX_JOURNAL:raise StorageHold('finite storage journal exhausted')
        cell.journal.append({'operation':'CLOSE_CAPTURE','status':'PENDING','slot':original._next})
        cell._anchor.verify()
        _begin(original,'CLOSE_CAPTURE')
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        if allocation._index>=52 or allocation.phase!='OPEN' or original._next!=allocation._index+1 or original._active_slot is not None or original._target_custody_known is not True or allocation._host_pin not in original._used_hosts:raise StorageHold('independently known completed slot required')
        pin=_host_evidence(cell,allocation._context)
        elapsed=c.time.monotonic()-original._started
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        if pin!=allocation._host_pin:raise StorageHold('capture H binding changed')
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable before close')
        allocation.phase='CLOSED'
        cell._anchor.verify()
        _end(cell)
        # Independent caller-held postcheck, even if the inner finalizer changed.
        cell._anchor.verify()
        if type(cell._guard) is _Guard:_GUARD_VERIFY(cell._guard)
        elapsed=c.time.monotonic()-original._started
        if not 0<=elapsed<=10800:raise StorageHold('original storage deadline unavailable after authentication')
        cell.journal[-1]['status']='APPLIED';object.__setattr__(cell,'busy',False)
    except BaseException as error:
        # This held entry cannot dispatch a possibly revoked emergency helper.
        object.__setattr__(original,'_stopped',True);object.__setattr__(cell,'phase','STOPPED')
        if cell.first_failure is None:
            object.__setattr__(cell,'first_exception',error)
            object.__setattr__(cell,'first_failure',{'schema':'TEST_ONLY-pdf-storage-first-failure/v1','operation':'CLOSE_CAPTURE','exception_type':type(error).__name__[:80],
                'target_custody':'KNOWN_TERMINAL' if original._active_slot is None and original._target_custody_known else 'UNKNOWN'})
        if cell.journal and cell.journal[-1]['status']=='PENDING':cell.journal[-1]['status']='HELD'
        raise
