"""TEST_ONLY parser/transport controls, not candidate performance."""
import hashlib
import json

import pytest

from twin import substrate_candidate as candidate
from twin.skills import Stated


def test_raw_answer_and_actual_basis_are_preserved_without_filling_content():
    raw = b'{"answer":{"channels":{},"plants":[]},"basis":{"counts":"TEST_ONLY wrong"}}'
    stated = candidate.parse(raw, {})
    assert stated.answer == {'channels': {}, 'plants': []}
    assert stated.basis == {'model_basis': {'counts': 'TEST_ONLY wrong'},
        'observed_answer': stated.answer, 'raw_output_sha256': hashlib.sha256(raw).hexdigest()}
    assert candidate.parse(b'{"answer":17}', {}) == Stated(17, None)
    assert candidate.parse(b'{"answer":{},"basis":null}', {}) == Stated({}, None)


@pytest.mark.parametrize('raw', [b'```json\n{"answer":{}}\n```', b'prefix {"answer":{}}',
    b'{"answer":{},"answer":17}', b'{"answer":{},"other":1}', b'[]', b'{"answer":NaN}', b'\xff'])
def test_parser_refuses_salvage_duplicate_keys_and_non_json_numbers(raw):
    with pytest.raises((ValueError, UnicodeError)):
        candidate.parse(raw, {})


def test_only_the_frozen_exact_terminal_may_be_removed_and_original_hash_survives():
    raw = b'{"answer":{},"basis":{}}<|im_end|>'
    assert candidate.parse(raw, {'terminal_token': '<|im_end|>'}).basis['raw_output_sha256'] == hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError):
        candidate.parse(raw + b'\n', {'terminal_token': '<|im_end|>'})
    with pytest.raises(ValueError):
        candidate.parse(raw, {'terminal_token': 'other'})


def test_decline_retains_the_models_reason_without_an_answer():
    assert candidate.parse(b'{"decline":"TEST_ONLY cannot complete"}', {}) == Stated(None, {'decline': 'TEST_ONLY cannot complete'})


def test_pinned_test_only_transport_preserves_one_raw_capture_and_never_pads(tmp_path):
    import sys
    from pathlib import Path
    script = tmp_path / 'TEST_ONLY-backend.py'
    script.write_text('import sys,json,base64\nr=json.load(sys.stdin)\n'
        'v={"input_tokens":30} if sys.argv[1]=="--preflight" else '
        '{"raw_base64":base64.b64encode(b\'{"answer":{},"basis":null}\').decode(),'
        '"observed_runtime":{"TEST_ONLY":"observed"},"output_tokens":8,"stop_reason":"eos"}\n'
        'print(json.dumps(v))\n')
    config = {'purpose': 'TEST_ONLY', 'profile': 'TEST_ONLY-substrate-transport/v1',
        'backend': {'script': str(script), 'sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
            'python': sys.executable, 'python_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
        'runtime_contract': {'TEST_ONLY': 'observed'}, 'max_input_tokens': 4096, 'max_new_tokens': 2048,
        'context_tokens': 8192, 'raw_output_max_bytes': 131072, 'timeout_seconds': 600,
        'threads': 2, 'interop_threads': 1, 'terminal_token': '<|im_end|>',
        'prompt_sha256': hashlib.sha256(Path(candidate.__file__).with_name('substrate-candidate-prompt.txt').read_bytes()).hexdigest()}
    recipe = 'schema: twin.substrate-recipe/v1\nid: TEST_ONLY\nseed: 1\nmodel_version: TEST_ONLY\ntemplates: [TEST_ONLY cue]\nplanted_signals: []\n'
    actor = candidate.freeze_actor(config)
    output = actor.invoke(recipe)
    assert output.raw == b'{"answer":{},"basis":null}'
    assert output.stated == Stated({}, None)
    assert output.failure is None
