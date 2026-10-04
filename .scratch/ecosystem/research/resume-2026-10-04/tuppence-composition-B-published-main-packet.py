"""Bind fresh normal postmerge Composition B to the exact published main."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import yaml

HUB = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
E = HUB/'.scratch/ecosystem/research/resume-2026-10-04'
ESTATE = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/tuppence-estate')
A = ESTATE/'tuppence'
HEAD = 'dbaa026f6510fe5c0042f33f29081f3840ea59c3'
TREE = 'f8ad854469bfe76f591c72746d76334e7d1fa290'
SOURCE_A = 'f575dc12de130c444d98a831de0ca21fd68b9c46'
TOOLS = '703eff6aee959843c4160aa54fd03413f62858cc'

def git(*args):
    return subprocess.check_output(['git','-C',str(A),*args])

def sha(data):
    return hashlib.sha256(data).hexdigest()

assert git('rev-parse','HEAD').decode().strip() == HEAD
assert git('rev-parse','origin/main').decode().strip() == HEAD
assert git('rev-parse','HEAD^{tree}').decode().strip() == TREE
assert git('branch','--show-current').decode().strip() == 'delivery-stage2-composition-B-20261004'
assert not git('status','--porcelain','--untracked-files=all').strip()
assert not git('diff','HEAD').strip()
main_receipt = E/'tuppence-composition-B-main-commit-verification.json'
main = json.loads(main_receipt.read_text())
assert main['sha'] == HEAD and main['verification']['verified'] is True
assert main['verification']['reason'] == 'valid'
assert main['verification']['payload'].startswith('tree '+TREE+'\n')
assert main['parents'] == [SOURCE_A, '0dd1cf6987f04484a00141b2a962a3e69af200f8']
for tag, expected in [('delivery-stage2-20261004','d1dbe766e09bb8112efa609836af0aa95cbe0ee4'),
                      ('delivery-stage2-atomic-20261004','0dd1cf6987f04484a00141b2a962a3e69af200f8')]:
    assert git('rev-parse',tag).decode().strip() == expected
assert git('rev-parse','refs/tags/v4.0.0').decode().strip() == '17070ad568397bb7c394f80cb0d51ebcf560089e'
assert git('rev-parse','refs/tags/v4.0.0^{commit}').decode().strip() == SOURCE_A
assert subprocess.check_output(['git','-C',str(ESTATE/'platform-tools'),'rev-parse','HEAD'],text=True).strip() == TOOLS
spec = importlib.util.spec_from_file_location('released_inventory',ESTATE/'platform-tools/wargamer/inventory.py')
inventory_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory_module)
inventory = json.loads((A/'inventory/images.json').read_text())
provenance = json.loads((A/'inventory/PROVENANCE.json').read_text())
images = inventory_module.served_images(A)
inventory_module.validate(A,inventory)
version = json.loads((HUB/'.scratch/ecosystem/research/resume-2026-10-03/adopter-stage2-trivy-raw/version-before.json').read_text())
for row in provenance['images']:
    raw = HUB/row['raw_report']
    assert sha(raw.read_bytes()) == row['raw_report_sha256']
    trimmed = inventory_module.trim(row['requested_image'],json.loads(raw.read_text()),version)
    assert trimmed == next(r for r in inventory['images'] if r['image']==row['requested_image'])
assert provenance['apps_source']['tag'] == 'v4.0.0'
assert provenance['apps_source']['commit'] == SOURCE_A
assert provenance['apps_source']['tag_object'] == '17070ad568397bb7c394f80cb0d51ebcf560089e'
compose_log = E/'tuppence-composition-B-published-main-compose.log'
verify_log = E/'tuppence-composition-B-published-main-verify.log'
document = json.loads(compose_log.read_text())
assert document['outcome']=='composed' and document['refusals']==[]
assert 'OK: composed artefact re-renders byte-for-byte' in verify_log.read_text()
assert (A/'composed/evidence.json').read_bytes() == git('show',HEAD+':composed/evidence.json')
pin = E/'tuppence-composition-B-published-main-old-platform-pin.yaml'
pin.write_bytes(git('show',SOURCE_A+':gitops/platform/platform-pin.yaml'))
gate_out = E/'tuppence-composition-B-published-main-gate.json'
identity = r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'
gate_argv = [sys.executable,str(A/'.github/scripts/adopter-gate.py'),'--platform-dir',str(ESTATE/'platform'),
             '--new-pin-yaml',str(A/'gitops/platform/platform-pin.yaml'),'--old-pin-yaml',str(pin),
             '--identity-regexp',identity,'--issuer','https://token.actions.githubusercontent.com',
             '--adopter-dir',str(A),'--base-ref',SOURCE_A,'--head-ref',HEAD,'--out',str(gate_out)]
gate = subprocess.run(gate_argv,cwd=A,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
(E/'tuppence-composition-B-published-main-gate.log').write_text(gate.stdout+gate.stderr)
assert gate.returncode==0,gate.stdout+gate.stderr
grade=json.loads(gate_out.read_text())
assert grade['declared']==grade['composed']=='none' and grade['added']==grade['retired']==[]
reach_argv=[sys.executable,str(A/'scripts/render_composed.py'),'reach','--ref','v4.0.0']
reach=subprocess.run(reach_argv,cwd=A,capture_output=True,text=True)
(E/'tuppence-composition-B-published-main-reach.log').write_text(reach.stdout+reach.stderr)
assert reach.returncode==0,reach.stdout+reach.stderr
header=yaml.safe_load((A/'composed/HEADER.yaml').read_text())
composed_files=git('ls-tree','-r','--name-only',HEAD,'--','composed').decode().splitlines()
hashes={p:sha((A/p).read_bytes()) for p in composed_files}
for p in composed_files:
    assert (A/p).read_bytes()==git('show',HEAD+':'+p),p
assert not git('status','--porcelain','--untracked-files=all').strip()
result={'scope':'Fresh Composition B on actual published main; no cut, tag or workflow retry',
        'head':HEAD,'tree':TREE,'origin_main':HEAD,'branch':'delivery-stage2-composition-B-20261004',
        'GitHub_merge_signature_verified':True,'main_commit_receipt_sha256':sha(main_receipt.read_bytes()),
        'source_A_tag':'v4.0.0','source_A_commit':SOURCE_A,'tools_tag':'v5.0.0','tools_commit':TOOLS,
        'fresh_normal_compose':{'exit':0,'log':str(compose_log),'sha256':sha(compose_log.read_bytes()),
            'argv':[sys.executable,'.github/scripts/platform-tools.py','--adopter-dir','.','--tools-dir','../platform-tools','compose','.','--estate-clone','..']},
        'fresh_normal_verify':{'exit':0,'log':str(verify_log),'sha256':sha(verify_log.read_bytes()),
            'argv':[sys.executable,'.github/scripts/platform-tools.py','--adopter-dir','.','--tools-dir','../platform-tools','verify','.','--estate-clone','..']},
        'source_output_diff':[],'source_clean_after_fresh_rerender':True,'rendered_files_sha256':hashes,
        'recorded_comparison_after':header['comparison-inputs']['after'],
        'inventory_graph_and_primary_trim_passed':True,'served_images':images,'inventory_sha256':sha((A/'inventory/images.json').read_bytes()),
        'institutional_gate':{'argv':gate_argv,'exit':0,'result':grade},
        'genuine_source_A_reach':{'argv':reach_argv,'exit':0,'stdout':reach.stdout},
        'original_source_A_and_atomic_branches_preserved':True,'future_source_B_tag_created':False,
        'remote_mutations':False,'live_observation_or_activation_claimed':False}
(E/'tuppence-composition-B-published-main-candidate.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('PASS: exact published dbaa Composition B normal fresh render/verify, empty source diff, apps graph/primary scan and gate none')
