"""Pure replay of initial-principal refusal; all OS/account state is modeled."""
import ast
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest

SOURCE = Path(__file__).resolve().parents[1] / 'bench/pinned-candidate'

def load(name):
    spec=importlib.util.spec_from_file_location('TEST_ONLY_'+name, SOURCE/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

@pytest.mark.parametrize("refusal", ("uid-share", "gid-share", "home-exposed", "caller-gid"))
def test_observed_unsafe_principal_keeps_failed_receipt_instead_of_losing_export(monkeypatch, refusal):
    ci=load('linux_lease_control_ci'); control=load('linux_lease_control')
    tree=ast.parse((SOURCE/'linux_lease_control_ci.py').read_text())
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='suite_main')
    stage=next(n for n in main.body if isinstance(n,ast.Try) and any(
        isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='installed_module' for c in ast.walk(n)))
    nobody=SimpleNamespace(pw_name='nobody',pw_uid=65534,pw_gid=65534,pw_dir='/TEST_ONLY-no-home')
    other=SimpleNamespace(pw_name='TEST_ONLY-shared-account',pw_uid=65534 if refusal=='uid-share' else 42,pw_gid=65534 if refusal=='gid-share' else 42)
    monkeypatch.setattr(control.pwd,'getpwnam',lambda name:nobody)
    monkeypatch.setattr(control.pwd,'getpwall',lambda:[nobody,other] if refusal in ('uid-share','gid-share') else [nobody])
    monkeypatch.setattr(control.grp,'getgrall',lambda:[SimpleNamespace(gr_name='nogroup',gr_gid=65534,gr_mem=[])])
    class ModelPath:
        def __init__(self,path): self.path=path
        def read_text(self):
            assert self.path=='/proc/201/status'
            return 'TEST_ONLY raw caller status'
        def exists(self): return refusal=='home-exposed'
        def stat(self): return SimpleNamespace(st_uid=65534,st_gid=65534,st_mode=0o700)
    monkeypatch.setattr(control,'Path',ModelPath)
    g=SimpleNamespace(parse_status=lambda raw:{'Gid':'65534' if refusal=='caller-gid' else '1001'},candidate_unused=lambda uid,gid:None)
    caller=SimpleNamespace(pid=201,uid=[1001]*4,verify=lambda:None)
    observed={}; outcome=None; base={}
    def keep(g,base,name,value,**kwargs):
        observed[name]=value; base[name]=ci.canonical(value)+b'\n'
    scope={'time':SimpleNamespace(monotonic=lambda:150.),'budget':ci.SuiteBudget(100.,1000.),
           'g':g,'caller':caller,'control':control,'installed_module':lambda *args:None,
           'manifest':{},'base':base,'outcome':outcome,'PrerequisiteUnavailable':ci.PrerequisiteUnavailable,
           'persist_observation':keep,'admit_ci_root':lambda *args:None}
    escaped=None
    try: exec(compile(ast.Module(body=[stage],type_ignores=[]),'TEST_ONLY-initial-principal-stage','exec'),scope)
    except ValueError as error: escaped=error
    assert escaped is None, f'Observed unsafe principal escaped before failed export: {escaped}'
    assert scope['outcome']['status']=='FAIL' and scope['outcome']['executed'] is False
    assert scope['outcome']['control_passed'] is False
    assert observed, 'Original account observations must be retained before refusal export'

    record=observed['suite/principal.json']
    assert record['status']=='REFUSED' and record['schema']=='TEST_ONLY-ci-principal-refusal/v1'
    assert record['started']==100. and record['deadline']==1000. and record['observed_monotonic']==150.
    assert record['facts']['caller_gid']==(65534 if refusal=='caller-gid' else 1001)
    assert record['facts']['home_exposed']==(refusal=='home-exposed')
    assert record['facts']['uid_names']==(['TEST_ONLY-shared-account','nobody'] if refusal=='uid-share' else ['nobody'])
    assert record['facts']['primary_names']==(['TEST_ONLY-shared-account','nobody'] if refusal=='gid-share' else ['nobody'])
    files={**base,'suite/result.json':ci.canonical(scope['outcome'])+b'\n'}
    replay=ci.receive_export(b''.join(ci.export_frames(files,scope['outcome'])))
    assert replay['outcome']['status']=='FAIL' and replay['outcome']['production_capture_accepted'] is False
    assert replay['files']['suite/principal.json']==base['suite/principal.json']
    with pytest.raises(ValueError) as original: control.principal_facts(g,caller)
    assert type(original.value) is ValueError, 'Production keeps its original rejection behavior'


def test_ci_principal_unknown_caller_custody_does_not_become_complete_refusal(monkeypatch):
    control=load('linux_lease_control')
    nobody=SimpleNamespace(pw_name='nobody',pw_uid=65534,pw_gid=65534,pw_dir='/TEST_ONLY-no-home')
    monkeypatch.setattr(control.pwd,'getpwnam',lambda name:nobody)
    monkeypatch.setattr(control.pwd,'getpwall',lambda:[])
    monkeypatch.setattr(control.grp,'getgrall',lambda:[])
    class ModelPath:
        def __init__(self,path): pass
        def read_text(self): return 'TEST_ONLY caller status'
        def exists(self): return False
    monkeypatch.setattr(control,'Path',ModelPath)
    def lost(): raise OSError('TEST_ONLY actual caller changed')
    g=SimpleNamespace(parse_status=lambda raw:{'Gid':'1001'},candidate_unused=lambda uid,gid:None)
    with pytest.raises(OSError,match='caller changed'): control.ci_principal_facts(g,SimpleNamespace(pid=201,uid=[1001]*4,verify=lost))


def test_valid_ci_and_production_principal_facts_are_identical(monkeypatch):
    control=load('linux_lease_control')
    nobody=SimpleNamespace(pw_name='nobody',pw_uid=65534,pw_gid=65534,pw_dir='/TEST_ONLY-no-home')
    monkeypatch.setattr(control.pwd,'getpwnam',lambda name:nobody)
    monkeypatch.setattr(control.pwd,'getpwall',lambda:[nobody])
    monkeypatch.setattr(control.grp,'getgrall',lambda:[SimpleNamespace(gr_name='nogroup',gr_gid=65534,gr_mem=[])])
    class ModelPath:
        def __init__(self,path): pass
        def read_text(self): return 'TEST_ONLY caller status'
        def exists(self): return False
    monkeypatch.setattr(control,'Path',ModelPath)
    verified=[]
    caller=SimpleNamespace(pid=201,uid=[1001]*4,verify=lambda:verified.append(True))
    g=SimpleNamespace(parse_status=lambda raw:{'Gid':'1001'},candidate_unused=lambda uid,gid:None)
    assert control.ci_principal_facts(g,caller)==control.principal_facts(g,caller)
    assert verified==[True,True]
