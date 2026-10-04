"""Bind actual final public merge to reviewed bytes and genuine A/B receipts."""
from pathlib import Path
import hashlib
import json
import subprocess
import yaml
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
A = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate/ludlow')
MAIN = '179e4e0d8e754044b07a65933754244352e28ec5'
HEAD = 'b84006a176e6c783bbb45fc2463c46be6ba73071'
B = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
SOURCE_A = 'c5f33cc8982fc9bfeb7fcc2068ea8de0dda63dae'
def git(*args):
    return subprocess.check_output(['git', '-C', str(A), *args])
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
candidate = json.loads((E / 'ludlow-final-composed-B-candidate.json').read_text())
merge = json.loads((E / 'ludlow-final-composed-B-actual-merge.json').read_text())
main = json.loads((E / 'ludlow-final-composed-B-main-commit-verification.json').read_text())
assert merge['state'] == 'MERGED' and merge['headRefOid'] == HEAD and merge['mergeCommit']['oid'] == MAIN
assert merge['mergedBy']['login'] == 'app/pavc-other-hand'
assert main['sha'] == MAIN and main['tree']['sha'] == candidate['tree']
assert main['verification']['verified'] is True and main['verification']['reason'] == 'valid'
assert [parent['sha'] for parent in main['parents']] == [B, HEAD]
assert git('rev-parse', 'origin/main').decode().strip() == MAIN
assert git('rev-parse', MAIN + '^{tree}').decode().strip() == candidate['tree']
for path, expected in candidate['source_files_sha256'].items():
    assert hashlib.sha256(git('show', MAIN + ':' + path)).hexdigest() == expected, path
apps = list(yaml.safe_load_all(git('show', MAIN + ':gitops/flux-system/gotk-sync.yaml')))
apps_source = next(doc for doc in apps if doc and doc.get('kind') == 'GitRepository')
docs = list(yaml.safe_load_all(git('show', MAIN + ':gitops/composed/composed-set.yaml')))
composed_source = next(doc for doc in docs if doc and doc.get('kind') == 'GitRepository')
assert apps_source['spec']['ref'] == {'tag': 'v4.0.0', 'commit': SOURCE_A}
assert composed_source['spec']['ref'] == {'tag': 'v4.0.1', 'commit': B}
assert git('rev-parse', 'refs/tags/v4.0.0').decode().strip() == '36a1d2634beb4a2321414b020a6527bc714a0aba'
assert git('rev-parse', 'refs/tags/v4.0.1').decode().strip() == 'efffeee3b39cc59dd5ecc1ac0536845e712d4c6f'
receipts = ['ludlow-atomic-delivery-actual-merge.json', 'ludlow-composition-B-authentic-release.json',
    'ludlow-final-composed-B-candidate.json', 'ludlow-final-composed-B-root-standards-review.json',
    'ludlow-final-composed-B-spec-review.json', 'ludlow-final-composed-B-app-review.json',
    'ludlow-final-composed-B-actual-merge.json', 'ludlow-final-composed-B-main-commit-verification.json']
result = {'status': 'Delivered through ordinary reviewed CI/App/matching-head merges and genuine releases',
    'repository': 'policy-as-versioned-ludlow/ludlow', 'actual_main': MAIN, 'tree': candidate['tree'],
    'actual_main_signature_valid': True, 'reviewed_final_head': HEAD,
    'atomic_PR': 52, 'atomic_main': B, 'final_pointer_PR': 53, 'final_merged_at': merge['mergedAt'],
    'apps_source': apps_source['spec']['ref'], 'composed_source': composed_source['spec']['ref'],
    'B_tag_object': 'efffeee3b39cc59dd5ecc1ac0536845e712d4c6f', 'B_tlog_index': 3077655513,
    'B_cut': 37201479463, 'B_release': 37201969669,
    'complete_policy_window': ['5.0.0', '6.0.0', '7.0.0'], 'four_signature_gates_preserved': True,
    'primary_scans_dates_native_valuation_and_engine_cloud_preserved': True,
    'retained_engine': '1.18.2', 'cloud_activation': False,
    'new_live_PolicyReport_baseline_claimed': False,
    'run377_red_findings_preserved': 'hub-run377-failure-classification.md',
    'maintenance_not_in_delivery_candidate': True,
    'receipts_sha256': {name: sha(E / name) for name in receipts}}
(E / 'ludlow-delivery-complete.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('PASS: actual final main179e4e0 exactly matches reviewed source; A apps, B composed, real receipts intact.')
