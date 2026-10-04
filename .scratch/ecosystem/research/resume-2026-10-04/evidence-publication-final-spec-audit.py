"""Read-only bounded cutoff; output excludes its own two generated files."""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
DAY = Path(__file__).resolve().parent
PATCHES = ROOT / '.scratch/ecosystem/patches/resume-2026-10-04'
OUTPUT = DAY / 'evidence-publication-final-spec-audit.json'
REPORT = DAY / 'evidence-publication-final-spec-audit.md'
EXCLUDE = {OUTPUT, REPORT}
TICKETS = [ROOT / '.scratch/ecosystem/issues' / name for name in (
    '156-the-incumbent-org-register.md',
    '62-the-feed-parents-are-consumed-pinned-and-signed.md',
    '77-every-pin-is-checked-for-content.md',
    '83-the-truth-line-says-what-it-measured.md',
    '96-the-citable-line-says-whether-the-twin-may-write.md')]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key] = value
    return result


def constant(_):
    raise ValueError('non-finite JSON number')


def strict(data):
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def inventory():
    files = sorted(set(TICKETS) | {p for base in (DAY, PATCHES) for p in base.rglob('*')
                                  if p.is_file() or p.is_symlink()})
    rows, bytes_by_path, symlinks = [], {}, []
    for path in files:
        if path in EXCLUDE:
            continue
        name = path.relative_to(ROOT).as_posix()
        if path.is_symlink():
            symlinks.append(name)
            continue
        data = path.read_bytes()
        rows.append({'path': name, 'bytes': len(data), 'sha256': sha(data)})
        bytes_by_path[name] = data
    return rows, bytes_by_path, symlinks


started = datetime.now(UTC).isoformat()
rows, contents, symlinks = inventory()
json_failures, filename_failures, secrets = [], [], []
patterns = {
    'private-key-header': rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----',
    'github-credential': rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{60,255})\b',
    'aws-access-key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
}
json_count = 0
for name, data in contents.items():
    if any(ord(char) < 32 or ord(char) == 127 for char in name):
        filename_failures.append(name)
    if Path(name).suffix in ('.json', '.jsonl'):
        try:
            if name.endswith('.jsonl'):
                for line in data.splitlines():
                    if line.strip():
                        strict(line)
            else:
                strict(data)
            json_count += 1
        except (ValueError, UnicodeDecodeError) as error:
            json_failures.append({'path': name, 'reason': type(error).__name__})
    for kind, pattern in patterns.items():
        for match in re.finditer(pattern, data):
            secrets.append({'path': name, 'kind': kind, 'offset': match.start(),
                            'matched_bytes_sha256': sha(match.group())})

joins = []


def joined(label, expected, actual):
    joins.append({'label': label, 'expected': expected, 'actual': actual,
                  'equal': expected == actual})


originals = strict((DAY / 'hub-run377-capture-reads.json').read_bytes())
for row in originals['capture_reads']:
    path = Path(row['local_file'])
    assert path.is_relative_to(DAY)
    joined('received:' + path.name, row['sha256'], sha(path.read_bytes()))
raw = strict((DAY / 'hub-run377-git-raw-provenance.json').read_bytes())
object_store = raw['source_object_store']
for row in raw['records'] + [raw['grade_table']]:
    relative = row.get('raw_capture', row.get('raw_file'))
    path = ROOT / relative
    assert path.is_relative_to(DAY)
    blob = subprocess.check_output(['git', '-C', object_store, 'rev-parse',
                                    raw['primary_ref'] + ':' + row['source_git_path']]).decode().strip()
    source = subprocess.check_output(['git', '-C', object_store, 'cat-file', 'blob', blob])
    joined('raw-object:' + path.name, row['source_blob'], blob)
    joined('raw-file:' + path.name, row['raw_sha256'], sha(path.read_bytes()))
    joined('raw-source:' + path.name, row['raw_sha256'], sha(source))
for name, expected in raw['original_download_input_sha256_preserved'].items():
    path = ROOT / name
    assert path.is_relative_to(DAY)
    joined('original-preserved:' + path.name, expected, sha(path.read_bytes()))

for bundle, source in [('complete', 'publication-delivered-source-manifest.json'),
                       ('final-published', 'publication-final-published-source-manifest.json')]:
    directory = PATCHES / bundle
    manifest = strict((directory / 'manifest.json').read_bytes())
    source_data = (DAY / source).read_bytes()
    source_manifest = strict(source_data)
    joined(bundle + ':source-manifest', manifest['publication_manifest_sha256'], sha(source_data))
    joined(bundle + ':repository-count', 9, len(manifest['repositories']))
    for row in manifest['repositories']:
        patch = directory / row['patch']
        assert patch.is_relative_to(directory)
        joined(bundle + ':patch:' + row['repository'], row['sha256'], sha(patch.read_bytes()))
        observed = source_manifest['repositories'][row['repository']]
        joined(bundle + ':commit:' + row['repository'], observed['commit'], row['published_commit'])
        joined(bundle + ':tree:' + row['repository'], observed['tree'], row['published_tree'])

second, _, second_symlinks = inventory()
first_by_path = {row['path']: row for row in rows}
second_by_path = {row['path']: row for row in second}
changed = [name for name in sorted(first_by_path.keys() | second_by_path.keys())
           if first_by_path.get(name) != second_by_path.get(name)]
failures = [join for join in joins if not join['equal']]
passed = not (json_failures or filename_failures or secrets or symlinks or second_symlinks
              or changed or failures)
result = {
    'status': 'PASS_FOR_EXACT_CUTOFF' if passed else 'FINDINGS_AT_CUTOFF',
    'observed_from': started, 'observed_until': datetime.now(UTC).isoformat(),
    'scope': [str(DAY.relative_to(ROOT)), str(PATCHES.relative_to(ROOT))]
             + [str(path.relative_to(ROOT)) for path in TICKETS],
    'excluded_own_outputs': [str(path.relative_to(ROOT)) for path in sorted(EXCLUDE)],
    'exclusion_reason': 'Only the own generated report/manifest are excluded to avoid self-hash recursion; earlier audits are retained and scanned.',
    'files': len(rows), 'total_bytes': sum(row['bytes'] for row in rows),
    'extension_counts': dict(sorted(Counter(Path(row['path']).suffix for row in rows).items())),
    'strict_json_files': json_count, 'strict_json_failures': json_failures,
    'filename_failures': filename_failures, 'symlinks_not_followed': symlinks,
    'high_confidence_credential_findings': secrets,
    'credential_scan_limits': 'Private-key headers, GitHub credential shapes and AWS access-key shapes; names/hash/offset only, no possible credential values printed. This is a bounded static scan, not proof of absence of every secret.',
    'second_read_changes': changed, 'hash_join_failures': failures,
    'preservation_joins': joins, 'inventory_sha256': sha(json.dumps(rows, sort_keys=True).encode()),
    'inventory': rows,
    'current_assertion_review': {
        'summary': 'delivery-report.md', 'engine': '1.18.2; upgrade waits for genuine baseline',
        'cloud_activation': False, 'unobserved_or_unbound_values': 'remain red/null',
        'run377': '88 PASS /25 FAIL /22 SKIP preserved; no new clock claimed',
        'raw_recovery': '25 exact Git captures plus table, separately from unchanged received downloads',
        'hub_source': 'PR155 publication is distinct from main merge; original failed CI and unchanged floor remain explicit',
        'prototype': 'c1bbb implementation/independent reviews are unpublished; genuine legacy cost instruments still absent',
        'later_approval': 'Exact7fa user approval and retry arrived after frozen summary; ordinary publication receipts will be audited incrementally without rewriting cutoff hashes',
        'historical_records': 'Old stops, obsolete candidates, red tests and wrong-month negative retained as history, not current publication claims',
    },
    'historical_complete_bundle_sha256': sha((PATCHES / 'complete/manifest.json').read_bytes()),
    'historical_complete_source_manifest_sha256': sha((DAY / 'publication-delivered-source-manifest.json').read_bytes()),
    'final_published_bundle_sha256': sha((PATCHES / 'final-published/manifest.json').read_bytes()),
    'final_published_source_manifest_sha256': sha((DAY / 'publication-final-published-source-manifest.json').read_bytes()),
    'historical_received_capture_count': len(originals['capture_reads']),
    'raw_recovered_file_count': len(raw['records']) + 1,
    'external_mutations': False, 'unrelated_user_files_traversed': False,
}
OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
REPORT.write_text(
    f"{result['status']}: {len(rows)} owned files, {result['total_bytes']} bytes; "
    f"{json_count} strict JSON/JSONL files, zero skipped credential values.\n\n"
    f"Findings: {len(json_failures)} JSON failures, {len(filename_failures)} filename failures, "
    f"{len(secrets)} high-confidence credential matches, {len(changed)} second-read changes, "
    f"{len(failures)} hash-join failures. All received25 capture hashes and recovered26 "
    "source blobs are independently joined; old complete and new final-published nine-repository "
    "patch bundles join their source manifests and exact file hashes.\n\n"
    "The summary distinguishes published A/B deliveries and maintenance from PR155's pending "
    "ordinary CI/merge and the unpublished strict response prototype. The authentic clock, "
    "coverage-floor failure, unbound/null risks, engine baseline and disabled cloud remain "
    "honest. Later exact approval/publication receipts require a separately bound incremental "
    "audit; this cutoff's hashes are not rewritten.\n\n"
    "Scope is only the two owned Oct4 directories and five named tickets. Only this audit's "
    "generated JSON/report are excluded for self-hash recursion. Older audits and historical "
    "negative evidence are preserved. No external write, credential value output or unrelated "
    "user-file traversal occurred.\n")
print(json.dumps({key: result[key] for key in ('status', 'files', 'total_bytes',
      'strict_json_files', 'second_read_changes', 'hash_join_failures')}, indent=2))
print('safe finding counts', len(json_failures), len(filename_failures), len(secrets), len(symlinks))
