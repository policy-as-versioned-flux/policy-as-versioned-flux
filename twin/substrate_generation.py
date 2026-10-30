"""Protected recipe resolution and one-capture AUTHORED generator delivery.

No registration, runtime, reference population or model permission is supplied here.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable

from . import qualification as q
from .model import Overlay
from .repo import ModelRepo, load_yaml
from .reference_cases import source_record
from .blob import BlobRef
from .substrate_recipe_basis import recipe_fields, reference_basis, source_bytes


SCOPES = {
    'driftwood': {'domain': 'retail checkout', 'component': 'cart-checkout-service', 'additional': ['cart-pii', 'cage-policy-line']},
    'tuppence': {'domain': 'payment authorisation and settlement', 'component': 'payments-api', 'additional': ['customer-account-records', 'cage-policy-line']},
    'ludlow': {'domain': 'health plan claims administration', 'component': 'claims-adjudication', 'additional': ['member-record-store', 'cage-policy-line']},
}
FRAME = 'estate-synthetic-recipe-structural-conformance/current-model-snapshot-20261030'
METRIC = 'substrate-generator'


def authority_identity(checker: Callable[[bytes, dict[str, Any]], bool]) -> dict[str, Any]:
    path = Path(inspect.getfile(checker)).resolve()
    return {'callable': q._callable_identity(checker), 'path': q._source_name(path),
            'source': hashlib.sha256(path.read_bytes()).hexdigest()}


def _authority(packet: bytes, policy: dict[str, Any]) -> None:
    identity = policy['source_authority']
    checker = q._restore_callable(identity['callable'])
    if authority_identity(checker) != identity or checker(packet, policy) is not True:
        raise ValueError('recipe source authority was not established by the protected host checker')


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate source packet field')
        result[key] = value
    return result


def _packet(raw: bytes, text: str, policy: dict[str, Any]) -> dict[str, Any]:
    packet = json.loads(raw, object_pairs_hook=_unique)
    required = {'schema', 'subject', 'version', 'organisation', 'domain', 'component', 'focus_components',
                'family', 'recipe_sha256', 'intent', 'rights', 'authority', 'exposure'}
    if (not isinstance(packet, dict) or set(packet) != required or packet['schema'] != 'twin.substrate-source/v1'
            or any(not isinstance(packet[key], str) or not packet[key].strip()
                   for key in ('subject', 'version', 'organisation', 'domain', 'component', 'family', 'authority'))):
        raise ValueError('exact established recipe source packet required')
    org = packet['organisation']
    scope = SCOPES.get(org)
    if (scope is None or packet['domain'] != scope['domain'] or packet['component'] != scope['component']
            or policy['domain'] != scope['domain']):
        raise ValueError('recipe adopter/domain/component tuple differs')
    focuses = packet['focus_components']
    if (not isinstance(focuses, list) or any(not isinstance(value, str) for value in focuses)
            or len(set(focuses)) != len(focuses) or scope['component'] not in focuses
            or not set(focuses) <= {scope['component'], *scope['additional']}):
        raise ValueError('recipe focus set is outside the established adopter tuple')
    if packet['recipe_sha256'] != hashlib.sha256(text.encode()).hexdigest():
        raise ValueError('raw recipe source pin differs')
    fields = recipe_fields(text)
    profile = policy['profile']
    if (not isinstance(profile, dict) or set(profile) != {'templates', 'min_plants', 'max_plants'}
            or any(type(value) is not int for value in profile.values()) or profile['templates'] != 8
            or not 0 <= profile['min_plants'] <= profile['max_plants'] <= 4
            or len(fields['templates']) != profile['templates']
            or not profile['min_plants'] <= len(fields['planted_signals']) <= profile['max_plants']):
        raise ValueError('recipe structural profile is outside protected authoring scope')
    rights = packet['rights']
    if (not isinstance(rights, dict) or not rights.get('statement') or not isinstance(rights.get('uses'), list)
            or 'generation' not in rights['uses'] or not packet['exposure']):
        raise ValueError('recipe source rights/exposure do not support this use')
    reference_basis(text, {}, packet['intent'])
    _authority(raw, policy)
    return packet


def _policy(policy: dict[str, Any]) -> None:
    if (not isinstance(policy, dict) or set(policy) != {'issuer', 'domain', 'capability', 'frame', 'as_of', 'model_pins', 'source_authority', 'profile'}
            or not isinstance(policy['issuer'], str) or not policy['issuer'].strip()
            or policy['capability'] != 'synthetic-substrate' or policy['frame'] != FRAME or policy['as_of'] != '2026-10-30'):
        raise ValueError('exact protected generator source policy required')


@dataclass(frozen=True)
class ResolvedRecipeInput:
    description: bytes

    @property
    def host_record(self) -> dict[str, Any]:
        return json.loads(self.description)

    def host_inputs(self) -> q.HostInputs:
        row = self.host_record
        return q.HostInputs.freeze((row,), (row['issuer'],))


def resolve_recipe_input(repo: ModelRepo, org: str, recipe_bytes: bytes, recipe_pin: str,
                         source_packet: bytes, source_pin: str, party_bytes: bytes, party_pin: str,
                         policy: dict[str, Any], source_checker: Callable[[bytes, dict[str, Any]], bool]) -> ResolvedRecipeInput:
    """Host-selected authority, exact source pins and full current model precede the child."""
    _policy(policy)
    for raw, pin in ((recipe_bytes, recipe_pin), (source_packet, source_pin), (party_bytes, party_pin)):
        if hashlib.sha256(raw).hexdigest() != pin:
            raise ValueError('protected recipe/source/party pin differs')
    if authority_identity(source_checker) != policy['source_authority']:
        raise ValueError('source checker differs from protected authority')
    text = recipe_bytes.decode('utf-8')
    packet = _packet(source_packet, text, policy)
    party = load_yaml(party_bytes.decode())
    if not isinstance(party, dict) or party.get('id') != org or packet['organisation'] != org:
        raise ValueError('recipe/party belongs to another organisation')
    current = ModelRepo.open(repo.model_root, ref=repo.pin.commit)
    overlay = Overlay.load(current, org, pricing_threshold=party.get('appetite', {}).get('pricing_threshold', 2))
    pins = {'model_repo': current.pin.as_dict(), 'overlay': overlay.ref.as_dict(), 'world': overlay.world.ref.as_dict()}
    if current.pin != repo.pin or pins != policy['model_pins']:
        raise ValueError('actual full model closure differs from protected pins')
    definitions = {**overlay.world.components, **overlay.components}
    if len(definitions) != 20 or any(focus not in definitions for focus in packet['focus_components']):
        raise ValueError('all twenty current model definitions and every focus are required')
    source = source_record(q.canonical(text), f'estate-synthetic-recipe:{org}:v1', packet['version'])
    core = {**policy, 'organisation': org, 'source': source['identity'], 'component': packet['component'],
        'allowed_focus_components': [packet['component'], *SCOPES[org]['additional']],
        'definitions': definitions, 'definitions_sha256': q.digest(definitions),
        'input_construction_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    context = {key: core[key] for key in ('organisation', 'domain', 'capability', 'frame', 'as_of', 'source', 'component')}
    context.update({'source_sha256': source['sha256'], 'generator_context': core,
        'focus_components': packet['focus_components'], 'recipe_family': packet['family'],
        'raw_recipe_sha256': recipe_pin, 'source_packet_sha256': source_pin,
        'party_sha256': party_pin, 'source_policy': policy,
        'original_sources': {'recipe': source_record(recipe_bytes, 'raw-substrate-recipe:' + recipe_fields(text)['id'], source['version']),
                             'intent': packet['intent'], 'source_packet': source_record(source_packet, source['identity'], packet['version'])}})
    return ResolvedRecipeInput(q.canonical({'subject': packet['subject'], 'issuer': policy['issuer'],
        'input': text, 'source': source, 'context': context}))


def validate_row(row: dict[str, Any], model_version: str | None = None) -> None:
    """Revalidate original source/authority and exact protected context at every invocation."""
    context, text = row['context'], row['input']
    core, policy = context['generator_context'], context['source_policy']
    _policy(policy)
    sources = context['original_sources']
    packet_raw = source_bytes(sources['source_packet'])
    packet = _packet(packet_raw, text, policy)
    fields = recipe_fields(text)
    if (model_version is not None and fields['model_version'] != model_version):
        raise ValueError('recipe names a different frozen actor')
    if (row['issuer'] != policy['issuer'] or row['subject'] != packet['subject']
            or row['source'] != source_record(q.canonical(text), core['source'], packet['version'])
            or context['raw_recipe_sha256'] != hashlib.sha256(text.encode()).hexdigest()
            or source_bytes(sources['recipe']) != text.encode() or sources['intent'] != packet['intent']
            or context['source_packet_sha256'] != hashlib.sha256(packet_raw).hexdigest()
            or context['focus_components'] != packet['focus_components'] or context['recipe_family'] != packet['family']
            or any(context[key] != core[key] for key in ('organisation', 'domain', 'capability', 'frame', 'as_of', 'source', 'component'))
            or any(core[key] != value for key, value in policy.items())
            or core['definitions_sha256'] != q.digest(core['definitions']) or len(core['definitions']) != 20
            or any(focus not in core['definitions'] for focus in context['focus_components'])
            or core['input_construction_sha256'] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()):
        raise ValueError('protected recipe/input/source/context binding differs')


def live_reference(row: dict[str, Any]) -> dict[str, Any]:
    validate_row(row)
    return reference_basis(row['input'], row['context'], row['context']['original_sources']['intent'])


def scope_reasons(population: q.Population, context: dict[str, Any]) -> list[str]:
    try:
        core = context['generator_context']
        expected = population.envelope['generator_contexts'][context['organisation']]
        focuses = context['focus_components']
        if (core != expected or any(context[key] != core[key] for key in ('organisation', 'domain', 'capability', 'frame', 'as_of', 'source', 'component'))
                or not isinstance(focuses, list) or not focuses or any(not isinstance(item, str) for item in focuses)
                or len(set(focuses)) != len(focuses) or core['component'] not in focuses
                or not set(focuses) <= set(core['allowed_focus_components'])):
            return ['host generator tuple/full model/focus context differs from qualification']
        return []
    except (KeyError, TypeError, ValueError):
        return ['host generator tuple/full model/focus context is missing']


def validate_population(actor: q.Actor, population: q.Population) -> None:
    from .substrate_recipe_basis import expected_for
    envelope = population.envelope
    contexts = envelope.get('generator_contexts', {})
    if set(contexts) != set(SCOPES) or set(envelope['adopters']) != set(SCOPES):
        raise ValueError('generator qualification requires all three exact contexts')
    selected = json.loads(population.description)['selected']
    if {packet['case']['context']['organisation'] for packet in selected} != set(SCOPES):
        raise ValueError('generator population does not measure all three adopters')
    for packet in selected:
        case = packet['case']
        context = case['context']
        row = {'subject': case['host_subject'], 'input': case['input'], 'context': context,
               'source': case['host_source'], 'issuer': case['host_issuer']}
        validate_row(row, actor.model_version)
        reference = live_reference(row)
        if (scope_reasons(population, context) or case['expected'] != expected_for(case['input'])
                or any(case['basis'].get(key) != value for key, value in reference.items() if key != 'source_hashes')
                or any(case['basis'].get('source_hashes', {}).get(key) != value for key, value in reference['source_hashes'].items())
                or not isinstance(case['group'], str)):
            raise ValueError('qualification recipe/context/reference binding differs')


def _validation(session: q.HostSession, token: str) -> tuple[str | None, dict[str, Any]]:
    from .substrate_recipe_basis import expected_for
    from .substrate_generator import scorer
    record = json.loads(session._records[token])
    try:
        if record['metric'] != METRIC:
            raise ValueError('generation session cannot contain another metric')
        session._verify_record(record)
        row = session._inputs.resolve(record['subject'])
        validate_row(row, record['model_version'])
        selected, _ = session._resolver._bindings[(METRIC, record['model_version'])]
        output = record['output']
        if not scorer(output['answer'], expected_for(row['input'])):
            return 'structural conformance failed', record
        if selected.basis_checker(output['basis'], live_reference(row)) is not True:
            return 'actual basis failed', record
        return None, record
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        # A successful internal host receipt can still become a final validation decline.
        # Preserve it and its raw capture even if a dependency changes after invocation.
        return 'protected capture validation failed: ' + str(exc), record


def _batch(record: dict[str, Any], token: str, blob: str) -> dict[str, Any]:
    output = record['output']
    raw = base64.b64decode(output['raw'], validate=True)
    return {'host_receipt': token, 'subject': record['subject'], 'blob': blob,
        'model_version': record['model_version'], 'actor_digest': output['actor_digest'],
        'input_sha256': output['input_digest'], 'context_sha256': q.digest(record['context']),
        'selection_digest': record['selection'], 'raw_output_sha256': hashlib.sha256(raw).hexdigest(),
        'evidence': output['basis']}


def verify_session(session: q.HostSession) -> None:
    """Verify conserved internal receipts, final declines and every captured authored blob."""
    tokens, declined, blobs = [], [], set()
    for index, final in enumerate(session._generation_dispositions):
        if type(final.get('attempt_index')) is not int or final['attempt_index'] != index or not isinstance(final.get('subject'), str):
            raise ValueError('generation disposition order/subject differs')
        state = final.get('state')
        if state == 'host-decline':
            pointer = final.get('host_decline_index')
            if type(pointer) is not int or not 0 <= pointer < len(session.declines):
                raise ValueError('generation decline has no internal host decline')
            entry = session.declines[pointer]
            if set(final) != {'attempt_index', 'subject', 'state', 'host_decline_index', 'reason'} or final['subject'] != entry['subject'] or final['reason'] != entry['reason']:
                raise ValueError('generation decline differs from retained host decline')
            declined.append(pointer)
            continue
        token = final.get('host_receipt')
        if not isinstance(token, str) or token not in session._records:
            raise ValueError('generation has no internal protected receipt')
        tokens.append(token)
        reason, record = _validation(session, token)
        if final['subject'] != record['subject']:
            raise ValueError('generation disposition subject differs from receipt')
        if state == 'validation-decline':
            if set(final) != {'attempt_index', 'subject', 'state', 'host_receipt', 'reason'} or not reason or final['reason'] != reason:
                raise ValueError('generation postvalidation decline differs from actual capture')
        elif state == 'delivered':
            if set(final) != {'attempt_index', 'subject', 'state', 'host_receipt', 'blob'} or reason:
                raise ValueError('generation deliverable failed live validation')
            blob = final['blob']
            raw = base64.b64decode(session._generation_blobs[blob], validate=True)
            if not BlobRef.parse(blob).resolves(raw) or raw != q.canonical(record['output']['answer']):
                raise ValueError('authored blob differs from actual same-raw answer')
            blobs.add(blob)
        else:
            raise ValueError('unknown generation final disposition')
    if (len(set(tokens)) != len(tokens) or set(tokens) != set(session._records)
            or len(set(declined)) != len(declined) or set(declined) != set(range(len(session.declines)))
            or blobs != set(session._generation_blobs)):
        raise ValueError('generation omits or duplicates counted host calls or blobs')


class GenerationParent:
    """Protected parent owns delivery; the model never selects the checker or validator."""
    def __init__(self, resolver: q.Resolver, model_version: str, *, role: str = 'model-steward', clock: str | None = None):
        self.resolver, self.model_version, self.role = resolver, model_version, role
        self.clock = q.mp.derive_clock(clock)[0]

    def start(self, inputs: q.HostInputs) -> GenerationRun:
        session = self.resolver.host_session(inputs)
        run = GenerationRun(self, session)
        for row in json.loads(inputs.description)['records']:
            result = session.judge(METRIC, self.model_version, row['subject'])
            run.results.append(result)
            final: dict[str, Any] = {'attempt_index': len(session._generation_dispositions), 'subject': row['subject']}
            if result.receipt is None:
                final.update({'state': 'host-decline', 'host_decline_index': len(session.declines) - 1, 'reason': result.reason})
            else:
                reason, record = _validation(session, result.receipt)
                final['host_receipt'] = result.receipt
                if reason:
                    final.update({'state': 'validation-decline', 'reason': reason})
                else:
                    raw = q.canonical(record['output']['answer'])
                    blob = str(BlobRef.of(raw))
                    session._generation_blobs[blob] = base64.b64encode(raw).decode()
                    final.update({'state': 'delivered', 'blob': blob})
            session._generation_dispositions.append(final)
        return run


class GenerationRun:
    def __init__(self, parent: GenerationParent, session: q.HostSession):
        self.parent, self.session = parent, session
        self.results: list[q.Judgement] = []

    def document(self) -> dict[str, Any]:
        batches = [_batch(json.loads(self.session._records[final['host_receipt']]), final['host_receipt'], final['blob'])
            for final in self.session._generation_dispositions if final['state'] == 'delivered']
        organisations = {json.loads(record)['context']['organisation'] for record in self.session._records.values()}
        if len(organisations) > 1:
            raise ValueError('one generation document belongs to one adopter')
        return {'schema': 'twin.substrate-generation/v1', 'mark': 'authored', 'metric': METRIC,
            'org': next(iter(organisations), None), 'batches': batches,
            'run': {'skill': METRIC, 'operator_role': self.parent.role, 'headless': True, 'clock': self.parent.clock,
                    'model_version': self.parent.model_version, 'host_session': self.session.identity,
                    'declined': self.session.declines, 'generation_dispositions': json.loads(q.canonical(self.session._generation_dispositions))}}

    def validate(self) -> list[str]:
        return self.parent.resolver.check_generation_document(self.document(), self.parent.clock)

    def replay(self, blob: str) -> bytes:
        verify_session(self.session)
        raw = base64.b64decode(self.session._generation_blobs[blob], validate=True)
        if not BlobRef.parse(blob).resolves(raw):
            raise ValueError('captured authored blob changed')
        return raw

    def save(self, output: Path) -> dict[str, Any]:
        output.mkdir(parents=True, exist_ok=False)
        (output / 'host-session.json').write_bytes(self.session.archive())
        bad = self.validate()
        document = self.document()
        if not bad:
            (output / 'generation.json').write_bytes(q.canonical(document))
            for blob in self.session._generation_blobs:
                (output / (BlobRef.parse(blob).digest + '.json')).write_bytes(self.replay(blob))
        summary = {'accepted': not bad, 'reasons': bad, 'declined': self.session.declines,
            'generation_dispositions': self.session._generation_dispositions,
            'actual_permission_grant': False, 'target_runtime_measured_by_this_command': False}
        (output / 'summary.json').write_bytes(q.canonical(summary))
        return summary


def check_document(session: q.HostSession, document: dict[str, Any], clock: str) -> list[str]:
    bad = []
    try:
        verify_session(session)
        run = document['run']
        derived_clock = q.mp.derive_clock(clock)[0]
        if (set(document) != {'schema', 'mark', 'metric', 'org', 'batches', 'run'}
                or document['schema'] != 'twin.substrate-generation/v1' or document['mark'] != 'authored' or document['metric'] != METRIC
                or set(run) != {'skill', 'operator_role', 'headless', 'clock', 'model_version', 'host_session', 'declined', 'generation_dispositions'}
                or run['skill'] != METRIC or run['headless'] is not True or run['clock'] != derived_clock
                or run['host_session'] != session.identity or run['declined'] != session.declines
                or run['generation_dispositions'] != session._generation_dispositions):
            bad.append('generation document schema/authority/clock/counted dispositions differ')
        roles = load_yaml(Path(q.__file__).with_name('roles.yaml').read_text())
        if run['operator_role'] not in {role['id'] for role in roles['roles']}:
            bad.append('generation operator role is not registered')
        permission = session._resolver.permission(METRIC, run['model_version'])
        if not permission.permits(q.mp.JUDGE):
            bad.append(permission.why())
        expected = []
        for final in session._generation_dispositions:
            if final['state'] != 'delivered':
                continue
            record = json.loads(session._records[final['host_receipt']])
            if record['model_version'] != run['model_version'] or record['context']['organisation'] != document['org']:
                bad.append('generation actor/adopter differs from protected receipt')
            expected.append(_batch(record, final['host_receipt'], final['blob']))
        if not expected:
            bad.append('no validated generated batch; human/local authoring fallback remains')
        if document['batches'] != expected:
            bad.append('generation document omits, duplicates or changes protected captures/blobs')
    except (ValueError, KeyError, TypeError, OSError, AttributeError) as exc:
        bad.append('protected generation verification failed: ' + str(exc))
    return bad


def run_registered(organisation: str, output: Path, clock: str | None = None) -> dict[str, Any]:
    """Existing validator CLI uses only independently pinned jobs in its protected package.

    No claim/output path can choose the registry, backend, source authority or model scope.
    The initially empty catalogue supplies no operational generation job or permission.
    """
    from .qualified_signals import _member
    if output.exists():
        raise FileExistsError('host evidence output already exists; historical runs are immutable')
    catalogue = Path(q.__file__).with_name('qualification-registry.json')
    root = catalogue.parent
    try:
        raw = catalogue.read_bytes()
        resolver = q.Resolver.from_catalogue(catalogue, hashlib.sha256(raw).hexdigest())
        entry = json.loads(raw).get('generation_jobs', {}).get(organisation)
        if entry is None:
            raise ValueError('no registered generation job; current custody, exact target/runtime and qualification remain required')
        job = json.loads(_member(root, entry['job'], entry['sha256']))
        parent = GenerationParent(resolver, job['model_version'], role=job['operator_role'], clock=clock)
        permission = resolver.permission(METRIC, parent.model_version)
        if not permission.granted:
            raise ValueError(permission.why())
        if job.get('resume_session'):
            run = GenerationRun(parent, resolver._sessions[job['resume_session']])
        else:
            recipe = _member(root, job['recipe']['path'], job['recipe']['sha256'])
            source = _member(root, job['source']['path'], job['source']['sha256'])
            party = _member(root, job['party']['path'], job['party']['sha256'])
            repo_path = root / job['repo']
            if repo_path.is_symlink() or not repo_path.resolve().is_relative_to(root.resolve()):
                raise ValueError('registered model repository escapes protected snapshot')
            resolved = resolve_recipe_input(ModelRepo.open(repo_path), organisation, recipe,
                job['recipe']['sha256'], source, job['source']['sha256'], party, job['party']['sha256'],
                job['policy'], q._restore_callable(job['policy']['source_authority']['callable']))
            run = parent.start(resolved.host_inputs())
        return run.save(output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        output.mkdir(parents=True, exist_ok=False)
        summary = {'accepted': False, 'reasons': [str(exc)], 'declined': [],
            'generation_dispositions': [], 'actual_permission_grant': False,
            'target_runtime_measured_by_this_command': False}
        (output / 'summary.json').write_bytes(q.canonical(summary))
        return summary
