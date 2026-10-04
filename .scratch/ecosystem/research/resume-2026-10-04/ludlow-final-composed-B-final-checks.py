"""Normal exact-commit LU final pointer checks; no remote actions."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
ESTATE = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate')
A = ESTATE / 'ludlow'
BASE = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
HEAD = 'b84006a176e6c783bbb45fc2463c46be6ba73071'
TREE = '3cd9ee3f18b4cd5c189e747a540b143988aee073'
def git(*args):
    return subprocess.check_output(['git', '-C', str(A), *args])
def sha(data):
    return hashlib.sha256(data).hexdigest()
assert git('rev-parse', 'HEAD').decode().strip() == HEAD
assert git('rev-parse', 'HEAD^{tree}').decode().strip() == TREE
assert git('rev-parse', 'HEAD^').decode().strip() == BASE
assert git('log', '-1', '--format=%G?').decode().strip() == 'G'
assert not git('status', '--porcelain', '--untracked-files=all').strip()
signature = subprocess.run(['git', '-C', str(A), 'verify-commit', HEAD], capture_output=True, text=True, check=True)
(E / 'ludlow-final-composed-B-source-signature.log').write_text(signature.stdout + signature.stderr)
patch = git('diff', '--binary', BASE, HEAD)
assert sha(patch) == sha((E / 'ludlow-final-composed-B.patch').read_bytes())
sanity = json.loads((E / 'ludlow-final-composed-B-sanity.json').read_text())
assert git('diff', '--name-only', BASE, HEAD).decode().splitlines() == sanity['changed_paths']
for path, expected in sanity['preserved_other_paths_sha256'].items():
    assert sha(git('show', HEAD + ':' + path)) == expected, path
environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PAVF_REAL_ESTATE=str(ESTATE), GITSIGN_REKOR_MODE='offline')
identity = r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'
gate_md = E / 'ludlow-final-composed-B-gate.md'
gate = [sys.executable, str(A / '.github/scripts/adopter_gate.py'), '--platform-dir', str(ESTATE / 'platform'),
    '--ludlow-dir', str(A), '--old-ref', BASE, '--new-ref', HEAD, '--composed-base-ref', BASE,
    '--composed-head-ref', HEAD, '--identity-regexp', identity, '--issuer', 'https://token.actions.githubusercontent.com',
    '--out-comment', str(gate_md)]
checks = [('gate', gate),
    ('reach', [sys.executable, str(A / 'scripts/render_composed.py'), 'reach', '--ref', 'v4.0.1']),
    ('postcommit_real_estate_public_tests', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'])]
result = {'head': HEAD, 'tree': TREE, 'base': BASE, 'branch': 'delivery-stage2-composed-B-20261004',
    'normal_SSH_signature': 'G', 'source_clean': True, 'checks': {}, 'remote_mutations': False}
out = E / 'ludlow-final-composed-B-final-checks.json'
def save():
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
save()
for name, argv in checks:
    run = subprocess.run(argv, cwd=A, env=environment, capture_output=True, text=True)
    text = run.stdout + run.stderr
    log = E / ('ludlow-final-composed-B-' + name + '.log')
    log.write_text(text)
    result['checks'][name] = {'argv': argv, 'cwd': str(A), 'PAVF_REAL_ESTATE': str(ESTATE),
        'exit': run.returncode, 'log': str(log), 'log_sha256': sha(log.read_bytes())}
    save()
    assert run.returncode == 0, text
    if name == 'gate':
        markdown = gate_md.read_text()
        assert '| bump | **none** | **none** |' in markdown and 'platform pin unchanged in this PR.' in markdown
        assert git('show', BASE + ':composed/evidence.json') == git('show', HEAD + ':composed/evidence.json')
        result['checks'][name].update({'declared': 'none', 'composed': 'none', 'same_pin_early_return': True,
            'composed_evidence_independently_byte_equal': True, 'markdown_sha256': sha(gate_md.read_bytes())})
    if name == 'postcommit_real_estate_public_tests':
        assert 'RealCompilerLayout.test_composition_bytes_do_not_depend_on_checkout_prefix' in text
        count = re.search(r'Ran (\d+) tests?', text)
        assert count and int(count.group(1)) == 37 and 'skipped' not in text.lower()
        result['checks'][name].update({'test_count': int(count.group(1)), 'skips': 0})
    save()
    print('PASS:', name, flush=True)
assert not git('status', '--porcelain', '--untracked-files=all').strip()
result['source_still_clean'] = True
save()
