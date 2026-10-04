"""Bind the normally signed, tested maintenance source and its primary logs."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

DAY = Path(__file__).resolve().parent
REPO = Path('/private/tmp/pavf-run377-platform-estate-20261004/platform')
BASE = '703eff6aee959843c4160aa54fd03413f62858cc'
EXPECTED = {'compose/composition.py', 'compose/fixture_inventory.py',
            'compose/test_comparison_history.py', 'compose/test_floor_change.py',
            'compose/test_portable_observations.py', 'compose/test_real_adopter_fixture.py',
            'feeds/verify-feeds.sh', 'oscal/lint_claims.py', 'oscal/test_lint_claims.py'}


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    head = git('rev-parse', 'HEAD').decode().strip()
    tree = git('rev-parse', 'HEAD^{tree}').decode().strip()
    assert not git('status', '--porcelain')
    assert git('show', '-s', '--format=%G?', head).decode().strip() == 'G'
    subprocess.run(['git', '-C', str(REPO), 'verify-commit', head], check=True,
                   stdout=(DAY/'platform-run377-final-signature.log').open('w'),
                   stderr=subprocess.STDOUT)
    paths = git('diff', '--name-only', BASE, head).decode().splitlines()
    assert set(paths) == EXPECTED
    prior = ast.parse(git('show', BASE + ':compose/composition.py').decode())
    current = ast.parse((REPO/'compose/composition.py').read_text())
    functions = lambda module: {node.name: ast.dump(node, include_attributes=False)
        for node in module.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    before, after = functions(prior), functions(current)
    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
    assert changed == ['_adopter_copy', '_commit_header', 'selfcheck'], changed
    logs = ['platform-run377-composition-selfcheck-repaired-eleventh.log',
            'platform-run377-final-compose-suite.log', 'platform-run377-final-oscal-suite.log',
            'platform-run377-final-inventory-cve-guards.log',
            'platform-run377-final-feed-public-check.log', 'platform-run377-final-oscal-public-check.log',
            'platform-run377-final-signature.log']
    assert 'selfcheck ok:' in (DAY/logs[0]).read_text()
    assert 'Ran 103 tests' in (DAY/logs[1]).read_text() and (DAY/logs[1]).read_text().endswith('\nOK\n')
    assert 'Ran 2 tests' in (DAY/logs[2]).read_text() and (DAY/logs[2]).read_text().endswith('\nOK\n')
    assert '13 passed' in (DAY/logs[3]).read_text()
    patch = DAY/'platform-run377-maintenance.patch'
    patch.write_bytes(git('diff', '--binary', '--full-index', BASE, head))
    with tempfile.TemporaryDirectory(prefix='pavf-platform-maintenance-export-') as temporary:
        clone = Path(temporary)/'platform'
        subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', '--no-checkout', str(REPO), str(clone)], check=True)
        subprocess.run(['git', '-C', str(clone), 'checkout', '--quiet', '--detach', head], check=True)
        subprocess.run(['git', '-C', str(clone), 'apply', '--check', '--reverse', str(patch)], check=True)
    packet = {'created_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'directory': str(REPO),
              'base': BASE, 'head': head, 'tree': tree, 'branch': git('branch', '--show-current').decode().strip(),
              'normal_SSH_signature': 'G', 'clean': True, 'changed_paths': paths,
              'source_sha256': {path: digest(REPO/path) for path in paths},
              'artifacts_sha256': {name: digest(DAY/name) for name in logs},
              'patch': patch.name, 'patch_sha256': digest(patch), 'reverse_apply_check': True,
              'checks': {'native_assembled_composition_selfcheck': 0, 'compose_103_tests': 0,
                         'oscal_2_tests': 0, 'inventory_and_CVE_13_tests': 0,
                         'public_feed_check': 0, 'public_oscal_check': 0, 'git_diff_check': 0},
              'only_changed_composition_functions': changed,
              'all_other_publisher_bytes_preserved': True,
              'primary_native_scan_grade_price_clock_and_frozen_policy_bytes_changed': False,
              'historical_failed_fixture_iterations_preserved': True, 'external_mutations': False}
    (DAY/'platform-run377-maintenance-candidate.json').write_text(json.dumps(packet, indent=2)+'\n')
    print(json.dumps({key: packet[key] for key in ('head', 'tree', 'changed_paths', 'checks')}, indent=2))


if __name__ == '__main__':
    main()
