"""Protected remaining-task parents. Pure document projection never grants permission.

The qualification host owns acquisition, actual output, review, receipts and their validation.
No actor, job, reviewer, backend or acquisition is registered by this module.
"""
from __future__ import annotations

import base64
import re
from typing import Any

from . import qualification as q
from .task_contracts import TaskContract, decode, validate


SCHEMAS = {'causal': 'twin.causal-proposal/v1', 'gameplay': 'twin.gameplay-proposal/v1',
           'ethics': 'twin.ethics-judgement/v1'}
ATTEMPT_FIELDS = ('attempt_id', 'subject', 'input_sha256', 'target_sha256', 'actor_sha256',
                  'capture_sha256', 'raw_available', 'disposition', 'reason')


def _job(job: dict[str, Any]) -> TaskContract:
    if (not isinstance(job, dict) or set(job) != {
            'task', 'task_contract_sha256', 'model_version', 'organisation', 'subjects'}
            or not isinstance(job['model_version'], str)
            or not re.fullmatch(r'actor-[0-9a-f]{64}', job['model_version'])
            or not isinstance(job['organisation'], str) or not job['organisation']
            or not isinstance(job['subjects'], list) or not job['subjects']
            or any(not isinstance(subject, str) or not subject for subject in job['subjects'])
            or len(set(job['subjects'])) != len(job['subjects'])):
        raise ValueError('exact protected task execution job required')
    contract = TaskContract.freeze(job['task'])
    if job['task_contract_sha256'] != contract.digest:
        raise ValueError('protected job names a different task contract')
    return contract


def _pins(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError('all original source pins are required')
    seen = set()
    for pin in value:
        if (not isinstance(pin, dict) or set(pin) != {'identity', 'version', 'sha256'}
                or any(not isinstance(pin[key], str) or not pin[key] for key in ('identity', 'version'))
                or not isinstance(pin['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', pin['sha256'])):
            raise ValueError('exact original source pin required')
        encoded = q.canonical(pin)
        if encoded in seen:
            raise ValueError('duplicate original source pin')
        seen.add(encoded)
    return value


def _attempt_rows(job: dict[str, Any], snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for attempt in snapshot['attempts']:
        row = {key: attempt[key] for key in ATTEMPT_FIELDS}
        validate('Attempt', row)
        rows.append(row)
    if ([row['subject'] for row in rows] != job['subjects']
            or len({row['attempt_id'] for row in rows}) != len(rows)):
        raise ValueError('task snapshot omits, reorders or duplicates logical attempts')
    return rows


def document_from_snapshot(job: dict[str, Any], snapshot: dict[str, Any], *, role: str,
                           clock: str) -> dict[str, Any] | None:
    """Losslessly project observed host state; host receipt validation is separately required."""
    contract = _job(job)
    try:
        if (snapshot['schema'] != 'twin.task-session-snapshot/v1' or not isinstance(snapshot['identity'], str)
                or not snapshot['identity'] or q.canonical(snapshot['job']) != q.canonical(job)):
            raise ValueError('original task session snapshot required')
        attempts = _attempt_rows(job, snapshot)
        accepted = [attempt for attempt in snapshot['attempts'] if attempt['status'] == 'accepted']
        if not accepted:
            return None
        pins = _pins(snapshot['source_pins'])
        run = {'task_contract_sha256': contract.digest, 'model_version': job['model_version'],
            'host_session': snapshot['identity'], 'clock': q.mp.derive_clock(clock)[0],
            'operator_role': role, 'headless': True, 'declined': snapshot['declines'], 'attempts': attempts,
            'action_authority': False, 'merge_authority': False, 'override_authority': False, 'price_eligible': False}
        judgements, receipts = [], set()
        for attempt in accepted:
            output = attempt['output']
            if (attempt['task'] != contract.task or attempt['metrics'] != list(contract.metrics)
                    or not isinstance(attempt['receipt'], str) or not attempt['receipt']
                    or attempt['receipt'] in receipts or output is None or output.get('failure')
                    or attempt['context']['organisation'] != job['organisation']
                    or output['actor_digest'] != job['model_version'][6:]
                    or output['input_digest'] != attempt['input_sha256']
                    or q.digest(attempt['target']) != attempt['target_sha256']
                    or q.digest(output) != attempt['capture_sha256']
                    or attempt['assessment_outcomes'] != {metric: 'pass' for metric in contract.metrics}):
                raise ValueError('accepted task snapshot differs from complete protected capture')
            if not isinstance(output['raw'], str) or output['raw_available'] is not True:
                raise ValueError('accepted task output lacks original raw capture')
            base64.b64decode(output['raw'], validate=True)
            receipts.add(attempt['receipt'])
            _pins(attempt['source_pins'])
            validate(contract.task.title() + 'Answer', output['answer'])
            validate('GameplayBasis' if contract.task == 'gameplay' else 'Basis', output['basis'])
            judgements.append({'subject': attempt['subject'], 'attempt_id': attempt['attempt_id'],
                'host_receipt': attempt['receipt'], 'target': attempt['target'], 'answer': output['answer'],
                'basis': output['basis'], 'actual_output_sha256': attempt['capture_sha256'],
                'mandatory_gate': attempt['mandatory_gate']})
        if contract.task != 'evolution':
            document = {'schema': SCHEMAS[contract.task], 'org': job['organisation'],
                'source_pins': pins, 'run': run, 'judgements': judgements}
            validate('ProposalDocument', document)
        else:
            claims = []
            for attempt, judgement in zip(accepted, judgements):
                validate('TargetComponent', judgement['target'])
                if judgement['mandatory_gate'] is not None:
                    raise ValueError('position judgement cannot carry an ethics gate')
                claims.append({'id': attempt['subject'] + '-position-' + attempt['attempt_id'],
                    'kind': 'position', 'component': judgement['target']['component'],
                    'evolution_position': judgement['answer']['evolution_position'], 'evidence_grade': 5,
                    'claimed_by': 'evolution-judge candidate (skill)', 'price_eligible': False,
                    'evidence': q.canonical(judgement['basis']).decode('utf-8'),
                    'host_subject': attempt['subject'], 'host_receipt': attempt['receipt'],
                    'source_pins': attempt['source_pins']})
            document = {'schema': 'twin.headline-claim/v1', 'org': job['organisation'], 'source_pins': pins,
                'derived_from': [], 'claims': claims, 'run': {**run, 'skill': 'classify-and-judge'}}
        return decode(q.canonical(document))
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('incomplete protected task snapshot') from exc
