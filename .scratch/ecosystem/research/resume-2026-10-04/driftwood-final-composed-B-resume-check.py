"""Complete the saved normal signed DW pointer proof; no source or remote writes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

day = Path(__file__).resolve().parent
path = day / 'driftwood-final-composed-B-candidate.json'
packet = json.loads(path.read_text())
repo = Path(packet['directory'])
estate = repo.parent
head, base = packet['head'], packet['base']
env = dict(os.environ, PAVF_REAL_ESTATE=str(estate), PYTHONPATH=str(repo/'tests'),
           PYTHONDONTWRITEBYTECODE='1', GITSIGN_REKOR_MODE='offline')

def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

def sha(data):
    return hashlib.sha256(data).hexdigest()

assert git('rev-parse', 'HEAD') == head
assert git('rev-parse', 'HEAD^{tree}') == packet['tree']
assert git('log', '-1', '--format=%G?') == 'G'
assert not git('status', '--porcelain', '--untracked-files=all')
failed = day/'driftwood-final-composed-B-helper-CLI-negative.json'
if not failed.exists():
    failed.write_text(json.dumps(packet['checks']['gate'], indent=2)+'\n')
    (day/'driftwood-final-composed-B-helper-CLI-negative.log').write_bytes(
        (day/'driftwood-final-composed-B-gate.log').read_bytes())

out = day/'driftwood-final-composed-B-gate.json'
commands = {
    'gate': [sys.executable, '.github/scripts/adopter-gate.py', 'compose',
             str(estate/'platform'), 'v4.0.1', 'UNRELEASED-FINAL-COMPOSED-POINTER',
             '--adopter-dir', str(repo), '--base-ref', base, '--head-ref', head,
             '--out', str(out)],
    'postcommit-real-layout': [sys.executable, '-m', 'unittest', 'discover',
                              '-s', 'tests', '-p', 'test_platform_tools.py', '-v'],
}
for name, argv in commands.items():
    result = subprocess.run(argv, cwd=repo, env=env, text=True, capture_output=True, timeout=300)
    log = day/f'driftwood-final-composed-B-{name}.log'
    log.write_text(result.stdout+result.stderr)
    packet['checks'][name] = {'argv': argv, 'exit': result.returncode,
                             'log': str(log), 'log_sha256': sha(log.read_bytes())}
    path.write_text(json.dumps(packet, indent=2, sort_keys=True)+'\n')
    assert result.returncode == 0, result.stdout+result.stderr
    if name == 'gate':
        grade = json.loads(out.read_text())['result']
        assert grade['declared_bump'] == grade['composed_bump'] == 'none'
        assert grade['added'] == grade['retired'] == []
        packet['checks'][name]['result'] = grade
        packet['measured_bump'] = 'none'
    else:
        assert 'skipped' not in result.stderr
    print(name, 'PASS', flush=True)
assert git('rev-parse', 'HEAD') == head
assert not git('status', '--porcelain', '--untracked-files=all')
patch = day/'driftwood-final-composed-B.patch'
subprocess.run(['git', '-C', str(repo), 'apply', '--reverse', '--check', str(patch)], check=True)
packet.update(source_clean=True, patch_sha256=sha(patch.read_bytes()),
              authentic_release_receipt=str(day/'driftwood-composition-B-authentic-release.json'),
              authentic_release_receipt_sha256=sha((day/'driftwood-composition-B-authentic-release.json').read_bytes()))
path.write_text(json.dumps(packet, indent=2, sort_keys=True)+'\n')
(day/'driftwood-final-composed-B-PR-body.md').write_text('''Move composed delivery to the genuine signed and published v4.0.1 Composition B release, whose tree binds apps and the native inventory to v4.0.0 Source A. Apps and inventory retain their genuine A source, and policies 5.0.0, 6.0.0 and 7.0.0 retain all four signature gates.

Only the composed source reference and its explanatory comments change, with a fresh derived HEADER comparison fingerprint. All remaining source bytes are preserved. Signed v5.0.0 tools re-render and verify byte-for-byte; reach against authentic v4.0.1, the exact-head institutional none gate, and three enabled real-estate public layout tests pass. Engine 1.18.2 and the existing cloud declaration are preserved. Live reconciliation is established by the scheduled observer.
''')
print('Exact final composed-only candidate ready:', head, flush=True)
