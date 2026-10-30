"""Conserve a reference and its admission decision before exposing task input.

This module checks custody and the declared claim, not the truth of an annotation. Source
agreement, an agent-authored coordinate and empirical human calibration remain distinct.
No decision here grants permission or admits a qualification population. Callers pass the
ordinary evaluator item to skills.evaluate with its existing scorer and independent checker.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date
from typing import Any


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def source_record(content: bytes, identity: str, version: str) -> dict[str, Any]:
    """Freeze already acquired bytes; identity/version describe what was captured, not fetched."""
    return {'identity': identity, 'version': version, 'sha256': hashlib.sha256(content).hexdigest(),
            'bytes': len(content), 'content_base64': base64.b64encode(content).decode('ascii')}


def binding_for(case: dict[str, Any]) -> dict[str, str]:
    """Custodian's binding for a separately supplied basis, computed before predictions."""
    return {key: _digest(case.get(key)) for key in ('input', 'expected', 'context', 'basis')}


@dataclass(frozen=True)
class Admission:
    """An immutable packet includes selected and held inputs, never only successful selections."""
    packet_bytes: bytes
    reasons: tuple[str, ...]

    @property
    def admitted(self) -> bool:
        return not self.reasons

    @property
    def packet_digest(self) -> str:
        return hashlib.sha256(self.packet_bytes).hexdigest()

    def input_projection(self) -> Any:
        return self.evaluator_item()['input']

    def evaluator_item(self) -> dict[str, Any]:
        if not self.admitted:
            raise ValueError('reference held: ' + '; '.join(self.reasons))
        case = json.loads(self.packet_bytes)['case']
        return {key: case[key] for key in ('id', 'input', 'expected', 'basis')}


def admit_reference(case: dict[str, Any], scope: dict[str, Any]) -> Admission:
    """Return a retained admission/hold decision; qualification needs separate population custody.

    The request is host/custodian supplied. Never obtain scope, rights or support from a
    candidate's response. Returned projections are fresh copies, so candidate mutation cannot
    change the conserved packet. Source rights and label provenance are separate declarations.
    """
    reasons: list[str] = []
    for field in ('expected', 'sources', 'rights', 'basis', 'field_support', 'selection', 'exposure'):
        if field in case and not isinstance(case[field], dict):
            reasons.append('invalid-shape:' + field)
    for field in ('sources', 'field_support'):
        if isinstance(case.get(field), dict) and any(not isinstance(v, dict) for v in case[field].values()):
            reasons.append('invalid-shape:' + field)
    if reasons:
        return _decision(case, scope, reasons)
    reasons.extend(_support_shape_reasons(case.get('field_support', {})))
    if reasons:
        return _decision(case, scope, reasons)
    if 'input' not in case or case['input'] is None:
        reasons.append('missing-input')
    if case.get('context') != scope:
        reasons.append('scope-context-conflict')
    if scope.get('purpose') != 'development':
        reasons.append('qualification-requires-separately-admitted-population')
    for field in ('purpose', 'claim', 'metric', 'domain', 'capability', 'organisation', 'as_of', 'frame'):
        if not isinstance(scope.get(field), str) or not scope[field].strip():
            reasons.append('missing-context:' + field)
    try:
        date.fromisoformat(scope.get('as_of', ''))
    except (ValueError, TypeError):
        reasons.append('invalid-context-date')
    for field in ('id', 'group', 'exposure', 'selection', 'reference_kind', 'limitations'):
        if not case.get(field):
            reasons.append('missing-' + field)
    if case.get('selection', {}).get('decision') != 'selected':
        reasons.append('selection-held')
    if not case.get('exposure', {}).get('status') or not case.get('exposure', {}).get('history'):
        reasons.append('missing-exposure-history')
    if not case.get('selection', {}).get('reason'):
        reasons.append('missing-selection-reason')
    targets = {'signal-classify': ('steep', 'component'),
               'evolution-judge': ('evolution_position',),
               'causal-claims': ('sign', 'lag_days', 'elasticity_mode', 'evidence_grade'),
               'causal-claims-grade-accuracy': ('evidence_grade',),
               'gameplay-lens': ('opportunities',),
               'substrate-generator': ('channels', 'planted_signals', 'min_mundane_fraction'),
               'ethics-gate': ('admitted', 'stopped_at')}
    metric = str(scope.get('metric', ''))
    if metric not in targets:
        reasons.append('unsupported-metric')
    expected = case.get('expected', {})
    for field in targets.get(metric, ()):
        if field not in expected or (expected[field] is None and field != 'stopped_at'):
            reasons.append('missing-target:' + field)
    sources = case.get('sources', {})
    for name, source in sources.items():
        try:
            raw = base64.b64decode(source['content_base64'], validate=True)
            valid = (hashlib.sha256(raw).hexdigest() == source['sha256']
                     and len(raw) == source['bytes'] and source.get('identity') and source.get('version'))
        except (KeyError, TypeError, ValueError):
            valid = False
        if not valid:
            reasons.append('source-integrity:' + name)
    rights = case.get('rights', {})
    if not rights.get('statement') or not rights.get('evidence'):
        reasons.append('missing-rights')
    elif any(name not in sources for name in rights['evidence']):
        reasons.append('unbound-rights')
    if scope.get('purpose') not in rights.get('uses', []):
        reasons.append('rights-scope-conflict')
    for field in targets.get(metric, ()):
        support = case.get('field_support', {}).get(field, {})
        if (not support.get('meaning') or not support.get('sources')
                or any(name not in sources for name in support.get('sources', []))):
            reasons.append('unsupported-target:' + field)
    if expected.get('opportunities') == [] and not case.get('field_support', {}).get('opportunities', {}).get('complete_negative_basis'):
        reasons.append('unsupported-negative-set')
    if case.get('basis_binding') != binding_for(case):
        reasons.append('stale-basis-binding')
    basis = case.get('basis', {})
    hashes = basis.get('source_hashes', {})
    used = {name for support in case.get('field_support', {}).values() for name in support.get('sources', [])}
    if not basis or not used:
        reasons.append('missing-separate-basis')
    for name in sorted(used):
        if name not in rights.get('covered_sources', []):
            reasons.append('rights-do-not-cover-source:' + name)
        if name not in sources or hashes.get(name) != sources[name].get('sha256'):
            reasons.append('stale-source-basis:' + name)
    validators = {
        'evolution_position': _fraction, 'elasticity_mode': _fraction,
        'min_mundane_fraction': _fraction,
        'steep': lambda x: x in ('social', 'technological', 'economic', 'environmental', 'political'),
        'component': lambda x: isinstance(x, str) and bool(x.strip()),
        'sign': lambda x: x in ('positive', 'negative'),
        'lag_days': lambda x: type(x) is int and x >= 0,
        'evidence_grade': lambda x: type(x) is int and 1 <= x <= 5,
        'admitted': lambda x: type(x) is bool,
        'stopped_at': lambda x: x is None or isinstance(x, str) and bool(x.strip()),
        'opportunities': lambda x: isinstance(x, list) and all(isinstance(row, (list, tuple)) and len(row) == 2 and all(isinstance(v, str) and v for v in row) for row in x),
        'channels': lambda x: isinstance(x, list) and bool(x) and all(isinstance(v, str) and v for v in x),
        'planted_signals': lambda x: isinstance(x, list) and all(isinstance(v, str) and v for v in x),
    }
    for field in targets.get(metric, ()):
        if field in expected and expected[field] is not None and not validators[field](expected[field]):
            reasons.append('invalid-target:' + field)
    claims = {'published-reference-agreement': 'published-coordinate',
              'agent-reference-agreement': 'agent-authored',
              'complete-causal-reference': 'causal-reference',
              'task-conformance': 'declared-constraints'}
    if claims.get(scope.get('claim', '')) != case.get('reference_kind'):
        reasons.append('reference-claim-conflict')
    if _contains_reference_fields(case.get('input')):
        reasons.append('reference-fields-in-input')
    for field, support in case.get('field_support', {}).items():
        if set(support.get('sources', [])) != {w.get('source') for w in support.get('witnesses', [])}:
            reasons.append('unbound-support-witness:' + field)
        if not support.get('witnesses'):
            reasons.append('missing-support-witness:' + field)
        for witness in support.get('witnesses', []):
            try:
                raw = base64.b64decode(sources[witness['source']]['content_base64'], validate=True)
                start, end = witness['start'], witness['end']
                valid = (type(start) is int and type(end) is int and 0 <= start < end <= len(raw)
                         and hashlib.sha256(raw[start:end]).hexdigest() == witness['sha256'])
            except (KeyError, TypeError, ValueError):
                valid = False
            if not valid:
                reasons.append('invalid-support-witness:' + field)
    return _decision(case, scope, reasons)


def _support_shape_reasons(supports: dict[str, dict[str, Any]]) -> list[str]:
    """Parse nested collections before source lookup, set comparison or byte slicing.

    Originals stay untouched in the packet. Missing/empty support is diagnosed by admission;
    malformed declarations are held here instead of being treated as an empty declaration.
    """
    reasons: list[str] = []
    for field, support in supports.items():
        sources = support.get('sources', [])
        if not isinstance(sources, list) or any(not isinstance(name, str) for name in sources):
            reasons.append('invalid-shape:field-support-sources:' + field)
        witnesses = support.get('witnesses', [])
        if not isinstance(witnesses, list):
            reasons.append('invalid-shape:field-support-witnesses:' + field)
            continue
        for witness in witnesses:
            if (not isinstance(witness, dict)
                    or not isinstance(witness.get('source'), str)
                    or type(witness.get('start')) is not int
                    or type(witness.get('end')) is not int
                    or not isinstance(witness.get('sha256'), str)):
                reasons.append('invalid-shape:field-support-witnesses:' + field)
                break
    return reasons


def _decision(case: dict[str, Any], scope: dict[str, Any], reasons: list[str]) -> Admission:
    packet = {'schema': 'twin.reference-case/v1', 'case': case, 'requested_scope': scope,
              'admitted': not reasons, 'reasons': reasons}
    return Admission(_canonical(packet), tuple(reasons))


def _fraction(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def _contains_reference_fields(value: Any) -> bool:
    if isinstance(value, dict):
        return bool({'expected', 'basis', 'field_support', 'reference_kind'} & value.keys()) or any(
            _contains_reference_fields(v) for v in value.values())
    return isinstance(value, list) and any(_contains_reference_fields(v) for v in value)
