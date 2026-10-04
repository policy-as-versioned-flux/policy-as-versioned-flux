"""Finite read-only release prerequisite audit, no dispatch or tag mutation."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

HUB = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
E = HUB / '.scratch/ecosystem/research/resume-2026-10-04'
A = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate/ludlow')
HEAD = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
repo = 'policy-as-versioned-ludlow/ludlow'
result = {'read_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'head': HEAD,
    'tag': 'v4.0.1', 'read_only': True, 'dispatch_executed': False, 'reads': {}}
for key, endpoint in [('main', f'repos/{repo}/git/ref/heads/main'),
    ('tag', f'repos/{repo}/git/ref/tags/v4.0.1'), ('release', f'repos/{repo}/releases/tags/v4.0.1')]:
    run = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True, timeout=25)
    try:
        data = json.loads(run.stdout)
    except ValueError:
        data = None
    result['reads'][key] = {'argv': ['gh', 'api', endpoint], 'exit': run.returncode,
        'response': data, 'stderr': run.stderr.strip()}
    if key == 'main':
        assert run.returncode == 0 and data['object']['sha'] == HEAD, result['reads'][key]
    else:
        assert run.returncode != 0 and data and data.get('status') == '404', result['reads'][key]
result['actual_main_matches_fresh_reviewed_B'] = True
result['tag_and_release_namespace_unused_at_read'] = True
result['workflows'] = {path: hashlib.sha256((A / path).read_bytes()).hexdigest() for path in
    ['.github/workflows/cut-release.yml', '.github/workflows/release.yml']}
result['normal_future_commands_after_actual_explicit_approval'] = [
    ['gh', 'workflow', 'run', 'cut-release.yml', '--repo', repo, '--ref', 'main',
     '-f', 'version=v4.0.1', '-f', 'message=Fresh Composition B serves authentic v4.0.0 apps and policy 5/6/7; policy bump none; engine 1.18.2 and cloud inactive.'],
    ['gh', 'workflow', 'run', 'release.yml', '--repo', repo, '--ref', 'v4.0.1', '-f', 'tag=v4.0.1'],
]
(E / 'ludlow-composition-B-release-preflight.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('PASS: actual main matches fresh B; v4.0.1 tag/release unused. No dispatch executed.')
