"""Paired Linux host invocation. Importing this module starts no helper or model.

Authority is acquired from the protected judge catalogue and an OS-protected host anchor,
never from actor config, candidate input, model output or a root-looking pathname.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .qualification import RuntimeResult, canonical

HOST_ANCHOR = Path('/run/policy-as-versioned-flux-candidate/host.json')
PROFILES = {
    'signal-linux-bf16-v1': {'max_input_tokens': 4096, 'max_new_tokens': 512,
        'timeout_seconds': 900, 'threads': 2, 'interop_threads': 1},
    'substrate-linux-bf16-v1': {'max_input_tokens': 4096, 'max_new_tokens': 2048,
        'timeout_seconds': 600, 'context_tokens': 8192, 'raw_output_max_bytes': 131072,
        'threads': 2, 'interop_threads': 1},
}
MODEL = 'Qwen/Qwen3-4B-Instruct-2507'
REVISION = 'cdbee75f17c01a7cc42f958dc650907174af0554'


def validate_profile(config: dict[str, Any]) -> dict[str, Any]:
    """Pure validation of the reviewed actor, never acquisition or execution authority."""
    expected = {'model_id': MODEL, 'revision': REVISION,
        'model_manifest_sha256': '409410d7d41d7e62aafb27c18f049fe3c62d66383b3a5b89d5fadfd3b773fd7e',
        'chat_template_sha256': '64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326',
        'dtype': 'torch.bfloat16', 'device': 'cpu', 'attention': 'eager',
        'do_sample': False, 'num_beams': 1, 'num_return_sequences': 1, 'seed': 0,
        'use_cache': True, 'cache_implementation': 'dynamic',
        'eos_token_ids': [151645, 151643], 'pad_token_id': 151643}
    if not isinstance(config, dict) or not isinstance(config.get('profile'), str):
        raise ValueError('explicit reviewed Linux profile identity required')
    value = json.loads(canonical(config))
    limits = PROFILES.get(value['profile'], {})
    declared = value.get('linux_profile')
    if (not limits or not isinstance(declared, dict)
            or any(key in value for key in {'context_tokens', 'raw_output_max_bytes'} - set(limits))
            or set(declared) != set(expected) | {'runtime_manifest_sha256'}
            or any(canonical(declared[key]) != canonical(wanted) for key, wanted in expected.items())
            or any(type(value.get(key)) is not int or value[key] != wanted for key, wanted in limits.items())
            or not isinstance(value.get('runtime_contract'), dict) or not value['runtime_contract']):
        raise ValueError('config differs from the reviewed Linux profile; a new profile needs separate review')
    pin = declared['runtime_manifest_sha256']
    backend = value.get('backend')
    if (not isinstance(pin, str) or len(pin) != 64 or any(c not in '0123456789abcdef' for c in pin)
            or not isinstance(backend, dict) or set(backend) != {'script', 'sha256', 'python', 'python_sha256'}
            or any(not isinstance(backend[key], str) or not Path(backend[key]).is_absolute()
                   for key in ('script', 'python'))
            or any(not isinstance(backend[key], str) or len(backend[key]) != 64
                   or any(c not in '0123456789abcdef' for c in backend[key])
                   for key in ('sha256', 'python_sha256'))):
        raise ValueError('reviewed Linux profile needs complete pinned backend/runtime identities')
    return value


class PairJournal:
    """Verify ordered host-guardian evidence; this pure reader does not authenticate a host.

    Only invoke_pair supplies bytes acquired from the independently protected guardian.
    TEST_ONLY packets at this interface prove protocol mechanics, never OS/model authority.
    """
    def __init__(self, request: dict[str, Any], config: dict[str, Any], authority_digest: str):
        if (not isinstance(request, dict) or set(request) != {'input', 'prompt_utf8'}
                or not isinstance(request['input'], (dict, str))
                or not isinstance(request['prompt_utf8'], str)):
            raise ValueError('exact input-only paired request required')
        self.request = json.loads(canonical(request))
        self.config = validate_profile(config)
        self.authority = authority_digest
        self.lease: str | None = None
        self.phase: str | None = None
        self.identities: list[list[Any]] = []
        self.ended: list[str] = []
        self.binding: dict[str, Any] | None = None
        self.generation_binding = False
        self.output_ids: list[int] = []
        self.raw = b''
        self.raw_count = 0
        self.raw_total = 0
        self.raw_pending = False
        self.runtime: dict[str, Any] = {}
        self.stream_end = False
        self.complete = False
        self.done = False
        self.frames: list[dict[str, Any]] = []
        self.child_observations: list[dict[str, Any]] = []
        self.failure: str | None = None
        self.teardown = False
        self.bytes = 0

    def accept(self, packet: dict[str, Any]) -> None:
        encoded = canonical(packet)
        self.bytes += len(encoded) + 1
        if self.bytes > 8*1024**2 or len(encoded) > 65536 or self.done:
            raise ValueError('paired journal exceeds its frozen bound or terminal state')
        if not isinstance(packet, dict):
            raise ValueError('guardian event must be an object')
        kind = packet.get('event')
        if self.lease is None:
            lease = packet.get('lease')
            if (kind != 'lease' or not isinstance(lease, str) or len(lease) != 48
                    or any(c not in '0123456789abcdef' for c in lease)
                    or packet.get('authority') != self.authority
                    or packet.get('profile_sha256') != hashlib.sha256(canonical(self.config)).hexdigest()):
                raise ValueError('guardian lease/authority/profile binding differs')
            self.lease = lease
        elif packet.get('lease') != self.lease:
            raise ValueError('paired phases cannot change their guardian lease')
        elif kind in ('proof', 'resources'):
            if packet.get('phase') != self.phase or not isinstance(packet.get('facts'), dict):
                raise ValueError('host proof/resource facts have no matching phase')
        elif kind == 'failure':
            if not isinstance(packet.get('error'), str) or not packet['error']:
                raise ValueError('host failure requires its actual reason')
            self.failure = self.failure or packet['error']
        elif kind == 'phase_start':
            wanted = 'preflight' if not self.ended else 'generate'
            identity = [packet.get('pid'), packet.get('start')]
            if (self.failure or self.phase or len(self.ended) >= 2 or packet.get('phase') != wanted
                    or type(identity[0]) is not int or identity[0] <= 0
                    or not isinstance(identity[1], str) or not identity[1]
                    or identity in self.identities):
                raise ValueError('fresh ordered phase identity required after prior empty/reaped phase')
            self.phase = wanted
            self.identities.append(identity)
        elif kind == 'frame':
            if self.phase is None or packet.get('phase') != self.phase:
                raise ValueError('child frame has no active matching phase')
            body = packet['body']
            if not isinstance(body, dict):
                raise ValueError('child protocol object required')
            self._child(body)
        elif kind == 'phase_end':
            if (self.phase is None or packet.get('phase') != self.phase or type(packet.get('returncode')) is not int
                    or not self.failure and packet['returncode'] != 0
                    or packet.get('empty') is not True or packet.get('reaped') is not True
                    or not self.failure and self.phase == 'preflight' and self.binding is None
                    or not self.failure and self.phase == 'generate' and not self.complete):
                raise ValueError('phase failed or lacks verified empty/reaped complete evidence')
            self.ended.append(self.phase)
            self.phase = None
        elif kind in ('done', 'aborted'):
            if (self.phase or kind == 'done' and self.ended != ['preflight', 'generate']
                    or kind == 'aborted' and not self.failure
                    or any(packet.get(key) is not True for key in ('empty', 'reaped', 'removed'))):
                raise ValueError('paired completion lacks verified final teardown')
            self.done = True
            self.teardown = True
        else:
            raise ValueError('unexpected guardian event')
        self.frames.append(json.loads(encoded))

    def _child(self, body: dict[str, Any]) -> None:
        kind = body.get('type')
        if self.failure:
            raise ValueError('child frame after terminal failure')
        if kind in ('ready', 'observation'):
            if not isinstance(body.get('facts'), dict):
                raise ValueError('actual child observation object required')
            self.child_observations.append(json.loads(canonical(body['facts'])))
        elif kind == 'failure':
            if not isinstance(body.get('error'), str) or not body['error']:
                raise ValueError('actual child failure reason required')
            self.failure = body['error']
        elif kind in ('preflight', 'input'):
            if ((self.phase == 'preflight') != (kind == 'preflight')
                    or self.phase == 'preflight' and self.binding is not None
                    or self.phase == 'generate' and (self.generation_binding or self.output_ids or self.stream_end)):
                raise ValueError('unexpected tokenizer binding position')
            binding = body.get('binding')
            if not isinstance(binding, dict):
                raise ValueError('actual tokenizer binding object required')
            ids = binding.get('input_ids')
            if (not isinstance(ids, list) or not 0 < len(ids) <= self.config['max_input_tokens']
                    or any(type(item) is not int or item < 0 for item in ids)
                    or binding.get('input_ids_sha256') != hashlib.sha256(canonical(ids)).hexdigest()
                    or binding.get('input_sha256') != hashlib.sha256(canonical(self.request['input'])).hexdigest()
                    or binding.get('prompt_sha256') != hashlib.sha256(self.request['prompt_utf8'].encode()).hexdigest()
                    or not isinstance(binding.get('rendered_chat_sha256'), str)):
                raise ValueError('actual input/prompt/token-ID binding differs')
            if self.phase == 'preflight':
                self.binding = json.loads(canonical(binding))
            elif binding != self.binding:
                raise ValueError('generation tokenization differs from exact preflight')
            else:
                self.generation_binding = True
        elif kind == 'token':
            if self.phase == 'generate' and not self.generation_binding:
                raise ValueError('generation must retain its actual tokenizer binding')
            if (self.phase != 'generate' or self.binding is None or self.stream_end
                    or type(body.get('index')) is not int or body['index'] != len(self.output_ids) or type(body.get('id')) is not int
                    or body['id'] < 0 or len(self.output_ids) >= self.config['max_new_tokens']):
                raise ValueError('bounded ordered actual token steps required')
            self.output_ids.append(body['id'])
            if 'raw_base64' in body:
                self.raw = base64.b64decode(body['raw_base64'], validate=True)
                if len(self.raw) > self.config.get('raw_output_max_bytes', 131072):
                    raise ValueError('raw output exceeds frozen byte bound')
                self.raw_count = len(self.output_ids)
        elif kind == 'raw':
            count, offset, total = (body.get(key) for key in ('count', 'offset', 'total'))
            if type(count) is not int or type(offset) is not int or type(total) is not int:
                raise ValueError('raw snapshot requires genuine integer count/offset/total')
            chunk = base64.b64decode(body['raw_base64'], validate=True)
            if (self.phase != 'generate' or not self.generation_binding or self.stream_end
                    or not 0 < count <= len(self.output_ids)
                    or not 0 <= total <= self.config.get('raw_output_max_bytes', 131072)
                    or not 0 <= offset <= total or len(chunk) > 32768 or offset+len(chunk) > total):
                raise ValueError('raw snapshot exceeds its ordered token/byte bound')
            if offset == 0:
                if self.raw_pending or self.raw_count >= count:
                    raise ValueError('raw snapshot overlap or stale token count')
                self.raw, self.raw_total, self.raw_pending = b'', total, True
            if not self.raw_pending or offset != len(self.raw) or total != self.raw_total:
                raise ValueError('raw snapshot is foreign, incomplete or out of order')
            self.raw += chunk
            if len(self.raw) == total:
                self.raw_count, self.raw_pending = count, False
        elif kind == 'end':
            if self.phase != 'generate' or self.stream_end:
                raise ValueError('unexpected generation end')
            self.stream_end = True
        elif kind == 'complete':
            raw = (base64.b64decode(body['raw_base64'], validate=True)
                if 'raw_base64' in body else self.raw)
            if (self.raw_pending or self.raw_count != len(self.output_ids)
                    or 'raw_sha256' in body and body['raw_sha256'] != hashlib.sha256(raw).hexdigest()
                    or self.phase != 'generate' or not self.stream_end or self.complete
                    or body.get('output_ids') != self.output_ids or raw != self.raw
                    or not self.output_ids or self.output_ids[-1] not in self.config['linux_profile']['eos_token_ids']
                    or body.get('stop_reason') != 'eos'
                    or canonical(body.get('observed_runtime')) != canonical(self.config['runtime_contract'])):
                raise ValueError('completion raw/IDs/EOS/observed runtime differs or is incomplete')
            self.runtime = json.loads(canonical(body['observed_runtime']))
            self.complete = True
        else:
            raise ValueError('unknown child protocol frame')

    def result(self, failure: str | None = None) -> RuntimeResult:
        why = failure or self.failure or (None if self.done else 'incomplete paired capture/teardown; actual partial bytes retained')
        return RuntimeResult(self.raw, self.runtime, {'lease': self.lease,
            'input_ids': self.binding['input_ids'] if self.binding else [], 'output_ids': self.output_ids,
            'phase_identities': self.identities, 'guardian_events': self.frames,
            'partial': bool(why), 'child_observations': self.child_observations,
            'teardown_verified': self.teardown}, why)


def protected_bytes(path: Path, expected: str, maximum: int = 64*1024**2) -> bytes:
    """Read an independently pinned root-owned closure member, rejecting mutable ancestors."""
    if not path.is_absolute():
        raise ValueError('protected host authority needs an absolute root-owned anchor')
    for member in (path, *path.parents):
        info = member.lstat()
        if (stat.S_ISLNK(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022
                or any(name in getattr(os, 'listxattr')(member, follow_symlinks=False)
                    for name in ('system.posix_acl_access', 'system.posix_acl_default'))):
            raise ValueError('protected host authority has a writable or foreign owner/ancestor')
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('protected host authority member is not immutable to the child')
        with os.fdopen(descriptor, 'rb', closefd=False) as stream:
            raw = stream.read(maximum+1)
        if len(raw) > maximum:
            raise ValueError('protected host member exceeds frozen byte bound')
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('protected host authority digest changed')
        return raw
    finally:
        os.close(descriptor)


@dataclass(frozen=True)
class HostAuthority:
    description: bytes

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.description).hexdigest()

    def select(self, config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        """Resolve only a complete exact allowlisted actor from the protected host anchor."""
        host = json.loads(self.description)
        keys = {'schema', 'supervisor_uid', 'candidate_uid', 'candidate_gid', 'cgroup_parent',
            'cpus', 'guardian_entry', 'guardian_entry_sha256', 'guardian_python',
            'guardian_python_sha256', 'support_sources', 'profiles'}
        if (not isinstance(host, dict) or set(host) != keys or host['schema'] != 'linux-candidate-host/v1'
                or host['supervisor_uid'] != os.getuid() or os.getuid() == 0
                or any(type(host[key]) is not int or host[key] <= 0
                    for key in ('supervisor_uid', 'candidate_uid', 'candidate_gid'))
                or host['candidate_uid'] == host['supervisor_uid']
                or not isinstance(host['cpus'], list) or len(set(host['cpus'])) != 2
                or len(host['cpus']) != 2 or any(type(cpu) is not int or cpu < 0 for cpu in host['cpus'])):
            raise ValueError('protected host principal/schema/two-CPU binding differs')
        selected = host['profiles'].get(hashlib.sha256(canonical(config)).hexdigest())
        if (not isinstance(selected, dict)
                or set(selected) != {'config', 'paths', 'readonly_mounts', 'acquisition'}
                or canonical(selected['config']) != canonical(config)
                or selected['acquisition'] != {'manifest_sha256': config['linux_profile']['model_manifest_sha256'],
                    'runtime_manifest_sha256': config['linux_profile']['runtime_manifest_sha256']}):
            raise ValueError('exact actor/profile/acquisition absent from protected host allowlist')
        bench = Path(__file__).resolve().parents[1]/'bench/pinned-candidate'
        actual_backend = hashlib.sha256((bench/'qwen_backend.py').read_bytes()).hexdigest()
        if config['backend']['sha256'] != actual_backend:
            raise ValueError('operational Linux profile requires the concrete frozen Qwen child source')
        required_support = {hashlib.sha256((bench/name).read_bytes()).hexdigest() for name in
            ('qwen_backend.py','linux_guardian.py','linux_runtime_filter.py','linux_network.py','smoke.py')}
        if (not isinstance(host['support_sources'], dict)
                or not required_support <= set(host['support_sources'].values())):
            raise ValueError('installed Linux support differs from the complete frozen computation')
        for key in ('guardian_entry', 'guardian_python'):
            protected_bytes(Path(host[key]), host[key+'_sha256'])
        if not isinstance(host['support_sources'], dict) or not host['support_sources']:
            raise ValueError('complete protected guardian support closure required')
        for path, pin in host['support_sources'].items(): protected_bytes(Path(path), pin)
        return host, selected

    @classmethod
    def from_checkout(cls) -> HostAuthority:
        catalogue = json.loads(Path(__file__).with_name('qualification-registry.json').read_bytes())
        entry = catalogue.get('linux_runtime_authority')
        if not isinstance(entry, dict) or set(entry) != {'sha256'}:
            raise ValueError('no registered protected host authority; Linux resources/runtime remain unproved')
        return cls(protected_bytes(HOST_ANCHOR, entry['sha256']))


def invoke_pair(request: dict[str, Any], config: dict[str, Any],
                protected_lease: HostAuthority | None = None) -> RuntimeResult:
    """One exact allowlisted guardian owns both fresh phases and their shared deadline."""
    import ctypes
    import platform
    import subprocess
    import sys
    import time
    started = time.monotonic()
    acquired = HostAuthority.from_checkout()
    if protected_lease is not None and protected_lease != acquired:
        raise ValueError('protected host authority changed')
    config = validate_profile(config)
    # Validate request/caps before any privileged launch. This starts no process.
    PairJournal(request, config, acquired.digest)
    if (sys.platform != 'linux' or sys.byteorder != 'little' or ctypes.sizeof(ctypes.c_void_p) != 8
            or platform.machine() not in ('x86_64', 'aarch64')):
        raise ValueError('protected paired host requires actual native Linux64; Mac evidence cannot substitute')
    host, profile = acquired.select(config)
    # Only a fixed protected administrative entry is invoked. Existing administrative
    # rights may be broader; neither the candidate nor this data API selects commands.
    sudo = Path('/usr/bin/sudo')
    if (sudo.is_symlink() or not sudo.is_file() or sudo.stat().st_uid != 0 or sudo.stat().st_mode & 0o022):
        raise ValueError('fixed protected administrative launcher unavailable')
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(4, 0, 0, 0, 0):
        raise ValueError('trusted supervisor nondumpability could not be enforced')
    identity = proc_identity(os.getpid())
    deadline = started+config['timeout_seconds']
    control = canonical({'authority': acquired.digest, 'profile_sha256': hashlib.sha256(canonical(config)).hexdigest(),
        'request': request, 'supervisor_pid': os.getpid(), 'supervisor_start': identity['start'],
        'deadline_monotonic': deadline})
    if len(control)+1 > 1024**2: raise ValueError('input/control frame exceeds frozen bound')
    if time.monotonic() >= deadline-10: raise ValueError('paired authority setup exhausted shared work budget')
    process = subprocess.Popen([str(sudo), '-n', '--', host['guardian_entry'], '--lease'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True,
        start_new_session=True, env=clean_environment())
    capture = HostCapture(acquired, host, profile, process.pid, identity, deadline)
    return read_pair(process, request, config, acquired.digest, control, deadline, capture)


def clean_environment() -> dict[str, str]:
    """Allowlist only; never forward credentials, import hooks or host cache paths."""
    result = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
        'TOKENIZERS_PARALLELISM': 'false', 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
        'HF_DATASETS_OFFLINE': '1', 'HOME': '/attempt/home', 'TMPDIR': '/attempt/tmp', 'HF_HOME': '/attempt/cache'}
    result.update({name: '2' for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
        'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')})
    return result


def proc_identity(pid: int) -> dict[str, Any]:
    fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    status = dict(line.split(':', 1) for line in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line)
    return {'pid': pid, 'start': fields[19], 'ppid': int(fields[1]),
            'uids': [int(item) for item in status['Uid'].split()]}


def support_sources(config: dict[str, Any]) -> tuple[Path, ...]:
    """Whole transitive support; model/runtime closures are pinned manifests in full config.

    Freezing support starts no helper/imported runtime and grants no execution authority.
    Actual host-installed entry/interpreter pins additionally bind the registered anchor.
    """
    value = validate_profile(config)
    root = Path(__file__).resolve().parents[1]
    sources = [Path(__file__), *(root/'bench/pinned-candidate'/name for name in
        ('qwen_backend.py', 'linux_guardian.py', 'linux_runtime_filter.py', 'linux_network.py', 'smoke.py')),
        Path(value['backend']['script']), Path(value['backend']['python'])]
    if any(not source.is_file() for source in sources):
        raise ValueError('complete pinned Linux backend/support sources unavailable')
    # An operational Actor must bind its actual authority before any registration,
    # record, restoration or cache reuse. Source plans are not callable Actors.
    acquired = HostAuthority.from_checkout()
    host, _ = acquired.select(value)
    sources.extend((HOST_ANCHOR, Path(host['guardian_entry']), Path(host['guardian_python']),
        Path(__file__).with_name('qualification-registry.json')))
    sources.extend(Path(path) for path in host['support_sources'])
    return tuple(dict.fromkeys(sources))


def read_pair(process: Any, request: dict[str, Any], config: dict[str, Any],
              authority_digest: str, control: bytes, deadline: float, host: HostCapture | None = None) -> RuntimeResult:
    """Incrementally retain a paired stream. This transport reader grants no host authority.

    invoke_pair alone acquires the independently protected root guardian. Authored
    subprocesses calling this seam establish byte/protocol controls, never a real cage.
    """
    import selectors
    import time
    journal = PairJournal(request, config, authority_digest)
    if len(control)+1 > 1024**2:
        raise ValueError('paired initial input/control exceeds frozen byte bound')
    selector = selectors.DefaultSelector()
    pending = bytearray()
    stdout = bytearray()
    stderr = bytearray()
    failure: str | None = None
    sent = 0
    outgoing = control+b'\n'
    def close_control() -> None:
        if process.stdin is not None and not process.stdin.closed:
            try: selector.unregister(process.stdin)
            except KeyError: pass
            process.stdin.close()
    def fail(reason: str) -> None:
        nonlocal failure
        failure = failure or reason
        # EOF is a guardian kill/teardown command, never a request to retry or widen.
        close_control()
    try:
        for stream, name in ((process.stdin, 'control'), (process.stdout, 'stdout'), (process.stderr, 'stderr')):
            if stream is None: raise ValueError('bounded paired transport requires all private data pipes')
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_WRITE if name == 'control' else selectors.EVENT_READ, name)
        while selector.get_map() or process.poll() is None:
            now = time.monotonic()
            if now >= deadline:
                fail('shared paired deadline exhausted; teardown is unverified unless independently received')
                break
            if now >= deadline-10 and not journal.done:
                fail('shared paired work deadline exhausted; reserved teardown interval started')
            for key, _ in selector.select(min(.05, max(0, deadline-now))):
                if key.data == 'control':
                    try: sent += os.write(key.fd, outgoing[sent:])
                    except (BrokenPipeError, OSError):
                        fail('guardian control closed before protected invocation')
                        continue
                    if sent == len(outgoing): selector.unregister(key.fileobj)
                    continue
                try: chunk = os.read(key.fd, 65536)
                except BlockingIOError: continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    if key.data == 'stdout' and pending: fail('unterminated guardian frame at EOF')
                    continue
                if key.data == 'stderr':
                    available = 1024**2-len(stderr)
                    stderr.extend(chunk[:max(0, available)])
                    if len(chunk) > available: fail('guardian stderr exceeded frozen byte bound')
                    continue
                available = 8*1024**2-len(stdout)
                stdout.extend(chunk[:max(0, available)])
                if len(chunk) > available:
                    fail('guardian stdout exceeded frozen journal bound')
                    continue
                pending.extend(chunk)
                while b'\n' in pending:
                    index = pending.index(10)
                    raw = bytes(pending[:index]); del pending[:index+1]
                    try:
                        if len(raw)+1 > 65536: raise ValueError('guardian frame exceeds frozen bound')
                        packet = json.loads(raw)
                        journal.accept(packet)
                        if host is not None: host.accept(packet)
                    except (ValueError, TypeError, KeyError, OSError, AttributeError, OverflowError) as exc:
                        fail('invalid protected guardian stream: '+str(exc)[:1000])
                if len(pending) >= 65536:
                    fail('guardian unterminated frame exceeds frozen bound')
                    pending.clear()
            if process.poll() is not None:
                close_control()
        returncode = process.poll()
        if returncode != 0: failure = failure or 'guardian exit/teardown failed: '+str(returncode)
        if host is not None and failure is None:
            try: host.finish(journal)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                failure = 'protected host proof incomplete: '+str(exc)[:1000]
        result = journal.result(failure)
        observations = dict(result.observations, guardian_returncode=returncode,
            guardian_stdout_base64=base64.b64encode(stdout).decode(),
            guardian_stderr=stderr.decode(errors='replace'),
            guardian_stderr_base64=base64.b64encode(stderr).decode(), control_bytes_sent=sent,
            protected_receipts=host.receipts if host is not None else {})
        return RuntimeResult(result.raw, result.observed_runtime, observations, result.failure)
    finally:
        close_control()
        selector.close()
        for stream in (process.stdout, process.stderr):
            if stream is not None: stream.close()


def _guardian_policy() -> Any:
    """Import the frozen inert policy reader, never its privileged entry point."""
    import importlib.util
    path = Path(__file__).resolve().parents[1]/'bench/pinned-candidate/linux_guardian.py'
    spec = importlib.util.spec_from_file_location('pinned_guardian_policy', path)
    if spec is None or spec.loader is None: raise ValueError('frozen guardian policy source missing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HostCapture:
    """Actual-consumer boundary for independently protected guardian receipts.

    This object is constructed by invoke_pair only after fixed-anchor acquisition and
    a fixed root launch. Pure TEST_ONLY constructions establish refusal mechanics only.
    Child JSON never calls these host-proof/receipt methods through the guardian wrapper.
    """
    def __init__(self, authority: HostAuthority, host: dict[str, Any], profile: dict[str, Any],
                 launcher_pid: int, supervisor: dict[str, Any], deadline: float):
        self.authority, self.host, self.profile = authority, host, profile
        self.launcher_pid, self.supervisor, self.deadline = launcher_pid, supervisor, deadline
        self.policy = _guardian_policy()
        self.lease: str | None = None
        self.lease_proof = False
        self.phase: str | None = None
        self.identity: list[Any] | None = None
        self.ready: set[str] = set()
        self.observations: dict[str, int] = {'preflight': 0, 'generate': 0}
        self.mapping_counts: dict[str, int] = {'preflight': 0, 'generate': 0}
        self.resource_counts: dict[str, int] = {'preflight': 0, 'generate': 0}
        self.receipts: dict[str, Any] = {}
        self.sources: dict[str, list[dict[str, Any]]] = {}
        self.mappings: dict[str, list[dict[str, Any]]] = {}
        self.initial_cgroup: dict[str, Any] | None = None

    def accept(self, packet: dict[str, Any]) -> None:
        kind, facts = packet['event'], packet.get('facts')
        if kind == 'lease':
            self.lease = packet['lease']
        elif kind == 'phase_start':
            if not self.lease_proof: raise ValueError('protected host lease proof missing before child')
            self.phase, self.identity = packet['phase'], [packet['pid'], packet['start']]
        elif kind == 'proof':
            if not isinstance(facts, dict): raise ValueError('protected host proof object required')
            role = facts.get('role')
            if role == 'lease': self._lease(facts)
            elif role in ('sources', 'native_mappings'): self._receipt(facts)
            elif role == 'ready': self._ready(facts)
            elif set(facts) == {'stderr_base64'}:
                if len(base64.b64decode(facts['stderr_base64'], validate=True)) > 32768:
                    raise ValueError('protected child stderr chunk exceeds bound')
            else: raise ValueError('unknown protected host proof role')
        elif kind == 'resources':
            if not isinstance(facts, dict): raise ValueError('actual host resource object required')
            self.policy.validate_resources(facts, set(self.host['cpus']),
                self.policy.storage_paths(self.host,self.profile))
            for row in facts['reserve']['storage']:
                actual = self.policy.protected_path(row['path'],False)
                if (actual.st_dev,actual.st_ino) != (row['device'],row['inode']):
                    raise ValueError('protected storage identity changed after observation')
            gap = facts.get('gap_seconds')
            if gap is not None and (type(gap) not in (int, float) or not 0 <= gap <= 2):
                raise ValueError('actual host observer gap exceeds frozen bound')
            if self.phase is not None:
                self.resource_counts[self.phase] += 1
                if 'pid' in facts and [facts['pid'], facts.get('start')] != self.identity:
                    raise ValueError('resource observation belongs to another process')
        elif kind == 'frame':
            body = packet['body']
            if self.phase not in self.ready:
                raise ValueError('child frame has no independent actual host READY proof')
            if body['type'] == 'observation':
                self.observations[self.phase] += 1
                # The guardian snapshots maps after this frame and sends a fixed ACK.
            elif body['type'] == 'ready':
                if type(body['facts'].get('dumpable')) is not int or body['facts']['dumpable'] != 0:
                    raise ValueError('pinned post-exec child dumpability readback missing')
            elif body['type'] == 'complete':
                self._native_match(body['observed_runtime'].get('native_mappings'))
        elif kind == 'phase_end':
            if not self.phase: raise ValueError('host phase end has no live phase')
            if self.phase not in self.ready: raise ValueError('host phase lacks READY proof')
            if (self.mapping_counts[self.phase] != self.observations[self.phase]+1
                    or not self.resource_counts[self.phase]):
                raise ValueError('actual host observation/loaded-runtime mapping receipts incomplete')
            self.phase, self.identity = None, None

    def _lease(self, facts: dict[str, Any]) -> None:
        import math
        if (self.lease_proof or self.phase is not None or facts.get('authority') != self.authority.digest
                or facts.get('profile_sha256') != hashlib.sha256(canonical(self.profile['config'])).hexdigest()
                or facts.get('supervisor_pid') != self.supervisor['pid']
                or facts.get('supervisor_start') != self.supervisor['start']
                or facts.get('supervisor_uid') != self.host['supervisor_uid']
                or facts.get('guardian_uid') != 0
                or facts.get('source_pins') != self.host['support_sources']):
            raise ValueError('protected host lease identity/source/authority binding differs')
        shared, work = facts.get('shared_deadline'), facts.get('work_deadline')
        if not isinstance(shared, (int, float)) or not isinstance(work, (int, float)):
            raise ValueError('protected shared deadline requires finite numeric clocks')
        if (type(shared) not in (int, float) or type(work) not in (int, float)
                or not math.isfinite(shared) or not math.isfinite(work) or shared-work != 10
                or shared > self.deadline):
            raise ValueError('protected shared work/teardown deadline differs')
        guardian = proc_identity(facts['guardian_pid'])
        if guardian['uids'] != [0]*4 or guardian['start'] != facts['guardian_start']:
            raise ValueError('actual guardian UID/start identity differs')
        current = guardian['pid']
        seen: set[int] = set()
        while current > 1 and current not in seen and len(seen) < 32:
            if current == self.launcher_pid: break
            seen.add(current)
            actual = proc_identity(current)
            if actual['uids'] not in ([0]*4, self.supervisor['uids']):
                raise ValueError('foreign principal in actual guardian launch ancestry')
            current = actual['ppid']
        if current != self.launcher_pid:
            raise ValueError('actual root guardian did not descend from fixed private launch')
        self.lease_proof = True

    def _receipt(self, facts: dict[str, Any]) -> None:
        if not self.phase or self.identity != [facts.get('pid'), facts.get('start')]:
            raise ValueError('protected source/native receipt has a foreign phase identity')
        role = facts['role']
        if role == 'sources':
            if self.phase in self.sources: raise ValueError('duplicate protected source receipt')
            name = self.phase+'-sources.jsonl'
        else:
            sequence = facts.get('sequence')
            if type(sequence) is not int or sequence != self.mapping_counts[self.phase]:
                raise ValueError('actual native mapping receipt sequence differs')
            name = self.phase+f'-native-mappings-{sequence:06d}.jsonl'
        if (type(facts.get('bytes')) is not int or not 0 <= facts['bytes'] <= 64*1024**2
                or type(facts.get('total')) is not int or facts['total'] < 0):
            raise ValueError('protected source/native receipt count/bytes exceed bound')
        path = HOST_ANCHOR.parent/'receipts'/str(self.lease)/name
        raw = protected_bytes(path, facts['sha256'])
        if len(raw) != facts['bytes']: raise ValueError('protected receipt byte length differs')
        rows = [json.loads(line) for line in raw.splitlines()]
        if len(rows) != facts['total'] or any(not isinstance(row, dict) for row in rows):
            raise ValueError('protected receipt record count/shape differs')
        # Preserve complete canonical records; a digest or root-looking path alone
        # is never accepted in place of acquisition from this fixed protected store.
        self.receipts[name] = {'sha256': facts['sha256'], 'bytes': len(raw), 'records': rows}
        if role == 'sources':
            expected = {item['target']: item for item in self.profile['readonly_mounts']}
            if len(rows) != len(expected) or {row.get('target') for row in rows} != set(expected):
                raise ValueError('actual mounted source universe differs from protected closure')
            for row in rows:
                declared = expected[row['target']]
                if row.get('source') != declared['source'] or row.get('sha256') != declared['sha256']:
                    raise ValueError('actual mounted source identity/pin differs')
                status = Path(declared['source']).stat()
                if (row.get('device'), row.get('inode')) != (status.st_dev, status.st_ino):
                    raise ValueError('actual mounted source inode/device binding differs')
            self.sources[self.phase] = rows
        else:
            expected = {item['target']: item['sha256'] for item in self.profile['readonly_mounts']}
            if any(row.get('path') not in expected or row.get('sha256') != expected[row['path']] for row in rows):
                raise ValueError('actual native mapping escapes acquired readonly closure')
            self.mappings[self.phase] = rows
            self.mapping_counts[self.phase] += 1

    def _ready(self, facts: dict[str, Any]) -> None:
        if (not self.phase or self.phase in self.ready or [facts.get('pid'), facts.get('start')] != self.identity
                or self.phase not in self.sources or self.mapping_counts[self.phase] != 1
                or facts.get('source_count') != len(self.sources[self.phase])
                or facts.get('native_mapping_count') != len(self.mappings[self.phase])):
            raise ValueError('actual host READY source/native/process binding incomplete')
        status = facts['status']
        # Guardian acquired these live proc facts before releasing READY/input.
        # Reopening child proc here would race with a fast phase's verified exit.
        expected_dumpability = {'proc_owners':{'mem':{'uid':0,'gid':0},'auxv':{'uid':0,'gid':0}},
            'user_namespace':os.readlink('/proc/self/ns/user')}
        if facts.get('nondumpability') != expected_dumpability:
            raise ValueError('independent post-exec nondumpability observation differs')
        if (list(map(int, status['Uid'].split())) != [self.host['candidate_uid']]*4
                or list(map(int, status['Gid'].split())) != [self.host['candidate_gid']]*4
                or status['Groups'].strip() or status['NSpid'].split()[-1] != '1'
                or any(int(status[key], 16) for key in ('CapEff','CapPrm','CapInh','CapAmb','CapBnd'))
                or status['NoNewPrivs'] != '1' or status['Seccomp'] != '2'
                or int(status['Seccomp_filters']) < 2
                or facts.get('root_readonly') is not True or facts.get('proc_readonly') is not True
                or facts.get('tmpfs_bytes') != 134217728):
            raise ValueError('actual host credential/capability/private-root proof differs')
        writable = facts['writable_mounts']
        if (not isinstance(writable, list) or len(writable) != 1
                or writable[0].get('path') != '/attempt' or writable[0].get('fstype') != 'tmpfs'
                or not {'rw','nosuid','nodev','noexec'} <= set(writable[0]['flags'])):
            raise ValueError('actual host writable mount scope differs')
        for namespace in ('pid','mnt'):
            if facts['namespaces'][namespace] == os.readlink('/proc/self/ns/'+namespace):
                raise ValueError('actual host child namespace is not private')
        limits = facts['limits']
        expected_limits = {'memory.max':'12884901888','memory.swap.max':'0','pids.max':'128',
            'cpu.max':'200000 100000','cpu.max.burst':'0'}
        if (any(limits.get(key) != value for key,value in expected_limits.items())
                or self.policy.parse_set(limits['cpuset.cpus.effective']) != set(self.host['cpus'])
                or not self.policy.parse_set(limits['cpuset.mems.effective'])):
            raise ValueError('actual host kernel memory/CPU/cpuset limits differ')
        cgroup = facts['cgroup_identity']
        if cgroup.get('name') != 'lease-'+str(self.lease): raise ValueError('actual host cgroup lease changed')
        if self.initial_cgroup is None: self.initial_cgroup = cgroup
        elif self.initial_cgroup != cgroup: raise ValueError('paired phases changed protected cgroup identity')
        self.ready.add(self.phase)

    def _native_match(self, actual: Any) -> None:
        if not self.phase or not isinstance(actual, list):
            raise ValueError('actual child runtime lacks loaded native observations')
        host = {row['path']: row['sha256'] for row in self.mappings.get(self.phase, [])}
        candidate = {row['path']: row['sha256'] for row in actual if isinstance(row, dict)}
        if host != candidate or len(actual) != len(candidate):
            raise ValueError('child loaded runtime differs from independent actual host native mappings')

    def finish(self, journal: PairJournal) -> None:
        if not self.lease_proof or self.ready != {'preflight','generate'}:
            raise ValueError('protected host lease/kernel proof missing for both phases')
        if self.observations['preflight'] != 1 or self.observations['generate'] != 2:
            raise ValueError('protected post-import and post-generation observations incomplete')
        if not journal.done or journal.failure or self.phase is not None:
            raise ValueError('protected host lifecycle/teardown incomplete')
