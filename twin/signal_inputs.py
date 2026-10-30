"""One protected source/model projection for qualification and live signal input.

Pins and policy are supplied independently by the protected parent, never read from a child
response. The repository is already staged by the existing emitter. This module neither stages
repositories nor authenticates a publisher or a feed relationship from its display name.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from . import evidence, qualification as q
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


@dataclass(frozen=True)
class ResolvedSignalInput:
    """Immutable retained bytes; every public projection is a fresh object."""
    description: bytes

    @property
    def payload(self) -> dict[str, Any]:
        return self.host_record['input']

    @property
    def host_record(self) -> dict[str, Any]:
        return json.loads(self.description)

    def host_inputs(self) -> q.HostInputs:
        record = self.host_record
        return q.HostInputs.freeze((record,), (record['issuer'],))


def resolve_signal_input(repo: ModelRepo, org: str, source_packet: bytes, source_pin: str,
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
    context['input_construction_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return ResolvedSignalInput(q.canonical({'subject': packet['signal']['id'], 'input': payload,
        'source': canonical_source, 'context': context, 'issuer': policy['issuer']}))
