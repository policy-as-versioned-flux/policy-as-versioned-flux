"""Finite coupled-source and preservation checks; never changes source."""
from pathlib import Path
import hashlib
import json
import subprocess
import yaml

ADOPTER = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/tuppence-estate/tuppence')
EVIDENCE = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
BASE = 'f575dc12de130c444d98a831de0ca21fd68b9c46'
TAG_OBJECT = '17070ad568397bb7c394f80cb0d51ebcf560089e'
PATHS = ['composed/HEADER.yaml', 'gitops/composed/composed-set.yaml', 'gitops/flux-system/gotk-sync.yaml', 'inventory/PROVENANCE.json']

def git(*args):
    return subprocess.check_output(['git','-C',str(ADOPTER),*args])

def old(path):
    return git('show',BASE+':'+path)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def docs(path):
    return list(yaml.safe_load_all((ADOPTER/path).read_text()))

changed = git('diff',BASE,'--name-only').decode().splitlines()
assert sorted(changed) == sorted(PATHS), changed
apps = next(d for d in docs('gitops/flux-system/gotk-sync.yaml') if d['kind']=='GitRepository')
composed_docs = docs('gitops/composed/composed-set.yaml')
composed = next(d for d in composed_docs if d['kind']=='GitRepository')
assert apps['spec']['ref'] == composed['spec']['ref'] == {'tag':'v4.0.0','commit':BASE}
assert git('rev-parse','refs/tags/v4.0.0').decode().strip() == TAG_OBJECT
assert git('rev-parse','refs/tags/v4.0.0^{commit}').decode().strip() == BASE
assert 'verify' not in composed['spec']
array = next(d for d in composed_docs if d['kind']=='ResourceSet')['spec']['inputs'][0]['versions']
assert array == [{'version':'5.0.0'},{'version':'6.0.0'},{'version':'7.0.0'}]
expected_gates = ['flux-system/composed-v5-0-0','flux-system/composed-v6-0-0','flux-system/composed-v7-0-0','flux-system/composed-machinery']
assert composed['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates'].split(',') == expected_gates
provenance = json.loads((ADOPTER/'inventory/PROVENANCE.json').read_text())
previous = json.loads(old('inventory/PROVENANCE.json'))
assert {k:v for k,v in provenance.items() if k!='apps_source'} == {k:v for k,v in previous.items() if k!='apps_source'}
assert provenance['apps_source']['tag'] == 'v4.0.0' and provenance['apps_source']['commit'] == BASE
assert provenance['apps_source']['tag_object'] == TAG_OBJECT
assert provenance['apps_source']['signature']['tlog_index'] == '3077499916'
assert sha((ADOPTER/'inventory/images.json').read_bytes()) == provenance['inventory_sha256']
unchanged = {}
for path in ['inventory/images.json','party.yaml','gitops/engine/kyverno.yaml','gitops/cloud/cloud-delivery.yaml','gitops/cloud/claims.yaml','gitops/apps/kustomization.yaml','composed/evidence.json']:
    current = (ADOPTER/path).read_bytes()
    assert current == old(path), path
    unchanged[path] = sha(current)
policy_files = git('ls-tree','-r','--name-only',BASE,'--','composed/policies').decode().splitlines()
for path in policy_files:
    assert (ADOPTER/path).read_bytes() == old(path), path
machinery = [p for p in git('ls-tree','-r','--name-only',BASE,'--','composed').decode().splitlines()
             if not p.startswith('composed/policies/') and p!='composed/HEADER.yaml']
for path in machinery:
    assert (ADOPTER/path).read_bytes() == old(path), path
assert git('rev-parse','delivery-stage2-20261004').decode().strip() == 'd1dbe766e09bb8112efa609836af0aa95cbe0ee4'
assert yaml.safe_load((ADOPTER/'party.yaml').read_text())['appetite']['pricing_threshold'] == 3
assert not any('composed' in str(r) or 'cloud' in str(r) for r in yaml.safe_load((ADOPTER/'gitops/apps/kustomization.yaml').read_text())['resources'])
result = {'base':BASE, 'head':git('rev-parse','HEAD').decode().strip(), 'changed_paths':changed,
          'coupled_apps_composed_pins':apps['spec']['ref'], 'tag_object':TAG_OBJECT,
          'version_array':[x['version'] for x in array], 'gitsign_gates':expected_gates,
          'inventory_primary_metadata_unchanged':True,'policy_bytes_unchanged':len(policy_files),
          'other_composed_bytes_unchanged':len(machinery), 'preserved_files_sha256':unchanged,
          'pricing_threshold':3, 'original_signed_source_A_branch_preserved':True,
          'composed_and_cloud_remain_opt_in':True,'remote_mutations':False}
(EVIDENCE/'tuppence-atomic-delivery-sanity.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('PASS: coupled delivery refs, full array/gates, unchanged inventory/engine/cloud/pricing/policy bytes')
