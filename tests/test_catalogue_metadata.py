"""TEST_ONLY combined catalogue controls; never reserved source or model evidence."""
import json

import pytest

from twin import qualification as q, source_metadata as sm
from test_signal_inputs import protected_request, metadata_revision_selection, metadata_request, resolve_signal_input
from test_signal_inputs import METADATA_REVISION_CALLS


@pytest.fixture(scope='module')
def catalogue_material(tmp_path_factory):
    from bench import substrate_contract_controls as generator_controls
    from twin import substrate_generation as generation
    root = tmp_path_factory.mktemp('TEST_ONLY-catalogue-metadata')
    signal_root = root / 'signal'
    signal_root.mkdir()
    request = protected_request.__wrapped__(signal_root)
    signal_config = metadata_revision_selection(request)
    signal = q.Selection.freeze(**signal_config)
    signal_capture = signal.capture()
    generator_root = root / 'generator'
    generator_root.mkdir()
    generator, generator_resolver, requests = generator_controls.setup(generator_root)
    generator_capture = generator_resolver._bindings[(generation.METRIC, generator.actor.model_version)][1]
    scores = generator_root / 'scores.jsonl'
    signal.record(signal_capture, '2026-10-30T00:00:00Z', scores)
    signal_resolver = q.Resolver(((signal, signal_capture),), scores, allow_test_only=True)
    signal_input = resolve_signal_input(**metadata_request(request)[0])
    signal_session = signal_resolver.host_session(signal_input.host_inputs())
    result = signal_session.judge('signal-classify', signal.actor.model_version, 'test-only-signal')
    assert result.receipt is None and signal_session.declines
    generator_input = generator_controls.resolve(requests['driftwood'], generator.actor, 801)
    generator_run = generation.GenerationParent(generator_resolver, generator.actor.model_version, clock='github').start(
        generator_input.host_inputs())
    assert generator_run.validate() == []
    artifacts = {'signal': signal.archive(signal_capture), 'generator': generator.archive(generator_capture),
        'signal-session': signal_session.archive(), 'generator-session': generator_run.session.archive()}
    for name, raw in artifacts.items():
        (root / (name + '.json')).write_bytes(raw)
    return {'root': root, 'scores': scores, 'artifacts': artifacts, 'signal_config': signal_config,
        'generator_document': generator_run.document()}


def load_catalogue(material, name, bundles, sessions=(), *, with_metadata=True, metadata_kwargs=None):
    root = material['root']
    def entry(kind):
        return {'bundle': kind + '.json', 'sha256': sm.sha256(material['artifacts'][kind])}
    document = {'schema': 'twin.qualification-registry/v1', 'entries': [entry(kind) for kind in bundles],
                'sessions': [entry(kind) for kind in sessions]}
    path = root / (name + '.json')
    path.write_bytes(q.canonical(document))
    kwargs = {'metadata_store': material['signal_config']['metadata_store'],
              'source_metadata_policy': material['signal_config']['source_metadata_policy']} if with_metadata else {}
    if metadata_kwargs is not None:
        kwargs = metadata_kwargs
    return q.Resolver.from_catalogue(path, q.digest(document), material['scores'], allow_test_only=True, **kwargs)


@pytest.mark.parametrize('with_metadata', [False, True])
@pytest.mark.parametrize('with_session', [False, True])
def test_generator_bundle_restore_is_unchanged_by_signal_metadata(catalogue_material, with_metadata, with_session):
    sessions = ['generator-session'] if with_session else []
    restored = load_catalogue(catalogue_material, f'generator-{with_metadata}-{with_session}', ['generator'], sessions,
                              with_metadata=with_metadata)
    assert restored is not None
    if with_session:
        assert restored.check_generation_document(catalogue_material['generator_document'], 'github') == []


@pytest.mark.parametrize('reverse', [False, True])
def test_combined_catalogue_restores_actual_signal_and_generator_sessions(catalogue_material, reverse):
    from bench import substrate_contract_controls as generator_controls
    before = (len(generator_controls.CALLS), len(METADATA_REVISION_CALLS))
    bundles = ['signal', 'generator'][::(-1 if reverse else 1)]
    sessions = ['signal-session', 'generator-session'][::(-1 if reverse else 1)]
    restored = load_catalogue(catalogue_material, 'combined-with-sessions-' + str(reverse), bundles, sessions)
    assert restored.check_generation_document(catalogue_material['generator_document'], 'github') == []
    config = catalogue_material['signal_config']
    for name in sessions:
        raw = catalogue_material['artifacts'][name]
        session = q.HostSession.restore(raw, restored, metadata_store=config['metadata_store'],
                                        metadata_policy=config['source_metadata_policy'])
        assert session.archive() == raw
    assert (len(generator_controls.CALLS), len(METADATA_REVISION_CALLS)) == before


@pytest.mark.parametrize('mode', ['good', 'missing', 'empty', 'foreign-policy'])
def test_signal_catalogue_still_requires_its_actual_metadata_handles(catalogue_material, mode):
    config = catalogue_material['signal_config']
    kwargs = {'metadata_store': config['metadata_store'], 'source_metadata_policy': config['source_metadata_policy']}
    if mode == 'missing':
        kwargs = {}
    elif mode == 'empty':
        kwargs['metadata_store'] = sm.MetadataStore(purpose='TEST_ONLY')
    elif mode == 'foreign-policy':
        kwargs['source_metadata_policy'] = {**config['source_metadata_policy'], 'authority_digest': '0' * 64}
    if mode == 'good':
        load_catalogue(catalogue_material, 'signal-good', ['signal'], ['signal-session'], metadata_kwargs=kwargs)
    else:
        with pytest.raises(ValueError, match='metadata'):
            load_catalogue(catalogue_material, 'signal-' + mode, ['signal'], ['signal-session'], metadata_kwargs=kwargs)


def test_combined_catalogue_cannot_omit_required_signal_handles(catalogue_material):
    with pytest.raises(ValueError, match='metadata'):
        load_catalogue(catalogue_material, 'combined-missing', ['generator', 'signal'], with_metadata=False)


@pytest.mark.parametrize('with_metadata', [False, True])
def test_signal_archive_cannot_downgrade_by_removing_saved_metadata_binding(catalogue_material, with_metadata):
    packet = json.loads(catalogue_material['artifacts']['signal-session'])
    packet['inputs'].pop('source_metadata_policy')
    config = catalogue_material['signal_config']
    kwargs = {'metadata_store': config['metadata_store'], 'metadata_policy': config['source_metadata_policy']} if with_metadata else {}
    with pytest.raises(ValueError, match='metadata'):
        q.HostSession.restore(q.canonical(packet), q.Resolver(), **kwargs)
