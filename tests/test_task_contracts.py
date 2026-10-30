"""CASE-FREE task shapes and independently frozen rubrics."""
import pytest


def test_task_contract_shapes_reject_bool_magnitude_and_invalid_dates():
    from twin.task_contracts import TaskContract, validate, decode
    contract = TaskContract.freeze('causal')
    assert contract.metrics == ('causal-claims', 'causal-claims-grade-accuracy')
    contract.verify()
    validate('Pert', {'min': 0, 'mode': .5, 'max': 1})
    for bad in ({'min': False, 'mode': .5, 'max': 1}, {'min': 0, 'mode': 2, 'max': 1}):
        with pytest.raises(ValueError):
            validate('Pert', bad)
    with pytest.raises(ValueError):
        validate('PublicContext', {'as_of': '2026-02-30'})
    for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'```{}', b'{} {}', b'"\xff"'):
        with pytest.raises(ValueError):
            decode(raw)


def test_task_review_uses_exact_metric_dimensions_and_typed_value_witness(tmp_path):
    import hashlib
    from twin import qualification as q
    from twin.basis_assessment import BasisPolicy, ReviewStore
    policy = BasisPolicy.for_task('evolution', 'evolution-judge', ('TEST_ONLY-review',))
    assert policy.dimensions == ('witness', 'applicability', 'position_support', 'temporal_frame')
    original = {'id': 'TEST_ONLY-one', 'input': {'coordinate': .25}, 'context': {}, 'sources': {},
                'output': {'answer': {'evolution_position': .25}, 'basis': {'reason': 'TEST_ONLY'}}}
    request = q.canonical({'rows': [original]})
    record = {'schema': 'twin.task-basis-assessment/v2', 'policy_digest': policy.digest,
        'request_digest': hashlib.sha256(request).hexdigest(), 'issuer': 'TEST_ONLY-review', 'rows': [{
        'id': original['id'], 'subject_digest': q.digest(original), 'reason': 'TEST_ONLY retained review control',
        'decisions': {name: 'pass' for name in policy.dimensions}, 'support': {name: {
            'reason': 'TEST_ONLY value identity, not semantic proof',
            'witnesses': [{'path': ['input', 'coordinate'], 'value': .25}]} for name in policy.dimensions}}]}
    raw = q.canonical(record)
    (tmp_path / 'record.json').write_bytes(raw)
    store = {'schema': 'twin.semantic-review-store/v1', 'entries': [{
        'request': hashlib.sha256(request).hexdigest(), 'record': 'record.json', 'sha256': hashlib.sha256(raw).hexdigest(),
        'issuer': 'TEST_ONLY-review', 'authority': 'TEST_ONLY', 'provenance': 'TEST_ONLY independent artifact'}]}
    path = tmp_path / 'store.json'
    path.write_bytes(q.canonical(store))
    assessment = ReviewStore(path, hashlib.sha256(path.read_bytes()).hexdigest()).assess(policy, request)
    assert assessment.outcome(original['id']) is True
    policy.verify()
    with pytest.raises(ValueError):
        BasisPolicy.for_task('evolution', 'causal-claims', ('TEST_ONLY-review',))


@pytest.mark.parametrize('metric', ['causal-claims', 'causal-claims-grade-accuracy'])
def test_causal_review_dimensions_do_not_borrow_each_others_support(metric):
    from twin.basis_assessment import BasisPolicy
    policy = BasisPolicy.for_task('causal', metric, ('TEST_ONLY-review',))
    assert ('grade_support' in policy.dimensions) == (metric == 'causal-claims-grade-accuracy')
    assert ('elasticity_support' in policy.dimensions) == (metric == 'causal-claims')


def test_remaining_task_metric_cannot_omit_protected_contract_and_policy():
    from twin import qualification as q
    from bench.qualification_controls import mechanical_selection, basis_holds
    original = mechanical_selection()
    with pytest.raises(ValueError, match='protected task'):
        q.Selection.freeze(original.actor, original.population, basis_holds, review=original.review)
