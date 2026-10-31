"""Fixed TEST_ONLY existing-CI installation/suite. Import is inert.

Actual installation and privileged execution require separate reviewed authority.
No model, package, production registration or permission is supplied.
"""
from __future__ import annotations
from dataclasses import dataclass
import base64
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterator

STORE='/var/lib/policy-as-versioned-flux-linux-control'
START_SCHEMA='TEST_ONLY-ci-start/v1'
MEMBERS=('linux_guardian.py','linux_lease_control.py','linux_lease_control_child.py',
    'linux_lease_control_entry','linux_lease_control_ci.py','linux_lease_control_ci_entry',
    'linux_network.py','linux_runtime_filter.py','qwen_backend.py')
MAX_FILE=16*1024**2
MAX_RAW=128*1024**2
MAX_STREAM=256*1024**2
MAX_FRAME=65536
OUTCOME_KEYS=('schema','status','executed','control_passed','production_capture_accepted')
OBSERVATIONS=('context','caller','principal','kernel','installation','host','availability','admission-failure')


def admission_reference(value:Any)->dict[str,Any]:
    if (not isinstance(value,dict) or set(value)!={'name','bytes','sha256'}
            or value['name']!='suite/admission-failure.json' or type(value['bytes']) is not int
            or not 0<value['bytes']<=MAX_FILE or not pin(value['sha256'])):
        raise ValueError('fixed original failed-admission reference required')
    return value


def validate_os_closure(rows:Any,loaded:set[str],control:Any)->dict[str,int]:
    facts=control.validate_closure(rows)
    sources={row['source'] for row in rows}
    if not loaded<=sources:raise ValueError('actual loaded source/native alias absent from closure')
    for row in rows:
        path=row['source']
        if not isinstance(path,str) or not path.startswith(('/usr/lib/','/usr/bin/','/lib/','/lib64/',STORE+'/source/')):
            raise ValueError('existing protected OS/source closure only, no toolcache or acquired runtime')
    python=next(row for row in rows if row['target']=='/usr/bin/python3.12')
    if python['source']!='/usr/bin/python3.12':raise ValueError('literal OS interpreter, no source alias')
    return facts


def verify_suite(value:Any,control:Any)->dict[str,Any]:
    """Check original protected observer records, never manufacture an issuer."""
    if (not isinstance(value,dict) or value.get('schema')!='TEST_ONLY-ci-suite/v1'
            or value.get('status')!='PASS' or value.get('executed') is not True
            or value.get('control_passed') is not True or value.get('production_capture_accepted') is not False
            or value.get('error') is not None or value.get('admission_failure') is not None):raise ValueError('complete executed suite required')
    began,deadline,finished=(finite(value.get(key)) for key in ('started','deadline','finished'))
    if deadline!=began+900 or not began<=finished<=deadline:raise ValueError('original whole-control ceiling differs')
    rows=value.get('scenarios')
    if not isinstance(rows,list) or [row.get('scenario') for row in rows if isinstance(row,dict)]!=list(control.SCENARIOS):
        raise ValueError('all six original scenarios in fixed order required')
    previous=began
    for row in rows:
        control.verify_result(row)
        if not previous<=finite(row['started'])<=finite(row['finished'])<=finished:
            raise ValueError('serialized scenario timeline escaped original budget')
        previous=finite(row['finished'])
    if sum(len(row['attempts']) for row in rows)!=20:raise ValueError('twenty complete serialized subcases required')
    return {'control_passed':True,'production_capture_accepted':False}


def export_name(name:Any)->bool:
    if not isinstance(name,str) or '..' in name.split('/') or name.startswith('/'):return False
    if name in ('suite/start.json','suite/sources.json','suite/result.json',*(f'suite/{name}.json' for name in OBSERVATIONS)):return True
    if name.startswith('source/'):return name[7:] in MEMBERS
    return re.fullmatch(r'cases/(baseline|boundaries|resources|supervisor-loss|guardian-loss|invalid-evidence)/[a-z-]+\.(jsonl|json)',name) is not None or re.fullmatch(
        r'receipts/[0-9a-f]{48}/(preflight|generate)-(sources|native-mappings-[0-9]{6})\.jsonl',name) is not None


def export_frames(files:dict[str,bytes],outcome:dict[str,Any])->Iterator[bytes]:
    if not files or len(files)>4096 or any(not export_name(name) for name in files):
        raise ValueError('closed fixed export member set required')
    if any(not isinstance(raw,bytes) or len(raw)>MAX_FILE for raw in files.values()) or sum(map(len,files.values()))>MAX_RAW:
        raise ValueError('bounded original export bytes required; no truncation')
    if outcome.get('production_capture_accepted') is not False:
        raise ValueError('tiny control export cannot confer production permission')
    total=0;manifest=[]
    def frame(value:dict[str,Any])->bytes:
        nonlocal total
        raw=canonical(value)+b'\n';total+=len(raw)
        if len(raw)>MAX_FRAME or total>MAX_STREAM:raise ValueError('bounded export frame/stream exceeded')
        return raw
    yield frame({'kind':'start','schema':'TEST_ONLY-ci-export/v1',
                 'outcome':{key:outcome[key] for key in OUTCOME_KEYS},'files':len(files)})
    for name,raw in sorted(files.items()):
        row={'name':name,'bytes':len(raw),'sha256':sha(raw)};manifest.append(row)
        yield frame({'kind':'file',**row})
        for offset in range(0,len(raw),32768):
            yield frame({'kind':'chunk','name':name,'offset':offset,'base64':base64.b64encode(raw[offset:offset+32768]).decode()})
        yield frame({'kind':'end-file','name':name})
    yield frame({'kind':'end','manifest_sha256':sha(canonical(manifest)),'files':len(manifest)})


def receive_export(raw:bytes)->dict[str,Any]:
    """Integrity parser, not a protected issuer/catalogue or permission import."""
    if not isinstance(raw,bytes) or len(raw)>MAX_STREAM or not raw.endswith(b'\n'):
        raise ValueError('bounded terminated complete export required')
    frames=[]
    for line in raw.splitlines():
        if len(line)+1>MAX_FRAME:raise ValueError('export frame exceeded')
        frames.append(json.loads(line,object_pairs_hook=unique_object))
    if len(frames)<4 or not isinstance(frames[0],dict) or set(frames[0])!={'kind','schema','outcome','files'}:
        raise ValueError('closed export start required')
    first=frames.pop(0)
    if first['kind']!='start' or first['schema']!='TEST_ONLY-ci-export/v1' or type(first['files']) is not int or not 0<first['files']<=4096:
        raise ValueError('fixed export schema/member count required')
    outcome=first['outcome']
    if (not isinstance(outcome,dict) or outcome.get('production_capture_accepted') is not False
            or outcome.get('status') not in ('PASS','SKIP','FAIL','UNVERIFIED')
            or type(outcome.get('executed')) is not bool or type(outcome.get('control_passed')) is not bool
            or outcome['control_passed']!=(outcome['status']=='PASS')
            or outcome['status']=='SKIP' and outcome['executed'] is not False):
        raise ValueError('truthful native outcome required')
    files={};manifest=[];current=None;payload=bytearray();row=None;count=0;ended=False
    for frame in frames:
        if ended or not isinstance(frame,dict):raise ValueError('foreign or trailing export frame')
        kind=frame.get('kind')
        if kind=='file':
            if current is not None or set(frame)!={'kind','name','bytes','sha256'} or not export_name(frame['name']) or frame['name'] in files:
                raise ValueError('foreign/duplicate/overlapping export file')
            if type(frame['bytes']) is not int or not 0<=frame['bytes']<=MAX_FILE or not pin(frame['sha256']):raise ValueError('bounded file facts required')
            current=frame['name'];row={key:frame[key] for key in ('name','bytes','sha256')};payload=bytearray()
        elif kind=='chunk':
            if (current is None or set(frame)!={'kind','name','offset','base64'} or frame['name']!=current
                    or type(frame['offset']) is not int or frame['offset']!=len(payload)):
                raise ValueError('ordered exact file chunk required')
            try:part=base64.b64decode(frame['base64'],validate=True)
            except (ValueError,TypeError) as error:raise ValueError('actual base64 bytes required') from error
            payload.extend(part);count+=len(part)
            if len(payload)>MAX_FILE or count>MAX_RAW:raise ValueError('original export byte cap exceeded')
        elif kind=='end-file':
            if current is None or row is None or set(frame)!={'kind','name'} or frame['name']!=current or len(payload)!=row['bytes'] or sha(bytes(payload))!=row['sha256']:
                raise ValueError('complete exact exported file bytes required')
            files[current]=bytes(payload);manifest.append(row);current=None
        elif kind=='end':
            if (current is not None or set(frame)!={'kind','manifest_sha256','files'} or frame['files']!=len(files)
                    or first['files']!=len(files) or frame['manifest_sha256']!=sha(canonical(manifest))):
                raise ValueError('complete actual export manifest required')
            ended=True
        else:raise ValueError('closed export frame kind required')
    if not ended or 'suite/result.json' not in files:raise ValueError('final export/result receipt missing')
    original=json.loads(files['suite/result.json'],object_pairs_hook=unique_object)
    if not isinstance(original,dict) or {key:original.get(key) for key in OUTCOME_KEYS}!=outcome:
        raise ValueError('stream outcome differs from actual exported result')
    outcome=original
    if outcome.get('admission_failure') is not None:
        reference=admission_reference(outcome['admission_failure']);admission_raw=files.get(reference['name'])
        if (outcome['status']=='PASS' or admission_raw is None or len(admission_raw)!=reference['bytes']
                or sha(admission_raw)!=reference['sha256']):
            raise ValueError('original failed-admission evidence missing, changed or falsely passed')
    if outcome['status']=='PASS':
        required={'suite/start.json','suite/sources.json','suite/installation.json','suite/host.json',
                  *('source/'+name for name in MEMBERS)}
        if not required<=set(files):raise ValueError('PASS source/start/installation/host receipts missing')
        start=json.loads(files['suite/start.json'],object_pairs_hook=unique_object)
        sources=source_manifest(files['suite/sources.json'],start['source_manifest_sha256'])
        for name in MEMBERS:check_member(sources,name,files['source/'+name])
        if start['started']!=outcome['started'] or start['deadline']!=outcome['deadline']:
            raise ValueError('PASS original startup clock differs')
        # Use this reviewed receiver's fixed adjacent reader. Exported Python is
        # retained as data, NEVER executed or imported to validate its own claim.
        import types
        source=Path(__file__).with_name('linux_lease_control.py')
        reader=types.ModuleType('fixed_nonroot_receipt_reader')
        exec(compile(source.read_bytes(),str(source),'exec'),reader.__dict__)
        verify_suite(outcome,reader)
        for scenario in outcome['scenarios']:
            for attempt in scenario['attempts']:
                prefix='cases/'+scenario['scenario']+'/'+attempt['case']
                if (prefix+'.json' not in files or not files.get(prefix+'.jsonl')
                        or json.loads(files[prefix+'.json'],object_pairs_hook=unique_object)!=attempt):
                    raise ValueError('original per-attempt journal/record missing or different')
                for receipt in attempt.get('observations',{}).get('receipts',[]):
                    path=receipt['path'];prefix=STORE+'/'
                    if not isinstance(path,str) or not path.startswith(prefix):raise ValueError('foreign source/native receipt')
                    original=files.get(path[len(prefix):])
                    if original is None or len(original)!=receipt['bytes'] or sha(original)!=receipt['sha256']:
                        raise ValueError('original source/native receipt missing or different')
    return {'files':files,'outcome':outcome,'manifest':manifest,'production_capture_accepted':False}


def canonical(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()


def pin(value:Any)->bool:
    return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def unique_object(pairs:list[tuple[str,Any]])->dict[str,Any]:
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate JSON member')
        result[key]=value
    return result


def source_manifest(raw:bytes,reviewed:str)->dict[str,dict[str,Any]]:
    if len(raw)>65536 or not pin(reviewed) or sha(raw)!=reviewed:
        raise ValueError('literal reviewed source manifest pin differs')
    value=json.loads(raw,object_pairs_hook=unique_object)
    if (not isinstance(value,dict) or set(value)!={'schema','files'} or value['schema']!='TEST_ONLY-ci-sources/v1'
            or not isinstance(value['files'],dict) or set(value['files'])!=set(MEMBERS)):
        raise ValueError('closed fixed nine-source manifest required')
    for row in value['files'].values():
        if (not isinstance(row,dict) or set(row)!={'sha256','bytes'} or not pin(row['sha256'])
                or type(row['bytes']) is not int or not 0<row['bytes']<=1024**2):
            raise ValueError('bounded exact source bytes/pin required')
    return value['files']


def check_member(manifest:dict[str,dict[str,Any]],name:str,raw:bytes)->None:
    if name not in MEMBERS or name not in manifest or len(raw)!=manifest[name]['bytes'] or sha(raw)!=manifest[name]['sha256']:
        raise ValueError('actual source member bytes differ from reviewed manifest')


def finite(value:Any)->float:
    if type(value) not in (int,float) or not math.isfinite(value):
        raise ValueError('finite numeric host monotonic time required')
    return float(value)


@dataclass(frozen=True)
class SuiteBudget:
    started:float
    deadline:float

    @classmethod
    def admit(cls,receipt:Any,*,pid:int,start:str,manifest:str,now:float)->SuiteBudget:
        if (not isinstance(receipt,dict) or set(receipt)!={'schema','pid','start','started','deadline','source_manifest_sha256'}
                or receipt['schema']!=START_SCHEMA or type(receipt['pid']) is not int or receipt['pid']!=pid
                or receipt['start']!=start or receipt['source_manifest_sha256']!=manifest):
            raise ValueError('protected same-process source-bound startup receipt required')
        began,deadline=finite(receipt['started']),finite(receipt['deadline'])
        if deadline!=began+900 or not began<=finite(now)<deadline-10:
            raise ValueError('original whole-control budget invalid or exhausted')
        return cls(began,deadline)

    def require_work(self,now:float)->None:
        if not self.started<=finite(now)<self.deadline-10:raise ValueError('original shared work budget exhausted')

    def attempt_deadline(self,now:float,case:str)->float:
        self.require_work(now)
        return min(finite(now)+(30 if case=='deadline' else 60),self.deadline)


class PrerequisiteUnavailable(ValueError):
    """Initial observed native capability unavailable; never an executed PASS."""
    def __init__(self,message:str,facts:dict[str,Any]|None=None):
        super().__init__(message);self.facts=facts


def installed_read(path:str,maximum:int)->bytes:
    """Fixed-root bootstrap reader. No project code has authority before this read."""
    import os,stat
    target=Path(path)
    if not (path in (STORE+'/start.json',STORE+'/source-manifest.json',STORE+'/ci-context.json')
            or path.startswith(STORE+'/source/') and target.name in MEMBERS):
        raise ValueError('closed installed bootstrap path required')
    for member in (target,*target.parents):
        info=member.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022:
            raise ValueError('unsafe fixed root source/store')
        if any(name in os.listxattr(member,follow_symlinks=False) for name in
                ('system.posix_acl_access','system.posix_acl_default','security.capability')):
            raise ValueError('fixed root path has discretionary ACL/capability')
    info=target.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_mode&0o6000:
        raise ValueError('single-link unprivileged root source required')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        actual=os.fstat(fd)
        if (info.st_dev,info.st_ino)!=(actual.st_dev,actual.st_ino):raise ValueError('fixed source identity changed')
        parts=[];size=0
        while True:
            part=os.read(fd,min(65536,maximum+1-size))
            if not part:break
            parts.append(part);size+=len(part)
            if size>maximum:raise ValueError('fixed source read cap exceeded')
        return b''.join(parts)
    finally:os.close(fd)


def installed_module(name:str,manifest:dict[str,dict[str,Any]])->Any:
    import sys,types
    if name not in MEMBERS or not name.endswith('.py'):raise ValueError('fixed Python source member required')
    path=STORE+'/source/'+name;raw=installed_read(path,1024**2);check_member(manifest,name,raw)
    module=types.ModuleType('fixed_ci_'+name[:-3]);module.__file__=path
    sys.modules[module.__name__]=module
    exec(compile(raw,path,'exec'),module.__dict__)
    return module


def workflow_context(raw:bytes,manifest:str)->dict[str,Any]:
    """Public workflow attribution only; native authority is observed separately."""
    if len(raw)>65536:raise ValueError('bounded workflow attribution required')
    value=json.loads(raw,object_pairs_hook=unique_object)
    if (not isinstance(value,dict) or set(value)!={'schema','source_manifest_sha256','workflow_run'}
            or value['schema']!='TEST_ONLY-ci-context/v1' or value['source_manifest_sha256']!=manifest):
        raise ValueError('source-bound fixed workflow annotation required')
    run=value['workflow_run']
    if (not isinstance(run,dict) or set(run)!={'repository','workflow','job','run_id','attempt','source_commit','event','arch','runner_label'}
            or any(not isinstance(item,str) for item in run.values()) or run['workflow']!='twin' or run['job']!='determinism'
            or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',run['repository'])
            or any(re.fullmatch(r'[1-9][0-9]*',run[key]) is None for key in ('run_id','attempt'))
            or re.fullmatch(r'[0-9a-f]{40}',run['source_commit']) is None
            or run['event'] not in ('push','pull_request','workflow_dispatch','schedule')
            or (run['arch'],run['runner_label']) not in (('x86_64-linux','ubuntu-24.04'),('aarch64-linux','ubuntu-24.04-arm'))):
        raise ValueError('closed attributed public workflow/run/source/job/architecture required')
    return value


def write_fixed(path:Path,raw:bytes)->None:
    import os
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o400)
    try:
        offset=0
        while offset<len(raw):
            count=os.write(fd,raw[offset:])
            if count<=0:raise ValueError('short immutable evidence write')
            offset+=count
        os.fsync(fd)
    finally:os.close(fd)


def persist_observation(g:Any,base:dict[str,bytes],name:str,value:Any)->None:
    """Retain original protected bytes before any subsequent work can fail."""
    if name not in tuple(f'suite/{item}.json' for item in OBSERVATIONS):
        raise ValueError('fixed observed prerequisite record required')
    directory=Path(STORE,'ci-evidence')
    try:directory.mkdir(mode=0o700)
    except FileExistsError:g.protected_path(str(directory),False)
    raw=canonical(value)+b'\n';path=directory/Path(name).name
    write_fixed(path,raw)
    actual=g.protected_read(str(path),sha(raw),MAX_FILE)
    if actual!=raw:raise ValueError('persisted original prerequisite bytes differ')
    base[name]=actual


def discover_closure(g:Any,control:Any,budget:SuiteBudget)->tuple[list[dict[str,Any]],dict[str,Any]]:
    """Acquire actual existing OS bytes and native mappings, never execute ldd."""
    import os,sys,time
    budget.require_work(time.monotonic())
    paths={'/usr/bin/python3.12'};loaded=set();caches=set()
    for module in tuple(sys.modules.values()):
        origin=getattr(module,'__file__',None)
        if origin:loaded.add(str(origin));paths.add(str(origin))
        cache=getattr(module,'__cached__',None)
        if cache and Path(cache).exists():caches.add(str(cache));paths.add(str(cache))
    maps=Path('/proc/self/maps').read_text()
    mapped=set()
    for line in maps.splitlines():
        fields=line.split(maxsplit=5)
        if len(fields)==6 and fields[5].startswith('/'):
            if fields[5].endswith(' (deleted)'):raise ValueError('deleted native mapping')
            mapped.add(fields[5]);paths.add(fields[5]);loaded.add(fields[5])
    for name in MEMBERS:paths.add(STORE+'/source/'+name)
    records={};identities=set()
    for path in sorted(paths):
        budget.require_work(time.monotonic())
        info=g.protected_path(path,True)
        if info.st_size<=0 or info.st_size>256*1024**2:raise ValueError('unbounded OS closure member')
        identity=(info.st_dev,info.st_ino)
        if identity in identities:raise ValueError('ambiguous loaded inode alias')
        identities.add(identity)
        raw=g.protected_read(path,maximum=256*1024**2)
        records[path]={'source':path,'target':'/app/'+Path(path).name if path.startswith(STORE+'/source/') else path,
            'bytes':len(raw),'sha256':sha(raw),'elf':control.elf_dependencies(raw)}
        if len(records)>4096 or sum(row['bytes'] for row in records.values())>256*1024**2:
            raise ValueError('OS closure exceeds fixed file/byte bounds')
    # PT_INTERP may be a symlink alias on the host. Pin the actually mapped
    # canonical inode as source, retaining the exact ELF path only as jail target.
    for row in list(records.values()):
        elf=row['elf']
        if elf is None:continue
        interpreter=elf['interpreter']
        if interpreter is not None:
            canonical_path=os.path.realpath(interpreter)
            if canonical_path not in mapped or canonical_path not in records:
                raise ValueError('actual ELF interpreter not in native mappings')
            selected=records[canonical_path]
            if selected['target'] not in (canonical_path,interpreter):raise ValueError('ambiguous ELF loader target')
            selected['target']=interpreter
        for needed in elf['needed']:
            matches=[path for path in mapped if Path(path).name==needed]
            if len(matches)!=1:raise ValueError('missing/ambiguous actually mapped ELF NEEDED')
    rows=list(records.values());facts:dict[str,Any]=dict(validate_os_closure(rows,loaded,control))
    facts.update({'native_maps_sha256':sha(maps.encode()),'loaded_sources':sorted(loaded),'cached_sources':sorted(caches),
        'identities':[{'source':path,'device':g.protected_path(path,True).st_dev,
                       'inode':g.protected_path(path,True).st_ino} for path in sorted(paths)]})
    budget.require_work(time.monotonic())
    return rows,facts


def admit_ci_root(g:Any)->dict[str,Any]:
    """Observe only the fixed disposable-VM lab parent; never enable a controller."""
    import ctypes,os
    parent='/sys/fs/cgroup'
    try:g.protected_path(parent,False)
    except FileNotFoundError as failure:
        raise PrerequisiteUnavailable('fixed initial cgroup root absent',{
            'stage':'initial-cgroup-root-presence','path':parent,'operation':'protected_path',
            'error_type':type(failure).__name__,'args':list(failure.args),
            'errno':failure.errno,'filename':failure.filename}) from failure
    fd=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd);block=(ctypes.c_long*32)()
        g.libc_call('fstatfs',fd,ctypes.byref(block))
        if block[0]!=0x63677270:raise PrerequisiteUnavailable('fixed root is not cgroup-v2')
    finally:os.close(fd)
    mountinfo=Path('/proc/self/mountinfo').read_text()
    matches=[]
    for line in mountinfo.splitlines():
        left,right=line.split(' - ',1);fields=left.split()
        if fields[4]==parent:matches.append((fields,right.split()))
    if len(matches)!=1 or matches[0][0][3]!='/' or matches[0][1][0]!='cgroup2':
        raise PrerequisiteUnavailable('actual full cgroup-v2 root mount required')
    if os.readlink('/proc/self/ns/cgroup')!=os.readlink('/proc/1/ns/cgroup'):
        raise PrerequisiteUnavailable('private/unproved cgroup namespace')
    manager=os.path.realpath('/proc/1/exe')
    if manager!='/usr/lib/systemd/systemd':raise PrerequisiteUnavailable('fresh systemd guest root not observed')
    g.protected_path(manager,True)
    enabled=Path(parent,'cgroup.subtree_control').read_text().split()
    if not {'memory','cpu','cpuset','pids'}<=set(enabled):raise PrerequisiteUnavailable('four root controllers not already enabled')
    cpus=g.parse_set(Path(parent,'cpuset.cpus.effective').read_text()) & os.sched_getaffinity(0)
    if len(cpus)<2:raise PrerequisiteUnavailable('two eligible actual CPUs unavailable')
    return {'parent':parent,'device':info.st_dev,'inode':info.st_ino,'controllers':enabled,
        'eligible_cpus':sorted(cpus),'mountinfo_sha256':sha(mountinfo.encode()),'manager':manager,
        'lab_exception':'fresh disposable existing CI VM only; no systemd delegation claim'}


def execute_suite(g:Any,control:Any,caller:Any,budget:SuiteBudget,directory:Path)->dict[str,Any]:
    """One foreground operation. Each prior exact leaf is removed before next."""
    import time
    scenarios=[];executed=False;error=None;phase='suite-setup'
    try:
        for scenario in control.SCENARIOS:
            budget.require_work(time.monotonic())
            phase='host-admission'
            host,profile,prerequisites=control.load_ci_control_host(g,scenario,caller)
            began=time.monotonic();attempts=[];checks={}
            for case in control.CASES[scenario]:
                phase='subcase'
                budget.require_work(time.monotonic());caller.verify();executed=True
                attempt=control.run_attempt(g,host,profile,caller,case,budget.deadline,directory)
                attempts.append(attempt);checks.update(attempt['checks'])
                write_fixed(directory/(scenario+'-'+case+'.json'),canonical(attempt)+b'\n')
                control.verify_attempt(attempt,scenario,case)
            last=attempts[-1]
            result={'scenario':scenario,'executed':True,'started':began,'finished':time.monotonic(),
                'attempts':attempts,'checks':checks,'outer':last['outer'],'sentinel':last['sentinel'],
                'guardian_terminal':last['guardian_terminal'],'error':None,'prerequisites':prerequisites}
            control.verify_result(result);scenarios.append(result)
        outcome={'schema':'TEST_ONLY-ci-suite/v1','status':'PASS','executed':True,'control_passed':True,
            'production_capture_accepted':False,'started':budget.started,'deadline':budget.deadline,
            'finished':time.monotonic(),'scenarios':scenarios,'error':None}
        verify_suite(outcome,control)
        return outcome
    except BaseException as failure:
        error=type(failure).__name__+': '+str(failure)[:2000]
        reference=None
        if isinstance(failure,control.CiPrerequisiteUnavailable):
            records:dict[str,bytes]={};name='suite/admission-failure.json'
            persist_observation(g,records,name,{'schema':'TEST_ONLY-ci-admission-failure/v1','scenario':scenario,
                'phase':phase,'executed_before_failure':executed,'started':budget.started,'deadline':budget.deadline,
                'observed_monotonic':time.monotonic(),'error_type':type(failure).__name__,'facts':failure.facts})
            raw=records[name];reference={'name':name,'bytes':len(raw),'sha256':sha(raw)}
        return {'schema':'TEST_ONLY-ci-suite/v1','status':'FAIL','executed':executed,'control_passed':False,
            'production_capture_accepted':False,'started':budget.started,'deadline':budget.deadline,
            'finished':time.monotonic(),'scenarios':scenarios,'error':error,'admission_failure':reference}


def owned_exports(g:Any,base:dict[str,bytes],directory:Path|None,outcome:dict[str,Any],budget:SuiteBudget)->dict[str,bytes]:
    import time
    files=dict(base);files['suite/result.json']=canonical(outcome)+b'\n'
    for name,raw in tuple(base.items()):
        if name in tuple(f'suite/{item}.json' for item in OBSERVATIONS):
            actual=g.protected_read(str(Path(STORE,'ci-evidence',Path(name).name)),sha(raw),MAX_FILE)
            if actual!=raw:raise ValueError('protected original prerequisite changed before export')
            files[name]=actual
    if outcome.get('admission_failure') is not None:
        reference=admission_reference(outcome['admission_failure'])
        raw=g.protected_read(str(Path(STORE,'ci-evidence','admission-failure.json')),reference['sha256'],MAX_FILE)
        if len(raw)!=reference['bytes']:raise ValueError('original failed-admission byte count changed')
        files[reference['name']]=raw
    if directory is None:return files
    # Only filenames appointed by this source in this exact created directory.
    # Read even failed attempts' journals. No recursive/private tree discovery.
    control_cases={'baseline':('standard',),'boundaries':('standard',),'resources':('standard','oom','pids'),
        'supervisor-loss':('descendants',),'guardian-loss':('raw-clone','attached','dropped','armed','ready','descendants'),
        'invalid-evidence':('eof','deadline','ready','source','overflow','observer','incomplete','stale-lock')}
    for scenario,cases in control_cases.items():
        for case in cases:
            for suffix in ('.json','.jsonl'):
                if time.monotonic()>=budget.deadline:raise ValueError('original ceiling during local export')
                path=directory/(scenario+'-'+case+suffix)
                if path.exists():files['cases/'+scenario+'/'+case+suffix]=g.protected_read(str(path),maximum=MAX_FILE)
    for name,raw in tuple(files.items()):
        if not name.startswith('cases/') or not name.endswith('.json'):continue
        attempt=json.loads(raw,object_pairs_hook=unique_object)
        for receipt in attempt.get('observations',{}).get('receipts',[]):
            path=receipt['path'];prefix=STORE+'/'
            if not isinstance(path,str) or not path.startswith(prefix) or not export_name(path[len(prefix):]):
                raise ValueError('foreign receipt path cannot be exported')
            actual=g.protected_read(path,receipt['sha256'],MAX_FILE)
            if len(actual)!=receipt['bytes']:raise ValueError('protected receipt changed before export')
            files[path[len(prefix):]]=actual
    return files


def send_export(files:dict[str,bytes],outcome:dict[str,Any],budget:SuiteBudget)->None:
    import os,select,time
    os.set_blocking(1,False)
    for frame in export_frames(files,outcome):
        offset=0
        while offset<len(frame):
            left=budget.deadline-time.monotonic()
            if left<=0:raise ValueError('original whole-control ceiling during export')
            if not select.select([],[1],[],min(.05,left))[1]:continue
            try:count=os.write(1,frame[offset:])
            except BlockingIOError:continue
            if count<=0:raise ValueError('closed bounded export transport')
            offset+=count
    if time.monotonic()>budget.deadline:raise ValueError('original local export ceiling exceeded')


def suite_main()->int:
    import ctypes,os,platform,sys,time
    if (sys.platform!='linux' or sys.byteorder!='little' or ctypes.sizeof(ctypes.c_void_p)!=8
            or platform.machine() not in ('x86_64','aarch64') or os.getresuid()!=(0,0,0)
            or sys.executable!='/usr/bin/python3.12' or not sys.flags.isolated or not sys.flags.no_site
            or not sys.dont_write_bytecode or str(Path(__file__))!=STORE+'/source/linux_lease_control_ci.py'):
        raise ValueError('fixed installed native root isolated OS Python required')
    # start.json is root-created by the independently reviewed literal workflow
    # BEFORE copying/importing source. Neither argv nor an actor supplies a clock.
    start_raw=installed_read(STORE+'/start.json',65536);start=json.loads(start_raw,object_pairs_hook=unique_object)
    source_raw=installed_read(STORE+'/source-manifest.json',65536)
    manifest=source_manifest(source_raw,start['source_manifest_sha256'])
    check_member(manifest,'linux_lease_control_ci.py',installed_read(str(Path(__file__)),1024**2))
    pid=os.getpid();actual_start=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]
    budget=SuiteBudget.admit(start,pid=pid,start=actual_start,manifest=sha(source_raw),now=time.monotonic())
    control=installed_module('linux_lease_control.py',manifest)
    g=installed_module('linux_guardian.py',manifest)
    base={'suite/start.json':start_raw,'suite/sources.json':source_raw}
    for name in MEMBERS:
        raw=installed_read(STORE+'/source/'+name,1024**2);check_member(manifest,name,raw);base['source/'+name]=raw
    directory=None;outcome=None
    try:caller=control.original_caller(g)
    except control.CallerAncestryError as failure:
        # Refusal is unchanged. Preserve observed pinned UID/executable facts
        # before bounded export; never guess a CI privilege-transition exception.
        persist_observation(g,base,'suite/caller.json',failure.facts)
        outcome={'schema':'TEST_ONLY-ci-suite/v1','status':'FAIL','executed':False,'control_passed':False,
            'production_capture_accepted':False,'started':budget.started,'deadline':budget.deadline,
            'finished':time.monotonic(),'reason':type(failure).__name__+': '+str(failure)[:2000]}
        files=owned_exports(g,base,None,outcome,budget)
        write_fixed(Path(STORE,'result.json'),files['suite/result.json'])
        send_export(files,outcome,budget)
        return 1
    caller.verify()
    persist_observation(g,base,'suite/caller.json',{'pid':caller.pid,'start':caller.start,'uid':caller.uid,'ppid':caller.ppid})
    context_raw=installed_read(STORE+'/ci-context.json',65536)
    context=workflow_context(context_raw,sha(source_raw))
    try:os_release=g.protected_read('/usr/lib/os-release',maximum=65536)
    except FileNotFoundError:os_release=None
    persist_observation(g,base,'suite/context.json',{'workflow':context,'workflow_context_sha256':sha(context_raw),
        'observed_os_release':None if os_release is None else os_release.decode('utf-8'),
        'os_release_sha256':None if os_release is None else sha(os_release),
        'kernel':platform.release(),'machine':platform.machine(),'python':sys.version,
        'runner_image_build_identity':None,
        'limit':'workflow labels are attribution, not independent native authority; image build identity unobserved'})
    try:
        budget.require_work(time.monotonic())
        # Warm the actual NSS and all fixed inert fixture imports before pinning
        # actual loaded stdlib/native bytes. No code calls a model/runtime loader.
        principal=control.ci_principal_facts(g,caller)
        persist_observation(g,base,'suite/principal.json',principal)
        for name in ('linux_lease_control_child.py','linux_network.py','linux_runtime_filter.py','qwen_backend.py'):
            installed_module(name,manifest)
        kernel=admit_ci_root(g)
        persist_observation(g,base,'suite/kernel.json',kernel)
        rows,installation=discover_closure(g,control,budget)
        persist_observation(g,base,'suite/installation.json',installation)
        write_fixed(Path(STORE,'host.json'),canonical({'schema':control.SCHEMA,'files':rows})+b'\n')
        host,profile,prerequisites=control.load_ci_control_host(g,'baseline',caller)
        persist_observation(g,base,'suite/host.json',{'kernel':kernel,'host':host,'prerequisites':prerequisites})
        budget.require_work(time.monotonic())
    except (PrerequisiteUnavailable,control.CiPrerequisiteUnavailable) as failure:
        # Only explicitly observed initial native absence is neutral. Source,
        # ownership, closure, issuer and unknown errors propagate as failures.
        elapsed=time.monotonic()>=budget.deadline-10
        if failure.facts is not None:
            persist_observation(g,base,'suite/availability.json',failure.facts)
        outcome={'schema':'TEST_ONLY-ci-suite/v1','status':'FAIL' if elapsed else 'SKIP','executed':False,'control_passed':False,
            'production_capture_accepted':False,'started':budget.started,'deadline':budget.deadline,
            'finished':time.monotonic(),'reason':type(failure).__name__+': '+str(failure)[:2000]}
    if outcome is None:
        g.prctl(4,0);g.prctl(36,1)
        parent=Path(STORE,'ci-attempts');parent.mkdir(mode=0o700)
        directory=parent/os.urandom(24).hex();directory.mkdir(mode=0o700)
        identity=g.Identity(os.getpid())
        try:outcome=execute_suite(g,control,caller,budget,directory)
        finally:identity.close()
    if caller is not None:caller.close()
    files=owned_exports(g,base,directory,outcome,budget)
    write_fixed(Path(STORE,'result.json'),files['suite/result.json'])
    send_export(files,outcome,budget)
    return 0 if outcome['status']=='PASS' else 77 if outcome['status']=='SKIP' else 1


def receiver_main()->int:
    import os,sys,time
    if os.geteuid()==0:raise ValueError('artifact receiver must be unprivileged')
    raw=sys.stdin.buffer.read(MAX_STREAM+1);result=receive_export(raw)
    began,deadline=(finite(result['outcome'].get(key)) for key in ('started','deadline'))
    def checkpoint()->None:
        if deadline!=began+900 or not began<=time.monotonic()<deadline:
            raise ValueError('original whole-control ceiling during nonroot local export')
    checkpoint()
    # The nonroot working directory is fixed by the literal workflow. Root never
    # receives or opens it. No absolute paths, symlinks or existing overwrite.
    root=Path.cwd()
    for name,data in result['files'].items():
        checkpoint()
        path=root/name
        for parent in reversed(path.parent.relative_to(root).parents):
            if str(parent)=='.':continue
            selected=root/parent
            if selected.exists() and selected.is_symlink():raise ValueError('artifact staging symlink')
            selected.mkdir(mode=0o700,exist_ok=True)
        path.parent.mkdir(mode=0o700,exist_ok=True)
        if path.parent.is_symlink():raise ValueError('artifact staging symlink')
        write_fixed(path,data)
    write_fixed(root/'export-manifest.json',canonical(result['manifest'])+b'\n')
    write_fixed(root/'native-outcome.json',canonical(result['outcome'])+b'\n')
    checkpoint()
    return 0 if result['outcome']['status'] in ('PASS','SKIP') else 1


def native_disposition(outcome:Any,native_exit:int,receiver_exit:int)->dict[str,Any]:
    """Native process/transport failure cannot leave a successful artifact verdict."""
    if (type(native_exit) is int and type(receiver_exit) is int and isinstance(outcome,dict)
            and outcome.get('production_capture_accepted') is False):
        status=outcome.get('status')
        if (receiver_exit==0 and native_exit==0 and status=='PASS'
                and outcome.get('control_passed') is True and outcome.get('executed') is True):return outcome
        if (receiver_exit==0 and native_exit==77 and status=='SKIP'
                and outcome.get('control_passed') is False and outcome.get('executed') is False):return outcome
        if native_exit not in (0,77) and status in ('FAIL','UNVERIFIED') and outcome.get('control_passed') is False:
            return outcome
    return {'schema':'TEST_ONLY-ci-native-disposition/v1','status':'UNVERIFIED','control_passed':False,
        'production_capture_accepted':False,'executed':outcome.get('executed') if isinstance(outcome,dict) else None,
        'native_exit':native_exit,'receiver_exit':receiver_exit,
        'reason':'complete root receipt and actual native/receiver terminal status do not agree'}


def disposition_main()->int:
    import os,time
    if os.geteuid()==0:raise ValueError('native disposition writer must be nonroot')
    def read(name:str,maximum:int)->bytes:
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            raw=os.read(fd,maximum+1)
            if len(raw)>maximum:raise ValueError('bounded disposition input required')
            return raw
        finally:os.close(fd)
    native=int(read('native-exit.txt',32));receiver=int(read('receiver-exit.txt',32))
    try:outcome=json.loads(read('native-outcome.json',MAX_FILE),object_pairs_hook=unique_object)
    except (OSError,ValueError):outcome=None
    result=native_disposition(outcome,native,receiver)
    if result['status'] in ('PASS','SKIP'):
        try:
            began,deadline=(finite(result.get(key)) for key in ('started','deadline'))
            if deadline!=began+900 or not began<=time.monotonic()<deadline:raise ValueError('expired')
        except ValueError:
            result={'schema':'TEST_ONLY-ci-native-disposition/v1','status':'UNVERIFIED','control_passed':False,
                'production_capture_accepted':False,'executed':result.get('executed'),
                'reason':'original900 ceiling exceeded or missing before local export disposition'}
    write_fixed(Path('native-disposition.json'),canonical(result)+b'\n')
    return 0 if result['status'] in ('PASS','SKIP') else 1


def main()->int:
    import sys
    if sys.argv[1:]==['--ci-suite']:return suite_main()
    if sys.argv[1:]==['--receive']:return receiver_main()
    if sys.argv[1:]==['--disposition']:return disposition_main()
    raise ValueError('closed fixed ci-suite or nonroot artifact entry required')


if __name__=='__main__':raise SystemExit(main())
