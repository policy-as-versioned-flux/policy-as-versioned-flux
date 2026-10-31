"""TEST_ONLY actual model declarations and retained source artifacts; no empirical labels."""
import json

import pytest

from twin import qualification as q, source_metadata as sm
from twin.reference_cases import source_record
from twin.task_contracts import TaskContract
from test_signal_inputs import protected_request
from test_source_metadata import fixture_import


def task_request(protected_request, task='evolution', org='driftwood', *, metadata_policy_version='1'):
    request = protected_request(org)
    manifest, archive, receipts, authority = fixture_import()
    if metadata_policy_version != '1':
        value = json.loads(authority.description)
        authority = sm.MetadataAuthority.freeze(value['issuer'], value['policy_id'], metadata_policy_version,
            value['policy_sha256'], authority.acquire_adapter, authority.source_checker, policy=value['policy'])
    store = sm.MetadataStore(purpose='TEST_ONLY')
    acquired = store.acquire('TEST_ONLY-task-import', sm.canonical(manifest), archive, receipts,
                             sm.sha256(sm.canonical(manifest)), authority)
    originals = {name: source_record(archive[value['sha256']], value['identity'], value['version'])
                 for name, value in acquired.public['members'].items()}
    evidence = [{'id': 'TEST_ONLY-evidence', 'source_id': 'primary',
        'visible_excerpt_id': None, 'statement': acquired.public['statement']['text']}]
    target = {'kind': 'component', 'component': 'test-only-cloud'}
    task_fields = {'evidence': evidence}
    if task == 'causal':
        target = {'kind': 'edge', 'from': 'test-only-local-records', 'to': 'test-only-local-service'}
        task_fields['measurement'] = {'from_unit': 'TEST_ONLY source units', 'to_unit': 'TEST_ONLY outcome units',
            'lag_unit': 'days', 'elasticity_definition': 'TEST_ONLY declared finite magnitude',
            'temporal_interpretation': 'TEST_ONLY subsequent interval, no measured effect'}
    elif task == 'gameplay':
        target = {'kind': 'map', 'organisation': org}
        task_fields = {}
    elif task == 'ethics':
        from twin.ethics_gate import load_sensors, SENSOR_REQUIRED
        table = [{key: row[key] for key in SENSOR_REQUIRED} for row in load_sensors()['sensors']]
        original = originals['original']
        policy_text = archive[original['sha256']].decode()
        target = {'kind': 'sensor', 'sensor': table[0]['sensor'], 'policy_sha256': original['sha256']}
        task_fields = {'sensor': {'id': table[0]['sensor'], 'name': table[0]['name']},
            'sensor_table': table, 'sensor_table_sha256': q.digest(table),
            'policy': {key: original[key] for key in ('identity', 'version', 'sha256')},
            'purpose': {'scenario': 'TEST_ONLY explicitly declared fixture purpose', 'will_act': True},
            'necessity': {'kind': 'structural', 'level': 'aggregate', 'alternatives': []},
            'proportionality': {'intrusion_cost': 1, 'value_illuminated': 10},
            'dpia': {'channels': ['keystroke'], 'profiling': False, 'financial_loss_risk': False,
                     'complete': False, 'completion_source_id': None}}
        task_fields['policy'].update(text=policy_text, as_of='2019-01-01')
    packet = q.canonical({'schema': 'twin.task-source-packet/v1', 'subject': 'TEST_ONLY-task-subject',
        'as_of': '2019-01-03', 'target': target, 'task': task_fields,
                          'original_sources': {'primary': originals}})
    job = {**{key: request['policy'][key] for key in ('issuer', 'domain', 'capability', 'frame', 'model_as_of', 'model_pins')},
        'subject': 'TEST_ONLY-task-subject', 'organisation': org, 'target': target,
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


def test_factual_decline_is_preserved_as_actual_basis(protected_request):
    from twin.task_inputs import resolve_task_input, verify_output
    from twin.skills import Stated
    payload = resolve_task_input(**task_request(protected_request)).payload
    actual = Stated(None, {'decline': 'TEST_ONLY no supplied source establishes an answer'})
    verify_output(payload, actual)
    assert actual.basis == {'decline': 'TEST_ONLY no supplied source establishes an answer'}


@pytest.mark.parametrize('task', ['evolution', 'causal', 'gameplay', 'ethics'])
@pytest.mark.parametrize('org', ['driftwood', 'tuppence', 'ludlow'])
def test_all_typed_tasks_keep_actual_twenty_model_and_independent_source_handles(protected_request, task, org):
    import copy
    from twin.task_inputs import resolve_task_input, TaskPolicy, validate_payload
    resolved = resolve_task_input(**task_request(protected_request, task, org))
    payload, row = resolved.payload, resolved.host_record
    validate_payload(payload)
    policy = TaskPolicy.freeze(TaskContract.freeze(task), (resolved,))
    policy.verify_input(row)
    assert payload['context']['organisation'] == org
    assert payload['context']['model_pins']['model_repo']['root'] == ''
    if task == 'gameplay':
        assert len(payload['task']['components']) == len(payload['task']['positions']) == 20
        assert len(payload['task']['org_components']) > 0
    if task == 'ethics':
        assert payload['target']['policy_sha256'] == payload['task']['policy']['sha256']
    for field in ('target', 'model_pins', 'source_metadata_bindings', 'input_constructor_sha256', 'task_contract_sha256'):
        forged = copy.deepcopy(row); forged['context'].pop(field)
        with pytest.raises(ValueError):
            policy.verify_input(forged)
    for mutate in (
        lambda value: value['input'].update(schema='TEST_ONLY-generic', component='TEST_ONLY-sentinel'),
        lambda value: value['input']['context'].update(metadata={}),
        lambda value: value['context'].update(organisation='TEST_ONLY-foreign'),
        lambda value: value['context'].update(as_of='2019-01'),
        lambda value: value['sources'].pop('party'),
    ):
        forged = copy.deepcopy(row); mutate(forged)
        with pytest.raises(ValueError):
            policy.verify_input(forged)
