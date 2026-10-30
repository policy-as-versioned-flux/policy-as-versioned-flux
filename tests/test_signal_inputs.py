"""TEST_ONLY source declarations, never fresh reference labels or model outputs."""
from pathlib import Path
import copy
import hashlib
import json

import pytest
import yaml

from twin import fixtures, qualification as q
from twin.model import Overlay
from twin.reference_cases import source_record
from twin.repo import ModelRepo
from twin.signal_inputs import resolve_signal_input
from twin import source_metadata as sm
from test_source_metadata import acquire_fixture, unknown_fixture


WORLD_IDS = ('test-only-access', 'test-only-cloud', 'test-only-compute-budget',
             'test-only-dependency', 'test-only-enforcement', 'test-only-feed',
             'test-only-key', 'test-only-knowledge', 'test-only-platform',
             'test-only-prices', 'test-only-role', 'test-only-sequence',
             'test-only-site', 'test-only-supplier', 'test-only-trade')
LOCAL_IDS = ('test-only-local-cage', 'test-only-local-records', 'test-only-local-revenue',
             'test-only-local-service', 'test-only-local-standing')


@pytest.fixture
def protected_request(tmp_path):
    root = tmp_path / 'TEST_ONLY-computed-model'
    root.mkdir()
    fixtures.git(root, 'init', '-q', '-b', 'main', '--object-format=sha1')
    def put(rel, value):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(value))
    put('world/meta.yaml', {'id': 'test-only-world', 'unit': 'world'})
    for ident in WORLD_IDS:
        put(f'world/components/{ident}.yaml', {'id': ident, 'name': ident,
            'kind': 'activity', 'evolution': 'product', 'visibility': .25})
    fixtures.git(root, 'add', '--', 'world')
    fixtures.git(root, 'commit', '-q', '-m', 'TEST_ONLY world declarations')
    world = fixtures.git(root, 'rev-parse', 'HEAD').strip()
    for org in ('driftwood', 'tuppence', 'ludlow'):
        put(f'orgs/{org}/meta.yaml', {'id': org, 'unit': 'overlay', 'org': org, 'world_ref': world})
        for ident in LOCAL_IDS:
            put(f'orgs/{org}/components/{ident}.yaml', {'id': ident, 'name': f'{org} {ident}',
                'kind': 'activity', 'evolution': 'product', 'visibility': .5,
                'description': 'TEST_ONLY complete original definition, without a target label.',
                'needs': ['test-only-cloud']})
        put(f'orgs/{org}/perspectives/test-only-firm.yaml', {
            'id': 'test-only-firm', 'name': 'TEST_ONLY declared perspective', 'party': 'employer',
            'pays': 'TEST_ONLY firm', 'cash_flow': ['test-only-local-revenue'],
            'ruin': {'insolvency': 'TEST_ONLY cannot meet obligations'},
            'values': {'test-only-local-revenue': {'amount': 100, 'evidence_grade': 3,
                'basis': 'TEST_ONLY published record'}}})
    fixtures.git(root, 'add', '--', 'orgs')
    fixtures.git(root, 'commit', '-q', '-m', 'TEST_ONLY overlays, not observed history')
    repo = ModelRepo.open(root)
    url = 'https://example.invalid/TEST_ONLY/original-bulletin'
    original = b'TEST_ONLY original bulletin.\nAdministrators propose a change; no event has occurred.\n'
    packet = {'statement': 'TEST_ONLY administrators propose a change.', 'source': 'TEST_ONLY bulletin',
        'source_context': {'url': url, 'version': 'TEST_ONLY-original-v1',
            'excerpts': ['Administrators propose a change; no event has occurred.'],
            'publication_date': '2019-01-03', 'event_date': '2019-01-02',
            'as_of': '2019-01-03', 'family': 'TEST_ONLY-bulletin-family',
            'original_sources': {'bulletin': source_record(original, url, 'TEST_ONLY-original-v1')}},
        'signal': {'id': 'test-only-signal', 'date': '2019-01-03',
            'from': {'party': 'TEST_ONLY-publisher', 'kind': 'bulletin', 'name': 'fixture', 'version': 'TEST_ONLY-v1'},
            'provenance': {'url': url, 'date': '2019-01-03'}}}
    def request(org='driftwood'):
        party = yaml.safe_dump({'id': org, 'appetite': {'pricing_threshold': 3}}).encode()
        overlay = Overlay.load(repo, org, pricing_threshold=3)
        return {'repo': repo, 'org': org, 'source_packet': q.canonical(packet),
            'source_pin': hashlib.sha256(q.canonical(packet)).hexdigest(),
            'party_bytes': party, 'party_pin': hashlib.sha256(party).hexdigest(),
            'policy': {'issuer': 'TEST_ONLY-protected-resolver', 'domain': 'TEST_ONLY-source-task',
                'capability': 'TEST_ONLY-primary-subject', 'frame': 'TEST_ONLY-current-model-relevance',
                'model_as_of': '2026-10-30', 'model_pins': {'model_repo': repo.pin.as_dict(),
                    'overlay': overlay.ref.as_dict(), 'world': overlay.world.ref.as_dict()}},
            'test_only': q.TEST_ONLY_MECHANICS}
    return request


@pytest.mark.parametrize('org', ['driftwood', 'tuppence', 'ludlow'])
def test_full_source_input_and_actual_host_share_all_twenty_original_definitions(protected_request, org):
    resolved = resolve_signal_input(**protected_request(org))
    payload = resolved.payload
    assert set(payload) == {'statement', 'source', 'source_context', 'model_context', 'candidates'}
    assert [item['id'] for item in payload['candidates']] == list(WORLD_IDS + LOCAL_IDS)
    assert payload['candidates'][0]['definition'] == {'id': 'test-only-access',
        'name': 'test-only-access', 'kind': 'activity', 'evolution': 'product', 'visibility': .25}
    assert payload['candidates'][-2]['definition']['needs'] == ['test-only-cloud']
    assert payload['source_context']['as_of'] == '2019-01-03'
    assert payload['model_context']['as_of'] == '2026-10-30'
    host = resolved.host_inputs().resolve('test-only-signal')
    assert host['input'] == payload
    assert host['context']['eligible_components'] == list(WORLD_IDS + LOCAL_IDS)
    assert 'component' not in host['context']
    assert host['source']['identity'] == 'TEST_ONLY-bulletin-family'


@pytest.mark.parametrize('forgery', ['source-pin', 'party-pin', 'world-pin', 'party-org'])
def test_independent_packet_party_and_model_pins_refuse_forged_closures(protected_request, forgery):
    request = protected_request()
    if forgery == 'source-pin':
        request['source_pin'] = '0' * 64
    elif forgery == 'party-pin':
        request['party_pin'] = '0' * 64
    elif forgery == 'world-pin':
        request['policy']['model_pins']['world']['commit'] = '0' * 40
    else:
        request['party_bytes'] = b'id: tuppence\nappetite: {pricing_threshold: 3}\n'
        request['party_pin'] = hashlib.sha256(request['party_bytes']).hexdigest()
    with pytest.raises(ValueError, match='pin|party|closure'):
        resolve_signal_input(**request)


@pytest.mark.parametrize('forgery', ['original-hash', 'original-version', 'excerpt',
    'task-date', 'publication-date', 'signal-date', 'provenance-url'])
def test_pinned_packet_must_still_have_valid_original_witnesses_and_source_dates(protected_request, forgery):
    request = protected_request()
    packet = json.loads(request['source_packet'])
    source = packet['source_context']
    if forgery == 'original-hash':
        source['original_sources']['bulletin']['sha256'] = '0' * 64
    elif forgery == 'original-version':
        source['original_sources']['bulletin']['version'] = 'foreign-version'
    elif forgery == 'excerpt':
        source['excerpts'] = ['TEST_ONLY unsupported invented occurrence.']
    elif forgery == 'task-date':
        source['as_of'] = 'not-a-date'
    elif forgery == 'publication-date':
        source['publication_date'] = '2019-99-99'
    elif forgery == 'signal-date':
        packet['signal']['date'] = '2026-10-30'
    else:
        packet['signal']['provenance']['url'] = 'https://example.invalid/foreign'
    request['source_packet'] = q.canonical(packet)
    request['source_pin'] = hashlib.sha256(request['source_packet']).hexdigest()
    with pytest.raises(ValueError, match='original|excerpt|date|provenance'):
        resolve_signal_input(**request)


@pytest.mark.parametrize('forgery', ['hidden-reference', 'child-candidates', 'context-target',
    'missing-family', 'null-signal', 'empty-from', 'duplicate-json'])
def test_input_schema_cannot_smuggle_labels_or_child_scope(protected_request, forgery):
    request = protected_request()
    packet = json.loads(request['source_packet'])
    if forgery == 'hidden-reference':
        packet['expected'] = {'component': 'test-only-local-service'}
    elif forgery == 'child-candidates':
        packet['candidates'] = [{'id': 'foreign-only'}]
    elif forgery == 'context-target':
        request['policy']['component'] = 'test-only-local-service'
    elif forgery == 'missing-family':
        del packet['source_context']['family']
    elif forgery == 'null-signal':
        packet['signal'] = None
    elif forgery == 'empty-from':
        packet['signal']['from'] = {}
    request['source_packet'] = q.canonical(packet)
    if forgery == 'duplicate-json':
        request['source_packet'] = request['source_packet'][:-1] + b',"statement":"replaced statement"}'
    request['source_pin'] = hashlib.sha256(request['source_packet']).hexdigest()
    with pytest.raises(ValueError, match='shape|field|policy|duplicate|declared|text'):
        resolve_signal_input(**request)


def test_a_previously_open_model_cannot_hide_later_working_tree_changes(protected_request):
    request = protected_request()
    repo = request['repo']
    path = repo.model_root / 'world/components/test-only-access.yaml'
    path.write_text(path.read_text() + 'description: TEST_ONLY uncommitted mutation\n')
    with pytest.raises(RuntimeError, match='uncommitted|dirty'):
        resolve_signal_input(**request)


def test_only_declared_excerpts_and_original_metadata_enter_fresh_candidate_projections(protected_request):
    request = protected_request()
    resolved = resolve_signal_input(**request)
    packet = json.loads(request['source_packet'])
    context = resolved.payload['source_context']
    assert context['excerpts'] == ['Administrators propose a change; no event has occurred.']
    assert set(context['original_sources']['bulletin']) == {'identity', 'version', 'bytes', 'sha256'}
    assert 'content_base64' not in q.canonical(resolved.payload).decode()
    assert context['original_source_manifest_digest'] == q.digest(packet['source_context']['original_sources'])
    host = resolved.host_record
    assert host['context']['original_sources'] == packet['source_context']['original_sources']
    assert host['context']['signal']['from'] == packet['signal']['from']
    host['context']['original_sources'].clear()
    projected = resolved.payload
    projected['candidates'].clear()
    projected['source_context']['excerpts'].append('injected after resolution')
    request['policy']['frame'] = 'changed after resolution'
    assert len(resolved.payload['candidates']) == 20
    assert resolved.payload['source_context']['excerpts'] == ['Administrators propose a change; no event has occurred.']
    assert resolved.host_record['context']['original_sources']
    assert resolved.host_inputs().resolve('test-only-signal')['context']['frame'] == 'TEST_ONLY-current-model-relevance'


def test_an_existing_model_head_does_not_substitute_for_the_pinned_world_dependency(protected_request):
    request = protected_request()
    request['policy']['model_pins']['world'] = copy.deepcopy(request['policy']['model_pins']['overlay'])
    with pytest.raises(ValueError, match='closure'):
        resolve_signal_input(**request)


def metadata_request(protected_request, org='driftwood', *, imported=None):
    request = protected_request(org)
    store, acquired, authority = acquire_fixture() if imported is None else imported
    metadata = acquired.public
    source = metadata['source']
    packet = {'schema': 'twin.source-packet/v2', 'statement': metadata['statement']['text'],
        'source': source['display_source'], 'source_context': {
            **{key: source[key] for key in ('url', 'version', 'family')}, 'as_of': '2019-01-03',
            'visible_excerpt_ids': [item['id'] for item in metadata['visible_excerpts']],
            'source_metadata_manifest_sha256': acquired.binding['expected_manifest_sha256']},
        'signal': {'id': 'test-only-signal', 'date': '2019-01-03', 'from': {'party': 'TEST_ONLY'},
                   'provenance': {'url': source['url'], 'date': '2019-01-03'}}}
    request.update(source_packet=q.canonical(packet), source_pin=q.digest(packet), metadata_store=store)
    request.pop('test_only')
    request['policy']['source_metadata'] = sm.policy_for(acquired)
    return request, authority


@pytest.mark.parametrize('org', ['driftwood', 'tuppence', 'ludlow'])
def test_v2_constructor_and_same_parent_host_share_protected_month_metadata(protected_request, org):
    request, authority = metadata_request(protected_request, org)
    resolved = resolve_signal_input(**request)
    context = resolved.payload['source_context']
    assert context['metadata']['publication']['value'] == '2021-08'
    assert context['metadata']['publication']['precision'] == 'month'
    assert len(resolved.payload['candidates']) == 20
    host = resolved.host_inputs().resolve('test-only-signal')
    assert host['input'] == resolved.payload
    assert host['context']['source_metadata'] == request['policy']['source_metadata']
    assert host['context']['input_construction_sha256'] != hashlib.sha256(
        Path(__import__('twin.signal_inputs', fromlist=['__file__']).__file__).read_bytes()).hexdigest()
    assert context['metadata']['binding']['expected_authority_digest'] == authority.digest


@pytest.mark.parametrize('forgery', ['packet-manifest', 'packet-authority', 'packet-publication',
    'packet-statement', 'packet-excerpts', 'task-date', 'model-date', 'policy-authority',
    'policy-import', 'policy-receipt', 'empty-store'])
def test_v2_packet_cannot_appoint_metadata_or_bypass_host_guards(protected_request, forgery):
    request, _ = metadata_request(protected_request)
    packet = json.loads(request['source_packet'])
    if forgery == 'packet-manifest':
        packet['source_context']['source_metadata_manifest_sha256'] = '0' * 64
    elif forgery == 'packet-authority':
        packet['source_context']['authority'] = 'self-appointed'
    elif forgery == 'packet-publication':
        packet['source_context']['publication'] = {'precision': 'day', 'value': '2021-08-01'}
    elif forgery == 'packet-statement':
        packet['statement'] = 'invented claim'
    elif forgery == 'packet-excerpts':
        packet['source_context']['visible_excerpt_ids'] = []
    elif forgery == 'task-date':
        packet['source_context']['as_of'] = '20190103'
    elif forgery == 'model-date':
        request['policy']['model_as_of'] = '20261030'
    elif forgery.startswith('policy-'):
        field = {'policy-authority': 'authority_digest', 'policy-import': 'import_id',
                 'policy-receipt': 'acquisition_receipt_sha256'}[forgery]
        request['policy']['source_metadata'][field] = '0' * 64
    else:
        request['metadata_store'] = sm.MetadataStore()
    request.update(source_packet=q.canonical(packet), source_pin=q.digest(packet))
    with pytest.raises(ValueError):
        resolve_signal_input(**request)


def test_v2_host_archive_cannot_restore_from_public_dictionary_without_parent_store(protected_request):
    request, _ = metadata_request(protected_request)
    resolved = resolve_signal_input(**request)
    public = resolved.host_inputs().description
    with pytest.raises(ValueError, match='independently selected'):
        q.HostInputs(public).resolve('test-only-signal')


def test_v2_host_archive_restore_requires_same_store_and_policy(protected_request):
    request, authority = metadata_request(protected_request)
    resolved = resolve_signal_input(**request)
    inputs = resolved.host_inputs()
    restored = q.HostInputs.restore(inputs.description, metadata_store=request['metadata_store'],
        metadata_policy={'authority_digest': authority.digest, 'purpose': 'TEST_ONLY'})
    assert restored.resolve('test-only-signal') == inputs.resolve('test-only-signal')
    with pytest.raises(ValueError):
        q.HostInputs.restore(inputs.description, metadata_store=sm.MetadataStore(),
            metadata_policy={'authority_digest': authority.digest, 'purpose': 'TEST_ONLY'})


def test_v2_constructor_and_host_preserve_honest_unknown_publication(protected_request):
    request, _ = metadata_request(protected_request, imported=unknown_fixture())
    resolved = resolve_signal_input(**request)
    public = resolved.payload['source_context']['metadata']
    assert public['publication']['value'] is None
    assert public['publication']['basis'] == 'unestablished'
    assert resolved.host_inputs().resolve('test-only-signal')['input'] == resolved.payload


def metadata_selection(protected_request):
    from bench import signal_contract_controls as controls
    from twin.reference_cases import admit_reference, binding_for
    original = controls.selection()
    value = json.loads(original.population.description)
    requests = {org: metadata_request(protected_request, org) for org in value['envelope']['adopters']}
    first, authority = next(iter(requests.values()))
    store = first['metadata_store']
    contexts, admissions = {}, []
    for packet in value['selected'][:3]:
        case = packet['case']
        org = case['context']['organisation']
        request, _ = requests[org]
        request['metadata_store'] = store
        resolved = resolve_signal_input(**request)
        row = resolved.host_record
        case['input'] = row['input']
        case['context'] = {**case['context'], **{key: row['context'][key] for key in (
            'organisation', 'domain', 'capability', 'frame', 'as_of', 'source',
            'source_metadata', 'source_metadata_public_sha256')}}
        case['basis_binding'] = binding_for(case)
        admitted = admit_reference(case, case['context'])
        assert admitted.admitted, admitted.reasons
        admissions.append(admitted)
        contexts[org] = {key: row['context'][key] for key in (
            'candidate_universe_digest', 'model_pins', 'model_as_of', 'input_construction_sha256')}
    envelope = value['envelope']
    envelope.update(signal_contexts=contexts, domains=[first['policy']['domain']],
        capabilities=[first['policy']['capability']], frames=[first['policy']['frame']],
        sources=['TEST_ONLY-family'], **{'from': '2019-01-01', 'until': '2026-10-30'})
    population = q.Population.freeze('signal-classify', tuple(admissions), envelope, value['exposure'])
    actor = q.Actor.freeze(controls.signal_actor, controls.parse, {'purpose': 'TEST_ONLY'},
                           source_metadata_authority=authority)
    return {'actor': actor, 'population': population, 'basis_checker': controls.basis_holds,
        'review': q.PopulationReview.test_only(population), 'assessment_policy': original.assessment_policy,
        'source_metadata_policy': {'authority_digest': authority.digest, 'purpose': 'TEST_ONLY'},
        'metadata_store': store}


def test_reviewed_v2_selection_requires_actual_source_import_before_runner(protected_request):
    request = metadata_selection(protected_request)
    selected = q.Selection.freeze(**request)
    selected.verify()
    assert json.loads(selected.description)['source_metadata_policy'] == request['source_metadata_policy']
    request['metadata_store'] = sm.MetadataStore()
    with pytest.raises(ValueError, match='authority|acquired'):
        q.Selection.freeze(**request)


def test_reviewed_v2_selection_cannot_use_public_projection_as_authority(protected_request):
    request = metadata_selection(protected_request)
    request.pop('metadata_store')
    request.pop('source_metadata_policy')
    with pytest.raises(ValueError, match='protected metadata'):
        q.Selection.freeze(**request)


def test_host_session_restore_refuses_missing_metadata_even_without_any_model_run(protected_request):
    request, authority = metadata_request(protected_request)
    inputs = resolve_signal_input(**request).host_inputs()
    resolver = q.Resolver()
    session = resolver.host_session(inputs)
    with pytest.raises(ValueError, match='restore'):
        q.HostSession.restore(session.archive(), resolver)
    restored = q.HostSession.restore(session.archive(), resolver, metadata_store=request['metadata_store'],
        metadata_policy={'authority_digest': authority.digest, 'purpose': 'TEST_ONLY'})
    assert restored.archive() == session.archive()


def test_legacy_test_mechanics_cannot_enter_ordinary_constructor_or_restore(protected_request):
    request = protected_request()
    request.pop('test_only')
    with pytest.raises(ValueError, match='actual protected'):
        resolve_signal_input(**request)
    from bench import signal_contract_controls as controls
    with pytest.raises(ValueError, match='restore'):
        q.HostInputs.restore(controls.inputs().description)


def test_legacy_fixture_mechanics_cannot_restore_operational_bundle_or_record_official_scores(tmp_path):
    from bench import signal_contract_controls as controls
    selected = controls.selection()
    capture = selected.capture()
    review_request = selected.assessment_request(capture)
    assessment = controls.review_store(tmp_path, selected.assessment_policy, review_request).assess(
        selected.assessment_policy, review_request)
    bundle = selected.archive(capture, assessment)
    (tmp_path / 'bundle.json').write_bytes(bundle)
    catalogue = {'schema': 'twin.qualification-registry/v1',
        'entries': [{'bundle': 'bundle.json', 'sha256': sm.sha256(bundle)}]}
    (tmp_path / 'catalogue.json').write_bytes(q.canonical(catalogue))
    with pytest.raises(ValueError, match='ordinary operational'):
        q.Resolver.from_catalogue(tmp_path / 'catalogue.json', q.digest(catalogue))
    with pytest.raises(ValueError, match='official scores'):
        selected.record(capture, '2026-10-30T00:00:00Z', Path(q.__file__).with_name('skill-scores.jsonl'), assessment)


def test_changing_normalizer_without_changing_constructor_invalidates_authority(protected_request, monkeypatch):
    request, _ = metadata_request(protected_request)
    resolved = resolve_signal_input(**request)
    original = sm.normalize_publication
    # The helper code changes in memory while the source filename/version remains unchanged.
    monkeypatch.setattr(sm, 'normalize_publication', lambda _: ('month', '2021-08'))
    with pytest.raises(ValueError, match='changed|normalization|differs'):
        resolved.host_inputs().resolve('test-only-signal')
    monkeypatch.setattr(sm, 'normalize_publication', original)


@pytest.mark.parametrize('path,key,value', [
    ((), 'expected', 'hidden target'), (('publication',), 'field_support', {}),
    (('statement',), 'basis', {'target': 'hidden'}),
    (('source',), 'reference_kind', 'hidden'),
    (('publication',), 'basis', 'generator'), (('publication',), 'value', '2021-08-01'),
    (('members', 'original'), 'expected', 'hidden target')])
def test_typed_publication_basis_allowance_preserves_hidden_reference_guards(path, key, value):
    from bench import signal_contract_controls as controls
    from twin.reference_cases import admit_reference, binding_for
    _, acquired, _ = acquire_fixture()
    public = acquired.public
    case = json.loads(controls.selection().population.description)['selected'][0]['case']
    case['input'] = {'source_context': {'metadata': public}}
    case['basis_binding'] = binding_for(case)
    assert admit_reference(case, case['context']).admitted
    target = public
    for part in path:
        target = target[part]
    target[key] = value
    # Even a recomputed manifest hash cannot make an unknown hidden-answer field legal.
    manifest = {name: item for name, item in public.items() if name not in ('binding', 'source_metadata_manifest_sha256', 'source_archive_closure_digest',
        'metadata_authority_digest', 'metadata_acquisition_receipt_sha256', 'input_construction_sha256')}
    manifest['schema'] = 'twin.source-metadata/v1'
    public['binding']['expected_manifest_sha256'] = sm.sha256(sm.canonical(manifest))
    public['source_metadata_manifest_sha256'] = public['binding']['expected_manifest_sha256']
    case['basis_binding'] = binding_for(case)
    assert 'reference-fields-in-input' in admit_reference(case, case['context']).reasons


def test_valid_foreign_acquisition_cannot_replace_independently_selected_manifest(protected_request):
    request, _ = metadata_request(protected_request)
    _, foreign, _ = unknown_fixture()
    packet = json.loads(request['source_packet'])
    packet['source_context'].update({key: foreign.public['source'][key] for key in ('url', 'version', 'family')})
    packet['source_context']['source_metadata_manifest_sha256'] = foreign.binding['expected_manifest_sha256']
    packet['source_context']['visible_excerpt_ids'] = [item['id'] for item in foreign.public['visible_excerpts']]
    request.update(source_packet=q.canonical(packet), source_pin=q.digest(packet))
    with pytest.raises(ValueError, match='protected source metadata packet mapping'):
        resolve_signal_input(**request)


def test_self_consistent_child_metadata_change_cannot_replace_parent_projection(protected_request):
    request, authority = metadata_request(protected_request)
    row = resolve_signal_input(**request).host_record
    row['input']['source_context']['metadata']['bounded_review']['scope_qualification'] += ' altered'
    row['source'] = source_record(q.canonical(row['input']), 'TEST_ONLY-family', 'TEST_ONLY-original-v1')
    row['context']['source_sha256'] = row['source']['sha256']
    row['context']['source_metadata_public_sha256'] = q.digest(row['input']['source_context']['metadata'])
    inputs = q.HostInputs.freeze((row,), (row['issuer'],), metadata_store=request['metadata_store'],
        metadata_policy={'authority_digest': authority.digest, 'purpose': 'TEST_ONLY'})
    with pytest.raises(ValueError, match='protected metadata projection'):
        inputs.resolve('test-only-signal')


def test_test_only_metadata_store_cannot_enter_actual_constructor_policy(protected_request):
    request, _ = metadata_request(protected_request)
    request['policy']['issuer'] = 'actual-protected-parent'
    with pytest.raises(ValueError, match='TEST_ONLY metadata authority'):
        resolve_signal_input(**request)


def test_reviewed_signal_metadata_is_mandatory_without_semantic_assessment(protected_request):
    request = metadata_selection(protected_request)
    request.pop('assessment_policy')
    request.pop('metadata_store')
    request.pop('source_metadata_policy')
    with pytest.raises(ValueError, match='protected metadata'):
        q.Selection.freeze(**request)


METADATA_REVISION_CALLS = []


def metadata_revision_runner(payload, config):
    """TEST_ONLY input-only mechanical capture; no model or competence claim."""
    METADATA_REVISION_CALLS.append(payload['statement'])
    return q.canonical({'steep': 'economic', 'component': payload['candidates'][0]['id'],
        'basis': {'statement_quotes': [payload['statement']],
            'component_quotes': [payload['candidates'][0]['name']], 'reason': 'TEST_ONLY mechanical control'}})


def metadata_revision_selection(protected_request):
    from bench import signal_contract_controls as controls
    request = metadata_selection(protected_request)
    request.pop('assessment_policy')
    authority = request['metadata_store'].authority(request['source_metadata_policy']['authority_digest'])
    request['actor'] = q.Actor.freeze(metadata_revision_runner, controls.parse, {'purpose': 'TEST_ONLY'},
                                    source_metadata_authority=authority)
    return request


def test_acquired_v2_without_semantic_assessment_preserves_capture_and_durable_boundary(protected_request, tmp_path):
    request = metadata_revision_selection(protected_request)
    selected = q.Selection.freeze(**request)
    selected.verify()
    row = json.loads(selected.population.description)['selected'][0]['case']
    selected.verify_input(row)
    captured = selected.capture()
    assert len(json.loads(captured.packet)['rows']) == 3
    recorded = selected.record(captured, '2026-10-30T00:00:00Z', tmp_path / 'local-mechanical-scores.jsonl')
    assert recorded['outcome'] == 'not-measurable'
    bundle = selected.archive(captured)
    (tmp_path / 'bundle.json').write_bytes(bundle)
    catalogue = {'schema': 'twin.qualification-registry/v1',
        'entries': [{'bundle': 'bundle.json', 'sha256': sm.sha256(bundle)}]}
    (tmp_path / 'catalogue.json').write_bytes(q.canonical(catalogue))
    with pytest.raises(ValueError, match='protected metadata'):
        q.Resolver.from_catalogue(tmp_path / 'catalogue.json', q.digest(catalogue), allow_test_only=True)
    restored = q.Resolver.from_catalogue(tmp_path / 'catalogue.json', q.digest(catalogue),
        allow_test_only=True, metadata_store=request['metadata_store'],
        source_metadata_policy=request['source_metadata_policy'])
    assert not restored.permission('signal-classify', selected.actor.model_version).granted
    # A serialized actor/public selection cannot supply the protected handles, even
    # when it removes its authority claim and consistently rehashes the public packet.
    public_only = json.loads(bundle)
    public_only['actor'].pop('source_metadata_authority')
    actor_digest = q.digest(public_only['actor'])
    public_only['selection']['actor'] = actor_digest
    public_only['selection'].pop('source_metadata_policy')
    public_only['capture']['selection'] = q.digest(public_only['selection'])
    for item in public_only['capture']['rows']:
        item['output']['actor_digest'] = actor_digest
    raw = q.canonical(public_only)
    (tmp_path / 'public-only.json').write_bytes(raw)
    catalogue['entries'] = [{'bundle': 'public-only.json', 'sha256': sm.sha256(raw)}]
    (tmp_path / 'public-only-catalogue.json').write_bytes(q.canonical(catalogue))
    with pytest.raises(ValueError, match='protected metadata'):
        q.Resolver.from_catalogue(tmp_path / 'public-only-catalogue.json', q.digest(catalogue), allow_test_only=True)


def test_public_selection_without_handles_cannot_verify_capture_or_record(protected_request, tmp_path):
    from dataclasses import replace
    request = metadata_revision_selection(protected_request)
    selected = q.Selection.freeze(**request)
    captured = selected.capture()
    public = json.loads(selected.description)
    public.pop('source_metadata_policy')
    public_only = replace(selected, description=q.canonical(public), _metadata_store=None, _metadata_policy=None)
    before = len(METADATA_REVISION_CALLS)
    with pytest.raises(ValueError, match='protected metadata'):
        public_only.verify()
    with pytest.raises(ValueError, match='protected metadata'):
        public_only.capture()
    with pytest.raises(ValueError, match='protected metadata'):
        public_only.record(captured, '2026-10-30T00:00:00Z', tmp_path / 'must-not-exist.jsonl')
    assert len(METADATA_REVISION_CALLS) == before
    assert not (tmp_path / 'must-not-exist.jsonl').exists()


def test_live_source_import_is_checked_without_semantic_assessment(protected_request):
    request = metadata_revision_selection(protected_request)
    selected = q.Selection.freeze(**request)
    row = json.loads(selected.population.description)['selected'][0]['case']
    _, foreign, _ = unknown_fixture()
    source = row['input']['source_context']
    source.update({key: foreign.public['source'][key] for key in ('url', 'version', 'family')})
    source['visible_excerpt_ids'] = [item['id'] for item in foreign.public['visible_excerpts']]
    source['metadata'] = foreign.public
    row['context']['source_metadata'] = sm.policy_for(foreign)
    row['context']['source_metadata_public_sha256'] = q.digest(foreign.public)
    with pytest.raises(ValueError, match='actual protected metadata acquisition'):
        selected.verify_input(row)


@pytest.mark.parametrize('change', ['actor-authority', 'full-construction'])
def test_optional_assessment_cannot_skip_actor_or_constructor_identity(protected_request, change):
    from bench import signal_contract_controls as controls
    request = metadata_revision_selection(protected_request)
    if change == 'actor-authority':
        request['actor'] = q.Actor.freeze(metadata_revision_runner, controls.parse, {'purpose': 'TEST_ONLY'})
        reason = 'actor lacks exact protected metadata'
    else:
        public = json.loads(request['population'].description)
        public['envelope']['signal_contexts']['driftwood']['input_construction_sha256'] = '0' * 64
        request['population'] = q.Population(q.canonical(public))
        reason = 'qualification input differs'
    with pytest.raises(ValueError, match=reason):
        q.Selection.freeze(**request)
