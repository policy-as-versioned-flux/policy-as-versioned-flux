"""Independent structural attribution checker; no generation or runtime call."""
from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

import yaml

from .qualification import canonical, digest
from .reference_cases import source_record
from .substrate import RECIPE_SCHEMA
from .substrate_generator import CHANNELS, MIN_MUNDANE_FRACTION, scorer


class _RecipeLoader(yaml.SafeLoader):
    def compose_node(self, parent: Any, index: Any) -> Any:
        if self.check_event(yaml.events.AliasEvent):
            raise ValueError('recipe aliases are not accepted')
        return super().compose_node(parent, index)


def _mapping(loader: _RecipeLoader, node: yaml.MappingNode) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError('duplicate or nonstring recipe key')
        result[key] = loader.construct_object(value_node)
    return result


_RecipeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def recipe_fields(text: str) -> dict[str, Any]:
    """Trusted closed-shape intake before the legacy coercive recipe loader."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError('recipe YAML string required')
    try:
        value = yaml.load(text, Loader=_RecipeLoader)
    except yaml.YAMLError as exc:
        raise ValueError('invalid recipe YAML') from exc
    if (not isinstance(value, dict) or set(value) != {
            'schema', 'id', 'seed', 'templates', 'model_version', 'planted_signals'}
            or value['schema'] != RECIPE_SCHEMA or type(value['seed']) is not int
            or any(not isinstance(value[key], str) or not value[key].strip() for key in ('id', 'model_version'))):
        raise ValueError('exact typed versioned recipe required')
    for key in ('templates', 'planted_signals'):
        if (not isinstance(value[key], list) or key == 'templates' and not value[key]
                or any(not isinstance(item, str) or not item.strip() or '\n' in item or '\r' in item
                       for item in value[key])):
            raise ValueError('recipe must declare literal nonblank single-line ' + key)
    return value


def expected_for(text: str) -> dict[str, Any]:
    recipe = recipe_fields(text)
    return {'channels': list(CHANNELS), 'planted_signals': recipe['planted_signals'],
            'min_mundane_fraction': MIN_MUNDANE_FRACTION}


def source_bytes(record: Any) -> bytes:
    if (not isinstance(record, dict) or set(record) != {
            'identity', 'version', 'sha256', 'bytes', 'content_base64'}
            or any(not isinstance(record[key], str) or not record[key] for key in ('identity', 'version'))):
        raise ValueError('exact original source record required')
    raw = base64.b64decode(record['content_base64'], validate=True)
    if type(record['bytes']) is not int or len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('original source bytes/hash differ')
    return raw


def reference_basis(text: str, context: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
    """Bind authentic host sources, never construct the model's actual explanation."""
    recipe = recipe_fields(text)
    authored = json.loads(source_bytes(intent))
    if (not isinstance(authored, dict) or any(authored.get(key) != recipe[key]
            for key in ('id', 'seed', 'templates', 'planted_signals'))):
        raise ValueError('independent intent differs from actual recipe')
    return {'schema': 'twin.substrate-recipe-basis/v1',
        'recipe': source_record(text.encode(), 'raw-substrate-recipe:' + recipe['id'], recipe['model_version']),
        'intent': intent, 'context_sha256': digest(context),
        'source_hashes': {'recipe': hashlib.sha256(text.encode()).hexdigest(), 'intent': intent['sha256']}}


def check(actual: Any, reference: Any) -> bool:
    """A relevant quotation, occurrence and arithmetic are all actual model obligations."""
    try:
        if (not isinstance(reference, dict) or reference.get('schema') != 'twin.substrate-recipe-basis/v1'
                or not isinstance(reference.get('context_sha256'), str) or len(reference['context_sha256']) != 64):
            return False
        text = source_bytes(reference['recipe']).decode('utf-8')
        recipe = recipe_fields(text)
        intent = json.loads(source_bytes(reference['intent']))
        if (any(intent.get(key) != recipe[key] for key in ('id', 'seed', 'templates', 'planted_signals'))
                or any(reference['source_hashes'].get(key) != reference[key]['sha256'] for key in ('recipe', 'intent'))):
            return False
        if (not isinstance(actual, dict) or set(actual) != {'model_basis', 'observed_answer', 'raw_output_sha256'}
                or not isinstance(actual['raw_output_sha256'], str) or len(actual['raw_output_sha256']) != 64):
            return False
        answer, model = actual['observed_answer'], actual['model_basis']
        if not scorer(answer, expected_for(text)) or not isinstance(model, dict) or set(model) != {'recipe_quotes', 'occurrences', 'counts'}:
            return False
        quotes = model['recipe_quotes']
        if not isinstance(quotes, list) or not quotes:
            return False
        tree = yaml.compose(text)
        spans = {key.value: text[key.start_mark.index:value.end_mark.index] for key, value in tree.value}
        literals = {key.value: [(node.value, text[node.start_mark.index:node.end_mark.index]) for node in value.value]
                    for key, value in tree.value if key.value in ('templates', 'planted_signals')}
        by_field: dict[str, list[str]] = {'templates': [], 'planted_signals': []}
        for quote in quotes:
            if (not isinstance(quote, dict) or set(quote) != {'field', 'quote'}
                    or quote['field'] not in by_field or not isinstance(quote['quote'], str)
                    or not quote['quote'].strip() or quote['quote'] not in spans[quote['field']]):
                return False
            by_field[quote['field']].append(quote['quote'])
        for field in by_field:
            if not by_field[field] or any(not any(item in quote or literal in quote for quote in by_field[field])
                                          for item, literal in literals[field]):
                return False
        if not recipe['planted_signals'] and not any('[]' in quote for quote in by_field['planted_signals']):
            return False
        occurrences = model['occurrences']
        if not isinstance(occurrences, list) or len(occurrences) != len(answer['plants']):
            return False
        observed = []
        for row in occurrences:
            if (not isinstance(row, dict) or set(row) != {'channel', 'index', 'signal', 'line_quote'}
                    or type(row['index']) is not int or row['index'] < 0
                    or row['line_quote'] != answer['channels'][row['channel']][row['index']]):
                return False
            observed.append({key: row[key] for key in ('channel', 'index', 'signal')})
        if sorted(map(canonical, observed)) != sorted(map(canonical, answer['plants'])):
            return False
        channel_lines = {key: len(answer['channels'][key]) for key in CHANNELS}
        total, planted = sum(channel_lines.values()), len(answer['plants'])
        counts = model['counts']
        expected = {'channel_lines': channel_lines, 'total_lines': total, 'plant_count': planted, 'mundane_lines': total - planted}
        if (not isinstance(counts, dict) or set(counts) != set(expected)
                or not isinstance(counts['channel_lines'], dict) or set(counts['channel_lines']) != set(CHANNELS)
                or any(type(value) is not int for value in counts['channel_lines'].values())
                or any(type(counts[key]) is not int for key in ('total_lines', 'plant_count', 'mundane_lines'))):
            return False
        return counts == expected
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, yaml.YAMLError):
        return False
