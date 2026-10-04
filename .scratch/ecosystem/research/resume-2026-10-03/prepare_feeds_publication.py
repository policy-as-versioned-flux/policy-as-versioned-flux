"""Local-only, idempotent source preparation; performs no network action."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
FEEDS = ROOT / '.estate-publish/feeds'
SOURCE = ROOT / '.estate-clone/feeds'
HERE = Path(__file__).resolve().parent
BASE = 'ff3ac9ab00bdc73e1bbf83cabf91c767d35b8e88'
BRANCH = 'resume/2026-10-03-primary-cve-fx-threat-feeds'


def git(*arguments):
    return subprocess.run(['git', *arguments],
                          cwd=FEEDS, capture_output=True, check=True).stdout


assert git('branch', '--show-current').decode().strip() == BRANCH
git('diff', '--check')
changed = git('diff', '--name-only', BASE, '-z')
fresh = git('ls-files', '--others', '--exclude-standard', '-z')
paths = sorted({item.decode() for item in (changed + fresh).split(b'\0') if item})
assert paths, 'No reviewed candidate diff remains'
patterns = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
            r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}',
            r'\bgithub_pat_[A-Za-z0-9_]{40,}', r'\bAKIA[0-9A-Z]{16}\b',
            r'\bxox[baprs]-[A-Za-z0-9-]{20,}']
for path in paths:
    assert not path.startswith(('.git/', '.aws/', '.codex/'))
    data = (FEEDS / path).read_bytes()
    assert data == (SOURCE / path).read_bytes(), 'Source mirror differs: ' + path
    for pattern in patterns:
        assert not re.search(pattern, data.decode(errors='replace')), 'Secret pattern in ' + path
scan = {'repository': 'policy-as-versioned-feeds/feeds', 'paths': paths,
        'high_confidence_secret_findings': 0,
        'scope': 'Changed public primary corpus and feed adapters; no credential files or private user data',
        'file_sha256': {path: hashlib.sha256((FEEDS / path).read_bytes()).hexdigest() for path in paths}}
(HERE / 'feeds-publication-secret-scan.json').write_text(json.dumps(scan, indent=2, sort_keys=True) + '\n')
if git('status', '--porcelain'):
    git('add', '--', *paths)
    message = ('feeds: publish captured KEV and HMRC inputs plus cited agent threat frequency\n\n'
               'Prepare cve 3.0.0, fx 1.1.0 and threat-register 4.0.0 behind review.\n\n'
               'Prepared-by: Codex agent; no human was present during preparation.\n'
               'No release tags or adopter bindings were created.\n')
    subprocess.run(['git', 'commit', '-F', '-'], cwd=FEEDS, input=message, text=True,
                   capture_output=True, check=True)
assert not git('status', '--porcelain'), 'Candidate tree is not clean after preparation'
commit = git('rev-parse', 'HEAD').decode().strip()
patch = git('diff', BASE, 'HEAD', '--binary', '--no-ext-diff', '--no-textconv')
(ROOT / '.scratch/ecosystem/patches/resume-2026-10-03/feeds-reviewed-publication.patch').write_bytes(patch)
checkpoint = {'repository': 'policy-as-versioned-feeds/feeds', 'branch': BRANCH,
              'base': BASE, 'commit': commit, 'paths': paths,
              'patch_sha256': hashlib.sha256(patch).hexdigest(),
              'cuts': ['cve/v3.0.0', 'fx/v1.1.0', 'threat-register/v4.0.0'],
              'external_writes': 'not performed by this local-only preparation',
              'local_signature': 'ordinary repository signing configuration; workflow release tag remains the feed signature'}
(HERE / 'feeds-publication-checkpoint.json').write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + '\n')
print('PASS: complete source mirror, zero high-confidence secret findings, clean local source commit ' + commit)
