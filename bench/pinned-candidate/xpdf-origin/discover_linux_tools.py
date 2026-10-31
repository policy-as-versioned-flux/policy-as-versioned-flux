#!/usr/bin/env python3
"""Separate discovery DATA capability. Public records cannot appoint execution."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import posixpath
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import time
from typing import Any, Mapping

PACKAGE = Path(__file__).resolve().parent
_DISCOVERY_APPOINTMENT: Mapping[str, Any] | None = None
MAX_TOTAL = 256 * 1024 * 1024
MAX_METADATA = 1024 * 1024
FAILURE_RESERVE = 16 * MAX_METADATA
DATA_LIMIT = MAX_TOTAL - FAILURE_RESERVE - 2 * MAX_METADATA
MAX_FILES = 8192
# Thirty query-stream prefixes, one partial-file prefix, and first-failure metadata.
FAILURE_FILES = 32
_PINS = {
    'QUERY-PROFILE.json': '80decb0cbcb0780746754311962ce67c36e2c6a73202fbf0a87a7bb9fc4b84b6',
    'RECORDS.json': 'f3f7f30a4b548b6a6834077e7244d61b4caa136a91e88eae98f437e9806c3622',
    'BINDING-PROJECTION.md': 'a22cb830df2e2c6a4f1c66c77deba31c7160ecc253fe7adb8b9cd0cb8061a33a',
}
_HELPER_PINS = {
    'build_linux_pair.py': '974fd63a8ab6b4e244b06ed10818a71e01f9e8c439b626b1533fc684681a8fce',
    'prepare_source.py': '1bf46d43d1ef2879ef1481dda8f46ce24349d0b6c3622acb462e0e6ab129fc87',
}
_spec = importlib.util.spec_from_file_location('xpdf_discovery_build_custody', PACKAGE / 'build_linux_pair.py')
assert _spec and _spec.loader
_build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_build)


class DiscoveryHold(ValueError):
    def __init__(self, stage: str, operation: str, message: str, *, observed_at: float | None = None):
        super().__init__(message)
        self.stage, self.operation = stage, operation
        self.observed_at = observed_at


def _json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require(condition: Any, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load(raw: bytes) -> Any:
    def pairs(entries):
        output = {}
        for key, value in entries:
            _require(key not in output, 'duplicate JSON key')
            output[key] = value
        return output
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def _contract(name: str) -> bytes:
    raw = (PACKAGE / 'discovery-contract' / name).read_bytes()
    _require(name in _PINS and _sha(raw) == _PINS[name], 'discovery contract drift')
    return raw


def _new_result(selection: Mapping[str, Any]) -> dict[str, Any]:
    return dict(schema='twin.xpdf-linux-discovery-result/v1', scope='DISCOVERY_ONLY', selection_sha256=_sha(_json(dict(selection))),
        run_identity=None, inventory_state='NOT_STARTED', build_hold='H_PROBE_EXECUTION_UNESTABLISHED', build_complete=False, native_execution=False,
        original_started=None, deadline=None, entered=None, finished=None, bootstrap=None, tools=[], module_root=None, modules=[], commands=[], faults=[],
        custody=dict(known_terminal=False, workspace_preserved=True, reason='discovery not appointed'), files_manifest_sha256=None, gcc_internals=[], directory_snapshots=[])


def _fault(result: dict[str, Any], stage: str, operation: str, error: BaseException, at: float | None) -> None:
    if len(result['faults']) < 16:
        message = str(error).encode('utf-8')[:2048].decode('utf-8', 'ignore')
        result['faults'].append(dict(stage=stage, operation=operation[:64], error_type=type(error).__name__.encode('ascii', 'replace')[:128].decode(),
            errno=error.errno if isinstance(error, OSError) else None, message=message, at=at))
    for secondary in getattr(error, '_discovery_close_faults', ()):
        if len(result['faults']) < 16:
            result['faults'].append(dict(secondary))
    result['custody'] = dict(known_terminal=False, workspace_preserved=True, reason='partial or unknown discovery facts')
    if result['inventory_state'] != 'NOT_STARTED':
        result['inventory_state'] = 'PARTIAL_DATA'


def _close_files(descriptors: list[int | None], primary: BaseException | None, stage: str) -> None:
    """One attempt per owned descriptor; a failed close is an unknown outcome."""
    first = primary
    for descriptor in descriptors:
        if descriptor is None:
            continue
        try:
            os.close(descriptor)
        except BaseException as error:
            if first is None:
                first = error
            else:
                faults = getattr(first, '_discovery_close_faults', [])
                if len(faults) < 4:
                    message = ('descriptor close unestablished: ' + str(error)).encode('utf-8')[:2048].decode('utf-8', 'ignore')
                    faults.append(dict(stage=stage, operation=f'close-fd-{descriptor}', error_type=type(error).__name__.encode('ascii', 'replace')[:128].decode(),
                        errno=error.errno if isinstance(error, OSError) else None, message=message, at=None))
                    setattr(first, '_discovery_close_faults', faults)
    if primary is None and first is not None:
        raise first


def _closed(value: Any, keys: str) -> None:
    _require(type(value) is dict and set(value) == set(keys.split()), 'closed record keys')


def _text(value: Any, limit: int, ascii_only: bool = False, nonempty: bool = True) -> None:
    _require(type(value) is str and (bool(value) or not nonempty) and len(value.encode('utf-8')) <= limit, 'bounded text')
    _require(not ascii_only or value.isascii(), 'ASCII text')


def _pin(value: Any, length: int = 64) -> None:
    _require(type(value) is str and re.fullmatch('[a-f0-9]{' + str(length) + '}', value) is not None, 'digest shape')


def _number(value: Any, nullable: bool = True) -> None:
    _require((nullable and value is None) or type(value) in (int, float) and math.isfinite(value), 'finite observed number')


def _integer(value: Any, minimum: int = 0, maximum: int = MAX_TOTAL) -> None:
    _require(type(value) is int and minimum <= value <= maximum, 'strict bounded integer')


def _absolute(value: Any) -> None:
    _text(value, 4096)
    _require(value.startswith('/') and str(PurePosixPath(value)) == value and not any(p in ('.', '..') for p in value.split('/'))
             and '\\' not in value and '\x00' not in value, 'canonical absolute POSIX path')


def _selection(value: Any) -> None:
    _closed(value, 'schema scope source_commit source_tree workflow_sha256 driver_sha256 bootstrap_selection_sha256 query_profile_sha256 limits_profile expected_row')
    _require(value['schema'] == 'twin.xpdf-linux-discovery-selection/v1' and value['scope'] == 'DISCOVERY_ONLY'
             and value['limits_profile'] == 'discovery-A60/v1', 'separate discovery selection')
    for field in ('source_commit', 'source_tree'):
        _pin(value[field], 40)
    for field in ('workflow_sha256', 'driver_sha256', 'bootstrap_selection_sha256', 'query_profile_sha256'):
        _pin(value[field])
    _require(value['query_profile_sha256'] == _PINS['QUERY-PROFILE.json'], 'fixed query profile')
    _require(value['expected_row'] == {'os': 'ubuntu-24.04', 'arch': 'x86_64-linux'}, 'fixed row')


def _identity(value: Any, kind: str) -> None:
    _require(type(value) is list and len(value) == 9 and all(type(v) is int for v in value), 'nine strict identity integers')
    # dev, ino, mode, uid, gid, size, mtime_ns, ctime_ns, nlink.
    _require(value[0] >= 0 and value[1] >= 0 and value[3] == 0 and value[4] >= 0 and value[5] >= 0 and value[8] > 0, 'root-owned identity')
    predicate = {'file': stat.S_ISREG, 'directory': stat.S_ISDIR, 'link': stat.S_ISLNK}[kind]
    _require(predicate(value[2]) and (kind == 'link' or not value[2] & 0o022), 'safe object mode')


def _file(value: Any, role: str, by_hash: dict[str, bytes], roles: dict[str, set[str]]) -> None:
    _closed(value, 'role path resolved links before after sha256 bytes')
    _require(value['role'] == role, 'candidate role')
    for field in ('path', 'resolved'):
        _absolute(value[field])
    _require(type(value['links']) is list and len(value['links']) <= 40, 'bounded symlink route')
    for link in value['links']:
        _closed(link, 'path target identity')
        _absolute(link['path'])
        _text(link['target'], 4096)
        _require('\x00' not in link['target'], 'link target NUL')
        _identity(link['identity'], 'link')
    _identity(value['before'], 'file')
    _identity(value['after'], 'file')
    _pin(value['sha256'])
    _integer(value['bytes'])
    _require(value['before'] == value['after'] and value['before'][5] == value['bytes'], 'stable file identity/size')
    _require(value['sha256'] in by_hash and len(by_hash[value['sha256']]) == value['bytes'], 'candidate bytes absent')
    _require(role in roles.get(value['sha256'], set()), 'candidate payload role association')
    current, remaining, used = '/', list(PurePosixPath(value['path']).parts[1:]), 0
    while remaining:
        current = posixpath.join(current, remaining.pop(0))
        if used < len(value['links']) and current == value['links'][used]['path']:
            target = value['links'][used]['target']
            resolved = posixpath.normpath(target if target.startswith('/') else posixpath.join(posixpath.dirname(current), target))
            _absolute(resolved)
            remaining = list(PurePosixPath(resolved).parts[1:]) + remaining
            current = '/'
            used += 1
    _require(used == len(value['links']) and current == value['resolved'], 'exact observed symlink/resolved path relation')


def _projection(result: dict[str, Any], query: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    environment = _build._json(query['environment'])  # Normative ASCII canonical JSON WITH newline.
    command = dict(id=f'bootstrap-input-tools/{query["index"]:03}', phase='bootstrap-input-tools', argv=query['argv'],
        environment_sha256=_sha(environment), started=query['started'], deadline=query['deadline'], ended=query['finished'], custody=query['custody'], disposition='HELD')
    context = dict(selection_sha256=result['selection_sha256'], clock=dict(started=result['original_started'], deadline=result['deadline'], ended=result['finished']))
    return context, command


def _gnu_version(index: int, raw: bytes) -> None:
    # A deliberately finite DATA syntax, not executable trust or actual compatibility.
    # GCC's Ubuntu banner identifies the compiler without a literal "GNU" token.
    version = rb'(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){1,3}'
    vendor = rb'\((?:GCC|GNU|Ubuntu [0-9][A-Za-z0-9.+~:-]*)\)'
    headings = {
        1: rb'GNU Make ', 2: rb'gcc ' + vendor + rb' ', 3: rb'g\+\+ ' + vendor + rb' ',
        4: rb'GNU patch ', 5: rb'GNU assembler \(GNU Binutils(?: for Ubuntu)?\) ',
        6: rb'GNU ld \(GNU Binutils(?: for Ubuntu)?\) ', 7: rb'GNU ar \(GNU Binutils(?: for Ubuntu)?\) ',
        8: rb'GNU ranlib \(GNU Binutils(?: for Ubuntu)?\) ', 9: rb'GNU readelf \(GNU Binutils(?: for Ubuntu)?\) ',
    }
    _require(index in headings and raw.endswith(b'\n') and b'\r' not in raw, 'unsupported version DATA framing')
    lines = raw.split(b'\n')[:-1]
    _require(bool(lines) and re.fullmatch(headings[index] + version, lines[0]) is not None, 'unsupported intended GNU tool/version')
    notices = (
        rb'', rb'Copyright \(C\) [0-9, -]+ Free Software Foundation, Inc\.',
        rb'License GPLv[23]\+: GNU GPL version [23] or later <https?://gnu\.org/licenses/gpl\.html>',
        rb'This is free software: you are free to change and redistribute it\.',
        rb'There is NO WARRANTY, to the extent permitted by law\.',
        rb'This is free software; see the source for copying conditions\.  There is NO',
        rb'warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE\.',
        rb'This program is free software; you may redistribute it under the terms of',
        rb'the GNU General Public License version [23] or \(at your option\) a later version\.',
        rb'This program has absolutely no warranty\.', rb'Built for x86_64[-A-Za-z0-9_]*',
        rb"This assembler was configured for a target of [`']x86_64[-A-Za-z0-9_]*'\.",
        rb'Written by [A-Za-z .,\-]+\.',
    )
    _require(all(any(re.fullmatch(pattern, line) is not None for pattern in notices) for line in lines[1:]), 'unsupported or ambiguous version DATA tail')


def _query(query: Any, index: int, result: dict[str, Any], bundle: Mapping[str, bytes], by_hash: dict[str, bytes]) -> bool:
    _closed(query, 'index argv environment command_binding_sha256 started deadline finished stdout stderr raw_wait_status returncode custody')
    _integer(query['index'], 0, 14)
    profile = _load(_contract('QUERY-PROFILE.json'))
    _require(query['index'] == index and query['argv'] == profile['ordered_query_argv'][index], 'fixed ordered query prefix')
    _require(type(query['environment']) is dict and bundle.get('ENVIRONMENT.json') == _build._json(query['environment']), 'exact newline environment artifact')
    home = query['environment'].get('HOME')
    _require(type(home) is str and home.endswith('/home'), 'owned environment')
    root = Path(home).parent
    _absolute(str(root))
    _require(query['environment'] == _build._fresh_environment(root), 'fresh closed environment')
    for field in ('started', 'deadline', 'finished'):
        _number(query[field])
    if query['started'] is not None and query['deadline'] is not None:
        _require(query['deadline'] == query['started'] + 5 and result['deadline'] is not None
                 and query['deadline'] + 10 <= result['deadline'], 'five seconds plus original ten-second reserve')
    if query['finished'] is not None and query['started'] is not None:
        _require(query['finished'] >= query['started'], 'query clock order')
    if query['raw_wait_status'] is not None:
        _integer(query['raw_wait_status'], 0, 65535)
    if query['returncode'] is not None:
        _integer(query['returncode'], -126, 255)
    custody_schema = _build._schema('BUILD-RESULT.schema.json')['properties']['commands']['items']['properties']['custody']
    _build._validate(query['custody'], custody_schema)
    _require(query['command_binding_sha256'] == query['custody']['command_binding_sha256'], 'outer/custody observed binding equality')
    context, command = _projection(result, query)
    if query['command_binding_sha256'] is not None:
        _pin(query['command_binding_sha256'])
        _require(query['command_binding_sha256'] == _build._binding(context, command), 'independent earlier-fact binding projection')
    known = _build._check_custody(context, command)
    custody = query['custody']
    _require(query['raw_wait_status'] == custody['raw_wait'], 'actual raw wait projection')
    decoded = custody['exit_code'] if custody['wait_kind'] == 'EXITED' else -custody['signal'] if custody['wait_kind'] == 'SIGNALED' else None
    _require(query['returncode'] == decoded, 'actual return code projection')
    streams_known = True
    for name in ('stdout', 'stderr'):
        record = query[name]
        if record is None:
            streams_known = False
            continue
        _closed(record, 'sha256 bytes complete observed_bytes_lower_bound')
        _pin(record['sha256'])
        _integer(record['bytes'], 0, 16 * MAX_METADATA)
        _integer(record['observed_bytes_lower_bound'], record['bytes'], 2**63 - 1)
        _require(type(record['complete']) is bool and record['sha256'] in by_hash and len(by_hash[record['sha256']]) == record['bytes'], 'retained stream')
        if record['complete']:
            _require(record['bytes'] == record['observed_bytes_lower_bound'], 'complete stream lower bound')
        streams_known &= record['complete']
    success = known and streams_known and query['returncode'] == 0 and query['command_binding_sha256'] is not None and all(query[k] is not None for k in ('started', 'deadline', 'finished'))
    if success:
        _require(query['finished'] <= query['deadline'], 'query terminal after bound')
        output = by_hash[query['stdout']['sha256']]
        try:
            if index == 0:
                _cmake_root(output)
            elif index < 10:
                _gnu_version(index, output)
            elif index == 10:
                _require(re.fullmatch(rb'x86_64-(?:[A-Za-z0-9_]+-)?linux(?:-[A-Za-z0-9_]+)*\n?', output) is not None, 'unsupported target observation')
            elif index == 11:
                _require(bool(output), 'unobserved specs')
            else:
                _internal_path(output, ('cc1', 'cc1plus', 'collect2')[index - 12])
        except (ValueError, UnicodeError):
            success = False  # Retain unsupported raw facts as held; no next dependent query.
    return bool(success)


def check_discovery_bundle(bundle: Mapping[str, bytes], expected_selection_sha256: str) -> dict[str, Any]:
    """Pure closed DATA checker; never inspect the host or appoint a later build."""
    _require(len(bundle) <= MAX_FILES and all(type(k) is str and _build._safe_name(k) and type(v) is bytes and len(v) <= MAX_TOTAL for k, v in bundle.items()), 'bundle paths/extents')
    _require(sum(map(len, bundle.values())) <= MAX_TOTAL and {'SELECTION.json', 'ENVIRONMENT.json', 'RESULT.json', 'FILES.json'}.issubset(bundle), 'bundle cap/required artifacts')
    selection, result, files = [_load(bundle[name]) for name in ('SELECTION.json', 'RESULT.json', 'FILES.json')]
    _selection(selection)
    _require(all(bundle[name] == _json(value) and len(bundle[name]) <= MAX_METADATA for name, value in [('SELECTION.json', selection), ('RESULT.json', result), ('FILES.json', files)]), 'canonical bounded records')
    _closed(result, 'schema scope selection_sha256 run_identity inventory_state build_hold build_complete native_execution original_started deadline entered finished bootstrap tools module_root modules commands faults custody files_manifest_sha256 gcc_internals directory_snapshots')
    _require(result['schema'] == 'twin.xpdf-linux-discovery-result/v1' and result['scope'] == 'DISCOVERY_ONLY'
             and result['inventory_state'] in ('NOT_STARTED', 'PARTIAL_DATA', 'COMPLETE_DATA'), 'discovery result discriminator')
    _require(result['selection_sha256'] == expected_selection_sha256 == _sha(bundle['SELECTION.json']), 'selected discovery bytes')
    _require(result['build_hold'] == 'H_PROBE_EXECUTION_UNESTABLISHED' and result['build_complete'] is False and result['native_execution'] is False, 'DATA never grants build/native execution')
    _closed(files, 'schema entries')
    _require(files['schema'] == 'twin.xpdf-linux-discovery-files/v1' and type(files['entries']) is list and len(files['entries']) <= MAX_FILES, 'files manifest')
    _require(result['files_manifest_sha256'] is None or result['files_manifest_sha256'] == _sha(bundle['FILES.json']), 'observed files digest')
    names = []
    for entry in files['entries']:
        _closed(entry, 'path sha256 bytes role')
        _text(entry['role'], 64, True)
        _pin(entry['sha256'])
        _integer(entry['bytes'])
        name = entry['path']
        _require(type(name) is str and name in bundle and _build._safe_name(name), 'manifest payload path')
        _require(len(bundle[name]) == entry['bytes'] and _sha(bundle[name]) == entry['sha256'], 'manifest payload identity')
        if entry['role'] == 'metadata':
            _require(entry['bytes'] <= MAX_METADATA, 'metadata cap')
        names.append(name)
    _require(names == sorted(set(names)) and set(names) == set(bundle) - {'FILES.json', 'RESULT.json'}, 'exact sorted payload set; no self/future hash')
    by_hash = {_sha(value): value for value in bundle.values()}
    roles: dict[str, set[str]] = {}
    for entry in files['entries']:
        roles.setdefault(entry['sha256'], set()).add(entry['role'])
    for key in ('original_started', 'deadline', 'entered', 'finished'):
        _number(result[key])
    if result['run_identity'] is not None:
        _run_identity(result['run_identity'], selection)
    if result['original_started'] is not None and result['deadline'] is not None:
        _require(result['original_started'] <= result['deadline'] <= result['original_started'] + 60, 'original inclusive sixty seconds')
    _closed(result['custody'], 'known_terminal workspace_preserved reason')
    _require(type(result['custody']['known_terminal']) is bool and result['custody']['workspace_preserved'] is True, 'truthful retained custody')
    _text(result['custody']['reason'], 2048, True, False)
    _require(type(result['faults']) is list and len(result['faults']) <= 16, 'bounded first fault prefix')
    for fault in result['faults']:
        _closed(fault, 'stage operation error_type errno message at')
        _require(fault['stage'] in ('appointment', 'setup', 'snapshot', 'query', 'custody', 'export', 'clock', 'capacity'), 'fault stage')
        _text(fault['operation'], 64, True, False)
        _text(fault['error_type'], 128, True)
        _text(fault['message'], 2048, False, False)
        _number(fault['at'])
        _require(fault['errno'] is None or type(fault['errno']) is int, 'fault errno')
    for field, role, maximum in [('tools', 'selector', 11), ('modules', 'cmake-module', MAX_FILES), ('gcc_internals', 'gcc-internal', 3)]:
        _require(type(result[field]) is list and len(result[field]) <= maximum, 'bounded candidate collection')
        for candidate in result[field]:
            _file(candidate, role, by_hash, roles)
    _require([v['path'] for v in result['tools']] == _load(_contract('QUERY-PROFILE.json'))['selectors'][:len(result['tools'])], 'fixed selector prefix')
    _require(type(result['commands']) is list and len(result['commands']) <= 15, 'fixed query prefix length')
    _require(not result['commands'] or len(result['tools']) == 11, 'all fixed selector identities before any query attempt')
    prior_end, failed = result['entered'], False
    for index, query in enumerate(result['commands']):
        _require(not failed, 'query after unknown/failure')
        succeeded = _query(query, index, result, bundle, by_hash)
        if query['started'] is not None and prior_end is not None:
            _require(query['started'] >= prior_end, 'serial raw query chronology')
        prior_end = query['finished']
        failed = not succeeded
    bootstrap = []
    if result['bootstrap'] is not None:
        _pin(result['bootstrap'])
        _require(result['bootstrap'] in by_hash and 'BOOTSTRAP-SELECTION.json' in bundle, 'bootstrap observed artifact')
        bootstrap = _check_bootstrap(bundle, selection, result, by_hash, roles)
    if result['module_root'] is not None:
        _absolute(result['module_root'])
        _require(bool(result['commands']) and result['commands'][0]['stdout'] is not None
                 and result['module_root'] == _cmake_root(by_hash[result['commands'][0]['stdout']['sha256']]), 'fixed module-root/raw-version association')
    _require(not result['modules'] or result['module_root'] is not None, 'module files before module root observation')
    for item in result['modules']:
        _require(PurePosixPath(item['path']).is_relative_to(result['module_root']) and item['path'] == item['resolved'] and not item['links'], 'module DATA scope/no symlinks')
    _require(len(result['gcc_internals']) <= min(3, max(0, len(result['commands']) - 12)), 'GCC candidate before its actual fixed query')
    for index, item in enumerate(result['gcc_internals']):
        query = result['commands'][index + 12]
        _require(query['stdout'] is not None and query['stdout']['complete']
                 and item['path'] == _internal_path(by_hash[query['stdout']['sha256']], ('cc1', 'cc1plus', 'collect2')[index]), 'GCC internal raw reply association')
    _check_directory_snapshots(bundle, result, bootstrap, result['inventory_state'] == 'COMPLETE_DATA')
    if result['inventory_state'] == 'NOT_STARTED':
        _require(not result['commands'] and not result['tools'] and not result['modules'] and not result['gcc_internals'] and not result['directory_snapshots']
                 and result['bootstrap'] is None and result['module_root'] is None, 'not-started has no invented acquisition')
    if result['inventory_state'] == 'COMPLETE_DATA':
        _check_complete(bundle, selection, result, by_hash, roles)
    return {key: result[key] for key in ('inventory_state', 'build_hold', 'build_complete', 'native_execution')}


def _vector(info: Any) -> list[int]:
    return [getattr(info, 'st_' + key) for key in ('dev', 'ino', 'mode', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns', 'nlink')]


def _check_bootstrap(bundle: Mapping[str, bytes], selection: dict[str, Any], result: dict[str, Any], by_hash: dict[str, bytes], roles: dict[str, set[str]]) -> list[dict[str, Any]]:
    selected_boot = _load(bundle['BOOTSTRAP-SELECTION.json'])
    _require(_sha(bundle['BOOTSTRAP-SELECTION.json']) == selection['bootstrap_selection_sha256'], 'independent bootstrap DATA identity')
    _closed(selected_boot, 'schema interpreter roots loaded_files files startup_provenance_sha256 writer_control_sha256')
    _require(selected_boot['schema'] == 'twin.xpdf-discovery-parent-bootstrap/v1', 'parent bootstrap discriminator')
    for key in ('startup_provenance_sha256', 'writer_control_sha256'):
        _pin(selected_boot[key])
    _require(type(selected_boot['roots']) is list and bool(selected_boot['roots']) and selected_boot['roots'] == sorted(set(selected_boot['roots'])), 'selected bootstrap roots')
    for path in selected_boot['roots']:
        _absolute(path)
    _require(result['bootstrap'] in by_hash, 'bootstrap inventory bytes missing')
    boot = _load(by_hash[result['bootstrap']])
    _closed(boot, 'schema selected_bootstrap_sha256 interpreter loaded_files')
    _require(boot['schema'] == 'twin.xpdf-linux-bootstrap-inventory/v1' and boot['selected_bootstrap_sha256'] == selection['bootstrap_selection_sha256'], 'bootstrap inventory association')
    _require(type(boot['loaded_files']) is list and len(boot['loaded_files']) <= MAX_FILES, 'loaded candidate count')
    boot_candidates = [boot['interpreter']] + boot['loaded_files']
    _require(boot['interpreter']['path'] == selected_boot['interpreter'] and [v['path'] for v in boot['loaded_files']] == selected_boot['loaded_files']
             and selected_boot['loaded_files'] == sorted(set(selected_boot['loaded_files']))
             and set(selected_boot['files']) == {v['path'] for v in boot_candidates}, 'exact independently selected startup candidates; no closure inference')
    for value in boot_candidates:
        _file(value, 'bootstrap', by_hash, roles)
        _require(selected_boot['files'][value['path']] == value['sha256']
                 and any(PurePosixPath(value['path']).is_relative_to(root) and PurePosixPath(value['resolved']).is_relative_to(root) for root in selected_boot['roots']), 'bootstrap candidate path/byte association')
    return boot_candidates


def _check_complete(bundle: Mapping[str, bytes], selection: dict[str, Any], result: dict[str, Any], by_hash: dict[str, bytes], roles: dict[str, set[str]]) -> None:
    _require(sum(map(len, bundle.values())) <= MAX_TOTAL - FAILURE_RESERVE, 'complete DATA consumed its reserved failure capacity')
    _require(len(bundle) <= MAX_FILES - FAILURE_FILES, 'complete DATA consumed its reserved failure file count')
    _require(not result['faults'] and result['custody']['known_terminal'] is True and result['files_manifest_sha256'] is not None, 'complete inventory cannot contain faults/unknown custody/export')
    _require(all(result[k] is not None for k in ('original_started', 'deadline', 'entered', 'finished', 'run_identity', 'bootstrap', 'module_root')), 'complete observed facts required')
    _require(result['original_started'] <= result['entered'] <= result['finished'] <= result['deadline'], 'complete original inclusive clock')
    _run_identity(result['run_identity'], selection)
    _require(len(result['tools']) == 11 and len(result['commands']) == 15 and len(result['gcc_internals']) == 3, 'complete fixed candidate/query set')
    _require(all(_query(q, i, result, bundle, by_hash) for i, q in enumerate(result['commands'])), 'complete exact terminal/custody/stream facts')
    _require('PARENT.json' in bundle and 'BOOTSTRAP-SELECTION.json' in bundle and 'ENTRY-OBSERVATION.json' in bundle and 'CAPACITY.json' in bundle, 'independent source/bootstrap/row/capacity associations absent')
    parent = _load(bundle['PARENT.json'])
    _closed(parent, 'selection_sha256 source_commit source_tree workflow_source source_files run_identity owned_parent original_started a_deadline deadline bootstrap_selection query_acceptance capacity')
    _require(parent['selection_sha256'] == result['selection_sha256'] and parent['source_commit'] == selection['source_commit'] and parent['source_tree'] == selection['source_tree']
             and parent['run_identity'] == result['run_identity'], 'parent source/run association')
    _number(parent['a_deadline'], False)
    _require(parent['original_started'] == result['original_started'] and parent['deadline'] == result['deadline'] == min(result['original_started'] + 60, parent['a_deadline']), 'appointed parent clock association')
    _absolute(parent['owned_parent'])
    _require(Path(parent['owned_parent']).name == f'D-{result["run_identity"]["run_id"]}-{result["run_identity"]["run_attempt"]}', 'owned run root association')
    _require(all(q['environment'] == _build._fresh_environment(Path(parent['owned_parent'])) for q in result['commands']), 'owned selected environment association')
    _require(type(parent['source_files']) is dict, 'held source closure')
    for path, pin in parent['source_files'].items():
        _absolute(path)
        _pin(pin)
        _require(pin in by_hash, 'retained source closure bytes')
    drivers = [path for path in parent['source_files'] if PurePosixPath(path).name == 'discover_linux_tools.py']
    _require(len(drivers) == 1 and parent['source_files'][drivers[0]] == selection['driver_sha256'], 'exact selected discovery driver')
    package = PurePosixPath(drivers[0]).parent
    expected = {str(package / name): pin for name, pin in _HELPER_PINS.items()}
    expected.update({str(package / 'build-contract' / name): pin for name, pin in _build._CONTRACT_PINS.items()})
    expected.update({str(package / 'discovery-contract' / name): pin for name, pin in _PINS.items()})
    _absolute(parent['workflow_source'])
    _require(set(parent['source_files']) == set(expected) | {drivers[0], parent['workflow_source']}
             and all(parent['source_files'][path] == pin for path, pin in expected.items())
             and parent['source_files'][parent['workflow_source']] == selection['workflow_sha256'], 'unchanged custody/helper/profile/workflow closure')
    accepted = parent['query_acceptance']
    _closed(accepted, 'selectors review_sha256 writer_control_sha256')
    _pin(accepted['review_sha256'])
    _pin(accepted['writer_control_sha256'])
    _require(accepted['selectors'] == {item['path']: item for item in result['tools']}, 'independent trusted-query/writer-control acceptance association')
    _require(_load(bundle['BOOTSTRAP-SELECTION.json']) == parent['bootstrap_selection'], 'appointed bootstrap selection')
    boot_candidates = _check_bootstrap(bundle, selection, result, by_hash, roles)
    entry = _load(bundle['ENTRY-OBSERVATION.json'])
    _closed(entry, 'system machine python_version isolated no_site dont_write_bytecode entered')
    _require(entry['system'] == 'Linux' and entry['machine'] == 'x86_64' and type(entry['python_version']) is list and len(entry['python_version']) == 3
             and all(type(v) is int and v >= 0 for v in entry['python_version']) and entry['python_version'][:2] == [3, 12]
             and all(entry[k] is True for k in ('isolated', 'no_site', 'dont_write_bytecode')) and entry['entered'] == result['entered'], 'actual selected bootstrap/row observation')
    capacity = _load(bundle['CAPACITY.json'])
    _closed(capacity, 'selection observed_free_bytes live_disk_quota_enforced')
    _require(capacity['selection'] == parent['capacity'] and capacity['live_disk_quota_enforced'] is False, 'capacity DATA association; no hard quota')
    _closed(capacity['selection'], 'review_sha256 minimum_free_bytes')
    _pin(capacity['selection']['review_sha256'])
    _integer(capacity['selection']['minimum_free_bytes'], 1, 2**63 - 1)
    _integer(capacity['observed_free_bytes'], capacity['selection']['minimum_free_bytes'], 2**63 - 1)
    outputs = [by_hash[q['stdout']['sha256']] for q in result['commands']]
    _require(result['module_root'] == _cmake_root(outputs[0]), 'sole fixed prospective module root')
    for index in range(1, 10):
        _gnu_version(index, outputs[index])
    _require(re.fullmatch(rb'x86_64-(?:[A-Za-z0-9_]+-)?linux(?:-[A-Za-z0-9_]+)*\n?', outputs[10]) is not None and bool(outputs[11]), 'target/specs raw DATA')
    internals = [_internal_path(outputs[index + 12], name) for index, name in enumerate(('cc1', 'cc1plus', 'collect2'))]
    _require([v['path'] for v in result['gcc_internals']] == internals and len({str(PurePosixPath(p).parent) for p in internals}) == 1, 'fixed GCC reply/candidate association')
    for item in result['gcc_internals']:
        _require(PurePosixPath(item['resolved']).parent == PurePosixPath(item['path']).parent, 'GCC candidate escaped its canonical root')
    module_paths = [value['path'] for value in result['modules']]
    _require(module_paths == sorted(set(module_paths)) and all(PurePosixPath(path).is_relative_to(result['module_root']) for path in module_paths), 'exact module candidate scope/order')
    _require(all(not v['links'] and v['path'] == v['resolved'] for v in result['modules']), 'no module symlink traversal')
    _check_directory_snapshots(bundle, result, boot_candidates, True)


def _check_directory_snapshots(bundle: Mapping[str, bytes], result: dict[str, Any], bootstrap: list[dict[str, Any]], complete: bool) -> None:
    directories = result['directory_snapshots']
    _require(type(directories) is list and len(directories) <= MAX_FILES, 'bounded directory snapshots')
    expected_parents: set[str] = set()
    for item in result['tools'] + result['gcc_internals'] + result['modules'] + bootstrap:
        for path in [item['path'], item['resolved']] + [link['path'] for link in item['links']]:
            expected_parents.update(str(p) for p in PurePosixPath(path).parents)
    if result['module_root'] is not None:
        expected_parents.add(result['module_root'])
        expected_parents.update(str(p) for p in PurePosixPath(result['module_root']).parents)
    artifacts = {}
    for name, raw in bundle.items():
        if not name.startswith('directories/'):
            continue
        value = _load(raw)
        _closed(value, 'path before_names after_names')
        _require(value['path'] not in artifacts, 'duplicate directory DATA')
        artifacts[value['path']] = value
    paths = [item['path'] for item in directories]
    _require(paths == sorted(set(paths)) and set(paths) == set(artifacts), 'exact ordered directory DATA associations')
    for item in directories:
        _closed(item, 'path before after child_names_sha256')
        _absolute(item['path'])
        _identity(item['before'], 'directory')
        _identity(item['after'], 'directory')
        _pin(item['child_names_sha256'])
        data = artifacts[item['path']]
        for key in ('before_names', 'after_names'):
            _require(type(data[key]) is list and data[key] == sorted(set(data[key])) and len(data[key]) <= MAX_FILES, 'sorted bounded directory names')
            for child in data[key]:
                _text(child, 4096)
                _require(child not in ('.', '..') and '/' not in child and '\x00' not in child, 'directory component')
        _require(item['child_names_sha256'] == _sha(_json(data['before_names'])), 'actual directory child-name digest')
        if complete:
            _require(item['before'] == item['after'] and data['before_names'] == data['after_names'], 'complete directory snapshot changed')
    # Module directories are a rooted observed graph, not just ancestors of files:
    # stable empty leaves have no file descendant from which to infer their path.
    module_dirs: set[str] = set()
    if result['module_root'] is not None:
        pending = [result['module_root']]
        while pending:
            directory = pending.pop()
            if directory in module_dirs or directory not in artifacts:
                continue
            module_dirs.add(directory)
            names = artifacts[directory]['before_names']
            if not complete:
                names = sorted(set(names) | set(artifacts[directory]['after_names']))
            for child in names:
                candidate = posixpath.join(directory, child)
                if candidate in artifacts:
                    pending.append(candidate)
    _require(set(paths).issubset(expected_parents | module_dirs), 'unrelated directory snapshot')
    if complete:
        _require(set(paths) == expected_parents | module_dirs, 'missing traversed candidate directory snapshot')
        module_files = {v['path'] for v in result['modules']}
        _require({path for path in paths if PurePosixPath(path).is_relative_to(result['module_root'])} == module_dirs
                 and module_files.isdisjoint(module_dirs), 'unrooted or conflicting module directory/file')
        for path in module_files:
            parent = str(PurePosixPath(path).parent)
            _require(parent in module_dirs and PurePosixPath(path).name in artifacts[parent]['before_names'], 'module file missing from observed parent child set')
        for directory in module_dirs:
            for child in artifacts[directory]['before_names']:
                _require(posixpath.join(directory, child) in module_files | module_dirs, 'omitted module file/subdirectory or unsupported entry')


def _directory_fd(path: str) -> int:
    _absolute(path)
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in PurePosixPath(path).parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            old_fd, fd = fd, next_fd
            _close_files([old_fd], None, 'snapshot')
        return fd
    except BaseException as error:
        _close_files([fd], error, 'snapshot')
        raise


class _Collection:
    """Private bounded observation state; effects cross only OS/clock boundaries."""
    def __init__(self, result: dict[str, Any], root: Path):
        self.result, self.root = result, root
        self.payload: dict[str, tuple[bytes, str]] = {}
        self.directories: dict[str, tuple[list[int], list[str]]] = {}
        self.candidates: list[dict[str, Any]] = []

    def tick(self) -> float:
        now = time.monotonic()
        if type(now) not in (int, float) or not math.isfinite(now):
            raise DiscoveryHold('clock', 'monotonic', 'unknown original clock')
        started = self.result['original_started']
        if started is None or now < started:
            raise DiscoveryHold('clock', 'original-start', 'observation before or without immutable original start', observed_at=now)
        if now > self.result['deadline']:
            raise DiscoveryHold('clock', 'original-deadline', 'original discovery bound exhausted', observed_at=now)
        return now

    def room(self, extra: int = 0, files: int = 0) -> None:
        if len(self.payload) + files > MAX_FILES - 2 - FAILURE_FILES or sum(len(raw) for raw, _ in self.payload.values()) + extra > DATA_LIMIT:
            raise DiscoveryHold('capacity', 'retained-cap', 'discovery payload exceeds fixed retained bounds/reserve')

    def add(self, path: str, raw: bytes, role: str) -> None:
        self.tick()
        if path in self.payload or not _build._safe_name(path) or len(raw) > MAX_TOTAL or role == 'metadata' and len(raw) > MAX_METADATA:
            raise DiscoveryHold('capacity', 'payload', 'duplicate, unsafe or excessive payload')
        self.room(len(raw), 1)
        self.payload[path] = (raw, role)
        self.tick()

    def names(self, fd: int) -> list[str]:
        names: list[str] = []
        extent = 2
        with os.scandir(fd) as entries:
            for entry in entries:
                self.tick()
                _require(len(names) < MAX_FILES, 'bounded directory child count')
                name = entry.name
                _text(name, 4096)
                _require(name not in ('.', '..') and '/' not in name and '\x00' not in name, 'directory child name')
                extent += len(_json(name)) + bool(names)
                _require(extent <= MAX_METADATA, 'bounded directory child metadata')
                names.append(name)
        _require(len(names) == len(set(names)), 'duplicate directory child')
        return sorted(names)

    def directory(self, path: str) -> list[str]:
        self.tick()
        fd = _directory_fd(path)
        primary = None
        try:
            before = _vector(os.fstat(fd))
            _identity(before, 'directory')
            names = self.names(fd)
            after = _vector(os.fstat(fd))
            self.tick()
            _require(before == after and after == _vector(os.lstat(path)), 'directory identity changed during snapshot')
        except BaseException as error:
            primary = error
            raise
        finally:
            _close_files([fd], primary, 'snapshot')
        if path in self.directories:
            _require(self.directories[path] == (before, names), 'directory changed between candidates')
        else:
            _require(len(self.directories) < MAX_FILES, 'directory snapshot count')
            self.directories[path] = (before, names)
        return names

    def resolve(self, path: str) -> tuple[str, list[dict[str, Any]]]:
        _absolute(path)
        remaining = list(PurePosixPath(path).parts[1:])
        current = '/'
        links: list[dict[str, Any]] = []
        while remaining:
            self.tick()
            self.directory(current)
            target = posixpath.join(current, remaining.pop(0))
            info = _vector(os.lstat(target))
            if stat.S_ISLNK(info[2]):
                _identity(info, 'link')
                _require(len(links) < 40, 'symlink route bound')
                raw_target = os.readlink(target)
                _text(raw_target, 4096)
                _require(info == _vector(os.lstat(target)), 'symlink changed')
                links.append(dict(path=target, target=raw_target, identity=info))
                resolved = posixpath.normpath(raw_target if raw_target.startswith('/') else posixpath.join(current, raw_target))
                _absolute(resolved)
                remaining = list(PurePosixPath(resolved).parts[1:]) + remaining
                current = '/'
            else:
                _identity(info, 'directory' if remaining else 'file')
                current = target
        return current, links

    def read(self, path: str, maximum: int, require_root: bool = True) -> tuple[bytes, list[int], list[int]]:
        self.tick()
        parent = _directory_fd(str(PurePosixPath(path).parent))
        fd = None
        raw = bytearray()
        primary = None
        try:
            fd = os.open(PurePosixPath(path).name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
            before = _vector(os.fstat(fd))
            if require_root:
                _identity(before, 'file')
            _require(stat.S_ISREG(before[2]) and before[5] <= maximum, 'regular bounded observed file')
            self.room(before[5], 1)
            while True:
                self.tick()
                block = os.read(fd, min(65536, maximum + 1 - len(raw)))
                raw.extend(block)
                self.tick()
                if len(raw) > maximum:
                    raise DiscoveryHold('capacity', 'file-read', 'observed regular file overflow')
                if not block:
                    break
            after = _vector(os.fstat(fd))
            current = _vector(os.stat(PurePosixPath(path).name, dir_fd=parent, follow_symlinks=False))
            _require(before == after == current and len(raw) == before[5], 'file identity/hash-length observation unstable')
            return bytes(raw), before, after
        except BaseException as error:
            primary = error
            if raw and 'journal/partial-file.bin' not in self.payload:
                self.payload['journal/partial-file.bin'] = (bytes(raw[:15 * MAX_METADATA]), 'failure-prefix')
            raise
        finally:
            _close_files([fd, parent], primary, 'snapshot')

    def snapshot(self, path: str, role: str, roots: list[str] | None = None) -> dict[str, Any]:
        resolved, links = self.resolve(path)
        if roots is not None:
            _require(any(PurePosixPath(path).is_relative_to(root) and PurePosixPath(resolved).is_relative_to(root) for root in roots), 'candidate outside sole selected root')
        if role == 'cmake-module':
            _require(not links, 'symlink in module snapshot')
        raw, before, after = self.read(resolved, min(MAX_TOTAL, DATA_LIMIT - sum(len(v[0]) for v in self.payload.values())))
        again, second_route = self.resolve(path)
        _require(again == resolved and links == second_route, 'candidate route changed')
        candidate = dict(role=role, path=path, resolved=resolved, links=links, before=before, after=after, sha256=_sha(raw), bytes=len(raw))
        self.add(f'files/{len(self.candidates):05}.bin', raw, role)
        self.candidates.append(candidate)
        return candidate

    def seal_directories(self) -> None:
        # Preserve actual changed observations as partial; never rewrite them into stability.
        changed = False
        for index, (path, (before, names)) in enumerate(sorted(self.directories.items())):
            self.tick()
            fd = _directory_fd(path)
            primary = None
            try:
                after = _vector(os.fstat(fd))
                after_names = self.names(fd)
            except BaseException as error:
                primary = error
                raise
            finally:
                _close_files([fd], primary, 'snapshot')
            changed |= before != after or names != after_names
            self.result['directory_snapshots'].append(dict(path=path, before=before, after=after, child_names_sha256=_sha(_json(names))))
            self.add(f'directories/{index:05}.json', _json(dict(path=path, before_names=names, after_names=after_names)), 'metadata')
            self.tick()
        _require(not changed, 'directory identity or child set changed')
        for candidate in self.candidates:
            self.tick()
            _require(_vector(os.lstat(candidate['resolved'])) == candidate['after'], 'candidate changed before terminal snapshot')


def _cmake_root(raw: bytes) -> str:
    lines = raw.decode('ascii').splitlines()
    _require(lines and sum(line.startswith('cmake version ') for line in lines) == 1, 'unambiguous CMake version')
    match = re.fullmatch(r'cmake version (0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[A-Za-z0-9._-]+)?', lines[0])
    _require(match is not None and (int(match[1]), int(match[2])) >= (3, 24), 'supported canonical CMake >=3.24')
    assert match is not None
    return f'/usr/share/cmake-{match[1]}.{match[2]}/Modules'


def _internal_path(raw: bytes, name: str) -> str:
    value = raw.decode('ascii')
    match = re.fullmatch(r'(/usr/lib/gcc/x86_64-linux-gnu/(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*))*/' + name + r')\n?', value)
    _require(match is not None, 'canonical GCC internal DATA reply')
    assert match is not None
    return match[1]


def _run_identity(value: Any, selection: dict[str, Any]) -> None:
    _closed(value, 'repository workflow_path run_id run_attempt job row source_commit')
    for key in ('repository', 'workflow_path', 'job', 'source_commit'):
        _text(value[key], 4096, True)
    for key in ('run_id', 'run_attempt'):
        _integer(value[key], 1, 2**63 - 1)
    _require(value['row'] == selection['expected_row'] and value['source_commit'] == selection['source_commit'], 'independently selected run/row/source')


def _appointment(selection: dict[str, Any], root: Path) -> dict[str, Any]:
    # No public dictionary can populate this distinct source-appointed slot.
    selected = _DISCOVERY_APPOINTMENT
    _require(selected is not None, 'discovery appointment absent')
    assert selected is not None
    value = _load(_json(dict(selected)))
    _closed(value, 'selection_sha256 source_commit source_tree workflow_source source_files run_identity owned_parent original_started a_deadline deadline bootstrap_selection query_acceptance capacity')
    _selection(selection)
    _require(value['selection_sha256'] == _sha(_json(selection)) and value['source_commit'] == selection['source_commit']
             and value['source_tree'] == selection['source_tree'], 'source-appointed selection differs')
    _run_identity(value['run_identity'], selection)
    for key in ('original_started', 'a_deadline', 'deadline'):
        _number(value[key], False)
    _require(value['original_started'] <= value['deadline'] == min(value['original_started'] + 60, value['a_deadline']), 'parent original discovery clock')
    _absolute(value['owned_parent'])
    _require(str(root) == value['owned_parent'] and root.name == f'D-{value["run_identity"]["run_id"]}-{value["run_identity"]["run_attempt"]}', 'exact independently owned root')
    _absolute(value['workflow_source'])
    required = [Path(__file__).resolve(), PACKAGE / 'build_linux_pair.py', PACKAGE / 'prepare_source.py', Path(value['workflow_source'])]
    required += [PACKAGE / 'build-contract' / name for name in _build._CONTRACT_PINS]
    required += [PACKAGE / 'discovery-contract' / name for name in _PINS]
    _require(type(value['source_files']) is dict and set(value['source_files']) == {str(p) for p in required}, 'exact discovery source/helper/profile/workflow closure')
    for pin in value['source_files'].values():
        _pin(pin)
    _require(value['source_files'][str(Path(__file__).resolve())] == selection['driver_sha256']
             and value['source_files'][value['workflow_source']] == selection['workflow_sha256'], 'appointed driver/workflow identity')
    _require(all(value['source_files'][str(PACKAGE / name)] == pin for name, pin in _HELPER_PINS.items()), 'unchanged accepted custody helper source')
    _require(_sha(_json(value['bootstrap_selection'])) == selection['bootstrap_selection_sha256'], 'independent bootstrap selection digest')
    boot = value['bootstrap_selection']
    _closed(boot, 'schema interpreter roots loaded_files files startup_provenance_sha256 writer_control_sha256')
    _require(boot['schema'] == 'twin.xpdf-discovery-parent-bootstrap/v1', 'parent bootstrap discriminator')
    _absolute(boot['interpreter'])
    for key in ('startup_provenance_sha256', 'writer_control_sha256'):
        _pin(boot[key])
    _require(type(boot['roots']) is list and bool(boot['roots']) and boot['roots'] == sorted(set(boot['roots'])), 'selected bootstrap roots')
    for path in boot['roots'] + boot['loaded_files']:
        _absolute(path)
    _require(type(boot['loaded_files']) is list and boot['loaded_files'] == sorted(set(boot['loaded_files']))
             and type(boot['files']) is dict and set(boot['files']) == set(boot['loaded_files']) | {boot['interpreter']}, 'independently selected loaded candidates')
    for pin in boot['files'].values():
        _pin(pin)
    acceptance = value['query_acceptance']
    _closed(acceptance, 'selectors review_sha256 writer_control_sha256')
    _pin(acceptance['review_sha256'])
    _pin(acceptance['writer_control_sha256'])
    _require(type(acceptance['selectors']) is dict and set(acceptance['selectors']) == set(_load(_contract('QUERY-PROFILE.json'))['selectors']), 'independent trusted fixed-query acceptance')
    _closed(value['capacity'], 'review_sha256 minimum_free_bytes')
    _pin(value['capacity']['review_sha256'])
    _integer(value['capacity']['minimum_free_bytes'], 1, 2**63 - 1)
    return value


def _loaded_candidates(roots: list[str]) -> list[str]:
    # Already-loaded __file__ candidates only. No import, cache crawl or completeness inference.
    result = set()
    for loaded in tuple(sys.modules.values()):
        path = getattr(loaded, '__file__', None)
        if type(path) is str and path.startswith('/') and any(PurePosixPath(path).is_relative_to(root) for root in roots):
            _absolute(path)
            result.add(path)
    return sorted(result)


def _source_guard(collection: _Collection, appointed: dict[str, Any], retain: bool) -> None:
    for index, (path, expected) in enumerate(sorted(appointed['source_files'].items())):
        raw, _, _ = collection.read(path, MAX_METADATA, False)
        _require(_sha(raw) == expected, 'selected source/helper/workflow file changed')
        if retain:
            collection.add(f'source/{index:03}.bin', raw, 'source')
    for name in _PINS:
        _contract(name)
    for name in _build._CONTRACT_PINS:
        _build._contract(name)


def _bootstrap(collection: _Collection, appointed: dict[str, Any]) -> None:
    selected = appointed['bootstrap_selection']
    _require(tuple(sys.version_info[:2]) == (3, 12) and sys.flags.isolated == 1 and sys.flags.no_site == 1 and sys.dont_write_bytecode is True
             and sys.executable == selected['interpreter'], 'independently selected isolated Python3.12 startup unestablished')
    uname = os.uname()
    _require(uname.sysname == 'Linux' and uname.machine == 'x86_64', 'actual selected Linux row unestablished')
    _require(_loaded_candidates(selected['roots']) == selected['loaded_files'], 'already-loaded bootstrap candidates differ from independent selection')
    interpreter = collection.snapshot(sys.executable, 'bootstrap', selected['roots'])
    _require(interpreter['sha256'] == selected['files'][sys.executable], 'selected interpreter bytes changed')
    loaded = []
    for path in selected['loaded_files']:
        observed = collection.snapshot(path, 'bootstrap', selected['roots'])
        _require(observed['sha256'] == selected['files'][path], 'selected loaded candidate changed')
        loaded.append(observed)
    raw = _json(dict(schema='twin.xpdf-linux-bootstrap-inventory/v1', selected_bootstrap_sha256=_sha(_json(selected)), interpreter=interpreter, loaded_files=loaded))
    collection.add('BOOTSTRAP.json', raw, 'metadata')
    collection.result['bootstrap'] = _sha(raw)
    collection.add('ENTRY-OBSERVATION.json', _json(dict(system=uname.sysname, machine=uname.machine, python_version=list(sys.version_info[:3]),
        isolated=True, no_site=True, dont_write_bytecode=True, entered=collection.result['entered'])), 'metadata')


def _modules(collection: _Collection, root: str) -> None:
    # An empty tree still traverses this fixed chain; no file snapshot may supply it.
    for parent in reversed(PurePosixPath(root).parents):
        collection.directory(str(parent))
    def visit(path: str) -> None:
        for name in collection.directory(path):
            current = posixpath.join(path, name)
            info = os.lstat(current)
            if stat.S_ISDIR(info.st_mode):
                visit(current)
            else:
                _require(stat.S_ISREG(info.st_mode), 'symlink or special entry in fixed module tree')
                collection.result['modules'].append(collection.snapshot(current, 'cmake-module', [root]))
    visit(root)
    collection.result['modules'].sort(key=lambda candidate: candidate['path'])


def _observed_query(index: int, command: dict[str, Any], environment: dict[str, str]) -> dict[str, Any]:
    _require(command['id'] == f'bootstrap-input-tools/{index:03}' and command['phase'] == 'bootstrap-input-tools', 'supervisor original command identity')
    record = dict(index=index, argv=list(command['argv']), environment=dict(environment), command_binding_sha256=command['custody']['command_binding_sha256'],
        started=command['started'], deadline=command['deadline'], finished=command['ended'], custody=command['custody'],
        raw_wait_status=command['custody']['raw_wait'], returncode=None)
    custody = command['custody']
    if custody['wait_kind'] == 'EXITED': record['returncode'] = custody['exit_code']
    elif custody['wait_kind'] == 'SIGNALED': record['returncode'] = -custody['signal']
    for stream in ('stdout', 'stderr'):
        original = command[stream]
        record[stream] = None if original['sha256'] is None else dict(sha256=original['sha256'], bytes=original['retained_bytes'],
            complete=original['state'] == 'COMPLETE', observed_bytes_lower_bound=original['observed_bytes_lower_bound'])
    return record


def _collect(collection: _Collection, selection: dict[str, Any], appointed: dict[str, Any]) -> None:
    result = collection.result
    environment = _build._fresh_environment(collection.root)
    collection.add('SELECTION.json', _json(selection), 'metadata')
    collection.add('ENVIRONMENT.json', _build._json(environment), 'metadata')
    collection.add('PARENT.json', _json(appointed), 'metadata')
    collection.add('BOOTSTRAP-SELECTION.json', _json(appointed['bootstrap_selection']), 'metadata')
    usage = os.statvfs(collection.root)
    observed_free = usage.f_bavail * usage.f_frsize
    _require(observed_free >= appointed['capacity']['minimum_free_bytes'], 'actual selected capacity changed')
    collection.add('CAPACITY.json', _json(dict(selection=appointed['capacity'], observed_free_bytes=observed_free, live_disk_quota_enforced=False)), 'metadata')
    _source_guard(collection, appointed, True)
    _bootstrap(collection, appointed)
    profile = _load(_contract('QUERY-PROFILE.json'))
    for path in profile['selectors']:
        observed = collection.snapshot(path, 'selector')
        _require(observed == appointed['query_acceptance']['selectors'][path], 'independently accepted query selector changed')
        result['tools'].append(observed)
    context = dict(selection_sha256=result['selection_sha256'], clock=dict(started=result['original_started'], deadline=result['deadline']),
                   commands=[], environment_manifest_sha256=_sha(_build._json(environment)))
    for index, argv in enumerate(profile['ordered_query_argv']):
        started = collection.tick()
        _require(started + 5 + 10 <= result['deadline'], 'original query allowance and terminal reserve unavailable')
        collection.room(32 * MAX_METADATA, 2)
        try:
            _build._supervise(context, 'bootstrap-input-tools', list(argv), collection.root, environment, 5, collection.payload, terminal_reserve=10)
        finally:
            if len(context['commands']) > index:
                result['commands'].append(_observed_query(index, context['commands'][index], environment))
        collection.room()
        collection.tick()
        query = result['commands'][-1]
        streams = [collection.payload[f'journal/{index:03}-{stream}.log'][0] for stream in ('stdout', 'stderr')]
        try:
            _require(_query(query, index, result, {'ENVIRONMENT.json': collection.payload['ENVIRONMENT.json'][0]}, {_sha(raw): raw for raw in streams}), 'fixed query observation is unsupported or unestablished')
        except (ValueError, UnicodeError) as error:
            raise DiscoveryHold('query', 'fixed-query-observation', str(error)) from error
        collection.tick()
        output = collection.payload[f'journal/{index:03}-stdout.log'][0]
        if index == 0:
            result['module_root'] = _cmake_root(output)
            _modules(collection, result['module_root'])
        elif index < 10:
            _gnu_version(index, output)
        elif index == 10:
            _require(re.fullmatch(rb'x86_64-(?:[A-Za-z0-9_]+-)?linux(?:-[A-Za-z0-9_]+)*\n?', output) is not None, 'unsupported compiler target DATA')
        elif index == 11:
            _require(bool(output), 'unobserved GCC specs DATA')
        else:
            path = _internal_path(output, ['cc1', 'cc1plus', 'collect2'][index - 12])
            if result['gcc_internals']:
                _require(PurePosixPath(path).parent == PurePosixPath(result['gcc_internals'][0]['path']).parent, 'one canonical GCC internal parent')
            result['gcc_internals'].append(collection.snapshot(path, 'gcc-internal', [str(PurePosixPath(path).parent)]))
    _require(_loaded_candidates(appointed['bootstrap_selection']['roots']) == appointed['bootstrap_selection']['loaded_files'], 'bootstrap candidate set changed during discovery')
    collection.seal_directories()
    _source_guard(collection, appointed, False)
    result['inventory_state'] = 'COMPLETE_DATA'
    result['custody'] = dict(known_terminal=True, workspace_preserved=True, reason='complete candidate DATA only; no build permission')


def _write(root: Path, relative: str, raw: bytes, tick: Any = None) -> None:
    _require(_build._safe_name(relative), 'safe owned output path')
    parent = _directory_fd(str(root))
    primary = None
    try:
        parts = relative.split('/')
        for part in parts[:-1]:
            try: os.mkdir(part, 0o700, dir_fd=parent)
            except FileExistsError: pass
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            old_parent, parent = parent, next_fd
            _close_files([old_parent], None, 'export')
        fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        write_error = None
        try:
            for offset in range(0, len(raw), 65536):
                if tick is not None: tick()
                block = memoryview(raw)[offset:offset + 65536]
                while block:
                    count = os.write(fd, block)
                    _require(count > 0, 'output writer made no progress')
                    block = block[count:]
                if tick is not None: tick()
        except BaseException as error:
            write_error = error
            raise
        finally:
            _close_files([fd], write_error, 'export')
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        readback_error = None
        try:
            before, observed = _vector(os.fstat(fd)), bytearray()
            while True:
                if tick is not None: tick()
                value = os.read(fd, 65536)
                observed.extend(value)
                if tick is not None: tick()
                if not value: break
                _require(len(observed) <= len(raw), 'output readback grew')
            _require(bytes(observed) == raw and before == _vector(os.fstat(fd)), 'stable exact owned output readback')
            os.fchmod(fd, 0o444)
        except BaseException as error:
            readback_error = error
            raise
        finally:
            _close_files([fd], readback_error, 'export')
    except BaseException as error:
        primary = error
        raise
    finally:
        _close_files([parent], primary, 'export')


def _export(collection: _Collection) -> None:
    result = collection.result
    entries = [dict(path=name, sha256=_sha(raw), bytes=len(raw), role=role) for name, (raw, role) in sorted(collection.payload.items())]
    files = _json(dict(schema='twin.xpdf-linux-discovery-files/v1', entries=entries))
    _require(len(files) <= MAX_METADATA, 'files metadata cap')
    for name, (raw, _) in collection.payload.items():
        _write(collection.root / 'export', name, raw, collection.tick)
    _write(collection.root / 'export', 'FILES.json', files, collection.tick)
    result['files_manifest_sha256'] = _sha(files)
    result['finished'] = collection.tick()
    terminal = _json(result)
    _require(len(terminal) <= MAX_METADATA, 'result metadata cap')
    bundle = {name: value[0] for name, value in collection.payload.items()}
    bundle.update({'FILES.json': files, 'RESULT.json': terminal})
    check_discovery_bundle(bundle, result['selection_sha256'])
    _write(collection.root / 'export', 'RESULT.json', terminal, collection.tick)
    collection.tick()


def _retain_failure(collection: _Collection) -> None:
    # A finite diagnostic prefix, never a renewed normal export or a deleted workspace.
    try:
        limit = 15 * MAX_METADATA
        retained: dict[str, bytes] = {}
        for index, (name, (raw, role)) in enumerate(sorted(collection.payload.items(), reverse=True)):
            if role not in ('raw-log', 'failure-prefix'):
                continue
            prefix = raw[:limit]
            _write(collection.root, f'journal/failure-{index:05}.bin', prefix)
            limit -= len(prefix)
            retained[name] = prefix
        for query in collection.result['commands']:
            for stream in ('stdout', 'stderr'):
                name = f'journal/{query["index"]:03}-{stream}.log'
                if name in retained and query[stream] is not None:
                    prefix = retained[name]
                    record = query[stream]
                    if len(prefix) != record['bytes']:
                        record['complete'] = False
                    record.update(sha256=_sha(prefix), bytes=len(prefix))
        collection.result['files_manifest_sha256'] = None
        raw = _json(collection.result)
        if len(raw) <= MAX_METADATA:
            _write(collection.root, 'FIRST-FAILURE.json', raw)
    except BaseException:
        pass


def _partial_export_safe(collection: _Collection, at: float | None) -> bool:
    if at is None or collection.result['entered'] is None or at > collection.result['deadline']:
        return False
    for query in collection.result['commands']:
        custody = query['custody']
        if query['started'] is None:
            return False
        if custody['reservation'] == 'NO_CHILD_CREATED' and custody['leader_pid'] is None and not custody['observations']:
            continue
        context, command = _projection(collection.result, query)
        try:
            if not _build._check_custody(context, command):
                return False
        except ValueError:
            return False
    return True


def discover_linux_tools(selection: Mapping[str, Any], owned_parent: Path) -> dict[str, Any]:
    result = _new_result(selection)
    if _DISCOVERY_APPOINTMENT is None:
        _fault(result, 'appointment', 'source-appointment', DiscoveryHold('appointment', 'source-appointment', 'independent discovery source appointment absent'), None)
        return result
    collection = None
    original: BaseException | None = None
    stage = 'appointment'
    try:
        appointed = _appointment(dict(selection), owned_parent)
        result.update(original_started=appointed['original_started'], deadline=appointed['deadline'], run_identity=appointed['run_identity'])
        collection = _Collection(result, owned_parent)
        result['entered'] = collection.tick()
        stage = 'setup'
        _source_guard(collection, appointed, False)
        usage = os.statvfs(owned_parent.parent)
        _require(usage.f_bavail * usage.f_frsize >= appointed['capacity']['minimum_free_bytes'], 'independently selected capacity unestablished')
        parent = _directory_fd(str(owned_parent.parent))
        setup_error = None
        try:
            os.mkdir(owned_parent.name, 0o700, dir_fd=parent)
        except BaseException as error:
            setup_error = error
            raise
        finally:
            _close_files([parent], setup_error, 'setup')
        result['inventory_state'] = 'PARTIAL_DATA'
        for name in ('home', 'tmp', 'journal', 'export'):
            os.mkdir(str(owned_parent / name), 0o700)
        stage = 'snapshot'
        _collect(collection, dict(selection), appointed)
        stage = 'export'
        _export(collection)
    except BaseException as error:
        original = error
        at = None
        try:
            at = time.monotonic()  # Preserve actual late observation; never clamp or restamp.
            _number(at, False)
        except BaseException:
            at = None
        fault_at = error.observed_at if isinstance(error, DiscoveryHold) and error.observed_at is not None else at
        _fault(result, error.stage if isinstance(error, DiscoveryHold) else stage, error.operation if isinstance(error, DiscoveryHold) else 'discovery', error, fault_at)
        result['finished'] = at
        if collection is not None and result['inventory_state'] != 'NOT_STARTED':
            try:
                (owned_parent / 'export/RESULT.json').rename(owned_parent / 'export/RESULT-INCOMPLETE.json')
            except BaseException:
                pass
            exported = False
            if stage != 'export' and _partial_export_safe(collection, at):
                try:
                    collection.room()
                    _export(collection)  # Same original clock; terminal held DATA, no new query/read/acquisition.
                    exported = True
                except BaseException as secondary:
                    secondary_at = None
                    try:
                        secondary_at = time.monotonic()
                        _number(secondary_at, False)
                    except BaseException:
                        secondary_at = None
                    _fault(result, 'export', 'partial-export', secondary, secondary_at)
                    result['finished'] = secondary_at
                    try:
                        (owned_parent / 'export/RESULT.json').rename(owned_parent / 'export/RESULT-INCOMPLETE.json')
                    except BaseException:
                        pass
            if not exported:
                _retain_failure(collection)
    if original is not None and not isinstance(original, Exception):
        raise original
    return result
