#!/usr/bin/env python3
"""Fixed BUILD_ONLY capability. Public build data never appoints its own execution."""
from __future__ import annotations

import argparse
import hashlib
import http.client
import importlib.util
import json
import math
import os
import re
import selectors
import signal
import ssl
import stat
import struct
import subprocess
import sys
from pathlib import Path
import time
from typing import Any, Mapping
import urllib.request

PACKAGE = Path(__file__).resolve().parent
# A later independently reviewed source activation must appoint concrete identities.
# No environment, CLI argument, artifact or public selection can populate this slot.
_APPOINTED_EXECUTION: Mapping[str, Any] | None = None
MAX_FILE = 256 * 1024 * 1024
MAX_METADATA = 1024 * 1024
MAX_UMASK_FAULT = 8192  # Within the original 1MiB failure-metadata allowance.
MAX_BUNDLE = 2 * 1024 * 1024 * 1024
MAX_STREAM = 16 * 1024 * 1024
_UNSETTLED: list[subprocess.Popen[bytes]] = []
_CONTRACT_PINS = {
    'BUILD-SELECTION.schema.json': '649a27f158fc5dde36c7085d17d465cfdf534acf5f2f39b992b586b1a1e52616',
    'BUILD-RESULT.schema.json': '45508aa9c3dce95ee2e598d3ee3d5d3b585b6541d2555624540b3554733e70c6',
    'BUILD-FILES.schema.json': '10feb21744a7196796b3da5e0359043164d93cda55f713e849ed7a040ab80947',
    'LIMITS-AND-RECIPE.json': '6a7a76a793746700e7c7df561342b2638c76fe3c0d69affa0e27512f44af4f43',
    'HOLD-CODES.json': 'e190f156d8f3797f3a76fae0e976e559c93bd4aa2e957da4befdc58dfdb31792',
}

_source_spec = importlib.util.spec_from_file_location('xpdf_build_source', PACKAGE / 'prepare_source.py')
assert _source_spec and _source_spec.loader
_source = importlib.util.module_from_spec(_source_spec)
_source_spec.loader.exec_module(_source)


class BuildHold(ValueError):
    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code


def _contract(name: str) -> bytes:
    if name not in _CONTRACT_PINS:
        raise BuildHold('H_EXECUTION_SELECTION', 'unknown fixed source contract')
    raw = _stable_read(PACKAGE / 'build-contract' / name, MAX_METADATA)
    if _sha(raw) != _CONTRACT_PINS[name]:
        raise BuildHold('H_EXECUTION_SELECTION', 'fixed source contract drifted')
    return raw


def _fresh_environment(root: Path) -> dict[str, str]:
    return {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC',
            'HOME': str(root / 'home'), 'TMPDIR': str(root / 'tmp'), 'CMAKE_BUILD_PARALLEL_LEVEL': '2'}


def _empty_custody() -> dict[str, Any]:
    return {'schema': 'twin.xpdf-build-command-custody/v1', 'command_binding_sha256': None,
            'leader_pid': None, 'reservation': 'NO_CHILD_CREATED', 'wait_kind': 'UNOBSERVED',
            'raw_wait': None, 'exit_code': None, 'signal': None, 'direct_reap': 'UNOBSERVED',
            'group_absence': 'UNOBSERVED', 'cleanup_started': None, 'cleanup_deadline': None,
            'cleanup_ended': None, 'signals': [], 'observations': [], 'workspace': 'RETAINED'}


def _record(custody: dict[str, Any], kind: str, at: float | None, detail: dict[str, Any]) -> dict[str, Any]:
    events = custody['observations']
    if len(events) >= 32 or (kind == 'signal-attempt' and len(custody['signals']) >= 8) or (kind == 'group-probe' and sum(e['kind'] == kind for e in events) >= 16):
        raise BuildHold('H_CUSTODY', 'custody journal overflow')
    event = {'ordinal': len(events), 'kind': kind, 'at': at, 'detail': detail}
    events.append(event)
    return event


def _supervise(result: dict[str, Any], phase: str, argv: list[str], cwd: Path,
               environment: dict[str, str], allowance: float, payload: dict[str, tuple[bytes, str]], *, terminal_reserve: int = 0) -> dict[str, Any]:
    """One private fixed-command route; all OS effects modeled in source-only tests."""
    _require(type(terminal_reserve) is int and terminal_reserve in (0, 10), 'fixed private terminal reserve')
    limits = _load_json(_contract('LIMITS-AND-RECIPE.json'))
    _require(_permitted_dispatch(argv, phase), 'forbidden executable/target/worker dispatch')
    if len(result['commands']) >= 256:
        raise BuildHold('H_CAPACITY', 'command record count exhausted')
    budget = next(p for p in limits['phases'] if p['id'] == phase)
    custody = _empty_custody()
    absent = {'sha256': None, 'retained_bytes': 0, 'observed_bytes_lower_bound': 0, 'state': 'ABSENT'}
    command = {'id': f'{phase}/{len(result["commands"]):03}', 'phase': phase, 'argv': argv,
               'environment_sha256': result['environment_manifest_sha256'], 'started': None,
               'deadline': None, 'ended': None, 'stdout': dict(absent), 'stderr': dict(absent),
               'custody': custody, 'disposition': 'HELD'}
    result['commands'].append(command)  # launch uncertainty must survive a missing return.
    try:
        started = time.monotonic()
        command['started'] = started
        original = result['clock']['started']
        deadline = started + allowance
        if deadline + terminal_reserve > min(original + budget['cumulative_end_seconds'], result['clock']['deadline']):
            raise BuildHold('H_DEADLINE', 'original phase allowance unavailable')
        command['deadline'] = deadline
    except BaseException as error:
        command['disposition'] = 'INTERRUPTED' if not isinstance(error, Exception) else 'HELD'
        raise
    process = None
    selector = None
    data = {'stdout': bytearray(), 'stderr': bytearray()}
    observed = {'stdout': 0, 'stderr': 0}
    eof: set[str] = set()
    overflow = False
    saved: BaseException | None = None
    cleanup_error: BaseException | None = None
    reaping = False
    reaped = False
    previous_logs = sum(c[s]['retained_bytes'] for c in result['commands'][:-1] for s in ('stdout', 'stderr'))

    def drain(timeout: float) -> None:
        nonlocal overflow
        if selector is None:
            return
        _scratch_usage(Path(environment['HOME']).parent)
        for key, _ in selector.select(max(0, min(timeout, 0.1))):
            stream_name = key.data
            remaining = min(MAX_STREAM - len(data[stream_name]), 256 * 1024 * 1024 - previous_logs - sum(map(len, data.values())),
                            MAX_BUNDLE - MAX_METADATA - sum(len(v[0]) for v in payload.values()) - sum(map(len, data.values())))
            value = os.read(key.fd, min(65536, max(1, remaining + 1)))
            observed[stream_name] += len(value)
            if not value:
                selector.unregister(key.fileobj)
                eof.add(stream_name)
            else:
                data[stream_name].extend(value[:max(0, remaining)])
                if len(value) > remaining:
                    overflow = True

    def send(number: int) -> None:
        if reaping:
            raise BuildHold('H_CUSTODY', 'refused destructive signal after first consuming wait')
        at = time.monotonic()
        if custody['cleanup_deadline'] is None or at >= custody['cleanup_deadline']:
            raise BuildHold('H_CUSTODY', 'cleanup signal deadline unavailable')
        detail = {'target': 'OWNED_GROUP', 'pid': custody['leader_pid'], 'signal': number, 'outcome': None}
        event = _record(custody, 'signal-attempt', at, detail)
        projection = dict(detail, at=at)
        custody['signals'].append(projection)
        try:
            os.killpg(custody['leader_pid'], number)
            outcome = 'SENT'
        except ProcessLookupError:
            outcome = 'ABSENT'
        except PermissionError:
            outcome = 'PERMISSION_DENIED'
        except OSError:
            outcome = 'OS_ERROR'
        event['detail']['outcome'] = projection['outcome'] = outcome

    def reap_group() -> None:
        nonlocal reaping, reaped
        assert process is not None
        # Set the cutoff before allocating the marker or entering a consuming wait.
        reaping = True
        _record(custody, 'reaping-start', time.monotonic(), {'leader_pid': process.pid, 'operation': 'FIRST_CONSUMING_WAIT'})
        while time.monotonic() < custody['cleanup_deadline']:
            pid, raw_wait = os.waitpid(process.pid, os.WNOHANG)
            if pid == process.pid and (os.WIFEXITED(raw_wait) or os.WIFSIGNALED(raw_wait)):
                reaped = True
                exit_code = os.WEXITSTATUS(raw_wait) if os.WIFEXITED(raw_wait) else None
                number = os.WTERMSIG(raw_wait) if os.WIFSIGNALED(raw_wait) else None
                process.returncode = exit_code if exit_code is not None else -(number or 0)
                detail = {'leader_pid': process.pid, 'wait_kind': 'EXITED' if exit_code is not None else 'SIGNALED',
                          'raw_wait': raw_wait, 'exit_code': exit_code, 'signal': number}
                _record(custody, 'direct-reap', time.monotonic(), detail)
                custody.update({k: detail[k] for k in ('wait_kind', 'raw_wait', 'exit_code', 'signal')})
                custody['direct_reap'] = 'OBSERVED'
                break
            drain(0.1)
        if reaped:
            while time.monotonic() < custody['cleanup_deadline'] and len(eof) < 2 and not overflow:
                drain(0.1)
            detail = {'leader_pid': process.pid, 'outcome': None}
            event = _record(custody, 'group-probe', time.monotonic(), detail)
            try:
                os.killpg(process.pid, 0)
                outcome = 'PRESENT'
            except ProcessLookupError:
                outcome = 'ABSENT'
            except PermissionError:
                outcome = 'PERMISSION_DENIED'
            except OSError:
                outcome = 'OS_ERROR'
            event['detail']['outcome'] = outcome
            custody['group_absence'] = outcome if outcome in ('ABSENT', 'PRESENT') else 'UNOBSERVED'

    def finish_cleanup() -> None:
        custody['cleanup_ended'] = time.monotonic()
        _record(custody, 'cleanup-end', custody['cleanup_ended'], {})

    try:
        # Record uncertain launch before entering Popen; a raised call is not proof no child exists.
        custody['reservation'] = 'UNESTABLISHED'
        process = subprocess.Popen(argv, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
                                   close_fds=True)
        custody.update(leader_pid=process.pid, reservation='UNREAPED_DIRECT_LEADER')
        custody['command_binding_sha256'] = _binding(result, command)
        selector = selectors.DefaultSelector()
        assert process.stdout and process.stderr
        for name, stream in [('stdout', process.stdout), ('stderr', process.stderr)]:
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while time.monotonic() < deadline - 2:
            drain(0.1)
            if overflow:
                raise BuildHold('H_STREAM_LIMIT', 'bounded raw stream overflow')
            peek = os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            if peek is not None and peek.si_pid == process.pid and len(eof) == 2:
                break
        else:
            raise BuildHold('H_DEADLINE', 'command original allowance exhausted')
    except BaseException as error:
        saved = error
    finally:
        # Includes deadline acquisition: a secondary clock/cancellation must not replace saved.
        try:
            if process is not None:
                cleanup_started = time.monotonic()
                custody['cleanup_started'] = cleanup_started
                custody['cleanup_deadline'] = min(cleanup_started + 2, deadline, result['clock']['deadline'])
                _record(custody, 'cleanup-start', cleanup_started, {'selected_deadline': custody['cleanup_deadline']})
                send(signal.SIGTERM)
                kill_at = min(cleanup_started + 1, custody['cleanup_deadline'])
                while time.monotonic() < kill_at:
                    drain(min(0.1, kill_at - time.monotonic()))
                send(signal.SIGKILL)
                reap_group()
                finish_cleanup()
        except BaseException as error:
            cleanup_error = error
            # Best effort only while the same deadline and unreaped reservation remain.
            # Never retry/continue the consuming-wait route or renew the grace.
            try:
                if process is not None and not reaping and custody['cleanup_deadline'] is not None:
                    send(signal.SIGKILL)
                    reap_group()
                    finish_cleanup()
            except BaseException:
                pass
        finally:
            # Never let Popen.__del__ introduce an unjournaled wait on an unsettled leader.
            if process is not None and not reaped:
                _UNSETTLED.append(process)
            try:
                if selector is not None:
                    selector.close()
                if process is not None:
                    for open_stream in (process.stdout, process.stderr):
                        if open_stream is not None:
                            open_stream.close()
            except BaseException as error:
                if cleanup_error is None:
                    cleanup_error = error
            try:
                command['ended'] = time.monotonic()
            except BaseException as error:
                if cleanup_error is None:
                    cleanup_error = error
            for name in ('stdout', 'stderr'):
                raw = bytes(data[name])
                path = f'journal/{len(result["commands"])-1:03}-{name}.log'
                payload[path] = (raw, 'raw-log')
                command[name] = {'sha256': _sha(raw), 'retained_bytes': len(raw), 'observed_bytes_lower_bound': observed[name],
                                 'state': 'COMPLETE' if name in eof and not overflow else 'PREFIX_ONLY'}
    if saved is not None:
        command['disposition'] = 'INTERRUPTED' if not isinstance(saved, Exception) else 'HELD'
        raise saved
    if cleanup_error is not None:
        command['disposition'] = 'INTERRUPTED' if not isinstance(cleanup_error, Exception) else 'HELD'
        raise cleanup_error
    if overflow:
        raise BuildHold('H_STREAM_LIMIT', 'bounded raw stream overflow')
    if (not reaped or custody['group_absence'] != 'ABSENT' or command['ended'] is None
            or custody['cleanup_ended'] > custody['cleanup_deadline'] or command['ended'] > deadline
            or any(command[s]['state'] != 'COMPLETE' for s in ('stdout', 'stderr'))):
        raise BuildHold('H_CUSTODY', 'unestablished cleanup; owned workspace retained')
    if custody['exit_code'] != 0:
        command['disposition'] = 'FAILED'
        raise BuildHold('H_TOOLS', 'fixed command nonzero/signal exit')
    command['disposition'] = 'EXIT0_COMPLETE'
    return command


def _stable_read(path: Path, maximum: int = MAX_FILE) -> bytes:
    parent = _source._directory_fd(path.parent)
    fd = None
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise BuildHold('H_EXPORT', 'nonregular or oversized retained file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(maximum + 1)
        after = os.fstat(fd)
        current = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        def identity(value: os.stat_result) -> tuple[int, ...]:
            return (value.st_dev, value.st_ino, value.st_mode, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if len(raw) > maximum or len(raw) != before.st_size or identity(before) != identity(after) or identity(after) != identity(current):
            raise BuildHold('H_EXPORT', 'unstable retained file')
        return raw
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent)


def _scratch_usage(root: Path) -> None:
    total = count = 0
    for parent, directories, files in os.walk(root, followlinks=False):
        for name in directories:
            if (Path(parent) / name).is_symlink():
                raise BuildHold('H_CAPACITY', 'symlink in owned build workspace')
        for name in files:
            info = (Path(parent) / name).lstat()
            if not stat.S_ISREG(info.st_mode):
                raise BuildHold('H_CAPACITY', 'special file in owned build workspace')
            count += 1
            total += info.st_size
            if count > 32768 or total > MAX_BUNDLE or info.st_size > MAX_FILE:
                raise BuildHold('H_CAPACITY', 'observed scratch capacity overflow; polling is not a quota')


def _payload_add(payload: dict[str, tuple[bytes, str]], name: str, raw: bytes, role: str) -> None:
    if (not _safe_name(name) or name in payload or len(raw) > MAX_FILE or len(payload) >= 32768
            or (role == 'metadata' and len(raw) > MAX_METADATA)
            or sum(len(v[0]) for v in payload.values()) + len(raw) > MAX_BUNDLE - 16 * 1024 * 1024):
        raise BuildHold('H_CAPACITY', 'retained artifact allowance exceeded')
    payload[name] = (raw, role)


def _output_parent(root: Path, name: str) -> int:
    if not _safe_name(name):
        raise BuildHold('H_EXPORT', 'unsafe output path')
    fd = _source._directory_fd(root)
    try:
        for part in name.split('/')[:-1]:
            try:
                os.mkdir(part, 0o700, dir_fd=fd)
            except FileExistsError:
                pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _tree(root: Path, prefix: str, payload: dict[str, tuple[bytes, str]], source: bool = False) -> dict[str, dict[str, Any]]:
    manifest = {}
    for parent, directories, files in os.walk(root, followlinks=False):
        if any((Path(parent) / name).is_symlink() for name in directories):
            raise BuildHold('H_EXPORT', 'output directory symlink')
        for name in sorted(files):
            path = Path(parent) / name
            relative = path.relative_to(root).as_posix()
            raw = _stable_read(path)
            role = 'source' if source else ('binary' if relative == 'xpdf/pdftotext' else 'object' if name.endswith('.o') else 'library' if name.endswith('.a') else 'config')
            _payload_add(payload, prefix + '/' + relative, raw, role)
            manifest[relative] = {'bytes': len(raw), 'sha256': _sha(raw)}
    return manifest


def _fixed_configure(source: Path, build: Path, root: Path, release: str) -> list[str]:
    definitions = dict(_load_json(_contract('LIMITS-AND-RECIPE.json'))['configure']['definitions'])
    definitions['CMAKE_SYSTEM_VERSION'] = release
    definitions['CMAKE_INSTALL_PREFIX'] = str(root / 'unused-install')
    return ['/usr/bin/cmake', '-G', 'Unix Makefiles', str(source)] + [f'-D{key}={definitions[key]}' for key in sorted(definitions)]


def _appointment(selection: Mapping[str, Any]) -> Mapping[str, Any]:
    appointed = _APPOINTED_EXECUTION
    if appointed is None or appointed.get('selection_sha256') != _sha(_json(dict(selection))):
        raise BuildHold('H_EXECUTION_SELECTION', 'actual execution source selection is not appointed')
    required = {'selection_sha256', 'bootstrap', 'modules', 'tools', 'capacity', 'source_transport', 'run', 'linux_release'}
    if set(appointed) != required:
        raise BuildHold('H_EXECUTION_SELECTION', 'incomplete private source-appointed prerequisites')
    for name in _CONTRACT_PINS:
        _contract(name)
    for field, code in [('bootstrap', 'H_BOOTSTRAP'), ('modules', 'H_PROBE_EXECUTION_UNESTABLISHED'),
                        ('tools', 'H_TOOLS'), ('capacity', 'H_CAPACITY'), ('source_transport', 'H_SOURCE_TRANSPORT'), ('run', 'H_EXECUTION_SELECTION')]:
        if not appointed[field]:
            raise BuildHold(code, 'actual independently selected prerequisite absent: ' + field)
    if selection['driver_sha256'] != _sha(_stable_read(Path(__file__))) or selection['preparer_sha256'] != _sha(_stable_read(PACKAGE / 'prepare_source.py')):
        raise BuildHold('H_EXECUTION_SELECTION', 'selected driver/preparer bytes drifted')
    if selection['source_package_sha256'] != _sha(_stable_read(PACKAGE / 'SOURCE-PINS.json')):
        raise BuildHold('H_SOURCE_CONSERVATION', 'selected source package drifted')
    if not isinstance(appointed['linux_release'], str) or not re.fullmatch(r'[A-Za-z0-9._+\-]{1,128}', appointed['linux_release']):
        raise BuildHold('H_BOOTSTRAP', 'actual Linux release unobserved')
    return appointed


def _selected_files(selection: Mapping[str, Any], appointed: Mapping[str, Any], payload: dict[str, tuple[bytes, str]]) -> None:
    # These are source-appointed exact actual facts, not public flags or caller-selected file lists.
    bootstrap = appointed['bootstrap']
    modules = appointed['modules']
    if _sha(_json(bootstrap)) != selection['bootstrap_selection_sha256']:
        raise BuildHold('H_BOOTSTRAP', 'bootstrap association differs')
    if _sha(_json(modules)) != selection['tool_module_review_sha256']:
        raise BuildHold('H_PROBE_EXECUTION_UNESTABLISHED', 'actual Linux module review differs')
    if not all(modules['files'].get(record['resolved']) == record['sha256'] for record in appointed['tools'].values()):
        raise BuildHold('H_PROBE_EXECUTION_UNESTABLISHED', 'actual selected tool files outside independently held module/toolchain review')
    for role, record, code in [('bootstrap', bootstrap, 'H_BOOTSTRAP'), ('tool', modules, 'H_PROBE_EXECUTION_UNESTABLISHED')]:
        if set(record) != {'files', 'review_sha256'} or not record['files'] or not re.fullmatch('[a-f0-9]{64}', record['review_sha256']):
            raise BuildHold(code, 'unestablished source-appointed review/files')
        for index, (name, pin) in enumerate(sorted(record['files'].items())):
            raw = _stable_read(Path(name))
            if _sha(raw) != pin:
                raise BuildHold(code, 'selected actual file drifted')
            _payload_add(payload, f'inputs/{role}/{index:04}.bin', raw, role)
        _payload_add(payload, f'{role.upper()}-SELECTION.json', _json(record), 'metadata')
    if set(appointed['capacity']) != {'acceptance_sha256', 'minimum_free_bytes'} or not re.fullmatch('[a-f0-9]{64}', appointed['capacity']['acceptance_sha256']):
        raise BuildHold('H_CAPACITY', 'unaccepted actual capacity condition')
    if (set(appointed['source_transport']) != {'selection_sha256', 'ssl_files', 'ca_file'}
            or not appointed['source_transport']['ssl_files']
            or appointed['source_transport']['ca_file'] not in appointed['source_transport']['ssl_files']):
        raise BuildHold('H_SOURCE_TRANSPORT', 'fixed HTTPS/bootstrap trust association unestablished')
    for name, pin in appointed['source_transport']['ssl_files'].items():
        raw = _stable_read(Path(name))
        if _sha(raw) != pin:
            raise BuildHold('H_SOURCE_TRANSPORT', 'selected SSL/trust bytes drifted')
        _payload_add(payload, f'inputs/ssl/{len(payload):04}.bin', raw, 'bootstrap')
    _payload_add(payload, 'SOURCE-TRANSPORT-SELECTION.json', _json(appointed['source_transport']), 'metadata')
    _payload_add(payload, 'RUN-ASSOCIATION.json', _json(appointed['run']), 'metadata')


def _tool_inventory(result: dict[str, Any], root: Path, environment: dict[str, str], appointed: Mapping[str, Any], payload: dict[str, tuple[bytes, str]]) -> None:
    selectors_fixed = _load_json(_contract('LIMITS-AND-RECIPE.json'))['tools']['fixed_selectors']
    expected = appointed['tools']
    if not set(selectors_fixed).issubset(expected):
        raise BuildHold('H_TOOLS', 'actual fixed tool closure missing')
    inventory: dict[str, Any] = {}
    for index, name in enumerate(sorted(expected)):
        path = Path(name)
        resolved = path.resolve(strict=True)
        info = resolved.stat()
        raw = _stable_read(resolved)
        if info.st_uid != 0 or info.st_mode & 0o022 or raw[:4] != b'\x7fELF' or _sha(raw) != expected[name]['sha256'] or str(resolved) != expected[name]['resolved']:
            raise BuildHold('H_TOOLS', 'tool route/owner/ELF/source identity differs')
        route = []
        current = path
        for _ in range(32):
            entry = current.lstat()
            if entry.st_uid != 0 or entry.st_mode & 0o022 and not stat.S_ISLNK(entry.st_mode):
                raise BuildHold('H_TOOLS', 'tool route is writable/unowned')
            if not stat.S_ISLNK(entry.st_mode):
                break
            target = os.readlink(current)
            route.append({'path': str(current), 'target': target})
            current = Path(target) if target.startswith('/') else current.parent / target
        else:
            raise BuildHold('H_TOOLS', 'tool symlink route overflow')
        if route != expected[name]['links']:
            raise BuildHold('H_TOOLS', 'tool link route changed')
        _payload_add(payload, f'inputs/tools/{index:04}.bin', raw, 'tool')
        observation = {key: getattr(info, 'st_' + key) for key in ('uid', 'mode', 'dev', 'ino', 'size', 'mtime_ns', 'ctime_ns')}
        inventory[name] = dict(expected[name], observation=observation)
    for name in selectors_fixed:
        if name == '/bin/sh':
            continue  # dash has no GNU --version contract; retain its selected ELF bytes/route.
        command = _supervise(result, 'bootstrap-input-tools', [name, '--version'], root, environment, 5, payload)
        stdout = next(raw for raw, _ in payload.values() if _sha(raw) == command['stdout']['sha256'])
        if b'GNU' not in stdout and name != '/usr/bin/cmake':
            raise BuildHold('H_TOOLS', 'selected build tool is not GNU')
        if name == '/usr/bin/cmake':
            match = re.search(rb'cmake version (\d+)\.(\d+)\.', stdout)
            if match is None or (int(match[1]), int(match[2])) < (3, 24):
                raise BuildHold('H_TOOLS', 'CMake guard semantics unsupported')
    for compiler, option, expected_path in [('/usr/bin/gcc', '-print-prog-name=cc1', 'cc1'), ('/usr/bin/g++', '-print-prog-name=cc1plus', 'cc1plus'), ('/usr/bin/gcc', '-print-prog-name=collect2', 'collect2')]:
        command = _supervise(result, 'bootstrap-input-tools', [compiler, option], root, environment, 5, payload)
        selected_stdout = next(raw for raw, _ in payload.values() if _sha(raw) == command['stdout']['sha256']).decode('ascii').strip()
        if selected_stdout not in expected or Path(selected_stdout).name != expected_path:
            raise BuildHold('H_TOOLS', 'GCC selected internal tool unreviewed')
    command = _supervise(result, 'bootstrap-input-tools', ['/usr/bin/gcc', '-dumpmachine'], root, environment, 5, payload)
    triple = next(raw for raw, _ in payload.values() if _sha(raw) == command['stdout']['sha256']).decode('ascii').strip()
    if not re.fullmatch(r'x86_64-(?:[A-Za-z0-9_]+-)?linux(?:-[A-Za-z0-9_]+)*', triple):
        raise BuildHold('H_ELF_ASSOCIATION', 'actual compiler target is not x86_64 Linux')
    command = _supervise(result, 'bootstrap-input-tools', ['/usr/bin/gcc', '-dumpspecs'], root, environment, 5, payload)
    inventory['compiler_target'] = triple
    inventory['specs_sha256'] = command['stdout']['sha256']
    raw = _json(inventory)
    _payload_add(payload, 'TOOL-MANIFEST.json', raw, 'metadata')
    result['tool_manifest_sha256'] = _sha(raw)


def _fixed_tool_queries() -> list[list[str]]:
    selectors = _load_json(_contract('LIMITS-AND-RECIPE.json'))['tools']['fixed_selectors']
    return [[name, '--version'] for name in selectors if name != '/bin/sh'] + [
        ['/usr/bin/gcc', '-print-prog-name=cc1'], ['/usr/bin/g++', '-print-prog-name=cc1plus'],
        ['/usr/bin/gcc', '-print-prog-name=collect2'], ['/usr/bin/gcc', '-dumpmachine'], ['/usr/bin/gcc', '-dumpspecs']]


def _fixed_fetch(output: Any) -> None:
    """Internal fixed data child; unavailable until a new reviewed source appointment."""
    if _APPOINTED_EXECUTION is None or not _APPOINTED_EXECUTION.get('source_transport'):
        raise BuildHold('H_SOURCE_TRANSPORT', 'actual fixed source transport is not appointed')
    profile = _load_json(_contract('LIMITS-AND-RECIPE.json'))['archive']
    class HeaderReader:
        def __init__(self, stream: Any):
            self.stream = stream
            self.remaining = 32768
            self.headers_done = False

        def readline(self, maximum: int = -1) -> bytes:
            bound = maximum if self.headers_done else min(maximum if maximum >= 0 else 32769, self.remaining + 1)
            value = self.stream.readline(bound)
            if not self.headers_done:
                self.remaining -= len(value)
                if self.remaining < 0:
                    raise BuildHold('H_SOURCE_TRANSPORT', 'fixed HTTPS headers overflow')
                if value in (b'\r\n', b'\n'):
                    self.headers_done = True
            return value

        def __getattr__(self, name: str) -> Any:
            return getattr(self.stream, name)

    class Response(http.client.HTTPResponse):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)
            self.fp = HeaderReader(self.fp)  # type: ignore[assignment]

        def _read_status(self) -> Any:
            value = getattr(super(), '_read_status')()
            if value[1] != 200:
                raise BuildHold('H_SOURCE_TRANSPORT', 'fixed HTTPS non200/redirect/interim status')
            return value

    transport = _APPOINTED_EXECUTION['source_transport']
    ca_file = transport['ca_file']
    if ca_file not in transport['ssl_files'] or _sha(_stable_read(Path(ca_file))) != transport['ssl_files'][ca_file]:
        raise BuildHold('H_SOURCE_TRANSPORT', 'selected actual CA file drifted/absent')
    context = ssl.create_default_context(cafile=ca_file)
    # Direct literal HTTPSConnection has no proxy/mirror/redirect/cookie handler.
    connection = http.client.HTTPSConnection('dl.xpdfreader.com', timeout=25, context=context)
    connection.response_class = Response
    try:
        connection.request('GET', '/xpdf-4.06.tar.gz', headers={'Accept-Encoding': 'identity'})
        response = connection.getresponse()
        if response.status != 200 or response.headers.get('Content-Encoding', 'identity').lower() != 'identity':
            raise BuildHold('H_SOURCE_TRANSPORT', 'fixed HTTPS status/route/encoding differs')
        headers = str(response.headers).encode('utf-8')
        if len(headers) > 32768:
            raise BuildHold('H_SOURCE_TRANSPORT', 'fixed HTTPS headers overflow')
        # Public bounded response facts use stderr; stdout is only the bounded raw body.
        sys.stderr.buffer.write(_json({'url': profile['url'], 'status': response.status, 'headers': headers.decode('utf-8')}))
        observed = 0
        checksum = hashlib.sha256()
        while observed <= profile['bytes']:
            block = response.read(min(65536, profile['bytes'] + 1 - observed))
            if not block:
                break
            prefix = block[:max(0, profile['bytes'] - observed)]
            observed += len(block)
            output.write(prefix)
            output.flush()
            checksum.update(block)
        sys.stderr.buffer.write(_json({'observed_body_bytes_lower_bound': observed, 'body_overflow': observed > profile['bytes']}))
        if observed != profile['bytes'] or checksum.hexdigest() != profile['sha256']:
            raise BuildHold('H_SOURCE_TRANSPORT', 'fixed source archive length/hash/overflow differs')
    finally:
        connection.close()


def _command_output(command: dict[str, Any], payload: dict[str, tuple[bytes, str]], stream: str = 'stdout') -> bytes:
    return next(raw for raw, _ in payload.values() if _sha(raw) == command[stream]['sha256'])


def _source_pair(root: Path, raw: bytes, result: dict[str, Any], environment: dict[str, str], payload: dict[str, tuple[bytes, str]]) -> dict[str, Any]:
    archive = _source.archive_files(raw)
    pins, package = _source.source_package()
    pristine = _source.materialize_source(archive, root / 'pristine-source')
    instrumented_files = dict(archive)
    for name in ('TwinOrigin.h', 'TwinOrigin.cc'):
        instrumented_files['xpdf/' + name] = package[name]
    instrumented = _source.materialize_source(instrumented_files, root / 'instrumented-source')
    patch_path = root / 'inputs' / 'xpdf-4.06-origin.patch'
    fd = os.open(patch_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(package['xpdf-4.06-origin.patch'])
    command = _supervise(result, 'two-source-preparations', ['/usr/bin/patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(patch_path)], instrumented, environment, 30, payload)
    if re.search(rb'offset|fuzz|reject', _command_output(command, payload) + _command_output(command, payload, 'stderr'), re.I):
        raise BuildHold('H_SOURCE_CONSERVATION', 'patch offset/fuzz/reject diagnostic')
    _source.verify_prepared(instrumented, pins)
    first = _tree(pristine, 'pristine/source', payload, True)
    second = _tree(instrumented, 'instrumented/source', payload, True)
    expected = set(first) | {'xpdf/TwinOrigin.h', 'xpdf/TwinOrigin.cc'}
    if set(second) != expected or any(second[n] != first[n] for n in first if n not in pins['patched_sources']):
        raise BuildHold('H_SOURCE_CONSERVATION', 'unaccepted full-tree source delta')
    for name, record in pins['patched_sources'].items():
        if second.get(name) != record:
            raise BuildHold('H_SOURCE_CONSERVATION', 'accepted patched source pin differs')
    for name, value in package.items():
        _payload_add(payload, 'package/' + name, value, 'notice' if name.startswith('upstream-notices/') else 'package')
    _payload_add(payload, 'package/SOURCE-PINS.json', _stable_read(PACKAGE / 'SOURCE-PINS.json'), 'package')
    for variant, manifest in [('pristine', first), ('instrumented', second)]:
        _payload_add(payload, variant + '/SOURCES.json', _json(manifest), 'metadata')
    conservation = {'schema': 'twin.xpdf-build-source-conservation/v1', 'archive_sha256': _sha(raw),
                    'source_package_sha256': _sha(_stable_read(PACKAGE / 'SOURCE-PINS.json')),
                    'pristine': first, 'instrumented': second}
    value = _json(conservation)
    _payload_add(payload, 'SOURCE-CONSERVATION.json', value, 'metadata')
    result['source_conservation_sha256'] = _sha(value)
    return {'pristine': first, 'instrumented': second}


def _logical_cache(cache_raw: bytes, root: Path, source: Path, build: Path, argv: list[str]) -> dict[str, Any]:
    entries = {}
    for line in cache_raw.decode('utf-8').splitlines():
        if not line or line.startswith(('#', '//')):
            continue
        match = re.fullmatch(r'([^:=]+):([^=]+)=(.*)', line)
        if match is None or match[1] in entries:
            raise BuildHold('H_CONFIG_EQUIVALENCE', 'invalid/duplicate CMake cache entry')
        entries[match[1]] = {'type': match[2], 'value': match[3]}
    for argument in argv[4:]:
        key, value = argument[2:].split('=', 1)
        if key not in entries or entries[key]['value'] != value:
            raise BuildHold('H_CONFIG_EQUIVALENCE', 'fixed CMake definition unsupported/different: ' + key)
    def logical(value: str) -> str:
        return value.replace(str(source), '<SOURCE>').replace(str(build), '<BUILD>').replace(str(root), '<OWNED>')
    normalized = {key: {'type': value['type'], 'value': logical(value['value'])} for key, value in entries.items()}
    return normalized


def _configuration(root: Path, variant: str, source: Path, build: Path, argv: list[str], payload: dict[str, tuple[bytes, str]]) -> bytes:
    cache_raw = _stable_read(build / 'CMakeCache.txt', 4 * MAX_METADATA)
    normalized = _logical_cache(cache_raw, root, source, build, argv)
    raw = _json({'schema': 'twin.xpdf-build-configuration/v1', 'logical_cache': normalized})
    _payload_add(payload, variant + '/CONFIGURATION.json', raw, 'metadata')
    return raw


def _elf(raw: bytes) -> dict[str, Any]:
    """Bounded static ELF64 reader. Never invoke artifact, interpreter, ldd or readelf."""
    if len(raw) < 64 or raw[:7] != b'\x7fELF\x02\x01\x01':
        raise BuildHold('H_ELF_ASSOCIATION', 'not little-endian ELF64')
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', raw)
    if header[1] not in (2, 3) or header[2] != 62 or header[3] != 1 or header[9] != 56 or header[10] > 4096:
        raise BuildHold('H_ELF_ASSOCIATION', 'unsupported ELF target/header')
    loads = []
    dynamic = []
    interpreter = None
    for i in range(header[10]):
        offset = header[5] + 56 * i
        if offset + 56 > len(raw):
            raise BuildHold('H_ELF_ASSOCIATION', 'ELF program table bounds')
        kind, _, file_offset, address, _, size, _, _ = struct.unpack_from('<IIQQQQQQ', raw, offset)
        if file_offset + size > len(raw):
            raise BuildHold('H_ELF_ASSOCIATION', 'ELF segment bounds')
        if kind == 1:
            loads.append((address, file_offset, size))
        if kind == 3:
            value = raw[file_offset:file_offset + size]
            if interpreter is not None or not value.endswith(b'\0') or b'\0' in value[:-1]:
                raise BuildHold('H_ELF_ASSOCIATION', 'ELF interpreter shape')
            interpreter = value[:-1].decode('ascii')
        if kind == 2:
            if size % 16:
                raise BuildHold('H_ELF_ASSOCIATION', 'ELF dynamic alignment')
            dynamic = [struct.unpack_from('<QQ', raw, file_offset + j) for j in range(0, size, 16)]
    table = dict((key, value) for key, value in dynamic if key in (5, 10))
    strings = b''
    if dynamic:
        if set(table) != {5, 10}:
            raise BuildHold('H_ELF_ASSOCIATION', 'ELF dynamic string table absent')
        matches = [(file_offset + table[5] - address) for address, file_offset, size in loads if address <= table[5] and table[5] + table[10] <= address + size]
        if len(matches) != 1:
            raise BuildHold('H_ELF_ASSOCIATION', 'ELF string table mapping unknown')
        strings = raw[matches[0]:matches[0] + table[10]]
    associations: dict[str, Any] = {'class': 'ELF64', 'endian': 'little', 'machine': 'x86_64', 'OSABI': raw[7],
                                    'interpreter': interpreter, 'needed': [], 'soname': None, 'rpath': None, 'runpath': None}
    for key, string_offset in dynamic:
        if key not in (1, 14, 15, 29):
            continue
        end = strings.find(b'\0', string_offset)
        if string_offset >= len(strings) or end < 0:
            raise BuildHold('H_ELF_ASSOCIATION', 'ELF dynamic string bounds')
        decoded = strings[string_offset:end].decode('ascii')
        if key == 1:
            associations['needed'].append(decoded)
        else:
            field = {14: 'soname', 15: 'rpath', 29: 'runpath'}[key]
            if associations[field] is not None:
                raise BuildHold('H_ELF_ASSOCIATION', 'duplicate ELF dynamic name')
            associations[field] = decoded
    return associations


def _candidate_library_name(raw: bytes, resolved: str) -> str | None:
    # Archives/linker scripts remain retained DATA, but cannot stand in for an ELF library.
    if not raw.startswith(b'\x7fELF'):
        return None
    observed = _elf(raw)
    return observed['soname'] if observed['soname'] is not None else Path(resolved).name


def _link_association(binary: bytes, root: Path, variant: str, logs: bytes, appointed: Mapping[str, Any], payload: dict[str, tuple[bytes, str]]) -> tuple[str, str]:
    association = _elf(binary)
    interpreter = association['interpreter']
    if interpreter is None or not interpreter.startswith(('/lib/', '/lib64/')):
        raise BuildHold('H_ELF_ASSOCIATION', 'Linux loader association unestablished')
    paths = {line.decode('utf-8') for line in logs.splitlines() if re.fullmatch(rb'/[^\s\x00]+', line)}
    paths.add(interpreter)
    candidates: dict[str, Any] = {}
    library_names = set()
    for path in sorted(paths):
        candidate = Path(path)
        if candidate.is_relative_to(root):
            continue
        if path not in appointed['tools']:
            raise BuildHold('H_ELF_ASSOCIATION', 'unselected actual link candidate: ' + path)
        selected = appointed['tools'][path]
        resolved = candidate.resolve(strict=True)
        value = _stable_read(resolved)
        route = []
        current = candidate
        for _ in range(32):
            if not current.is_symlink():
                break
            target = os.readlink(current)
            route.append({'path': str(current), 'target': target})
            current = Path(target) if target.startswith('/') else current.parent / target
        else:
            raise BuildHold('H_ELF_ASSOCIATION', 'link candidate route overflow')
        if _sha(value) != selected['sha256'] or str(resolved) != selected['resolved'] or route != selected['links']:
            raise BuildHold('H_ELF_ASSOCIATION', 'link candidate drift')
        name = f'{variant}/candidates/{len(candidates):04}.bin'
        _payload_add(payload, name, value, 'candidate')
        candidates[path] = {'sha256': _sha(value), 'bytes': len(value), 'payload': name}
        if path != interpreter:
            library_names.add(_candidate_library_name(value, selected['resolved']))
    if any(name not in library_names for name in association['needed']):
        raise BuildHold('H_ELF_ASSOCIATION', 'DT_NEEDED candidate association unestablished')
    raw = _json({'schema': 'twin.xpdf-build-link-candidates/v1', 'paths': candidates, 'runtime_access_closure': 'UNESTABLISHED'})
    _payload_add(payload, variant + '/LINK-CANDIDATES.json', raw, 'metadata')
    association['compiler_target'] = _load_json(payload['TOOL-MANIFEST.json'][0])['compiler_target']
    association['runtime_access_closure'] = 'UNESTABLISHED'
    elf_raw = _json(association)
    _payload_add(payload, variant + '/ELF.json', elf_raw, 'metadata')
    return _sha(elf_raw), _sha(raw)


def _export(root: Path, result: dict[str, Any], payload: dict[str, tuple[bytes, str]], stages: dict[str, Any], export_started: float) -> None:
    # Copy/read back frozen payload first. Last metadata records describe that observed
    # endpoint; their own commit/readback is additionally guarded by the same deadline.
    destination = root / 'export'
    destination.mkdir(mode=0o700)
    deadline = min(export_started + 120, result['clock']['started'] + 1740, result['clock']['deadline'])

    def write(name: str, value: bytes) -> None:
        if time.monotonic() > deadline:
            raise BuildHold('H_DEADLINE', 'original A export deadline expired')
        path = destination / name
        parent = _output_parent(destination, name)
        try:
            fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
            with os.fdopen(fd, 'wb') as stream:
                for offset in range(0, len(value), 65536):
                    if time.monotonic() > deadline:
                        raise BuildHold('H_DEADLINE', 'original A export copy deadline expired')
                    stream.write(value[offset:offset + 65536])
        finally:
            os.close(parent)
        if _stable_read(path) != value:
            raise BuildHold('H_EXPORT', 'export readback differs')
        path.chmod(0o444)
    for name, (value, _) in payload.items():
        write(name, value)
    _end_stage(result, stages, 'local-export-readback', export_started)
    _payload_add(payload, 'STAGES.json', _json(stages), 'metadata')
    write('STAGES.json', payload['STAGES.json'][0])
    result['clock']['ended'] = time.monotonic()
    entries: list[dict[str, Any]] = [{'path': name, 'bytes': len(raw), 'sha256': _sha(raw), 'role': role} for name, (raw, role) in sorted(payload.items())]
    manifest = _json({'schema': 'twin.xpdf-linux-build-files/v1', 'files': entries, 'logical_bytes': sum(e['bytes'] for e in entries), 'self_included': False})
    result['files_manifest_sha256'] = _sha(manifest)
    terminal = _json(result)
    if len(manifest) > MAX_METADATA or len(terminal) > MAX_METADATA or sum(e['bytes'] for e in entries) + len(manifest) + len(terminal) > MAX_BUNDLE:
        raise BuildHold('H_EXPORT', 'closed export cap exceeded')
    bundle = {name: value[0] for name, value in payload.items()}
    bundle.update({'FILES.json': manifest, 'RESULT.json': terminal})
    check_build_bundle(bundle, result['selection_sha256'])
    write('FILES.json', manifest)
    write('RESULT.json', terminal)
    # Qualification of the terminal file is conditional on this final original-budget check.
    # Preserve its raw bytes under an explicitly incomplete name if the final commit overran.
    if time.monotonic() > deadline:
        (destination / 'RESULT.json').rename(destination / 'RESULT-INCOMPLETE.json')
        raise BuildHold('H_DEADLINE', 'terminal export exceeded original phase/A deadline')


def _end_stage(result: dict[str, Any], stages: dict[str, Any], phase: str, started: float) -> float:
    ended = time.monotonic()
    profile = next(p for p in _load_json(_contract('LIMITS-AND-RECIPE.json'))['phases'] if p['id'] == phase)
    deadline = min(started + profile['allocation_seconds'], result['clock']['started'] + profile['cumulative_end_seconds'], result['clock']['deadline'])
    stages[phase] = {'started': started, 'ended': ended, 'deadline': deadline}
    if ended > deadline:
        raise BuildHold('H_DEADLINE', 'original stage allowance exhausted: ' + phase)
    return ended


def _build_appointed(selection: Mapping[str, Any], root: Path, result: dict[str, Any], appointed: Mapping[str, Any], payload: dict[str, tuple[bytes, str]]) -> None:
    stages: dict[str, Any] = {}
    environment = _fresh_environment(root)
    _payload_add(payload, 'SELECTION.json', _json(dict(selection)), 'metadata')
    _payload_add(payload, 'ENVIRONMENT.json', _json(environment), 'metadata')
    result['environment_manifest_sha256'] = _sha(payload['ENVIRONMENT.json'][0])
    for name in ('build_linux_pair.py', 'prepare_source.py'):
        _payload_add(payload, 'package/' + name, _stable_read(PACKAGE / name), 'package')
    _selected_files(selection, appointed, payload)
    if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode and sys.version_info[:2] == (3, 12)):
        raise BuildHold('H_BOOTSTRAP', 'parent isolated -I -S -B bootstrap unestablished')
    uname = os.uname()
    os_release_path = Path('/etc/os-release').resolve(strict=True)
    os_release_raw = _stable_read(os_release_path, 65536)
    if (uname.sysname != 'Linux' or uname.machine != 'x86_64' or uname.release != appointed['linux_release']
            or appointed['bootstrap']['files'].get(str(os_release_path)) != _sha(os_release_raw)):
        raise BuildHold('H_BOOTSTRAP', 'actual Linux/x86_64/release/OS identity differs')
    os_release = {}
    for line in os_release_raw.decode('utf-8').splitlines():
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            if key in os_release:
                raise BuildHold('H_BOOTSTRAP', 'duplicate OS release key')
            os_release[key] = value.strip('"')
    if os_release.get('ID') != 'ubuntu' or os_release.get('VERSION_ID') != '24.04':
        raise BuildHold('H_BOOTSTRAP', 'actual selected Ubuntu24 row unestablished')
    _payload_add(payload, 'BOOTSTRAP-OBSERVATION.json', _json({'executable': sys.executable, 'version': sys.version,
                 'driver_path': str(Path(__file__).resolve()),
                 'isolated': bool(sys.flags.isolated), 'no_site': bool(sys.flags.no_site),
                 'dont_write_bytecode': bool(sys.dont_write_bytecode), 'runtime_access_closure': 'UNESTABLISHED',
                 'uname': {'system': uname.sysname, 'machine': uname.machine, 'release': uname.release},
                 'os_release': {'path': str(os_release_path), 'sha256': _sha(os_release_raw), 'ID': 'ubuntu', 'VERSION_ID': '24.04'}}), 'metadata')
    usage = os.statvfs(root)
    free = usage.f_bavail * usage.f_frsize
    if free < appointed['capacity']['minimum_free_bytes']:
        raise BuildHold('H_CAPACITY', 'actual free space below independently selected minimum; no quota claim')
    _payload_add(payload, 'CAPACITY-OBSERVATION.json', _json({'selection': appointed['capacity'], 'observed_free_bytes': free, 'live_disk_quota_enforced': False}), 'metadata')
    _tool_inventory(result, root, environment, appointed, payload)
    archive_command = _supervise(result, 'bootstrap-input-tools', [sys.executable, '-I', '-S', '-B', str(Path(__file__).resolve()), '--internal-fetch'], root, environment, 30, payload)
    archive = _command_output(archive_command, payload)
    if len(archive) != 999317 or _sha(archive) != _source.ARCHIVE_SHA256:
        raise BuildHold('H_SOURCE_TRANSPORT', 'actual acquired raw archive differs')
    _payload_add(payload, 'inputs/xpdf-4.06.tar.gz', archive, 'archive')
    stage_started = _end_stage(result, stages, 'bootstrap-input-tools', result['clock']['started'])
    try:
        sources = _source_pair(root, archive, result, environment, payload)
    except ValueError as error:
        raise BuildHold('H_SOURCE_CONSERVATION', str(error)) from error
    stage_started = _end_stage(result, stages, 'two-source-preparations', stage_started)
    recipe = _contract('LIMITS-AND-RECIPE.json')
    _payload_add(payload, 'RECIPE.json', recipe, 'metadata')
    configs = []
    for variant in ('pristine', 'instrumented'):
        source = root / (variant + '-source')
        build = root / (variant + '-build')
        build.mkdir(mode=0o700)
        argv = _fixed_configure(source, build, root, appointed['linux_release'])
        _supervise(result, variant, argv, build, environment, 120, payload)
        config = _configuration(root, variant, source, build, argv, payload)
        configs.append(config)
        if len(configs) == 2 and configs[0] != configs[1]:
            raise BuildHold('H_CONFIG_EQUIVALENCE', 'actual variant configurations differ beyond path roles')
        command = _supervise(result, variant, ['/usr/bin/make', '-C', str(build), '-j2', 'VERBOSE=1', 'SHELL=/bin/sh', 'pdftotext'], build, environment, 480, payload)
        products = _tree(build, variant + '/build', payload)
        for required in ('CMakeCache.txt', 'compile_commands.json', 'xpdf/pdftotext'):
            if required not in products:
                raise BuildHold('H_EXPORT', 'required build product absent: ' + required)
        products_raw = _json(products)
        _payload_add(payload, variant + '/PRODUCTS.json', products_raw, 'metadata')
        binary = payload[variant + '/build/xpdf/pdftotext'][0]
        elf_sha, candidates_sha = _link_association(binary, root, variant, _command_output(command, payload), appointed, payload)
        result['variants'].append({'variant': variant, 'source_manifest_sha256': _sha(_json(sources[variant])), 'recipe_sha256': _sha(recipe),
                                   'configuration_manifest_sha256': _sha(config), 'products_manifest_sha256': _sha(products_raw), 'binary_sha256': _sha(binary),
                                   'ELF_association_sha256': elf_sha, 'link_candidate_manifest_sha256': candidates_sha,
                                   'runtime_access_closure': 'UNESTABLISHED', 'actual_converter_invocations': 0, 'actual_native_config_use': None})
        stage_started = _end_stage(result, stages, variant, stage_started)
    _scratch_usage(root)
    for name, pin in [('build_linux_pair.py', selection['driver_sha256']), ('prepare_source.py', selection['preparer_sha256']), ('SOURCE-PINS.json', selection['source_package_sha256'])]:
        if _sha(_stable_read(PACKAGE / name)) != pin:
            raise BuildHold('H_EXECUTION_SELECTION', 'selected source drift before freeze')
    for records in (appointed['bootstrap']['files'], appointed['modules']['files']):
        for name, pin in records.items():
            if _sha(_stable_read(Path(name))) != pin:
                raise BuildHold('H_BOOTSTRAP', 'selected bootstrap/module drift before freeze')
    for name, pin in appointed['tools'].items():
        if _sha(_stable_read(Path(name).resolve(strict=True))) != pin['sha256']:
            raise BuildHold('H_TOOLS', 'actual tool/candidate drift before freeze')
    for variant in ('pristine', 'instrumented'):
        actual = {path.relative_to(root / (variant + '-source')).as_posix() for path in (root / (variant + '-source')).rglob('*') if path.is_file()}
        if actual != set(sources[variant]):
            raise BuildHold('H_SOURCE_CONSERVATION', 'source path set changed during build')
        for relative, pin in sources[variant].items():
            if _sha(_stable_read(root / (variant + '-source') / relative)) != pin['sha256']:
                raise BuildHold('H_SOURCE_CONSERVATION', 'source changed during build')
    stage_started = _end_stage(result, stages, 'associations-freeze-cleanup', stage_started)
    result['clock']['ended'] = time.monotonic()
    if result['clock']['ended'] > result['clock']['deadline']:
        raise BuildHold('H_DEADLINE', 'original A exhausted before export')
    result['status'] = 'COMPLETE_BUILD_PAIR'
    try:
        _export(root, result, payload, stages, stage_started)
    except BaseException:
        # A failed terminal commit cannot remain the installed complete stage.
        try:
            parent = _source._directory_fd(root / 'export')
            try:
                try:
                    os.stat('RESULT-INCOMPLETE.json', dir_fd=parent, follow_symlinks=False)
                except FileNotFoundError:
                    os.rename('RESULT.json', 'RESULT-INCOMPLETE.json', src_dir_fd=parent, dst_dir_fd=parent)
            finally:
                os.close(parent)
        except BaseException:
            pass
        raise


def _load_json(raw: bytes) -> Any:
    if len(raw) > MAX_METADATA:
        raise ValueError('metadata limit')
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in items:
            if key in value:
                raise ValueError('duplicate JSON key')
            value[key] = item
        return value
    def bad_constant(value: str) -> Any:
        raise ValueError('nonfinite JSON value: ' + value)
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)
    except (UnicodeError, RecursionError, json.JSONDecodeError) as error:
        raise ValueError('invalid bounded JSON') from error


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _validate(value: Any, schema: dict[str, Any]) -> None:
    """The closed subset used by the three source-owned schemas; never external schemas."""
    def accepts(candidate: dict[str, Any]) -> bool:
        try:
            _validate(value, candidate)
            return True
        except ValueError:
            return False
    for mode in ('anyOf', 'oneOf'):
        if mode in schema:
            count = sum(accepts(s) for s in schema[mode])
            _require(count >= 1 if mode == 'anyOf' else count == 1, 'schema ' + mode)
    if 'const' in schema:
        _require(value == schema['const'] and isinstance(value, bool) == isinstance(schema['const'], bool), 'schema const')
    if 'enum' in schema:
        _require(any(value == v and isinstance(value, bool) == isinstance(v, bool) for v in schema['enum']), 'schema enum')
    kind = schema.get('type')
    types: dict[str, Any] = {'object': dict, 'array': list, 'string': str, 'integer': int, 'number': (int, float), 'null': type(None), 'boolean': bool}
    if kind:
        _require(isinstance(value, types[kind]) and not (kind in ('integer', 'number') and isinstance(value, bool)), 'schema type')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        _require(math.isfinite(value), 'finite number required')
        if 'minimum' in schema:
            _require(value >= schema['minimum'], 'schema minimum')
        if 'maximum' in schema:
            _require(value <= schema['maximum'], 'schema maximum')
    if isinstance(value, str):
        _require(len(value) >= schema.get('minLength', 0) and len(value) <= schema.get('maxLength', len(value)), 'schema string length')
        if 'pattern' in schema:
            _require(re.fullmatch(schema['pattern'], value) is not None, 'schema pattern')
    if isinstance(value, list):
        _require(len(value) >= schema.get('minItems', 0) and len(value) <= schema.get('maxItems', len(value)), 'schema array bound')
        if schema.get('uniqueItems'):
            _require(len({_json(v) for v in value}) == len(value), 'schema unique array')
        if 'items' in schema:
            for item in value:
                _validate(item, schema['items'])
    if isinstance(value, dict):
        _require(set(schema.get('required', [])).issubset(value), 'schema missing key')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            _require(set(value).issubset(properties), 'schema extra key')
        for key in value.keys() & properties.keys():
            _validate(value[key], properties[key])
    for item in schema.get('allOf', []):
        _validate(value, item)
    if 'if' in schema:
        branch = 'then' if accepts(schema['if']) else 'else'
        if branch in schema:
            _validate(value, schema[branch])


def _schema(name: str) -> dict[str, Any]:
    return _load_json(_contract(name))


def _safe_name(name: str) -> bool:
    return (bool(name) and len(name.encode('utf-8')) <= 4096 and '\\' not in name and '\x00' not in name
            and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')))


def _permitted_dispatch(argv: list[str], phase: str) -> bool:
    if not argv:
        return False
    if len(argv) == 2 and phase == 'bootstrap-input-tools':
        allowed = _load_json(_contract('LIMITS-AND-RECIPE.json'))['tools']['fixed_selectors']
        return (argv[0] in allowed and argv[0] != '/bin/sh' and argv[1] == '--version') or (argv[0] == '/usr/bin/gcc' and argv[1] in ('-dumpmachine', '-dumpspecs', '-print-prog-name=cc1', '-print-prog-name=collect2')) or (argv[0] == '/usr/bin/g++' and argv[1] == '-print-prog-name=cc1plus')
    if len(argv) == 7 and phase in ('pristine', 'instrumented'):
        return argv[0:2] == ['/usr/bin/make', '-C'] and argv[3:] == ['-j2', 'VERBOSE=1', 'SHELL=/bin/sh', 'pdftotext']
    if len(argv) == 7 and phase == 'two-source-preparations':
        return argv[:6] == ['/usr/bin/patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i']
    if len(argv) == 6 and phase == 'bootstrap-input-tools':
        return argv[1:4] == ['-I', '-S', '-B'] and argv[-1] == '--internal-fetch' and argv[4].endswith('/build_linux_pair.py')
    if argv[:3] == ['/usr/bin/cmake', '-G', 'Unix Makefiles'] and phase in ('pristine', 'instrumented'):
        definitions = _load_json(_contract('LIMITS-AND-RECIPE.json'))['configure']['definitions']
        supplied = {}
        for argument in argv[4:]:
            if not argument.startswith('-D') or '=' not in argument:
                return False
            key, value = argument[2:].split('=', 1)
            if key in supplied:
                return False
            supplied[key] = value
        return set(supplied) == set(definitions) and all(supplied[k] == v for k, v in definitions.items() if k not in ('CMAKE_INSTALL_PREFIX', 'CMAKE_SYSTEM_VERSION'))
    return False


def _binding(result: dict[str, Any], command: dict[str, Any]) -> str:
    context = {
        'schema': 'twin.xpdf-build-custody-binding/v1', 'selection_sha256': result['selection_sha256'],
        'command_id': command['id'], 'phase': command['phase'], 'argv': command['argv'],
        'environment_sha256': command['environment_sha256'], 'command_started': command['started'],
        'command_deadline': command['deadline'], 'checkpoint_started': result['clock']['started'],
        'checkpoint_deadline': result['clock']['deadline'], 'leader_pid': command['custody']['leader_pid'],
    }
    # The contract digest has no terminating LF (unlike retained JSON documents).
    return _sha(_json(context)[:-1])


def _check_custody(result: dict[str, Any], command: dict[str, Any]) -> bool:
    custody = command['custody']
    events = custody['observations']
    grouped: dict[str, list[dict[str, Any]]] = {}
    last = None
    for index, event in enumerate(events):
        _require(event['ordinal'] == index, 'custody ordinal')
        at = event['at']
        if at is not None:
            _require(last is None or at >= last, 'custody decreasing clock')
            for low in (command['started'], result['clock']['started']):
                _require(low is None or at >= low, 'custody before original start')
            last = at
            _require(command['ended'] is None or at <= command['ended'], 'custody after command end')
            _require(result['clock']['ended'] is None or at <= result['clock']['ended'], 'custody after A end')
        grouped.setdefault(event['kind'], []).append(event)
        for key in ('leader_pid', 'pid'):
            if key in event['detail']:
                _require(event['detail'][key] == custody['leader_pid'], 'custody PID binding')
    for kind in ('cleanup-start', 'reaping-start', 'direct-reap', 'cleanup-end'):
        _require(len(grouped.get(kind, [])) <= 1, 'duplicate custody singleton')
    _require(len(grouped.get('signal-attempt', [])) <= 8 and len(grouped.get('group-probe', [])) <= 16, 'custody kind cap')
    binding = custody['command_binding_sha256']
    _require(binding is None or binding == _binding(result, command), 'custody context binding')
    def one(kind: str) -> dict[str, Any] | None:
        records = grouped.get(kind, [])
        return records[0] if records else None
    start, reaping, terminal, end = [one(k) for k in ('cleanup-start', 'reaping-start', 'direct-reap', 'cleanup-end')]
    probes = grouped.get('group-probe', [])
    signals = grouped.get('signal-attempt', [])
    _require(custody['cleanup_started'] == (start['at'] if start else None), 'cleanup start projection')
    _require(custody['cleanup_deadline'] == (start['detail']['selected_deadline'] if start else None), 'cleanup deadline projection')
    _require(custody['cleanup_ended'] == (end['at'] if end else None), 'cleanup end projection')
    times = [custody['cleanup_started'], command['deadline'], result['clock']['deadline']]
    if all(value is not None for value in times):
        _require(custody['cleanup_deadline'] == min(times[0] + 2, times[1], times[2]), 'original shared cleanup grace')
    projected = [dict(e['detail'], at=e['at']) for e in signals]
    _require(projected == custody['signals'], 'signal projection')
    for signal in signals:
        _require(start is not None and signal['ordinal'] > start['ordinal'], 'signal before cleanup start')
        _require(reaping is None or signal['ordinal'] < reaping['ordinal'], 'signal after first consuming wait')
    if reaping:
        _require(start is not None and start['ordinal'] < reaping['ordinal'], 'first reaping order')
    if terminal:
        _require(reaping is not None and reaping['ordinal'] < terminal['ordinal'], 'direct terminal reap order')
        details = terminal['detail']
        raw = details['raw_wait']
        if details['wait_kind'] == 'EXITED':
            _require(type(details['exit_code']) is int and 0 <= details['exit_code'] <= 255
                     and raw == details['exit_code'] << 8 and details['signal'] is None, 'raw exit decoding')
        else:
            _require(type(details['signal']) is int and 0 < details['signal'] < 127
                     and raw in (details['signal'], details['signal'] | 128)
                     and details['exit_code'] is None, 'raw signal decoding')
        _require(custody['direct_reap'] == 'OBSERVED' and all(custody[k] == details[k] for k in ('wait_kind', 'raw_wait', 'exit_code', 'signal')), 'terminal projection')
    else:
        _require(custody['direct_reap'] == 'UNOBSERVED' and custody['wait_kind'] == 'UNOBSERVED' and all(custody[k] is None for k in ('raw_wait', 'exit_code', 'signal')), 'invented terminal reap')
    for probe in probes:
        _require(terminal is not None and terminal['ordinal'] < probe['ordinal'], 'absence before direct reap')
    outcome = probes[-1]['detail']['outcome'] if probes else None
    expected_absence = outcome if outcome in ('ABSENT', 'PRESENT') else 'UNOBSERVED'
    _require(custody['group_absence'] == expected_absence, 'group absence projection')
    if end:
        _require(end['ordinal'] == len(events) - 1, 'event after cleanup end')
        _require(start is not None and start['ordinal'] < end['ordinal'], 'cleanup ending order')
    deadline = custody['cleanup_deadline']
    if deadline is not None:
        _require(all(e['at'] is None or e['at'] <= deadline for e in events), 'cleanup after original deadline')
    known = (binding is not None and custody['leader_pid'] is not None and custody['reservation'] == 'UNREAPED_DIRECT_LEADER'
             and all(e['at'] is not None for e in events) and all(v is not None for v in times)
             and all(e['detail']['outcome'] is not None for e in signals)
             and all(e is not None for e in (start, reaping, terminal, end)) and bool(probes) and outcome == 'ABSENT')
    if command['disposition'] == 'EXIT0_COMPLETE':
        _require(known and custody['exit_code'] == 0 and all(command[k] is not None for k in ('started', 'deadline', 'ended')), 'incomplete successful custody')
    elif not known:
        _require(custody['workspace'] in ('RETAINED', 'NOT_CREATED'), 'unknown custody workspace deletion')
    if custody['reservation'] == 'NO_CHILD_CREATED':
        _require(custody['leader_pid'] is None and not events and not signals, 'started child claimed absent')
    return bool(known)


def check_build_bundle(bundle: Mapping[str, bytes], expected_selection_sha256: str) -> dict[str, Any]:
    """Check exact closed build DATA and chronology, without granting execution/native authority."""
    _require(len(bundle) <= 32770 and all(isinstance(k, str) and _safe_name(k) for k in bundle), 'unsafe bundle paths/count')
    _require(all(type(v) is bytes and len(v) <= MAX_FILE for v in bundle.values()) and sum(map(len, bundle.values())) <= MAX_BUNDLE, 'bundle extent')
    _require({'RESULT.json', 'FILES.json', 'SELECTION.json', 'ENVIRONMENT.json'}.issubset(bundle), 'missing bundle records')
    selection = _load_json(bundle['SELECTION.json'])
    result = _load_json(bundle['RESULT.json'])
    files = _load_json(bundle['FILES.json'])
    for value, name in [(selection, 'BUILD-SELECTION.schema.json'), (result, 'BUILD-RESULT.schema.json'), (files, 'BUILD-FILES.schema.json')]:
        _validate(value, _schema(name))
    _require(result['selection_sha256'] == expected_selection_sha256 == _sha(bundle['SELECTION.json']), 'selection identity')
    _require(result['files_manifest_sha256'] == _sha(bundle['FILES.json']), 'file manifest identity')
    entries = files['files']
    names = [entry['path'] for entry in entries]
    _require(len(names) == len(set(names)) and set(names) == set(bundle) - {'RESULT.json', 'FILES.json'}, 'exact file manifest set')
    for entry in entries:
        raw = bundle[entry['path']]
        _require(len(raw) == entry['bytes'] and _sha(raw) == entry['sha256'], 'file bytes/hash')
        if entry['role'] == 'metadata':
            _require(len(raw) <= MAX_METADATA, 'metadata record limit')
    _require(files['logical_bytes'] == sum(len(bundle[name]) for name in names), 'logical byte sum')
    _require(result['environment_manifest_sha256'] == _sha(bundle['ENVIRONMENT.json']), 'environment identity')
    clock = result['clock']
    if clock['started'] is not None and clock['deadline'] is not None:
        _require(clock['deadline'] == clock['started'] + 1800, 'original A deadline')
    if clock['ended'] is not None and clock['started'] is not None:
        _require(clock['ended'] >= clock['started'], 'A ended before start')
    ids: set[str] = set()
    unknown_seen = False
    previous_command_end = clock['started']
    raw_logs = 0
    phases = {p['id']: p for p in _load_json(_contract('LIMITS-AND-RECIPE.json'))['phases']}
    for command in result['commands']:
        _require(_permitted_dispatch(command['argv'], command['phase']), 'forbidden executable/target/worker dispatch')
        _require(command['id'] not in ids and not unknown_seen, 'duplicate command or next phase after unknown/failure')
        ids.add(command['id'])
        if command['started'] is not None and previous_command_end is not None:
            _require(command['started'] >= previous_command_end, 'command chronology/retry after later stage')
        previous_command_end = command['ended']
        _require(command['environment_sha256'] == result['environment_manifest_sha256'], 'command environment')
        if command['started'] is not None and command['deadline'] is not None:
            _require(command['started'] <= command['deadline'], 'command deadline before start')
            if clock['started'] is not None:
                _require(command['deadline'] <= clock['started'] + phases[command['phase']]['cumulative_end_seconds'], 'phase deadline renewed')
        if command['ended'] is not None and command['deadline'] is not None:
            _require(command['ended'] <= command['deadline'], 'command ended beyond deadline')
        known = _check_custody(result, command)
        for stream in ('stdout', 'stderr'):
            record = command[stream]
            _require(record['observed_bytes_lower_bound'] >= record['retained_bytes'], 'stream lower bound')
            if record['sha256'] is not None:
                candidates = [bundle[n] for n in names if _sha(bundle[n]) == record['sha256']]
                _require(bool(candidates) and len(candidates[0]) == record['retained_bytes'], 'stream missing exact retained bytes')
            else:
                _require(record['state'] == 'ABSENT' and record['retained_bytes'] == 0, 'unknown stream identity')
            if record['state'] == 'COMPLETE':
                _require(record['sha256'] is not None and record['observed_bytes_lower_bound'] == record['retained_bytes'], 'incomplete stream claimed complete')
            raw_logs += record['retained_bytes']
        unknown_seen = not known or command['disposition'] != 'EXIT0_COMPLETE'
    _require(raw_logs <= 256 * 1024 * 1024, 'global raw log bound')
    complete = result['status'] == 'COMPLETE_BUILD_PAIR'
    if complete:
        _check_complete_bundle(bundle, result, entries)
    else:
        _require(result['first_failure'] is not None and bool(result['hold_codes']), 'missing first failure')
    return {'status': result['status'], 'build_complete': complete, 'runtime_access_closure': 'UNESTABLISHED', 'native_permission': False}


def _check_complete_bundle(bundle: Mapping[str, bytes], result: dict[str, Any], entries: list[dict[str, Any]]) -> None:
    _require(all(result['clock'][k] is not None for k in ('started', 'deadline', 'ended')) and result['clock']['ended'] <= result['clock']['deadline'], 'complete A timing')
    _require(result['commands'] and all(c['disposition'] == 'EXIT0_COMPLETE' and all(c[s]['state'] == 'COMPLETE' for s in ('stdout', 'stderr')) for c in result['commands']), 'complete command coverage')
    _require([v['variant'] for v in result['variants']] == ['pristine', 'instrumented'], 'exact variant order')
    by_hash = {_sha(raw): (name, raw) for name, raw in bundle.items()}
    for key in ('tool_manifest_sha256', 'source_conservation_sha256'):
        _require(result[key] in by_hash, 'missing complete association ' + key)
    for variant in result['variants']:
        for key in ('source_manifest_sha256', 'recipe_sha256', 'configuration_manifest_sha256', 'products_manifest_sha256', 'binary_sha256', 'ELF_association_sha256', 'link_candidate_manifest_sha256'):
            _require(variant[key] is not None and variant[key] in by_hash, 'missing variant association ' + key)
    _require(result['variants'][0]['recipe_sha256'] == result['variants'][1]['recipe_sha256'], 'variant recipe mismatch')
    roles = {entry['role'] for entry in entries}
    _require({'archive', 'source', 'package', 'notice', 'bootstrap', 'tool', 'candidate', 'config', 'object', 'library', 'binary', 'raw-log', 'metadata'}.issubset(roles), 'missing complete artifact roles')
    selection = _load_json(bundle['SELECTION.json'])
    environment = _load_json(bundle['ENVIRONMENT.json'])
    _require(isinstance(environment, dict) and isinstance(environment.get('HOME'), str) and environment['HOME'].endswith('/home'), 'owned environment absent')
    root = Path(environment['HOME']).parent
    _require(root.is_absolute() and '..' not in root.parts and environment == _fresh_environment(root), 'fresh closed environment differs')
    _require('STAGES.json' in bundle, 'original stage observations absent')
    stages = _load_json(bundle['STAGES.json'])
    stage_profiles = _load_json(_contract('LIMITS-AND-RECIPE.json'))['phases'][:-1]
    _require(set(stages) == {p['id'] for p in stage_profiles}, 'exact original stage set')
    previous_end = result['clock']['started']
    for profile in stage_profiles:
        record = stages[profile['id']]
        _require(set(record) == {'started', 'ended', 'deadline'} and all(type(v) in (int, float) and math.isfinite(v) for v in record.values()), 'known finite stage observations')
        _require(record['started'] == previous_end and record['started'] <= record['ended'] <= record['deadline'], 'stage chronological original bound')
        _require(record['deadline'] == min(record['started'] + profile['allocation_seconds'], result['clock']['started'] + profile['cumulative_end_seconds'], result['clock']['deadline']), 'stage renewed deadline')
        previous_end = record['ended']
    _require(previous_end <= result['clock']['ended'], 'terminal record precedes payload export')
    for command in result['commands']:
        record = stages[command['phase']]
        _require(command['started'] is not None and command['ended'] is not None and record['started'] <= command['started'] <= command['ended'] <= record['ended'], 'command outside original stage')
    for name, key in [('package/build_linux_pair.py', 'driver_sha256'), ('package/prepare_source.py', 'preparer_sha256'), ('package/SOURCE-PINS.json', 'source_package_sha256')]:
        _require(name in bundle and _sha(bundle[name]) == selection[key], 'selected source bytes absent/drifted')
    _require(any(_sha(raw) == selection['workflow_sha256'] for raw in bundle.values()), 'selected workflow bytes absent')
    for name, key in [('BOOTSTRAP-SELECTION.json', 'bootstrap_selection_sha256'), ('TOOL-SELECTION.json', 'tool_module_review_sha256')]:
        _require(name in bundle and _sha(bundle[name]) == selection[key], 'independent prerequisite association absent')
        record = _load_json(bundle[name])
        _require(set(record) == {'files', 'review_sha256'} and bool(record['files']) and re.fullmatch('[a-f0-9]{64}', record['review_sha256']) is not None, 'prerequisite record shape')
        _require(all(pin in by_hash for pin in record['files'].values()), 'retained prerequisite file missing')
    recipe_name, recipe_raw = by_hash[result['variants'][0]['recipe_sha256']]
    _require(recipe_raw == _contract('LIMITS-AND-RECIPE.json'), 'fixed recipe bytes differ')
    archives = [bundle[e['path']] for e in entries if e['role'] == 'archive']
    _require(len(archives) == 1 and len(archives[0]) == 999317, 'one fixed official archive required')
    original = _source.archive_files(archives[0])
    pins = _load_json(bundle['package/SOURCE-PINS.json'])
    _require(pins == _load_json((PACKAGE / 'SOURCE-PINS.json').read_bytes()), 'fixed source package pins differ')
    for name, pin in pins['package_files'].items():
        path = 'package/' + name
        _require(path in bundle and len(bundle[path]) == pin['bytes'] and _sha(bundle[path]) == pin['sha256'], 'retained package/notice bytes differ')
    conservation = _load_json(by_hash[result['source_conservation_sha256']][1])
    _require(set(conservation) == {'schema', 'archive_sha256', 'source_package_sha256', 'pristine', 'instrumented'}
             and conservation['schema'] == 'twin.xpdf-build-source-conservation/v1'
             and conservation['archive_sha256'] == _sha(archives[0])
             and conservation['source_package_sha256'] == selection['source_package_sha256'], 'source conservation association')
    expected_original = {name: {'bytes': len(raw), 'sha256': _sha(raw)} for name, raw in original.items()}
    _require(conservation['pristine'] == expected_original, 'pristine source is not identical frozen raw')
    changed = conservation['instrumented']
    _require(set(changed) == set(expected_original) | {'xpdf/TwinOrigin.h', 'xpdf/TwinOrigin.cc'}, 'unaccepted source path delta')
    _require(all(changed[n] == p for n, p in pins['patched_sources'].items()), 'accepted six patched source pins')
    _require(all(changed[n] == pin for n, pin in expected_original.items() if n not in pins['patched_sources']), 'unaccepted source semantic repair')
    tool = _load_json(by_hash[result['tool_manifest_sha256']][1])
    selectors = _load_json(recipe_raw)['tools']['fixed_selectors']
    _require(set(selectors).issubset(tool), 'required fixed selector observations absent')
    _require(re.fullmatch(r'x86_64-(?:[A-Za-z0-9_]+-)?linux(?:-[A-Za-z0-9_]+)*', tool.get('compiler_target', '')) is not None, 'compiler target association')
    _require(tool.get('specs_sha256') in by_hash, 'retained GCC specs absent')
    module_files = _load_json(bundle['TOOL-SELECTION.json'])['files']
    for name, record in tool.items():
        if name in ('compiler_target', 'specs_sha256'):
            continue
        _require(set(record) == {'sha256', 'resolved', 'links', 'observation'} and record['sha256'] in by_hash and module_files.get(record['resolved']) == record['sha256']
                 and by_hash[record['sha256']][1].startswith(b'\x7fELF'), 'actual tool bytes/review association missing')
        observed = record['observation']
        _require(set(observed) == {'uid', 'mode', 'dev', 'ino', 'size', 'mtime_ns', 'ctime_ns'}
                 and all(type(v) is int and v >= 0 for v in observed.values())
                 and observed['uid'] == 0 and stat.S_ISREG(observed['mode']) and not observed['mode'] & 0o022
                 and observed['size'] == len(by_hash[record['sha256']][1]), 'actual tool identity/ownership observation')
    _require('SOURCE-TRANSPORT-SELECTION.json' in bundle and 'RUN-ASSOCIATION.json' in bundle and 'BOOTSTRAP-OBSERVATION.json' in bundle, 'actual bootstrap/transport/run observation missing')
    transport = _load_json(bundle['SOURCE-TRANSPORT-SELECTION.json'])
    _require(set(transport) == {'selection_sha256', 'ssl_files', 'ca_file'} and transport['ca_file'] in transport['ssl_files'] and re.fullmatch('[a-f0-9]{64}', transport['selection_sha256']) is not None and transport['ssl_files'] and all(pin in by_hash for pin in transport['ssl_files'].values()), 'actual SSL/trust association')
    bootstrap_observation = _load_json(bundle['BOOTSTRAP-OBSERVATION.json'])
    _require(set(bootstrap_observation) == {'executable', 'version', 'driver_path', 'isolated', 'no_site', 'dont_write_bytecode', 'runtime_access_closure', 'uname', 'os_release'}
             and all(bootstrap_observation[k] is True for k in ('isolated', 'no_site', 'dont_write_bytecode'))
             and bootstrap_observation['runtime_access_closure'] == 'UNESTABLISHED'
             and bootstrap_observation['executable'] in _load_json(bundle['BOOTSTRAP-SELECTION.json'])['files'], 'actual isolated bootstrap observation')
    driver_path = Path(bootstrap_observation['driver_path'])
    _require(driver_path.is_absolute() and '..' not in driver_path.parts and driver_path.name == 'build_linux_pair.py', 'observed acquisition source path')
    _require(bootstrap_observation['uname']['system'] == 'Linux' and bootstrap_observation['uname']['machine'] == 'x86_64'
             and bootstrap_observation['os_release']['ID'] == 'ubuntu' and bootstrap_observation['os_release']['VERSION_ID'] == '24.04'
             and bootstrap_observation['os_release']['sha256'] in by_hash
             and _load_json(bundle['BOOTSTRAP-SELECTION.json'])['files'].get(bootstrap_observation['os_release']['path']) == bootstrap_observation['os_release']['sha256']
             and bootstrap_observation['version'].startswith('3.12.'), 'actual fixed Linux row association')
    run = _load_json(bundle['RUN-ASSOCIATION.json'])
    _require(set(run) == {'id', 'attempt', 'runner_temp', 'workflow_sha256'} and run['workflow_sha256'] == selection['workflow_sha256']
             and str(root.parent) == run['runner_temp'] and root.name == f'A-{run["id"]}-{run["attempt"]}', 'actual run/attempt/owned-root association')
    _require('CAPACITY-OBSERVATION.json' in bundle, 'actual capacity observation absent')
    capacity = _load_json(bundle['CAPACITY-OBSERVATION.json'])
    _require(set(capacity) == {'selection', 'observed_free_bytes', 'live_disk_quota_enforced'} and capacity['live_disk_quota_enforced'] is False
             and set(capacity['selection']) == {'acceptance_sha256', 'minimum_free_bytes'}
             and re.fullmatch('[a-f0-9]{64}', capacity['selection']['acceptance_sha256']) is not None
             and type(capacity['selection']['minimum_free_bytes']) is int and capacity['selection']['minimum_free_bytes'] > 0
             and type(capacity['observed_free_bytes']) is int and capacity['observed_free_bytes'] >= capacity['selection']['minimum_free_bytes'], 'capacity selection/observation; no quota claim')
    configurations = []
    for variant in result['variants']:
        name = variant['variant']
        source_manifest = _load_json(by_hash[variant['source_manifest_sha256']][1])
        _require(source_manifest == conservation[name], 'variant source manifest differs')
        for directory, manifest in [('source', source_manifest), ('build', _load_json(by_hash[variant['products_manifest_sha256']][1]))]:
            prefix = name + '/' + directory + '/'
            actual_names = {path[len(prefix):] for path in bundle if path.startswith(prefix)}
            _require(set(manifest) == actual_names, 'source/products manifest exact set')
            for relative, pin in manifest.items():
                raw = bundle[prefix + relative]
                _require(_safe_name(relative) and set(pin) == {'bytes', 'sha256'} and len(raw) == pin['bytes'] and _sha(raw) == pin['sha256'], 'source/products manifest bytes')
        _require(name + '/build/compile_commands.json' in bundle and name + '/build/CMakeCache.txt' in bundle, 'raw build configuration missing')
        binary = bundle.get(name + '/build/xpdf/pdftotext')
        _require(binary is not None and _sha(binary) == variant['binary_sha256'], 'variant binary path/identity')
        assert binary is not None
        elf = _load_json(by_hash[variant['ELF_association_sha256']][1])
        observed_elf = _elf(binary)
        _require(elf == dict(observed_elf, compiler_target=tool['compiler_target'], runtime_access_closure='UNESTABLISHED'), 'static ELF association differs')
        candidates = _load_json(by_hash[variant['link_candidate_manifest_sha256']][1])
        _require(set(candidates) == {'schema', 'paths', 'runtime_access_closure'} and candidates['schema'] == 'twin.xpdf-build-link-candidates/v1' and candidates['runtime_access_closure'] == 'UNESTABLISHED', 'link candidate record')
        for path, pin in candidates['paths'].items():
            _require(set(pin) == {'bytes', 'sha256', 'payload'} and pin['payload'] in bundle and _sha(bundle[pin['payload']]) == pin['sha256'] and len(bundle[pin['payload']]) == pin['bytes'], 'link candidate bytes')
            _require(path in tool and pin['sha256'] == tool[path]['sha256'], 'link candidate not independently preselected')
        library_names = {_candidate_library_name(bundle[pin['payload']], tool[path]['resolved'])
                         for path, pin in candidates['paths'].items() if path != elf['interpreter']}
        _require(elf['interpreter'] in candidates['paths'] and all(n in library_names for n in elf['needed']), 'Linux loader/needed candidate association')
        config_raw = by_hash[variant['configuration_manifest_sha256']][1]
        config = _load_json(config_raw)
        _require(set(config) == {'schema', 'logical_cache'} and config['schema'] == 'twin.xpdf-build-configuration/v1', 'configuration association shape')
        expected_definitions = _load_json(recipe_raw)['configure']['definitions']
        for key, value in expected_definitions.items():
            record = config['logical_cache'].get(key)
            _require(isinstance(record, dict) and set(record) == {'type', 'value'}, 'fixed CMake guard missing')
            if key == 'CMAKE_INSTALL_PREFIX':
                value = '<OWNED>/unused-install'
            elif key == 'CMAKE_SYSTEM_VERSION':
                _require(re.fullmatch(r'[A-Za-z0-9._+\-]{1,128}', record['value']) is not None, 'actual Linux release missing')
                continue
            _require(record['value'] == value, 'fixed CMake guard changed')
        release = config['logical_cache']['CMAKE_SYSTEM_VERSION']['value']
        _require(release == bootstrap_observation['uname']['release'], 'actual observed Linux release/configuration differs')
        expected_cache = _logical_cache(bundle[name + '/build/CMakeCache.txt'], root, root / (name + '-source'), root / (name + '-build'), _fixed_configure(root / (name + '-source'), root / (name + '-build'), root, release))
        _require(config['logical_cache'] == expected_cache, 'raw cache and selected configuration differ')
        configurations.append(config_raw)
    _require(configurations[0] == configurations[1], 'variant configuration/optional features differ')
    required_queries = _fixed_tool_queries()
    _require([c['argv'] for c in result['commands'][:len(required_queries)]] == required_queries, 'exact required fixed query sequence')
    kinds: list[tuple[str, str]] = []
    for command in result['commands']:
        argv = command['argv']
        phase = command['phase']
        if argv[:3] == ['/usr/bin/cmake', '-G', 'Unix Makefiles']:
            _require(phase in ('pristine', 'instrumented'), 'configure phase')
            config = _load_json(by_hash[next(v['configuration_manifest_sha256'] for v in result['variants'] if v['variant'] == phase)][1])
            release = config['logical_cache']['CMAKE_SYSTEM_VERSION']['value']
            _require(argv == _fixed_configure(root / (phase + '-source'), root / (phase + '-build'), root, release), 'fixed configure argv changed')
            kinds.append((phase, 'configure'))
        elif len(argv) > 2 and argv[0] == '/usr/bin/make':
            _require(phase in ('pristine', 'instrumented') and argv == ['/usr/bin/make', '-C', str(root / (phase + '-build')), '-j2', 'VERBOSE=1', 'SHELL=/bin/sh', 'pdftotext'], 'fixed build argv changed')
            kinds.append((phase, 'build'))
        elif len(argv) > 2 and argv[0] == '/usr/bin/patch':
            _require(phase == 'two-source-preparations' and argv == ['/usr/bin/patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(root / 'inputs/xpdf-4.06-origin.patch')], 'fixed patch argv changed')
            output = by_hash[command['stdout']['sha256']][1] + by_hash[command['stderr']['sha256']][1]
            _require(re.search(rb'offset|fuzz|reject', output, re.I) is None, 'patch diagnostic refusal')
            kinds.append((phase, 'patch'))
        elif len(argv) == 6 and argv[1:4] == ['-I', '-S', '-B'] and argv[-1] == '--internal-fetch':
            _require(phase == 'bootstrap-input-tools' and argv[0] == bootstrap_observation['executable']
                     and argv[4] == bootstrap_observation['driver_path'], 'fixed source acquisition phase/bootstrap/source')
            _require(by_hash[command['stdout']['sha256']][1] == archives[0], 'actual acquisition output differs')
            kinds.append((phase, 'acquire'))
        else:
            _require(phase == 'bootstrap-input-tools' and argv in required_queries, 'unsupported executable/target/query')
            output = by_hash[command['stdout']['sha256']][1]
            if argv[1] == '--version':
                if argv[0] == '/usr/bin/cmake':
                    match = re.search(rb'cmake version (\d+)\.(\d+)\.', output)
                    _require(match is not None and (int(match[1]), int(match[2])) >= (3, 24), 'CMake guard semantics unsupported')
                else:
                    _require(b'GNU' in output, 'required GNU tool observation')
            elif argv[1].startswith('-print-prog-name='):
                selected_path = output.decode('ascii').strip()
                _require(selected_path in tool and Path(selected_path).name == argv[1].split('=')[1], 'GCC internal selector association')
            elif argv[1] == '-dumpmachine':
                _require(output.decode('ascii').strip() == tool['compiler_target'], 'compiler target/query association')
            else:
                _require(_sha(output) == tool['specs_sha256'], 'GCC specs/query association')
            kinds.append((phase, 'query'))
        duration = {'query': 5, 'acquire': 30, 'patch': 30, 'configure': 120, 'build': 480}[kinds[-1][1]]
        _require(command['deadline'] == command['started'] + duration, 'command allowance changed/renewed')
    meaningful = [kind for kind in kinds if kind[1] != 'query']
    _require(sum(kind[1] == 'query' for kind in kinds) == len(required_queries), 'missing/duplicate fixed queries')
    _require(meaningful == [('bootstrap-input-tools', 'acquire'), ('two-source-preparations', 'patch'), ('pristine', 'configure'), ('pristine', 'build'), ('instrumented', 'configure'), ('instrumented', 'build')], 'exact first-failure/no-retry stage order')


def _json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _new_result(selection: Mapping[str, Any], started: float | None) -> dict[str, Any]:
    return {
        'schema': 'twin.xpdf-linux-build-result/v2', 'scope': 'BUILD_DATA_ONLY',
        'selection_sha256': _sha(_json(dict(selection))), 'status': 'HELD',
        'hold_codes': [], 'first_failure': None,
        'clock': {'original_seconds': 1800, 'started': started, 'deadline': None if started is None else started + 1800, 'ended': None},
        'environment_manifest_sha256': _sha(_json({})), 'tool_manifest_sha256': None,
        'source_conservation_sha256': None, 'variants': [], 'commands': [],
        'files_manifest_sha256': None, 'runtime_access_closure': 'UNESTABLISHED',
        'native_H': None, 'private_native_handle': None, 'native_N01_N08': 'UNRUN',
        'actual_converter_invocations': 0, 'execution_or_publication_grant': 'NONE',
    }


def _hold(result: dict[str, Any], code: str, reason: str, phase: str = 'bootstrap-input-tools', command_id: str | None = None) -> None:
    if code not in result['hold_codes']:
        result['hold_codes'].append(code)
    if result['first_failure'] is None:
        result['first_failure'] = {'phase': phase, 'command_id': command_id, 'reason': reason[:4096]}
    result['status'] = 'HELD'


def build_linux_pair(selection: Mapping[str, Any], owned_parent: Path) -> dict[str, Any]:
    """Return build data; absent independent source appointment holds before effects."""
    try:
        started = time.monotonic()
    except Exception:
        started = None
    result = _new_result(selection, started)
    payload: dict[str, tuple[bytes, str]] = {}
    created = False
    previous_umask = None
    original_cancellation: BaseException | None = None
    try:
        if _APPOINTED_EXECUTION is None:
            raise BuildHold('H_EXECUTION_SELECTION', 'actual execution source selection is not appointed')
        _validate(dict(selection), _schema('BUILD-SELECTION.schema.json'))
        if started is None:
            raise BuildHold('H_DEADLINE', 'actual original start unobserved')
        appointed = _appointment(selection)
        run = appointed['run']
        if (set(run) != {'id', 'attempt', 'runner_temp', 'workflow_sha256'}
                or not re.fullmatch(r'[0-9]{1,24}', str(run['id']))
                or not re.fullmatch(r'[1-9][0-9]{0,5}', str(run['attempt']))
                or run['workflow_sha256'] != selection['workflow_sha256']
                or owned_parent.absolute().parent != Path(run['runner_temp']).absolute()
                or owned_parent.name != f'A-{run["id"]}-{run["attempt"]}'):
            raise BuildHold('H_EXECUTION_SELECTION', 'actual run/attempt/workflow/owned path differs')
        previous_umask = os.umask(0o077)
        parent = _source._directory_fd(owned_parent.parent)
        try:
            os.mkdir(owned_parent.name, 0o700, dir_fd=parent)
        finally:
            os.close(parent)
        created = True
        for name in ('inputs', 'home', 'tmp', 'journal'):
            (owned_parent / name).mkdir(mode=0o700)
        _build_appointed(selection, owned_parent, result, appointed, payload)
    except BuildHold as error:
        _hold(result, error.code, str(error), result['commands'][-1]['phase'] if result['commands'] else 'bootstrap-input-tools',
              result['commands'][-1]['id'] if result['commands'] else None)
    except Exception as error:
        _hold(result, 'H_CUSTODY' if result['commands'] else 'H_EXECUTION_SELECTION', type(error).__name__ + ': ' + str(error))
    except BaseException as error:
        # The explicit owned workspace has no destructor/finalizer. Preserve original interruption.
        original_cancellation = error
        _hold(result, 'H_CUSTODY', 'original interruption; workspace retained')
        if created:
            try:
                _retain_failure(owned_parent, result, payload)
            except BaseException:
                pass
        raise
    finally:
        if previous_umask is not None:
            try:
                os.umask(previous_umask)
            except BaseException as error:
                _hold(result, 'H_CUSTODY', 'umask restoration unobserved; workspace retained', 'local-export-readback')
                if created:
                    try:
                        _retain_umask_fault(owned_parent, result, payload, error, original_cancellation)
                    except BaseException:
                        pass  # Never replace the pending original cancellation with evidence failure.
                if original_cancellation is None:
                    raise  # A new restoration failure cannot return success.
    if result['status'] != 'COMPLETE_BUILD_PAIR':
        try:
            result['clock']['ended'] = time.monotonic()
        except BaseException:
            pass
        if created:
            _retain_failure(owned_parent, result, payload)
    return result


def _retain_umask_fault(root: Path, result: dict[str, Any], payload: dict[str, tuple[bytes, str]],
                       secondary: BaseException, original: BaseException | None) -> None:
    terminal = 'UNOBSERVED'
    try:
        (root / 'export/RESULT.json').rename(root / 'export/RESULT-INCOMPLETE.json')
        terminal = 'RENAMED_INCOMPLETE'
    except FileNotFoundError:
        terminal = 'NOT_OBSERVED'
    except BaseException:
        pass
    fault = {'schema': 'twin.xpdf-build-umask-restore-fault/v1', 'restoration': 'UNOBSERVED',
             'secondary_type': type(secondary).__name__[:128],
             'original_type': None if original is None else type(original).__name__[:128],
             'first_failure_sha256': _sha(_json(result['first_failure'])),
             'workspace': 'RETAINED', 'export_terminal': terminal}
    raw = _json(fault)
    if len(raw) > MAX_UMASK_FAULT:
        raise BuildHold('H_CUSTODY', 'secondary restoration evidence exceeds its reserved metadata allowance')
    parent = _output_parent(root, 'UMASK-RESTORE-FAULT.json')
    try:
        fd = os.open('UMASK-RESTORE-FAULT.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
    finally:
        os.close(parent)
    _retain_failure(root, result, payload)


def _retain_failure(root: Path, result: dict[str, Any], payload: dict[str, tuple[bytes, str]]) -> None:
    """Bounded already-observed first facts only; no live workspace sweep, retry or deletion."""
    try:
        remaining = 15 * MAX_METADATA
        current = len(result['commands']) - 1
        ordered = sorted(payload.items(), key=lambda pair: (not pair[0].startswith(f'journal/{current:03}-'), pair[0]))
        retained: dict[str, tuple[str, int]] = {}
        for index, (name, (raw, role)) in enumerate(ordered):
            if role != 'raw-log':
                continue
            prefix = raw[:remaining]
            relative = f'journal/failure-prefix-{index:03}.log'
            parent = _output_parent(root, relative)
            try:
                fd = os.open(relative.split('/')[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(prefix)
            finally:
                os.close(parent)
            retained[name] = (_sha(prefix), len(prefix))
            remaining -= len(prefix)
        for index, command in enumerate(result['commands']):
            for stream_name in ('stdout', 'stderr'):
                key = f'journal/{index:03}-{stream_name}.log'
                if key in retained:
                    checksum, length = retained[key]
                    record = command[stream_name]
                    if length != record['retained_bytes']:
                        record['state'] = 'PREFIX_ONLY'
                    record.update(sha256=checksum, retained_bytes=length)
        # A partial stage is never advertised as a verified complete export.
        result['files_manifest_sha256'] = None
        failure = _json(result)
        if len(failure) <= MAX_METADATA - MAX_UMASK_FAULT:
            parent = _output_parent(root, 'FIRST-FAILURE.json')
            try:
                fd = os.open('FIRST-FAILURE.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(failure)
            finally:
                os.close(parent)
    except Exception:
        # No replacement of the first failure/interruption and no false export claim.
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--build', nargs=2, metavar=('SELECTION_JSON', 'NEW_OWNED_PARENT'))
    group.add_argument('--check-bundle', nargs=2, metavar=('BUNDLE_DIRECTORY', 'SELECTION_SHA256'))
    group.add_argument('--internal-fetch', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.internal_fetch:
        try:
            _fixed_fetch(sys.stdout.buffer)
            return 0
        except Exception as error:
            sys.stderr.buffer.write(_json({'held': str(error)[:4096]}))
            return 2
    if args.build:
        selection = _load_json(_stable_read(Path(args.build[0]), MAX_METADATA))
        result = build_linux_pair(selection, Path(args.build[1]))
        sys.stdout.buffer.write(_json(result))
        return 0 if result['status'] == 'COMPLETE_BUILD_PAIR' else 2
    root = Path(args.check_bundle[0])
    _scratch_usage(root)
    bundle = {path.relative_to(root).as_posix(): _stable_read(path) for path in root.rglob('*') if path.is_file()}
    sys.stdout.buffer.write(_json(check_build_bundle(bundle, args.check_bundle[1])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
