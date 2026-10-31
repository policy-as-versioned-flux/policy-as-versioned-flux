"""Wholly synthetic TEST_ONLY migration, no private sources or real PDF tools."""
import json

import pytest

from twin import source_metadata as sm
from twin import source_metadata_migration as migration
from twin import source_native_observation as native


def retained_legacy(optional=None):
    entry = {'id': 'TEST_ONLY-capture', 'url': 'https://example.invalid/raw',
        'final_url': 'https://example.invalid/raw', 'status': 200,
        'at_utc': '2026-01-01T01:02:03Z', 'bytes': 4, 'sha256': sm.sha256(b'raw\n'),
        'path': 'TEST_ONLY-retained', 'headers': {'Content-Type': 'text/plain'},
        'derived_text': {'bytes': 4, 'path': 'TEST_ONLY-old', 'sha256': sm.sha256(b'raw\n')},
        'kind': 'TEST_ONLY-http', 'method': 'TEST_ONLY-retain',
        'routing_reason': 'TEST_ONLY', 'timeout_seconds': 30}
    if optional is not None:
        for key in set(entry) - {'id','url','final_url','status','at_utc','bytes','sha256','path','headers','derived_text'}:
            del entry[key]
        entry.update(optional)
    raw = sm.canonical([entry]); pin = sm.sha256(raw)
    contract = sm.canonical({'schema':'twin.source-legacy-transport-contract/v1', 'purpose':'TEST_ONLY',
        'legacy_kind':'TEST_ONLY-http', 'legacy_method':'TEST_ONLY-retain', 'acquisition_kind':'TEST_ONLY-fixture'})
    config = {'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY',
              'transport_contract_sha256':sm.sha256(contract)}
    acq = {'id':entry['id'],'kind':'TEST_ONLY-fixture','requested_url':entry['url'],
        'final_url':entry['final_url'],'response_status':entry['status'],'captured_at':entry['at_utc'],
        'body_bytes':entry['bytes'],'body_sha256':entry['sha256'],
        'receipt_artifact_sha256':pin,'receipt_entry_pointer':'/0'}
    artifacts = {pin:raw,sm.sha256(contract):contract}
    adaptation = migration.describe_legacy_adaptation(acq, config)
    artifacts[sm.sha256(adaptation)] = adaptation
    return entry, acq, artifacts, config


def test_truthful_legacy_aliases_preserve_original_and_stock_stays_strict():
    _, acq, artifacts, config = retained_legacy()
    original = artifacts[acq['receipt_artifact_sha256']]
    migration.retained_legacy_receipt_adapter(acq, artifacts, {'purpose':'TEST_ONLY'}, layout_config=config)
    assert artifacts[acq['receipt_artifact_sha256']] == original
    with pytest.raises(ValueError):
        sm.retained_receipt_adapter(acq, artifacts, {'purpose':'TEST_ONLY'})

@pytest.mark.parametrize('profile,raw,expected', [
    ('utf8-identity/1', b'\xef\xbb\xbfA\r\nB\n', b'\xef\xbb\xbfA\r\nB\n'),
    ('html-text-utf8/1', b'<p>A</p><p>B</p>', b'\nA\n\nB\n')])
def test_actual_fixed_child_retains_exact_execution(profile, raw, expected):
    plan = migration.prepare_extraction_plan(profile, raw, purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY predecessor'), member_id='TEST_ONLY-new')
    result = migration.execute_new_extraction(plan, raw)
    assert result['status'] == 'success', result.get('failure')
    assert result['archive'][sm.sha256(expected)] == expected
    dossier = sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['exit_code'] == 0 and dossier['stdout']['sha256'] == sm.sha256(expected)
    assert dossier['closure_scope'] == 'TEST_ONLY-process-file-closure/v1'
    assert dossier['platform_closure'] == 'UNESTABLISHED'
    assert result['member']['parent']['sha256'] == sm.sha256(raw)
    if profile.startswith('html'):
        syntax = sm._json(result['receipts'][dossier['generated_syntax_sha256']])
        assert [(r['start_byte'],r['end_byte']) for r in syntax['ranges']] == [(0,1),(2,3),(3,4),(5,6)]


def migrated_fixture(raw=b'<p>A</p><p>B</p>', text='A', start=1, end=2):
    from test_source_metadata import fixture_import
    manifest, archive, receipts, old = fixture_import()
    plan = migration.prepare_extraction_plan('html-text-utf8/1', raw, purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY predecessor'),member_id='TEST_ONLY-new')
    result = migration.execute_new_extraction(plan, raw)
    assert result['status'] == 'success'
    archive.update(result['archive']); receipts.update(result['receipts'])
    original = manifest['members']['original']
    original.update(sha256=sm.sha256(raw),bytes=len(raw))
    manifest['members'].pop('extraction')
    manifest['members']['TEST_ONLY-new'] = result['member']
    manifest['members']['qualifier']['support_members'][0]['sha256'] = sm.sha256(raw)
    acq = manifest['acquisitions']['fixture-acq']
    acq.update(body_sha256=sm.sha256(raw),body_bytes=len(raw))
    receipt = sm.canonical({k:v for k,v in acq.items() if k not in ('receipt_artifact_sha256','receipt_entry_pointer')})
    acq['receipt_artifact_sha256'] = sm.sha256(receipt); receipts[sm.sha256(receipt)] = receipt
    witness = {'member_id':'TEST_ONLY-new','member_sha256':result['member']['sha256'],
        'start_byte':start,'end_byte':end,'text_utf8':text}
    manifest['observations'] = {}
    manifest['publication'] = {'precision':'unknown','value':None,'basis':'unestablished','observation_id':None,
        'assertion_origin':'unestablished','qualification':'TEST_ONLY no publication assertion'}
    manifest['statement'] = {'text':text,'origin_role':'publisher-quotation','witness':witness}
    manifest['visible_excerpts'] = [{'id':'TEST_ONLY-visible','origin_role':'publisher-quotation','witness':dict(witness)}]
    manifest['bounded_review']['reviewed_member_ids'] = list(manifest['members'])
    policy = json.loads(old.description)['policy']
    transform = result['member']['transform']
    policy['allowed_transforms'] = [{k:transform[k] for k in ('identity','version','implementation_artifact_sha256','configuration_sha256')}]
    layout = {'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None}
    execution = {'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY',
                 'index_sha256s':[result['index_sha256']]}
    authority = migration.freeze_migration_authority('TEST_ONLY-parent','TEST_ONLY-migration','1',
        sm.sha256(sm.canonical(policy)),policy=policy,layout_config=layout,execution_contract=execution)
    return manifest, archive, receipts, authority, result, plan


def test_actual_child_acquisition_resolves_and_generated_html_crossing_is_held():
    manifest, archive, receipts, authority, _, _ = migrated_fixture()
    store = sm.MetadataStore(purpose='TEST_ONLY')
    raw = sm.canonical(manifest)
    acquired = store.acquire('TEST_ONLY-migrated', raw, archive, receipts, sm.sha256(raw), authority)
    assert store.resolve(**acquired.binding).public['statement']['text'] == 'A'
    manifest['statement']['text'] = 'A\n\nB'
    manifest['statement']['witness'].update(text_utf8='A\n\nB',end_byte=5)
    with pytest.raises(ValueError, match='generated|syntax'):
        changed = sm.canonical(manifest)
        store.acquire('TEST_ONLY-crossing',changed,archive,receipts,sm.sha256(changed),authority)


def test_pdf_profile_executes_only_a_truthful_synthetic_converter_fixture(tmp_path):
    import sys
    from pathlib import Path
    tool = tmp_path/'TEST_ONLY-pdftotext'
    tool.write_text('#!' + str(Path(sys.executable).resolve()) + ' -ISB\n' + '''import sys
from pathlib import Path
assert sys.argv[1] == '-cfg'
assert sys.argv[3:8] == ['-enc','UTF-8','-eol','unix','-nopgbrk']
assert sys.argv[-1] == '-'
assert Path(sys.argv[-2]).read_bytes() == b'%PDF-TEST_ONLY-not-a-real-PDF'
sys.stdout.buffer.write(b'TEST_ONLY PDF fixture text\\n')
''')
    tool.chmod(0o700)
    raw = b'%PDF-TEST_ONLY-not-a-real-PDF'
    plan = migration.prepare_pdf_extraction_plan(raw,purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY predecessor'),member_id='TEST_ONLY-pdf',
        executable=str(tool),configuration=b'# TEST_ONLY fixed converter config\n',
        tool_version='TEST_ONLY-fixed-converter/1',version_observation=b'TEST_ONLY version observation',
        retained_files={str(tool):tool.read_bytes(),str(Path(sys.executable).resolve()):Path(sys.executable).resolve().read_bytes()})
    result = migration.execute_new_extraction(plan,raw)
    assert result['status'] == 'success',result.get('failure')
    assert result['archive'][sm.sha256(b'TEST_ONLY PDF fixture text\n')] == b'TEST_ONLY PDF fixture text\n'
    dossier = sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['closure_scope'] == 'TEST_ONLY-native-converter-fixture/v1'
    assert dossier['platform_closure'] == 'UNESTABLISHED'


@pytest.mark.parametrize('optional',[
    {'derived_text_alternate':{'bytes':4,'extractor':'TEST_ONLY','path':'TEST_ONLY-alt','sha256':'TEST_ONLY'},
     'error':None,'extractor':{'command':'TEST_ONLY-not-executed','exit_code':0,'stderr':''}},
    {'error':None,'extractor':{'command':'TEST_ONLY-not-executed','exit_code':0,'stderr':''}},
    {'error':None},
    {'ext':'txt','family':'TEST_ONLY','initial_derived_text':{'bytes':4,'path':'TEST_ONLY-old','sha256':'TEST_ONLY'},
     'kind':'TEST_ONLY-http','method':'TEST_ONLY-retain','slot':0,
     'text_extraction':{'exit':0,'stderr':''},'timeout_seconds':30},
    {'ext':'txt','family':'TEST_ONLY','kind':'TEST_ONLY-http','method':'TEST_ONLY-retain','slot':0,'timeout_seconds':30},
    {'family':'TEST_ONLY','kind':'TEST_ONLY-http','method':'TEST_ONLY-retain','slot':0,'timeout_seconds':30},
    {'kind':'TEST_ONLY-http','method':'TEST_ONLY-retain','routing_reason':'TEST_ONLY','timeout_seconds':30,
     'transform':{'command':'TEST_ONLY-not-executed','exit':0}},
    {'kind':'TEST_ONLY-http','method':'TEST_ONLY-retain','routing_reason':'TEST_ONLY','timeout_seconds':30}])
def test_all_frozen_legacy_grammars_preserve_old_unestablished_metadata(optional):
    _,acq,artifacts,config = retained_legacy(optional)
    if 'kind' not in optional:
        with pytest.raises(migration.MetadataMigrationHold,match='unmappable-transport'):
            migration.retained_legacy_receipt_adapter(acq,artifacts,{'purpose':'TEST_ONLY'},layout_config=config)
    else:
        migration.retained_legacy_receipt_adapter(acq,artifacts,{'purpose':'TEST_ONLY'},layout_config=config)
    assert 'TEST_ONLY-not-executed' not in acq.values()


@pytest.mark.parametrize('change', ['bool','missing','unknown','nested-unknown','nested-type','header-type',
    'pointer','pointer-leading-zero','pointer-negative','pointer-nested','timestamp','status','url','hash','adaptation','transport'])
def test_legacy_invalid_or_unmappable_facts_never_gain_new_capture(change):
    entry,acq,artifacts,config = retained_legacy()
    if change=='bool': entry['bytes']=True
    elif change=='missing': del entry['final_url']
    elif change=='unknown': entry['unexpected']='TEST_ONLY'
    elif change=='nested-unknown': entry['derived_text']['version']='invented'
    elif change=='nested-type': entry['derived_text']['bytes']='4'
    elif change=='header-type': entry['headers']['Content-Type']=7
    elif change.startswith('pointer'):
        acq['receipt_entry_pointer']={'pointer':'/9','pointer-leading-zero':'/00','pointer-negative':'/-1','pointer-nested':'/0/id'}[change]
    elif change=='timestamp': entry['at_utc']='2026-01-01T01:02:03'
    elif change=='status': entry['status']=500
    elif change=='url': entry['final_url']='https://example.invalid/changed'
    elif change=='hash': entry['sha256']='0'*64
    elif change=='adaptation':
        artifacts.pop(sm.sha256(migration.describe_legacy_adaptation(acq,config)))
    else: config['transport_contract_sha256']=None
    if change not in ('adaptation','transport') and not change.startswith('pointer'):
        raw=sm.canonical([entry]); acq['receipt_artifact_sha256']=sm.sha256(raw); artifacts[sm.sha256(raw)]=raw
    with pytest.raises(ValueError):
        migration.retained_legacy_receipt_adapter(acq,artifacts,{'purpose':'TEST_ONLY'},layout_config=config)


@pytest.mark.parametrize('nested', [
    {'bytes':4,'path':'TEST_ONLY','sha256':'TEST_ONLY'},
    {'bytes':4,'path':'TEST_ONLY','sha256':'TEST_ONLY','method':'TEST_ONLY-old-unestablished'},
    {'bytes':4,'path':'TEST_ONLY','sha256':'TEST_ONLY','command':'TEST_ONLY-old-unexecuted','encoding':'UTF-8','exit':0}])
def test_all_derived_text_shapes_preserve_original_without_inventing_old_pins(nested):
    entry,acq,artifacts,config=retained_legacy()
    entry['derived_text']=nested
    raw=sm.canonical([entry]); acq['receipt_artifact_sha256']=sm.sha256(raw); artifacts[sm.sha256(raw)]=raw
    adaptation=migration.describe_legacy_adaptation(acq,config);artifacts[sm.sha256(adaptation)]=adaptation
    migration.retained_legacy_receipt_adapter(acq,artifacts,{'purpose':'TEST_ONLY'},layout_config=config)
    assert 'implementation_artifact_sha256' not in sm._json(raw)[0]['derived_text']


@pytest.mark.parametrize('behavior,status,exit_code',[('diagnostic','success',0),('nonzero','failure',7)])
def test_actual_zero_exit_diagnostic_and_nonzero_are_distinct(behavior,status,exit_code):
    plan=migration.prepare_extraction_plan('utf8-identity/1',b'TEST_ONLY output\n',purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY',test_only_behavior=behavior)
    result=migration.execute_new_extraction(plan,b'TEST_ONLY output\n')
    dossier=sm._json(result['receipts'][result['dossier_sha256']])
    assert result['status']==status and dossier['exit_code']==exit_code
    assert result['archive'][dossier['stderr']['sha256']]==b'TEST_ONLY fixed diagnostic\n'
    assert ('index_sha256' in result)==(status=='success')
    assert (dossier['standard_receipt_sha256'] is not None)==(status=='success')


@pytest.mark.parametrize('raw',[b'\xff',b''])
def test_actual_invalid_text_or_empty_unrepresentable_output_is_retained_failure(raw):
    plan=migration.prepare_extraction_plan('utf8-identity/1',raw,purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY')
    result=migration.execute_new_extraction(plan,raw)
    assert result['status']=='failure' and 'index_sha256' not in result
    dossier=sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['disposition']=='failure' and dossier['standard_receipt_sha256'] is None
    assert sm._artifact(result['archive'],dossier['stderr']['sha256']) is not None


def test_changed_raw_and_partial_actual_closure_reject_before_child(monkeypatch):
    plan=migration.prepare_extraction_plan('utf8-identity/1',b'A',purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY')
    def forbidden(*args,**kwargs):
        raise AssertionError('no child may run')
    monkeypatch.setattr(migration.subprocess,'Popen',forbidden)
    monkeypatch.setattr(native,'_acquire_actual',forbidden)
    with pytest.raises(ValueError,match='parent'):
        migration.execute_new_extraction(plan,b'B')
    plan['purpose']='actual'
    config=sm._json(plan['archive'][plan['configuration_sha256']]);config['purpose']='actual'
    raw=sm.canonical(config);plan['configuration_sha256']=sm.sha256(raw);plan['archive'][sm.sha256(raw)]=raw
    closure=sm._json(plan['archive'][plan['implementation_artifact_sha256']]);closure['purpose']='actual'
    raw=sm.canonical(closure);plan['implementation_artifact_sha256']=sm.sha256(raw);plan['archive'][sm.sha256(raw)]=raw
    with pytest.raises(ValueError,match='^independently selected actual host authority required$'):
        migration.execute_new_extraction(plan,b'A')


@pytest.mark.parametrize('path',['observation','statement','excerpt'])
def test_every_publisher_quotation_path_excludes_generated_syntax(path):
    manifest,archive,receipts,authority,_,_=migrated_fixture()
    crossing={'member_id':'TEST_ONLY-new','member_sha256':manifest['members']['TEST_ONLY-new']['sha256'],
              'start_byte':1,'end_byte':5,'text_utf8':'A\n\nB'}
    if path=='statement': manifest['statement'].update(text='A\n\nB',witness=crossing)
    elif path=='excerpt': manifest['visible_excerpts'][0]['witness']=crossing
    else:
        manifest['observations']={'TEST_ONLY':{'id':'TEST_ONLY','observed_kind':'other','literal_value':'A\n\nB',
            'metadata_key':None,'normalization':'none','witness':crossing}}
    policy=sm._json(authority.description)['policy']
    # This was the published seam: byte/whole-transform checks alone accept this crossing.
    sm.retained_source_checker(manifest,archive,receipts,policy)
    with pytest.raises(ValueError,match='generated syntax'):
        raw=sm.canonical(manifest)
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-cross',raw,archive,receipts,sm.sha256(raw),authority)


def test_original_html_data_newline_is_not_mislabelled_as_generated():
    manifest,archive,receipts,authority,_,_=migrated_fixture(b'<p>A\nB</p>','A\nB',1,4)
    raw=sm.canonical(manifest);store=sm.MetadataStore(purpose='TEST_ONLY')
    acquired=store.acquire('TEST_ONLY-data-LF',raw,archive,receipts,sm.sha256(raw),authority)
    assert store.resolve(**acquired.binding).public['statement']['text']=='A\nB'


@pytest.mark.parametrize('mutation',['missing-range','duplicate','wrong-byte','wrong-parent'])
def test_pinned_but_false_separator_map_cannot_self_attest_completeness(mutation):
    manifest,archive,receipts,old,result,_=migrated_fixture()
    index=sm._json(receipts[result['index_sha256']]);dossier=sm._json(receipts[index['dossier_sha256']])
    syntax=sm._json(receipts[dossier['generated_syntax_sha256']])
    if mutation=='missing-range': syntax['ranges'].pop()
    elif mutation=='duplicate': syntax['ranges'].append(syntax['ranges'][-1])
    elif mutation=='wrong-byte': syntax['ranges'][0]['text_utf8']='X'
    else: syntax['parent_sha256']='0'*64
    raw=sm.canonical(syntax);dossier['generated_syntax_sha256']=sm.sha256(raw);receipts[sm.sha256(raw)]=raw
    raw=sm.canonical(dossier);index['dossier_sha256']=sm.sha256(raw);receipts[sm.sha256(raw)]=raw
    receipts.pop(result['index_sha256']);raw=sm.canonical(index);pin=sm.sha256(raw);receipts[pin]=raw
    policy=sm._json(old.description)['policy']
    authority=migration.freeze_migration_authority('TEST_ONLY-parent','TEST_ONLY-mutated-index','1',
        sm.sha256(sm.canonical(policy)),policy=policy,
        layout_config={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None},
        execution_contract={'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY','index_sha256s':[pin]})
    with pytest.raises(ValueError,match='syntax'):
        raw=sm.canonical(manifest)
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-false-map',raw,archive,receipts,sm.sha256(raw),authority)


def test_clone_defaults_are_independent_and_cannot_cross_enrol_runs():
    a,aa,ar,authority_a,_,_=migrated_fixture()
    b,ba,br,authority_b,_,_=migrated_fixture()
    stores=[]
    for manifest,archive,receipts,authority in [(a,aa,ar,authority_a),(b,ba,br,authority_b)]:
        store=sm.MetadataStore(purpose='TEST_ONLY');raw=sm.canonical(manifest)
        acquired=store.acquire('TEST_ONLY-isolated',raw,archive,receipts,sm.sha256(raw),authority)
        stores.append((store,acquired))
    with pytest.raises(ValueError,match='observed custody index'):
        raw=sm.canonical(a)
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-cross',raw,aa,ar,sm.sha256(raw),authority_b)
    before_b=authority_b.description
    authority_a.source_checker.__kwdefaults__['execution_contract']['index_sha256s'].append('0'*64)
    with pytest.raises(ValueError,match='helper|authority'):
        authority_a.verify()
    assert authority_b.description==before_b
    assert stores[1][0].resolve(**stores[1][1].binding).public['statement']['text']=='A'


def test_forged_complete_declaration_and_arbitrary_platform_files_do_not_mint_actual_closure(tmp_path,monkeypatch):
    plan=migration.prepare_extraction_plan('utf8-identity/1',b'A',purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY')
    plan['purpose']='actual'
    config=sm._json(plan['archive'][plan['configuration_sha256']]);config['purpose']='actual'
    raw=sm.canonical(config);plan['configuration_sha256']=sm.sha256(raw);plan['archive'][sm.sha256(raw)]=raw
    platform=tmp_path/'TEST_ONLY-arbitrary-not-an-OS-closure';platform.write_bytes(b'TEST_ONLY arbitrary')
    closure=sm._json(plan['archive'][plan['implementation_artifact_sha256']])
    closure.update(purpose='actual',scope='complete-approved-runtime/v1',platform_closure='retained-exact-platform-files',
        platform_files=[{'path':str(platform.resolve()),'sha256':sm.sha256(platform.read_bytes()),'bytes':len(platform.read_bytes())}])
    plan['archive'][sm.sha256(platform.read_bytes())]=platform.read_bytes()
    raw=sm.canonical(closure);plan['implementation_artifact_sha256']=sm.sha256(raw);plan['archive'][sm.sha256(raw)]=raw
    def forbidden(*args,**kwargs):
        raise AssertionError('forged declaration must reject before actual process')
    monkeypatch.setattr(migration.subprocess,'Popen',forbidden)
    monkeypatch.setattr(native,'_acquire_actual',forbidden)
    with pytest.raises(ValueError,match='^independently selected actual host authority required$'):
        migration.execute_new_extraction(plan,b'A')


@pytest.mark.parametrize('failure',['timeout','stderr-overflow','stdout-overflow'])
def test_os_boundary_timeout_and_stream_caps_reap_without_success(monkeypatch,failure):
    import os
    import signal
    plan=migration.prepare_extraction_plan('utf8-identity/1',b'A',purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY')
    actual_read=os.read; signals=[]; instances=[]
    class FakeProcess:
        def __init__(self,*args,**kwargs):
            self.pid=123456789;self.returncode=None;self.waits=0;self.writers=[]
            for name in ('stdout','stderr'):
                r,w=os.pipe();os.write(w,b'x');self.writers.append(w)
                setattr(self,name,os.fdopen(r,'rb',buffering=0))
            instances.append(self)
        def wait(self,timeout):
            self.waits+=1
            assert signals == [(self.pid,signal.SIGTERM),(self.pid,signal.SIGKILL)]
            for writer in self.writers:os.close(writer)
            self.writers=[];self.returncode=-9
            return self.returncode
    monkeypatch.setattr(migration.subprocess,'Popen',FakeProcess)
    def own_group(pid,sig):
        if sig:
            assert not instances[0].waits, 'no destructive signal after direct-child reap'
            signals.append((pid,sig))
        elif instances[0].waits:
            raise ProcessLookupError('TEST_ONLY group absence')
    monkeypatch.setattr(migration.os,'killpg',own_group)
    monkeypatch.setattr(migration.os,'waitid',lambda *args:None)
    if failure=='timeout':
        clock=iter([0.,100.,1000.])
        monkeypatch.setattr(migration.time,'monotonic',lambda:next(clock,1000.))
    else:
        selected=failure.split('-')[0]
        def synthetic_read(fd,count):
            if instances and fd==getattr(instances[0],selected).fileno():return b'X'*count
            return actual_read(fd,count)
        monkeypatch.setattr(migration.os,'read',synthetic_read)
    result=migration.execute_new_extraction(plan,b'A')
    assert result['status']=='failure' and result['failure']==failure and 'index_sha256' not in result
    assert [sig for _,sig in signals]==[signal.SIGTERM,signal.SIGKILL]
    dossier=sm._json(result['receipts'][result['dossier_sha256']])
    assert instances[0].waits==1 and instances[0].stdout.closed and instances[0].stderr.closed
    assert dossier['process_group']['direct_child_reaped'] is True
    assert dossier['process_group']['absence_verified'] is True
    assert not dossier['streams_complete'] and dossier['standard_receipt_sha256'] is None
    if failure!='timeout':
        stream=failure.split('-')[0]
        assert dossier[stream]['bytes']==migration.PROFILES['utf8-identity/1'][stream+'_bytes']
        assert dossier['observed_bytes_lower_bound'][stream]>dossier[stream]['bytes']


def test_cleanup_failure_keeps_actual_output_and_no_success(monkeypatch):
    from pathlib import Path
    plan=migration.prepare_extraction_plan('utf8-identity/1',b'A',purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY')
    real_cleanup=migration.tempfile.TemporaryDirectory.cleanup;owned=[]
    def cleanup(self):
        owned.append(self.name);real_cleanup(self)
        raise OSError('TEST_ONLY simulated cleanup report failure')
    monkeypatch.setattr(migration.tempfile.TemporaryDirectory,'cleanup',cleanup)
    result=migration.execute_new_extraction(plan,b'A')
    assert result['status']=='failure' and result['failure']=='cleanup-failed'
    assert result['archive'][sm.sha256(b'A')]==b'A'
    assert owned and all(not Path(name).exists() for name in owned)
    dossier=sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['exit_code']==0 and dossier['standard_receipt_sha256'] is None


def test_post_run_evidence_failure_retains_real_stream_observations(monkeypatch):
    from pathlib import Path
    plan=migration.prepare_extraction_plan('utf8-identity/1',b'A',purpose='TEST_ONLY',
        predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY')
    real_popen=migration.subprocess.Popen
    class CorruptRuntimeObservation:
        def __init__(self,argv,*args,**kwargs):
            self.process=real_popen(argv,*args,**kwargs);self.runtime=argv[-1]
        def __getattr__(self,name):return getattr(self.process,name)
        def wait(self,timeout):
            result=self.process.wait(timeout=timeout)
            Path(self.runtime).write_bytes(b'{TEST_ONLY broken observation')
            return result
    monkeypatch.setattr(migration.subprocess,'Popen',CorruptRuntimeObservation)
    result=migration.execute_new_extraction(plan,b'A')
    assert result['status']=='failure' and result['failure']=='post-run-evidence:ValueError'
    dossier=sm._json(result['receipts'][result['dossier_sha256']])
    assert dossier['exit_code']==0 and dossier['stdout']=={'sha256':sm.sha256(b'A'),'bytes':1}
    assert 'index_sha256' not in result


@pytest.mark.parametrize('artifact',['index','dossier','standard','syntax','stdout','stderr','closure','config','invocation','runtime','driver'])
def test_required_execution_artifacts_are_not_optional(artifact):
    manifest,archive,receipts,authority,result,_=migrated_fixture()
    dossier=sm._json(receipts[result['dossier_sha256']])
    if artifact in ('index','dossier','standard','syntax'):
        pin={'index':result['index_sha256'],'dossier':result['dossier_sha256'],
             'standard':dossier['standard_receipt_sha256'],'syntax':dossier['generated_syntax_sha256']}[artifact]
        del receipts[pin]
    else:
        pin={'stdout':dossier['stdout']['sha256'],'stderr':dossier['stderr']['sha256'],
             'closure':dossier['implementation_artifact_sha256'],'config':dossier['configuration_sha256'],
             'invocation':dossier['invocation_sha256'],'runtime':dossier['runtime_observation_sha256']}.get(artifact)
        if artifact=='driver':
            closure=sm._json(archive[dossier['implementation_artifact_sha256']]);pin=closure['driver_files'][0]['sha256']
        del archive[pin]
    with pytest.raises(ValueError):
        raw=sm.canonical(manifest)
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-missing',raw,archive,receipts,sm.sha256(raw),authority)


def test_extra_standard_receipt_fields_still_fail_the_stock_contract():
    from test_source_metadata import fixture_import
    manifest,archive,receipts,authority=fixture_import()
    transform=manifest['members']['extraction']['transform']
    execution=sm._json(receipts[transform['execution_receipt_artifact_sha256']]);execution['command']='TEST_ONLY richer evidence belongs elsewhere'
    raw=sm.canonical(execution);transform['execution_receipt_artifact_sha256']=sm.sha256(raw);receipts[sm.sha256(raw)]=raw
    with pytest.raises(ValueError,match='execution receipt differs'):
        raw=sm.canonical(manifest)
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-extra-field',raw,archive,receipts,sm.sha256(raw),authority)


def test_old_recipe_receipt_and_unknown_lineage_cannot_be_relabelled_as_new_execution():
    from test_source_metadata import fixture_import
    manifest,archive,receipts,old=fixture_import();policy=sm._json(old.description)['policy']
    authority=migration.freeze_migration_authority('TEST_ONLY-parent','TEST_ONLY-no-run','1',sm.sha256(sm.canonical(policy)),
        policy=policy,layout_config={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None},
        execution_contract={'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY','index_sha256s':[]})
    with pytest.raises(ValueError,match='observed custody index'):
        raw=sm.canonical(manifest)
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-old',raw,archive,receipts,sm.sha256(raw),authority)


@pytest.mark.parametrize('name',['_bind','_checked_execution','_syntax_check','_execution_contract'])
def test_migration_validator_binder_and_dispatch_drift_reject_all_store_paths(name,monkeypatch):
    manifest,archive,receipts,authority,_,_=migrated_fixture()
    raw=sm.canonical(manifest);store=sm.MetadataStore(purpose='TEST_ONLY')
    acquired=store.acquire('TEST_ONLY-before',raw,archive,receipts,sm.sha256(raw),authority)
    def replacement(*args,**kwargs):
        return None
    monkeypatch.setattr(migration,name,replacement)
    for action in (authority.verify,lambda:store.resolve(**acquired.binding),
                   lambda:store.acquire('TEST_ONLY-after',raw,archive,receipts,sm.sha256(raw),authority)):
        with pytest.raises(ValueError,match='helper|binding'):
            action()


def test_callback_globals_copy_cannot_replace_the_actual_protected_namespace():
    import types
    manifest,archive,receipts,authority,_,_=migrated_fixture()
    original=authority.source_checker
    clone=types.FunctionType(original.__code__,dict(original.__globals__),original.__name__,original.__defaults__)
    clone.__kwdefaults__=original.__kwdefaults__
    policy=sm._json(authority.description)['policy']
    with pytest.raises(ValueError,match='protected helper namespace'):
        sm.MetadataAuthority.freeze('TEST_ONLY-parent','TEST_ONLY-copy','1',sm.sha256(sm.canonical(policy)),
            authority.acquire_adapter,clone,policy=policy,helper_modules=(migration,))


def test_external_configuration_mutation_does_not_mutate_bound_defaults():
    manifest,archive,receipts,old,result,_=migrated_fixture();policy=sm._json(old.description)['policy']
    layout={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None}
    execution={'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY','index_sha256s':[result['index_sha256']]}
    authority=migration.freeze_migration_authority('TEST_ONLY-parent','TEST_ONLY-isolation','1',sm.sha256(sm.canonical(policy)),
        policy=policy,layout_config=layout,execution_contract=execution)
    before=authority.description;execution['index_sha256s'].clear();layout['purpose']='actual'
    authority.verify();assert authority.description==before
    raw=sm.canonical(manifest)
    acquired=sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-isolation',raw,archive,receipts,sm.sha256(raw),authority)
    assert acquired.public['statement']['text']=='A'


def test_alias_output_member_cannot_escape_separator_exclusion():
    import copy
    manifest,archive,receipts,old,result,_=migrated_fixture();policy=sm._json(old.description)['policy']
    alias=copy.deepcopy(result['member']);alias['id']='TEST_ONLY-alias';manifest['members'][alias['id']]=alias
    index=sm._json(receipts[result['index_sha256']]);index['member_id']=alias['id']
    raw=sm.canonical(index);pin=sm.sha256(raw);receipts[pin]=raw
    manifest['bounded_review']['reviewed_member_ids']=list(manifest['members'])
    manifest['statement'].update(text='A\n\nB',witness={'member_id':alias['id'],'member_sha256':alias['sha256'],
        'start_byte':1,'end_byte':5,'text_utf8':'A\n\nB'})
    authority=migration.freeze_migration_authority('TEST_ONLY-parent','TEST_ONLY-alias','1',sm.sha256(sm.canonical(policy)),
        policy=policy,layout_config={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None},
        execution_contract={'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY',
                            'index_sha256s':[result['index_sha256'],pin]})
    with pytest.raises(ValueError,match='generated syntax'):
        raw=sm.canonical(manifest)
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-alias',raw,archive,receipts,sm.sha256(raw),authority)


def test_unsupported_unchanged_text_holds_and_old_artifacts_remain_unchanged():
    manifest,archive,receipts,authority,_,_=migrated_fixture(text='Z')
    old_archive=dict(archive);old_receipts=dict(receipts);raw=sm.canonical(manifest)
    store=sm.MetadataStore(purpose='TEST_ONLY')
    with pytest.raises(ValueError,match='span/bytes'):
        store.acquire('TEST_ONLY-no-support',raw,archive,receipts,sm.sha256(raw),authority)
    assert archive==old_archive and receipts==old_receipts and manifest['statement']['text']=='Z'
    with pytest.raises(ValueError,match='no actual protected'):
        store.resolve('TEST_ONLY-no-support',sm.sha256(raw),authority.digest,'0'*64)


@pytest.mark.parametrize('raw',[b'[{"id":"TEST_ONLY","id":"TEST_ONLY-duplicate"}]',b'not JSON'])
def test_original_legacy_json_is_strict_even_before_mapping(raw):
    _,acq,artifacts,config=retained_legacy();pin=sm.sha256(raw);artifacts[pin]=raw;acq['receipt_artifact_sha256']=pin
    with pytest.raises(ValueError):
        migration.retained_legacy_receipt_adapter(acq,artifacts,{'purpose':'TEST_ONLY'},layout_config=config)


@pytest.mark.parametrize('target',['layout','execution','plan'])
def test_public_trusted_flags_do_not_open_a_bypass(target):
    if target=='plan':
        plan=migration.prepare_extraction_plan('utf8-identity/1',b'A',purpose='TEST_ONLY',
            predecessor_sha256=sm.sha256(b'TEST_ONLY seal'),member_id='TEST_ONLY')
        plan['trusted']=True
        with pytest.raises(ValueError,match='closed'):
            migration.execute_new_extraction(plan,b'A')
    else:
        manifest,archive,receipts,old,result,_=migrated_fixture();policy=sm._json(old.description)['policy']
        layout={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None}
        execution={'schema':'twin.source-migration-execution-contract/v1','purpose':'TEST_ONLY','index_sha256s':[result['index_sha256']]}
        (layout if target=='layout' else execution)['trusted']=True
        with pytest.raises(ValueError,match='closed'):
            migration.freeze_migration_authority('TEST_ONLY-parent','TEST_ONLY-no-flags','1',sm.sha256(sm.canonical(policy)),
                policy=policy,layout_config=layout,execution_contract=execution)


@pytest.mark.parametrize('container,pointer',[('array','/0'),('nested','/captures/0')])
def test_migration_keeps_stock_standardized_entries_at_original_pointers(container,pointer):
    _,acq,artifacts,_=retained_legacy()
    standard={k:v for k,v in acq.items() if k not in ('receipt_artifact_sha256','receipt_entry_pointer')}
    raw=sm.canonical([standard] if container=='array' else {'captures':[standard]})
    acq.update(receipt_artifact_sha256=sm.sha256(raw),receipt_entry_pointer=pointer)
    artifacts[sm.sha256(raw)]=raw
    migration.retained_legacy_receipt_adapter(acq,artifacts,{'purpose':'TEST_ONLY'},
        layout_config={'schema':'twin.source-legacy-layout/v1','purpose':'TEST_ONLY','transport_contract_sha256':None})
