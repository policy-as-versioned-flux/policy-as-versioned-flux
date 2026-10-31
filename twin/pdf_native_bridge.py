"""Fixed PDF-origin profile bundle consistency and private final assembly.

Public verification is structural only: no store access, issuance or index approval.
Only the native actual-acquisition call graph may deposit a completed extraction.
"""
from __future__ import annotations
import copy
from pathlib import Path
import sys
from typing import Any
from . import source_metadata as sm
from . import pdf_output_origin as origin

PROFILE='pdf-text-xpdf-origin/2'
ARCHIVE_SHA256='1c38f527c46caee0f712386d42a885b96a31ed9ce11904e872559859894d137e'
PACKAGE_SHA256='37b3903b671b49c2d75efa7e2ab0694e64dde6affd0df7208df176aa86152adc'
PATCH_SHA256='ce4d927e34922b737552a605ae8332651031c8b77893264e72699215ed181395'
ORIGIN_BYTES=64*1048576
ORIGIN_RECORD_BYTES=65536
ORIGIN_EVENTS=1000000
BUFFER_BYTES=456*1048576
CONFIG_KEYS={'schema','profile','purpose','limits','environment','diagnostic_policy','test_only_behavior','native_config_sha256','pdf_origin'}
ORIGIN_CONFIG_KEYS={'protocol_sha256','event_schema_sha256','verifier_artifact_sha256','build_identity_sha256','origin_bytes','origin_record_bytes','origin_events'}
BUILD_KEYS={'schema','source_archive_sha256','source_package_sha256','patch_sha256','prepared_tree_sha256','build_configuration_sha256','toolchain_sha256','build_log_sha256','executable_sha256','executable_bytes','target'}
VERIFIER_KEYS={'schema','module','source_sha256','helper_inventory_sha256','protocol_sha256','event_schema_sha256'}
ENVELOPE_KEYS={'schema','purpose','profile','plan_sha256','run_id','parent_sha256','parent_bytes','configuration_sha256','implementation_artifact_sha256','executable','build_identity_sha256','verifier_artifact_sha256','invocation_sha256','host_policy_sha256','native_observation_sha256','process','streams','wait','interval','native_custody_sha256','workspace_cleanup','pdf_origin_map_sha256','errors'}
DOSSIER_KEYS={'schema','purpose','profile','disposition','relation','predecessor_sha256','parent_sha256','parent_bytes','output_sha256','output_bytes','standard_receipt_sha256','identity','version','implementation_artifact_sha256','configuration_sha256','invocation_sha256','runtime_observation_sha256','closure_scope','platform_closure','started_at','ended_at','elapsed_seconds','exit_code','stdout','stderr','streams_complete','observed_bytes_lower_bound','process_group','workspace_cleanup','failure','native_observation_sha256','origin','pdf_origin_map_sha256','pdf_origin_observation_sha256'}


class PdfBridgeHold(ValueError):
    """Bounded consistency/selection hold; never acquisition authority."""


def _closed(value: Any, fields: set[str]) -> None:
    if type(value) is not dict or set(value)!=fields: raise PdfBridgeHold('closed PDF bridge record required')


def _raw(archive: dict, pin: str) -> bytes:
    return sm._artifact(archive,pin)


def _put(archive: dict, raw: bytes) -> str:
    pin=sm.sha256(raw);archive[pin]=raw;return pin


def _json_put(archive: dict, value: Any) -> str:
    return _put(archive,sm.canonical(value))


def _modules() -> tuple:
    from . import source_native_observation as native, source_metadata_migration as migration
    return migration,native,origin,sys.modules[__name__]


def _driver_inventory() -> list[dict]:
    return sm._runtime_helper_inventory(_modules())[0]


def _validate_profile_config(plan: dict, archive: dict, closure: dict) -> dict:
    from . import source_metadata_migration as migration
    config=sm._json(_raw(archive,plan['configuration_sha256']));_closed(config,CONFIG_KEYS)
    _closed(config['limits'],set(migration.PROFILES[PROFILE]))
    if any(type(value) is not int for value in config['limits'].values()): raise PdfBridgeHold('fixed PDF limits require exact integers')
    if config!={'schema':'twin.source-extraction-config/v2','profile':PROFILE,'purpose':plan['purpose'],
            'limits':migration.PROFILES[PROFILE],'environment':migration.ENVIRONMENT,'diagnostic_policy':'accept-bounded-on-zero',
            'test_only_behavior':'normal','native_config_sha256':config['native_config_sha256'],'pdf_origin':config['pdf_origin']}:
        raise PdfBridgeHold('fixed PDF profile/config differs')
    spec=config['pdf_origin'];_closed(spec,ORIGIN_CONFIG_KEYS)
    if spec!={'protocol_sha256':origin.PROTOCOL_SHA256,'event_schema_sha256':origin.SCHEMA_SHA256,
            'verifier_artifact_sha256':spec['verifier_artifact_sha256'],'build_identity_sha256':spec['build_identity_sha256'],
            'origin_bytes':ORIGIN_BYTES,'origin_record_bytes':ORIGIN_RECORD_BYTES,'origin_events':ORIGIN_EVENTS}:
        raise PdfBridgeHold('fixed origin contract differs')
    for key in ('origin_bytes','origin_record_bytes','origin_events'):
        if type(spec[key]) is not int: raise PdfBridgeHold('origin bound must be an integer')
    _raw(archive,config['native_config_sha256'])
    pf=closure['process_files'];exe=next((row for row in pf['files'] if row['path']==pf['executable']),None)
    if exe is None: raise PdfBridgeHold('fixed executable candidate missing')
    build=sm._json(_raw(archive,spec['build_identity_sha256']));_closed(build,BUILD_KEYS)
    if (build['schema']!='twin.native-build-identity/v1' or build['source_archive_sha256']!=ARCHIVE_SHA256
            or build['source_package_sha256']!=PACKAGE_SHA256 or build['patch_sha256']!=PATCH_SHA256
            or build['executable_sha256']!=exe['sha256'] or type(build['executable_bytes']) is not int
            or build['executable_bytes']!=exe['bytes'] or build['target']!={'system':'Linux','machine':'x86_64','elf_class':64}
            or type(build['target']['elf_class']) is not int):
        raise PdfBridgeHold('selected Linux source/build/executable association differs')
    for key in ('source_archive_sha256','source_package_sha256','patch_sha256','prepared_tree_sha256','build_configuration_sha256','toolchain_sha256','build_log_sha256','executable_sha256'):
        if not _raw(archive,build[key]): raise PdfBridgeHold('retained build evidence empty')
    package=sm._json(_raw(archive,build['source_package_sha256']))
    if package.get('archive_sha256')!=ARCHIVE_SHA256 or package.get('package_files',{}).get('xpdf-4.06-origin.patch',{}).get('sha256')!=PATCH_SHA256:
        raise PdfBridgeHold('source package association differs')
    verifier=sm._json(_raw(archive,spec['verifier_artifact_sha256']));_closed(verifier,VERIFIER_KEYS)
    source=Path(origin.__file__).read_bytes();inventory=closure['driver_inventory']
    if verifier!={'schema':'twin.pdf-origin-verifier-identity/v1','module':'twin.pdf_output_origin','source_sha256':sm.sha256(source),
            'helper_inventory_sha256':sm.sha256(sm.canonical(inventory)),'protocol_sha256':origin.PROTOCOL_SHA256,'event_schema_sha256':origin.SCHEMA_SHA256}:
        raise PdfBridgeHold('selected verifier/source inventory differs')
    if _raw(archive,verifier['source_sha256'])!=source or _raw(archive,verifier['helper_inventory_sha256'])!=sm.canonical(inventory): raise PdfBridgeHold('verifier evidence differs')
    return config


def _validate_plan(plan: dict, parent: bytes) -> tuple[dict,dict]:
    from . import source_native_observation as native, source_metadata_migration as migration
    _closed(plan,{'schema','purpose','profile','parent_sha256','parent_bytes','member_id','predecessor_sha256','implementation_artifact_sha256','configuration_sha256','archive'})
    if (plan['schema']!='twin.source-extraction-plan/v1' or plan['profile']!=PROFILE or plan['purpose'] not in ('actual','TEST_ONLY')
            or type(parent) is not bytes or plan['parent_sha256']!=sm.sha256(parent) or type(plan['parent_bytes']) is not int
            or plan['parent_bytes']!=len(parent) or len(parent)>256*1048576 or type(plan['member_id']) is not str or not plan['member_id']):
        raise PdfBridgeHold('frozen PDF plan/parent differs')
    migration._hash(plan['predecessor_sha256']);archive=plan['archive']
    if type(archive) is not dict: raise PdfBridgeHold('retained archive required')
    for pin in archive: _raw(archive,pin)
    closure=sm._json(_raw(archive,plan['implementation_artifact_sha256']))
    _closed(closure,{'schema','purpose','scope','platform_closure','process_files','platform_files','driver_files','driver_inventory'})
    if closure['schema']!='twin.source-extraction-closure/v1' or closure['purpose']!=plan['purpose'] or closure['scope']!='native-candidate-file-set/v1' or closure['platform_closure']!='OBSERVATION-REQUIRED': raise PdfBridgeHold('candidate scope is not observation')
    if closure['driver_inventory']!=_driver_inventory(): raise PdfBridgeHold('PDF reached-helper inventory changed')
    pf=closure['process_files'];_closed(pf,{'schema','executable','files','version','version_observation_sha256'})
    if pf['schema']!='twin.source-extraction-native-tool-files/v1' or type(pf['version']) is not str or not pf['version'] or plan['purpose']=='actual' and pf['version'].startswith('TEST_ONLY'):
        raise PdfBridgeHold('native tool candidate identity differs')
    _raw(archive,pf['version_observation_sha256'])
    paths=set();total=0
    for row in pf['files']+closure['platform_files']+closure['driver_files']:
        _closed(row,{'path','sha256','bytes'});path=native._path(row['path']);raw=_raw(archive,row['sha256'])
        if path in paths or type(row['bytes']) is not int or row['bytes']!=len(raw): raise PdfBridgeHold('candidate bytes/paths differ')
        total+=len(raw);paths.add(path)
    required={str(Path(module.__file__).resolve()) for module in _modules()}|{str(Path(sm.__file__).resolve()),str(sm.SCHEMA_PATH.resolve())}
    if not required<=paths or pf['executable'] not in paths or len(paths)>native.MAX_FILES or total>native.MAX_DEPENDENCY_BYTES: raise PdfBridgeHold('driver candidate closure missing/over limit')
    executable=next(row for row in pf['files'] if row['path']==pf['executable']);native.elf_interpreter(_raw(archive,executable['sha256']))
    return _validate_profile_config(plan,archive,closure),closure


def _require_actual_selection(store: Any, plan: dict) -> None:
    """Packet bytes cannot select their own actual build/config association."""
    from . import source_native_observation as native
    if type(store) is not native.NativeObservationStore or store._purpose!='actual' or store._host_context is None: raise PdfBridgeHold('actual private host selection absent')
    policy=native._host_window(store._host_context)
    config=sm._json(_raw(plan['archive'],plan['configuration_sha256']))
    for pin in (plan['configuration_sha256'],config['pdf_origin']['build_identity_sha256']):
        if pin not in policy['evidence_sha256s'] or _raw(store._host_context._evidence,pin)!=_raw(plan['archive'],pin):
            raise PdfBridgeHold('independently selected actual build/config association unestablished')


def _binding(observation: dict, plan: dict, parent: bytes, invocation: dict) -> None:
    from . import source_metadata_migration as migration
    config,closure=_validate_plan(plan,parent);spec=observation['spec'];cwd=spec['cwd']
    if invocation!={'schema':'twin.source-extraction-invocation/v1','argv':migration._pdf_origin_command(closure['process_files']['executable'],cwd),'cwd':cwd,'environment':migration.ENVIRONMENT,'stdin':'OWNED-EOF-PIPE'}:
        raise PdfBridgeHold('fixed invocation differs')
    wanted={r['path']:r for r in closure['process_files']['files']+closure['platform_files']+closure['driver_files']}
    for name,raw in [('input',parent),('config',_raw(plan['archive'],plan['configuration_sha256'])),('native-config',_raw(plan['archive'],config['native_config_sha256']))]:
        wanted[cwd+'/'+name]={'path':cwd+'/'+name,'sha256':sm.sha256(raw),'bytes':len(raw)}
    if (observation['schema']!='twin.native-file-observation/v2' or observation['purpose']!=plan['purpose']
            or spec['purpose']!=plan['purpose'] or spec['profile']!=PROFILE
            or spec['plan_sha256']!=sm.sha256(sm.canonical({k:v for k,v in plan.items() if k!='archive'}))
            or spec['argv']!=invocation['argv'] or spec['environment']!=invocation['environment'] or spec['limits']!=config['limits']
            or {r['path']:r for r in spec['candidates']}!=wanted):
        raise PdfBridgeHold('exact plan/parent/invocation/candidate binding differs')


def _streams(observation: dict, archive: dict) -> dict:
    events=observation['events'];start=events[0]['data'];terminal=events[-1]['data']
    exit_event=next(e for e in events if e['kind']=='exit-stop');streams={}
    for name,fd in [('stdout',1),('stderr',2),('origin',3)]:
        initial=next(r for r in start['fds'] if r['fd']==fd)
        eof=next(e for e in events if e['kind']=='pipe-eof' and e['data']['channel']==name)
        closure={'kind':'kernel-exit','exit_stop_seq':exit_event['seq'],'terminal_seq':events[-1]['seq']}
        pending=None
        for event in events[:-1]:
            if event['kind']=='enter': pending=event
            elif event['kind']=='leave':
                if pending is not None and pending['data']['nr']==3 and pending['data']['args'][0]==fd and event['data']['result']==0:
                    if fd==3: raise PdfBridgeHold('origin explicit close forbidden')
                    closure={'kind':'explicit-close','enter_seq':pending['seq'],'leave_seq':event['seq']}
                pending=None
        pin=terminal[name+'_sha256'];raw=_raw(archive,pin)
        streams[name]={'fd':fd,'generation':0,'identity':initial['identity'],'sha256':pin,'bytes':len(raw),'eof_event_seq':eof['seq'],'closure':closure}
    return streams


def _project_completed_bundle(plan: dict, parent: bytes, observation: dict, artifacts: dict) -> dict:
    """Sole final assembler. Pure consistency; callers still need actual acquisition.

    This internal function never deposits an entry or approves a custody index.
    """
    from . import source_native_observation as native
    config,closure=_validate_plan(plan,parent);archive=dict(plan['archive']);archive.update(artifacts)
    for pin in archive: _raw(archive,pin)
    _put(archive,parent)
    native.verify_native_observation(observation,archive,purpose=plan['purpose'])
    spec=observation['spec'];invocation={'schema':'twin.source-extraction-invocation/v1','argv':spec['argv'],'cwd':spec['cwd'],'environment':spec['environment'],'stdin':'OWNED-EOF-PIPE'}
    _binding(observation,plan,parent,invocation)
    terminal=observation['events'][-1]['data'];run=observation['run'];host=observation['host_policy_sha256']
    if plan['purpose']=='actual':
        if type(host) is not str: raise PdfBridgeHold('actual host policy required')
        policy=sm._json(_raw(archive,host))
        if not sm._instant(policy['not_before'])<=sm._instant(run['started_at'])<=sm._instant(run['ended_at'])<sm._instant(policy['not_after']): raise PdfBridgeHold('actual host interval differs')
    elif host is not None: raise PdfBridgeHold('TEST_ONLY consistency requires null host policy')
    streams=_streams(observation,archive);output=_raw(archive,streams['stdout']['sha256'])
    if not output: raise PdfBridgeHold('empty output cannot form a derived member')
    mapping=origin.check_pdf_origin_events(output,_raw(archive,streams['origin']['sha256']))
    receipts: dict[str,bytes]={};map_pin=_put(receipts,mapping.description);obs_pin=_json_put(archive,observation);inv_pin=_json_put(archive,invocation)
    process={k:observation['events'][0]['data'][k] for k in ('pid','starttime','ppid','uid','gid')}
    executable=copy.deepcopy(observation['files'][spec['argv'][0]])
    envelope={'schema':'twin.pdf-output-origin-observation/v1','purpose':plan['purpose'],'profile':PROFILE,'plan_sha256':spec['plan_sha256'],'run_id':run['run_id'],
        'parent_sha256':plan['parent_sha256'],'parent_bytes':len(parent),'configuration_sha256':plan['configuration_sha256'],'implementation_artifact_sha256':plan['implementation_artifact_sha256'],
        'executable':executable,'build_identity_sha256':config['pdf_origin']['build_identity_sha256'],'verifier_artifact_sha256':config['pdf_origin']['verifier_artifact_sha256'],
        'invocation_sha256':inv_pin,'host_policy_sha256':host,'native_observation_sha256':obs_pin,'process':process,'streams':streams,'wait':terminal['wait'],'interval':run,
        'native_custody_sha256':_json_put(archive,terminal['custody']),'workspace_cleanup':'removed','pdf_origin_map_sha256':map_pin,'errors':[]}
    _closed(envelope,ENVELOPE_KEYS);env_pin=_json_put(receipts,envelope)
    transform={'identity':'pdf-text-xpdf-origin','version':'2','implementation_artifact_sha256':plan['implementation_artifact_sha256'],'configuration_sha256':plan['configuration_sha256']}
    standard=_json_put(receipts,{'schema':'twin.source-transform-receipt/v1',**transform,'parent_sha256':plan['parent_sha256'],'output_sha256':streams['stdout']['sha256'],'output_bytes':len(output),'exit_code':0})
    dossier={'schema':'twin.source-extraction-execution/v3','purpose':plan['purpose'],'profile':PROFILE,'disposition':'success','relation':'new-execution-from-identical-frozen-raw',
        'predecessor_sha256':plan['predecessor_sha256'],'parent_sha256':plan['parent_sha256'],'parent_bytes':len(parent),'output_sha256':streams['stdout']['sha256'],'output_bytes':len(output),
        'standard_receipt_sha256':standard,**transform,'invocation_sha256':inv_pin,'runtime_observation_sha256':_json_put(archive,{'schema':'twin.native-observed-runtime/v1','observation_sha256':obs_pin}),
        'closure_scope':closure['scope'],'platform_closure':closure['platform_closure'],'started_at':run['started_at'],'ended_at':run['ended_at'],'elapsed_seconds':run['elapsed_ns']/10**9,'exit_code':0,
        'stdout':{k:streams['stdout'][k] for k in ('sha256','bytes')},'stderr':{k:streams['stderr'][k] for k in ('sha256','bytes')},'origin':{k:streams['origin'][k] for k in ('sha256','bytes')},
        'streams_complete':True,'observed_bytes_lower_bound':{name:streams[name]['bytes'] for name in ('stdout','stderr','origin')},'process_group':terminal['custody'],'workspace_cleanup':'removed','failure':None,
        'native_observation_sha256':obs_pin,'pdf_origin_map_sha256':map_pin,'pdf_origin_observation_sha256':env_pin}
    _closed(dossier,DOSSIER_KEYS);dossier_pin=_json_put(receipts,dossier)
    member={'id':plan['member_id'],'identity':'new:'+PROFILE,'version':'1','role':'derived-extraction','sha256':streams['stdout']['sha256'],'bytes':len(output),
        'parent':{'member_id':'original','sha256':plan['parent_sha256']},'transform':{'lineage_status':'pinned',**transform,'execution_receipt_artifact_sha256':standard},
        'lineage':[{'kind':'whole-transform-output','output_start':0,'output_end':len(output),'parent_scope':'complete-exact-parent-artifact','claim':'disclosed-transformation-not-raw-byte-equivalence'}]}
    index=_json_put(receipts,{'schema':'twin.source-extraction-custody-index/v1','member_id':plan['member_id'],'standard_receipt_sha256':standard,'dossier_sha256':dossier_pin,'predecessor_sha256':plan['predecessor_sha256']})
    return {'status':'success','failure':None,'archive':archive,'receipts':receipts,'dossier_sha256':dossier_pin,'member':member,'index_sha256':index}


def _complete_pdf_extraction(plan: dict, parent: bytes, observation: dict, artifacts: dict) -> dict:
    """Sole final builder; called once by the internal actual execution flow."""
    return _project_completed_bundle(plan,parent,observation,artifacts)


def verify_pdf_extraction_bundle(plan: dict, parent: bytes, result: dict) -> None:
    """Replay complete public consistency only; never acquire, approve or deposit."""
    _closed(result,{'status','failure','archive','receipts','dossier_sha256','member','index_sha256'})
    dossier=sm._json(_raw(result['receipts'],result['dossier_sha256']));_closed(dossier,DOSSIER_KEYS)
    observation=sm._json(_raw(result['archive'],dossier['native_observation_sha256']))
    expected=_project_completed_bundle(plan,parent,observation,result['archive'])
    for key in ('status','failure','dossier_sha256','member','index_sha256'):
        if result[key]!=expected[key]: raise PdfBridgeHold('complete PDF bundle binding differs')
    for pin,raw in expected['receipts'].items():
        if _raw(result['receipts'],pin)!=raw: raise PdfBridgeHold('PDF receipt/map/envelope/index differs')


def _failed_pdf_extraction(plan: dict, parent: bytes, run: dict, observation: dict, artifacts: dict, workspace_cleanup: str) -> dict:
    """Retain bounded failure evidence without a successful receipt/member/index."""
    archive=dict(plan['archive']);archive.update(artifacts);_put(archive,parent)
    pin=_json_put(archive,observation)
    config,closure=_validate_plan(plan,parent)
    streams={name:{'sha256':_put(archive,run[name]),'bytes':len(run[name])} for name in ('stdout','stderr','origin')}
    dossier={'schema':'twin.source-extraction-execution/v3','purpose':plan['purpose'],'profile':PROFILE,
        'disposition':'failure','relation':'new-execution-from-identical-frozen-raw','predecessor_sha256':plan['predecessor_sha256'],
        'parent_sha256':plan['parent_sha256'],'parent_bytes':len(parent),'output_sha256':streams['stdout']['sha256'],'output_bytes':len(run['stdout']),
        'standard_receipt_sha256':None,'identity':'pdf-text-xpdf-origin','version':'2',
        'configuration_sha256':plan['configuration_sha256'],'implementation_artifact_sha256':plan['implementation_artifact_sha256'],
        'invocation_sha256':_json_put(archive,{'schema':'twin.source-extraction-invocation/v1','argv':observation['spec']['argv'],'cwd':observation['spec']['cwd'],'environment':observation['spec']['environment'],'stdin':'OWNED-EOF-PIPE'}),
        'runtime_observation_sha256':None,'closure_scope':closure['scope'],'platform_closure':closure['platform_closure'],
        'started_at':run['started_at'],'ended_at':run['ended_at'],'elapsed_seconds':run['elapsed_seconds'],'exit_code':run['exit_code'],
        'stdout':streams['stdout'],'stderr':streams['stderr'],'origin':streams['origin'],'streams_complete':run['streams_complete'],
        'observed_bytes_lower_bound':run['observed_bytes_lower_bound'],'process_group':run['process_group'],'workspace_cleanup':workspace_cleanup,
        'failure':run['failure'] or 'native-completion-unestablished','native_observation_sha256':pin,
        'pdf_origin_map_sha256':None,'pdf_origin_observation_sha256':None}
    _closed(dossier,DOSSIER_KEYS)
    receipts: dict[str,bytes]={};dossier_pin=_json_put(receipts,dossier)
    return {'status':'failure','failure':dossier['failure'],'archive':archive,'receipts':receipts,'dossier_sha256':dossier_pin}
