"""Separate fresh public clones, preserving all immutable final delivery branches."""
from pathlib import Path
import json
import subprocess
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
original = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7')
result = {'scope': 'Separate local scenario/ordering maintenance, no remote mutation', 'adopters': {}}
for org in ('ludlow', 'tuppence'):
    estate = Path('/private/tmp') / ('pavf-' + org + '-maintenance-20261004-estate')
    repo = estate / org
    estate.mkdir(exist_ok=True)
    assert not repo.exists(), repo
    argv = ['git', 'clone', '--quiet', f'https://github.com/policy-as-versioned-{org}/{org}', str(repo)]
    subprocess.run(argv, check=True)
    base = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    subprocess.run(['git', '-C', str(repo), 'switch', '-c', 'maintenance/2026-10-04-scenario-and-apps-order'], check=True)
    for name in ('platform-tools', 'platform', 'nist', 'ico', 'feeds', 'insurer'):
        target = original / (org + '-estate') / name
        if target.is_dir():
            (estate / name).symlink_to(target, target_is_directory=True)
    result['adopters'][org] = {'directory': str(repo), 'estate': str(estate), 'actual_base': base,
        'branch': 'maintenance/2026-10-04-scenario-and-apps-order', 'source_untouched': True}
    (E / 'adopter-scenario-order-maintenance-checkouts.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Prepared separate fresh', org, base, flush=True)
