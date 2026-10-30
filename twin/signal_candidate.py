"""Input-only signal adapter. No model runtime, provider or permission is installed here."""
from __future__ import annotations

import json
import hashlib
import base64
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from .qualification import canonical, Actor, RuntimeResult
from .skills import Stated
from .schema import STEEP


def _backend(config: dict[str, Any]) -> tuple[str, str]:
    if config.get('profile') is None and config.get('purpose') != 'TEST_ONLY':
        raise ValueError('unprotected host transport is TEST_ONLY; operational profile/authority required')
    if config.get('profile') is not None and config['profile'] != 'signal-linux-bf16-v1':
        raise ValueError('signal adapter requires its exact reviewed Linux profile')
    backend = config.get('backend')
    if not isinstance(backend, dict) or set(backend) != {'script', 'sha256', 'python', 'python_sha256'}:
        raise ValueError('no pinned reviewed target backend; actual runtime acquisition/measurement remains required')
    for name, pin in (('script', 'sha256'), ('python', 'python_sha256')):
        path = Path(backend[name])
        # Python installations commonly expose an executable symlink; its resolved bytes
        # are pinned, while the backend source itself must be an ordinary host file.
        if (not path.is_absolute() or name == 'script' and path.is_symlink() or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != backend[pin]):
            raise ValueError('actual host backend/executable changed')
    for field, maximum in (('max_input_tokens', 4096), ('max_new_tokens', 512), ('timeout_seconds', 900)):
        if type(config.get(field)) is not int or not 0 < config[field] <= maximum:
            raise ValueError('explicit bounded host profile required: ' + field)
    if config.get('threads') != 2 or config.get('interop_threads') != 1 or not config.get('runtime_contract'):
        raise ValueError('explicit two-thread host runtime contract required')
    return backend['python'], backend['script']


def freeze_actor(config: dict[str, Any]) -> Actor:
    """Bind the whole adapter/config/support computation; this performs no inference."""
    from . import qualification as q, signal_inputs, basis_assessment, qualified_signals
    executable, backend = _backend(config)
    support: list[Path] = []
    if config.get('profile') is not None:
        from .linux_candidate import support_sources
        if config['profile'] != 'signal-linux-bf16-v1':
            raise ValueError('signal adapter requires its exact reviewed Linux profile')
        support.extend(support_sources(config))
    for module in (signal_inputs, basis_assessment, qualified_signals):
        if module.__file__ is None:
            raise ValueError('host support module has no source file')
        support.append(Path(module.__file__))
    return q.Actor.freeze(run, parse, config, support=(*support, Path(backend), Path(executable),
        Path(__file__).with_name('signal-candidate-prompt.txt')))


def run(payload: dict[str, Any], config: dict[str, Any]) -> RuntimeResult:
    """Transport to a pinned HOST program, never interpret identity fields in model output.

    The concrete Linux profile uses one protected paired invocation. Its actual
    assets/runtime/resources remain unmeasured. A real backend must earn independent
    source/cage/assets/resource review and actual target measurement before registration.
    Preflight must tokenize without loading a model; generation must observe the actual
    loaded build/assets/dtype/device and process-resource/cage facts. Controlled TEST_ONLY
    subprocesses prove this transport, not those outstanding real backend obligations.
    """
    if config.get('profile') is not None:
        if config['profile'] != 'signal-linux-bf16-v1':
            raise ValueError('signal adapter requires its exact reviewed Linux profile')
        from .linux_candidate import invoke_pair
        return invoke_pair({'input': payload, 'prompt_utf8': render_prompt(payload, config).decode()}, config)
    executable, backend = _backend(config)
    prompt = render_prompt(payload, config)
    request = canonical({'input': payload, 'prompt_utf8': prompt.decode(), 'config': config})
    deadline = time.monotonic() + config['timeout_seconds']
    def call(mode: str) -> dict[str, Any]:
        environment = dict(os.environ)
        environment.update({key: '2' for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')})
        environment['TOKENIZERS_PARALLELISM'] = 'false'
        process = subprocess.Popen([executable, backend, mode], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True, env=environment)
        try:
            stdout, stderr = process.communicate(request, timeout=max(0.001, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise ValueError('host backend timed out; no complete candidate envelope available') from None
        if process.returncode:
            raise ValueError('host backend failed without complete candidate bytes: ' + stderr.decode(errors='replace')[-1000:])
        value = json.loads(stdout)
        if not isinstance(value, dict):
            raise ValueError('host backend protocol object required')
        return value
    preflight = call('--preflight')
    count = preflight.get('input_tokens')
    if type(count) is not int or not 0 < count <= config['max_input_tokens']:
        raise ValueError('input token preflight exceeds the frozen bound; no truncation/generation')
    result = call('--generate')
    raw = base64.b64decode(result['raw_base64'], validate=True)
    observed = result.get('observed_runtime')
    if not isinstance(observed, dict):
        observed = {}
    observations = {'input_tokens': count, 'output_tokens': result.get('output_tokens'),
        'stop_reason': result.get('stop_reason'), 'host_elapsed_seconds': config['timeout_seconds'] - (deadline - time.monotonic()),
        'backend_observations': result.get('observations'), 'backend_source_sha256': config['backend']['sha256']}
    output_count = result.get('output_tokens')
    failure = None
    if (type(output_count) is not int or not 0 <= output_count <= config['max_new_tokens']
            or result.get('stop_reason') != 'eos'):
        failure = 'host output bound/termination not satisfied; actual raw bytes retained'
    return RuntimeResult(raw, observed, observations, failure)


def render_prompt(payload: dict[str, Any], config: dict[str, Any]) -> bytes:
    """Render the predeclared input-only template; never shorten the task to fit a cap."""
    from .signal_inputs import binding_context
    binding_context(payload)
    template = Path(__file__).with_name('signal-candidate-prompt.txt').read_bytes()
    if hashlib.sha256(template).hexdigest() != config.get('prompt_sha256'):
        raise ValueError('frozen signal prompt source changed')
    return template.replace(b'{{INPUT_JSON}}', canonical(payload))


def evidence_text(basis: Any) -> str:
    """Lossless schema-text projection of an actual basis, never newly authored reasoning."""
    return basis if isinstance(basis, str) else canonical(basis).decode('utf-8')


def quote_integrity(stated: Stated, payload: dict[str, Any]) -> bool:
    """Literal input witnesses are necessary, never a semantic applicability judgement."""
    def strings(value: Any) -> list[str]:
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            return [text for item in value.values() for text in strings(item)]
        if isinstance(value, list):
            return [text for item in value for text in strings(item)]
        return []
    try:
        basis = stated.basis
        selected = next(item for item in payload['candidates']
                        if item['id'] == stated.answer['claim']['component'])
        statement = [payload['statement'], *payload.get('source_context', {}).get('excerpts', [])]
        definitions = [selected['name'], *strings(selected['definition'])]
        return (isinstance(basis, dict) and isinstance(basis.get('reason'), str) and bool(basis['reason'].strip())
            and all(isinstance(basis.get(field), list) and bool(basis[field])
                    and all(isinstance(quote, str) and bool(quote)
                            and any(quote in text for text in texts) for quote in basis[field])
                    for field, texts in (('statement_quotes', statement), ('component_quotes', definitions))))
    except (KeyError, TypeError, StopIteration):
        return False


def parse(raw: bytes, config: dict[str, Any]) -> Stated:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError('duplicate response key')
            result[key] = item
        return result
    text = raw.decode('utf-8')
    terminal = config.get('terminal_token')
    if terminal:
        if terminal != '<|im_end|>':
            raise ValueError('unsupported terminal token')
        if text.endswith(terminal):
            text = text[:-len(terminal)]
    value = json.loads(text, object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError('one response object required')
    if set(value) == {'decline'}:
        if not isinstance(value['decline'], str) or not value['decline'].strip():
            raise ValueError('decline needs its factual reason')
        return Stated(None, value)
    if (set(value) not in ({'steep', 'component'}, {'steep', 'component', 'basis'})
            or not isinstance(value['steep'], str) or value['steep'] not in STEEP
            or not isinstance(value['component'], str) or not value['component'].strip()):
        raise ValueError('actual response must state an existing STEEP and selected component')
    if 'basis' in value:
        basis = value['basis']
        if (not isinstance(basis, dict) or set(basis) != {'statement_quotes', 'component_quotes', 'reason'}
                or not isinstance(basis['reason'], str)
                or any(not isinstance(basis[field], list)
                       or any(not isinstance(quote, str) for quote in basis[field])
                       for field in ('statement_quotes', 'component_quotes'))):
            raise ValueError('present basis must preserve actual quote lists and reason')
    return Stated({'steep': value['steep'], 'claim': {'kind': 'binding',
        'component': value['component'], 'evidence_grade': 5,
        'claimed_by': 'signal-classify candidate (skill)'}}, value.get('basis'))
