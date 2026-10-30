"""New tiny TEST_ONLY host controls; no model or qualification evidence."""
from pathlib import Path
import hashlib
import json
from typing import Any

import yaml

from twin import fixtures, qualification as q
from twin.model import Overlay
from twin.reference_cases import source_record


def source_authority(packet: bytes, policy: dict) -> bool:
    return json.loads(packet).get('authority') == 'TEST_ONLY-original-author' and policy['issuer'] == 'TEST_ONLY-host'


def request(root: Path, org: str = 'driftwood') -> dict:
    from twin.substrate_generation import SCOPES, authority_identity
    from twin.repo import ModelRepo
    root.mkdir()
    fixtures.git(root, 'init', '-q', '-b', 'main', '--object-format=sha1')
    def put(rel, value):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(value))
    put('world/meta.yaml', {'id': 'test-only-world', 'unit': 'world'})
    for index in range(14):
        ident = f'test-only-world-{index}'
        put(f'world/components/{ident}.yaml', {'id': ident, 'name': ident, 'kind': 'activity', 'evolution': 'product', 'visibility': .2})
    put('world/components/cage-policy-line.yaml', {'id': 'cage-policy-line', 'name': 'TEST_ONLY cage policy', 'kind': 'activity', 'evolution': 'product', 'visibility': .2})
    fixtures.git(root, 'add', '--', 'world')
    fixtures.git(root, 'commit', '-q', '-m', 'TEST_ONLY world')
    world = fixtures.git(root, 'rev-parse', 'HEAD').strip()
    scope: Any
    for adopter, scope in SCOPES.items():
        put(f'orgs/{adopter}/meta.yaml', {'id': adopter, 'unit': 'overlay', 'org': adopter, 'world_ref': world})
        for ident in [scope['component'], scope['additional'][0], 'test-only-local-a', 'test-only-local-b', 'test-only-local-c']:
            put(f'orgs/{adopter}/components/{ident}.yaml', {'id': ident, 'name': 'TEST_ONLY ' + ident,
                'description': 'TEST_ONLY structural definition; no observed incident.', 'kind': 'activity', 'evolution': 'product', 'visibility': .5})
    fixtures.git(root, 'add', '--', 'orgs')
    fixtures.git(root, 'commit', '-q', '-m', 'TEST_ONLY overlays')
    repo = ModelRepo.open(root)
    overlay = Overlay.load(repo, org)
    scope = SCOPES[org]
    fields = {'schema': 'twin.substrate-recipe/v1', 'id': 'TEST_ONLY-request', 'seed': 9,
        'model_version': 'TEST_ONLY-actor', 'templates': [f'TEST_ONLY contextual cue {i}' for i in range(8)],
        'planted_signals': ['TEST_ONLY marker birch']}
    recipe = yaml.safe_dump(fields).encode()
    intent = {key: fields[key] for key in ('id', 'seed', 'templates', 'planted_signals')}
    packet = {'schema': 'twin.substrate-source/v1', 'subject': 'TEST_ONLY-live', 'version': 'TEST_ONLY-v1',
        'organisation': org, 'domain': scope['domain'], 'component': scope['component'],
        'focus_components': [scope['component'], *scope['additional']], 'family': 'TEST_ONLY-family',
        'recipe_sha256': hashlib.sha256(recipe).hexdigest(),
        'intent': source_record(q.canonical(intent), 'TEST_ONLY-original-intent', 'v1'),
        'rights': {'statement': 'TEST_ONLY internal exercise', 'uses': ['development', 'qualification', 'generation']},
        'authority': 'TEST_ONLY-original-author', 'exposure': {'status': 'TEST_ONLY', 'history': ['new control']}}
    source = q.canonical(packet)
    party = yaml.safe_dump({'id': org, 'appetite': {'pricing_threshold': 3}}).encode()
    policy = {'issuer': 'TEST_ONLY-host', 'domain': scope['domain'], 'capability': 'synthetic-substrate',
        'frame': 'estate-synthetic-recipe-structural-conformance/current-model-snapshot-20261030',
        'as_of': '2026-10-30', 'model_pins': {'model_repo': repo.pin.as_dict(), 'overlay': overlay.ref.as_dict(), 'world': overlay.world.ref.as_dict()},
        'source_authority': authority_identity(source_authority), 'profile': {'templates': 8, 'min_plants': 0, 'max_plants': 4}}
    return {'repo': repo, 'org': org, 'recipe_bytes': recipe, 'recipe_pin': hashlib.sha256(recipe).hexdigest(),
        'source_packet': source, 'source_pin': hashlib.sha256(source).hexdigest(), 'party_bytes': party,
        'party_pin': hashlib.sha256(party).hexdigest(), 'policy': policy, 'source_checker': source_authority}


CALLS: list[str] = []


def runner(payload: str, config: dict) -> bytes:
    """Explicit TEST_ONLY adapter; its content must never be used as candidate evidence."""
    from twin.substrate_generator import CHANNELS
    fields = yaml.safe_load(payload)
    CALLS.append(fields['id'])
    channels = {channel: [f'TEST_ONLY {fields["id"]} {channel} background {i}' for i in range(4)] for channel in CHANNELS}
    plants = []
    for signal in fields['planted_signals']:
        index = len(channels['events'])
        channels['events'].append('[TEST_ONLY arbitrary prefix] ' + signal)
        plants.append({'channel': 'events', 'index': index, 'signal': signal})
    answer: dict[str, Any] = {'channels': channels, 'plants': plants}
    tree = yaml.compose(payload)
    quotes = [{'field': key.value, 'quote': payload[key.start_mark.index:value.end_mark.index]}
              for key, value in tree.value if key.value in ('templates', 'planted_signals')]
    counts = {key: len(lines) for key, lines in channels.items()}
    basis: dict[str, Any] = {'recipe_quotes': quotes,
        'occurrences': [{**plant, 'line_quote': channels[plant['channel']][plant['index']]} for plant in plants],
        'counts': {'channel_lines': counts, 'total_lines': sum(counts.values()), 'plant_count': len(plants),
                   'mundane_lines': sum(counts.values()) - len(plants)}}
    if 'bad-structure' in fields['id']: answer['channels']['hr'] = []
    if 'bad-basis' in fields['id']: basis['counts']['total_lines'] = 999
    return q.canonical({'answer': answer, 'basis': basis})


def resolve(args: dict, actor: q.Actor, serial: int = 0, mode: str = 'good'):
    from twin.substrate_generation import resolve_recipe_input
    args = dict(args)
    fields = yaml.safe_load(args['recipe_bytes'])
    fields.update({'id': f'TEST_ONLY-{mode}-{serial}', 'seed': serial, 'model_version': actor.model_version,
        'templates': [f'TEST_ONLY cue {serial} {i}' for i in range(8)],
        'planted_signals': [f'TEST_ONLY plant {serial} {i}' for i in range(serial % 5)]})
    args['recipe_bytes'] = yaml.safe_dump(fields).encode()
    args['recipe_pin'] = hashlib.sha256(args['recipe_bytes']).hexdigest()
    packet = json.loads(args['source_packet'])
    packet.update({'subject': f'TEST_ONLY-{mode}-{serial}', 'recipe_sha256': args['recipe_pin'],
        'intent': source_record(q.canonical({key: fields[key] for key in ('id', 'seed', 'templates', 'planted_signals')}), 'TEST_ONLY-original-intent', 'v1')})
    args['source_packet'] = q.canonical(packet)
    args['source_pin'] = hashlib.sha256(args['source_packet']).hexdigest()
    return resolve_recipe_input(**args)


def setup(root: Path):
    from twin import substrate_candidate, substrate_recipe_basis as basis
    from twin import substrate_generation as generation
    from twin.reference_cases import admit_reference, binding_for
    actor = q.Actor.freeze(runner, substrate_candidate.parse, {'purpose': 'TEST_ONLY'})
    requests = {org: request(root / org, org) for org in generation.SCOPES}
    resolved = [resolve(requests[list(requests)[i % 3]], actor, i) for i in range(18)]
    rows = [item.host_record for item in resolved]
    admissions = []
    for i, row in enumerate(rows):
        context = {**row['context'], 'purpose': 'development', 'claim': 'task-conformance', 'metric': generation.METRIC}
        # These custody-only fields are deliberately present in both reference/live context.
        row['context'] = context
        raw = b'TEST_ONLY explicit structural constraint authority'
        source = source_record(raw, 'TEST_ONLY-structural-contract', 'v1')
        support = {'meaning': 'TEST_ONLY declared structural constraint', 'sources': ['contract'],
            'witnesses': [{'source': 'contract', 'start': 0, 'end': len(raw), 'sha256': source['sha256']}]}
        reference = generation.live_reference(row)
        # The reference retains its raw recipe/intent identity as required by normal admission.
        reference['source_hashes']['contract'] = source['sha256']
        case = {'id': f'TEST_ONLY-case-{i}', 'group': f'TEST_ONLY-group-{i}', 'input': row['input'],
            'expected': basis.expected_for(row['input']), 'basis': reference, 'context': context,
            'host_subject': row['subject'], 'host_source': row['source'], 'host_issuer': row['issuer'],
            'sources': {'contract': source}, 'rights': {'statement': 'TEST_ONLY exercise', 'evidence': ['contract'],
                'covered_sources': ['contract'], 'uses': ['development', 'qualification']},
            'reference_kind': 'declared-constraints', 'field_support': {key: support for key in ('channels', 'planted_signals', 'min_mundane_fraction')},
            'selection': {'decision': 'selected', 'reason': 'TEST_ONLY fixed order'},
            'exposure': {'status': 'held-out', 'history': ['TEST_ONLY fictional split']}, 'limitations': ['TEST_ONLY mechanics only']}
        case['basis_binding'] = binding_for(case)
        admitted = admit_reference(case, context)
        if not admitted.admitted: raise ValueError(admitted.reasons)
        admissions.append(admitted)
    envelope = {'adopters': list(generation.SCOPES), 'domains': [scope['domain'] for scope in generation.SCOPES.values()],
        'capabilities': ['synthetic-substrate'], 'frames': [generation.FRAME],
        'sources': [f'estate-synthetic-recipe:{org}:v1' for org in generation.SCOPES],
        'from': '2026-10-30', 'until': '2026-10-30',
        'generator_contexts': {row['context']['organisation']: row['context']['generator_context'] for row in rows}}
    pop = q.Population.freeze(generation.METRIC, tuple(admissions), envelope,
        {'status': 'held-out', 'history': ['TEST_ONLY'], 'training_provenance': 'TEST_ONLY unknown'})
    selected = q.Selection.freeze(actor, pop, basis.check, review=q.PopulationReview.test_only(pop))
    captured = selected.capture()
    scores = root / 'scores.jsonl'
    selected.record(captured, '2026-10-30T00:00:00Z', scores)
    resolver = q.Resolver(((selected, captured),), scores, allow_test_only=True)
    return selected, resolver, requests
