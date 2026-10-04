"""Prepare only LU's composed source pointer after genuine B publication."""
from pathlib import Path
import json
import subprocess
import yaml
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
A = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate/ludlow')
BASE = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
SOURCE_A = 'c5f33cc8982fc9bfeb7fcc2068ea8de0dda63dae'
git = lambda *args: subprocess.check_output(['git', '-C', str(A), *args]).decode().strip()
assert git('rev-parse', 'HEAD') == git('rev-parse', 'origin/main') == BASE
assert not git('status', '--porcelain', '--untracked-files=all')
assert git('branch', '--show-current') == 'delivery-stage2-composed-B-20261004'
receipt = json.loads((E / 'ludlow-composition-B-authentic-release.json').read_text())
assert receipt['tag'] == 'v4.0.1' and receipt['commit'] == BASE
assert receipt['release_conclusion'] == 'success' and all(receipt['signature'][key] is True for key in ('Git', 'Rekor', 'certificate'))
assert git('rev-parse', 'refs/tags/v4.0.1') == receipt['tag_object']
assert git('rev-parse', 'refs/tags/v4.0.1^{commit}') == BASE
path = A / 'gitops/composed/composed-set.yaml'
before = path.read_text()
replacements = {
    '  * apps and composed delivery use the same genuine v4.0.0 Source A release.\n#     Its complete policy window and signature gates move with the inventory binding.':
    '  * apps remain at genuine v4.0.0 Source A; composed serves signed v4.0.1 Composition B.\n#     Composition B renders from Source A\'s apps/inventory binding and carries policy 5/6/7.',
    '    tag: v4.0.0': '    tag: v4.0.1',
    '    commit: ' + SOURCE_A: '    commit: ' + BASE,
    '# The resolved SHA of the genuine signed v4.0.0 Source A release.': '# The resolved SHA of the genuine signed v4.0.1 Composition B release.',
}
after = before
for old, new in replacements.items():
    assert after.count(old) == 1, old
    after = after.replace(old, new)
old_documents = list(yaml.safe_load_all(before))
new_documents = list(yaml.safe_load_all(after))
expected = old_documents.copy()
expected = json.loads(json.dumps(expected))
sources = [d for d in expected if d and d.get('kind') == 'GitRepository']
assert len(sources) == 1 and sources[0]['metadata']['name'] == 'ludlow-composed'
assert sources[0]['spec']['ref'] == {'tag': 'v4.0.0', 'commit': SOURCE_A}
sources[0]['spec']['ref'] = {'tag': 'v4.0.1', 'commit': BASE}
assert new_documents == expected
path.write_text(after)
assert git('diff', '--name-only') == 'gitops/composed/composed-set.yaml'
(E / 'ludlow-final-composed-B-prepare.json').write_text(json.dumps({
    'base': BASE, 'branch': 'delivery-stage2-composed-B-20261004',
    'apps_stays': {'tag': 'v4.0.0', 'commit': SOURCE_A},
    'composed_target': {'tag': 'v4.0.1', 'commit': BASE, 'tag_object': receipt['tag_object']},
    'parsed_change_only_composed_ref': True, 'gates_array_and_engine_cloud_unchanged': True,
    'source_edits': ['gitops/composed/composed-set.yaml'], 'remote_mutations': False,
    'authentic_release': 'ludlow-composition-B-authentic-release.json'}, indent=2) + '\n')
print('Prepared exact genuine composed B pointer; apps/provenance/array/gates unchanged.')
