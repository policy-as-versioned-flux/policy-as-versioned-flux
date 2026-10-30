"""TEST_ONLY token callback controls: no torch/tokenizer/model is imported."""
import importlib.util
from pathlib import Path

import pytest


def backend():
    spec = importlib.util.spec_from_file_location('test_only_qwen_backend',
        Path(__file__).parents[1]/'bench/pinned-candidate/qwen_backend.py')
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IDs:
    def __init__(self, values): self.values = values
    def tolist(self): return self.values


class LiteralDecoder:
    def decode(self, ids, **kwargs):
        if 99 in ids: raise ValueError('TEST_ONLY external decoder failure')
        return 'TEST_ONLY actual token text' * len(ids)


def test_actual_id_is_journalled_before_external_decode_failure():
    frames = []
    journal = backend().TokenJournal(LiteralDecoder(), [1, 2], 2, frames.append)
    journal.put(IDs([[1, 2]]))
    with pytest.raises(ValueError, match='external decoder'):
        journal.put(IDs([99]))
    assert frames == [{'type': 'token', 'index': 0, 'id': 99}]
    assert journal.output_ids == [99] and not journal.ended


def test_actual_raw_snapshot_is_chunked_and_bounded_before_emission():
    class Decoder:
        def decode(self, ids, **kwargs): return 'A'*100000
    frames = []
    module = backend()
    journal = module.TokenJournal(Decoder(), [1], 2, frames.append, raw_maximum=131072)
    journal.put(IDs([[1]]))
    journal.put(IDs([151645]))
    journal.end()
    chunks = [frame for frame in frames if frame['type'] == 'raw']
    assert len(chunks) > 1
    assert chunks[0]['offset'] == 0 and chunks[-1]['total'] == 100000
    assert all(len(module.json.dumps(frame).encode()) < 65536 for frame in frames)
    assert journal.raw == b'A'*100000


def test_decode_overflow_retains_the_id_but_never_emits_a_truncated_answer():
    class Decoder:
        def decode(self, ids, **kwargs): return 'A'*32
    frames = []
    journal = backend().TokenJournal(Decoder(), [1], 2, frames.append, raw_maximum=16)
    journal.put(IDs([[1]]))
    with pytest.raises(ValueError, match='raw byte bound'):
        journal.put(IDs([151645]))
    assert journal.output_ids == [151645] and journal.raw == b''
    assert frames == [{'type': 'token', 'index': 0, 'id': 151645}]


def test_full_tokenization_binding_never_truncates_or_accepts_a_foreign_template():
    class Tokenizer:
        chat_template = 'TEST_ONLY frozen template'
        def apply_chat_template(self, messages, **kwargs):
            assert kwargs == {'tokenize': False, 'add_generation_prompt': True}
            return 'FULL '+messages[0]['content']
        def __call__(self, text, **kwargs):
            assert text == 'FULL TEST_ONLY full prompt'
            assert kwargs == {'add_special_tokens': False, 'truncation': False}
            return {'input_ids': list(range(8))}
    module = backend()
    import hashlib
    profile = {'max_input_tokens': 7, 'max_new_tokens': 2,
        'linux_profile': {'chat_template_sha256': hashlib.sha256(Tokenizer.chat_template.encode()).hexdigest()}}
    request = {'input': 'TEST_ONLY YAML', 'prompt_utf8': 'TEST_ONLY full prompt'}
    with pytest.raises(ValueError, match='full input.*bound'):
        module.token_binding(Tokenizer(), request, profile, {'max_position_embeddings': 100})
    profile['max_input_tokens'] = 8
    result = module.token_binding(Tokenizer(), request, profile, {'max_position_embeddings': 10})
    assert result['input_ids'] == list(range(8))
    with pytest.raises(ValueError, match='position capacity'):
        module.token_binding(Tokenizer(), request, profile, {'max_position_embeddings': 9})
    profile['linux_profile']['chat_template_sha256'] = '0'*64
    with pytest.raises(ValueError, match='chat template'):
        module.token_binding(Tokenizer(), request, profile, {'max_position_embeddings': 100})


def test_uncaged_process_refuses_before_any_runtime_import():
    module = backend()
    import sys
    if sys.platform == 'linux': pytest.skip('this source control is the Mac unsupported-target refusal')
    with pytest.raises(ValueError, match='native Linux'):
        module.check_bootstrap()
    assert 'torch' not in module.__dict__ and 'transformers' not in module.__dict__


def test_runtime_manifest_closure_rejects_changed_native_bytes(tmp_path):
    module = backend()
    library = tmp_path/'TEST_ONLY-native.so'
    library.write_bytes(b'TEST_ONLY native closure bytes')
    manifest = {'files': [{'path': str(library), 'bytes': 30,
        'sha256': module.sha(b'TEST_ONLY native closure bytes')}], 'site_packages': [str(tmp_path)]}
    assert len(b'TEST_ONLY native closure bytes') == 30
    assert module.verify_runtime_closure(manifest) == {str(library)}
    library.write_bytes(b'TEST_ONLY foreign native bytes')
    with pytest.raises(ValueError, match='runtime closure'):
        module.verify_runtime_closure(manifest)


def test_unmanifested_importable_code_refuses_before_runtime_path_is_enabled(tmp_path):
    module = backend()
    package = tmp_path/'TEST_ONLY_package.py'
    package.write_bytes(b'# TEST_ONLY acquired source')
    manifest = {'roots': [str(tmp_path)], 'files': [{'path': str(package),
        'bytes': package.stat().st_size, 'sha256': module.sha(package.read_bytes())}]}
    assert module.verify_runtime_closure(manifest) == {str(package)}
    (tmp_path/'torch.py').write_text('raise RuntimeError("TEST_ONLY unacquired import")')
    with pytest.raises(ValueError, match='unmanifested'):
        module.verify_runtime_closure(manifest)


def test_decode_failure_does_not_relabel_prior_raw_with_the_new_token_count():
    frames = []
    journal = backend().TokenJournal(LiteralDecoder(), [1], 3, frames.append)
    journal.put(IDs([[1]]))
    journal.put(IDs([7]))
    with pytest.raises(ValueError): journal.put(IDs([99]))
    journal.flush()
    chunks = [frame for frame in frames if frame['type'] == 'raw']
    assert chunks and {frame['count'] for frame in chunks} == {1}
    assert journal.output_ids == [7, 99]


def test_observation_checkpoint_requires_fixed_host_ack_before_continuation():
    import io
    frames = []
    module = backend()
    module.observation_checkpoint(frames.append, io.BytesIO(b'continue\n'), {'TEST_ONLY': 'actual maps'})
    assert frames == [{'type': 'observation', 'facts': {'TEST_ONLY': 'actual maps'}}]
    with pytest.raises(ValueError, match='guardian checkpoint'):
        module.observation_checkpoint(frames.append, io.BytesIO(b''), {'TEST_ONLY': 'actual maps'})
    with pytest.raises(ValueError, match='guardian checkpoint'):
        module.observation_checkpoint(frames.append, io.BytesIO(b'continue extra\n'), {})


def test_overlong_full_input_retains_actual_count_without_claiming_truncated_binding():
    module = backend()
    class Tokenizer:
        chat_template = 'TEST_ONLY template'
        def apply_chat_template(self, *args, **kwargs): return 'TEST_ONLY whole rendered input'
        def __call__(self, *args, **kwargs): return {'input_ids': list(range(9))}
    config = {'max_input_tokens':8,'max_new_tokens':2,
        'linux_profile':{'chat_template_sha256':module.sha(Tokenizer.chat_template.encode())}}
    request = {'input':'TEST_ONLY full input','prompt_utf8':'TEST_ONLY full prompt'}
    with pytest.raises(module.InputAdmissionError) as error:
        module.token_binding(Tokenizer(),request,config,{'max_position_embeddings':100})
    assert error.value.facts['full_input_tokens'] == 9
    assert error.value.facts['max_input_tokens'] == 8
    assert error.value.facts['truncated'] is False


def synthetic_bootstrap(set_result=0, sticky_dumpable=False):
    """Compile only the bootstrap decision, replacing every OS/ctypes boundary."""
    import ast
    import hashlib
    from types import SimpleNamespace
    path = Path(__file__).parents[1]/'bench/pinned-candidate/qwen_backend.py'
    tree = ast.parse(path.read_text())
    check = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'check_bootstrap')
    check.body = [node for node in check.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
    operations = []
    dumpable = [1]  # Linux ordinary exec resets the earlier bootstrap setting.
    status = '\n'.join([*(key+': 00000000' for key in ('CapEff','CapPrm','CapInh','CapAmb','CapBnd')),
        'NoNewPrivs: 1','Seccomp: 2'])
    mounts = ('1 0 0:1 / / ro,nosuid,nodev - tmpfs tmpfs ro\n'
        '2 1 0:2 / /proc ro,nosuid,nodev,noexec - proc proc ro\n'
        '3 1 0:3 / /attempt rw,nosuid,nodev,noexec - tmpfs tmpfs rw,size=131072k\n')
    class FakePath:
        def __init__(self, name): self.name = name
        def read_text(self): return {'/proc/self/status':status,'/proc/self/mountinfo':mounts}[self.name]
        def read_bytes(self): return self.read_text().encode()
        def iterdir(self):
            assert self.name == '/proc/self/task'
            return iter(['TEST_ONLY-one-thread'])
    class Integer:
        value = 0
    class LibC:
        def prctl(self, operation, argument, *unused):
            operations.append(operation)
            if operation == 4:
                assert argument == 0
                if not set_result and not sticky_dumpable: dumpable[0] = 0
                return set_result
            if operation == 3: return dumpable[0]
            if operation == 2:
                argument.value = 9
                return 0
            raise AssertionError('unexpected kernel request')
    namespace = {'Any':object,'Path':FakePath,
        'protected_json':lambda _: {'candidate_uid':65534,'candidate_gid':65534},
        'sha':lambda raw: hashlib.sha256(raw).hexdigest(),
        'os':SimpleNamespace(getresuid=lambda: (65534,)*3,getresgid=lambda: (65534,)*3,
            getgroups=lambda: [],getpid=lambda: 1,readlink=lambda path: 'TEST_ONLY-private-'+path),
        'platform':SimpleNamespace(machine=lambda: 'x86_64'),
        'sys':SimpleNamespace(platform='linux',byteorder='little',
            flags=SimpleNamespace(isolated=True,no_site=True),dont_write_bytecode=True),
        'signal':SimpleNamespace(SIGKILL=9),
        'ctypes':SimpleNamespace(sizeof=lambda _: 8,c_void_p=object,CDLL=lambda *a,**k: LibC(),
            c_int=Integer,byref=lambda value: value)}
    exec(compile(ast.Module(body=[check],type_ignores=[]),str(path),'exec'),namespace)
    return namespace['check_bootstrap'], operations


def test_post_exec_bootstrap_restores_and_reads_nondumpability_before_ready():
    check, operations = synthetic_bootstrap()
    result = check()
    assert operations[:2] == [4,3]
    assert result['observed']['dumpable'] == 0


@pytest.mark.parametrize('set_result,sticky', [(-1,False),(0,True)])
def test_post_exec_dumpability_reset_or_readback_failure_refuses(set_result, sticky):
    check, _ = synthetic_bootstrap(set_result, sticky)
    with pytest.raises(ValueError, match='post-exec.*nondumpability'):
        check()
