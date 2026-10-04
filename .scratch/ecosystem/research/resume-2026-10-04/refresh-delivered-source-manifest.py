"""Read published main references without altering preserved source worktrees."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
DAY = ROOT / '.scratch/ecosystem/research/resume-2026-10-04'
DESTINATION = DAY / 'publication-delivered-source-manifest.json'


def call(*args: str) -> bytes:
    result = subprocess.run(args, capture_output=True, check=True, timeout=180)
    return result.stdout


def git(directory: str, *args: str) -> bytes:
    return call('git', '-C', directory, *args)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert not DESTINATION.exists(), 'Preserve every earlier source manifest'
    previous = sorted(DAY.glob('publication-*-source-manifest.json'))
    old_hashes = {str(p.relative_to(ROOT)): sha(p) for p in previous}
    foundation = json.loads((DAY / 'publication-foundation-refreshed-source-manifest.json').read_text())
    sources = dict(foundation['repositories'])
    sources.update({
        'driftwood': {
            'directory': '/private/tmp/pavf-driftwood-moved-20261004-k0udi0xf/hub/.estate-clone/driftwood',
            'commit': '2ebde7efd1f3c11071719d25f2cba23368cfcdd7',
        },
        'ludlow': {
            'directory': '/private/tmp/pavf-ludlow-maintenance-20261004-estate/ludlow',
            'commit': 'e7243d917c323364c0fb74d312f921d0d1ec1356',
        },
        'tuppence': {
            'directory': '/private/tmp/pavf-tuppence-maintenance-20261004-estate/tuppence',
            'commit': '011942de87ba827b5bc2949da0057d862b6b69f6',
        },
    })
    rows = {}
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    for name, source in sources.items():
        directory = source['directory']
        before_status = git(directory, 'status', '--porcelain')
        before_head = git(directory, 'rev-parse', 'HEAD').decode().strip()
        before_branch = git(directory, 'symbolic-ref', '-q', 'HEAD').decode().strip()
        remote = git(directory, 'remote', 'get-url', 'origin').decode().strip()
        match = re.fullmatch(r'(?:https://github.com/|git@github.com:)([^/]+/[^/]+?)(?:\.git)?/?', remote)
        assert match, 'Expected public GitHub origin'
        endpoint = 'repos/' + match.group(1) + '/commits/main'
        api = json.loads(call('gh', 'api', endpoint))
        commit = api['sha']
        call('git', '-C', directory, 'fetch', 'origin', 'main')
        assert git(directory, 'rev-parse', 'origin/main').decode().strip() == commit, 'Remote changed during snapshot: ' + name
        tree = git(directory, 'rev-parse', commit + '^{tree}').decode().strip()
        assert tree == api['commit']['tree']['sha']
        expected = source['commit']
        paths = git(directory, 'diff', '--name-only', expected, commit).decode().splitlines()
        if commit != expected:
            assert name in {'driftwood', 'ludlow', 'tuppence'}, 'Unexpected foundation source move: ' + name
            git(directory, 'merge-base', '--is-ancestor', expected, commit)
            assert paths and all(p.startswith('observations/') for p in paths), 'Unexpected non-observation main move: ' + name
        assert before_head == git(directory, 'rev-parse', 'HEAD').decode().strip()
        assert before_branch == git(directory, 'symbolic-ref', '-q', 'HEAD').decode().strip()
        assert before_status == git(directory, 'status', '--porcelain')
        rows[name] = {
            'directory': directory, 'commit': commit, 'tree': tree, 'remote': remote,
            'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'read_only_api': endpoint, 'remote_main_matches_local_fetched_origin_main': True,
            'github_commit_signature': api['commit']['verification']['reason'],
            'github_commit_signature_valid': api['commit']['verification']['verified'],
            'reviewed_published_source_commit': expected,
            'later_main_delta_paths': paths,
            'later_main_delta_scope': 'none' if commit == expected else 'Only actual upstream observation paths; no new source approval inferred',
            'preserved_worktree_head': before_head, 'preserved_worktree_branch': before_branch,
            'preserved_worktree_status_sha256': hashlib.sha256(before_status).hexdigest(),
            'scope': 'Exact published current main cutoff; preserved candidate worktree is not exported',
        }
        print(name + ': remote main ' + commit + ', worktree preserved', flush=True)
    assert all(sha(ROOT / p) == digest for p, digest in old_hashes.items())
    result = {
        'observed_from': start, 'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': 'Nine exact published current main cutoffs, independently read from normal GitHub API and fetched origin/main; not pending source or a new live observation grade',
        'repositories': rows,
        'earlier_source_manifest_hashes_preserved': old_hashes,
        'pending_excluded': {
            'driftwood': {'candidate': '8d9ae2ec514ca75c2c460b4f057a3a741e69b21a', 'reason': 'Reviewed maintenance source awaits exact public approval; published main remains separate'},
            'platform': {'candidate': '0547a5fa7babe34227be5085ff63b1cf196d8cae', 'reason': 'Reviewed maintenance source awaits exact public approval; genuine published main remains 703eff6'},
            'hub': {'candidate': '4c4b53c7163b0da7e11e9d0574057bcbc24e298d', 'reason': 'Hub verifier maintenance publication was rejected before execution; outside nine-repository source export'},
            'prototype': {'reason': 'Prepared prototype is outside approved delivered source and excluded'},
        },
        'other_published_source_outside_nine_repository_bundle': {
            'insurer': {'commit': '5d1a7cde88230370074ed2a2ce4e94adf4eb8790', 'proof': 'insurer-compatible-platform-pin-publication-complete.json'},
        },
        'external_mutations': False,
    }
    DESTINATION.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
