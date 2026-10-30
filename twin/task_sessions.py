"""Protected remaining-task lifecycle shared by proposal/position parents.

This module owns counts and retained mechanical output, never sensing or action authority.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
import hmac
import json
import re
import secrets
from typing import Any

from . import qualification as q
from .task_contracts import TaskContract, METRIC_TASK, validate

ATTEMPT_FIELDS = ('attempt_id', 'subject', 'input_sha256', 'target_sha256', 'actor_sha256',
                  'capture_sha256', 'raw_available', 'disposition', 'reason')
_REFUSAL_KEY = secrets.token_bytes(32)


@dataclass(frozen=True)
class _ReviewRefusal:
    packet: bytes
    authentication: bytes

    @property
    def digest(self) -> str:
        return q.hashlib.sha256(self.packet).hexdigest()

    def verify(self) -> None:
        if not hmac.compare_digest(self.authentication, hmac.digest(_REFUSAL_KEY, self.packet, 'sha256')):
            raise ValueError('task review refusal requires original private transaction authentication')


def _refusal(resolver: q.Resolver, identity: str) -> _ReviewRefusal:
    result = resolver._task_refusal_receipts.get(identity)
    if not isinstance(result, _ReviewRefusal) or result.digest != identity:
        raise ValueError('no independently retained private task refusal receipt')
    result.verify()
    return result


def archive_refusals(session: q.HostSession) -> dict[str, Any]:
    return {attempt: {'digest': identity, 'record': json.loads(_refusal(session._resolver, identity).packet)}
            for attempt, identity in session._task_refusals.items()}


def restore_refusals(session: q.HostSession, records: dict[str, Any]) -> None:
    if not isinstance(records, dict):
        raise ValueError('protected task refusal receipt map required')
    for attempt, value in records.items():
        if not isinstance(value, dict) or set(value) != {'digest', 'record'}:
            raise ValueError('exact retained task refusal receipt required')
        receipt = _refusal(session._resolver, value['digest'])
        if receipt.packet != q.canonical(value['record']):
            raise ValueError('task refusal record differs from original private transaction')
        session._task_refusals[attempt] = receipt.digest
    # The original protected resolver also remembers consumed transactions that
    # a public archive tries to erase or relabel after permission returns.
    for identity, receipt in session._resolver._task_refusal_receipts.items():
        if not isinstance(receipt, _ReviewRefusal):
            raise ValueError('protected task refusal store contains no authenticated transaction')
        receipt.verify()
        bindings = json.loads(receipt.packet).get('bindings')
        if isinstance(bindings, dict) and bindings.get('session') == session.identity:
            original_attempt = bindings.get('attempt')
            if not isinstance(original_attempt, str) or session._task_refusals.get(original_attempt) != identity:
                raise ValueError('public task history cannot erase an original consumed refusal')


def _import_refusals_from_pinned_archive(archive: bytes, resolver: q.Resolver) -> None:
    """Only after Resolver verifies independently pinned catalogue AND session bytes.

    Public dictionaries cannot invoke this import through HostSession.restore. The
    host's protected catalogue pin supplies cross-process provenance, as for the
    existing capture and independent-assessment import paths. No key is exported.
    """
    records = json.loads(archive).get('task_refusals', {})
    if not isinstance(records, dict):
        raise ValueError('protected task refusal receipt map required')
    for value in records.values():
        if not isinstance(value, dict) or set(value) != {'digest', 'record'}:
            raise ValueError('exact protected task refusal receipt required')
        raw = q.canonical(value['record'])
        if q.hashlib.sha256(raw).hexdigest() != value['digest']:
            raise ValueError('protected task refusal receipt digest differs')
        resolver._task_refusal_receipts[value['digest']] = _ReviewRefusal(raw, hmac.digest(_REFUSAL_KEY, raw, 'sha256'))


def bind_job(session: q.HostSession, job: dict[str, Any]) -> None:
    if (not isinstance(job, dict) or set(job) != {'task', 'task_contract_sha256', 'model_version', 'organisation', 'subjects'}
            or not isinstance(job['organisation'], str) or not job['organisation']
            or not isinstance(job['model_version'], str) or not re.fullmatch(r'actor-[0-9a-f]{64}', job['model_version'])
            or not isinstance(job['subjects'], list) or not job['subjects']
            or any(not isinstance(subject, str) or not subject for subject in job['subjects'])
            or len(set(job['subjects'])) != len(job['subjects'])
            or not isinstance(job['task_contract_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', job['task_contract_sha256'])):
        raise ValueError('exact protected task parent job required')
    TaskContract.freeze(job['task']).verify()
    raw = q.canonical(job)
    if session._task_job is not None and session._task_job != raw:
        raise ValueError('protected task parent job cannot be rebound')
    session._task_job = raw


def _raw_rows(session: q.HostSession) -> list[dict[str, Any]]:
    return json.loads(session._inputs.description)['records']


def _pins(row: dict[str, Any]) -> list[dict[str, str]]:
    pins = {}
    sources = row.get('sources', {}) if isinstance(row, dict) else {}
    for record in sources.values() if isinstance(sources, dict) else ():
        if isinstance(record, dict) and all(isinstance(record.get(key), str) and record[key] for key in ('identity', 'version', 'sha256')):
            item = {key: record[key] for key in ('identity', 'version', 'sha256')}
            pins[q.digest(item)] = item
    return sorted(pins.values(), key=lambda item: (item['identity'], item['version'], item['sha256']))


def _input_binding(row: dict[str, Any], model_version: str) -> dict[str, Any]:
    payload, context = row.get('input'), row.get('context', {})
    target = context.get('target', payload.get('target') if isinstance(payload, dict) else None) if isinstance(context, dict) else None
    actor = model_version.removeprefix('actor-') if re.fullmatch(r'actor-[0-9a-f]{64}', model_version) else None
    return {'target': target, 'context': context or None, 'input_sha256': q.digest(payload), 'target_sha256': q.digest(target),
            'actor_sha256': actor, 'source_pins': _pins(row)}


def _attempt(session: q.HostSession, task: str, metrics: tuple[str, ...], model_version: str,
             subject: str) -> dict[str, Any]:
    row = next((row for row in _raw_rows(session) if isinstance(row, dict) and row.get('subject') == subject), {})
    result = {'attempt_id': secrets.token_hex(24), 'subject': subject, 'task': task, 'metrics': list(metrics),
        **_input_binding(row, model_version), 'capture_sha256': None, 'raw_sha256': None, 'raw_available': False,
        'disposition': 'refused-before-invocation', 'reason': 'human required; input not yet invoked',
        'status': 'declined', 'receipt': None, 'output': None, 'assessment_outcomes': {},
        'mandatory_gate': None}
    session._task_attempts.append(result)
    return result


def _finish(session: q.HostSession, attempt: dict[str, Any], disposition: str, reason: str,
            output: dict[str, Any] | None = None, receipt: str | None = None) -> None:
    attempt.update(disposition=disposition, reason=reason, receipt=receipt)
    attempt['status'] = {'refused-before-invocation': 'declined', 'pending-review': 'pending',
        'held-review': 'held', 'failed-review': 'failed'}.get(disposition, disposition)
    if output is not None:
        attempt.update(output=output, capture_sha256=q.digest(output), raw_available=output['raw_available'],
                       raw_sha256=q.hashlib.sha256(base64.b64decode(output['raw'], validate=True)).hexdigest())
    session._task_events.append({'attempt_id': attempt['attempt_id'], 'disposition': disposition,
                                'reason': reason, 'receipt': receipt})
    if disposition != 'accepted':
        session._declines.append({'subject': attempt['subject'], 'reason': reason})


def decline_run(session: q.HostSession, subjects: tuple[str, ...], reason: str) -> None:
    if session._task_job is None or not isinstance(reason, str) or not reason:
        raise ValueError('preflight refusal requires original protected task job and factual reason')
    job = json.loads(session._task_job)
    if list(subjects) != job['subjects']:
        raise ValueError('refused run must conserve the complete ordered parent job')
    for subject in subjects:
        attempt = _attempt(session, job['task'], TaskContract.freeze(job['task']).metrics, job['model_version'], subject)
        _finish(session, attempt, 'refused-before-invocation', reason)


def snapshot(session: q.HostSession) -> dict[str, Any]:
    # A failed preflight must remain saveable: these are retained host bytes, not a
    # fresh authority assertion or a second attempt to resolve invalid inputs.
    rows = _raw_rows(session)
    pending = [{'request_digest': key, 'request': record['task_review_request']}
        for key, raw in session._pending.items() if 'task_review_request' in (record := json.loads(raw))]
    pins = {q.digest(pin): pin for row in rows for pin in _pins(row)}
    return json.loads(q.canonical({'schema': 'twin.task-session-snapshot/v1', 'identity': session.identity,
        'job': json.loads(session._task_job) if session._task_job else None, 'inputs': rows,
        'attempts': session._task_attempts, 'events': session._task_events, 'declines': session.declines,
        'pending_reviews': pending, 'source_pins': sorted(pins.values(), key=lambda pin: (pin['identity'], pin['version'], pin['sha256']))}))


def _selections(session: q.HostSession, task: str, model_version: str) -> tuple[q.Selection, ...]:
    metrics = TaskContract.freeze(task).metrics
    selections = []
    for metric in metrics:
        binding = session._resolver._bindings.get((metric, model_version))
        if binding is None:
            raise ValueError('no protected registered task selection for ' + metric + '; human required')
        selected = binding[0]
        selected.verify()
        if (selected._task_contract is None or selected._task_contract.task != task
                or selected.actor.model_version != model_version):
            raise ValueError('selected actor/task contract does not match protected task')
        selections.append(selected)
    if len({item.actor.digest for item in selections}) != 1:
        raise ValueError('paired task requires the exact same actor')
    if task == 'causal':
        group = session._resolver._groups.get(model_version)
        if group is None or {item.digest for item in selections} != {item.digest for item in group.selections}:
            raise ValueError('causal live use requires original complete authenticated capture group')
        group.verify()
    return tuple(selections)


class _PermissionRefused(ValueError):
    def __init__(self, permissions: list[dict[str, Any]], reason: str):
        super().__init__(reason)
        self.permissions = permissions


def _permission_record(permission: Any, selected: q.Selection) -> dict[str, Any]:
    native = isinstance(permission, q.mp.Permission)
    if native and (permission.skill != selected.population.metric or permission.model_version != selected.actor.model_version):
        raise ValueError('current permission belongs to another task metric or actor')
    if not native and json.loads(selected.actor.description)['config'].get('purpose') != 'TEST_ONLY':
        raise ValueError('operational task permission requires actual host permission facts')
    return {'metric': selected.population.metric, 'model_version': selected.actor.model_version,
        'kind': 'native' if native else 'TEST_ONLY-precondition', 'granted': bool(permission.granted),
        'conditions': [{'item': item.item, 'name': item.name, 'passed': item.passed, 'detail': item.detail}
                       for item in permission.conditions] if native else []}


def _permissions(session: q.HostSession, selections: tuple[q.Selection, ...]) -> list[dict[str, Any]]:
    records, reasons = [], []
    for selected in selections:
        permission = session._resolver.permission(selected.population.metric, selected.actor.model_version)
        records.append(_permission_record(permission, selected))
        if not permission.granted:
            reasons.append(permission.why())
    if reasons:
        raise _PermissionRefused(records, '; '.join(reasons) + '; human required')
    return records


def _refusal_bindings(session: q.HostSession, attempt: dict[str, Any], selections: tuple[q.Selection, ...]) -> dict[str, Any]:
    return {'session': session.identity, 'attempt': attempt['attempt_id'], 'subject': attempt['subject'],
        'job_sha256': q.hashlib.sha256(session._task_job or b'').hexdigest(), 'actor_sha256': selections[0].actor.digest,
        'selection_digests': {item.population.metric: item.digest for item in selections},
        'task_policy_digests': {item.population.metric: item._task_policy.digest for item in selections},
        'input_sha256': attempt['input_sha256'], 'output_sha256': attempt['capture_sha256'],
        'assessment_digests': {metric: value['digest'] for metric, value in session._task_reviews[attempt['attempt_id']].items()}}


def _retain_refusal(session: q.HostSession, attempt: dict[str, Any], selections: tuple[q.Selection, ...],
                    pending: dict[str, Any], request_digest: str, start: list[dict[str, Any]],
                    refused: Exception, reason: str) -> None:
    permission_loss = isinstance(refused, _PermissionRefused)
    value = {'schema': 'twin.task-review-refusal/v1', 'bindings': _refusal_bindings(session, attempt, selections),
        'request': {'metric': pending['task_review_metric'], 'sha256': request_digest},
        'failure': {'kind': 'current-permission-refused' if permission_loss else 'post-consumption-verification-error',
                    'exception_type': type(refused).__module__ + '.' + type(refused).__qualname__, 'message': str(refused)},
        'permissions_before_acquisition': start,
        'permissions_after_acquisition': refused.permissions if isinstance(refused, _PermissionRefused) else None,
        'prior_event_count': len(session._task_events), 'prior_events_sha256': q.digest(session._task_events), 'reason': reason}
    raw = q.canonical(value)
    receipt = _ReviewRefusal(raw, hmac.digest(_REFUSAL_KEY, raw, 'sha256'))
    session._resolver._task_refusal_receipts[receipt.digest] = receipt
    session._task_refusals[attempt['attempt_id']] = receipt.digest


def _verify_refusal(session: q.HostSession, attempt: dict[str, Any], selections: tuple[q.Selection, ...]) -> None:
    receipt = _refusal(session._resolver, session._task_refusals.get(attempt['attempt_id'], ''))
    value = json.loads(receipt.packet)
    if (set(value) != {'schema', 'bindings', 'request', 'failure', 'permissions_before_acquisition', 'permissions_after_acquisition',
                       'prior_event_count', 'prior_events_sha256', 'reason'}
            or value['schema'] != 'twin.task-review-refusal/v1'
            or q.canonical(value['bindings']) != q.canonical(_refusal_bindings(session, attempt, selections))
            or value['reason'] != attempt['reason']):
        raise ValueError('task refusal differs from original private review transaction')
    failure = value['failure']
    if (not isinstance(failure, dict) or set(failure) != {'kind', 'exception_type', 'message'}
            or not isinstance(failure['exception_type'], str) or not failure['exception_type']
            or not isinstance(failure['message'], str)):
        raise ValueError('task refusal lacks the actual typed transaction failure')
    permission_loss = failure['kind'] == 'current-permission-refused'
    permission_type = _PermissionRefused.__module__ + '.' + _PermissionRefused.__qualname__
    if permission_loss:
        expected_reason = 'current task permission refused after acquired reviews were consumed: ' + failure['message']
        if failure['exception_type'] != permission_type:
            raise ValueError('task permission refusal exception type differs')
    else:
        expected_reason = ('task verification failed after acquired reviews were consumed: ' + failure['exception_type']
                           + ': ' + failure['message'] + '; human required')
        if (failure['kind'] != 'post-consumption-verification-error' or failure['exception_type'] == permission_type
                or value['permissions_after_acquisition'] is not None):
            raise ValueError('task verification error cannot invent a current permission observation')
    if value['reason'] != expected_reason:
        raise ValueError('task refusal reason differs from the authenticated typed failure')
    request = value['request']; reviews = session._task_reviews[attempt['attempt_id']]
    if (not isinstance(request, dict) or set(request) != {'metric', 'sha256'} or request['metric'] not in reviews
            or request['sha256'] != q.digest(review_request(session, reviews[request['metric']]['record'], request['metric']))):
        raise ValueError('task refusal does not bind the actual consumed review request')
    offset = value['prior_event_count']
    if (type(offset) is not int or offset < 1 or offset >= len(session._task_events)
            or value['prior_events_sha256'] != q.digest(session._task_events[:offset])
            or session._task_events[offset] != {'attempt_id': attempt['attempt_id'], 'disposition': 'failed-review',
                'reason': value['reason'], 'receipt': None}):
        raise ValueError('task refusal event history differs from original private transaction')
    for phase in ('before', 'after'):
        records = value['permissions_' + phase + '_acquisition']
        if phase == 'after' and not permission_loss:
            continue
        if not isinstance(records, list) or len(records) != len(selections):
            raise ValueError('task refusal omits an independent current permission observation')
        for record, selected in zip(records, selections):
            if (set(record) != {'metric', 'model_version', 'kind', 'granted', 'conditions'}
                    or record['metric'] != selected.population.metric or record['model_version'] != selected.actor.model_version
                    or type(record['granted']) is not bool):
                raise ValueError('task refusal permission actor/metric observation differs')
            conditions = record['conditions']
            if record['kind'] == 'native':
                # Items 3/4/7 are checked at the claim/exercise seam; the native
                # Permission carries the seven measured permission conditions.
                if (not isinstance(conditions, list) or [item['item'] for item in conditions] != [1, 2, 5, 6, 8, 9, 10]
                        or any(set(item) != {'item', 'name', 'passed', 'detail'} or type(item['passed']) is not bool
                               or not isinstance(item['name'], str) or not isinstance(item['detail'], str) for item in conditions)
                        or record['granted'] != all(item['passed'] for item in conditions)):
                    raise ValueError('task refusal differs from actual native permission facts')
            elif (record['kind'] != 'TEST_ONLY-precondition' or conditions != []
                  or json.loads(selected.actor.description)['config'].get('purpose') != 'TEST_ONLY'):
                raise ValueError('public permission claims cannot authenticate a task refusal')
        if (phase == 'before' and not all(item['granted'] for item in records)
                or phase == 'after' and all(item['granted'] for item in records)):
            raise ValueError('task refusal lacks acquired-review current-permission loss')


def _gate(row: dict[str, Any], task: str) -> dict[str, Any] | None:
    if task != 'ethics':
        return None
    from .ethics_gate import admit_stated, SENSOR_TABLE_PATH
    value = admit_stated(row['input']['task'])
    return {'admitted': value.answer['admitted'],
        'source_sha256': q.digest({'input': row['input']['task'], 'sensor_table_sha256': q.hashlib.sha256(SENSOR_TABLE_PATH.read_bytes()).hexdigest()}),
        'result_sha256': q.digest({'answer': value.answer, 'basis': value.basis})}


def _base(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in (
        'task_review_metric', 'task_review_request', 'assessments', 'assessment_digests')}


def review_request(session: q.HostSession, record: dict[str, Any], metric: str | None = None) -> dict[str, Any]:
    metric = metric or record.get('task_review_metric', record['metric'])
    selected = session._resolver._bindings[(metric, record['model_version'])][0]
    row = session._inputs.resolve(record['subject'])
    if selected.assessment_policy is None:
        raise ValueError('task review requires its frozen independent rubric')
    return {'schema': 'twin.basis-request/v1', 'policy': selected.assessment_policy.digest,
        'actor_digest': selected.actor.digest, 'population_digest': selected.population.digest,
        'selection_digest': selected.digest, 'capture_digest': q.digest(_base(record)),
        'rows': [{'id': record['subject'], 'input': row['input'], 'context': row['context'],
                  'sources': row['sources'], 'output': record['output']}]}


def judge(session: q.HostSession, task: str, model_version: str, subject: str, *, paired: bool) -> q.Judgement:
    metrics = TaskContract.freeze(task).metrics
    attempt = _attempt(session, task, metrics, model_version, subject)
    output = None
    invoked = False
    try:
        if task == 'causal' and not paired:
            raise ValueError('registered causal task requires paired judgement and both current permissions; human required')
        if session._task_job is None:
            raise ValueError('protected task parent job must be bound before invocation; human required')
        job = json.loads(session._task_job)
        if (job['task'] != task or job['model_version'] != model_version or subject not in job['subjects']
                or job['task_contract_sha256'] != TaskContract.freeze(task).digest):
            raise ValueError('judgement differs from original protected task parent job')
        if any(item is not attempt and item['subject'] == subject and item['output'] is not None for item in session._task_attempts):
            raise ValueError('protected task subject already invoked; no automatic retry; human required')
        selections = _selections(session, task, model_version)
        row = session._inputs.resolve(subject)
        if row['context']['organisation'] != job['organisation']:
            raise ValueError('task adopter differs from protected parent job')
        for selected in selections:
            selected.verify_input(row)
        _permissions(session, selections)
        gate = _gate(row, task)
        attempt['mandatory_gate'] = gate
        invoked = True
        captured = selections[0].actor.invoke(row['input'])
        output = json.loads(captured.packet)
        if captured.failure or output['answer'] is None or output['basis'] is None:
            reason = captured.failure
            if not reason:
                try:
                    reason = json.loads(captured.raw).get('decline')
                except (ValueError, UnicodeError):
                    pass
            session._failed_outputs.append({'subject': subject, 'attempt': attempt['attempt_id'], 'output': output})
            _finish(session, attempt, 'failed' if captured.failure else 'declined', str(reason or 'actor declined') + '; human required', output)
            return q.Judgement(None, attempt['reason'], captured)
        record = {'subject': subject, 'metric': metrics[0], 'task_metrics': list(metrics), 'task': task,
            'model_version': model_version, 'selection': selections[0].digest,
            'task_selections': {selected.population.metric: selected.digest for selected in selections},
            'context': row['context'], 'output': output, 'attempt': attempt['attempt_id'],
            'mandatory_gate': gate, 'source_pins': _pins(row)}
        for selected in selections:
            request = review_request(session, record, selected.population.metric)
            pending = {**record, 'task_review_metric': selected.population.metric, 'task_review_request': request}
            session._pending[q.digest(request)] = q.canonical(pending)
        attempt['assessment_outcomes'] = {metric: 'pending' for metric in metrics}
        _finish(session, attempt, 'pending-review', 'independent task semantic assessment required; human required', output)
        return q.Judgement(None, attempt['reason'], captured)
    except Exception as exc:
        if invoked and output is None:
            output = {'actor_digest': model_version.removeprefix('actor-'), 'input_digest': attempt['input_sha256'],
                'raw': '', 'raw_available': False, 'failure': type(exc).__name__ + ': ' + str(exc),
                'observed_runtime': None, 'observations': {}, 'answer': None, 'basis': None}
            session._failed_outputs.append({'subject': subject, 'attempt': attempt['attempt_id'], 'output': output})
        _finish(session, attempt, 'refused-before-invocation' if output is None else 'failed', str(exc), output)
        return q.Judgement(None, str(exc))


def verify_record(session: q.HostSession, record: dict[str, Any], *, current: bool = False) -> tuple[q.Selection, ...]:
    required = {'subject', 'metric', 'task_metrics', 'task', 'model_version', 'selection', 'task_selections',
                'context', 'output', 'attempt', 'mandatory_gate', 'source_pins'}
    optional = {'task_review_metric', 'task_review_request', 'assessments', 'assessment_digests'}
    if not isinstance(record, dict) or not required <= set(record) or not set(record) <= required | optional:
        raise ValueError('registered task metric requires complete protected task receipt/job fields')
    try:
        return _verify_record(session, record, current=current)
    except (KeyError, TypeError, IndexError, AttributeError) as exc:
        raise ValueError('malformed protected task record') from exc


def _verify_record(session: q.HostSession, record: dict[str, Any], *, current: bool = False) -> tuple[q.Selection, ...]:
    selections = _selections(session, record['task'], record['model_version'])
    job = json.loads(session._task_job) if session._task_job else {}
    if (job.get('task') != record['task'] or job.get('model_version') != record['model_version']
            or job.get('task_contract_sha256') != selections[0]._task_contract.digest
            or record['subject'] not in job.get('subjects', [])):
        raise ValueError('task receipt differs from original current protected parent job')
    if record['metric'] != selections[0].population.metric or record['task_metrics'] != [item.population.metric for item in selections]:
        raise ValueError('task receipt omits or changes an independently required metric')
    row = session._inputs.resolve(record['subject'])
    if row['context']['organisation'] != job.get('organisation'):
        raise ValueError('task receipt adopter differs from original protected parent job')
    for selected in selections:
        selected.verify_input(row)
    if current:
        _permissions(session, selections)
    output = record['output']
    actor = selections[0].actor
    parsed = actor.parser(base64.b64decode(output['raw'], validate=True), json.loads(actor.description)['config'])
    from .task_inputs import verify_output
    verify_output(row['input'], parsed)
    runtime = json.loads(actor.description)['config'].get('runtime_contract')
    if (record['task_selections'] != {item.population.metric: item.digest for item in selections}
            or record['selection'] != selections[0].digest or record['context'] != row['context']
            or output['actor_digest'] != actor.digest or output['input_digest'] != q.digest(row['input'])
            or output.get('failure') or runtime and output.get('observed_runtime') != runtime
            or q.canonical({'answer': parsed.answer, 'basis': parsed.basis}) != q.canonical({'answer': output['answer'], 'basis': output['basis']})
            or record['source_pins'] != _pins(row) or record['mandatory_gate'] != _gate(row, record['task'])):
        raise ValueError('protected task receipt differs from actual input/output/target/source/gate binding')
    return selections


def review_pending(session: q.HostSession, request_digest: str, store: q.ReviewStore) -> q.Judgement:
    if request_digest not in session._pending:
        return q.Judgement(None, 'original task review absent or already consumed; human required')
    pending = json.loads(session._pending[request_digest])
    attempt = next(item for item in session._task_attempts if item['attempt_id'] == pending['attempt'])
    consumed = False
    try:
        selections = verify_record(session, pending)
        permission_start = _permissions(session, selections)
        request = review_request(session, pending)
        if request != pending['task_review_request'] or q.digest(request) != request_digest:
            raise ValueError('pending task review request/source/capture changed')
        selected = next(item for item in selections if item.population.metric == pending['task_review_metric'])
        policy = selected.assessment_policy
        if policy is None:
            raise ValueError('task independent assessment policy absent')
        assessment = store.assess(policy, q.canonical(request))
        outcome = assessment.outcome(pending['subject'])
        status = 'pass' if outcome is True else 'fail' if outcome is False else 'held'
        del session._pending[request_digest]
        attempt['assessment_outcomes'][selected.population.metric] = status
        session._reviewed_outputs.append({'record': pending, 'assessment': json.loads(assessment.packet)})
        session._task_reviews.setdefault(pending['attempt'], {})[selected.population.metric] = {
            'record': _base(pending), 'assessment': json.loads(assessment.packet), 'digest': assessment.digest}
        session._live_assessments[assessment.digest] = assessment
        consumed = True
        if outcome is not True:
            for key, raw in list(session._pending.items()):
                if json.loads(raw).get('attempt') == pending['attempt']:
                    del session._pending[key]
            _finish(session, attempt, 'failed-review' if outcome is False else 'held-review',
                    'independent task review ' + status + '; consumed without inference; human required')
            return q.Judgement(None, attempt['reason'])
        if any(value != 'pass' for value in attempt['assessment_outcomes'].values()):
            _finish(session, attempt, 'pending-review', 'other independent causal metric assessment required; human required')
            return q.Judgement(None, attempt['reason'])
        _permissions(session, selections)
        reviewed = session._task_reviews[pending['attempt']]
        record = {**_base(pending), 'assessments': {metric: value['assessment'] for metric, value in reviewed.items()},
                  'assessment_digests': {metric: value['digest'] for metric, value in reviewed.items()}}
        receipt = secrets.token_hex(24)
        session._records[receipt] = q.canonical(record)
        _finish(session, attempt, 'accepted', 'independent task assessments passed; recommendation only', receipt=receipt)
        return q.Judgement(receipt, None, q.Output(q.canonical(record['output'])))
    except Exception as exc:
        if consumed and set(attempt['assessment_outcomes'].values()) == {'pass'}:
            if isinstance(exc, _PermissionRefused):
                reason = 'current task permission refused after acquired reviews were consumed: ' + str(exc)
            else:
                reason = ('task verification failed after acquired reviews were consumed: ' + type(exc).__module__
                          + '.' + type(exc).__qualname__ + ': ' + str(exc) + '; human required')
            _retain_refusal(session, attempt, selections, pending, request_digest, permission_start, exc, reason)
            _finish(session, attempt, 'failed-review', reason)
            return q.Judgement(None, reason)
        # No assessment was consumed on an absent/stale acquisition. Its original
        # pending request and raw capture remain available without reinvocation.
        _finish(session, attempt, 'pending-review', str(exc) + '; human required')
        return q.Judgement(None, attempt['reason'])


def restore_assessments(session: q.HostSession) -> None:
    for by_metric in session._task_reviews.values():
        for metric, value in by_metric.items():
            selections = verify_record(session, value['record'])
            selected = next(item for item in selections if item.population.metric == metric)
            policy = selected.assessment_policy
            if policy is None:
                raise ValueError('task independent assessment policy absent')
            assessment = q._restore_assessment(q.canonical(value['assessment']), policy,
                                               q.canonical(review_request(session, value['record'], metric)))
            if assessment.digest != value['digest']:
                raise ValueError('retained task review digest changed')
            session._live_assessments[assessment.digest] = assessment


def restore_record(session: q.HostSession, record: dict[str, Any]) -> None:
    selections = verify_record(session, record)
    if set(record.get('assessments', {})) != set(record['task_metrics']):
        raise ValueError('paired/single task receipt omits required independent assessment')
    for selected in selections:
        metric = selected.population.metric
        policy = selected.assessment_policy
        if policy is None:
            raise ValueError('task independent assessment policy absent')
        assessment = q._restore_assessment(q.canonical(record['assessments'][metric]), policy,
                                           q.canonical(review_request(session, record, metric)))
        if assessment.digest != record['assessment_digests'][metric] or assessment.outcome(record['subject']) is not True:
            raise ValueError('task receipt independent basis did not pass')
        session._live_assessments[assessment.digest] = assessment


def verify_session(session: q.HostSession) -> None:
    try:
        _verify_session(session)
    except (KeyError, TypeError, IndexError, AttributeError) as exc:
        raise ValueError('malformed retained task lifecycle history') from exc


def _verify_session(session: q.HostSession) -> None:
    """Conserve task attempts, events, raw captures and independently acquired reviews.

    Protected archive pinning admits the bytes; it does not excuse an inconsistent
    count ledger or allow a public attempt row to manufacture a reviewed capture.
    Failed preflights use retained original rows without trying to resolve them again.
    """
    if session._task_job is None:
        raise ValueError('original protected task job required')
    job = json.loads(session._task_job)
    metrics = TaskContract.freeze(job['task']).metrics
    rows = {row.get('subject'): row for row in _raw_rows(session) if isinstance(row, dict)}
    attempts = session._task_attempts
    ids = [item.get('attempt_id') for item in attempts]
    if len(set(ids)) != len(ids) or any(not isinstance(identity, str) or not re.fullmatch(r'[0-9a-f]{48}', identity) for identity in ids):
        raise ValueError('task attempt identities must be complete and unique')
    expected_fields = {'attempt_id', 'subject', 'task', 'metrics', 'target', 'context', 'input_sha256', 'target_sha256',
        'actor_sha256', 'capture_sha256', 'raw_sha256', 'raw_available', 'disposition', 'reason', 'status', 'receipt',
        'output', 'assessment_outcomes', 'mandatory_gate', 'source_pins'}
    events = session._task_events
    dispositions = {'refused-before-invocation', 'failed', 'declined', 'pending-review', 'accepted', 'held-review', 'failed-review'}
    if any(not isinstance(event, dict) or set(event) != {'attempt_id', 'disposition', 'reason', 'receipt'}
           or event['attempt_id'] not in ids or event['disposition'] not in dispositions
           or not isinstance(event['reason'], str) or not event['reason'] for event in events):
        raise ValueError('task lifecycle event differs from counted attempt')
    if list(dict.fromkeys(event['attempt_id'] for event in events)) != ids:
        raise ValueError('task lifecycle omits or reorders counted attempts')
    declines = [{'subject': next(item['subject'] for item in attempts if item['attempt_id'] == event['attempt_id']),
                 'reason': event['reason']} for event in events if event['disposition'] != 'accepted']
    if declines != session.declines:
        raise ValueError('task lifecycle omits or rewrites counted declines')
    records = {json.loads(raw)['attempt']: (token, json.loads(raw)) for token, raw in session._records.items()}
    if (len(records) != len(session._records) or not set(records) <= set(ids) or not set(session._task_reviews) <= set(ids)
            or not set(session._task_refusals) <= set(ids)):
        raise ValueError('task receipt/review has no unique original counted attempt')
    pending: dict[str, dict[str, Any]] = {}
    for key, raw in session._pending.items():
        record = json.loads(raw)
        identity, metric = record.get('attempt'), record.get('task_review_metric')
        if identity not in ids or metric not in metrics or metric in pending.setdefault(identity, {}):
            raise ValueError('task pending review has no unique original metric/attempt')
        pending[identity][metric] = record
        if q.digest(review_request(session, record, metric)) != key:
            raise ValueError('pending task review request changed')
    observed_subjects = []
    failed = {}
    for item in attempts:
        identity, subject = item['attempt_id'], item['subject']
        binding = _input_binding(rows.get(subject, {}), job['model_version'])
        history = [event for event in events if event['attempt_id'] == identity]
        status = {'refused-before-invocation': 'declined', 'pending-review': 'pending',
                  'held-review': 'held', 'failed-review': 'failed'}.get(item['disposition'], item['disposition'])
        if (set(item) != expected_fields or subject not in job['subjects'] or item['task'] != job['task']
                or item['metrics'] != list(metrics) or any(q.canonical(item[key]) != q.canonical(value) for key, value in binding.items())
                or item['status'] != status or not history
                or {key: item[key] for key in ('disposition', 'reason', 'receipt')} != {
                    key: history[-1][key] for key in ('disposition', 'reason', 'receipt')}):
            raise ValueError('task attempt differs from original input/target/actor/event binding')
        output = item['output']
        reviews = session._task_reviews.get(identity, {})
        outcomes = {}
        for metric, value in reviews.items():
            if metric not in metrics or value['record'].get('attempt') != identity or value['record']['subject'] != subject:
                raise ValueError('task review belongs to another metric/attempt/subject')
            if q.canonical(value['record']['output']) != q.canonical(output):
                raise ValueError('task review changed the original captured output')
            assessment = session._live_assessments[value['digest']]
            outcome = assessment.outcome(subject)
            outcomes[metric] = 'pass' if outcome is True else 'fail' if outcome is False else 'held'
        if output is None:
            if (item['disposition'] != 'refused-before-invocation' or item['capture_sha256'] is not None
                    or item['raw_sha256'] is not None or item['raw_available'] is not False
                    or item['mandatory_gate'] is not None or item['assessment_outcomes'] or reviews or pending.get(identity)
                    or identity in records):
                raise ValueError('pre-invocation task refusal invents capture/review/receipt')
            continue
        observed_subjects.append(subject)
        row = session._inputs.resolve(subject)
        selections = _selections(session, job['task'], job['model_version'])
        for selected in selections:
            selected.verify_input(row)
        raw = base64.b64decode(output['raw'], validate=True)
        if (set(output) != {'actor_digest', 'input_digest', 'raw', 'raw_available', 'failure', 'observed_runtime', 'observations', 'answer', 'basis'}
                or type(output['raw_available']) is not bool or not output['raw_available'] and raw
                or output['actor_digest'] != job['model_version'].removeprefix('actor-')
                or output['input_digest'] != item['input_sha256'] or item['capture_sha256'] != q.digest(output)
                or item['raw_available'] is not output['raw_available'] or item['raw_sha256'] != q.hashlib.sha256(raw).hexdigest()
                or item['mandatory_gate'] != _gate(row, job['task'])):
            raise ValueError('task raw capture/digest/gate differs from actual original input')
        if output['failure'] or output['answer'] is None:
            if item['disposition'] not in ('failed', 'declined') or reviews or pending.get(identity) or identity in records:
                raise ValueError('failed/declined task capture cannot invent a review or receipt')
            if output['failure'] and (output['answer'] is not None or output['basis'] is not None):
                raise ValueError('failed task capture invents answer/basis')
            if not output['failure']:
                parsed = selections[0].actor.parser(raw, json.loads(selections[0].actor.description)['config'])
                from .task_inputs import verify_output
                verify_output(row['input'], parsed)
                if q.canonical({'answer': parsed.answer, 'basis': parsed.basis}) != q.canonical({'answer': output['answer'], 'basis': output['basis']}):
                    raise ValueError('declined task capture differs from actual raw')
            failed[identity] = {'subject': subject, 'attempt': identity, 'output': output}
            continue
        expected_outcomes = {metric: outcomes.get(metric, 'pending') for metric in metrics}
        if item['assessment_outcomes'] != expected_outcomes:
            raise ValueError('task attempt assessment outcomes differ from actual retained reviews')
        authority_refused = len(outcomes) == len(metrics) and set(outcomes.values()) == {'pass'} and item['disposition'] == 'failed-review'
        if authority_refused:
            if item['receipt'] is not None or identity in records or pending.get(identity):
                raise ValueError('consumed authority refusal cannot invent receipt or pending work')
            _verify_refusal(session, item, selections)
        elif identity in session._task_refusals:
            raise ValueError('task refusal receipt cannot replace another lifecycle disposition')
        elif any(value in ('fail', 'held') for value in outcomes.values()):
            expected_disposition = 'failed-review' if 'fail' in outcomes.values() else 'held-review'
            if item['disposition'] != expected_disposition or pending.get(identity) or identity in records:
                raise ValueError('failed/held task review was not consumed')
        elif len(outcomes) == len(metrics):
            token, record = records.get(identity, (None, {}))
            if (item['disposition'] != 'accepted' or item['receipt'] != token or token is None or pending.get(identity)
                    or q.canonical(record.get('output')) != q.canonical(output)
                    or record.get('assessment_digests') != {metric: value['digest'] for metric, value in reviews.items()}):
                raise ValueError('task acceptance lacks exact independent reviewed receipt')
        elif (item['disposition'] != 'pending-review' or item['receipt'] is not None or identity in records
              or set(pending.get(identity, {})) != set(metrics) - set(outcomes)
              or any(q.canonical(value['output']) != q.canonical(output) for value in pending.get(identity, {}).values())):
            raise ValueError('task pending attempt omits an independent review/capture')
    if len(set(observed_subjects)) != len(observed_subjects):
        raise ValueError('task subject was automatically reinvoked')
    if session._failed_outputs != list(failed.values()):
        raise ValueError('task failed raw capture history changed')


def check_document(session: q.HostSession, document: dict[str, Any]) -> list[str]:
    """Verify a proposal against original host history and both current authorities."""
    bad = []
    try:
        if session._task_job is None:
            raise ValueError('no original protected task parent job')
        verify_session(session)
        job = json.loads(session._task_job)
        state = snapshot(session)
        run = document.get('run', {})
        expected_schema = {'evolution': 'twin.headline-claim/v1', 'causal': 'twin.causal-proposal/v1',
                           'gameplay': 'twin.gameplay-proposal/v1', 'ethics': 'twin.ethics-judgement/v1'}[job['task']]
        if document.get('schema') != expected_schema:
            raise ValueError('task document schema differs from protected job')
        if job['task'] != 'evolution':
            validate('ProposalDocument', document)
        clock = q.mp.derive_clock(run.get('clock'))[0]
        if (document.get('org') != job['organisation'] or run.get('host_session') != session.identity
                or run.get('task_contract_sha256') != job['task_contract_sha256']
                or run.get('model_version') != job['model_version'] or run.get('clock') != clock
                or any(run.get(key) is not False for key in ('action_authority', 'merge_authority', 'override_authority', 'price_eligible'))
                or run.get('declined') != session.declines
                or q.canonical(run.get('attempts')) != q.canonical([{key: item[key] for key in ATTEMPT_FIELDS} for item in state['attempts']])
                or document.get('source_pins') != state['source_pins']):
            raise ValueError('task document job/clock/authority/count/source pins differ from protected history')
        rows = document.get('claims') if job['task'] == 'evolution' else document.get('judgements')
        if not isinstance(rows, list):
            raise ValueError('complete task judgement rows required')
        seen = []
        for item in rows:
            token = item.get('host_receipt')
            if not isinstance(token, str) or token not in session._records:
                raise ValueError('task judgement lacks actual protected receipt')
            seen.append(token)
            record = json.loads(session._records[token])
            selections = verify_record(session, record, current=True)
            if record['task'] != job['task'] or record['model_version'] != job['model_version']:
                raise ValueError('receipt task/actor differs from original job')
            for selected in selections:
                digest = record['assessment_digests'][selected.population.metric]
                assessment = session._live_assessments.get(digest)
                if assessment is None:
                    raise ValueError('no protected actual independent task assessment')
                policy = selected.assessment_policy
                if policy is None:
                    raise ValueError('task independent assessment policy absent')
                assessment.verify(policy, q.canonical(review_request(session, record, selected.population.metric)))
                if assessment.outcome(record['subject']) is not True:
                    raise ValueError('independent task basis did not pass')
            row = session._inputs.resolve(record['subject'])
            if job['task'] == 'evolution':
                if (item.get('kind') != 'position' or item.get('component') != row['context']['target']['component']
                        or item.get('host_subject') != record['subject']
                        or q.canonical(item.get('evolution_position')) != q.canonical(record['output']['answer']['evolution_position'])
                        or item.get('evidence') != q.canonical(record['output']['basis']).decode()
                        or item.get('evidence_grade') != 5 or item.get('price_eligible') is not False
                        or item.get('source_pins') != record['source_pins'] or document.get('derived_from') != []):
                    raise ValueError('position differs from complete actual task target/output/basis/pins')
            elif (item.get('subject') != record['subject'] or item.get('attempt_id') != record['attempt']
                    or item.get('target') != row['context']['target']
                    or q.canonical(item.get('answer')) != q.canonical(record['output']['answer'])
                    or q.canonical(item.get('basis')) != q.canonical(record['output']['basis'])
                    or item.get('actual_output_sha256') != q.digest(record['output'])
                    or item.get('mandatory_gate') != record['mandatory_gate']):
                raise ValueError('proposal differs from complete actual task target/output/basis/gate')
        accepted = {item['receipt'] for item in state['attempts'] if item['disposition'] == 'accepted'}
        if len(set(seen)) != len(seen) or set(seen) != accepted or set(seen) != set(session._records):
            raise ValueError('task document omits/duplicates/replays protected judgements')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        bad.append(str(exc))
    return bad
