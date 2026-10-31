"""Exact CI urllib-empty source models; no actual OS/NSS/proc/native operations."""
import copy
import hashlib
import json
from pathlib import PurePosixPath
from types import SimpleNamespace
import struct
import pytest
from test_linux_lease_control import control
from test_linux_lease_control_ci_closure_refusal import model, CANDIDATE

URLLIB='/usr/lib/python3.12/urllib/__init__.py'
EMPTY=hashlib.sha256(b'').hexdigest()


def empty_row():
    return {'source':URLLIB,'target':URLLIB,'bytes':0,'sha256':EMPTY,'elf':None}


def fixture(monkeypatch):
    f=model(monkeypatch,1);c=control()
    raw=bytearray(64);raw[:16]=b'\x7fELF\x02\x01\x01'+b'\0'*9
    struct.pack_into('<HHIQQQIHHHHHH',raw,16,3,62,1,0,64,0,0,64,56,0,0,0,0)
    f.data['/usr/bin/python3.12']=bytes(raw);f.stats['/usr/bin/python3.12'].st_size=len(raw)
    f.data[URLLIB]=b'';f.stats[URLLIB]=copy.copy(f.stats[CANDIDATE]);f.stats[URLLIB].st_size=0;f.stats[URLLIB].st_ino=999
    f.modules[0].__file__=URLLIB
    rows=[{'source':path,'target':'/app/'+PurePosixPath(path).name if path.startswith(f.m.STORE+'/source/')else path,
        'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'elf':c.elf_dependencies(data)}for path,data in f.data.items()if path!=CANDIDATE]
    f.control=c;f.rows=rows
    return f


def host_model(monkeypatch,f):
    c=f.control;source=c.STORE+'/source/linux_lease_control.py';read=f.g.protected_read;path=f.g.protected_path
    anchor=json.dumps({'schema':c.SCHEMA,'files':f.rows}).encode()
    class ModelPath:
        def __init__(self,*parts):self.value=PurePosixPath(*(str(p)for p in parts))
        def __str__(self):return str(self.value)
        @property
        def parts(self):return self.value.parts
        @property
        def name(self):return self.value.name
        def read_text(self):
            assert str(self)in ('/sys/fs/cgroup/cpuset.cpus.effective','/sys/fs/cgroup/cgroup.subtree_control')
            return '2-3'if str(self).endswith('cpuset.cpus.effective')else'memory cpu cpuset pids'
    monkeypatch.setattr(c,'Path',ModelPath);monkeypatch.setattr(c,'__file__',source);monkeypatch.setattr(c.sys,'executable','/usr/bin/python3.12')
    monkeypatch.setattr(c.os,'sched_getaffinity',lambda pid:{2,3},raising=False);monkeypatch.setattr(c.platform,'release',lambda:'PURE_TEST_ONLY_kernel')
    monkeypatch.setattr(c.platform,'machine',lambda:'PURE_TEST_ONLY_machine')
    monkeypatch.setattr(c,'ci_principal_facts',lambda *args:{'name':'irc','uid':39,'gid':39,'caller_uid':1001,'caller_gid':1001,
        'uid_names':['irc'],'gid_names':['irc'],'primary_names':['irc'],'supplementary_names':[],'home_exposed':False,'active':False})
    f.g.protected_read=lambda name,*args,**kwargs:anchor if name==c.ANCHOR else read(name,*args,**kwargs)
    f.g.protected_path=lambda name,*args:SimpleNamespace(st_dev=8,st_ino=9999)if name=='/sys/fs/cgroup'else path(name,*args)
    f.g.parse_set=lambda raw:{2,3};f.g.storage_paths=lambda *args:('/var/lib',)
    f.g.reserve=lambda *args:{'memory_available':20*1024**3,'disk_free':10*1024**3}
    f.g.observe_ancestors=lambda parent:[];f.g.effective_memory=lambda *args:20*1024**3;f.g.validate_reserve=lambda *args:None
    f.g.verify_guardian_closure=lambda host,verify:verify();f.g.digest=lambda raw:hashlib.sha256(raw).hexdigest()
    f.g.MEMORY=12*1024**3;f.g.RESERVE=2*1024**3;f.g.DISK=5*1024**3
    f.caller.pid=201;f.caller.start='77';f.caller.uid=[1001]*4
    return c


def test_real_discovery_reads_and_retains_the_exact_empty_loaded_urllib(monkeypatch):
    f=fixture(monkeypatch)
    rows,facts=f.m.discover_closure(f.g,f.control,f.budget)
    assert next(row for row in rows if row['source']==URLLIB)==empty_row()
    assert URLLIB in f.reads and facts['files']==len(rows)and URLLIB in facts['loaded_sources']
    assert facts['bytes']==sum(row['bytes']for row in rows)


def test_separate_ci_validator_accepts_exact_zero_without_omission_or_fake_positive_size(monkeypatch):
    f=fixture(monkeypatch)
    validator=getattr(f.control,'validate_ci_closure',f.control.validate_closure)
    facts=validator(f.rows)
    assert facts=={'files':len(f.rows),'bytes':sum(row['bytes']for row in f.rows)}
    with pytest.raises(ValueError):f.control.validate_closure(f.rows)


def test_real_later_ci_host_load_retains_the_empty_row_and_rechecks_actual_bytes(monkeypatch):
    f=fixture(monkeypatch);c=host_model(monkeypatch,f)
    host,profile,facts=c.load_ci_control_host(f.g,'baseline',f.caller)
    observed=next(row for row in facts['closure']if row['source']==URLLIB)
    assert {k:observed[k]for k in empty_row()}==empty_row()
    assert observed['device']==8 and observed['inode']==999 and host['candidate_uid']==39
    assert {'source':URLLIB,'target':URLLIB,'sha256':EMPTY}in profile['readonly_mounts']
    assert facts['principal']['name']=='irc'and URLLIB in f.reads


def test_ordinary_positive_neighbor_stays_valid_and_ordinary_zero_stays_refused(monkeypatch):
    f=fixture(monkeypatch);without=[row for row in f.rows if row['source']!=URLLIB]
    assert f.control.validate_closure(without)['files']==len(without)
    with pytest.raises(ValueError):f.control.validate_closure(f.rows)


@pytest.mark.parametrize('mutation',['source','target','negative','bool','float','hash','ELF','extra-key','missing-key','other-zero','duplicate-source','duplicate-target','too-many','too-large','missing-python','python-not-ELF','missing-loader','missing-needed','ambiguous-needed','empty-as-loader','empty-as-needed'])
def test_ci_exception_retains_closed_unique_count_size_hash_and_ELF_guards(monkeypatch,mutation):
    f=fixture(monkeypatch);rows=copy.deepcopy(f.rows);row=next(row for row in rows if row['source']==URLLIB);python=next(row for row in rows if row['target']=='/usr/bin/python3.12')
    if mutation=='source':row['source']='/usr/lib/python3.12/urllib/other.py'
    if mutation=='target':row['target']='/app/__init__.py'
    if mutation=='negative':row['bytes']=-1
    if mutation=='bool':row['bytes']=False
    if mutation=='float':row['bytes']=0.0
    if mutation=='hash':row['sha256']='0'*64
    if mutation=='ELF':row['elf']={'interpreter':None,'needed':[]}
    if mutation=='extra-key':row['approved']=True
    if mutation=='missing-key':row.pop('elf')
    if mutation=='other-zero':rows[0]['bytes']=0
    if mutation=='duplicate-source':rows.append(dict(row,target='/lib/alias.py'))
    if mutation=='duplicate-target':rows.append(dict(row,source='/lib/alias.py'))
    if mutation=='too-many':rows=rows*(f.control.MAX_FILES//len(rows)+1)
    if mutation=='too-large':python['bytes']=f.control.MAX_BYTES+1
    if mutation=='missing-python':rows.remove(python)
    if mutation=='python-not-ELF':python['elf']=None
    if mutation=='missing-loader':python['elf']['interpreter']='/lib/absent-loader'
    if mutation=='missing-needed':python['elf']['needed']=['absent.so']
    if mutation=='ambiguous-needed':
        python['elf']['needed']=['two.so'];rows.extend([{'source':path,'target':path,'bytes':1,'sha256':'1'*64,'elf':None}for path in ['/usr/lib/a/two.so','/usr/lib/b/two.so']])
    if mutation=='empty-as-loader':python['elf']['interpreter']=URLLIB
    if mutation=='empty-as-needed':python['elf']['needed']=['__init__.py']
    with pytest.raises(ValueError):f.control.validate_ci_closure(rows)


@pytest.mark.parametrize('role',['also-mapped','also-cache','cache-only','other-empty-module'])
def test_discovery_does_not_broaden_empty_urllib_to_other_roles_or_paths(monkeypatch,role):
    f=fixture(monkeypatch);path=URLLIB
    if role=='also-mapped':f.mapped.append(URLLIB)
    if role in ('also-cache','cache-only'):
        if role=='cache-only':f.modules[0]=SimpleNamespace()
        f.modules[0].__cached__=URLLIB;f.caches.add(URLLIB)
    if role=='other-empty-module':
        path='/usr/lib/python3.12/other/__init__.py';f.modules[0].__file__=path
        f.data[path]=b'';f.stats[path]=copy.copy(f.stats[URLLIB]);f.stats[path].st_ino=1000
    with pytest.raises(f.m.ClosureStatRefused)as failure:f.m.discover_closure(f.g,f.control,f.budget)
    assert failure.value.facts['source']==path and path not in f.reads


@pytest.mark.parametrize('fault',['stat-error','stat-close-error','read-error','read-nonempty','read-nonbytes','stat-positive-empty-read','inode-alias','deadline-after-read','bool-stat','float-stat','negative-stat'])
def test_discovery_matches_actual_zero_stat_empty_bytes_and_original_clock(monkeypatch,fault):
    f=fixture(monkeypatch);path=f.g.protected_path;read=f.g.protected_read
    def metadata(name,*args):
        if name==URLLIB and fault in ('stat-error','stat-close-error'):raise OSError('PURE_TEST_ONLY '+fault)
        return path(name,*args)
    f.g.protected_path=metadata
    def acquire(name,*args,**kwargs):
        if name==URLLIB:
            if fault=='read-error':raise OSError('PURE_TEST_ONLY read-error')
            if fault=='read-nonempty':return b'x'
            if fault=='read-nonbytes':return bytearray()
            if fault=='deadline-after-read':f.now[0]=1000.
        return read(name,*args,**kwargs)
    f.g.protected_read=acquire
    if fault=='stat-positive-empty-read':f.stats[URLLIB].st_size=1
    if fault=='inode-alias':f.stats[URLLIB].st_ino=f.stats['/usr/bin/python3.12'].st_ino
    if fault=='bool-stat':f.stats[URLLIB].st_size=False
    if fault=='float-stat':f.stats[URLLIB].st_size=0.0
    if fault=='negative-stat':f.stats[URLLIB].st_size=-1
    with pytest.raises((ValueError,OSError)):f.m.discover_closure(f.g,f.control,f.budget)


@pytest.mark.parametrize('fault',['changed-read','stat-positive','stat-bool','stat-error','caller-changed','source-pin-tamper'])
def test_later_ci_host_load_rechecks_zero_stat_bytes_hash_caller_and_source(monkeypatch,fault):
    f=fixture(monkeypatch);c=host_model(monkeypatch,f);read=f.g.protected_read;path=f.g.protected_path
    def acquire(name,*args,**kwargs):
        if name==URLLIB and fault=='changed-read':return b'x'
        return read(name,*args,**kwargs)
    f.g.protected_read=acquire
    if fault=='source-pin-tamper':
        source=c.STORE+'/source/linux_network.py';f.data[source]=b'x'*len(f.data[source])
    if fault=='stat-positive':f.stats[URLLIB].st_size=1
    if fault=='stat-bool':f.stats[URLLIB].st_size=False
    if fault=='stat-error':
        def metadata(name,*args):
            if name==URLLIB:raise OSError('PURE_TEST_ONLY stat-error')
            return path(name,*args)
        f.g.protected_path=metadata
    if fault=='caller-changed':f.caller.verify=lambda:(_ for _ in ()).throw(OSError('PURE_TEST_ONLY caller changed'))
    with pytest.raises((ValueError,OSError)):c.load_ci_control_host(f.g,'baseline',f.caller)


def test_zero_module_counts_at_exact_file_and_byte_caps_without_positive_byte_substitution(monkeypatch):
    f=fixture(monkeypatch);rows=copy.deepcopy(f.rows)
    while len(rows)<f.control.MAX_FILES:
        i=len(rows);rows.append({'source':f'/usr/lib/PURE_TEST_ONLY-{i}.py','target':f'/usr/lib/PURE_TEST_ONLY-{i}.py','bytes':1,'sha256':'1'*64,'elf':None})
    python=next(row for row in rows if row['target']=='/usr/bin/python3.12');python['bytes']+=f.control.MAX_BYTES-sum(row['bytes']for row in rows)
    assert f.control.validate_ci_closure(rows)=={'files':f.control.MAX_FILES,'bytes':f.control.MAX_BYTES}
    assert next(row for row in rows if row['source']==URLLIB)['bytes']==0
    with pytest.raises(ValueError):f.control.validate_closure(rows)


def test_ordinary_later_host_route_rejects_the_retained_zero_row_before_any_NSS_query(monkeypatch):
    f=fixture(monkeypatch);c=host_model(monkeypatch,f)
    monkeypatch.setattr(c,'principal_facts',lambda *args:(_ for _ in ()).throw(AssertionError('ordinary principal path must not run')))
    with pytest.raises(ValueError):c.load_control_host(f.g,'baseline',f.caller)


def test_nonempty_urllib_positive_neighbor_keeps_ordinary_and_ci_behavior(monkeypatch):
    f=fixture(monkeypatch);f.data[URLLIB]=b'x';f.stats[URLLIB].st_size=1
    rows,facts=f.m.discover_closure(f.g,f.control,f.budget)
    row=next(row for row in rows if row['source']==URLLIB)
    assert row['bytes']==1 and row['sha256']==hashlib.sha256(b'x').hexdigest()
    assert f.control.validate_closure(rows)==f.control.validate_ci_closure(rows)
