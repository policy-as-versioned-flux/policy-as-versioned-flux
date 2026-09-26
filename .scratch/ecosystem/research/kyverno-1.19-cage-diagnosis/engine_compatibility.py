#!/usr/bin/env python3
"""Published policy × exact engine evidence; not a runtime support range.

Only the released cage-tier and cage-netpol fixture matrices are measured.
Signatures, Kubernetes admission, reach and live controller behavior are outside
this instrument. The normal caller installs a checksummed CLI; this gate records
its actual executable digest and rejects a different reported version.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
from typing import Any

import yaml

SCOPE = 'published-cage-fixtures-v1'
FAMILIES = ('cage-tier', 'cage-netpol')
LIMITS = [
    'Only the released cage-tier mutation and cage-netpol generation fixtures are graded; '
    'no complete policy, validation, Kubernetes admission or live network compatibility claim.',
    'Exact CLI versions only; no patch range, Kubernetes version or adopter runtime is inferred.',
    'Tag signature verification remains the provenance gate; this check binds tag and array policy trees.',
    'Executable SHA256 identifies this run; binary authenticity rests on the caller checksum pin.',
    'This evidence changes no policy body, policy bump, money, or release authorization.',
]


class SourceUnavailable(Exception):
    """The local checkout cannot supply a historical input for measurement."""


def _run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=120, **kwargs)


def _git(repo: Path, *args: str) -> str:
    result = _run(['git', '-C', str(repo), *args])
    if result.returncode:
        raise ValueError(result.stderr.strip() or 'Git source unavailable')
    return result.stdout.strip()


def _adapt(value: Any, version: str) -> None:
    """Change version-scoping identifiers only, never expected dial/reach values."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'policy-as-versioned.dev/policy-version':
                value[key] = version
            elif key == 'priorityClassName' and isinstance(item, str) and item in (
                    'cage-baseline', 'cage-restricted', 'cage-quarantine', 'cage-isolated'):
                value[key] = item + '-' + version.replace('.', '-')
            else:
                _adapt(item, version)
    elif isinstance(value, list):
        for item in value:
            _adapt(item, version)


def _matrix(root: Path, version: str, family: str, binary: str) -> dict:
    folder = root / 'graded/tests' / family
    manifest = folder / 'kyverno-test.yaml'
    test = yaml.safe_load(manifest.read_text())
    results = test.get('results', [])
    if not results or not any(r.get('result') == 'pass' for r in results):
        raise ValueError(f'{family}: no positive assertions in published fixture')
    for path in folder.glob('*.yaml'):
        if path == manifest:
            continue
        docs = list(yaml.safe_load_all(path.read_text()))
        for doc in docs:
            _adapt(doc, version)
            # Authoring generator fixtures are unversioned. Select the released
            # policy without changing their caged/tier labels or reach assertions.
            if family == 'cage-netpol' and path.name == 'resources.yaml' and isinstance(doc, dict):
                doc['metadata'].setdefault('labels', {})['policy-as-versioned.dev/policy-version'] = version
        path.write_text(yaml.safe_dump_all(docs, sort_keys=False))
    test['policies'] = [str(root / 'distribution/policies' / ('v' + version) / (family + '.yaml'))]
    for result in results:
        result['policy'] = family + '-' + version.replace('.', '-')
        result['rule'] = result['policy']
    manifest.write_text(yaml.safe_dump(test, sort_keys=False))
    run = _run([binary, 'test', str(folder)])
    output = run.stdout + run.stderr
    summaries = re.findall(r'Test Summary:\s*(\d+) tests passed and (\d+) tests failed', output)
    passed, failed = (map(int, summaries[0]) if len(summaries) == 1 else (0, 0))
    ok = run.returncode == 0 and passed > 0 and failed == 0 and len(summaries) == 1
    return {'family': family, 'outcome': 'passed' if ok else 'failed',
            'passed_assertions': passed, 'failed_assertions': failed,
            'exit_code': run.returncode,
            'output_sha256': hashlib.sha256(output.encode()).hexdigest(),
            'diagnostic': None if ok else output[-6000:]}


def _published_row(repo: Path, entry: dict, binary: str) -> dict:
    version, tag, commit = entry['version'], entry['tag'], entry['commit']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or tag != 'policy/v' + version:
        raise ValueError('published policy requires its exact policy/vX.Y.Z tag')
    if not re.fullmatch(r'[a-f0-9]{40}', commit):
        raise ValueError('published array commit must be a full SHA')
    ref = 'refs/tags/' + tag
    for source in (ref, commit):
        available = _run(['git', '-C', str(repo), 'cat-file', '-e', source])
        if available.returncode:
            raise SourceUnavailable(f'historical Git input unavailable: {source}')
    if _git(repo, 'cat-file', '-t', ref) != 'tag':
        raise ValueError('published policy tag is not annotated')
    path = 'distribution/policies/v' + version
    tree = _git(repo, 'rev-parse', ref + ':' + path)
    if tree != _git(repo, 'rev-parse', commit + ':' + path):
        raise ValueError('tag policy tree differs from the array-pinned policy tree')
    row: dict[str, Any] = {'policy_version': version, 'tag': tag, 'array_commit': commit,
           'tag_commit': _git(repo, 'rev-parse', ref + '^{commit}'), 'policy_tree': tree,
           'fixtures_tree': _git(repo, 'rev-parse', ref + ':graded/tests')}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        data = subprocess.check_output(['git', '-C', str(repo), 'archive', ref, path, 'graded/tests'])
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            archive.extractall(root, filter='data')
        files = {str(p.relative_to(root / path)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted((root / path).rglob('*')) if p.is_file()}
        row['policy_sha256'] = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
        apis = sorted({doc['apiVersion'] for p in (root / path).glob('*.yaml')
                       for doc in yaml.safe_load_all(p.read_text())
                       if isinstance(doc, dict) and 'apiVersion' in doc})
        row['api_versions'] = apis
        row['prerelease_api_versions'] = [api for api in apis if re.search(r'/v\d+(alpha|beta)', api)]
        row['matrices'] = [_matrix(root, version, family, binary) for family in FAMILIES]
    row['outcome'] = 'passed' if all(m['outcome'] == 'passed' for m in row['matrices']) else 'failed'
    return row


def check(repo: Path, binary: str = 'kyverno') -> dict:
    """Public seam. A missing/undeclared instrument never reports compatibility."""
    report: dict[str, Any] = {'schema': 1, 'scope': SCOPE, 'outcome': 'could-not-look',
              'engine': None, 'rows': [], 'limits': LIMITS}
    resolved = shutil.which(binary)
    if resolved is None:
        return {**report, 'reason': 'Kyverno binary is unavailable'}
    try:
        identity = _run([resolved, 'version'])
        match = re.search(r'^Version:\s*v?(\d+\.\d+\.\d+)\s*$', identity.stdout, re.MULTILINE)
        if identity.returncode or not match:
            return {**report, 'reason': 'Kyverno binary version could not be identified'}
        version = match.group(1)
        report['engine'] = {'name': 'kyverno', 'version': version,
                            'sha256': hashlib.sha256(Path(resolved).read_bytes()).hexdigest()}
        doc = yaml.safe_load((repo / 'distribution/versions.yaml').read_text())
        entries = doc['spec']['inputs'][0]['versions']
        if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
            raise ValueError('declared policy lines must be a list of array elements')
        if not entries:
            return {**report, 'reason': 'no declared policy lines'}
        for entry in entries:
            base = {'policy_version': entry.get('version'), 'outcome': 'could-not-look'}
            declared = entry.get('tested_engines')
            if not entry.get('commit'):
                report['rows'].append({**base, 'reason': 'uncut policy line has no published tree to grade'})
            elif (not isinstance(declared, dict) or declared.get('scope') != SCOPE
                  or not isinstance(declared.get('kyverno'), list)
                  or declared['kyverno'] != [version]):
                report['rows'].append({**base, 'reason': 'engine/version outside the declared test matrix or additional engines unmeasured; compatibility unknown'})
            else:
                try:
                    report['rows'].append(_published_row(repo, entry, resolved))
                except SourceUnavailable as exc:
                    report['rows'].append({**base, 'reason': str(exc)})
                except (ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError, yaml.YAMLError) as exc:
                    report['rows'].append({**base, 'outcome': 'failed', 'reason': str(exc)})
        outcomes = [row['outcome'] for row in report['rows']]
        report['outcome'] = ('failed' if 'failed' in outcomes else
                             'could-not-look' if 'could-not-look' in outcomes else 'passed')
        return report
    except (ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError, yaml.YAMLError) as exc:
        return {**report, 'outcome': 'failed', 'reason': str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--engine', default='kyverno')
    args = parser.parse_args()
    result = check(args.repo, args.engine)
    print(json.dumps(result, indent=2))
    code = {'passed': 0, 'failed': 1, 'could-not-look': 3}[result['outcome']]
    print(('PASS' if code == 0 else 'FAIL' if code == 1 else 'SKIP') +
          ': published cage fixture compatibility -- ' + result['outcome'])
    return code


if __name__ == '__main__':
    raise SystemExit(main())
