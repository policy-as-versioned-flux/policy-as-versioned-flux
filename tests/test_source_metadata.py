"""Noncase TEST_ONLY acquisition and exact retained metadata controls."""
import hashlib
import json
from pathlib import Path

import pytest

from twin import source_metadata as sm


FIXTURE = Path(__file__).parent / 'fixtures/TEST_ONLY-source-metadata'


def fixture_import():
    manifest = json.loads((FIXTURE / 'manifest.example.json').read_bytes())
    archive = {hashlib.sha256(path.read_bytes()).hexdigest(): path.read_bytes()
               for path in FIXTURE.iterdir() if path.is_file()}
    acquisition = manifest['acquisitions']['fixture-acq']
    receipt = {key: value for key, value in acquisition.items()
               if key not in ('receipt_artifact_sha256', 'receipt_entry_pointer')}
    parent = (FIXTURE / 'original.txt').read_bytes()
    receipt.update(body_bytes=len(parent), body_sha256=sm.sha256(parent))
    raw = sm.canonical(receipt)
    acquisition['receipt_artifact_sha256'] = sm.sha256(raw)
    receipts = {sm.sha256(raw): raw}
    transform = manifest['members']['extraction']['transform']
    # Execute only the independently fixed TEST_ONLY declarative transform. Packet data
    # never chooses an executable. The retained receipt follows actual output bytes.
    recipe = json.loads((FIXTURE / 'transform-recipe.json').read_bytes())
    output = b''.join(parent[step['copy_parent_start']:step['copy_parent_end']]
        if 'copy_parent_start' in step else step['insert_utf8'].encode() for step in recipe['steps'])
    assert output == (FIXTURE / 'extraction.txt').read_bytes()
    execution = {'schema': 'twin.source-transform-receipt/v1', 'parent_sha256': sm.sha256(parent),
        'output_sha256': sm.sha256(output), 'output_bytes': len(output), 'exit_code': 0,
        **{key: transform[key] for key in ('identity', 'version',
            'implementation_artifact_sha256', 'configuration_sha256')}}
    raw = sm.canonical(execution)
    transform['execution_receipt_artifact_sha256'] = sm.sha256(raw)
    receipts[sm.sha256(raw)] = raw
    policy = {'purpose': 'TEST_ONLY', 'allowed_transforms': [{key: transform[key]
        for key in ('identity', 'version', 'implementation_artifact_sha256', 'configuration_sha256')}],
        'reviewer_id': 'TEST_ONLY-reviewer', 'reviewer_role': 'TEST_ONLY-fixture-custodian'}
    authority = sm.MetadataAuthority.freeze('TEST_ONLY-parent', 'TEST_ONLY-source-policy', '1',
        sm.sha256(sm.canonical(policy)), sm.retained_receipt_adapter, sm.retained_source_checker, policy=policy)
    return manifest, archive, receipts, authority


def acquire_fixture(manifest=None, *, statement_text=None):
    original, archive, receipts, authority = fixture_import()
    manifest = original if manifest is None else manifest
    if statement_text is not None:
        raw = statement_text.encode()
        archive[sm.sha256(raw)] = raw
        qualifier = manifest['members']['qualifier']
        qualifier.update(sha256=sm.sha256(raw), bytes=len(raw), version='TEST_ONLY-authored-qualifier-v2')
        manifest['statement']['text'] = statement_text
        manifest['statement']['witness'].update(member_sha256=sm.sha256(raw), start_byte=0,
            end_byte=len(raw), text_utf8=statement_text)
    store = sm.MetadataStore(purpose='TEST_ONLY')
    acquired = store.acquire('TEST_ONLY-import', sm.canonical(manifest), archive, receipts,
                             sm.sha256(sm.canonical(manifest)), authority)
    return store, acquired, authority


def acquire_simple_fixture(body, observed_kind, literal, normalization, publication, *, metadata_key=None):
    """Actually retain a separate noncase original and its fixture capture receipt."""
    manifest, archive, receipts, authority = fixture_import()
    pin = sm.sha256(body)
    archive[pin] = body
    original = manifest['members']['original']
    original.update(sha256=pin, bytes=len(body), version='TEST_ONLY-simple-original-v1')
    manifest['source']['version'] = original['version']
    manifest['members'].pop('extraction')
    manifest['members']['qualifier']['support_members'][0]['sha256'] = pin
    acquisition = manifest['acquisitions']['fixture-acq']
    acquisition.update(body_sha256=pin, body_bytes=len(body))
    raw = sm.canonical({key: value for key, value in acquisition.items()
                        if key not in ('receipt_artifact_sha256', 'receipt_entry_pointer')})
    acquisition['receipt_artifact_sha256'] = sm.sha256(raw)
    receipts[sm.sha256(raw)] = raw
    witness = {'member_id': 'original', 'member_sha256': pin, 'start_byte': 0,
               'end_byte': body.index(b'\n'), 'text_utf8': body.split(b'\n')[0].decode()}
    observation = {'id': 'observed-date', 'observed_kind': observed_kind, 'literal_value': literal,
        'normalization': normalization, 'metadata_key': metadata_key, 'witness': witness}
    manifest['observations'] = {'observed-date': observation}
    manifest['publication'] = publication
    manifest['visible_excerpts'] = [{'id': 'retained-date', 'origin_role': 'publisher-quotation',
                                     'witness': witness}]
    manifest['bounded_review']['reviewed_member_ids'] = ['original', 'qualifier']
    store = sm.MetadataStore(purpose='TEST_ONLY')
    acquired = store.acquire('TEST_ONLY-simple-import', sm.canonical(manifest), archive, receipts,
        sm.sha256(sm.canonical(manifest)), authority)
    return store, acquired, authority


def unknown_fixture():
    return acquire_simple_fixture(b'Reviewed: 2026-10-01\n',
        'publisher-review', '2026-10-01', 'literal-iso-day',
        {'precision': 'unknown', 'value': None, 'basis': 'unestablished', 'observation_id': None,
         'assertion_origin': 'unestablished',
         'qualification': 'TEST_ONLY retained original reports review only; publication is unestablished.'})


def test_parent_acquisition_retains_month_precision_and_resolves_actual_receipt():
    store, acquired, authority = acquire_fixture()
    resolved = store.resolve(**acquired.binding)
    assert resolved.public['publication'] == {'precision': 'month', 'value': '2021-08',
        'basis': 'first-publication', 'observation_id': 'published-month',
        'assertion_origin': 'captured-publisher-assertion'}
    assert resolved.public['statement']['origin_role'] == 'producer-authored'
    assert resolved.binding['expected_authority_digest'] == authority.digest
    assert 'content_base64' not in sm.canonical(resolved.public).decode()
    assert store.receipt(resolved.binding['expected_acquisition_receipt_sha256'])


@pytest.mark.parametrize('forgery', ['receipt', 'pointer', 'body', 'url', 'witness', 'span', 'hash',
    'kind', 'normalization', 'qualifier', 'parent', 'role', 'execution', 'unestablished',
    'separator', 'overlap', 'unknown-field', 'reviewer', 'missing-archive'])
def test_protected_acquisition_refuses_false_source_or_lineage(forgery):
    manifest, archive, receipts, authority = fixture_import()
    observation = manifest['observations']['published-month']
    member = manifest['members']['extraction']
    if forgery == 'receipt':
        receipts.clear()
    elif forgery == 'pointer':
        manifest['acquisitions']['fixture-acq']['receipt_entry_pointer'] = '/absent-entry'
    elif forgery == 'body':
        manifest['acquisitions']['fixture-acq']['body_bytes'] = 1
    elif forgery == 'url':
        manifest['members']['original']['identity'] = 'https://example.invalid/forged'
    elif forgery == 'witness':
        observation['witness']['text_utf8'] = 'invented publisher text'
    elif forgery == 'span':
        observation['witness']['end_byte'] = 999
    elif forgery == 'hash':
        observation['witness']['member_sha256'] = '0' * 64
    elif forgery == 'kind':
        observation['observed_kind'] = 'generator'
    elif forgery == 'normalization':
        manifest['publication']['value'] = '2021-08-01'
    elif forgery == 'qualifier':
        observation['witness'] = dict(manifest['statement']['witness'])
    elif forgery == 'parent':
        member['parent']['sha256'] = '0' * 64
    elif forgery == 'role':
        member['role'] = 'acquired-original'
    elif forgery == 'execution':
        member['transform']['configuration_sha256'] = '0' * 64
    elif forgery == 'unestablished':
        member['transform']['lineage_status'] = 'unestablished'
        member['transform']['version'] = None
    elif forgery == 'separator':
        observation['witness'].update(end_byte=29, text_utf8='First published: August 2021\n')
    elif forgery == 'overlap':
        member['lineage'][1]['output_start'] = 27
    elif forgery == 'unknown-field':
        manifest['expected'] = 'hidden reference prohibited'
    elif forgery == 'reviewer':
        manifest['bounded_review']['reviewer_id'] = 'self-appointed'
    else:
        archive.pop(manifest['members']['original']['sha256'])
    with pytest.raises(ValueError):
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-import', sm.canonical(manifest), archive, receipts,
                                  sm.sha256(sm.canonical(manifest)), authority)


def test_public_acquired_shape_and_forged_receipts_do_not_create_store_authority():
    _, acquired, _ = acquire_fixture()
    forged = sm.AcquiredMetadata(acquired.description)
    with pytest.raises(ValueError, match='actual protected'):
        sm.MetadataStore().resolve(**forged.binding)


def test_differently_acquired_manifest_cannot_replace_host_selected_receipt():
    store, acquired, _ = acquire_fixture()
    binding = acquired.binding
    binding['expected_acquisition_receipt_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='binding'):
        store.resolve(**binding)


def test_honest_unknown_retains_review_context_and_cannot_satisfy_known_age():
    _, acquired, _ = unknown_fixture()
    assert acquired.public['publication']['value'] is None
    assert acquired.public['observations']['observed-date']['observed_kind'] == 'publisher-review'
    with pytest.raises(ValueError, match='unknown source age'):
        sm.require_known_age(acquired.public)


@pytest.mark.parametrize('literal,rule,expected', [
    ('2021-08-31', 'literal-iso-day', ('day', '2021-08-31')),
    ('2021-08-31T23:30:00-07:00', 'source-local-calendar-day', ('day', '2021-08-31')),
    ('August 2021', 'english-month-year', ('month', '2021-08'))])
def test_declared_normalization_preserves_source_local_precision(literal, rule, expected):
    assert sm.normalize_publication({'literal_value': literal, 'normalization': rule}) == expected


@pytest.mark.parametrize('literal,rule', [('2021-02-30', 'literal-iso-day'),
    ('2021-08', 'literal-iso-day'), ('2021-08-31T23:30:00', 'source-local-calendar-day'),
    ('Smarch 2021', 'english-month-year')])
def test_invalid_or_partial_dates_cannot_supply_known_publication(literal, rule):
    with pytest.raises(ValueError):
        sm.normalize_publication({'literal_value': literal, 'normalization': rule})


def test_test_only_authority_cannot_be_selected_for_actual_parent_purpose():
    manifest, archive, receipts, authority = fixture_import()
    policy = json.loads(authority.description)['policy']
    policy['purpose'] = 'actual'
    actual = sm.MetadataAuthority.freeze('actual-parent', 'actual-policy', '1', sm.sha256(sm.canonical(policy)),
        sm.retained_receipt_adapter, sm.retained_source_checker, policy=policy)
    with pytest.raises(ValueError, match='TEST_ONLY'):
        sm.MetadataStore().acquire('actual-import', sm.canonical(manifest), archive, receipts,
                                  sm.sha256(sm.canonical(manifest)), actual)


def test_fixture_authority_cannot_enter_default_actual_store():
    manifest, archive, receipts, authority = fixture_import()
    with pytest.raises(ValueError, match='protected store purpose'):
        sm.MetadataStore().acquire('actual-import', sm.canonical(manifest), archive, receipts,
                                  sm.sha256(sm.canonical(manifest)), authority)


def test_actual_fixture_acquisition_preserves_offset_first_publication_assertion():
    _, acquired, _ = acquire_simple_fixture(
        b'govuk:first-published-at=2021-08-31T23:30:00-07:00\n', 'publisher-first-publication',
        '2021-08-31T23:30:00-07:00', 'source-local-calendar-day',
        {'precision': 'day', 'value': '2021-08-31', 'basis': 'first-publication',
         'observation_id': 'observed-date', 'assertion_origin': 'captured-publisher-assertion'},
        metadata_key='govuk:first-published-at')
    assert acquired.public['publication']['value'] == '2021-08-31'
    assert acquired.public['observations']['observed-date']['literal_value'].endswith('-07:00')
    assert acquired.public['observations']['observed-date']['metadata_key'] == 'govuk:first-published-at'


def test_metadata_authority_requires_independently_pinned_policy_bytes():
    _, _, _, authority = fixture_import()
    with pytest.raises(ValueError, match='pinned metadata authority policy'):
        sm.MetadataAuthority.freeze('TEST_ONLY-parent', 'TEST_ONLY-policy', '1', '0' * 64,
            sm.retained_receipt_adapter, sm.retained_source_checker,
            policy=json.loads(authority.description)['policy'])


def fixture_custodian_holds_interpretation(manifest, archive, receipts, policy):
    sm.retained_source_checker(manifest, archive, receipts, policy)
    raise ValueError('TEST_ONLY attributed custodian finding: interpretation held for source review')


def test_actual_protected_source_checker_hold_produces_no_acquisition():
    manifest, archive, receipts, old = fixture_import()
    policy = json.loads(old.description)['policy']
    authority = sm.MetadataAuthority.freeze('TEST_ONLY-parent', 'TEST_ONLY-reviewed-hold', '1',
        sm.sha256(sm.canonical(policy)), sm.retained_receipt_adapter,
        fixture_custodian_holds_interpretation, policy=policy)
    store = sm.MetadataStore(purpose='TEST_ONLY')
    with pytest.raises(ValueError, match='attributed custodian finding'):
        store.acquire('TEST_ONLY-held', sm.canonical(manifest), archive, receipts,
                      sm.sha256(sm.canonical(manifest)), authority)
    with pytest.raises(ValueError, match='no actual protected'):
        store.resolve('TEST_ONLY-held', sm.sha256(sm.canonical(manifest)), authority.digest, '0' * 64)


@pytest.mark.parametrize('kind', ['publisher-update', 'publisher-review', 'event', 'generator', 'capture', 'other'])
def test_each_nonpublication_observation_kind_is_held_by_actual_acquisition(kind):
    manifest, archive, receipts, authority = fixture_import()
    manifest['observations']['published-month']['observed_kind'] = kind
    with pytest.raises(ValueError, match='observed kind'):
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-wrong-kind', sm.canonical(manifest),
            archive, receipts, sm.sha256(sm.canonical(manifest)), authority)


@pytest.mark.parametrize('field,value', [('value', '2021-08'), ('observation_id', 'published-month'),
    ('basis', 'publication'), ('assertion_origin', 'captured-publisher-assertion'), ('qualification', '')])
def test_unknown_shape_cannot_smuggle_a_positive_publication_claim(field, value):
    manifest, archive, receipts, authority = fixture_import()
    manifest['publication'] = {'precision': 'unknown', 'value': None, 'basis': 'unestablished',
        'observation_id': None, 'assertion_origin': 'unestablished', 'qualification': 'TEST_ONLY bounded unknown'}
    manifest['publication'][field] = value
    with pytest.raises(ValueError, match='schema'):
        sm.MetadataStore(purpose='TEST_ONLY').acquire('TEST_ONLY-invalid-unknown', sm.canonical(manifest),
            archive, receipts, sm.sha256(sm.canonical(manifest)), authority)

