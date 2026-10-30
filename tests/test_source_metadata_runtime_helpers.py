"""Public TEST_ONLY live helper conservation through authority/store interfaces."""
import importlib.util
import json
from pathlib import Path

import pytest

from twin import source_metadata as sm
from test_source_metadata import fixture_import


def helper_module(tmp_path):
    path = tmp_path / 'TEST_ONLY_helpers.py'
    path.write_text('''from twin import source_metadata as sm

def helper():
    return None

DISPATCH = {"check": helper}

def adapter(acquisition, artifacts, policy):
    return sm.retained_receipt_adapter(acquisition, artifacts, policy)

def checker(manifest, archive, receipts, policy):
    DISPATCH["check"]()
    return sm.retained_source_checker(manifest, archive, receipts, policy)
''')
    spec = importlib.util.spec_from_file_location('TEST_ONLY_helpers', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_fixture(tmp_path):
    manifest, archive, receipts, old = fixture_import()
    module = helper_module(tmp_path)
    policy = json.loads(old.description)['policy']
    authority = sm.MetadataAuthority.freeze('TEST_ONLY-parent', 'TEST_ONLY-guarded', '1',
        sm.sha256(sm.canonical(policy)), module.adapter, module.checker,
        policy=policy, helper_modules=(module,))
    store = sm.MetadataStore(purpose='TEST_ONLY')
    raw = sm.canonical(manifest)
    acquired = store.acquire('TEST_ONLY-before', raw, archive, receipts, sm.sha256(raw), authority)
    return module, authority, store, acquired, raw, archive, receipts


def test_changed_actual_dispatch_rejects_verify_acquire_and_resolve(tmp_path, monkeypatch):
    module, authority, store, acquired, raw, archive, receipts = guarded_fixture(tmp_path)
    def replacement():
        raise AssertionError('must reject before invoking replacement')
    monkeypatch.setitem(module.DISPATCH, 'check', replacement)
    for action in (authority.verify,
                   lambda: store.acquire('TEST_ONLY-after', raw, archive, receipts, sm.sha256(raw), authority),
                   lambda: store.resolve(**acquired.binding)):
        with pytest.raises(ValueError, match='helper|binding'):
            action()


@pytest.mark.parametrize('mutation', ['binding','code','defaults','kwdefaults','add','remove','rename','alias','config','file'])
def test_live_helper_drift_is_conserved(tmp_path, monkeypatch, mutation):
    module, authority, store, acquired, raw, archive, receipts = guarded_fixture(tmp_path)
    def replacement():
        return 'TEST_ONLY different behavior'
    if mutation == 'binding':
        monkeypatch.setattr(module,'helper',replacement)
    elif mutation == 'code':
        monkeypatch.setattr(module.helper,'__code__',replacement.__code__)
    elif mutation == 'defaults':
        monkeypatch.setattr(module.helper,'__defaults__',(7,))
    elif mutation == 'kwdefaults':
        monkeypatch.setattr(module.helper,'__kwdefaults__',{'TEST_ONLY':{'changed':True}})
    elif mutation == 'add':
        monkeypatch.setattr(module,'added',replacement,raising=False)
    elif mutation == 'remove':
        monkeypatch.delattr(module,'helper')
    elif mutation == 'rename':
        monkeypatch.setattr(module,'renamed',module.helper,raising=False)
        monkeypatch.delattr(module,'helper')
    elif mutation == 'alias':
        monkeypatch.setattr(module,'sm',type(module)('TEST_ONLY-fake-core'))
    elif mutation == 'config':
        monkeypatch.setitem(module.DISPATCH,'new-setting',True)
    else:
        Path(module.__file__).write_text(Path(module.__file__).read_text()+'\n# changed source\n')
    for action in (authority.verify,
                   lambda: store.acquire('TEST_ONLY-after',raw,archive,receipts,sm.sha256(raw),authority),
                   lambda: store.resolve(**acquired.binding)):
        with pytest.raises(ValueError,match='helper|binding'):
            action()


@pytest.mark.parametrize('mutation',['binding','code','defaults'])
def test_runtime_inventory_guard_cannot_self_attest_unchanged(tmp_path,monkeypatch,mutation):
    _, authority, _, _, _, _, _ = guarded_fixture(tmp_path)
    guard = sm._runtime_helper_inventory
    def replacement(modules):
        return [], ()
    if mutation == 'binding':
        monkeypatch.setattr(sm,'_runtime_helper_inventory',replacement)
    elif mutation == 'code':
        monkeypatch.setattr(guard,'__code__',replacement.__code__)
    else:
        monkeypatch.setattr(guard,'__defaults__',(None,))
    with pytest.raises(ValueError,match='guard binding'):
        authority.verify()


def test_post_callback_helper_mutation_installs_no_receipt(tmp_path):
    manifest, archive, receipts, old = fixture_import()
    module = helper_module(tmp_path)
    source = Path(module.__file__).read_text().replace(
        'return sm.retained_source_checker(manifest, archive, receipts, policy)',
        'sm.retained_source_checker(manifest, archive, receipts, policy)\n    globals()["added"] = helper')
    Path(module.__file__).write_text(source)
    exec(compile(source,module.__file__,'exec'),vars(module))
    policy = json.loads(old.description)['policy']
    authority = sm.MetadataAuthority.freeze('TEST_ONLY-parent','TEST_ONLY-post','1',sm.sha256(sm.canonical(policy)),
        module.adapter,module.checker,policy=policy,helper_modules=(module,))
    store = sm.MetadataStore(purpose='TEST_ONLY'); raw = sm.canonical(manifest)
    with pytest.raises(ValueError,match='helper|binding'):
        store.acquire('TEST_ONLY-mutating',raw,archive,receipts,sm.sha256(raw),authority)
    with pytest.raises(ValueError,match='no actual protected'):
        store.resolve('TEST_ONLY-mutating',sm.sha256(raw),authority.digest,'0'*64)


def test_only_actual_unique_module_objects_can_be_selected(tmp_path):
    module = helper_module(tmp_path)
    _,_,_,old = fixture_import(); policy = json.loads(old.description)['policy']
    for modules in ((module,module),('TEST_ONLY_helpers',)):
        with pytest.raises(ValueError,match='actual helper'):
            sm.MetadataAuthority.freeze('TEST_ONLY-parent','TEST_ONLY-invalid','1',sm.sha256(sm.canonical(policy)),
                module.adapter,module.checker,policy=policy,helper_modules=modules)


def test_double_underscore_function_is_not_hidden_from_helper_inventory(tmp_path,monkeypatch):
    module,authority,_,_,_,_,_=guarded_fixture(tmp_path)
    def hidden():
        return 'TEST_ONLY hidden dispatch'
    monkeypatch.setattr(module,'__dispatch',hidden,raising=False)
    with pytest.raises(ValueError,match='helper|binding'):
        authority.verify()


def test_helper_default_aliasing_is_part_of_runtime_identity(tmp_path):
    module=helper_module(tmp_path)
    source=Path(module.__file__).read_text().replace('def helper():','def helper(a=None, b=None):')
    Path(module.__file__).write_text(source);exec(compile(source,module.__file__,'exec'),vars(module))
    shared=[0];module.helper.__defaults__=(shared,shared)
    _,_,_,old=fixture_import();policy=json.loads(old.description)['policy']
    authority=sm.MetadataAuthority.freeze('TEST_ONLY-parent','TEST_ONLY-default-alias','1',sm.sha256(sm.canonical(policy)),
        module.adapter,module.checker,policy=policy,helper_modules=(module,))
    module.helper.__defaults__=([0],[0])
    with pytest.raises(ValueError,match='helper|binding'):
        authority.verify()


def test_runtime_function_simple_name_is_conserved(tmp_path,monkeypatch):
    module,authority,_,_,_,_,_=guarded_fixture(tmp_path)
    monkeypatch.setattr(module.helper,'__name__','TEST_ONLY-rebound-name')
    with pytest.raises(ValueError,match='helper|binding'):
        authority.verify()
