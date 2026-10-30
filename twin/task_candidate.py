"""Strict input-only adapters for the four reviewed judgement tasks."""
from __future__ import annotations

from typing import Any
import hashlib
import importlib
from pathlib import Path

from . import task_contracts
from .skills import Stated
from .qualification import Actor, RuntimeResult, canonical


def _contract(config: dict[str, Any]) -> task_contracts.TaskContract:
    if not isinstance(config, dict) or not isinstance(config.get('task'), str):
        raise ValueError('explicit frozen task required')
    contract = task_contracts.TaskContract.freeze(config['task'])
    if config.get('task_contract_digest') != contract.digest:
        raise ValueError('frozen task contract differs')
    return contract


def _task_profile(config: dict[str, Any]) -> task_contracts.TaskContract:
    contract = _contract(config)
    if config.get('profile') != contract.task + '-linux-bf16-v1':
        raise ValueError('exact task-specific paired Linux profile required')
    if config.get('terminal_token') not in (None, '<|im_end|>'):
        raise ValueError('unsupported task terminal token')
    return contract


def _backend(config: dict[str, Any]) -> Any:
    _task_profile(config)
    try:
        paired = importlib.import_module('twin.linux_candidate')
    except ModuleNotFoundError as exc:
        raise ValueError('reviewed paired Linux backend source unavailable') from exc
    paired.validate_profile(config)
    return paired


def _template(contract: task_contracts.TaskContract, config: dict[str, Any]) -> bytes:
    template = Path(__file__).with_name('task_prompts').joinpath(contract.task + '.txt').read_bytes()
    declared = task_contracts.decode((task_contracts.ASSETS / 'prompts.json').read_bytes())
    expected = next(item['sha256'] for item in declared['prompts'] if item['task'] == contract.task)
    if hashlib.sha256(template).hexdigest() != expected or config.get('prompt_sha256') != expected:
        raise ValueError('exact reviewed task prompt identity required')
    if template.count(b'{{INPUT_JSON}}') != 1:
        raise ValueError('one complete task input placeholder required')
    return template


def render_prompt(payload: dict[str, Any], config: dict[str, Any]) -> bytes:
    """Use the exact frozen task template and complete canonical public input."""
    contract = _task_profile(config)
    from . import task_inputs
    task_contracts.validate(contract.task.title() + 'Input', payload)
    task_inputs.validate_payload(payload)
    template = _template(contract, config)
    return template.replace(b'{{INPUT_JSON}}', canonical(payload))


def freeze_actor(task: str, config: dict[str, Any], *, task_policy: Any = None) -> Actor:
    """Bind all task/support bytes only under the actual acquired backend authority."""
    contract = _task_profile(config)
    if contract.task != task:
        raise ValueError('explicit task differs from frozen invocation config')
    from . import task_inputs
    if not isinstance(task_policy, task_inputs.TaskPolicy):
        raise ValueError('actual private task policy required before backend authority acquisition')
    task_policy.verify()
    if (task_policy.contract.description != contract.description
            or config.get('task_policy_digest') != task_policy.digest):
        raise ValueError('frozen actor task policy differs from actual protected construction')
    _template(contract, config)
    paired = _backend(config)
    # Authority acquisition must precede Actor.freeze; source-only plans cannot be Actors.
    support = paired.support_sources(config)
    from . import qualified_tasks
    if qualified_tasks.__file__ is None:
        raise ValueError('actual qualified task parent source unavailable')
    return Actor.freeze(run, parse, config, support=(*support, *task_inputs.support_sources(),
        *task_contracts.support_sources(), Path(qualified_tasks.__file__),
        Path(__file__).with_name('task_prompts').joinpath(task + '.txt')))


def run(payload: dict[str, Any], config: dict[str, Any]) -> RuntimeResult:
    """Use one protected pair, retaining its exact capture through output refusal."""
    paired = _backend(config)
    prompt = render_prompt(payload, config)
    result = paired.invoke_pair({'input': payload, 'prompt_utf8': prompt.decode('utf-8')}, config)
    if not isinstance(result, RuntimeResult):
        raise ValueError('paired host must return its actual RuntimeResult')
    if result.failure:
        return result
    from . import task_inputs
    try:
        task_inputs.verify_output(payload, parse(result.raw, config))
    except Exception as exc:  # a captured failed attempt must never lose its raw bytes
        return RuntimeResult(result.raw, result.observed_runtime, result.observations,
            type(exc).__name__ + ': ' + str(exc))
    return result


def parse(raw: bytes, config: dict[str, Any]) -> Stated:
    """Preserve the whole actual answer and basis; syntax confers no permission."""
    contract = _contract(config)
    if not isinstance(raw, bytes) or len(raw) > 131072:
        raise ValueError('bounded original task response bytes required')
    terminal = config.get('terminal_token')
    if terminal is not None:
        if terminal != '<|im_end|>':
            raise ValueError('unsupported task terminal token')
        suffix = terminal.encode('utf-8')
        if raw.endswith(suffix):
            raw = raw[:-len(suffix)]
    value = task_contracts.decode(raw)
    task_contracts.validate(contract.task.title() + 'Response', value)
    if 'decline' in value:
        if not value['decline'].strip():
            raise ValueError('factual task decline required')
        return Stated(None, value)
    return Stated(value['answer'], value['basis'])
