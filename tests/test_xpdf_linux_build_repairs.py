"""Independent Spec regression controls: only existing OS models and static ELF DATA."""
import json
import os
import stat
import struct
from pathlib import Path
import pytest
from test_xpdf_linux_build import module,encoded,sha
from test_xpdf_linux_build_model import whole_model,retained_archive,reseal_complete

@pytest.mark.parametrize('mutation',['control','remove_all_queries','unsupported_cmake_version','unreviewed_fetch_script','remove_selector_observations','impossible_normal_raw_wait'])
def test_complete_checker_enforces_fixed_tool_evidence(monkeypatch,tmp_path,mutation):
 selection,root,calls=whole_model(monkeypatch,tmp_path,retained_archive())
 result=module.build_linux_pair(selection,root)
 assert result['status']=='COMPLETE_BUILD_PAIR',result['first_failure']
 bundle={p.relative_to(root/'export').as_posix():p.read_bytes() for p in (root/'export').rglob('*') if p.is_file()}
 assert module.check_build_bundle(bundle,sha(encoded(selection)))['build_complete']
 if mutation=='remove_all_queries':
  result['commands']=[c for c in result['commands'] if len(c['argv'])!=2]
 elif mutation=='unsupported_cmake_version':
  command=next(c for c in result['commands'] if c['argv']==['/usr/bin/cmake','--version'])
  old=command['stdout']['sha256'];new=b'cmake version 0.0.0 TEST_ONLY unsupported guard surface\n'
  for path in list(bundle):
   if sha(bundle[path])==old:bundle[path]=new
  command['stdout'].update(sha256=sha(new),retained_bytes=len(new),observed_bytes_lower_bound=len(new))
 elif mutation=='unreviewed_fetch_script':
  command=next(c for c in result['commands'] if c['argv'][-1]=='--internal-fetch')
  command['argv'][4]='/TEST_ONLY/unreviewed/build_linux_pair.py'
  command['custody']['command_binding_sha256']=module._binding(result,command)
 elif mutation=='impossible_normal_raw_wait':
  custody=result['commands'][0]['custody'];custody['raw_wait']=128
  next(e for e in custody['observations'] if e['kind']=='direct-reap')['detail']['raw_wait']=128
 elif mutation=='remove_selector_observations':
  tool=json.loads(bundle['TOOL-MANIFEST.json']);tool={k:v for k,v in tool.items() if k in ['compiler_target','specs_sha256']}
  bundle['TOOL-MANIFEST.json']=encoded(tool);result['tool_manifest_sha256']=sha(bundle['TOOL-MANIFEST.json'])
 bundle=reseal_complete(bundle,result)
 try:summary=module.check_build_bundle(bundle,sha(encoded(selection)));accepted=True;reason=None
 except ValueError as e:summary=None;accepted=False;reason=str(e)
 if mutation=='control':assert accepted
 else:assert not accepted,'independent Spec regression: malformed complete build DATA was accepted: '+mutation

def elf_data(*,interpreter=None,needed=(),soname=None):
 strings=b'\0';entries=[]
 for tag,value in [(1,x) for x in needed]+([(14,soname)] if soname is not None else []):
  entries.append((tag,len(strings)));strings+=value.encode()+b'\0'
 num=3 if interpreter else 2
 start=64+num*56;ip=(interpreter.encode()+b'\0') if interpreter else b''
 dynamic_offset=(start+len(ip)+15)//16*16
 str_offset=dynamic_offset+(len(entries)+3)*16
 dynamic=entries+[(5,str_offset),(10,len(strings)),(0,0)]
 size=str_offset+len(strings)
 header=struct.pack('<16sHHIQQQIHHHHHH',b'\x7fELF\x02\x01\x01'+bytes(9),3,62,1,0,64,0,0,64,56,num,0,0,0)
 programs=[struct.pack('<IIQQQQQQ',1,4,0,0,0,size,size,4096)]
 if interpreter:programs.append(struct.pack('<IIQQQQQQ',3,4,start,0,0,len(ip),len(ip),1))
 programs.append(struct.pack('<IIQQQQQQ',2,4,dynamic_offset,0,0,len(dynamic)*16,len(dynamic)*16,8))
 raw=header+b''.join(programs)+ip;raw+=bytes(dynamic_offset-len(raw));raw+=b''.join(struct.pack('<QQ',*p) for p in dynamic)+strings
 assert len(raw)==size
 return raw

def test_selected_linker_symlink_soname_is_valid_static_association(monkeypatch,tmp_path):
 fixtures=tmp_path/'fixtures';fixtures.mkdir();owned=tmp_path/'owned';owned.mkdir()
 versioned=fixtures/'libTEST_ONLY.so.1';versioned.write_bytes(elf_data(soname='libTEST_ONLY.so.1'))
 link=fixtures/'libTEST_ONLY.so';link.symlink_to(versioned.name)
 loader='/lib64/ld-TEST_ONLY.so.2';binary=elf_data(interpreter=loader,needed=['libTEST_ONLY.so.1'])
 assert module._elf(binary)['needed']==['libTEST_ONLY.so.1']
 original_resolve=Path.resolve;original_read=module._stable_read
 monkeypatch.setattr(Path,'resolve',lambda p,*a,**k:p if str(p)==loader else original_resolve(p,*a,**k))
 monkeypatch.setattr(module,'_stable_read',lambda p,*a,**k:b'TEST_ONLY selected loader bytes' if str(p)==loader else original_read(p,*a,**k))
 tools={str(link):{'sha256':sha(versioned.read_bytes()),'resolved':str(versioned),'links':[{'path':str(link),'target':versioned.name}]},loader:{'sha256':sha(b'TEST_ONLY selected loader bytes'),'resolved':loader,'links':[]}}
 payload={'TOOL-MANIFEST.json':(encoded({'compiler_target':'x86_64-linux-gnu'}),'metadata')}
 try:module._link_association(binary,owned,'pristine',(str(link)+'\n').encode(),{'tools':tools},payload);accepted=True;reason=None
 except module.BuildHold as e:accepted=False;reason=str(e)
 assert accepted,'independent Spec regression: correctly preselected symlink/SONAME association was rejected: '+str(reason)


def test_source_evidence_patch_has_required_private_mode(monkeypatch,tmp_path):
 selection,root,_=whole_model(monkeypatch,tmp_path,retained_archive())
 result=module.build_linux_pair(selection,root)
 assert result['status']=='COMPLETE_BUILD_PAIR',result['first_failure']
 mode=stat.S_IMODE((root/'inputs/xpdf-4.06-origin.patch').stat().st_mode)
 assert mode==0o600,'independent Spec regression: patch evidence uses ambient mode '+oct(mode)


@pytest.mark.parametrize('raw,kind,exit_code,number,valid', [
    (0, 'EXITED', 0, None, True), (256, 'EXITED', 1, None, True),
    (65280, 'EXITED', 255, None, True), (128, 'EXITED', 0, None, False),
    (65536, 'EXITED', 0, None, False), (9, 'SIGNALED', None, 9, True),
    (137, 'SIGNALED', None, 9, True), (265, 'SIGNALED', None, 9, False),
    (127, 'SIGNALED', None, 127, False), (0, 'SIGNALED', None, 0, False),
])
def test_terminal_raw_status_is_exact_and_mutually_exclusive(raw, kind, exit_code, number, valid):
    from test_xpdf_linux_build import custody_bundle, reseal
    bundle, result = custody_bundle()
    command = result['commands'][0]
    command['disposition'] = 'HELD'
    custody = command['custody']
    terminal = next(event for event in custody['observations'] if event['kind'] == 'direct-reap')
    details = dict(wait_kind=kind, raw_wait=raw, exit_code=exit_code, signal=number)
    custody.update(details)
    terminal['detail'].update(details)
    bundle = reseal(bundle, result)
    if valid:
        assert not module.check_build_bundle(bundle, result['selection_sha256'])['native_permission']
    else:
        with pytest.raises(ValueError):
            module.check_build_bundle(bundle, result['selection_sha256'])


@pytest.mark.parametrize('mutation', ['one_selector', 'reordered_queries', 'internal_selector', 'non_gnu', 'target', 'specs'])
def test_complete_query_associations_cannot_be_repaired_by_public_resealing(monkeypatch, tmp_path, mutation):
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive())
    result = module.build_linux_pair(selection, root)
    assert result['status'] == 'COMPLETE_BUILD_PAIR', result['first_failure']
    bundle = {path.relative_to(root / 'export').as_posix(): path.read_bytes() for path in (root / 'export').rglob('*') if path.is_file()}
    if mutation == 'one_selector':
        tool = json.loads(bundle['TOOL-MANIFEST.json'])
        del tool['/bin/sh']
        bundle['TOOL-MANIFEST.json'] = encoded(tool)
        result['tool_manifest_sha256'] = sha(bundle['TOOL-MANIFEST.json'])
    elif mutation == 'reordered_queries':
        first, second = result['commands'][:2]
        first['argv'], second['argv'] = second['argv'], first['argv']
        for command in (first, second):
            command['custody']['command_binding_sha256'] = module._binding(result, command)
    else:
        options = {'internal_selector': '-print-prog-name=cc1', 'non_gnu': '--version', 'target': '-dumpmachine', 'specs': '-dumpspecs'}
        command = next(c for c in result['commands'] if c['argv'] == ['/usr/bin/gcc', options[mutation]])
        replacement = {'internal_selector': b'/TEST_ONLY/unselected/cc1\n', 'non_gnu': b'TEST_ONLY non-GNU-without-marker'.replace(b'GNU', b'vendor'),
                       'target': b'x86_64-different-linux-gnu\n', 'specs': b'TEST_ONLY changed specs\n'}[mutation]
        bundle['journal/changed-query.log'] = replacement
        command['stdout'].update(sha256=sha(replacement), retained_bytes=len(replacement), observed_bytes_lower_bound=len(replacement))
    with pytest.raises(ValueError):
        module.check_build_bundle(reseal_complete(bundle, result), sha(encoded(selection)))


@pytest.mark.parametrize('resolved,needed,accepted', [
    ('libTEST_ONLY.so.1', 'libTEST_ONLY.so.1', True),
    ('libTEST_ONLY-storage.so.9', 'libTEST_ONLY.so.1', True),
    ('libTEST_ONLY-storage.so.9', 'libTEST_ONLY-unselected.so.2', False),
])
def test_selected_soname_alias_crosses_the_full_driver_and_checker(monkeypatch, tmp_path, resolved, needed, accepted):
    import test_xpdf_linux_build_model as model
    binary = elf_data(interpreter='/lib64/ld-linux-x86-64.so.2', needed=[needed])
    monkeypatch.setattr(model, 'fake_binary', lambda: binary)
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive(), link_library=(elf_data(soname='libTEST_ONLY.so.1'), resolved))
    result = module.build_linux_pair(selection, root)
    if not accepted:
        assert result['status'] == 'HELD' and result['hold_codes'] == ['H_ELF_ASSOCIATION']
        assert not (root / 'export/RESULT.json').exists()
        return
    assert result['status'] == 'COMPLETE_BUILD_PAIR', result['first_failure']
    bundle = {path.relative_to(root / 'export').as_posix(): path.read_bytes() for path in (root / 'export').rglob('*') if path.is_file()}
    assert module.check_build_bundle(bundle, sha(encoded(selection)))['build_complete']
    assert result['runtime_access_closure'] == 'UNESTABLISHED'


@pytest.mark.parametrize('failure', [False, True])
def test_private_creation_and_child_inheritance_restore_the_callers_umask(monkeypatch, tmp_path, failure):
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive(), fail_stage='cmake' if failure else None)
    popen = module.subprocess.Popen
    inherited = []
    def modeled_popen(*args, **kwargs):
        current = os.umask(0o077)
        os.umask(current)
        inherited.append(current)
        return popen(*args, **kwargs)
    monkeypatch.setattr(module.subprocess, 'Popen', modeled_popen)
    caller_mask = os.umask(0o022)
    try:
        result = module.build_linux_pair(selection, root)
        restored = os.umask(0o022)
        assert restored == 0o022
    finally:
        os.umask(caller_mask)
    assert inherited and all(value == 0o077 for value in inherited)
    assert result['status'] == ('HELD' if failure else 'COMPLETE_BUILD_PAIR')
    assert stat.S_IMODE((root / 'inputs/xpdf-4.06-origin.patch').stat().st_mode) == 0o600
    assert stat.S_IMODE((root / 'pristine-source/CMakeLists.txt').stat().st_mode) == 0o600


def test_original_cancellation_restores_umask_and_retains_owned_evidence(monkeypatch, tmp_path):
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive())
    def interrupted_launch(*args, **kwargs):
        current = os.umask(0o077)
        os.umask(current)
        assert current == 0o077
        raise KeyboardInterrupt('TEST_ONLY original cancellation')
    monkeypatch.setattr(module.subprocess, 'Popen', interrupted_launch)
    caller_mask = os.umask(0o022)
    try:
        with pytest.raises(KeyboardInterrupt, match='original cancellation'):
            module.build_linux_pair(selection, root)
        assert os.umask(0o022) == 0o022
    finally:
        os.umask(caller_mask)
    assert root.exists() and (root / 'FIRST-FAILURE.json').is_file()
    assert not (root / 'export/RESULT.json').exists()
