"""Export final exact reviewed-source candidate after normal checks complete."""
from pathlib import Path
import hashlib
import json
import subprocess
import yaml
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
A = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate/ludlow')
HEAD = 'b84006a176e6c783bbb45fc2463c46be6ba73071'
TREE = '3cd9ee3f18b4cd5c189e747a540b143988aee073'
BASE = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
SOURCE_A = 'c5f33cc8982fc9bfeb7fcc2068ea8de0dda63dae'
def git(*args):
    return subprocess.check_output(['git', '-C', str(A), *args])
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert git('rev-parse', 'HEAD').decode().strip() == HEAD
assert git('rev-parse', 'HEAD^{tree}').decode().strip() == TREE
assert not git('status', '--porcelain', '--untracked-files=all').strip()
checks = json.loads((E / 'ludlow-final-composed-B-final-checks.json').read_text())
assert checks['head'] == HEAD and checks['tree'] == TREE and checks['source_still_clean']
assert all(row['exit'] == 0 for row in checks['checks'].values())
for row in checks['checks'].values():
    assert sha(Path(row['log'])) == row['log_sha256']
compose_log = E / 'ludlow-final-composed-B-compose.log'
verify_log = E / 'ludlow-final-composed-B-verify.log'
doc = json.loads(compose_log.read_text())
assert doc['outcome'] == 'composed' and doc['refusals'] == []
assert 'OK: composed artefact re-renders byte-for-byte' in verify_log.read_text()
auth = json.loads((E / 'ludlow-composition-B-authentic-release.json').read_text())
assert auth['commit'] == BASE and auth['tag'] == 'v4.0.1' and auth['release_conclusion'] == 'success'
docs = list(yaml.safe_load_all((A / 'gitops/composed/composed-set.yaml').read_text()))
source = next(d for d in docs if d and d.get('kind') == 'GitRepository')
resources = next(d for d in docs if d and d.get('kind') == 'ResourceSet')
versions = [item['version'] for item in resources['spec']['inputs'][0]['versions']]
gates = source['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates'].split(',')
assert source['spec']['ref'] == {'tag': 'v4.0.1', 'commit': BASE}
assert versions == ['5.0.0', '6.0.0', '7.0.0']
assert gates == ['flux-system/composed-v5-0-0', 'flux-system/composed-v6-0-0', 'flux-system/composed-v7-0-0', 'flux-system/composed-machinery']
files = git('ls-tree', '-r', '--name-only', HEAD).decode().splitlines()
artifacts = ['ludlow-final-composed-B.patch', 'ludlow-final-composed-B-source-signature.log',
    'ludlow-final-composed-B-sanity.json', 'ludlow-final-composed-B-final-checks.json',
    'ludlow-final-composed-B-compose.log', 'ludlow-final-composed-B-verify.log',
    'ludlow-final-composed-B-PR-body.md', 'ludlow-composition-B-authentic-release.json',
    'ludlow-composition-B-published-main-candidate.json']
result = {'scope': 'Final composed-only genuine B pointer; no remote mutation or new live report claim',
    'directory': str(A), 'head': HEAD, 'tree': TREE, 'base': BASE,
    'branch': 'delivery-stage2-composed-B-20261004', 'source_signature': 'G', 'source_clean': True,
    'changed_paths': git('diff', '--name-only', BASE, HEAD).decode().splitlines(),
    'source_files_sha256': {path: sha(A / path) for path in files},
    'apps_source': {'tag': 'v4.0.0', 'commit': SOURCE_A},
    'composed_source': {'tag': 'v4.0.1', 'commit': BASE, 'tag_object': auth['tag_object']},
    'version_array': versions, 'signature_gates': gates,
    'normal_tools_compose': {'exit': 0, 'log': str(compose_log), 'sha256': sha(compose_log)},
    'normal_tools_verify': {'exit': 0, 'log': str(verify_log), 'sha256': sha(verify_log)},
    'exact_postcommit_checks': checks['checks'],
    'all_other_source_primary_and_valuation_bytes_preserved': True,
    'HEADER_only_after_fingerprint_changed': True,
    'retained_engine': '1.18.2', 'cloud_activation': False, 'high_confidence_source_secret_scan_matches': 0,
    'artifact_sha256': {name: sha(E / name) for name in artifacts},
    'authentic_release': auth, 'external_publication_attempted': False,
    'run377_red_primary_evidence_preserved': True,
    'maintenance_edits_excluded': True}
(E / 'ludlow-final-composed-B-candidate.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('READY: exact final b84006a two-path candidate and body, normal checks bound; no external mutation.')
