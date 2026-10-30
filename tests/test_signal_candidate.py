"""Authored TEST_ONLY literals exercise parsing, never real candidate competence."""
import json
import pytest

from twin import signal_candidate as candidate
from twin.signal_classify import scorer
from twin.skills import Stated, evaluate


def test_flat_binding_and_actual_structured_basis_reach_the_existing_scorer():
    raw = b'{"steep":"social","component":"TEST_ONLY-support","basis":{"statement_quotes":["staff ask"],"component_quotes":["support"],"reason":"Staff ask support, rather than the records store."}}'
    stated = candidate.parse(raw, {})
    assert stated.answer['claim']['component'] == 'TEST_ONLY-support'
    assert stated.answer['claim']['evidence_grade'] == 5
    assert stated.basis == json.loads(raw)['basis']
    result = evaluate('signal-classify', lambda _: stated, [{'id': 'TEST_ONLY-one', 'input': {},
        'expected': {'steep': 'social', 'component': 'TEST_ONLY-support'}, 'basis': stated.basis}], scorer=scorer)
    assert result.items[0].verdict == 'right'
    assert candidate.evidence_text(stated.basis) == '{"component_quotes":["support"],"reason":"Staff ask support, rather than the records store.","statement_quotes":["staff ask"]}'


def test_decline_and_absent_basis_are_preserved_without_inventing_support():
    assert candidate.parse(b'{"decline":"Two definitions fit equally."}', {}) == Stated(None, {'decline': 'Two definitions fit equally.'})
    assert candidate.parse(b'{"steep":"social","component":"TEST_ONLY-support"}', {}).basis is None


@pytest.mark.parametrize('text', [
    '{"steep":"social","steep":"political","component":"x"}',
    '{"steep":"social","component":"x","grade":1}',
    '{"steep":"alien","component":"x"}',
    '{"steep":"social","component":""}',
    '{"steep":"social","component":"x","basis":"invented fallback"}',
    '{"steep":"social","component":"x","basis":{"statement_quotes":"quote","component_quotes":[],"reason":"r"}}',
    '{"decline":""}', '{"decline":"no","component":"x"}',
    '[]', '{}', '{"steep":"social","component":"x"} trailing',
])
def test_parser_refuses_malformed_or_identity_repairing_output(text):
    with pytest.raises(ValueError):
        candidate.parse(text.encode(), {})


def test_only_the_frozen_terminal_token_can_be_removed():
    raw = b'{"steep":"social","component":"x"}<|im_end|>'
    with pytest.raises(ValueError):
        candidate.parse(raw, {})
    assert candidate.parse(raw, {'terminal_token': '<|im_end|>'}).answer['claim']['component'] == 'x'


def full_input():
    from bench.signal_contract_controls import choices
    from test_source_metadata import acquire_fixture
    _, acquired, _ = acquire_fixture(statement_text='TEST_ONLY proposal, not an event')
    public = acquired.public
    return {'statement': public['statement']['text'], 'source': public['source']['display_source'],
        'source_context': {**{key: public['source'][key] for key in ('url', 'version', 'family')},
            'as_of': '2026-10-30', 'metadata': public,
            'visible_excerpt_ids': [item['id'] for item in public['visible_excerpts']]},
        'model_context': {'organisation': 'driftwood', 'domain': 'TEST_ONLY domain', 'capability': 'TEST_ONLY task',
            'frame': 'TEST_ONLY primary subject', 'as_of': '2026-10-30', 'pins': {'TEST_ONLY': 'pins'}},
        'candidates': choices()}


def test_prompt_preserves_all_twenty_original_definitions_and_refuses_hidden_fields():
    from pathlib import Path
    import hashlib
    template = Path(candidate.__file__).with_name('signal-candidate-prompt.txt').read_bytes()
    config = {'prompt_sha256': hashlib.sha256(template).hexdigest()}
    payload = full_input()
    prompt = candidate.render_prompt(payload, config)
    assert json.loads(prompt.decode().split('INPUT:\n', 1)[1]) == payload
    assert 'TEST_ONLY choice meaning 19' in prompt.decode()
    with pytest.raises(ValueError, match='input'):
        candidate.render_prompt({**payload, 'expected': {'component': 'TEST_ONLY-19'}}, config)
    with pytest.raises(ValueError, match='twenty'):
        candidate.render_prompt({**payload, 'candidates': payload['candidates'][:5]}, config)


def test_literal_quotes_are_necessary_but_do_not_attest_semantic_entailment():
    payload = full_input()
    raw = b'{"steep":"political","component":"TEST_ONLY-19","basis":{"statement_quotes":["proposal, not an event"],"component_quotes":["Choice 19"],"reason":"It already happened to this company."}}'
    stated = candidate.parse(raw, {})
    assert candidate.quote_integrity(stated, payload)
    result = evaluate('signal-classify', lambda _: stated, [{'id': 'TEST_ONLY-tense-control',
        'input': payload, 'expected': {'steep': 'political', 'component': 'TEST_ONLY-19'},
        'basis': {'TEST_ONLY': 'hidden reference withheld from semantic reviewer'}}],
        scorer=scorer, contextual_basis_scorer=lambda item_id, actual, reference: False)
    assert result.items[0].verdict == 'wrong-basis'
    stated.basis['statement_quotes'] = ['an event definitely happened']
    assert not candidate.quote_integrity(stated, payload)


def test_pinned_host_subprocess_preflight_precedes_generation_and_response_identity_is_not_runtime(tmp_path):
    import hashlib
    import sys
    from pathlib import Path
    from twin import qualification as q
    backend = tmp_path / 'TEST_ONLY_backend.py'
    backend.write_text('''import json,sys,base64
value=json.load(sys.stdin)
if sys.argv[1]=='--preflight':
 print(json.dumps({'input_tokens':value['config']['TEST_ONLY_input_tokens']}))
else:
 raw=b'{"steep":"social","component":"TEST_ONLY-19","basis":{"statement_quotes":["TEST_ONLY proposal"],"component_quotes":["Choice 19"],"reason":"TEST_ONLY"}}'
 print(json.dumps({'raw_base64':base64.b64encode(raw).decode(),'output_tokens':value['config'].get('TEST_ONLY_output_tokens',40),'stop_reason':'eos',
  'observed_runtime':{'build':value['config'].get('TEST_ONLY_build','TEST_ONLY actual host backend; not response identity')}}))
''')
    template = Path(candidate.__file__).with_name('signal-candidate-prompt.txt')
    config = {'purpose': 'TEST_ONLY', 'prompt_sha256': hashlib.sha256(template.read_bytes()).hexdigest(),
        'backend': {'script': str(backend), 'sha256': hashlib.sha256(backend.read_bytes()).hexdigest(),
                    'python': sys.executable, 'python_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
        'max_input_tokens': 4096, 'max_new_tokens': 512, 'timeout_seconds': 5,
        'threads': 2, 'interop_threads': 1, 'TEST_ONLY_input_tokens': 290,
        'runtime_contract': {'build': 'TEST_ONLY actual host backend; not response identity'}}
    actor = candidate.freeze_actor(config)
    output = actor.invoke(full_input())
    assert output.failure is None
    assert output.stated.answer['claim']['component'] == 'TEST_ONLY-19'
    assert json.loads(output.packet)['observed_runtime'] == config['runtime_contract']
    config['TEST_ONLY_input_tokens'] = 4097
    rejected = candidate.freeze_actor(config).invoke(full_input())
    assert 'input token' in rejected.failure
    assert rejected.raw == b''
    assert actor.model_version != candidate.freeze_actor(config).model_version
    config['TEST_ONLY_input_tokens'] = 290
    config['TEST_ONLY_output_tokens'] = 513
    bounded = candidate.freeze_actor(config).invoke(full_input())
    assert bounded.raw.startswith(b'{"steep":') and 'output bound' in bounded.failure
    assert json.loads(bounded.packet)['observations']['output_tokens'] == 513
    config['TEST_ONLY_output_tokens'] = 40
    config['TEST_ONLY_build'] = 'different actual backend build'
    mismatch = candidate.freeze_actor(config).invoke(full_input())
    assert mismatch.raw.startswith(b'{"steep":') and 'runtime differs' in mismatch.failure


def test_real_signal_profile_cannot_fall_back_to_unprotected_two_call_transport(tmp_path):
    import hashlib
    import sys
    from pathlib import Path
    backend = tmp_path/'TEST_ONLY_never_run.py'
    marker = tmp_path/'TEST_ONLY_was_run'
    backend.write_text('from pathlib import Path\nPath('+repr(str(marker))+').touch()\n')
    template = Path(candidate.__file__).with_name('signal-candidate-prompt.txt')
    config = {'profile': 'signal-linux-bf16-v1', 'purpose': 'TEST_ONLY',
        'prompt_sha256': hashlib.sha256(template.read_bytes()).hexdigest(),
        'backend': {'script': str(backend), 'sha256': hashlib.sha256(backend.read_bytes()).hexdigest(),
            'python': sys.executable, 'python_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
        'max_input_tokens':4096,'max_new_tokens':512,'timeout_seconds':900,
        'threads':2,'interop_threads':1,'runtime_contract': {'TEST_ONLY':'unacquired'}}
    with pytest.raises(ValueError, match='protected host authority'):
        candidate.run(full_input(), config)
    assert not marker.exists()


def test_omitted_operational_profile_cannot_reuse_the_test_only_transport(tmp_path):
    import hashlib
    import sys
    from pathlib import Path
    backend = tmp_path/'TEST_ONLY_operational_fallback.py'
    marker = tmp_path/'TEST_ONLY_fallback_was_run'
    backend.write_text('import json,sys\nfrom pathlib import Path\nPath('+repr(str(marker))+').touch()\n'
        'json.load(sys.stdin)\n'
        'print(json.dumps({\"input_tokens\":1} if sys.argv[1]==\"--preflight\" else '
        '{\"raw_base64\":\"e30=\",\"output_tokens\":1,\"stop_reason\":\"eos\",\"observed_runtime\":{\"TEST_ONLY\":True}}))\n')
    template = Path(candidate.__file__).with_name('signal-candidate-prompt.txt')
    config = {'purpose':'operational', 'prompt_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),
        'backend':{'script':str(backend),'sha256':hashlib.sha256(backend.read_bytes()).hexdigest(),
            'python':sys.executable,'python_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()},
        'max_input_tokens':4096,'max_new_tokens':512,'timeout_seconds':5,'threads':2,'interop_threads':1,
        'runtime_contract':{'TEST_ONLY':True}}
    with pytest.raises(ValueError, match='TEST_ONLY'):
        candidate.run(full_input(), config)
    assert not marker.exists()
    with pytest.raises(ValueError, match='reviewed Linux profile'):
        candidate.run(full_input(), {'purpose': 'TEST_ONLY', 'profile': 'unknown-linux-profile'})
