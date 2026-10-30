"""One protected source/model projection for qualification and live signal input.

Pins and policy are supplied independently by the protected parent, never read from a child
response. The repository is already staged by the existing emitter. This module neither stages
repositories nor authenticates a publisher or a feed relationship from its display name.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from . import evidence, qualification as q, source_metadata as sm
from .ingest import candidates_of
from .model import Overlay
from .reference_cases import source_record
from .repo import ModelRepo, load_yaml


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError('missing source input text: ' + field)
    return value


def _date(value: Any, field: str) -> str:
    try:
        valid = isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        valid = False
    if not valid:
        raise ValueError('invalid source input date: ' + field)
    return value


def _object(value: Any, field: str, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    if (not isinstance(value, dict) or not required <= set(value)
            or set(value) - required - (optional or set())):
        raise ValueError('source input shape differs: ' + field)
    return value


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate source packet field: ' + key)
        value[key] = item
    return value


def _original_sources(context: dict[str, Any]) -> dict[str, Any]:
    originals = context.get('original_sources')
    if not isinstance(originals, dict) or not originals:
        raise ValueError('original source records are required')
    bodies = []
    primary = False
    for key, value in originals.items():
        if (not isinstance(key, str) or not key or not isinstance(value, dict)
                or set(value) != {'identity', 'version', 'content_base64', 'bytes', 'sha256'}):
            raise ValueError('original source record shape differs')
        try:
            raw = base64.b64decode(value['content_base64'], validate=True)
            if (type(value['bytes']) is not int or len(raw) != value['bytes']
                    or hashlib.sha256(raw).hexdigest() != value['sha256']):
                raise ValueError('original source bytes/hash mismatch')
            _text(value['identity'], 'original identity')
            _text(value['version'], 'original version')
        except (TypeError, KeyError) as exc:
            raise ValueError('invalid original source bytes') from exc
        primary |= value['identity'] == context['url'] and value['version'] == context['version']
        bodies.append(raw)
    if not primary:
        raise ValueError('original source URL/version does not match primary member')
    excerpts = context.get('excerpts')
    if (not isinstance(excerpts, list) or any(not isinstance(quote, str) or not quote
            or not any(quote.encode('utf-8') in body for body in bodies) for quote in excerpts)):
        raise ValueError('source excerpt lacks an original byte witness')
    return originals


def binding_context(payload: dict[str, Any], *, test_only: q.TestOnlyPurpose | None = None) -> dict[str, Any]:
    """Validate the complete input-only projection and derive its qualification identity.

    The protected constructor authenticates source bytes/closure separately. This shared
    reader prevents a qualification packet from claiming another live universe or model.
    """
    if (not isinstance(payload, dict) or set(payload) != {
            'statement', 'source', 'source_context', 'model_context', 'candidates'}
            or any(not isinstance(payload[key], str) or not payload[key] for key in ('statement', 'source'))):
        raise ValueError('exact input-only signal projection required')
    choices = payload['candidates']
    if (not isinstance(choices, list) or len(choices) != 20
            or any(not isinstance(item, dict) or set(item) != {'id', 'name', 'definition'}
                   or not isinstance(item['id'], str) or not item['id']
                   or not isinstance(item['name'], str) or not item['name']
                   or not isinstance(item['definition'], dict)
                   or item['definition'].get('id') != item['id']
                   or item['definition'].get('name') != item['name'] for item in choices)
            or len({item['id'] for item in choices}) != 20):
        raise ValueError('all twenty distinct full source definitions required')
    model = _object(payload['model_context'], 'model context',
        {'organisation', 'domain', 'capability', 'frame', 'as_of', 'pins'})
    for field in ('organisation', 'domain', 'capability', 'frame'):
        _text(model[field], 'model context ' + field)
    _date(model['as_of'], 'model context as_of')
    if not isinstance(model['pins'], dict) or not model['pins']:
        raise ValueError('model context requires actual closure pins')
    source = payload['source_context']
    if test_only is q.TEST_ONLY_MECHANICS and 'metadata' not in source:
        _object(source, 'TEST_ONLY legacy source context',
            {'url', 'version', 'family', 'excerpts', 'publication_date', 'as_of',
             'original_sources', 'original_source_manifest_digest'}, {'event_date'})
        if not source['family'].startswith('TEST_ONLY'):
            raise ValueError('legacy source mechanics require protected TEST_ONLY purpose')
    else:
        _object(source, 'candidate source context',
            {'url', 'version', 'family', 'as_of', 'visible_excerpt_ids', 'metadata'}, {'event_date'})
        sm.validate_public_projection(source['metadata'])
        public = source['metadata']
        if (any(source[key] != public['source'][key] for key in ('url', 'version', 'family'))
                or payload['source'] != public['source']['display_source']
                or payload['statement'] != public['statement']['text']
                or source['visible_excerpt_ids'] != [item['id'] for item in public['visible_excerpts']]):
            raise ValueError('candidate public metadata/source/statement differs')
    _date(source['as_of'], 'source context as_of')
    if 'event_date' in source:
        _date(source['event_date'], 'source context event_date')
    result = {'candidate_universe_digest': q.digest(choices), 'model_pins': model['pins'],
            'model_as_of': model['as_of'],
            'input_construction_sha256': sm.construction_identity(Path(__file__))}
    return result


@dataclass(frozen=True)
class ResolvedSignalInput:
    """Immutable retained bytes; every public projection is a fresh object."""
    description: bytes
    _metadata_store: sm.MetadataStore | None = field(default=None, repr=False, compare=False)
    _metadata_policy: bytes | None = field(default=None, repr=False, compare=False)
    _test_only: q.TestOnlyPurpose | None = field(default=None, repr=False, compare=False)

    @property
    def payload(self) -> dict[str, Any]:
        return self.host_record['input']

    @property
    def host_record(self) -> dict[str, Any]:
        return json.loads(self.description)

    def host_inputs(self) -> q.HostInputs:
        record = self.host_record
        return q.HostInputs.freeze((record,), (record['issuer'],), metadata_store=self._metadata_store,
            metadata_policy=json.loads(self._metadata_policy) if self._metadata_policy else None,
            test_only=self._test_only)


def _resolve_test_only_legacy(repo: ModelRepo, org: str, source_packet: bytes, source_pin: str,
                         party_bytes: bytes, party_pin: str,
                         policy: dict[str, Any]) -> ResolvedSignalInput:
    """Resolve all declared candidates and separately pin original source/model context."""
    if hashlib.sha256(source_packet).hexdigest() != source_pin:
        raise ValueError('source packet pin does not match protected bytes')
    if hashlib.sha256(party_bytes).hexdigest() != party_pin:
        raise ValueError('party pin does not match protected bytes')
    packet = _object(json.loads(source_packet, object_pairs_hook=_unique), 'packet',
                     {'statement', 'source', 'source_context', 'signal'})
    _text(packet['statement'], 'statement')
    _text(packet['source'], 'source')
    _object(policy, 'protected policy', {'issuer', 'domain', 'capability', 'frame', 'model_as_of', 'model_pins'})
    for field in ('issuer', 'domain', 'capability', 'frame'):
        _text(policy[field], 'protected policy ' + field)
    _date(policy['model_as_of'], 'model_as_of')
    original_context = _object(packet['source_context'], 'source context',
        {'url', 'version', 'family', 'excerpts', 'publication_date', 'as_of', 'original_sources'}, {'event_date'})
    for field in ('url', 'version', 'family'):
        _text(original_context.get(field), field)
    for field in ('publication_date', 'as_of'):
        _date(original_context.get(field), field)
    if 'event_date' in original_context:
        _date(original_context['event_date'], 'event_date')
    signal = _object(packet['signal'], 'signal', {'id', 'date', 'from', 'provenance'})
    _text(signal['id'], 'signal id')
    if not isinstance(signal['from'], dict) or not signal['from']:
        raise ValueError('signal from must preserve its declared host pin mapping')
    if signal['date'] != original_context['as_of']:
        raise ValueError('signal date differs from declared task date')
    provenance = signal['provenance']
    if (not isinstance(provenance, dict) or provenance.get('url') != original_context['url']
            or provenance.get('date', signal['date']) != signal['date']):
        raise ValueError('signal provenance URL/date differs from source context')
    originals = _original_sources(original_context)
    party = load_yaml(party_bytes.decode('utf-8'))
    if not isinstance(party, dict) or party.get('id') != org:
        raise ValueError('party declaration belongs to a different organisation')
    current = ModelRepo.open(repo.model_root, ref=repo.pin.commit)
    if current.pin != repo.pin:
        raise ValueError('actual model source pin differs from supplied repository')
    overlay = Overlay.load(current, org, pricing_threshold=evidence.declared_threshold(party))
    pins = {'model_repo': current.pin.as_dict(), 'overlay': overlay.ref.as_dict(),
            'world': overlay.world.ref.as_dict()}
    if policy.get('model_pins') != pins:
        raise ValueError('actual model closure differs from protected model pins')
    definitions = {**overlay.world.components, **overlay.components}
    candidates = [{**item, 'definition': definitions[item['id']]} for item in candidates_of(overlay)]
    manifest_digest = q.digest(originals)
    source_context = {**original_context, 'original_sources': {
        key: {field: value[field] for field in ('identity', 'version', 'bytes', 'sha256')}
        for key, value in originals.items()}, 'original_source_manifest_digest': manifest_digest}
    model_context = {key: policy[key] for key in ('domain', 'capability', 'frame')}
    model_context.update({'organisation': org, 'as_of': policy['model_as_of'], 'pins': pins})
    payload = {'statement': packet['statement'], 'source': packet['source'],
               'source_context': source_context, 'model_context': model_context, 'candidates': candidates}
    canonical_source = source_record(q.canonical(payload), original_context['family'], original_context['version'])
    context = {key: policy[key] for key in ('domain', 'capability', 'frame')}
    context.update({'organisation': org, 'as_of': original_context['as_of'],
        'source': original_context['family'], 'source_sha256': canonical_source['sha256'],
        'eligible_components': [item['id'] for item in candidates],
        'candidate_universe_digest': q.digest(candidates), 'model_pins': pins,
        'model_as_of': policy['model_as_of'], 'original_source_manifest_digest': manifest_digest,
        'original_sources': originals, 'source_packet_sha256': source_pin,
        'party_sha256': party_pin, 'signal': packet['signal']})
    context.update(binding_context(payload, test_only=q.TEST_ONLY_MECHANICS))
    return ResolvedSignalInput(q.canonical({'subject': packet['signal']['id'], 'input': payload,
        'source': canonical_source, 'context': context, 'issuer': policy['issuer']}),
        _test_only=q.TEST_ONLY_MECHANICS)


def resolve_signal_input(repo: ModelRepo, org: str, source_packet: bytes, source_pin: str,
                         party_bytes: bytes, party_pin: str, policy: dict[str, Any], *,
                         metadata_store: sm.MetadataStore | None = None,
                         test_only: q.TestOnlyPurpose | None = None) -> ResolvedSignalInput:
    """Resolve v2 solely against the actual independently selected protected acquisition.

    The explicit parent TEST_ONLY token keeps old toy mechanics reproducible, never an
    operational fallback. A packet cannot enable it, select an authority or supply a receipt.
    """
    if test_only is q.TEST_ONLY_MECHANICS:
        if metadata_store is not None or not all(str(policy.get(key, '')).startswith('TEST_ONLY')
                for key in ('issuer', 'domain', 'capability', 'frame')):
            raise ValueError('legacy constructor requires protected TEST_ONLY purpose')
        return _resolve_test_only_legacy(repo, org, source_packet, source_pin, party_bytes, party_pin, policy)
    if test_only is not None:
        raise ValueError('invalid protected TEST_ONLY purpose')
    if not isinstance(metadata_store, sm.MetadataStore):
        raise ValueError('actual protected source metadata store required')
    if hashlib.sha256(source_packet).hexdigest() != source_pin or hashlib.sha256(party_bytes).hexdigest() != party_pin:
        raise ValueError('source packet or party pin differs from protected bytes')
    packet = _object(json.loads(source_packet, object_pairs_hook=_unique), 'v2 packet',
        {'schema', 'statement', 'source', 'source_context', 'signal'})
    if packet['schema'] != 'twin.source-packet/v2':
        raise ValueError('protected source packet schema v2 required')
    _object(policy, 'protected policy', {'issuer', 'domain', 'capability', 'frame', 'model_as_of', 'model_pins', 'source_metadata'})
    for key in ('issuer', 'domain', 'capability', 'frame'):
        _text(policy[key], 'protected policy ' + key)
    if metadata_store.purpose == 'TEST_ONLY' and not policy['issuer'].startswith('TEST_ONLY'):
        raise ValueError('TEST_ONLY metadata authority cannot enter actual protected signal import')
    _date(policy['model_as_of'], 'model_as_of')
    metadata_policy = sm.source_binding(policy['source_metadata'])
    acquired = metadata_store.resolve(**metadata_policy)
    public = acquired.public
    source = _object(packet['source_context'], 'v2 source context',
        {'url', 'version', 'family', 'as_of', 'visible_excerpt_ids', 'source_metadata_manifest_sha256'}, {'event_date'})
    if (any(source[key] != public['source'][key] for key in ('url', 'version', 'family'))
            or source['source_metadata_manifest_sha256'] != metadata_policy['expected_manifest_sha256']
            or packet['statement'] != public['statement']['text']
            or packet['source'] != public['source']['display_source']
            or source['visible_excerpt_ids'] != [item['id'] for item in public['visible_excerpts']]):
        raise ValueError('protected source metadata packet mapping differs')
    _date(source['as_of'], 'source task as_of')
    if 'event_date' in source:
        _date(source['event_date'], 'source event_date')
    signal = _object(packet['signal'], 'signal', {'id', 'date', 'from', 'provenance'})
    _text(signal['id'], 'signal id')
    if not isinstance(signal['from'], dict) or not signal['from']:
        raise ValueError('signal from must preserve its declared host pin mapping')
    if signal['date'] != source['as_of']:
        raise ValueError('signal date differs from exact task date')
    if (not isinstance(signal['provenance'], dict) or signal['provenance'].get('url') != source['url']
            or signal['provenance'].get('date', signal['date']) != signal['date']):
        raise ValueError('signal provenance URL/date differs')
    party = load_yaml(party_bytes.decode('utf-8'))
    if not isinstance(party, dict) or party.get('id') != org:
        raise ValueError('party declaration belongs to a different organisation')
    current = ModelRepo.open(repo.model_root, ref=repo.pin.commit)
    if current.pin != repo.pin:
        raise ValueError('actual model source pin differs')
    overlay = Overlay.load(current, org, pricing_threshold=evidence.declared_threshold(party))
    pins = {'model_repo': current.pin.as_dict(), 'overlay': overlay.ref.as_dict(), 'world': overlay.world.ref.as_dict()}
    if policy['model_pins'] != pins:
        raise ValueError('actual model closure differs from protected model pins')
    definitions = {**overlay.world.components, **overlay.components}
    candidates = [{**item, 'definition': definitions[item['id']]} for item in candidates_of(overlay)]
    source_context = {key: value for key, value in source.items() if key != 'source_metadata_manifest_sha256'}
    source_context['metadata'] = public
    model_context = {key: policy[key] for key in ('domain', 'capability', 'frame')}
    model_context.update(organisation=org, as_of=policy['model_as_of'], pins=pins)
    payload = {'statement': packet['statement'], 'source': packet['source'], 'source_context': source_context,
               'model_context': model_context, 'candidates': candidates}
    canonical_source = source_record(q.canonical(payload), source['family'], source['version'])
    context = {key: policy[key] for key in ('domain', 'capability', 'frame')}
    context.update(organisation=org, as_of=source['as_of'], source=source['family'],
        source_sha256=canonical_source['sha256'], eligible_components=[item['id'] for item in candidates],
        source_packet_sha256=source_pin, party_sha256=party_pin, signal=signal,
        source_metadata=policy['source_metadata'], source_metadata_public_sha256=q.digest(public))
    context.update(binding_context(payload))
    authority = metadata_store.authority(metadata_policy['expected_authority_digest'])
    parent_policy = {'authority_digest': authority.digest, 'purpose': json.loads(authority.description)['policy']['purpose']}
    return ResolvedSignalInput(q.canonical({'subject': signal['id'], 'input': payload, 'source': canonical_source,
        'context': context, 'issuer': policy['issuer']}), metadata_store, q.canonical(parent_policy))
