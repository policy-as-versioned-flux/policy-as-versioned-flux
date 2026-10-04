"""Bounded local audit: no secret values or source payloads are printed."""
from __future__ import annotations

from collections import Counter
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
DAY = ROOT / '.scratch/ecosystem/research/resume-2026-10-04'
PATCHES = ROOT / '.scratch/ecosystem/patches/resume-2026-10-04'
OUTPUT = DAY / 'publication-delivered-source-audit.json'
REPORT = DAY / 'publication-delivered-source-audit.md'
EXCLUDED = {OUTPUT, REPORT}
PROTOTYPE_PREFIXES = ('own-response-annual-model', 'pound-model')
TICKETS = [
    '.scratch/ecosystem/issues/156-the-incumbent-org-register.md',
    '.scratch/ecosystem/issues/62-the-feed-parents-are-consumed-pinned-and-signed.md',
    '.scratch/ecosystem/issues/77-every-pin-is-checked-for-content.md',
    '.scratch/ecosystem/issues/83-the-truth-line-says-what-it-measured.md',
    '.scratch/ecosystem/issues/96-the-citable-line-says-whether-the-twin-may-write.md',
]
PATTERNS = {
    'private-key-material': re.compile(rb'-----BEGIN (?:RSA |DSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----'),
    'github-token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b'),
    'aws-access-key-id': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'google-api-key': re.compile(rb'\bAIza[0-9A-Za-z_-]{35}\b'),
    'slack-token': re.compile(rb'\bxox[baprs]-[0-9A-Za-z-]{20,}\b'),
    'openai-api-key': re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}\b'),
    'credential-bearing-url': re.compile(rb'https?://[A-Za-z0-9_.%+-]+:[A-Za-z0-9_./+%=-]{16,}@'),
    'literal-aws-secret': re.compile(rb'(?i)aws_secret_access_key[\s\"\']*[:=][\s\"\']*[A-Za-z0-9/+]{40}\b'),
}
SECRET_ASSIGNMENT = re.compile(rb'(?i)[\"\'](?:password|passwd|api_key|access_token|client_secret|private_key)[\"\']\s*:\s*[\"\']([A-Za-z0-9_+/=-]{24,})[\"\']')


def sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def files_under(directory: Path):
    for folder, children, filenames in os.walk(directory, followlinks=False):
        children[:] = sorted(n for n in children if not (Path(folder) / n).is_symlink())
        for name in sorted(filenames):
            yield Path(folder) / name


def main() -> None:
    assert not OUTPUT.exists() and not REPORT.exists(), 'Keep prior audit immutable'
    ticket_dir = PATCHES / 'ticket-diffs'
    ticket_dir.mkdir(exist_ok=True)
    ticket_diffs = []
    for ticket in TICKETS:
        content = subprocess.run(['git', '-C', str(ROOT), 'diff', '--binary', '--full-index', '--', ticket], capture_output=True, check=True).stdout
        assert content, 'Expected owned ticket diff: ' + ticket
        path = ticket_dir / (Path(ticket).stem + '.patch')
        assert not path.exists(), 'Keep earlier ticket export immutable'
        path.write_bytes(content)
        ticket_diffs.append({'ticket': ticket, 'diff': str(path.relative_to(ROOT)), 'bytes': len(content), 'sha256': sha(content)})
    manifest = []
    findings = []
    invalid_json = []
    symlinks = []
    credential_filenames = []
    prototype_excluded = []
    extensions = Counter()
    for path in sorted({p for directory in (DAY, PATCHES) for p in files_under(directory)}):
        if path in EXCLUDED:
            continue
        name = str(path.relative_to(ROOT))
        if path.name.startswith(PROTOTYPE_PREFIXES):
            prototype_excluded.append(name)
            continue
        if path.is_symlink():
            symlinks.append(name)
            continue
        content = path.read_bytes()
        row = {'path': name, 'bytes': len(content), 'sha256': sha(content)}
        manifest.append(row)
        extensions[path.suffix] += 1
        if path.name in {'.env', 'credentials', 'id_rsa', 'id_ed25519', 'secrets.json', 'secrets.yaml', 'secrets.yml'}:
            credential_filenames.append(row)
        if path.suffix == '.json':
            try:
                json.loads(content)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                invalid_json.append(dict(row, error_type=type(error).__name__, line=getattr(error, 'lineno', None), column=getattr(error, 'colno', None)))
        for kind, pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                findings.append({'path': name, 'sha256': row['sha256'], 'kind': kind, 'line': content[:match.start()].count(b'\n') + 1, 'match_sha256': sha(match.group())})
        for match in SECRET_ASSIGNMENT.finditer(content):
            value = match.group(1)
            if re.fullmatch(rb'[a-fA-F0-9]{24,}', value) or value.lower().startswith((b'example', b'placeholder', b'dummy', b'not-a-real', b'test-')):
                continue
            findings.append({'path': name, 'sha256': row['sha256'], 'kind': 'long-literal-secret-field-review', 'line': content[:match.start()].count(b'\n') + 1, 'match_sha256': sha(value)})
    changed = [row['path'] for row in manifest if sha((ROOT / row['path']).read_bytes()) != row['sha256']]
    assert not changed, 'Audit snapshot changed during read: ' + ','.join(changed)
    scope = ['.scratch/ecosystem/research/resume-2026-10-04', '.scratch/ecosystem/patches/resume-2026-10-04']
    result = {
        'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': scope, 'five_owned_ticket_diffs': ticket_diffs,
        'status': 'PASS_FOR_BOUNDED_SNAPSHOT' if not findings and not invalid_json and not credential_filenames else 'REVIEW_REQUIRED',
        'scanned_files': len(manifest), 'bytes': sum(row['bytes'] for row in manifest),
        'extension_counts': dict(sorted(extensions.items())),
        'high_confidence_credential_findings': findings,
        'credential_filename_findings': credential_filenames,
        'invalid_json': invalid_json, 'symlinks_not_followed': symlinks,
        'audit_self_outputs_excluded': [str(p.relative_to(ROOT)) for p in sorted(EXCLUDED)],
        'in_flight_prototype_files_excluded': prototype_excluded,
        'in_flight_prototype_prefixes_excluded': list(PROTOTYPE_PREFIXES),
        'hash_manifest_sha256': sha(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()),
        'snapshot_stable_on_second_hash_read': True, 'inventory': manifest,
        'limitations': 'Local high-confidence pattern and JSON syntax audit of this explicit snapshot; no live observation, whole-hub green CI, semantic proof, or external publication inferred. Later mapper prototype records require their own incremental audit.',
        'historical_raw_negatives_modified': False, 'worktrees_modified': False,
        'external_mutations': False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
    REPORT.write_text(
        f"{result['status']}: {len(manifest)} files, {result['bytes']} bytes, including the nine published-source patches and five owned ticket diffs. "
        f"Credential findings: {len(findings)}; credential filenames: {len(credential_filenames)}; JSON parse failures: {len(invalid_json)}. "
        "Only names and hashes are recorded for possible matches. Historical primary negatives and every source worktree are preserved.\n\n"
        "The cutoff excludes pending DW8d, platform0547, hub4c4 and the prototype from the delivered-source bundle. Research records may describe those preparations explicitly. "
        "The root truth/twin workflow filters do not run on these DAY, patch, or ecosystem-ticket paths; this audit does not claim new green CI or a qualified live baseline. "
        "Future mapper records require a separately bound incremental audit.\n"
    )
    print(json.dumps({k: result[k] for k in ['status', 'scanned_files', 'bytes', 'high_confidence_credential_findings', 'credential_filename_findings', 'invalid_json', 'hash_manifest_sha256']}, indent=2))


if __name__ == '__main__':
    main()
