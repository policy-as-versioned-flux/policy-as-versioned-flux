"""Pure actual-source ELF NEEDED diagnostic models; no target/native queries."""
import copy
import struct
from types import SimpleNamespace
import pytest
from test_linux_lease_control_ci_empty_urllib import fixture, URLLIB

NEEDED='PURE_TEST_ONLY-library.so'
OWNER='/usr/bin/python3.12'


def elf_with_needed(name):
    raw=bytearray(1024);raw[:16]=b'\x7fELF\x02\x01\x01'+b'\0'*9
    struct.pack_into('<HHIQQQIHHHHHH',raw,16,3,62,1,0,64,0,0,64,56,2,0,0,0)
    struct.pack_into('<IIQQQQQQ',raw,64,1,4,0,0x400000,0,1024,1024,4096)
    struct.pack_into('<IIQQQQQQ',raw,120,2,4,400,0,0,64,64,8)
    text=name.encode()+b'\0';struct.pack_into('<qQqQqQqQ',raw,400,1,0,5,0x400200,10,len(text),0,0);raw[512:512+len(text)]=text
    return bytes(raw)


def needed_model(monkeypatch,count=0):
    f=fixture(monkeypatch);f.data[OWNER]=elf_with_needed(NEEDED);f.stats[OWNER].st_size=len(f.data[OWNER])
    paths=[]if count==0 else(['/usr/lib/'+NEEDED]if count==1 else['/usr/lib/a/'+NEEDED,'/usr/lib/b/'+NEEDED])
    if count==0:paths=['/usr/lib/PURE_TEST_ONLY-related-canonical-name.so.9']
    for i,path in enumerate(paths):
        f.data[path]=b'PURE_TEST_ONLY library';f.stats[path]=copy.copy(f.stats[OWNER]);f.stats[path].st_ino=2000+i;f.stats[path].st_size=len(f.data[path]);f.mapped.append(path)
    f.path_calls=[];f.maps_reads=[];original=f.g.protected_path
    def metadata(path,*args):f.path_calls.append(path);return original(path,*args)
    f.g.protected_path=metadata
    path_type=f.m.Path
    class ModelPath(path_type):
        def read_text(self):f.maps_reads.append(str(self));return super().read_text()
    monkeypatch.setattr(f.m,'Path',ModelPath)
    monkeypatch.setattr(f.control,'ci_principal_facts',lambda *args:{'PURE_TEST_ONLY_principal':39})
    f.scope['control']=f.control;f.expected_matches=[]if count==0 else paths
    return f


@pytest.mark.parametrize('count',[0,2])
def test_real_discovery_retains_owner_needed_maps_and_matches_without_extra_query(monkeypatch,count):
    f=needed_model(monkeypatch,count)
    with pytest.raises(ValueError)as failure:f.m.discover_closure(f.g,f.control,f.budget)
    assert hasattr(failure.value,'facts'),'NEEDED refusal lost already-acquired dependency/mapping facts'
    facts=failure.value.facts
    assert facts['owner']['source']==OWNER and facts['owner']['target']==OWNER
    assert facts['owner']['elf']['needed']==[NEEDED]and facts['needed']==NEEDED
    assert facts['matches']==sorted(f.expected_matches)and facts['match_count']==count
    assert facts['mapped_paths']==sorted(f.mapped)
    assert f.maps_reads==['/proc/self/maps']
    assert f.path_calls==sorted(path for path in f.data if path!='/usr/lib/python3.12/TEST_ONLY-member.py')


@pytest.mark.parametrize('count',[0,2])
def test_real_coordinator_exports_narrow_elf_needed_refusal_with_original_prerequisites(monkeypatch,count):
    f=needed_model(monkeypatch,count);escaped=None
    try:exit_code=f.run()
    except ValueError as error:escaped=error
    assert escaped is None,f'ELF NEEDED refusal escaped before failure export: {escaped}'
    assert exit_code==1 and f.closed==[True]and len(f.sent)==1
    replay=f.sent[0];record=f.m.json.loads(replay['files']['suite/installation.json'])
    assert replay['outcome']['status']=='FAIL'and replay['outcome']['executed']is False
    assert replay['outcome']['control_passed']is False and replay['outcome']['production_capture_accepted']is False
    assert record['status']=='REFUSED'and record['facts']['needed']==NEEDED and record['facts']['match_count']==count
    assert {'suite/caller.json','suite/context.json','suite/principal.json','suite/kernel.json','suite/sources.json'}<=set(replay['files'])
    assert all('source/'+name in replay['files']for name in f.m.MEMBERS)


def test_exactly_one_existing_mapped_basename_keeps_existing_acceptance(monkeypatch):
    f=needed_model(monkeypatch,1);rows,facts=f.m.discover_closure(f.g,f.control,f.budget)
    assert facts['files']==len(rows)and next(row for row in rows if row['source']==OWNER)['elf']['needed']==[NEEDED]
    assert next(row for row in rows if row['source']==URLLIB)['bytes']==0


@pytest.mark.parametrize('count',[0,2])
def test_retained_mapping_metadata_and_original_clock_match_only_already_acquired_facts(monkeypatch,count):
    f=needed_model(monkeypatch,count)
    with pytest.raises(f.m.ClosureNeededRefused)as failure:f.m.discover_closure(f.g,f.control,f.budget)
    facts=failure.value.facts
    assert facts['native_maps_sha256']==f.m.sha('\n'.join('00-01 r-xp 0 0 0 '+path for path in f.mapped).encode())
    assert facts['owner']['sha256']==f.m.sha(f.data[OWNER])and facts['owner']['bytes']==len(f.data[OWNER])
    assert facts['owner_metadata']=={'device':8,'inode':f.stats[OWNER].st_ino,'stat_bytes':len(f.data[OWNER]),'roles':['interpreter','native-mapping']}
    assert facts['original_started']==100. and facts['original_deadline']==1000. and facts['observed_monotonic']==150.
    assert facts['bounds']=={'required_matches':1,'closure_files':4096,'closure_bytes':256*1024**2,'diagnostic_bytes':f.m.MAX_FILE-65536}
    assert [row['member']['source']for row in facts['mapped_records']]==sorted(f.mapped)
    for row in facts['mapped_records']:
        path=row['member']['source'];assert row['member']['sha256']==f.m.sha(f.data[path])
        assert row['metadata']['inode']==f.stats[path].st_ino and row['metadata']['stat_bytes']==len(f.data[path])
    f.mapped.append('/usr/lib/PURE_TEST_ONLY-later-map');f.stats[OWNER].st_ino=99999
    assert '/usr/lib/PURE_TEST_ONLY-later-map'not in facts['mapped_paths']and facts['owner_metadata']['inode']!=99999


@pytest.mark.parametrize('fault',['stat-error','stat-close-error','read-error','source-integrity','bad-ELF','unknown-metadata','caller-changed','caller-close-error','persistence-error','persistence-tamper','export-tamper','metadata-bound','deadline-before-facts','deadline-after-facts','deadline-after-persist'])
def test_unknown_paths_do_not_become_complete_elf_needed_refusal_exports(monkeypatch,fault):
    f=needed_model(monkeypatch,0);path=f.g.protected_path;read=f.g.protected_read;write=f.m.write_fixed;canonical=f.m.canonical
    def metadata(name,*args):
        if name==OWNER and fault in ('stat-error','stat-close-error'):raise OSError('PURE_TEST_ONLY '+fault)
        return path(name,*args)
    f.g.protected_path=metadata
    def acquire(name,*args,**kwargs):
        if name==OWNER and fault=='read-error':raise OSError('PURE_TEST_ONLY read-error')
        if name==max(path for path in f.data if path!='/usr/lib/python3.12/TEST_ONLY-member.py')and fault=='deadline-before-facts':f.now[0]=990.
        return read(name,*args,**kwargs)
    f.g.protected_read=acquire
    if fault=='source-integrity':f.scope['installed_module']=lambda *args:(_ for _ in ()).throw(ValueError('PURE_TEST_ONLY source pin changed'))
    if fault=='bad-ELF':f.data[OWNER]=b'\x7fELF'
    if fault=='unknown-metadata':f.stats[OWNER].st_dev=True
    if fault=='caller-changed':f.caller.verify=lambda:(_ for _ in ()).throw(OSError('PURE_TEST_ONLY caller changed'))
    if fault=='caller-close-error':f.caller.close=lambda:(_ for _ in ()).throw(OSError('PURE_TEST_ONLY unknown close'))
    if fault=='metadata-bound':monkeypatch.setattr(f.m,'MAX_FILE',65536)
    if fault=='deadline-after-facts':
        def encode(value):
            raw=canonical(value)
            if isinstance(value,dict)and value.get('stage')=='discover-closure-ELF-needed-match':f.now[0]=990.
            return raw
        monkeypatch.setattr(f.m,'canonical',encode)
    def persist(name,raw):
        if str(name).endswith('/installation.json'):
            if fault=='persistence-error':raise OSError('PURE_TEST_ONLY persistence failed')
            write(name,raw)
            if fault=='persistence-tamper':f.storage[str(name)]=b'PURE_TEST_ONLY tampered original'
            if fault=='deadline-after-persist':f.now[0]=1000.
        else:write(name,raw)
    monkeypatch.setattr(f.m,'write_fixed',persist)
    if fault=='export-tamper':f.caller.close=lambda:f.storage.__setitem__(f.m.STORE+'/ci-evidence/installation.json',b'PURE_TEST_ONLY tampered before export')
    with pytest.raises((OSError,ValueError)):f.run()
    assert not f.sent


@pytest.mark.parametrize('clock',[True,float('nan'),float('inf'),float('-inf')])
def test_unknown_clock_never_mints_needed_refusal_facts(monkeypatch,clock):
    f=needed_model(monkeypatch,0);f.now[0]=clock
    with pytest.raises(ValueError):f.run()
    assert not f.sent and f.m.STORE+'/ci-evidence/installation.json'not in f.storage


def test_delayed_handoff_preserves_original_needed_observation_time(monkeypatch):
    f=needed_model(monkeypatch,0);f.caller.verify=lambda:f.now.__setitem__(0,160.)
    assert f.run()==1
    record=f.m.json.loads(f.sent[0]['files']['suite/installation.json'])
    assert record['facts']['observed_monotonic']==150. and record['observed_monotonic']==160.
    assert record['started']==100. and record['deadline']==1000.


def test_missing_ELF_interpreter_is_not_misclassified_as_needed_refusal(monkeypatch):
    f=needed_model(monkeypatch,0);parse=f.control.elf_dependencies
    monkeypatch.setattr(f.control,'elf_dependencies',lambda raw:{'interpreter':'/lib/PURE_TEST_ONLY-unmapped-loader','needed':[]}if raw==f.data[OWNER]else parse(raw))
    import os
    monkeypatch.setattr(os.path,'realpath',lambda path:path)
    with pytest.raises(ValueError,match='actual ELF interpreter')as failure:f.m.discover_closure(f.g,f.control,f.budget)
    assert type(failure.value)is ValueError and not hasattr(failure.value,'facts')
