"""TEST_ONLY full-universe host contracts, never actual estate qualification."""
import json
import pytest
from twin import qualification as q
from twin.reference_cases import source_record


def signal_inputs(**changes):
    candidates = [{'id': f'TEST_ONLY-{i}', 'name': f'Choice {i}',
                   'definition': {'id': f'TEST_ONLY-{i}', 'name': f'Choice {i}'}} for i in range(20)]
    payload = {'statement': 'TEST_ONLY staff ask for support', 'source': 'TEST_ONLY source',
        'candidates': candidates}
    source = source_record(q.canonical(payload), 'TEST_ONLY-family', 'v1')
    context = {'organisation': 'driftwood', 'domain': 'estate cloud', 'capability': 'delivery',
        'as_of': '2026-10-30', 'frame': 'TEST_ONLY Wardley axis', 'source': source['identity'],
        'source_sha256': source['sha256'], 'eligible_components': [item['id'] for item in candidates],
        'candidate_universe_digest': q.digest(candidates), 'signal': {'id': 'TEST_ONLY-live',
            'date': '2026-10-30', 'from': {'party': 'TEST_ONLY'},
            'provenance': {'url': 'https://test.invalid/fixture'}}}
    context.update(changes)
    return q.HostInputs.freeze(({'subject': 'TEST_ONLY-live', 'input': payload, 'context': context,
        'source': source, 'issuer': 'TEST_ONLY-host'},), ('TEST_ONLY-host',))


def test_host_resolves_the_eligible_universe_without_preselecting_the_answer():
    resolved = signal_inputs().resolve('TEST_ONLY-live')
    assert 'component' not in resolved['context']
    assert resolved['context']['eligible_components'][-1] == 'TEST_ONLY-19'


@pytest.mark.parametrize('changes', [{'component': 'TEST_ONLY-0'},
    {'eligible_components': ['TEST_ONLY-forged']}, {'candidate_universe_digest': 'forged'}])
def test_host_refuses_target_hints_and_universes_unbound_to_actual_input(changes):
    with pytest.raises(ValueError):
        signal_inputs(**changes).resolve('TEST_ONLY-live')


def test_nonfirst_component_and_original_structured_basis_validate_after_actual_review(tmp_path):
    from bench import signal_contract_controls as controls
    from twin.signal_candidate import evidence_text
    selected = controls.selection()
    capture = selected.capture()
    request = selected.assessment_request(capture)
    assessment = controls.review_store(tmp_path / 'qualification', selected.assessment_policy, request).assess(selected.assessment_policy, request)
    scores = tmp_path / 'scores.jsonl'
    selected.record(capture, '2026-10-30T00:00:00Z', scores, assessment)
    resolver = q.Resolver(((selected, capture, assessment),), scores, allow_test_only=True)
    session = resolver.host_session(controls.inputs())
    assert session.judge('signal-classify', selected.actor.model_version, 'TEST_ONLY-live').receipt is None
    pending = session.pending_reviews[0]
    store = controls.review_store(tmp_path / 'live', selected.assessment_policy, q.canonical(pending['request']))
    result = session.review_pending(pending['request_digest'], store)
    assert result.receipt
    signal = controls.inputs().resolve('TEST_ONLY-live')['context']['signal']
    signal = {**signal, 'steep': 'social', 'statement': 'social TEST_ONLY-19 literal supplied witness', 'source': 'TEST_ONLY'}
    doc = {'org': 'driftwood', 'run': {'clock': 'github', 'model_version': selected.actor.model_version,
        'host_session': session.identity, 'declined': session.declines}, 'claims': [{
            'id': 'TEST_ONLY-binding', 'kind': 'binding', 'component': 'TEST_ONLY-19',
            'host_subject': 'TEST_ONLY-live', 'host_receipt': result.receipt,
            'evidence': evidence_text(result.output.stated.basis), 'signal': signal, 'price_eligible': False}]}
    assert resolver.check_claim_document(doc, 'github') == []
    import hashlib
    import subprocess
    import sys
    bundle = selected.archive(capture, assessment)
    session_bundle = session.archive()
    (tmp_path / 'qualified.json').write_bytes(bundle)
    (tmp_path / 'session.json').write_bytes(session_bundle)
    catalogue = {'schema': 'twin.qualification-registry/v1', 'entries': [
        {'bundle': 'qualified.json', 'sha256': hashlib.sha256(bundle).hexdigest()}], 'sessions': [
        {'bundle': 'session.json', 'sha256': hashlib.sha256(session_bundle).hexdigest()}]}
    path = tmp_path / 'registry.json'
    path.write_bytes(q.canonical(catalogue))
    (tmp_path / 'claim.json').write_bytes(q.canonical(doc))
    command = [sys.executable, '-c',
        'import json,sys; from pathlib import Path; from twin.qualification import Resolver; '
        'r=Resolver.from_catalogue(Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3]),allow_test_only=True); '
        'bad=r.check_claim_document(json.loads(Path(sys.argv[4]).read_bytes()),"github"); '
        'print(json.dumps(bad)); raise SystemExit(bool(bad))',
        str(path), hashlib.sha256(path.read_bytes()).hexdigest(), str(scores), str(tmp_path / 'claim.json')]
    completed = subprocess.run(command, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_protected_parent_produces_only_validated_grade_five_binding_after_review(tmp_path):
    from bench import signal_contract_controls as controls
    from twin.qualified_signals import SignalParent
    selected = controls.selection()
    capture = selected.capture()
    request = selected.assessment_request(capture)
    assessment = controls.review_store(tmp_path / 'qualification', selected.assessment_policy, request).assess(selected.assessment_policy, request)
    scores = tmp_path / 'scores.jsonl'
    selected.record(capture, '2026-10-30T00:00:00Z', scores, assessment)
    resolver = q.Resolver(((selected, capture, assessment),), scores, allow_test_only=True)
    run = SignalParent(resolver, selected.actor.model_version).start(controls.inputs())
    assert run.document() is None
    pending = run.session.pending_reviews[0]
    store = controls.review_store(tmp_path / 'live', selected.assessment_policy, q.canonical(pending['request']))
    assert run.review(pending['request_digest'], store).receipt
    document = run.document()
    assert document['claims'][0]['component'] == 'TEST_ONLY-19'
    assert document['claims'][0]['evidence_grade'] == 5
    assert document['claims'][0]['price_eligible'] is False
    assert run.validate() == []


def test_existing_validator_entrypoint_refuses_unregistered_parent_execution(tmp_path):
    import subprocess
    import sys
    result = subprocess.run([sys.executable, '.claude/skills/classify-and-judge/assets/validate_claim.py',
        '--run-registered-signals', 'driftwood', '--output', str(tmp_path / 'run')],
        text=True, capture_output=True)
    assert result.returncode == 2
    report = json.loads((tmp_path / 'run' / 'summary.json').read_bytes())
    assert report['accepted'] is False
    assert 'no registered signal job' in report['reasons'][0]


def test_self_consistent_changed_host_closure_cannot_borrow_the_qualified_frame(tmp_path):
    from bench import signal_contract_controls as controls
    selected = controls.selection()
    capture = selected.capture()
    request = selected.assessment_request(capture)
    assessment = controls.review_store(tmp_path / 'qualification', selected.assessment_policy, request).assess(selected.assessment_policy, request)
    scores = tmp_path / 'scores.jsonl'
    selected.record(capture, '2026-10-30T00:00:00Z', scores, assessment)
    resolver = q.Resolver(((selected, capture, assessment),), scores, allow_test_only=True)
    value = json.loads(controls.inputs().description)
    row = value['records'][0]
    row['context']['model_pins'] = {'TEST_ONLY': 'a different legitimate model closure'}
    # These new input bytes and host provenance are internally consistent.
    row['input']['model_context'] = {'pins': row['context']['model_pins']}
    row['source'] = source_record(q.canonical(row['input']), 'TEST_ONLY', 'v2')
    row['context']['source_sha256'] = row['source']['sha256']
    inputs = q.HostInputs(q.canonical(value))
    inputs.resolve('TEST_ONLY-live')
    session = resolver.host_session(inputs)
    result = session.judge('signal-classify', selected.actor.model_version, 'TEST_ONLY-live')
    assert result.receipt is None
    assert session.pending_reviews == []
    assert 'model' in session.declines[0]['reason']


def test_signal_eligible_set_cannot_replace_an_evolution_fixed_target(tmp_path):
    from bench.qualification_controls import host_inputs, host_setup
    value = json.loads(host_inputs().description)
    row = value['records'][0]
    del row['context']['component']
    row['input']['candidates'] = [{'id': 'delivery', 'name': 'Delivery', 'definition': {'id': 'delivery'}}]
    row['context']['eligible_components'] = ['delivery']
    row['context']['candidate_universe_digest'] = q.digest(row['input']['candidates'])
    row['source'] = source_record(q.canonical(row['input']), 'TEST_ONLY', 'v1')
    row['context']['source_sha256'] = row['source']['sha256']
    inputs = q.HostInputs(q.canonical(value))
    inputs.resolve('live-one')
    selected, resolver, session = host_setup(tmp_path, inputs)
    result = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
    assert result.receipt is None and 'fixed' in result.reason
