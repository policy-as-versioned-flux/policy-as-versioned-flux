"""Bind real cut/release, immutable object and normal crypto verification."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
A = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate/ludlow')
HEAD = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
OBJECT = 'efffeee3b39cc59dd5ecc1ac0536845e712d4c6f'
cut = json.loads((E / 'ludlow-composition-B-cut-run.json').read_text())
release = json.loads((E / 'ludlow-composition-B-release-run.json').read_text())
published = json.loads((E / 'ludlow-composition-B-github-release.json').read_text())
for run in (cut, release):
    assert run['headSha'] == HEAD and run['status'] == 'completed' and run['conclusion'] == 'success'
assert cut['databaseId'] == 37201479463 and release['databaseId'] == 37201969669
assert published['tagName'] == 'v4.0.1' and published['isDraft'] is False and published['publishedAt']
assert 'Resolved commit: ' + HEAD in published['body']
git = lambda *args: subprocess.check_output(['git', '-C', str(A), *args]).decode().strip()
assert git('rev-parse', 'refs/tags/v4.0.1') == OBJECT
assert git('rev-parse', 'refs/tags/v4.0.1^{commit}') == HEAD
identity = 'https://github.com/policy-as-versioned-ludlow/ludlow/.github/workflows/cut-release.yml@refs/heads/main'
issuer = 'https://token.actions.githubusercontent.com'
siglog = (E / 'ludlow-composition-B-tag-verification.log').read_text()
assert identity in siglog and issuer in siglog
assert all('Validated ' + claim + ': true' in siglog for claim in ('Git signature', 'Rekor entry', 'Certificate claims'))
tlog = re.search(r'tlog index:\s*(\d+)', siglog)
assert tlog and int(tlog.group(1)) == 3077655513
release_log = (E / 'ludlow-composition-B-release.log').read_text()
assert identity in release_log and all('Validated ' + claim + ': true' in release_log for claim in ('Git signature', 'Rekor entry', 'Certificate claims'))
names = ['ludlow-composition-B-cut-run.json', 'ludlow-composition-B-release-run.json',
    'ludlow-composition-B-github-release.json', 'ludlow-composition-B-tag-object.txt',
    'ludlow-composition-B-tag-verification.log', 'ludlow-composition-B-cut.log', 'ludlow-composition-B-release.log']
result = {'scope': 'Authentic approved Composition B signed release, no live observation claimed',
    'tag': 'v4.0.1', 'tag_object': OBJECT, 'commit': HEAD, 'tree': git('rev-parse', HEAD + '^{tree}'),
    'cut_run': cut['databaseId'], 'cut_conclusion': 'success',
    'release_run': release['databaseId'], 'release_conclusion': 'success',
    'published_at': published['publishedAt'], 'release_url': published['url'],
    'signature': {'exact_identity': identity, 'issuer': issuer, 'rekor_mode': 'offline',
        'tlog_index': int(tlog.group(1)), 'Git': True, 'Rekor': True, 'certificate': True},
    'immutable_release_ref_and_input': 'v4.0.1',
    'artifact_sha256': {name: hashlib.sha256((E / name).read_bytes()).hexdigest() for name in names},
    'explicit_user_approval': 'ludlow-composition-B-explicit-release-approval.json',
    'fresh_Standards': 'ludlow-composition-B-root-standards-review.json',
    'fresh_Spec': 'ludlow-composition-B-spec-review.json'}
(E / 'ludlow-composition-B-authentic-release.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('PASS: genuine Bv4.0.1 release, exact reviewed source, normal crypto and published receipt.')
