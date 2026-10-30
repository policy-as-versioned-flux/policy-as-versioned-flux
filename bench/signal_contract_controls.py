"""Authored TEST_ONLY signal/review mechanics; never genuine reference or reviewer authority."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from twin import qualification as q
from twin.basis_assessment import BasisPolicy, ReviewStore
from twin.signal_candidate import parse
from twin.reference_cases import admit_reference, binding_for, source_record
from bench.qualification_controls import reference, envelope, basis_holds


def choices():
    return [{'id': f'TEST_ONLY-{i}', 'name': f'Choice {i}',
        'definition': {'id': f'TEST_ONLY-{i}', 'name': f'Choice {i}',
                       'description': f'TEST_ONLY choice meaning {i}'}} for i in range(20)]


def model_context():
    from twin import signal_inputs
    return {'candidate_universe_digest': q.digest(choices()), 'model_pins': {'TEST_ONLY': 'fixture-model-pins'},
            'model_as_of': '2026-10-30',
            'input_construction_sha256': hashlib.sha256(Path(signal_inputs.__file__).read_bytes()).hexdigest()}


def signal_input(statement, organisation):
    return {'statement': statement, 'source': 'TEST_ONLY', 'candidates': choices(),
        'model_context': {'organisation': organisation, 'domain': 'estate cloud', 'capability': 'delivery',
            'frame': 'TEST_ONLY Wardley axis', 'as_of': '2026-10-30', 'pins': model_context()['model_pins']},
        'source_context': {'url': 'https://test.invalid/fixture', 'version': 'v1', 'family': 'TEST_ONLY',
            'excerpts': [statement], 'publication_date': '2026-10-30', 'as_of': '2026-10-30',
            'original_source_manifest_digest': 'TEST_ONLY', 'original_sources': {'literal': {
                'identity': 'https://test.invalid/fixture', 'version': 'v1', 'bytes': 1, 'sha256': 'TEST_ONLY'}}}}


def signal_actor(payload, config):
    component = payload['statement'].split()[1]
    selected = next(item for item in payload['candidates'] if item['id'] == component)
    return q.canonical({'steep': payload['statement'].split()[0], 'component': component,
        'basis': {'statement_quotes': [payload['statement']], 'component_quotes': [selected['name']],
                  'reason': 'TEST_ONLY literal fixture lookup; no semantic competence claim'}})


def selection():
    admissions = []
    for index in range(16):
        packet = json.loads(reference(case_id=f'TEST_ONLY-signal-contract-{index}',
            org=('driftwood', 'tuppence', 'ludlow')[index % 3]).packet_bytes)
        case, scope = packet['case'], packet['requested_scope']
        scope['metric'] = 'signal-classify'
        case['context'] = scope
        steep = 'social' if index % 2 else 'economic'
        case['input'] = signal_input(f'{steep} TEST_ONLY-{index} authored fixture {index}', scope['organisation'])
        case['expected'] = {'steep': steep, 'component': f'TEST_ONLY-{index}'}
        support = case['field_support']['evolution_position']
        case['field_support'] = {'steep': support, 'component': support}
        case['basis']['witness'] = 'TEST_ONLY reference; assessed independently in this control'
        case['basis_binding'] = binding_for(case)
        admitted = admit_reference(case, scope)
        assert admitted.admitted, admitted.reasons
        admissions.append(admitted)
    scope_envelope = envelope()
    scope_envelope['signal_contexts'] = {org: model_context() for org in scope_envelope['adopters']}
    pop = q.Population.freeze('signal-classify', tuple(admissions), scope_envelope,
        {'status': 'development', 'history': ['TEST_ONLY openly authored'], 'training_provenance': 'unknown'})
    policy = BasisPolicy.freeze({'claim': 'TEST_ONLY review mechanics'}, ('TEST_ONLY-independent-review',))
    return q.Selection.freeze(q.Actor.freeze(signal_actor, parse, {'purpose': 'TEST_ONLY'}),
        pop, basis_holds, review=q.PopulationReview.test_only(pop), assessment_policy=policy)


def review_store(path: Path, policy: BasisPolicy, request: bytes, decision: str = 'pass') -> ReviewStore:
    path.mkdir(parents=True, exist_ok=True)
    value = json.loads(request)
    record = {'policy': policy.digest, 'request': hashlib.sha256(request).hexdigest(),
        'issuer': 'TEST_ONLY-independent-review', 'rows': [{'id': row['id'], 'subject_digest': q.digest(row),
        'decisions': {name: decision for name in ('witness', 'steep', 'binding', 'applicability')},
        'support': {name: {'reason': 'TEST_ONLY actual fixture witness; no semantic competence claim',
            'witnesses': [{'path': ['input', 'statement'], 'quote': row['input']['statement']}]}
            for name in ('witness', 'steep', 'binding', 'applicability')},
        'reason': 'TEST_ONLY authored independent-receipt control, not real model review'} for row in value['rows']]}
    raw = q.canonical(record)
    (path / 'record.json').write_bytes(raw)
    store = {'schema': 'twin.semantic-review-store/v1', 'entries': [{'request': record['request'],
        'record': 'record.json', 'sha256': hashlib.sha256(raw).hexdigest(),
        'issuer': 'TEST_ONLY-independent-review',
        'authority': 'TEST_ONLY control authority', 'provenance': 'TEST_ONLY authored, not a reviewer call'}]}
    raw = q.canonical(store)
    (path / 'store.json').write_bytes(raw)
    return ReviewStore(path / 'store.json', hashlib.sha256(raw).hexdigest())


def inputs():
    payload = signal_input('social TEST_ONLY-19 literal supplied witness', 'driftwood')
    source = source_record(q.canonical(payload), 'TEST_ONLY', 'v1')
    context = {'organisation': 'driftwood', 'domain': 'estate cloud', 'capability': 'delivery',
        'as_of': '2026-10-30', 'frame': 'TEST_ONLY Wardley axis', 'source': 'TEST_ONLY',
        'source_sha256': source['sha256'], 'eligible_components': [item['id'] for item in choices()],
        'candidate_universe_digest': q.digest(choices()), 'signal': {'id': 'TEST_ONLY-live',
            'date': '2026-10-30', 'from': {'party': 'TEST_ONLY', 'kind': 'feed', 'version': 'v1'},
            'provenance': {'url': 'https://test.invalid/fixture'}}}
    context.update(model_context())
    return q.HostInputs.freeze(({'subject': 'TEST_ONLY-live', 'input': payload, 'context': context,
        'source': source, 'issuer': 'TEST_ONLY-host'},), ('TEST_ONLY-host',))


def public_controls():
    from tempfile import TemporaryDirectory
    from twin.qualified_signals import SignalParent
    with TemporaryDirectory() as directory:
        root = Path(directory)
        selected = selection()
        capture = selected.capture()
        request = selected.assessment_request(capture)
        assert selected.assessment_policy is not None
        assessment = review_store(root / 'qualification', selected.assessment_policy, request).assess(
            selected.assessment_policy, request)
        scores = root / 'scores.jsonl'
        selected.record(capture, '2026-10-30T00:00:00Z', scores, assessment)
        resolver = q.Resolver(((selected, capture, assessment),), scores, allow_test_only=True)
        run = SignalParent(resolver, selected.actor.model_version, clock='github').start(inputs())
        missing_refuses = run.document() is None and len(run.session.declines) == 1
        pending = run.session.pending_reviews[0]
        live_store = review_store(root / 'live', selected.assessment_policy, q.canonical(pending['request']))
        result = run.review(pending['request_digest'], live_store)
        accepted = bool(result.receipt) and not run.validate()
        selection_bundle, session_bundle = selected.archive(capture, assessment), run.session.archive()
        (root / 'selection.json').write_bytes(selection_bundle)
        (root / 'session.json').write_bytes(session_bundle)
        catalogue = q.canonical({'schema': 'twin.qualification-registry/v1',
            'entries': [{'bundle': 'selection.json', 'sha256': hashlib.sha256(selection_bundle).hexdigest()}],
            'sessions': [{'bundle': 'session.json', 'sha256': hashlib.sha256(session_bundle).hexdigest()}]})
        (root / 'catalogue.json').write_bytes(catalogue)
        restored = q.Resolver.from_catalogue(root / 'catalogue.json', hashlib.sha256(catalogue).hexdigest(),
            scores, allow_test_only=True)
        durable = not restored.check_claim_document(run.document(), 'github')
        default = q.Resolver(((selected, capture, assessment),), scores).permission(
            'signal-classify', selected.actor.model_version)
        absent = q.Resolver(((selected, capture),), scores, allow_test_only=True).permission(
            'signal-classify', selected.actor.model_version)
        return {'missing live independent assessment refused and counted': missing_refuses,
                'reviewed nonfirst-of20 TEST_ONLY binding passes actual validator': accepted,
                'durable actual basis/assessment/host receipt import accepted': durable,
                'default operational mode refuses TEST_ONLY semantic receipts': not default.granted,
                'missing qualification assessment cannot borrow recorded pass': not absent.granted}
