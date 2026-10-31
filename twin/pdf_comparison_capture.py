"""Bounded TEST_ONLY comparative PDF DATA; never a metadata/extraction issuer.

Pure records cannot appoint a host or reconstruct private completion. Native source
is reached only with an independently selected private host context; deployments
must supply that selection and a separately reviewed exact execution GO.
"""
from __future__ import annotations
import copy
import ctypes
import dataclasses
import datetime
import errno
import os
from pathlib import Path
import platform
import selectors
import signal
import stat
import sys
import tempfile
import time
from typing import Any
from . import source_metadata as sm
from . import source_native_observation as n
from . import source_metadata_migration as migration
from . import pdf_native_bridge as bridge
from . import pdf_output_origin as origin

MIB=1048576
DATA_SCOPE='TEST_ONLY-pdf-baseline-comparison/linux-x86_64-v1'
LIMITS=dict(migration.PROFILES['pdf-text-xpdf/1'])
B_SECONDS=10800
SLOT_SECONDS=182
MAX_SUITE_BYTES=8192*MIB
FAILURE_RESERVE=16*MIB
MAX_CAPTURE_BYTES=1024*MIB
MAX_BUFFER_BYTES=456*MIB
ARCHIVE='1c38f527c46caee0f712386d42a885b96a31ed9ce11904e872559859894d137e'
PATCH='ce4d927e34922b737552a605ae8332651031c8b77893264e72699215ed181395'


class _PrivateCapability:
    """Copying or serializing a private capability cannot reset its spent state."""
    def __copy__(self):
        raise ValueError('private comparison capability cannot be copied')

    def __deepcopy__(self, memo):
        raise ValueError('private comparison capability cannot be copied')

    def __reduce_ex__(self, protocol):
        raise ValueError('private comparison capability cannot be serialized')


@dataclasses.dataclass(eq=False, frozen=True, init=False, repr=False)
class ComparisonCaptureAuthority(_PrivateCapability):
    _context: n.NativeHostContext
    _guard: Any
    _pair: bytes
    _archive: dict[str,bytes]
    _selected_at: float
    _spent: bool
    _suite_started: float
    _slots_used: int
    _retained_bytes: int
    _reserve_bytes: int
    _plan: bytes
    _session: ComparisonSession
    _slot: int


@dataclasses.dataclass(eq=False, frozen=True, init=False, repr=False)
class ComparisonCompletion(_PrivateCapability):
    _record: bytes
    _held_record: bytes
    _archive: dict[str,bytes]
    _plan: bytes
    _pair: bytes
    _guard: Any
    _session: ComparisonSession


def _closed(value: Any, fields: set[str]) -> None:
    if type(value) is not dict or set(value)!=fields: raise ValueError('closed comparison DATA record required')


def _uint(value: Any, high: int=2**64-1) -> int:
    if type(value) is not int or not 0<=value<=high: raise ValueError('exact bounded unsigned integer required')
    return value


def _hash(value: Any) -> str:
    if type(value) is not str or len(value)!=64 or any(ch not in '0123456789abcdef' for ch in value): raise ValueError('exact comparison hash required')
    return value


def _raw(archive: dict, pin: str) -> bytes:
    _hash(pin)
    if type(archive) is not dict or pin not in archive or type(archive[pin]) is not bytes or sm.sha256(archive[pin])!=pin: raise ValueError('retained comparison bytes required')
    return archive[pin]


def _json(archive: dict, pin: str) -> dict:
    raw=_raw(archive,pin)
    if len(raw)>MIB: raise ValueError('comparison record size exceeded')
    value=sm._json(raw)
    if type(value) is not dict or sm.canonical(value)!=raw: raise ValueError('canonical comparison record required')
    return value


def _put(archive: dict, raw: bytes) -> str:
    if type(raw) is not bytes: raise ValueError('exact artifact bytes required')
    pin=sm.sha256(raw);archive[pin]=raw;return pin


def _record(archive: dict, value: Any) -> str:
    raw=sm.canonical(value)
    if len(raw)>MIB: raise ValueError('comparison record size exceeded')
    return _put(archive,raw)


def _blob(value: Any, archive: dict, cap: int) -> bytes:
    _closed(value,{'sha256','bytes'});raw=_raw(archive,value['sha256'])
    if _uint(value['bytes'],cap)!=len(raw): raise ValueError('comparison blob length differs')
    return raw


def _inventory(rows: Any, archive: dict) -> list[dict]:
    if type(rows) is not list or not rows or len(rows)>4096: raise ValueError('bounded candidate inventory required')
    total=0;paths=set()
    for row in rows:
        _closed(row,{'path','sha256','bytes'});path=n._path(row['path'])
        raw=_blob({k:row[k] for k in ('sha256','bytes')},archive,256*MIB);total+=len(raw)
        if path in paths or total>256*MIB: raise ValueError('unique bounded candidate inventory required')
        paths.add(path)
    return rows


def admit_slot(*, elapsed_ns: int, slots_used: int, retained_bytes: int, reserve_bytes: int) -> None:
    """Conservative admission, never renews the original suite or target deadline."""
    _uint(elapsed_ns);_uint(slots_used,52);_uint(retained_bytes,MAX_SUITE_BYTES);_uint(reserve_bytes,MAX_SUITE_BYTES)
    if slots_used>=52 or elapsed_ns+(SLOT_SECONDS+600)*10**9>B_SECONDS*10**9 or retained_bytes+MAX_CAPTURE_BYTES+FAILURE_RESERVE+reserve_bytes>MAX_SUITE_BYTES:
        raise ValueError('original comparison suite budget/capacity exhausted')


def _guard_callback(*args: Any) -> None:
    pass


def _guard() -> Any:
    policy={'purpose':'TEST_ONLY','allowed_transforms':[],'reviewer_id':'comparison-source-binding','reviewer_role':'source-binding-only'}
    return sm.MetadataAuthority.freeze('comparison-source-guard','comparison-source-bindings','1',sm.sha256(sm.canonical(policy)),_guard_callback,_guard_callback,policy=policy,helper_modules=(sys.modules[__name__],n,migration,bridge,origin))


def capture_baseline(authority: ComparisonCaptureAuthority, plan: dict, artifacts: dict) -> ComparisonCompletion:
    if type(authority) is not ComparisonCaptureAuthority: raise ValueError('private comparison authority required')
    return _capture_baseline(authority,plan,artifacts)


def _stdio_snapshot(rows: Any) -> None:
    if type(rows) is not list or len(rows)!=3: raise ValueError('only original inherited FD0-2 required')
    for fd,row in enumerate(rows):
        _closed(row,{'fd','kind','identity'})
        if type(row['fd']) is not int or row['fd']!=fd or row['kind']!=('stdin','stdout','stderr')[fd] or type(row['identity']) is not list or len(row['identity'])!=2: raise ValueError('original stdio descriptor differs')
        for value in row['identity']: _uint(value)
    if len({tuple(row['identity']) for row in rows})!=3: raise ValueError('distinct original stdio pipes required')


def _clock(run: dict, events: list[dict]) -> None:
    _closed(run,{'started_at','ended_at','monotonic_start_ns','elapsed_ns','wall_deadline_ns','cleanup_started_ns','cleanup_deadline_ns'})
    for key in ('monotonic_start_ns','elapsed_ns','wall_deadline_ns','cleanup_started_ns','cleanup_deadline_ns'): _uint(run[key])
    start=run['monotonic_start_ns'];elapsed=run['elapsed_ns'];cleanup=run['cleanup_started_ns']
    if run['wall_deadline_ns']!=start+120*10**9 or elapsed>120*10**9 or not start<=cleanup<=start+elapsed or run['cleanup_deadline_ns']!=min(cleanup+2*10**9,start+122*10**9): raise ValueError('original comparison deadline differs')
    duration=(sm._instant(run['ended_at'])-sm._instant(run['started_at'])).total_seconds()
    if duration<0 or abs(duration-elapsed/10**9)>.01 or events[-1]['at_ns']!=elapsed: raise ValueError('comparison clock interval differs')
    terminal=events[-1]['data'];wait=terminal['wait'];n._validate_wait(wait,terminal['returncode'],success=True)
    exit_at=next(row['at_ns'] for row in events if row['kind']=='exit-stop')
    if not exit_at<=wait['observed_at_ns']<=cleanup-start or wait['observed_at_ns']>elapsed: raise ValueError('wait outside checked exit/cleanup interval')
    custody=terminal['custody'];n.validate_native_custody(custody,pid=events[0]['data']['pid'],reaped=terminal['reaped'])
    if abs(custody['grace_deadline']-run['cleanup_deadline_ns']/10**9)>.000001 or custody['cleanup_ended']>start/10**9+elapsed/10**9 or custody['signals']: raise ValueError('comparison custody/cleanup clock differs')


def check_comparison_events(observation: dict, artifacts: dict[str,bytes], *, observation_mode: str) -> dict:
    """Pure two-channel DATA replay. Does not acquire, issue or adopt native state."""
    _closed(observation,{'schema','scope','purpose','spec','files','events','platform','host_policy_sha256','run'})
    if observation['schema']!='TEST_ONLY-pdf-baseline-events/v1' or observation['scope']!=DATA_SCOPE or observation['purpose']!='TEST_ONLY' or observation_mode not in ('actual','SIMULATED_DATA'): raise ValueError('comparison DATA observation scope differs')
    spec=observation['spec'];_closed(spec,{'schema','purpose','profile','plan_sha256','argv','environment','cwd','limits','candidates'})
    if spec['schema']!='TEST_ONLY-pdf-baseline-spec/v1' or spec['purpose']!='TEST_ONLY' or spec['profile']!=DATA_SCOPE or spec['limits']!=LIMITS or any(type(v) is not int for v in spec['limits'].values()): raise ValueError('fixed comparison spec differs')
    _hash(spec['plan_sha256'])
    if observation_mode=='SIMULATED_DATA' and observation['host_policy_sha256'] is not None: raise ValueError('simulated DATA cannot claim actual H')
    if observation_mode=='actual': _raw(artifacts,observation['host_policy_sha256'])
    events=observation['events']
    if type(events) is not list or not events or len(events)>1000000 or len(sm.canonical(events))>64*MIB: raise ValueError('comparison event cap')
    if events[0].get('kind')!='start' or events[-1].get('kind')!='terminal': raise ValueError('complete comparison lifetime required')
    initial=events[0]['data']['fds'];_stdio_snapshot(initial)
    pending=None;closed=set();provisional=set();eof={};exit_seen=False;previous=-1
    projected: list[dict]=[];buffer_pins=set()
    for seq,row in enumerate(events):
        _closed(row,{'seq','at_ns','kind','data'})
        if type(row['seq']) is not int or row['seq']!=seq or _uint(row['at_ns'])<previous or row['at_ns']>120*10**9: raise ValueError('comparison event ordering differs')
        previous=row['at_ns'];kind=row['kind'];data=row['data'];copied=copy.deepcopy(row)
        if kind=='enter':
            if pending is not None: raise ValueError('comparison pending syscall differs')
            nr=data['nr'];args=data['args'];name=n.SYSCALLS.get(str(nr))
            if name in ('dup','dup2','dup3') or name=='fcntl' and args[1] in (0,1030): raise ValueError('comparison stream aliases unsupported')
            if name in ('open','openat'):
                flags=args[1] if name=='open' else args[2]
                if flags&(3|0x40|0x80|0x200|0x400): raise ValueError('comparison writable resource/sidecar forbidden')
            if name in ('write','writev'):
                if args[0] not in (1,2): raise ValueError('only original comparison stdout/stderr writes')
                buffer_pins.add(data['detail']['buffer_sha256'])
            if 'buffer_sha256' in data['detail']:buffer_pins.add(data['detail']['buffer_sha256'])
            pending=(name,args)
        elif kind=='leave':
            if pending is None: raise ValueError('comparison leave without entry')
            name,args=pending
            if name=='close':
                if data['result']==0:closed.add(args[0]);provisional.discard(args[0])
                elif args[0] in provisional:raise ValueError('provisional EOF close failed')
            if name in ('open','openat') and 0<=data['result']<=2: raise ValueError('original comparison descriptor replaced')
            if 'buffer_sha256' in data['detail']:buffer_pins.add(data['detail']['buffer_sha256'])
            pending=None
        elif kind=='exec':
            if data.get('fds')!=initial: raise ValueError('comparison original channels changed across exec')
            copied['data'].pop('fds')
        elif kind=='exit-stop':exit_seen=True;pending=None
        elif kind=='pipe-eof':
            _closed(data,{'channel','fd','generation','identity','request_bytes','result','captured_bytes'})
            channel=data['channel'];fd={'stdout':1,'stderr':2}.get(channel)
            if fd is None or channel in eof or type(data['fd']) is not int or data['fd']!=fd or _uint(data['generation'],0)!=0 or data['identity']!=initial[fd]['identity'] or not 1<=_uint(data['request_bytes'],65536) or _uint(data['result'],0)!=0: raise ValueError('original positive-capacity comparison EOF differs')
            _uint(data['captured_bytes'],LIMITS[channel+'_bytes'])
            if not exit_seen and fd not in closed:
                if pending is None or pending[0]!='close' or pending[1][0]!=fd:raise ValueError('comparison EOF before checked closure')
                provisional.add(fd)
            eof[channel]=data
            continue
        elif kind=='terminal':
            if seq!=len(events)-1 or provisional or set(eof)!={'stdout','stderr'}: raise ValueError('complete original comparison EOF required')
            _closed(data,{'returncode','stdout_sha256','stderr_sha256','sidecars','eof','reaped','cleanup','custody','wait'})
            for channel in ('stdout','stderr'):
                raw=_raw(artifacts,data[channel+'_sha256']);buffer_pins.add(data[channel+'_sha256'])
                if len(raw)!=eof[channel]['captured_bytes']:raise ValueError('comparison EOF stream length differs')
            copied['data'].pop('wait')
        copied['seq']=len(projected);projected.append(copied)
    if sum(len(_raw(artifacts,pin)) for pin in buffer_pins)>MAX_BUFFER_BYTES:raise ValueError('comparison retained buffer cap')
    _clock(observation['run'],events)
    if observation_mode=='actual':
        policy=_json(artifacts,observation['host_policy_sha256']);run=observation['run']
        before=sm._instant(policy['not_before']);after=sm._instant(policy['not_after'])
        if not 0<(after-before).total_seconds()<=300 or not before<=sm._instant(run['started_at'])<=sm._instant(run['ended_at'])<after:raise ValueError('actual comparative host interval differs')
    # This is only common pure file/map/syscall replay. The projected value never
    # enters a native store/issuer and is not exported as a native observation.
    common=copy.deepcopy(observation);common.pop('run');common.update(schema='twin.native-file-observation/v1',scope=n.SCOPE,purpose='actual' if observation_mode=='actual' else 'TEST_ONLY',events=projected)
    common['spec'].update(schema='twin.native-observation-spec/v1',purpose=common['purpose'],profile='pdf-text-xpdf/1')
    summary=n.verify_native_observation(common,artifacts,purpose=common['purpose'])
    return {'scope':DATA_SCOPE,'observation_mode':observation_mode,'stdout_bytes':summary['stdout_bytes'],'stderr_bytes':summary['stderr_bytes'],'qualification':'NONE'}


FIXTURES=(('01-one-fragment', 'cb396869f51d2b95da6a171c68089fac989d6b927d97ed5ac53ea1014a898101', 861), ('02-literal-space', 'a80caf1663a591828f7ff0321be3a050eabc1edfb78c5e8c7c33924b635ecf6b', 863), ('03-geometric-space', '9fc1b0a274d5f7c7a61e8a1ad05b1088c8905962def5355a236dcf7995ac2546', 891), ('04-separate-Tj', 'ce1fb6a8c4d49c44b85a2b92491ff543d84011c899c1a67a1c7a9ca51e21ff9d', 866), ('05-TJ-operands', '0e6b3b8721888f936880dd654957aa45f95e745267775c17848e69957cfcf2b5', 867), ('06-line-join', '4cb34f9909476a0107cb20ab97cd83bba70fb01e7e7db72b42a5c8f3dfcb9e4b', 873), ('07-page-join', 'ef0143e41818a0ae69b6c817cd2d2611f2a15e72c6794f4b4b9858d79498f293', 1120), ('08-hyphen-line', 'a28ffd6ae3f704a89c058d067ae21495dd87d3ca32d054bd911ef437bb138ad4', 876), ('09-column-order', '6f2628ad1651b1ac02734b80f3957daac806d762b2cff7dc9b558ce8908f22b3', 938), ('10-duplicate-paint', '16cfe12c88cb94601e9c270ed713913488a012c75eba517ec40843ca5f4127a0', 890), ('11-overlap-paint', '38450c1c211ef7cff9292353637149c87f5fe58539fe836de316c113a067fd59', 886), ('12-reversed-paint', '393269606c3b223c3a502541af804cdb657508b5ddf83a86392dd6d05d4dc64e', 891), ('13-one-to-many', '9e7a96f80dea93b5222359b4b289318044d30d82228539f44b55255457cf86b4', 1280), ('14-multibyte-scalars', '8862d44ae4fdb7d8d301d2d443b5660385b1d842a6846b02f7d58974aa363948', 1300), ('15-bidi-brackets', '24e1e4fb2e6402896acc38ab70978d8a4c731110be57ec7e5bec7687214170da', 1320), ('16-ActualText', 'cf6866bc9e9c96fcb3b0d49e2097fdaad3e77943b8d6bf54112b104880354011', 906), ('17-repeated-form', '0a2c2ba1f4c2fdb13cf246aeb8a6c2677aad1cc1591ecad9d0903ba615bdb2fb', 1102), ('18-Type3-neighbor', 'c4bdad5403f402474da90b18fa99c8ec088fcca4ff66afdaf5486230935ae581', 1533))


def _pair_plan(pair: dict, archive: dict) -> None:
    _closed(pair,{'schema','purpose','fixture_id','fixture','config','resource','archive_sha256','patch_sha256','build_pair','schedule_index','suite_selection_sha256'})
    if pair['schema']!='TEST_ONLY-pdf-pair-plan/v1' or pair['purpose']!='TEST_ONLY' or pair['archive_sha256']!=ARCHIVE or pair['patch_sha256']!=PATCH:raise ValueError('fixed comparison pair selection differs')
    index=_uint(pair['schedule_index'],20);expected=FIXTURES[index if index<18 else 0]
    if pair['fixture_id']!=expected[0] or pair['fixture']!={'sha256':expected[1],'bytes':expected[2]}: raise ValueError('fixed public synthetic fixture differs')
    _blob(pair['fixture'],archive,256*MIB);_blob(pair['config'],archive,MIB);_hash(pair['suite_selection_sha256'])
    resource=pair['resource']
    if index<18:
        if resource is not None: raise ValueError('ordinary baseline config cannot select remap resource')
    else:
        _closed(resource,{'relative_path','blob'})
        if resource['relative_path']!='TEST_ONLY-remap.txt' or _blob(resource['blob'],archive,MIB)!=(b'0041 0041\n',b'0041 0042\n',b'0041 0041 0042\n')[index-18] or _blob(pair['config'],archive,MIB)!=b'unicodeRemapping TEST_ONLY-remap.txt\n':raise ValueError('fixed remap bytes differ')
    build=pair['build_pair'];_closed(build,{'pristine_build_sha256','patched_build_sha256','pristine_executable','patched_executable','same_toolchain_recipe_sha256','accepted_differences_sha256'})
    left=_json(archive,build['pristine_build_sha256'])
    _closed(left,{'schema','variant','source_archive_sha256','patch_sha256','prepared_tree_sha256','toolchain_recipe_sha256','configuration_recipe_sha256','executable','dependency_inventory_sha256'})
    if left['schema']!='TEST_ONLY-pdf-comparison-build-selection/v1' or left['variant']!='pristine' or left['source_archive_sha256']!=ARCHIVE or left['patch_sha256'] is not None or left['executable']!=build['pristine_executable'] or left['toolchain_recipe_sha256']!=build['same_toolchain_recipe_sha256']:raise ValueError('selected pristine build association differs')
    _hash(left['prepared_tree_sha256']);_raw(archive,left['toolchain_recipe_sha256']);_raw(archive,left['configuration_recipe_sha256'])
    n.elf_interpreter(_blob(left['executable'],archive,256*MIB))
    _inventory(sm._json(_raw(archive,left['dependency_inventory_sha256'])),archive)
    right=_json(archive,build['patched_build_sha256']);_closed(right,bridge.BUILD_KEYS)
    if right['schema']!='twin.native-build-identity/v1' or right['source_archive_sha256']!=ARCHIVE or right['patch_sha256']!=PATCH or right['target']!={'system':'Linux','machine':'x86_64','elf_class':64} or right['toolchain_sha256']!=build['same_toolchain_recipe_sha256'] or right['build_configuration_sha256']!=left['configuration_recipe_sha256'] or build['patched_executable']!={'sha256':right['executable_sha256'],'bytes':right['executable_bytes']}:raise ValueError('selected patched build association differs')
    _closed(right['target'],{'system','machine','elf_class'})
    if type(right['target']['elf_class']) is not int:raise ValueError('exact paired target ABI required')
    n.elf_interpreter(_blob(build['patched_executable'],archive,256*MIB))
    for key in ('source_package_sha256','prepared_tree_sha256','build_configuration_sha256','toolchain_sha256','build_log_sha256'):_raw(archive,right[key])
    _raw(archive,build['accepted_differences_sha256'])


def _reconcile_build_candidates(pair: dict, rows: list[dict], archive: dict) -> None:
    build=_json(archive,pair['build_pair']['pristine_build_sha256'])
    selected=_inventory(sm._json(_raw(archive,build['dependency_inventory_sha256'])),archive)
    if {row['path']:(row['sha256'],row['bytes']) for row in rows}!={row['path']:(row['sha256'],row['bytes']) for row in selected}:
        raise ValueError('pristine build dependency selection differs')


def prepare_comparison_plan(pair_selection: dict, fixture_bytes: bytes, retained_build_and_config_bytes: dict[str,bytes], *, executable_path: str, candidate_inventory: list[dict], recorder_inventory: list[dict]) -> dict:
    """Pure preparation; retained hashes describe selection, never approve a host."""
    archive=dict(retained_build_and_config_bytes);pair=copy.deepcopy(pair_selection)
    _pair_plan(pair,archive)
    if type(fixture_bytes) is not bytes or fixture_bytes!=_blob(pair['fixture'],archive,256*MIB):raise ValueError('frozen comparison fixture bytes differ')
    rows=_inventory(candidate_inventory,archive);drivers=_inventory(recorder_inventory,archive)
    _reconcile_build_candidates(pair,rows,archive)
    executable=n._path(executable_path)
    row=next((r for r in rows if r['path']==executable),None)
    if row is None or {k:row[k] for k in ('sha256','bytes')}!=pair['build_pair']['pristine_executable']:raise ValueError('selected pristine executable differs')
    plan={'schema':'TEST_ONLY-pdf-baseline-plan/v1','purpose':'TEST_ONLY','capture_kind':'pristine-comparative-data','pair_plan_sha256':_record(archive,pair),'fixture':copy.deepcopy(pair['fixture']),'config':copy.deepcopy(pair['config']),'resource':copy.deepcopy(pair['resource']),'build_identity_sha256':pair['build_pair']['pristine_build_sha256'],'executable_path':executable,'executable':copy.deepcopy(pair['build_pair']['pristine_executable']),'candidate_inventory_sha256':_put(archive,sm.canonical(rows)),'recorder_inventory_sha256':_put(archive,sm.canonical(drivers)),'limits_sha256':_record(archive,LIMITS),'schedule_index':2*pair['schedule_index']}
    return {'plan':plan,'archive':archive}


def _plan(plan: dict, archive: dict) -> dict:
    _closed(plan,{'schema','purpose','capture_kind','pair_plan_sha256','fixture','config','resource','build_identity_sha256','executable_path','executable','candidate_inventory_sha256','recorder_inventory_sha256','limits_sha256','schedule_index'})
    pair=_json(archive,plan['pair_plan_sha256']);_pair_plan(pair,archive)
    if plan['schema']!='TEST_ONLY-pdf-baseline-plan/v1' or plan['purpose']!='TEST_ONLY' or plan['capture_kind']!='pristine-comparative-data' or plan['fixture']!=pair['fixture'] or plan['config']!=pair['config'] or plan['resource']!=pair['resource'] or plan['build_identity_sha256']!=pair['build_pair']['pristine_build_sha256'] or plan['executable']!=pair['build_pair']['pristine_executable'] or type(plan['schedule_index']) is not int or plan['schedule_index']!=2*pair['schedule_index']:raise ValueError('frozen baseline plan differs')
    if _json(archive,plan['limits_sha256'])!=LIMITS:raise ValueError('comparison limits differ')
    rows=_inventory(sm._json(_raw(archive,plan['candidate_inventory_sha256'])),archive)
    _reconcile_build_candidates(pair,rows,archive)
    _inventory(sm._json(_raw(archive,plan['recorder_inventory_sha256'])),archive)
    path=n._path(plan['executable_path']);row=next((r for r in rows if r['path']==path),None)
    if row is None or {k:row[k] for k in ('sha256','bytes')}!=plan['executable']:raise ValueError('pristine candidate executable differs')
    return pair


def freeze_comparison_authority(context: n.NativeHostContext, plan: dict, archive: dict, *, session: ComparisonSession) -> ComparisonCaptureAuthority:
    """Conserve an independent custodian selection; this does not select/approve H.

    No deployment selector is installed. A trusted caller must independently obtain
    the exact private native context and build/config evidence before using this.
    """
    if type(context) is not n.NativeHostContext or type(session) is not ComparisonSession:raise ValueError('private independent actual host context/session required')
    _check_original_suite(session)
    if session._stopped or session._awaiting_comparison or session._active_slot is not None or session._target_custody_known is not True:raise ValueError('comparison suite stopped or awaiting first-pair review')
    suite_started_monotonic=session._started;slots_used=session._next;retained_bytes=session._retained;reserve_bytes=session._reserve
    context._guard.verify();pair=_plan(plan,archive);policy=n._host_window(context)
    if (sm._instant(policy['not_after'])-sm._instant(policy['not_before'])).total_seconds()>300:raise ValueError('comparison H interval exceeds300s')
    for pin in (plan['build_identity_sha256'],pair['build_pair']['patched_build_sha256'],plan['config']['sha256'],pair['suite_selection_sha256']):
        if pin not in policy['evidence_sha256s'] or _raw(context._evidence,pin)!=_raw(archive,pin):raise ValueError('independent build/config/suite selection absent')
    if pair['suite_selection_sha256']!=session._selection or plan['schedule_index']!=session._next-session._next%2:raise ValueError('preselected suite/order differs')
    if plan['resource'] is not None:raise ValueError('remap staging/observed-read contract remains held')
    if type(suite_started_monotonic) not in (int,float) or not 0<=suite_started_monotonic<=time.monotonic():raise ValueError('original suite start required')
    admit_slot(elapsed_ns=int((time.monotonic()-suite_started_monotonic)*10**9),slots_used=slots_used,retained_bytes=retained_bytes,reserve_bytes=reserve_bytes)
    authority=object.__new__(ComparisonCaptureAuthority)
    for key,value in {'_context':context,'_guard':_guard(),'_pair':sm.canonical(pair),'_archive':dict(archive),'_selected_at':time.monotonic(),'_spent':False,'_suite_started':suite_started_monotonic,'_slots_used':slots_used,'_retained_bytes':retained_bytes,'_reserve_bytes':reserve_bytes,'_plan':sm.canonical(plan),'_session':session,'_slot':session._next}.items():object.__setattr__(authority,key,value)
    return authority


def _comparison_admit(nr: int, args: list[int], detail: dict, spec: dict, fds: dict, created: set, executed: bool, *, maps: list[dict] | None=None) -> str:
    name=n._admit(nr,args,detail,spec,fds,created,executed,maps=maps)
    if name in ('dup','dup2','dup3') or name=='fcntl' and args[1] in (0,1030):raise ValueError('comparison aliases forbidden')
    if name in ('open','openat'):
        flags=args[1] if name=='open' else args[2]
        if flags&(3|0x40|0x80|0x200|0x400):raise ValueError('comparison resource writes forbidden')
        if not set(range(3))<=set(fds):raise ValueError('closed original stdio cannot be replaced')
    if name in ('write','writev') and (args[0] not in (1,2) or fds[args[0]]['generation']!=0):raise ValueError('only original comparison output writes allowed')
    return name


def _comparison_snapshot(proc: Path, records: dict[int,dict]) -> list[dict]:
    snapshot=n._fd_snapshot(proc,records);_stdio_snapshot(snapshot)
    for row in snapshot:
        fd=row['fd'];info=(proc/'fd'/str(fd)).stat()
        lines=(proc/'fdinfo'/str(fd)).read_text().splitlines()
        flags=[int(line.split(':',1)[1].strip(),8) for line in lines if line.startswith('flags:')]
        if len(flags)!=1 or flags[0]&os.O_ACCMODE!=(os.O_RDONLY if fd==0 else os.O_WRONLY) or flags[0]&os.O_CLOEXEC or not stat.S_ISFIFO(info.st_mode):raise ValueError('original actual comparison pipe required')
    return snapshot


def _linux_run_comparison(authority: ComparisonCaptureAuthority, spec: dict, artifacts: dict) -> dict:
    """Real kernel route, never called by TEST_ONLY injection/replay tests."""
    if type(authority) is not ComparisonCaptureAuthority or authority._context is None:
        raise ValueError('actual private host context required')
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise ValueError('unsupported-native-observer-platform')
    authority._guard.verify()
    policy = n._host_window(authority._context)
    if len(list(Path('/proc/self/task').iterdir())) != 1:
        raise ValueError('single-threaded native recorder required')
    n._put(artifacts, authority._context._policy)
    artifacts.update(authority._context._evidence)
    held, candidate_facts = n._acquire_candidates(spec, artifacts, authority._context, preparation_deadline=min(authority._selected_at+60,authority._suite_started+B_SECONDS))
    if time.monotonic() - authority._selected_at > 60:
        for fd in held.values():
            os.close(fd)
        raise ValueError('original comparison preparation deadline')
    budget = {'bytes': 0, 'limit': MAX_BUFFER_BYTES}
    events: list[dict] = []
    native_wait = None
    native_terminal = None
    used_files: dict[str, dict] = {}
    records: dict[int, dict] = {}
    created: set[str] = set()
    outputs: dict[str, bytearray] = {}
    acquired: list[int] = []
    generations = {0: 0, 1: 0, 2: 0}
    current_maps: list[dict] = []
    pending = None
    executed = False
    exit_stop = False
    pid = None
    mem = -1
    procfd = -1
    failure = None
    returncode = None
    reaped = []
    interruption = None
    descendants: set[int] = set()
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    observed_streams = {'stdout': 0, 'stderr': 0}
    write_totals = {'stdout': 0, 'stderr': 0}
    eof = []
    pipes = []
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    event_budget = {'bytes': 2}
    start_ns = int(start * 10 ** 9)
    with selectors.DefaultSelector() as selector:
        try:
            input_read, input_write = os.pipe2(os.O_CLOEXEC)
            os.close(input_write)
            out_read, out_write = os.pipe2(os.O_CLOEXEC)
            err_read, err_write = os.pipe2(os.O_CLOEXEC)
            pipes = [input_read, out_read, out_write, err_read, err_write]
            n._check_preparation_deadline(min(authority._selected_at+60,authority._suite_started+B_SECONDS))
            pid = os.fork()
            if pid == 0:
                try:
                    os.setsid()
                    os.umask(63)
                    os.chdir(spec['cwd'])
                    n._install_child_channels([input_read, out_write, err_write] + [])
                    n._ptrace(0, 0)
                    os.kill(os.getpid(), signal.SIGSTOP)
                    os.execve(spec['argv'][0], spec['argv'], spec['environment'])
                except BaseException:
                    os._exit(127)
            os.close(input_read)
            os.close(out_write)
            os.close(err_write)
            pipes = [out_read, err_read]
            stream_fds = [(out_read, 'stdout'), (err_read, 'stderr')]
            for fd, name in stream_fds:
                os.set_blocking(fd, False)
                selector.register(fd, selectors.EVENT_READ, name)
            got, status = (0, 0)
            while not got and time.monotonic() - start < spec['limits']['wall_seconds']:
                got, status = os.waitpid(pid, os.WNOHANG | os.WUNTRACED)
                if not got:
                    time.sleep(0.001)
            if got == pid and (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                returncode = os.waitstatus_to_exitcode(status)
                reaped.append(pid)
                native_wait = n._wait_record(status, int((time.monotonic() - start) * 10 ** 9))
            if got != pid or not os.WIFSTOPPED(status) or os.WSTOPSIG(status) != signal.SIGSTOP:
                raise ValueError('initial native pre-exec stop missing')
            n._ptrace(16896, pid, 0, n.OPTIONS)
            proc = Path('/proc') / str(pid)
            procfd = os.open(proc, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
            mem = os.open(proc / 'mem', os.O_RDONLY | os.O_CLOEXEC)
            lifetime = n._lifetime(proc)
            if lifetime['ppid'] != os.getpid() or lifetime['uid'] != os.getuid() or lifetime['gid'] != os.getgid():
                raise ValueError('owned native lifetime differs')
            for fd, name in enumerate(('stdin', 'stdout', 'stderr')):
                info = (proc / 'fd' / str(fd)).stat()
                records[fd] = {'kind': name, 'identity': [info.st_dev, info.st_ino], 'generation': 0}
            initial = _comparison_snapshot(proc, records)
            n._append(events, 'start', {**lifetime, 'fds': initial}, start, spec['limits'], budget=event_budget)
            n._ptrace(24, pid)
            while returncode is None or selector.get_map():
                if time.monotonic() - start >= spec['limits']['wall_seconds']:
                    raise ValueError('native observation deadline')
                n._host_window(authority._context, verify_guard=False)
                for key, _ in selector.select(0.001):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fd)
                        eof.append(key.data)
                        if True:
                            number = {'stdout': 1, 'stderr': 2}[key.data]
                            n._append(events, 'pipe-eof', {'channel': key.data, 'fd': number, 'generation': 0, 'identity': initial[number]['identity'], 'request_bytes': 65536, 'result': 0, 'captured_bytes': len(streams[key.data])}, start, spec['limits'], budget=event_budget)
                        continue
                    observed_streams[key.data] += len(chunk)
                    remaining = n._channel_cap(spec, key.data) - len(streams[key.data])
                    streams[key.data].extend(chunk[:max(0, remaining)])
                    if observed_streams[key.data] > n._channel_cap(spec, key.data):
                        raise ValueError('native stream overflow')
                if returncode is not None:
                    continue
                got, status = os.waitpid(pid, os.WNOHANG | os.WUNTRACED)
                if not got:
                    continue
                if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                    returncode = os.waitstatus_to_exitcode(status)
                    reaped.append(pid)
                    native_wait = n._wait_record(status, int((time.monotonic() - start) * 10 ** 9))
                    if returncode or not exit_stop:
                        raise ValueError('native early/nonzero death')
                    continue
                if not os.WIFSTOPPED(status):
                    raise ValueError('unknown native wait status')
                stop_signal = os.WSTOPSIG(status)
                event = status >> 16
                if n._lifetime(proc) != lifetime:
                    raise ValueError('native lifetime/credential drift')
                if event == 4:
                    if pending is None or pending['name'] != 'execve' or executed:
                        raise ValueError('unexpected native exec')
                    os.close(mem)
                    mem = os.open(proc / 'mem', os.O_RDONLY | os.O_CLOEXEC)
                    maps = n._maps(proc)
                    current_maps = n._map_rows(maps, candidate_facts)
                    executable = os.path.realpath(proc / 'exe')
                    for row in maps:
                        path = row['path']
                        if path and path.startswith('/'):
                            if path not in candidate_facts:
                                raise ValueError('native startup dependency unretained')
                            info = Path(path).stat()
                            if [info.st_dev, info.st_ino] != row['identity']:
                                raise ValueError('native executable map identity differs')
                            used_files[path] = candidate_facts[path]
                    interpreter = n.elf_interpreter(n._raw(artifacts, used_files[executable]['sha256']))
                    actual_interpreter, interpreter_links = n._observe_open_route(interpreter) if interpreter else (None, [])
                    interpreter_route = {'path': actual_interpreter, **({'requested_path': interpreter, 'route': interpreter_links} if interpreter_links else {})} if interpreter else None
                    n._append(events, 'exec', {'maps': maps, 'executable': executable, 'credentials': [lifetime['uid'], lifetime['gid']], 'interpreter': actual_interpreter, 'interpreter_route': interpreter_route, **{'fds': _comparison_snapshot(proc, records)}}, start, spec['limits'], budget=event_budget)
                    executed = True
                elif event == 6:
                    if pending is None or pending['name'] not in ('exit', 'exit_group'):
                        raise ValueError('unexplained native exit-stop')
                    n._append(events, 'exit-stop', {'status': pending['args'][0], 'maps': n._maps(proc), 'fds': n._fd_snapshot(proc, records), 'pid': pid, 'starttime': lifetime['starttime']}, start, spec['limits'], budget=event_budget)
                    exit_stop = True
                    pending = None
                elif event in (1, 2, 3):
                    child_buffer = ctypes.c_ulonglong()
                    n._ptrace(16897, pid, 0, ctypes.addressof(child_buffer))
                    if child_buffer.value > 0 and child_buffer.value != pid:
                        descendants.add(child_buffer.value)
                    raise ValueError('unexpected native owned descendant')
                elif event:
                    raise ValueError('unsupported native process/ptrace event')
                elif stop_signal == signal.SIGTRAP | 128:
                    stop = n._syscall_stop(pid)
                    if stop['op'] == 'enter':
                        if pending is not None:
                            raise ValueError('native entry/leave gap')
                        detail = n._entry_detail(stop, mem, proc, artifacts, budget)
                        name = _comparison_admit(stop['nr'], stop['args'], detail, spec, records, created, executed, maps=current_maps)
                        if 'path' in detail and detail['path'] != '/proc/self/exe' and (not n._inside(detail['path'], policy['roots'])) and (not detail['path'].startswith(spec['cwd'] + '/')):
                            raise ValueError('native lookup outside selected host roots')
                        if name in ('open', 'openat'):
                            path = detail['path']
                            side = path in (spec['cwd'] + '/runtime', spec['cwd'] + '/syntax') and spec['profile'] not in ('pdf-text-xpdf/1', 'pdf-text-xpdf-origin/2')
                            if side:
                                if os.path.lexists(path):
                                    raise ValueError('preexisting native output')
                            elif os.path.lexists(path):
                                canonical = os.path.realpath(path)
                                if canonical != path:
                                    raise ValueError('native observed route changed before open')
                                info = Path(path).stat()
                                if path not in candidate_facts and (not (stat.S_ISDIR(info.st_mode) and path in {str(Path(p).parent) for p in candidate_facts})):
                                    raise ValueError('native dependency unretained before exposure')
                            elif not n._inside(path, policy['roots']) and (not path.startswith(spec['cwd'] + '/')):
                                raise ValueError('native lookup outside selected host roots')
                        if name in ('write', 'writev'):
                            record = records[stop['args'][0]]
                            requested = n._raw(artifacts, detail['buffer_sha256'])
                            path = record['description']['path'] if record['kind'] == 'sidecar' else record['kind']
                            total = len(outputs[path]) if record['kind'] == 'sidecar' else write_totals[path]
                            cap = n._channel_cap(spec, path)
                            if total + len(requested) > cap:
                                raise ValueError('native requested write exceeds owned-output cap')
                        pending = {**stop, 'name': name, 'detail': detail}
                        if name in ('read', 'readv') and records[stop['args'][0]]['kind'] == 'file':
                            pending['offset'] = records[stop['args'][0]]['description']['offset']
                        n._append(events, 'enter', {'nr': stop['nr'], 'args': stop['args'], 'detail': detail}, start, spec['limits'], budget=event_budget)
                    else:
                        if pending is None:
                            raise ValueError('native leave without entry')
                        result = stop['result']
                        name = pending['name']
                        a = pending['args']
                        detail = {}
                        if name in ('open', 'openat') and result >= 0:
                            path = pending['detail']['path']
                            info = (proc / 'fd' / str(result)).stat()
                            identity = n._identity(info)
                            actual_path = os.readlink(proc / 'fd' / str(result))
                            if actual_path != path:
                                raise ValueError('actual opened native path differs')
                            side = path in (spec['cwd'] + '/runtime', spec['cwd'] + '/syntax') and spec['profile'] not in ('pdf-text-xpdf/1', 'pdf-text-xpdf-origin/2')
                            kind = 'sidecar' if side else 'directory' if stat.S_ISDIR(info.st_mode) else 'file'
                            if side:
                                if identity[2] != 33152 or identity[3] != lifetime['uid'] or identity[5] != 1 or (identity[6] != 0):
                                    raise ValueError('actual sidecar creation differs')
                                created.add(path)
                                outputs[path] = bytearray()
                            elif kind == 'file':
                                fd = os.open(proc / 'fd' / str(result), os.O_RDONLY | os.O_CLOEXEC)
                                acquired.append(fd)
                                if len(acquired) + len(held) > n.MAX_FILES:
                                    raise ValueError('native retained FD limit')
                                raw = n._read_fd(fd, n.MAX_DEPENDENCY_BYTES)
                                if n._identity(os.fstat(fd)) != identity or path not in candidate_facts or identity != candidate_facts[path]['identity'] or (raw != n._raw(artifacts, candidate_facts[path]['sha256'])):
                                    raise ValueError('actual native FD acquisition differs')
                                used_files[path] = candidate_facts[path]
                            elif kind == 'directory':
                                if not stat.S_ISDIR(info.st_mode):
                                    raise ValueError('native directory required')
                            generations[result] = generations.get(result, -1) + 1
                            records[result] = {'kind': kind, 'identity': identity[:2], 'generation': generations[result], 'description': {'path': path, 'offset': 0, 'identity': identity}}
                            detail = {'kind': kind, 'identity': identity}
                        elif name in ('read', 'pread64', 'readv'):
                            raw = n._result_buffer(pending, result, mem)
                            detail = {'buffer_sha256': sm.sha256(raw), 'buffer_bytes': len(raw)}
                            record = records[a[0]]
                            if result >= 0:
                                if record['kind'] == 'stdin':
                                    if result:
                                        raise ValueError('owned stdin is not EOF')
                                else:
                                    desc = record['description']
                                    offset = a[3] if name == 'pread64' else desc['offset']
                                    expected = os.pread(held[desc['path']], result, offset)
                                    if raw != expected:
                                        raise ValueError('actual native read differs')
                                    if name != 'pread64':
                                        desc['offset'] += result
                        elif name in ('write', 'writev') and result >= 0:
                            raw = n._raw(artifacts, pending['detail']['buffer_sha256'])
                            if result > len(raw):
                                raise ValueError('native partial write differs')
                            record = records[a[0]]
                            if record['kind'] == 'sidecar':
                                path = record['description']['path']
                                outputs[path].extend(raw[:result])
                                cap = n.RUNTIME_BYTES if path.endswith('/runtime') else spec['limits']['syntax_bytes']
                                if len(outputs[path]) > cap:
                                    raise ValueError('native sidecar overflow')
                            else:
                                write_totals[record['kind']] += result
                        elif name == 'close' and result == 0:
                            del records[a[0]]
                        elif name in ('dup', 'dup2', 'dup3') and result >= 0:
                            if result != a[0]:
                                generations[result] = generations.get(result, -1) + 1
                                records[result] = {**records[a[0]], 'generation': generations[result]}
                        elif name == 'fcntl' and a[1] in (0, 1030) and (result >= 0):
                            generations[result] = generations.get(result, -1) + 1
                            records[result] = {**records[a[0]], 'generation': generations[result]}
                        elif name == 'lseek' and result >= 0:
                            records[a[0]]['description']['offset'] = result
                        elif name == 'ioctl' and result != -errno.ENOTTY:
                            raise ValueError('native TCGETS did not fail ENOTTY')
                        elif name in ('mmap', 'mprotect', 'munmap', 'brk'):
                            detail = {'maps': n._maps(proc)}
                            desc = records[a[4]]['description'] if name == 'mmap' and (not a[3] & 32) else None
                            current_maps = n._reconcile_maps(name, a, result, current_maps, detail['maps'], used_files, desc)
                        elif name in ('stat', 'lstat', 'fstat', 'newfstatat', 'readlink', 'readlinkat', 'getdents64', 'getcwd', 'uname', 'getrlimit', 'sysinfo', 'clock_gettime', 'prlimit64', 'getrandom', 'arch_prctl', 'rt_sigaction', 'rt_sigprocmask'):
                            raw = n._result_buffer(pending, result, mem)
                            identity = None
                            fd_kind = None
                            if name == 'fstat':
                                record = records[a[0]]
                                fd_kind = record['kind']
                                identity = record['description']['identity'] if 'description' in record else record['identity']
                                if fd_kind == 'sidecar':
                                    identity = identity[:6]
                            uname = os.uname()
                            n._validate_metadata_result(pending, result, raw, spec, candidate_facts, identity, {'system': 'Linux', 'machine': 'x86_64', 'release': uname.release, 'version': uname.version}, fd_kind=fd_kind)
                            detail = {'buffer_sha256': n._runtime_blob(artifacts, raw, budget)}
                        n._append(events, 'leave', {'result': result, 'detail': detail}, start, spec['limits'], budget=event_budget)
                        pending = None
                else:
                    raise ValueError('unsupported native signal/restart stop')
                n._ptrace(24, pid)
            sidecars = {}
            for path, raw in outputs.items():
                fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
                try:
                    identity = n._identity(os.fstat(fd))
                    actual = n._read_fd(fd, n.RUNTIME_BYTES if path.endswith('/runtime') else spec['limits']['syntax_bytes'])
                    if actual != bytes(raw) or identity[5] != 1:
                        raise ValueError('native final output/write mismatch')
                    sidecars[path] = {'sha256': n._runtime_blob(artifacts, actual, budget), 'identity': identity}
                finally:
                    os.close(fd)
            for path, fd in held.items():
                if n._identity(os.fstat(fd)) != candidate_facts[path]['identity'] or n._read_fd(fd, n.MAX_DEPENDENCY_BYTES) != n._raw(artifacts, candidate_facts[path]['sha256']):
                    raise ValueError('native post-run file drift')
            n._host_window(authority._context)
            authority._guard.verify()
            native_terminal = {'returncode': returncode, 'stdout_sha256': n._runtime_blob(artifacts, bytes(streams['stdout']), budget), 'stderr_sha256': n._runtime_blob(artifacts, bytes(streams['stderr']), budget), 'sidecars': sidecars, 'eof': sorted(eof, reverse=True), 'reaped': reaped, 'cleanup': 'pending-owned-workspace-cleanup', 'wait': native_wait}
            pass
        except BaseException as exc:
            interruption = exc if not isinstance(exc, Exception) else None
            failure = 'native-observation:' + type(exc).__name__ + ':' + str(exc)[:240]
        finally:
            grace = spec['limits']['termination_grace_seconds']
            cleanup_started = time.monotonic()
            cleanup_deadline = min(start + spec['limits']['wall_seconds'] + grace, cleanup_started + grace)
            custody, returncode = n._finish_native_custody(pid, descendants, reaped, returncode, deadline=cleanup_deadline)
            try:
                n.validate_native_custody(custody)
            except ValueError:
                failure = failure or 'native-terminal-custody-uncertain'
            for fd in set(list(held.values()) + acquired + pipes + [mem, procfd]):
                if fd >= 0:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
    uname = os.uname()
    observation: dict[str, Any] = {'schema': 'TEST_ONLY-pdf-baseline-events/v1', 'scope': DATA_SCOPE, 'purpose': 'TEST_ONLY', 'spec': copy.deepcopy(spec), 'files': used_files, 'events': events, 'platform': {'system': 'Linux', 'machine': 'x86_64', 'release': uname.release, 'version': uname.version}, 'host_policy_sha256': sm.sha256(authority._context._policy), 'run': None}
    observation['spec'].update(schema='TEST_ONLY-pdf-baseline-spec/v1', purpose='TEST_ONLY', profile=DATA_SCOPE)
    clock = {'started_at': started, 'ended_at': None, 'monotonic_start_ns': start_ns, 'elapsed_ns': None, 'wall_deadline_ns': start_ns + 120 * 10 ** 9, 'cleanup_started_ns': int(cleanup_started * 10 ** 9), 'cleanup_deadline_ns': min(int(cleanup_started * 10 ** 9) + 2 * 10 ** 9, start_ns + 122 * 10 ** 9)}
    observation['run'] = clock
    return {'stdout': bytes(streams['stdout']), 'stderr': bytes(streams['stderr']), 'observed_bytes_lower_bound': observed_streams, 'failure': failure, 'native_observation': observation, 'native_artifacts': artifacts, 'process_group': custody, '_terminal': native_terminal, '_wait': native_wait, '_eof': list(eof), '_interruption': interruption, '_start': start}

def _driver_inventory() -> list[dict]:
    paths=[str(Path(str(module.__file__)).resolve()) for module in (sys.modules[__name__],n,migration,bridge,origin,sm)]+[str(sm.SCHEMA_PATH.resolve())]
    return [{'path':path,'sha256':sm.sha256(Path(path).read_bytes()),'bytes':len(Path(path).read_bytes())} for path in sorted(paths)]


def _check_drivers(plan: dict, archive: dict) -> None:
    drivers=sm._json(_raw(archive,plan['recorder_inventory_sha256']))
    if drivers!=_driver_inventory():raise ValueError('reached comparison source inventory changed')
    for row in drivers:
        if Path(row['path']).read_bytes()!=_raw(archive,row['sha256']):raise ValueError('retained driver source bytes differ')


def _stream(raw: bytes, name: str, events: list[dict], observed: int, archive: dict, complete: bool) -> dict:
    initial=events[0]['data']['fds'] if events and events[0]['kind']=='start' else None
    fd=1 if name=='stdout' else 2
    eof=next((event['seq'] for event in events if event['kind']=='pipe-eof' and event['data']['channel']==name),None)
    return {'captured':{'sha256':_put(archive,raw),'bytes':len(raw)},'observed_bytes_lower_bound':observed,'complete':complete,'original_descriptor':fd,'generation':0,'identity':initial[fd]['identity'] if initial else None,'eof_event_seq':eof}


def _finalize_capture(plan: dict, run: dict, archive: dict, *, workspace_cleanup: str) -> dict:
    observation=run['native_observation'];clock=observation['run'];events=observation['events']
    clock['elapsed_ns']=int((time.monotonic()-run['_start'])*10**9)
    clock['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    terminal=run['_terminal'];failure=run['failure']
    if workspace_cleanup!='removed':failure=failure or 'comparison-workspace-custody-unverified'
    if terminal is not None and failure is None:
        terminal=copy.deepcopy(terminal);terminal['cleanup']='owned-workspace-removed';terminal['custody']=copy.deepcopy(run['process_group'])
        events.append({'seq':len(events),'at_ns':clock['elapsed_ns'],'kind':'terminal','data':terminal})
    if failure is None:
        try:check_comparison_events(observation,archive,observation_mode='actual')
        except (ValueError,KeyError,TypeError):failure='comparison-independent-replay-refused'
    complete=failure is None
    wait=copy.deepcopy(run['_wait'])
    if wait is not None:wait['provenance']='natural_terminal'
    initial=events[0]['data'] if events and events[0]['kind']=='start' else None
    invocation={'schema':'twin.source-extraction-invocation/v1','argv':observation['spec']['argv'],'cwd':observation['spec']['cwd'],'environment':dict(migration.ENVIRONMENT),'stdin':'OWNED-EOF-PIPE'}
    intervention='cleanup_intervention' if run['process_group']['signals'] else 'none'
    run_id=sm.sha256(sm.canonical({'plan_sha256':sm.sha256(sm.canonical(plan)),'invocation_sha256':sm.sha256(sm.canonical(invocation)),'started_at':clock['started_at'],'monotonic_start_ns':clock['monotonic_start_ns'],'process':{k:initial[k] for k in ('pid','starttime','ppid','uid','gid')}})) if initial else None
    events_raw=sm.canonical(observation)
    if len(events_raw)>64*MIB:raise ValueError('comparison native event artifact cap')
    data={'schema':'TEST_ONLY-pdf-baseline-capture-data/v1','purpose':'TEST_ONLY','observation_mode':'actual','plan_sha256':sm.sha256(sm.canonical(plan)),'pair_plan_sha256':plan['pair_plan_sha256'],'host_policy_sha256':observation['host_policy_sha256'],'host_evidence_sha256':_record(archive,{'schema':'TEST_ONLY-comparison-host-evidence-index/v1','sha256s':sorted(sm._json(_raw(archive,observation['host_policy_sha256']))['evidence_sha256s'])}),'run_id':run_id,'invocation_sha256':_record(archive,invocation),'process_sha256':_record(archive,initial) if initial else None,'run_clock_sha256':_record(archive,clock),'native_events_sha256':_put(archive,events_raw),'dependency_observation_sha256':_record(archive,observation['files']),'stdout':_stream(run['stdout'],'stdout',events,run['observed_bytes_lower_bound']['stdout'],archive,complete),'stderr':_stream(run['stderr'],'stderr',events,run['observed_bytes_lower_bound']['stderr'],archive,complete),'terminal_wait':wait,'custody_sha256':_record(archive,run['process_group']),'cleanup':workspace_cleanup,'intervention':intervention,'status':'COMPLETE_EXIT0_DATA' if complete else 'FAILED_DATA','failure':None}
    if failure is not None:data['failure']={'stage':'observation' if workspace_cleanup=='removed' else 'cleanup','code':'CAPTURE_REFUSED','original_exception_type':None,'facts_sha256':_failure_facts(data,archive,str(failure)[:240],None,None)}
    return data


def _failure_facts(data: dict, archive: dict, reason: str, exception_type: str | None, workspace: str | None) -> str:
    facts={'schema':'TEST_ONLY-comparison-failure-facts/v1','reason':reason[:240],'exception_type':exception_type,'workspace':workspace,**{key:copy.deepcopy(data[key]) for key in ('stdout','stderr','terminal_wait','custody_sha256','cleanup','intervention')}}
    return _record(archive,facts)


def _completion(authority: ComparisonCaptureAuthority, plan: dict, data: dict, archive: dict) -> ComparisonCompletion:
    check_comparison_capture(data,archive,expected_plan=plan)
    completion=object.__new__(ComparisonCompletion);raw=sm.canonical(data)
    for key,value in {'_record':raw,'_held_record':bytes(bytearray(raw)),'_archive':dict(archive),'_plan':sm.canonical(plan),'_pair':authority._pair,'_guard':authority._guard,'_session':authority._session}.items():object.__setattr__(completion,key,value)
    _retain_completion(authority,archive,failed=data['status']!='COMPLETE_EXIT0_DATA',patched=False)
    return completion


def _failed_capture(authority: ComparisonCaptureAuthority, plan: dict, archive: dict, error: BaseException, workdir: Path | None) -> ComparisonCompletion:
    # Passive, bounded facts only. Unknown process/custody/terminal facts stay null.
    authority._session._stopped=True
    empty={'sha256':_put(archive,b''),'bytes':0}
    stream=lambda fd:{'captured':dict(empty),'observed_bytes_lower_bound':0,'complete':False,'original_descriptor':fd,'generation':0,'identity':None,'eof_event_seq':None}
    policy_pin=_put(archive,authority._context._policy);archive.update(authority._context._evidence)
    policy=sm._json(authority._context._policy)
    facts={'exception_type':type(error).__name__[:80],'workspace':str(workdir) if workdir is not None else None,'custody':'UNKNOWN; no successful collector return'}
    data={'schema':'TEST_ONLY-pdf-baseline-capture-data/v1','purpose':'TEST_ONLY','observation_mode':'actual','plan_sha256':sm.sha256(sm.canonical(plan)),'pair_plan_sha256':plan['pair_plan_sha256'],'host_policy_sha256':policy_pin,'host_evidence_sha256':_record(archive,{'schema':'TEST_ONLY-comparison-host-evidence-index/v1','sha256s':sorted(policy['evidence_sha256s'])}),'run_id':None,'invocation_sha256':None,'process_sha256':None,'run_clock_sha256':None,'native_events_sha256':None,'dependency_observation_sha256':None,'stdout':stream(1),'stderr':stream(2),'terminal_wait':None,'custody_sha256':None,'cleanup':'preserved-uncertain' if workdir is not None else 'not-created','intervention':'none','status':'FAILED_DATA','failure':{'stage':'prepare','code':'CAPTURE_REFUSED','original_exception_type':type(error).__name__[:80],'facts_sha256':None}}
    data['failure']['facts_sha256']=_failure_facts(data,archive,'collector returned no custody/stream facts',type(error).__name__[:80],str(workdir) if workdir is not None else None)
    completion=_completion(authority,plan,data,archive)
    if workdir is not None:
        try:migration._write_owned(workdir/'comparison-failed-data.json',completion._record)
        except OSError:pass
    return completion


def _capture_baseline(authority: ComparisonCaptureAuthority, plan: dict, artifacts: dict) -> ComparisonCompletion:
    authority._guard.verify()
    if authority._spent or sm.canonical(plan)!=authority._plan:raise ValueError('private authority spent or frozen plan changed')
    archive=dict(authority._archive)
    if artifacts!=archive:raise ValueError('independently selected comparison archive differs')
    _plan(plan,archive);_check_drivers(plan,archive)
    context=authority._context;n._host_window(context)
    if time.monotonic()-authority._selected_at>60:raise ValueError('original comparison preparation deadline')
    _consume(authority,patched=False);object.__setattr__(authority,'_spent',True)
    workdir=None;run=None;cleanup='preserved-uncertain'
    try:
        workdir=Path(tempfile.mkdtemp(prefix='TEST_ONLY-pdf-comparison-'))
        os.chmod(workdir,0o700)
        for name,blob in [('input',plan['fixture']),('native-config',plan['config'])]:migration._write_owned(workdir/name,_blob(blob,archive,256*MIB))
        candidates=_candidate_rows(plan,archive,str(workdir))
        spec={'schema':'twin.native-observation-spec/v1','purpose':'actual','profile':'pdf-text-xpdf/1','plan_sha256':sm.sha256(sm.canonical(plan)),'argv':migration._pdf_command(plan['executable_path'],str(workdir)),'environment':dict(migration.ENVIRONMENT),'cwd':str(workdir),'limits':dict(LIMITS),'candidates':candidates}
        run=_linux_run_comparison(authority,spec,archive)
        try:n.validate_native_custody(run['process_group'])
        except (ValueError,KeyError,TypeError):pass
        else:
            object.__setattr__(authority._session,'_target_custody_known',True);object.__setattr__(authority._session,'_active_slot',None)
            try:
                import shutil
                shutil.rmtree(workdir);cleanup='removed'
            except OSError:cleanup='failed'
        try:n._host_window(context);authority._guard.verify();_check_drivers(plan,archive)
        except (ValueError,OSError,TypeError):run['failure']=run['failure'] or 'post-run-host-or-source-refused'
        data=_finalize_capture(plan,run,archive,workspace_cleanup=cleanup)
        completion=_completion(authority,plan,data,archive)
    except BaseException as error:
        completion=_failed_capture(authority,plan,archive,error,workdir if cleanup!='removed' else None)
        if not isinstance(error,Exception):
            setattr(error,'comparison_failed_data',sm._json(completion._record));raise
        return completion
    interruption=run['_interruption']
    if interruption is not None:
        authority._session._stopped=True
        setattr(interruption,'comparison_failed_data',sm._json(completion._record));raise interruption
    return completion


def _candidate_rows(plan: dict, archive: dict, cwd: str) -> list[dict]:
    rows=copy.deepcopy(sm._json(_raw(archive,plan['candidate_inventory_sha256'])))
    drivers=sm._json(_raw(archive,plan['recorder_inventory_sha256']))
    for row in drivers:
        old=next((r for r in rows if r['path']==row['path']),None)
        if old is not None and old!=row:raise ValueError('driver/candidate source collision')
        if old is None:rows.append(row)
    for name,blob in [('input',plan['fixture']),('native-config',plan['config'])]:
        if any(r['path']==cwd+'/'+name for r in rows):raise ValueError('candidate collides with fixed staged input/config')
        rows.append({'path':cwd+'/'+name,**blob})
    if len(rows)>4096:raise ValueError('comparison candidate count cap')
    return rows


def _wait(value: dict) -> None:
    if type(value) is not dict:raise ValueError('typed actual wait required')
    expected={'kind','raw_status','exit_code','observed_at_ns','provenance'} if value.get('kind')=='exited' else {'kind','raw_status','signal','core_dumped','observed_at_ns','provenance'}
    _closed(value,expected)
    if value['provenance'] not in ('natural_terminal','cleanup_intervention'):raise ValueError('wait provenance differs')
    raw={k:v for k,v in value.items() if k!='provenance'}
    returncode=value['exit_code'] if value['kind']=='exited' else -value['signal']
    n._validate_wait(raw,returncode,success=False)


def check_comparison_capture(record: dict, artifacts: dict[str,bytes], *, expected_plan: dict) -> dict:
    """Check exported DATA consistency; public records never recreate completion."""
    _closed(record,{'schema','purpose','observation_mode','plan_sha256','pair_plan_sha256','host_policy_sha256','host_evidence_sha256','run_id','invocation_sha256','process_sha256','run_clock_sha256','native_events_sha256','dependency_observation_sha256','stdout','stderr','terminal_wait','custody_sha256','cleanup','intervention','status','failure'})
    pair=_plan(expected_plan,artifacts)
    if record['schema']!='TEST_ONLY-pdf-baseline-capture-data/v1' or record['purpose']!='TEST_ONLY' or record['plan_sha256']!=sm.sha256(sm.canonical(expected_plan)) or record['pair_plan_sha256']!=expected_plan['pair_plan_sha256']:raise ValueError('comparison data plan binding differs')
    mode=record['observation_mode'];status=record['status']
    if mode not in ('actual','SIMULATED_DATA','NOT_STARTED') or status not in ('COMPLETE_EXIT0_DATA','FAILED_DATA','HELD_BEFORE_OS') or record['cleanup'] not in ('removed','failed','preserved-uncertain','not-created') or record['intervention'] not in ('none','cleanup_intervention'):raise ValueError('comparison disposition differs')
    if mode!='actual' and (record['host_policy_sha256'] is not None or record['host_evidence_sha256'] is not None):raise ValueError('nonactual DATA cannot claim H')
    if mode=='actual':
        policy=_json(artifacts,record['host_policy_sha256']);n._validate_host_policy(policy)
        host=_json(artifacts,record['host_evidence_sha256']);_closed(host,{'schema','sha256s'})
        if host!={'schema':'TEST_ONLY-comparison-host-evidence-index/v1','sha256s':sorted(policy['evidence_sha256s'])}:raise ValueError('comparison H evidence index differs')
        for pin in policy['evidence_sha256s']:_raw(artifacts,pin)
        for pin in (expected_plan['build_identity_sha256'],pair['build_pair']['patched_build_sha256'],expected_plan['config']['sha256'],pair['suite_selection_sha256']):
            if pin not in policy['evidence_sha256s']:raise ValueError('comparison independent build/config evidence absent')
    for name,fd in [('stdout',1),('stderr',2)]:
        stream=record[name];_closed(stream,{'captured','observed_bytes_lower_bound','complete','original_descriptor','generation','identity','eof_event_seq'})
        raw=_blob(stream['captured'],artifacts,LIMITS[name+'_bytes'])
        if _uint(stream['observed_bytes_lower_bound'])<len(raw) or type(stream['complete']) is not bool or type(stream['original_descriptor']) is not int or stream['original_descriptor']!=fd or _uint(stream['generation'],0)!=0:raise ValueError('comparison stream relation differs')
        if stream['identity'] is not None:
            if type(stream['identity']) is not list or len(stream['identity'])!=2:raise ValueError('comparison stream identity differs')
            for x in stream['identity']:_uint(x)
        if stream['eof_event_seq'] is not None:_uint(stream['eof_event_seq'])
    if record['terminal_wait'] is not None:_wait(record['terminal_wait'])
    if status=='HELD_BEFORE_OS':
        if mode!='NOT_STARTED' or record['cleanup']!='not-created' or any(record[k] is not None for k in ('run_id','process_sha256','run_clock_sha256','native_events_sha256','dependency_observation_sha256','terminal_wait','custody_sha256')) or any(record[k]['complete'] or record[k]['captured']['bytes'] or record[k]['identity'] is not None or record[k]['eof_event_seq'] is not None for k in ('stdout','stderr')):raise ValueError('prelaunch DATA claims observations')
    elif mode=='NOT_STARTED':raise ValueError('not-started DATA cannot claim a run')
    for key in ('invocation_sha256','process_sha256','run_clock_sha256','native_events_sha256','dependency_observation_sha256','custody_sha256'):
        if record[key] is not None:_raw(artifacts,record[key])
    if status=='COMPLETE_EXIT0_DATA':
        if record['failure'] is not None or record['cleanup']!='removed' or record['intervention']!='none' or any(record[k] is None for k in ('run_id','invocation_sha256','process_sha256','run_clock_sha256','native_events_sha256','dependency_observation_sha256','custody_sha256')):raise ValueError('complete DATA missing original facts')
        obs_raw=_raw(artifacts,record['native_events_sha256'])
        if len(obs_raw)>64*MIB:raise ValueError('comparison events artifact cap')
        observation=sm._json(obs_raw);check_comparison_events(observation,artifacts,observation_mode=mode)
        if observation['spec']['candidates']!=_candidate_rows(expected_plan,artifacts,observation['spec']['cwd']):raise ValueError('completed DATA candidate/input/config selection differs')
        if observation['spec']['plan_sha256']!=record['plan_sha256'] or observation['host_policy_sha256']!=record['host_policy_sha256'] or _json(artifacts,record['run_clock_sha256'])!=observation['run'] or _json(artifacts,record['process_sha256'])!=observation['events'][0]['data'] or _json(artifacts,record['dependency_observation_sha256'])!=observation['files'] or _json(artifacts,record['custody_sha256'])!=observation['events'][-1]['data']['custody']:raise ValueError('completed DATA replaces recorder facts')
        invocation=_json(artifacts,record['invocation_sha256']);wanted={'schema':'twin.source-extraction-invocation/v1','argv':migration._pdf_command(expected_plan['executable_path'],observation['spec']['cwd']),'cwd':observation['spec']['cwd'],'environment':dict(migration.ENVIRONMENT),'stdin':'OWNED-EOF-PIPE'}
        if invocation!=wanted or observation['spec']['argv']!=wanted['argv']:raise ValueError('completed DATA invocation differs')
        initial=observation['events'][0]['data'];clock=observation['run']
        run_id=sm.sha256(sm.canonical({'plan_sha256':record['plan_sha256'],'invocation_sha256':record['invocation_sha256'],'started_at':clock['started_at'],'monotonic_start_ns':clock['monotonic_start_ns'],'process':{k:initial[k] for k in ('pid','starttime','ppid','uid','gid')}}))
        if record['run_id']!=run_id:raise ValueError('completed DATA run identity differs')
        for name in ('stdout','stderr'):
            stream=record[name];eofs=[e for e in observation['events'] if e['kind']=='pipe-eof' and e['data']['channel']==name]
            if stream['complete'] is not True or stream['observed_bytes_lower_bound']!=stream['captured']['bytes'] or stream['captured']['sha256']!=observation['events'][-1]['data'][name+'_sha256'] or stream['identity']!=initial['fds'][stream['original_descriptor']]['identity'] or stream['eof_event_seq']!=eofs[0]['seq']:raise ValueError('completed DATA stream differs')
        if record['terminal_wait']!={**observation['events'][-1]['data']['wait'],'provenance':'natural_terminal'}:raise ValueError('completed DATA typed wait differs')
    else:
        if record['failure'] is None or any(record[name]['complete'] for name in ('stdout','stderr')):raise ValueError('failed DATA cannot claim complete streams')
        failure=record['failure'];_closed(failure,{'stage','code','original_exception_type','facts_sha256'})
        if failure['stage'] not in ('prepare','selection','launch','observation','terminal','cleanup','export') or failure['code'] not in ('CAPTURE_REFUSED','PRELAUNCH_HELD') or failure['original_exception_type'] is not None and (type(failure['original_exception_type']) is not str or len(failure['original_exception_type'])>80):raise ValueError('closed failure code required')
        facts=_json(artifacts,failure['facts_sha256'])
        _closed(facts,{'schema','reason','exception_type','workspace','stdout','stderr','terminal_wait','custody_sha256','cleanup','intervention'})
        if facts['schema']!='TEST_ONLY-comparison-failure-facts/v1' or type(facts['reason']) is not str or len(facts['reason'])>240 or facts['exception_type']!=failure['original_exception_type'] or facts['workspace'] is not None and (type(facts['workspace']) is not str or len(facts['workspace'])>4096) or any(facts[key]!=record[key] for key in ('stdout','stderr','terminal_wait','custody_sha256','cleanup','intervention')):raise ValueError('retained comparison failure facts differ')
    if sum(len(raw) for raw in artifacts.values())>MAX_CAPTURE_BYTES:raise ValueError('comparison capture artifact cap')
    return {'status':status,'observation_mode':mode,'qualification':'NONE'}


def _baseline_view(completion: ComparisonCompletion, pair: dict) -> tuple[dict,dict]:
    if type(completion) is not ComparisonCompletion:raise ValueError('private baseline completion required')
    completion._guard.verify()
    if completion._record!=completion._held_record or completion._pair!=sm.canonical(pair):raise ValueError('actual completed baseline record changed')
    data=sm._json(completion._record);plan=sm._json(completion._plan)
    check_comparison_capture(data,completion._archive,expected_plan=plan)
    if data['observation_mode']!='actual':raise ValueError('simulated DATA cannot become actual completion')
    return data,completion._archive


def _compare_data(pair: dict, baseline: dict | None, baseline_archive: dict, patched: dict | None, patched_archive: dict, *, actual_origin_confirmed: bool) -> dict:
    comparisons: dict[str,bool | None]={name:None for name in ('stdout','stderr','exit')}
    if baseline is not None and patched is not None:
        for name in ('stdout','stderr'):
            if baseline[name]['complete'] and patched[name]['complete']:comparisons[name]=_blob(baseline[name]['captured'],baseline_archive,LIMITS[name+'_bytes'])==_blob(patched[name]['captured'],patched_archive,LIMITS[name+'_bytes'])
        left=baseline['terminal_wait'];right=patched['terminal_wait']
        if left is not None and right is not None and left['provenance']==right['provenance']=='natural_terminal':
            _wait(left);_wait(right);comparisons['exit']=(left['kind'],left['raw_status'])==(right['kind'],right['raw_status'])
    complete=baseline is not None and patched is not None and baseline['status']==patched['status']=='COMPLETE_EXIT0_DATA'
    status='MISMATCH' if False in comparisons.values() else 'MATCH' if complete and all(v is True for v in comparisons.values()) else 'NOT_COMPARABLE'
    return {'schema':'TEST_ONLY-pdf-pair-comparison/v1','purpose':'TEST_ONLY','pair_plan_sha256':sm.sha256(sm.canonical(pair)),'baseline_data_sha256':sm.sha256(sm.canonical(baseline)) if baseline is not None else None,'patched_data_sha256':sm.sha256(sm.canonical(patched)) if patched is not None else None,'stdout_equal':comparisons['stdout'],'stderr_equal':comparisons['stderr'],'exit_equal':comparisons['exit'],'status':status,'n01_full_stdout_equal':comparisons['stdout'],'stop_suite':status!='MATCH' or not actual_origin_confirmed,'qualification':'NONE'}


def compare_pair(pair_plan: dict, baseline_completed: ComparisonCompletion, patched_completed: PatchedComparisonCompletion | None=None) -> dict:
    """Consume source-guarded comparative completions, never adopt native handles."""
    baseline,archive=_baseline_view(baseline_completed,pair_plan);session=baseline_completed._session
    if patched_completed is not None and type(patched_completed) is not PatchedComparisonCompletion:raise ValueError('private paired comparative completion required')
    if baseline['status']!='COMPLETE_EXIT0_DATA':
        if patched_completed is not None:raise ValueError('failed pristine gate cannot accept a patched partner')
        session._stopped=True
        return _compare_data(pair_plan,baseline,archive,None,{},actual_origin_confirmed=False)
    if patched_completed is None:
        session._stopped=True
        return _compare_data(pair_plan,baseline,archive,None,{},actual_origin_confirmed=False)
    if patched_completed._session is not session:raise ValueError('same private original suite required')
    patched,patched_archive=_private_patched_view(patched_completed,pair_plan,archive)
    result=_compare_data(pair_plan,baseline,archive,patched,patched_archive,actual_origin_confirmed=patched['status']=='COMPLETE_EXIT0_DATA')
    baseline_completed._guard.verify()
    session._stopped=session._stopped or result['stop_suite'];session._awaiting_comparison=False
    return result


def compare_simulated_pair(pair_plan: dict, baseline_record: dict, baseline_archive: dict, baseline_plan: dict, patched_record: dict, patched_archive: dict, patched_plan: dict) -> dict:
    """Pure public controls only; cannot clear the actual suite's stop condition."""
    for data,archive,plan in ((baseline_record,baseline_archive,baseline_plan),(patched_record,patched_archive,patched_plan)):
        check_comparison_capture(data,archive,expected_plan=plan)
        if data['observation_mode']!='SIMULATED_DATA' or data['pair_plan_sha256']!=sm.sha256(sm.canonical(pair_plan)):raise ValueError('explicit simulated pair DATA required')
    return _compare_data(pair_plan,baseline_record,baseline_archive,patched_record,patched_archive,actual_origin_confirmed=False)


@dataclasses.dataclass(eq=False, frozen=True, init=False, repr=False)
class PatchedComparisonCompletion(_PrivateCapability):
    _completed: tuple[dict,dict]
    _plan: bytes
    _pair: bytes
    _guard: Any
    _context: n.NativeHostContext
    _session: ComparisonSession


def capture_patched_comparison(authority: ComparisonCaptureAuthority, baseline_completed: ComparisonCompletion, store: n.NativeObservationStore, plan: dict, parent: bytes) -> PatchedComparisonCompletion:
    """One existing paired bridge execution, conserving all pre-OS acquisition gates.

    Retains failed actual pairs as comparative DATA. Does not deposit/acquire/adopt
    any native handle, and cannot accept a public result or failure dictionary.
    """
    if type(authority) is not ComparisonCaptureAuthority or type(baseline_completed) is not ComparisonCompletion:raise ValueError('private comparison authority/completion required')
    authority._guard.verify();pair=sm._json(authority._pair)
    if baseline_completed._session is not authority._session:raise ValueError('same private original comparison session required')
    baseline,baseline_archive=_baseline_view(baseline_completed,pair)
    if baseline['status']!='COMPLETE_EXIT0_DATA' or authority._spent:raise ValueError('failed baseline gate or spent authority')
    if type(store) is not n.NativeObservationStore or store._purpose!='actual' or type(store._host_context) is not n.NativeHostContext or store._host_context is not authority._context:raise ValueError('exact private actual patched store/host required')
    store._guard.verify();authority._guard.verify();n._host_window(store._host_context)
    frozen=copy.deepcopy(plan);n.validate_native_candidate_plan(frozen,parent)
    if frozen['purpose']!='actual' or frozen['profile']!=bridge.PROFILE:raise ValueError('actual profile2 patched plan required')
    bridge._require_actual_selection(store,frozen)
    config=sm._json(_raw(frozen['archive'],frozen['configuration_sha256']))
    if frozen['parent_sha256']!=pair['fixture']['sha256'] or frozen['parent_bytes']!=pair['fixture']['bytes'] or parent!=_blob(pair['fixture'],baseline_archive,256*MIB) or config['native_config_sha256']!=pair['config']['sha256'] or config['pdf_origin']['build_identity_sha256']!=pair['build_pair']['patched_build_sha256'] or _raw(frozen['archive'],config['native_config_sha256'])!=_blob(pair['config'],baseline_archive,MIB):raise ValueError('patched plan/input/config/build pair selection differs')
    if _raw(frozen['archive'],config['pdf_origin']['build_identity_sha256'])!=_raw(baseline_archive,pair['build_pair']['patched_build_sha256']):raise ValueError('independent paired build bytes differ')
    admit_slot(elapsed_ns=int((time.monotonic()-authority._suite_started)*10**9),slots_used=authority._slots_used,retained_bytes=authority._retained_bytes,reserve_bytes=authority._reserve_bytes)
    if time.monotonic()-authority._selected_at>60:raise ValueError('original comparison preparation deadline')
    _consume(authority,patched=True)
    object.__setattr__(authority,'_spent',True)
    try:completed=migration._execute_prepared_extraction(frozen,parent,observation_store=store,preparation_deadline=min(authority._selected_at+60,authority._suite_started+B_SECONDS))
    except BaseException:
        authority._session._stopped=True
        raise
    try:
        result,actual_record=n._completed_pdf_result(completed)
        dossier=sm._json(_raw(result['receipts'],result['dossier_sha256']))
        try:n.validate_native_custody(dossier['process_group'])
        except (ValueError,KeyError,TypeError):authority._session._stopped=True
        else:object.__setattr__(authority._session,'_target_custody_known',True);object.__setattr__(authority._session,'_active_slot',None)
        if actual_record['host_policy_sha256']!=sm.sha256(store._host_context._policy):raise ValueError('patched actual completion changed private H')
        if result['status']=='success':
            n.verify_native_observation(actual_record,result['archive'],purpose='actual');bridge.verify_pdf_extraction_bundle(frozen,parent,result)
        elif result['status']!='failure':raise ValueError('patched completion disposition differs')
        store._guard.verify();authority._guard.verify()
        value=object.__new__(PatchedComparisonCompletion)
        for key,item in {'_completed':(copy.deepcopy(result),copy.deepcopy(actual_record)),'_plan':sm.canonical({k:v for k,v in frozen.items() if k!='archive'}),'_pair':authority._pair,'_guard':authority._guard,'_context':store._host_context,'_session':authority._session}.items():object.__setattr__(value,key,item)
        _retain_completion(authority,result['archive'],failed=result['status']!='success',patched=True)
        return value
    except BaseException:
        authority._session._stopped=True
        raise


def _private_patched_view(completion: PatchedComparisonCompletion, pair: dict, baseline_archive: dict) -> tuple[dict,dict]:
    if type(completion) is not PatchedComparisonCompletion:raise ValueError('private patched comparative completion required')
    completion._guard.verify();completion._context._guard.verify()
    if completion._pair!=sm.canonical(pair):raise ValueError('patched comparative pair changed')
    result,observation=n._completed_pdf_result(completion._completed)
    if observation['host_policy_sha256']!=sm.sha256(completion._context._policy):raise ValueError('private patched H binding differs')
    plan=sm._json(completion._plan);plan['archive']=result['archive']
    config,closure=bridge._validate_plan(plan,_blob(pair['fixture'],baseline_archive,256*MIB))
    if config['native_config_sha256']!=pair['config']['sha256'] or config['pdf_origin']['build_identity_sha256']!=pair['build_pair']['patched_build_sha256']:raise ValueError('held patched comparative selection differs')
    dossier=sm._json(_raw(result['receipts'],result['dossier_sha256']));archive=result['archive']
    if result['status']=='success':
        bridge.verify_pdf_extraction_bundle(plan,_blob(pair['fixture'],baseline_archive,256*MIB),result)
        terminal=observation['events'][-1]['data'];wait=copy.deepcopy(terminal['wait']);complete=True
    else:
        complete=False;wait=copy.deepcopy(observation.get('failure',{}).get('wait'))
    if wait is not None:wait['provenance']='natural_terminal';_wait(wait)
    data={'schema':'TEST_ONLY-pdf-patched-comparison-data/v1','purpose':'TEST_ONLY','observation_mode':'actual','pair_plan_sha256':sm.sha256(sm.canonical(pair)),'stdout':{'captured':dossier['stdout'],'complete':complete},'stderr':{'captured':dossier['stderr'],'complete':complete},'terminal_wait':wait,'status':'COMPLETE_EXIT0_DATA' if complete else 'FAILED_DATA','origin_effect_confirmed':complete,'host_policy_sha256':observation['host_policy_sha256'],'native_observation_sha256':sm.sha256(sm.canonical(observation))}
    for name in ('stdout','stderr'):_blob(data[name]['captured'],archive,LIMITS[name+'_bytes'])
    return data,archive


@dataclasses.dataclass(eq=False, init=False, repr=False)
class OriginalComparisonSuite(_PrivateCapability):
    """The one source-appointed original custody carrier; no genesis API exists.

    A future independently reviewed trusted selector must hold this capability.
    Contexts, selection hashes, JSON and repeated factory calls cannot appoint it.
    """
    _selection_raw: bytes
    _selection: str
    _started: float
    _next: int
    _retained: int
    _reserve: int
    _stopped: bool
    _awaiting_comparison: bool
    _used_hosts: set[str]
    _guard: Any
    _technical_state: object | None
    _active_slot: int | None
    _target_custody_known: bool

    def __new__(cls, *args, **kwargs):
        raise ValueError('private original suite must be source-appointed; no constructor')

    def __setattr__(self, name, value):
        if name in ('_selection_raw','_selection','_started','_guard') and hasattr(self,name):
            raise ValueError('private original suite selection/clock is immutable')
        if name=='_stopped' and getattr(self,'_stopped',False) and value is not True:
            raise ValueError('private original suite cannot resume after stop')
        if name=='_target_custody_known' and hasattr(self,name) and self._target_custody_known is False and value is True:
            raise ValueError('private target custody requires independent terminal validation')
        if name=='_active_slot' and getattr(self,'_active_slot',None) is not None and value is None:
            raise ValueError('private active slot requires independent terminal validation')
        if name=='_technical_state' and getattr(self,'_technical_state',None) is not None and value is not self._technical_state:
            raise ValueError('private original technical custody cannot be reset')
        object.__setattr__(self,name,value)


# Compatibility name denotes the same carrier, never another wrapper or state.
ComparisonSession=OriginalComparisonSuite


def _original_selection(raw: bytes) -> dict:
    if type(raw) is not bytes or len(raw)>MIB:raise ValueError('private original suite selection bytes required')
    selection=sm._json(raw)
    _closed(selection,{'schema','original_started_monotonic_ns','original_seconds','max_invocations','slot_seconds','preparation_seconds','target_seconds','failed_cleanup_seconds','transport_seconds','storage_bytes','reserve_bytes'})
    expected={'schema':'TEST_ONLY-pdf-comparison-suite-selection/v1','original_started_monotonic_ns':selection['original_started_monotonic_ns'],'original_seconds':10800,'max_invocations':52,'slot_seconds':182,'preparation_seconds':60,'target_seconds':120,'failed_cleanup_seconds':2,'transport_seconds':300,'storage_bytes':MAX_SUITE_BYTES,'reserve_bytes':selection['reserve_bytes']}
    if sm.canonical(selection)!=raw or selection!=expected or any(type(selection[k]) is not int for k in selection if k!='schema'):raise ValueError('fixed original suite selection differs')
    _uint(selection['original_started_monotonic_ns']);_uint(selection['reserve_bytes'],MAX_SUITE_BYTES)
    return selection


def _check_original_suite(original: OriginalComparisonSuite) -> None:
    """Pure private-carrier/source validation; neither appointment nor terminal proof."""
    if type(original) is not OriginalComparisonSuite:raise ValueError('private original suite capability required')
    fields=('_selection_raw','_selection','_started','_next','_retained','_reserve','_stopped','_awaiting_comparison','_used_hosts','_guard','_technical_state','_active_slot','_target_custody_known')
    if any(not hasattr(original,key) for key in fields):raise ValueError('private original suite was not source-appointed')
    original._guard.verify();selection=_original_selection(original._selection_raw)
    if original._selection!=sm.sha256(original._selection_raw) or type(original._started) not in (int,float) or original._started!=selection['original_started_monotonic_ns']/10**9:raise ValueError('private original suite selection/clock changed')
    _uint(original._next,52);_uint(original._retained,MAX_SUITE_BYTES);_uint(original._reserve,selection['reserve_bytes'])
    if type(original._stopped) is not bool or type(original._awaiting_comparison) is not bool or type(original._target_custody_known) is not bool or type(original._used_hosts) is not set or len(original._used_hosts)!=original._next:raise ValueError('private original mutable custody differs')
    for pin in original._used_hosts:_hash(pin)
    if original._active_slot is None:
        if original._target_custody_known is not True:raise ValueError('private original target custody unknown')
    elif _uint(original._active_slot,51)!=original._next-1 or original._target_custody_known is not False or original._awaiting_comparison:
        raise ValueError('private original active target custody differs')


def _charge_technical_bytes(original: OriginalComparisonSuite, count: int) -> None:
    """Consume shared original storage before technical retention; never refund."""
    _check_original_suite(original);_uint(count)
    if original._retained+count+original._reserve+FAILURE_RESERVE>MAX_SUITE_BYTES:
        original._stopped=True
        raise ValueError('original technical storage exhausted before retention')
    original._retained+=count


def new_comparison_session(context: n.NativeHostContext, selection_sha256: str, *, original_suite: OriginalComparisonSuite | None=None) -> OriginalComparisonSuite:
    """Return the held original carrier unchanged; context/hash never creates one."""
    if type(context) is not n.NativeHostContext or type(original_suite) is not OriginalComparisonSuite:raise ValueError('private source-appointed original suite and host context required')
    _check_original_suite(original_suite);context._guard.verify();policy=n._host_window(context)
    if selection_sha256!=original_suite._selection or selection_sha256 not in policy['evidence_sha256s'] or _raw(context._evidence,selection_sha256)!=original_suite._selection_raw:raise ValueError('independent original suite selection differs')
    return original_suite


def _consume(authority: ComparisonCaptureAuthority, *, patched: bool) -> None:
    session=authority._session
    if type(session) is not ComparisonSession:raise ValueError('private original comparison session required')
    _check_original_suite(session)
    if session._stopped or session._awaiting_comparison or session._active_slot is not None or session._target_custody_known is not True or session._next!=authority._slot or bool(session._next%2)!=patched:raise ValueError('comparison schedule stopped, stale or out of order')
    host=sm.sha256(authority._context._policy)
    if host in session._used_hosts:raise ValueError('host interval already used; no renewal/reuse')
    admit_slot(elapsed_ns=int((time.monotonic()-session._started)*10**9),slots_used=session._next,retained_bytes=session._retained,reserve_bytes=session._reserve)
    session._used_hosts.add(host);session._next+=1
    session._active_slot=authority._slot;session._target_custody_known=False


def _retain_completion(authority: ComparisonCaptureAuthority, archive: dict, *, failed: bool, patched: bool) -> None:
    session=authority._session
    session._retained+=sum(len(raw) for raw in archive.values())
    if session._retained+FAILURE_RESERVE+session._reserve>MAX_SUITE_BYTES:session._stopped=True;raise ValueError('suite retained storage exhausted')
    session._stopped=session._stopped or failed
    session._awaiting_comparison=patched and not failed
