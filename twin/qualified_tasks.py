"""Protected remaining-task parents. Pure document projection never grants permission.

The qualification host owns acquisition, actual output, review, receipts and their validation.
No actor, job, reviewer, backend or acquisition is registered by this module.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path
import re
from typing import Any, Protocol, cast

from . import qualification as q
from .task_contracts import TaskContract, decode, validate


SCHEMAS = {'causal': 'twin.causal-proposal/v1', 'gameplay': 'twin.gameplay-proposal/v1',
           'ethics': 'twin.ethics-judgement/v1'}
ATTEMPT_FIELDS = ('attempt_id', 'subject', 'input_sha256', 'target_sha256', 'actor_sha256',
                  'capture_sha256', 'raw_available', 'disposition', 'reason')
CATALOGUE = Path(q.__file__).with_name('qualification-registry.json')


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


class TaskInputs(Protocol):
    @property
    def records(self) -> tuple[dict[str, Any], ...]: ...


class TaskSession(Protocol):
    def bind_task_job(self, job: dict[str, Any]) -> None: ...
    def decline_task_run(self, subjects: tuple[str, ...], reason: str) -> None: ...
    def judge(self, metric: str, model_version: str, subject: str) -> q.Judgement: ...
    def judge_group(self, model_version: str, subject: str) -> q.Judgement: ...
    def review_pending(self, request_digest: str, store: Any) -> q.Judgement: ...
    def task_snapshot(self) -> dict[str, Any]: ...
    def check_task_document(self, document: dict[str, Any]) -> list[str]: ...
    def archive(self) -> bytes: ...


class TaskResolver(Protocol):
    def host_session(self, inputs: Any) -> TaskSession: ...
    def task_session(self, identity: str) -> TaskSession: ...
    def task_policy(self, digest: str) -> Any: ...


def validate_document(document: dict[str, Any], resolver: TaskResolver, clock: str | None = None) -> list[str]:
    """Public validator hook: a document cannot recreate a private host session/receipt."""
    from .repo import load_yaml
    bad = []
    try:
        run = document.get('run') or {}
        if run.get('clock') != q.mp.derive_clock(clock)[0]:
            bad.append('task document clock differs from the protected caller/environment')
        if run.get('headless') is not True:
            bad.append('protected model task document must retain its headless parent mode')
        roles = load_yaml(Path(q.__file__).with_name('roles.yaml').read_text())
        if run.get('operator_role') not in {item['id'] for item in roles['roles']}:
            bad.append('task operator role is not registered')
        identity = run.get('host_session')
        if not isinstance(identity, str) or not identity:
            raise ValueError('no protected task session identity')
        session = resolver.task_session(identity)
        bad.extend(session.check_task_document(document))
    except (ValueError, KeyError, TypeError, AttributeError, OSError, RuntimeError) as exc:
        bad.append('protected task session verification failed: ' + str(exc))
    return bad


class TaskParent:
    """A protected parent invokes only the host's registered task or paired causal seam."""
    def __init__(self, resolver: TaskResolver, *, role: str = 'model-steward', clock: str | None = None):
        self.resolver, self.role = resolver, role
        self.clock = q.mp.derive_clock(clock)[0]

    def start(self, protected_job: dict[str, Any], inputs: TaskInputs) -> TaskRun:
        session = self.resolver.host_session(inputs)
        session.bind_task_job(protected_job)
        run = TaskRun(self, protected_job, session)
        try:
            contract = _job(protected_job)
            rows = inputs.records
            if ([row['subject'] for row in rows] != protected_job['subjects']
                    or {row['context']['organisation'] for row in rows} != {protected_job['organisation']}
                    or protected_job['organisation'] not in ('driftwood', 'tuppence', 'ludlow')):
                raise ValueError('mixed or mismatched adopter/subject scope is outside the protected task run')
            for row in rows:
                context = row['context']
                if context['task_contract_sha256'] != contract.digest:
                    raise ValueError('host input names a stale or foreign task contract')
                target = context['target']
                validate({'evolution': 'TargetComponent', 'causal': 'TargetEdge',
                          'gameplay': 'TargetMap', 'ethics': 'TargetSensor'}[contract.task], target)
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            session.decline_task_run(tuple(protected_job['subjects']), 'human-required: ' + str(exc))
            return run
        for subject in protected_job['subjects']:
            result = (session.judge_group(protected_job['model_version'], subject) if contract.task == 'causal'
                else session.judge(contract.metrics[0], protected_job['model_version'], subject))
            run.results.append(result)
        return run

    def resume(self, protected_job: dict[str, Any], session: TaskSession) -> TaskRun:
        _job(protected_job)
        if q.canonical(session.task_snapshot()['job']) != q.canonical(protected_job):
            raise ValueError('restored task session names a different protected job')
        return TaskRun(self, protected_job, session)


class TaskRun:
    def __init__(self, parent: TaskParent, job: dict[str, Any], session: TaskSession):
        self.parent, self.session = parent, session
        self._job_bytes = q.canonical(job)
        self.results: list[q.Judgement] = []

    @property
    def job(self) -> dict[str, Any]:
        return decode(self._job_bytes)

    def review_pending(self, protected_store: Any) -> list[q.Judgement]:
        results = []
        original = self.session.task_snapshot()['pending_reviews']
        for request in original:
            key = request['request_digest']
            current = {item['request_digest'] for item in self.session.task_snapshot()['pending_reviews']}
            if key in current:
                result = self.session.review_pending(key, protected_store)
                results.append(result)
                self.results.append(result)
        return results

    def document(self) -> dict[str, Any] | None:
        return document_from_snapshot(self.job, self.session.task_snapshot(), role=self.parent.role, clock=self.parent.clock)

    def validate(self) -> list[str]:
        document = self.document()
        if document is None:
            return ['no accepted task judgement; human-required fallback remains']
        return validate_document(document, self.parent.resolver, self.parent.clock)

    def save(self, output: Path) -> dict[str, Any]:
        output.mkdir(parents=True, exist_ok=False)
        (output / 'host-session.json').write_bytes(self.session.archive())
        state = self.session.task_snapshot()
        (output / 'task-snapshot.json').write_bytes(q.canonical(state))
        (output / 'review-requests.json').write_bytes(q.canonical(state['pending_reviews']))
        document = None
        try:
            document = self.document()
            bad = self.validate()
        except (ValueError, KeyError, TypeError, AttributeError, OSError, RuntimeError) as exc:
            bad = ['protected task validation failed; human-required: ' + str(exc)]
        if document is not None and not bad:
            (output / ('claim.json' if self.job['task'] == 'evolution' else 'proposal.json')).write_bytes(q.canonical(document))
        blocked = [item['subject'] for item in state['attempts']
                   if isinstance(item.get('mandatory_gate'), dict) and item['mandatory_gate'].get('admitted') is False]
        summary = {'accepted': document is not None and not bad, 'human_required': bool(bad), 'reasons': bad,
            'declined': state['declines'], 'attempts': state['attempts'], 'events': state.get('events', []),
            'pending_reviews': len(state['pending_reviews']), 'mandatory_gate_blocked': blocked,
            'sensor_activation': False, 'action_authority': False, 'merge_authority': False,
            'actual_permission_grant': False, 'target_runtime_measured_by_this_command': False}
        (output / 'summary.json').write_bytes(q.canonical(summary))
        return summary


def _member(root: Path, descriptor: dict[str, Any]) -> bytes:
    if (not isinstance(descriptor, dict) or set(descriptor) != {'path', 'sha256'}
            or not isinstance(descriptor['path'], str) or not descriptor['path']
            or not isinstance(descriptor['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', descriptor['sha256'])):
        raise ValueError('exact pinned protected member descriptor required')
    relative = Path(descriptor['path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('protected task member escapes catalogue')
    path = root
    for part in relative.parts:
        path /= part
        if path.is_symlink():
            raise ValueError('protected task member traverses a symlink')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('protected task member escapes catalogue')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != descriptor['sha256']:
        raise ValueError('protected task member digest changed')
    return raw


def run_registered(task: str, organisation: str, output: Path, clock: str | None = None,
                   *, resolver: TaskResolver | None = None) -> dict[str, Any]:
    """Use only fixed protected-package jobs and original independently supplied handles."""
    if output.exists():
        raise FileExistsError('historical task output already exists')
    catalogue = CATALOGUE
    try:
        TaskContract.freeze(task)
        if catalogue.is_symlink():
            raise ValueError('protected task catalogue is a symlink')
        raw = catalogue.read_bytes()
        entry = decode(raw).get('task_jobs', {}).get(task, {}).get(organisation)
        if entry is None:
            raise ValueError('no registered task job; qualification, acquisition and target prerequisites remain')
        root = catalogue.parent
        bundle = decode(_member(root, entry))
        if (not isinstance(bundle, dict) or not {'schema', 'execution', 'task_policy_sha256', 'inputs'} <= set(bundle)
                or set(bundle) - {'schema', 'execution', 'task_policy_sha256', 'inputs', 'resume_session', 'review_store'}
                or bundle['schema'] != 'twin.protected-task-job/v1'
                or bundle['execution']['task'] != task or bundle['execution']['organisation'] != organisation):
            raise ValueError('registered task job shape or route differs')
        host = resolver or cast(TaskResolver, q.Resolver.from_catalogue(catalogue, hashlib.sha256(raw).hexdigest()))
        policy = host.task_policy(bundle['task_policy_sha256'])
        inputs_raw = _member(root, bundle['inputs'])
        # Only the original independently supplied handle can restore host inputs.
        inputs = q.HostInputs.restore(inputs_raw, task_policy=policy)
        store = None
        if bundle.get('review_store'):
            from .basis_assessment import ReviewStore
            _member(root, bundle['review_store'])
            store = ReviewStore(root / bundle['review_store']['path'], bundle['review_store']['sha256'])
        parent = TaskParent(host, clock=clock)
        run = (parent.resume(bundle['execution'], host.task_session(bundle['resume_session']))
               if bundle.get('resume_session') else parent.start(bundle['execution'], inputs))
        if store is not None:
            run.review_pending(store)
        return run.save(output)
    except (ValueError, KeyError, TypeError, AttributeError, OSError, RuntimeError) as exc:
        output.mkdir(parents=True, exist_ok=True)
        summary = {'accepted': False, 'human_required': True, 'reasons': [str(exc)],
            'declined': [], 'attempts': [], 'pending_reviews': 0, 'actual_permission_grant': False,
            'target_runtime_measured_by_this_command': False, 'sensor_activation': False}
        (output / 'summary.json').write_bytes(q.canonical(summary))
        return summary
