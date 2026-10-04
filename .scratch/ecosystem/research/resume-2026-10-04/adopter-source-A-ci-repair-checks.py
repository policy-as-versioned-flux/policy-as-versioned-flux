"""Check only DW/LU CI repairs against genuine full-history signed inputs."""
import json
import os
from pathlib import Path
import subprocess
import sys

DAY = Path(__file__).resolve().parent
LOC = json.loads((DAY / 'adopter-stage2-isolated.json').read_text())
results = {}
for org in ('driftwood', 'ludlow'):
    repo = Path(LOC['adopters'][org]['dir'])
    estate = Path(LOC['adopters'][org]['estate'])
    env = dict(os.environ, GITSIGN_REKOR_MODE='offline', PAVF_REAL_ESTATE=str(estate))
    commands = {
        'compose': [sys.executable, str(repo / '.github/scripts/platform-tools.py'), '--adopter-dir', str(repo), '--tools-dir', str(estate / 'platform-tools'), 'compose', str(repo), '--estate-clone', str(estate)],
        'verify': [sys.executable, str(repo / '.github/scripts/platform-tools.py'), '--adopter-dir', str(repo), '--tools-dir', str(estate / 'platform-tools'), 'verify', str(repo), '--estate-clone', str(estate)],
        'public-tests': [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'],
        'workflow-tests': [sys.executable, '-m', 'unittest', 'discover', '-s', '.github/tests', '-p', 'test_*.py'],
    }
    results[org] = {}
    for label, argv in commands.items():
        done = subprocess.run(argv, cwd=repo, env=env, text=True, capture_output=True, timeout=300)
        log = DAY / f'{org}-source-A-ci-repair-{label}.log'
        log.write_text(done.stdout + done.stderr)
        results[org][label] = {'argv': argv, 'cwd': str(repo), 'PAVF_REAL_ESTATE': str(estate), 'exit': done.returncode, 'log': str(log)}
        (DAY / 'adopter-source-A-ci-repair-checks.json').write_text(json.dumps(results, indent=2) + '\n')
        print(org, label, done.returncode, flush=True)
        if done.returncode:
            print((done.stdout + done.stderr)[-3500:], flush=True)
            raise SystemExit(done.returncode)
