"""Bind fresh normal Composition B to actual published LU main; no external writes."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import yaml

HUB = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
E = HUB / '.scratch/ecosystem/research/resume-2026-10-04'
ESTATE = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate')
A = ESTATE / 'ludlow'
HEAD = '3b57f0ce3a9b3da79abf78d4a0ab3ff67dc6e289'
TREE = 'deff0089ff3c28f68d7fb0d097c926d7de4f6b63'
SOURCE_A = 'c5f33cc8982fc9bfeb7fcc2068ea8de0dda63dae'
ATOMIC = '6de0d00ce850ea820777f46fbea5c93a3238ea68'
TAG_OBJECT = '36a1d2634beb4a2321414b020a6527bc714a0aba'
TOOLS = '703eff6aee959843c4160aa54fd03413f62858cc'

def git(*args):
    return subprocess.check_output(['git', '-C', str(A), *args])

def sha(data):
    return hashlib.sha256(data).hexdigest()

assert git('rev-parse', 'HEAD').decode().strip() == HEAD
assert git('rev-parse', 'origin/main').decode().strip() == HEAD
assert git('rev-parse', 'HEAD^{tree}').decode().strip() == TREE
assert git('branch', '--show-current').decode().strip() == 'delivery-stage2-composition-B-20261004'
assert not git('status', '--porcelain', '--untracked-files=all').strip()
receipt = E / 'ludlow-composition-B-main-commit-verification.json'
main = json.loads(receipt.read_text())
assert main['sha'] == HEAD and main['tree']['sha'] == TREE
assert main['verification']['verified'] is True and main['verification']['reason'] == 'valid'
assert main['verification']['payload'].startswith('tree ' + TREE + '\n')
assert [p['sha'] for p in main['parents']] == [SOURCE_A, ATOMIC]
for branch, expected in [
    ('delivery-stage2-20261004', '323a1b09dc9d7f4c243c66a3f53f12ea1a4cfeea'),
    ('delivery-stage2-atomic-20261004', ATOMIC),
]:
    assert git('rev-parse', branch).decode().strip() == expected
assert git('rev-parse', 'refs/tags/v4.0.0').decode().strip() == TAG_OBJECT
assert git('rev-parse', 'refs/tags/v4.0.0^{commit}').decode().strip() == SOURCE_A
assert subprocess.check_output(['git', '-C', str(ESTATE / 'platform-tools'), 'rev-parse', 'HEAD'], text=True).strip() == TOOLS

spec = importlib.util.spec_from_file_location('released_inventory', ESTATE / 'platform-tools/wargamer/inventory.py')
inventory_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory_module)
inventory = json.loads((A / 'inventory/images.json').read_text())
provenance = json.loads((A / 'inventory/PROVENANCE.json').read_text())
images = inventory_module.served_images(A)
inventory_module.validate(A, inventory)
version = json.loads((HUB / '.scratch/ecosystem/research/resume-2026-10-03/adopter-stage2-trivy-raw/version-before.json').read_text())
for row in provenance['images']:
    raw = HUB / row['raw_report']
    assert sha(raw.read_bytes()) == row['raw_report_sha256']
    trimmed = inventory_module.trim(row['requested_image'], json.loads(raw.read_text()), version)
    assert trimmed == next(r for r in inventory['images'] if r['image'] == row['requested_image'])
assert provenance['apps_source']['tag'] == 'v4.0.0'
assert provenance['apps_source']['commit'] == SOURCE_A
assert provenance['apps_source']['tag_object'] == TAG_OBJECT

compose_log = E / 'ludlow-composition-B-published-main-compose.log'
verify_log = E / 'ludlow-composition-B-published-main-verify.log'
document = json.loads(compose_log.read_text())
assert document['outcome'] == 'composed' and document['refusals'] == []
assert 'OK: composed artefact re-renders byte-for-byte' in verify_log.read_text()
assert (A / 'composed/evidence.json').read_bytes() == git('show', HEAD + ':composed/evidence.json')
assert git('show', SOURCE_A + ':composed/evidence.json') == git('show', HEAD + ':composed/evidence.json')

identity = r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'
gate_md = E / 'ludlow-composition-B-published-main-gate.md'
gate_argv = [sys.executable, str(A / '.github/scripts/adopter_gate.py'),
    '--platform-dir', str(ESTATE / 'platform'), '--ludlow-dir', str(A),
    '--old-ref', SOURCE_A, '--new-ref', HEAD, '--composed-base-ref', SOURCE_A,
    '--composed-head-ref', HEAD, '--identity-regexp', identity,
    '--issuer', 'https://token.actions.githubusercontent.com', '--out-comment', str(gate_md)]
gate = subprocess.run(gate_argv, cwd=A, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), capture_output=True, text=True)
gate_log = E / 'ludlow-composition-B-published-main-gate.log'
gate_log.write_text(gate.stdout + gate.stderr)
assert gate.returncode == 0, gate.stdout + gate.stderr
markdown = gate_md.read_text()
assert '| bump | **none** | **none** |' in markdown
assert 'platform pin unchanged in this PR.' in markdown
reach_argv = [sys.executable, str(A / 'scripts/render_composed.py'), 'reach', '--ref', 'v4.0.0']
reach = subprocess.run(reach_argv, cwd=A, capture_output=True, text=True)
reach_log = E / 'ludlow-composition-B-published-main-reach.log'
reach_log.write_text(reach.stdout + reach.stderr)
assert reach.returncode == 0, reach.stdout + reach.stderr
files = git('ls-tree', '-r', '--name-only', HEAD, '--', 'composed').decode().splitlines()
hashes = {p: sha((A / p).read_bytes()) for p in files}
for p in files:
    assert (A / p).read_bytes() == git('show', HEAD + ':' + p), p
assert not git('status', '--porcelain', '--untracked-files=all').strip()
header = yaml.safe_load((A / 'composed/HEADER.yaml').read_text())
result = {
    'scope': 'Fresh Composition B on actual published main; no cut/tag/workflow execution',
    'head': HEAD, 'tree': TREE, 'origin_main': HEAD,
    'branch': 'delivery-stage2-composition-B-20261004',
    'GitHub_merge_signature_verified': True, 'main_commit_receipt_sha256': sha(receipt.read_bytes()),
    'source_A_tag': 'v4.0.0', 'source_A_commit': SOURCE_A, 'source_A_tag_object': TAG_OBJECT,
    'tools_tag': 'v5.0.0', 'tools_commit': TOOLS,
    'fresh_normal_compose': {'exit': 0, 'log': str(compose_log), 'sha256': sha(compose_log.read_bytes()),
        'argv': [sys.executable, '.github/scripts/platform-tools.py', '--adopter-dir', '.', '--tools-dir', '../platform-tools', 'compose', '.', '--estate-clone', '..']},
    'fresh_normal_verify': {'exit': 0, 'log': str(verify_log), 'sha256': sha(verify_log.read_bytes()),
        'argv': [sys.executable, '.github/scripts/platform-tools.py', '--adopter-dir', '.', '--tools-dir', '../platform-tools', 'verify', '.', '--estate-clone', '..']},
    'source_output_diff': [], 'source_clean_after_fresh_rerender': True,
    'rendered_files_sha256': hashes, 'recorded_comparison_after': header['comparison-inputs']['after'],
    'inventory_graph_and_primary_trim_passed': True, 'served_images': images,
    'inventory_sha256': sha((A / 'inventory/images.json').read_bytes()),
    'institutional_gate': {'argv': gate_argv, 'exit': 0, 'declared': 'none', 'composed': 'none',
        'same_pin_early_return': True, 'composed_evidence_independently_byte_equal': True,
        'log_sha256': sha(gate_log.read_bytes()), 'markdown_sha256': sha(gate_md.read_bytes())},
    'genuine_source_A_reach': {'argv': reach_argv, 'exit': 0, 'stdout': reach.stdout, 'log_sha256': sha(reach_log.read_bytes())},
    'original_source_A_and_atomic_branches_preserved': True,
    'future_source_B_tag_created': False, 'remote_mutations': False,
    'live_observation_or_activation_claimed': False,
}
(E / 'ludlow-composition-B-published-main-candidate.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('PASS: actual published 3b57f0c fresh normal Composition B, byte-equal outputs, genuine A graph/primary trim, none gate')
