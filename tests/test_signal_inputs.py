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
                    'overlay': overlay.ref.as_dict(), 'world': overlay.world.ref.as_dict()}}}
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
