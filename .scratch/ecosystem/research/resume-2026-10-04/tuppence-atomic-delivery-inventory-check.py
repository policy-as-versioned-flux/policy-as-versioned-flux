"""Validate existing primary scans against the genuine released apps graph."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile

HUB = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
ESTATE = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/tuppence-estate')
ADOPTER = ESTATE / 'tuppence'
EVIDENCE = HUB / '.scratch/ecosystem/research/resume-2026-10-04'
TAG = 'v4.0.0'
COMMIT = 'f575dc12de130c444d98a831de0ca21fd68b9c46'
TAG_OBJECT = '17070ad568397bb7c394f80cb0d51ebcf560089e'
TOOLS_COMMIT = '703eff6aee959843c4160aa54fd03413f62858cc'

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()

def sha(data):
    return hashlib.sha256(data).hexdigest()

assert git(ADOPTER, 'rev-parse', 'origin/main') == COMMIT
assert git(ADOPTER, 'rev-parse', 'refs/tags/' + TAG) == TAG_OBJECT
assert git(ADOPTER, 'rev-parse', 'refs/tags/' + TAG + '^{commit}') == COMMIT
assert git(ESTATE/'platform-tools', 'rev-parse', 'HEAD') == TOOLS_COMMIT
assert not git(ESTATE/'platform-tools', 'status', '--porcelain', '--untracked-files=all')
receipt_path = EVIDENCE/'tuppence-source-A-authentic-release.json'
receipt = json.loads(receipt_path.read_text())
assert receipt['tag_object'] == TAG_OBJECT and receipt['peeled_commit'] == COMMIT
assert all(receipt[k] is True for k in ('git_signature', 'rekor_entry', 'certificate_claims'))
signature_log = (EVIDENCE/'tuppence-source-A-tag-verification.log').read_text()
assert 'tlog index: 3077499916' in signature_log
assert 'Good signature from [https://github.com/policy-as-versioned-tuppence/tuppence/.github/workflows/cut-release.yml@refs/heads/main](https://token.actions.githubusercontent.com)' in signature_log
assert all('Validated ' + item + ': true' in signature_log for item in ('Git signature', 'Rekor entry', 'Certificate claims'))

module_path = ESTATE/'platform-tools/wargamer/inventory.py'
spec = importlib.util.spec_from_file_location('released_inventory', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
inventory_bytes = (ADOPTER/'inventory/images.json').read_bytes()
inventory = json.loads(inventory_bytes)
provenance = json.loads((ADOPTER/'inventory/PROVENANCE.json').read_text())
assert sha(inventory_bytes) == provenance['inventory_sha256']
old_images = module.served_images(ADOPTER)
declaration = (ADOPTER/'gitops/flux-system/gotk-sync.yaml').read_text()
old = provenance['apps_source']
declaration = declaration.replace('tag: '+old['tag'], 'tag: '+TAG).replace('commit: '+old['commit'], 'commit: '+COMMIT)
with tempfile.TemporaryDirectory(prefix='tuppence-released-apps-') as tmp:
    declared = Path(tmp)
    target = declared/'gitops/flux-system/gotk-sync.yaml'
    target.parent.mkdir(parents=True)
    target.write_text(declaration)
    images = module.served_images(declared, repository=ADOPTER)
    module.validate(declared, inventory, repository=ADOPTER)
assert images == old_images
version_path = HUB/'.scratch/ecosystem/research/resume-2026-10-03/adopter-stage2-trivy-raw/version-before.json'
version = json.loads(version_path.read_text())
assert version == provenance['scanner']['version']
rows = []
for p in provenance['images']:
    raw = HUB/p['raw_report']
    assert sha(raw.read_bytes()) == p['raw_report_sha256']
    report = json.loads(raw.read_text())
    normalized = module.trim(p['requested_image'], report, version)
    original = next(row for row in inventory['images'] if row['image'] == p['requested_image'])
    assert normalized == original
    rows.append({'image': normalized['image'], 'raw_report': p['raw_report'],
                 'raw_report_sha256': sha(raw.read_bytes()), 'normalized_row_equal': True,
                 'vulnerability_rows': len(normalized['vulnerabilities'])})
result = {'scope': 'Existing primary scans replayed against authentic released apps; no fresh scan or activation asserted',
          'apps_tag': TAG, 'apps_tag_object': TAG_OBJECT, 'apps_commit': COMMIT,
          'tools_commit': TOOLS_COMMIT, 'inventory_module_sha256': sha(module_path.read_bytes()),
          'receipt_sha256': sha(receipt_path.read_bytes()),
          'signature_log_sha256': sha(signature_log.encode()), 'tlog_index': '3077499916',
          'served_images': images, 'old_and_released_graph_images_equal': True,
          'inventory_sha256': sha(inventory_bytes), 'inventory_bytes_unchanged': True,
          'validate_passed': True, 'primary_trim_rows': rows}
(EVIDENCE/'tuppence-atomic-delivery-released-inventory-check.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
print('PASS: released apps graph, exact digest inventory, genuine receipt, and primary scan replay')
