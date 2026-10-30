"""Host-owned actor/population bindings around the existing skill evaluator.

Bindings identify measured computation, not the truth of a custodian's references. The host
owns adapters/configuration and keeps its session outside the model child. Model output and
claim documents cannot register an actor or manufacture a host invocation receipt.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
import hashlib
import hmac
import importlib
import inspect
import json
import marshal
from pathlib import Path
import platform
import sys
import secrets
import types
from typing import Any, Callable
from datetime import date
from enum import Enum

from .skills import Stated, EvalResult, evaluate, record_score, load_scores, threshold_for, min_items_for
from .reference_cases import Admission
from . import record_skill_scores as rss
from . import model_permission as mp
from .canon import digest_of
from .basis_assessment import BasisPolicy, BasisAssessment, ReviewStore, _restore_assessment


class TestOnlyPurpose(Enum):
    """Explicit protected parent purpose, never inferred from serialized packet text."""
    MECHANICS = 'TEST_ONLY-legacy-mechanics'


TEST_ONLY_MECHANICS = TestOnlyPurpose.MECHANICS


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _runtime() -> dict[str, str]:
    return {'platform': platform.platform(), 'python': sys.version,
            'executable_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()}


def _source_name(path: Path) -> str:
    try:
        return 'repo:' + path.resolve().relative_to(Path(__file__).resolve().parents[1]).as_posix()
    except ValueError:
        return 'external:' + str(path.resolve())


def _source_path(name: str) -> Path:
    kind, value = name.split(':', 1)
    if kind == 'repo':
        root = Path(__file__).resolve().parents[1]
        path = root / value
        if not path.resolve().is_relative_to(root):
            raise ValueError('support source escapes the protected checkout')
        return path
    if kind == 'external':
        return Path(value)
    raise ValueError('unknown source identity')


def _code_identity(code: types.CodeType) -> types.CodeType:
    return code.replace(co_filename='<host-source>', co_consts=tuple(
        _code_identity(value) if isinstance(value, types.CodeType) else value for value in code.co_consts))


def _default_identity(value: Any) -> dict[str, Any]:
    """JSON-safe defaults without losing tuple/list types, mapping order or shared state.

    The actual imported function retains its Python defaults; this is only their comparison
    identity. Built-in JSON scalars/collections are supported, including nested tuples. Custom
    objects and cycles require explicit invocation config instead of implicit captured state.
    """
    seen: dict[int, int] = {}
    active: set[int] = set()
    def encode(item: Any) -> dict[str, Any]:
        kind = type(item)
        if kind is float:
            return {'kind': 'float', 'value': canonical(item).decode()}
        if kind in (type(None), bool, int, str):
            return {'kind': kind.__name__, 'value': item}
        if kind not in (tuple, list, dict):
            raise ValueError('unsupported callable default; use explicit config')
        identity = id(item)
        if identity in active:
            raise ValueError('cyclic callable default; use explicit config')
        if identity in seen:
            return {'kind': 'alias', 'index': seen[identity]}
        index = seen[identity] = len(seen)
        active.add(identity)
        values: list[Any]
        if kind is dict:
            if any(type(key) not in (type(None), bool, int, float, str) for key in item):
                raise ValueError('unsupported callable default mapping key; use explicit config')
            values = [[encode(key), encode(child)] for key, child in item.items()]
        else:
            values = [encode(child) for child in item]
        active.remove(identity)
        return {'kind': kind.__name__, 'index': index, 'items': values}
    return encode(value)


def _callable_identity(fn: Callable[..., Any]) -> dict[str, Any]:
    if not inspect.isfunction(fn) or fn.__closure__:
        raise ValueError('host adapters must be module functions without captured state; use config')
    return {'module': fn.__module__, 'name': fn.__qualname__,
            'code_sha256': hashlib.sha256(marshal.dumps(_code_identity(fn.__code__))).hexdigest(),
            'defaults': _default_identity({'positional': fn.__defaults__, 'keyword': fn.__kwdefaults__})}


@dataclass(frozen=True)
class Output:
    packet: bytes

    @property
    def raw(self) -> bytes:
        return base64.b64decode(json.loads(self.packet)['raw'])

    @property
    def stated(self) -> Stated:
        value = json.loads(self.packet)
        return Stated(value['answer'], value['basis'])

    @property
    def actor_digest(self) -> str:
        return str(json.loads(self.packet)['actor_digest'])

    @property
    def failure(self) -> str | None:
        return json.loads(self.packet).get('failure')


@dataclass(frozen=True)
class RuntimeResult:
    """Trusted runner observations, kept outside model-produced response bytes.

    A backend adapter obtains these from its actual assets/build/loaded computation. A parser
    cannot construct them after reading the response, and their required shape is frozen in
    the same runtime_contract that the runner receives for invocation.
    """
    raw: bytes
    observed_runtime: dict[str, Any]
    observations: dict[str, Any] = field(default_factory=dict)
    failure: str | None = None


@dataclass(frozen=True)
class Actor:
    """Actual adapters plus immutable invocation config; neither comes from a model response."""
    description: bytes
    runner: Callable[[Any, dict[str, Any]], bytes | RuntimeResult]
    parser: Callable[[bytes, dict[str, Any]], Stated]
    _source_metadata_authority: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def freeze(cls, runner: Callable[[Any, dict[str, Any]], bytes | RuntimeResult],
               parser: Callable[[bytes, dict[str, Any]], Stated], config: dict[str, Any],
               *, support: tuple[Path, ...] = (), source_metadata_authority: Any = None) -> Actor:
        paths = {Path(__file__).resolve(), *(Path(inspect.getfile(fn)).resolve() for fn in (runner, parser))} | {
            path.resolve() for path in support}
        authority = None
        if source_metadata_authority is not None:
            from . import source_metadata, signal_inputs
            source_metadata_authority.verify()
            authority = json.loads(source_metadata_authority.description)
            paths |= {_source_path(path) for path in authority['sources']}
            paths |= {Path(source_metadata.__file__), source_metadata.SCHEMA_PATH, Path(signal_inputs.__file__)}
        sources = {_source_name(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        description = {'config': config, 'runtime': _runtime(), 'sources': sources,
                              'runner': _callable_identity(runner),
                              'parser': _callable_identity(parser)}
        if authority is not None:
            description['source_metadata_authority'] = authority
        return cls(canonical(description), runner, parser, source_metadata_authority)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.description).hexdigest()

    @property
    def model_version(self) -> str:
        return 'actor-' + self.digest

    def verify(self) -> None:
        value = json.loads(self.description)
        if value.get('source_metadata_authority') is not None:
            if self._source_metadata_authority is None:
                raise ValueError('actor requires protected metadata authority handle')
            self._source_metadata_authority.verify()
            if value['source_metadata_authority'] != json.loads(self._source_metadata_authority.description):
                raise ValueError('actor metadata authority changed')
        if (value['runtime'] != _runtime() or value['runner'] != _callable_identity(self.runner)
                or value['parser'] != _callable_identity(self.parser)):
            raise ValueError('actor runtime or adapter changed')
        for name, expected in value['sources'].items():
            if hashlib.sha256(_source_path(name).read_bytes()).hexdigest() != expected:
                raise ValueError('actor support source changed')

    def invoke(self, payload: Any) -> Output:
        self.verify()
        original = canonical(payload)
        config = json.loads(self.description)['config']
        raw = None
        observed_runtime = None
        observations = None
        failure = None
        stated = Stated(None, None)
        try:
            produced = self.runner(json.loads(original), config)
            if isinstance(produced, RuntimeResult):
                raw = produced.raw
                observed_runtime = json.loads(canonical(produced.observed_runtime))
                observations = json.loads(canonical(produced.observations))
                if produced.failure:
                    raise ValueError(produced.failure)
                if not config.get('runtime_contract') or canonical(observed_runtime) != canonical(config['runtime_contract']):
                    raise ValueError('observed host runtime differs from the immutable invocation contract')
            else:
                raw = produced
                if (config.get('runtime_contract') or
                        config.get('purpose') != 'TEST_ONLY' and not config.get('capture_replay')):
                    raise ValueError('trusted host runtime observations required; response identity strings do not attest execution')
            if not isinstance(raw, bytes):
                raw = None
                raise ValueError('actor must retain raw output bytes')
            stated = self.parser(raw, json.loads(self.description)['config'])
            if not isinstance(stated, Stated):
                raise ValueError('actor parser must retain stated answer and actual basis')
            if config.get('task') in ('evolution', 'causal', 'gameplay', 'ethics'):
                from .task_inputs import verify_output
                verify_output(payload, stated)
            canonical({'answer': stated.answer, 'basis': stated.basis})
        except Exception as exc:  # an attempted item stays in the denominator, including parser failure
            failure = type(exc).__name__ + ': ' + str(exc)
            stated = Stated(None, None)
        if not isinstance(raw, bytes):
            raw = None
        self.verify()
        return Output(canonical({'actor_digest': self.digest, 'input_digest': hashlib.sha256(original).hexdigest(),
                                 'raw': base64.b64encode(raw or b'').decode(), 'raw_available': raw is not None,
                                 'failure': failure, 'observed_runtime': observed_runtime,
                                 'observations': observations,
                                 'answer': stated.answer, 'basis': stated.basis}))


@dataclass(frozen=True)
class Population:
    """Conserved case decisions, exposure and scope, frozen before an actor sees inputs.

    Current reference admission supports development only. Qualification needs a separately
    checked population review, never inferred from a case count or a model's display name.
    """
    description: bytes

    @classmethod
    def freeze(cls, metric: str, admissions: tuple[Admission, ...], envelope: dict[str, Any],
               exposure: dict[str, Any], *, held: tuple[Admission, ...] = ()) -> Population:
        return cls._freeze(metric, admissions, envelope, exposure, held, trace=False)

    @classmethod
    def held_development_trace(cls, metric: str, observations: tuple[Admission, ...],
                               envelope: dict[str, Any], exposure: dict[str, Any]) -> Population:
        """Report already exposed captures against retained proposed references, never qualify.

        Original hold decisions and proposed bases survive intact. The evaluator projection
        deliberately supplies no independently checked basis; its rate therefore stays null.
        """
        return cls._freeze(metric, observations, envelope, exposure, (), trace=True)

    @classmethod
    def _freeze(cls, metric: str, admissions: tuple[Admission, ...], envelope: dict[str, Any],
                exposure: dict[str, Any], held: tuple[Admission, ...], *, trace: bool) -> Population:
        if metric not in rss.METRICS or not admissions:
            raise ValueError('a supported metric and nonempty admitted population are required')
        packets = []
        for admission in admissions:
            packet = json.loads(admission.packet_bytes)
            if not trace and (not admission.admitted or not packet['admitted']):
                raise ValueError('held reference cannot enter selected population')
            if trace and (admission.admitted or packet['admitted']
                          or packet['requested_scope'].get('purpose') != 'development'):
                raise ValueError('held development observations required; no qualification admission')
            if packet['requested_scope']['metric'] != metric:
                raise ValueError('reference metric differs from population')
            packets.append(packet)
        ids = [packet['case']['id'] for packet in packets]
        inputs = [digest(packet['case']['input']) for packet in packets]
        if len(set(ids)) != len(ids) or len(set(inputs)) != len(inputs):
            raise ValueError('duplicate case or input cannot inflate a population')
        for name in ('adopters', 'domains', 'capabilities', 'frames', 'sources'):
            values = envelope.get(name)
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values):
                raise ValueError('nonempty applicability envelope required: ' + name)
        if date.fromisoformat(envelope['from']) > date.fromisoformat(envelope['until']):
            raise ValueError('applicability dates reversed')
        return cls(canonical({'metric': metric, 'selected': [] if trace else packets,
                              'observations': packets if trace else [], 'trace_only': trace,
                              'held': packets if trace else [json.loads(item.packet_bytes) for item in held],
                              'envelope': envelope, 'exposure': exposure,
                              'population_review': None}))

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.description).hexdigest()

    @property
    def metric(self) -> str:
        return str(json.loads(self.description)['metric'])

    @property
    def corpus(self) -> list[dict[str, Any]]:
        value = json.loads(self.description)
        rows = value['observations'] if value.get('trace_only') else value['selected']
        return [{**{key: row['case'][key] for key in ('id', 'input', 'expected')},
                 'basis': None if value.get('trace_only') else row['case']['basis']} for row in rows]

    @property
    def envelope(self) -> dict[str, Any]:
        return dict(json.loads(self.description)['envelope'])

    @property
    def qualification_admitted(self) -> bool:
        return False  # case admission is explicitly development-only; see PopulationReview


@dataclass(frozen=True)
class Capture:
    packet: bytes
    authentication: bytes = field(repr=False, default=b'')
    _group: Any = field(default=None, repr=False, compare=False)
    _core: Any = field(default=None, repr=False, compare=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.packet).hexdigest()


@dataclass(frozen=True)
class PopulationReview:
    """A separate custodian decision, checked by a host-selected authority adapter.

    This does not widen reference_cases' development admission. The retained review must
    explicitly reassess this entire population's rights, split, authority and applicability.
    A checker's own provenance is part of the selection; a model cannot select that checker.
    """
    record: bytes
    checker: Callable[[bytes, Population], bool] | None
    checker_identity: bytes

    @classmethod
    def freeze(cls, population: Population, record: bytes,
               checker: Callable[[bytes, Population], bool]) -> PopulationReview:
        path = Path(inspect.getfile(checker)).resolve()
        return cls(bytes(record), checker, canonical({'callable': _callable_identity(checker),
            'path': _source_name(path), 'source': hashlib.sha256(path.read_bytes()).hexdigest(),
            'population': population.digest}))

    @classmethod
    def test_only(cls, population: Population) -> PopulationReview:
        """Explicit fabricated positive control; unavailable to default operational resolution."""
        return cls(canonical({'schema': 'TEST_ONLY-qualification-mechanics',
                              'population_digest': population.digest}), None, b'')

    @property
    def digest(self) -> str:
        return digest({'record': base64.b64encode(self.record).decode(),
                       'checker': base64.b64encode(self.checker_identity).decode()})

    def reasons(self, population: Population, *, allow_test_only: bool, actor: Actor) -> list[str]:
        value = json.loads(self.record)
        if value.get('population_digest') != population.digest:
            return ['population review names a different population']
        if value.get('schema') == 'TEST_ONLY-qualification-mechanics':
            if allow_test_only and json.loads(actor.description)['config'].get('purpose') == 'TEST_ONLY':
                return []
            return ['TEST_ONLY review cannot authorise an operational actor']
        reasons = []
        identity = json.loads(self.checker_identity)
        if (self.checker is None or _callable_identity(self.checker) != identity['callable']
                or hashlib.sha256(_source_path(identity['path']).read_bytes()).hexdigest() != identity['source']
                or not self.checker(self.record, population)):
            return ['population review authority was not established by the host checker']
        if value.get('schema') != 'twin.population-review/v1' or value.get('decision') != 'admitted':
            reasons.append('population review did not admit qualification')
        for name in ('issuer', 'authority', 'reference_authority', 'rights', 'limitations'):
            if not value.get(name):
                reasons.append('population review omits ' + name)
        pop = json.loads(population.description)
        groups = {row['case']['group'] for row in pop['selected']}
        split = value.get('source_family_split', {})
        if (set(split.get('qualification_groups', [])) != groups
                or groups & set(split.get('development_groups', []))):
            reasons.append('population source-family split is missing or overlaps development')
        if set(value.get('coverage', [])) != set(population.envelope['adopters']):
            reasons.append('qualification review must account for every covered adopter')
        if set(population.envelope['adopters']) != {'driftwood', 'tuppence', 'ludlow'}:
            reasons.append('estate qualification must account for all three adopters')
        exposure = pop['exposure']
        if exposure.get('status') != 'held-out' or not exposure.get('history') or not exposure.get('training_provenance'):
            reasons.append('explicit held-out exposure/history and disclosed training provenance required')
        for row in pop['selected']:
            case = row['case']
            if case['exposure'].get('status') != 'held-out' or 'qualification' not in case['rights'].get('uses', []):
                reasons.append('case exposure or rights do not support qualification: ' + case['id'])
        return reasons


def project_reference(metric: str, expected: Any) -> Any:
    """Shape supported labels for the existing scorer; no candidate predictions enter here."""
    if metric == 'signal-classify':
        return {'steep': expected['steep'], 'claim': {'component': expected['component']}}
    if metric == 'evolution-judge':
        return {'evolution_position': expected['evolution_position']}
    if metric in ('causal-claims', 'causal-claims-grade-accuracy'):
        return {'edge': {**({'sign': expected['sign'], 'lag_days': expected['lag_days'],
                           'elasticity': {'mode': expected['elasticity_mode']}}
                          if metric == 'causal-claims' else {}),
                         **({'evidence_grade': expected['evidence_grade']}
                            if 'evidence_grade' in expected else {})}}
    if metric == 'gameplay-lens':
        return {'opportunities': [{'play': play, 'component': component}
                                 for play, component in expected['opportunities']]}
    if metric == 'ethics-gate':
        return {'admitted': expected['admitted'], 'ladder': {'stopped_at': expected['stopped_at']}}
    if metric == 'substrate-generator':
        # A declared constraint's scorer-shaped witness, not a claim to realistic generation.
        channels = expected['channels']
        plants = [{'signal': signal} for signal in expected['planted_signals']]
        floor = expected['min_mundane_fraction']
        if not channels:
            raise ValueError('reference projection needs a channel for its witnesses')
        if floor >= 1 and plants:
            raise ValueError('reference projection cannot meet a unit mundane floor with plants')
        lines = max(1, int(len(plants) / max(1 - floor, 1e-12)) + 1)
        signals = set(expected['planted_signals'])
        mundane = 'reference constraint witness'
        while mundane in signals:
            mundane += '.'
        # A fresh decoration prevents a signal which already has a prefix from also
        # crediting another declared signal. Its identity carries no graded meaning.
        prefix = 'reference'
        while any(signal.startswith(f'[{prefix}] ') for signal in signals):
            prefix += '.'
        bodies = {channel: [mundane] * lines for channel in channels}
        for index, plant in enumerate(plants):
            channel = channels[index % len(channels)]
            plant.update(channel=channel, index=len(bodies[channel]))
            bodies[channel].append(f'[{prefix}] {plant["signal"]}')
        return {'channels': bodies, 'plants': plants}
    raise ValueError('unsupported reference metric')


@dataclass(frozen=True)
class Selection:
    actor: Actor
    population: Population
    basis_checker: Callable[[Any, Any], bool]
    reference_projection: Callable[[str, Any], Any]
    description: bytes
    _capture_key: bytes = field(repr=False, compare=False)
    review: PopulationReview | None = None
    assessment_policy: BasisPolicy | None = None
    _metadata_store: Any = field(default=None, repr=False, compare=False)
    _metadata_policy: bytes | None = field(default=None, repr=False, compare=False)
    _test_only: TestOnlyPurpose | None = field(default=None, repr=False, compare=False)
    _task_contract: Any = field(default=None, repr=False, compare=False)
    _task_policy: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def freeze(cls, actor: Actor, population: Population,
               basis_checker: Callable[[Any, Any], bool], *,
               reference_projection: Callable[[str, Any], Any] = project_reference,
               review: PopulationReview | None = None,
               assessment_policy: BasisPolicy | None = None,
               source_metadata_policy: dict[str, Any] | None = None, metadata_store: Any = None,
               test_only: TestOnlyPurpose | None = None, task_contract: Any = None,
               task_policy: Any = None) -> Selection:
        identity = _callable_identity(basis_checker)
        functions = (basis_checker, reference_projection, rss.scorer_for(population.metric))
        sources = {_source_name(Path(inspect.getfile(fn))): hashlib.sha256(
            Path(inspect.getfile(fn)).read_bytes()).hexdigest() for fn in functions}
        if population.metric == 'substrate-generator':
            from . import substrate_generation, substrate_recipe_basis
            if basis_checker is not substrate_recipe_basis.check or reference_projection is not project_reference:
                raise ValueError('generator requires the reviewed independent checker and approved reference projection')
            substrate_generation.validate_population(actor, population)
            for module in (substrate_generation, substrate_recipe_basis):
                path = Path(inspect.getfile(module))
                sources[_source_name(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        description = {'actor': actor.digest, 'population': population.digest,
                              'basis_checker': identity, 'projection': _callable_identity(reference_projection),
                              'sources': sources, 'review': review.digest if review else None}
        if test_only is not None:
            if (test_only is not TEST_ONLY_MECHANICS or json.loads(actor.description)['config'].get('purpose') != 'TEST_ONLY'
                    or source_metadata_policy is not None or metadata_store is not None):
                raise ValueError('legacy selection requires protected TEST_ONLY actor purpose')
            description['purpose'] = test_only.value
        if assessment_policy:
            assessment_policy.verify()
            description['assessment_policy'] = json.loads(assessment_policy.description)
        from .task_contracts import METRIC_TASK, validate
        if population.metric in METRIC_TASK and test_only is not TEST_ONLY_MECHANICS:
            from .task_inputs import support_sources, reference_row
            if task_contract is None or task_policy is None:
                raise ValueError('registered metric requires independently selected protected task contract/policy')
            task_contract.verify(); task_policy.verify()
            config = json.loads(actor.description)['config']
            if (task_contract.task != METRIC_TASK[population.metric]
                    or task_policy.contract.description != task_contract.description
                    or config.get('task') != task_contract.task or config.get('task_contract_digest') != task_contract.digest):
                raise ValueError('actor/metric/protected task contract differs')
            actor_sources = json.loads(actor.description)['sources']
            for path in support_sources():
                pin = hashlib.sha256(path.read_bytes()).hexdigest()
                if actor_sources.get(_source_name(path)) != pin:
                    raise ValueError('task actor lacks exact constructor/rubric/metadata/schema support identity')
                sources[_source_name(path)] = pin
            if (assessment_policy is None or json.loads(assessment_policy.description).get('schema') != 'twin.basis-policy/v2'
                    or json.loads(assessment_policy.description).get('metric') != population.metric
                    or json.loads(assessment_policy.description).get('contract') != task_contract.digest):
                raise ValueError('registered task requires its exact independently acquired task rubric')
            validate('Envelope', population.envelope)
            policy_value = json.loads(task_policy.description)
            if policy_value['contexts'] != population.envelope['task_contexts']:
                raise ValueError('qualified task context differs from actual protected model/party/universe/policy')
            for packet in json.loads(population.description)['selected']:
                row = reference_row(packet['case'])
                task_policy.verify_input(row)
                if _scope_reasons(population, row['context']):
                    raise ValueError('qualification task input lies outside declared scope/source families')
            description['task_contract'] = json.loads(task_contract.description)
            description['task_policy'] = policy_value
        elif task_contract is not None or task_policy is not None:
            raise ValueError('task contract handles cannot replace metric or protected TEST_ONLY mechanics')
        if population.metric == 'signal-classify' and (test_only is not TEST_ONLY_MECHANICS or assessment_policy is not None):
            from .signal_inputs import binding_context
            from . import source_metadata as sm
            if test_only is not TEST_ONLY_MECHANICS:
                sm.validate_parent_policy(source_metadata_policy, metadata_store)
                assert source_metadata_policy is not None
                authority = metadata_store.authority(source_metadata_policy['authority_digest'])
                if (json.loads(actor.description).get('source_metadata_authority') != json.loads(authority.description)
                        or source_metadata_policy['purpose'] == 'TEST_ONLY'
                        and json.loads(actor.description)['config'].get('purpose') != 'TEST_ONLY'):
                    raise ValueError('signal actor lacks exact protected metadata authority/support identity')
                description['source_metadata_policy'] = source_metadata_policy
                for path in (*[_source_path(path) for path in json.loads(authority.description)['sources']],
                             Path(sm.__file__), sm.SCHEMA_PATH):
                    sources[_source_name(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            envelope = population.envelope
            contexts = envelope.get('signal_contexts', {})
            if (set(contexts) != set(envelope['adopters'])
                    or any(not isinstance(value, dict) or set(value) != {
                        'candidate_universe_digest', 'model_pins', 'model_as_of',
                        'input_construction_sha256'} for value in contexts.values())):
                raise ValueError('reviewed signal selection requires every adopter exact model/universe/construction context')
            for packet in json.loads(population.description)['selected']:
                case = packet['case']
                try:
                    actual = binding_context(case['input'], test_only=test_only)
                    if test_only is not TEST_ONLY_MECHANICS:
                        sm.verify_host_metadata(case, metadata_store, source_metadata_policy)
                    model = case['input']['model_context']
                    if (actual != contexts.get(case['context']['organisation'])
                            or any(model[field] != case['context'][field]
                                   for field in ('organisation', 'domain', 'capability', 'frame'))
                            or any(model[field] not in envelope[allowed] for field, allowed in (
                                ('domain', 'domains'), ('capability', 'capabilities'), ('frame', 'frames')))
                            or case['input']['source_context']['family'] not in envelope['sources']
                            or case['input']['source_context']['as_of'] != case['context']['as_of']
                            or not date.fromisoformat(envelope['from']) <= date.fromisoformat(case['context']['as_of'])
                                <= date.fromisoformat(envelope['until'])):
                        raise ValueError('model/universe/date/construction or declared scope differs')
                except (ValueError, KeyError, TypeError) as exc:
                    raise ValueError('qualification input differs from qualified signal context: ' + str(exc)) from exc
            source = Path(inspect.getfile(binding_context))
            sources[_source_name(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
        return cls(actor, population, basis_checker, reference_projection,
                   canonical(description), secrets.token_bytes(32), review, assessment_policy,
                   metadata_store, canonical(source_metadata_policy) if source_metadata_policy else None, test_only,
                   task_contract, task_policy)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.description).hexdigest()

    def verify(self) -> None:
        self.actor.verify()
        if self.assessment_policy:
            self.assessment_policy.verify()
        value = json.loads(self.description)
        if value.get('purpose') != (self._test_only.value if self._test_only else None):
            raise ValueError('selection requires original protected TEST_ONLY purpose')
        if value.get('source_metadata_policy') != (json.loads(self._metadata_policy) if self._metadata_policy else None):
            raise ValueError('selection requires original protected metadata policy')
        from .task_contracts import METRIC_TASK
        if self.population.metric in METRIC_TASK and self._test_only is not TEST_ONLY_MECHANICS:
            rebound = Selection.freeze(self.actor, self.population, self.basis_checker,
                reference_projection=self.reference_projection, review=self.review,
                assessment_policy=self.assessment_policy, task_contract=self._task_contract, task_policy=self._task_policy)
            if rebound.description != self.description:
                raise ValueError('selection requires original protected task model/source/policy handles')
        if self.population.metric == 'signal-classify' and self._test_only is not TEST_ONLY_MECHANICS:
            # Reapply the mandatory constructor/acquisition/actor invariants using the
            # retained protected handles, including for restored public descriptions.
            rebound = Selection.freeze(self.actor, self.population, self.basis_checker,
                reference_projection=self.reference_projection, review=self.review,
                assessment_policy=self.assessment_policy, metadata_store=self._metadata_store,
                source_metadata_policy=json.loads(self._metadata_policy) if self._metadata_policy else None)
            if rebound.description != self.description:
                raise ValueError('selection protected metadata/construction binding changed')
        elif self._metadata_policy:
            from .source_metadata import verify_host_metadata
            for packet in json.loads(self.population.description)['selected']:
                verify_host_metadata(packet['case'], self._metadata_store, json.loads(self._metadata_policy))
        if (value['actor'] != self.actor.digest or value['population'] != self.population.digest
                or value['basis_checker'] != _callable_identity(self.basis_checker)
                or value['projection'] != _callable_identity(self.reference_projection)
                or value['review'] != (self.review.digest if self.review else None)
                or value.get('assessment_policy') != (json.loads(self.assessment_policy.description)
                                                       if self.assessment_policy else None)):
            raise ValueError('selection or basis checker changed')
        if any(hashlib.sha256(_source_path(path).read_bytes()).hexdigest() != expected
               for path, expected in value['sources'].items()):
            raise ValueError('selection support source changed')

    def verify_input(self, row: dict[str, Any]) -> None:
        """Recompute the complete live signal binding for the selected task."""
        self.verify()
        from .task_contracts import METRIC_TASK
        if self.population.metric in METRIC_TASK and self._test_only is not TEST_ONLY_MECHANICS:
            self._task_policy.verify_input(row)
            if _scope_reasons(self.population, row['context']):
                raise ValueError('task input is outside qualified model/source/date/target scope')
        if self.population.metric == 'signal-classify' and self._test_only is not TEST_ONLY_MECHANICS:
            from .signal_inputs import binding_context
            from .source_metadata import verify_host_metadata
            verify_host_metadata(row, self._metadata_store,
                json.loads(self._metadata_policy) if self._metadata_policy else None)
            try:
                actual = binding_context(row['input'])
                context = row['context']
                model, source = row['input']['model_context'], row['input']['source_context']
                qualified = self.population.envelope['signal_contexts'].get(context['organisation'])
                if (actual != qualified or any(context.get(key) != value for key, value in actual.items())
                        or context.get('eligible_components') != [item['id'] for item in row['input']['candidates']]
                        or 'component' in context
                        or any(model[key] != context[key] for key in ('organisation', 'domain', 'capability', 'frame'))
                        or source['family'] != context['source'] or source['as_of'] != context['as_of']
                        or _scope_reasons(self.population, context)):
                    raise ValueError('actual model/universe/date/construction or declared scope differs')
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError('live input differs from qualified signal context: ' + str(exc)) from exc

    def capture(self) -> Capture:
        self.verify()
        if self._task_contract is not None and self._task_contract.task == 'causal':
            raise ValueError('registered causal task requires authenticated paired CaptureGroup')
        rows = []
        for item in self.population.corpus:
            output = self.actor.invoke(item['input'])
            rows.append({'id': item['id'], 'output': json.loads(output.packet)})
        packet = canonical({'selection': self.digest, 'rows': rows})
        return Capture(packet, hmac.digest(self._capture_key, packet, 'sha256'))

    def _capture_rows(self, capture: Capture) -> list[dict[str, Any]]:
        if capture._group is not None:
            return capture._group._rows(self, capture)
        if capture._core is not None:
            raise ValueError('capture core requires original authenticated group membership')
        if self._task_contract is not None and self._task_contract.task == 'causal':
            raise ValueError('registered causal capture requires original authenticated group core')
        value = json.loads(capture.packet)
        if value.get('selection') != self.digest:
            raise ValueError('capture belongs to a different selection')
        if not hmac.compare_digest(capture.authentication, hmac.digest(self._capture_key, capture.packet, 'sha256')):
            raise ValueError('host capture authentication failed')
        return value['rows']

    def captured_outputs(self, capture: Capture) -> list[Stated]:
        """Verify actual host capture before constructing a reviewer-visible projection."""
        self.verify()
        corpus = self.population.corpus
        rows = self._capture_rows(capture)
        if [row['id'] for row in rows] != [item['id'] for item in corpus]:
            raise ValueError('capture must cover exact ordered population')
        outputs = []
        for row, item in zip(rows, corpus):
            output = row['output']
            if (output['actor_digest'] != self.actor.digest or output['input_digest'] != digest(item['input'])):
                raise ValueError('capture actor or input changed')
            raw = base64.b64decode(output['raw'], validate=True)
            if output.get('failure'):
                if output['answer'] is not None or output['basis'] is not None:
                    raise ValueError('failed host capture cannot invent an answer or basis')
                stated = Stated(None, None)
            else:
                config = json.loads(self.actor.description)['config']
                if config.get('runtime_contract') and output.get('observed_runtime') != config['runtime_contract']:
                    raise ValueError('capture host runtime differs from the immutable contract')
                stated = self.actor.parser(raw, json.loads(self.actor.description)['config'])
                if self._task_contract is not None:
                    from .task_inputs import verify_output
                    verify_output(item['input'], stated)
            if canonical({'answer': stated.answer, 'basis': stated.basis}) != canonical({
                    'answer': output['answer'], 'basis': output['basis']}):
                raise ValueError('capture raw output and stated answer differ')
            outputs.append(stated)
        return outputs

    def assessment_request(self, capture: Capture) -> bytes:
        self.captured_outputs(capture)
        if self.assessment_policy is None:
            raise ValueError('selection has no independent assessment policy')
        rows = self._capture_rows(capture)
        packets = json.loads(self.population.description)
        original = packets['observations'] if packets.get('trace_only') else packets['selected']
        return canonical({'schema': 'twin.basis-request/v1', 'policy': self.assessment_policy.digest,
            **self.binding(capture), 'rows': [{'id': row['id'], 'input': packet['case']['input'],
                'context': packet['case']['context'], 'sources': packet['case']['sources'],
                'output': row['output']}
                for row, packet in zip(rows, original)]})

    def evaluate(self, capture: Capture, assessment: BasisAssessment | None = None) -> EvalResult:
        outputs = self.captured_outputs(capture)
        if self.assessment_policy:
            if assessment is None:
                raise ValueError('exact independent semantic assessment is required')
            assessment.verify(self.assessment_policy, self.assessment_request(capture))
        elif assessment is not None:
            raise ValueError('assessment cannot replace an unfrozen policy')
        stream = iter(outputs)
        scorer = rss.scorer_for(self.population.metric)
        def valid_answer(actual: Any, expected: Any) -> bool:
            if actual is None:
                return False
            try:
                return bool(scorer(actual, expected))
            except (KeyError, TypeError, AttributeError, ValueError, OverflowError):
                return False
        def assessed_basis(item_id: str, actual: Stated, reference: Any) -> bool | None:
            if assessment is None:
                raise ValueError('independent assessment missing')
            if self.population.metric == 'signal-classify':
                from .signal_candidate import quote_integrity
                item = next(item for item in self.population.corpus if item['id'] == item_id)
                if not quote_integrity(actual, item['input']):
                    return False
            return assessment.outcome(item_id)
        return evaluate(self.population.metric, lambda _: next(stream), self.population.corpus,
                        scorer=valid_answer, basis_scorer=self.basis_checker,
                        contextual_basis_scorer=assessed_basis if assessment else None)

    def facts(self, capture: Capture, assessment: BasisAssessment | None = None) -> dict[str, Any]:
        result = self.evaluate(capture, assessment)
        corpus = self.population.corpus
        metric = self.population.metric
        scorer = rss.scorer_for(metric)
        references = [self.reference_projection(metric, item['expected']) for item in corpus]
        if any(not mp.scores_item(scorer, answer, item['expected']) for answer, item in zip(references, corpus)):
            raise ValueError('reference projection must score correctly before baseline derivation')
        baseline = mp.frozen_field_baseline(references, corpus, scorer)
        answers = [row['output']['answer'] for row in self._capture_rows(capture)]
        variance = mp.answer_variance(answers, baseline.reads)
        return {'skill': metric, 'model_version': self.actor.model_version,
                'reference_admission': 'held development trace' if json.loads(self.population.description).get('trace_only')
                                       else 'development case admission; population review separate',
                'selection_digest': self.digest, 'population_digest': self.population.digest,
                'capture_digest': capture.digest, 'actor_digest': self.actor.digest,
                'assessment_digest': assessment.digest if assessment else None,
                'corpus_digest': digest_of(corpus), 'reference_score': 1.0,
                'baseline': baseline, 'variance': variance, 'evaluation': result,
                'readings': tuple(mp.HeadReading(self.actor.model_version, name, len(answers), distinct,
                                                'capture:' + capture.digest)
                                  for name, distinct in variance.items())}

    def binding(self, capture: Capture, assessment: BasisAssessment | None = None) -> dict[str, str]:
        value = {'selection_digest': self.digest, 'population_digest': self.population.digest,
                'capture_digest': capture.digest, 'actor_digest': self.actor.digest}
        if assessment:
            value['assessment_digest'] = assessment.digest
        return value

    def record(self, capture: Capture, recorded_at: str, path: Path,
               assessment: BasisAssessment | None = None) -> dict[str, Any]:
        """Append one complete host-bound row; no official destination is implicit."""
        if (self._test_only is TEST_ONLY_MECHANICS or json.loads(self.actor.description)['config'].get('purpose') == 'TEST_ONLY'
                or self._metadata_policy and json.loads(self._metadata_policy)['purpose'] == 'TEST_ONLY') and path.resolve() == Path(__file__).with_name('skill-scores.jsonl').resolve():
            raise ValueError('TEST_ONLY mechanics cannot record official scores')
        result = self.evaluate(capture, assessment)
        self.facts(capture, assessment)  # invalid reference projection must not produce an official row
        return record_score(result, self.actor.model_version, recorded_at, path,
                            binding=self.binding(capture, assessment))

    def archive(self, capture: Capture, assessment: BasisAssessment | None = None) -> bytes:
        """Export public evidence without the ephemeral host key.

        Export alone does not authorise later import. A protected, reviewed catalogue must
        independently pin these exact bytes before a later verifier can rebind the capture.
        """
        self.evaluate(capture, assessment)
        return canonical({'schema': 'twin.qualification-bundle/v1',
            'actor': json.loads(self.actor.description), 'population': json.loads(self.population.description),
            'selection': json.loads(self.description), 'capture': json.loads(capture.packet),
            'assessment': json.loads(assessment.packet) if assessment else None,
            'review': {'record': base64.b64encode(self.review.record).decode(),
                       'checker_identity': base64.b64encode(self.review.checker_identity).decode()}
                      if self.review else None})


@dataclass(frozen=True)
class GroupCapture:
    packet: bytes
    authentication: bytes = field(repr=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.packet).hexdigest()


def _neutral_population(population: Population) -> dict[str, Any]:
    value = json.loads(population.description)
    if value.get('trace_only'):
        raise ValueError('held development traces cannot become paired causal proof')
    rows = []
    for packet in value['selected']:
        case = packet['case']
        scope = {key: child for key, child in packet['requested_scope'].items() if key != 'metric'}
        context = {key: child for key, child in case['context'].items() if key != 'metric'}
        rows.append({'scope': scope, **{key: case[key] for key in (
            'id', 'group', 'input', 'reference_kind', 'sources', 'rights', 'selection', 'exposure', 'limitations')},
            'context': context})
    return {'rows': rows, 'envelope': value['envelope'], 'exposure': value['exposure'], 'held': value['held']}


@dataclass(frozen=True)
class CaptureGroup:
    description: bytes
    selections: tuple[Selection, Selection] = field(repr=False)
    _capture_key: bytes = field(repr=False)

    @classmethod
    def freeze(cls, selections: tuple[Selection, ...]) -> CaptureGroup:
        metrics = ('causal-claims', 'causal-claims-grade-accuracy')
        if len(selections) != 2 or {item.population.metric for item in selections} != set(metrics):
            raise ValueError('causal capture requires exactly quantity and grade selections')
        pair = tuple(next(item for item in selections if item.population.metric == metric) for metric in metrics)
        first, second = pair
        for selected in pair:
            selected.verify()
        legacy = all(item._test_only is TEST_ONLY_MECHANICS for item in pair)
        contracts = [json.loads(item.description).get('task_contract') for item in pair]
        if (first.actor.digest != second.actor.digest or contracts[0] != contracts[1]
                or not legacy and contracts[0] is None
                or canonical(_neutral_population(first.population)) != canonical(_neutral_population(second.population))):
            raise ValueError('causal group actor/task/ordered input/target/source/custody/exposure/scope differs')
        description = canonical({'schema': 'twin.capture-group/v1', 'actor_digest': first.actor.digest,
            'task_contract_digest': digest(contracts[0]) if contracts[0] else digest({'purpose': TEST_ONLY_MECHANICS.value}),
            'ordered_batch_digest': digest(_neutral_population(first.population)),
            'allowed_selection_digests': [item.digest for item in pair]})
        return cls(description, (first, second), secrets.token_bytes(32))

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.description).hexdigest()

    def verify(self) -> None:
        if self.description != self.freeze(self.selections).description:
            raise ValueError('causal group membership or support binding changed')

    def capture(self) -> GroupCapture:
        self.verify()
        rows = []
        for item in self.selections[0].population.corpus:
            output = self.selections[0].actor.invoke(item['input'])
            rows.append({'id': item['id'], 'target_digest': digest(item['input'].get('target')),
                         'attempt_id': secrets.token_hex(24), 'output': json.loads(output.packet)})
        packet = canonical({'schema': 'twin.invocation-capture/v1', 'group_digest': self.digest,
            'actor_digest': self.selections[0].actor.digest,
            'batch_digest': json.loads(self.description)['ordered_batch_digest'], 'rows': rows})
        return GroupCapture(packet, hmac.digest(self._capture_key, packet, 'sha256'))

    def _verify_capture(self, capture: GroupCapture) -> dict[str, Any]:
        self.verify()
        if not hmac.compare_digest(capture.authentication, hmac.digest(self._capture_key, capture.packet, 'sha256')):
            raise ValueError('group capture was not invoked by the protected host')
        core = json.loads(capture.packet)
        corpus = self.selections[0].population.corpus
        if (core['schema'] != 'twin.invocation-capture/v1' or core['group_digest'] != self.digest
                or core['actor_digest'] != self.selections[0].actor.digest
                or core['batch_digest'] != json.loads(self.description)['ordered_batch_digest']
                or [row['id'] for row in core['rows']] != [item['id'] for item in corpus]
                or len({row['attempt_id'] for row in core['rows']}) != len(corpus)
                or any(row['target_digest'] != digest(item['input'].get('target')) for row, item in zip(core['rows'], corpus))):
            raise ValueError('group raw core differs from exact frozen membership/batch')
        return core

    def view(self, selection: Selection, capture: GroupCapture) -> Capture:
        core = self._verify_capture(capture)
        if selection.digest not in [item.digest for item in self.selections]:
            raise ValueError('selection is outside frozen causal group')
        packet = canonical({'schema': 'twin.group-capture-view/v1', 'selection_digest': selection.digest,
            'group_digest': capture.digest, 'row_refs': [{'id': row['id'], 'index': index} for index, row in enumerate(core['rows'])]})
        return Capture(packet, hmac.digest(selection._capture_key, packet + capture.packet, 'sha256'), self, capture)

    def archive(self, capture: GroupCapture, assessments: dict[str, BasisAssessment] | None = None) -> bytes:
        self._verify_capture(capture)
        assessments = assessments or {}
        if set(assessments) != {selected.population.metric for selected in self.selections if selected.assessment_policy}:
            raise ValueError('group archive requires every independent metric assessment')
        members = [json.loads(selected.archive(self.view(selected, capture), assessments.get(selected.population.metric)))
                   for selected in self.selections]
        return canonical({'schema': 'twin.qualification-group-bundle/v1', 'group': json.loads(self.description),
                          'core': json.loads(capture.packet), 'members': members})

    def _rows(self, selection: Selection, view: Capture) -> list[dict[str, Any]]:
        if view._group is not self or not isinstance(view._core, GroupCapture):
            raise ValueError('group view requires original protected core')
        expected = self.view(selection, view._core)
        if view.packet != expected.packet or not hmac.compare_digest(view.authentication, expected.authentication):
            raise ValueError('causal view membership/raw core authentication changed')
        return [{'id': row['id'], 'output': row['output']} for row in json.loads(view._core.packet)['rows']]


def _refuse(permission: mp.Permission, item: int, detail: str) -> mp.Permission:
    old = next(condition for condition in permission.conditions if condition.item == item)
    return mp.Permission(permission.skill, permission.model_version, tuple(
        mp.Condition(condition.item, condition.name, False, detail) if condition is old else condition
        for condition in permission.conditions))


class Resolver:
    """The same host registry resolves recording, validation and public verification facts.

    Only the incumbent receives historical mechanism facts. An unregistered actor cannot
    borrow them. TEST_ONLY registries are explicit test controls and never the default.
    """
    def __init__(self, bindings: tuple[tuple[Selection, Capture] | tuple[Selection, Capture, BasisAssessment], ...] = (),
                 scores_path: Path | None = None, *, allow_test_only: bool = False):
        self._bindings = {(bound[0].population.metric, bound[0].actor.model_version): (bound[0], bound[1])
                          for bound in bindings}
        self._assessments = {(bound[0].population.metric, bound[0].actor.model_version): bound[2]
                             for bound in bindings if len(bound) == 3}
        if len(self._bindings) != len(bindings):
            raise ValueError('one current selection/capture per actor and metric is required')
        self._scores_path = scores_path
        self._allow_test_only = allow_test_only
        self._facts: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._sessions: dict[str, HostSession] = {}
        self._task_policies: dict[str, Any] = {}
        self._groups: dict[str, CaptureGroup] = {}
        for selected, captured in self._bindings.values():
            if selected._task_policy is not None:
                self._task_policies[selected._task_policy.digest] = selected._task_policy
            if selected._task_contract is not None and selected._task_contract.task == 'causal':
                if not isinstance(captured._group, CaptureGroup):
                    raise ValueError('registered causal binding requires both authenticated group views')
                group = captured._group
                if any((member.population.metric, member.actor.model_version) not in self._bindings
                       or self._bindings[(member.population.metric, member.actor.model_version)][1]._group is not group
                       for member in group.selections):
                    raise ValueError('ordinary single-metric causal registration is forbidden')
                self._groups[selected.actor.model_version] = group

    @classmethod
    def from_catalogue(cls, catalogue: Path, expected_digest: str, scores_path: Path | None = None,
                       *, allow_test_only: bool = False, metadata_store: Any = None,
                       source_metadata_policy: dict[str, Any] | None = None,
                       task_policies: dict[str, Any] | None = None) -> Resolver:
        """Import a durable host snapshot, not a model-provided path or checksum.

        The caller must obtain expected_digest from its protected source/configuration before
        starting the model child. CLI claim validation exposes no catalogue/path override.
        The normal entrypoint below reads its versioned judge checkout, never claim output.
        """
        raw = catalogue.read_bytes()
        if catalogue.is_symlink() or hashlib.sha256(raw).hexdigest() != expected_digest:
            raise ValueError('protected catalogue digest differs')
        document = json.loads(raw)
        if document.get('schema') != 'twin.qualification-registry/v1':
            raise ValueError('unknown host catalogue schema')
        bindings = []
        for entry in document['entries']:
            path = catalogue.parent / entry['bundle']
            if path.is_symlink() or not path.resolve().is_relative_to(catalogue.parent.resolve()):
                raise ValueError('bundle escapes protected catalogue')
            bundle = path.read_bytes()
            if hashlib.sha256(bundle).hexdigest() != entry['sha256']:
                raise ValueError('protected bundle digest differs')
            if json.loads(bundle).get('schema') == 'twin.qualification-group-bundle/v1':
                bindings.extend(_restore_group_bundle(bundle, metadata_store=metadata_store,
                    source_metadata_policy=source_metadata_policy, task_policies=task_policies,
                    test_only=TEST_ONLY_MECHANICS if allow_test_only else None))
            else:
                bindings.append(_restore_bundle(bundle, metadata_store=metadata_store,
                    source_metadata_policy=source_metadata_policy, task_policies=task_policies,
                    test_only=TEST_ONLY_MECHANICS if allow_test_only else None))
        resolver = cls(tuple(bindings), scores_path, allow_test_only=allow_test_only)
        for key, policy in (task_policies or {}).items():
            policy.verify()
            if key != policy.digest:
                raise ValueError('protected task policy lookup digest differs')
            resolver._task_policies[key] = policy
        for entry in document.get('sessions', []):
            path = catalogue.parent / entry['bundle']
            if path.is_symlink() or not path.resolve().is_relative_to(catalogue.parent.resolve()):
                raise ValueError('session bundle escapes protected catalogue')
            session_bytes = path.read_bytes()
            if hashlib.sha256(session_bytes).hexdigest() != entry['sha256']:
                raise ValueError('protected session bundle digest differs')
            legacy = json.loads(session_bytes).get('inputs', {}).get('purpose')
            session = HostSession.restore(session_bytes, resolver, metadata_store=metadata_store,
                metadata_policy=source_metadata_policy,
                test_only=TEST_ONLY_MECHANICS if allow_test_only and legacy else None,
                task_policy=(task_policies or {}).get(digest(json.loads(session_bytes)['inputs']['task_policy']))
                    if 'task_policy' in json.loads(session_bytes)['inputs'] else None)
            if session.identity in resolver._sessions:
                raise ValueError('duplicate host session')
            resolver._sessions[session.identity] = session
        return resolver

    @classmethod
    def from_checkout(cls, scores_path: Path | None = None) -> Resolver:
        """Only the current protected judge package supplies operational registrations."""
        path = Path(__file__).with_name('qualification-registry.json')
        snapshot = path.read_bytes()
        return cls.from_catalogue(path, hashlib.sha256(snapshot).hexdigest(), scores_path)

    def permission(self, metric: str, model_version: str) -> mp.Permission:
        rows = load_scores(self._scores_path)
        bound = self._bindings.get((metric, model_version))
        if bound is None and model_version == rss.HEURISTIC_MODEL_VERSION:
            facts = rss.corpus_facts(metric)
            return mp.permission_for(metric, model_version, scores=rows,
                corpus_digest_now=facts['corpus_digest'], threshold_now=threshold_for(metric),
                min_items_now=min_items_for(metric), baseline=facts['baseline'], variance=facts['variance'],
                readings=mp.load_head_readings(), fitted_models=rss.fitted_models())
        if bound is None:
            permission = mp.permission_for(metric, model_version, scores=[], corpus_digest_now='',
                threshold_now=threshold_for(metric), min_items_now=min_items_for(metric),
                baseline=None, variance=None, seam_crossed=False)
            return _refuse(permission, 10, 'no host-registered actor/population/exposure binding')
        selected, capture = bound
        assessment = self._assessments.get((metric, model_version))
        try:
            selected.evaluate(capture, assessment)  # verify current sources/runtime/capture/assessment on cache hits
            key = (selected.digest, capture.digest, assessment.digest if assessment else '')
            if key not in self._facts:
                self._facts[key] = selected.facts(capture, assessment)
            facts = self._facts[key]
        except (ValueError, OSError, KeyError, TypeError) as exc:
            permission = mp.permission_for(metric, model_version, scores=[], corpus_digest_now='',
                threshold_now=threshold_for(metric), min_items_now=min_items_for(metric),
                baseline=None, variance=None, seam_crossed=False)
            return _refuse(permission, 2, 'current host selection/capture failed verification: ' + str(exc))
        permission = mp.permission_for(metric, model_version, scores=rows,
            corpus_digest_now=facts['corpus_digest'], threshold_now=threshold_for(metric),
            min_items_now=min_items_for(metric), baseline=facts['baseline'], variance=facts['variance'],
            readings=facts['readings'], fitted_models={})
        latest = mp.newest_score(metric, model_version, rows)
        result = facts['evaluation']
        if (latest is None or latest.get('qualification') != selected.binding(capture, assessment)
                or any(latest.get(name) != value for name, value in {
                    'score': result.score, 'attributable_rate': result.attributable_rate,
                    'measured_count': result.measured_count, 'total': len(result.items),
                    'wrong_basis': result.wrong_basis, 'unscoreable': result.unscoreable,
                    'outcome': result.outcome}.items())):
            permission = _refuse(permission, 5, 'newest recorded row is not the exact host-bound capture evaluation')
        try:
            reasons = (selected.review.reasons(selected.population, allow_test_only=self._allow_test_only,
                                               actor=selected.actor) if selected.review else
                       ['no separately checked qualification population review; development admission is insufficient'])
        except (ValueError, KeyError, TypeError, OSError) as exc:
            reasons = ['population review could not establish qualification: ' + str(exc)]
        exposure = json.loads(selected.population.description)['exposure']
        if not exposure.get('status') or not exposure.get('history') or not exposure.get('training_provenance'):
            reasons.append('missing explicit exposure/history or training-provenance disclosure')
        if json.loads(selected.population.description).get('trace_only'):
            reasons.append('held development traces cannot qualify, including under a TEST_ONLY review')
        if json.loads(selected.actor.description)['config'].get('capture_replay'):
            reasons.append('historical capture-only replay cannot earn live-actor permission')
        if not self._allow_test_only and json.loads(selected.actor.description)['config'].get('purpose') == 'TEST_ONLY':
            reasons.append('TEST_ONLY actors are unavailable to default operational resolution')
        if reasons:
            permission = _refuse(permission, 10, '; '.join(reasons))
        return permission

    def task_policy(self, policy_digest: str) -> Any:
        policy = self._task_policies.get(policy_digest)
        if policy is None:
            raise ValueError('protected task policy handle was not independently supplied')
        policy.verify()
        return policy

    def task_session(self, identity: str) -> HostSession:
        session = self._sessions.get(identity)
        if session is None:
            raise ValueError('no protected imported/registered task session')
        return session

    def host_session(self, inputs: HostInputs) -> HostSession:
        """Create before the child starts, from protected host-resolved source projections."""
        session = HostSession(self, inputs)
        self._sessions[session.identity] = session
        return session

    def check_claim_document(self, doc: dict[str, Any], clock: str,
                             _lookup: Callable[[str, str], mp.Permission] | None = None) -> list[str]:
        if doc.get('schema') == 'twin.substrate-generation/v1':
            return self.check_generation_document(doc, clock)
        bad = mp.check_claim_document(doc, clock, self.permission)
        if clock != mp.GOVERNED_CLOCK:
            return bad
        identity = (doc.get('run') or {}).get('host_session')
        session = self._sessions.get(identity) if isinstance(identity, str) else None
        if session is None:
            return bad + ['no protected host session for this claim; model-provided identity is insufficient']
        return bad + session.check_document(doc)

    def check_generation_document(self, doc: dict[str, Any], clock: str) -> list[str]:
        from .substrate_generation import check_document
        identity = (doc.get('run') or {}).get('host_session')
        session = self._sessions.get(identity) if isinstance(identity, str) else None
        if session is None:
            return ['no protected host session for generation document']
        return check_document(session, doc, clock)


@dataclass(frozen=True)
class HostInputs:
    """Trusted host data, not fields read from a candidate's claim or response.

    The host creates this before the child starts, or imports it from an independently pinned
    host-session archive. Its explicit issuer allowlist is protected host configuration.
    A canonical input source must actually match the projected input bytes and context hash.
    """
    description: bytes
    _metadata_store: Any = field(default=None, repr=False, compare=False)
    _metadata_policy: bytes | None = field(default=None, repr=False, compare=False)
    _test_only: TestOnlyPurpose | None = field(default=None, repr=False, compare=False)
    _task_policy: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def freeze(cls, records: tuple[dict[str, Any], ...], issuers: tuple[str, ...], *,
               metadata_store: Any = None, metadata_policy: dict[str, Any] | None = None,
               test_only: TestOnlyPurpose | None = None, task_policy: Any = None) -> HostInputs:
        subjects = [row.get('subject') for row in records]
        if any(not isinstance(subject, str) or not subject for subject in subjects) or len(set(subjects)) != len(subjects):
            raise ValueError('host inputs need unique nonempty subjects')
        if test_only is not None and test_only is not TEST_ONLY_MECHANICS:
            raise ValueError('invalid protected TEST_ONLY host purpose')
        description: dict[str, Any] = {'records': records, 'issuers': issuers}
        if test_only is TEST_ONLY_MECHANICS:
            if metadata_store is not None or metadata_policy is not None or task_policy is not None or any(
                    not row.get('issuer', '').startswith('TEST_ONLY') for row in records):
                raise ValueError('legacy mechanics require protected TEST_ONLY host purpose')
            description['purpose'] = test_only.value
        if metadata_policy is not None:
            from .source_metadata import validate_parent_policy
            validate_parent_policy(metadata_policy, metadata_store)
            if metadata_policy['purpose'] == 'TEST_ONLY' and any(not row.get('issuer', '').startswith('TEST_ONLY') for row in records):
                raise ValueError('TEST_ONLY source authority cannot enter an actual host import')
            description['source_metadata_policy'] = metadata_policy
        if task_policy is not None:
            task_policy.verify()
            for row in records:
                task_policy.verify_input(row)
            description['task_policy'] = json.loads(task_policy.description)
        return cls(canonical(description), metadata_store,
                   canonical(metadata_policy) if metadata_policy is not None else None, test_only, task_policy)

    @classmethod
    def restore(cls, archive: bytes, *, metadata_store: Any = None,
                metadata_policy: dict[str, Any] | None = None,
                test_only: TestOnlyPurpose | None = None, task_policy: Any = None) -> HostInputs:
        value = json.loads(archive)
        if 'task_policy' not in value:
            task_policy = None
        # A catalogue's signal handles must not add a binding to unrelated inputs.
        # Actual signal rows still require their protected handles in resolve below.
        if 'source_metadata_policy' not in value:
            metadata_store, metadata_policy = None, None
        restored = cls.freeze(tuple(value['records']), tuple(value['issuers']), metadata_store=metadata_store,
                              metadata_policy=metadata_policy, test_only=test_only, task_policy=task_policy)
        if restored.description != archive:
            raise ValueError('host restore differs from independently selected protected store/policy/purpose')
        for record in value['records']:
            restored.resolve(record['subject'])
        return restored

    @property
    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(self.resolve(row['subject']) for row in json.loads(self.description)['records'])

    def resolve(self, subject: str) -> dict[str, Any]:
        value = json.loads(self.description)
        if value.get('purpose') != (self._test_only.value if self._test_only else None):
            raise ValueError('host archive requires the same protected TEST_ONLY purpose')
        if value.get('source_metadata_policy') != (json.loads(self._metadata_policy) if self._metadata_policy else None):
            raise ValueError('host archive requires independently selected metadata store/policy')
        row = next((row for row in value['records'] if row['subject'] == subject), None)
        if row is None:
            raise ValueError('host has no source/input provenance for subject ' + subject)
        if row.get('issuer') not in value['issuers']:
            raise ValueError('input provenance issuer is not registered by the host')
        try:
            source, context = row['source'], row['context']
            raw = base64.b64decode(source['content_base64'], validate=True)
            if (len(raw) != source['bytes'] or hashlib.sha256(raw).hexdigest() != source['sha256']
                    or raw != canonical(row['input']) or not source['version']
                    or context['source'] != source['identity'] or context['source_sha256'] != source['sha256']):
                raise ValueError('host source/input/context provenance conflict')
            for name in ('organisation', 'domain', 'capability', 'as_of', 'frame', 'source'):
                if not isinstance(context.get(name), str) or not context[name]:
                    raise ValueError('missing host context: ' + name)
            if value.get('task_policy') != (json.loads(self._task_policy.description) if self._task_policy else None):
                raise ValueError('host archive requires original protected task policy')
            from .task_contracts import TASK_METRICS
            typed_task = isinstance(row['input'], dict) and row['input'].get('schema') in {
                f'twin.{task}-input/v2' for task in TASK_METRICS}
            if self._task_policy is not None:
                self._task_policy.verify_input(row)
                return row
            if typed_task:
                raise ValueError('typed task input requires independently selected protected task policy')
            # A v2 source projection cannot opt into generic component routing by
            # removing public signal flags or its serialized metadata policy.
            source_context = row['input'].get('source_context') if isinstance(row['input'], dict) else None
            public_metadata = source_context.get('metadata') if isinstance(source_context, dict) else None
            if ('eligible_components' in context or 'source_metadata' in context
                    or isinstance(public_metadata, dict)
                    and public_metadata.get('schema') == 'twin.source-metadata-public/v1'):
                candidates = row['input'].get('candidates')
                if (not isinstance(candidates, list) or not candidates
                        or any(not isinstance(item, dict) or not isinstance(item.get('id'), str)
                               or not isinstance(item.get('definition'), dict) for item in candidates)):
                    raise ValueError('signal host needs full candidate definitions')
                eligible = [item['id'] for item in candidates]
                if (len(set(eligible)) != len(eligible) or context['eligible_components'] != eligible
                        or context.get('candidate_universe_digest') != digest(candidates)
                        or 'component' in context):
                    raise ValueError('signal host universe differs from actual input or preselects an answer')
                if 'source_metadata' in context:
                    from .signal_inputs import binding_context
                    from .source_metadata import verify_host_metadata
                    verify_host_metadata(row, self._metadata_store,
                        json.loads(self._metadata_policy) if self._metadata_policy else None)
                    if any(context.get(key) != item for key, item in binding_context(row['input']).items()):
                        raise ValueError('signal host input construction/model context differs')
                elif self._test_only is not TEST_ONLY_MECHANICS:
                    raise ValueError('signal host requires actual protected metadata acquisition')
            elif not isinstance(context.get('component'), str) or not context['component']:
                raise ValueError('missing fixed host component')
        except (KeyError, TypeError) as exc:
            raise ValueError('missing host source provenance') from exc
        return row


def _scope_reasons(population: Population, context: dict[str, Any]) -> list[str]:
    envelope = population.envelope
    reasons = []
    if population.metric == 'substrate-generator':
        from .substrate_generation import scope_reasons
        reasons.extend(scope_reasons(population, context))
    for field, allowed in (('organisation', 'adopters'), ('domain', 'domains'),
                           ('capability', 'capabilities'), ('frame', 'frames'), ('source', 'sources')):
        if context.get(field) not in envelope[allowed]:
            reasons.append('host ' + field + ' is outside the predeclared applicability envelope')
    from .task_contracts import METRIC_TASK
    if population.metric in METRIC_TASK and 'task_contexts' in envelope:
        frozen = envelope['task_contexts'].get(context.get('organisation'), {})
        for name in ('model_pins', 'model_as_of', 'party_sha256', 'input_constructor_sha256', 'task_contract_sha256'):
            if context.get(name) != frozen.get(name) or not frozen.get(name):
                reasons.append('host ' + name + ' differs from qualified task context')
        if context.get('estate_scope_sha256') != envelope.get('estate_scope_sha256'):
            reasons.append('host task estate scope differs')
        if not context.get('source_families') or any(family not in envelope['sources'] for family in context['source_families']):
            reasons.append('a task source family is outside declared applicability')
    if population.metric == 'signal-classify' and 'signal_contexts' in envelope:
        frozen = envelope['signal_contexts'].get(context.get('organisation'), {})
        for name in ('candidate_universe_digest', 'model_pins', 'model_as_of', 'input_construction_sha256'):
            if not frozen.get(name) or context.get(name) != frozen[name]:
                reasons.append('host ' + name + ' differs from qualified signal model context')
    try:
        as_of = date.fromisoformat(context['as_of'])
        if not date.fromisoformat(envelope['from']) <= as_of <= date.fromisoformat(envelope['until']):
            reasons.append('host date is outside the predeclared applicability envelope')
    except (KeyError, TypeError, ValueError):
        reasons.append('host date is missing or invalid')
    return reasons


@dataclass(frozen=True)
class Judgement:
    receipt: str | None
    reason: str | None
    output: Output | None = None


class HostSession:
    """A protected parent owns invocation and receipts; a child can only echo receipt tokens.

    Live receipts are held in parent memory. Later validation accepts only an exact session
    archive independently pinned in the protected judge catalogue, never a child-written file.
    No secret or ephemeral authentication key is exported.
    """
    def __init__(self, resolver: Resolver, inputs: HostInputs):
        self._resolver = resolver
        self._inputs = inputs
        self.identity = secrets.token_hex(24)
        self._records: dict[str, bytes] = {}
        self._declines: list[dict[str, str]] = []
        self._failed_outputs: list[dict[str, Any]] = []
        self._pending: dict[str, bytes] = {}
        self._live_assessments: dict[str, BasisAssessment] = {}
        self._reviewed_outputs: list[dict[str, Any]] = []
        self._generation_dispositions: list[dict[str, Any]] = []
        self._generation_blobs: dict[str, str] = {}
        self._task_job: bytes | None = None
        self._task_attempts: list[dict[str, Any]] = []
        self._task_events: list[dict[str, Any]] = []
        self._task_reviews: dict[str, Any] = {}

    def bind_task_job(self, job: dict[str, Any]) -> None:
        from .task_sessions import bind_job
        bind_job(self, job)

    def task_snapshot(self) -> dict[str, Any]:
        from .task_sessions import snapshot
        return snapshot(self)

    def decline_task_run(self, subjects: tuple[str, ...], reason: str) -> None:
        from .task_sessions import decline_run
        decline_run(self, subjects, reason)

    def judge_group(self, model_version: str, subject: str) -> Judgement:
        from .task_sessions import judge
        return judge(self, 'causal', model_version, subject, paired=True)

    def check_task_document(self, document: dict[str, Any]) -> list[str]:
        from .task_sessions import check_document
        return check_document(self, document)

    @property
    def declines(self) -> list[dict[str, str]]:
        return json.loads(canonical(self._declines))

    @property
    def pending_reviews(self) -> list[dict[str, Any]]:
        return [{'request_digest': key, 'request': json.loads(record).get('task_review_request') or self._review_request(json.loads(record))}
                for key, record in self._pending.items()]

    def _review_request(self, record: dict[str, Any]) -> dict[str, Any]:
        if 'task_metrics' in record:
            from .task_sessions import review_request
            return review_request(self, record)
        selected, _ = self._resolver._bindings[(record['metric'], record['model_version'])]
        if selected.assessment_policy is None:
            raise ValueError('live selection has no independent assessment policy')
        row = self._inputs.resolve(record['subject'])
        return {'schema': 'twin.basis-request/v1', 'policy': selected.assessment_policy.digest,
            'actor_digest': selected.actor.digest, 'population_digest': selected.population.digest,
            'selection_digest': selected.digest, 'capture_digest': digest(record),
            'rows': [{'id': record['subject'], 'input': row['input'], 'context': row['context'],
                'sources': row['context'].get('original_sources', {'input': row['source']}),
                'output': record['output']}]}

    def _verify_record(self, record: dict[str, Any]) -> None:
        if 'task_metrics' in record:
            from .task_sessions import verify_record
            verify_record(self, record)
            return
        row = self._inputs.resolve(record['subject'])
        selected, _ = self._resolver._bindings[(record['metric'], record['model_version'])]
        selected.verify_input(row)
        output = record['output']
        parsed = selected.actor.parser(base64.b64decode(output['raw'], validate=True),
                                      json.loads(selected.actor.description)['config'])
        runtime = json.loads(selected.actor.description)['config'].get('runtime_contract')
        if (record['selection'] != selected.digest or record['context'] != row['context']
                or _scope_reasons(selected.population, row['context'])
                or output['actor_digest'] != selected.actor.digest or output['input_digest'] != digest(row['input'])
                or output.get('failure') or runtime and output.get('observed_runtime') != runtime
                or canonical({'answer': parsed.answer, 'basis': parsed.basis}) != canonical({
                    'answer': output['answer'], 'basis': output['basis']})):
            raise ValueError('protected session no longer matches current host binding')

    def review_pending(self, request_digest: str, store: ReviewStore) -> Judgement:
        """Resume the retained actual output after host acquisition, never rerun inference."""
        if request_digest in self._pending and 'task_metrics' in json.loads(self._pending[request_digest]):
            from .task_sessions import review_pending
            return review_pending(self, request_digest, store)
        subject = request_digest
        try:
            record = json.loads(self._pending[request_digest])
            self._verify_record(record)
            subject = record['subject']
            selected, _ = self._resolver._bindings[(record['metric'], record['model_version'])]
            selected.verify()
            permission = self._resolver.permission(record['metric'], record['model_version'])
            if not permission.granted:
                raise ValueError(permission.why())
            row = self._inputs.resolve(subject)
            if row['context'] != record['context'] or _scope_reasons(selected.population, row['context']):
                raise ValueError('pending review host context is stale')
            request = canonical(self._review_request(record))
            if digest(json.loads(request)) != request_digest or selected.assessment_policy is None:
                raise ValueError('pending actual-output review request changed')
            assessment = store.assess(selected.assessment_policy, request)
            del self._pending[request_digest]  # a failed assessment cannot be selectively replaced
            self._reviewed_outputs.append({'record': record, 'assessment': json.loads(assessment.packet)})
            if assessment.outcome(subject) is not True:
                raise ValueError('independent live semantic assessment did not pass')
            self._live_assessments[assessment.digest] = assessment
            record['assessment'] = json.loads(assessment.packet)
            record['assessment_digest'] = assessment.digest
            receipt = secrets.token_hex(24)
            self._records[receipt] = canonical(record)
            return Judgement(receipt, None, Output(canonical(record['output'])))
        except Exception as exc:
            self._declines.append({'subject': subject, 'reason': str(exc)})
            return Judgement(None, str(exc))

    def judge(self, metric: str, model_version: str, subject: str) -> Judgement:
        from .task_contracts import METRIC_TASK
        binding = self._resolver._bindings.get((metric, model_version))
        if metric in METRIC_TASK and (binding is None or binding[0]._test_only is not TEST_ONLY_MECHANICS):
            from .task_sessions import judge
            return judge(self, METRIC_TASK[metric], model_version, subject, paired=False)
        try:
            row = self._inputs.resolve(subject)
            bound = self._resolver._bindings.get((metric, model_version))
            permission = self._resolver.permission(metric, model_version)
            if bound is None or not permission.granted:
                raise ValueError(permission.why())
            selected, _ = bound
            selected.verify_input(row)
            reasons = _scope_reasons(selected.population, row['context'])
            if reasons:
                raise ValueError('; '.join(reasons))
            if selected._task_contract is not None and selected._task_contract.task == 'causal':
                raise ValueError('registered causal task requires paired judgement and both current permissions')
            if metric != 'signal-classify' and selected._task_contract is None and not row['context'].get('component'):
                raise ValueError('non-signal judgement requires its fixed host component')
            if metric == 'substrate-generator':
                from .substrate_generation import validate_row
                validate_row(row, selected.actor.model_version)
            if metric == 'signal-classify':
                if selected.assessment_policy and 'eligible_components' not in row['context']:
                    raise ValueError('reviewed signal actor requires the full protected eligible universe')
                metadata = row['context'].get('signal', {})
                if (metadata.get('id') != subject or metadata.get('date') != row['context']['as_of']
                        or not metadata.get('from') or not metadata.get('provenance', {}).get('url')):
                    raise ValueError('host signal identity/date/pin/provenance is missing')
            output = selected.actor.invoke(row['input'])
            if output.failure:
                self._failed_outputs.append({'subject': subject, 'metric': metric,
                                             'output': json.loads(output.packet)})
                raise ValueError('actor declined: ' + output.failure)
            if not isinstance(output.stated.answer, dict) or output.stated.basis is None:
                self._failed_outputs.append({'subject': subject, 'metric': metric,
                                             'output': json.loads(output.packet)})
                raise ValueError('live actor output lacks an answer object or actual stated basis')
            if metric == 'signal-classify' and 'eligible_components' in row['context']:
                if output.stated.answer.get('claim', {}).get('component') not in row['context']['eligible_components']:
                    self._failed_outputs.append({'subject': subject, 'metric': metric,
                                                 'output': json.loads(output.packet)})
                    raise ValueError('actual signal selected a component outside the host universe')
                if selected.assessment_policy:
                    from .signal_candidate import quote_integrity
                    if not quote_integrity(output.stated, row['input']):
                        self._failed_outputs.append({'subject': subject, 'metric': metric,
                                                     'output': json.loads(output.packet)})
                        raise ValueError('actual signal quotes lack literal input witnesses; semantics not assessed')
            record = {'subject': subject, 'metric': metric,
                'model_version': model_version, 'selection': selected.digest,
                'context': row['context'], 'output': json.loads(output.packet),
                'attempt': secrets.token_hex(24)}
            if selected.assessment_policy:
                request = self._review_request(record)
                self._pending[digest(request)] = canonical(record)
                raise ValueError('independent live semantic assessment required; actual output retained')
            receipt = secrets.token_hex(24)
            self._records[receipt] = canonical(record)
            return Judgement(receipt, None, output)
        except Exception as exc:  # every attempted operation/decline remains counted
            reason = str(exc)
            self._declines.append({'subject': subject, 'reason': reason})
            return Judgement(None, reason)

    def check_document(self, doc: dict[str, Any]) -> list[str]:
        run = doc.get('run') or {}
        bad = []
        if run.get('declined') != self.declines:
            bad.append('document does not preserve the host counted declines')
        seen = []
        for claim in doc.get('claims') or []:
            token = claim.get('host_receipt')
            packet = self._records.get(token) if isinstance(token, str) else None
            if packet is None:
                bad.append('claim has no matching protected host receipt')
                continue
            seen.append(token)
            record = json.loads(packet)
            metric = mp.SKILL_FOR_CLAIM_KIND.get(claim.get('kind'))
            if (record['metric'] != metric or record['model_version'] != run.get('model_version')
                    or doc.get('org') != record['context']['organisation']
                    or claim.get('host_subject') != record['subject']):
                bad.append('claim actor/metric/adopter/subject differs from host receipt')
            row = self._inputs.resolve(record['subject'])
            bound = self._resolver._bindings.get((record['metric'], record['model_version']))
            if bound is None or record['selection'] != bound[0].digest:
                bad.append('claim host receipt has a stale selection')
                continue
            selected, _ = bound
            selected.verify_input(row)
            bad.extend(_scope_reasons(selected.population, row['context']))
            if selected.assessment_policy:
                assessment = self._live_assessments.get(record.get('assessment_digest', ''))
                if assessment is None:
                    bad.append('claim lacks actual independent live semantic assessment')
                else:
                    original = {key: item for key, item in record.items()
                                if key not in ('assessment', 'assessment_digest')}
                    try:
                        assessment.verify(selected.assessment_policy, canonical(self._review_request(original)))
                        if assessment.outcome(record['subject']) is not True:
                            bad.append('claim independent semantic assessment did not pass')
                    except (ValueError, KeyError, TypeError) as exc:
                        bad.append('claim semantic assessment failed verification: ' + str(exc))
            output = record['output']
            answer = output['answer']
            matches = claim.get('evidence') == output['basis']
            if metric == 'evolution-judge':
                matches = (matches and claim.get('component') == row['context']['component']
                           and claim.get('evolution_position') == answer.get('evolution_position'))
            elif metric == 'signal-classify':
                from .signal_candidate import evidence_text
                allowed = row['context'].get('eligible_components', [row['context'].get('component')])
                matches = (claim.get('component') in allowed
                           and claim.get('evidence') == evidence_text(output['basis']))
                signal = claim.get('signal', {})
                matches = (matches and claim.get('component') == answer.get('claim', {}).get('component')
                           and signal.get('steep') == answer.get('steep')
                           and signal.get('statement') == row['input'].get('statement')
                           and signal.get('source') == row['input'].get('source')
                           and all(signal.get(field) == row['context'].get('signal', {}).get(field)
                                   for field in ('id', 'date', 'from', 'provenance')))
            else:
                matches = False
            if not matches:
                bad.append('claim semantic assertion differs from actual host output/input')
        if len(set(seen)) != len(seen) or set(seen) != set(self._records):
            bad.append('document omits or duplicates host counted judgements')
        return bad

    def archive(self) -> bytes:
        return canonical({'schema': 'twin.host-session/v1', 'identity': self.identity,
            'inputs': json.loads(self._inputs.description),
            'records': {token: json.loads(packet) for token, packet in self._records.items()},
            'declines': self.declines, 'failed_outputs': self._failed_outputs,
            'pending_reviews': {key: json.loads(value) for key, value in self._pending.items()},
            'reviewed_outputs': self._reviewed_outputs,
            'generation_dispositions': self._generation_dispositions,
            'generation_blobs': self._generation_blobs,
            **({'task_job': json.loads(self._task_job), 'task_attempts': self._task_attempts,
                'task_events': self._task_events, 'task_reviews': self._task_reviews} if self._task_job is not None else {})})

    @classmethod
    def restore(cls, archive: bytes, resolver: Resolver, *, metadata_store: Any = None,
                metadata_policy: dict[str, Any] | None = None,
                test_only: TestOnlyPurpose | None = None, task_policy: Any = None) -> HostSession:
        value = json.loads(archive)
        if value.get('schema') != 'twin.host-session/v1':
            raise ValueError('unknown protected session schema')
        session = cls(resolver, HostInputs.restore(canonical(value['inputs']), metadata_store=metadata_store,
            metadata_policy=metadata_policy, test_only=test_only, task_policy=task_policy))
        session.identity = value['identity']
        session._declines = value['declines']
        session._failed_outputs = value.get('failed_outputs', [])
        session._reviewed_outputs = value.get('reviewed_outputs', [])
        session._generation_dispositions = value.get('generation_dispositions', [])
        session._generation_blobs = value.get('generation_blobs', {})
        if 'task_job' in value:
            session.bind_task_job(value['task_job'])
            session._task_attempts = value['task_attempts']
            session._task_events = value['task_events']
            session._task_reviews = value['task_reviews']
            from .task_sessions import restore_assessments
            restore_assessments(session)
        for key, record in value.get('pending_reviews', {}).items():
            session._verify_record(record)
            selected, _ = resolver._bindings[(record['metric'], record['model_version'])]
            request = session._review_request(record)
            if digest(request) != key:
                raise ValueError('pending host review request differs from protected capture')
            session._pending[key] = canonical(record)
        for token, record in value['records'].items():
            if 'task_metrics' in record:
                from .task_sessions import restore_record
                restore_record(session, record)
                session._records[token] = canonical(record)
                continue
            row = session._inputs.resolve(record['subject'])
            selected, _ = resolver._bindings[(record['metric'], record['model_version'])]
            selected.verify_input(row)
            output = record['output']
            parsed = selected.actor.parser(base64.b64decode(output['raw'], validate=True),
                                            json.loads(selected.actor.description)['config'])
            runtime_contract = json.loads(selected.actor.description)['config'].get('runtime_contract')
            if (record['selection'] != selected.digest or record['context'] != row['context']
                    or _scope_reasons(selected.population, row['context'])
                    or output['actor_digest'] != selected.actor.digest or output['input_digest'] != digest(row['input'])
                    or runtime_contract and output.get('observed_runtime') != runtime_contract
                    or canonical({'answer': parsed.answer, 'basis': parsed.basis}) != canonical({
                        'answer': output['answer'], 'basis': output['basis']})):
                raise ValueError('protected session no longer matches current host binding')
            if selected.assessment_policy:
                if not record.get('assessment'):
                    raise ValueError('live receipt omits independent semantic assessment')
                original = {key: item for key, item in record.items()
                            if key not in ('assessment', 'assessment_digest')}
                assessment = _restore_assessment(canonical(record['assessment']), selected.assessment_policy,
                    canonical(session._review_request(original)))
                if assessment.digest != record.get('assessment_digest') or assessment.outcome(record['subject']) is not True:
                    raise ValueError('live receipt semantic assessment does not pass for actual output')
                session._live_assessments[assessment.digest] = assessment
            session._records[token] = canonical(record)
        if session._generation_dispositions or session._generation_blobs:
            from .substrate_generation import verify_session
            verify_session(session)
        return session


def _restore_callable(identity: dict[str, Any]) -> Callable[..., Any]:
    """Only called after an independently pinned host bundle was verified."""
    value: Any = importlib.import_module(identity['module'])
    for name in identity['name'].split('.'):
        if name == '<locals>':
            raise ValueError('archived adapters must be importable host functions')
        value = getattr(value, name)
    if _callable_identity(value) != identity:
        raise ValueError('archived adapter differs from current host source')
    return value


def _restore_selection(value: dict[str, Any], *, metadata_store: Any = None,
                       source_metadata_policy: dict[str, Any] | None = None,
                       test_only: TestOnlyPurpose | None = None,
                       task_policies: dict[str, Any] | None = None) -> Selection:
    if value.get('schema') != 'twin.qualification-bundle/v1':
        raise ValueError('unknown host bundle schema')
    actor_value = value['actor']
    authority = None
    if actor_value.get('source_metadata_authority') is not None:
        from .source_metadata import validate_parent_policy
        validate_parent_policy(source_metadata_policy, metadata_store)
        assert source_metadata_policy is not None
        authority = metadata_store.authority(source_metadata_policy['authority_digest'])
        if actor_value['source_metadata_authority'] != json.loads(authority.description):
            raise ValueError('restored actor protected metadata authority differs')
    actor = Actor(canonical(actor_value), _restore_callable(actor_value['runner']),
                  _restore_callable(actor_value['parser']), authority)
    population = Population(canonical(value['population']))
    review_value = value['review']
    review = None
    if review_value:
        checker_identity = base64.b64decode(review_value['checker_identity'], validate=True)
        review = PopulationReview(base64.b64decode(review_value['record'], validate=True),
            _restore_callable(json.loads(checker_identity)['callable']) if checker_identity else None,
            checker_identity)
    selection_value = value['selection']
    legacy = selection_value.get('purpose')
    if legacy and test_only is not TEST_ONLY_MECHANICS:
        raise ValueError('ordinary operational catalogue cannot restore TEST_ONLY legacy mechanics')
    policy = BasisPolicy(canonical(selection_value['assessment_policy'])) if selection_value.get('assessment_policy') else None
    task_policy = None
    if selection_value.get('task_policy') is not None:
        task_policy = (task_policies or {}).get(digest(selection_value['task_policy']))
        if task_policy is None or task_policy.description != canonical(selection_value['task_policy']):
            raise ValueError('restored task requires original independently selected protected policy handles')
    selected = Selection.freeze(actor, population, _restore_callable(selection_value['basis_checker']),
        reference_projection=_restore_callable(selection_value['projection']), review=review, assessment_policy=policy,
        source_metadata_policy=source_metadata_policy if population.metric == 'signal-classify' else None,
        metadata_store=metadata_store if population.metric == 'signal-classify' else None,
        test_only=TEST_ONLY_MECHANICS if legacy and test_only is TEST_ONLY_MECHANICS else None,
        task_contract=task_policy.contract if task_policy else None, task_policy=task_policy)
    if selected.description != canonical(selection_value):
        raise ValueError('archived selection differs from current host binding')
    return selected


def _restore_bundle(bundle: bytes, *, metadata_store: Any = None,
                    source_metadata_policy: dict[str, Any] | None = None,
                    test_only: TestOnlyPurpose | None = None,
                    task_policies: dict[str, Any] | None = None) -> tuple[Selection, Capture] | tuple[Selection, Capture, BasisAssessment]:
    value = json.loads(bundle)
    selected = _restore_selection(value, metadata_store=metadata_store,
        source_metadata_policy=source_metadata_policy, test_only=test_only, task_policies=task_policies)
    if selected._task_contract is not None and selected._task_contract.task == 'causal':
        raise ValueError('ordinary single-metric bundle cannot establish paired causal proof')
    policy = selected.assessment_policy
    packet = canonical(value['capture'])
    captured = Capture(packet, hmac.digest(selected._capture_key, packet, 'sha256'))
    if policy:
        if value.get('assessment') is None:
            raise ValueError('protected bundle omits required semantic assessment')
        assessment = _restore_assessment(canonical(value['assessment']), policy, selected.assessment_request(captured))
        selected.evaluate(captured, assessment)
        return selected, captured, assessment
    selected.evaluate(captured)
    return selected, captured


def _restore_group_bundle(bundle: bytes, *, metadata_store: Any = None,
                          source_metadata_policy: dict[str, Any] | None = None,
                          test_only: TestOnlyPurpose | None = None,
                          task_policies: dict[str, Any] | None = None) -> list[Any]:
    value = json.loads(bundle)
    if value.get('schema') != 'twin.qualification-group-bundle/v1' or len(value.get('members', [])) != 2:
        raise ValueError('complete paired causal group bundle required')
    selections = tuple(_restore_selection(member, metadata_store=metadata_store,
        source_metadata_policy=source_metadata_policy, test_only=test_only, task_policies=task_policies)
        for member in value['members'])
    group = CaptureGroup.freeze(selections)
    if canonical(value['group']) != group.description:
        raise ValueError('restored causal group membership/actor/input/custody differs')
    raw = canonical(value['core'])
    core = GroupCapture(raw, hmac.digest(group._capture_key, raw, 'sha256'))
    group._verify_capture(core)
    result: list[tuple[Selection, Capture] | tuple[Selection, Capture, BasisAssessment]] = []
    for selected, member in zip(selections, value['members']):
        view = group.view(selected, core)
        if view.packet != canonical(member['capture']):
            raise ValueError('restored metric view differs from actual shared raw core')
        selected.captured_outputs(view)
        if selected.assessment_policy:
            if member.get('assessment') is None:
                raise ValueError('group member omits its independent semantic assessment')
            assessment = _restore_assessment(canonical(member['assessment']), selected.assessment_policy,
                                              selected.assessment_request(view))
            selected.evaluate(view, assessment)
            result.append((selected, view, assessment))
        else:
            selected.evaluate(view)
            result.append((selected, view))
    return result
