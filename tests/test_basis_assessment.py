"""Independent TEST_ONLY assessment receipts exercise mechanics, not semantic calibration."""
import pytest
import hashlib
import json
from twin import qualification as q
from twin.basis_assessment import BasisPolicy, ReviewStore
from bench.qualification_controls import mechanical_selection, basis_holds, host_inputs, position_document
from twin.skills import Stated, evaluate


@pytest.mark.parametrize('held,verdict', [(True, 'right'), (False, 'wrong-basis'), (None, 'unscoreable')])
def test_contextual_assessment_preserves_three_basis_outcomes(held, verdict):
    seen = []
    def assess(item_id, actual, reference):
        seen.append((item_id, actual))
        return held
    stated = Stated({'evolution_position': .5}, {'reason': 'TEST_ONLY actual witness'})
    result = evaluate('evolution-judge', lambda _: stated,
        [{'id': 'TEST_ONLY-one', 'input': {}, 'expected': stated.answer, 'basis': {'hidden': 'reference'}}],
        contextual_basis_scorer=assess)
    assert result.items[0].verdict == verdict
    assert seen == [('TEST_ONLY-one', stated)]


def reviewed_store(tmp_path, policy, request, decision='pass'):
    """Authored review-control receipt; never an actual independent semantic assessment."""
    value = json.loads(request)
    record = {'policy': policy.digest, 'request': hashlib.sha256(request).hexdigest(),
        'issuer': 'TEST_ONLY-independent-review', 'rows': [
            {'id': row['id'], 'subject_digest': q.digest(row),
             'decisions': {name: decision for name in ('witness', 'steep', 'binding', 'applicability')},
             'support': {name: {'reason': 'TEST_ONLY control fact, not semantic calibration',
                 'witnesses': [{'path': ['input', 'evidence'], 'quote': row['input']['evidence']}]}
                 for name in ('witness', 'steep', 'binding', 'applicability')},
             'reason': 'TEST_ONLY independently authored receipt mechanics'} for row in value['rows']]}
    raw = q.canonical(record)
    (tmp_path / 'review.json').write_bytes(raw)
    store = {'schema': 'twin.semantic-review-store/v1', 'entries': [{
        'request': record['request'], 'record': 'review.json', 'sha256': hashlib.sha256(raw).hexdigest(),
        'issuer': 'TEST_ONLY-independent-review',
        'authority': 'TEST_ONLY control authority', 'provenance': 'TEST_ONLY authored receipt, not model execution'}]}
    path = tmp_path / 'reviews.json'
    path.write_bytes(q.canonical(store))
    return ReviewStore(path, hashlib.sha256(path.read_bytes()).hexdigest())


def assessed_selection():
    original = mechanical_selection()
    policy = BasisPolicy.freeze({'claim': 'TEST_ONLY semantics; no real qualification'},
        ('TEST_ONLY-independent-review',))
    return q.Selection.freeze(original.actor, original.population, basis_holds,
        review=original.review, assessment_policy=policy)


def test_exact_independent_assessment_controls_the_actual_capture_evaluation(tmp_path):
    selected = assessed_selection()
    captured = selected.capture()
    request = selected.assessment_request(captured)
    assert 'expected' not in json.loads(request)['rows'][0]
    assert 'basis' not in json.loads(request)['rows'][0]['input']
    with pytest.raises(ValueError, match='assessment'):
        selected.facts(captured)
    assessment = reviewed_store(tmp_path, selected.assessment_policy, request).assess(selected.assessment_policy, request)
    assert selected.evaluate(captured, assessment).attributable_rate == 1.0
    assert selected.facts(captured, assessment)['assessment_digest'] == assessment.digest


def test_assessment_identity_is_preserved_by_record_lookup_and_protected_import(tmp_path):
    selected = assessed_selection()
    captured = selected.capture()
    request = selected.assessment_request(captured)
    assessment = reviewed_store(tmp_path, selected.assessment_policy, request).assess(selected.assessment_policy, request)
    scores = tmp_path / 'scores.jsonl'
    row = selected.record(captured, '2026-10-30T00:00:00Z', scores, assessment)
    assert row['qualification']['assessment_digest'] == assessment.digest
    resolver = q.Resolver(((selected, captured, assessment),), scores, allow_test_only=True)
    assert resolver.permission('evolution-judge', selected.actor.model_version).granted
    bundle = selected.archive(captured, assessment)
    (tmp_path / 'qualified.json').write_bytes(bundle)
    path = tmp_path / 'registry.json'
    path.write_bytes(q.canonical({'schema': 'twin.qualification-registry/v1', 'entries': [
        {'bundle': 'qualified.json', 'sha256': hashlib.sha256(bundle).hexdigest()}]}))
    restored = q.Resolver.from_catalogue(path, hashlib.sha256(path.read_bytes()).hexdigest(), scores,
        allow_test_only=True)
    assert restored.permission('evolution-judge', selected.actor.model_version).granted


@pytest.mark.parametrize('decision,verdict', [('fail', 'wrong-basis'), ('held', 'unscoreable')])
def test_a_real_quote_is_not_semantic_assessment_permission(tmp_path, decision, verdict):
    selected = assessed_selection()
    captured = selected.capture()
    request = selected.assessment_request(captured)
    assessment = reviewed_store(tmp_path, selected.assessment_policy, request, decision).assess(selected.assessment_policy, request)
    assert selected.evaluate(captured, assessment).items[0].verdict == verdict
    scores = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', scores, assessment)
    assert not q.Resolver(((selected, captured, assessment),), scores, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version).granted


def test_forged_or_foreign_assessment_cannot_reuse_positive_cache(tmp_path):
    from dataclasses import replace
    selected = assessed_selection()
    captured = selected.capture()
    request = selected.assessment_request(captured)
    assessment = reviewed_store(tmp_path, selected.assessment_policy, request).assess(selected.assessment_policy, request)
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path, assessment)
    resolver = q.Resolver(((selected, captured, assessment),), path, allow_test_only=True)
    assert resolver.permission('evolution-judge', selected.actor.model_version).granted
    value = json.loads(assessment.packet)
    value['record']['rows'][0]['reason'] = 'forged model assertion'
    forged = replace(assessment, packet=q.canonical(value))
    with pytest.raises(ValueError, match='protected host'):
        selected.evaluate(captured, forged)
    assert not q.Resolver(((selected, captured),), path, allow_test_only=True).permission(
        'evolution-judge', selected.actor.model_version).granted
    other = json.loads(request)
    other['rows'][0]['context']['frame'] = 'foreign frame'
    with pytest.raises(ValueError, match='foreign'):
        assessment.verify(selected.assessment_policy, q.canonical(other))


def test_review_acquisition_requires_a_host_held_store_pin(tmp_path):
    path = tmp_path / 'root-looking.json'
    path.write_text('{"schema":"twin.semantic-review-store/v1","entries":[]}')
    with pytest.raises(ValueError, match='digest'):
        ReviewStore(path, 'model-supplied-issuer-is-not-authority')


@pytest.mark.parametrize('change', ['wrong issuer', 'nonexistent witness', 'malformed witness', 'missing case'])
def test_authenticated_acquisition_still_requires_correct_complete_review_facts(tmp_path, change):
    selected = assessed_selection()
    capture = selected.capture()
    request = selected.assessment_request(capture)
    reviewed_store(tmp_path, selected.assessment_policy, request)
    record = json.loads((tmp_path / 'review.json').read_bytes())
    store = json.loads((tmp_path / 'reviews.json').read_bytes())
    if change == 'wrong issuer':
        store['entries'][0]['issuer'] = 'a different acquired reviewer'
    elif change == 'nonexistent witness':
        record['rows'][0]['support']['witness']['witnesses'][0]['quote'] = 'absent actual witness'
    elif change == 'malformed witness':
        record['rows'][0]['support']['witness']['witnesses'] = [None]
    else:
        record['rows'].pop()
    raw = q.canonical(record)
    (tmp_path / 'review.json').write_bytes(raw)
    store['entries'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
    path = tmp_path / 'reviews.json'
    path.write_bytes(q.canonical(store))
    acquired = ReviewStore(path, hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError):
        acquired.assess(selected.assessment_policy, request)


def test_live_judgement_waits_for_exact_independent_assessment_without_reinference(tmp_path):
    selected = assessed_selection()
    capture = selected.capture()
    qualification = tmp_path / 'qualification'
    qualification.mkdir()
    request = selected.assessment_request(capture)
    assessment = reviewed_store(qualification, selected.assessment_policy, request).assess(selected.assessment_policy, request)
    scores = tmp_path / 'scores.jsonl'
    selected.record(capture, '2026-10-30T00:00:00Z', scores, assessment)
    resolver = q.Resolver(((selected, capture, assessment),), scores, allow_test_only=True)
    session = resolver.host_session(host_inputs())
    missing = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
    assert missing.receipt is None and len(session.declines) == 1
    pending = session.pending_reviews[0]
    forged = json.loads(session.archive())
    original_record = next(iter(forged['pending_reviews'].values()))
    original_record['output']['actor_digest'] = 'a model-written false actor'
    forged_request = json.loads(q.canonical(pending['request']))
    forged_request['rows'][0]['output'] = original_record['output']
    forged_request['capture_digest'] = q.digest(original_record)
    forged['pending_reviews'] = {q.digest(forged_request): original_record}
    with pytest.raises(ValueError, match='host binding'):
        q.HostSession.restore(q.canonical(forged), resolver)
    live = tmp_path / 'live'
    live.mkdir()
    store = reviewed_store(live, selected.assessment_policy, q.canonical(pending['request']))
    accepted = session.review_pending(pending['request_digest'], store)
    assert accepted.receipt and accepted.output.raw == b'{"position": 0.25, "evidence": "literal supplied witness"}'
    doc = position_document(selected, session, accepted)
    assert resolver.check_claim_document(doc, 'github') == []
