"""TEST_ONLY actors prove binding mechanics; none certifies a real model."""
from __future__ import annotations

import json
import hashlib

import pytest

from twin import record_skill_scores as rss
from twin import qualification as q
from twin.skills import Stated
from twin.reference_cases import source_record
from bench.qualification_controls import (basis_holds, constant_actor, envelope, host_inputs, host_setup, literal_actor, mechanical_selection, parse_position, population, position_document, reference, wrong_reference)
from bench.qualification_controls import signal_selection
from bench.qualification_controls import intermittent_actor, failing_actor, wrong_basis_actor
from bench.qualification_controls import reviewed_mechanical_selection
from bench.qualification_controls import observed_runtime_actor
from bench.qualification_controls import (defaulted_runner, nested_default_runner, defaulted_parser,
    keyword_default_parser, defaulted_basis_checker, defaulted_review_checker, changed_defaulted_runner,
    defaulted_reference_projection, defaulted_selection)














def test_a_candidate_label_cannot_relabel_incumbent_evaluation(tmp_path):
    path = tmp_path / 'scores.jsonl'
    with pytest.raises(ValueError, match='select.*actor'):
        rss.run('2026-10-30T00:00:00Z', 'TEST_ONLY-alternate', path)
    assert not path.exists()


def test_the_selected_actor_actually_receives_only_input():
    actor = q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'})
    result = actor.invoke({'position': 0.25, 'evidence': 'literal supplied witness'})
    assert result.stated == Stated({'evolution_position': 0.25}, 'literal supplied witness')
    assert json.loads(result.raw) == {'position': 0.25, 'evidence': 'literal supplied witness'}
    assert result.actor_digest == actor.digest


def test_population_and_candidate_input_cannot_mutate_retained_references():
    original = reference()
    scope = envelope()
    admitted = q.Population.freeze('evolution-judge', (original,), scope,
        {'status': 'development', 'history': ['exposed'], 'training_provenance': 'unknown'})
    first = admitted.corpus
    first[0]['expected']['evolution_position'] = 0.9
    scope['adopters'].clear()
    assert admitted.corpus[0]['expected'] == {'evolution_position': 0.25}
    assert admitted.envelope['adopters'] == ['driftwood', 'tuppence', 'ludlow']
    assert not admitted.qualification_admitted


def test_a_held_reference_cannot_enter_the_selected_population():
    from dataclasses import replace
    held = replace(reference(), reasons=('scope-context-conflict',))
    with pytest.raises(ValueError, match='held reference'):
        q.Population.freeze('evolution-judge', (held,), envelope(), {})


def test_a_capture_cannot_borrow_a_different_actor_or_revised_population():
    actor = q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'})
    selected = q.Selection.freeze(actor, population(), basis_holds)
    captured = selected.capture()
    other = q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY', 'revision': 2})
    foreign = q.Selection.freeze(other, population(), basis_holds)
    with pytest.raises(ValueError, match='selection'):
        foreign.evaluate(captured)
    with pytest.raises(ValueError, match='selection'):
        q.Selection.freeze(actor, population(count=3), basis_holds).evaluate(captured)
    assert selected.evaluate(captured).score == 1.0






def test_reference_baseline_and_candidate_variance_are_separate_facts():
    selected = q.Selection.freeze(q.Actor.freeze(constant_actor, parse_position, {'purpose': 'TEST_ONLY'}),
                                  population(), basis_holds)
    captured = selected.capture()
    facts = selected.facts(captured)
    assert facts['reference_score'] == 1.0
    assert facts['baseline'].score == pytest.approx(0.25)
    assert facts['variance'] == {'evolution_position': 1}
    assert facts['readings'][0].distinct == 1
    with pytest.raises(ValueError, match='reference projection'):
        wrong = q.Selection.freeze(selected.actor, population(), basis_holds,
                                   reference_projection=wrong_reference)
        wrong.facts(wrong.capture())


def test_a_modified_capture_cannot_be_attested_by_its_own_identity_fields():
    from dataclasses import replace
    selected = q.Selection.freeze(q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'}),
                                  population(), basis_holds)
    captured = selected.capture()
    changed = json.loads(captured.packet)
    changed['rows'][0]['output']['answer']['evolution_position'] = 0.99
    with pytest.raises(ValueError, match='host capture'):
        selected.evaluate(replace(captured, packet=q.canonical(changed)))


def test_prompt_parser_and_support_configuration_change_actor_identity():
    actor = q.Actor.freeze(literal_actor, parse_position, {'prompt': 'first', 'purpose': 'TEST_ONLY'})
    changed = q.Actor.freeze(literal_actor, parse_position, {'prompt': 'second', 'purpose': 'TEST_ONLY'})
    assert actor.model_version != changed.model_version




def test_recording_lookup_and_test_only_permission_share_the_exact_capture(tmp_path):
    selected = mechanical_selection()
    captured = selected.capture()
    path = tmp_path / 'scores.jsonl'
    first = selected.record(captured, '2026-10-30T00:00:00Z', path)
    before = path.read_bytes()
    selected.record(captured, '2026-10-30T01:00:00Z', path)
    assert path.read_bytes().startswith(before)
    assert first['qualification']['capture_digest'] == captured.digest
    bound = q.Resolver(((selected, captured),), path, allow_test_only=True)
    assert bound.permission('evolution-judge', selected.actor.model_version).granted
    assert not q.Resolver(((selected, captured),), path).permission(
        'evolution-judge', selected.actor.model_version).granted
    row = json.loads(path.read_text().splitlines()[-1])
    row['qualification']['capture_digest'] = 'foreign capture'
    with path.open('a') as stream:
        stream.write(json.dumps(row) + '\n')
    assert not bound.permission('evolution-judge', selected.actor.model_version).granted


def test_development_exposure_and_absent_approval_refuse_even_a_perfect_score(tmp_path):
    selected = q.Selection.freeze(q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'}),
                                  population(), basis_holds)
    captured = selected.capture()
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path)
    permission = q.Resolver(((selected, captured),), path, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version)
    assert not permission.granted
    assert 10 in {condition.item for condition in permission.refusals}


def test_unknown_actor_cannot_borrow_incumbent_facts_or_other_head_readings(tmp_path):
    path = tmp_path / 'scores.jsonl'
    path.write_text(json.dumps({'skill': 'evolution-judge', 'model_version': 'TEST_ONLY-unknown',
        'score': 1.0, 'threshold': 0.75, 'attributable_rate': 1.0,
        'measured_count': 12, 'min_items': 12, 'total': 12}) + '\n')
    assert not q.Resolver((), path).permission('evolution-judge', 'TEST_ONLY-unknown').granted


def test_a_later_process_imports_only_the_protected_catalogues_exact_bundle(tmp_path):
    selected = mechanical_selection()
    captured = selected.capture()
    scores = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', scores)
    bundle = selected.archive(captured)
    (tmp_path / 'capture.json').write_bytes(bundle)
    catalogue = q.canonical({'schema': 'twin.qualification-registry/v1', 'entries': [
        {'bundle': 'capture.json', 'sha256': hashlib.sha256(bundle).hexdigest()}]})
    anchor = hashlib.sha256(catalogue).hexdigest()
    path = tmp_path / 'catalogue.json'
    path.write_bytes(catalogue)
    restored = q.Resolver.from_catalogue(path, anchor, scores, allow_test_only=True)
    assert restored.permission('evolution-judge', selected.actor.model_version).granted
    assert not q.Resolver.from_catalogue(path, anchor, scores).permission(
        'evolution-judge', selected.actor.model_version).granted
    (tmp_path / 'capture.json').write_bytes(bundle + b' ')
    with pytest.raises(ValueError, match='bundle'):
        q.Resolver.from_catalogue(path, anchor, scores, allow_test_only=True)
    path.write_bytes(catalogue + b' ')
    with pytest.raises(ValueError, match='catalogue'):
        q.Resolver.from_catalogue(path, anchor, scores, allow_test_only=True)








@pytest.mark.parametrize('org', ['driftwood', 'tuppence', 'ludlow'])
def test_each_adopter_can_accept_only_a_host_bound_in_scope_judgement(tmp_path, org):
    selected, resolver, session = host_setup(tmp_path, host_inputs(org))
    result = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
    assert result.receipt and not result.reason
    doc = position_document(selected, session, result, org)
    assert resolver.check_claim_document(doc, 'github') == []
    doc['claims'][0]['evolution_position'] = 0.9
    assert any('host output' in reason for reason in resolver.check_claim_document(doc, 'github'))
    doc['claims'][0]['evolution_position'] = 0.25
    doc['claims'][0]['host_receipt'] = 'model supplied forged receipt'
    assert any('host receipt' in reason for reason in resolver.check_claim_document(doc, 'github'))


@pytest.mark.parametrize('change', [{'organisation': 'foreign-estate'}, {'domain': 'unrelated industry'},
    {'capability': 'foreign capability'}, {'frame': 'wrong axis'}, {'as_of': '2028-01-01'},
    {'source': 'foreign source'}, {'source_sha256': None}])
def test_scope_or_missing_provenance_refusals_are_counted_without_invoking(tmp_path, change):
    selected, resolver, session = host_setup(tmp_path, host_inputs(**change))
    result = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
    assert result.receipt is None and result.reason
    assert len(session.declines) == 1
    doc = {'run': {'clock': 'github', 'model_version': selected.actor.model_version,
                   'host_session': session.identity, 'declined': []}, 'claims': []}
    assert any('counted' in reason for reason in resolver.check_claim_document(doc, 'github'))


def test_a_model_provided_scope_cannot_replace_the_host_source_context(tmp_path):
    selected, resolver, session = host_setup(tmp_path, host_inputs('foreign-estate'))
    result = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
    doc = position_document(selected, session, result)
    doc['run']['scope'] = envelope()
    assert resolver.check_claim_document(doc, 'github')
    assert not result.receipt


def load_validator():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / '.claude/skills/classify-and-judge/assets/validate_claim.py'
    spec = importlib.util.spec_from_file_location('qualification_actual_validator', path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_actual_validator_uses_host_session_receipts_not_declared_model_scope(tmp_path):
    selected, resolver, session = host_setup(tmp_path, host_inputs())
    result = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
    doc = position_document(selected, session, result)
    validator = load_validator()
    _, check, lookup = validator.permission_rules('.', resolver=resolver)
    assert check(doc, 'github', lookup) == []
    doc['claims'][0]['host_subject'] = 'unrelated-input'
    assert any('host receipt' in reason for reason in check(doc, 'github', lookup))
    doc['claims'][0]['host_subject'] = 'live-one'
    doc['run']['host_session'] = 'response-created session'
    assert any('host session' in reason for reason in check(doc, 'github', lookup))
    assert check(doc, 'human', lookup) == check(doc, 'local', lookup) == []


def test_a_later_validator_accepts_only_an_independently_pinned_host_session(tmp_path):
    selected, resolver, session = host_setup(tmp_path, host_inputs())
    result = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
    doc = position_document(selected, session, result)
    # The host pins both archives after its real invocation. No ephemeral key is exported.
    captured = selected.capture()
    # Select the exact recorded capture again; deterministic bytes have the same identity.
    bundle = selected.archive(captured)
    (tmp_path / 'selection.json').write_bytes(bundle)
    archived = session.archive()
    (tmp_path / 'session.json').write_bytes(archived)
    catalogue = q.canonical({'schema': 'twin.qualification-registry/v1',
        'entries': [{'bundle': 'selection.json', 'sha256': hashlib.sha256(bundle).hexdigest()}],
        'sessions': [{'bundle': 'session.json', 'sha256': hashlib.sha256(archived).hexdigest()}]})
    path = tmp_path / 'catalogue.json'
    path.write_bytes(catalogue)
    restored = q.Resolver.from_catalogue(path, hashlib.sha256(catalogue).hexdigest(),
        tmp_path / 'scores.jsonl', allow_test_only=True)
    assert restored.check_claim_document(doc, 'github') == []
    import os
    import subprocess
    import sys
    from pathlib import Path
    child = subprocess.run([sys.executable, '-c',
        'import json,sys; from pathlib import Path; from twin.qualification import Resolver; '
        'r=Resolver.from_catalogue(Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3]),allow_test_only=True); '
        'print(json.dumps(r.check_claim_document(json.loads(sys.argv[4]), "github")))',
        str(path), hashlib.sha256(catalogue).hexdigest(), str(tmp_path / 'scores.jsonl'), json.dumps(doc)],
        env={**os.environ, 'PYTHONPATH': str(Path(__file__).parent) + os.pathsep + str(Path(__file__).parents[1])},
        text=True, capture_output=True)
    assert child.returncode == 0, child.stderr
    assert json.loads(child.stdout) == []
    (tmp_path / 'session.json').write_bytes(archived.replace(b'live-one', b'live-two'))
    with pytest.raises(ValueError, match='session bundle'):
        q.Resolver.from_catalogue(path, hashlib.sha256(catalogue).hexdigest(),
            tmp_path / 'scores.jsonl', allow_test_only=True)


def test_the_complete_existing_validator_accepts_a_bound_signal_and_refuses_changed_provenance(tmp_path):
    selected = signal_selection()
    captured = selected.capture()
    scores = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', scores)
    resolver = q.Resolver(((selected, captured),), scores, allow_test_only=True)
    payload = {'statement': 'social TEST_ONLY live headline', 'source': 'TEST_ONLY fixture',
               'candidates': [{'id': 'delivery', 'name': 'delivery'}]}
    source = source_record(q.canonical(payload), 'TEST_ONLY', 'v1')
    pin = {'party': 'feeds', 'kind': 'feed', 'name': 'TEST_ONLY', 'version': '1'}
    signal_metadata = {'id': 'live-one', 'date': '2026-10-30', 'from': pin,
                       'provenance': {'url': 'https://example.invalid/TEST_ONLY'}}
    context = {'organisation': 'driftwood', 'domain': 'estate cloud', 'capability': 'delivery',
        'as_of': '2026-10-30', 'frame': 'TEST_ONLY Wardley axis', 'source': 'TEST_ONLY',
        'source_sha256': source['sha256'], 'component': 'delivery', 'signal': signal_metadata}
    session = resolver.host_session(q.HostInputs.freeze(({'subject': 'live-one', 'input': payload,
        'source': source, 'context': context, 'issuer': 'TEST_ONLY-loader'},), ('TEST_ONLY-loader',)))
    result = session.judge('signal-classify', selected.actor.model_version, 'live-one')
    assert result.receipt, result.reason
    doc = {'schema': 'twin.headline-claim/v1', 'org': 'driftwood', 'derived_from': [pin],
        'run': {'skill': 'classify-and-judge', 'operator_role': 'TEST_ONLY-role', 'clock': 'github',
                'model_version': selected.actor.model_version, 'host_session': session.identity, 'declined': []},
        'claims': [{'id': 'c1', 'kind': 'binding', 'component': 'delivery', 'evidence_grade': 5,
            'claimed_by': 'signal-classify (skill)', 'evidence': payload['statement'], 'price_eligible': False,
            'host_receipt': result.receipt, 'host_subject': 'live-one', 'signal': {
                **signal_metadata, 'statement': payload['statement'], 'source': payload['source'], 'steep': 'social'}}]}
    validator = load_validator()
    _, check, lookup = validator.permission_rules('.', resolver=resolver)
    assert validator.validate(doc, ('binding', 'position', 'override'), {'TEST_ONLY-role'},
                              clock='github', permission=(check, lookup)) == []
    doc['claims'][0]['signal']['provenance'] = {'url': 'https://example.invalid/foreign-source'}
    assert any('host' in reason for reason in validator.validate(doc, ('binding',), {'TEST_ONLY-role'},
        clock='github', permission=(check, lookup)))


@pytest.mark.parametrize('actor_fn', [intermittent_actor, failing_actor])
def test_failed_candidate_items_remain_in_the_frozen_denominator_with_actual_raw_availability(actor_fn):
    selected = mechanical_selection(actor_fn)
    captured = selected.capture()
    result = selected.evaluate(captured)
    rows = json.loads(captured.packet)['rows']
    assert len(rows) == len(result.items) == 12
    assert result.score == 0.75
    assert sum(bool(row['output'].get('failure')) for row in rows) == 3
    failed = rows[0]['output']
    assert failed['raw_available'] is (actor_fn is intermittent_actor)
    if actor_fn is intermittent_actor:
        import base64
        assert base64.b64decode(failed['raw']) == b'invalid JSON retained literally'


def test_another_models_variance_cannot_rescue_a_constant_candidate_in_the_same_resolver(tmp_path):
    constant = mechanical_selection(constant_actor)
    varying = mechanical_selection()
    c1, c2 = constant.capture(), varying.capture()
    path = tmp_path / 'scores.jsonl'
    constant.record(c1, '2026-10-30T00:00:00Z', path)
    varying.record(c2, '2026-10-30T00:00:00Z', path)
    resolver = q.Resolver(((varying, c2), (constant, c1)), path, allow_test_only=True)
    assert resolver.permission('evolution-judge', varying.actor.model_version).granted
    refused = resolver.permission('evolution-judge', constant.actor.model_version)
    assert 8 in {condition.item for condition in refused.refusals}


def test_changed_support_source_revokes_the_binding_before_invocation_or_lookup(tmp_path):
    support = tmp_path / 'prompt.txt'
    support.write_text('first prompt')
    pop = population()
    actor = q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'}, support=(support,))
    selected = q.Selection.freeze(actor, pop, basis_holds, review=q.PopulationReview.test_only(pop))
    captured = selected.capture()
    scores = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', scores)
    resolver = q.Resolver(((selected, captured),), scores, allow_test_only=True)
    assert resolver.permission('evolution-judge', actor.model_version).granted
    support.write_text('changed prompt')
    with pytest.raises(ValueError, match='source changed'):
        actor.invoke({'position': 0.25, 'evidence': 'literal supplied witness'})
    assert not resolver.permission('evolution-judge', actor.model_version).granted


@pytest.mark.parametrize('missing', ['status', 'history', 'training_provenance'])
def test_missing_exposure_facts_refuse_even_an_explicit_test_only_review(tmp_path, missing):
    original = population()
    description = json.loads(original.description)
    description['exposure'].pop(missing)
    pop = q.Population(q.canonical(description))
    selected = q.Selection.freeze(q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'}),
        pop, basis_holds, review=q.PopulationReview.test_only(pop))
    captured = selected.capture()
    scores = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', scores)
    permission = q.Resolver(((selected, captured),), scores, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version)
    assert 10 in {condition.item for condition in permission.refusals}


def test_a_right_answer_on_a_foreign_basis_cannot_qualify(tmp_path):
    selected = mechanical_selection(wrong_basis_actor)
    captured = selected.capture()
    result = selected.evaluate(captured)
    assert result.wrong_basis == 12
    assert result.attributable_rate == 0.0
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path)
    assert not q.Resolver(((selected, captured),), path, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version).granted


def test_a_held_development_trace_can_be_reported_without_promoting_its_reference(tmp_path):
    from twin.reference_cases import admit_reference
    held_packet = json.loads(reference().packet_bytes)
    held_packet['case']['rights'] = {}
    held = admit_reference(held_packet['case'], held_packet['requested_scope'])
    assert not held.admitted
    pop = q.Population.held_development_trace('evolution-judge', (held,), envelope(),
        {'status': 'development', 'history': ['already exposed'], 'training_provenance': 'unknown'})
    selected = q.Selection.freeze(q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'}),
        pop, basis_holds, review=q.PopulationReview.test_only(pop))
    captured = selected.capture()
    result = selected.evaluate(captured)
    assert result.attributable_rate is None and result.unscoreable == 1
    assert json.loads(pop.description)['held'][0] == json.loads(held.packet_bytes)
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path)
    permission = q.Resolver(((selected, captured),), path, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version)
    assert 10 in {condition.item for condition in permission.refusals}


@pytest.mark.parametrize('metric,expected,literal', [
    ('signal-classify', {'steep': 'social', 'component': 'delivery'},
     {'steep': 'social', 'claim': {'component': 'delivery'}}),
    ('evolution-judge', {'evolution_position': 0.63}, {'evolution_position': 0.63}),
    ('causal-claims', {'sign': 'positive', 'lag_days': 90, 'elasticity_mode': 0.4, 'evidence_grade': 3},
     {'edge': {'sign': 'positive', 'lag_days': 90, 'elasticity': {'mode': 0.4}, 'evidence_grade': 3}}),
    ('causal-claims-grade-accuracy', {'evidence_grade': 2}, {'edge': {'evidence_grade': 2}}),
    ('gameplay-lens', {'opportunities': [['play-a', 'delivery']]},
     {'opportunities': [{'play': 'play-a', 'component': 'delivery'}]}),
    ('ethics-gate', {'admitted': False, 'stopped_at': 'purpose'},
     {'admitted': False, 'ladder': {'stopped_at': 'purpose'}}),
])
def test_each_reference_projection_uses_the_existing_scorers_answer_shape(metric, expected, literal):
    assert q.project_reference(metric, expected) == literal
    assert rss.scorer_for(metric)(literal, expected)


def test_substrate_reference_projection_meets_declared_constraints_without_claiming_generation_quality():
    expected = {'channels': ['chat', 'mail'], 'planted_signals': ['one'], 'min_mundane_fraction': 0.8}
    assert rss.scorer_for('substrate-generator')(q.project_reference('substrate-generator', expected), expected)


def test_historical_smoke_import_requires_the_host_held_manifest_pin(tmp_path):
    from twin.development_capture import import_smoke
    (tmp_path / 'EVIDENCE-MANIFEST.json').write_text('{"files": []}')
    with pytest.raises(ValueError, match='host.*manifest'):
        import_smoke(tmp_path, 'foreign digest', tmp_path / 'corpus.json', tmp_path / 'smoke.py')


def test_replay_parser_retains_actual_free_text_basis_without_fabricating_witnesses():
    from twin.development_capture import parse_smoke_signal
    raw = b'{"steep":"technological","component":"delivery","basis":"actual free text"}<|im_end|>'
    assert parse_smoke_signal(raw, {}) == Stated(
        {'steep': 'technological', 'claim': {'component': 'delivery'}}, 'actual free text')
    with pytest.raises(ValueError):
        parse_smoke_signal(b'{"expected": {"steep": "technological"}}', {})


def test_separate_custody_review_keeps_unknown_pretraining_disclosed_and_test_only_isolation(tmp_path):
    selected = reviewed_mechanical_selection()
    captured = selected.capture()
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path)
    assert q.Resolver(((selected, captured),), path, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version).granted
    assert not q.Resolver(((selected, captured),), path).permission(
        'evolution-judge', selected.actor.model_version).granted


@pytest.mark.parametrize('change', [
    {'issuer': 'a model supplied custodian name'}, {'population_digest': 'another population'},
    {'authority': ''}, {'coverage': ['driftwood', 'tuppence']},
    {'source_family_split': {'qualification_groups': [], 'development_groups': ['TEST_ONLY-0']}},
])
def test_missing_or_foreign_population_custody_does_not_turn_a_score_into_permission(tmp_path, change):
    selected = reviewed_mechanical_selection(change)
    captured = selected.capture()
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path)
    permission = q.Resolver(((selected, captured),), path, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version)
    assert 10 in {condition.item for condition in permission.refusals}


def test_actual_host_runtime_observations_must_match_the_immutable_invocation_contract():
    payload = {'position': 0.25, 'evidence': 'literal supplied witness'}
    actor = q.Actor.freeze(observed_runtime_actor, parse_position, {'purpose': 'TEST_ONLY',
        'runtime_contract': {'build': 'TEST_ONLY observed build-A'}})
    observed = actor.invoke(payload)
    assert not observed.failure
    assert json.loads(observed.packet)['observed_runtime'] == {'build': 'TEST_ONLY observed build-A'}
    changed = q.Actor.freeze(observed_runtime_actor, parse_position, {'purpose': 'TEST_ONLY',
        'runtime_contract': {'build': 'TEST_ONLY build-B'}})
    assert 'runtime' in changed.invoke(payload).failure


def test_response_identity_strings_cannot_supply_missing_host_runtime_observations():
    actor = q.Actor.freeze(literal_actor, parse_position,
        {'purpose': 'candidate invocation', 'runtime_contract': {'build': 'declared build'}})
    output = actor.invoke({'position': 0.25, 'evidence': 'literal supplied witness',
                           'model_version': 'claimed model', 'runtime': {'build': 'declared build'}})
    assert output.failure and 'host runtime' in output.failure


@pytest.mark.parametrize('runner,parser', [(defaulted_runner, parse_position),
    (literal_actor, defaulted_parser), (nested_default_runner, keyword_default_parser)])
def test_unchanged_defaulted_module_adapters_invoke_the_actual_callable(runner, parser):
    actor = q.Actor.freeze(runner, parser, {'purpose': 'TEST_ONLY'})
    output = actor.invoke({'position': 0.25, 'evidence': 'literal supplied witness'})
    assert not output.failure
    assert output.stated == Stated({'evolution_position': 0.25}, 'literal supplied witness')


def test_defaulted_runner_parser_basis_and_custody_checker_restore_in_a_separate_process(tmp_path):
    import subprocess
    import sys
    selected = defaulted_selection()
    captured = selected.capture()
    scores = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', scores)
    resolver = q.Resolver(((selected, captured),), scores, allow_test_only=True)
    assert resolver.permission('evolution-judge', selected.actor.model_version).granted
    bundle = selected.archive(captured)
    (tmp_path / 'selection.json').write_bytes(bundle)
    catalogue = q.canonical({'schema': 'twin.qualification-registry/v1', 'entries': [
        {'bundle': 'selection.json', 'sha256': hashlib.sha256(bundle).hexdigest()}]})
    path = tmp_path / 'catalogue.json'
    path.write_bytes(catalogue)
    child = subprocess.run([sys.executable, '-c',
        'import json,sys; from pathlib import Path; from twin.qualification import Resolver; '
        'r=Resolver.from_catalogue(Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3]),allow_test_only=True); '
        'print(json.dumps(r.permission("evolution-judge",sys.argv[4]).granted))',
        str(path), hashlib.sha256(catalogue).hexdigest(), str(scores), selected.actor.model_version],
        text=True, capture_output=True)
    assert child.returncode == 0, child.stderr
    assert json.loads(child.stdout) is True


@pytest.mark.parametrize('target,attribute,replacement', [
    (defaulted_runner, '__defaults__', (0.25,)),
    (keyword_default_parser, '__kwdefaults__', {'keys': {'position': ('evidence',), 'basis': ['position']}}),
    (defaulted_basis_checker, '__defaults__', (('foreign-prefix',),)),
    (defaulted_review_checker, '__kwdefaults__', {'issuer': ('foreign-custodian',)}),
    (defaulted_reference_projection, '__defaults__', ((2,),)),
    (defaulted_runner, '__code__', changed_defaulted_runner.__code__),
])
def test_actual_default_or_code_mutations_revoke_the_frozen_selection(tmp_path, target, attribute, replacement):
    selected = defaulted_selection()
    captured = selected.capture()
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path)
    resolver = q.Resolver(((selected, captured),), path, allow_test_only=True)
    assert resolver.permission('evolution-judge', selected.actor.model_version).granted
    original = getattr(target, attribute)
    try:
        setattr(target, attribute, replacement)
        assert not resolver.permission('evolution-judge', selected.actor.model_version).granted
    finally:
        setattr(target, attribute, original)


def test_nested_mutable_default_values_and_tuple_list_types_remain_identity_relevant():
    import copy
    actor = q.Actor.freeze(nested_default_runner, parse_position, {'purpose': 'TEST_ONLY'})
    original = nested_default_runner.__defaults__
    try:
        changed = copy.deepcopy(original)
        changed[0][1]['fallback'][0] = 0.25
        nested_default_runner.__defaults__ = changed
        with pytest.raises(ValueError, match='adapter changed'):
            actor.invoke({'position': 0.25, 'evidence': 'literal'})
        nested_default_runner.__defaults__ = ([0, {'fallback': [0]}],)
        with pytest.raises(ValueError, match='adapter changed'):
            actor.invoke({'position': 0.25, 'evidence': 'literal'})
    finally:
        nested_default_runner.__defaults__ = original


def test_a_signed_zero_default_change_cannot_hide_behind_python_numeric_equality():
    original = defaulted_runner.__defaults__
    try:
        defaulted_runner.__defaults__ = (-0.0,)
        actor = q.Actor.freeze(defaulted_runner, parse_position, {'purpose': 'TEST_ONLY'})
        assert b'-0.0' in actor.invoke({'position': -0.0, 'evidence': 'literal'}).raw
        defaulted_runner.__defaults__ = (0.0,)
        with pytest.raises(ValueError, match='adapter changed'):
            actor.invoke({'position': -0.0, 'evidence': 'literal'})
    finally:
        defaulted_runner.__defaults__ = original
