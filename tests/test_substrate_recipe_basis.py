"""New tiny TEST_ONLY schedules, not qualification examples."""
import copy
import json

import pytest

from twin import substrate_candidate as candidate, substrate_recipe_basis as basis
from twin.reference_cases import source_record


RECIPE = ('schema: twin.substrate-recipe/v1\nid: TEST_ONLY-recipe\nseed: 7\n'
    'model_version: TEST_ONLY-actor\ntemplates:\n- TEST_ONLY cue amber\n- TEST_ONLY cue violet\n'
    'planted_signals:\n- TEST_ONLY marker cedar\n- TEST_ONLY marker cedar\n')


def example():
    answer = {'channels': {'events': ['TEST_ONLY marker cedar', '[other] TEST_ONLY marker cedar', 'TEST_ONLY ordinary a', 'TEST_ONLY ordinary b'],
        'communications': ['TEST_ONLY ordinary c'], 'hr': ['TEST_ONLY ordinary d'], 'telemetry': ['TEST_ONLY ordinary e']},
        'plants': [{'channel': 'events', 'index': i, 'signal': 'TEST_ONLY marker cedar'} for i in (0, 1)]}
    stated_basis = {'recipe_quotes': [{'field': 'templates', 'quote': '- TEST_ONLY cue amber\n- TEST_ONLY cue violet'},
        {'field': 'planted_signals', 'quote': '- TEST_ONLY marker cedar'}],
        'occurrences': [{**plant, 'line_quote': answer['channels']['events'][plant['index']]} for plant in answer['plants']],
        'counts': {'channel_lines': {'events': 4, 'communications': 1, 'hr': 1, 'telemetry': 1},
            'total_lines': 7, 'plant_count': 2, 'mundane_lines': 5}}
    intent = {'id': 'TEST_ONLY-recipe', 'seed': 7, 'templates': ['TEST_ONLY cue amber', 'TEST_ONLY cue violet'],
        'planted_signals': ['TEST_ONLY marker cedar'] * 2}
    reference = basis.reference_basis(RECIPE, {'TEST_ONLY': 'authentic host context'},
        source_record(json.dumps(intent).encode(), 'TEST_ONLY-independent-intent', 'v1'))
    raw = json.dumps({'answer': answer, 'basis': stated_basis}).encode()
    return candidate.parse(raw, {}), reference


def test_basis_checks_actual_recipe_support_occurrences_and_counts():
    actual, reference = example()
    assert basis.check(actual.basis, reference)


@pytest.mark.parametrize('mutation', ['counts', 'boolean count', 'missing occurrence', 'foreign quote',
    'irrelevant quote', 'wrong line', 'foreign intent', 'stale raw recipe', 'missing basis'])
def test_correct_schedule_cannot_credit_fabricated_or_irrelevant_basis(mutation):
    actual, reference = example()
    value = copy.deepcopy(actual.basis)
    if mutation == 'counts': value['model_basis']['counts']['total_lines'] = 100
    elif mutation == 'boolean count': value['model_basis']['counts']['plant_count'] = True
    elif mutation == 'missing occurrence': value['model_basis']['occurrences'].pop()
    elif mutation == 'foreign quote': value['model_basis']['recipe_quotes'][0]['quote'] = 'TEST_ONLY unseen cue'
    elif mutation == 'irrelevant quote': value['model_basis']['recipe_quotes'][0] = {'field': 'templates', 'quote': 'TEST_ONLY-recipe'}
    elif mutation == 'wrong line': value['model_basis']['occurrences'][0]['line_quote'] = 'TEST_ONLY invented line'
    elif mutation == 'foreign intent': reference['intent']['sha256'] = '0' * 64
    elif mutation == 'stale raw recipe': reference['recipe']['sha256'] = '0' * 64
    else: value = None
    assert not basis.check(value, reference)


@pytest.mark.parametrize('text', [RECIPE.replace('seed: 7', 'seed: true'), RECIPE + 'hidden: label\n',
    RECIPE + 'seed: 8\n', RECIPE.replace('TEST_ONLY marker cedar', '  '),
    RECIPE.replace('templates:\n-', 'templates: 17\n# -')])
def test_trusted_recipe_reader_refuses_coercion_duplicate_and_unknown_fields(text):
    with pytest.raises(ValueError): basis.recipe_fields(text)


def test_actual_yaml_escaped_literals_remain_relevant_quotations():
    import yaml
    actual, _ = example()
    fields = basis.recipe_fields(RECIPE)
    fields['templates'] = ['TEST_ONLY caf\u00e9 cue']
    text = yaml.safe_dump(fields)
    intent = {key: fields[key] for key in ('id', 'seed', 'templates', 'planted_signals')}
    reference = basis.reference_basis(text, {}, source_record(json.dumps(intent).encode(), 'TEST_ONLY-intent', 'v1'))
    tree = yaml.compose(text)
    actual.basis['model_basis']['recipe_quotes'] = [{'field': key.value, 'quote': text[key.start_mark.index:value.end_mark.index]}
        for key, value in tree.value if key.value in ('templates', 'planted_signals')]
    assert basis.check(actual.basis, reference)
