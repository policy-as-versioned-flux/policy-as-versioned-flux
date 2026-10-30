"""Fixed, privileged, one-lease Linux guardian. Importing this source is inert.

Only --lease is accepted. Host configuration is obtained from the protected fixed
anchor; stdin can select an allowlisted digest and input, never a command or path.
Source implementation is not evidence of target authority or kernel compatibility.
"""
from __future__ import annotations

import base64
import ctypes
import errno
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import pwd
import resource
import select
import selectors
import signal
import stat
import sys
import time
from typing import Any, Callable

ANCHOR = '/run/policy-as-versioned-flux-candidate/host.json'
MEMORY = 12884901888
RESERVE = 2147483648
DISK = 5368709120
MAX_INPUT = 1048576
MAX_FRAME = 65536
MAX_STDOUT = 8388608
MAX_STDERR = 1048576
SAMPLE_SECONDS = 1.0
CLONE_NEWNS = 0x00020000
CLONE_NEWPID = 0x20000000
MS_RDONLY, MS_NOSUID, MS_NODEV, MS_NOEXEC = 1, 2, 4, 8
MS_REMOUNT, MS_BIND, MS_REC, MS_PRIVATE = 32, 4096, 16384, 1 << 18


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pin(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


class FrameReader:
    """Incremental untrusted newline-JSON reader with independent frame/total limits."""
    def __init__(self, frame_limit: int = MAX_FRAME, total_limit: int = MAX_STDOUT):
        self.pending = bytearray()
        self.total = 0
        self.frame_limit, self.total_limit = frame_limit, total_limit

    def feed(self, raw: bytes) -> list[dict[str, Any]]:
        self.total += len(raw)
        if self.total > self.total_limit:
            raise ValueError('stdout journal byte cap exceeded')
        self.pending.extend(raw)
        result = []
        while b'\n' in self.pending:
            at = self.pending.index(10)
            if at+1 > self.frame_limit:
                raise ValueError('stdout frame byte cap exceeded')
            raw_line = bytes(self.pending[:at])
            del self.pending[:at+1]
            value = json.loads(raw_line)
            if not isinstance(value, dict):
                raise ValueError('child frame must be an object')
            result.append(value)
        if len(self.pending) >= self.frame_limit:
            raise ValueError('unterminated stdout frame byte cap exceeded')
        return result

    def eof(self) -> None:
        if self.pending:
            raise ValueError('unterminated child frame at EOF')


class Wire:
    """Host event author; child bytes are always nested beneath an actual frame event."""
    def __init__(self, lease: str):
        self.lease = lease
        self.total = 0

    def event(self, event: str, **fields: Any) -> bytes:
        if 'event' in fields or 'lease' in fields:
            raise ValueError('host event identity cannot be replaced')
        raw = canonical(dict(event=event, lease=self.lease, **fields))+b'\n'
        # Reserve one failure and teardown receipt rather than consuming all capacity.
        terminal = event in ('failure', 'phase_end', 'aborted', 'done')
        limit = MAX_STDOUT if terminal else MAX_STDOUT-32768
        if len(raw) > MAX_FRAME or self.total+len(raw) > limit:
            raise ValueError('protected host journal byte cap exceeded')
        self.total += len(raw)
        return raw

    def frame(self, phase: str, body: dict[str, Any]) -> bytes:
        return self.event('frame', phase=phase, body=body)


def teardown_receipt(populated: bool, pidfd_dead: bool, reaped: bool, removed: bool) -> dict[str, bool]:
    """Closed teardown seam: issued kills and timeouts are never empty receipts."""
    if (type(populated) is not bool or populated is not False or pidfd_dead is not True
            or reaped is not True or removed is not True):
        raise ValueError('actual empty/dead/reaped/removed teardown witnesses required')
    return {'empty':True,'reaped':True,'removed':True}


class Identity:
    """Pinned pidfd plus proc start-time. A numeric PID alone never authorizes an action."""
    def __init__(self, pid: int, start: str | None = None):
        self.pid = pid
        before = self.read(pid)
        self.fd = os.pidfd_open(pid, 0)
        after = self.read(pid)
        if before != after or start is not None and after['start'] != start or self.dead():
            os.close(self.fd)
            raise ValueError('process identity changed while pinning pidfd')
        self.start = after['start']
        self.uid = after['uid']
        self.ppid = after['ppid']

    @staticmethod
    def read(pid: int) -> dict[str, Any]:
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        status = parse_status(Path(f'/proc/{pid}/status').read_text())
        return {'start': fields[19], 'ppid': int(fields[1]),
                'uid': [int(x) for x in status['Uid'].split()]}

    def verify(self) -> None:
        value = self.read(self.pid)
        if value['start'] != self.start or value['uid'] != self.uid or self.dead():
            raise ValueError('pinned process identity no longer live')

    def dead(self) -> bool:
        return bool(select.select([self.fd], [], [], 0)[0])

    def close(self) -> None:
        os.close(self.fd)


def parse_status(raw: str) -> dict[str, str]:
    return {key: value.strip() for line in raw.splitlines() if ':' in line
            for key, value in [line.split(':', 1)]}


def protected_path(path: str, regular: bool | None = None) -> os.stat_result:
    target = Path(path)
    if not target.is_absolute() or str(target) != path or '..' in target.parts:
        raise ValueError('protected absolute canonical host path required')
    for member in (target, *target.parents):
        info = member.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('mutable or aliased protected path: '+str(member))
        attrs = os.listxattr(member, follow_symlinks=False)
        if any(name in attrs for name in ('system.posix_acl_access', 'system.posix_acl_default')):
            raise ValueError('protected paths cannot carry discretionary ACLs')
    info = target.lstat()
    if regular is True and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                            or info.st_mode & 0o6000 or 'security.capability' in os.listxattr(target)):
        raise ValueError('protected source must be single-link regular without privilege bits/caps')
    if regular is False and not stat.S_ISDIR(info.st_mode):
        raise ValueError('protected directory required')
    return info


def protected_read(path: str, expected: str | None = None, maximum: int = 16*1024**2) -> bytes:
    before = protected_path(path, True)
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        current = os.fstat(descriptor)
        if (before.st_dev, before.st_ino) != (current.st_dev, current.st_ino):
            raise ValueError('protected source replaced during open')
        chunks, count = [], 0
        while True:
            chunk = os.read(descriptor, min(4*1024**2, maximum+1-count))
            if not chunk: break
            chunks.append(chunk)
            count += len(chunk)
            if count > maximum: raise ValueError('protected source exceeds byte cap')
        raw = b''.join(chunks)
        if expected is not None and digest(raw) != expected:
            raise ValueError('protected source pin differs')
        return raw
    finally:
        os.close(descriptor)


def hash_file(path: str, expected: str, checkpoint: Callable[[],None] | None = None) -> dict[str, Any]:
    before = protected_path(path, True)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        seen = os.fstat(fd)
        if (seen.st_dev, seen.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError('acquired source replaced')
        sha = hashlib.sha256()
        while True:
            if checkpoint is not None: checkpoint()
            chunk = os.read(fd,4*1024**2)
            if not chunk: break
            sha.update(chunk)
        if sha.hexdigest() != expected: raise ValueError('acquired source hash differs')
        return {'path': path, 'device': seen.st_dev, 'inode': seen.st_ino,
                'bytes': seen.st_size, 'sha256': expected}
    finally:
        os.close(fd)


def validate_request(value: Any) -> dict[str, Any]:
    if (not isinstance(value, dict) or set(value) != {'authority', 'profile_sha256', 'request',
            'supervisor_pid', 'supervisor_start', 'deadline_monotonic'} or not pin(value['authority'])
            or not pin(value['profile_sha256']) or type(value['supervisor_pid']) is not int
            or value['supervisor_pid'] <= 1 or not isinstance(value['supervisor_start'], str)
            or not value['supervisor_start'].isdigit()):
        raise ValueError('exact fixed lease request required')
    deadline = value['deadline_monotonic']
    if type(deadline) not in (int, float) or not math.isfinite(deadline) or deadline <= 0:
        raise ValueError('host monotonic deadline must be finite numeric and cannot be model-appointed')
    request = value['request']
    if (not isinstance(request, dict) or set(request) != {'input', 'prompt_utf8'}
            or not isinstance(request['input'], (dict, str)) or not isinstance(request['prompt_utf8'], str)
            or len(canonical(value))+1 > MAX_INPUT):
        raise ValueError('bounded exact input-only request required')
    return value


def validate_reviewed_profile(config: dict[str,Any])->None:
    """Even protected host installation cannot silently widen these reviewed actors."""
    profiles={'signal-linux-bf16-v1':{'max_input_tokens':4096,'max_new_tokens':512,
        'timeout_seconds':900,'threads':2,'interop_threads':1},
        'substrate-linux-bf16-v1':{'max_input_tokens':4096,'max_new_tokens':2048,
        'timeout_seconds':600,'threads':2,'interop_threads':1,'context_tokens':8192,
        'raw_output_max_bytes':131072}}
    profile_id=config.get('profile')
    if not isinstance(profile_id,str):raise ValueError('reviewed profile ID required')
    limits=profiles.get(profile_id)
    if (limits is None or any(type(config.get(key)) is not int or config[key]!=value
            for key,value in limits.items()) or any(key in config for key in
                {'context_tokens','raw_output_max_bytes'}-set(limits))):
        raise ValueError('reviewed numerical profile differs; no widening or fallback')
    expected={'model_id':'Qwen/Qwen3-4B-Instruct-2507',
        'revision':'cdbee75f17c01a7cc42f958dc650907174af0554',
        'model_manifest_sha256':'409410d7d41d7e62aafb27c18f049fe3c62d66383b3a5b89d5fadfd3b773fd7e',
        'chat_template_sha256':'64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326',
        'dtype':'torch.bfloat16','device':'cpu','attention':'eager','do_sample':False,
        'num_beams':1,'num_return_sequences':1,'seed':0,'use_cache':True,
        'cache_implementation':'dynamic','eos_token_ids':[151645,151643],'pad_token_id':151643}
    actual=config.get('linux_profile')
    if (not isinstance(actual,dict) or set(actual)!=set(expected)|{'runtime_manifest_sha256'}
            or any(canonical(actual[key])!=canonical(value) for key,value in expected.items())
            or not pin(actual['runtime_manifest_sha256'])):
        raise ValueError('reviewed exact CPU BF16 greedy decode/model pins differ')


def control_checkpoint(deadline: float) -> None:
    if time.monotonic() >= deadline: raise ValueError('shared setup/work deadline exhausted')
    if select.select([0],[],[],0)[0]:
        extra=os.read(0,1)
        raise ValueError('private control EOF during setup' if not extra else 'unexpected private control byte')


def load_host(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    setup_deadline = min(request['deadline_monotonic'], time.monotonic()+900)-10
    control_checkpoint(setup_deadline)
    host = json.loads(protected_read(ANCHOR, request['authority'], 64*1024**2))
    control_checkpoint(setup_deadline)
    required = {'schema', 'supervisor_uid', 'candidate_uid', 'candidate_gid', 'cgroup_parent',
                'cpus', 'guardian_entry', 'guardian_entry_sha256', 'guardian_python',
                'guardian_python_sha256', 'support_sources', 'profiles'}
    if not isinstance(host, dict) or set(host) != required or host['schema'] != 'linux-candidate-host/v1':
        raise ValueError('protected host anchor schema differs')
    uid, gid, supervisor = host['candidate_uid'], host['candidate_gid'], host['supervisor_uid']
    if (any(type(x) is not int or x <= 0 for x in (uid, gid, supervisor)) or uid == supervisor
            or uid == os.getuid() or gid == os.getgid() or len(host['cpus']) != 2
            or any(type(x) is not int or x < 0 for x in host['cpus'])
            or len(set(host['cpus'])) != 2):
        raise ValueError('distinct existing candidate identity and exactly two CPUs required')
    account = pwd.getpwuid(uid)
    if account.pw_gid != gid:
        raise ValueError('existing candidate UID/GID binding differs')
    if not isinstance(host['profiles'], dict) or request['profile_sha256'] not in host['profiles']:
        raise ValueError('profile not in protected allowlist')
    profile = host['profiles'][request['profile_sha256']]
    if (not isinstance(profile, dict) or set(profile) != {'config', 'paths', 'readonly_mounts', 'acquisition'}
            or digest(canonical(profile['config'])) != request['profile_sha256']):
        raise ValueError('full frozen profile digest differs')
    validate_reviewed_profile(profile['config'])
    setup_deadline = min(setup_deadline,time.monotonic()+profile['config']['timeout_seconds']-10)
    def checkpoint() -> None: control_checkpoint(setup_deadline)
    if (not isinstance(host['support_sources'], dict) or not host['support_sources']
            or host['support_sources'].get(str(Path(__file__).absolute())) != digest(Path(__file__).read_bytes())
            or os.path.realpath('/proc/self/exe') != host['guardian_python']):
        raise ValueError('running guardian executable/source authority differs')
    hash_file(host['guardian_entry'],host['guardian_entry_sha256'],checkpoint)
    hash_file(host['guardian_python'], host['guardian_python_sha256'],checkpoint)
    for source, expected in host['support_sources'].items(): hash_file(source, expected,checkpoint)
    mounts = profile['readonly_mounts']
    if not isinstance(mounts, list) or not mounts:
        raise ValueError('complete immutable read closure required')
    targets = set()
    for entry in mounts:
        if (not isinstance(entry, dict) or set(entry) != {'source', 'target', 'sha256'}
                or not pin(entry['sha256']) or not isinstance(entry['target'], str)
                or not entry['target'].startswith('/') or '..' in Path(entry['target']).parts
                or entry['target'] in targets or entry['target'] in ('/', '/proc', '/attempt')
                or entry['target'].startswith(('/proc/', '/attempt/'))):
            raise ValueError('readonly closure mapping differs')
        targets.add(entry['target'])
        hash_file(entry['source'], entry['sha256'],checkpoint)
    for key, pin_key in (('script', 'sha256'), ('python', 'python_sha256')):
        backend = profile['config']['backend']
        if not any(item['source'] == backend[key] and item['sha256'] == backend[pin_key] for item in mounts):
            raise ValueError('pinned fixed child executable absent from readonly closure')
    paths = profile['paths']
    if (not isinstance(paths, dict) or set(paths) != {'assets','model_manifest','runtime_manifest',
            'network_module','smoke_module','site_packages','support_sources'}):
        raise ValueError('exact child path projection required')
    for jailed, expected in paths['support_sources'].items():
        if not any(item['target'] == jailed and item['sha256'] == expected
                   and host['support_sources'].get(item['source']) == expected for item in mounts):
            raise ValueError('support projection lacks protected source binding')
    if (profile['acquisition'] != {'manifest_sha256': profile['config']['linux_profile']['model_manifest_sha256'],
            'runtime_manifest_sha256': profile['config']['linux_profile']['runtime_manifest_sha256']}):
        raise ValueError('protected acquisition pins differ')
    return host, profile


def verify_guardian_closure(host:dict[str,Any],checkpoint:Callable[[],None])->dict[str,str]:
    """Pin actual privileged interpreter sources/native mappings before clone."""
    allowed=dict(host['support_sources'])
    allowed[host['guardian_python']]=host['guardian_python_sha256']
    paths:set[str]=set()
    for module in tuple(sys.modules.values()):
        origin=getattr(module,'__file__',None)
        if origin:paths.add(str(origin))
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields=line.split(maxsplit=5)
        if len(fields)==6 and fields[5].startswith('/'):paths.add(fields[5])
    result={}
    for path in sorted(paths):
        if path not in allowed:raise ValueError('unpinned privileged guardian read closure: '+path)
        hash_file(path,allowed[path],checkpoint)
        result[path]=allowed[path]
    return result


def supervisor_identity(host: dict[str, Any], request: dict[str, Any]) -> Identity:
    # Freeze the direct parent before walking trusted sudo/launcher ancestry. The
    # declared supervisor can only match an actual ancestor with all four UIDs.
    parent = Identity(os.getppid())
    current = parent.pid
    found = False
    visited = set()
    try:
        while current > 1 and current not in visited:
            visited.add(current)
            state = Identity.read(current)
            if current == request['supervisor_pid']:
                found = state['start'] == request['supervisor_start'] and state['uid'] == [host['supervisor_uid']]*4
                break
            if state['uid'] not in ([0]*4, [host['supervisor_uid']]*4):
                break
            current = state['ppid']
        parent.verify()
        if not found: raise ValueError('original supervisor ancestry/UID/start not authenticated')
        identity = Identity(request['supervisor_pid'], request['supervisor_start'])
        status = parse_status(Path(f'/proc/{identity.pid}/status').read_text())
        # Linux exposes dumpability through ownership of proc sensitive members.
        if Path(f'/proc/{identity.pid}/mem').stat().st_uid != 0:
            identity.close()
            raise ValueError('supervisor is not demonstrably nondumpable')
        return identity
    finally:
        parent.close()


def candidate_unused(uid: int, gid: int) -> None:
    for item in Path('/proc').iterdir():
        if not item.name.isdigit(): continue
        try: state = parse_status((item/'status').read_text())
        except FileNotFoundError: continue
        if (uid in map(int, state['Uid'].split()) or gid in map(int, state['Gid'].split())
                or gid in map(int,state['Groups'].split())):
            raise ValueError('candidate UID/GID already has an active process')


def parse_set(raw: str) -> set[int]:
    found: set[int] = set()
    for item in raw.strip().split(','):
        if not item: continue
        parts = item.split('-')
        if len(parts) == 1: found.add(int(parts[0]))
        elif len(parts) == 2: found.update(range(int(parts[0]), int(parts[1])+1))
        else: raise ValueError('invalid kernel set')
    return found


def key_values(raw: str) -> dict[str, int]:
    return {key: int(value) for line in raw.splitlines() for key, value in [line.split()]}


def validate_resources(facts: dict[str, Any], cpus: set[int]) -> None:
    """Public resource-proof seam over independently acquired kernel snapshots."""
    expected = {'memory.max':str(MEMORY),'memory.swap.max':'0','pids.max':'128',
                'cpu.max':'200000 100000','cpu.max.burst':'0'}
    limits = facts['limits']
    if (any(limits.get(key) != value for key,value in expected.items())
            or parse_set(limits['cpuset.cpus.effective']) != cpus or len(cpus) != 2
            or not parse_set(limits['cpuset.mems.effective'])):
        raise ValueError('actual resource limits/effective cpuset differ')
    for key in ('memory.current','memory.peak','memory.swap.current','pids.current'):
        if type(facts[key]) is not int or facts[key] < 0:
            raise ValueError('actual resource counter is not a nonnegative integer')
    if (facts['memory.current'] > MEMORY or facts['memory.peak'] > MEMORY
            or facts['memory.peak'] < facts['memory.current'] or facts['memory.swap.current']
            or facts['pids.current'] > 128
            or any(facts['memory.events'].get(key,0) for key in ('oom','oom_kill','max'))):
        raise ValueError('actual resource cap/swap/oom failure')
    if (facts['reserve']['memory_available'] < RESERVE or facts['reserve']['disk_free'] < DISK):
        raise ValueError('actual host reserve unavailable')


class UnverifiedSetupCleanup(ValueError):
    """Setup created host state whose removal could not be independently verified."""


class Leaf:
    """Pinned unique cgroup directory; every control access is relative/no-follow."""
    def __init__(self, parent: str, lease: str, cpus: list[int]):
        protected_path(parent, False)
        self.parent_path = parent
        self.name = 'lease-'+lease
        self.parentfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        self.parent_identity = os.fstat(self.parentfd)
        self.fd = -1
        self.cpus = set(cpus)
        self.removed = False
        self.identity = None
        self.mount_id = None
        created=False
        try:
            # Never enable controllers. Verify existing subtree enablement only.
            needed = {'memory','cpu','cpuset','pids'}
            enabled = set(Path(parent,'cgroup.subtree_control').read_text().split())
            if not needed <= enabled: raise ValueError('required cgroup controllers are not already enabled')
            ancestor = Path(parent)
            while True:
                protected_path(str(ancestor), False)
                for name in ('cgroup.procs','cgroup.threads','cgroup.subtree_control','memory.max',
                        'memory.swap.max','pids.max','cpu.max','cpu.max.burst','cpuset.cpus','cpuset.mems'):
                    if (ancestor/name).exists():protected_path(str(ancestor/name), True)
                if (ancestor/'memory.max').exists():
                    maximum = (ancestor/'memory.max').read_text().strip()
                    current = int((ancestor/'memory.current').read_text())
                    if maximum != 'max' and int(maximum)-current < MEMORY+RESERVE:
                        raise ValueError('cgroup ancestor lacks 14GiB headroom')
                if ancestor == Path('/sys/fs/cgroup'): break
                if ancestor.parent == ancestor or Path('/sys/fs/cgroup') not in ancestor.parents:
                    raise ValueError('protected cgroup2 parent must lie beneath /sys/fs/cgroup')
                ancestor = ancestor.parent
            reserve(parent, MEMORY+RESERVE)
            os.mkdir(self.name, 0o700, dir_fd=self.parentfd)
            created=True
            self.fd = os.open(self.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                              dir_fd=self.parentfd)
            self.identity = os.fstat(self.fd)
            self.mount_id = self._mount_id()
            if self.mount_id != int(Path(f'/proc/self/fdinfo/{self.parentfd}').read_text().split('mnt_id:')[1].split()[0]):
                raise ValueError('cgroup leaf changed mount')
            # cgroup v2 magic from fstatfs, not path naming.
            block = (ctypes.c_long*32)()
            libc_call('fstatfs', self.fd, ctypes.byref(block))
            if block[0] != 0x63677270: raise ValueError('not an actual cgroup2 filesystem')
            for name, value in {'memory.max':str(MEMORY),'memory.swap.max':'0','pids.max':'128',
                    'cpu.max':'200000 100000','cpu.max.burst':'0',
                    'cpuset.cpus':','.join(map(str,sorted(self.cpus)))}.items():
                self.write(name, value)
            mems = Path(parent,'cpuset.mems.effective').read_text().strip()
            if not parse_set(mems): raise ValueError('no valid inherited cpuset memory nodes')
            self.write('cpuset.mems', mems)
            self.verify_limits()
        except BaseException as original:
            # No child exists yet, but a partial directory is still owned state.
            # Failure to remove it must retain the identity lock and never yield
            # an optimistic removed receipt from the outer guardian.
            if self.fd >= 0:
                os.close(self.fd)
                self.fd = -1
            cleanup_error=None
            if created:
                try:os.rmdir(self.name,dir_fd=self.parentfd)
                except OSError as exc:cleanup_error=exc
            os.close(self.parentfd)
            if cleanup_error is not None:
                raise UnverifiedSetupCleanup('partial cgroup setup removal failed: '+str(cleanup_error)) from original
            raise

    def _mount_id(self) -> int:
        return int(Path(f'/proc/self/fdinfo/{self.fd}').read_text().split('mnt_id:')[1].split()[0])

    def verify(self) -> None:
        if self.identity is None:raise ValueError('cgroup descriptor identity unavailable')
        current = os.stat(self.name, dir_fd=self.parentfd, follow_symlinks=False)
        parent = os.stat(self.parent_path, follow_symlinks=False)
        if (self.removed or (current.st_dev,current.st_ino) != (self.identity.st_dev,self.identity.st_ino)
                or (parent.st_dev,parent.st_ino) != (self.parent_identity.st_dev,self.parent_identity.st_ino)
                or self._mount_id() != self.mount_id):
            raise ValueError('pinned cgroup identity changed')

    def read(self, name: str) -> str:
        self.verify()
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=self.fd)
        try:
            info = os.fstat(fd)
            if info.st_uid or info.st_mode & 0o022: raise ValueError('candidate-writable cgroup control')
            return os.read(fd, 65536).decode().strip()
        finally: os.close(fd)

    def write(self, name: str, value: str) -> None:
        self.verify()
        fd = os.open(name, os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=self.fd)
        try:
            if os.write(fd, value.encode()) != len(value): raise ValueError('short cgroup control write')
        finally: os.close(fd)

    def read_limits(self) -> dict[str,str]:
        return {name:self.read(name) for name in ('memory.max','memory.swap.max','pids.max',
            'cpu.max','cpu.max.burst','cpuset.cpus.effective','cpuset.mems.effective')}

    def verify_limits(self) -> dict[str, Any]:
        expected = {'memory.max':str(MEMORY),'memory.swap.max':'0','pids.max':'128',
                    'cpu.max':'200000 100000','cpu.max.burst':'0'}
        actual = self.read_limits()
        if any(actual[key]!=value for key,value in expected.items()) or self.read('memory.swap.current') != '0':
            raise ValueError('actual cgroup limits/swap differ')
        if parse_set(actual['cpuset.cpus.effective']) != self.cpus or not parse_set(actual['cpuset.mems.effective']):
            raise ValueError('effective protected cpuset differs from exact two CPUs')
        return actual

    def populated(self) -> bool:
        return key_values(self.read('cgroup.events'))['populated'] != 0

    def sample(self, child: Identity | None, previous: float | None) -> dict[str, Any]:
        now = time.monotonic()
        facts: dict[str, Any] = {'monotonic':now,'gap_seconds':None if previous is None else now-previous,
            'limits':self.read_limits(),'memory.current':int(self.read('memory.current')),
            'memory.peak':int(self.read('memory.peak')),'memory.events':key_values(self.read('memory.events')),
            'memory.swap.current':int(self.read('memory.swap.current')),
            'cpu.stat':key_values(self.read('cpu.stat')),'cgroup.events':key_values(self.read('cgroup.events')),
            'pids.current':int(self.read('pids.current')),'reserve':reserve(self.parent_path, RESERVE,False)}
        if child is not None and not child.dead():
            child.verify()
            facts['pid'] = child.pid
            facts['start'] = child.start
            state=parse_status(Path(f'/proc/{child.pid}/status').read_text())
            facts['status']={key:state[key] for key in ('VmRSS','VmHWM','VmSize','VmSwap','Threads',
                'Cpus_allowed_list','Mems_allowed_list') if key in state}
            facts['stat'] = Path(f'/proc/{child.pid}/stat').read_text()
            facts['schedstat'] = Path(f'/proc/{child.pid}/schedstat').read_text()
        return facts

    def remove(self) -> None:
        self.verify()
        if self.populated(): raise ValueError('cannot remove populated cgroup')
        os.rmdir(self.name, dir_fd=self.parentfd)
        self.removed = True
        os.close(self.fd)
        os.close(self.parentfd)


def reserve(path: str, minimum: int, enforce: bool = True) -> dict[str, int]:
    info = parse_status(Path('/proc/meminfo').read_text())
    available = int(info['MemAvailable'].split()[0])*1024
    disk = os.statvfs(path)
    free = disk.f_bavail*disk.f_frsize
    if enforce and (available < minimum or free < DISK):
        raise ValueError('host memory reserve or 5GiB free disk unavailable')
    return {'memory_available':available,'disk_free':free,'required_memory':minimum,'required_disk':DISK}


def libc_call(name: str, *args: Any) -> int:
    libc = ctypes.CDLL(None, use_errno=True)
    result = getattr(libc, name)(*args)
    if result == -1:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), name)
    return result


def prctl(option: int, value: int = 0) -> None:
    libc_call('prctl', option, value, 0, 0, 0)


def mount(source: str | None, target: str, filesystem: str | None, flags: int, data: str | None = None) -> None:
    def encoded(value: str | None) -> bytes | None: return None if value is None else os.fsencode(value)
    libc_call('mount', encoded(source), encoded(target), encoded(filesystem), ctypes.c_ulong(flags), encoded(data))


def wait_guardian(fd: int) -> None:
    if select.select([fd], [], [], 0)[0]: os._exit(125)


def fixed_environment() -> dict[str, str]:
    value = {name:'2' for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS',
                                  'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')}
    value.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',
        HF_DATASETS_OFFLINE='1',HOME='/attempt/home',TMPDIR='/attempt/tmp',HF_HOME='/attempt/cache',
        XDG_CACHE_HOME='/attempt/cache',LANG='C.UTF-8',LC_ALL='C.UTF-8')
    return value


def projected(profile: dict[str, Any], source: str) -> str:
    matches = [entry['target'] for entry in profile['readonly_mounts'] if entry['source'] == source]
    if len(matches) != 1: raise ValueError('fixed source requires one unambiguous jail projection')
    return matches[0]


def bootstrap(host: dict[str, Any], profile: dict[str, Any], lease: dict[str, Any], root: str,
              guardian_fd: int, barrier: int, pipes: tuple[int,int,int], close_fds: set[int]) -> None:
    """Only this fixed trusted function runs privileged in namespace init."""
    try:
        # clone creates this process directly as private PID namespace init. PPID
        # is invisible (0); inherited pidfd is the guardian-death race authority.
        prctl(1, signal.SIGKILL)
        wait_guardian(guardian_fd)
        # Immediately replace guardian control/evidence stdio with only the
        # candidate data pipes, then close ALL inherited handles except the
        # trusted early guardian-death and attach-barrier handles.
        for target_fd,data_fd in enumerate(pipes):os.dup2(data_fd,target_fd,inheritable=True)
        inherited={int(item.name) for item in Path('/proc/self/fd').iterdir() if item.name.isdigit()}
        for fd in inherited | close_fds:
            if fd>2 and fd not in {guardian_fd,barrier,*pipes}:
                try:os.close(fd)
                except OSError as exc:
                    if exc.errno!=errno.EBADF:raise
        ready = select.select([barrier,guardian_fd], [], [], 10)[0]
        if guardian_fd in ready or barrier not in ready or os.read(barrier,1) != b'A': os._exit(125)
        os.close(barrier)
        wait_guardian(guardian_fd)
        os.setsid()
        mount(None, '/', None, MS_REC | MS_PRIVATE)
        mount('tmpfs',root,'tmpfs',MS_NOSUID|MS_NODEV,'size=64m,mode=0755')
        for entry in profile['readonly_mounts']:
            target = Path(root+entry['target'])
            target.parent.mkdir(parents=True,exist_ok=True)
            target.touch(mode=0o444)
            mount(entry['source'],str(target),None,MS_BIND)
            mount(None,str(target),None,MS_BIND|MS_REMOUNT|MS_RDONLY|MS_NOSUID|MS_NODEV)
        app = Path(root,'app')
        app.mkdir(exist_ok=True)
        for name, value in [('actor-config.json',profile['config']),('paths.json',profile['paths']),('lease.json',lease)]:
            target = app/name
            # Never overwrite a mounted closure member.
            fd = os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
            try: os.write(fd,canonical(value))
            finally: os.close(fd)
        Path(root,'proc').mkdir()
        mount('proc',root+'/proc','proc',MS_RDONLY|MS_NOSUID|MS_NODEV|MS_NOEXEC)
        Path(root,'attempt').mkdir()
        mount('tmpfs',root+'/attempt','tmpfs',MS_NOSUID|MS_NODEV|MS_NOEXEC,'size=134217728,mode=0700')
        os.chown(root+'/attempt',host['candidate_uid'],host['candidate_gid'])
        for name in ('home','cache','tmp','shm'):
            path = root+'/attempt/'+name
            os.mkdir(path,0o700)
            os.chown(path,host['candidate_uid'],host['candidate_gid'])
        mount(None,root,None,MS_REMOUNT|MS_RDONLY|MS_NOSUID|MS_NODEV)
        os.chroot(root)
        os.chdir('/')
        # Lock resource elevation before dropping privilege.
        for key, maximum in ((resource.RLIMIT_CORE,0),(resource.RLIMIT_NOFILE,128),
                (resource.RLIMIT_NPROC,128),(resource.RLIMIT_MEMLOCK,0),
                (resource.RLIMIT_RTPRIO,0),(resource.RLIMIT_NICE,0)):
            resource.setrlimit(key,(maximum,maximum))
        os.sched_setscheduler(0,os.SCHED_OTHER,os.sched_param(0))
        os.setgroups([])
        # Drop all bounding capabilities while CAP_SETPCAP still exists.
        last = int(Path('/proc/sys/kernel/cap_last_cap').read_text())
        for capability in range(last+1): prctl(24,capability)
        prctl(47,4)  # PR_CAP_AMBIENT_CLEAR_ALL
        os.setresgid(host['candidate_gid'],host['candidate_gid'],host['candidate_gid'])
        os.setresuid(host['candidate_uid'],host['candidate_uid'],host['candidate_uid'])
        # UID change empties capabilities; explicitly capset verifies exact zeros.
        class Header(ctypes.Structure): _fields_ = [('version',ctypes.c_uint),('pid',ctypes.c_int)]
        class Data(ctypes.Structure): _fields_ = [('effective',ctypes.c_uint),('permitted',ctypes.c_uint),('inheritable',ctypes.c_uint)]
        libc_call('capset',ctypes.byref(Header(0x20080522,0)),ctypes.byref((Data*2)()))
        prctl(4,0)  # nondumpable after the final credential transition
        prctl(38,1) # no_new_privs
        prctl(1,signal.SIGKILL) # credentials reset PDEATHSIG, therefore re-arm now
        wait_guardian(guardian_fd)
        filter_sources = [path for path in profile['paths']['support_sources'] if Path(path).name == 'linux_runtime_filter.py']
        if len(filter_sources) != 1: raise ValueError('exact pinned runtime filter source required')
        source = filter_sources[0]
        if digest(Path(source).read_bytes()) != profile['paths']['support_sources'][source]:
            raise ValueError('runtime filter source changed')
        spec = importlib.util.spec_from_file_location('fixed_runtime_filter',source)
        if spec is None or spec.loader is None: raise ValueError('runtime filter loader missing')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.install_runtime_denial()
        wait_guardian(guardian_fd)
        for target_fd,fd in enumerate(pipes): os.dup2(fd,target_fd,inheritable=True)
        # Only the three candidate data pipes survive exec; pidfds, cgroup/root,
        # helper/evidence/control and all old-root descriptors are closed.
        open_fds = [int(item.name) for item in Path('/proc/self/fd').iterdir() if item.name.isdigit()]
        for fd in open_fds:
            if fd > 2:
                try: os.close(fd)
                except OSError as exc:
                    if exc.errno != errno.EBADF: raise
        backend = profile['config']['backend']
        python = projected(profile,backend['python'])
        script = projected(profile,backend['script'])
        os.execve(python,[python,'-B','-I','-S',script,'--'+lease['phase']],fixed_environment())
    except BaseException:
        os._exit(126)


class Child:
    def __init__(self,phase:str,root:str):
        self.phase=phase
        self.root=root
        self.pid=-1
        self.input_r=self.input_w=self.output_r=self.output_w=self.error_r=self.error_w=-1
        self.reaped=True
        self.returncode:int|None=None
        self.identity:Identity|None=None

    def launch(self,host:dict[str,Any],profile:dict[str,Any],lease:dict[str,Any],leaf:Leaf)->None:
        root=self.root
        self.input_r,self.input_w = os.pipe2(os.O_CLOEXEC)
        self.output_r,self.output_w = os.pipe2(os.O_CLOEXEC)
        self.error_r,self.error_w = os.pipe2(os.O_CLOEXEC)
        barrier_r,barrier_w = os.pipe2(os.O_CLOEXEC)
        guardian_fd = os.pidfd_open(os.getpid(),0)
        descriptors = {self.input_r,self.input_w,self.output_r,self.output_w,self.error_r,self.error_w,
                       barrier_r,barrier_w,guardian_fd,leaf.fd,leaf.parentfd}
        pid = -1
        try:
            number = {'x86_64':56,'aarch64':220}[platform.machine()]
            # No CLONE_VM/CLONE_THREAD: raw clone has fork semantics and requires
            # no userspace child stack. Guardian/bootstrap are single threaded.
            libc = ctypes.CDLL(None,use_errno=True)
            pid = libc.syscall(number,CLONE_NEWNS|CLONE_NEWPID|signal.SIGCHLD,0,0,0,0)
            if pid == -1:
                code=ctypes.get_errno()
                raise OSError(code,os.strerror(code),'clone namespace-init')
            if pid == 0:
                bootstrap(host,profile,lease,root,guardian_fd,barrier_r,
                          (self.input_r,self.output_w,self.error_w),descriptors)
                os._exit(126)
            self.pid=pid
            self.reaped=False
            self.identity = Identity(pid)
            leaf.write('cgroup.procs',str(pid))
            members = [int(value) for value in leaf.read('cgroup.procs').split()]
            if members != [pid]: raise ValueError('exact namespace-init attach readback differs')
            self.identity.verify()
            leaf.verify_limits()
            os.write(barrier_w,b'A')
        finally:
            for fd in (self.input_r,self.output_w,self.error_w,barrier_r,barrier_w,guardian_fd): os.close(fd)
            for fd in (self.output_r,self.error_r,self.input_w): os.set_blocking(fd,False)
        if self.identity is None: raise ValueError('namespace child identity missing')

    def poll(self) -> None:
        if self.reaped: return
        waited,status = os.waitpid(self.pid,os.WNOHANG)
        if waited:
            self.returncode = os.waitstatus_to_exitcode(status)
            self.reaped = True

    def close(self) -> None:
        for fd in (self.input_w,self.output_r,self.error_r):
            try: os.close(fd)
            except OSError as exc:
                if exc.errno != errno.EBADF: raise
        if self.identity is not None: self.identity.close()


def inspect_mounts(raw: str, targets: set[str]) -> dict[str, Any]:
    """Validate an external host-proc mount snapshot, never a child's claims."""
    rows = [line.split() for line in raw.splitlines()]
    seen: set[str] = set()
    writable = []
    for row in rows:
        if len(row) < 10 or '-' not in row:
            raise ValueError('invalid host mountinfo snapshot')
        split = row.index('-')
        target, flags, filesystem = row[4], set(row[5].split(',')), row[split+1]
        if target in seen or target not in targets | {'/', '/proc', '/attempt'}:
            raise ValueError('duplicate or undeclared mount in private root')
        seen.add(target)
        if 'rw' in flags:
            if target != '/attempt' or filesystem != 'tmpfs' or not {'nosuid','nodev','noexec'} <= flags:
                raise ValueError('unexpected writable mount or missing writable confinement')
            writable.append({'path':target,'fstype':filesystem,'bytes':134217728,
                             'flags':['rw','nosuid','nodev','noexec']})
        elif 'ro' not in flags or not {'nosuid','nodev'} <= flags:
            raise ValueError('readonly mount lacks immutable privilege controls')
        if target == '/proc' and (filesystem != 'proc' or 'noexec' not in flags):
            raise ValueError('private readonly proc mount differs')
        if filesystem.startswith('cgroup'):
            raise ValueError('cgroup filesystem exposed in private root')
    if seen != targets | {'/', '/proc', '/attempt'} or len(writable) != 1:
        raise ValueError('missing declared private-root mounts')
    return {'root_readonly':True,'proc_readonly':True,'writable_mounts':writable,
            'mountinfo_sha256':digest(raw.encode())}


def verify_ready(child: Child,host:dict[str,Any],profile:dict[str,Any],leaf:Leaf,
                 checkpoint:Callable[[],None]) -> dict[str,Any]:
    identity = child.identity
    if identity is None or leaf.identity is None:raise ValueError('READY pinned identity unavailable')
    identity.verify()
    pid = identity.pid
    status = parse_status(Path(f'/proc/{pid}/status').read_text())
    if ([int(x) for x in status['Uid'].split()] != [host['candidate_uid']]*4
            or [int(x) for x in status['Gid'].split()] != [host['candidate_gid']]*4
            or status['Groups'].strip() or status['NSpid'].split()[-1] != '1'
            or any(int(status[key],16) for key in ('CapEff','CapPrm','CapInh','CapAmb','CapBnd'))
            or status['NoNewPrivs'] != '1' or status['Seccomp'] != '2'
            or int(status.get('Seccomp_filters','0')) < 2):
        raise ValueError('actual READY credential/capability/PID/filter state differs')
    namespaces = {name:os.readlink(f'/proc/{pid}/ns/{name}') for name in ('mnt','pid')}
    if any(value == os.readlink('/proc/self/ns/'+name) for name,value in namespaces.items()):
        raise ValueError('actual child namespace is not private')
    members = [int(value) for value in leaf.read('cgroup.procs').split()]
    if members != [pid]: raise ValueError('READY has unexpected leaf members')
    if os.getsid(pid)==os.getsid(0) or os.getpgid(pid)==os.getpgid(0):
        raise ValueError('candidate session/process group is not separate from guardian')
    mount_facts = inspect_mounts(Path(f'/proc/{pid}/mountinfo').read_text(),
                                {entry['target'] for entry in profile['readonly_mounts']})
    attempt = Path(f'/proc/{pid}/root/attempt')
    fs = os.statvfs(attempt)
    if fs.f_blocks*fs.f_frsize != 134217728:
        raise ValueError('actual writable tmpfs is not exactly 128MiB')
    for item in Path(f'/proc/{pid}/fd').iterdir():
        if int(item.name) > 2 or not os.readlink(item).startswith('pipe:'):
            raise ValueError('candidate inherited a privileged or non-data descriptor')
    sources = []
    for entry in profile['readonly_mounts']:
        checkpoint()
        source = protected_path(entry['source'],True)
        target = Path(f'/proc/{pid}/root'+entry['target']).stat()
        if (source.st_dev,source.st_ino) != (target.st_dev,target.st_ino):
            raise ValueError('actual mount source inode binding differs')
        sources.append({'target':entry['target'],'source':entry['source'],
            'device':source.st_dev,'inode':source.st_ino,'sha256':entry['sha256']})
    # Independently identify executable and current native mappings from host proc.
    backend = profile['config']['backend']
    if digest(Path(f'/proc/{pid}/exe').read_bytes()) != backend['python_sha256']:
        raise ValueError('actual child interpreter pin differs')
    mapped=host_mappings(child,profile,sources)
    identity.verify()
    return {'role':'ready','pid':pid,'start':identity.start,'status':status,'namespaces':namespaces,
            'limits':leaf.verify_limits(),'sources':sources,'native_mappings':mapped,
            **mount_facts,
            'cgroup_identity':{'device':leaf.identity.st_dev,'inode':leaf.identity.st_ino,
                'mount_id':leaf.mount_id,'name':leaf.name},'tmpfs_bytes':134217728}


def host_mappings(child: Child, profile: dict[str, Any],
                  bindings:list[dict[str,Any]]) -> list[dict[str, Any]]:
    """Observe actual files by backing inode; host/jailed display names may differ."""
    identity=child.identity
    if identity is None:raise ValueError('loaded mapping process identity unavailable')
    identity.verify()
    index:dict[tuple[int,int],dict[str,Any]]={}
    for entry in bindings:
        key=(entry['device'],entry['inode'])
        if key in index:raise ValueError('ambiguous acquired source inode has multiple jailed targets')
        index[key]=entry
    found:dict[str,dict[str,Any]]={}
    for line in Path(f'/proc/{identity.pid}/maps').read_text().splitlines():
        fields=line.split(maxsplit=5)
        if len(fields)!=6 or not fields[5].startswith('/'):continue
        major,minor=fields[3].split(':')
        key=(os.makedev(int(major,16),int(minor,16)),int(fields[4]))
        mapping_entry=index.get(key)
        if mapping_entry is None:raise ValueError('unacquired actual native/model mapping inode')
        info=protected_path(mapping_entry['source'],True)
        if (info.st_dev,info.st_ino)!=key:
            raise ValueError('actual loaded backing inode changed after mount verification')
        target=mapping_entry['target']
        found[target]={'path':target,'source':mapping_entry['source'],'sha256':mapping_entry['sha256'],
                       'device':info.st_dev,'inode':info.st_ino}
    identity.verify()
    return [found[key] for key in sorted(found)]


def receipt_bytes(items: list[dict[str, Any]]) -> bytes:
    """Canonical protected receipt encoding; bounded before any file is published."""
    raw=b''.join(canonical(item)+b'\n' for item in items)
    if len(raw)>64*1024**2:raise ValueError('protected source receipt exceeds 64MiB')
    return raw


def attempt_deadlines(started: float, timeout: int, requested: Any) -> tuple[float,float]:
    """The earlier host start-based budget survives setup; a request may only narrow it."""
    if type(requested) not in (int,float) or not math.isfinite(requested):
        raise ValueError('finite numeric host deadline required')
    outer = min(started+timeout, requested)
    work = outer-10
    if work <= started:
        raise ValueError('shared work budget exhausted before setup; cleanup reserve cannot be spent')
    return work,outer


class Guardian:
    def __init__(self,request:dict[str,Any],host:dict[str,Any],profile:dict[str,Any],supervisor:Identity):
        self.request,self.host,self.profile,self.supervisor = request,host,profile,supervisor
        self.lease=os.urandom(24).hex()
        self.wire=Wire(self.lease)
        self.started=time.monotonic()
        timeout=profile['config']['timeout_seconds']
        if timeout not in (600,900): raise ValueError('unreviewed shared attempt deadline')
        self.work_deadline,self.deadline=attempt_deadlines(self.started,timeout,request['deadline_monotonic'])
        self.child:Child|None=None
        self.leaf:Leaf|None=None
        self.root: str|None=None
        self.phase: str|None=None
        self.last_sample:float|None=None
        self.broken_output=False
        self.stderr_total=0
        self.lockfd: int|None=None
        self.lock_path: str|None=None
        self.lock_identity: os.stat_result|None=None
        self.cleanup_deadline:float|None=None
        self.receipt_directory:str|None=None
        self.mapping_sequence=0
        self.observer_failure:str|None=None
        self.source_bindings:list[dict[str,Any]]=[]
        self.setup_unverified=False
        self.root_identity:os.stat_result|None=None

    def emit(self,event:str,**fields:Any)->None:
        raw=self.wire.event(event,**fields)
        if self.broken_output:return
        try:
            offset=0
            while offset<len(raw):
                ready=select.select([], [1], [], min(.1,max(0,self.deadline-time.monotonic())))[1]
                if not ready:
                    if time.monotonic()>=self.work_deadline: raise ValueError('protected output observer blocked')
                    continue
                offset+=os.write(1,raw[offset:])
        except (BrokenPipeError,OSError):
            self.broken_output=True
            raise ValueError('protected output observer lost')

    def receipt(self,role:str,items:list[dict[str,Any]],sequence:int|None=None)->None:
        if (role not in ('sources','native-mappings') or self.child is None
                or self.child.identity is None or self.phase is None):
            raise ValueError('fixed protected receipt role required')
        if self.receipt_directory is None:
            parent=str(Path(ANCHOR).parent)+'/receipts'
            try:os.mkdir(parent,0o755)
            except FileExistsError:protected_path(parent,False)
            self.receipt_directory=parent+'/'+self.lease
            os.mkdir(self.receipt_directory,0o755)
        name=self.phase+'-'+role+(f'-{sequence:06d}' if sequence is not None else '')+'.jsonl'
        raw=receipt_bytes(items)
        target=self.receipt_directory+'/'+name
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o400)
        try:
            offset=0
            while offset<len(raw):
                offset+=os.write(fd,raw[offset:])
            os.fsync(fd)
            os.fchmod(fd,0o444)
        finally:os.close(fd)
        facts={'role':role.replace('-','_'),'pid':self.child.identity.pid,
            'start':self.child.identity.start,'total':len(items),'sha256':digest(raw),'bytes':len(raw)}
        if sequence is not None:facts['sequence']=sequence
        self.emit('proof',phase=self.phase,facts=facts)

    def liveness(self)->None:
        if self.supervisor.dead():raise ValueError('supervisor pidfd reports death')
        if time.monotonic()>=self.work_deadline:raise ValueError('shared work deadline exhausted')
        if select.select([0],[],[],0)[0]:
            extra=os.read(0,1)
            raise ValueError('private control EOF' if not extra else 'unexpected private control bytes')

    def checkpoint(self)->None:
        self.liveness()
        if self.last_sample is None or time.monotonic()-self.last_sample>=SAMPLE_SECONDS:
            self.sample()

    def sample(self,enforce:bool=True)->None:
        if self.leaf is None:raise ValueError('resource leaf unavailable')
        facts=self.leaf.sample(self.child.identity if self.child and self.child.identity and not self.child.reaped else None,self.last_sample)
        self.last_sample=facts['monotonic']
        self.emit('resources',phase=self.phase,facts=facts)
        try:
            validate_resources(facts,self.leaf.cpus)
            if facts['gap_seconds'] is not None and facts['gap_seconds']>2:
                raise ValueError('observer gap exceeds 2s: '+str(facts['gap_seconds']))
        except ValueError as exc:
            self.observer_failure=str(exc)
            if enforce:raise
            self.emit('failure',error='final accounting: '+str(exc)[:1000])

    def teardown_phase(self)->tuple[bool,bool,int|None]:
        """The single bounded kill/reap path; no numeric PID/group is ever killed."""
        if self.leaf is None:return True,True,None
        self.leaf.write('cgroup.kill','1')
        empty=False
        child=self.child
        if self.cleanup_deadline is None:self.cleanup_deadline=min(self.deadline,time.monotonic()+10)
        cleanup_deadline=self.cleanup_deadline
        while time.monotonic()<cleanup_deadline:
            empty=not self.leaf.populated()
            if child:
                child.poll()
                dead=child.identity.dead() if child.identity is not None else child.reaped
                reaped=child.reaped
            else:dead,reaped=True,True
            if empty and dead and reaped:
                # Retain final accounting even after failure without claiming an
                # observation gap/reserve violation disappeared during cleanup.
                try:self.sample(False)
                except Exception as exc:
                    try:self.emit('failure',error='final accounting: '+str(exc)[:1000])
                    except Exception:pass
                    return False,reaped,child.returncode if child else None
                return True,True,child.returncode if child else None
            select.select([child.identity.fd] if child and child.identity and not dead else [],[],[],.05)
        return empty,bool(child is None or child.reaped),child.returncode if child else None

    def run_phase(self,phase:str)->None:
        self.phase=phase
        if self.leaf is None or self.root is None:raise ValueError('protected phase setup unavailable')
        self.liveness()
        lease={'schema':'linux-candidate-lease/v1','lease':self.lease,
               'authority':self.request['authority'],'profile_sha256':self.request['profile_sha256'],
               'candidate_uid':self.host['candidate_uid'],'candidate_gid':self.host['candidate_gid'],'phase':phase}
        # self.leaf/root are registered before clone so every exception reaches
        # pinned-leaf teardown. Child is constructed without any candidate input.
        child=Child(phase,self.root)
        self.child=child
        child.launch(self.host,self.profile,lease,self.leaf)
        if child.identity is None:raise ValueError('phase child identity unavailable')
        self.emit('phase_start',phase=phase,pid=child.identity.pid,start=child.identity.start)
        reader=FrameReader()
        ready=False
        stdout_eof=False
        stderr_eof=False
        selector=selectors.DefaultSelector()
        selector.register(child.output_r,selectors.EVENT_READ,'stdout')
        selector.register(child.error_r,selectors.EVENT_READ,'stderr')
        try:
            while not (stdout_eof and stderr_eof and child.reaped):
                self.liveness()
                now=time.monotonic()
                if self.last_sample is None or now-self.last_sample>=SAMPLE_SECONDS:self.sample()
                for key,_ in selector.select(.05):
                    raw=os.read(key.fd,65536)
                    if not raw:
                        selector.unregister(key.fd)
                        if key.data=='stdout':reader.eof();stdout_eof=True
                        else:stderr_eof=True
                        continue
                    if key.data=='stderr':
                        self.stderr_total+=len(raw)
                        if self.stderr_total>MAX_STDERR:raise ValueError('stderr journal cap exceeded')
                        # Keep actual bounded bytes in protected journal, never forward
                        # them as host statements or discard failures silently.
                        self.emit('proof',phase=phase,facts={'stderr_base64':base64.b64encode(raw[:32768]).decode()})
                        if len(raw)>32768:
                            self.emit('proof',phase=phase,facts={'stderr_base64':base64.b64encode(raw[32768:]).decode()})
                        continue
                    for packet in reader.feed(raw):
                        if not ready:
                            if packet.get('type')!='ready':raise ValueError('child spoke before READY')
                            facts=verify_ready(child,self.host,self.profile,self.leaf,self.checkpoint)
                            sources=facts.pop('sources')
                            mappings=facts.pop('native_mappings')
                            self.source_bindings=sources
                            self.receipt('sources',sources)
                            self.receipt('native-mappings',mappings,0)
                            self.mapping_sequence=1
                            facts['source_count']=len(sources)
                            facts['native_mapping_count']=len(mappings)
                            self.emit('proof',phase=phase,facts=facts)
                            ready=True
                            self.emit('frame',phase=phase,body=packet)
                            payload=canonical(self.request['request'])+b'\n'
                            sent=0
                            while sent<len(payload):
                                self.liveness()
                                if select.select([], [child.input_w], [], .05)[1]:
                                    sent+=os.write(child.input_w,payload[sent:])
                            # Keep only this explicit candidate data pipe for fixed
                            # observation handoffs; no privileged control handle leaks.
                        else:
                            if packet.get('type')=='ready':raise ValueError('duplicate child READY')
                            if packet.get('type')=='observation':
                                self.receipt('native-mappings',host_mappings(child,self.profile,self.source_bindings),self.mapping_sequence)
                                self.mapping_sequence+=1
                                ack=b'continue\n'
                                sent=0
                                while sent<len(ack):
                                    self.liveness()
                                    if select.select([], [child.input_w], [], .05)[1]:
                                        sent+=os.write(child.input_w,ack[sent:])
                            self.emit('frame',phase=phase,body=packet)
                            if packet.get('type')=='failure':raise ValueError('actual child failure: '+str(packet.get('error'))[:1000])
                child.poll()
            if not ready or child.returncode!=0:raise ValueError('child phase exited without valid READY/success')
            empty,reaped,code=self.teardown_phase()
            if not empty or not reaped:raise ValueError('phase teardown unverified')
            if self.observer_failure:raise ValueError('phase accounting failed: '+self.observer_failure)
            self.emit('phase_end',phase=phase,returncode=code,empty=True,reaped=True)
            child.close()
            self.child=None
            self.phase=None
            self.last_sample=None
            self.cleanup_deadline=None
        finally:selector.close()

    def run(self)->int:
        failed=False
        cleanup=False
        try:
            self.emit('lease',authority=self.request['authority'],profile_sha256=self.request['profile_sha256'])
            lock_parent=str(Path(ANCHOR).parent)
            protected_path(lock_parent,False)
            self.lock_path=lock_parent+'/candidate-'+str(self.host['candidate_uid'])+'.lease'
            self.lockfd=os.open(self.lock_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            self.lock_identity=os.fstat(self.lockfd)
            os.write(self.lockfd,self.lease.encode())
            candidate_unused(self.host['candidate_uid'],self.host['candidate_gid'])
            guardian_closure=verify_guardian_closure(self.host,self.liveness)
            self.leaf=Leaf(self.host['cgroup_parent'],self.lease,self.host['cpus'])
            root_parent=str(Path(ANCHOR).parent)
            protected_path(root_parent,False)
            self.root=root_parent+'/root-'+self.lease
            os.mkdir(self.root,0o700)
            self.root_identity=os.stat(self.root,follow_symlinks=False)
            self.emit('proof',phase=None,facts={'guardian_pid':os.getpid(),
                'role':'lease','authority':self.request['authority'],'profile_sha256':self.request['profile_sha256'],
                'guardian_start':Identity.read(os.getpid())['start'],'guardian_uid':os.getuid(),
                'supervisor_uid':self.host['supervisor_uid'],'supervisor_pid':self.supervisor.pid,
                'supervisor_start':self.supervisor.start,'shared_deadline':self.deadline,
                'work_deadline':self.work_deadline,'source_pins':self.host['support_sources'],
                'guardian_loaded_closure_sha256':digest(canonical(guardian_closure)),
                'guardian_loaded_closure_count':len(guardian_closure)})
            self.run_phase('preflight')
            self.run_phase('generate')
            cleanup=True
        except BaseException as exc:
            failed=True
            self.setup_unverified=isinstance(exc,UnverifiedSetupCleanup)
            try:self.emit('failure',error=type(exc).__name__+': '+str(exc)[:2000])
            except Exception:pass
        finally:
            try:
                if self.setup_unverified:raise ValueError('partial setup teardown is unverified')
                empty,reaped,code=self.teardown_phase()
                if self.child and self.child.identity and self.phase and empty and reaped:
                    self.emit('phase_end',phase=self.phase,returncode=code,empty=True,reaped=True)
                if not empty or not reaped:raise ValueError('bounded cleanup empty/dead/reaped evidence unavailable')
                if self.child:self.child.close();self.child=None
                if self.leaf:self.leaf.remove()
                if self.root and self.root_identity is not None:
                    current_root=os.stat(self.root,follow_symlinks=False)
                    if (current_root.st_dev,current_root.st_ino)!=(self.root_identity.st_dev,self.root_identity.st_ino):
                        raise ValueError('private-root directory identity changed')
                    # Namespace mounts disappeared with its init. The host root is
                    # its own empty directory, never recursively removed.
                    os.rmdir(self.root)
                if self.lockfd is not None:
                    if self.lock_path is None or self.lock_identity is None:
                        raise ValueError('exclusive candidate lease lock identity unavailable')
                    current=os.stat(self.lock_path,follow_symlinks=False)
                    if (current.st_dev,current.st_ino)!=(self.lock_identity.st_dev,self.lock_identity.st_ino):
                        raise ValueError('exclusive candidate identity lock changed')
                    os.unlink(self.lock_path)
                    os.close(self.lockfd)
                    self.lockfd=None
                failed=failed or self.observer_failure is not None
                self.emit('aborted' if failed else 'done',**teardown_receipt(not empty,True,reaped,True))
            except BaseException as exc:
                failed=True
                try:self.emit('failure',error='UNVERIFIED TEARDOWN: '+str(exc)[:2000])
                except Exception:pass
            self.supervisor.close()
        return 1 if failed or not cleanup else 0


def read_initial()->dict[str,Any]:
    raw=bytearray()
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        if not select.select([0],[],[],.1)[0]:continue
        chunk=os.read(0,1) # Do not buffer/consume the private control EOF.
        if not chunk:raise ValueError('private control closed before lease request')
        raw.extend(chunk)
        if len(raw)>MAX_INPUT:raise ValueError('lease request exceeds 1MiB')
        if chunk==b'\n':return validate_request(json.loads(raw))
    raise ValueError('lease request initial deadline exhausted')


def main()->int:
    if sys.argv[1:]!=['--lease']:raise ValueError('only the fixed --lease operation exists')
    if (sys.platform!='linux' or sys.byteorder!='little' or ctypes.sizeof(ctypes.c_void_p)!=8
            or platform.machine() not in ('x86_64','aarch64') or os.getresuid()!=(0,0,0)
            or len(list(Path('/proc/self/task').iterdir()))!=1
            or not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode):
        raise ValueError('native single-threaded root Linux guardian required')
    prctl(4,0)
    request=read_initial()
    host,profile=load_host(request)
    supervisor=supervisor_identity(host,request)
    os.set_blocking(1,False)
    # Foreground guardian must survive supervisor session termination. It watches
    # authenticated pidfd/control instead; namespace-init has its own death lock.
    signal.signal(signal.SIGHUP,signal.SIG_IGN)
    signal.signal(signal.SIGPIPE,signal.SIG_IGN)
    return Guardian(request,host,profile,supervisor).run()


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        sys.stderr.write(type(exc).__name__+': '+str(exc)[:2000]+'\n')
        raise SystemExit(1)
