"""Fixed external remap DATA and original-suite-owned technical fixtures.

Pure plans/checks cannot choose H, grant filesystem access, restore completions or
issue extraction authority. Actual appointment and comparison-v2 wiring are held.
"""
from __future__ import annotations
import copy
import math
import os
from pathlib import PurePosixPath
import re
import stat
import time
from typing import Any
from . import source_metadata as sm
from . import pdf_comparison_capture as c
from . import source_native_observation as n
from . import pdf_native_bridge as bridge
from . import pdf_output_origin as origin

MIB=1048576
RECIPES=(('identity','identity-remap.txt',b'0041 0041\n'),
         ('a-to-b','a-to-b-remap.txt',b'0041 0042\n'),
         ('a-to-ab','a-to-ab-remap.txt',b'0041 0041 0042\n'))
PAIR_KEYS={'schema','purpose','fixture_id','fixture','config','resource','archive_sha256','patch_sha256','build_pair','schedule_index','suite_selection_sha256'}
PLAN_KEYS={'schema','purpose','capture_kind','pair_plan_sha256','fixture','config','resource','build_identity_sha256','executable_path','executable','candidate_inventory_sha256','recorder_inventory_sha256','limits_sha256','schedule_index'}
RESOURCE_KEYS={'schema','control','blob','path','identity','association_sha256'}
ASSOCIATION_KEYS={'schema','control','fixture_id','fixture','resource_path','resource_blob','resource_identity','native_config'}


class RemapHold(ValueError):
    """Unproved DATA/custody, never an authorization or successful native result."""


def _closed(value:Any,keys:set[str])->None:
    if type(value) is not dict or set(value)!=keys:raise RemapHold('closed fixed remap DATA required')


def _root(value:Any)->str:
    if (type(value) is not str or not value.isascii() or not value.startswith('/') or value=='/'
            or str(PurePosixPath(value))!=value or any(not re.fullmatch(r'[A-Za-z0-9._-]+',part)
                or part in ('.','..') for part in value.split('/')[1:])
            or value.split('/')[1] in ('proc','sys','dev')):raise RemapHold('canonical fixed technical root required')
    if any(len((value+'/'+name).encode('ascii'))>4096 for _,name,_ in RECIPES):raise RemapHold('bounded external resource path required')
    return value


def _identity(value:Any,size:int)->list[int]:
    if type(value) is not list or len(value)!=9:raise RemapHold('nine-field staged identity required')
    for i,item in enumerate(value):
        n._integer(item,-2**63 if i>=7 else 0,2**63-1 if i>=7 else 2**64-1)
    if value[1]<1 or value[2]!=stat.S_IFREG|0o444 or value[5]!=1 or value[6]!=size:
        raise RemapHold('single-link regular0444 exact staged identity required')
    return value


def _blob(raw:bytes,archive:dict)->dict:
    if type(raw) is not bytes:raise RemapHold('exact retained remap bytes required')
    archive[sm.sha256(raw)]=raw
    return {'sha256':sm.sha256(raw),'bytes':len(raw)}


def _record(value:Any,archive:dict)->str:
    raw=sm.canonical(value)
    if len(raw)>MIB:raise RemapHold('bounded canonical remap record required')
    return _blob(raw,archive)['sha256']


def _fixed_resource(control:str,root:str,identity:list[int],archive:dict)->tuple[dict,dict]:
    try:_,name,data=next(row for row in RECIPES if row[0]==control)
    except StopIteration as error:raise RemapHold('fixed remap control required') from error
    path=_root(root)+'/'+name;config=b'unicodeRemapping '+path.encode('ascii')+b'\n'
    if len(config)>8192:raise RemapHold('bounded raw native config required')
    resource_blob=_blob(data,archive);config_blob=_blob(config,archive)
    association={'schema':'TEST_ONLY-pdf-external-remap-association/v1','control':control,
        'fixture_id':c.FIXTURES[0][0],'fixture':{'sha256':c.FIXTURES[0][1],'bytes':c.FIXTURES[0][2]},
        'resource_path':path,'resource_blob':resource_blob,'resource_identity':copy.deepcopy(_identity(identity,len(data))),
        'native_config':config_blob}
    resource={'schema':'TEST_ONLY-pdf-external-remap-resource/v1','control':control,'blob':resource_blob,
        'path':path,'identity':copy.deepcopy(identity),'association_sha256':_record(association,archive)}
    return resource,config_blob


def _resource(resource:dict,archive:dict)->dict:
    _closed(resource,RESOURCE_KEYS)
    control=resource['control']
    try:_,name,data=next(row for row in RECIPES if row[0]==control)
    except StopIteration as error:raise RemapHold('fixed resource control required') from error
    path=resource['path']
    if type(path) is not str or not path.endswith('/'+name):raise RemapHold('fixed external filename required')
    root=_root(path[:-len(name)-1]);_identity(resource['identity'],len(data))
    if c._blob(resource['blob'],archive,MIB)!=data:raise RemapHold('fixed external resource bytes required')
    association=c._json(archive,resource['association_sha256']);_closed(association,ASSOCIATION_KEYS)
    expected={'schema':'TEST_ONLY-pdf-external-remap-association/v1','control':control,'fixture_id':c.FIXTURES[0][0],
        'fixture':{'sha256':c.FIXTURES[0][1],'bytes':c.FIXTURES[0][2]},'resource_path':root+'/'+name,
        'resource_blob':resource['blob'],'resource_identity':resource['identity'],
        'native_config':{'sha256':sm.sha256(b'unicodeRemapping '+path.encode('ascii')+b'\n'),
                         'bytes':len(b'unicodeRemapping '+path.encode('ascii')+b'\n')}}
    if resource['schema']!='TEST_ONLY-pdf-external-remap-resource/v1' or association!=expected:
        raise RemapHold('acyclic earlier remap association differs')
    c._blob(association['fixture'],archive,256*MIB)
    if c._blob(association['native_config'],archive,8192)!=b'unicodeRemapping '+path.encode('ascii')+b'\n':raise RemapHold('raw native config differs')
    return association


def make_remap_plans(fixture_root:str,identities:dict,ordinary_plan:dict,retained_archive:dict)->tuple[dict,...]:
    """Pure three fixed v2 projections. Passive identities never establish staging."""
    root=_root(fixture_root);_closed(identities,{row[0] for row in RECIPES})
    archive=dict(retained_archive);ordinary=c._plan(ordinary_plan,archive)
    if ordinary['resource'] is not None or ordinary['schedule_index']!=0:raise RemapHold('selected first ordinary fixture plan required')
    results=[]
    for i,(control,_,_) in enumerate(RECIPES):
        current=dict(archive);resource,config=_fixed_resource(control,root,identities[control],current)
        pair=copy.deepcopy(ordinary);pair.update(schema='TEST_ONLY-pdf-pair-plan/v2',schedule_index=18+i,resource=resource,config=config)
        plan=copy.deepcopy(ordinary_plan);plan.update(schema='TEST_ONLY-pdf-baseline-plan/v2',schedule_index=36+2*i,
            pair_plan_sha256=_record(pair,current),resource=copy.deepcopy(resource),config=copy.deepcopy(config))
        candidates=copy.deepcopy(sm._json(c._raw(current,plan['candidate_inventory_sha256'])))
        if any(row['path']==resource['path'] for row in candidates):raise RemapHold('resource candidate collision')
        candidates.append({'path':resource['path'],**resource['blob']})
        plan['candidate_inventory_sha256']=_record(candidates,current)
        packet={'pair_plan':pair,'comparison_plan':plan,'archive':current}
        check_remap_plan(packet);results.append(packet)
    return tuple(results)


def _build_pair(pair:dict,archive:dict)->None:
    # Same fixed association checks as the ordinary comparator; v2 is never
    # relabelled/reinterpreted as a v1 record to get through its closed parser.
    build=pair['build_pair'];c._closed(build,{'pristine_build_sha256','patched_build_sha256','pristine_executable','patched_executable','same_toolchain_recipe_sha256','accepted_differences_sha256'})
    left=c._json(archive,build['pristine_build_sha256'])
    c._closed(left,{'schema','variant','source_archive_sha256','patch_sha256','prepared_tree_sha256','toolchain_recipe_sha256','configuration_recipe_sha256','executable','dependency_inventory_sha256'})
    if (left['schema']!='TEST_ONLY-pdf-comparison-build-selection/v1' or left['variant']!='pristine'
            or left['source_archive_sha256']!=c.ARCHIVE or left['patch_sha256'] is not None
            or left['executable']!=build['pristine_executable'] or left['toolchain_recipe_sha256']!=build['same_toolchain_recipe_sha256']):raise RemapHold('selected pristine build association differs')
    c._hash(left['prepared_tree_sha256']);c._raw(archive,left['toolchain_recipe_sha256']);c._raw(archive,left['configuration_recipe_sha256'])
    n.elf_interpreter(c._blob(left['executable'],archive,256*MIB));c._inventory(sm._json(c._raw(archive,left['dependency_inventory_sha256'])),archive)
    right=c._json(archive,build['patched_build_sha256']);c._closed(right,bridge.BUILD_KEYS);c._closed(right['target'],{'system','machine','elf_class'})
    if (right['schema']!='twin.native-build-identity/v1' or right['source_archive_sha256']!=c.ARCHIVE or right['patch_sha256']!=c.PATCH
            or right['target']!={'system':'Linux','machine':'x86_64','elf_class':64} or type(right['target']['elf_class']) is not int
            or right['toolchain_sha256']!=build['same_toolchain_recipe_sha256'] or right['build_configuration_sha256']!=left['configuration_recipe_sha256']
            or build['patched_executable']!={'sha256':right['executable_sha256'],'bytes':right['executable_bytes']}):raise RemapHold('selected patched build association differs')
    n.elf_interpreter(c._blob(build['patched_executable'],archive,256*MIB))
    for key in ('source_package_sha256','prepared_tree_sha256','build_configuration_sha256','toolchain_sha256','build_log_sha256'):c._raw(archive,right[key])
    c._raw(archive,build['accepted_differences_sha256'])


def check_remap_plan(packet:dict)->dict:
    """Closed DATA only; no v1 adoption, host selection or filesystem operation."""
    _closed(packet,{'pair_plan','comparison_plan','archive'});pair=packet['pair_plan'];plan=packet['comparison_plan'];archive=packet['archive']
    _closed(pair,PAIR_KEYS);_closed(plan,PLAN_KEYS)
    index=c._uint(pair['schedule_index'],20)
    if index not in (18,19,20):raise RemapHold('only three fixed v2 remap pairs required')
    if (pair['schema']!='TEST_ONLY-pdf-pair-plan/v2' or pair['purpose']!='TEST_ONLY' or pair['archive_sha256']!=c.ARCHIVE
            or pair['patch_sha256']!=c.PATCH or pair['fixture_id']!=c.FIXTURES[0][0]
            or pair['fixture']!={'sha256':c.FIXTURES[0][1],'bytes':c.FIXTURES[0][2]}):raise RemapHold('fixed first-fixture remap pair required')
    c._hash(pair['suite_selection_sha256']);association=_resource(pair['resource'],archive)
    if pair['resource']['control']!=RECIPES[index-18][0] or pair['config']!=association['native_config']:raise RemapHold('control/schedule/native-config relation differs')
    _build_pair(pair,archive)
    if (plan['schema']!='TEST_ONLY-pdf-baseline-plan/v2' or plan['purpose']!='TEST_ONLY' or plan['capture_kind']!='pristine-comparative-data'
            or c._uint(plan['schedule_index'])!=2*index or c._json(archive,plan['pair_plan_sha256'])!=pair
            or any(plan[key]!=pair[key] for key in ('fixture','config','resource'))
            or plan['build_identity_sha256']!=pair['build_pair']['pristine_build_sha256'] or plan['executable']!=pair['build_pair']['pristine_executable']
            or c._json(archive,plan['limits_sha256'])!=c.LIMITS):raise RemapHold('explicit v2 comparison relation differs')
    rows=c._inventory(sm._json(c._raw(archive,plan['candidate_inventory_sha256'])),archive)
    c._inventory(sm._json(c._raw(archive,plan['recorder_inventory_sha256'])),archive)
    executable=next((row for row in rows if row['path']==n._path(plan['executable_path'])),None)
    if executable is None or {k:executable[k] for k in ('sha256','bytes')}!=plan['executable']:raise RemapHold('selected executable candidate differs')
    resource=pair['resource'];candidate={'path':resource['path'],**resource['blob']}
    if [row for row in rows if row['path']==resource['path']]!=[candidate]:raise RemapHold('exact external candidate required')
    # The fixed external resource is the sole v2 addition to the accepted
    # pristine build's ordinary dependency map. Retained bytes do not select
    # another library. Recorder and fixed workspace additions stay separate.
    c._reconcile_build_candidates(pair,[row for row in rows if row['path']!=resource['path']],archive)
    root=resource['path'].rsplit('/',1)[0]
    if any(row['path']==root+'/'+name for row in rows for control,name,_ in RECIPES if control!=resource['control']):raise RemapHold('only selected resource belongs to each run')
    return association


def remap_native_projection(packet:dict,patched_wrapper:bytes|None=None)->dict:
    """Project existing native fields and earlier H evidence, never choose H."""
    association=check_remap_plan(packet);pair=packet['pair_plan'];resource=pair['resource'];archive=packet['archive']
    evidence={pin:c._raw(archive,pin) for pin in (resource['blob']['sha256'],pair['config']['sha256'],resource['association_sha256'])}
    wrapper_pin=None
    build_key='pristine_build_sha256' if patched_wrapper is None else 'patched_build_sha256'
    build_pin=pair['build_pair'][build_key];evidence[build_pin]=c._raw(archive,build_pin)
    if patched_wrapper is not None:
        if type(patched_wrapper) is not bytes or len(patched_wrapper)>MIB:raise RemapHold('bounded patched wrapper required')
        wrapper=sm._json(patched_wrapper);_closed(wrapper,bridge.CONFIG_KEYS)
        if (sm.canonical(wrapper)!=patched_wrapper or wrapper['profile']!=bridge.PROFILE or wrapper['native_config_sha256']!=pair['config']['sha256']
                or wrapper['pdf_origin']['build_identity_sha256']!=pair['build_pair']['patched_build_sha256']):raise RemapHold('distinct patched wrapper/build/config relation required')
        wrapper_pin=sm.sha256(patched_wrapper)
        if wrapper_pin==pair['config']['sha256']:raise RemapHold('raw config is not JSON wrapper')
        evidence[wrapper_pin]=patched_wrapper
    return {'platform_file':{'path':resource['path'],**resource['blob']},'evidence':evidence,
            'native_config_sha256':association['native_config']['sha256'],'patched_wrapper_sha256':wrapper_pin}


def check_remap_host_evidence(packet:dict,policy:dict,evidence:dict,patched_wrapper:bytes|None=None)->None:
    """Pure H consistency only; supplied DATA never becomes a host context."""
    projection=remap_native_projection(packet,patched_wrapper);n._validate_host_policy(policy)
    if not n._inside(projection['platform_file']['path'],policy['roots']):raise RemapHold('external resource outside independently selected H roots')
    for pin,raw in projection['evidence'].items():
        if pin not in policy['evidence_sha256s'] or c._raw(evidence,pin)!=raw:raise RemapHold('independent H config/resource/association evidence absent')


def _full_original_reads(observation:dict,archive:dict,wanted:dict[str,dict])->dict:
    """Additional fixed stdio gate AFTER unchanged native replay, not a replay issuer."""
    fds={row['fd']:{'path':None,'generation':0} for row in observation['events'][0]['data']['fds']}
    generations={fd:0 for fd in fds}
    opens:dict[str,list[tuple[int,int,int]]]={path:[] for path in wanted}
    reads:dict[str,list[dict]]={path:[] for path in wanted};pending=None
    for event in observation['events']:
        kind=event['kind'];data=event['data']
        if kind=='enter':
            name=n.SYSCALLS[str(data['nr'])];args=data['args'];detail=data['detail']
            touched=[fds.get(args[0],{}).get('path')]
            if name in ('dup2','dup3'):touched.append(fds.get(args[1],{}).get('path'))
            if name=='mmap':touched.append(fds.get(args[4],{}).get('path'))
            if any(path in wanted for path in touched) and (name in ('dup','dup2','dup3','lseek','mmap') or name=='fcntl' and args[1] in (0,1030)):
                raise RemapHold('resource/config alias, seek or mapping remains held')
            pending=(name,args,detail,event['seq'])
        elif kind=='leave':
            if pending is None:raise RemapHold('checked original syscall pair required')
            name,args,detail,entry_seq=pending;pending=None;result=data['result']
            if name in ('open','openat') and result<0 and detail['path'] in wanted:raise RemapHold('failed intended resource/config open')
            if name in ('open','openat') and result>=0:
                path=detail['path'];generation=generations.get(result,-1)+1;generations[result]=generation
                description={'path':path,'generation':generation,'open_seq':event['seq'],'offset':0,'identity':data['detail']['identity']}
                fds[result]=description
                if path in wanted:
                    if set(detail)!={'path'} or data['detail']['kind']!='file' or description['identity']!=wanted[path]['identity']:
                        raise RemapHold('exact original resource open/file identity required')
                    opens[path].append((event['seq'],result,generation))
                    if len(opens[path])!=1:raise RemapHold('resource/config reopened or replaced')
            elif name in ('read','readv','pread64'):
                desc=fds.get(args[0],{});path=desc.get('path')
                if path in wanted:
                    expected=wanted[path];offset=args[3] if name=='pread64' else desc['offset']
                    count=sum(row[1] for row in detail['iovecs']) if name=='readv' else args[2]
                    if (result==expected['bytes'] and offset==0 and count>0 and result<=count
                            and data['detail']['buffer_bytes']==result and data['detail']['buffer_sha256']==expected['sha256']):
                        reads[path].append({'open_seq':desc['open_seq'],'read_seq':event['seq'],'fd':args[0],
                            'generation':desc['generation'],'offset':0,'bytes':result})
                    elif not (result==0 and offset==expected['bytes'] and reads[path]):
                        raise RemapHold('complete offset0 original resource/config read required')
                if name!='pread64' and result>=0 and 'offset' in desc:desc['offset']+=result
            elif name=='close':
                desc=fds.get(args[0],{})
                if desc.get('path') in wanted and result!=0:raise RemapHold('uncertain original file-description close')
                if result==0:fds.pop(args[0],None)
            elif name in ('dup','dup2','dup3','fcntl'):
                if result>=0 and (name!='fcntl' or args[1] in (0,1030)):
                    generations[result]=generations.get(result,-1)+1
                    fds[result]={**fds[args[0]],'generation':generations[result]}
            elif name=='lseek' and result>=0 and 'offset' in fds.get(args[0],{}):fds[args[0]]['offset']=result
        elif kind=='exit-stop':pending=None
        if kind in ('exec','leave'):
            maps=data.get('maps',data.get('detail',{}).get('maps',[]))
            if any(row.get('path') in wanted for row in maps):raise RemapHold('resource/config mapped rather than fixed stdio')
    if any(len(opens[path])!=1 or not reads[path] for path in wanted):raise RemapHold('declared but unused intended resource/config')
    return reads


def check_remap_control(packet:dict,baseline:dict,patched:dict)->dict:
    """Pure read/effect DATA gate. No private completion restoration or launch path.

    The later fixed driver must supply separately acquired/checked completions;
    this extra gate reruns their unchanged trace/binding/origin consistency checks.
    Its return is not an acquisition receipt or permission to continue a suite.
    """
    association=check_remap_plan(packet);pair=packet['pair_plan'];resource=pair['resource'];selected=packet['archive']
    for bundle in (baseline,patched):_closed(bundle,{'observation','archive','plan'})
    left,left_archive=baseline['observation'],baseline['archive'];right,right_archive=patched['observation'],patched['archive']
    if baseline['plan']!=packet['comparison_plan']:raise RemapHold('same preselected v2 pristine plan required')
    mode='SIMULATED_DATA' if left['purpose']=='TEST_ONLY' else 'actual'
    c.check_comparison_events(left,left_archive,observation_mode=mode)
    if (left['spec']['plan_sha256']!=sm.sha256(sm.canonical(baseline['plan']))
            or left['spec']['candidates']!=c._candidate_rows(baseline['plan'],selected,left['spec']['cwd'])):
        raise RemapHold('pristine v2 plan/input/config/candidate binding differs')
    parent=c._blob(pair['fixture'],selected,256*MIB);native_plan=patched['plan']
    config,closure=bridge._validate_plan(native_plan,parent)
    invocation={'schema':'twin.source-extraction-invocation/v1','argv':right['spec']['argv'],'cwd':right['spec']['cwd'],
        'environment':right['spec']['environment'],'stdin':'OWNED-EOF-PIPE'}
    bridge._binding(right,native_plan,parent,invocation)
    if (config['native_config_sha256']!=pair['config']['sha256']
            or config['pdf_origin']['build_identity_sha256']!=pair['build_pair']['patched_build_sha256']):raise RemapHold('patched config/build pair association differs')
    projection=remap_native_projection(packet,c._raw(native_plan['archive'],native_plan['configuration_sha256']))
    if [row for row in closure['platform_files'] if row['path']==resource['path']]!=[projection['platform_file']]:raise RemapHold('patched external platform candidate absent/substituted')
    n.verify_native_observation(right,right_archive,purpose=right['purpose'])
    if right['purpose']!=left['purpose']:raise RemapHold('same comparative observation purpose required')
    read_facts=[]
    for observation,archive in ((left,left_archive),(right,right_archive)):
        config_path=observation['spec']['cwd']+'/native-config'
        wanted={}
        for path,blob,identity in ((resource['path'],resource['blob'],resource['identity']),
                (config_path,pair['config'],None)):
            row=observation['files'].get(path)
            if (row is None or any(row[key]!=blob[key] for key in ('sha256','bytes'))
                    or identity is not None and row['identity']!=identity
                    or c._raw(archive,blob['sha256'])!=c._raw(selected,blob['sha256'])):raise RemapHold('independently observed original candidate bytes/identity differ')
            wanted[path]=row
        if observation['purpose']=='actual':
            policy=c._json(archive,observation['host_policy_sha256'])
            wrapper=c._raw(native_plan['archive'],native_plan['configuration_sha256']) if observation is right else None
            check_remap_host_evidence(packet,policy,archive,wrapper)
        read_facts.append(_full_original_reads(observation,archive,wanted))
    terminal=right['events'][-1]['data'];stdout=c._raw(right_archive,terminal['stdout_sha256']);wire=c._raw(right_archive,terminal['origin_sha256'])
    mapping=origin.check_pdf_origin_events(stdout,wire)
    import json
    events=[json.loads(line) for line in wire.splitlines()];items=[row for row in events if row.get('record')=='item' and row['input_scalars']==[65]]
    expected={'identity':([65],'none'),'a-to-b':([66],'unicode-remap'),'a-to-ab':([65,66],'unicode-remap')}[resource['control']]
    if not items or any((row['scalars'],row['taint'])!=expected for row in items):raise RemapHold('actual origin inputA/remap effect absent or contradictory')
    if resource['control']!='identity':
        item_ids={row['item'] for row in items}
        for row in events:
            if row.get('record')=='emit' and row['origin_item'] in item_ids:
                if row['operation']!='modified' or row['reason'] not in ('remap','mirror','duplicate'):raise RemapHold('modified remap classification required')
                try:origin.check_pdf_witness(mapping,row['start'],row['end'])
                except origin.PdfOriginHold:pass
                else:raise RemapHold('changed remap output cannot be eligible publisher witness')
    equality={name:c._raw(left_archive,left['events'][-1]['data'][name+'_sha256'])==c._raw(right_archive,terminal[name+'_sha256']) for name in ('stdout','stderr')}
    equality['exit']=(left['events'][-1]['data']['wait']['kind'],left['events'][-1]['data']['wait']['raw_status'])==(terminal['wait']['kind'],terminal['wait']['raw_status'])
    if not all(equality.values()):raise RemapHold('adverse remap pair: stop, retain originals, no retry')
    return {'schema':'TEST_ONLY-pdf-remap-read-effect-data/v1','qualification':'NONE','scope':'DATA-only-no-native-authority',
        'control':resource['control'],'pair_plan_sha256':sm.sha256(sm.canonical(pair)),'association_sha256':resource['association_sha256'],
        'baseline_observation_sha256':sm.sha256(sm.canonical(left)),'patched_observation_sha256':sm.sha256(sm.canonical(right)),
        'intended_reads':read_facts,'input_a_items':len(items),'stream_exit_equality':equality,
        'origin_map_sha256':sm.sha256(mapping.description)}


# These fixed bodies are reachable only through a held original carrier. There is
# deliberately no selector, public stage constructor, importer or driver wiring.
class _StageState:
    def __new__(cls,*args:Any,**kwargs:Any)->Any:
        raise RemapHold('private original-suite technical custody required')

    def __copy__(self)->Any:raise RemapHold('technical custody cannot be copied')
    def __deepcopy__(self,memo:Any)->Any:raise RemapHold('technical custody cannot be copied')
    def __reduce__(self)->Any:raise RemapHold('technical custody cannot be serialized')

    phase:str
    root:str
    deadline:float|None
    final_deadline:float|None
    final_attempted:bool
    last_time:float|None
    root_removal_known:bool
    clock_observation:dict
    guard:Any
    fds:set[int]
    uncertain:bool
    parent_fd:int|None
    root_fd:int|None
    parent_identity:list[int]|None
    root_identity:list[int]|None
    owned:dict[str,list[int]]
    identities:dict[str,list[int]]
    facts:list[dict]
    failure:dict|None


def _guard_callback(*args:Any)->None:
    pass


def _source_guard()->Any:
    import sys
    policy={'purpose':'TEST_ONLY','allowed_transforms':[],'reviewer_id':'remap-source-binding','reviewer_role':'source-binding-only'}
    return sm.MetadataAuthority.freeze('remap-source-guard','remap-source-bindings','1',sm.sha256(sm.canonical(policy)),
        _guard_callback,_guard_callback,policy=policy,helper_modules=(sys.modules[__name__],c,n,bridge,origin))


def _stat_identity(value:Any)->list[int]:
    return [value.st_dev,value.st_ino,value.st_mode,value.st_uid,value.st_gid,value.st_nlink,value.st_size,value.st_mtime_ns,value.st_ctime_ns]


def _fault(error:BaseException)->dict:
    # Fixed names/errno only, never an unbounded or private exception message.
    return {'kind':type(error).__name__[:128],'errno':getattr(error,'errno',None) if type(getattr(error,'errno',None)) is int else None}


def _clock()->float:
    now=time.monotonic()
    if type(now) not in (int,float) or not math.isfinite(now):raise RemapHold('unknown original technical clock')
    return now


def _clock_value(state:_StageState,deadline:float|None)->float:
    state.clock_observation={'at':None,'deadline':deadline,'status':'UNKNOWN'}
    try:now=_clock()
    except BaseException:
        _remember(state,'clock-hold',observation=copy.deepcopy(state.clock_observation))
        raise
    state.clock_observation={'at':now,'deadline':deadline,'status':'OBSERVED'}
    return now


def _tick(state:_StageState,deadline:float|None)->None:
    now=_clock_value(state,deadline)
    status=('UNKNOWN' if deadline is None else 'NONMONOTONIC' if state.last_time is not None and now<state.last_time
            else 'LATE' if now>=deadline else 'ONTIME')
    state.clock_observation['status']=status
    if state.last_time is None or now>state.last_time:state.last_time=now
    if status!='ONTIME':
        _remember(state,'clock-hold',observation=copy.deepcopy(state.clock_observation))
        raise RemapHold('original technical deadline exhausted/unknown/nonmonotonic')


def _remember(state:_StageState,operation:str,**facts:Any)->None:
    if len(state.facts)>=8192:raise RemapHold('finite technical custody record capacity exhausted')
    state.facts.append({'operation':operation,**facts})


def _open(state:_StageState,path:str,flags:int,deadline:float|None,*,dir_fd:int|None=None,mode:int=0o600)->int:
    _tick(state,deadline)
    # If a BaseException prevents a result, acquisition ownership is unknown.
    prior=state.uncertain;state.uncertain=True
    try:fd=os.open(path,flags,mode,dir_fd=dir_fd)
    except OSError:
        state.uncertain=prior
        raise
    state.fds.add(fd);state.uncertain=prior
    _remember(state,'open',fd=fd,path=path)
    _tick(state,deadline)
    return fd


def _close(state:_StageState,fd:int)->None:
    if fd not in state.fds:raise RemapHold('owned technical descriptor required')
    # Transfer out of the retry set BEFORE close: an error never authorizes a
    # second close of a possibly reused numeric descriptor.
    state.fds.remove(fd);prior=state.uncertain;state.uncertain=True
    os.close(fd)
    state.uncertain=prior;_remember(state,'close',fd=fd)


def _close_remaining(state:_StageState,*,transient_only:bool=False)->None:
    for fd in sorted(state.fds):
        if transient_only and fd in (state.parent_fd,state.root_fd):continue
        try:_close(state,fd)
        except BaseException as error:
            state.uncertain=True;_remember(state,'close-fault',fd=fd,error=_fault(error))


def _directory(value:list[int],uid:int,*,private:bool)->None:
    if (not stat.S_ISDIR(value[2]) or value[1]<1 or value[3]!=uid
            or (stat.S_IMODE(value[2])!=0o700 if private else bool(value[2]&0o022))):raise RemapHold('owned protected directory required')


def _same_inode(left:list[int],right:list[int])->bool:
    return left[:5]==right[:5]


def _binding(state:_StageState)->None:
    if state.parent_fd is None or state.root_fd is None or state.parent_identity is None or state.root_identity is None:raise RemapHold('owned staged directory binding absent')
    parent,name=state.root.rsplit('/',1)
    if (not _same_inode(_stat_identity(os.fstat(state.parent_fd)),state.parent_identity)
            or not _same_inode(_stat_identity(os.stat(parent,follow_symlinks=False)),state.parent_identity)
            or not _same_inode(_stat_identity(os.fstat(state.root_fd)),state.root_identity)
            or not _same_inode(_stat_identity(os.stat(name,dir_fd=state.parent_fd,follow_symlinks=False)),state.root_identity)):
        raise RemapHold('staged parent/root identity replaced')


def _remove_owned(state:_StageState,deadline:float|None)->None:
    if state.uncertain:raise RemapHold('uncertain technical ownership: preserve root')
    _tick(state,deadline);_binding(state);_tick(state,deadline)
    for name,identity in list(state.owned.items()):
        _tick(state,deadline);_binding(state);_tick(state,deadline)
        actual=_stat_identity(os.stat(name,dir_fd=state.root_fd,follow_symlinks=False))
        if actual!=identity:raise RemapHold('owned fixed resource replaced: preserve root')
        _tick(state,deadline)
        state.uncertain=True
        os.unlink(name,dir_fd=state.root_fd)
        state.uncertain=False;del state.owned[name];_remember(state,'unlink',path=name)
    _tick(state,deadline);_binding(state);_tick(state,deadline)
    state.uncertain=True
    os.rmdir(state.root.rsplit('/',1)[1],dir_fd=state.parent_fd)
    state.uncertain=False;state.root_removal_known=True;_remember(state,'rmdir',path=state.root)
    _close_remaining(state)
    _tick(state,deadline)  # Includes the returned rmdir and every final close.
    if state.uncertain:raise RemapHold('technical close ownership uncertain after removal')
    state.phase='REMOVED'


def _stage_data(state:_StageState)->dict:
    value={'schema':'TEST_ONLY-pdf-remap-technical-custody/v1','qualification':'NONE','phase':state.phase,
        'root':state.root,'stage_deadline':state.deadline,'final_cleanup_deadline':state.final_deadline,
        'uncertain_ownership':state.uncertain,'open_fds':sorted(state.fds),'created_files':sorted(state.owned),
        'identities':state.identities,'facts':state.facts,'failure':state.failure,
        'root_removal_known':state.root_removal_known,'clock_observation':state.clock_observation}
    raw=sm.canonical(value)
    if len(raw)>2*MIB:raise RemapHold('technical retention exceeds charged capacity')
    return copy.deepcopy(value)


def _success_data(state:_StageState,deadline:float|None)->dict:
    # Bound serialization/copying precedes the final success observation as well.
    data=_stage_data(state);_tick(state,deadline)
    data['clock_observation']=copy.deepcopy(state.clock_observation)
    return data


def _stage_remap_resources(original:c.OriginalComparisonSuite,fixture_root:str)->dict:
    """Unappointed fixed source seam; passive paths/records cannot authorize OS.

    The placeholder survives every failure. No reset, adoption or second attempt
    exists. A future reviewed selector must hold the original source capability.
    """
    c._check_original_suite(original)
    if (original._technical_state is not None or original._stopped or original._next!=0
            or original._active_slot is not None or not original._target_custody_known or original._awaiting_comparison):raise RemapHold('initial original suite staging slot required')
    state=object.__new__(_StageState)
    state.phase='ALLOCATED';state.root='';state.deadline=None;state.final_deadline=None;state.final_attempted=False;state.last_time=None
    state.root_removal_known=False;state.clock_observation={'at':None,'deadline':None,'status':'NOT_OBSERVED'}
    state.guard=None;state.fds=set();state.uncertain=False;state.parent_fd=None;state.root_fd=None
    state.parent_identity=None;state.root_identity=None;state.owned={};state.identities={};state.facts=[];state.failure=None
    original._technical_state=state  # Before root parsing, source reads or clocks.
    try:
        # Reserve the complete finite custody/three-blob bound before retention;
        # never refund, including a rejected stage. No independent byte ledger.
        c._charge_technical_bytes(original,2*MIB)
        state.root=_root(fixture_root);now=_clock_value(state,None)
        if now<original._started:raise RemapHold('technical clock precedes original suite')
        state.last_time=now;state.deadline=min(now+5,original._started+60,original._started+c.B_SECONDS)
        _tick(state,state.deadline);state.guard=_source_guard();state.guard.verify();_tick(state,state.deadline)
        state.phase='STAGING';parent,name=state.root.rsplit('/',1);parent=parent or '/'
        flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
        fd=_open(state,'/',flags,state.deadline)
        for component in parent.split('/')[1:]:
            if not component:continue
            next_fd=_open(state,component,flags,state.deadline,dir_fd=fd);_close(state,fd);fd=next_fd
        state.parent_fd=fd;state.parent_identity=_stat_identity(os.fstat(fd));_directory(state.parent_identity,os.geteuid(),private=True)
        _tick(state,state.deadline);state.uncertain=True
        os.mkdir(name,0o700,dir_fd=fd)
        state.uncertain=False;_remember(state,'mkdir',path=state.root)
        state.root_fd=_open(state,name,flags,state.deadline,dir_fd=fd)
        state.root_identity=_stat_identity(os.fstat(state.root_fd));_directory(state.root_identity,os.geteuid(),private=True)
        _binding(state)
        for control,filename,raw in RECIPES:
            _tick(state,state.deadline);_binding(state)
            writer=_open(state,filename,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,state.deadline,dir_fd=state.root_fd)
            identity=_stat_identity(os.fstat(writer))
            if not stat.S_ISREG(identity[2]) or identity[1]<1 or identity[3]!=os.geteuid() or identity[5]!=1:raise RemapHold('exclusive owned regular writer required')
            state.owned[filename]=identity
            offset=0
            while offset<len(raw):
                _tick(state,state.deadline);count=os.write(writer,raw[offset:])
                if type(count) is not int or count<1 or count>len(raw)-offset:raise RemapHold('positive bounded technical write required')
                offset+=count;state.owned[filename]=_stat_identity(os.fstat(writer));_remember(state,'write',path=filename,bytes=count)
            _tick(state,state.deadline);os.fchmod(writer,0o444);os.fsync(writer)
            written=_stat_identity(os.fstat(writer));state.owned[filename]=written;_identity(written,len(raw))
            _close(state,writer);_binding(state)
            reader=_open(state,filename,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,state.deadline,dir_fd=state.root_fd)
            before=_stat_identity(os.fstat(reader))
            if before!=written:raise RemapHold('original staged readback identity differs')
            got=b''
            while len(got)<=len(raw):
                _tick(state,state.deadline);part=os.read(reader,len(raw)+1-len(got))
                if type(part) is not bytes:raise RemapHold('technical readback bytes required')
                if not part:break
                got+=part
                if len(got)>len(raw):raise RemapHold('technical readback exceeds fixed bytes')
            after=_stat_identity(os.fstat(reader));_tick(state,state.deadline)
            if before!=after or got!=raw or _stat_identity(os.stat(filename,dir_fd=state.root_fd,follow_symlinks=False))!=after:raise RemapHold('staged readback bytes/hash/identity drift')
            _close(state,reader);state.identities[control]=after
            _remember(state,'readback',path=filename,sha256=sm.sha256(got),bytes=len(got),identity=after)
        _tick(state,state.deadline);_binding(state);_tick(state,state.deadline);state.phase='COMPLETE_STAGE'
        return _success_data(state,state.deadline)
    except BaseException as error:
        state.failure=_fault(error);state.phase='FAILED';original._stopped=True
        _close_remaining(state,transient_only=True)
        try:
            if state.root_identity is not None:_remove_owned(state,state.deadline)
            else:_close_remaining(state)
        except BaseException as cleanup_error:
            state.phase='REMOVED_HELD' if state.root_removal_known else 'PRESERVED';_remember(state,'failure-cleanup-hold',error=_fault(cleanup_error));_close_remaining(state)
        raise


def _held_stage_data(original:c.OriginalComparisonSuite)->dict:
    c._check_original_suite(original);state=original._technical_state
    if type(state) is not _StageState:raise RemapHold('one private original technical state required')
    return _stage_data(state)


def _cleanup_remap_resources(original:c.OriginalComparisonSuite)->dict:
    """Once final-suite cleanup, never a retry of failed/partial stage cleanup."""
    c._check_original_suite(original);state=original._technical_state
    if type(state) is not _StageState:raise RemapHold('one private original technical state required')
    if (state.phase!='COMPLETE_STAGE' or state.final_attempted or original._active_slot is not None
            or original._target_custody_known is not True):raise RemapHold('complete stage and independently known terminal targets required')
    original._stopped=True;state.final_attempted=True
    try:
        now=_clock_value(state,None)
        if now<original._started or state.last_time is not None and now<state.last_time:raise RemapHold('final clock precedes original technical interval')
        state.final_deadline=min(now+2,original._started+c.B_SECONDS)
        _tick(state,state.final_deadline);state.guard.verify();_remove_owned(state,state.final_deadline)
        return _success_data(state,state.final_deadline)
    except BaseException as error:
        state.failure=_fault(error);state.phase='REMOVED_HELD' if state.root_removal_known else 'PRESERVED';_close_remaining(state)
        raise
