"""TEST_ONLY retained reviewer controls; no semantic expertise or target labels."""
import hashlib
import json

import pytest

from twin import qualification as q
from twin.basis_assessment import BasisPolicy, ReviewStore


def retained_review(tmp_path, policy, *, decision='pass', witness=None, mutate=None):
    original = {'id': 'TEST_ONLY-review', 'input': {'coordinate': 1, 'statement': 'TEST_ONLY retained text'},
                'context': {}, 'sources': {}, 'output': {'answer': {'evolution_position': .5}, 'basis': {'reason': 'TEST_ONLY'}}}
    request = q.canonical({'rows': [original]})
    row = {'id': original['id'], 'subject_digest': q.digest(original), 'reason': 'TEST_ONLY retained decision',
        'decisions': {name: decision for name in policy.dimensions}, 'support': {name: {
            'reason': 'TEST_ONLY witness membership does not establish entailment',
            'witnesses': [witness or {'path': ['input', 'coordinate'], 'value': 1}]} for name in policy.dimensions}}
    record = {'schema': 'twin.task-basis-assessment/v2', 'policy_digest': policy.digest,
              'request_digest': hashlib.sha256(request).hexdigest(), 'issuer': 'TEST_ONLY-review', 'rows': [row]}
    if mutate:
        mutate(record)
    raw = q.canonical(record); (tmp_path / 'review.json').write_bytes(raw)
    store = {'schema': 'twin.semantic-review-store/v1', 'entries': [{
        'request': hashlib.sha256(request).hexdigest(), 'record': 'review.json', 'sha256': hashlib.sha256(raw).hexdigest(),
        'issuer': 'TEST_ONLY-review', 'authority': 'TEST_ONLY artifact authority only', 'provenance': 'TEST_ONLY retained artifact'}]}
    path = tmp_path / 'store.json'; path.write_bytes(q.canonical(store))
    return ReviewStore(path, hashlib.sha256(path.read_bytes()).hexdigest()), request


@pytest.mark.parametrize(('decision', 'outcome'), [('pass', True), ('fail', False), ('held', None)])
def test_each_retained_task_review_conserves_pass_fail_held(tmp_path, decision, outcome):
    policy = BasisPolicy.for_task('evolution', 'evolution-judge', ('TEST_ONLY-review',))
    store, request = retained_review(tmp_path, policy, decision=decision)
    assert store.assess(policy, request).outcome('TEST_ONLY-review') is outcome


@pytest.mark.parametrize('witness', [
    {'path': ['input', 'coordinate'], 'value': True},
    {'path': ['input', 'coordinate'], 'value': 2},
    {'path': ['input', 'missing'], 'value': 1},
    {'path': ['output', 'answer', 'evolution_position'], 'value': .5},
    {'path': ['input', 'statement'], 'quote': 'foreign text'},
    {'path': ['input', 'statement'], 'quote': 'TEST_ONLY', 'value': 1},
])
def test_foreign_or_type_confused_witness_cannot_pass(tmp_path, witness):
    policy = BasisPolicy.for_task('evolution', 'evolution-judge', ('TEST_ONLY-review',))
    store, request = retained_review(tmp_path, policy, witness=witness)
    with pytest.raises(ValueError):
        store.assess(policy, request)


@pytest.mark.parametrize('mutation', ['missing-dimension', 'foreign-dimension', 'missing-support', 'extra-field', 'foreign-request', 'na'])
def test_task_review_cannot_drop_rubric_or_invent_applicability(tmp_path, mutation):
    policy = BasisPolicy.for_task('evolution', 'evolution-judge', ('TEST_ONLY-review',))
    def mutate(record):
        row = record['rows'][0]
        if mutation == 'missing-dimension':
            del row['decisions'][policy.dimensions[0]]
        elif mutation == 'foreign-dimension':
            row['decisions']['grade_support'] = 'pass'
        elif mutation == 'missing-support':
            del row['support'][policy.dimensions[0]]
        elif mutation == 'extra-field':
            record['expected'] = 'TEST_ONLY hidden reference injection'
        elif mutation == 'foreign-request':
            record['request_digest'] = '0' * 64
        else:
            row['decisions'][policy.dimensions[0]] = 'not-applicable'
    store, request = retained_review(tmp_path, policy, mutate=mutate)
    with pytest.raises(ValueError):
        store.assess(policy, request)
