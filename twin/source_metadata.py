"""Protected acquisition of retained source metadata, never candidate-selected authority.

Byte checks conserve the attributed custodian interpretation. They neither authenticate a
publisher nor establish historical first publication. No executable is selected from a packet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import hashlib
import inspect
import json
from pathlib import Path
import re
from typing import Any, Callable
from types import ModuleType


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate metadata key: ' + key)
        result[key] = value
    return result


def _json(raw: bytes) -> Any:
    try:
        return json.loads(raw, object_pairs_hook=_unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (UnicodeError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('invalid metadata JSON') from exc


def _helper_identities() -> dict[str, Any]:
    from .qualification import _callable_identity
    return {name: _callable_identity(fn) for name, fn in globals().items()
            if inspect.isfunction(fn) and fn.__module__ == __name__}


SCHEMA_PATH = Path(__file__).with_name('source_metadata.schema.json')


def _shape(value: Any, rule: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate the closed, vendored contract without a new runtime dependency."""
    if '$ref' in rule:
        return _shape(value, schema['$defs'][rule['$ref'].split('/')[-1]], schema)
    for choice in ('oneOf', 'anyOf'):
        if choice in rule:
            matches = 0
            for option in rule[choice]:
                try:
                    _shape(value, option, schema)
                    matches += 1
                except ValueError:
                    pass
            if matches != 1 and choice == 'oneOf' or not matches:
                raise ValueError('metadata schema alternative differs')
            return
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'null': type(None), 'boolean': bool}
    if 'type' in rule and type(value) is not types[rule['type']]:
        raise ValueError('metadata schema type differs')
    if 'const' in rule and (type(value) is not type(rule['const']) or value != rule['const']):
        raise ValueError('metadata schema constant differs')
    if 'enum' in rule and value not in rule['enum']:
        raise ValueError('metadata schema enum differs')
    if isinstance(value, dict):
        properties = rule.get('properties', {})
        if not set(rule.get('required', ())) <= set(value):
            raise ValueError('metadata schema missing fields')
        if rule.get('additionalProperties') is False and set(value) - set(properties):
            raise ValueError('metadata schema unknown fields')
        if len(value) < rule.get('minProperties', 0):
            raise ValueError('metadata schema empty map')
        for key, child in value.items():
            child_rule = properties.get(key, rule.get('additionalProperties', {}))
            if isinstance(child_rule, dict):
                _shape(child, child_rule, schema)
    if isinstance(value, list):
        if len(value) < rule.get('minItems', 0):
            raise ValueError('metadata schema empty list')
        if rule.get('uniqueItems') and len({canonical(item) for item in value}) != len(value):
            raise ValueError('metadata schema duplicate members')
        for child in value:
            _shape(child, rule.get('items', {}), schema)
    if isinstance(value, str):
        if len(value) < rule.get('minLength', 0) or ('pattern' in rule and not re.search(rule['pattern'], value)):
            raise ValueError('metadata schema text/hash differs')
    if type(value) is int and (value < rule.get('minimum', value) or value > rule.get('maximum', value)):
        raise ValueError('metadata schema interval differs')


def exact_day(value: Any) -> str:
    try:
        if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) or date.fromisoformat(value).isoformat() != value:
            raise ValueError('invalid exact ISO day')
    except (TypeError, ValueError) as exc:
        raise ValueError('invalid exact ISO day') from exc
    return value


def _instant(value: str) -> datetime:
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
            raise ValueError('offset required')
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.utcoffset() is None:
            raise ValueError('offset required')
        return result
    except (TypeError, ValueError) as exc:
        raise ValueError('invalid source offset timestamp') from exc


def normalize_publication(observation: dict[str, Any]) -> tuple[str, str]:
    literal, rule = observation['literal_value'], observation['normalization']
    if rule == 'literal-iso-day':
        return 'day', exact_day(literal)
    if rule == 'source-local-calendar-day':
        return 'day', _instant(literal).date().isoformat()
    if rule == 'english-month-year':
        months = ('January February March April May June July August September October November December').split()
        parts = literal.split(' ')
        if len(parts) == 2 and parts[0] in months and re.fullmatch(r'\d{4}', parts[1]) and 1 <= int(parts[1]) <= 9999:
            return 'month', parts[1] + '-' + str(months.index(parts[0]) + 1).zfill(2)
    raise ValueError('unestablished publication normalization')


def _artifact(archive: dict[str, bytes], pin: str) -> bytes:
    raw = archive.get(pin)
    if not isinstance(raw, bytes) or sha256(raw) != pin:
        raise ValueError('missing or changed retained artifact')
    return raw


def retained_receipt_adapter(acquisition: dict[str, Any], artifacts: dict[str, bytes],
                             policy: dict[str, Any]) -> None:
    """Resolve an independently retained receipt entry, never a packet-authored receipt."""
    entry = _json(_artifact(artifacts, acquisition['receipt_artifact_sha256']))
    pointer = acquisition['receipt_entry_pointer']
    try:
        for token in pointer.split('/')[1:] if pointer else ():
            if re.search(r'~(?![01])', token) or isinstance(entry, list) and not re.fullmatch(r'0|[1-9]\d*', token):
                raise ValueError('invalid retained receipt JSON pointer')
            token = token.replace('~1', '/').replace('~0', '~')
            entry = entry[int(token)] if isinstance(entry, list) else entry[token]
        expected = {key: value for key, value in acquisition.items()
                    if key not in ('receipt_artifact_sha256', 'receipt_entry_pointer')}
        if entry != expected:
            raise ValueError('original acquisition receipt entry differs')
        if acquisition['kind'] == 'TEST_ONLY-fixture' and policy['purpose'] != 'TEST_ONLY':
            raise ValueError('TEST_ONLY acquisition cannot enter actual import')
        if acquisition['kind'] == 'retained-http' and not 200 <= acquisition['response_status'] < 300:
            raise ValueError('original acquisition did not succeed')
        _instant(acquisition['captured_at'])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError('missing original acquisition receipt entry') from exc


def _reference(ref: dict[str, Any], members: dict[str, Any]) -> dict[str, Any]:
    member = members.get(ref['member_id'])
    if member is None or member['sha256'] != ref['sha256']:
        raise ValueError('source parent member/hash differs')
    return member


def _witness(witness: dict[str, Any], members: dict[str, Any], archive: dict[str, bytes],
             origin: str) -> None:
    member = _reference({'member_id': witness['member_id'], 'sha256': witness['member_sha256']}, members)
    start, end = witness['start_byte'], witness['end_byte']
    raw = _artifact(archive, member['sha256'])
    if not 0 <= start < end <= len(raw) or raw[start:end] != witness['text_utf8'].encode('utf-8'):
        raise ValueError('source witness span/bytes differ')
    if (member['role'] == 'producer-qualifier') != (origin == 'producer-authored'):
        raise ValueError('source witness origin role differs')
    if member['role'] == 'derived-extraction':
        if member['transform']['lineage_status'] != 'pinned':
            raise ValueError('unestablished extraction lineage held')
        if any(span['kind'] == 'syntactic-separator' and start < span['output_end'] and end > span['output_start']
               for span in member['lineage']):
            raise ValueError('transform syntax is not publisher content')


def retained_source_checker(manifest: dict[str, Any], archive: dict[str, bytes],
                            receipts: dict[str, bytes], policy: dict[str, Any]) -> None:
    """Conserve exact bytes and the actual named custodian's bounded interpretation."""
    members = manifest['members']
    primary = 0
    for key, member in members.items():
        if key != member['id'] or len(_artifact(archive, member['sha256'])) != member['bytes']:
            raise ValueError('source member ID/bytes differ')
        if member['role'] == 'acquired-original':
            receipt = manifest['acquisitions'].get(member['acquisition_id'])
            if (receipt is None or receipt['body_sha256'] != member['sha256'] or receipt['body_bytes'] != member['bytes']
                    or member['identity'] not in (receipt['requested_url'], receipt['final_url'])):
                raise ValueError('original source receipt/body/URL differs')
            if member['purpose'] == 'primary':
                primary += 1
                if member['identity'] != manifest['source']['url'] or member['version'] != manifest['source']['version']:
                    raise ValueError('primary original source identity/version differs')
        elif member['role'] == 'producer-qualifier':
            _instant(member['authorship']['authored_at'])
            if member['authorship']['kind'] == 'TEST_ONLY' and policy['purpose'] != 'TEST_ONLY':
                raise ValueError('TEST_ONLY qualifier cannot enter actual import')
            for ref in member['support_members']:
                if _reference(ref, members)['role'] == 'producer-qualifier':
                    raise ValueError('qualifier support requires publisher source')
        else:
            parent = _reference(member['parent'], members)
            if parent['role'] != 'acquired-original':
                raise ValueError('extraction requires acquired original parent')
            transform = member['transform']
            if transform['lineage_status'] != 'pinned' or any(transform[key] is None for key in transform):
                raise ValueError('unestablished extraction lineage held; no invented legacy pins')
            approved = {key: transform[key] for key in ('identity', 'version', 'implementation_artifact_sha256', 'configuration_sha256')}
            if approved not in policy['allowed_transforms']:
                raise ValueError('source transform is not host approved')
            for key in ('implementation_artifact_sha256', 'configuration_sha256'):
                _artifact(archive, transform[key])
            execution = _json(_artifact(receipts, transform['execution_receipt_artifact_sha256']))
            if execution != {'schema': 'twin.source-transform-receipt/v1', **approved,
                    'parent_sha256': parent['sha256'], 'output_sha256': member['sha256'],
                    'output_bytes': member['bytes'], 'exit_code': 0}:
                raise ValueError('source transform execution receipt differs')
            output, original, cursor = _artifact(archive, member['sha256']), _artifact(archive, parent['sha256']), 0
            for span in member['lineage']:
                start, end = span['output_start'], span['output_end']
                if start != cursor or not start < end <= len(output):
                    raise ValueError('source lineage gap/overlap/span differs')
                if span['kind'] == 'byte-copy':
                    ps, pe = span['parent_start'], span['parent_end']
                    if not 0 <= ps < pe <= len(original) or output[start:end] != original[ps:pe]:
                        raise ValueError('source lineage copy bytes differ')
                elif span['kind'] == 'syntactic-separator':
                    if output[start:end] != span['text_utf8'].encode('utf-8'):
                        raise ValueError('source lineage separator bytes differ')
                elif start != 0 or end != len(output) or len(member['lineage']) != 1:
                    raise ValueError('whole transform must cover complete retained output')
                cursor = end
            if cursor != len(output):
                raise ValueError('source lineage does not cover output')
    if primary != 1:
        raise ValueError('exactly one primary acquired original required')
    for key, observation in manifest['observations'].items():
        if key != observation['id']:
            raise ValueError('metadata observation ID differs')
        _witness(observation['witness'], members, archive, 'publisher-quotation')
        text = observation['witness']['text_utf8']
        if observation['literal_value'] not in text or observation['metadata_key'] is not None and observation['metadata_key'] not in text:
            raise ValueError('metadata literal/key lacks exact witness')
    publication = manifest['publication']
    if publication['precision'] != 'unknown':
        observation = manifest['observations'].get(publication['observation_id'])
        kinds = {'first-publication': 'publisher-first-publication', 'publication': 'publisher-publication', 'release': 'publisher-release'}
        if observation is None or observation['observed_kind'] != kinds[publication['basis']]:
            raise ValueError('publication basis/observed kind differs')
        if normalize_publication(observation) != (publication['precision'], publication['value']):
            raise ValueError('publication precision/value normalization differs')
    statement = manifest['statement']
    _witness(statement['witness'], members, archive, statement['origin_role'])
    if statement['text'] != statement['witness']['text_utf8']:
        raise ValueError('statement lacks exact source witness')
    ids = []
    for excerpt in manifest['visible_excerpts']:
        ids.append(excerpt['id'])
        _witness(excerpt['witness'], members, archive, excerpt['origin_role'])
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate visible excerpt ID')
    review = manifest['bounded_review']
    if (review['reviewer_id'] != policy['reviewer_id'] or review['reviewer_role'] != policy['reviewer_role']
            or set(review['reviewed_member_ids']) != set(members)):
        raise ValueError('protected source custodian/review scope differs')


def _runtime_helper_inventory(modules: tuple[ModuleType, ...]) -> tuple[list[dict[str, Any]], tuple[tuple[str, Any], ...]]:
    """Core-owned self-contained guard; dependencies are trusted Python/stdlib only.

    Return both a canonical description and actual dispatch targets. The authority
    privately retains the latter; supplied JSON cannot substitute for live bindings.
    """
    import hashlib
    import inspect
    import json
    import marshal
    import types
    from pathlib import Path

    bindings: list[tuple[str, Any]] = []
    active: set[int] = set()
    seen_containers: dict[int, int] = {}
    def code_identity(code: types.CodeType) -> types.CodeType:
        return code.replace(co_filename='<host-source>', co_consts=tuple(
            code_identity(v) if isinstance(v, types.CodeType) else v for v in code.co_consts))
    def encode(value: Any, name: str) -> dict[str, Any]:
        if type(value) is bytes:
            return {'type':'bytes','sha256':hashlib.sha256(value).hexdigest(),'bytes':len(value)}
        if value is None or type(value) in (str, int, bool):
            return {'type': type(value).__name__, 'value': value}
        if type(value) is float:
            json.dumps(value, allow_nan=False)
            return {'type': 'float', 'value': value}
        if inspect.isfunction(value):
            if value.__closure__:
                raise ValueError('runtime helper closure is unsupported')
            bindings.append((name, value))
            return {'type': 'function', 'module': value.__module__, 'name': value.__name__, 'qualname':value.__qualname__,
                'code': hashlib.sha256(marshal.dumps(code_identity(value.__code__))).hexdigest(),
                'defaults': encode(value.__defaults__, name + ':defaults'),
                'kwdefaults': encode(value.__kwdefaults__, name + ':kwdefaults')}
        if isinstance(value, types.ModuleType):
            bindings.append((name, value))
            return {'type': 'module', 'name': value.__name__}
        if type(value) not in (dict, list, tuple):
            raise ValueError('unsupported runtime helper dispatch/config')
        if id(value) in active:
            raise ValueError('cyclic runtime helper config')
        if id(value) in seen_containers:
            return {'type':'alias','index':seen_containers[id(value)]}
        index = seen_containers[id(value)] = len(seen_containers)
        active.add(id(value))
        try:
            contents: list[Any]
            if type(value) is dict:
                if any(type(k) is not str for k in value):
                    raise ValueError('runtime helper config keys must be strings')
                contents = [[k, encode(v, name + '/' + k)] for k, v in value.items()]
            else:
                contents = [encode(v, name + '/' + str(i)) for i, v in enumerate(value)]
            return {'type': type(value).__name__, 'index':index,'items': contents}
        finally:
            active.remove(id(value))
    inventory: list[dict[str, Any]] = []
    for module in modules:
        if not isinstance(module, types.ModuleType) or not isinstance(module.__file__, str):
            raise ValueError('actual helper module with source required')
        namespace = {}
        for name, value in sorted(vars(module).items()):
            if name in ('__name__','__doc__','__package__','__loader__','__spec__',
                        '__file__','__cached__','__builtins__','__annotations__'):
                continue
            if (inspect.isfunction(value) or isinstance(value, types.ModuleType)
                    or value is None or type(value) in (str, int, bool, float, bytes, dict, list, tuple)):
                namespace[name] = encode(value, module.__name__ + ':' + name)
            elif isinstance(value, type):
                # Data-only constructors are held by identity; arbitrary class-method
                # replacement is outside this explicit helper/function seam.
                bindings.append((module.__name__ + ':' + name, value))
            elif callable(value):
                raise ValueError('unsupported runtime helper callable dispatch')
        path = Path(module.__file__).resolve()
        inventory.append({'module': module.__name__, 'source': str(path),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'namespace': namespace})
    return inventory, tuple(bindings)


@dataclass(frozen=True)
class MetadataAuthority:
    description: bytes
    acquire_adapter: Callable[..., None] = field(repr=False)
    source_checker: Callable[..., None] = field(repr=False)
    _helper_modules: tuple[ModuleType, ...] = field(default=(), repr=False, compare=False)
    _runtime_bindings: tuple[tuple[str, Any], ...] = field(default=(), repr=False, compare=False)
    _guard: Any = field(default=None, repr=False, compare=False)
    _guard_code: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def freeze(cls, issuer: str, policy_id: str, policy_version: str, policy_sha256: str,
               acquire_adapter: Callable[..., None], source_checker: Callable[..., None], *,
               policy: dict[str, Any], helper_modules: tuple[ModuleType, ...] = ()) -> MetadataAuthority:
        from .qualification import _callable_identity, _source_name
        if (any(not isinstance(item, str) or not item for item in (issuer, policy_id, policy_version))
                or set(policy) != {'purpose', 'allowed_transforms', 'reviewer_id', 'reviewer_role'}
                or policy['purpose'] not in ('TEST_ONLY', 'actual')
                or not isinstance(policy['allowed_transforms'], list)
                or any(not isinstance(policy[key], str) or not policy[key] for key in ('reviewer_id', 'reviewer_role'))):
            raise ValueError('invalid protected metadata policy')
        if sha256(canonical(policy)) != policy_sha256:
            raise ValueError('independently pinned metadata authority policy differs')
        if (type(helper_modules) is not tuple
                or any(not isinstance(module, ModuleType) for module in helper_modules)
                or len({id(module) for module in helper_modules}) != len(helper_modules)
                or len({module.__name__ for module in helper_modules}) != len(helper_modules)):
            raise ValueError('unique actual helper module tuple required')
        functions = (acquire_adapter, source_checker)
        value = {'issuer': issuer, 'policy_id': policy_id, 'policy_version': policy_version,
            'policy': policy, 'policy_sha256': policy_sha256,
            'functions': [_callable_identity(fn) for fn in functions],
            'helpers': _helper_identities(),
            'sources': {_source_name(Path(inspect.getfile(fn))): sha256(Path(inspect.getfile(fn)).read_bytes()) for fn in functions},
            'schema_sha256': sha256(SCHEMA_PATH.read_bytes()), 'module_sha256': sha256(Path(__file__).read_bytes())}
        bindings: tuple[tuple[str, Any], ...] = ()
        guard: Any = None
        if helper_modules:
            guard = _runtime_helper_inventory
            inventory, bindings = guard(helper_modules)
            for fn in functions:
                if not any(fn.__globals__ is vars(module) for module in helper_modules):
                    raise ValueError('callback is outside actual protected helper namespace')
            value['runtime_helper_bindings'] = {'schema': 'runtime-helper-bindings/v1',
                'modules': inventory, 'guard': _callable_identity(guard), 'guard_name':guard.__name__,
                'callback_names':[fn.__name__ for fn in functions]}
        return cls(canonical(value), acquire_adapter, source_checker, helper_modules, bindings,
                   guard, guard.__code__ if guard is not None else None)

    @property
    def digest(self) -> str:
        return sha256(self.description)

    def verify(self) -> None:
        if self._helper_modules:
            guard = self._guard
            if (globals().get('_runtime_helper_inventory') is not guard
                    or guard.__code__ is not self._guard_code or guard.__closure__
                    or guard.__defaults__ is not None or guard.__kwdefaults__ is not None):
                raise ValueError('protected runtime helper guard binding changed')
            _, bindings = guard(self._helper_modules)
            if (len(bindings) != len(self._runtime_bindings)
                    or any(name != old_name or obj is not old_obj
                           for (name, obj), (old_name, old_obj) in zip(bindings, self._runtime_bindings))):
                raise ValueError('protected runtime helper binding changed')
        value = _json(self.description)
        current = self.freeze(value['issuer'], value['policy_id'], value['policy_version'], value['policy_sha256'],
                              self.acquire_adapter, self.source_checker, policy=value['policy'], helper_modules=self._helper_modules)
        if current.description != self.description:
            raise ValueError('protected metadata authority/helper source changed')


@dataclass(frozen=True)
class AcquiredMetadata:
    """Public receipt references alone cannot install this value into a protected store."""
    description: bytes

    @property
    def binding(self) -> dict[str, str]:
        return _json(self.description)['binding']

    @property
    def public(self) -> dict[str, Any]:
        return _json(self.description)['public']


def public_projection(manifest: dict[str, Any], binding: dict[str, str], archive_digest: str) -> dict[str, Any]:
    from . import signal_inputs
    return {**{key: manifest[key] for key in ('source', 'acquisitions', 'members', 'observations', 'publication', 'statement', 'visible_excerpts', 'bounded_review')},
        'schema': 'twin.source-metadata-public/v1', 'binding': binding,
        'source_metadata_manifest_sha256': binding['expected_manifest_sha256'],
        'source_archive_closure_digest': archive_digest,
        'metadata_authority_digest': binding['expected_authority_digest'],
        'metadata_acquisition_receipt_sha256': binding['expected_acquisition_receipt_sha256'],
        'input_construction_sha256': construction_identity(Path(signal_inputs.__file__))}


def validate_public_projection(public: dict[str, Any]) -> None:
    bindings = {'source_metadata_manifest_sha256', 'source_archive_closure_digest', 'metadata_authority_digest',
                'metadata_acquisition_receipt_sha256', 'input_construction_sha256', 'binding'}
    fields = {'schema', 'source', 'acquisitions', 'members', 'observations', 'publication', 'statement',
              'visible_excerpts', 'bounded_review'} | bindings
    if not isinstance(public, dict) or set(public) != fields or public['schema'] != 'twin.source-metadata-public/v1':
        raise ValueError('exact public source metadata projection required')
    binding = source_binding(policy_for(AcquiredMetadata(canonical({'binding': public['binding']}))))
    if (binding != public['binding'] or not re.fullmatch(r'[0-9a-f]{64}', public['source_archive_closure_digest'])
            or public['source_metadata_manifest_sha256'] != binding['expected_manifest_sha256']
            or public['metadata_authority_digest'] != binding['expected_authority_digest']
            or public['metadata_acquisition_receipt_sha256'] != binding['expected_acquisition_receipt_sha256']):
        raise ValueError('public metadata binding/closure differs')
    from . import signal_inputs
    if public['input_construction_sha256'] != construction_identity(Path(signal_inputs.__file__)):
        raise ValueError('public metadata input construction/helper identity changed')
    manifest = {key: value for key, value in public.items() if key not in bindings}
    manifest['schema'] = 'twin.source-metadata/v1'
    schema = _json(SCHEMA_PATH.read_bytes())
    _shape(manifest, schema, schema)
    if sha256(canonical(manifest)) != binding['expected_manifest_sha256']:
        raise ValueError('public metadata manifest digest differs')
    publication = public['publication']
    if publication['precision'] != 'unknown':
        observation = public['observations'].get(publication['observation_id'])
        kinds = {'first-publication': 'publisher-first-publication', 'publication': 'publisher-publication', 'release': 'publisher-release'}
        if (observation is None or observation['observed_kind'] != kinds[publication['basis']]
                or normalize_publication(observation) != (publication['precision'], publication['value'])):
            raise ValueError('public publication normalization/kind differs')


def validate_parent_policy(policy: dict[str, Any] | None, store: Any) -> None:
    if (not isinstance(store, MetadataStore) or not isinstance(policy, dict)
            or set(policy) != {'authority_digest', 'purpose'} or policy['purpose'] not in ('TEST_ONLY', 'actual')):
        raise ValueError('actual protected metadata store/policy required')
    authority = store.authority(policy['authority_digest'])
    if _json(authority.description)['policy']['purpose'] != policy['purpose'] or store.purpose != policy['purpose']:
        raise ValueError('protected metadata authority purpose differs')


def verify_host_metadata(row: dict[str, Any], store: Any, policy: dict[str, Any] | None) -> None:
    validate_parent_policy(policy, store)
    assert policy is not None
    binding = source_binding(row['context']['source_metadata'])
    if binding['expected_authority_digest'] != policy['authority_digest']:
        raise ValueError('source import is outside frozen metadata authority policy')
    acquired = store.resolve(**binding)
    public = row['input']['source_context']['metadata']
    if public != acquired.public or row['context']['source_metadata_public_sha256'] != sha256(canonical(public)):
        raise ValueError('host/candidate protected metadata projection differs')


class MetadataStore:
    def __init__(self, *, purpose: str = 'actual') -> None:
        if purpose not in ('actual', 'TEST_ONLY'):
            raise ValueError('protected metadata store purpose required')
        self._purpose = purpose
        self._imports: dict[str, tuple[AcquiredMetadata, MetadataAuthority, bytes, dict[str, bytes], dict[str, bytes]]] = {}
        self._receipts: dict[str, bytes] = {}

    def acquire(self, import_id: str, manifest_bytes: bytes, archive: dict[str, bytes],
                retained_receipt_artifacts: dict[str, bytes], expected_manifest_sha256: str,
                authority: MetadataAuthority) -> AcquiredMetadata:
        if not isinstance(import_id, str) or not import_id or import_id in self._imports:
            raise ValueError('metadata import ID missing or already acquired')
        authority.verify()
        if sha256(manifest_bytes) != expected_manifest_sha256:
            raise ValueError('protected metadata manifest pin differs')
        manifest = _json(manifest_bytes)
        if canonical(manifest) != manifest_bytes:
            raise ValueError('metadata manifest must be canonical JSON')
        _shape(manifest, _json(SCHEMA_PATH.read_bytes()), _json(SCHEMA_PATH.read_bytes()))
        archive, receipts = dict(archive), dict(retained_receipt_artifacts)
        for collection in (archive, receipts):
            for pin in collection:
                _artifact(collection, pin)
        policy = _json(authority.description)['policy']
        if policy['purpose'] != self._purpose:
            raise ValueError('TEST_ONLY/actual authority differs from protected store purpose')
        for key, acquisition in manifest['acquisitions'].items():
            if key != acquisition['id']:
                raise ValueError('acquisition map ID differs')
            if authority._helper_modules:
                authority.verify()
            authority.acquire_adapter(acquisition, receipts, policy)
            if authority._helper_modules:
                authority.verify()
        if authority._helper_modules:
            authority.verify()
        authority.source_checker(manifest, archive, receipts, policy)
        if authority._helper_modules:
            authority.verify()
        closure = sha256(canonical({'archive': sorted(archive), 'receipts': sorted(receipts)}))
        identities = [{**identity, 'source_sha256': sha256(Path(inspect.getfile(fn)).read_bytes())}
            for identity, fn in zip(_json(authority.description)['functions'],
                                    (authority.acquire_adapter, authority.source_checker))]
        receipt = canonical({'schema': 'twin.source-metadata-acquisition/v1', 'import_id': import_id,
            'manifest_sha256': expected_manifest_sha256, 'archive_closure_digest': closure,
            'authority_digest': authority.digest, 'actual_acquire_adapter_identity': identities[0],
            'actual_source_checker_identity': identities[1], 'disposition': 'acquired',
            'reviewer_id': policy['reviewer_id'], 'reviewer_role': policy['reviewer_role'],
            'retained_receipt_artifact_digests': sorted(receipts)})
        binding = {'import_id': import_id, 'expected_manifest_sha256': expected_manifest_sha256,
            'expected_authority_digest': authority.digest, 'expected_acquisition_receipt_sha256': sha256(receipt)}
        result = AcquiredMetadata(canonical({'binding': binding, 'public': public_projection(manifest, binding, closure)}))
        self._imports[import_id] = result, authority, manifest_bytes, archive, receipts
        self._receipts[sha256(receipt)] = receipt
        return result

    def resolve(self, import_id: str, expected_manifest_sha256: str, expected_authority_digest: str,
                expected_acquisition_receipt_sha256: str) -> AcquiredMetadata:
        try:
            result, authority, manifest, archive, receipts = self._imports[import_id]
        except KeyError as exc:
            raise ValueError('no actual protected metadata acquisition for import') from exc
        authority.verify()
        expected = {'import_id': import_id, 'expected_manifest_sha256': expected_manifest_sha256,
            'expected_authority_digest': expected_authority_digest,
            'expected_acquisition_receipt_sha256': expected_acquisition_receipt_sha256}
        if expected != result.binding or sha256(self.receipt(expected_acquisition_receipt_sha256)) != expected_acquisition_receipt_sha256:
            raise ValueError('protected metadata manifest/authority/acquisition binding differs')
        # Revalidate held bytes and actual callbacks; a public dictionary is never the handle.
        check = MetadataStore(purpose=self._purpose).acquire(import_id, manifest, archive, receipts, expected_manifest_sha256, authority)
        if check.description != result.description:
            raise ValueError('retained metadata acquisition changed')
        authority.verify()
        return result

    def receipt(self, pin: str) -> bytes:
        try:
            return self._receipts[pin]
        except KeyError as exc:
            raise ValueError('actual protected acquisition receipt absent') from exc

    def authority(self, digest: str) -> MetadataAuthority:
        for _, authority, _, _, _ in self._imports.values():
            if authority.digest == digest:
                authority.verify()
                return authority
        raise ValueError('metadata authority was not independently acquired')

    @property
    def purpose(self) -> str:
        return self._purpose


def source_binding(policy: dict[str, Any]) -> dict[str, str]:
    names = ('import_id', 'manifest_sha256', 'authority_digest', 'acquisition_receipt_sha256')
    if (not isinstance(policy, dict) or set(policy) != set(names)
            or any(not isinstance(policy[key], str) or not policy[key] for key in names)
            or any(not re.fullmatch(r'[0-9a-f]{64}', policy[key]) for key in names[1:])):
        raise ValueError('exact protected source metadata policy required')
    return {'import_id': policy['import_id'], **{'expected_' + key: policy[key] for key in names[1:]}}


def policy_for(acquired: AcquiredMetadata) -> dict[str, str]:
    return {key.removeprefix('expected_'): value for key, value in acquired.binding.items()}


def require_known_age(public: dict[str, Any]) -> None:
    if public['publication']['precision'] == 'unknown':
        raise ValueError('unknown source age cannot satisfy known-age policy')


def construction_identity(constructor_path: Path) -> str:
    from .qualification import _callable_identity
    from . import signal_inputs
    return sha256(canonical({'version': 'protected-source-construction/v3', 'sources': {
        path.name: sha256(path.read_bytes()) for path in (constructor_path, Path(__file__), SCHEMA_PATH)},
        'helpers': _helper_identities(), 'constructor_callables': {
            'constructor': _callable_identity(signal_inputs.resolve_signal_input),
            'binding_reader': _callable_identity(signal_inputs.binding_context)}}))
