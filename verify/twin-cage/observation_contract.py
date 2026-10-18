"""Render and recognize the two closed, reviewed observation writer programs.

This is a conservative static program contract, not an arbitrary Bash proof.
Unknown programs retain the normal declaration-proposal rung restriction. The
assets are the actual forward/emitter writers; their common transport remains
the production source in talk/observation-delivery-producer.sh. Display labels
are immaterial, but every executable statement, effective environment, ordering
and source path must match. No actor/capability or sandbox claim follows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ADAPTERS = {'driftwood': 'forward', 'tuppence': 'emitter', 'ludlow': 'emitter'}
MARKER = '@OBSERVATION_TRANSPORT@\n'


def render_writer(organization: str) -> dict[str, Any]:
    """The complete reviewed program and effective workflow defaults/environment."""
    if organization not in ADAPTERS:
        raise ValueError('no reviewed observation writer for this organization')
    source = (HERE / f'writer-{ADAPTERS[organization]}.yaml').read_text()
    contract = yaml.safe_load(source.replace('@ORGANIZATION@', organization))
    tail = (ROOT / 'talk/observation-delivery-producer.sh').read_text()
    markers = 0
    for step in contract['writer']['steps']:
        script = step.get('run', '')
        markers += script.count(MARKER)
        if MARKER in script:
            step['run'] = script.replace(MARKER, tail)
    if markers != 1:
        raise ValueError('reviewed writer must carry exactly one observation transport')
    return contract


def _program(writer: dict[str, Any]) -> dict[str, Any]:
    # Strip display labels only. with.name (an artifact selector), IDs, conditions,
    # environment, defaults, actions and all run bytes remain load-bearing.
    result = {key: value for key, value in writer.items() if key != 'name'}
    result['steps'] = [{key: value for key, value in step.items() if key != 'name'}
                       for step in writer.get('steps', [])]
    return result


def observation_steps(workflow: dict[str, Any], organization: str | None) -> frozenset[int]:
    """Only exact recognized observation transports avoid the proposal predicate.

    Organization comes from the served reader's loop, never from workflow data.
    Comparing the whole writer closes mixed/post-cage writes and cross-step or
    workflow-level overrides; a matching tail alone is insufficient.
    """
    if organization not in ADAPTERS:
        return frozenset()
    assert organization is not None
    try:
        expected = render_writer(organization)
        actual = workflow['jobs']['write']
        actual_contract = {'environment': workflow.get('env', {}),
                           'defaults': workflow.get('defaults', {}),
                           'writer': _program(actual)}
        expected['writer'] = _program(expected['writer'])
        # JSON preserves scalar types: Python dict equality would call False,
        # integer0 and float0.0 interchangeable executable input values.
        if json.dumps(actual_contract, sort_keys=True) != json.dumps(expected, sort_keys=True):
            return frozenset()
        tail = (ROOT / 'talk/observation-delivery-producer.sh').read_text()
        return frozenset(index for index, step in enumerate(actual['steps'])
                         if str(step.get('run', '')).endswith(tail))
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError):
        # A missing or changed contract never widens the declared rung.
        return frozenset()
