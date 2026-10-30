"""TEST_ONLY task-selected signal guards; no permission or competence claim."""
import copy
import json
from types import SimpleNamespace

import pytest

from twin import qualification as q
from twin.reference_cases import source_record
from test_signal_inputs import (protected_request, metadata_revision_selection, metadata_request,
                               resolve_signal_input, METADATA_REVISION_CALLS)


@pytest.fixture(scope='module')
def live_material(tmp_path_factory):
    root = tmp_path_factory.mktemp('TEST_ONLY-live-signal-binding')
    request = protected_request.__wrapped__(root)
    config = metadata_revision_selection(request)
    selected = q.Selection.freeze(**config)
    inputs = resolve_signal_input(**metadata_request(request)[0]).host_inputs()
    return config, selected, inputs


def rehash(row):
    row['source'] = source_record(q.canonical(row['input']), row['source']['identity'], row['source']['version'])
    row['context']['source_sha256'] = row['source']['sha256']


def assumed_permission(selected, monkeypatch):
    """Replace only permission, never the constructor, actor, or receipt guards."""
    resolver = q.Resolver(((selected, None),), allow_test_only=True)
    monkeypatch.setattr(resolver, 'permission', lambda *args: SimpleNamespace(
        granted=True, why=lambda: 'TEST_ONLY assumed permission precondition; no ten-condition grant'))
    return resolver


def test_selected_signal_refuses_generic_downgrade_before_mechanical_actor(live_material, monkeypatch):
    config, selected, inputs = live_material
    public = json.loads(inputs.description)
    public.pop('source_metadata_policy')
    row = public['records'][0]
    row['context'].pop('eligible_components')
    row['context']['component'] = row['input']['candidates'][0]['id']
    row['input']['candidates'] = row['input']['candidates'][:1]
    rehash(row)
    # Even an in-memory host object cannot turn a selected signal task into a
    # generic component judgement by changing public discriminator fields.
    downgraded = q.HostInputs.freeze((row,), tuple(public['issuers']))
    session = assumed_permission(selected, monkeypatch).host_session(downgraded)
    before = len(METADATA_REVISION_CALLS)
    result = session.judge('signal-classify', selected.actor.model_version, row['subject'])
    assert result.receipt is None and result.reason
    assert len(METADATA_REVISION_CALLS) == before
    assert len(session.declines) == 1


@pytest.mark.parametrize('with_handles', [False, True])
def test_v2_archive_cannot_remove_public_routing_and_policy(live_material, with_handles):
    config, _, inputs = live_material
    public = json.loads(inputs.description)
    public.pop('source_metadata_policy')
    row = public['records'][0]
    row['context'].pop('eligible_components')
    row['context']['component'] = row['input']['candidates'][0]['id']
    row['input']['candidates'] = row['input']['candidates'][:1]
    rehash(row)
    kwargs = {'metadata_store': config['metadata_store'], 'metadata_policy': config['source_metadata_policy']} if with_handles else {}
    with pytest.raises(ValueError):
        q.HostInputs.restore(q.canonical(public), **kwargs)


def changed_row(inputs, change):
    row = copy.deepcopy(json.loads(inputs.description)['records'][0])
    payload, context = row['input'], row['context']
    if change == 'discriminators':
        context.pop('eligible_components')
        context['component'] = payload['candidates'][0]['id']
    elif change in ('one', 'nineteen'):
        payload['candidates'] = payload['candidates'][:1 if change == 'one' else 19]
        context['eligible_components'] = [item['id'] for item in payload['candidates']]
        context['candidate_universe_digest'] = q.digest(payload['candidates'])
    elif change in ('reordered', 'definition'):
        if change == 'reordered':
            payload['candidates'].reverse()
        else:
            payload['candidates'][0]['definition']['description'] = 'TEST_ONLY changed complete definition'
        context['eligible_components'] = [item['id'] for item in payload['candidates']]
        context['candidate_universe_digest'] = q.digest(payload['candidates'])
    elif change == 'closure':
        payload['model_context']['pins'] = {'model_repo': 'TEST_ONLY-forged-local-pin'}
        context['model_pins'] = payload['model_context']['pins']
    elif change == 'construction':
        context['input_construction_sha256'] = '0' * 64
    elif change == 'model-date':
        payload['model_context']['as_of'] = context['model_as_of'] = '2020-01-01'
    elif change in ('domain', 'party'):
        key = 'domain' if change == 'domain' else 'organisation'
        payload['model_context'][key] = context[key] = 'TEST_ONLY-foreign'
    elif change == 'task-date':
        payload['source_context']['as_of'] = context['as_of'] = '2026-10-31'
        context['signal']['date'] = '2026-10-31'
    elif change == 'claimed-universe':
        context['candidate_universe_digest'] = '0' * 64
    elif change == 'model-context':
        payload['model_context']['domain'] = 'TEST_ONLY-mismatched-model'
    else:
        raise AssertionError(change)
    rehash(row)
    return row


@pytest.mark.parametrize('change', ['discriminators', 'one', 'nineteen', 'reordered', 'definition',
    'closure', 'construction', 'model-date', 'domain', 'party', 'task-date', 'claimed-universe', 'model-context'])
def test_selected_signal_recomputes_actual_live_binding(live_material, monkeypatch, change):
    config, selected, inputs = live_material
    row = changed_row(inputs, change)
    with pytest.raises(ValueError, match='live input differs'):
        selected.verify_input(row)
    host = q.HostInputs.freeze((row,), (row['issuer'],), metadata_store=config['metadata_store'],
                              metadata_policy=config['source_metadata_policy'])
    session = assumed_permission(selected, monkeypatch).host_session(host)
    before = len(METADATA_REVISION_CALLS)
    result = session.judge('signal-classify', selected.actor.model_version, row['subject'])
    assert result.receipt is None and result.reason
    assert len(METADATA_REVISION_CALLS) == before
    assert len(session.declines) == 1


def test_genuine_acquired_signal_reaches_receipt_or_pending_review(live_material, monkeypatch, tmp_path):
    from bench import signal_contract_controls as controls
    from twin.qualified_signals import SignalParent, SignalRun
    config, unassessed, inputs = live_material
    for assessed in (False, True):
        selected = q.Selection.freeze(**{**config, 'assessment_policy': controls.selection().assessment_policy}) if assessed else unassessed
        resolver = assumed_permission(selected, monkeypatch)
        session = resolver.host_session(inputs)
        before = len(METADATA_REVISION_CALLS)
        result = session.judge('signal-classify', selected.actor.model_version, 'test-only-signal')
        assert len(METADATA_REVISION_CALLS) == before + 1
        if assessed:
            assert result.receipt is None and 'assessment required' in result.reason
            assert len(session.pending_reviews) == 1
            pending = session.pending_reviews[0]
            store = controls.review_store(tmp_path / 'TEST_ONLY-review', selected.assessment_policy,
                                          q.canonical(pending['request']))
            result = session.review_pending(pending['request_digest'], store)
        assert result.receipt is not None and result.reason is None
        document = SignalRun(SignalParent(resolver, selected.actor.model_version, clock='github'), session).document()
        assert session.check_document(document) == []
        restored = q.HostSession.restore(session.archive(), resolver, metadata_store=config['metadata_store'],
                                         metadata_policy=config['source_metadata_policy'])
        assert restored.archive() == session.archive()
        assert len(METADATA_REVISION_CALLS) == before + 1


def test_later_receipt_import_and_document_recompute_live_model(live_material, monkeypatch):
    from twin.qualified_signals import SignalParent, SignalRun
    config, selected, inputs = live_material
    resolver = assumed_permission(selected, monkeypatch)
    session = resolver.host_session(inputs)
    result = session.judge('signal-classify', selected.actor.model_version, 'test-only-signal')
    assert result.receipt
    document = SignalRun(SignalParent(resolver, selected.actor.model_version, clock='github'), session).document()
    packet = json.loads(session.archive())
    row = changed_row(inputs, 'domain')
    packet['inputs']['records'] = [row]
    # Retain a structurally self-consistent old receipt; claimed input hashes and
    # contexts cannot authorize a model outside the selected constructor context.
    for record in packet['records'].values():
        record['context'] = row['context']
        record['output']['input_digest'] = q.digest(row['input'])
    before = len(METADATA_REVISION_CALLS)
    with pytest.raises(ValueError, match='live input differs'):
        q.HostSession.restore(q.canonical(packet), resolver, metadata_store=config['metadata_store'],
                              metadata_policy=config['source_metadata_policy'])
    stale = q.HostInputs.freeze((row,), (row['issuer'],), metadata_store=config['metadata_store'],
                               metadata_policy=config['source_metadata_policy'])
    # Simulate a host binding becoming stale after capture, then use the public
    # document validation boundary rather than trusting the old receipt token.
    monkeypatch.setattr(session, '_inputs', stale)
    with pytest.raises(ValueError, match='live input differs'):
        session.check_document(document)
    assert len(METADATA_REVISION_CALLS) == before


def test_pending_review_and_import_recompute_live_model(live_material, monkeypatch, tmp_path):
    from bench import signal_contract_controls as controls
    config, _, inputs = live_material
    selected = q.Selection.freeze(**{**config, 'assessment_policy': controls.selection().assessment_policy})
    resolver = assumed_permission(selected, monkeypatch)
    session = resolver.host_session(inputs)
    result = session.judge('signal-classify', selected.actor.model_version, 'test-only-signal')
    assert not result.receipt and len(session.pending_reviews) == 1
    pending = session.pending_reviews[0]
    store = controls.review_store(tmp_path / 'TEST_ONLY-review', selected.assessment_policy,
                                  q.canonical(pending['request']))
    row = changed_row(inputs, 'domain')
    packet = json.loads(session.archive())
    packet['inputs']['records'] = [row]
    for record in packet['pending_reviews'].values():
        record['context'] = row['context']
        record['output']['input_digest'] = q.digest(row['input'])
    before = len(METADATA_REVISION_CALLS)
    with pytest.raises(ValueError, match='live input differs'):
        q.HostSession.restore(q.canonical(packet), resolver, metadata_store=config['metadata_store'],
                              metadata_policy=config['source_metadata_policy'])
    stale = q.HostInputs.freeze((row,), (row['issuer'],), metadata_store=config['metadata_store'],
                               metadata_policy=config['source_metadata_policy'])
    monkeypatch.setattr(session, '_inputs', stale)
    result = session.review_pending(pending['request_digest'], store)
    assert result.receipt is None and 'live input differs' in result.reason
    assert len(METADATA_REVISION_CALLS) == before


@pytest.mark.parametrize('payload', [
    {'source_context': {'metadata': {'note': 'TEST_ONLY ordinary non-signal metadata'}}},
    {'source_context': None},
    ['TEST_ONLY ordinary generic input'],
    'TEST_ONLY ordinary generic text',
])
def test_generic_host_input_keeps_unrelated_metadata_semantics(live_material, payload):
    _, _, inputs = live_material
    row = copy.deepcopy(json.loads(inputs.description)['records'][0])
    row['input'] = payload
    row['context'].pop('eligible_components')
    row['context'].pop('source_metadata')
    row['context']['component'] = 'TEST_ONLY-fixed-generic-component'
    rehash(row)
    host = q.HostInputs.freeze((row,), (row['issuer'],))
    assert host.resolve(row['subject'])['input'] == payload
