"""Protected independent review receipts, not a semantic oracle or quotation-based scorer.

Only a host-held store digest authenticates acquisition. Responses/claims cannot select this
store or mint an assessment. Public evidence contains no process authentication key.
"""
from __future__ import annotations

import hashlib
import base64
import hmac
import json
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_KEY = secrets.token_bytes(32)
DIMENSIONS = ('witness', 'steep', 'binding', 'applicability')


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True)
class BasisPolicy:
    description: bytes

    @classmethod
    def freeze(cls, rubric: dict[str, Any], issuers: tuple[str, ...]) -> BasisPolicy:
        if not rubric or not issuers or any(not isinstance(item, str) or not item for item in issuers):
            raise ValueError('review needs a frozen rubric and registered host acquisition issuers')
        return cls(_canonical({'schema': 'twin.basis-policy/v1', 'rubric': rubric,
            'issuers': issuers, 'source': _digest(Path(__file__).read_bytes())}))

    @classmethod
    def for_task(cls, task: str, metric: str, issuers: tuple[str, ...]) -> BasisPolicy:
        from .task_contracts import ASSETS, TaskContract
        contract = TaskContract.freeze(task)
        if metric not in contract.metrics or not issuers or any(not isinstance(item, str) or not item for item in issuers):
            raise ValueError('task review requires exact metric and protected acquisition issuers')
        rubric = json.loads((ASSETS / 'rubrics.json').read_bytes())
        return cls(_canonical({'schema': 'twin.basis-policy/v2', 'task': task, 'metric': metric,
            'contract': contract.digest, 'dimensions': rubric['metric_dimensions'][metric],
            'rubric': rubric, 'issuers': issuers, 'source': _digest(Path(__file__).read_bytes())}))

    @property
    def dimensions(self) -> tuple[str, ...]:
        value = json.loads(self.description)
        return tuple(value['dimensions']) if value['schema'] == 'twin.basis-policy/v2' else DIMENSIONS

    @property
    def digest(self) -> str:
        return _digest(self.description)

    def verify(self) -> None:
        value = json.loads(self.description)
        if value.get('schema') == 'twin.basis-policy/v2':
            if self.description != self.for_task(value['task'], value['metric'], tuple(value['issuers'])).description:
                raise ValueError('task assessment policy/rubric/source changed')
        elif (value.get('schema') != 'twin.basis-policy/v1'
                or value.get('source') != _digest(Path(__file__).read_bytes())):
            raise ValueError('semantic assessment policy/source changed')


@dataclass(frozen=True)
class BasisAssessment:
    packet: bytes
    authentication: bytes = field(repr=False)

    @property
    def digest(self) -> str:
        return _digest(self.packet)

    def verify(self, policy: BasisPolicy, request: bytes) -> None:
        policy.verify()
        if not hmac.compare_digest(self.authentication, hmac.digest(_KEY, self.packet, 'sha256')):
            raise ValueError('assessment was not acquired by the protected host')
        value, wanted = json.loads(self.packet), json.loads(request)
        record = value['record']
        task_review = json.loads(policy.description).get('schema') == 'twin.basis-policy/v2'
        if task_review:
            from .task_contracts import validate
            validate('AssessmentRecord', record)
        policy_key, request_key = ('policy_digest', 'request_digest') if task_review else ('policy', 'request')
        dimensions = policy.dimensions
        acquisition = value['acquisition']['entry']
        raw_record = base64.b64decode(value['raw_record'], validate=True)
        if (json.loads(raw_record) != record or _digest(raw_record) != acquisition['sha256']
                or acquisition.get('issuer') != record.get('issuer')
                or acquisition.get('request') != record.get(request_key)):
            raise ValueError('independent reviewer acquisition identity or record bytes changed')
        if (record.get(policy_key) != policy.digest or record.get(request_key) != _digest(request)
                or record.get('issuer') not in json.loads(policy.description)['issuers']):
            raise ValueError('assessment names a foreign policy, input/source/capture or issuer')
        rows = record.get('rows')
        if not isinstance(rows, list) or [row.get('id') for row in rows if isinstance(row, dict)] != [
                row['id'] for row in wanted['rows']]:
            raise ValueError('assessment must cover the complete ordered request')
        for row, original in zip(rows, wanted['rows']):
            if row.get('subject_digest') != _digest(_canonical(original)):
                raise ValueError('assessment raw/basis/source/context binding changed')
            if not isinstance(row.get('reason'), str) or not row['reason'].strip():
                raise ValueError('independent assessment needs its actual reasons')
            decisions = row.get('decisions')
            if (not isinstance(decisions, dict) or set(decisions) != set(dimensions)
                    or any(decision not in ('pass', 'fail', 'held', 'not-applicable')
                           for decision in decisions.values())):
                raise ValueError('assessment must state every semantic dimension')
            actual = original['output']
            declined = actual.get('answer') is None
            if not declined and 'not-applicable' in decisions.values():
                allowed = _later_ethics_dimensions(actual) if task_review and json.loads(policy.description)['task'] == 'ethics' else set()
                if any(decision == 'not-applicable' and dimension not in allowed for dimension, decision in decisions.items()):
                    raise ValueError('actual answers require actual semantic assessment')
            support = row.get('support')
            if not isinstance(support, dict) or set(support) != set(dimensions):
                raise ValueError('assessment needs reasons/witness locations for every dimension')
            for dimension in dimensions:
                detail = support[dimension]
                if (not isinstance(detail, dict) or not isinstance(detail.get('reason'), str)
                        or not detail['reason'].strip() or not isinstance(detail.get('witnesses'), list)
                        or decisions[dimension] == 'pass' and not detail['witnesses']):
                    raise ValueError('assessment conclusion lacks its actual reason/witness')
                for witness in detail['witnesses']:
                    value_witness = task_review and isinstance(witness, dict) and set(witness) == {'path', 'value'}
                    if not isinstance(witness, dict) or not value_witness and set(witness) != {'path', 'quote'}:
                        raise ValueError('review witness must identify its actual source location and quote/value')
                    path, quote = witness.get('path'), witness.get('quote')
                    if (not isinstance(path, list) or not path or path[0] not in ('input', 'context', 'sources')
                            or not value_witness and (not isinstance(quote, str) or not quote)):
                        raise ValueError('review witness must locate an actual original source/context')
                    cursor: Any = original
                    try:
                        for step in path:
                            if (not isinstance(step, str) and type(step) is not int
                                    or type(step) is int and step < 0):
                                raise ValueError('invalid witness path')
                            cursor = cursor[step]
                    except (KeyError, IndexError, TypeError) as exc:
                        raise ValueError('review witness source location is absent') from exc
                    if value_witness:
                        if _canonical(cursor) != _canonical(witness['value']):
                            raise ValueError('review witness value differs at its actual source location')
                    elif not isinstance(cursor, str) or not isinstance(quote, str) or quote not in cursor:
                        raise ValueError('review witness text is absent at its actual source location')

    def outcome(self, item_id: str) -> bool | None:
        row = next(row for row in json.loads(self.packet)['record']['rows'] if row['id'] == item_id)
        decisions = tuple(row['decisions'].values())
        if 'fail' in decisions:
            return False
        task_review = json.loads(self.packet)['record'].get('schema') == 'twin.task-basis-assessment/v2'
        return True if all(value == 'pass' or task_review and value == 'not-applicable' for value in decisions) and 'pass' in decisions else None


def _later_ethics_dimensions(actual: dict[str, Any]) -> set[str]:
    from .task_contracts import validate
    answer = actual['answer']
    validate('EthicsAnswer', answer)
    ladder = answer['ladder']
    names = ['purpose', 'necessity', 'proportionality']
    rungs, stop = ladder['rungs'], ladder['stopped_at']
    if (answer['admitted'] or stop not in names or len(rungs) != names.index(stop) + 1
            or [item['rung'] for item in rungs] != names[:len(rungs)]
            or any(not item['passed'] for item in rungs[:-1]) or rungs[-1]['passed']):
        raise ValueError('ethics N/A requires an actual verified stopping prefix')
    return set(names[names.index(stop) + 1:])


class ReviewStore:
    """Read only receipts independently acquired/pinned by the protected parent.

    A root-looking path or issuer is insufficient. `expected_digest` must be supplied by
    protected host configuration, acquired outside candidate/reviewer response data.
    """
    def __init__(self, path: Path, expected_digest: str):
        raw = path.read_bytes()
        if path.is_symlink() or _digest(raw) != expected_digest:
            raise ValueError('protected review acquisition store digest differs')
        value = json.loads(raw)
        if value.get('schema') != 'twin.semantic-review-store/v1' or not isinstance(value.get('entries'), list):
            raise ValueError('invalid protected review acquisition store')
        requests = [entry['request'] for entry in value['entries']]
        if len(set(requests)) != len(requests):
            raise ValueError('duplicate independent assessment acquisition')
        self._root, self._raw, self._entries = path.parent, raw, value['entries']

    def assess(self, policy: BasisPolicy, request: bytes) -> BasisAssessment:
        entry = next((entry for entry in self._entries if entry['request'] == _digest(request)), None)
        if entry is None:
            raise ValueError('no independently acquired semantic assessment for this actual output')
        if not entry.get('authority') or not entry.get('provenance'):
            raise ValueError('review acquisition lacks actual authority/provenance')
        path = self._root / entry['record']
        if path.is_symlink() or not path.resolve().is_relative_to(self._root.resolve()):
            raise ValueError('review record escapes protected acquisition store')
        raw = path.read_bytes()
        if _digest(raw) != entry['sha256']:
            raise ValueError('independent semantic review record changed')
        packet = _canonical({'record': json.loads(raw), 'raw_record': base64.b64encode(raw).decode(), 'acquisition': {
            'store_sha256': _digest(self._raw), 'entry': entry}})
        return _restore_assessment(packet, policy, request)


def _restore_assessment(packet: bytes, policy: BasisPolicy, request: bytes) -> BasisAssessment:
    """Only after protected store/catalogue bytes were independently verified by host code."""
    result = BasisAssessment(packet, hmac.digest(_KEY, packet, 'sha256'))
    result.verify(policy, request)
    return result
