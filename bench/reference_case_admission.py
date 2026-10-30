"""Offline custody demonstration using already acquired references, never model qualification.

Run from a source checkout with PYTHONPATH=. and --source-root pointing to the checkout
holding the frozen research artifacts. Uses the ordinary evaluator with a disclosed TEST_ONLY
literal answer. No model, provider, score recorder or permission API is invoked.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from twin.reference_cases import admit_reference, binding_for, source_record
from twin.skills import Stated, evaluate
from twin import evolution_judge


VERSION = '98a6c88922c69dea2186fd1bebeb1751ce475c8a'


def read_json(path: Path) -> Any:
    return json.loads(path.read_bytes())


def capture(path: Path, identity: str | None = None, version: str | None = None) -> dict[str, Any]:
    content = path.read_bytes()
    return source_record(content, identity or str(path), version or 'sha256:' + hashlib.sha256(content).hexdigest())


def checked_capture(binding: dict[str, Any]) -> dict[str, Any]:
    record = capture(Path(binding['path']))
    if record['sha256'] != binding['sha256'] or record['bytes'] != binding['bytes']:
        raise ValueError('acquired source drift: ' + binding['path'])
    return record


def demonstrate(source_root: Path, output: Path) -> dict[str, Any]:
    research = source_root / '.scratch/ecosystem/research'
    author = research / 'resume-20261028-case-admission/author-v1'
    published = research / 'resume-20261028-independent-label-sources'
    row = read_json(author / 'CASES.json')[0]
    bindings = read_json(author / 'SOURCE-QUOTE-CELL-BINDINGS.json')['quotes']
    provenance = row['provenance']
    cell = next(c for c in read_json(published / 'published-coordinate-register-v1/COORDINATES.json')
                if c['id'] == provenance['register_cell_id'])
    sources = {'map': checked_capture(provenance['source']['raw']),
               'source-receipt': checked_capture(provenance['source']['receipt']),
               'authored-cases': capture(author / 'CASES.json'),
               'selection-ledger': capture(author / 'DECISIONS.json'),
               'withheld-ledger': capture(author / 'WITHHELD.json'),
               'original-bases': capture(author / 'BASES.json'),
               'original-bindings': capture(author / 'SOURCE-QUOTE-CELL-BINDINGS.json'),
               'original-exposure': capture(author / 'ACK.json')}
    raw = base64.b64decode(sources['map']['content_base64'])
    line = raw.splitlines(keepends=True)[cell['original_line_number'] - 1]
    # Independent frozen literal source check; no new coordinate is authored.
    coordinates = re.search(rb'\[([^,]+),\s*([^]]+)\]', line)
    if (line.decode().strip() != cell['original_line'] or coordinates is None
            or float(coordinates.group(2)) != row['expected']['evolution_position']):
        raise ValueError('published-coordinate binding mismatch')
    start = sum(map(len, raw.splitlines(keepends=True)[:cell['original_line_number'] - 1]))
    witnesses = [{'source': 'map', 'start': start, 'end': start + len(line),
                  'sha256': hashlib.sha256(line).hexdigest()}]
    for name in row['basis']['supporting_quote_ids']:
        quote = bindings[name]
        sources[name] = checked_capture(quote['binding'])
        witnesses.append({'source': name, 'start': quote['byte_start'], 'end': quote['byte_end_exclusive'],
                          'sha256': quote['quote_sha256']})
    acquisition = published / 'evolution-source-research'
    licence_receipt = acquisition / 'receipts/8b98b6f422054a060468bcc0c2aed7c95a0f595af47df08174835988c86847b6.json'
    licence = read_json(licence_receipt)
    sources['licence'] = checked_capture({'path': str(acquisition / licence['raw_path']),
                                          'sha256': licence['sha256'], 'bytes': licence['bytes']})
    sources['licence-receipt'] = capture(licence_receipt)
    scope = {'purpose': 'development', 'claim': 'published-reference-agreement', 'metric': 'evolution-judge',
             'domain': 'published own-business Wardley map', 'capability': row['input']['component']['id'],
             'organisation': 'Sergio Visinoni / Sudo Make Me a CTO', 'as_of': '2025-11-17',
             'frame': provenance['map_frame']}
    basis = {**row['basis'], 'input_witness': row['input']['evidence'][1],
             'source_hashes': {k: sources[k]['sha256'] for k in ['map', *row['basis']['supporting_quote_ids']]}}
    case = {'id': row['id'], 'sources': sources, 'input': row['input'], 'expected': row['expected'],
            'context': scope, 'reference_kind': 'published-coordinate', 'basis': basis,
            'field_support': {'evolution_position': {'meaning': 'Exact original second coordinate token in Take 2',
                'sources': ['map', *row['basis']['supporting_quote_ids']], 'witnesses': witnesses}},
            'rights': {'statement': 'MIT; copyright (c) 2025 Sergio Visinoni; full original notice conserved',
                       'uses': ['development'], 'evidence': ['licence', 'licence-receipt'],
                       'covered_sources': ['map', *row['basis']['supporting_quote_ids']]},
            'group': row['group_id'], 'exposure': {'status': 'exposed', 'history': [
                'Original nominal holdout is consumed; authors/reviewers saw labels', provenance['family_overlap_status']]},
            'selection': {'decision': 'selected', 'reason': 'Previously accepted literal source-agreement tracer',
                          'original_decisions_source': 'selection-ledger', 'withheld_source': 'withheld-ledger'},
            'limitations': row['basis']['limitations'], 'original_provenance': provenance}
    case['basis_binding'] = binding_for(case)
    admitted = admit_reference(case, scope)
    if not admitted.admitted:
        raise ValueError(admitted.reasons)
    item = admitted.evaluator_item()
    seen: list[Any] = []
    raw_outputs: list[Any] = []
    def test_only_candidate(payload: Any) -> Stated:
        seen.append(payload)
        result = Stated({'evolution_position': 0.27}, {'selected_evidence': payload['evidence'][1]})
        raw_outputs.append({'actor': 'TEST_ONLY-literal-answer', 'answer': result.answer, 'basis': result.basis})
        return result
    def basis_holds(actual: Any, reference: Any) -> bool:
        return actual['selected_evidence'] == reference['input_witness']
    result = evaluate('evolution-judge', test_only_candidate, [item], scorer=evolution_judge.scorer,
                      basis_scorer=basis_holds)
    # The second reference retains all original authority and all null causal targets.
    external = research / 'resume-20261028-dataset-commission/dataset-owner/reusable'
    ei = json.loads((external / 'rationale-ready-cases.jsonl').read_text().splitlines()[0])
    article = external / ei['article_document']['relative_xml_path']
    if hashlib.sha256(article.read_bytes()).hexdigest() != ei['article_document']['xml_sha256']:
        raise ValueError('imported article binding mismatch')
    rights = next(json.loads(line) for line in (external / 'rights.jsonl').read_text().splitlines()
                  if json.loads(line)['pmcid'] == ei['input']['article_pmcid'])
    ei_scope = {'purpose': 'development', 'claim': 'complete-causal-reference', 'metric': 'causal-claims',
                'domain': 'reported trial significance', 'capability': ei['original_prompt']['Outcome'],
                'organisation': 'published trial context', 'as_of': None,
                'frame': 'Original intervention/comparator/outcome; causal date and frame unestablished'}
    ei_case = {'id': ei['case_id'], 'sources': {'article': capture(article, version='original acquired XML'),
                'original-cases': capture(external / 'rationale-ready-cases.jsonl', version='original imported rows'),
                'original-rights': capture(external / 'rights.jsonl', version='original acquired rights')},
        'input': ei['input'], 'expected': {key: ei['product_skill_admission'][key] for key in
            ('sign', 'lag_days', 'elasticity_mode', 'evidence_grade')}, 'basis': {'original_annotations': ei['original_annotations']},
        'context': ei_scope, 'reference_kind': 'reported-significance', 'field_support': {},
        'rights': {'statement': rights['rights_scope'], 'uses': ['development'], 'evidence': ['original-rights']},
        'group': 'article:PMC' + ei['input']['article_pmcid'],
        'exposure': {'status': 'exposed', 'history': [ei['exposure']]},
        'selection': {'decision': 'held', 'reason': ei['product_skill_admission']['reason']},
        'limitations': ['No complete causal fields or repository evidence-grade target',
                       'No established causal date/frame admission'], 'original_reference': ei}
    # Do not supply a fabricated date: refusal retains absence explicitly.
    ei_case['basis_binding'] = binding_for(ei_case)
    held = admit_reference(ei_case, ei_scope)
    if held.admitted:
        raise ValueError('task-mismatched significance was admitted')
    output.mkdir(parents=True, exist_ok=True)
    for name, admission in [('published', admitted), ('significance-as-causal', held)]:
        (output / (name + '.packet.json')).write_bytes(admission.packet_bytes)
    summary = {'schema': 'reference-case-demonstration/v1', 'actor': 'TEST_ONLY-literal-answer',
               'source_agreement_only': True, 'qualification': False, 'permission_granted': False,
               'published_packet_sha256': admitted.packet_digest, 'held_packet_sha256': held.packet_digest,
               'published_scope': scope, 'held_reasons': held.reasons,
               'original_selection_decisions': len(read_json(author / 'DECISIONS.json')),
               'evaluation': result.as_dict()}
    (output / 'candidate-inputs.json').write_text(json.dumps(seen, indent=2) + '\n')
    (output / 'candidate-outputs.json').write_text(json.dumps(raw_outputs, indent=2) + '\n')
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(demonstrate(args.source_root, args.output), indent=2))
