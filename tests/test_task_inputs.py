"""TEST_ONLY actual model declarations and retained source artifacts; no empirical labels."""
import json

import pytest

from twin import qualification as q, source_metadata as sm
from twin.reference_cases import source_record
from twin.task_contracts import TaskContract
from test_signal_inputs import protected_request
from test_source_metadata import fixture_import


def task_request(protected_request, task='evolution', org='driftwood'):
    request = protected_request(org)
    manifest, archive, receipts, authority = fixture_import()
    store = sm.MetadataStore(purpose='TEST_ONLY')
    acquired = store.acquire('TEST_ONLY-task-import', sm.canonical(manifest), archive, receipts,
                             sm.sha256(sm.canonical(manifest)), authority)
    originals = {name: source_record(archive[value['sha256']], value['identity'], value['version'])
                 for name, value in acquired.public['members'].items()}
    evidence = [{'id': 'TEST_ONLY-evidence', 'source_id': 'primary',
        'visible_excerpt_id': None, 'statement': acquired.public['statement']['text']}]
    packet = q.canonical({'schema': 'twin.task-source-packet/v1', 'subject': 'TEST_ONLY-task-subject',
        'as_of': '2019-01-03', 'target': {'kind': 'component', 'component': 'test-only-cloud'}, 'task': {'evidence': evidence},
                          'original_sources': {'primary': originals}})
    job = {**{key: request['policy'][key] for key in ('issuer', 'domain', 'capability', 'frame', 'model_as_of', 'model_pins')},
        'subject': 'TEST_ONLY-task-subject', 'organisation': org, 'target': {'kind': 'component', 'component': 'test-only-cloud'},
        'as_of': '2019-01-03', 'source': 'TEST_ONLY-protected-common-source', 'estate_scope_sha256': '1' * 64,
        'source_packet': packet, 'source_pin': sm.sha256(packet),
        'source_bindings': {'primary': acquired.binding},
        'metadata_policies': {'primary': {'authority_digest': authority.digest, 'purpose': 'TEST_ONLY'}}}
    return {'contract': TaskContract.freeze(task), 'protected_job': job, 'repo': request['repo'],
            'source_store': store, 'party_bytes': request['party_bytes'], 'party_pin': request['party_pin']}


def test_constructor_builds_actual_typed_component_and_metadata_without_private_handles(protected_request):
    from twin.task_inputs import resolve_task_input, TaskPolicy
    args = task_request(protected_request)
    resolved = resolve_task_input(**args)
    payload = resolved.payload
    assert payload['schema'] == 'twin.evolution-input/v2'
    assert payload['task']['component'] == {'id': 'test-only-cloud', 'name': 'test-only-cloud',
        'kind': 'activity', 'evolution': 'product', 'visibility': .25}
    assert payload['context']['metadata']['primary'] == args['source_store'].resolve(
        **args['protected_job']['source_bindings']['primary']).public
    assert 'source_bindings' not in payload and 'metadata_policies' not in payload
    host = resolved.host_inputs()
    assert host.resolve('TEST_ONLY-task-subject')['input'] == payload
    policy = TaskPolicy.freeze(args['contract'], (resolved,))
    policy.verify_input(resolved.host_record)
    with pytest.raises(ValueError):
        q.HostInputs.restore(host.description)
