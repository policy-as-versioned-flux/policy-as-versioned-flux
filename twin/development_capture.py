"""Import the sole retained Mac smoke as an exposed, unqualified development trace.

This module never imports a model runtime, acquires assets or runs inference. Its replay actor
is identified separately from the historical generator and can return only the pinned capture
for the exact original input. Proposed reference authority and original observer limits survive.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from . import qualification as q
from .reference_cases import admit_reference, binding_for, source_record
from .skills import Stated


def parse_smoke_signal(raw: bytes, config: dict[str, Any]) -> Stated:
    """Strip the known terminal token and shape fields; never invent semantic support."""
    text = raw.decode()
    if text.endswith('<|im_end|>'):
        text = text[:-len('<|im_end|>')]
    value = json.loads(text)
    if (not isinstance(value, dict) or set(value) != {'steep', 'component', 'basis'}
            or any(not isinstance(item, str) or not item for item in value.values())):
        raise ValueError('actual signal output must state steep, component and its original basis')
    return Stated({'steep': value['steep'], 'claim': {'component': value['component']}}, value['basis'])


def replay_raw(payload: Any, config: dict[str, Any]) -> bytes:
    if q.digest(payload) != config['original_input_digest']:
        raise ValueError('historical replay has no capture for another input')
    return base64.b64decode(config['raw_output_base64'], validate=True)


def unattested_basis(actual: Any, reference: Any) -> bool:
    """No independent semantic basis judgement is asserted for this development trace."""
    return False


def import_smoke(evidence: Path, manifest_pin: str, corpus_path: Path,
                 producer_script: Path) -> tuple[q.Selection, q.Capture]:
    """The host supplies its held receipt pin, not a checksum offered by model output."""
    manifest_bytes = (evidence / 'EVIDENCE-MANIFEST.json').read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != manifest_pin:
        raise ValueError('host-held smoke manifest pin differs')
    manifest = json.loads(manifest_bytes)
    for entry in manifest['files']:
        path = evidence / entry['path']
        if path.is_symlink() or not path.resolve().is_relative_to(evidence.resolve()):
            raise ValueError('smoke evidence escapes its host snapshot')
        raw = path.read_bytes()
        if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('smoke evidence changed: ' + entry['path'])
    def read(name: str) -> Any:
        if name not in {item['path'] for item in manifest['files']}:
            raise ValueError('missing pinned smoke receipt: ' + name)
        return json.loads((evidence / name).read_bytes())
    actor = read('smoke-run-1/actor.json')
    provenance = read('input-provenance.json')
    weights = read('model-manifest.json')
    observer = read('observer-bindings.json')
    for name, field in (('development-input.json', 'input_sha256'),
                        ('model-manifest.json', 'manifest_sha256'),
                        ('smoke-run-1/raw-output.txt', 'raw_output_sha256'),
                        ('smoke-run-1/prompt.txt', 'prompt_sha256'),
                        ('smoke-run-1/rendered-chat.txt', 'rendered_chat_sha256')):
        if name not in {item['path'] for item in manifest['files']}:
            raise ValueError('missing original actor-bound file: ' + name)
        if hashlib.sha256((evidence / name).read_bytes()).hexdigest() != actor[field]:
            raise ValueError('historical actor/file binding differs: ' + name)
    if hashlib.sha256(producer_script.read_bytes()).hexdigest() != actor['script_sha256']:
        raise ValueError('historical producer source changed; no reinterpretation of its run')
    if (actor['model'] != weights['model_id'] or actor['revision'] != weights['revision']
            or actor['purpose'] != 'development feasibility only; no qualification or permission'):
        raise ValueError('historical generator identity or purpose differs')
    original_corpus = corpus_path.read_bytes()
    if hashlib.sha256(original_corpus).hexdigest() != provenance['source_sha256']:
        raise ValueError('original proposed-reference corpus changed')
    original = next(row for row in json.loads(original_corpus) if row['id'] == provenance['case_id'])
    payload = json.loads((evidence / 'development-input.json').read_bytes())
    if payload != original['input'] or original['split'] != 'development' or provenance['split'] != 'development':
        raise ValueError('historical input or development exposure differs')
    scope = {'purpose': 'development', 'claim': 'agent-reference-agreement', 'metric': 'signal-classify',
             'domain': 'CI definition management', 'capability': 'Project build definition management',
             'organisation': 'GitLab', 'as_of': original['provenance']['target_context_date'],
             'frame': 'Publisher-attributed retrospective announcement; not original-time ingestion'}
    case = {'id': original['id'], 'input': original['input'], 'expected': original['expected'],
            'basis': original['basis'], 'original_reference': original,
            'context': scope, 'reference_kind': 'agent-authored', 'group': original['group_id'],
            'sources': {'original-proposed-corpus': source_record(original_corpus,
                provenance['source_path'], provenance['source_sha256'])},
            'field_support': {},
            'rights': {'statement': 'No independent source-rights admission asserted by this trace',
                       'evidence': [], 'uses': ['development'], 'covered_sources': []},
            'selection': {'decision': 'held', 'reason': 'Original unreviewed agent proposal; preserve its authority'},
            'exposure': {'status': 'development', 'history': [provenance['old_packet_exposure'],
                                                           provenance['new_exposure']]},
            'limitations': ['Unreviewed agent-authored development reference; no empirical calibration',
                            'No independent semantic checking of the actual free-text basis',
                            'Retrospective source/date/frame only; no original-byte ingestion proof']}
    case['basis_binding'] = binding_for(case)
    held = admit_reference(case, scope)
    if held.admitted:
        raise ValueError('a held development proposal unexpectedly became an admitted reference')
    envelope = {'adopters': ['GitLab'], 'domains': [scope['domain']], 'capabilities': [scope['capability']],
                'frames': [scope['frame']], 'sources': [provenance['source_path']],
                'from': scope['as_of'], 'until': scope['as_of']}
    population = q.Population.held_development_trace('signal-classify', (held,), envelope,
        {'status': 'development', 'history': [provenance['old_packet_exposure'], provenance['new_exposure']],
         'training_provenance': 'unknown; original smoke never claimed clean pretraining'})
    replay = q.Actor.freeze(replay_raw, parse_smoke_signal, {
        'purpose': 'historical development capture replay; no inference or permission',
        'capture_replay': True,
        'original_input_digest': q.digest(payload), 'raw_output_base64': base64.b64encode(
            (evidence / 'smoke-run-1/raw-output.txt').read_bytes()).decode(),
        'historical_generator': actor, 'host_manifest_sha256': manifest_pin,
        'original_observer_bindings': observer}, support=(producer_script,))
    selected = q.Selection.freeze(replay, population, unattested_basis)
    return selected, selected.capture()


def demonstrate(evidence: Path, manifest_pin: str, corpus: Path, producer: Path, output: Path,
                recorded_at: str) -> dict[str, Any]:
    selected, captured = import_smoke(evidence, manifest_pin, corpus, producer)
    output.mkdir(parents=True, exist_ok=False)
    facts = selected.facts(captured)
    row = selected.record(captured, recorded_at, output / 'scores.jsonl')
    resolver = q.Resolver(((selected, captured),), output / 'scores.jsonl')
    permission = resolver.permission('signal-classify', selected.actor.model_version)
    if permission.granted or row['attributable_rate'] is not None:
        raise ValueError('held development replay unexpectedly qualified')
    (output / 'population.json').write_bytes(selected.population.description)
    (output / 'selection.json').write_bytes(selected.description)
    (output / 'actor.json').write_bytes(selected.actor.description)
    (output / 'capture.json').write_bytes(captured.packet)
    (output / 'bundle.json').write_bytes(selected.archive(captured))
    summary = {'schema': 'twin.historical-smoke-replay/v1', 'actual_new_inference': False,
        'historical_generator': json.loads(selected.actor.description)['config']['historical_generator'],
        'processing_actor': selected.actor.model_version, 'binding': selected.binding(captured),
        'reference_admission': facts['reference_admission'], 'reference_authority':
            'held unreviewed agent-authored development proposal; no qualification authority',
        'evaluation': facts['evaluation'].as_dict(), 'baseline': facts['baseline'].score,
        'variance': facts['variance'], 'permission_granted': permission.granted,
        'refusals': [{'item': condition.item, 'reason': condition.detail} for condition in permission.refusals],
        'original_observer_bindings': json.loads(selected.actor.description)['config']['original_observer_bindings']}
    (output / 'summary.json').write_bytes(q.canonical(summary))
    return summary
