"""Truthful retained legacy mapping and bounded new deterministic extraction.

No public dictionary is acquisition authority. Actual use additionally needs independently
reviewed complete tool/platform closure and observed-run pins. TEST_ONLY process-file
closure deliberately does not establish macOS/dyld or actual-purpose readiness.
"""
from __future__ import annotations

import copy
import importlib
import json
import os
import datetime
import selectors
import signal
import subprocess
import tempfile
import time
from pathlib import Path
import sys
import types
from typing import Any

from . import source_metadata as sm
from . import pdf_output_origin
from . import pdf_native_bridge

MIGRATION_CONTRACT_VERSION = 'source-metadata-migration/v1'
COMMON = {'at_utc':'string','bytes':'integer','derived_text':'object','final_url':'string',
          'headers':'object','id':'string','path':'string','sha256':'string','status':'integer','url':'string'}
# Type specifications use immutable names in guarded JSON configuration, not callables.
OPTION_TYPES = {'derived_text_alternate':'object','error':'null','extractor':'object',
    'ext':'string','family':'string','initial_derived_text':'object','kind':'string',
    'method':'string','slot':'integer','text_extraction':'object','timeout_seconds':'integer',
    'routing_reason':'string','transform':'object'}
VARIANTS = (
    ('derived_text_alternate','error','extractor'), ('error','extractor'), ('error',),
    ('ext','family','initial_derived_text','kind','method','slot','text_extraction','timeout_seconds'),
    ('ext','family','kind','method','slot','timeout_seconds'),
    ('family','kind','method','slot','timeout_seconds'),
    ('kind','method','routing_reason','timeout_seconds','transform'),
    ('kind','method','routing_reason','timeout_seconds'))
NESTED = {
    'derived_text': ({'bytes':'integer','path':'string','sha256':'string'},
        {'bytes':'integer','path':'string','sha256':'string','method':'string'},
        {'bytes':'integer','path':'string','sha256':'string','command':'string','encoding':'string','exit':'integer'}),
    'derived_text_alternate': ({'bytes':'integer','extractor':'string','path':'string','sha256':'string'},),
    'initial_derived_text': ({'bytes':'integer','path':'string','sha256':'string'},),
    'extractor': ({'command':'string','exit_code':'integer','stderr':'string'},),
    'text_extraction': ({'exit':'integer','stderr':'string'},),
    'transform': ({'command':'string','exit':'integer'},)}


class MetadataMigrationHold(ValueError):
    """An evidence/contract hold, never successful acquisition."""


def _closed(value: Any, keys: set[str]) -> None:
    if type(value) is not dict or set(value) != keys:
        raise MetadataMigrationHold('closed migration shape differs')


def _hash(value: Any) -> None:
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise MetadataMigrationHold('invalid migration hash')


def _typed(value: Any, name: str) -> bool:
    return type(value) is {'string':str,'integer':int,'object':dict,'null':type(None)}[name]


def _legacy_entry(entry: Any) -> None:
    if type(entry) is not dict or not set(COMMON) <= set(entry):
        raise MetadataMigrationHold('legacy required core differs')
    if any(not _typed(entry[k], t) for k,t in COMMON.items()):
        raise MetadataMigrationHold('legacy core type differs')
    extra = set(entry) - set(COMMON)
    if sum(extra == set(keys) for keys in VARIANTS) != 1:
        raise MetadataMigrationHold('unsupported legacy structural variant')
    if any(not _typed(entry[k], OPTION_TYPES[k]) for k in extra):
        raise MetadataMigrationHold('legacy optional type differs')
    if any(type(k) is not str or type(v) is not str for k,v in entry['headers'].items()):
        raise MetadataMigrationHold('legacy header types differ')
    for key, variants in NESTED.items():
        if key in entry:
            obj = entry[key]
            if not any(type(obj) is dict and set(obj) == set(rule)
                       and all(_typed(obj[k], t) for k,t in rule.items()) for rule in variants):
                raise MetadataMigrationHold('legacy nested type/shape differs')


def _layout(config: Any, purpose: str) -> None:
    _closed(config, {'schema','purpose','transport_contract_sha256'})
    if config['schema'] != 'twin.source-legacy-layout/v1' or config['purpose'] != purpose:
        raise MetadataMigrationHold('legacy layout purpose/schema differs')
    if config['transport_contract_sha256'] is not None:
        _hash(config['transport_contract_sha256'])


def describe_legacy_adaptation(acquisition: dict, layout_config: dict) -> bytes:
    """New representation record only: never a historical capture receipt."""
    return sm.canonical({'schema':'twin.source-legacy-adaptation/v1',
        'claim':'new-representation-of-retained-capture-evidence',
        'layout':layout_config, 'acquisition':acquisition})


def retained_legacy_receipt_adapter(acquisition: dict, artifacts: dict[str, bytes], policy: dict,
                                    *, layout_config: dict | None = None) -> None:
    if layout_config is None:
        raise MetadataMigrationHold('unbound legacy layout')
    _layout(layout_config, policy['purpose'])
    # The stock path remains exact. No catch-and-fallback after a standardized failure.
    entry = sm._json(sm._artifact(artifacts, acquisition['receipt_artifact_sha256']))
    standard = {k:v for k,v in acquisition.items() if k not in ('receipt_artifact_sha256','receipt_entry_pointer')}
    pointer = acquisition['receipt_entry_pointer']
    token = pointer[1:] if type(pointer) is str and pointer.startswith('/') else ''
    if (type(entry) is not list or not token.isascii() or not token.isdecimal()
            or token != str(int(token)) or int(token) >= len(entry)):
        # Other standardized containers/pointers are the unchanged stock adapter's
        # responsibility. It must succeed itself; no error is caught as a fallback.
        sm.retained_receipt_adapter(acquisition, artifacts, policy)
        return
    entry = entry[int(token)]
    if type(entry) is dict and set(entry) == set(standard):
        sm.retained_receipt_adapter(acquisition, artifacts, policy)
        return
    _legacy_entry(entry)
    pin = layout_config['transport_contract_sha256']
    if pin is None or 'kind' not in entry or 'method' not in entry:
        raise MetadataMigrationHold('unmappable-transport')
    transport = sm._json(sm._artifact(artifacts, pin))
    _closed(transport, {'schema','purpose','legacy_kind','legacy_method','acquisition_kind'})
    if (transport['schema'] != 'twin.source-legacy-transport-contract/v1'
            or transport['purpose'] != policy['purpose']
            or any(type(transport[k]) is not str or not transport[k] for k in ('legacy_kind','legacy_method'))
            or entry['kind'] != transport['legacy_kind'] or entry['method'] != transport['legacy_method']
            or transport['acquisition_kind'] != ('TEST_ONLY-fixture' if policy['purpose'] == 'TEST_ONLY' else 'retained-http')):
        raise MetadataMigrationHold('unmappable-transport')
    expected = {'id':entry['id'],'kind':transport['acquisition_kind'],'requested_url':entry['url'],
        'final_url':entry['final_url'],'response_status':entry['status'],'captured_at':entry['at_utc'],
        'body_bytes':entry['bytes'],'body_sha256':entry['sha256']}
    if standard != expected or type(acquisition['response_status']) is not int or type(acquisition['body_bytes']) is not int:
        raise MetadataMigrationHold('legacy mapped acquisition differs')
    if (not all(type(expected[k]) is str and expected[k] for k in ('id','requested_url','final_url'))
            or not 200 <= expected['response_status'] < 300 or expected['body_bytes'] < 0):
        raise MetadataMigrationHold('legacy capture facts invalid')
    _hash(expected['body_sha256'])
    sm._instant(expected['captured_at'])
    adaptation = describe_legacy_adaptation(acquisition, layout_config)
    if sm._artifact(artifacts, sm.sha256(adaptation)) != adaptation:
        raise MetadataMigrationHold('missing retained new adaptation record')

MIB = 1048576
PROFILES = {
    'utf8-identity/1': {'input_bytes':64*MIB,'stdout_bytes':64*MIB,'stderr_bytes':MIB,
        'syntax_bytes':64*MIB,'wall_seconds':10,'termination_grace_seconds':2},
    'html-text-utf8/1': {'input_bytes':64*MIB,'stdout_bytes':128*MIB,'stderr_bytes':MIB,
        'syntax_bytes':64*MIB,'wall_seconds':30,'termination_grace_seconds':2},
    'pdf-text-xpdf/1': {'input_bytes':256*MIB,'stdout_bytes':128*MIB,'stderr_bytes':4*MIB,
        'syntax_bytes':64*MIB,'wall_seconds':120,'termination_grace_seconds':2}}
PROFILES['pdf-text-xpdf-origin/2'] = dict(PROFILES['pdf-text-xpdf/1'])
CHILD = str(Path(__file__).with_name('_source_metadata_extract_child.py').resolve())
ENVIRONMENT = {'LC_ALL':'C','LANG':'C','TZ':'UTC'}


def _put(collection: dict[str, bytes], raw: bytes) -> str:
    pin = sm.sha256(raw)
    collection[pin] = raw
    return pin


def _json_artifact(collection: dict[str, bytes], value: Any) -> str:
    return _put(collection, sm.canonical(value))


def _instant_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _finish_owned_group(process, waitid, grace: float, group: dict, custody: dict) -> str | None:
    """One local cleanup continuation, sharing its original deadline and solewait state."""
    if custody['reaping_started']:
        return 'direct-child-reap-unverified'
    if not custody['reservation_checked']:
        try:
            waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        except OSError:
            group['reservation'] = 'unverified-direct-child'
            return 'direct-child-reservation-unverified'
        custody['reservation_checked'] = True
    deadline = custody['deadline']
    signals = (signal.SIGTERM, signal.SIGKILL)
    while custody['next_signal'] < len(signals) and not custody['absent']:
        sig = signals[custody['next_signal']]
        # Advance before invocation: an interruption may occur after the signal acted.
        custody['next_signal'] += 1
        try:
            os.killpg(process.pid, sig)
            outcome = 'sent'
        except ProcessLookupError:
            outcome, custody['absent'] = 'absent', True
        except PermissionError:
            outcome = 'permission-denied'
        except OSError:
            outcome = 'os-error'
        except BaseException:
            group['signals'].append({'signal':int(sig),'outcome':'interrupted'})
            raise
        group['signals'].append({'signal':int(sig),'outcome':outcome})
        if sig == signal.SIGTERM and outcome == 'sent':
            term_deadline = deadline - min(.05, grace / 4)
            while time.monotonic() < term_deadline:
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    custody['absent'] = True
                    break
                except OSError:
                    break
                time.sleep(min(.01, max(0, term_deadline-time.monotonic())))
    # Set BEFORE wait: cancellation may occur after the OS reaped but before return.
    # No continuation may signal or start another wait after this transition.
    custody['reaping_started'] = True
    try:
        process.wait(timeout=max(0, deadline-time.monotonic()))
        group['direct_child_reaped'] = True
    except (subprocess.TimeoutExpired, OSError):
        return 'direct-child-reap-unverified'
    while True:
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            group['absence_verified'] = True
            return None
        except PermissionError:
            pass
        except OSError:
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(min(.005, max(0, deadline-time.monotonic())))
    return 'owned-group-unverified'


def _run(argv: list[str], cwd: str, limits: dict) -> dict:
    """Bounded own session; reserve its leader PID until the last group signal.

    waitid(WNOWAIT) observes exit without releasing the PGID reservation. Only the
    direct child is reaped here; absence of the remaining group is a separate fact.
    """
    start, monotonic_start = _instant_now(), time.monotonic()
    deadline = monotonic_start + limits['wall_seconds']
    # Cleanup shares the profile wall budget, including TERM grace, KILL and reap.
    grace = min(limits['termination_grace_seconds'], limits['wall_seconds'])
    execution_deadline = deadline - grace
    streams = {'stdout':bytearray(),'stderr':bytearray()}
    observed = {'stdout':0,'stderr':0}
    failure = None
    interruption: BaseException | None = None
    custody: dict[str, Any] = {}
    process = None
    group: dict[str, Any] = {'leader_pid':None,'reservation':'unreaped-direct-child',
        'signals':[], 'direct_child_reaped':False,'absence_verified':False}
    waitid: Any = getattr(os, 'waitid', None)
    with selectors.DefaultSelector() as selector:
        try:
            if not callable(waitid) or not all(hasattr(os, name) for name in ('waitid','P_PID','WEXITED','WNOHANG','WNOWAIT')):
                raise OSError('non-reaping child observation unsupported')
            process = subprocess.Popen(argv, cwd=cwd, env=dict(ENVIRONMENT), stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            group['leader_pid'] = process.pid
            for name in streams:
                pipe = getattr(process, name)
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            while True:
                remaining = execution_deadline - time.monotonic()
                if remaining <= 0:
                    failure = 'timeout'
                    break
                for key, _ in selector.select(min(.05, remaining)):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        getattr(process,key.data).close()
                        continue
                    name = key.data
                    observed[name] += len(chunk)
                    capacity = limits[name + '_bytes'] - len(streams[name])
                    streams[name].extend(chunk[:max(0, capacity)])
                    if observed[name] > limits[name + '_bytes']:
                        failure = name + '-overflow'
                        break
                if failure:
                    break
                if not selector.get_map():
                    status = waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
                    if status is not None:
                        break
                    time.sleep(min(.005, max(0, execution_deadline-time.monotonic())))
        except OSError as exc:
            failure = 'os-error:' + type(exc).__name__
        except BaseException as exc:
            interruption = exc
        finally:
            try:
                if process is not None:
                    custody = {'deadline':min(deadline,time.monotonic()+grace),
                        'reaping_started':False,'reservation_checked':False,'next_signal':0,'absent':False}
                    # At most one continuation, never a renewed grace or second wait.
                    for attempt in range(2):
                        try:
                            cleanup_failure = _finish_owned_group(process,waitid,grace,group,custody)
                            failure = cleanup_failure or failure
                        except BaseException as exc:
                            if interruption is None:
                                interruption = exc
                            if custody['reaping_started']:
                                break
                        else:
                            break
                    for name in streams:
                        pipe = getattr(process, name)
                        if pipe is not None:
                            try:
                                pipe.close()
                            except BaseException as exc:
                                if interruption is None:
                                    interruption = exc
            except BaseException as exc:
                # Deadline acquisition is cleanup too; never replace saved cancellation.
                if interruption is None:
                    interruption = exc
    if interruption is not None:
        # A missing return cannot convey custody to the caller. Retain bounded stream
        # prefixes and facts in the already owned workspace, then propagate the original.
        try:
            observation = {'schema':'twin.source-interrupted-execution/v1',
                'disposition':'interrupted','success':False,
                'cancellation_type':type(interruption).__name__,'process_group':group,
                'cleanup_custody':custody,'started_at':start,'ended_at':_instant_now(),
                'observed_bytes_lower_bound':observed,
                'stdout':{'bytes':len(streams['stdout']),'sha256':sm.sha256(bytes(streams['stdout']))},
                'stderr':{'bytes':len(streams['stderr']),'sha256':sm.sha256(bytes(streams['stderr']))}}
            _write_owned(Path(cwd)/'interrupted-stdout.bin',bytes(streams['stdout']))
            _write_owned(Path(cwd)/'interrupted-stderr.bin',bytes(streams['stderr']))
            _write_owned(Path(cwd)/'interrupted-execution.json',sm.canonical(observation))
        except BaseException:
            # Interrupted/failed evidence IO cannot justify workspace removal or success.
            pass
        raise interruption
    return {'started_at':start,'ended_at':_instant_now(),
        'elapsed_seconds':time.monotonic()-monotonic_start,
        'exit_code':process.returncode if process is not None else None,
        'stdout':bytes(streams['stdout']),'stderr':bytes(streams['stderr']),
        'observed_bytes_lower_bound':observed, 'streams_complete':failure is None,
        'process_group':group,'failure':failure}


def _cleanup_workspace(directory, run: dict | None, *, run_started: bool = False) -> str:
    """Never remove a workspace while an owned group might still use it."""
    if run is not None and 'native_observation' in run:
        from . import source_native_observation as native
        try: native.validate_native_custody(run['process_group'])
        except (ValueError,KeyError,TypeError):
            getattr(directory, '_finalizer').detach()
            return 'preserved-unverified-group'
    if (run is None and run_started or run is not None
            and not (run['process_group']['direct_child_reaped']
                     and run['process_group']['absence_verified'])):
        getattr(directory, '_finalizer').detach()
        return 'preserved-unverified-group'
    try:
        directory.cleanup()
    except OSError:
        return 'failed'
    return 'removed'


def _command(executable: str, workdir: str, *, inventory: bool = False) -> list[str]:
    prefix = [executable,'-I','-S','-B','-X','pycache_prefix=' + str(Path(workdir)/'pycache'),CHILD]
    if inventory:
        return prefix + ['--inventory']
    return prefix + ['--run', str(Path(workdir)/'input'),str(Path(workdir)/'config'),
                     str(Path(workdir)/'syntax'),str(Path(workdir)/'runtime')]


def prepare_extraction_plan(profile: str, parent: bytes, *, purpose: str,
                            predecessor_sha256: str, member_id: str,
                            test_only_behavior: str = 'normal') -> dict:
    """Retain an actual TEST_ONLY preflight closure before running source bytes.

    No actual-purpose platform closure is commissioned by this constructor. Complete
    actual closure can only come from separate independent custody, not this fixture.
    """
    if profile not in PROFILES:
        raise MetadataMigrationHold('unsupported extraction profile')
    if purpose != 'TEST_ONLY':
        raise MetadataMigrationHold('complete approved actual platform closure unestablished')
    if profile in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2'):
        raise MetadataMigrationHold('real PDF native closure/execution unproved')
    if type(parent) is not bytes or len(parent) > PROFILES[profile]['input_bytes']:
        raise MetadataMigrationHold('input-limit/type')
    _hash(predecessor_sha256)
    if type(member_id) is not str or not member_id or test_only_behavior not in ('normal','diagnostic','nonzero'):
        raise MetadataMigrationHold('invalid extraction member/fixture behavior')
    executable = str(Path(sys.executable).resolve())
    directory = tempfile.TemporaryDirectory(prefix='source-metadata-preflight-')
    result = None
    run_started = False
    try:
        getattr(directory, '_finalizer').detach()
        run_started = True
        result = _run(_command(executable, directory.name, inventory=True), directory.name,
            {'wall_seconds':10,'stdout_bytes':MIB,'stderr_bytes':MIB,'termination_grace_seconds':2})
    finally:
        workspace_cleanup = _cleanup_workspace(directory, result, run_started=run_started)
    if workspace_cleanup != 'removed':
        raise MetadataMigrationHold('preflight workspace ' + workspace_cleanup + ': ' + directory.name)
    if result['failure'] or result['exit_code'] != 0:
        raise MetadataMigrationHold('process-file preflight failed')
    observation = sm._json(result['stdout'])
    if observation['schema'] != 'twin.source-extraction-process-files/v1' or observation['executable'] != executable:
        raise MetadataMigrationHold('preflight interpreter differs')
    archive: dict[str,bytes] = {}
    for row in observation['files']:
        raw = Path(row['path']).read_bytes()
        if sm.sha256(raw) != row['sha256'] or len(raw) != row['bytes']:
            raise MetadataMigrationHold('preflight resource changed')
        _put(archive, raw)
    driver_files = []
    for path in (Path(__file__), Path(sm.__file__), sm.SCHEMA_PATH):
        raw = path.read_bytes()
        driver_files.append({'path':str(path.resolve()),'sha256':_put(archive,raw),'bytes':len(raw)})
    driver_inventory, _ = sm._runtime_helper_inventory((sys.modules[__name__],))
    closure = {'schema':'twin.source-extraction-closure/v1','scope':'TEST_ONLY-process-file-closure/v1',
        'purpose':purpose,'platform_closure':'UNESTABLISHED','process_files':observation,
        'platform_files':[],'driver_files':driver_files,'driver_inventory':driver_inventory}
    implementation_pin = _json_artifact(archive, closure)
    config = {'schema':'twin.source-extraction-config/v1','profile':profile,'purpose':purpose,
        'limits':copy.deepcopy(PROFILES[profile]),'environment':dict(ENVIRONMENT),
        'diagnostic_policy':'accept-bounded-on-zero','test_only_behavior':test_only_behavior,
        'native_config_sha256':None}
    configuration_pin = _json_artifact(archive, config)
    return {'schema':'twin.source-extraction-plan/v1','purpose':purpose,'profile':profile,
        'parent_sha256':sm.sha256(parent),'parent_bytes':len(parent),'member_id':member_id,
        'predecessor_sha256':predecessor_sha256,'implementation_artifact_sha256':implementation_pin,
        'configuration_sha256':configuration_pin,'archive':archive}


def _validate_plan(plan: Any, parent: bytes) -> tuple[dict, dict]:
    _closed(plan, {'schema','purpose','profile','parent_sha256','parent_bytes','member_id',
        'predecessor_sha256','implementation_artifact_sha256','configuration_sha256','archive'})
    if (plan['schema'] != 'twin.source-extraction-plan/v1' or plan['profile'] not in PROFILES
            or plan['purpose'] not in ('TEST_ONLY','actual') or type(parent) is not bytes
            or type(plan['parent_bytes']) is not int or len(parent) != plan['parent_bytes']
            or sm.sha256(parent) != plan['parent_sha256']):
        raise MetadataMigrationHold('exact frozen extraction parent/plan differs')
    _hash(plan['predecessor_sha256'])
    if type(plan['member_id']) is not str or not plan['member_id']:
        raise MetadataMigrationHold('missing extraction member id')
    archive = plan['archive']
    if type(archive) is not dict:
        raise MetadataMigrationHold('retained closure archive required')
    for pin in archive:
        sm._artifact(archive, pin)
    config = sm._json(sm._artifact(archive, plan['configuration_sha256']))
    _closed(config, {'schema','profile','purpose','limits','environment','diagnostic_policy','test_only_behavior','native_config_sha256'})
    if (config['schema'] != 'twin.source-extraction-config/v1' or config['profile'] != plan['profile']
            or config['purpose'] != plan['purpose'] or config['limits'] != PROFILES[plan['profile']]
            or config['environment'] != ENVIRONMENT or config['diagnostic_policy'] != 'accept-bounded-on-zero'
            or config['test_only_behavior'] not in ('normal','diagnostic','nonzero')
            or plan['purpose'] == 'actual' and config['test_only_behavior'] != 'normal'):
        raise MetadataMigrationHold('frozen profile configuration differs')
    if len(parent) > config['limits']['input_bytes']:
        raise MetadataMigrationHold('input-limit')
    closure = sm._json(sm._artifact(archive, plan['implementation_artifact_sha256']))
    _closed(closure, {'schema','scope','purpose','platform_closure','process_files','platform_files','driver_files','driver_inventory'})
    if closure['schema'] != 'twin.source-extraction-closure/v1' or closure['purpose'] != plan['purpose']:
        raise MetadataMigrationHold('closure purpose differs')
    if plan['purpose'] == 'actual':
        # No supported actual OS/native dependency observation adapter exists yet.
        # A scope label, caller file list or hash cannot establish completeness.
        raise MetadataMigrationHold('actual native dependency observation/closure unestablished')
    elif closure['scope'] != ('TEST_ONLY-native-converter-fixture/v1' if plan['profile']=='pdf-text-xpdf/1'
                              else 'TEST_ONLY-process-file-closure/v1') or closure['platform_closure'] != 'UNESTABLISHED':
        raise MetadataMigrationHold('TEST_ONLY closure scope differs')
    process_files = closure['process_files']
    native = plan['profile'] == 'pdf-text-xpdf/1'
    _closed(process_files, {'schema','executable','files','version','version_observation_sha256'} if native
            else {'schema','python','executable','files'})
    if process_files['schema'] != ('twin.source-extraction-native-tool-files/v1' if native else 'twin.source-extraction-process-files/v1') or type(process_files['files']) is not list:
        raise MetadataMigrationHold('process closure shape differs')
    inventory, _ = sm._runtime_helper_inventory((sys.modules[__name__],))
    if inventory != closure['driver_inventory']:
        raise MetadataMigrationHold('actual extraction driver helper/dispatch changed')
    seen = set()
    for row in process_files['files'] + closure['platform_files'] + closure['driver_files']:
        _closed(row, {'path','sha256','bytes'})
        if type(row['path']) is not str or row['path'] in seen or type(row['bytes']) is not int:
            raise MetadataMigrationHold('closure file identity differs')
        seen.add(row['path'])
        raw = sm._artifact(archive, row['sha256'])
        if len(raw) != row['bytes'] or Path(row['path']).read_bytes() != raw:
            raise MetadataMigrationHold('actual executable/resource closure changed')
    if not {str(Path(__file__).resolve()),str(Path(sm.__file__).resolve()),str(sm.SCHEMA_PATH.resolve())} <= seen:
        raise MetadataMigrationHold('actual extraction driver source closure missing')
    if native:
        if (process_files['executable'] not in seen or type(process_files['version']) is not str
                or not process_files['version'] or config['test_only_behavior'] != 'normal'):
            raise MetadataMigrationHold('retained native converter identity/version differs')
        sm._artifact(archive,process_files['version_observation_sha256'])
        sm._artifact(archive,config['native_config_sha256'])
    elif (CHILD not in seen or str(Path(sys.executable).resolve()) != process_files['executable']
            or process_files['executable'] not in seen or config['native_config_sha256'] is not None):
        raise MetadataMigrationHold('fixed actual child/interpreter not established')
    return config, closure


def _write_owned(path: Path, raw: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as target:
        target.write(raw)


def execute_new_extraction(plan: dict, parent: bytes, *, observation_store=None) -> dict:
    if type(plan) is dict and plan.get('purpose') == 'actual':
        from . import source_native_observation as native
        try:
            acquired = native.acquire_native_observation(observation_store, plan, parent)
            return native.resolve_native_observation(observation_store, acquired)
        except native.NativeObservationFailure as exc:
            return exc.result
    if type(plan) is dict and plan.get('profile')=='pdf-text-xpdf-origin/2': raise MetadataMigrationHold('no TEST_ONLY profile2 execute/adopt API')
    if observation_store is not None:
        raise MetadataMigrationHold('TEST_ONLY executor cannot adopt an actual observer')
    result=_execute_prepared_extraction(plan,parent)
    if type(result) is not dict: raise MetadataMigrationHold('internal native completion cannot escape TEST_ONLY execute')
    return result


def _observed_command(executable: str, workdir: str) -> list[str]:
    return [executable,'-I','-S','-B','-X','pycache_prefix=' + str(Path(workdir)/'pycache'),
        str(Path(workdir)/'helper.py'),'--run',str(Path(workdir)/'input'),str(Path(workdir)/'config'),
        str(Path(workdir)/'syntax'),str(Path(workdir)/'runtime')]


def _execute_prepared_extraction(plan: dict, parent: bytes, *, observation_store=None) -> dict | tuple[dict,dict]:
    from . import source_native_observation as native_observer
    observed = observation_store is not None
    config, closure = (native_observer.validate_native_candidate_plan(plan,parent) if observed else _validate_plan(plan,parent))
    pdf2 = plan['profile'] == 'pdf-text-xpdf-origin/2'
    native = plan['profile'] in ('pdf-text-xpdf/1','pdf-text-xpdf-origin/2')
    archive = dict(plan['archive'])
    receipts: dict[str,bytes] = {}
    _put(archive, parent)
    run = None
    run_started = False
    ranges, runtime = [], None
    workspace_cleanup = None
    directory = tempfile.TemporaryDirectory(prefix='source-metadata-run-')
    try:
        workdir = directory.name
        os.chmod(workdir, 0o700)
        _write_owned(Path(workdir)/'input', parent)
        _write_owned(Path(workdir)/'config', sm._artifact(archive, plan['configuration_sha256']))
        if (Path(workdir)/'input').read_bytes() != parent:
            raise MetadataMigrationHold('copied raw parent differs')
        if native:
            _write_owned(Path(workdir)/'native-config',sm._artifact(archive,config['native_config_sha256']))
        if observed and not native:
            _write_owned(Path(workdir)/'helper.py', Path(CHILD).read_bytes())
        argv = (_pdf_origin_command(closure['process_files']['executable'],workdir) if pdf2 else _pdf_command(closure['process_files']['executable'],workdir) if native
                else _observed_command(closure['process_files']['executable'],workdir) if observed
                else _command(closure['process_files']['executable'], workdir))
        invocation = {'schema':'twin.source-extraction-invocation/v1','argv':argv,
            'cwd':workdir,'environment':dict(ENVIRONMENT),'stdin':'OWNED-EOF-PIPE' if observed else 'DEVNULL'}
        invocation_pin = _json_artifact(archive, invocation)
        getattr(directory, '_finalizer').detach()
        run_started = True
        run = (native_observer._run_native_extraction(observation_store,plan,parent,argv,workdir) if observed
               else _run(argv, workdir, config['limits']))
        if native and run['failure'] is None and run['exit_code'] == 0:
            runtime = copy.deepcopy(closure['process_files'])
        if not native and run['failure'] is None and run['exit_code'] == 0:
            for name, cap in [('runtime',16*MIB if observed else MIB),('syntax',config['limits']['syntax_bytes'])]:
                path = Path(workdir)/name
                if not path.is_file() or path.is_symlink() or path.stat().st_size > cap:
                    run['failure'] = 'missing/oversized-' + name
                    break
            if run['failure'] is None:
                runtime = sm._json((Path(workdir)/'runtime').read_bytes())
                ranges = [sm._json(line) for line in (Path(workdir)/'syntax').read_bytes().splitlines()]
                expected_runtime = copy.deepcopy(closure['process_files'])
                if observed:
                    for row in expected_runtime['files']:
                        if row['path']==CHILD: row['path']=str(Path(workdir)/'helper.py')
                    expected_runtime['files'].sort(key=lambda row:row['path'])
                if runtime != expected_runtime:
                    run['failure'] = 'observed-process-closure-differs'
        try:
            if observed:
                native_observer.validate_native_candidate_plan(plan,parent)
            else:
                _validate_plan(plan, parent)
        except (ValueError,OSError) as exc:
            run['failure'] = 'post-run-closure:' + type(exc).__name__
    except (ValueError,OSError,KeyError) as exc:
        if run is None:
            raise
        run['failure'] = 'post-run-evidence:' + type(exc).__name__
    finally:
        workspace_cleanup = _cleanup_workspace(directory, run, run_started=run_started)
    if run is None:
        raise MetadataMigrationHold('child was not invoked')
    if workspace_cleanup != 'removed':
        run['failure'] = ('cleanup-failed' if workspace_cleanup == 'failed'
                          else run['failure'] or 'owned-group-unverified')
    if pdf2:
        observation_store._guard.verify()
        try:
            observation,artifacts=native_observer._finalize_pdf_native_run(run,workspace_cleanup)
        except (ValueError,OSError) as exc:
            run['failure']='native-independent-replay:'+type(exc).__name__
            observation=run['native_observation'];artifacts=run['native_artifacts']
        if run['failure'] is not None or observation['schema']!='twin.native-file-observation/v2':
            return pdf_native_bridge._failed_pdf_extraction(plan,parent,run,observation,artifacts,workspace_cleanup),copy.deepcopy(observation)
        try:
            result=pdf_native_bridge._complete_pdf_extraction(plan,parent,observation,artifacts)
        except (ValueError,OSError) as exc:
            run['failure']='pdf-origin-completion:'+type(exc).__name__
            observation_store._guard.verify()
            return pdf_native_bridge._failed_pdf_extraction(plan,parent,run,observation,artifacts,workspace_cleanup),copy.deepcopy(observation)
        observation_store._guard.verify()
        pdf_native_bridge.verify_pdf_extraction_bundle(plan,parent,result)
        return result,copy.deepcopy(observation)
    native_observation_pin = None
    if observed and 'native_observation' in run:
        try:
            native_observation, native_artifacts = native_observer.finalize_native_observation(run,cleanup_failed=workspace_cleanup != 'removed')
            archive.update(native_artifacts)
            native_observation_pin = _json_artifact(archive,native_observation)
        except (ValueError,OSError) as exc:
            run['failure']='native-independent-replay:' + type(exc).__name__
    if run['elapsed_seconds'] > config['limits']['wall_seconds']:
        run['failure'] = 'timeout'
    if observed and native and native_observation_pin is not None:
        runtime = {'schema':'twin.native-observed-runtime/v1','observation_sha256':native_observation_pin}
    success = run['failure'] is None and run['exit_code'] == 0
    stdout_pin, stderr_pin = _put(archive, run['stdout']), _put(archive, run['stderr'])
    runtime_pin = _json_artifact(archive, runtime) if runtime is not None else None
    syntax = {'schema':'twin.source-extraction-generated-syntax/v1','profile':plan['profile'],
        'parent_sha256':plan['parent_sha256'],'output_sha256':stdout_pin,
        'output_bytes':len(run['stdout']),'ranges':ranges,
        'coverage':('UNESTABLISHED-native-generated-syntax' if native else 'complete-generated-syntax')}
    syntax_pin = _json_artifact(receipts, syntax) if success else None
    transform = {'identity':plan['profile'].split('/')[0],'version':plan['profile'].split('/')[1],
        'implementation_artifact_sha256':plan['implementation_artifact_sha256'],
        'configuration_sha256':plan['configuration_sha256']}
    standard_pin = None
    if success:
        standard_pin = _json_artifact(receipts, {'schema':'twin.source-transform-receipt/v1',**transform,
            'parent_sha256':plan['parent_sha256'],'output_sha256':stdout_pin,
            'output_bytes':len(run['stdout']),'exit_code':0})
    dossier = {'schema':'twin.source-extraction-execution/v2' if observed else 'twin.source-extraction-execution/v1','purpose':plan['purpose'],
        'profile':plan['profile'],'disposition':'success' if success else 'failure',
        'relation':'new-execution-from-identical-frozen-raw',
        'predecessor_sha256':plan['predecessor_sha256'],'parent_sha256':plan['parent_sha256'],
        'parent_bytes':len(parent),'output_sha256':stdout_pin,'output_bytes':len(run['stdout']),
        'standard_receipt_sha256':standard_pin, **transform,'invocation_sha256':invocation_pin,
        'runtime_observation_sha256':runtime_pin,'closure_scope':closure['scope'],
        'platform_closure':closure['platform_closure'],'started_at':run['started_at'],
        'ended_at':run['ended_at'],'elapsed_seconds':run['elapsed_seconds'],'exit_code':run['exit_code'],
        'stdout':{'sha256':stdout_pin,'bytes':len(run['stdout'])},
        'stderr':{'sha256':stderr_pin,'bytes':len(run['stderr'])},
        'streams_complete':run['streams_complete'],'observed_bytes_lower_bound':run['observed_bytes_lower_bound'],
        'process_group':run['process_group'],'workspace_cleanup':workspace_cleanup,
        'failure':run['failure'] if run['failure'] else (None if success else 'nonzero-exit'),
        'generated_syntax_sha256':syntax_pin}
    if observed:
        dossier['native_observation_sha256'] = native_observation_pin
    dossier_pin = _json_artifact(receipts, dossier)
    result = {'status':'success' if success else 'failure','failure':dossier['failure'],
        'archive':archive,'receipts':receipts,'dossier_sha256':dossier_pin}
    if success:
        assert standard_pin is not None and syntax_pin is not None
        lineage = ([{'kind':'byte-copy','output_start':0,'output_end':len(run['stdout']),
                    'parent_start':0,'parent_end':len(parent)}] if plan['profile']=='utf8-identity/1'
            else [{'kind':'whole-transform-output','output_start':0,'output_end':len(run['stdout']),
                'parent_scope':'complete-exact-parent-artifact','claim':'disclosed-transformation-not-raw-byte-equivalence'}])
        if not run['stdout']:
            # The published member contract requires a nonempty lineage span.
            result.update(status='failure', failure='empty-output-hold')
            # Do not return a successful receipt/index when no legal member can be made.
            receipts.pop(standard_pin)
            receipts.pop(syntax_pin)
            receipts.pop(dossier_pin)
            dossier.update(disposition='failure',failure='empty-output-hold',standard_receipt_sha256=None,
                           generated_syntax_sha256=None)
            result['dossier_sha256'] = _json_artifact(receipts,dossier)
            return result
        member = {'id':plan['member_id'],'identity':'new:' + plan['profile'],'version':'1',
            'role':'derived-extraction','sha256':stdout_pin,'bytes':len(run['stdout']),
            'parent':{'member_id':'original','sha256':plan['parent_sha256']},
            'transform':{'lineage_status':'pinned',**transform,'execution_receipt_artifact_sha256':standard_pin},
            'lineage':lineage}
        index_pin = _json_artifact(receipts, {'schema':'twin.source-extraction-custody-index/v1',
            'member_id':plan['member_id'],'standard_receipt_sha256':standard_pin,
            'dossier_sha256':dossier_pin,'predecessor_sha256':plan['predecessor_sha256']})
        result.update(member=member,index_sha256=index_pin)
    return result


def _execution_contract(config: Any, purpose: str) -> None:
    _closed(config, {'schema','purpose','index_sha256s'})
    if (config['schema'] != 'twin.source-migration-execution-contract/v1' or config['purpose'] != purpose
            or type(config['index_sha256s']) is not list
            or any(type(pin) is not str for pin in config['index_sha256s'])
            or len(set(config['index_sha256s'])) != len(config['index_sha256s'])):
        raise MetadataMigrationHold('independently pinned execution contract differs')
    for pin in config['index_sha256s']:
        _hash(pin)


def _bind(fn, config_name: str, config: dict):
    """Independent defaults, actual protected module globals; never mutate shared functions."""
    # JSON cloning has no object aliases/cycles or captured executable state.
    def no_alias(value, seen):
        if type(value) in (dict,list):
            if id(value) in seen:
                raise MetadataMigrationHold('aliased/cyclic binding config')
            seen.add(id(value))
            for child in value.values() if type(value) is dict else value:
                no_alias(child, seen)
        elif value is not None and type(value) not in (str,int,bool,float):
            raise MetadataMigrationHold('non-JSON binding config')
    no_alias(config, set())
    copied = sm._json(sm.canonical(config))
    bound = types.FunctionType(fn.__code__, fn.__globals__, fn.__name__, fn.__defaults__)
    bound.__module__, bound.__qualname__ = fn.__module__, fn.__qualname__
    bound.__kwdefaults__ = {config_name:copied}
    return bound


def freeze_migration_authority(issuer: str, policy_id: str, policy_version: str, policy_sha256: str,
                               *, policy: dict, layout_config: dict, execution_contract: dict) -> sm.MetadataAuthority:
    """The reviewed migration construction path always protects its actual helper module."""
    _layout(layout_config, policy['purpose'])
    _execution_contract(execution_contract, policy['purpose'])
    adapter = _bind(retained_legacy_receipt_adapter, 'layout_config', layout_config)
    checker = _bind(migration_source_checker, 'execution_contract', execution_contract)
    from . import source_native_observation as native_observer
    return sm.MetadataAuthority.freeze(issuer,policy_id,policy_version,policy_sha256,adapter,checker,
        policy=policy,helper_modules=(sys.modules[__name__],native_observer,pdf_output_origin,pdf_native_bridge))


def _syntax_check(syntax: Any, profile: str, parent_pin: str, output: bytes) -> list[dict]:
    _closed(syntax, {'schema','profile','parent_sha256','output_sha256','output_bytes','ranges','coverage'})
    if (syntax['schema'] != 'twin.source-extraction-generated-syntax/v1' or syntax['profile'] != profile
            or syntax['parent_sha256'] != parent_pin or syntax['output_sha256'] != sm.sha256(output)
            or type(syntax['output_bytes']) is not int or syntax['output_bytes'] != len(output)
            or type(syntax['ranges']) is not list
            or syntax['coverage'] != ('UNESTABLISHED-native-generated-syntax' if profile=='pdf-text-xpdf/1' else 'complete-generated-syntax')):
        raise MetadataMigrationHold('generated syntax binding differs')
    cursor = 0
    for ordinal, span in enumerate(syntax['ranges']):
        _closed(span, {'start_byte','end_byte','kind','text_utf8','event_ordinal','event_kind'})
        start, end = span['start_byte'], span['end_byte']
        if (type(start) is not int or type(end) is not int or type(span['event_ordinal']) is not int
                or not cursor <= start < end <= len(output) or span['event_ordinal'] != ordinal
                or span['kind'] != 'syntactic-separator' or span['text_utf8'] != '\n'
                or span['event_kind'] not in ('start','end','startend') or output[start:end] != b'\n'):
            raise MetadataMigrationHold('generated syntax range differs')
        cursor = end
    if profile == 'utf8-identity/1' and syntax['ranges']:
        raise MetadataMigrationHold('identity output cannot invent syntax')
    return syntax['ranges']


def _checked_execution(member: dict, parent: dict, index_pin: str, archive: dict, receipts: dict,
                       policy: dict) -> list[dict]:
    index = sm._json(sm._artifact(receipts,index_pin))
    _closed(index, {'schema','member_id','standard_receipt_sha256','dossier_sha256','predecessor_sha256'})
    if (index['schema'] != 'twin.source-extraction-custody-index/v1' or index['member_id'] != member['id']
            or index['standard_receipt_sha256'] != member['transform']['execution_receipt_artifact_sha256']):
        raise MetadataMigrationHold('observed custody index binding differs')
    _hash(index['predecessor_sha256'])
    dossier = sm._json(sm._artifact(receipts,index['dossier_sha256']))
    if dossier.get('schema')=='twin.source-extraction-execution/v3':
        if policy['purpose']!='actual': raise MetadataMigrationHold('profile2 actual custody selection required')
        plan={'schema':'twin.source-extraction-plan/v1','purpose':policy['purpose'],'profile':dossier['profile'],
            'parent_sha256':parent['sha256'],'parent_bytes':parent['bytes'],'member_id':member['id'],
            'predecessor_sha256':index['predecessor_sha256'],'implementation_artifact_sha256':dossier['implementation_artifact_sha256'],
            'configuration_sha256':dossier['configuration_sha256'],'archive':archive}
        if {key:member['transform'][key] for key in ('identity','version','implementation_artifact_sha256','configuration_sha256')} not in policy['allowed_transforms']:
            raise MetadataMigrationHold('execution transform not independently approved')
        pdf_native_bridge.verify_pdf_extraction_bundle(plan,sm._artifact(archive,parent['sha256']),
            {'status':'success','failure':None,'archive':archive,'receipts':receipts,'dossier_sha256':index['dossier_sha256'],'member':member,'index_sha256':index_pin})
        return []
    _closed(dossier, {'schema','purpose','profile','disposition','relation','predecessor_sha256',
        'parent_sha256','parent_bytes','output_sha256','output_bytes','standard_receipt_sha256',
        'identity','version','implementation_artifact_sha256','configuration_sha256','invocation_sha256',
        'runtime_observation_sha256','closure_scope','platform_closure','started_at','ended_at',
        'elapsed_seconds','exit_code','stdout','stderr','streams_complete','observed_bytes_lower_bound',
        'failure','generated_syntax_sha256','process_group','workspace_cleanup'} | ({'native_observation_sha256'} if dossier.get('schema')=='twin.source-extraction-execution/v2' else set()))
    observed = dossier['schema']=='twin.source-extraction-execution/v2'
    if (dossier['schema'] not in ('twin.source-extraction-execution/v1','twin.source-extraction-execution/v2') or dossier['purpose'] != policy['purpose']
            or dossier['disposition'] != 'success' or dossier['relation'] != 'new-execution-from-identical-frozen-raw'
            or dossier['predecessor_sha256'] != index['predecessor_sha256']
            or dossier['parent_sha256'] != parent['sha256'] or dossier['parent_bytes'] != parent['bytes']
            or dossier['output_sha256'] != member['sha256'] or dossier['output_bytes'] != member['bytes']
            or dossier['standard_receipt_sha256'] != index['standard_receipt_sha256']
            or type(dossier['exit_code']) is not int or dossier['exit_code'] != 0
            or dossier['streams_complete'] is not True or dossier['failure'] is not None):
        raise MetadataMigrationHold('actual execution dossier differs')
    group = dossier['process_group']
    from . import source_native_observation as native_observer
    if observed:
        native_observer.validate_native_custody(group)
        if dossier['workspace_cleanup']!='removed': raise MetadataMigrationHold('native workspace cleanup unestablished')
    else:
        _closed(group, {'leader_pid','reservation','signals','direct_child_reaped','absence_verified'})
        if (type(group['leader_pid']) is not int or group['leader_pid'] <= 0
                or group['reservation'] != 'unreaped-direct-child' or group['direct_child_reaped'] is not True
                or group['absence_verified'] is not True or dossier['workspace_cleanup'] != 'removed'
                or type(group['signals']) is not list or not group['signals']):
            raise MetadataMigrationHold('owned process group cleanup unestablished')
        if ([row.get('signal') for row in group['signals'] if type(row) is dict]
                not in ([int(signal.SIGTERM)], [int(signal.SIGTERM),int(signal.SIGKILL)])
                or len(group['signals']) == 1 and group['signals'][0].get('outcome') != 'absent'):
            raise MetadataMigrationHold('owned process group signal order differs')
        for observation in group['signals']:
            _closed(observation, {'signal','outcome'})
            if (type(observation['signal']) is not int or observation['signal'] not in (signal.SIGTERM,signal.SIGKILL)
                    or observation['outcome'] not in ('sent','absent','permission-denied','os-error')):
                raise MetadataMigrationHold('owned process group signal observation differs')
    for key in ('identity','version','implementation_artifact_sha256','configuration_sha256'):
        if dossier[key] != member['transform'][key]:
            raise MetadataMigrationHold('actual execution transform tuple differs')
    profile = dossier['profile']
    plan = {'schema':'twin.source-extraction-plan/v1','purpose':policy['purpose'],'profile':profile,
        'parent_sha256':parent['sha256'],'parent_bytes':parent['bytes'],'member_id':member['id'],
        'predecessor_sha256':index['predecessor_sha256'],
        'implementation_artifact_sha256':dossier['implementation_artifact_sha256'],
        'configuration_sha256':dossier['configuration_sha256'],'archive':archive}
    original, output = sm._artifact(archive,parent['sha256']), sm._artifact(archive,member['sha256'])
    from . import source_native_observation as native_observer
    if observed and policy['purpose']!='actual':
        raise MetadataMigrationHold('actual observer dossier purpose differs')
    config, closure = (native_observer.validate_native_candidate_plan(plan,original) if observed else _validate_plan(plan,original))
    approved = {key:member['transform'][key] for key in ('identity','version','implementation_artifact_sha256','configuration_sha256')}
    if approved not in policy['allowed_transforms']:
        raise MetadataMigrationHold('execution transform not independently approved')
    if dossier['closure_scope'] != closure['scope'] or dossier['platform_closure'] != closure['platform_closure']:
        raise MetadataMigrationHold('execution closure scope differs')
    started, ended = sm._instant(dossier['started_at']), sm._instant(dossier['ended_at'])
    if (ended < started or type(dossier['elapsed_seconds']) not in (int,float)
            or not 0 <= dossier['elapsed_seconds'] <= config['limits']['wall_seconds']):
        raise MetadataMigrationHold('actual execution interval differs')
    for stream in ('stdout','stderr'):
        record = dossier[stream]
        _closed(record, {'sha256','bytes'})
        raw = sm._artifact(archive,record['sha256'])
        if type(record['bytes']) is not int or record['bytes'] != len(raw) or len(raw) > config['limits'][stream+'_bytes']:
            raise MetadataMigrationHold('execution stream binding/limit differs')
    if (dossier['stdout'] != {'sha256':member['sha256'],'bytes':member['bytes']}
            or dossier['observed_bytes_lower_bound'] != {'stdout':dossier['stdout']['bytes'],'stderr':dossier['stderr']['bytes']}):
        raise MetadataMigrationHold('complete execution stream lengths differ')
    runtime = sm._json(sm._artifact(archive,dossier['runtime_observation_sha256']))
    if not observed and runtime != closure['process_files']:
        raise MetadataMigrationHold('actual observed runtime differs')
    invocation = sm._json(sm._artifact(archive,dossier['invocation_sha256']))
    _closed(invocation, {'schema','argv','cwd','environment','stdin'})
    if (type(invocation['cwd']) is not str or invocation != {
            'schema':'twin.source-extraction-invocation/v1','argv':(_pdf_command(closure['process_files']['executable'],invocation['cwd'])
                if profile=='pdf-text-xpdf/1' else _observed_command(closure['process_files']['executable'],invocation['cwd']) if observed else _command(closure['process_files']['executable'],invocation['cwd'])),
            'cwd':invocation['cwd'],'environment':ENVIRONMENT,'stdin':'OWNED-EOF-PIPE' if observed else 'DEVNULL'}):
        raise MetadataMigrationHold('actual invocation differs')
    syntax = sm._json(sm._artifact(receipts,dossier['generated_syntax_sha256']))
    ranges = _syntax_check(syntax,profile,parent['sha256'],output)
    if observed:
        observation = sm._json(sm._artifact(archive,dossier['native_observation_sha256']))
        native_observer.verify_native_observation(observation,archive,purpose='actual')
        native_observer.validate_observation_binding(observation,plan,original,invocation)
        host_policy=sm._json(sm._artifact(archive,observation['host_policy_sha256']))
        if not sm._instant(host_policy['not_before'])<=started<=ended<sm._instant(host_policy['not_after']):
            raise MetadataMigrationHold('observed invocation outside selected host interval')
        terminal=observation['events'][-1]['data']
        if group!=terminal['custody']: raise MetadataMigrationHold('native custody/dossier binding differs')
        if terminal['stdout_sha256']!=member['sha256'] or terminal['stderr_sha256']!=dossier['stderr']['sha256']:
            raise MetadataMigrationHold('observed stream/dossier binding differs')
        if profile=='pdf-text-xpdf/1':
            if runtime != {'schema':'twin.native-observed-runtime/v1','observation_sha256':dossier['native_observation_sha256']}:
                raise MetadataMigrationHold('actual native runtime binding differs')
        else:
            workdir=invocation['cwd']
            if terminal['sidecars'][workdir+'/runtime']['sha256']!=dossier['runtime_observation_sha256']:
                raise MetadataMigrationHold('actual runtime sidecar binding differs')
            expected_output,expected_ranges=_pure_observed_output(profile,original,config['limits'])
            sidecar_bytes=sm._artifact(archive,terminal['sidecars'][workdir+'/syntax']['sha256'])
            if expected_output!=output or expected_ranges!=ranges or sidecar_bytes!=b''.join(sm.canonical(row)+b'\n' for row in ranges):
                raise MetadataMigrationHold('observed generated syntax replay differs')
        return ranges
    # Bounded deterministic validation replay; it is NOT historical execution proof.
    replay = execute_new_extraction(plan,original)
    if replay['status'] != 'success' or sm._artifact(replay['archive'],member['sha256']) != output:
        raise MetadataMigrationHold('bounded extraction validation replay differs')
    replay_dossier = sm._json(sm._artifact(replay['receipts'],replay['dossier_sha256']))
    replay_syntax = sm._json(sm._artifact(replay['receipts'],replay_dossier['generated_syntax_sha256']))
    if replay_syntax != syntax:
        raise MetadataMigrationHold('generated syntax provenance replay differs')
    return ranges


def migration_source_checker(manifest: dict, archive: dict, receipts: dict, policy: dict,
                             *, execution_contract: dict | None = None) -> None:
    if execution_contract is None:
        raise MetadataMigrationHold('unbound actual execution evidence')
    _execution_contract(execution_contract,policy['purpose'])
    syntax_by_member = {}
    native_members = set()
    pdf_maps = {}
    indexes = []
    for pin, raw in receipts.items():
        # Receipt collections can contain arbitrary retained non-JSON logs. Only a valid
        # schema discriminator opts into the closed custody-index shape.
        try:
            entry = sm._json(raw)
        except ValueError:
            continue
        if type(entry) is dict and entry.get('schema') == 'twin.source-extraction-custody-index/v1':
            indexes.append((pin,entry))
    for member in manifest['members'].values():
        if member['role'] != 'derived-extraction':
            continue
        matches = [(pin,index) for pin,index in indexes if index.get('member_id') == member['id']]
        if len(matches) != 1 or matches[0][0] not in execution_contract['index_sha256s']:
            raise MetadataMigrationHold('exact independently observed custody index missing/ambiguous')
        parent = sm._reference(member['parent'],manifest['members'])
        if member['transform']['identity'] == 'pdf-text-xpdf':
            native_members.add(member['id'])
        syntax_by_member[member['id']] = _checked_execution(member,parent,matches[0][0],archive,receipts,policy)
        if member['transform']['identity']=='pdf-text-xpdf-origin':
            dossier=sm._json(sm._artifact(receipts,matches[0][1]['dossier_sha256']))
            pdf_maps[member['id']]=pdf_output_origin.check_pdf_origin_events(sm._artifact(archive,member['sha256']),sm._artifact(archive,dossier['origin']['sha256']))
    for member_id,mapping in pdf_maps.items():
        pdf_output_origin.check_pdf_publisher_witnesses(mapping,manifest,member_id)
    witnesses = [observation['witness'] for observation in manifest['observations'].values()]
    if manifest['statement']['origin_role'] == 'publisher-quotation':
        witnesses.append(manifest['statement']['witness'])
    witnesses += [excerpt['witness'] for excerpt in manifest['visible_excerpts'] if excerpt['origin_role']=='publisher-quotation']
    for witness in witnesses:
        if witness['member_id'] in native_members:
            raise MetadataMigrationHold('native generated syntax provenance unestablished for publisher quotation')
        for span in syntax_by_member.get(witness['member_id'],[]):
            if witness['start_byte'] < span['end_byte'] and witness['end_byte'] > span['start_byte']:
                raise MetadataMigrationHold('publisher witness intersects generated syntax')
    # Unconditionally preserve all stock source/semantic/lineage/role/precision checks.
    sm.retained_source_checker(manifest,archive,receipts,policy)


def _pdf_origin_command(executable: str, workdir: str) -> list[str]:
    return [executable,'-cfg',str(Path(workdir)/'native-config'),'-enc','UTF-8','-eol','unix',
            '-nopgbrk','-twin-origin-fd','3',str(Path(workdir)/'input'),'-']


def _pdf_command(executable: str, workdir: str) -> list[str]:
    return [executable,'-cfg',str(Path(workdir)/'native-config'),'-enc','UTF-8','-eol','unix',
            '-nopgbrk',str(Path(workdir)/'input'),'-']


def prepare_pdf_extraction_plan(parent: bytes, *, purpose: str, predecessor_sha256: str,
                                member_id: str, executable: str, configuration: bytes,
                                tool_version: str, version_observation: bytes,
                                retained_files: dict[str, bytes],
                                platform_files: dict[str, bytes] | None = None) -> dict:
    """Freeze independently supplied native closure without running a converter.

    A TEST_ONLY fake converter proves subprocess mechanics, not native PDF extraction.
    The fixed native route is implemented, but actual OS dependency observation is
    unsupported: actual plans hold even with a well-shaped complete declaration.
    Exact files, tool-version evidence and configuration are mandatory, never inferred.
    """
    profile = 'pdf-text-xpdf/1'
    if purpose not in ('TEST_ONLY','actual') or type(parent) is not bytes or len(parent)>PROFILES[profile]['input_bytes']:
        raise MetadataMigrationHold('native parent/purpose/limit differs')
    _hash(predecessor_sha256)
    if (type(member_id) is not str or not member_id or type(tool_version) is not str or not tool_version
            or type(configuration) is not bytes or type(version_observation) is not bytes or not version_observation
            or purpose=='TEST_ONLY' and not tool_version.startswith('TEST_ONLY-')):
        raise MetadataMigrationHold('native tool/config/version evidence missing')
    if purpose=='actual' and (not platform_files or tool_version.startswith('TEST_ONLY-')):
        raise MetadataMigrationHold('complete approved actual platform closure unestablished')
    if type(retained_files) is not dict or not retained_files:
        raise MetadataMigrationHold('native dependency closure missing')
    executable = str(Path(executable).resolve())
    archive: dict[str,bytes] = {}
    def retain(files):
        rows = []
        for path, raw in sorted(files.items()):
            if type(raw) is not bytes or str(Path(path).resolve()) != path or Path(path).read_bytes()!=raw:
                raise MetadataMigrationHold('exact native dependency resource differs')
            rows.append({'path':path,'sha256':_put(archive,raw),'bytes':len(raw)})
        return rows
    rows = retain(retained_files)
    if executable not in retained_files:
        raise MetadataMigrationHold('actual retained converter binary missing')
    platform_rows = retain(platform_files or {})
    driver_files = []
    for path in (Path(__file__),Path(sm.__file__),sm.SCHEMA_PATH):
        raw = path.read_bytes()
        driver_files.append({'path':str(path.resolve()),'sha256':_put(archive,raw),'bytes':len(raw)})
    driver_inventory, _ = sm._runtime_helper_inventory((sys.modules[__name__],))
    observation = {'schema':'twin.source-extraction-native-tool-files/v1','executable':executable,
        'version':tool_version,'version_observation_sha256':_put(archive,version_observation),'files':rows}
    closure = {'schema':'twin.source-extraction-closure/v1',
        'scope':'TEST_ONLY-native-converter-fixture/v1' if purpose=='TEST_ONLY' else 'complete-approved-runtime/v1',
        'purpose':purpose,'platform_closure':'UNESTABLISHED' if purpose=='TEST_ONLY' else 'retained-exact-platform-files',
        'process_files':observation,'platform_files':platform_rows,'driver_files':driver_files,'driver_inventory':driver_inventory}
    implementation_pin = _json_artifact(archive,closure)
    config = {'schema':'twin.source-extraction-config/v1','profile':profile,'purpose':purpose,
        'limits':copy.deepcopy(PROFILES[profile]),'environment':dict(ENVIRONMENT),
        'diagnostic_policy':'accept-bounded-on-zero','test_only_behavior':'normal',
        'native_config_sha256':_put(archive,configuration)}
    config_pin = _json_artifact(archive,config)
    plan = {'schema':'twin.source-extraction-plan/v1','purpose':purpose,'profile':profile,
        'parent_sha256':sm.sha256(parent),'parent_bytes':len(parent),'member_id':member_id,
        'predecessor_sha256':predecessor_sha256,'implementation_artifact_sha256':implementation_pin,
        'configuration_sha256':config_pin,'archive':archive}
    _validate_plan(plan,parent)
    return plan


def _pure_observed_output(profile: str, parent: bytes, limits: dict) -> tuple[bytes,list[dict]]:
    """Bounded semantic replay, no child/native execution or mutable class registry."""
    import html.parser
    text=parent.decode('utf8',errors='strict')
    if profile=='utf8-identity/1':
        return parent,[]
    if profile!='html-text-utf8/1':
        raise MetadataMigrationHold('native generated formatting remains unestablished')
    output=bytearray();ranges: list[dict]=[];syntax_bytes=0
    def emit(value: str, event: str | None = None) -> None:
        nonlocal syntax_bytes
        raw=value.encode('utf8'); start=len(output)
        if len(raw)+start>limits['stdout_bytes']:
            raise MetadataMigrationHold('pure output limit')
        output.extend(raw)
        if event is not None:
            row={'start_byte':start,'end_byte':len(output),'kind':'syntactic-separator',
                'text_utf8':value,'event_ordinal':len(ranges),'event_kind':event}
            syntax_bytes+=len(sm.canonical(row))+1
            if syntax_bytes>limits['syntax_bytes']:
                raise MetadataMigrationHold('pure syntax limit')
            ranges.append(row)
    parser=html.parser.HTMLParser(convert_charrefs=True)
    setattr(parser,'handle_data',lambda value: emit(value))
    setattr(parser,'handle_starttag',lambda tag, attrs: emit('\n','start'))
    setattr(parser,'handle_endtag',lambda tag: emit('\n','end'))
    setattr(parser,'handle_startendtag',lambda tag, attrs: emit('\n','startend'))
    parser.feed(text);parser.close()
    return bytes(output),ranges
