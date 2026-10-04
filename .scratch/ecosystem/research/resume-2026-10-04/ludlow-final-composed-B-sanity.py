"""Precisely constrain final LU delivery to the real B composed pointer and fingerprint."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import yaml
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
A = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate/ludlow')
BASE = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
SOURCE_A = 'c5f33cc8982fc9bfeb7fcc2068ea8de0dda63dae'
def git(*args):
    return subprocess.check_output(['git', '-C', str(A), *args])
def sha(data):
    return hashlib.sha256(data).hexdigest()
assert git('rev-parse', 'HEAD').decode().strip() == BASE
assert git('branch', '--show-current').decode().strip() == 'delivery-stage2-composed-B-20261004'
changed = git('diff', '--name-only', BASE).decode().splitlines()
assert changed == ['composed/HEADER.yaml', 'gitops/composed/composed-set.yaml'], changed
assert not git('ls-files', '--others', '--exclude-standard').strip()
all_paths = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
preserved = {}
for path in all_paths:
    if path not in changed:
        old = git('show', BASE + ':' + path)
        assert (A / path).read_bytes() == old, path
        preserved[path] = sha(old)
old_header = yaml.safe_load(git('show', BASE + ':composed/HEADER.yaml'))
new_header = yaml.safe_load((A / 'composed/HEADER.yaml').read_text())
old_after = old_header['comparison-inputs']['after']
new_after = new_header['comparison-inputs']['after']
assert old_after != new_after
old_header['comparison-inputs']['after'] = new_after
assert old_header == new_header
old_docs = list(yaml.safe_load_all(git('show', BASE + ':gitops/composed/composed-set.yaml')))
new_docs = list(yaml.safe_load_all((A / 'gitops/composed/composed-set.yaml').read_text()))
sources = [d for d in old_docs if d and d.get('kind') == 'GitRepository']
assert len(sources) == 1 and sources[0]['spec']['ref'] == {'tag': 'v4.0.0', 'commit': SOURCE_A}
sources[0]['spec']['ref'] = {'tag': 'v4.0.1', 'commit': BASE}
assert old_docs == new_docs
apps = [d for d in yaml.safe_load_all((A / 'gitops/flux-system/gotk-sync.yaml').read_text()) if d and d.get('kind') == 'GitRepository']
assert len(apps) == 1 and apps[0]['spec']['ref'] == {'tag': 'v4.0.0', 'commit': SOURCE_A}
prov = json.loads((A / 'inventory/PROVENANCE.json').read_text())
assert prov['apps_source']['commit'] == SOURCE_A and prov['apps_source']['tag'] == 'v4.0.0'
diff = git('diff', '--binary', BASE)
assert not re.search(rb'AKIA[A-Z0-9]{16}|ASIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-live-[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', diff)
(E / 'ludlow-final-composed-B.patch').write_bytes(diff)
result = {'base': BASE, 'changed_paths': changed, 'preserved_other_paths_sha256': preserved,
    'HEADER_only_changed_field': 'comparison-inputs.after', 'comparison_after_before': old_after,
    'comparison_after_new': new_after, 'parsed_change_only_composed_ref': True,
    'apps_source_A_and_primary_valuation_bytes_preserved': True,
    'high_confidence_changed_source_secret_matches': 0, 'remote_mutations': False,
    'authentic_B_receipt': 'ludlow-composition-B-authentic-release.json'}
(E / 'ludlow-final-composed-B-sanity.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('PASS: exact two paths, fingerprint only, all other source/primary bytes preserved.')
