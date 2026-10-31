"""Accepted case-free task shapes and identities, with no registration or authority."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

ASSETS = Path(__file__).with_name('task_contract')
TASK_METRICS = {'evolution': ('evolution-judge',),
    'causal': ('causal-claims', 'causal-claims-grade-accuracy'),
    'gameplay': ('gameplay-lens',), 'ethics': ('ethics-gate',)}
METRIC_TASK = {metric: task for task, metrics in TASK_METRICS.items() for metric in metrics}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate task JSON key')
        result[key] = value
    return result


def decode(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite task value')))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('exact UTF8 JSON task value required') from exc


def support_sources() -> tuple[Path, ...]:
    from . import source_metadata
    return (Path(__file__), source_metadata.SCHEMA_PATH,
            *(ASSETS / name for name in ('contract.md', 'lifecycle.json', 'semantic-rules.json',
                'task-shapes.schema.json', 'rubrics.json', 'red-plan.json', 'prompts.json', 'profiles.json')))


def _shape(value: Any, rule: dict[str, Any], schema: dict[str, Any]) -> None:
    if '$ref' in rule:
        _shape(value, schema['$defs'][rule['$ref'].split('/')[-1]], schema)
        return
    for alternative in ('oneOf', 'anyOf'):
        if alternative in rule:
            matches = 0
            for choice in rule[alternative]:
                try:
                    _shape(value, choice, schema)
                    matches += 1
                except ValueError:
                    pass
            if matches == 0 or alternative == 'oneOf' and matches != 1:
                raise ValueError('task schema alternative differs')
    for clause in rule.get('allOf', []):
        if 'if' in clause:
            try:
                _shape(value, clause['if'], schema)
            except ValueError:
                continue
            _shape(value, clause['then'], schema)
        else:
            _shape(value, clause, schema)
    kinds = {'object': (dict,), 'array': (list,), 'string': (str,), 'number': (int, float),
             'integer': (int,), 'boolean': (bool,), 'null': (type(None),)}
    required_type = rule.get('type')
    if required_type is not None:
        names = required_type if isinstance(required_type, list) else [required_type]
        if not any(type(value) in kinds[name] for name in names):
            raise ValueError('task schema type differs')
    if type(value) is float and not math.isfinite(value):
        raise ValueError('nonfinite task value')
    if 'const' in rule and _canonical(value) != _canonical(rule['const']):
        raise ValueError('task schema constant differs')
    if 'enum' in rule and not any(_canonical(value) == _canonical(item) for item in rule['enum']):
        raise ValueError('task schema enum differs')
    if isinstance(value, dict):
        properties = rule.get('properties', {})
        if not set(rule.get('required', [])) <= set(value):
            raise ValueError('task schema missing fields')
        if rule.get('additionalProperties') is False and set(value) - set(properties):
            raise ValueError('task schema unknown fields')
        if len(value) < rule.get('minProperties', 0):
            raise ValueError('task schema empty map')
        for key, child in value.items():
            spec = properties.get(key, rule.get('additionalProperties', {}))
            if isinstance(spec, dict):
                _shape(child, spec, schema)
    if isinstance(value, list):
        if len(value) < rule.get('minItems', 0) or len(value) > rule.get('maxItems', len(value)):
            raise ValueError('task schema list size differs')
        if rule.get('uniqueItems') and len({_canonical(child) for child in value}) != len(value):
            raise ValueError('task schema duplicate members')
        for child in value:
            _shape(child, rule.get('items', {}), schema)
    if isinstance(value, str):
        if len(value) < rule.get('minLength', 0) or 'pattern' in rule and not re.search(rule['pattern'], value):
            raise ValueError('task schema text differs')
        if rule.get('format') == 'date':
            try:
                if date.fromisoformat(value).isoformat() != value:
                    raise ValueError('task date is not an exact ISO day')
            except ValueError as exc:
                raise ValueError('task date is not an exact ISO day') from exc
    if type(value) in (int, float) and (value < rule.get('minimum', value) or value > rule.get('maximum', value)):
        raise ValueError('task schema numeric interval differs')


def validate(definition: str, value: Any) -> None:
    schema = decode((ASSETS / 'task-shapes.schema.json').read_bytes())
    if definition not in schema['$defs']:
        raise ValueError('unknown task shape')
    _shape(value, schema['$defs'][definition], schema)


@dataclass(frozen=True)
class TaskContract:
    description: bytes

    @classmethod
    def freeze(cls, task: str) -> TaskContract:
        if task not in TASK_METRICS:
            raise ValueError('unsupported registered task')
        return cls(_canonical({'schema': 'twin.task-contract/v1', 'task': task,
            'metrics': TASK_METRICS[task], 'sources': {str(path.name if path.parent != ASSETS else 'task_contract/' + path.name):
                hashlib.sha256(path.read_bytes()).hexdigest() for path in support_sources()}}))

    @property
    def task(self) -> str:
        return str(decode(self.description)['task'])

    @property
    def metrics(self) -> tuple[str, ...]:
        return tuple(decode(self.description)['metrics'])

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.description).hexdigest()

    def verify(self) -> None:
        if self.description != self.freeze(self.task).description:
            raise ValueError('accepted task contract or support sources changed')
