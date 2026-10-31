"""Pure source-route controls: synthetic ELF, modeled OS/clock; no native actions."""
import copy
import hashlib
import struct
import pytest
from test_linux_lease_control_ci_empty_urllib import fixture,host_model
from test_linux_lease_control_ci_elf_needed_refusal import elf_with_needed,OWNER

PIN='1'*64
NEEDED='libz.so.1'


def soname_elf(name=NEEDED,machine=62,extra=()):
    raw=bytearray(1024);raw[:16]=b'\x7fELF\x02\x01\x01'+b'\0'*9
    struct.pack_into('<HHIQQQIHHHHHH',raw,16,3,machine,1,0,64,0,0,64,56,2,0,0,0)
    struct.pack_into('<IIQQQQQQ',raw,64,1,4,0,0x400000,0,1024,1024,4096)
    entries=[(14,0),(5,0x400280),(10,len(name.encode())+1),*extra,(0,0)]
    struct.pack_into('<IIQQQQQQ',raw,120,2,4,400,0,0,len(entries)*16,len(entries)*16,8)
    for i,item in enumerate(entries):struct.pack_into('<qQ',raw,400+i*16,*item)
    raw[640:641+len(name.encode())]=name.encode()+b'\0'
    return bytes(raw)


def alias_model(monkeypatch,arch='x86_64',repeat=0):
    f=fixture(monkeypatch);f.data[OWNER]=elf_with_needed(NEEDED);f.stats[OWNER].st_size=len(f.data[OWNER])
    f.library=f'/usr/lib/{arch}-linux-gnu/libz.so.1.3';f.target=f'/usr/lib/{arch}-linux-gnu/libz.so.1'
    f.data[f.library]=soname_elf(machine=183 if arch=='aarch64' else 62)
    f.stats[f.library]=copy.copy(f.stats[OWNER]);f.stats[f.library].st_ino=2400+repeat;f.stats[f.library].st_size=len(f.data[f.library]);f.mapped.append(f.library)
    monkeypatch.setattr(f.control,'ci_principal_facts',lambda *args:{'PURE_TEST_ONLY_principal':39})
    f.scope['control']=f.control
    return f


@pytest.mark.parametrize('arch,repeat',[('x86_64',0),('aarch64',0),('x86_64',1),('aarch64',1)])
def test_discovery_identity_projects_canonical_source_through_actual_later_CI_host_load(monkeypatch,arch,repeat):
    f=alias_model(monkeypatch,arch,repeat)
    rows,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256='1'*64)
    row=next(r for r in rows if r['source']==f.library)
    assert row['target']==f.target and row['sha256']==hashlib.sha256(f.data[f.library]).hexdigest()
    assert f.control.validate_ci_closure(rows)['files']==len(rows)
    f.rows=rows;c=host_model(monkeypatch,f);host,profile,later=c.load_ci_control_host(f.g,'baseline',f.caller)
    assert {'source':f.library,'target':f.target,'sha256':row['sha256']}in profile['readonly_mounts']
    assert next(r for r in later['closure']if r['source']==f.library)['target']==f.target


def test_projection_DATA_is_closed_and_binds_original_source_maps_clock(monkeypatch):
    f=alias_model(monkeypatch);rows,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    proof=facts['elf_soname_projections'];assert proof['source_manifest_sha256']==PIN
    assert (proof['original_started'],proof['original_deadline'],proof['observed_monotonic'])==(100.,1000.,150.)
    assert proof['native_maps_sha256']==facts['native_maps_sha256']and proof['failure']is None
    assert next(r for r in proof['objects']if r['source']==f.library)['soname']==NEEDED
    assert proof['assignments']==[{'source':f.library,'target':f.target,'needed':NEEDED}]
    checker=getattr(f.m,'_check_projection_data',None)
    assert checker is not None,'closed projection DATA lacks its pure checker'
    checker(proof)
    changed=copy.deepcopy(proof);changed['public_approval']=True
    with pytest.raises(ValueError):checker(changed)


def test_new_known_projection_refusal_retains_protected_FAIL_export_and_verified_manifest(monkeypatch):
    f=alias_model(monkeypatch);f.data[f.library]=soname_elf(extra=((14,0),));f.stats[f.library].st_size=len(f.data[f.library])
    assert f.run()==1 and len(f.sent)==1 and f.closed==[True]
    replay=f.sent[0];record=f.m.json.loads(replay['files']['suite/installation.json']);proof=record['facts']
    assert record['status']=='REFUSED'and replay['outcome']['reason'].startswith('ClosureProjectionRefused:')
    assert proof['source_manifest_sha256']==f.m.sha(f.scope['source_raw'])
    assert proof['failure']['reason']=='MALFORMED_SONAME'and proof['failure']['source']==f.library
    assert {'suite/context.json','suite/caller.json','suite/principal.json','suite/kernel.json','suite/sources.json'}<=set(replay['files'])
    assert all('source/'+name in replay['files']for name in f.m.MEMBERS)
    assert replay['outcome']['status']=='FAIL'and replay['outcome']['executed']is False
    assert replay['outcome']['production_capture_accepted']is False and replay['outcome']['control_passed']is False


def replace_library(f,raw):
    f.data[f.library]=raw;f.stats[f.library].st_size=len(raw)


@pytest.mark.parametrize('name',['','.', '..','../libz.so.1','/libz.so.1','lib/z.so',r'lib\z.so','lib z.so','lib\tz.so','lib\nz.so','lib\x01z.so','libé.so','a'*256])
def test_unsafe_SONAME_is_new_parser_owned_refusal_at_real_discovery(monkeypatch,name):
    f=alias_model(monkeypatch);replace_library(f,soname_elf(name))
    with pytest.raises(f.m.ClosureProjectionRefused)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    proof=failed.value.facts;assert proof['failure']['reason']=='MALFORMED_SONAME'
    assert next(r for r in proof['objects']if r['source']==f.library)['format_error']=='LOCAL_NAME'


@pytest.mark.parametrize('fault,category',[('duplicate-soname','DYNAMIC'),('duplicate-strtab','DYNAMIC'),('duplicate-strsz','DYNAMIC'),('header-width','HEADER'),('no-table','STRING_TABLE'),('no-size','STRING_TABLE'),('offset','STRING_TABLE'),('unbacked','STRING_TABLE'),('unterminated-name','STRING_TABLE'),('ambiguous-backing','STRING_TABLE'),('dynamic-count','DYNAMIC')])
def test_bounded_new_format_refusals_do_not_replace_ordinary_parser_failures(monkeypatch,fault,category):
    f=alias_model(monkeypatch);raw=bytearray(soname_elf())
    if fault.startswith('duplicate-'):raw=bytearray(soname_elf(extra=(({'duplicate-soname':14,'duplicate-strtab':5,'duplicate-strsz':10}[fault],0),)))
    if fault=='header-width':struct.pack_into('<H',raw,52,63)
    if fault=='no-table':struct.pack_into('<q',raw,416,99)
    if fault=='no-size':struct.pack_into('<q',raw,432,99)
    if fault=='offset':struct.pack_into('<Q',raw,408,1024)
    if fault=='unbacked':struct.pack_into('<Q',raw,424,0x500000)
    if fault=='unterminated-name':raw[649]=ord('x')
    if fault=='ambiguous-backing':struct.pack_into('<H',raw,56,3);raw[176:232]=raw[64:120]
    if fault=='dynamic-count':raw.extend(b'\0'*65536);struct.pack_into('<Q',raw,120+32,65552)
    assert f.control.elf_dependencies(bytes(raw))=={'interpreter':None,'needed':[]}
    replace_library(f,bytes(raw))
    with pytest.raises(f.m.ClosureProjectionRefused)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    assert next(r for r in failed.value.facts['objects']if r['source']==f.library)['format_error']==category


@pytest.mark.parametrize('fault',['truncated','class','machine','program-count','duplicate-dynamic','partial-dynamic','no-terminator','segment-outside'])
def test_existing_ordinary_ELF_errors_keep_exact_type_message_and_no_complete_export(monkeypatch,fault):
    f=alias_model(monkeypatch);raw=bytearray(soname_elf())
    if fault=='truncated':raw=raw[:63]
    if fault=='class':raw[4]=1
    if fault=='machine':struct.pack_into('<H',raw,18,0)
    if fault=='program-count':struct.pack_into('<H',raw,56,4097)
    if fault=='duplicate-dynamic':struct.pack_into('<I',raw,64,2)
    if fault=='partial-dynamic':struct.pack_into('<Q',raw,120+32,63)
    if fault=='no-terminator':struct.pack_into('<qQ',raw,448,99,0)
    if fault=='segment-outside':struct.pack_into('<Q',raw,120+32,10000)
    with pytest.raises(ValueError)as ordinary:f.control.elf_dependencies(bytes(raw))
    replace_library(f,bytes(raw))
    with pytest.raises(ValueError)as actual:f.run()
    assert type(actual.value)is type(ordinary.value)is ValueError and str(actual.value)==str(ordinary.value)
    assert not f.sent and f.m.STORE+'/ci-evidence/installation.json'not in f.storage


def add_source(f,path,raw,*,mapped=True,loaded=False):
    from types import SimpleNamespace
    f.data[path]=raw;f.stats[path]=copy.copy(f.stats[OWNER]);f.stats[path].st_ino=4000+len(f.data);f.stats[path].st_size=len(raw)
    if mapped:f.mapped.append(path)
    if loaded:f.modules.append(SimpleNamespace(__file__=path))


@pytest.mark.parametrize('fault',['two-sonames','basename-and-soname','collision-loaded','two-needed-names'])
def test_exact_union_and_conflicting_projections_refuse_without_overwrite(monkeypatch,fault):
    f=alias_model(monkeypatch)
    if fault=='two-sonames':add_source(f,'/usr/lib/other/libz.so.9',soname_elf())
    if fault=='basename-and-soname':add_source(f,'/usr/lib/other/'+NEEDED,b'PURE_TEST_ONLY exact mapped source')
    if fault=='collision-loaded':add_source(f,f.target,b'PURE_TEST_ONLY retained module',mapped=False,loaded=True)
    if fault=='two-needed-names':
        raw=bytearray(elf_with_needed(NEEDED));first=NEEDED.encode()+b'\0';second=b'libz.so.1.3\0'
        struct.pack_into('<Q',raw,120+32,80)
        for i,item in enumerate([(1,0),(1,len(first)),(5,0x400200),(10,len(first+second)),(0,0)]):struct.pack_into('<qQ',raw,400+i*16,*item)
        raw[512:512+len(first+second)]=first+second;f.data[OWNER]=bytes(raw);f.stats[OWNER].st_size=len(raw)
    with pytest.raises(f.m.ClosureProjectionRefused)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    reason={'two-sonames':'MULTIPLE_IDENTITY','basename-and-soname':'MULTIPLE_IDENTITY','collision-loaded':'TARGET_COLLISION','two-needed-names':'SOURCE_TARGET_CONFLICT'}[fault]
    assert failed.value.facts['failure']['reason']==reason
    assert not failed.value.facts['assignments']and not f.sent


def test_exact_basename_and_SONAME_same_source_are_one_identity(monkeypatch):
    f=alias_model(monkeypatch);raw=f.data.pop(f.library);info=f.stats.pop(f.library);f.mapped.remove(f.library)
    f.library=f.target;f.data[f.library]=raw;f.stats[f.library]=info;f.mapped.append(f.library)
    rows,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    assert facts['elf_soname_projections']['requests']==[{'owner':OWNER,'needed':NEEDED,'candidates':[f.library]}]
    assert next(r for r in rows if r['source']==f.library)['target']==f.library


@pytest.mark.parametrize('name',['libz.so.2',None])
def test_wrong_or_missing_SONAME_keeps_legacy_needed_refusal_grammar(monkeypatch,name):
    f=alias_model(monkeypatch);replace_library(f,soname_elf(name)if name else b'PURE_TEST_ONLY non-ELF mapped source')
    with pytest.raises(f.m.ClosureNeededRefused)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    assert failed.value.facts['needed']==NEEDED and failed.value.facts['matches']==[]
    assert set(failed.value.facts)=={'stage','owner','owner_metadata','needed','mapped_paths','matches','match_count','mapped_records','native_maps_sha256','original_started','original_deadline','observed_monotonic','bounds'}


@pytest.mark.parametrize('pin',[None,True,'','0'*63,'G'*64])
def test_invalid_held_manifest_hash_refuses_before_any_acquisition(monkeypatch,pin):
    f=alias_model(monkeypatch);f.g.protected_path=lambda *args:(_ for _ in ()).throw(AssertionError('must not acquire'))
    with pytest.raises(ValueError,match='already verified'):f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=pin)
    assert not f.reads


@pytest.mark.parametrize('fault',['stat','read','caller','close','persist','persist-tamper','export-tamper','deadline','bad-clock','sourceguard'])
def test_unknown_failures_never_become_complete_new_projection_diagnosis(monkeypatch,fault):
    f=alias_model(monkeypatch);replace_library(f,soname_elf(extra=((14,0),)))
    metadata=f.g.protected_path;read=f.g.protected_read;write=f.m.write_fixed
    def path(name,*args):
        if name==f.library and fault=='stat':raise OSError('PURE_TEST_ONLY unknown stat')
        return metadata(name,*args)
    def acquire(name,*args,**kwargs):
        if name==f.library and fault=='read':raise OSError('PURE_TEST_ONLY unknown read')
        if name==max(p for p in f.data if p!='/usr/lib/python3.12/TEST_ONLY-member.py')and fault=='deadline':f.now[0]=990.
        return read(name,*args,**kwargs)
    f.g.protected_path=path;f.g.protected_read=acquire
    if fault=='caller':f.caller.verify=lambda:(_ for _ in ()).throw(OSError('PURE_TEST_ONLY caller changed'))
    if fault=='close':f.caller.close=lambda:(_ for _ in ()).throw(OSError('PURE_TEST_ONLY close unknown'))
    if fault=='bad-clock':f.now[0]=float('nan')
    if fault=='sourceguard':f.scope['installed_module']=lambda *args:(_ for _ in ()).throw(ValueError('PURE_TEST_ONLY sourceguard'))
    def persist(name,raw):
        if str(name).endswith('/installation.json')and fault=='persist':raise OSError('PURE_TEST_ONLY persist failed')
        write(name,raw)
        if str(name).endswith('/installation.json')and fault=='persist-tamper':f.storage[str(name)]=b'PURE_TEST_ONLY tamper'
    monkeypatch.setattr(f.m,'write_fixed',persist)
    if fault=='export-tamper':f.caller.close=lambda:f.storage.__setitem__(f.m.STORE+'/ci-evidence/installation.json',b'PURE_TEST_ONLY export tamper')
    with pytest.raises((ValueError,OSError)):f.run()
    assert not f.sent
    if fault=='sourceguard':assert f.reads==[f.m.STORE+'/ci-evidence/principal.json']


@pytest.mark.parametrize('fault',['hash','length','ELF','inode'])
def test_actual_later_host_load_rejects_changed_canonical_associations(monkeypatch,fault):
    f=alias_model(monkeypatch);f.rows,_=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    row=next(r for r in f.rows if r['source']==f.library)
    if fault=='hash':f.data[f.library]=f.data[f.library][:-1]+b'x'
    if fault=='length':row['bytes']+=1
    if fault=='ELF':row['elf']=None
    if fault=='inode':f.stats[f.library].st_ino=f.stats[OWNER].st_ino
    c=host_model(monkeypatch,f)
    with pytest.raises(ValueError):c.load_ci_control_host(f.g,'baseline',f.caller)


@pytest.mark.parametrize('fault',['extra','missing','schema','manifest','maps','bool-clock','NaN-clock','renewed','object-extra','object-bool','object-status','object-duplicate','request-extra','request-ambiguous','request-duplicate','assignment-extra','assignment-missing','assignment-name','assignment-duplicate','failure'])
def test_copied_projection_DATA_tamper_is_refused_by_pure_checker_without_authority(monkeypatch,fault):
    f=alias_model(monkeypatch);_,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN);proof=copy.deepcopy(facts['elf_soname_projections'])
    if fault=='extra':proof['approved']=True
    if fault=='missing':proof.pop('objects')
    if fault=='schema':proof['schema']='ACTUAL'
    if fault=='manifest':proof['source_manifest_sha256']='x'
    if fault=='maps':proof['native_maps_sha256']=True
    if fault=='bool-clock':proof['observed_monotonic']=True
    if fault=='NaN-clock':proof['observed_monotonic']=float('nan')
    if fault=='renewed':proof['original_deadline']+=1
    if fault=='object-extra':proof['objects'][0]['permit']=True
    if fault=='object-bool':proof['objects'][0]['bytes']=True
    if fault=='object-status':proof['objects'][0]['parse_status']='MALFORMED'
    if fault=='object-duplicate':proof['objects'].append(copy.deepcopy(proof['objects'][0]))
    if fault=='request-extra':proof['requests'][0]['permit']=True
    if fault=='request-ambiguous':proof['requests'][0]['candidates']=[]
    if fault=='request-duplicate':proof['requests'].append(copy.deepcopy(proof['requests'][0]))
    if fault=='assignment-extra':proof['assignments'][0]['permit']=True
    if fault=='assignment-missing':proof['assignments']=[]
    if fault=='assignment-name':proof['assignments'][0]['needed']='other.so'
    if fault=='assignment-duplicate':proof['assignments'].append(copy.deepcopy(proof['assignments'][0]))
    if fault=='failure':proof['failure']={'reason':'unknown'}
    with pytest.raises(ValueError):f.m._check_projection_data(proof)


def test_existing_PT_INTERP_projection_is_retained_for_matching_needed_basename(monkeypatch):
    import os
    f=alias_model(monkeypatch);old=f.library;f.library='/usr/lib/ld-fixture.so.9';f.target='/lib/ld-fixture.so'
    del f.data[old];del f.stats[old];f.mapped.remove(old)
    add_source(f,f.library,soname_elf('ld-fixture.so'))
    raw=bytearray(elf_with_needed('ld-fixture.so'));struct.pack_into('<H',raw,56,3)
    loader=f.target.encode()+b'\0';struct.pack_into('<IIQQQQQQ',raw,176,3,4,300,0,0,len(loader),len(loader),1);raw[300:300+len(loader)]=loader
    f.data[OWNER]=bytes(raw);f.stats[OWNER].st_size=len(raw)
    def resolve(path):
        assert path==f.target
        return f.library
    monkeypatch.setattr(os.path,'realpath',resolve)
    rows,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    assert next(r for r in rows if r['source']==f.library)['target']==f.target
    assert facts['elf_soname_projections']['assignments']==[{'source':f.library,'target':f.target,'needed':'ld-fixture.so'}]


def test_original_request_cap_stops_before_4097th_request_without_next_allocation(monkeypatch):
    f=alias_model(monkeypatch);other='/usr/lib/PURE_TEST_ONLY-other.so';add_source(f,other,b'PURE_TEST_ONLY other mapped source')
    raw=bytearray(elf_with_needed(NEEDED));first=NEEDED.encode()+b'\0';second=b'PURE_TEST_ONLY-other.so\0'
    struct.pack_into('<Q',raw,120+32,80)
    for i,item in enumerate([(1,0),(1,len(first)),(5,0x400200),(10,len(first+second)),(0,0)]):struct.pack_into('<qQ',raw,400+i*16,*item)
    raw[512:512+len(first+second)]=first+second
    for i in range(2050):add_source(f,f'/usr/lib/python3.12/TEST_ONLY-owner-{i:04d}.so',bytes(raw),mapped=False,loaded=True)
    with pytest.raises(f.m.ClosureProjectionRefused)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    assert failed.value.facts['failure']['reason']=='REQUEST_CAP'
    assert len(failed.value.facts['requests'])==4096 and not failed.value.facts['assignments']


@pytest.mark.parametrize('fault',['diagnostic-cap','late-parser','stat-bool','stat-length'])
def test_projection_capacity_original_deadline_and_stat_bindings_refuse_unknown_completion(monkeypatch,fault):
    f=alias_model(monkeypatch);read=f.g.protected_read
    if fault=='diagnostic-cap':monkeypatch.setattr(f.m,'MAX_FILE',65536+256)
    if fault=='stat-bool':f.stats[f.library].st_dev=True
    if fault=='stat-length':f.stats[f.library].st_size+=1
    if fault=='late-parser':
        def acquire(name,*args,**kwargs):
            raw=read(name,*args,**kwargs)
            if name==f.library:f.now[0]=990.
            return raw
        f.g.protected_read=acquire
    with pytest.raises(ValueError)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    assert type(failed.value)is ValueError and not f.sent


def test_manifest_and_workflow_context_bind_same_already_held_source_bytes_before_discovery():
    import ast
    from pathlib import Path
    source=(Path(__file__).parents[1]/'bench/pinned-candidate/linux_lease_control_ci.py').read_text();tree=ast.parse(source)
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='suite_main')
    calls=[n for n in ast.walk(main)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)]
    discovery=next(n for n in calls if n.func.id=='discover_closure')
    held=discovery.keywords[0].value
    assert discovery.keywords[0].arg=='_source_manifest_sha256'and ast.unparse(held)=='sha(source_raw)'
    context=next(n for n in calls if n.func.id=='workflow_context');guard=next(n for n in calls if n.func.id=='source_manifest')
    assert ast.unparse(context.args[1])=='sha(source_raw)'and guard.lineno<context.lineno<discovery.lineno
    assert not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='installed_read'for n in ast.walk(discovery))


def test_forged_known_failure_cannot_disagree_with_its_closed_held_DATA(monkeypatch):
    f=alias_model(monkeypatch);_,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    proof=copy.deepcopy(facts['elf_soname_projections'])
    proof['failure']={'reason':'MALFORMED_SONAME','source':f.library,'owner':None,'needed':None,'candidates':[]}
    with pytest.raises(ValueError):f.m._check_projection_data(proof)
