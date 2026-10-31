"""Independent pure reached-source DATA controls; all host transports mocked."""
import copy
import pytest
from test_linux_lease_control_ci_elf_alias import alias_model, binding_model, PIN

@pytest.mark.parametrize("fault", ["control", "unheld-source", "wrong-union", "wrong-directory"])
def test_closed_projection_relation(monkeypatch, fault):
    f=alias_model(monkeypatch)
    rows,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    assert f.control.validate_ci_closure(rows)["files"]==len(rows)
    proof=copy.deepcopy(facts["elf_soname_projections"])
    if fault=="control":
        f.m._check_projection_data(proof,_binding=binding_model(f,rows))
        return
    if fault=="unheld-source":
        other="/unheld/not-mapped/libz.so.1.3"
        proof["requests"][0]["candidates"]=[other]
        proof["assignments"][0]["source"]=other
    elif fault=="wrong-union":
        obj=next(row for row in proof["objects"] if row["source"]==f.library)
        obj["soname"]="unrelated.so"
    else:
        proof["assignments"][0]["target"]="/unrelated/libz.so.1"
    with pytest.raises(ValueError):
        f.m._check_projection_data(proof,_binding=binding_model(f,rows))


def acquired_rows(f):
    """Only bytes already returned by the modeled protected read, never new IO."""
    rows=[]
    for source in sorted(set(f.reads)&set(f.data)):
        raw=f.data[source]
        rows.append({'source':source,'target':'/app/'+source.rsplit('/',1)[1]if source.startswith(f.m.STORE+'/source/')else source,
            'bytes':len(raw),'sha256':f.m.sha(raw),'elf':f.control.elf_dependencies(raw)})
    return rows


@pytest.mark.parametrize('fault',['missing-binding','incomplete-binding','manifest','maps','clock','bool-start','deadline','hash','length','stat','inode','held-SONAME','held-status','mapped','target','missing-object','missing-request','extra-request'])
def test_binding_or_record_relation_tamper_refuses_without_new_acquisition(monkeypatch,fault):
    f=alias_model(monkeypatch);rows,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    proof=copy.deepcopy(facts['elf_soname_projections']);binding=binding_model(f,rows);reads=list(f.reads)
    if fault=='missing-binding':binding=None
    if fault=='incomplete-binding':binding.pop('records')
    if fault=='manifest':binding['source_manifest_sha256']='2'*64
    if fault=='maps':binding['native_maps_sha256']='2'*64
    if fault=='clock':proof['observed_monotonic']+=1
    if fault=='bool-start':binding['original_started']=True
    if fault=='deadline':binding['original_deadline']+=900
    if fault=='hash':binding['records'][f.library]['sha256']='2'*64
    if fault=='length':binding['records'][f.library]['bytes']+=1
    if fault=='stat':binding['metadata'][f.library]['stat_bytes']+=1
    if fault=='inode':binding['metadata'][f.library]['inode']+=1
    if fault=='held-SONAME':binding['sonames'][f.library]=('other.so','VALID',None)
    if fault=='held-status':binding['sonames'][f.library]=(None,'ABSENT',None)
    if fault=='mapped':binding['mapped'].remove(f.library)
    if fault=='target':binding['original_targets'][f.library]='/unrelated/libz.so.1'
    if fault=='missing-object':proof['objects'].pop()
    if fault=='missing-request':proof['requests']=[];proof['assignments']=[]
    if fault=='extra-request':proof['requests'].append({'owner':'/unheld/owner.so','needed':'libz.so.1','candidates':[f.library]})
    with pytest.raises(ValueError):f.m._check_projection_data(proof,_binding=binding)
    assert f.reads==reads


def set_two_needed(f):
    import struct
    from test_linux_lease_control_ci_elf_alias import NEEDED
    from test_linux_lease_control_ci_elf_needed_refusal import elf_with_needed,OWNER
    raw=bytearray(elf_with_needed(NEEDED));first=NEEDED.encode()+b'\0';second=b'other.so\0'
    struct.pack_into('<Q',raw,120+32,80)
    for i,item in enumerate([(1,0),(1,len(first)),(5,0x400200),(10,len(first+second)),(0,0)]):struct.pack_into('<qQ',raw,400+i*16,*item)
    raw[512:512+len(first+second)]=first+second;f.data[OWNER]=bytes(raw);f.stats[OWNER].st_size=len(raw)


@pytest.mark.parametrize('mutation',['valid-prefix','missing-earlier','invented-later','missing-held-object','false-failure'])
def test_partial_request_failure_binds_exact_available_prefix(monkeypatch,mutation):
    from test_linux_lease_control_ci_elf_alias import add_source,soname_elf
    from test_linux_lease_control_ci_elf_needed_refusal import elf_with_needed
    f=alias_model(monkeypatch);set_two_needed(f)
    add_source(f,'/usr/lib/other-a.so.9',soname_elf('other.so'))
    add_source(f,'/usr/lib/other-b.so.9',soname_elf('other.so'))
    future='/usr/lib/PURE_TEST_ONLY-future-owner.so';add_source(f,future,elf_with_needed('libz.so.1'),mapped=False,loaded=True)
    with pytest.raises(f.m.ClosureProjectionRefused)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    proof=copy.deepcopy(failed.value.facts);rows=acquired_rows(f);binding=binding_model(f,rows)
    assert proof['failure']['reason']=='MULTIPLE_IDENTITY'and len(proof['requests'])==1
    if mutation=='missing-earlier':proof['requests']=[]
    if mutation=='invented-later':proof['requests'].append({'owner':future,'needed':'libz.so.1','candidates':[f.library]})
    if mutation=='missing-held-object':proof['objects'].pop()
    if mutation=='false-failure':proof['failure']['needed']='different.so'
    if mutation=='valid-prefix':f.m._check_projection_data(proof,_binding=binding)
    else:
        with pytest.raises(ValueError):f.m._check_projection_data(proof,_binding=binding)


@pytest.mark.parametrize('mutation',['valid-early-malformed','positive-upgrade','invent-later-object'])
def test_known_malformed_held_prefix_never_invents_unacquired_future_facts(monkeypatch,mutation):
    import struct
    from test_linux_lease_control_ci_elf_alias import soname_elf
    from test_linux_lease_control_ci_elf_needed_refusal import OWNER
    f=alias_model(monkeypatch);raw=bytearray(soname_elf());struct.pack_into('<H',raw,52,63)
    f.data[OWNER]=bytes(raw);f.stats[OWNER].st_size=len(raw)
    with pytest.raises(f.m.ClosureProjectionRefused)as failed:f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    proof=copy.deepcopy(failed.value.facts);binding=binding_model(f,acquired_rows(f))
    later=next(row for row in proof['objects']if row['source']==f.library)
    # The modeled available prefix holds only the first actually acquired source.
    for key in ('records','metadata','sonames','original_targets'):binding[key]={OWNER:binding[key][OWNER]}
    proof['objects']=[row for row in proof['objects']if row['source']==OWNER]
    if mutation=='positive-upgrade':proof['failure']=None
    if mutation=='invent-later-object':proof['objects'].append(later)
    if mutation=='valid-early-malformed':f.m._check_projection_data(proof,_binding=binding)
    else:
        with pytest.raises(ValueError):f.m._check_projection_data(proof,_binding=binding)


@pytest.mark.parametrize('mutation',['valid','missing-resolution','wrong-directory','false-held-resolution','false-source'])
def test_legitimate_fixed_interpreter_alias_requires_matching_held_route(monkeypatch,mutation):
    import os,struct
    from test_linux_lease_control_ci_elf_alias import add_source,soname_elf
    from test_linux_lease_control_ci_elf_needed_refusal import elf_with_needed,OWNER
    f=alias_model(monkeypatch);old=f.library;f.library='/usr/lib/ld-fixture.so.9';f.target='/lib/ld-fixture.so'
    del f.data[old];del f.stats[old];f.mapped.remove(old);add_source(f,f.library,soname_elf('ld-fixture.so'))
    raw=bytearray(elf_with_needed('ld-fixture.so'));struct.pack_into('<H',raw,56,3)
    target=f.target.encode()+b'\0';struct.pack_into('<IIQQQQQQ',raw,176,3,4,300,0,0,len(target),len(target),1);raw[300:300+len(target)]=target
    f.data[OWNER]=bytes(raw);f.stats[OWNER].st_size=len(raw)
    monkeypatch.setattr(os.path,'realpath',lambda path:f.library if path==f.target else (_ for _ in ()).throw(AssertionError('no new resolution')))
    rows,facts=f.m.discover_closure(f.g,f.control,f.budget,_source_manifest_sha256=PIN)
    proof=copy.deepcopy(facts['elf_soname_projections']);binding=binding_model(f,rows,interpreter_targets={f.library:f.target})
    assert proof['assignments']==[{'source':f.library,'target':f.target,'needed':'ld-fixture.so'}]
    if mutation=='missing-resolution':binding['interpreter_targets']={}
    if mutation=='wrong-directory':proof['assignments'][0]['target']='/unrelated/ld-fixture.so'
    if mutation=='false-held-resolution':binding['interpreter_targets'][f.library]='/unrelated/ld-fixture.so'
    if mutation=='false-source':binding['interpreter_targets']={'/unheld/ld-fixture.so.9':f.target}
    if mutation=='valid':
        f.m._check_projection_data(proof,_binding=binding)
        from test_linux_lease_control_ci_empty_urllib import host_model
        f.rows=rows;c=host_model(monkeypatch,f);_,profile,_=c.load_ci_control_host(f.g,'baseline',f.caller)
        assert {'source':f.library,'target':f.target,'sha256':next(row['sha256']for row in rows if row['source']==f.library)}in profile['readonly_mounts']
    else:
        with pytest.raises(ValueError):f.m._check_projection_data(proof,_binding=binding)
