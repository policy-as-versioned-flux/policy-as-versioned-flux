"""Finite local proof for separate DW delivery-order/moved maintenance; no remote writes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

day = Path(__file__).resolve().parent
loc = json.loads((day/'driftwood-delivery-order-maintenance-final-checkout.json').read_text())
repo, estate, base = Path(loc['directory']), Path(loc['directory']).parent, loc['base']
env = dict(os.environ, GITSIGN_REKOR_MODE='offline', PYTHONDONTWRITEBYTECODE='1',
           PAVF_REAL_ESTATE=str(estate),
           PATH=str(Path(sys.executable).parent)+os.pathsep+os.environ.get('PATH', ''))
packet = {'scope': 'Separate native admission ordering and current-version moved selfcheck',
          'directory': str(repo), 'estate': str(estate), 'base': base,
          'checks': {}, 'remote_mutations': False, 'cloud_activation': False,
          'engine_preserved': '1.18.2', 'webhook_readiness_claimed': False}
output = day/'driftwood-delivery-order-maintenance-candidate.json'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

def save():
    output.write_text(json.dumps(packet, indent=2)+'\n')

def run(name, argv, expected=0):
    done = subprocess.run(argv, cwd=repo, env=env, text=True, capture_output=True, timeout=300)
    log = day/f'driftwood-delivery-order-maintenance-{name}.log'
    log.write_text(done.stdout+done.stderr)
    packet['checks'][name] = {'argv': argv, 'exit': done.returncode,
                             'log': str(log), 'sha256': sha(log.read_bytes())}
    save()
    assert done.returncode == expected, done.stdout+done.stderr
    print(name, 'PASS', flush=True)
    return done

assert git('rev-parse', 'HEAD') == base
assert git('branch', '--show-current') == loc['branch']
assert subprocess.check_output(['git', '-C', str(estate/'platform-tools'), 'rev-parse', 'HEAD'],
                               text=True).strip() == '703eff6aee959843c4160aa54fd03413f62858cc'
for action in ('compose', 'verify'):
    run(action, [sys.executable, '.github/scripts/platform-tools.py', '--adopter-dir', '.',
                 '--tools-dir', '../platform-tools', action, '.', '--estate-clone', '..'])
run('reach', [sys.executable, 'scripts/render_composed.py', 'reach', '--ref', 'v4.0.1'])
tests = run('public-tests', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
assert 'skipped' not in tests.stderr
helper = run('moved-selfcheck', ['bash', 'twin/verify-twin-sweep-moved.sh'], expected=3)
assert 'TOTAL: 4 pass, 0 fail, 1 could-not-look' in helper.stdout
assert 'moved path has not fired live yet' in helper.stdout
expected = {'composed/HEADER.yaml', 'gitops/flux-system/gotk-sync.yaml',
            'twin/verify-twin-sweep-moved.sh'}
assert set(git('diff', '--name-only').splitlines()) == expected
for path in git('ls-tree', '-r', '--name-only', base).splitlines():
    if path not in expected:
        assert (repo/path).read_bytes() == subprocess.check_output(
            ['git', '-C', str(repo), 'show', base+':'+path]), path
assert git('status', '--porcelain', '--untracked-files=all').splitlines()[-1] == '?? tests/test_apps_dependencies.py'
run('diff-check', ['git', 'diff', '--check'])
subprocess.run(['git', '-C', str(repo), 'add', '--', *sorted(expected),
                'tests/test_apps_dependencies.py'], check=True)
message = ('Order native apps after the complete composed policy window\n\n'
           'Wait on the actual 5/6/7 Flux policy Kustomizations and machinery before native '
           'admission. Prove the expanded dependency graph is complete and acyclic. '
           'Make the offline moved selfcheck mutate the current emitter VERSION and keep '
           'retained major feed history outside the current clock. Preserve signed Apps A/Composition B '
           'pins, measured inventory, native claims and engine declaration. Flux readiness does '
           'not supply a missing primary webhook or live-workload observation.\n\n'
           'Prepared-by: Codex agent; no human was present during preparation.')
subprocess.run(['git', '-C', str(repo), 'commit', '-m', message], check=True)
head = git('rev-parse', 'HEAD')
assert git('log', '-1', '--format=%G?') == 'G'
run('source-signature', ['git', 'verify-commit', head])
packet.update(head=head, tree=git('rev-parse', 'HEAD^{tree}'), branch=git('branch', '--show-current'),
              normal_SSH_signature='G', changed_paths=git('diff', '--name-only', base, head).splitlines())
patch = day/'driftwood-delivery-order-maintenance.patch'
patch.write_bytes(subprocess.check_output(['git', '-C', str(repo), 'diff', '--binary', '--full-index', base, head]))
packet.update(patch=str(patch), patch_sha256=sha(patch.read_bytes()),
              file_sha256={path: sha((repo/path).read_bytes()) for path in packet['changed_paths']})
save()
out = day/'driftwood-delivery-order-maintenance-gate.json'
run('gate', [sys.executable, '.github/scripts/adopter-gate.py', 'compose',
             str(estate/'platform'), 'v4.0.1', 'UNRELEASED-DELIVERY-ORDER-MAINTENANCE',
             '--adopter-dir', str(repo), '--base-ref', base, '--head-ref', head, '--out', str(out)])
grade = json.loads(out.read_text())['result']
assert grade['declared_bump'] == grade['composed_bump'] == 'none'
assert grade['added'] == grade['retired'] == []
packet['checks']['gate']['result'] = grade
packet['measured_bump'] = 'none'
run('postcommit-verify', [sys.executable, '.github/scripts/platform-tools.py', '--adopter-dir', '.',
                        '--tools-dir', '../platform-tools', 'verify', '.', '--estate-clone', '..'])
assert not git('status', '--porcelain', '--untracked-files=all')
packet['source_clean'] = True
packet['publication_hold'] = 'Fresh exact Standards/Spec review and ordinary authorized publication'
save()
print('Separate maintenance candidate ready:', head, flush=True)
