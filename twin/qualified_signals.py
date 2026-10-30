"""Protected parent invocation and existing-validator handoff for registered signal actors.

No actor, reviewer or runtime is registered by this module. Missing qualification/acquisition
remains a counted decline. Human/local and raw incumbent consumers keep their existing paths.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from . import qualification as q
from .basis_assessment import ReviewStore
from .signal_candidate import evidence_text


def _validator() -> Any:
    path = Path(__file__).resolve().parents[1] / '.claude/skills/classify-and-judge/assets/validate_claim.py'
    spec = importlib.util.spec_from_file_location('protected_signal_validator', path)
    if spec is None or spec.loader is None:
        raise ValueError('existing protected claim validator is unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SignalParent:
    def __init__(self, resolver: q.Resolver, model_version: str, *, role: str = 'model-steward',
                 clock: str | None = None):
        self.resolver, self.model_version, self.role = resolver, model_version, role
        self.clock = q.mp.derive_clock(clock)[0]

    def start(self, inputs: q.HostInputs) -> SignalRun:
        session = self.resolver.host_session(inputs)
        run = SignalRun(self, session)
        for row in json.loads(inputs.description)['records']:
            run.results.append(session.judge('signal-classify', self.model_version, row['subject']))
        return run


class SignalRun:
    def __init__(self, parent: SignalParent, session: q.HostSession):
        self.parent, self.session = parent, session
        self.results: list[q.Judgement] = []

    def review(self, request_digest: str, store: ReviewStore) -> q.Judgement:
        result = self.session.review_pending(request_digest, store)
        self.results.append(result)
        return result

    def document(self) -> dict[str, Any] | None:
        claims, pins = [], []
        for packet in json.loads(self.session.archive())['records'].values():
            if packet['metric'] != 'signal-classify':
                raise ValueError('signal parent cannot emit another metric')
            output, context = packet['output'], packet['context']
            subject = packet['subject']
            receipt = next(token for token, record in json.loads(self.session.archive())['records'].items()
                           if record == packet)
            row = self.session._inputs.resolve(subject)
            signal = {**context['signal'], 'statement': row['input']['statement'],
                      'source': row['input']['source'], 'steep': output['answer']['steep']}
            pin = signal['from']
            if pin not in pins:
                pins.append(pin)
            claims.append({**output['answer']['claim'], 'id': subject + '-binding-' + receipt[:12],
                'kind': 'binding', 'evidence_grade': 5, 'claimed_by': 'signal-classify candidate (skill)',
                'price_eligible': False, 'signal': signal, 'host_subject': subject,
                'host_receipt': receipt, 'evidence': evidence_text(output['basis'])})
        if not claims:
            return None
        organisations = {record['context']['organisation'] for record in json.loads(self.session.archive())['records'].values()}
        if len(organisations) != 1:
            raise ValueError('one claim document must belong to one adopter')
        return {'schema': 'twin.headline-claim/v1', 'org': next(iter(organisations)),
            'derived_from': pins, 'claims': claims, 'run': {'skill': 'classify-and-judge',
                'operator_role': self.parent.role, 'headless': True, 'clock': self.parent.clock,
                'model_version': self.parent.model_version, 'host_session': self.session.identity,
                'declined': self.session.declines}}

    def validate(self) -> list[str]:
        document = self.document()
        if document is None:
            return ['no accepted binding; qualification/reviewer/runtime prerequisites remain']
        validator = _validator()
        root = str(Path(__file__).resolve().parents[1])
        kinds, roles = validator.twin_facts(root)
        permission = self.parent.resolver.permission('signal-classify', self.parent.model_version)
        bad = [] if permission.granted else [permission.why()]
        bad.extend(self.session.check_document(document))
        return bad + validator.validate(document, kinds, roles, headless=True, clock=self.parent.clock,
            permission=(self.parent.resolver.check_claim_document, self.parent.resolver.permission))

    def save(self, output: Path) -> dict[str, Any]:
        output.mkdir(parents=True, exist_ok=False)
        (output / 'host-session.json').write_bytes(self.session.archive())
        (output / 'review-requests.json').write_bytes(q.canonical(self.session.pending_reviews))
        bad = self.validate()
        document = self.document()
        if document is not None and not bad:
            (output / 'claim.json').write_bytes(q.canonical(document))
        summary = {'accepted': document is not None and not bad, 'reasons': bad,
            'declined': self.session.declines, 'pending_reviews': len(self.session.pending_reviews),
            'actual_permission_grant': False, 'target_runtime_measured_by_this_command': False}
        (output / 'summary.json').write_bytes(q.canonical(summary))
        return summary


def _member(root: Path, name: str, expected: str) -> bytes:
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('registered host job member escapes protected catalogue')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('registered host job member changed')
    return raw


def run_registered(organisation: str, output: Path, clock: str | None = None) -> dict[str, Any]:
    """Called by the existing validator CLI, with registrations solely from its judge package.

    Job and acquisition roots are not CLI/claim-selected. The initially empty catalogue has
    no job, backend, live actor or permission; this path reports those blockers explicitly.
    """
    if output.exists():
        raise FileExistsError('host evidence output already exists; historical runs are immutable')
    catalogue = Path(q.__file__).with_name('qualification-registry.json')
    root = catalogue.parent
    try:
        raw = catalogue.read_bytes()
        resolver = q.Resolver.from_catalogue(catalogue, hashlib.sha256(raw).hexdigest())
        entry = json.loads(raw).get('signal_jobs', {}).get(organisation)
        if entry is None:
            raise ValueError('no registered signal job; current custody, actual target measurement and reviewer acquisition remain required')
        job = json.loads(_member(root, entry['job'], entry['sha256']))
        parent = SignalParent(resolver, job['model_version'], role=job['operator_role'], clock=clock)
        permission = resolver.permission('signal-classify', parent.model_version)
        if not permission.granted:
            raise ValueError(permission.why())
        if job.get('resume_session'):
            session = resolver._sessions[job['resume_session']]
            run = SignalRun(parent, session)
        else:
            from .repo import ModelRepo
            from .signal_inputs import resolve_signal_input
            source = _member(root, job['source']['path'], job['source']['sha256'])
            party = _member(root, job['party']['path'], job['party']['sha256'])
            repo_path = root / job['repo']
            if not repo_path.resolve().is_relative_to(root.resolve()):
                raise ValueError('registered model repository escapes host snapshot')
            resolved = resolve_signal_input(ModelRepo.open(repo_path), organisation, source,
                job['source']['sha256'], party, job['party']['sha256'], job['policy'])
            run = parent.start(resolved.host_inputs())
        if job.get('review_store'):
            store_entry = job['review_store']
            _member(root, store_entry['path'], store_entry['sha256'])
            store = ReviewStore(root / store_entry['path'], store_entry['sha256'])
            for request in list(run.session.pending_reviews):
                run.review(request['request_digest'], store)
        return run.save(output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        output.mkdir(parents=True, exist_ok=True)
        summary = {'accepted': False, 'reasons': [str(exc)], 'declined': [],
            'actual_permission_grant': False, 'target_runtime_measured_by_this_command': False}
        (output / 'summary.json').write_bytes(q.canonical(summary))
        return summary
