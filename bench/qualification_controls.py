"""Explicit TEST_ONLY fixture adapters: software controls, never real qualification data."""
from __future__ import annotations
import json
import hashlib
from twin import qualification as q
from twin.skills import Stated
from twin.reference_cases import admit_reference, binding_for, source_record

def reference(position=0.25, case_id='TEST_ONLY-one', org='driftwood'):
    content = b'TEST_ONLY literal invented coordinate; no empirical authority'
    scope = {'purpose': 'development', 'claim': 'agent-reference-agreement',
             'metric': 'evolution-judge', 'domain': 'estate cloud', 'capability': 'delivery',
             'organisation': org, 'as_of': '2026-10-30', 'frame': 'TEST_ONLY Wardley axis'}
    case = {'id': case_id, 'group': case_id,
            'input': {'position': position, 'evidence': 'TEST_ONLY witness ' + case_id},
            'expected': {'evolution_position': position},
            'basis': {'source_hashes': {'literal': hashlib.sha256(content).hexdigest()},
                      'witness': 'TEST_ONLY witness ' + case_id},
            'context': scope, 'reference_kind': 'agent-authored',
            'sources': {'literal': source_record(content, 'TEST_ONLY', 'v1')},
            'rights': {'statement': 'TEST_ONLY authored fixture', 'evidence': ['literal'],
                       'uses': ['development'], 'covered_sources': ['literal']},
            'field_support': {'evolution_position': {'meaning': 'TEST_ONLY literal coordinate',
                'sources': ['literal'], 'witnesses': [{'source': 'literal', 'start': 0,
                    'end': len(content), 'sha256': hashlib.sha256(content).hexdigest()}]}},
            'selection': {'decision': 'selected', 'reason': 'TEST_ONLY before predictions'},
            'exposure': {'status': 'development', 'history': ['fixture authored openly']},
            'limitations': ['TEST_ONLY; proves software only']}
    case['basis_binding'] = binding_for(case)
    admission = admit_reference(case, scope)
    assert admission.admitted, admission.reasons
    return admission


def envelope():
    return {'adopters': ['driftwood', 'tuppence', 'ludlow'], 'domains': ['estate cloud'],
            'capabilities': ['delivery'], 'frames': ['TEST_ONLY Wardley axis'],
            'sources': ['TEST_ONLY'], 'from': '2026-10-01', 'until': '2026-12-31'}


def basis_holds(actual, expected):
    return actual == expected['witness']


def population(*, count=12):
    admissions = tuple(reference((i % 4) / 3, f'TEST_ONLY-{i}',
                       ('driftwood', 'tuppence', 'ludlow')[i % 3]) for i in range(count))
    return q.Population.freeze('evolution-judge', admissions, envelope(),
        {'status': 'development', 'history': ['all fixture labels exposed'],
         'training_provenance': 'unknown; no clean pretraining claim'})


def literal_actor(payload, config):
    return json.dumps({'position': payload['position'], 'evidence': payload['evidence']}).encode()


def parse_position(raw, config):
    value = json.loads(raw)
    return Stated({'evolution_position': value['position']}, value['evidence'])


def constant_actor(payload, config):
    return json.dumps({'position': 0.0, 'evidence': payload['evidence']}).encode()


def wrong_reference(metric, expected):
    return {'evolution_position': 0.5}


def mechanical_selection(actor_fn=literal_actor):
    pop = population()
    return q.Selection.freeze(q.Actor.freeze(actor_fn, parse_position, {'purpose': 'TEST_ONLY'}),
        pop, basis_holds, review=q.PopulationReview.test_only(pop), test_only=q.TEST_ONLY_MECHANICS)


def host_inputs(org='driftwood', **changes):
    payload = {'position': 0.25, 'evidence': 'literal supplied witness'}
    source = source_record(q.canonical(payload), 'TEST_ONLY', 'v1')
    context = {'organisation': org, 'domain': 'estate cloud', 'capability': 'delivery',
               'as_of': '2026-10-30', 'frame': 'TEST_ONLY Wardley axis',
               'source': 'TEST_ONLY', 'source_sha256': source['sha256'], 'component': 'delivery'}
    context.update(changes)
    return q.HostInputs.freeze(({'subject': 'live-one', 'input': payload, 'context': context,
                                 'source': source, 'issuer': 'TEST_ONLY-loader'},),
                               ('TEST_ONLY-loader',))


def host_setup(tmp_path, inputs):
    selected = mechanical_selection()
    captured = selected.capture()
    path = tmp_path / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', path)
    resolver = q.Resolver(((selected, captured),), path, allow_test_only=True)
    return selected, resolver, resolver.host_session(inputs)


def position_document(selected, session, result, org='driftwood'):
    return {'org': org, 'run': {'clock': 'github', 'model_version': selected.actor.model_version,
        'host_session': session.identity, 'declined': session.declines},
        'claims': [{'id': 'claim-one', 'kind': 'position', 'component': 'delivery',
                    'host_subject': 'live-one',
                    'evolution_position': 0.25, 'evidence': 'literal supplied witness',
                    'price_eligible': False, 'host_receipt': result.receipt}]}


def signal_actor(payload, config):
    return json.dumps({'steep': payload['statement'].split()[0],
                       'component': payload['candidates'][0]['id'],
                       'basis': payload['statement']}).encode()


def parse_signal(raw, config):
    value = json.loads(raw)
    return Stated({'steep': value['steep'], 'claim': {'component': value['component']}}, value['basis'])


def intermittent_actor(payload, config):
    return b'invalid JSON retained literally' if payload['position'] == 0 else literal_actor(payload, config)


def failing_actor(payload, config):
    if payload['position'] == 0:
        raise RuntimeError('TEST_ONLY declared failure')
    return literal_actor(payload, config)


def observed_runtime_actor(payload, config):
    return q.RuntimeResult(literal_actor(payload, config), {'build': 'TEST_ONLY observed build-A'})


def defaulted_runner(payload, config, offset=0):
    return literal_actor({**payload, 'position': payload['position'] + offset}, config)


def nested_default_runner(payload, config, offsets=(0, {'fallback': [0]})):
    return literal_actor({**payload, 'position': payload['position'] + offsets[0] + offsets[1]['fallback'][0]}, config)


def defaulted_parser(raw, config, keys=('position', {'basis': ['evidence']})):
    value = json.loads(raw)
    return Stated({'evolution_position': value[keys[0]]}, value[keys[1]['basis'][0]])


def keyword_default_parser(raw, config, *, keys={'position': ('position',), 'basis': ['evidence']}):
    value = json.loads(raw)
    return Stated({'evolution_position': value[keys['position'][0]]}, value[keys['basis'][0]])


def defaulted_basis_checker(actual, expected, prefixes=('TEST_ONLY',)):
    return actual == expected['witness'] and actual.startswith(prefixes)


def defaulted_review_checker(record, population, *, issuer=('TEST_ONLY-population-custodian',)):
    return json.loads(record).get('issuer') == issuer[0]


def defaulted_reference_projection(metric, expected, version=(1,)):
    if version != (1,):
        return {'evolution_position': -1}
    return q.project_reference(metric, expected)


def changed_defaulted_runner(payload, config, offset=0):
    return literal_actor({**payload, 'position': payload['position'] + offset + 1}, config)


def defaulted_selection():
    original = reviewed_mechanical_selection()
    review = q.PopulationReview.freeze(original.population, original.review.record, defaulted_review_checker)
    actor = q.Actor.freeze(defaulted_runner, keyword_default_parser, {'purpose': 'TEST_ONLY'})
    return q.Selection.freeze(actor, original.population, defaulted_basis_checker,
        reference_projection=defaulted_reference_projection, review=review)


def wrong_basis_actor(payload, config):
    return json.dumps({'position': payload['position'], 'evidence': 'foreign witness'}).encode()


def signal_selection():
    admissions = []
    for i in range(16):
        packet = json.loads(reference(case_id=f'TEST_ONLY-signal-{i}',
            org=('driftwood', 'tuppence', 'ludlow')[i % 3]).packet_bytes)
        case, scope = packet['case'], packet['requested_scope']
        scope['metric'] = 'signal-classify'
        case['context'] = scope
        statement = ('social' if i % 2 else 'economic') + f' TEST_ONLY headline {i}'
        component = f'component-{i % 4}'
        case['input'] = {'statement': statement, 'source': 'TEST_ONLY fixture',
                         'candidates': [{'id': component, 'name': component}]}
        case['expected'] = {'steep': statement.split()[0], 'component': component}
        support = case['field_support']['evolution_position']
        case['field_support'] = {'steep': support, 'component': support}
        case['basis']['witness'] = statement
        case['basis_binding'] = binding_for(case)
        admission = admit_reference(case, scope)
        assert admission.admitted, admission.reasons
        admissions.append(admission)
    pop = q.Population.freeze('signal-classify', tuple(admissions), envelope(),
        {'status': 'development', 'history': ['TEST_ONLY literal fixture exposure'],
         'training_provenance': 'unknown'})
    return q.Selection.freeze(q.Actor.freeze(signal_actor, parse_signal, {'purpose': 'TEST_ONLY'}),
        pop, basis_holds, review=q.PopulationReview.test_only(pop), test_only=q.TEST_ONLY_MECHANICS)


def public_controls():
    """Exercise the real host lifecycle without registering a real candidate or lasting row."""
    from pathlib import Path
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as directory:
        root = Path(directory)
        selected, resolver, session = host_setup(root, host_inputs())
        result = session.judge('evolution-judge', selected.actor.model_version, 'live-one')
        document = position_document(selected, session, result)
        accepted = not resolver.check_claim_document(document, 'github')
        captured = selected.capture()
        default_refuses = not q.Resolver(((selected, captured),), root / 'scores.jsonl').permission(
            'evolution-judge', selected.actor.model_version).granted
        bundle = selected.archive(captured)
        (root / 'selection.json').write_bytes(bundle)
        archive = session.archive()
        (root / 'session.json').write_bytes(archive)
        catalogue = q.canonical({'schema': 'twin.qualification-registry/v1',
            'entries': [{'bundle': 'selection.json', 'sha256': hashlib.sha256(bundle).hexdigest()}],
            'sessions': [{'bundle': 'session.json', 'sha256': hashlib.sha256(archive).hexdigest()}]})
        (root / 'catalogue.json').write_bytes(catalogue)
        restored = q.Resolver.from_catalogue(root / 'catalogue.json', hashlib.sha256(catalogue).hexdigest(),
            root / 'scores.jsonl', allow_test_only=True)
        durable = not restored.check_claim_document(document, 'github')
        document['claims'][0]['host_receipt'] = 'a response cannot mint a receipt'
        forged_refuses = bool(restored.check_claim_document(document, 'github'))
        foreign = resolver.host_session(host_inputs('foreign-estate'))
        declined = foreign.judge('evolution-judge', selected.actor.model_version, 'live-one')
        return {'registered TEST_ONLY invocation accepted': accepted,
                'default operational registry refuses TEST_ONLY': default_refuses,
                'later protected catalogue import accepted': durable,
                'forged model receipt refused': forged_refuses,
                'foreign estate refused and counted': not declined.receipt and len(foreign.declines) == 1}


def fixture_review_checker(record, population):
    """TEST_ONLY authority adapter, not an assertion of empirical label provenance."""
    return json.loads(record).get('issuer') == 'TEST_ONLY-population-custodian'


def reviewed_mechanical_selection(change=None):
    admissions = []
    for packet in json.loads(population().description)['selected']:
        case, scope = packet['case'], packet['requested_scope']
        case['rights']['uses'].append('qualification')
        case['exposure'] = {'status': 'held-out', 'history': ['TEST_ONLY custodian declaration']}
        case['basis_binding'] = binding_for(case)
        admissions.append(admit_reference(case, scope))
    pop = q.Population.freeze('evolution-judge', tuple(admissions), envelope(),
        {'status': 'held-out', 'history': ['TEST_ONLY split custody'],
         'training_provenance': 'unknown; this is a disclosed uncertainty, not a clean-training claim'})
    groups = [row['case']['group'] for row in json.loads(pop.description)['selected']]
    record = {'schema': 'twin.population-review/v1', 'population_digest': pop.digest,
        'decision': 'admitted', 'issuer': 'TEST_ONLY-population-custodian',
        'authority': 'TEST_ONLY software authority adapter', 'reference_authority': 'TEST_ONLY literal fixture',
        'rights': 'TEST_ONLY authored fixture use', 'limitations': ['No empirical qualification authority'],
        'coverage': ['driftwood', 'tuppence', 'ludlow'],
        'source_family_split': {'qualification_groups': groups, 'development_groups': []}}
    if change:
        record.update(change)
    review = q.PopulationReview.freeze(pop, q.canonical(record), fixture_review_checker)
    return q.Selection.freeze(q.Actor.freeze(literal_actor, parse_position, {'purpose': 'TEST_ONLY'}),
        pop, basis_holds, review=review)

