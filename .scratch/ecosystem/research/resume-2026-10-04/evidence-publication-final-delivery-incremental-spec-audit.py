"""Read only explicit owned evidence; print names, counts and hashes only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import runpy

ROOT = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
DAY = ROOT / '.scratch/ecosystem/research/resume-2026-10-04'
PATCHES = ROOT / '.scratch/ecosystem/patches/resume-2026-10-04'
BASELINE = DAY / 'evidence-publication-final-spec-audit.json'
PRIOR_INCREMENTAL = DAY / 'evidence-publication-header-followup-incremental-spec-audit.json'
OUTPUT = DAY / 'evidence-publication-final-delivery-incremental-spec-audit.json'
REPORT = DAY / 'evidence-publication-final-delivery-incremental-spec-audit.md'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strict_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate object key')
        value[key] = item
    return value


def invalid_constant(_value):
    raise ValueError('non-finite JSON constant')


def main():
    assert not OUTPUT.exists() and not REPORT.exists(), 'Preserve historical audits'
    start = datetime.now(timezone.utc).isoformat()
    definitions = runpy.run_path(str(DAY / 'audit-delivered-publication-data.py'))
    patterns = definitions['PATTERNS']
    assignment = definitions['SECRET_ASSIGNMENT']
    baseline_bytes = BASELINE.read_bytes()
    baseline = json.loads(baseline_bytes)
    prior_incremental_bytes = PRIOR_INCREMENTAL.read_bytes()
    prior_incremental = json.loads(prior_incremental_bytes)
    prior = {row['path']: row for row in baseline['inventory']}
    prior.update({row['path']: row for row in prior_incremental['scanned_inventory']})
    paths = set()
    symlinks = []
    for directory in (DAY, PATCHES):
        for folder, children, files in os.walk(directory, followlinks=False):
            for child in children[:]:
                p = Path(folder) / child
                if p.is_symlink():
                    children.remove(child)
                    symlinks.append(str(p.relative_to(ROOT)))
            for name in files:
                paths.add(Path(folder) / name)
    paths.update(ROOT / name for name in definitions['TICKETS'])
    excluded = {OUTPUT, REPORT}
    inventory, changed, findings, names, invalid_json = [], [], [], [], []
    strict_count = 0
    for path in sorted(paths - excluded):
        name = str(path.relative_to(ROOT))
        if path.is_symlink():
            symlinks.append(name)
            continue
        content = path.read_bytes()
        row = {'path': name, 'bytes': len(content), 'sha256': sha(content)}
        inventory.append(row)
        if name in prior and prior[name]['sha256'] == row['sha256']:
            continue
        row['change_since_cutoff'] = 'changed' if name in prior else 'added'
        changed.append(row)
        if any(ord(character) < 32 or ord(character) == 127 for character in name):
            names.append({'path': name, 'kind': 'control-character-filename'})
        if path.name in {'.env', 'credentials', 'id_rsa', 'id_ed25519', 'secrets.json', 'secrets.yaml', 'secrets.yml'}:
            names.append({'path': name, 'kind': 'credential-filename', 'sha256': row['sha256']})
        if path.suffix in {'.json', '.jsonl', '.ndjson'}:
            strict_count += 1
            try:
                chunks = content.splitlines() if path.suffix != '.json' else [content]
                for chunk in chunks:
                    if chunk.strip():
                        json.loads(chunk, object_pairs_hook=strict_object, parse_constant=invalid_constant)
            except (ValueError, UnicodeDecodeError) as error:
                invalid_json.append({'path': name, 'sha256': row['sha256'], 'error_type': type(error).__name__, 'line': getattr(error, 'lineno', None), 'column': getattr(error, 'colno', None)})
        for kind, pattern in patterns.items():
            for match in pattern.finditer(content):
                findings.append({'path': name, 'sha256': row['sha256'], 'kind': kind, 'line': content[:match.start()].count(b'\n') + 1, 'match_sha256': sha(match.group())})
        for match in assignment.finditer(content):
            value = match.group(1)
            if re.fullmatch(rb'[a-fA-F0-9]{24,}', value) or value.lower().startswith((b'example', b'placeholder', b'dummy', b'not-a-real', b'test-')):
                continue
            findings.append({'path': name, 'sha256': row['sha256'], 'kind': 'long-literal-secret-field-review', 'line': content[:match.start()].count(b'\n') + 1, 'match_sha256': sha(value)})
    changed_during_read = [row['path'] for row in changed if sha((ROOT / row['path']).read_bytes()) != row['sha256']]
    missing_since_cutoff = sorted(name for name in prior if not (ROOT / name).exists())
    status = 'PASS_FOR_BOUNDED_INCREMENTAL_SNAPSHOT' if not (findings or names or invalid_json or symlinks or changed_during_read or missing_since_cutoff) else 'FINDINGS_AT_INCREMENTAL_CUTOFF'
    result = {'status': status, 'observed_from': start, 'observed_until': datetime.now(timezone.utc).isoformat(), 'baseline': str(BASELINE.relative_to(ROOT)), 'baseline_sha256': sha(baseline_bytes), 'prior_incremental': str(PRIOR_INCREMENTAL.relative_to(ROOT)), 'prior_incremental_sha256': sha(prior_incremental_bytes), 'scope': baseline['scope'], 'excluded_own_outputs': [str(path.relative_to(ROOT)) for path in sorted(excluded)], 'exclusion_reason': 'Only this new audit output pair is excluded to avoid self-hash recursion; earlier audits and all prototype evidence are included when new or changed.', 'compared_files': len(inventory), 'scanned_added_or_changed_files': len(changed), 'scanned_bytes': sum(row['bytes'] for row in changed), 'strict_json_files': strict_count, 'strict_json_failures': invalid_json, 'filename_failures': names, 'symlinks_not_followed': symlinks, 'high_confidence_credential_findings': findings, 'credential_pattern_names': sorted(patterns), 'long_literal_secret_field_pattern_included': True, 'second_read_changes': changed_during_read, 'missing_since_cutoff': missing_since_cutoff, 'scanned_inventory': changed, 'inventory_sha256': sha(json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()), 'baseline_historical_received_capture_count': baseline['historical_received_capture_count'], 'baseline_recovered_raw_file_count': baseline['raw_recovered_file_count'], 'actual_hub_source_head': 'f10faa536aa441a7f64f42a0aceed6a3d7b8f205', 'actual_merged_hub_main': '002f2a3c2e3849af6453d4e484a6efa3e4953fc7', 'completed_delivery_receipt': 'hub-run377-header-writer-delivery-complete.json', 'historical_f10_stop_preserved': 'hub-run377-header-writer-publication-stop.json', 'historical_primary_logs_modified_by_audit': False, 'external_mutations': False, 'unrelated_user_files_traversed': False, 'limits': 'Local final incremental names, JSON and high-confidence credential audit. Completed source delivery is joined to its authentic saved receipt; no new runtime check, authentication claim, green whole-hub CI or live observation is inferred. Any later files require a separately bound audit.'}
    frozen_docs = ['delivery-report.md', 'run377-closure-gap-map.md', 'root-delivery-evidence-PR-body.md', 'own-response-annual-model-prototype.md']
    result['frozen_final_documents'] = [{'path': str((DAY / name).relative_to(ROOT)), 'sha256': sha((DAY / name).read_bytes())} for name in frozen_docs]
    completion = json.loads((DAY / 'hub-run377-header-writer-delivery-complete.json').read_text())
    assert completion['merged_main'] == result['actual_merged_hub_main'] and completion['source_head'] == result['actual_hub_source_head']
    result['actual_delivery_receipt_join'] = True
    result['earlier_cutoff_and_incremental_audits_preserved'] = sha(BASELINE.read_bytes()) == sha(baseline_bytes) and sha(PRIOR_INCREMENTAL.read_bytes()) == sha(prior_incremental_bytes)
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
    REPORT.write_text(f'{status}: {len(changed)} added or changed files ({result["scanned_bytes"]} bytes), {strict_count} strict JSON files. Credentials: {len(findings)}; filename issues: {len(names)}; parse errors: {len(invalid_json)}; second-read changes: {len(changed_during_read)}. All eight original credential patterns and literal-secret checks ran. Prior audits and the two-file race closure remain unchanged. Only this output pair is excluded from its own hash inventory.\n\nPR155 is ordinarily App-reviewed and merged at genuine main002f with exact sourcef10; the completion receipt is joined. Actual CI clears all owned errors and preserves the one coverage-floor failure (2908 passed, 1 failed, 24 skipped, 2 subtests); no green whole-hub claim or waiver is made. This frozen snapshot includes final delivery documents and source publication receipts while preserving every historical stop, raw log, negative and prior audit. Any later review receipts require their own separately bound incremental scope.\n')
    print(json.dumps({key: result[key] for key in ['status', 'scanned_added_or_changed_files', 'scanned_bytes', 'strict_json_files', 'strict_json_failures', 'filename_failures', 'high_confidence_credential_findings', 'second_read_changes', 'inventory_sha256']}, indent=2))


if __name__ == '__main__':
    main()
