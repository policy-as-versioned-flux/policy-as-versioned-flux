"""Concrete offline Qwen child. Import is inert; main requires a real protected Linux lease.

No acquisition, provider, model registration or permission is supplied by this program.
Third-party runtime imports occur only inside the caged execution function.
"""
from __future__ import annotations

import base64
import json
from typing import Any, Callable


class TokenJournal:
    """Synchronous actual token IDs, with the initial prompt batch treated separately."""
    def __init__(self, tokenizer: Any, input_ids: list[int], maximum: int,
                 emit: Callable[[dict[str, Any]], None], raw_maximum: int = 131072):
        self.tokenizer, self.input_ids, self.maximum, self.emit = tokenizer, input_ids, maximum, emit
        self.output_ids: list[int] = []
        self.raw = b''
        self.prompt_seen = False
        self.ended = False
        self.raw_maximum = raw_maximum
        self.raw_count = 0
        self.decoded_count = 0

    def put(self, value: Any) -> None:
        ids = value.tolist()
        if not self.prompt_seen:
            if ids != [self.input_ids]:
                raise ValueError('actual generated prompt IDs differ from preflight')
            self.prompt_seen = True
            return
        if (self.ended or not isinstance(ids, list) or len(ids) != 1
                or type(ids[0]) is not int or ids[0] < 0 or len(self.output_ids) >= self.maximum):
            raise ValueError('bounded single-sequence next token required')
        self.output_ids.append(ids[0])
        # Persist the actual ID before decode: decode failure cannot erase a completed step.
        self.emit({'type': 'token', 'index': len(self.output_ids)-1, 'id': ids[0]})
        raw = self.tokenizer.decode(self.output_ids, skip_special_tokens=False,
                                    clean_up_tokenization_spaces=False).encode('utf-8')
        if len(raw) > self.raw_maximum:
            raise ValueError('actual decoded output exceeds frozen raw byte bound')
        self.raw = raw
        self.decoded_count = len(self.output_ids)
        if len(self.output_ids) % 64 == 0 or ids[0] in (151645, 151643):
            self.flush()

    def flush(self) -> None:
        if self.raw_count == self.decoded_count:
            return
        for offset in range(0, max(1, len(self.raw)), 32768):
            self.emit({'type': 'raw', 'count': self.decoded_count, 'offset': offset,
                'total': len(self.raw),
                'raw_base64': base64.b64encode(self.raw[offset:offset+32768]).decode()})
        self.raw_count = self.decoded_count

    def end(self) -> None:
        if not self.prompt_seen or self.ended or self.decoded_count != len(self.output_ids):
            raise ValueError('generation end lacks its actual initial prompt')
        self.flush()
        self.ended = True
        self.emit({'type': 'end'})


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def sha(raw: bytes) -> str:
    import hashlib
    return hashlib.sha256(raw).hexdigest()


class InputAdmissionError(ValueError):
    """Actual full-token admission facts, retained even when no generation is allowed."""
    def __init__(self, reason: str, facts: dict[str, Any]):
        super().__init__(reason)
        self.facts = facts


def token_binding(tokenizer: Any, request: dict[str, Any], config: dict[str, Any],
                  model_config: dict[str, Any]) -> dict[str, Any]:
    """Full actual tokenizer input, without padding, truncation or reference-derived repair."""
    if sha(tokenizer.chat_template.encode()) != config['linux_profile']['chat_template_sha256']:
        raise ValueError('pinned chat template changed')
    rendered = tokenizer.apply_chat_template([{'role': 'user', 'content': request['prompt_utf8']}],
        tokenize=False, add_generation_prompt=True)
    ids = tokenizer(rendered, add_special_tokens=False, truncation=False)['input_ids']
    if not isinstance(ids, list) or not ids or any(type(item) is not int or item < 0 for item in ids):
        raise ValueError('actual tokenizer did not return nonempty genuine token IDs')
    facts = {'full_input_tokens':len(ids), 'max_input_tokens':config['max_input_tokens'],
        'max_new_tokens':config['max_new_tokens'], 'truncated':False,
        'input_sha256':sha(canonical(request['input'])), 'prompt_sha256':sha(request['prompt_utf8'].encode()),
        'rendered_chat_sha256':sha(rendered.encode()), 'input_ids_sha256':sha(canonical(ids)),
        'model_position_capacity':model_config.get('max_position_embeddings')}
    if len(ids) > config['max_input_tokens']:
        raise InputAdmissionError('full input exceeds frozen token bound; no truncation or generation',facts)
    capacity = model_config.get('max_position_embeddings')
    if (type(capacity) is not int or len(ids)+config['max_new_tokens'] > capacity
            or config.get('context_tokens', 0) > capacity):
        raise InputAdmissionError('actual pinned model position capacity does not support this profile/input',facts)
    return {'input_sha256': sha(canonical(request['input'])),
        'prompt_sha256': sha(request['prompt_utf8'].encode()), 'rendered_chat_sha256': sha(rendered.encode()),
        'input_ids': ids, 'input_ids_sha256': sha(canonical(ids))}


def protected_json(path: str, maximum: int = 1024**2) -> dict[str, Any]:
    """Require an immutable root-owned jail member; this is not a substitute for host authority."""
    import os
    import stat
    from pathlib import Path
    target = Path(path)
    for member in (target, *target.parents):
        item = member.lstat()
        if stat.S_ISLNK(item.st_mode) or item.st_uid != 0 or item.st_mode & 0o022:
            raise ValueError('mutable/foreign bootstrap closure member')
    descriptor = os.open(target, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        item = os.fstat(descriptor)
        if not stat.S_ISREG(item.st_mode) or item.st_uid != 0 or item.st_mode & 0o022:
            raise ValueError('bootstrap member changed during acquisition')
        with os.fdopen(descriptor, 'rb', closefd=False) as stream:
            raw = stream.read(maximum+1)
        if len(raw) > maximum:
            raise ValueError('bootstrap JSON exceeds bound')
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError('bootstrap object required')
        return value
    finally:
        os.close(descriptor)


def check_bootstrap() -> dict[str, Any]:
    """Check actual child kernel state before installing network denial/runtime imports.

    The separate root guardian must independently attest these facts and protect the
    immutable jail. Running this child directly supplies no lease authority to a judge.
    """
    import ctypes
    import os
    import platform
    import signal
    import sys
    from pathlib import Path
    if (sys.platform != 'linux' or sys.byteorder != 'little' or ctypes.sizeof(ctypes.c_void_p) != 8
            or platform.machine() not in ('x86_64', 'aarch64')):
        raise ValueError('requires a native Linux64 little-endian protected child')
    lease = protected_json('/app/lease.json')
    state = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    state = {key: value.strip() for key, value in state.items()}
    uid, gid = lease.get('candidate_uid'), lease.get('candidate_gid')
    if (type(uid) is not int or uid <= 0 or type(gid) is not int or gid <= 0
            or os.getresuid() != (uid, uid, uid) or os.getresgid() != (gid, gid, gid)
            or os.getgroups() or os.getpid() != 1
            or any(int(state[key], 16) for key in ('CapEff', 'CapPrm', 'CapInh', 'CapAmb', 'CapBnd'))
            or state['NoNewPrivs'] != '1' or state['Seccomp'] != '2'
            or len(list(Path('/proc/self/task').iterdir())) != 1
            or not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode):
        raise ValueError('actual dedicated namespace/drop/capability/bootstrap state differs')
    libc = ctypes.CDLL(None, use_errno=True)
    death = ctypes.c_int()
    if libc.prctl(2, ctypes.byref(death), 0, 0, 0) or death.value != signal.SIGKILL:
        raise ValueError('actual guardian death protection missing')
    mounts = [line.split() for line in Path('/proc/self/mountinfo').read_text().splitlines()]
    writable = [row for row in mounts if 'rw' in row[5].split(',')]
    if (len(writable) != 1 or writable[0][4] != '/attempt'
            or not {'nosuid', 'nodev', 'noexec'} <= set(writable[0][5].split(','))
            or not any(row[4] == '/proc' and 'ro' in row[5].split(',') for row in mounts)
            or not any(row[4] == '/' and 'ro' in row[5].split(',') for row in mounts)):
        raise ValueError('actual minimal root/proc/attempt mount confinement differs')
    if any('cgroup' in row for row in mounts):
        raise ValueError('candidate must have no cgroup filesystem mount')
    lease['observed'] = {'uids': list(os.getresuid()), 'gids': list(os.getresgid()),
        'pid': os.getpid(), 'state': {key: state[key] for key in
            ('CapEff', 'CapPrm', 'CapInh', 'CapAmb', 'CapBnd', 'NoNewPrivs', 'Seccomp')},
        'mountinfo_sha256': sha(Path('/proc/self/mountinfo').read_bytes()),
        'pid_namespace': os.readlink('/proc/self/ns/pid'),
        'mount_namespace': os.readlink('/proc/self/ns/mnt'), 'parent_death_signal': death.value}
    return lease


def verify_runtime_closure(manifest: dict[str, Any]) -> set[str]:
    """Rehash acquired files; hashes bind bytes, and never grant host/acquisition authority."""
    import hashlib
    from pathlib import Path
    files = manifest.get('files')
    if not isinstance(files, list) or not files:
        raise ValueError('complete acquired runtime closure required')
    verified: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {'path', 'bytes', 'sha256'}:
            raise ValueError('runtime closure member schema differs')
        path = Path(entry['path'])
        if (not path.is_absolute() or path.is_symlink() or path.resolve() != path or not path.is_file()
                or str(path) in verified or type(entry['bytes']) is not int or entry['bytes'] < 0):
            raise ValueError('runtime closure requires distinct absolute regular acquired files')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            while chunk := stream.read(4*1024**2): digest.update(chunk)
        if path.stat().st_size != entry['bytes'] or digest.hexdigest() != entry['sha256']:
            raise ValueError('actual runtime closure bytes changed: '+str(path))
        verified.add(str(path))
    if 'roots' in manifest:
        roots = manifest['roots']
        if (not isinstance(roots, list) or not roots
                or any(not isinstance(root, str) or not Path(root).is_absolute()
                    or Path(root).resolve() != Path(root) or not Path(root).is_dir() for root in roots)):
            raise ValueError('runtime closure roots must be absolute immutable acquired directories')
        found: set[str] = set()
        for root in roots:
            for path in Path(root).rglob('*'):
                if path.is_symlink():
                    raise ValueError('unmanifested runtime symlink/alias')
                if path.is_file(): found.add(str(path))
        if found != verified:
            raise ValueError('unmanifested or missing code in acquired runtime closure')
    return verified


def file_sha(path: str) -> str:
    import hashlib
    from pathlib import Path
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while chunk := stream.read(4*1024**2): digest.update(chunk)
    return digest.hexdigest()


def _module(path: str, name: str) -> Any:
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('pinned support module unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mapped_files(allowed: set[str]) -> list[dict[str, str]]:
    """Identify actual mapped file bytes, including native dependencies, after eager loading."""
    import sys
    from pathlib import Path
    mapped: set[str] = set()
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) == 6 and fields[5].startswith('/'):
            path = fields[5]
            if path not in allowed or Path(path).resolve() != Path(path):
                raise ValueError('unacquired actual native/model mapping: '+path)
            mapped.add(path)
    for module in tuple(sys.modules.values()):
        origin = getattr(module, '__file__', None)
        if origin and origin not in allowed:
            raise ValueError('unacquired imported runtime source: '+str(origin))
    return [{'path': path, 'sha256': file_sha(path)} for path in sorted(mapped)]


def _runtime(torch: Any, model: Any, tokenizer: Any, config: dict[str, Any],
             paths: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    import importlib.metadata
    import os
    import platform
    import sys
    from pathlib import Path
    dtypes = sorted({str(item.dtype) for item in model.parameters()})
    devices = sorted({str(item.device) for item in model.parameters()})
    if (dtypes != ['torch.bfloat16'] or devices != ['cpu'] or torch.get_num_threads() != 2
            or torch.get_num_interop_threads() != 1
            or getattr(model.config, '_attn_implementation', None) != 'eager'):
        raise ValueError('actual loaded actor differs: no dtype/device/attention/thread fallback')
    cpu = Path('/proc/cpuinfo').read_text()
    features = sorted({flag for line in cpu.splitlines()
        if line.split(':', 1)[0].strip() in ('flags', 'Features')
        for flag in line.split(':', 1)[1].split()})
    return {'model_id': config['linux_profile']['model_id'],
        'revision': config['linux_profile']['revision'],
        'model_manifest_sha256': sha(Path(paths['model_manifest']).read_bytes()),
        'runtime_manifest_sha256': sha(Path(paths['runtime_manifest']).read_bytes()),
        'chat_template_sha256': sha(tokenizer.chat_template.encode()),
        'python': sys.version, 'python_executable_sha256': sha(Path('/proc/self/exe').read_bytes()),
        'packages': {name: importlib.metadata.version(name)
            for name in ('torch', 'transformers', 'tokenizers', 'safetensors', 'numpy')},
        'torch_version': str(torch.__version__), 'torch_git_version': torch.version.git_version,
        'torch_build': torch.__config__.show(), 'machine': platform.machine(), 'cpu_isa': features,
        'libc': list(platform.libc_ver()), 'parameter_dtypes': dtypes, 'parameter_devices': devices,
        'buffer_dtypes': sorted({str(item.dtype) for item in model.buffers()}),
        'buffer_devices': sorted({str(item.device) for item in model.buffers()}),
        'threads': torch.get_num_threads(), 'interop_threads': torch.get_num_interop_threads(),
        'attention': model.config._attn_implementation, 'native_mappings': _mapped_files(allowed),
        'cpu_affinity': sorted(getattr(os, 'sched_getaffinity')(0))}


def observation_checkpoint(emit: Callable[[dict[str, Any]], None], reader: Any,
                           facts: dict[str, Any]) -> None:
    """Keep this exact child alive while the guardian acquires independent proc evidence."""
    emit({'type': 'observation', 'facts': facts})
    if reader.readline(10) != b'continue\n':
        raise ValueError('protected guardian checkpoint acknowledgement missing/malformed')


def main() -> int:
    """Fixed caged entry. Guardian supplies protected files and releases stdin only after READY."""
    import os
    import sys
    from pathlib import Path
    total = 0
    def emit(value: dict[str, Any]) -> None:
        nonlocal total
        raw = canonical(value)+b'\n'
        total += len(raw)
        if len(raw) > 65536 or total > 8*1024**2:
            raise ValueError('actual child journal exceeds frozen byte bound')
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
    journal: TokenJournal | None = None
    try:
        lease = check_bootstrap()
        if len(sys.argv) != 2 or sys.argv[1] not in ('--preflight', '--generate'):
            raise ValueError('fixed preflight/generate child entry only')
        phase = sys.argv[1][2:]
        config, paths = protected_json('/app/actor-config.json'), protected_json('/app/paths.json')
        if lease.get('phase') != phase or sha(canonical(config)) != lease.get('profile_sha256'):
            raise ValueError('protected phase/config lease binding differs')
        required_paths = {'assets', 'model_manifest', 'runtime_manifest', 'network_module',
                          'smoke_module', 'site_packages', 'support_sources'}
        if set(paths) != required_paths or not isinstance(paths['support_sources'], dict):
            raise ValueError('protected jail path/closure schema differs')
        support = paths['support_sources']
        for path, pin in support.items():
            target = Path(path)
            for member in (target, *target.parents):
                item = member.lstat()
                if item.st_uid != 0 or item.st_mode & 0o022 or member.is_symlink():
                    raise ValueError('support source is mutable to candidate')
            if sha(target.read_bytes()) != pin:
                raise ValueError('pinned support source changed')
        if (str(Path(__file__)) not in support or paths['network_module'] not in support
                or paths['smoke_module'] not in support
                or sha(Path(__file__).read_bytes()) != config['backend']['sha256']):
            raise ValueError('whole backend/support source binding missing')
        network = _module(paths['network_module'], 'pinned_linux_network')
        installed = network.install_network_denial()
        before = network.observe_network_denial()
        for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                    'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
            if os.environ.get(key) != '2': raise ValueError('explicit two-thread environment required')
        expected_env = {'TOKENIZERS_PARALLELISM': 'false', 'HF_HUB_OFFLINE': '1',
            'TRANSFORMERS_OFFLINE': '1', 'HF_DATASETS_OFFLINE': '1',
            'HOME': '/attempt/home', 'TMPDIR': '/attempt/tmp', 'HF_HOME': '/attempt/cache'}
        if any(os.environ.get(key) != value for key, value in expected_env.items()):
            raise ValueError('clean offline attempt environment differs')
        emit({'type': 'ready', 'facts': lease['observed'], 'network': {'install': installed, 'before': before}})
        # The guardian independently verifies the actual READY credentials/kernel state
        # before forwarding this one input-only request. No expected answer is supplied.
        raw_request = sys.stdin.buffer.readline(1024**2+1)
        if len(raw_request) > 1024**2 or not raw_request.endswith(b'\n'):
            raise ValueError('input/control frame exceeds frozen bound')
        request = json.loads(raw_request)
        if (not isinstance(request, dict) or set(request) != {'input', 'prompt_utf8'}
                or not isinstance(request['input'], (dict, str)) or not isinstance(request['prompt_utf8'], str)):
            raise ValueError('exact input-only child request required')
        if sha(Path(paths['model_manifest']).read_bytes()) != config['linux_profile']['model_manifest_sha256']:
            raise ValueError('original model manifest binding differs')
        if sha(Path(paths['runtime_manifest']).read_bytes()) != config['linux_profile']['runtime_manifest_sha256']:
            raise ValueError('actual acquired runtime manifest binding differs')
        runtime_manifest = protected_json(paths['runtime_manifest'], 16*1024**2)
        if not runtime_manifest.get('roots'):
            raise ValueError('complete runtime/stdlib/native closure roots required before imports')
        allowed = verify_runtime_closure(runtime_manifest)
        if sha(Path('/proc/self/exe').read_bytes()) != config['backend']['python_sha256']:
            raise ValueError('actual pinned isolated Python differs')
        smoke = _module(paths['smoke_module'], 'pinned_historical_asset_verifier')
        model_manifest = protected_json(paths['model_manifest'])
        smoke.verify_assets(Path(paths['assets']), model_manifest)
        allowed |= {str(Path(paths['assets'])/item['path']) for item in model_manifest['files']}
        allowed |= set(support)
        if (paths['site_packages'] != runtime_manifest.get('site_packages')
                or not isinstance(paths['site_packages'], list)
                or any(not any(Path(root) == Path(path) or Path(root) in Path(path).parents
                    for root in runtime_manifest['roots']) for path in paths['site_packages'])):
            raise ValueError('site-packages outside acquired immutable closure')
        # -I -S prevents user sites, environment paths and .pth startup hooks. Enabling
        # only already-rehashed directories does not execute .pth or sitecustomize.
        for path in sys.path:
            if Path(path).exists() and not any(Path(root) == Path(path) or Path(root) in Path(path).parents
                                               for root in runtime_manifest['roots']):
                raise ValueError('interpreter search path outside acquired closure')
        sys.path.extend(paths['site_packages'])
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(paths['assets'], local_files_only=True, trust_remote_code=False)
        model_config = protected_json(str(Path(paths['assets'])/'config.json'))
        binding = token_binding(tokenizer, request, config, model_config)
        emit({'type': 'preflight' if phase == 'preflight' else 'input', 'binding': binding})
        if phase == 'preflight':
            observation_checkpoint(emit, sys.stdin.buffer, {'network_after_tokenizer': network.observe_network_denial(),
                'actual_runtime_mappings': _mapped_files(allowed)})
            return 0
        import torch
        from transformers import AutoModelForCausalLM, GenerationConfig
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        torch.manual_seed(0)
        with torch.device('cpu'):
            model = AutoModelForCausalLM.from_pretrained(paths['assets'], local_files_only=True,
                trust_remote_code=False, use_safetensors=True, torch_dtype=torch.bfloat16,
                device_map=None, low_cpu_mem_usage=True, attn_implementation='eager')
        model.eval()
        observed = _runtime(torch, model, tokenizer, config, paths, allowed)
        observation_checkpoint(emit, sys.stdin.buffer, {'loaded_runtime': observed,
            'network_before_generation': network.observe_network_denial()})
        ids = binding['input_ids']
        encoded = torch.tensor([ids], dtype=torch.long, device='cpu')
        journal = TokenJournal(tokenizer, ids, config['max_new_tokens'], emit,
                               config.get('raw_output_max_bytes', 131072))
        generation = GenerationConfig(max_new_tokens=config['max_new_tokens'], do_sample=False,
            num_beams=1, num_return_sequences=1, use_cache=True, cache_implementation='dynamic',
            eos_token_id=config['linux_profile']['eos_token_ids'],
            pad_token_id=config['linux_profile']['pad_token_id'])
        with torch.inference_mode():
            generated = model.generate(input_ids=encoded, attention_mask=torch.ones_like(encoded),
                generation_config=generation, streamer=journal)
        output = generated[0, len(ids):].tolist()
        if not journal.ended or output != journal.output_ids:
            raise ValueError('actual generation tensor/callback/end disagree')
        if not output or output[-1] not in config['linux_profile']['eos_token_ids']:
            raise ValueError('actual generation stopped at bound without EOS')
        observed = _runtime(torch, model, tokenizer, config, paths, allowed)
        observation_checkpoint(emit, sys.stdin.buffer, {'network_after_runtime': network.observe_network_denial()})
        if canonical(observed) != canonical(config['runtime_contract']):
            raise ValueError('actual loaded Linux runtime differs from frozen actor')
        emit({'type': 'complete', 'output_ids': output, 'raw_sha256': sha(journal.raw),
              'stop_reason': 'eos', 'observed_runtime': observed})
        return 0
    except Exception as exc:
        if isinstance(exc, InputAdmissionError):
            try: observation_checkpoint(emit,sys.stdin.buffer,{'input_admission':exc.facts})
            except Exception: pass
        if journal is not None:
            # Flush only successfully decoded actual prefixes. An ID whose decode
            # failed remains in token events, never paired with invented text.
            try: journal.flush()
            except Exception: pass
        try: emit({'type': 'failure', 'error': type(exc).__name__+': '+str(exc)[:2000]})
        except Exception: pass
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
