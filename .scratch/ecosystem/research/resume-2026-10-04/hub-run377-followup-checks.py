"""Record exact local postcommit checks; no network or primary-log mutation."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
DAY = ROOT / '.scratch/ecosystem/research/resume-2026-10-04'
REPO = Path('/private/tmp/pavf-hub-run377-repair-d72i2rav/hub')
PY = str(ROOT / '.venv/bin/python')
result = {'head': subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip(),
          'checks': {}, 'external_mutations': False, 'scheduled_run_regraded': False}
commands = {
    'signature': ['git', 'verify-commit', result['head']],
    'mypy': [PY, '-m', 'mypy', '--explicit-package-bases', '--follow-imports=silent',
             '--ignore-missing-imports', 'verify/_snapshot.py', 'verify/map-surface/map_surface.py',
             'verify/engine-pairing/engine_pairing.py', 'verify/e2e/step2_reprice.py'],
    'focused': [PY, '-m', 'pytest', '-q', 'tests/test_workload_lane_entrypoint.py',
                'tests/test_verifier_snapshots.py', 'tests/test_map_observation_ownership.py',
                'tests/test_truth_manifest.py', 'tests/test_map_surface.py',
                'tests/test_refusal_by_another_name.py'],
    'engine': [PY, str(REPO / 'verify/engine-pairing/engine_pairing.py'), 'check'],
    'e2e': [PY, str(REPO / 'verify/e2e/step2_reprice.py'), '--estate', str(REPO / '.estate-clone')],
}
for name, argv in commands.items():
    p = subprocess.run(argv, cwd=REPO, capture_output=True)
    log = DAY / f'hub-run377-followup-{name}.log'
    log.write_bytes(p.stdout + p.stderr)
    result['checks'][name] = {'argv': argv, 'exit': p.returncode, 'log': str(log),
                            'sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
    (DAY / 'hub-run377-followup-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(name, p.returncode, flush=True)
    if p.returncode:
        raise SystemExit(p.returncode)
result['clean'] = not subprocess.check_output(['git', '-C', str(REPO), 'status', '--porcelain'], text=True).strip()
(DAY / 'hub-run377-followup-checks.json').write_text(json.dumps(result, indent=2) + '\n')
