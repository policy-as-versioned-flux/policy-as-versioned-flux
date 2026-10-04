"""Prepare a coupled DW/LU delivery only after a genuine reviewed Source A release.

This script creates no tags, commits or remote writes. Run in a separate clean
checkout at the authentic release commit, with all actual signed parent objects.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--org', choices=('driftwood','ludlow'), required=True)
parser.add_argument('--adopter', type=Path, required=True)
parser.add_argument('--estate', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
repo, estate = args.adopter.resolve(), args.estate.resolve()
HUB = Path(__file__).resolve().parents[4]
receipt = json.loads(args.receipt.read_text())
assert receipt['institution'] == args.org
assert all(receipt[k] is True for k in ('git_signature','rekor_entry','certificate_claims','delivery_edits_may_begin'))
assert receipt['draft'] is False and receipt['prerelease'] is False
assert receipt['published_at'] and receipt['release_run'] and receipt['cut_run']
tag, commit, tag_object = receipt['tag'], receipt['peeled_commit'], receipt['tag_object']
assert re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', tag)
assert all(re.fullmatch(r'[0-9a-f]{40}', x) for x in (commit,tag_object))
def git(*argv):
    return subprocess.check_output(['git','-C',str(repo),*argv],text=True).strip()
assert git('rev-parse','HEAD') == commit
assert not git('status','--porcelain','--untracked-files=all')
assert git('rev-parse','refs/tags/'+tag) == tag_object
assert git('rev-parse','refs/tags/'+tag+'^{commit}') == commit
assert git('merge-base',commit,'origin/main') == commit
identity = f'https://github.com/policy-as-versioned-{args.org}/{args.org}/.github/workflows/cut-release.yml@refs/heads/main'
issuer = 'https://token.actions.githubusercontent.com'
signature_argv = ['gitsign','verify-tag',tag,'--certificate-identity='+identity,'--certificate-oidc-issuer='+issuer]
verified = subprocess.run(signature_argv,cwd=repo,text=True,capture_output=True,env=dict(os.environ,GITSIGN_REKOR_MODE='offline'))
siglog = verified.stdout+verified.stderr
args.out.mkdir(parents=True,exist_ok=True)
(args.out/(args.org+'-atomic-delivery-tag-verification.log')).write_text(siglog)
assert verified.returncode == 0, siglog
assert all('Validated '+claim+': true' in siglog for claim in ('Git signature','Rekor entry','Certificate claims'))
tlog = re.search(r'tlog index:\s*([0-9]+)',siglog)
assert tlog is not None, siglog
versions = sorted(name[1:] for name in git('ls-tree','--name-only',tag+':composed/policies').splitlines() if re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+',name))
assert versions == ['5.0.0','6.0.0','7.0.0'], versions
module_path = estate/'platform-tools/wargamer/inventory.py'
assert subprocess.check_output(['git','-C',str(estate/'platform-tools'),'rev-parse','HEAD'],text=True).strip() == '703eff6aee959843c4160aa54fd03413f62858cc'
spec = importlib.util.spec_from_file_location('released_inventory',module_path)
assert spec is not None and spec.loader is not None
inventory_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory_api)
sha = lambda data: hashlib.sha256(data).hexdigest()
inventory_bytes = (repo/'inventory/images.json').read_bytes()
inventory = json.loads(inventory_bytes)
provenance = json.loads((repo/'inventory/PROVENANCE.json').read_text())
before = copy.deepcopy(provenance)
assert sha(inventory_bytes) == provenance['inventory_sha256']
old = provenance['apps_source']
apps_path = repo/'gitops/flux-system/gotk-sync.yaml'
apps = apps_path.read_text()
assert apps.count('tag: '+old['tag']) == apps.count('commit: '+old['commit']) == 1
apps = apps.replace('tag: '+old['tag'],'tag: '+tag).replace('commit: '+old['commit'],'commit: '+commit)
apps = apps.replace('own signed '+old['tag']+' apps release','own signed '+tag+' apps release')
old_images = inventory_api.served_images(repo)
with tempfile.TemporaryDirectory(prefix=args.org+'-released-apps-') as temp:
    proposed = Path(temp)
    target = proposed/'gitops/flux-system/gotk-sync.yaml'
    target.parent.mkdir(parents=True)
    target.write_text(apps)
    images = inventory_api.served_images(proposed,repository=repo)
    inventory_api.validate(proposed,inventory,repository=repo)
assert images == old_images
version = json.loads((HUB/'.scratch/ecosystem/research/resume-2026-10-03/adopter-stage2-trivy-raw/version-before.json').read_text())
assert version == provenance['scanner']['version']
for image in provenance['images']:
    raw = HUB/image['raw_report']
    assert sha(raw.read_bytes()) == image['raw_report_sha256']
    normalized = inventory_api.trim(image['requested_image'],json.loads(raw.read_text()),version)
    assert normalized == next(row for row in inventory['images'] if row['image'] == image['requested_image'])
# Build every intended declaration before writing any of them.
source = provenance['apps_source']
source.update(tag=tag,commit=commit,tag_object=tag_object)
source['signature'].update(git=True,rekor=True,certificate_claims=True,identity=identity,issuer=issuer,
                           tlog_index=tlog.group(1),rekor_entry='https://rekor.sigstore.dev/api/v1/log/entries?logIndex='+tlog.group(1))
assert {k:v for k,v in before.items() if k!='apps_source'} == {k:v for k,v in provenance.items() if k!='apps_source'}
composed_path = repo/'gitops/composed/composed-set.yaml'
composed = composed_path.read_text()
import yaml
doc = next(d for d in yaml.safe_load_all(composed) if d and d.get('kind')=='GitRepository')
ref = doc['spec']['ref']
assert composed.count('tag: '+ref['tag']) == composed.count('commit: '+ref['commit']) == 1
composed = composed.replace('tag: '+ref['tag'],'tag: '+tag).replace('commit: '+ref['commit'],'commit: '+commit)
composed,count = re.subn(r'#   \* the tag is .*?(?=#   \* there is no)',
    '#   * apps and composed delivery use the same genuine '+tag+' Source A release.\n'
    '#     Its complete policy window and signature gates move with the inventory binding.\n',composed,flags=re.S)
assert count == 1
composed,count = re.subn(r'    # The resolved SHA.*?(?=\n---)',
    '    # The resolved SHA of the genuine signed '+tag+' Source A release.\n'
    '    # Belt-and-braces immutability, ADR-0001.',composed,flags=re.S)
assert count == 1
composed,count = re.subn(r'(policy-as-versioned.dev/gitsign-gates:) [^\n]+',
    r'\1 '+','.join('flux-system/composed-v'+v.replace('.','-') for v in versions)+',flux-system/composed-machinery',composed)
assert count == 1
composed,count = re.subn(r'        - \{ version: "5\.0\.0" \}.*?(?=  resourcesTemplate:)',
    ''.join('        - { version: "'+v+'" }\n' for v in versions)
    +'        # This array and all verification gates match the genuine signed target tree.\n'
    +'        # Current workload declarations claim 7.0.0; older supported claims remain caged.\n',composed,flags=re.S)
assert count == 1
apps_path.write_text(apps)
(repo/'inventory/PROVENANCE.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
composed_path.write_text(composed)
result = {'source_A_tag':tag,'source_A_tag_object':tag_object,'source_A_commit':commit,
          'signature_argv':signature_argv,'gitsign_exit':verified.returncode,'tlog_index':tlog.group(1),
          'inventory_sha256':sha(inventory_bytes),'inventory_bytes_unchanged':True,'primary_trim_equal':True,
          'served_images':images,'target_policy_versions':versions,'checks':{},'external_mutations':False}
for label,argv in [
    (action,[sys.executable,str(repo/'.github/scripts/platform-tools.py'),'--adopter-dir',str(repo),
             '--tools-dir',str(estate/'platform-tools'),action,str(repo),'--estate-clone',str(estate)])
    for action in ('compose','verify')]:
    done = subprocess.run(argv,cwd=repo,text=True,capture_output=True,timeout=240,env=dict(os.environ,GITSIGN_REKOR_MODE='offline'))
    log = args.out/(args.org+'-atomic-delivery-'+label+'.log')
    log.write_text(done.stdout+done.stderr)
    result['checks'][label] = {'argv':argv,'exit':done.returncode,'log':str(log)}
    (args.out/(args.org+'-atomic-delivery-local-preparation.json')).write_text(json.dumps(result,indent=2)+'\n')
    assert done.returncode == 0, (done.stdout+done.stderr)[-3500:]
assert (repo/'inventory/images.json').read_bytes() == inventory_bytes
reach = [sys.executable,str(repo/'scripts/render_composed.py'),'reach','--ref',tag]
checked = subprocess.run(reach,cwd=repo,text=True,capture_output=True,timeout=60)
log = args.out/(args.org+'-atomic-delivery-reach.log')
log.write_text(checked.stdout+checked.stderr)
result['checks']['reach'] = {'argv':reach,'exit':checked.returncode,'log':str(log)}
(args.out/(args.org+'-atomic-delivery-local-preparation.json')).write_text(json.dumps(result,indent=2)+'\n')
assert checked.returncode == 0, checked.stdout+checked.stderr
print(args.org,'real coupled declarations, primary inventory replay, authenticated compose/verify and target reach PASS')
