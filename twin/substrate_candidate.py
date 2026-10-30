"""Input-only generator adapter. No model, tokenizer or provider is installed here."""
from __future__ import annotations

import hashlib
import base64
import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import Any

from .qualification import Actor, RuntimeResult, canonical
from .skills import Stated


def parse(raw: bytes, config: dict[str, Any]) -> Stated:
    """Decode one original JSON object; never salvage, coerce or supply schedule content."""
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('duplicate response key')
            value[key] = item
        return value
    def invalid(value: str) -> Any:
        raise ValueError('non-JSON number: ' + value)
    text = raw.decode('utf-8')
    terminal = config.get('terminal_token')
    if terminal:
        if terminal != '<|im_end|>':
            raise ValueError('unsupported terminal token')
        if text.endswith(terminal):
            text = text[:-len(terminal)]
    value = json.loads(text, object_pairs_hook=unique, parse_constant=invalid)
    if not isinstance(value, dict):
        raise ValueError('one response object required')
    if set(value) == {'decline'}:
        if not isinstance(value['decline'], str) or not value['decline'].strip():
            raise ValueError('decline needs its factual reason')
        return Stated(None, value)
    if set(value) not in ({'answer'}, {'answer', 'basis'}):
        raise ValueError('response must contain only answer and optional actual basis')
    basis = value.get('basis')
    return Stated(value['answer'], None if basis is None else {
        'model_basis': basis, 'observed_answer': value['answer'],
        'raw_output_sha256': hashlib.sha256(raw).hexdigest()})


def render_prompt(payload: str, config: dict[str, Any]) -> bytes:
    from .substrate_recipe_basis import recipe_fields
    recipe_fields(payload)
    template = Path(__file__).with_name('substrate-candidate-prompt.txt').read_bytes()
    if hashlib.sha256(template).hexdigest() != config.get('prompt_sha256'):
        raise ValueError('frozen substrate prompt source changed')
    if template.count(b'{{recipe_yaml}}') != 1:
        raise ValueError('one input-only prompt placeholder required')
    return template.replace(b'{{recipe_yaml}}', payload.encode('utf-8'))


def _profile(config: dict[str, Any]) -> None:
    if config.get('profile') not in ('substrate-linux-bf16-v1', 'TEST_ONLY-substrate-transport/v1'):
        raise ValueError('explicit reviewed substrate profile required')
    if config['profile'].startswith('TEST_ONLY') and config.get('purpose') != 'TEST_ONLY':
        raise ValueError('TEST_ONLY transport cannot serve an operational actor')
    exact = {'max_input_tokens': 4096, 'max_new_tokens': 2048, 'context_tokens': 8192,
             'raw_output_max_bytes': 131072, 'timeout_seconds': 600, 'threads': 2, 'interop_threads': 1}
    if any(type(config.get(key)) is not int or config[key] != value for key, value in exact.items()) or not config.get('runtime_contract'):
        raise ValueError('generator requires the exact reviewed bounded runtime profile')


def _backend(config: dict[str, Any]) -> tuple[Path, Path]:
    _profile(config)
    backend = config.get('backend')
    if not isinstance(backend, dict) or set(backend) != {'script', 'sha256', 'python', 'python_sha256'}:
        raise ValueError('no pinned reviewed backend/executable')
    paths = []
    for key, pin in (('python', 'python_sha256'), ('script', 'sha256')):
        path = Path(backend[key])
        if (not path.is_absolute() or key == 'script' and path.is_symlink() or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != backend[pin]):
            raise ValueError('actual backend/executable source changed')
        paths.append(path)
    return paths[0], paths[1]


def freeze_actor(config: dict[str, Any]) -> Actor:
    """Freeze source/config only. Real target, authority and capacity remain prerequisites."""
    from . import qualification, substrate_generation, substrate_recipe_basis, substrate_generator
    from . import model, repo, schema, reference_cases, blob, substrate
    executable, backend = _backend(config)
    support = [Path(module.__file__) for module in (substrate_generation, substrate_recipe_basis,
        substrate_generator, model, repo, schema, reference_cases, blob, substrate) if module.__file__]
    if config['profile'] == 'substrate-linux-bf16-v1':
        paired = Path(__file__).with_name('linux_candidate.py')
        if not paired.is_file():
            raise ValueError('reviewed paired Linux backend source is unavailable; no operational actor frozen')
        linux_candidate = importlib.import_module('twin.linux_candidate')
        support.extend(linux_candidate.support_sources(config))
    return qualification.Actor.freeze(run, parse, config, support=(*support, executable, backend,
        Path(__file__).with_name('substrate-candidate-prompt.txt')))


def _test_pair(request: dict[str, Any], config: dict[str, Any]) -> RuntimeResult:
    """Only explicit TEST_ONLY executables exercise transport; no runtime is supplied."""
    executable, backend = _backend(config)
    deadline = time.monotonic() + config['timeout_seconds']
    retained = b''
    observed: dict[str, Any] = {}
    observations: dict[str, Any] = {}
    try:
        for mode in ('--preflight', '--generate'):
            process = subprocess.Popen([str(executable), str(backend), mode], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
                env={**os.environ, 'TOKENIZERS_PARALLELISM': 'false', **{key: '2' for key in
                    ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')}})
            try:
                stdout, stderr = process.communicate(canonical(request), timeout=max(.001, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
                raise ValueError('TEST_ONLY paired backend timed out') from None
            if process.returncode or len(stdout) > config['raw_output_max_bytes'] * 2:
                raise ValueError('TEST_ONLY backend envelope failed or exceeded bound')
            value = json.loads(stdout)
            if mode == '--preflight':
                count = value.get('input_tokens')
                if type(count) is not int or not 0 < count <= config['max_input_tokens']:
                    raise ValueError('input token preflight exceeds frozen bound; no generation')
                observations['input_tokens'] = count
            else:
                retained = base64.b64decode(value['raw_base64'], validate=True)
                observed = value.get('observed_runtime', {})
                count = value.get('output_tokens')
                observations.update({'output_tokens': count, 'stop_reason': value.get('stop_reason')})
                if (len(retained) > config['raw_output_max_bytes'] or type(count) is not int
                        or not 0 <= count <= config['max_new_tokens'] or value.get('stop_reason') != 'eos'):
                    raise ValueError('output bound/termination failed; original bytes retained')
        return RuntimeResult(retained, observed, observations)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return RuntimeResult(retained, observed, observations, str(exc))


def run(payload: str, config: dict[str, Any]) -> RuntimeResult:
    _profile(config)
    request = {'input': payload, 'prompt_utf8': render_prompt(payload, config).decode('utf-8')}
    if config['profile'] == 'TEST_ONLY-substrate-transport/v1':
        return _test_pair(request, config)
    # The shared protected route owns fresh paired preflight/generation, capacity, authority,
    # offline cage, deadline and partial capture. No helper/model/runtime call lives here.
    linux_candidate = importlib.import_module('twin.linux_candidate')
    return linux_candidate.invoke_pair(request, config)
