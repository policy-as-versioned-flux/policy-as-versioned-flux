"""Independently bind the six-path maintenance to the newly observed mains."""
import hashlib
import json
from pathlib import Path
import subprocess

import yaml

DAY = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    packet = DAY/'adopter-scenario-order-current-clock-maintenance-candidates.json'
    candidates = json.loads(packet.read_text())['adopters']
    checks_path = DAY/'adopter-scenario-order-current-clock-maintenance-postcommit.json'
    checks = json.loads(checks_path.read_text())['adopters']
    output = {'axis': 'Standards', 'verdict': 'PASS', 'candidate_sha256': sha(packet),
              'adopters': {}, 'substantive_findings': []}
    for name, row in candidates.items():
        repo = Path(row['directory'])
        def git(*args):
            return subprocess.check_output(['git', '-C', str(repo), *args])
        assert git('rev-parse', 'HEAD').decode().strip() == row['head']
        assert git('rev-parse', 'HEAD^{tree}').decode().strip() == row['tree']
        assert git('show', '-s', '--format=%G?', 'HEAD').decode().strip() == 'G'
        assert not git('status', '--porcelain')
        assert sorted(git('diff', '--name-only', row['base'], row['head']).decode().splitlines()) == sorted(row['changed_paths'])
        for path, expected in row['committed_source_sha256'].items():
            assert sha(repo/path) == expected, path
        for path, expected in row['original_tracked_sha256'].items():
            if path not in row['changed_paths']:
                assert sha(repo/path) == expected, path
        assert git('show', row['base']+':observations/twin-sweep.jsonl') == (repo/'observations/twin-sweep.jsonl').read_bytes()
        old = yaml.safe_load(git('show', row['base']+':composed/HEADER.yaml'))
        new = yaml.safe_load((repo/'composed/HEADER.yaml').read_text())
        del old['comparison-inputs']['after'], new['comparison-inputs']['after']
        assert old == new
        assert sha(DAY/row['patch']) == row['patch_sha256']
        body = DAY/(name+'-scenario-order-current-clock-maintenance-PR-body.md')
        assert sha(body) == row['PR_body_sha256']
        assert sha(checks_path) == row['postcommit_checks_sha256']
        check = checks[name]
        assert check['head'] == row['head'] and check['tree'] == row['tree']
        for kind, proof in check['checks'].items():
            assert proof['exit'] == 0, kind
            assert sha(Path(proof['log'])) == proof['log_sha256'], kind
        assert check['checks']['public-tests']['test_count'] == 47
        assert check['checks']['public-tests']['skips'] == 0
        assert check['checks']['gate']['composed_evidence_independently_byte_equal']
        log = DAY/(name+'-current-clock-root-standards-tests.log')
        assert '10 passed, 19 subtests passed' in log.read_text()
        output['adopters'][name] = {'head': row['head'], 'tree': row['tree'], 'base': row['base'],
            'normal_signature': 'G', 'clean': True, 'source_and_primary_artifact_hashes_match': True,
            'HEADER_fingerprint_only': True, 'actual_clock_preserved': True,
            'all_other_source_bytes_preserved': True, 'independent_tests': 10, 'independent_subtests': 19,
            'independent_test_log_sha256': sha(log)}
    (DAY/'adopter-scenario-order-current-clock-maintenance-root-standards-review.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
