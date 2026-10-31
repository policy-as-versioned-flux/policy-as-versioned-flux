"""Pure stat-refusal diagnostic models; no actual OS/NSS/proc/child operations."""
import ast
import copy
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
import sys
import pytest
from test_linux_lease_control_ci import ci

SOURCE=Path(__file__).resolve().parents[1]/'bench/pinned-candidate/linux_lease_control_ci.py'
CANDIDATE='/usr/lib/python3.12/TEST_ONLY-member.py'


def model(monkeypatch, size=0):
    m=ci();source=SOURCE.read_text();storage={};reads=[];sent=[];closed=[];now=[150.]
    data={m.STORE+'/source/'+name:b'PURE TEST_ONLY source'for name in m.MEMBERS}
    data.update({'/usr/bin/python3.12':b'PURE TEST_ONLY interpreter',CANDIDATE:b'x'})
    stats={path:SimpleNamespace(st_dev=8,st_ino=i+10,st_mode=0o100444,st_uid=0,st_gid=0,st_nlink=1,
        st_size=len(raw),st_mtime_ns=101,st_ctime_ns=102)for i,(path,raw)in enumerate(sorted(data.items()))}
    stats[CANDIDATE].st_size=size
    observed=[SimpleNamespace(__file__=CANDIDATE)];mapped=['/usr/bin/python3.12'];caches=set()
    class ModelPath:
        def __init__(self,*parts):self.value=PurePosixPath(*(str(part)for part in parts))
        def __str__(self):return str(self.value)
        def __truediv__(self,part):return ModelPath(self.value/part)
        @property
        def name(self):return self.value.name
        def exists(self):return str(self)in caches
        def mkdir(self,**kwargs):return None
        def read_text(self):
            assert str(self)=='/proc/self/maps'
            return '\n'.join('00-01 r-xp 0 0 0 '+path for path in mapped)
    class Modules(dict):
        def values(self):return observed
    monkeypatch.setattr(sys,'modules',Modules(sys.modules));monkeypatch.setattr(m,'Path',ModelPath)
    import time
    monkeypatch.setattr(time,'monotonic',lambda:now[0])
    def protected_path(path,*args):return stats[str(path)]
    def protected_read(path,pin=None,maximum=None):
        path=str(path);reads.append(path);raw=storage[path]if path in storage else data[path]
        if pin is not None and m.sha(raw)!=pin:raise ValueError('PURE TEST_ONLY changed protected original')
        return raw
    def write(path,raw):
        path=str(path)
        if path in storage:raise FileExistsError(path)
        storage[path]=raw
    monkeypatch.setattr(m,'write_fixed',write)
    g=SimpleNamespace(protected_path=protected_path,protected_read=protected_read)
    control=SimpleNamespace(elf_dependencies=lambda raw:None,validate_closure=lambda rows:{'files':len(rows)},validate_ci_closure=lambda rows:{'files':len(rows)},
        ci_principal_facts=lambda *args:{'PURE_TEST_ONLY_principal':39},
        CiPrincipalRejected=type('PrincipalRejected',(ValueError,),{}),CiPrerequisiteUnavailable=type('Unavailable',(ValueError,),{}))
    caller=SimpleNamespace(verify=lambda:None,close=lambda:closed.append(True))
    base={name:b'PURE_TEST_ONLY original'for name in ('suite/start.json','suite/sources.json',*('source/'+name for name in m.MEMBERS))}
    for name in ('context','caller'):
        raw=m.canonical({'PURE_TEST_ONLY':name})+b'\n';base['suite/'+name+'.json']=raw;storage[m.STORE+'/ci-evidence/'+name+'.json']=raw
    def send(files,outcome,budget):
        replay=m.receive_export(b''.join(m.export_frames(files,outcome)))
        sent.append(replay)
    tree=ast.parse(source);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='suite_main')
    stage=next(n for n in main.body if isinstance(n,ast.Try)and any(isinstance(c,ast.Call)and isinstance(c.func,ast.Name)and c.func.id=='installed_module'for c in ast.walk(n)))
    tail=next(i for i,n in enumerate(main.body)if isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='outcome')
    initial=[n for n in main.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ('directory','outcome')for t in n.targets)]
    body=[*initial,stage,*main.body[tail:]]
    function=ast.FunctionDef(name='run_model',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=body,decorator_list=[])
    scope={**vars(m),'g':g,'control':control,'caller':caller,'budget':m.SuiteBudget(100.,1000.),'base':base,'outcome':None,'directory':None,
        'time':time,'manifest':{},'installed_module':lambda *args:None,'admit_ci_root':lambda *args:{'PURE_TEST_ONLY_kernel':True},
        'send_export':send}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),'PURE_TEST_ONLY_actual_coordinator_model','exec'),scope)
    return SimpleNamespace(m=m,g=g,control=control,budget=scope['budget'],scope=scope,run=scope['run_model'],data=data,stats=stats,
        storage=storage,reads=reads,sent=sent,closed=closed,caller=caller,now=now,modules=observed,mapped=mapped,caches=caches)


@pytest.mark.parametrize('size',[0,256*1024**2+1])
def test_real_discovery_stat_bound_retains_candidate_without_reading_it(monkeypatch,size):
    f=model(monkeypatch,size)
    with pytest.raises(ValueError)as failure:f.m.discover_closure(f.g,f.control,f.budget)
    assert hasattr(failure.value,'facts'),'Bound refusal lost the already observed candidate/stat facts'
    facts=failure.value.facts
    assert facts['source']==CANDIDATE and facts['target']==CANDIDATE
    assert facts['roles']==['loaded-module'] and facts['stat']['size']==size
    assert facts['bounds']=={'minimum_exclusive':0,'maximum_inclusive':256*1024**2}
    assert CANDIDATE not in f.reads


@pytest.mark.parametrize('size',[0,256*1024**2+1])
def test_real_coordinator_keeps_bound_refusal_and_original_prerequisites_in_fail_export(monkeypatch,size):
    f=model(monkeypatch,size)
    escaped=None
    try:exit_code=f.run()
    except ValueError as error:escaped=error
    assert escaped is None,f'Observed stat refusal escaped before failed export: {escaped}'
    assert exit_code==1 and len(f.sent)==1 and f.closed==[True]
    replay=f.sent[0];assert replay['outcome']['status']=='FAIL'and replay['outcome']['control_passed']is False
    assert replay['outcome']['executed']is False and replay['outcome']['production_capture_accepted']is False
    installation=replay['files']['suite/installation.json']
    record=f.m.json.loads(installation)
    assert record['status']=='REFUSED'and record['facts']['stat']['size']==size
    assert record['started']==100. and record['deadline']==1000. and record['observed_monotonic']==150.
    assert {'suite/context.json','suite/caller.json','suite/principal.json','suite/kernel.json','suite/sources.json'}<=set(replay['files'])
    assert all('source/'+name in replay['files']for name in f.m.MEMBERS)
    assert installation==f.storage[f.m.STORE+'/ci-evidence/installation.json']
    assert CANDIDATE not in f.reads and not any(path.endswith('host.json')for path in f.storage)


def test_positive_size_neighbor_keeps_existing_discovery_route(monkeypatch):
    f=model(monkeypatch,1);rows,facts=f.m.discover_closure(f.g,f.control,f.budget)
    assert next(row for row in rows if row['source']==CANDIDATE)['bytes']==1
    assert CANDIDATE in f.reads and facts['files']==len(f.data)


@pytest.mark.parametrize('role',['fixed-source','bytecode-cache','native-mapping'])
def test_candidate_roles_target_and_exact_stat_facts_are_preserved(monkeypatch,role):
    f=model(monkeypatch,1);path=CANDIDATE
    if role=='fixed-source':
        path=f.m.STORE+'/source/linux_network.py';f.stats[path].st_size=0
        f.modules.append(SimpleNamespace(__file__=path))
    elif role=='bytecode-cache':
        path='/usr/lib/python3.12/__pycache__/TEST_ONLY-member.pyc';f.modules[0].__cached__=path;f.caches.add(path)
        f.data[path]=b'';f.stats[path]=copy.copy(f.stats[CANDIDATE]);f.stats[path].st_size=0;f.stats[path].st_ino=999
    else:f.stats[path].st_size=0;f.mapped.append(path)
    with pytest.raises(f.m.ClosureStatRefused)as failure:f.m.discover_closure(f.g,f.control,f.budget)
    facts=failure.value.facts;info=f.stats[path]
    assert facts['source']==path and role in facts['roles']
    assert facts['target']==('/app/linux_network.py'if role=='fixed-source'else path)
    assert facts['stat']=={'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,'uid':info.st_uid,'gid':info.st_gid,
        'links':info.st_nlink,'size':info.st_size,'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}
    assert facts['observed_monotonic']==150. and facts['protected_path_completed']is True
    assert path not in f.reads


def test_exact_upper_size_bound_is_not_reclassified_as_stat_refusal(monkeypatch):
    f=model(monkeypatch,256*1024**2);read=f.g.protected_read
    def refuse_read(path,*args,**kwargs):
        if path==CANDIDATE:raise OSError('PURE TEST_ONLY next-stage read failure')
        return read(path,*args,**kwargs)
    f.g.protected_read=refuse_read
    with pytest.raises(OSError,match='next-stage'):f.m.discover_closure(f.g,f.control,f.budget)


@pytest.mark.parametrize('fault',['stat-error','stat-close-error','missing-field','bool-field','read-error','caller-changed','caller-close-error','persistence-error','persistence-tamper','export-tamper','deadline-after-stat','deadline-after-persist','deadline-after-close'])
def test_unknown_or_late_paths_never_become_complete_refusal_exports(monkeypatch,fault):
    f=model(monkeypatch,1 if fault=='read-error'else 0);protected=f.g.protected_path;read=f.g.protected_read;write=f.m.write_fixed
    def path(path,*args):
        if path==CANDIDATE:
            if fault in ('stat-error','stat-close-error'):raise OSError('PURE TEST_ONLY '+fault)
            if fault=='deadline-after-stat':f.now[0]=990.
        return protected(path,*args)
    f.g.protected_path=path
    if fault=='missing-field':del f.stats[CANDIDATE].st_mtime_ns
    if fault=='bool-field':f.stats[CANDIDATE].st_uid=True
    if fault=='read-error':
        def failed_read(path,*args,**kwargs):
            if path==CANDIDATE:raise OSError('PURE TEST_ONLY failed protected read')
            return read(path,*args,**kwargs)
        f.g.protected_read=failed_read
    if fault=='caller-changed':f.caller.verify=lambda:(_ for _ in ()).throw(OSError('PURE TEST_ONLY caller changed'))
    if fault=='caller-close-error':f.caller.close=lambda:(_ for _ in ()).throw(OSError('PURE TEST_ONLY ambiguous caller close'))
    def changed_write(path,raw):
        if str(path).endswith('/installation.json'):
            if fault=='persistence-error':raise OSError('PURE TEST_ONLY failed exclusive persistence')
            write(path,raw)
            if fault=='persistence-tamper':f.storage[str(path)]=b'PURE TEST_ONLY altered installation'
            if fault=='deadline-after-persist':f.now[0]=1000.
        else:write(path,raw)
    monkeypatch.setattr(f.m,'write_fixed',changed_write)
    if fault in ('export-tamper','deadline-after-close'):
        def close():
            if fault=='export-tamper':f.storage[f.m.STORE+'/ci-evidence/installation.json']=b'PURE TEST_ONLY altered original'
            else:f.now[0]=1000.
        f.caller.close=close
    with pytest.raises((OSError,ValueError,AttributeError)):f.run()
    assert f.sent==[], 'Unknown/late state must not be relabeled a complete FAIL export'
    assert 'suite/principal.json'in f.scope['base']and 'suite/kernel.json'in f.scope['base']


@pytest.mark.parametrize('now',[True,float('nan'),float('inf'),float('-inf')])
def test_unknown_original_clock_cannot_create_stat_diagnostic_or_export(monkeypatch,now):
    f=model(monkeypatch,0);f.now[0]=now
    with pytest.raises(ValueError):f.run()
    assert not f.sent and f.m.STORE+'/ci-evidence/installation.json'not in f.storage


def test_original_bounds_are_not_relaxed_or_empty_file_admitted(monkeypatch):
    f=model(monkeypatch,0)
    with pytest.raises(f.m.ClosureStatRefused):f.m.discover_closure(f.g,f.control,f.budget)
    assert CANDIDATE not in f.reads
    f.stats[CANDIDATE].st_size=1
    rows,_=f.m.discover_closure(f.g,f.control,f.budget)
    assert next(row for row in rows if row['source']==CANDIDATE)['bytes']==1


def test_delayed_handoff_preserves_original_stat_clock_separately_from_persistence(monkeypatch):
    f=model(monkeypatch,0);f.caller.verify=lambda:f.now.__setitem__(0,160.)
    assert f.run()==1
    record=f.m.json.loads(f.sent[0]['files']['suite/installation.json'])
    assert record['facts']['observed_monotonic']==150. and record['observed_monotonic']==160.
    assert record['started']==100. and record['deadline']==1000.


def test_caller_change_after_persistence_keeps_original_bytes_but_refuses_export(monkeypatch):
    f=model(monkeypatch,0);checks=[]
    def verify():
        checks.append(True)
        if len(checks)==2:raise OSError('PURE TEST_ONLY caller changed after persistence')
    f.caller.verify=verify
    with pytest.raises(OSError,match='after persistence'):f.run()
    assert f.m.STORE+'/ci-evidence/installation.json'in f.storage and not f.sent
