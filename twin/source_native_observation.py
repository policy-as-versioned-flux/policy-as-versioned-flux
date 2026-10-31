"""Bounded Linux x86_64 exact-invocation file observation.

Native OS code is called only by actual acquisition with an independently selected
host context. TEST_ONLY event acquisition and replay perform no native operation.
A consistent public trace is not an acquired actual execution.
"""
from __future__ import annotations
import copy
import ctypes
import dataclasses
import datetime
import errno
import fcntl
import json
import os
from pathlib import Path
import platform
import selectors
import signal
import stat
import struct
import sys
import tempfile
import time
from typing import Any
from . import source_metadata as sm

SCOPE = 'exact-invocation-file-dependencies/linux-x86_64-v1'
MAX_FILES, MAX_DEPENDENCY_BYTES = 4096, 256 * 1048576
MAX_EVENTS, MAX_EVENT_BYTES, MAX_PATH = 1000000, 64 * 1048576, 4096
RUNTIME_BYTES, PREPARE_SECONDS = 16 * 1048576, 60
ARCH = 0xc000003e
SIDE_FLAGS = 1 | 0x40 | 0x80 | 0x80000
OPTIONS = 1 | 2 | 4 | 8 | 16 | 64 | 0x100000
# Closed number->name table. The admission function narrows every argument form.
SYSCALLS = {'0':'read','1':'write','2':'open','3':'close','4':'stat','5':'fstat','6':'lstat',
    '8':'lseek','9':'mmap','10':'mprotect','11':'munmap','12':'brk','13':'rt_sigaction',
    '14':'rt_sigprocmask','16':'ioctl','17':'pread64','19':'readv','20':'writev','21':'access',
    '28':'madvise','32':'dup','33':'dup2','39':'getpid','59':'execve','60':'exit','63':'uname','72':'fcntl',
    '79':'getcwd','89':'readlink','97':'getrlimit','99':'sysinfo','102':'getuid',
    '104':'getgid','107':'geteuid','108':'getegid','158':'arch_prctl','186':'gettid',
    '202':'futex','217':'getdents64','218':'set_tid_address','228':'clock_gettime',
    '231':'exit_group','257':'openat','262':'newfstatat','267':'readlinkat',
    '273':'set_robust_list','292':'dup3','302':'prlimit64','318':'getrandom','334':'rseq'}

@dataclasses.dataclass(eq=False, frozen=True, init=False, repr=False)
class NativeHostContext:
    _policy: bytes
    _evidence: dict[str, bytes]
    _guard: Any

@dataclasses.dataclass(eq=False, init=False, repr=False)
class NativeObservationStore:
    _purpose: str
    _host_context: NativeHostContext | None
    _guard: Any
    _entries: dict[int, tuple]

@dataclasses.dataclass(eq=False, frozen=True, init=False, repr=False)
class ObservedExtraction:
    token: object


def _closed(value: Any, keys: set[str]) -> None:
    if type(value) is not dict or set(value) != keys:
        raise ValueError('closed native observation record required')


def _source_guard_callback(*args: Any) -> None:
    pass


def _guard() -> sm.MetadataAuthority:
    from . import source_metadata_migration as migration, pdf_output_origin, pdf_native_bridge
    policy = {'purpose':'TEST_ONLY','allowed_transforms':[],
              'reviewer_id':'independently-selected-source','reviewer_role':'source-binding-only'}
    return sm.MetadataAuthority.freeze('native-source-guard','native-source-bindings','1',
        sm.sha256(sm.canonical(policy)), _source_guard_callback, _source_guard_callback,
        policy=policy, helper_modules=(sys.modules[__name__],migration,pdf_output_origin,pdf_native_bridge))


def new_native_observation_store(*, purpose: str, host_context: NativeHostContext | None = None) -> NativeObservationStore:
    if purpose not in ('actual','TEST_ONLY'):
        raise ValueError('native purpose required')
    if host_context is not None:
        if type(host_context) is not NativeHostContext:
            raise ValueError('private host context required')
        host_context._guard.verify()
    store=object.__new__(NativeObservationStore)
    store._purpose,store._host_context,store._guard,store._entries=purpose,host_context,_guard(),{}
    return store


def acquire_native_observation(store: NativeObservationStore, plan: dict, parent: bytes) -> ObservedExtraction:
    if type(store) is not NativeObservationStore or store._purpose != 'actual' or store._host_context is None:
        raise ValueError('independently selected actual host authority required')
    return _acquire_actual(store,plan,parent)


def resolve_native_observation(store: NativeObservationStore, observed: ObservedExtraction) -> dict:
    # Check passive custody types before invoking any supplied guard or ledger.
    if type(store) is not NativeObservationStore or type(observed) is not ObservedExtraction:
        raise ValueError('exact private native store and opaque reference required')
    store._guard.verify()
    try:
        entry = store._entries[id(observed)]
        held, result, plan_raw, observation = entry[:4]
    except (KeyError,TypeError) as exc:
        raise ValueError('no private acquired native observation') from exc
    if held is not observed:
        raise ValueError('store-local acquired reference required')
    if _result_digest(result) != plan_raw:
        raise ValueError('held native result changed')
    verify_native_observation(observation,result['archive'],purpose=store._purpose)
    if store._purpose=='actual':
        if store._host_context is None or observation['host_policy_sha256']!=sm.sha256(store._host_context._policy):
            raise ValueError('private host selection binding differs')
        store._host_context._guard.verify()
        for pin in sm._json(store._host_context._policy)['evidence_sha256s']:
            _raw(store._host_context._evidence,pin)
    if _pdf2(observation['spec']):
        from . import pdf_native_bridge as bridge
        if len(entry)!=5: raise ValueError('private frozen PDF plan absent')
        plan=sm._json(entry[4]);plan['archive']=result['archive']
        bridge.verify_pdf_extraction_bundle(plan,_raw(result['archive'],plan['parent_sha256']),result)
    store._guard.verify()
    return copy.deepcopy(result)


def acquire_test_only_observation(store: NativeObservationStore, plan: dict, parent: bytes,
                                 observation: dict, artifacts: dict[str, bytes]) -> ObservedExtraction:
    if type(store) is not NativeObservationStore or store._purpose != 'TEST_ONLY':
        raise ValueError('TEST_ONLY purpose required for event injection')
    store._guard.verify()
    if observation.get('schema')!='twin.native-file-observation/v1': raise ValueError('raw TEST_ONLY v2 cannot issue profile2 references')
    verify_native_observation(observation,artifacts,purpose='TEST_ONLY')
    result={'status':'TEST_ONLY-observed','observation':copy.deepcopy(observation),'archive':dict(artifacts)}
    return _deposit(store,result,observation)


def _raw(artifacts: dict, pin: str) -> bytes:
    return sm._artifact(artifacts, pin)


def _path(value: Any) -> str:
    if (type(value) is not str or not value.startswith('/') or '\0' in value
            or len(value.encode()) > MAX_PATH or str(Path(value)) != value or '..' in Path(value).parts):
        raise ValueError('canonical bounded native path required')
    return value


def _integer(value: Any, low: int = 0, high: int = 2**64-1) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError('bounded native integer required')
    return value


def elf_interpreter(raw: bytes) -> str | None:
    if len(raw) < 64 or raw[:7] != b'\x7fELF\x02\x01\x01':
        raise ValueError('native ELF64 little-endian executable required')
    h=struct.unpack_from('<HHIQQQIHHHHHH',raw,16)
    if h[0] not in (2,3) or h[1] != 62 or h[8] != 56 or h[9]>4096:
        raise ValueError('native x86_64 ELF required')
    interpreter=None
    for i in range(h[9]):
        at=h[4]+i*56
        if at+56>len(raw): raise ValueError('ELF header span differs')
        kind,flags,offset,address,_,size,memsize,align=struct.unpack_from('<IIQQQQQQ',raw,at)
        if offset+size>len(raw): raise ValueError('ELF segment span differs')
        if kind==3:
            if interpreter is not None or not 2<=size<=MAX_PATH or raw[offset+size-1]!=0:
                raise ValueError('ELF interpreter differs')
            interpreter=_path(raw[offset:offset+size-1].decode('utf8'))
    return interpreter


def _file_rows(spec: dict, files: dict, artifacts: dict) -> dict:
    candidates={}
    if type(spec['candidates']) is not list or len(spec['candidates'])>MAX_FILES:
        raise ValueError('native candidate limit')
    total=0
    for row in spec['candidates']:
        _closed(row,{'path','sha256','bytes'})
        path=_path(row['path'])
        if path in candidates: raise ValueError('duplicate candidate')
        raw=_raw(artifacts,row['sha256'])
        if _integer(row['bytes'])!=len(raw): raise ValueError('candidate bytes differ')
        if path!=spec['cwd']+'/input': total+=len(raw)
        candidates[path]=row
    if total>MAX_DEPENDENCY_BYTES: raise ValueError('native dependency limit')
    if type(files) is not dict or len(files)>MAX_FILES: raise ValueError('native file limit')
    for path,row in files.items():
        _closed(row,{'path','sha256','bytes','identity'})
        if path!=_path(row['path']) or path not in candidates or any(row[k]!=candidates[path][k] for k in ('sha256','bytes')):
            raise ValueError('native acquired file outside candidate closure')
        identity=row['identity']
        if type(identity) is not list or len(identity)!=9 or any(type(v) is not int or v<0 for v in identity):
            raise ValueError('actual file identity required')
        if not stat.S_ISREG(identity[2]) or identity[2]&0o6000 or identity[5]<1 or identity[6]!=row['bytes']:
            raise ValueError('actual regular file identity differs')
    return candidates


def _map_rows(rows: Any, files: dict) -> list[dict]:
    if type(rows) is not list or len(rows)>MAX_FILES*16: raise ValueError('map limit')
    result=[]; previous=0
    for row in rows:
        _closed(row,{'start','end','prot','offset','path','identity'})
        start,end=_integer(row['start']),_integer(row['end'])
        _integer(row['prot'],0,7);_integer(row['offset'])
        if row['offset']%4096 or type(row['identity']) is not list or len(row['identity'])!=2 or any(type(v) is not int or v<0 for v in row['identity']): raise ValueError('map primitive identity differs')
        if start<previous or end<=start or start%4096 or end%4096 or row['prot'] not in range(8):
            raise ValueError('map interval differs')
        previous=end
        path=row['path']
        if path and path.startswith('/'):
            if path not in files or row['identity']!=files[path]['identity'][:2] or row['prot']&6==6:
                raise ValueError('unacquired or writable executable native map')
            result.append(dict(row))
        elif path not in (None,'','[heap]','[stack]','[vdso]','[vvar]','[vvar_vclock]','[vsyscall]'):
            raise ValueError('unsupported special mapping')
        elif row['prot']&4 and path not in ('[vdso]','[vsyscall]'):
            raise ValueError('anonymous executable mapping')
    return _merge_maps(result)


def _merge_maps(rows: list[dict]) -> list[dict]:
    result: list[dict]=[]
    for row in sorted(rows,key=lambda r:r['start']):
        row=dict(row)
        if result and result[-1]['end']==row['start'] and all(result[-1][k]==row[k] for k in ('prot','path','identity')) and result[-1]['offset']+result[-1]['end']-result[-1]['start']==row['offset']:
            result[-1]['end']=row['end']
        else: result.append(row)
    return result


def _cut_maps(rows: list[dict], start: int, end: int, prot: int | None = None) -> list[dict]:
    result=[]
    for row in rows:
        if row['end']<=start or row['start']>=end: result.append(dict(row)); continue
        for a,b,p in ((row['start'],min(start,row['end']),row['prot']),
                      (max(start,row['start']),min(end,row['end']),prot),
                      (max(end,row['start']),row['end'],row['prot'])):
            if a<b and p is not None:
                result.append({**row,'start':a,'end':b,'prot':p,'offset':row['offset']+a-row['start']})
    return _merge_maps(result)


def _executable_interval(maps: list[dict] | None, start: int, length: int) -> None:
    """Require every affected page to have existing acquired file provenance."""
    end=start+((length+4095)//4096)*4096
    if maps is None or end>2**64: raise ValueError('executable mapping provenance required')
    position=start
    for row in maps:
        if row['end']<=position: continue
        if row['start']>position: break
        if not row['path'] or not row['path'].startswith('/') or len(row['identity'])!=2:
            raise ValueError('executable mapping file provenance required')
        position=min(end,row['end'])
        if position==end: return
    raise ValueError('executable mapping interval is not fully acquired')


def _reconcile_maps(name: str, args: list[int], result: int, current: list[dict],
                    observed: list[dict], files: dict, mapped_file: dict | None) -> list[dict]:
    expected=current
    if result>=0:
        if name=='mmap' and not args[3]&0x20:
            if mapped_file is None: raise ValueError('acquired mmap descriptor required')
            end=result+((args[1]+4095)//4096)*4096
            expected=_cut_maps(current,result,end)
            expected=_merge_maps(expected+[{'start':result,'end':end,'prot':args[2],
                'offset':args[5],'path':mapped_file['path'],'identity':mapped_file['identity'][:2]}])
        elif name in ('munmap','mprotect'):
            expected=_cut_maps(current,args[0],args[0]+((args[1]+4095)//4096)*4096,None if name=='munmap' else args[2])
    if _map_rows(observed,files)!=expected: raise ValueError('observed/replayed file mappings differ')
    return expected


def _admit(nr: int, args: list[int], detail: dict, spec: dict, fds: dict, created: set, executed: bool, *, maps: list[dict] | None = None) -> str:
    if str(nr) not in SYSCALLS or nr&0x40000000: raise ValueError('unsupported-native-access:syscall')
    if type(args) is not list or len(args)!=6 or any(type(x) is not int or not 0<=x<2**64 for x in args):
        raise ValueError('native syscall arguments differ')
    name=SYSCALLS[str(nr)]
    if _pdf2(spec):
        if name in ('open','openat','dup','dup2','dup3') or name=='fcntl' and args[1] in (0,1030):
            if executed and not set(range(4))<=set(fds): raise ValueError('retired original channel cannot be reused')
        uses_fd=name in ('read','pread64','readv','write','writev','close','dup','dup2','dup3','fcntl','ioctl','lseek','fstat','getdents64')
        if uses_fd and args[0]==3 and name not in ('write','writev'): raise ValueError('FD3 kernel-close-only write channel')
        if name in ('dup','dup2','dup3') and (args[0] in (0,1,2,3) or name!='dup' and args[1] in (0,1,2,3)) or name=='fcntl' and args[0] in (0,1,2,3) and args[1] in (0,1030): raise ValueError('original channel aliases forbidden')
        if name in ('write','writev'):
            record=fds.get(args[0],{})
            if args[0] not in (1,2,3) or record.get('generation')!=0 or record.get('kind')!=('pdf-origin' if args[0]==3 else 'stdout' if args[0]==1 else 'stderr'): raise ValueError('only original output channels may be written')
    if name=='execve':
        _closed(detail,{'path','argv','environment','cwd'})
        if executed or detail!={'path':spec['argv'][0],'argv':spec['argv'],'environment':spec['environment'],'cwd':spec['cwd']}:
            raise ValueError('fixed initial exec differs')
    elif name in ('open','openat'):
        _closed(detail,{'path','requested_path','route'} if 'route' in detail else {'path'})
        path=_replayed_open_path(detail); flags=args[1 if nr==2 else 2]; mode=args[2 if nr==2 else 3]
        side=path in (spec['cwd']+'/syntax',spec['cwd']+'/runtime') and spec['profile'] not in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2')
        if side:
            if 'route' in detail or path in created or flags!=SIDE_FLAGS or mode!=0o600: raise ValueError('fixed exclusive sidecar creation differs')
        elif flags & ~(0x80000|0x10000|0x20000|0x800) or flags&3:
            raise ValueError('read-only dependency open required')
        elif path.startswith(('/dev/','/proc/','/sys/')):
            raise ValueError('unsupported native file type/root')
    elif name in ('read','pread64','readv','write','writev','getdents64','lseek','fstat','ioctl','fcntl','close','dup','dup2','dup3'):
        if args[0] not in fds: raise ValueError('unknown native FD generation')
        record=fds[args[0]]
        if name=='ioctl':
            _closed(detail,{'buffer_bytes'})
            if _integer(detail['buffer_bytes'],36,36)!=36: raise ValueError('fixed TCGETS buffer extent required')
            if args[0] not in (0,1,2) or record['generation']!=0 or record['kind'] not in ('stdin','stdout','stderr') or args[1]!=0x5401 or not args[2]:
                raise ValueError('only original owned-stdio TCGETS allowed')
        elif name in ('dup','dup2','dup3'):
            _closed(detail,set())
            if record['kind']=='sidecar' or name!='dup' and args[1] in fds and fds[args[1]]['kind']=='sidecar' or name=='dup3' and args[2] not in (0,0x80000):
                raise ValueError('unsupported native FD duplication')
        elif name=='fcntl':
            _closed(detail,set())
            if args[1] not in (0,1,2,3,1030) or args[1]==2 and args[2] not in (0,1) or record['kind']=='sidecar':
                raise ValueError('unsupported native fcntl')
        elif name in ('write','writev'):
            _closed(detail,{'buffer_sha256','iovecs'} if name=='writev' else {'buffer_sha256'})
            if record['kind'] not in (('stdout','stderr','pdf-origin') if _pdf2(spec) else ('stdout','stderr','sidecar')): raise ValueError('only owned stream/sidecar writes allowed')
        elif name in ('read','pread64','readv'):
            _closed(detail,{'iovecs'} if name=='readv' else set())
            if record['kind'] not in ('file','stdin'): raise ValueError('read dependency FD differs')
        elif name=='getdents64':
            _closed(detail,set())
            if record['kind']!='directory': raise ValueError('directory FD required')
        elif name=='lseek':
            _closed(detail,set())
            if record['kind']!='file' or args[2] not in (0,1,2): raise ValueError('regular file lseek required')
        else: _closed(detail,set())
    elif name=='mmap':
        _closed(detail,set())
        prot,flags,fd=args[2],args[3],args[4]
        if not args[1] or prot&~7 or prot&6==6 or flags&~(2|0x10|0x20|0x800|0x1000|0x4000|0x20000) or not flags&2:
            raise ValueError('unsupported native mapping flags')
        if flags&0x20:
            if prot&4: raise ValueError('anonymous executable map')
        elif fd not in fds or fds[fd]['kind']!='file' or args[5]%4096:
            raise ValueError('acquired file map required')
    elif name in ('mprotect','munmap','madvise'):
        _closed(detail,set())
        if not args[1] or args[0]%4096 or name=='mprotect' and (args[2]&~7 or args[2]&6==6) or name=='madvise' and args[2] not in (0,1,2,3,4,8,14,15,16,17):
            raise ValueError('unsupported native map operation')
        if name=='mprotect' and args[2]&4: _executable_interval(maps,args[0],args[1])
    elif name in ('stat','lstat','access','newfstatat','readlink','readlinkat'):
        _closed(detail,{'path'}); path=_path(detail['path'])
        if path.startswith(('/dev/','/sys/')) or path.startswith('/proc/') and not (name in ('readlink','readlinkat') and path=='/proc/self/exe'):
            raise ValueError('unsupported native lookup root')
        if name=='newfstatat' and args[3]&~0x1100 or name=='access' and args[1]&~7:
            raise ValueError('unsupported metadata flags')
    else:
        _closed(detail,set())
        if name=='arch_prctl' and args[0] not in (0x1002,0x1003): raise ValueError('arch_prctl variant')
        if name=='prlimit64' and (args[0]!=0 or args[2]!=0): raise ValueError('read-only own limit required')
        if name=='getrandom' and (args[1]>1048576 or args[2]&~3): raise ValueError('entropy variant')
        if name=='futex' and args[1] not in (0,1,9,128,129,137): raise ValueError('futex variant')
        if name=='rseq' and (args[1]!=32 or args[2]!=0): raise ValueError('rseq variant')
        if name=='set_robust_list' and args[1]!=24: raise ValueError('robust list variant')
        if name in ('rt_sigaction','rt_sigprocmask') and args[3]!=8: raise ValueError('signal ABI variant')
    if name in ('stat','lstat','fstat','newfstatat','readlink','readlinkat','getdents64','getcwd','uname','getrlimit','sysinfo','clock_gettime','prlimit64','getrandom','arch_prctl','rt_sigaction','rt_sigprocmask'):
        # The declared metadata ABI and request bounds apply before dispatch too.
        _metadata_extent({'name':name,'args':args},0)
    if name in ('readv','writev'):
        vectors=detail['iovecs']
        if type(vectors) is not list or len(vectors)!=args[2] or len(vectors)>256: raise ValueError('native iovec count differs')
        total=0
        for vector in vectors:
            if type(vector) is not list or len(vector)!=2: raise ValueError('native iovec shape differs')
            _integer(vector[0]);total+=_integer(vector[1],0,128*1048576)
            if vector[1] and not vector[0]: raise ValueError('native iovec null extent')
        if total>128*1048576: raise ValueError('native iovec limit')
    return name


def _pdf2(spec: dict) -> bool:
    return spec.get('profile')=='pdf-text-xpdf-origin/2'


def _channel_cap(spec: dict, name: str) -> int:
    if name in ('origin','pdf-origin'): return 64*1048576
    if name.endswith('/runtime'): return RUNTIME_BYTES
    if name.endswith('/syntax'): return spec['limits']['syntax_bytes']
    return spec['limits'][name+'_bytes']


def _origin_transport_prefix(previous: bytes, requested: bytes) -> None:
    if len(previous)+len(requested)>64*1048576: raise ValueError('origin stream limit')
    if previous.count(b'\n')+requested.count(b'\n')>1000002: raise ValueError('origin event transport limit')
    # Only transport bounds here; semantic map construction waits for completion.
    tail=previous[previous.rfind(b'\n')+1:]+requested
    lines=tail.split(b'\n')
    if any(len(line)+1>65536 for line in lines[:-1]) or len(lines[-1])>=65536:
        raise ValueError('origin record transport limit')


def _origin_descriptor(row: dict) -> None:
    _closed(row,{'fd','kind','identity','generation','access_mode','file_type','inheritable'})
    if type(row['fd']) is not int or row['fd']!=3 or type(row['generation']) is not int or row['generation']!=0 or row['kind']!='pdf-origin' or row['access_mode']!='write-only' or row['file_type']!='pipe' or row['inheritable'] is not True:
        raise ValueError('original FD3 write pipe required')


def _wait_record(raw_status: int, at_ns: int) -> dict:
    _integer(raw_status,0,65535);_integer(at_ns)
    if os.WIFEXITED(raw_status):
        return {'kind':'exited','raw_status':raw_status,'exit_code':os.WEXITSTATUS(raw_status),'observed_at_ns':at_ns}
    if os.WIFSIGNALED(raw_status):
        return {'kind':'signaled','raw_status':raw_status,'signal':os.WTERMSIG(raw_status),'core_dumped':bool(raw_status&128),'observed_at_ns':at_ns}
    raise ValueError('terminal raw wait required')


def _validate_wait(record: dict, returncode: int, *, success: bool) -> None:
    _closed(record,{'kind','raw_status','exit_code','observed_at_ns'} if record.get('kind')=='exited' else {'kind','raw_status','signal','core_dumped','observed_at_ns'})
    raw=_integer(record['raw_status'],0,65535);at=_integer(record['observed_at_ns'])
    expected=_wait_record(raw,at)
    if record!=expected or type(returncode) is not int: raise ValueError('actual typed wait relation differs')
    if record['kind']=='exited':
        _integer(record['exit_code'],0,255)
        if raw!=record['exit_code']<<8 or returncode!=record['exit_code']: raise ValueError('normal raw wait relation differs')
    else:
        _integer(record['signal'],1,64)
        if type(record['core_dumped']) is not bool or raw!=(record['signal']|(128 if record['core_dumped'] else 0)) or returncode!=-record['signal']: raise ValueError('signal raw wait relation differs')
    if success and record!={'kind':'exited','raw_status':0,'exit_code':0,'observed_at_ns':at}: raise ValueError('actual normal exit0 required')


def _run_identity(spec: dict, run: dict, process: dict) -> str:
    invocation={'schema':'twin.source-extraction-invocation/v1','argv':spec['argv'],'cwd':spec['cwd'],'environment':spec['environment'],'stdin':'OWNED-EOF-PIPE'}
    return sm.sha256(sm.canonical({'plan_sha256':spec['plan_sha256'],'invocation_sha256':sm.sha256(sm.canonical(invocation)),
        'started_at':run['started_at'],'monotonic_start_ns':run['monotonic_start_ns'],'process':{k:process[k] for k in ('pid','starttime','ppid','uid','gid')}}))


def _validate_native_run(observation: dict) -> None:
    run=observation['run'];events=observation['events'];terminal=events[-1]
    _closed(run,{'run_id','started_at','ended_at','monotonic_start_ns','elapsed_ns','wall_deadline_ns','cleanup_started_ns','cleanup_deadline_ns'})
    for key in ('monotonic_start_ns','elapsed_ns','wall_deadline_ns','cleanup_started_ns','cleanup_deadline_ns'): _integer(run[key])
    start=run['monotonic_start_ns'];elapsed=run['elapsed_ns'];cleanup=run['cleanup_started_ns']
    if (run['wall_deadline_ns']!=start+120*10**9 or not start<=cleanup<=start+elapsed or elapsed>120*10**9
            or run['cleanup_deadline_ns']!=min(cleanup+2*10**9,run['wall_deadline_ns']+2*10**9)
            or terminal['at_ns']!=elapsed or run['run_id']!=_run_identity(observation['spec'],run,events[0]['data'])):
        raise ValueError('original native run/deadline binding differs')
    duration=(sm._instant(run['ended_at'])-sm._instant(run['started_at'])).total_seconds()
    if duration<0 or abs(duration-elapsed/10**9)>0.01: raise ValueError('native wall/monotonic interval differs')
    custody=terminal['data']['custody']
    if abs(custody['grace_deadline']-run['cleanup_deadline_ns']/10**9)>0.000001 or custody['cleanup_ended']>start/10**9+elapsed/10**9:
        raise ValueError('shared native cleanup deadline differs')
    wait=terminal['data']['wait'];_validate_wait(wait,terminal['data']['returncode'],success=True)
    if wait['observed_at_ns']>elapsed: raise ValueError('actual wait after terminal')
    exit_stop=next(event['at_ns'] for event in events if event['kind']=='exit-stop')
    if not exit_stop<=wait['observed_at_ns']<=cleanup-start:
        raise ValueError('actual wait outside checked exit/cleanup interval')


def verify_native_observation(observation: dict, artifacts: dict[str, bytes], *, purpose: str) -> dict:
    """Independent pure replay. Never issues acquired state or invokes native code."""
    v2=observation.get('schema')=='twin.native-file-observation/v2'
    _closed(observation,{'schema','scope','purpose','spec','files','events','platform','host_policy_sha256'} | ({'run'} if v2 else set()))
    if observation['schema'] not in ('twin.native-file-observation/v1','twin.native-file-observation/v2') or observation['scope']!=SCOPE or observation['purpose']!=purpose or purpose not in ('actual','TEST_ONLY'):
        raise ValueError('native observation purpose/scope differs')
    _closed(observation['platform'],{'system','machine','release','version'})
    if observation['platform']['system']!='Linux' or observation['platform']['machine']!='x86_64' or any(type(observation['platform'][k]) is not str or not observation['platform'][k] for k in ('release','version')):
        raise ValueError('native platform identity differs')
    spec=observation['spec']; files=observation['files']; events=observation['events']
    _closed(spec,{'schema','purpose','profile','plan_sha256','argv','environment','cwd','limits','candidates'})
    if spec['schema']!=('twin.native-observation-spec/v2' if v2 else 'twin.native-observation-spec/v1') or spec['purpose']!=purpose or (spec['profile']!='pdf-text-xpdf-origin/2' if v2 else spec['profile'] not in ('utf8-identity/1','html-text-utf8/1','pdf-text-xpdf/1')) or spec['environment']!={'LC_ALL':'C','LANG':'C','TZ':'UTC'}:
        raise ValueError('native spec differs')
    _path(spec['cwd'])
    from . import source_metadata_migration as migration
    if v2:
        _closed(spec['limits'],set(migration.PROFILES[spec['profile']]))
        if any(type(value) is not int for value in spec['limits'].values()): raise ValueError('fixed native limits require exact integers')
    if spec['limits']!=migration.PROFILES[spec['profile']]: raise ValueError('fixed native profile limits differ')
    if type(spec['plan_sha256']) is not str or len(spec['plan_sha256'])!=64: raise ValueError('native plan pin differs')
    if not isinstance(spec['argv'],list) or not spec['argv'] or _path(spec['argv'][0]) not in files: raise ValueError('native executable missing')
    wanted_argv=(migration._pdf_origin_command(spec['argv'][0],spec['cwd']) if v2 else migration._pdf_command(spec['argv'][0],spec['cwd']) if spec['profile']=='pdf-text-xpdf/1' else migration._observed_command(spec['argv'][0],spec['cwd']))
    if spec['argv']!=wanted_argv: raise ValueError('fixed native argv differs')
    if purpose=='actual':
        host_policy=sm._json(_raw(artifacts,observation['host_policy_sha256']))
        _validate_host_policy(host_policy)
        if host_policy.get('scope')!=SCOPE or host_policy.get('writer_control')!='trusted-administrator-controlled-interval': raise ValueError('retained host operating assumption missing')
        for pin in host_policy['evidence_sha256s']: _raw(artifacts,pin)
    elif observation['host_policy_sha256'] is not None: raise ValueError('TEST_ONLY cannot claim actual host selection')
    candidates=_file_rows(spec,files,artifacts)
    if type(events) is not list or not events or len(events)>MAX_EVENTS or len(sm.canonical(events))>MAX_EVENT_BYTES: raise ValueError('native event limit')
    fds: dict[int,dict]={}; generations: dict[int,int]={}; descriptions: dict[int,dict]={}; created: set[str]=set(); writes={'stdout':bytearray(),'stderr':bytearray()}; eof_events={}
    if v2: writes['pdf-origin']=bytearray()
    closed_channels: set[int]=set();pending_close_eof: set[int]=set()
    pending=None; executed=False; exit_seen=False; terminal=False; current_maps: list[dict]=[]; used=set(); start=None; previous=-1
    for seq,event in enumerate(events):
        _closed(event,{'seq','at_ns','kind','data'})
        if event['seq']!=seq or type(event['seq']) is not int or _integer(event['at_ns'])<previous or event['at_ns']>spec['limits']['wall_seconds']*10**9:
            raise ValueError('native event ordering/deadline differs')
        previous=event['at_ns']; kind=event['kind']; data=event['data']
        if terminal: raise ValueError('events after terminal')
        if kind=='start':
            _closed(data,{'pid','starttime','ppid','uid','gid','fds'})
            if seq!=0 or [_integer(data[x]) for x in ('pid','starttime','ppid','uid','gid')][:3].count(0): raise ValueError('owned process lifetime required')
            start=data
            if [r['fd'] for r in data['fds']]!=(list(range(4)) if v2 else [0,1,2]) or [r['kind'] for r in data['fds']]!=(['stdin','stdout','stderr','pdf-origin'] if v2 else ['stdin','stdout','stderr']):
                raise ValueError('only original owned nonterminal stdio required')
            for row in data['fds']:
                if v2 and row['fd']==3: _origin_descriptor(row)
                else: _closed(row,{'fd','kind','identity'})
                _integer(row['fd'],0,3 if v2 else 2)
                if len(row['identity'])!=2 or any(type(v) is not int or v<0 for v in row['identity']): raise ValueError('pipe identity differs')
                fds[row['fd']]={**row,'generation':0}; generations[row['fd']]=0
        elif start is None: raise ValueError('initial lifetime stop missing')
        elif kind=='enter':
            _closed(data,{'nr','args','detail'})
            if pending is not None or exit_seen: raise ValueError('syscall entry transition differs')
            name=_admit(data['nr'],data['args'],data['detail'],spec,fds,created,executed,maps=current_maps)
            if purpose=='actual' and 'path' in data['detail'] and data['detail']['path']!='/proc/self/exe' and not _inside(data['detail']['path'],host_policy['roots']) and not data['detail']['path'].startswith(spec['cwd']+'/'):
                raise ValueError('observed path outside selected host roots')
            if not executed and name!='execve': raise ValueError('pre-exec coverage gap')
            pending={**data,'name':name}
            if name in ('write','writev'):
                requested=_raw(artifacts,data['detail']['buffer_sha256'])
                record=fds[data['args'][0]]
                key=descriptions[record['description']]['path'] if record['kind']=='sidecar' else record['kind']
                cap=_channel_cap(spec,key)
                if key=='pdf-origin': _origin_transport_prefix(bytes(writes[key]),requested)
                if len(requested)+len(writes[key])>cap: raise ValueError('write buffer limit')
                if len(requested)!=(sum(v[1] for v in data['detail']['iovecs']) if name=='writev' else data['args'][2]): raise ValueError('requested write buffer differs')
        elif kind=='exec':
            _closed(data,{'maps','executable','credentials','interpreter','interpreter_route'} | ({'fds'} if v2 else set()))
            if pending is None or pending['name']!='execve' or executed or data['executable']!=spec['argv'][0] or data['credentials']!=[start['uid'],start['gid']]: raise ValueError('initial exec stop differs')
            if type(data['credentials']) is not list or len(data['credentials'])!=2 or any(type(v) is not int for v in data['credentials']): raise ValueError('credential primitive types differ')
            if v2 and data['fds']!=start['fds']: raise ValueError('original channels changed across exec')
            current_maps=_map_rows(data['maps'],files)
            paths={r['path'] for r in current_maps}; interpreter_requested=elf_interpreter(_raw(artifacts,files[data['executable']]['sha256'])); interpreter=data['interpreter']
            if (interpreter_requested is None)!=(interpreter is None) or interpreter is not None and _path(interpreter) not in files: raise ValueError('observed interpreter route differs')
            if interpreter_requested is None:
                if data['interpreter_route'] is not None: raise ValueError('unexpected interpreter route')
            else:
                route=data['interpreter_route']
                _closed(route,{'path','requested_path','route'} if type(route) is dict and 'route' in route else {'path'})
                if route.get('requested_path',route['path'])!=interpreter_requested or _replayed_open_path(route)!=interpreter:
                    raise ValueError('ELF interpreter route binding differs')
            if data['executable'] not in paths or interpreter is not None and interpreter not in paths: raise ValueError('actual exec/interpreter maps missing')
            if paths!={data['executable']} | ({interpreter} if interpreter else set()): raise ValueError('unexplained startup mapping')
            used.update(paths); executed=True
        elif kind=='leave':
            _closed(data,{'result','detail'})
            if pending is None: raise ValueError('syscall leave without entry')
            p=pending; pending=None; name=p['name']; args=p['args']; result=_integer(data['result'],-4095,2**63-1); detail=data['detail']
            if name in ('exit','exit_group'): raise ValueError('exit syscall must terminate')
            if name=='execve' and (not executed or result!=0): raise ValueError('exec failed/incomplete')
            if name in ('open','openat'):
                path=p['detail']['path']; flags=args[1 if name=='open' else 2]
                if result>=0:
                    _closed(detail,{'identity','kind'})
                    if result in fds: raise ValueError('opened occupied descriptor')
                    generation=generations.get(result,-1)+1; generations[result]=generation
                    side=path in (spec['cwd']+'/syntax',spec['cwd']+'/runtime') and spec['profile'] not in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2')
                    if side:
                        identity=detail['identity']
                        if detail['kind']!='sidecar' or len(identity)!=9 or identity[2]!=0o100600 or identity[3]!=start['uid'] or identity[5]!=1 or identity[6]!=0:
                            raise ValueError('actual exclusive output identity differs')
                        created.add(path); writes[path]=bytearray()
                    elif detail['kind']=='file':
                        if path not in files or detail['identity']!=files[path]['identity']: raise ValueError('actual opened dependency differs')
                        used.add(path)
                    elif detail['kind']!='directory' or not flags&0x10000 or path not in {str(Path(x).parent) for x in candidates}:
                        raise ValueError('unacquired directory open')
                    descriptions[seq]={'offset':0,'path':path,'identity':detail['identity'],'kind':detail['kind']}
                    fds[result]={'generation':generation,'description':seq,'kind':detail['kind'],'identity':detail['identity'][:2]}
                else: _closed(detail,set())
            elif name in ('read','pread64','readv'):
                _closed(detail,{'buffer_sha256','buffer_bytes'})
                count_bytes=_integer(detail['buffer_bytes'],0,128*1048576)
                record=fds[args[0]]
                if result<0:
                    if count_bytes or detail['buffer_sha256']!=sm.sha256(b''): raise ValueError('failed read buffer')
                elif record['kind']=='stdin':
                    if result!=0 or count_bytes or detail['buffer_sha256']!=sm.sha256(b''): raise ValueError('owned stdin must be EOF')
                else:
                    desc=descriptions[record['description']]; content=_raw(artifacts,files[desc['path']]['sha256']); offset=args[3] if name=='pread64' else desc['offset']
                    count=sum(v[1] for v in p['detail']['iovecs']) if name=='readv' else args[2]
                    if result!=count_bytes or len(content[offset:offset+result])!=result or detail['buffer_sha256']!=sm.sha256(content[offset:offset+result]) or result>count or result==0 and count>0 and offset<len(content): raise ValueError('actual read slice differs')
                    if name!='pread64': desc['offset']+=result
            elif name in ('write','writev'):
                _closed(detail,set())
                if result>=0:
                    requested=_raw(artifacts,p['detail']['buffer_sha256']); record=fds[args[0]]
                    if result>len(requested): raise ValueError('partial write differs')
                    key=descriptions[record['description']]['path'] if record['kind']=='sidecar' else record['kind']
                    if key=='pdf-origin' and requested and result==0: raise ValueError('origin write made no progress')
                    writes[key].extend(requested[:result]); cap=_channel_cap(spec,key)
                    if len(writes[key])>cap: raise ValueError('native stream/sidecar overflow')
                elif v2 and fds[args[0]]['kind']=='pdf-origin' and result!=-errno.EINTR: raise ValueError('origin write error')
            elif name=='close':
                _closed(detail,set())
                if result==0:
                    if v2 and args[0] in (1,2) and fds[args[0]]['generation']==0:
                        closed_channels.add(args[0]);pending_close_eof.discard(args[0])
                    del fds[args[0]]
                elif v2 and args[0] in pending_close_eof: raise ValueError('EOF requires successful original channel closure')
                elif fds[args[0]]['kind']=='sidecar': raise ValueError('uncertain sidecar close')
            elif name in ('dup','dup2','dup3'):
                _closed(detail,set())
                if result>=0:
                    if name!='dup' and result!=args[1]: raise ValueError('dup target result differs')
                    if result!=args[0]:
                        generations[result]=generations.get(result,-1)+1;fds[result]={**fds[args[0]],'generation':generations[result]}
            elif name=='fcntl':
                _closed(detail,set())
                if args[1] in (0,1030) and result>=0:
                    if result in fds: raise ValueError('dup target occupied')
                    generations[result]=generations.get(result,-1)+1; fds[result]={**fds[args[0]],'generation':generations[result]}
            elif name=='lseek':
                _closed(detail,set())
                if result>=0: descriptions[fds[args[0]]['description']]['offset']=result
            elif name=='ioctl':
                _closed(detail,set())
                if result!=-errno.ENOTTY: raise ValueError('owned TCGETS must fail ENOTTY')
            elif name in ('mmap','munmap','mprotect','brk'):
                _closed(detail,{'maps'})
                mapped_description=descriptions[fds[args[4]]['description']] if name=='mmap' and not args[3]&0x20 else None
                current_maps=_reconcile_maps(name,args,result,current_maps,detail['maps'],files,mapped_description)
                if mapped_description is not None and result>=0: used.add(mapped_description['path'])
            else:
                # Every output buffer is retained; no untracked extra data is accepted.
                _closed(detail,{'buffer_sha256'} if name in ('stat','lstat','fstat','newfstatat','readlink','readlinkat','getdents64','getcwd','uname','getrlimit','sysinfo','clock_gettime','prlimit64','getrandom','arch_prctl','rt_sigaction','rt_sigprocmask') else set())
                if detail:
                    identity=None;fd_kind=None
                    if name=='fstat':
                        record=fds[args[0]];fd_kind=record['kind']
                        identity=descriptions[record['description']]['identity'] if 'description' in record else record['identity']
                        if fd_kind=='sidecar': identity=identity[:6]  # size/times change through owned writes
                    _validate_metadata_result(p,result,_raw(artifacts,detail['buffer_sha256']),spec,files,identity,observation['platform'],fd_kind=fd_kind)
                elif name=='access' and result>0: raise ValueError('access success status differs')
        elif kind=='exit-stop':
            _closed(data,{'status','maps','fds','pid','starttime'})
            _integer(data['status'],0,0);_integer(data['pid']);_integer(data['starttime'])
            if not executed or exit_seen or pending is None or pending['name'] not in ('exit','exit_group') or pending['args'][0]!=0 or data['status']!=0 or data['pid']!=start['pid'] or data['starttime']!=start['starttime']:
                raise ValueError('complete terminal lifetime differs')
            if _map_rows(data['maps'],files)!=current_maps: raise ValueError('unexplained final mapping')
            expected=[{'fd':fd,'kind':r['kind'],'identity':r['identity']} for fd,r in sorted(fds.items())]
            if v2 and (3 not in fds or fds[3]['generation']!=0 or fds[3]['identity']!=start['fds'][3]['identity']): raise ValueError('original FD3 missing at exit-stop')
            if data['fds']!=expected or any(r['kind']=='sidecar' for r in fds.values()): raise ValueError('final descriptor/sidecar closure differs')
            pending=None; exit_seen=True
        elif kind=='pipe-eof' and v2:
            _closed(data,{'channel','fd','generation','identity','request_bytes','result','captured_bytes'})
            channel=data['channel'];expected_fd={'stdout':1,'stderr':2,'origin':3}.get(channel)
            if expected_fd is None or channel in eof_events or data['fd']!=expected_fd or type(data['fd']) is not int or _integer(data['generation'],0,0)!=0 or data['identity']!=start['fds'][expected_fd]['identity'] or _integer(data['request_bytes'],1,65536)<1 or _integer(data['result'],0,0)!=0 or _integer(data['captured_bytes'])!=len(writes['pdf-origin' if channel=='origin' else channel]): raise ValueError('original positive-capacity pipe EOF differs')
            if not exit_seen and expected_fd not in closed_channels:
                # The kernel may close stdio before the tracer consumes its leave.
                # This provisional EOF must be discharged by that exact close's
                # successful result; origin remains kernel-exit-only.
                if (expected_fd==3 or pending is None or pending['name']!='close'
                        or pending['args'][0]!=expected_fd or fds[expected_fd]['generation']!=0):
                    raise ValueError('original channel EOF precedes checked closure')
                pending_close_eof.add(expected_fd)
            eof_events[channel]=seq
        elif kind=='terminal':
            _closed(data,{'returncode','stdout_sha256','stderr_sha256','sidecars','eof','reaped','cleanup','custody'} | ({'origin_sha256','origin_bytes','wait'} if v2 else set()))
            _integer(data['returncode'],0,0)
            if not exit_seen or data['returncode']!=0 or data['eof']!=(['stdout','stderr','origin'] if v2 else ['stdout','stderr']) or data['reaped']!=[start['pid']] or data['cleanup']!='owned-workspace-removed': raise ValueError('incomplete EOF/reap/cleanup')
            validate_native_custody(data['custody'],pid=start['pid'],reaped=data['reaped'])
            for name in ('stdout','stderr'):
                if _raw(artifacts,data[name+'_sha256'])!=bytes(writes[name]): raise ValueError('observed stream/write replay differs')
            if v2:
                if pending_close_eof or set(eof_events)!={'stdout','stderr','origin'} or _raw(artifacts,data['origin_sha256'])!=bytes(writes['pdf-origin']) or _integer(data['origin_bytes'])!=len(writes['pdf-origin']): raise ValueError('complete origin write/capture/EOF relation differs')
                _validate_wait(data['wait'],data['returncode'],success=True)
            wanted=set() if spec['profile'] in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2') else {spec['cwd']+'/runtime',spec['cwd']+'/syntax'}
            if created!=wanted or set(data['sidecars'])!=wanted: raise ValueError('both fixed sidecars required')
            for path,row in data['sidecars'].items():
                _closed(row,{'sha256','identity'})
                if type(row['identity']) is not list or len(row['identity'])!=9 or any(type(v) is not int or v<0 for v in row['identity']): raise ValueError('sidecar final identity type differs')
                descs=[d for d in descriptions.values() if d['path']==path]
                if len(descs)!=1 or row['identity'][:6]!=descs[0]['identity'][:6] or row['identity'][6]!=len(writes[path]) or _raw(artifacts,row['sha256'])!=bytes(writes[path]): raise ValueError('final exact sidecar/write replay differs')
            terminal=True
        else: raise ValueError('unknown native stop')
    if not terminal: raise ValueError('native trace incomplete')
    if v2:
        _validate_native_run(observation)
        from . import pdf_native_bridge as bridge
        buffers=set()
        for event in events:
            data=event['data'];detail=data.get('detail',{})
            if 'buffer_sha256' in detail and 'buffer_bytes' not in detail: buffers.add(detail['buffer_sha256'])
        buffers.update(events[-1]['data'][name+'_sha256'] for name in ('stdout','stderr','origin'))
        if sum(len(_raw(artifacts,pin)) for pin in buffers)>bridge.BUFFER_BYTES: raise ValueError('native retained-buffer limit')
    return {'scope':SCOPE,'purpose':purpose,'used_paths':sorted(used),'stdout_bytes':len(writes['stdout']),'stderr_bytes':len(writes['stderr']),'plan_sha256':spec['plan_sha256'],**({'origin_bytes':len(writes['pdf-origin'])} if v2 else {})}


def _result_digest(value: Any) -> bytes:
    if type(value) is bytes: return sm.canonical({'bytes':len(value),'sha256':sm.sha256(value)})
    if type(value) is dict: return sm.canonical({k:sm.sha256(_result_digest(v)) for k,v in value.items()})
    if type(value) in (list,tuple): return sm.canonical([sm.sha256(_result_digest(v)) for v in value])
    return sm.canonical(value)


def _deposit(store: NativeObservationStore, result: dict, observation: dict, *, held_plan: dict | None = None) -> ObservedExtraction:
    store._guard.verify()
    handle=object.__new__(ObservedExtraction)
    object.__setattr__(handle,'token',object())
    held=copy.deepcopy(result)
    entry: tuple=(handle,held,_result_digest(held),copy.deepcopy(observation))
    if _pdf2(observation['spec']):
        from . import pdf_native_bridge as bridge
        if store._purpose!='actual' or held_plan is None: raise ValueError('final actual PDF acquisition only')
        bridge.verify_pdf_extraction_bundle(held_plan,_raw(held['archive'],held_plan['parent_sha256']),held)
        entry=entry+(sm.canonical({k:v for k,v in held_plan.items() if k!='archive'}),)
    store._guard.verify()
    store._entries[id(handle)]=entry
    return handle


def freeze_native_host_context(policy: dict, evidence: dict[str,bytes], expected_policy_sha256: str) -> NativeHostContext:
    """Freeze a host's independent selection, never infer writer control from packet data.

    This constructor conserves selection; any caller choosing a policy does not make
    it approved. The trusted custodian controls writers during the chosen interval.
    """
    policy_raw=sm.canonical(policy)
    policy=sm._json(policy_raw)
    evidence=dict(evidence)
    _validate_host_policy(policy)
    if sm.sha256(policy_raw)!=expected_policy_sha256 or policy['schema']!='twin.native-host-policy/v1' or policy['scope']!=SCOPE or not isinstance(policy['custodian'],str) or not policy['custodian'] or policy['writer_control']!='trusted-administrator-controlled-interval':
        raise ValueError('independently selected host policy differs')
    before,after=sm._instant(policy['not_before']),sm._instant(policy['not_after'])
    if after<=before or (after-before).total_seconds()>3600 or not isinstance(policy['roots'],list) or not policy['roots'] or len(set(policy['roots']))!=len(policy['roots']):
        raise ValueError('bounded host writer interval/roots required')
    for path in policy['roots']:
        if _path(path)=='/': raise ValueError('exact bounded host roots required')
    if not isinstance(policy['evidence_sha256s'],list) or not policy['evidence_sha256s'] or set(policy['evidence_sha256s'])!=set(evidence):
        raise ValueError('independent writer-control evidence absent')
    if sum(len(_raw(evidence,pin)) for pin in evidence)>MAX_EVENT_BYTES: raise ValueError('bounded host evidence required')
    for pin in evidence: _raw(evidence,pin)
    context=object.__new__(NativeHostContext)
    object.__setattr__(context,'_policy',policy_raw)
    object.__setattr__(context,'_evidence',dict(evidence))
    object.__setattr__(context,'_guard',_guard())
    return context


def decode_syscall_info(raw: bytes, returned: int) -> dict:
    """Decode the kernel v6.8 UAPI, rejecting truncation and compatibility ABIs."""
    if type(raw) is not bytes or not 24<=returned<=len(raw) or len(raw)>128 or struct.unpack_from('<I',raw,4)[0]!=ARCH:
        raise ValueError('unsupported/truncated native syscall-info')
    if raw[0]==1 and returned>=80:
        values=struct.unpack_from('<7Q',raw,24)
        if values[0]&0x40000000: raise ValueError('unsupported x32 syscall')
        return {'op':'enter','nr':values[0],'args':list(values[1:])}
    if raw[0]==2 and returned>=33:
        result=struct.unpack_from('<q',raw,24)[0]
        if result in (-512,-513,-514,-516): raise ValueError('unsupported syscall restart')
        if raw[32] not in (0,1) or bool(raw[32]) != (-4095<=result<0): raise ValueError('native syscall error discriminator differs')
        return {'op':'leave','result':result}
    raise ValueError('unknown/truncated native syscall stop')


def _ptrace(request: int, pid: int, address: int = 0, data: int = 0) -> int:
    libc=ctypes.CDLL(None,use_errno=True)
    fn=libc.ptrace; fn.restype=ctypes.c_long
    fn.argtypes=[ctypes.c_uint,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
    ctypes.set_errno(0)
    result=fn(request,pid,address,data)
    if result==-1 and ctypes.get_errno(): raise OSError(ctypes.get_errno(),'ptrace operation failed')
    return int(result)


def _syscall_stop(pid: int) -> dict:
    buffer=ctypes.create_string_buffer(128)
    size=_ptrace(0x420e,pid,128,ctypes.addressof(buffer))
    return decode_syscall_info(buffer.raw,size)


def _memory(fd: int, address: int, size: int) -> bytes:
    _integer(address);_integer(size,0,128*1048576)
    if not size: return b''
    if not address or address+size>2**64: raise ValueError('invalid native memory extent')
    raw=os.pread(fd,size,address)
    if len(raw)!=size: raise ValueError('short native memory observation')
    return raw


def _cstring(fd: int, address: int) -> str:
    out=bytearray()
    while len(out)<=MAX_PATH:
        block=_memory(fd,address+len(out),1)
        if block==b'\0': return bytes(out).decode('utf8',errors='strict')
        out.extend(block)
    raise ValueError('native path/string limit')


def _string_vector(fd: int, address: int) -> list[str]:
    values: list[str]=[]
    for index in range(256):
        ptr=struct.unpack('<Q',_memory(fd,address+index*8,8))[0]
        if not ptr: return values
        values.append(_cstring(fd,ptr))
    raise ValueError('native argv/environment limit')


def _identity(info: os.stat_result) -> list[int]:
    return [info.st_dev,info.st_ino,info.st_mode,info.st_uid,info.st_gid,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns]


def _put(artifacts: dict, raw: bytes) -> str:
    pin=sm.sha256(raw);artifacts[pin]=raw;return pin


def _lifetime(proc: Path) -> dict:
    raw=(proc/'stat').read_text(); fields=raw.rsplit(')',1)[1].split()
    status={k:v.strip() for k,v in (line.split(':',1) for line in (proc/'status').read_text().splitlines() if ':' in line)}
    uids=[int(x) for x in status['Uid'].split()]; gids=[int(x) for x in status['Gid'].split()]
    if len(set(uids))!=1 or len(set(gids))!=1 or int(status['Threads'])!=1:
        raise ValueError('native credentials/thread count differ')
    return {'pid':int(raw.split('(',1)[0]),'starttime':int(fields[19]),'ppid':int(fields[1]),'uid':uids[0],'gid':gids[0]}


def _maps(proc: Path) -> list[dict]:
    rows=[]
    raw=(proc/'maps').read_bytes()
    if len(raw)>4*1048576: raise ValueError('native map observation limit')
    for line in raw.decode().splitlines():
        parts=line.split(maxsplit=5); start,end=(int(x,16) for x in parts[0].split('-')); perms=parts[1]
        path=parts[5] if len(parts)==6 else None
        if path and path.endswith(' (deleted)'): raise ValueError('deleted native mapping')
        devmajor,devminor=(int(x,16) for x in parts[3].split(':'))
        if path and path.startswith('/'): path=os.path.realpath(path)
        rows.append({'start':start,'end':end,'prot':(1 if perms[0]=='r' else 0)|(2 if perms[1]=='w' else 0)|(4 if perms[2]=='x' else 0),
                     'offset':int(parts[2],16),'path':path,'identity':[os.makedev(devmajor,devminor),int(parts[4])]})
        if perms[3]=='s' and perms[1]=='w' and path and path.startswith('/'):
            raise ValueError('writable shared file mapping')
    return rows


def _fd_snapshot(proc: Path, records: dict[int,dict]) -> list[dict]:
    rows=[]
    for entry in sorted((proc/'fd').iterdir(),key=lambda p:int(p.name)):
        fd=int(entry.name)
        if fd not in records: raise ValueError('unexplained inherited/created descriptor')
        info=entry.stat(); r=records[fd]
        if [info.st_dev,info.st_ino]!=r['identity']: raise ValueError('native FD identity changed')
        if r['kind'] in ('stdin','stdout','stderr') and not stat.S_ISFIFO(info.st_mode): raise ValueError('owned nonterminal pipe required')
        rows.append({'fd':fd,'kind':r['kind'],'identity':r['identity']})
    if {r['fd'] for r in rows}!=set(records): raise ValueError('missing native descriptor')
    return rows


def _read_fd(fd: int, cap: int) -> bytes:
    size=os.fstat(fd).st_size
    if not 0<=size<=cap: raise ValueError('native acquired file limit')
    raw=os.pread(fd,size,0)
    if len(raw)!=size: raise ValueError('short acquired file')
    return raw


def _host_window(context: NativeHostContext, *, verify_guard: bool = True) -> dict:
    if verify_guard: context._guard.verify()
    policy=sm._json(context._policy)
    now=datetime.datetime.now(datetime.timezone.utc)
    if not sm._instant(policy['not_before'])<=now<sm._instant(policy['not_after']): raise ValueError('host writer interval unavailable')
    for pin in policy['evidence_sha256s']: _raw(context._evidence,pin)
    return policy


def _inside(path: str, roots: list[str]) -> bool:
    return any(path==root or path.startswith(root+'/') for root in roots)


def _acquire_candidates(spec: dict, artifacts: dict, context: NativeHostContext) -> tuple[dict,dict]:
    started=time.monotonic(); policy=_host_window(context); held={}; files={}
    try:
        total=0
        for row in spec['candidates']:
            if time.monotonic()-started>PREPARE_SECONDS: raise ValueError('native preparation deadline')
            path=_path(row['path'])
            resolved,route=_observe_open_route(path)
            if resolved!=path or route: raise ValueError('candidate must use acquired canonical source path')
            if not _inside(path,policy['roots']) and not path.startswith(spec['cwd']+'/'): raise ValueError('candidate outside independently selected host roots')
            fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
            held[path]=fd; before=os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_mode&0o6022: raise ValueError('mutable/special/privileged native candidate')
            try:
                capability=os.getxattr(fd,'security.capability')
            except OSError as exc:
                if exc.errno!=errno.ENODATA: raise
            else:
                if capability: raise ValueError('file-capability native candidate unsupported')
            raw=_read_fd(fd,MAX_DEPENDENCY_BYTES)
            if path!=spec['cwd']+'/input': total+=len(raw)
            if total>MAX_DEPENDENCY_BYTES or len(held)>MAX_FILES: raise ValueError('native dependency limit')
            if _identity(before)!=_identity(os.fstat(fd)) or sm.sha256(raw)!=row['sha256'] or len(raw)!=row['bytes'] or raw!=_raw(artifacts,row['sha256']): raise ValueError('native candidate byte/identity drift')
            files[path]={**row,'identity':_identity(before)}
        _host_window(context)
        return held,files
    except BaseException:
        for fd in held.values(): os.close(fd)
        raise


def _target_path(mem: int, proc: Path, address: int, dirfd: int = 2**64-100) -> str:
    text=_cstring(mem,address)
    if '..' in text.split('/'): raise ValueError('unsupported parent traversal in native path')
    if text.startswith('/'): return os.path.normpath(text)
    base=os.readlink(proc/'cwd') if dirfd==2**64-100 else os.readlink(proc/'fd'/str(dirfd))
    return os.path.normpath(base+'/'+text)


def _iovecs(mem: int, address: int, count: int) -> list[tuple[int,int]]:
    _integer(count,0,256); values=[];total=0
    for i in range(count):
        base,size=struct.unpack('<QQ',_memory(mem,address+i*16,16));total+=size
        if total>128*1048576: raise ValueError('native iovec limit')
        values.append((base,size))
    return values


def _entry_detail(stop: dict, mem: int, proc: Path, artifacts: dict, budget: dict) -> dict:
    nr,a=stop['nr'],stop['args']; name=SYSCALLS.get(str(nr))
    if name=='execve':
        env=_string_vector(mem,a[2]); pairs=[v.split('=',1) for v in env]
        if any(len(p)!=2 for p in pairs) or len({p[0] for p in pairs})!=len(pairs): raise ValueError('native environment differs')
        return {'path':_target_path(mem,proc,a[0]),'argv':_string_vector(mem,a[1]),'environment':dict(pairs),'cwd':os.readlink(proc/'cwd')}
    if name in ('open','openat'):
        requested=_target_path(mem,proc,a[0] if name=='open' else a[1],2**64-100 if name=='open' else a[0])
        resolved,route=_observe_open_route(requested)
        return {'path':resolved,**({'requested_path':requested,'route':route} if route else {})}
    if name in ('stat','lstat','access','readlink'): return {'path':_target_path(mem,proc,a[0])}
    if name in ('newfstatat','readlinkat'): return {'path':_target_path(mem,proc,a[1],a[0])}
    if name=='ioctl':
        _memory(mem,a[2],36)
        return {'buffer_bytes':36}
    if name=='readv': return {'iovecs':[list(v) for v in _iovecs(mem,a[1],a[2])]}
    if name in ('write','writev'):
        vectors=_iovecs(mem,a[1],a[2]) if name=='writev' else []
        raw=_memory(mem,a[1],a[2]) if name=='write' else b''.join(_memory(mem,b,s) for b,s in vectors)
        return {'buffer_sha256':_runtime_blob(artifacts,raw,budget),**({'iovecs':[list(v) for v in vectors]} if name=='writev' else {})}
    return {}


def _metadata_extent(pending: dict, result: int) -> tuple[int,int]:
    """x86_64 kernel output ABI; reject impossible counts before reading memory."""
    name=pending['name'];a=pending['args']
    if result<0: return 0,0
    variable={'readlink':(1,2,MAX_PATH),'readlinkat':(2,3,MAX_PATH),
              'getcwd':(0,1,MAX_PATH),'getdents64':(1,2,1048576),'getrandom':(0,1,1048576)}
    if name in variable:
        at,count,cap=variable[name]
        _integer(a[count],0,cap)
        if result>a[count] or result and not a[at]: raise ValueError('metadata returned extent exceeds requested buffer')
        return a[at],result
    sizes={'stat':(1,144),'lstat':(1,144),'fstat':(1,144),'newfstatat':(2,144),
        'uname':(0,390),'getrlimit':(1,16),'sysinfo':(0,112),'clock_gettime':(1,16),
        'prlimit64':(3,16),'arch_prctl':(1,8),'rt_sigaction':(2,32),'rt_sigprocmask':(2,8)}
    if name not in sizes or result!=0: raise ValueError('metadata success status differs')
    at,size=sizes[name]
    if name=='arch_prctl' and a[0]==0x1002: return 0,0
    optional=name in ('prlimit64','rt_sigaction','rt_sigprocmask')
    if not a[at]:
        if optional: return 0,0
        raise ValueError('successful metadata requires output pointer')
    return a[at],size


def _validate_metadata_result(pending: dict, result: int, raw: bytes, spec: dict,
                              files: dict, fd_identity: list | None, platform_record: dict,
                              *, fd_kind: str | None = None) -> None:
    name=pending['name'];a=pending['args'];_,extent=_metadata_extent(pending,result)
    if len(raw)!=extent: raise ValueError('metadata retained output extent differs')
    if result<0: return
    if name in ('readlink','readlinkat'):
        if not raw or b'\0' in raw: raise ValueError('invalid readlink output')
        if pending['detail']['path']=='/proc/self/exe':
            capacity=a[2 if name=='readlink' else 3];expected=spec['argv'][0].encode('utf8')[:capacity]
            if raw!=expected: raise ValueError('proc exe does not name actual fixed executable')
    elif name=='getcwd':
        if raw!=spec['cwd'].encode('utf8')+b'\0': raise ValueError('metadata cwd differs from fixed cwd')
    elif name in ('stat','lstat','fstat','newfstatat'):
        dev,ino,nlink=struct.unpack_from('<QQQ',raw)
        mode,uid,gid=struct.unpack_from('<III',raw,24);size=struct.unpack_from('<q',raw,48)[0]
        times=struct.unpack_from('<qqqqqq',raw,72)
        if mode&0o170000 not in (0o010000,0o020000,0o040000,0o060000,0o100000,0o120000,0o140000) or size<0 or any(not 0<=v<10**9 for v in times[1::2]):
            raise ValueError('metadata stat ABI values differ')
        identity=[dev,ino,mode,uid,gid,nlink,size,times[2]*10**9+times[3],times[4]*10**9+times[5]]
        known=fd_identity if name=='fstat' else files.get(pending['detail']['path'],{}).get('identity')
        if known is not None and identity[:len(known)]!=known: raise ValueError('metadata stat known identity differs')
        if name=='fstat':
            kinds={'stdin':stat.S_IFIFO,'stdout':stat.S_IFIFO,'stderr':stat.S_IFIFO,
                   'file':stat.S_IFREG,'directory':stat.S_IFDIR,'sidecar':stat.S_IFREG}
            if fd_kind not in kinds or stat.S_IFMT(mode)!=kinds[fd_kind]:
                raise ValueError('metadata stat descriptor kind differs')
    elif name=='getdents64':
        offset=0
        while offset<len(raw):
            if len(raw)-offset<24: raise ValueError('truncated linux_dirent64')
            _,_,size,kind=struct.unpack_from('<QqHB',raw,offset)
            if size<24 or size%8 or offset+size>len(raw) or kind not in (0,1,2,4,6,8,10,12,14): raise ValueError('invalid linux_dirent64 extent/type')
            field=raw[offset+19:offset+size];end=field.find(b'\0')
            if end<=0 or b'/' in field[:end]: raise ValueError('invalid linux_dirent64 name')
            offset+=size
    elif name=='uname':
        fields=[raw[i:i+65] for i in range(0,390,65)]
        if any(b'\0' not in v for v in fields): raise ValueError('unterminated utsname field')
        values=[v.split(b'\0',1)[0] for v in fields]
        if any(values[i]!=platform_record[k].encode('utf8') for i,k in ((0,'system'),(2,'release'),(3,'version'),(4,'machine'))): raise ValueError('utsname platform differs')
    elif name in ('getrlimit','prlimit64') and raw:
        soft,hard=struct.unpack('<QQ',raw)
        if soft>hard: raise ValueError('invalid rlimit extent values')
    elif name=='clock_gettime':
        _,nanoseconds=struct.unpack('<qq',raw)
        if not 0<=nanoseconds<10**9: raise ValueError('invalid timespec nanoseconds')
    elif name=='sysinfo':
        if struct.unpack_from('<q',raw)[0]<0 or not struct.unpack_from('<I',raw,104)[0]: raise ValueError('invalid sysinfo ABI values')


def _result_buffer(pending: dict, result: int, mem: int) -> bytes:
    name=pending['name'];a=pending['args']
    if result<0: return b''
    if name in ('read','pread64'):
        if result>a[2]: raise ValueError('read result exceeds requested extent')
        return _memory(mem,a[1],result)
    if name=='readv':
        remain=result;out=bytearray()
        for base,size in pending['detail']['iovecs']:
            amount=min(remain,size);out.extend(_memory(mem,base,amount));remain-=amount
        if remain: raise ValueError('native readv result exceeds iovec')
        return bytes(out)
    address,size=_metadata_extent(pending,result)
    return _memory(mem,address,size) if size else b''


def _append(events: list, kind: str, data: dict, start: float, limits: dict, *, budget: dict | None = None) -> None:
    elapsed=time.monotonic()-start
    if elapsed>=limits['wall_seconds'] or len(events)>=MAX_EVENTS: raise ValueError('native observation deadline/event limit')
    event={'seq':len(events),'at_ns':int(elapsed*10**9),'kind':kind,'data':data}
    size=len(sm.canonical(event))
    total=(budget['bytes']+size+(1 if events else 0)) if budget is not None else len(sm.canonical(events+[event]))
    if total>MAX_EVENT_BYTES: raise ValueError('native event limit')
    if budget is not None: budget['bytes']=total
    events.append(event)


def _native_signal(target: str, pid: int, sig: int, signals: list[dict]) -> None:
    try:
        (os.killpg if target=='group' else os.kill)(pid,sig)
        outcome='sent'
    except ProcessLookupError: outcome='absent'
    except PermissionError: outcome='permission-denied'
    except OSError: outcome='os-error'
    signals.append({'target':target,'pid':pid,'signal':int(sig),'outcome':outcome})


def _finish_native_custody(pid: int | None, descendants: set[int], reaped: list[int],
                           returncode: int | None, *, deadline: float) -> tuple[dict,int | None]:
    """One original deadline for TERM, KILL and every owned traced descendant."""
    signals: list[dict]=[];targets=sorted(({pid} if pid else set())|descendants)
    if pid is not None and pid not in reaped and time.monotonic()<deadline:
        _native_signal('group',pid,signal.SIGTERM,signals)
    for child in targets:
        if child not in reaped and time.monotonic()<deadline: _native_signal('pid',child,signal.SIGTERM,signals)
    midpoint=time.monotonic()+max(0,deadline-time.monotonic())/2
    for sig,until in ((signal.SIGTERM,midpoint),(signal.SIGKILL,deadline)):
        if sig==signal.SIGKILL:
            # A reaped leader no longer reserves its process-group number.
            if pid is not None and pid not in reaped and time.monotonic()<deadline:
                _native_signal('group',pid,sig,signals)
            for child in targets:
                if child not in reaped and time.monotonic()<deadline: _native_signal('pid',child,sig,signals)
        while any(child not in reaped for child in targets) and time.monotonic()<until:
            for child in targets:
                if child in reaped or time.monotonic()>=until: continue
                try: got,status=os.waitpid(child,os.WNOHANG|os.WUNTRACED|0x40000000)
                except (ChildProcessError,OSError): continue
                if got and (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                    reaped.append(child)
                    if child==pid: returncode=os.waitstatus_to_exitcode(status)
                # Never resume a stopped doomed target: it may be at a refused
                # syscall or unsafe mapping. SIGKILL does not require a ptrace
                # userspace continuation; absent terminal wait remains a hold.
            if any(child not in reaped for child in targets): time.sleep(min(.001,max(0,until-time.monotonic())))
    probe='not-observed'
    if pid is not None and all(child in reaped for child in targets) and time.monotonic()<deadline:
        try: os.killpg(pid,0);probe='present'
        except ProcessLookupError: probe='absent'
        except PermissionError: probe='permission-denied'
        except OSError: probe='os-error'
    ended=time.monotonic()
    return {'schema':'twin.native-custody/v1','leader_pid':pid,'reservation':'traced-owned-lifetime',
        'signals':signals,'direct_child_reaped':pid is not None and pid in reaped,
        'absence_verified':probe=='absent' and ended<=deadline,
        'absence_probe':probe,'descendants':sorted(descendants),'reaped':sorted(reaped),
        'grace_deadline':deadline,'cleanup_ended':ended},returncode


def validate_native_custody(custody: dict, *, pid: int | None = None, reaped: list[int] | None = None) -> None:
    _closed(custody,{'schema','leader_pid','reservation','signals','direct_child_reaped','absence_verified',
        'absence_probe','descendants','reaped','grace_deadline','cleanup_ended'})
    leader=_integer(custody['leader_pid'],1)
    if custody['schema']!='twin.native-custody/v1' or custody['reservation']!='traced-owned-lifetime' or custody['direct_child_reaped'] is not True or custody['absence_verified'] is not True or custody['absence_probe']!='absent':
        raise ValueError('native terminal custody unestablished')
    children=custody['descendants'];waited=custody['reaped']
    if type(children) is not list or type(waited) is not list or children!=sorted(set(children)) or waited!=sorted(set(waited)):
        raise ValueError('native custody PID inventory differs')
    for child in children+waited: _integer(child,1)
    if leader in children or waited!=sorted([leader]+children) or pid is not None and leader!=pid or reaped is not None and waited!=sorted(reaped): raise ValueError('native custody owned lifetime differs')
    for key in ('grace_deadline','cleanup_ended'):
        value=custody[key]
        if type(value) not in (int,float) or not 0<=value<float('inf'): raise ValueError('native cleanup deadline differs')
    if custody['cleanup_ended']>custody['grace_deadline']: raise ValueError('native cleanup exceeded original grace')
    if type(custody['signals']) is not list: raise ValueError('native cleanup signal inventory differs')
    for record in custody['signals']:
        _closed(record,{'target','pid','signal','outcome'})
        _integer(record['pid'],1);_integer(record['signal'])
        if record['target'] not in ('group','pid') or record['pid'] not in waited or record['target']=='group' and record['pid']!=leader or record['signal'] not in (signal.SIGTERM,signal.SIGKILL) or record['outcome'] not in ('sent','absent','permission-denied','os-error'):
            raise ValueError('native cleanup signal observation differs')


def _install_child_channels(channels: list[int]) -> None:
    """Collision-safe owned pre-exec setup; called only by actual fork child."""
    copies=[fcntl.fcntl(fd,fcntl.F_DUPFD_CLOEXEC,4) for fd in channels]
    for target,source in enumerate(copies): os.dup2(source,target,inheritable=True)
    for entry in list(Path('/proc/self/fd').iterdir()):
        number=int(entry.name)
        if number>=len(channels):
            try: os.close(number)
            except OSError: pass


def _channel_snapshot(proc: Path, records: dict[int,dict]) -> list[dict]:
    rows=_fd_snapshot(proc,records)
    if 3 not in records or records[3]['kind']!='pdf-origin' or records[3]['generation']!=0: raise ValueError('original native FD3 required')
    info=(proc/'fd'/'3').stat()
    flags_lines=(proc/'fdinfo'/'3').read_text().splitlines()
    flags=[int(line.split(':',1)[1].strip(),8) for line in flags_lines if line.startswith('flags:')]
    if len(flags)!=1 or flags[0]&os.O_ACCMODE!=os.O_WRONLY or flags[0]&os.O_CLOEXEC or not stat.S_ISFIFO(info.st_mode): raise ValueError('actual inherited FD3 is not the write pipe')
    for row in rows:
        if row['fd']==3: row.update(generation=0,access_mode='write-only',file_type='pipe',inheritable=True)
    return rows


def _finalize_pdf_native_run(run: dict, workspace_cleanup: str) -> tuple[dict,dict]:
    """Private caller owns workspace facts. No store issuance or public adoption."""
    observation=run['native_observation'];artifacts=run['native_artifacts']
    if not _pdf2(observation['spec']): raise ValueError('profile2 finalizer required')
    if workspace_cleanup!='removed': run['failure']=run['failure'] or 'native-workspace-cleanup-uncertain'
    run['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    end=time.monotonic();elapsed=int((end-run['_monotonic_start'])*10**9)
    run['elapsed_seconds']=elapsed/10**9
    info=observation['run']
    if info is not None:
        info['ended_at']=run['ended_at'];info['elapsed_ns']=elapsed
    terminal=run.get('_native_terminal')
    if run['failure'] is None and terminal is not None and elapsed<=120*10**9:
        terminal['cleanup']='owned-workspace-removed';terminal['custody']=copy.deepcopy(run['process_group'])
        observation['events'].append({'seq':len(observation['events']),'at_ns':elapsed,'kind':'terminal','data':terminal})
        try: verify_native_observation(observation,artifacts,purpose='actual')
        except (ValueError,OSError) as exc: run['failure']='native-independent-replay:'+type(exc).__name__
    if run['failure'] is not None or terminal is None or elapsed>120*10**9:
        run['failure']=run['failure'] or 'native-deadline-or-terminal-incomplete'
        observation['schema']='twin.native-file-observation-failure/v2'
        observation['failure']={'reason':run['failure'],'reaped':run['process_group']['reaped'],
            'eof':list(run['_native_eof']),'returncode':run['exit_code'],'wait':run['_native_wait'],
            'streams':_retain_failed_pdf_streams(run,artifacts)}
    return observation,artifacts


def _retain_failed_pdf_streams(run: dict, artifacts: dict) -> dict:
    """Failed captures cannot renew the invocation's retained-buffer allowance."""
    budget=run['_buffer_budget'];records={}
    for name in ('stdout','stderr','origin'):
        raw=run[name]
        if sm.sha256(raw) not in artifacts:
            raw=raw[:max(0,budget['limit']-budget['bytes'])]
        pin=_runtime_blob(artifacts,raw,budget);run[name]=raw
        lower=run['observed_bytes_lower_bound'][name]
        records[name]={'sha256':pin,'bytes':len(raw),'observed_bytes_lower_bound':lower,'truncated':lower>len(raw)}
    return records


def _linux_run(store: NativeObservationStore, spec: dict, artifacts: dict) -> dict:
    """Real kernel route, never called by TEST_ONLY injection/replay tests."""
    if store._purpose!='actual' or store._host_context is None: raise ValueError('actual private host context required')
    if platform.system()!='Linux' or platform.machine()!='x86_64': raise ValueError('unsupported-native-observer-platform')
    store._guard.verify();policy=_host_window(store._host_context)
    v2=_pdf2(spec)
    if len(list(Path('/proc/self/task').iterdir()))!=1: raise ValueError('single-threaded native recorder required')
    _put(artifacts,store._host_context._policy)
    artifacts.update(store._host_context._evidence)
    held,candidate_facts=_acquire_candidates(spec,artifacts,store._host_context)
    budget={'bytes':0,'limit':2*(spec['limits']['stdout_bytes']+spec['limits']['stderr_bytes']+spec['limits']['syntax_bytes']+RUNTIME_BYTES)+MAX_EVENT_BYTES}
    if v2: budget['limit']=456*1048576
    events: list[dict]=[]
    native_wait=None;native_terminal=None;origin_written=bytearray();origin_identity=None
    used_files: dict[str,dict]={}
    records: dict[int,dict]={}
    created: set[str]=set()
    outputs: dict[str,bytearray]={}
    acquired: list[int]=[]
    generations={0:0,1:0,2:0};current_maps: list[dict]=[]
    pending=None;executed=False;exit_stop=False;pid=None;mem=-1;procfd=-1;failure=None;returncode=None;reaped=[]
    descendants: set[int]=set()
    streams={'stdout':bytearray(),'stderr':bytearray()}; observed_streams={'stdout':0,'stderr':0};write_totals={'stdout':0,'stderr':0}; eof=[];pipes=[]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat(); start=time.monotonic(); event_budget={'bytes':2}
    start_ns=int(start*10**9)
    if v2:
        streams['origin']=bytearray();observed_streams['origin']=0;write_totals['pdf-origin']=0
    with selectors.DefaultSelector() as selector:
        try:
            input_read,input_write=os.pipe2(os.O_CLOEXEC);os.close(input_write)
            out_read,out_write=os.pipe2(os.O_CLOEXEC);err_read,err_write=os.pipe2(os.O_CLOEXEC)
            pipes=[input_read,out_read,out_write,err_read,err_write]
            origin_read=origin_write=-1
            if v2:
                origin_read,origin_write=os.pipe2(os.O_CLOEXEC);pipes.extend([origin_read,origin_write])
                origin_info=os.fstat(origin_read);origin_identity=[origin_info.st_dev,origin_info.st_ino]
            pid=os.fork()
            if pid==0:
                try:
                    os.setsid();os.umask(0o077);os.chdir(spec['cwd'])
                    _install_child_channels([input_read,out_write,err_write]+([origin_write] if v2 else []))
                    _ptrace(0,0);os.kill(os.getpid(),signal.SIGSTOP)
                    os.execve(spec['argv'][0],spec['argv'],spec['environment'])
                except BaseException: os._exit(127)
            os.close(input_read);os.close(out_write);os.close(err_write);pipes=[out_read,err_read]
            stream_fds=[(out_read,'stdout'),(err_read,'stderr')]
            if v2:
                os.close(origin_write);pipes.append(origin_read);stream_fds.append((origin_read,'origin'))
            for fd,name in stream_fds:
                os.set_blocking(fd,False);selector.register(fd,selectors.EVENT_READ,name)
            got,status=0,0
            while not got and time.monotonic()-start<spec['limits']['wall_seconds']:
                got,status=os.waitpid(pid,os.WNOHANG|os.WUNTRACED)
                if not got: time.sleep(0.001)
            if got==pid and (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                returncode=os.waitstatus_to_exitcode(status);reaped.append(pid)
                if v2: native_wait=_wait_record(status,int((time.monotonic()-start)*10**9))
            if got!=pid or not os.WIFSTOPPED(status) or os.WSTOPSIG(status)!=signal.SIGSTOP: raise ValueError('initial native pre-exec stop missing')
            _ptrace(0x4200,pid,0,OPTIONS)
            proc=Path('/proc')/str(pid);procfd=os.open(proc,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
            mem=os.open(proc/'mem',os.O_RDONLY|os.O_CLOEXEC)
            lifetime=_lifetime(proc)
            if lifetime['ppid']!=os.getpid() or lifetime['uid']!=os.getuid() or lifetime['gid']!=os.getgid(): raise ValueError('owned native lifetime differs')
            for fd,name in enumerate(('stdin','stdout','stderr')):
                info=(proc/'fd'/str(fd)).stat();records[fd]={'kind':name,'identity':[info.st_dev,info.st_ino],'generation':0}
            if v2:
                info=(proc/'fd'/'3').stat()
                if [info.st_dev,info.st_ino]!=origin_identity: raise ValueError('created/target origin pipe differs')
                records[3]={'kind':'pdf-origin','identity':origin_identity,'generation':0}
            initial=_channel_snapshot(proc,records) if v2 else _fd_snapshot(proc,records)
            _append(events,'start',{**lifetime,'fds':initial},start,spec['limits'],budget=event_budget);_ptrace(24,pid)
            while returncode is None or selector.get_map():
                if time.monotonic()-start>=spec['limits']['wall_seconds']: raise ValueError('native observation deadline')
                _host_window(store._host_context,verify_guard=False)
                for key,_ in selector.select(0.001):
                    chunk=os.read(key.fd,65536)
                    if not chunk:
                        selector.unregister(key.fd);eof.append(key.data)
                        if v2:
                            number={'stdout':1,'stderr':2,'origin':3}[key.data]
                            _append(events,'pipe-eof',{'channel':key.data,'fd':number,'generation':0,'identity':initial[number]['identity'],
                                'request_bytes':65536,'result':0,'captured_bytes':len(streams[key.data])},start,spec['limits'],budget=event_budget)
                        continue
                    observed_streams[key.data]+=len(chunk)
                    remaining=_channel_cap(spec,key.data)-len(streams[key.data])
                    streams[key.data].extend(chunk[:max(0,remaining)])
                    if observed_streams[key.data]>_channel_cap(spec,key.data): raise ValueError('native stream overflow')
                if returncode is not None: continue
                got,status=os.waitpid(pid,os.WNOHANG|os.WUNTRACED)
                if not got: continue
                if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                    returncode=os.waitstatus_to_exitcode(status);reaped.append(pid)
                    if v2: native_wait=_wait_record(status,int((time.monotonic()-start)*10**9))
                    if returncode or not exit_stop: raise ValueError('native early/nonzero death')
                    continue
                if not os.WIFSTOPPED(status): raise ValueError('unknown native wait status')
                stop_signal=os.WSTOPSIG(status);event=status>>16
                if _lifetime(proc)!=lifetime: raise ValueError('native lifetime/credential drift')
                if event==4:
                    if pending is None or pending['name']!='execve' or executed: raise ValueError('unexpected native exec')
                    os.close(mem);mem=os.open(proc/'mem',os.O_RDONLY|os.O_CLOEXEC)
                    maps=_maps(proc)
                    current_maps=_map_rows(maps,candidate_facts)
                    executable=os.path.realpath(proc/'exe')
                    for row in maps:
                        path=row['path']
                        if path and path.startswith('/'):
                            if path not in candidate_facts: raise ValueError('native startup dependency unretained')
                            info=Path(path).stat()
                            if [info.st_dev,info.st_ino]!=row['identity']: raise ValueError('native executable map identity differs')
                            used_files[path]=candidate_facts[path]
                    interpreter=elf_interpreter(_raw(artifacts,used_files[executable]['sha256']))
                    actual_interpreter,interpreter_links=_observe_open_route(interpreter) if interpreter else (None,[])
                    interpreter_route=({'path':actual_interpreter,**({'requested_path':interpreter,'route':interpreter_links} if interpreter_links else {})} if interpreter else None)
                    _append(events,'exec',{'maps':maps,'executable':executable,'credentials':[lifetime['uid'],lifetime['gid']],
                                          'interpreter':actual_interpreter,'interpreter_route':interpreter_route,**({'fds':_channel_snapshot(proc,records)} if v2 else {})},start,spec['limits'],budget=event_budget);executed=True
                elif event==6:
                    if pending is None or pending['name'] not in ('exit','exit_group'): raise ValueError('unexplained native exit-stop')
                    _append(events,'exit-stop',{'status':pending['args'][0],'maps':_maps(proc),'fds':_fd_snapshot(proc,records),
                                              'pid':pid,'starttime':lifetime['starttime']},start,spec['limits'],budget=event_budget);exit_stop=True;pending=None
                elif event in (1,2,3):
                    child_buffer=ctypes.c_ulonglong()
                    _ptrace(0x4201,pid,0,ctypes.addressof(child_buffer))
                    if child_buffer.value>0 and child_buffer.value!=pid: descendants.add(child_buffer.value)
                    raise ValueError('unexpected native owned descendant')
                elif event: raise ValueError('unsupported native process/ptrace event')
                elif stop_signal==signal.SIGTRAP|0x80:
                    stop=_syscall_stop(pid)
                    if stop['op']=='enter':
                        if pending is not None: raise ValueError('native entry/leave gap')
                        detail=_entry_detail(stop,mem,proc,artifacts,budget)
                        name=_admit(stop['nr'],stop['args'],detail,spec,records,created,executed,maps=current_maps)
                        if 'path' in detail and detail['path']!='/proc/self/exe' and not _inside(detail['path'],policy['roots']) and not detail['path'].startswith(spec['cwd']+'/'):
                            raise ValueError('native lookup outside selected host roots')
                        if name in ('open','openat'):
                            path=detail['path'];side=path in (spec['cwd']+'/runtime',spec['cwd']+'/syntax') and spec['profile'] not in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2')
                            if side:
                                if os.path.lexists(path): raise ValueError('preexisting native output')
                            elif os.path.lexists(path):
                                canonical=os.path.realpath(path)
                                if canonical!=path: raise ValueError('native observed route changed before open')
                                info=Path(path).stat()
                                if path not in candidate_facts and not (stat.S_ISDIR(info.st_mode) and path in {str(Path(p).parent) for p in candidate_facts}): raise ValueError('native dependency unretained before exposure')
                            elif not _inside(path,policy['roots']) and not path.startswith(spec['cwd']+'/'): raise ValueError('native lookup outside selected host roots')
                        if name in ('write','writev'):
                            record=records[stop['args'][0]]; requested=_raw(artifacts,detail['buffer_sha256'])
                            path=record['description']['path'] if record['kind']=='sidecar' else record['kind']
                            total=len(outputs[path]) if record['kind']=='sidecar' else write_totals[path]
                            cap=_channel_cap(spec,path)
                            if record['kind']=='pdf-origin': _origin_transport_prefix(bytes(origin_written),requested)
                            if total+len(requested)>cap: raise ValueError('native requested write exceeds owned-output cap')
                        pending={**stop,'name':name,'detail':detail}
                        if name in ('read','readv') and records[stop['args'][0]]['kind']=='file':
                            pending['offset']=records[stop['args'][0]]['description']['offset']
                        _append(events,'enter',{'nr':stop['nr'],'args':stop['args'],'detail':detail},start,spec['limits'],budget=event_budget)
                    else:
                        if pending is None: raise ValueError('native leave without entry')
                        result=stop['result'];name=pending['name'];a=pending['args'];detail={}
                        if name in ('open','openat') and result>=0:
                            path=pending['detail']['path'];info=(proc/'fd'/str(result)).stat();identity=_identity(info)
                            actual_path=os.readlink(proc/'fd'/str(result))
                            if actual_path!=path: raise ValueError('actual opened native path differs')
                            side=path in (spec['cwd']+'/runtime',spec['cwd']+'/syntax') and spec['profile'] not in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2')
                            kind='sidecar' if side else 'directory' if stat.S_ISDIR(info.st_mode) else 'file'
                            if side:
                                if identity[2]!=0o100600 or identity[3]!=lifetime['uid'] or identity[5]!=1 or identity[6]!=0: raise ValueError('actual sidecar creation differs')
                                created.add(path);outputs[path]=bytearray()
                            elif kind=='file':
                                fd=os.open(proc/'fd'/str(result),os.O_RDONLY|os.O_CLOEXEC)
                                acquired.append(fd)
                                if len(acquired)+len(held)>MAX_FILES: raise ValueError('native retained FD limit')
                                raw=_read_fd(fd,MAX_DEPENDENCY_BYTES)
                                if _identity(os.fstat(fd))!=identity or path not in candidate_facts or identity!=candidate_facts[path]['identity'] or raw!=_raw(artifacts,candidate_facts[path]['sha256']): raise ValueError('actual native FD acquisition differs')
                                used_files[path]=candidate_facts[path]
                            elif kind=='directory':
                                if not stat.S_ISDIR(info.st_mode): raise ValueError('native directory required')
                            generations[result]=generations.get(result,-1)+1
                            records[result]={'kind':kind,'identity':identity[:2],'generation':generations[result],
                                             'description':{'path':path,'offset':0,'identity':identity}}
                            detail={'kind':kind,'identity':identity}
                        elif name in ('read','pread64','readv'):
                            raw=_result_buffer(pending,result,mem);detail={'buffer_sha256':sm.sha256(raw),'buffer_bytes':len(raw)}
                            record=records[a[0]]
                            if result>=0:
                                if record['kind']=='stdin':
                                    if result: raise ValueError('owned stdin is not EOF')
                                else:
                                    desc=record['description']; offset=a[3] if name=='pread64' else desc['offset']
                                    expected=os.pread(held[desc['path']],result,offset)
                                    if raw!=expected: raise ValueError('actual native read differs')
                                    if name!='pread64': desc['offset']+=result
                        elif name in ('write','writev') and result>=0:
                            raw=_raw(artifacts,pending['detail']['buffer_sha256'])
                            if result>len(raw): raise ValueError('native partial write differs')
                            record=records[a[0]]
                            if record['kind']=='sidecar':
                                path=record['description']['path'];outputs[path].extend(raw[:result]);cap=RUNTIME_BYTES if path.endswith('/runtime') else spec['limits']['syntax_bytes']
                                if len(outputs[path])>cap: raise ValueError('native sidecar overflow')
                            else:
                                if record['kind']=='pdf-origin':
                                    if raw and result==0: raise ValueError('origin write made no progress')
                                    origin_written.extend(raw[:result])
                                write_totals[record['kind']]+=result
                        elif name in ('write','writev') and v2 and records[a[0]]['kind']=='pdf-origin' and result!=-errno.EINTR: raise ValueError('origin write failed')
                        elif name=='close' and result==0: del records[a[0]]
                        elif name in ('dup','dup2','dup3') and result>=0:
                            if result!=a[0]:
                                generations[result]=generations.get(result,-1)+1;records[result]={**records[a[0]],'generation':generations[result]}
                        elif name=='fcntl' and a[1] in (0,1030) and result>=0:
                            generations[result]=generations.get(result,-1)+1;records[result]={**records[a[0]],'generation':generations[result]}
                        elif name=='lseek' and result>=0: records[a[0]]['description']['offset']=result
                        elif name=='ioctl' and result!=-errno.ENOTTY: raise ValueError('native TCGETS did not fail ENOTTY')
                        elif name in ('mmap','mprotect','munmap','brk'):
                            detail={'maps':_maps(proc)}
                            desc=records[a[4]]['description'] if name=='mmap' and not a[3]&0x20 else None
                            # Reconcile at this syscall stop, before any further resume.
                            current_maps=_reconcile_maps(name,a,result,current_maps,detail['maps'],used_files,desc)
                        elif name in ('stat','lstat','fstat','newfstatat','readlink','readlinkat','getdents64','getcwd','uname','getrlimit','sysinfo','clock_gettime','prlimit64','getrandom','arch_prctl','rt_sigaction','rt_sigprocmask'):
                            raw=_result_buffer(pending,result,mem)
                            identity=None;fd_kind=None
                            if name=='fstat':
                                record=records[a[0]];fd_kind=record['kind']
                                identity=record['description']['identity'] if 'description' in record else record['identity']
                                if fd_kind=='sidecar': identity=identity[:6]  # mutable size/times are not fixed facts
                            uname=os.uname()
                            _validate_metadata_result(pending,result,raw,spec,candidate_facts,identity,{'system':'Linux','machine':'x86_64','release':uname.release,'version':uname.version},fd_kind=fd_kind)
                            detail={'buffer_sha256':_runtime_blob(artifacts,raw,budget)}
                        _append(events,'leave',{'result':result,'detail':detail},start,spec['limits'],budget=event_budget);pending=None
                else:
                    # No silent restart or signal forwarding: unsupported delivery holds.
                    raise ValueError('unsupported native signal/restart stop')
                _ptrace(24,pid)
            sidecars={}
            for path,raw in outputs.items():
                fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
                try:
                    identity=_identity(os.fstat(fd));actual=_read_fd(fd,RUNTIME_BYTES if path.endswith('/runtime') else spec['limits']['syntax_bytes'])
                    if actual!=bytes(raw) or identity[5]!=1: raise ValueError('native final output/write mismatch')
                    sidecars[path]={'sha256':_runtime_blob(artifacts,actual,budget),'identity':identity}
                finally: os.close(fd)
            for path,fd in held.items():
                if _identity(os.fstat(fd))!=candidate_facts[path]['identity'] or _read_fd(fd,MAX_DEPENDENCY_BYTES)!=_raw(artifacts,candidate_facts[path]['sha256']): raise ValueError('native post-run file drift')
            _host_window(store._host_context);store._guard.verify()
            native_terminal={'returncode':returncode,'stdout_sha256':_runtime_blob(artifacts,bytes(streams['stdout']),budget),
                'stderr_sha256':_runtime_blob(artifacts,bytes(streams['stderr']),budget),'sidecars':sidecars,'eof':sorted(eof,reverse=True),
                'reaped':reaped,'cleanup':'pending-owned-workspace-cleanup'}
            if v2:
                if bytes(origin_written)!=bytes(streams['origin']): raise ValueError('actual origin write/capture differs')
                native_terminal.update(origin_sha256=_runtime_blob(artifacts,bytes(streams['origin']),budget),origin_bytes=len(streams['origin']),wait=native_wait)
            else: _append(events,'terminal',native_terminal,start,spec['limits'],budget=event_budget)
        except Exception as exc:
            failure='native-observation:'+type(exc).__name__+':'+str(exc)[:240]
        finally:
            grace=spec['limits']['termination_grace_seconds']
            cleanup_started=time.monotonic()
            cleanup_deadline=min(start+spec['limits']['wall_seconds']+grace,cleanup_started+grace)
            custody,returncode=_finish_native_custody(pid,descendants,reaped,returncode,deadline=cleanup_deadline)
            try: validate_native_custody(custody)
            except ValueError: failure=failure or 'native-terminal-custody-uncertain'
            for fd in set(list(held.values())+acquired+pipes+[mem,procfd]):
                if fd>=0:
                    try: os.close(fd)
                    except OSError: pass
    if events and events[-1]['kind']=='terminal': events[-1]['data']['custody']=copy.deepcopy(custody)
    uname=os.uname()
    observation: dict[str,Any]={'schema':'twin.native-file-observation/v1','scope':SCOPE,'purpose':'actual','spec':spec,'files':used_files,
        'events':events,'platform':{'system':'Linux','machine':'x86_64','release':uname.release,'version':uname.version},'host_policy_sha256':sm.sha256(store._host_context._policy)}
    if v2:
        observation['schema']='twin.native-file-observation/v2'
        observation['run']=None
        if events and events[0]['kind']=='start':
            run_info: dict[str,Any]={'started_at':started,'ended_at':None,'monotonic_start_ns':start_ns,'elapsed_ns':None,
                'wall_deadline_ns':start_ns+120*10**9,'cleanup_started_ns':int(cleanup_started*10**9),
                'cleanup_deadline_ns':min(int(cleanup_started*10**9)+2*10**9,start_ns+122*10**9)}
            run_info['run_id']=_run_identity(spec,run_info,events[0]['data']);observation['run']=run_info
    if failure is not None and not v2:
        observation['schema']='twin.native-file-observation-failure/v1'
        observation['failure']={'reason':failure,'reaped':list(reaped),'eof':list(eof),'returncode':returncode}
    return {'started_at':started,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,
        'exit_code':returncode,'stdout':bytes(streams['stdout']),'stderr':bytes(streams['stderr']),
        'observed_bytes_lower_bound':observed_streams,'streams_complete':failure is None and set(eof)==({'stdout','stderr','origin'} if v2 else {'stdout','stderr'}),
        'failure':failure,'native_observation':observation,'native_artifacts':artifacts,'process_group':custody,
        **({'origin':bytes(streams['origin']),'_monotonic_start':start,'_native_terminal':native_terminal,'_native_wait':native_wait,'_native_eof':list(eof),'_buffer_budget':budget} if v2 else {})}


def validate_native_candidate_plan(plan: dict, parent: bytes) -> tuple[dict,dict]:
    """Validate a candidate set, never claim that a future run used only these files."""
    from . import source_metadata_migration as migration
    if type(plan) is dict and plan.get('profile')=='pdf-text-xpdf-origin/2':
        from . import pdf_native_bridge as bridge
        if plan.get('purpose')!='actual': raise ValueError('profile2 actual private acquisition only')
        return bridge._validate_plan(plan,parent)
    _closed(plan,{'schema','purpose','profile','parent_sha256','parent_bytes','member_id','predecessor_sha256','implementation_artifact_sha256','configuration_sha256','archive'})
    if plan['schema']!='twin.source-extraction-plan/v1' or plan['purpose']!='actual' or plan['profile'] not in migration.PROFILES or type(parent) is not bytes or plan['parent_sha256']!=sm.sha256(parent) or type(plan['parent_bytes']) is not int or plan['parent_bytes']!=len(parent) or type(plan['member_id']) is not str or not plan['member_id']:
        raise ValueError('native candidate parent/profile/purpose differs')
    migration._hash(plan['predecessor_sha256'])
    archive=plan['archive']
    if type(archive) is not dict: raise ValueError('retained candidate bytes required')
    for pin in archive: _raw(archive,pin)
    config=sm._json(_raw(archive,plan['configuration_sha256']))
    _closed(config,{'schema','profile','purpose','limits','environment','diagnostic_policy','test_only_behavior','native_config_sha256'})
    if config!={'schema':'twin.source-extraction-config/v1','profile':plan['profile'],'purpose':'actual',
        'limits':migration.PROFILES[plan['profile']],'environment':migration.ENVIRONMENT,
        'diagnostic_policy':'accept-bounded-on-zero','test_only_behavior':'normal','native_config_sha256':config['native_config_sha256']} or len(parent)>config['limits']['input_bytes']:
        raise ValueError('fixed native candidate configuration differs')
    closure=sm._json(_raw(archive,plan['implementation_artifact_sha256']))
    _closed(closure,{'schema','purpose','scope','platform_closure','process_files','platform_files','driver_files','driver_inventory'})
    if closure['schema']!='twin.source-extraction-closure/v1' or closure['purpose']!='actual' or closure['scope']!='native-candidate-file-set/v1' or closure['platform_closure']!='OBSERVATION-REQUIRED': raise ValueError('native candidate scope cannot claim completeness')
    from . import pdf_native_bridge as bridge
    inventory=bridge._driver_inventory()
    if inventory!=closure['driver_inventory']: raise ValueError('native driver source/helper changed')
    pf=closure['process_files'];native=plan['profile']=='pdf-text-xpdf/1'
    _closed(pf,{'schema','executable','files','version','version_observation_sha256'} if native else {'schema','executable','files','python'})
    if pf['schema']!=('twin.source-extraction-native-tool-files/v1' if native else 'twin.source-extraction-process-files/v1'): raise ValueError('candidate process schema differs')
    rows=pf['files']+closure['platform_files']+closure['driver_files']; paths=set();total=0
    for row in rows:
        _closed(row,{'path','sha256','bytes'});path=_path(row['path']);raw=_raw(archive,row['sha256'])
        if path in paths or type(row['bytes']) is not int or row['bytes']!=len(raw): raise ValueError('unique candidate bytes required')
        paths.add(path);total+=len(raw)
    if len(paths)>MAX_FILES or total>MAX_DEPENDENCY_BYTES or pf['executable'] not in paths: raise ValueError('candidate limit/executable missing')
    executable=next(row for row in rows if row['path']==pf['executable']);elf_interpreter(_raw(archive,executable['sha256']))
    required={str(Path(migration.__file__).resolve()),str(Path(__file__).resolve()),str(Path(sm.__file__).resolve()),str(sm.SCHEMA_PATH.resolve())}
    if not required<=paths: raise ValueError('native driver closure missing')
    if native:
        if type(pf['version']) is not str or not pf['version'] or pf['version'].startswith('TEST_ONLY'): raise ValueError('native tool identity unestablished')
        _raw(archive,pf['version_observation_sha256']);_raw(archive,config['native_config_sha256'])
    elif migration.CHILD not in paths or config['native_config_sha256'] is not None:
        raise ValueError('fixed helper candidate missing')
    return config,closure


def prepare_native_candidate_plan(profile: str, parent: bytes, *, predecessor_sha256: str,
                                  member_id: str, process_files: dict, retained_files: dict[str,bytes],
                                  native_configuration: bytes | None = None, pdf_origin: dict | None = None) -> dict:
    """Retain a host-selected candidate superset without executing or approving it."""
    from . import source_metadata_migration as migration
    archive: dict[str,bytes]={}
    pf=copy.deepcopy(process_files); process_paths={r['path'] for r in pf['files']}
    if any(path not in retained_files for path in process_paths): raise ValueError('retained process candidates missing')
    for row in pf['files']:
        if _put(archive,retained_files[row['path']])!=row['sha256'] or len(retained_files[row['path']])!=row['bytes']: raise ValueError('retained process candidate differs')
    if profile in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2'):
        # Caller retains the original tool-version observation, never a version string alone.
        version_pin=pf['version_observation_sha256']
        if version_pin not in retained_files: raise ValueError('retained version observation missing')
        if _put(archive,retained_files[version_pin])!=version_pin: raise ValueError('version observation differs')
    from . import pdf_native_bridge as bridge, pdf_output_origin
    if profile=='pdf-text-xpdf-origin/2':
        for pin,raw in retained_files.items():
            if not pin.startswith('/') and _put(archive,raw)!=pin: raise ValueError('retained build/config artifact differs')
    drivers=[]
    driver_paths=[str(Path(p).resolve()) for p in (migration.__file__,__file__,sm.__file__,str(sm.SCHEMA_PATH))]
    if profile=='pdf-text-xpdf-origin/2': driver_paths += [str(Path(bridge.__file__).resolve()),str(Path(pdf_output_origin.__file__).resolve())]
    for path in driver_paths:
        raw=Path(path).read_bytes();drivers.append({'path':path,'sha256':_put(archive,raw),'bytes':len(raw)})
    platform_rows=[]
    for path,raw in sorted(retained_files.items()):
        if path in process_paths or path in driver_paths or not path.startswith('/'): continue
        platform_rows.append({'path':_path(path),'sha256':_put(archive,raw),'bytes':len(raw)})
    from . import pdf_native_bridge as bridge
    inventory=bridge._driver_inventory()
    closure={'schema':'twin.source-extraction-closure/v1','purpose':'actual','scope':'native-candidate-file-set/v1',
        'platform_closure':'OBSERVATION-REQUIRED','process_files':pf,'platform_files':platform_rows,'driver_files':drivers,'driver_inventory':inventory}
    config={'schema':'twin.source-extraction-config/v1','profile':profile,'purpose':'actual','limits':copy.deepcopy(migration.PROFILES[profile]),
        'environment':dict(migration.ENVIRONMENT),'diagnostic_policy':'accept-bounded-on-zero','test_only_behavior':'normal',
        'native_config_sha256':_put(archive,native_configuration) if native_configuration is not None else None}
    if profile=='pdf-text-xpdf-origin/2':
        config['schema']='twin.source-extraction-config/v2';config['pdf_origin']=copy.deepcopy(pdf_origin)
    elif pdf_origin is not None: raise ValueError('origin config requires profile2')
    plan={'schema':'twin.source-extraction-plan/v1','purpose':'actual','profile':profile,'parent_sha256':sm.sha256(parent),'parent_bytes':len(parent),
        'member_id':member_id,'predecessor_sha256':predecessor_sha256,'implementation_artifact_sha256':_put(archive,sm.canonical(closure)),
        'configuration_sha256':_put(archive,sm.canonical(config)),'archive':archive}
    validate_native_candidate_plan(plan,parent)
    return plan


def _run_native_extraction(store: NativeObservationStore, plan: dict, parent: bytes, argv: list[str], workdir: str) -> dict:
    from . import source_metadata_migration as migration
    if type(store) is not NativeObservationStore or store._purpose!='actual' or store._host_context is None: raise ValueError('private actual observer authority absent')
    store._guard.verify();config,closure=validate_native_candidate_plan(plan,parent)
    expected=migration._pdf_origin_command(closure['process_files']['executable'],workdir) if plan['profile']=='pdf-text-xpdf-origin/2' else migration._pdf_command(closure['process_files']['executable'],workdir) if plan['profile']=='pdf-text-xpdf/1' else migration._observed_command(closure['process_files']['executable'],workdir)
    if argv!=expected: raise ValueError('fixed observed invocation differs')
    artifacts=dict(plan['archive']);rows=closure['process_files']['files']+closure['platform_files']+closure['driver_files']
    candidates={r['path']:dict(r) for r in rows}
    for name,raw in [('input',parent),('config',_raw(artifacts,plan['configuration_sha256']))]:
        candidates[workdir+'/'+name]={'path':workdir+'/'+name,'sha256':_put(artifacts,raw),'bytes':len(raw)}
    if plan['profile'] in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2'):
        raw=_raw(artifacts,config['native_config_sha256']);candidates[workdir+'/native-config']={'path':workdir+'/native-config','sha256':_put(artifacts,raw),'bytes':len(raw)}
    else:
        row=next(r for r in rows if r['path']==migration.CHILD)
        candidates[workdir+'/helper.py']={**row,'path':workdir+'/helper.py'}
    spec={'schema':'twin.native-observation-spec/v2' if plan['profile']=='pdf-text-xpdf-origin/2' else 'twin.native-observation-spec/v1','purpose':'actual','profile':plan['profile'],
        'plan_sha256':sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'})),
        'argv':argv,'environment':dict(migration.ENVIRONMENT),'cwd':workdir,'limits':dict(config['limits']),
        'candidates':list(candidates.values())}
    if _pdf2(spec):
        from . import pdf_native_bridge as bridge
        bridge._require_actual_selection(store,plan)
    return _linux_run(store,spec,artifacts)


def finalize_native_observation(run: dict, *, cleanup_failed: bool) -> tuple[dict,dict]:
    observation=run['native_observation'];artifacts=run['native_artifacts']
    terminal=observation['events'][-1] if observation['events'] else None
    if terminal is not None and terminal['kind']=='terminal' and terminal['data']['cleanup']=='pending-owned-workspace-cleanup':
        terminal['data']['cleanup']='cleanup-failed' if cleanup_failed else 'owned-workspace-removed'
    if cleanup_failed or run['failure'] is not None: return observation,artifacts
    if terminal is None or terminal['kind']!='terminal' or terminal['data']['cleanup']!='owned-workspace-removed': raise ValueError('native cleanup transition differs')
    verify_native_observation(observation,artifacts,purpose='actual')
    return observation,artifacts


class NativeObservationFailure(ValueError):
    """Passive exception carrying retained bounded failed evidence; no acquired handle."""
    result: dict


def _completed_pdf_result(completed: Any) -> tuple[dict,dict]:
    """Compare a private completed pair, without adopting or issuing anything."""
    if type(completed) is not tuple or len(completed)!=2 or any(type(row) is not dict for row in completed):
        raise ValueError('private completed PDF tuple required')
    result,actual_record=completed
    dossier=sm._json(_raw(result['receipts'],result['dossier_sha256']))
    observation=sm._json(_raw(result['archive'],dossier['native_observation_sha256']))
    if observation!=actual_record: raise ValueError('result substituted the actual completed native record')
    return result,actual_record


def _acquire_actual(store: NativeObservationStore, plan: dict, parent: bytes) -> ObservedExtraction:
    from . import source_metadata_migration as migration
    if type(store) is not NativeObservationStore or store._purpose!='actual' or store._host_context is None: raise ValueError('independently selected actual host authority required')
    store._guard.verify();_host_window(store._host_context)
    plan=copy.deepcopy(plan)
    validate_native_candidate_plan(plan,parent)
    if plan['profile']=='pdf-text-xpdf-origin/2':
        from . import pdf_native_bridge as bridge
        bridge._require_actual_selection(store,plan)
    completed=migration._execute_prepared_extraction(plan,parent,observation_store=store)
    actual_record=None
    if plan['profile']=='pdf-text-xpdf-origin/2':
        result,actual_record=_completed_pdf_result(completed)
    else:
        if type(completed) is not dict: raise ValueError('legacy result differs')
        result=completed
    if result['status']!='success':
        exc=NativeObservationFailure('native observation failed; no acquired success')
        exc.result=result
        raise exc
    observation=sm._json(_raw(result['archive'],sm._json(_raw(result['receipts'],result['dossier_sha256']))['native_observation_sha256']))
    if actual_record is not None and observation!=actual_record: raise ValueError('result substituted the actual completed native record')
    verify_native_observation(observation,result['archive'],purpose='actual')
    if observation['host_policy_sha256']!=sm.sha256(store._host_context._policy): raise ValueError('independent host selection binding differs')
    return _deposit(store,result,observation,held_plan=plan if plan['profile']=='pdf-text-xpdf-origin/2' else None)


def validate_observation_binding(observation: dict, plan: dict, parent: bytes, invocation: dict) -> None:
    """Bind public evidence to a preselected plan; never acquire or select an index."""
    from . import source_metadata_migration as migration
    config,closure=validate_native_candidate_plan(plan,parent)
    spec=observation['spec'];cwd=invocation['cwd']
    expected_rows=closure['process_files']['files']+closure['platform_files']+closure['driver_files']
    wanted={r['path']:dict(r) for r in expected_rows}
    for name,raw in [('input',parent),('config',_raw(plan['archive'],plan['configuration_sha256']))]:
        wanted[cwd+'/'+name]={'path':cwd+'/'+name,'sha256':sm.sha256(raw),'bytes':len(raw)}
    if plan['profile'] in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2'):
        raw=_raw(plan['archive'],config['native_config_sha256']);wanted[cwd+'/native-config']={'path':cwd+'/native-config','sha256':sm.sha256(raw),'bytes':len(raw)}
    else:
        helper=next(row for row in expected_rows if row['path']==migration.CHILD)
        wanted[cwd+'/helper.py']={**helper,'path':cwd+'/helper.py'}
    if (spec['purpose']!='actual' or spec['profile']!=plan['profile'] or spec['plan_sha256']!=sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'}))
            or spec['argv']!=invocation['argv'] or spec['cwd']!=cwd or spec['environment']!=invocation['environment'] or spec['limits']!=config['limits']
            or {r['path']:r for r in spec['candidates']}!=wanted):
        raise ValueError('observation exact plan/invocation/candidate binding differs')


def _replayed_open_path(detail: dict) -> str:
    final=_path(detail['path'])
    if 'route' not in detail: return final
    current=_path(detail['requested_path']);route=detail['route']
    if type(route) is not list or not 1<=len(route)<=40: raise ValueError('bounded symlink route required')
    for row in route:
        _closed(row,{'path','target'});prefix=_path(row['path']);target=row['target']
        if type(target) is not str or not target or '\0' in target or len(target.encode())>MAX_PATH or not (current==prefix or current.startswith(prefix+'/')):
            raise ValueError('symlink route step differs')
        current='/' + os.path.normpath((target if target.startswith('/') else str(Path(prefix).parent)+'/'+target)+current[len(prefix):]).lstrip('/')
        _path(current)
    if current!=final: raise ValueError('symlink route target differs')
    return final


def _observe_open_route(requested: str) -> tuple[str,list[dict]]:
    current=_path(requested);route: list[dict]=[]
    for _ in range(40):
        parts=current.split('/');changed=False
        for i in range(1,len(parts)):
            prefix='/'.join(parts[:i+1])
            try: target=os.readlink(prefix)
            except OSError as exc:
                if exc.errno in (errno.EINVAL,): continue
                if exc.errno in (errno.ENOENT,errno.ENOTDIR): return current,route
                raise
            row={'path':prefix,'target':target};route.append(row)
            current='/' + os.path.normpath((target if target.startswith('/') else str(Path(prefix).parent)+'/'+target)+'/'+'/'.join(parts[i+1:])).lstrip('/')
            _path(current);changed=True;break
        if not changed: return current,route
    raise ValueError('native symlink route limit')


def _runtime_blob(artifacts: dict, raw: bytes, budget: dict) -> str:
    pin=sm.sha256(raw)
    if pin not in artifacts:
        if budget['bytes']+len(raw)>budget['limit']: raise ValueError('native retained-buffer limit')
        budget['bytes']+=len(raw);artifacts[pin]=raw
    return pin


def _validate_host_policy(policy: dict) -> None:
    _closed(policy,{'schema','scope','custodian','not_before','not_after','roots','writer_control','evidence_sha256s'})
    if policy['schema']!='twin.native-host-policy/v1' or policy['scope']!=SCOPE or type(policy['custodian']) is not str or not policy['custodian'] or policy['writer_control']!='trusted-administrator-controlled-interval':
        raise ValueError('independently selected host operating assumption required')
    start,end=sm._instant(policy['not_before']),sm._instant(policy['not_after'])
    if not 0<(end-start).total_seconds()<=3600: raise ValueError('bounded host interval required')
    roots=policy['roots'];pins=policy['evidence_sha256s']
    if type(roots) is not list or not 1<=len(roots)<=128 or len(set(roots))!=len(roots) or any(_path(root)=='/' for root in roots): raise ValueError('exact bounded host roots required')
    if type(pins) is not list or not pins or len(set(pins))!=len(pins): raise ValueError('independent host evidence pins required')
    for pin in pins:
        if type(pin) is not str or len(pin)!=64 or any(c not in '0123456789abcdef' for c in pin): raise ValueError('host evidence pin differs')
