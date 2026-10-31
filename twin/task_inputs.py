"""Protected typed task construction and retained model/source policy handles.

A child gets only the accepted public input. Original bytes, clean model closure and
independently selected metadata authority policies stay with the host.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
import hashlib
import hmac
import json
from pathlib import Path
import secrets
from typing import Any

from . import evidence, qualification as q, source_metadata as sm
from .model import Overlay
from .repo import ModelRepo, load_yaml
from .reference_cases import source_record
from .task_contracts import TaskContract, decode, validate, support_sources as contract_sources

_KEY = secrets.token_bytes(32)
JOB_FIELDS = {'subject', 'issuer', 'organisation', 'target', 'domain', 'capability', 'frame', 'as_of',
    'model_as_of', 'model_pins', 'estate_scope_sha256', 'source', 'source_packet', 'source_pin',
    'source_bindings', 'metadata_policies'}
_POLICY_FIELDS = ('issuer', 'organisation', 'domain', 'capability', 'frame', 'model_as_of', 'model_pins',
                  'estate_scope_sha256', 'source', 'metadata_policies')


def _sources() -> dict[str, str]:
    from . import basis_assessment, gameplay_lens, causal_claims, ethics_gate, task_sessions
    return {q._source_name(path): sm.sha256(path.read_bytes()) for path in (
        Path(__file__), Path(q.__file__), Path(sm.__file__), Path(basis_assessment.__file__), Path(task_sessions.__file__),
        Path(gameplay_lens.__file__), Path(causal_claims.__file__), Path(ethics_gate.__file__),
        ethics_gate.SENSOR_TABLE_PATH, *contract_sources())}


def support_sources() -> tuple[Path, ...]:
    """Complete constructor/rubric/metadata support required by a task Actor."""
    return tuple(q._source_path(name) for name in _sources())


def _constructor(contract: TaskContract, policy: dict[str, Any]) -> str:
    return q.digest({'schema': 'twin.task-construction/v1', 'contract': contract.digest,
                     'sources': _sources(), 'policy': policy})


def _record_bytes(record: dict[str, Any]) -> bytes:
    try:
        if set(record) != {'identity', 'version', 'content_base64', 'bytes', 'sha256'}:
            raise ValueError('exact original task source record required')
        raw = base64.b64decode(record['content_base64'], validate=True)
        if (type(record['bytes']) is not int or len(raw) != record['bytes'] or sm.sha256(raw) != record['sha256']
                or any(not isinstance(record[key], str) or not record[key] for key in ('identity', 'version'))):
            raise ValueError('original task source bytes/pin differ')
        return raw
    except (KeyError, TypeError) as exc:
        raise ValueError('missing original task source record') from exc


def _metadata(store: sm.MetadataStore, policies: dict[str, Any], bindings: dict[str, Any],
              originals: dict[str, Any]) -> dict[str, Any]:
    if not policies or set(policies) != set(bindings) or set(originals) != set(bindings):
        raise ValueError('every source requires its independent protected policy/binding/originals')
    result = {}
    for source_id, policy in policies.items():
        sm.validate_parent_policy(policy, store)
        binding = bindings[source_id]
        if set(binding) != {'import_id', 'expected_manifest_sha256', 'expected_authority_digest', 'expected_acquisition_receipt_sha256'}:
            raise ValueError('exact task source acquisition binding required')
        if binding['expected_authority_digest'] != policy['authority_digest']:
            raise ValueError('source cannot appoint another metadata authority')
        acquired = store.resolve(**binding)
        public = acquired.public
        sm.validate_public_projection(public)
        if set(originals[source_id]) != set(public['members']):
            raise ValueError('all original/extraction/qualifier members must remain available for review')
        for name, member in public['members'].items():
            record = originals[source_id][name]
            _record_bytes(record)
            if any(q.canonical(record[key]) != q.canonical(member[key]) for key in ('identity', 'version', 'sha256', 'bytes')):
                raise ValueError('retained source member differs from acquired original lineage')
        result[source_id] = public
    return result


def _packet(raw: bytes) -> dict[str, Any]:
    packet = decode(raw)
    if (not isinstance(packet, dict) or set(packet) != {'schema', 'subject', 'as_of', 'target', 'task', 'original_sources'}
            or packet['schema'] != 'twin.task-source-packet/v1' or q.canonical(packet) != raw
            or not isinstance(packet['task'], dict)):
        raise ValueError('exact canonical protected task source packet required')
    sm.exact_day(packet['as_of'])
    return packet


def _compose(contract: TaskContract, policy: dict[str, Any], model: dict[str, Any], packet: dict[str, Any],
             metadata: dict[str, Any], party_sha: str) -> dict[str, Any]:
    from . import gameplay_lens, causal_claims
    target, task = packet['target'], packet['task']
    definitions = model['definitions']
    kind = {'evolution': 'component', 'causal': 'edge', 'gameplay': 'map', 'ethics': 'sensor'}[contract.task]
    validate('Target' + kind.title(), target)
    if target['kind'] != kind:
        raise ValueError('registered task target kind differs')
    built: dict[str, Any]
    if contract.task == 'evolution':
        if set(task) != {'evidence'} or target['component'] not in definitions:
            raise ValueError('fixed task component/evidence is absent from actual model')
        built = {'component': definitions[target['component']], 'evidence': task['evidence']}
    elif contract.task == 'causal':
        if (set(task) != {'evidence', 'measurement'} or target['from'] == target['to']
                or any(target[key] not in definitions for key in ('from', 'to'))):
            raise ValueError('fixed ordered causal pair/source measurement differs')
        neighbours: dict[str, set[str]] = {}
        for edge in model['graph']['edges']:
            neighbours.setdefault(edge['from'], set()).add(edge['to'])
            neighbours.setdefault(edge['to'], set()).add(edge['from'])
        confounders = sorted((neighbours.get(target['from'], set()) & neighbours.get(target['to'], set())) - {target['from'], target['to']})
        names = model['names']
        built = {**task, 'from': definitions[target['from']], 'to': definitions[target['to']],
                 'candidate_confounders': [{'id': name, 'name': names[name]} for name in confounders]}
    elif contract.task == 'gameplay':
        if task or target['organisation'] != policy['organisation'] or len(definitions) != 20:
            raise ValueError('complete actual twenty-definition adopter map required')
        built = {**model['graph'], 'components': [definitions[name] for name in sorted(definitions)],
                 'catalogue': ['exploit-commoditisation', 'land-grab'],
                 'catalogue_source_sha256': sm.sha256(Path(gameplay_lens.__file__).read_bytes())}
    else:
        built = dict(task)
        validate('EthicsTask', built)
        table = built['sensor_table']
        from .ethics_gate import load_sensors, SENSOR_REQUIRED
        actual_table = [{key: row[key] for key in SENSOR_REQUIRED} for row in load_sensors()['sensors']]
        if (q.canonical(table) != q.canonical(actual_table)
                or len({item['sensor'] for item in table}) != len(table)
                or built['sensor_table_sha256'] != q.digest(table)
                or built['sensor']['id'] != target['sensor']
                or not any(item['sensor'] == target['sensor'] and item['name'] == built['sensor']['name'] for item in table)
                or built['policy']['sha256'] != target['policy_sha256']
                or sm.sha256(built['policy']['text'].encode()) != target['policy_sha256']
                or built['policy']['as_of'] > packet['as_of']):
            raise ValueError('actual named sensor/table/policy identity differs')
        originals = packet['original_sources']
        if not any(record['sha256'] == target['policy_sha256'] and record['identity'] == built['policy']['identity']
                   and record['version'] == built['policy']['version'] for members in originals.values() for record in members.values()):
            raise ValueError('policy is not retained in an acquired original source')
        if built['dpia']['complete']:
            source_id = built['dpia']['completion_source_id']
            if source_id not in originals:
                raise ValueError('DPIA completion lacks acquired source')
            wanted = {'sensor': target['sensor'], 'policy_sha256': target['policy_sha256'],
                      'as_of': packet['as_of'], 'complete': True}
            found = False
            for record in originals[source_id].values():
                try:
                    found |= q.canonical(decode(_record_bytes(record))) == q.canonical(wanted)
                except ValueError:
                    pass
            if not found:
                raise ValueError('DPIA completion source does not bind sensor/policy/date')
    public_context = {key: policy[key] for key in ('organisation', 'domain', 'capability', 'frame', 'model_as_of', 'model_pins')}
    public_context.update(as_of=packet['as_of'], party_sha256=party_sha, metadata=metadata)
    payload = {'schema': f'twin.{contract.task}-input/v2', 'context': public_context, 'target': target, 'task': built}
    validate(contract.task.title() + 'Input', payload)
    for item in built.get('evidence', []):
        public = metadata.get(item['source_id'])
        if public is None:
            raise ValueError('evidence source is not independently acquired')
        text = public['statement']['text'] if item['visible_excerpt_id'] is None else next((
            excerpt['witness']['text_utf8'] for excerpt in public['visible_excerpts'] if excerpt['id'] == item['visible_excerpt_id']), None)
        if item['statement'] != text:
            raise ValueError('evidence does not identify the exact acquired statement/excerpt')
    ids = [item['id'] for item in built.get('evidence', [])]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate task evidence identity')
    return payload


def _exact_context(contract: TaskContract, model: dict[str, Any]) -> dict[str, Any]:
    policy = model['policy']
    return {'model_pins': policy['model_pins'], 'model_as_of': policy['model_as_of'],
        'party_sha256': model['party_sha256'], 'input_constructor_sha256': _constructor(contract, policy),
        'task_contract_sha256': contract.digest, 'universe_sha256': q.digest({key: model[key] for key in ('definitions', 'graph', 'names')}),
        'policy_sha256': model['policy_sha256'], 'metadata_policy_sha256': q.digest(policy['metadata_policies'])}


@dataclass(frozen=True)
class ResolvedTaskInput:
    description: bytes
    _model: bytes = field(repr=False)
    _store: sm.MetadataStore = field(repr=False, compare=False)
    _contract: TaskContract = field(repr=False)
    _authentication: bytes = field(repr=False)

    @property
    def host_record(self) -> dict[str, Any]:
        return decode(self.description)

    @property
    def payload(self) -> dict[str, Any]:
        return self.host_record['input']

    def host_inputs(self) -> q.HostInputs:
        policy = TaskPolicy.freeze(self._contract, (self,))
        return q.HostInputs.freeze((self.host_record,), (self.host_record['issuer'],), task_policy=policy)


def resolve_task_input(contract: TaskContract, protected_job: dict[str, Any], repo: ModelRepo,
                       source_store: sm.MetadataStore, party_bytes: bytes, party_pin: str) -> ResolvedTaskInput:
    contract.verify()
    job = protected_job
    if set(job) != JOB_FIELDS or not isinstance(job['source_packet'], bytes) or sm.sha256(job['source_packet']) != job['source_pin']:
        raise ValueError('exact independently pinned protected task job required')
    for key in ('subject', 'issuer', 'organisation', 'domain', 'capability', 'frame', 'source'):
        if not isinstance(job[key], str) or not job[key].strip():
            raise ValueError('missing protected task identity: ' + key)
    sm.exact_day(job['as_of']); sm.exact_day(job['model_as_of'])
    if source_store.purpose == 'TEST_ONLY' and not job['issuer'].startswith('TEST_ONLY'):
        raise ValueError('TEST_ONLY task sources cannot become actual host imports')
    if sm.sha256(party_bytes) != party_pin:
        raise ValueError('actual protected party pin differs')
    party = load_yaml(party_bytes.decode())
    if not isinstance(party, dict) or party.get('id') != job['organisation']:
        raise ValueError('task party belongs to another adopter')
    current = ModelRepo.open(repo.model_root, ref=repo.pin.commit)
    if current.pin != repo.pin:
        raise ValueError('actual clean model pin differs')
    overlay = Overlay.load(current, job['organisation'], pricing_threshold=evidence.declared_threshold(party))
    pins = {'model_repo': current.pin.as_dict(), 'overlay': overlay.ref.as_dict(), 'world': overlay.world.ref.as_dict()}
    if pins != job['model_pins']:
        raise ValueError('actual task model closure differs from independently pinned job')
    from .gameplay_lens import payload_for
    definitions = {**overlay.world.components, **overlay.components}
    if len(definitions) != 20:
        raise ValueError('complete actual twenty-definition task model required')
    graph = overlay.graph()
    model_sources = {}
    for label, ref in (('world', overlay.world.ref), ('overlay', overlay.ref)):
        for path in current.list_tree(ref.tree):
            if path == 'meta.yaml' or path.startswith(('components/', 'people/', 'edges/', 'regrades/')):
                model_sources[f'model-{label}:{path}'] = source_record(
                    current.read_blob(ref.tree, path), 'model:' + ref.path + '/' + path, ref.commit)
    model = {'policy': {key: job[key] for key in _POLICY_FIELDS}, 'party_sha256': party_pin,
        'original_model_sources': model_sources,
        'policy_sha256': job['target'].get('policy_sha256'), 'definitions': definitions,
        'graph': payload_for(overlay), 'names': {**{key: value['name'] for key, value in definitions.items()},
                  **{key: value.get('role', key) for key, value in graph.people.items()}}}
    packet = _packet(job['source_packet'])
    if any(packet[key] != job[key] for key in ('subject', 'as_of', 'target')):
        raise ValueError('source packet differs from independently selected subject/date/target')
    public = _metadata(source_store, job['metadata_policies'], job['source_bindings'], packet['original_sources'])
    payload = _compose(contract, model['policy'], model, packet, public, party_pin)
    sources = {'task_packet': source_record(job['source_packet'], job['source'], job['source_pin']),
               'party': source_record(party_bytes, job['organisation'], party_pin),
               **model_sources, **{f'{sid}:{name}': record for sid, members in packet['original_sources'].items() for name, record in members.items()}}
    context = {key: job[key] for key in ('estate_scope_sha256', 'organisation', 'domain', 'capability', 'frame', 'source', 'as_of', 'model_as_of', 'model_pins')}
    context.update(source_families=sorted({item['source']['family'] for item in public.values()}),
        source_sha256=q.digest(payload), party_sha256=party_pin, input_constructor_sha256=_constructor(contract, model['policy']),
        task_contract_sha256=contract.digest, target=job['target'], original_sources_sha256=q.digest(sources),
        source_metadata_bindings=job['source_bindings'], source_metadata_public_sha256={key: q.digest(value) for key, value in public.items()})
    validate('HostContext', context)
    record = {'subject': job['subject'], 'issuer': job['issuer'], 'input': payload, 'context': context,
              'source': source_record(q.canonical(payload), job['source'], job['source_pin']), 'sources': sources}
    raw, closure = q.canonical(record), q.canonical(model)
    return ResolvedTaskInput(raw, closure, source_store, contract, hmac.digest(_KEY, raw + closure, 'sha256'))


@dataclass(frozen=True)
class TaskPolicy:
    description: bytes
    _models: bytes = field(repr=False)
    _stores: dict[str, sm.MetadataStore] = field(repr=False, compare=False)
    _contract: TaskContract = field(repr=False)
    _authentication: bytes = field(repr=False)

    @classmethod
    def freeze(cls, contract: TaskContract, inputs: tuple[ResolvedTaskInput, ...]) -> TaskPolicy:
        contract.verify()
        if not inputs:
            raise ValueError('task policy requires actual constructed model/source handles')
        models: dict[str, Any] = {}
        stores: dict[str, sm.MetadataStore] = {}
        for item in inputs:
            if (item._contract.description != contract.description
                    or not hmac.compare_digest(item._authentication, hmac.digest(_KEY, item.description + item._model, 'sha256'))):
                raise ValueError('task policy cannot import public claimed construction')
            model = decode(item._model)
            org = model['policy']['organisation']
            if org in models and models[org] != model:
                raise ValueError('one exact qualified task model context per adopter required')
            models[org], stores[org] = model, item._store
        raw_models = q.canonical(models)
        description = q.canonical({'schema': 'twin.task-policy/v1', 'contract': decode(contract.description),
            'contexts': {org: _exact_context(contract, model) for org, model in models.items()},
            'models_sha256': sm.sha256(raw_models), 'sources': _sources()})
        result = cls(description, raw_models, stores, contract, hmac.digest(_KEY, description + raw_models, 'sha256'))
        for item in inputs:
            result.verify_input(item.host_record)
        return result

    @property
    def digest(self) -> str:
        return sm.sha256(self.description)

    @property
    def contract(self) -> TaskContract:
        return self._contract

    def verify(self) -> None:
        self._contract.verify()
        if not hmac.compare_digest(self._authentication, hmac.digest(_KEY, self.description + self._models, 'sha256')):
            raise ValueError('task policy requires independently constructed protected handles')
        value = decode(self.description)
        if value['sources'] != _sources() or value['models_sha256'] != sm.sha256(self._models):
            raise ValueError('task constructor/model/helper support changed')
        for org, model in decode(self._models).items():
            if value['contexts'][org] != _exact_context(self._contract, model):
                raise ValueError('task model/constructor policy identity changed')
            for policy in model['policy']['metadata_policies'].values():
                sm.validate_parent_policy(policy, self._stores.get(org))

    def verify_input(self, row: dict[str, Any]) -> None:
        self.verify()
        try:
            context = row['context']
            validate('HostContext', context)
            model = decode(self._models)[context['organisation']]
            policy = model['policy']
            if any(context[key] != policy[key] for key in ('estate_scope_sha256', 'organisation', 'domain', 'capability', 'frame', 'source', 'model_as_of', 'model_pins')):
                raise ValueError('task host context differs from actual qualified model/party/scope')
            sources = row['sources']
            packet = _packet(_record_bytes(sources['task_packet']))
            party = _record_bytes(sources['party'])
            if (row.get('issuer') != policy['issuer'] or packet['subject'] != row['subject']
                    or any(context[key] != packet[key] for key in ('as_of', 'target'))
                    or context['source_sha256'] != q.digest(row['input']) or context['original_sources_sha256'] != q.digest(sources)
                    or sm.sha256(party) != model['party_sha256'] or context['party_sha256'] != model['party_sha256']
                    or context['input_constructor_sha256'] != _constructor(self._contract, policy)
                    or context['task_contract_sha256'] != self._contract.digest):
                raise ValueError('actual task source/party/date/target/constructor differs')
            public = _metadata(self._stores[context['organisation']], policy['metadata_policies'],
                               context['source_metadata_bindings'], packet['original_sources'])
            if (context['source_metadata_public_sha256'] != {key: q.digest(value) for key, value in public.items()}
                    or context['source_families'] != sorted({value['source']['family'] for value in public.values()})
                    or q.canonical(_compose(self._contract, policy, model, packet, public, model['party_sha256'])) != q.canonical(row['input'])):
                raise ValueError('actual full task input/source/closure differs from public claims')
            expected_sources = {'task_packet': sources['task_packet'], 'party': sources['party'],
                **model['original_model_sources'], **{f'{sid}:{name}': record for sid, members in packet['original_sources'].items() for name, record in members.items()}}
            if sources != expected_sources:
                raise ValueError('task original source members changed or disappeared')
        except (KeyError, TypeError) as exc:
            raise ValueError('missing protected typed task input/model/source context') from exc


def reference_row(case: dict[str, Any]) -> dict[str, Any]:
    """Separate custody scope metadata from the identical actual host input core."""
    return {**case, 'subject': case['id'], 'context': {key: value for key, value in case['context'].items()
            if key not in ('purpose', 'claim', 'metric')}}


def _witness(witness: dict[str, Any], payload: dict[str, Any]) -> None:
    validate('Witness', witness)
    cursor: Any = payload
    try:
        for step in witness['path']:
            if type(step) is not int and not isinstance(step, str) or type(step) is int and step < 0:
                raise ValueError('invalid task witness path')
            cursor = cursor[step]
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError('task witness does not locate actual public input') from exc
    if 'quote' in witness:
        if not isinstance(cursor, str) or witness['quote'] not in cursor:
            raise ValueError('task quotation lacks literal public input witness')
    elif q.canonical(cursor) != q.canonical(witness['value']):
        raise ValueError('task value witness differs from actual public input')


def verify_output(payload: dict[str, Any], stated: q.Stated) -> None:
    """Mechanical target/witness consistency only; never semantic entailment."""
    if stated.answer is None:
        if stated.basis is not None:
            validate('Decline', stated.basis)
            if not stated.basis['decline'].strip():
                raise ValueError('factual task decline requires actual reason')
        return
    schema = payload.get('schema')
    task = next((name for name in ('evolution', 'causal', 'gameplay', 'ethics') if schema == f'twin.{name}-input/v2'), None)
    if task is None:
        raise ValueError('actual complete typed task input required')
    validate_payload(payload)
    validate(task.title() + 'Answer', stated.answer)
    validate('GameplayBasis' if task == 'gameplay' else 'Basis', stated.basis)
    for witness in stated.basis['witnesses']:
        _witness(witness, payload)
    answer, target = stated.answer, payload['target']
    if task == 'causal':
        edge = answer['edge']
        measurement = payload['task']['measurement']
        expected_units = {'from': measurement['from_unit'], 'to': measurement['to_unit'], 'lag': measurement['lag_unit'],
                          'elasticity_definition': measurement['elasticity_definition']}
        if (any(edge[key] != target[key] for key in ('from', 'to')) or answer['units'] != expected_units
                or not edge['elasticity']['min'] <= edge['elasticity']['mode'] <= edge['elasticity']['max']
                or len({item['id'] for item in answer['confounders']}) != len(answer['confounders'])
                or {item['id'] for item in answer['confounders']} != {item['id'] for item in payload['task']['candidate_confounders']}):
            raise ValueError('complete causal target/units/confounder/PERT binding differs')
    elif task == 'gameplay':
        checks = stated.basis['checks']
        pairs = [(item['play'], item['component']) for item in checks]
        required = {(play, component) for play in payload['task']['catalogue'] for component in payload['task']['org_components']}
        opportunities = [(item['play'], item['component']) for item in answer['opportunities']]
        if (len(set(pairs)) != len(pairs) or set(pairs) != required
                or len(set(opportunities)) != len(opportunities)
                or set(opportunities) != {pair for pair, check in zip(pairs, checks) if check['present']}):
            raise ValueError('complete positive/negative gameplay set/check domain differs')
        for check in checks:
            for witness in check['witnesses']:
                _witness(witness, payload)
    elif task == 'ethics':
        ladder = answer['ladder']; rungs = ladder['rungs']; names = ['purpose', 'necessity', 'proportionality']
        stop = ladder['stopped_at']
        if ([item['rung'] for item in rungs] != names[:len(rungs)] or len(rungs) > 3
                or any(not item['passed'] for item in rungs[:-1])
                or stop is None and (len(rungs) != 3 or not all(item['passed'] for item in rungs))
                or stop is not None and (stop != names[len(rungs) - 1] or rungs[-1]['passed'] or answer['admitted'])):
            raise ValueError('ethics ladder must be the exact verified ordered stopping prefix')


def validate_payload(payload: dict[str, Any]) -> None:
    """Public shape/projection consistency only; this never supplies acquisition."""
    if not isinstance(payload, dict):
        raise ValueError('complete typed public task input required')
    task = next((name for name in ('evolution', 'causal', 'gameplay', 'ethics')
                 if payload.get('schema') == f'twin.{name}-input/v2'), None)
    if task is None:
        raise ValueError('unsupported public task input')
    validate(task.title() + 'Input', payload)
    for public in payload['context']['metadata'].values():
        sm.validate_public_projection(public)
    target, data = payload['target'], payload['task']
    if task == 'evolution' and data['component']['id'] != target['component']:
        raise ValueError('public component target differs')
    if task == 'causal':
        if target['from'] == target['to'] or any(data[key]['id'] != target[key] for key in ('from', 'to')):
            raise ValueError('public ordered pair target differs')
        if len({item['id'] for item in data['candidate_confounders']}) != len(data['candidate_confounders']):
            raise ValueError('duplicate public confounder')
    if task == 'gameplay':
        ids = [item['id'] for item in data['components']]
        if (len(set(ids)) != 20 or target['organisation'] != payload['context']['organisation']
                or set(item['component'] for item in data['positions']) != set(ids)
                or len(data['positions']) != len(ids) or not set(data['org_components']) <= set(ids)
                or len({item['id'] for item in data['edges']}) != len(data['edges'])):
            raise ValueError('public complete gameplay model target/domain differs')
    if task == 'ethics':
        if (data['sensor']['id'] != target['sensor'] or data['policy']['sha256'] != target['policy_sha256']
                or sm.sha256(data['policy']['text'].encode()) != target['policy_sha256']
                or data['sensor_table_sha256'] != q.digest(data['sensor_table'])):
            raise ValueError('public sensor/policy target differs')
    ids = []
    for item in data.get('evidence', []):
        ids.append(item['id'])
        public = payload['context']['metadata'].get(item['source_id'])
        if public is None:
            raise ValueError('public evidence source absent')
        text = public['statement']['text'] if item['visible_excerpt_id'] is None else next((
            excerpt['witness']['text_utf8'] for excerpt in public['visible_excerpts'] if excerpt['id'] == item['visible_excerpt_id']), None)
        if item['statement'] != text:
            raise ValueError('public evidence witness differs')
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate public evidence id')
