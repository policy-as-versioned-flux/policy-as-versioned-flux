"""TEST_ONLY profile decisions. No runtime, helper, kernel, model or Actor is executed."""
import copy
import importlib.util
from pathlib import Path
import pytest
from twin import linux_candidate


def source_module(name):
    path = Path(__file__).parents[1]/'bench/pinned-candidate'/(name+'.py')
    spec = importlib.util.spec_from_file_location('TEST_ONLY_'+name,path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task_config(task,input_cap,output_cap,seconds):
    return {'profile':task+'-linux-bf16-v1','task':task,'task_contract_digest':'a'*64,
        'max_input_tokens':input_cap,'max_new_tokens':output_cap,'timeout_seconds':seconds,
        'context_tokens':8192,'raw_output_max_bytes':131072,'threads':2,'interop_threads':1,
        'backend':{'script':'/TEST_ONLY/qwen_backend.py','sha256':'1'*64,
            'python':'/TEST_ONLY/python','python_sha256':'2'*64},
        'runtime_contract':{'TEST_ONLY':'No acquired runtime or target authority'},
        'linux_profile':{'model_id':'Qwen/Qwen3-4B-Instruct-2507',
            'revision':'cdbee75f17c01a7cc42f958dc650907174af0554',
            'model_manifest_sha256':'409410d7d41d7e62aafb27c18f049fe3c62d66383b3a5b89d5fadfd3b773fd7e',
            'runtime_manifest_sha256':'3'*64,
            'chat_template_sha256':'64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326',
            'dtype':'torch.bfloat16','device':'cpu','attention':'eager','do_sample':False,
            'num_beams':1,'num_return_sequences':1,'seed':0,'use_cache':True,
            'cache_implementation':'dynamic','eos_token_ids':[151645,151643],'pad_token_id':151643}}


def test_evolution_exact_profile_has_coherent_parent_guardian_child_validation():
    config = task_config('evolution',4096,768,900)
    assert linux_candidate.validate_profile(config) == config
    source_module('linux_guardian').validate_reviewed_profile(config)
    source_module('qwen_backend').validate_runtime_profile(config)


def test_causal_exact_profile_keeps_its_shared_1200_second_budget():
    config = task_config('causal',4096,2048,1200)
    assert linux_candidate.validate_profile(config) == config
    source_module('linux_guardian').validate_reviewed_profile(config)
    source_module('qwen_backend').validate_runtime_profile(config)


def test_shared_deadline_supports_approved_1200_without_phase_or_setup_reset():
    import ast
    from types import SimpleNamespace
    path = Path(__file__).parents[1]/'bench/pinned-candidate/linux_guardian.py'
    tree = ast.parse(path.read_text())
    cls = next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='Guardian')
    initialize = next(node for node in cls.body if isinstance(node,ast.FunctionDef) and node.name=='__init__')
    policy = source_module('linux_guardian')
    namespace = {'os':SimpleNamespace(urandom=lambda count:b'x'*count),
        'time':SimpleNamespace(monotonic=lambda:1000.),'Wire':policy.Wire,
        'attempt_deadlines':policy.attempt_deadlines,'validate_reviewed_profile':policy.validate_reviewed_profile}
    future = ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,initialize],type_ignores=[])),str(path),'exec'),namespace)
    data = SimpleNamespace()
    namespace['__init__'](data,{'deadline_monotonic':2200.},{},
        {'config':task_config('causal',4096,2048,1200)},None)
    assert (data.work_deadline,data.deadline) == (2190.,2200.)
    namespace['__init__'](data,{'deadline_monotonic':1050.},{},
        {'config':task_config('causal',4096,2048,1200)},None)
    assert (data.work_deadline,data.deadline) == (1040.,1050.)


def test_gameplay_exact_profile_preserves_full_6144_input_and_8192_context():
    config = task_config('gameplay',6144,2048,1200)
    assert linux_candidate.validate_profile(config) == config
    source_module('linux_guardian').validate_reviewed_profile(config)
    source_module('qwen_backend').validate_runtime_profile(config)


def test_ethics_exact_profile_preserves_1024_output_and_900_shared_seconds():
    config = task_config('ethics',4096,1024,900)
    assert linux_candidate.validate_profile(config) == config
    source_module('linux_guardian').validate_reviewed_profile(config)
    source_module('qwen_backend').validate_runtime_profile(config)


TASKS = [('evolution',4096,768,900),('causal',4096,2048,1200),
         ('gameplay',6144,2048,1200),('ethics',4096,1024,900)]


def validators():
    return (linux_candidate.validate_profile,source_module('linux_guardian').validate_reviewed_profile,
            source_module('qwen_backend').validate_runtime_profile)


@pytest.mark.parametrize('task,input_cap,output_cap,seconds',TASKS)
def test_new_profile_refuses_mismatched_task_missing_or_malformed_contract_and_runtime_pin(task,input_cap,output_cap,seconds):
    config = task_config(task,input_cap,output_cap,seconds)
    for validate in validators():
        for invalid in (None,True,'','a'*63,'a'*65,'A'*64,'g'*64,{}):
            changed = dict(config,task_contract_digest=invalid)
            with pytest.raises(ValueError,match='task.*contract'):validate(changed)
        changed = dict(config);del changed['task_contract_digest']
        with pytest.raises(ValueError,match='task.*contract'):validate(changed)
        for task_value in ('signal','foreign',None,True):
            with pytest.raises(ValueError,match='task.*contract'):validate(dict(config,task=task_value))
        for pin in ('g'*64,'A'*64,'b'*63,None,True):
            changed = copy.deepcopy(config);changed['linux_profile']['runtime_manifest_sha256'] = pin
            with pytest.raises(ValueError):validate(changed)


@pytest.mark.parametrize('task,input_cap,output_cap,seconds',TASKS)
def test_new_profile_refuses_each_cap_change_unknown_alias_or_changed_decode(task,input_cap,output_cap,seconds):
    config = task_config(task,input_cap,output_cap,seconds)
    for validate in validators():
        for field in ('max_input_tokens','max_new_tokens','timeout_seconds','context_tokens',
                      'raw_output_max_bytes','threads','interop_threads'):
            for value in (config[field]+1,config[field]-1,True):
                with pytest.raises(ValueError):validate(dict(config,**{field:value}))
        for profile in ('unknown-linux-bf16-v1',task+'-linux-bf16-v2',task,'signal-linux-bf16-v1'):
            with pytest.raises(ValueError):validate(dict(config,profile=profile))
        for field,value in (('dtype','torch.float32'),('device','cuda'),('do_sample',True),
                            ('num_beams',2),('eos_token_ids',[151643]),('cache_implementation','static')):
            changed = copy.deepcopy(config);changed['linux_profile'][field] = value
            with pytest.raises(ValueError):validate(changed)


@pytest.mark.parametrize('task,input_cap,output_cap,seconds',TASKS)
def test_source_profile_never_supplies_missing_protected_operational_authority(task,input_cap,output_cap,seconds):
    import sys
    config = task_config(task,input_cap,output_cap,seconds)
    with pytest.raises(ValueError,match='protected host authority'):
        linux_candidate.invoke_pair({'input':{'TEST_ONLY':'input only'},'prompt_utf8':'TEST_ONLY prompt'},config)
    config['backend']['script'] = str(Path(__file__).parents[1]/'bench/pinned-candidate/qwen_backend.py')
    config['backend']['python'] = sys.executable
    with pytest.raises(ValueError,match='protected host authority'):
        linux_candidate.support_sources(config)


def test_setup_deadline_is_start_based_for_old_and_new_caps():
    import ast
    from types import SimpleNamespace
    path = Path(__file__).parents[1]/'bench/pinned-candidate/linux_guardian.py'
    tree = ast.parse(path.read_text())
    load = next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='load_host')
    assignments = [node for node in load.body if isinstance(node,ast.Assign)
        and any(isinstance(target,ast.Name) and target.id in ('setup_started','setup_deadline') for target in node.targets)]
    assert len(assignments) == 3
    for cap in (600,900,1200):
        for host_deadline,wanted in ((10000.,1000.+cap-10),(1050.,1040.)):
            namespace = {'time':SimpleNamespace(monotonic=lambda:1000.),'request':{'deadline_monotonic':host_deadline},
                'profile':{'config':{'timeout_seconds':cap}}}
            exec(compile(ast.Module(body=assignments,type_ignores=[]),str(path),'exec'),namespace)
            assert namespace['setup_deadline'] == wanted


@pytest.mark.parametrize('task,input_cap,output_cap,seconds',TASKS)
def test_paired_receipt_cannot_borrow_another_frozen_task_contract(task,input_cap,output_cap,seconds):
    import hashlib
    from twin.qualification import canonical
    config = task_config(task,input_cap,output_cap,seconds)
    request = {'input':{'TEST_ONLY':'no expected answer'},'prompt_utf8':'TEST_ONLY input-only prompt'}
    journal = linux_candidate.PairJournal(request,config,'5'*64)
    foreign = dict(config,task_contract_digest='b'*64)
    with pytest.raises(ValueError,match='lease/authority/profile'):
        journal.accept({'event':'lease','lease':'a'*48,'authority':'5'*64,
            'profile_sha256':hashlib.sha256(canonical(foreign)).hexdigest()})


def test_direct_child_checks_profile_before_any_network_or_runtime_import_or_input():
    import ast
    path = Path(__file__).parents[1]/'bench/pinned-candidate/qwen_backend.py'
    tree = ast.parse(path.read_text())
    main = next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='main')
    calls = [node for node in ast.walk(main) if isinstance(node,ast.Call)]
    profile = next(node for node in calls if isinstance(node.func,ast.Name) and node.func.id=='validate_runtime_profile')
    module_load = next(node for node in calls if isinstance(node.func,ast.Name) and node.func.id=='_module')
    input_read = next(node for node in calls if isinstance(node.func,ast.Attribute) and node.func.attr=='readline')
    assert profile.lineno < module_load.lineno and profile.lineno < input_read.lineno


def test_original_signal_and_substrate_configs_keep_exact_prior_caps_and_validation():
    for task,input_cap,output_cap,seconds in [('signal',4096,512,900),('substrate',4096,2048,600)]:
        config = task_config(task,input_cap,output_cap,seconds)
        del config['task'];del config['task_contract_digest']
        if task=='signal':
            del config['context_tokens'];del config['raw_output_max_bytes']
        assert linux_candidate.validate_profile(config) == config
        for validate in validators():validate(config)
