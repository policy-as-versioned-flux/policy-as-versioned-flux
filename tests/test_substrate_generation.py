"""TEST_ONLY protected generator mechanics; no earned model permission."""
import copy
import hashlib
import json

import pytest

from bench import substrate_contract_controls as controls
from twin import qualification as q, substrate_generation as generation


@pytest.fixture(scope='module')
def protected_system(tmp_path_factory):
    return controls.setup(tmp_path_factory.mktemp('TEST_ONLY-generator-system'))


@pytest.mark.parametrize('org', ['driftwood', 'tuppence', 'ludlow'])
def test_host_resolves_exact_tuple_all_focuses_and_full_current_model(tmp_path, org):
    resolved = generation.resolve_recipe_input(**controls.request(tmp_path / 'model', org))
    row = resolved.host_inputs().resolve('TEST_ONLY-live')
    assert isinstance(row['input'], str)
    assert len(row['context']['generator_context']['definitions']) == 20
    assert row['source']['identity'] == f'estate-synthetic-recipe:{org}:v1'
    assert row['source']['sha256'] == q.digest(row['input'])
    assert row['context']['raw_recipe_sha256'] == hashlib.sha256(row['input'].encode()).hexdigest()
    assert len(row['context']['focus_components']) == 3


@pytest.mark.parametrize('change', ['foreign domain', 'extra focus', 'source hash', 'missing issuer', 'world pin', 'authority', 'intent'])
def test_factory_refuses_foreign_or_unestablished_scope_before_invocation(tmp_path, change):
    args = controls.request(tmp_path / 'model')
    packet = json.loads(args['source_packet'])
    if change == 'foreign domain': packet['domain'] = generation.SCOPES['ludlow']['domain']
    elif change == 'extra focus': packet['focus_components'].append('TEST_ONLY-foreign')
    elif change == 'source hash': args['source_pin'] = '0' * 64
    elif change == 'missing issuer': args['policy']['issuer'] = ''
    elif change == 'world pin': args['policy']['model_pins']['world']['commit'] = '0' * 40
    elif change == 'authority': packet['authority'] = 'self-declared-model'
    else: packet['intent']['sha256'] = '0' * 64
    if change != 'source hash':
        args['source_packet'] = q.canonical(packet)
        args['source_pin'] = hashlib.sha256(args['source_packet']).hexdigest()
    with pytest.raises(ValueError): generation.resolve_recipe_input(**args)


def test_one_protected_invocation_supplies_the_authored_blob_and_replay(protected_system):
    selected, resolver, requests = protected_system
    resolved = controls.resolve(requests['driftwood'], selected.actor, 101)
    before = len(controls.CALLS)
    run = generation.GenerationParent(resolver, selected.actor.model_version).start(resolved.host_inputs())
    assert len(controls.CALLS) == before + 1
    assert run.validate() == []
    document = run.document()
    assert document['mark'] == 'authored'
    delivered = document['batches'][0]
    assert run.replay(delivered['blob']) == q.canonical(run.results[0].output.stated.answer)
    assert len(controls.CALLS) == before + 1


@pytest.mark.parametrize('organisations', [('driftwood', 'tuppence'), ('tuppence', 'driftwood')])
def test_mixed_adopter_run_declines_every_request_before_invocation_and_saves_fallback(protected_system, tmp_path, organisations):
    selected, resolver, requests = protected_system
    rows = tuple(controls.resolve(requests[org], selected.actor, 800 + index).host_record
                 for index, org in enumerate(organisations))
    inputs = q.HostInputs.freeze(rows, ('TEST_ONLY-host',))
    before = len(controls.CALLS)
    run = generation.GenerationParent(resolver, selected.actor.model_version).start(inputs)
    output = tmp_path / 'unsupported-run'
    save_error = None
    try:
        run.save(output)
    except ValueError as exc:
        save_error = str(exc)
    archived = json.loads(run.session.archive())
    observed = {'raw_calls': len(controls.CALLS) - before,
        'states': [item['state'] for item in archived['generation_dispositions']],
        'host_declines': len(archived['declines']), 'summary_exists': (output / 'summary.json').exists(),
        'save_error': save_error}
    assert observed == {'raw_calls': 0, 'states': ['host-decline', 'host-decline'],
        'host_declines': 2, 'summary_exists': True, 'save_error': None}
    assert [item['subject'] for item in archived['generation_dispositions']] == [row['subject'] for row in rows]
    assert len(run.results) == 2 and all(result.receipt is None and result.reason for result in run.results)
    assert archived['records'] == {} and archived['generation_blobs'] == {}
    generation.verify_session(run.session)
    assert json.loads((output / 'host-session.json').read_bytes()) == archived
    summary = json.loads((output / 'summary.json').read_bytes())
    assert summary['accepted'] is False and summary['declined'] == archived['declines']
    assert summary['generation_dispositions'] == archived['generation_dispositions']
    assert any('fallback' in reason for reason in summary['reasons'])
    assert all('cross-adopter' in item['reason'] for item in summary['declined'])
    assert not (output / 'generation.json').exists()


def test_multiple_requests_for_one_adopter_keep_the_supported_run_path(protected_system):
    selected, resolver, requests = protected_system
    rows = tuple(controls.resolve(requests['driftwood'], selected.actor, index).host_record for index in (810, 811))
    before = len(controls.CALLS)
    run = generation.GenerationParent(resolver, selected.actor.model_version).start(q.HostInputs.freeze(rows, ('TEST_ONLY-host',)))
    assert len(controls.CALLS) == before + 2
    assert [item['state'] for item in run.document()['run']['generation_dispositions']] == ['delivered', 'delivered']
    assert len(run.document()['batches']) == 2 and run.validate() == []


@pytest.mark.parametrize('mode,reason', [('bad-structure', 'structural'), ('bad-basis', 'actual basis')])
def test_permitted_actor_cannot_deliver_invalid_live_output_and_internal_receipt_survives(protected_system, mode, reason):
    selected, resolver, requests = protected_system
    run = generation.GenerationParent(resolver, selected.actor.model_version).start(
        controls.resolve(requests['driftwood'], selected.actor, 102, mode).host_inputs())
    assert run.results[0].receipt
    archive = json.loads(run.session.archive())
    assert len(archive['records']) == 1
    assert archive['generation_dispositions'][0]['state'] == 'validation-decline'
    assert reason in archive['generation_dispositions'][0]['reason']
    assert run.document()['batches'] == []
    assert run.validate()


def test_existing_validator_checks_generator_receipts_and_conserves_deliveries(protected_system):
    from twin.qualified_signals import _validator
    selected, resolver, requests = protected_system
    run = generation.GenerationParent(resolver, selected.actor.model_version, clock='github').start(
        controls.resolve(requests['ludlow'], selected.actor, 103).host_inputs())
    validator = _validator()
    kinds, roles = validator.twin_facts(str(__import__('pathlib').Path(__file__).resolve().parents[1]))
    document = run.document()
    assert validator.validate(document, kinds, roles, headless=True, clock='github',
        permission=(resolver.check_claim_document, resolver.permission)) == []
    changed = copy.deepcopy(document)
    changed['batches'][0]['blob'] = 'sha256:' + '0' * 64 + ':1'
    assert validator.validate(changed, kinds, roles, headless=True, clock='github',
        permission=(resolver.check_claim_document, resolver.permission))


@pytest.mark.parametrize('forgery', ['blob', 'raw', 'basis', 'receipt', 'omitted disposition', 'duplicate disposition', 'subject'])
def test_forged_or_incomplete_archive_cannot_import_as_protected_delivery(protected_system, forgery):
    selected, resolver, requests = protected_system
    run = generation.GenerationParent(resolver, selected.actor.model_version).start(
        controls.resolve(requests['driftwood'], selected.actor, 104).host_inputs())
    archived = json.loads(run.session.archive())
    receipt = next(iter(archived['records']))
    if forgery == 'blob': archived['generation_blobs'][next(iter(archived['generation_blobs']))] = 'e30='
    elif forgery == 'raw': archived['records'][receipt]['output']['raw'] = 'e30='
    elif forgery == 'basis': archived['records'][receipt]['output']['basis']['model_basis']['counts']['total_lines'] = 1
    elif forgery == 'receipt': archived['generation_dispositions'][0]['host_receipt'] = 'forged'
    elif forgery == 'omitted disposition': archived['generation_dispositions'].clear()
    elif forgery == 'duplicate disposition': archived['generation_dispositions'].append(archived['generation_dispositions'][0])
    else: archived['generation_dispositions'][0]['subject'] = 'foreign'
    with pytest.raises((ValueError, KeyError)):
        restored = q.HostSession.restore(q.canonical(archived), resolver)
        generation.verify_session(restored)


def test_independently_pinned_catalogue_restores_generation_in_a_fresh_process(protected_system, tmp_path):
    import subprocess
    import sys
    selected, resolver, requests = protected_system
    run = generation.GenerationParent(resolver, selected.actor.model_version, clock='github').start(
        controls.resolve(requests['tuppence'], selected.actor, 105).host_inputs())
    captured = resolver._bindings[(generation.METRIC, selected.actor.model_version)][1]
    bundle = selected.archive(captured)
    session = run.session.archive()
    (tmp_path / 'qualification.json').write_bytes(bundle)
    (tmp_path / 'session.json').write_bytes(session)
    catalogue = q.canonical({'schema': 'twin.qualification-registry/v1',
        'entries': [{'bundle': 'qualification.json', 'sha256': hashlib.sha256(bundle).hexdigest()}],
        'sessions': [{'bundle': 'session.json', 'sha256': hashlib.sha256(session).hexdigest()}]})
    (tmp_path / 'registry.json').write_bytes(catalogue)
    (tmp_path / 'generation.json').write_bytes(q.canonical(run.document()))
    scores = tmp_path / 'scores.jsonl'
    scores.write_bytes(resolver._scores_path.read_bytes())
    script = ('import json,sys; from pathlib import Path; from twin.qualification import Resolver; '
        'r=Resolver.from_catalogue(Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3]),allow_test_only=True); '
        'from twin.qualified_signals import _validator; v=_validator(); '
        'k,roles=v.twin_facts(str(Path.cwd())); '
        'bad=v.validate(json.loads(Path(sys.argv[4]).read_bytes()),k,roles,headless=True,clock="github",'
        'permission=(r.check_claim_document,r.permission)); print(json.dumps(bad)); raise SystemExit(bool(bad))')
    completed = subprocess.run([sys.executable, '-c', script, str(tmp_path / 'registry.json'),
        hashlib.sha256(catalogue).hexdigest(), str(scores), str(tmp_path / 'generation.json')], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_empty_default_registry_and_stale_scope_decline_before_inference(protected_system):
    selected, _, requests = protected_system
    inputs = controls.resolve(requests['driftwood'], selected.actor, 106).host_inputs()
    before = len(controls.CALLS)
    run = generation.GenerationParent(q.Resolver.from_checkout(), selected.actor.model_version).start(inputs)
    assert len(controls.CALLS) == before
    assert run.document()['run']['generation_dispositions'][0]['state'] == 'host-decline'
    assert run.validate()


@pytest.mark.parametrize('field', ['domain', 'focus', 'closure', 'source family', 'issuer', 'actor', 'date', 'frame'])
def test_individually_allowed_but_mismatched_or_stale_host_scope_never_invokes(protected_system, field):
    selected, resolver, requests = protected_system
    value = json.loads(controls.resolve(requests['driftwood'], selected.actor, 107).host_inputs().description)
    row = value['records'][0]
    if field == 'domain': row['context']['domain'] = generation.SCOPES['tuppence']['domain']
    elif field == 'focus': row['context']['focus_components'].append('payments-api')
    elif field == 'closure': row['context']['generator_context']['model_pins']['world']['commit'] = '0' * 40
    elif field == 'source family': row['context']['source'] = 'estate-synthetic-recipe:tuppence:v1'
    elif field == 'issuer': row['issuer'] = 'candidate-chosen'
    elif field == 'actor':
        from twin.reference_cases import source_record
        row['input'] = row['input'].replace(selected.actor.model_version, 'actor-foreign')
        row['source'] = source_record(q.canonical(row['input']), row['source']['identity'], row['source']['version'])
        row['context']['source_sha256'] = row['source']['sha256']
    elif field == 'date': row['context']['as_of'] = '2028-01-01'
    else: row['context']['frame'] = 'foreign frame'
    before = len(controls.CALLS)
    run = generation.GenerationParent(resolver, selected.actor.model_version).start(q.HostInputs(q.canonical(value)))
    assert len(controls.CALLS) == before
    assert run.document()['run']['generation_dispositions'][0]['state'] == 'host-decline'
    assert run.session.declines


def test_existing_validator_entrypoint_has_no_default_operational_generation_job(tmp_path):
    import subprocess
    import sys
    completed = subprocess.run([sys.executable, '.claude/skills/classify-and-judge/assets/validate_claim.py',
        '--run-registered-generation', 'driftwood', '--output', str(tmp_path / 'declined')], capture_output=True, text=True)
    assert completed.returncode == 2
    summary = json.loads((tmp_path / 'declined' / 'summary.json').read_bytes())
    assert summary['accepted'] is False
    assert 'no registered generation job' in summary['reasons'][0]
