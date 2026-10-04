"""Prepare only the final composed pointer after authentic immutable B exists.

No remote action or tag creation. Apps, inventory and the complete policy
window remain unchanged; authenticated rerender/review must follow preparation.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import yaml

parser=argparse.ArgumentParser()
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--receipt',type=Path,required=True)
args=parser.parse_args()
repo=args.repo.resolve()
release=json.loads(args.receipt.read_text())
assert release['institution']=='driftwood' and release['tag']=='v4.0.1'
assert all(release[k] is True for k in ('git_signature','rekor_entry','certificate_claims','final_composed_pointer_edits_may_begin'))
assert release['draft'] is False and release['prerelease'] is False and release['published_at']
commit=release['peeled_commit']
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
assert git('rev-parse','HEAD')==git('rev-parse','origin/main')==commit
assert git('rev-parse','refs/tags/v4.0.1')==release['tag_object']
assert git('rev-parse','refs/tags/v4.0.1^{commit}')==commit
assert not git('status','--porcelain','--untracked-files=all')
path=repo/'gitops/composed/composed-set.yaml'
text=path.read_text()
doc=next(d for d in yaml.safe_load_all(text) if d and d.get('kind')=='GitRepository')
old=doc['spec']['ref']
apps=(repo/'gitops/flux-system/gotk-sync.yaml').read_bytes()
provenance=(repo/'inventory/PROVENANCE.json').read_bytes()
assert old['tag']=='v4.0.0'
assert text.count('tag: '+old['tag'])==text.count('commit: '+old['commit'])==1
text=text.replace('tag: '+old['tag'],'tag: v4.0.1').replace('commit: '+old['commit'],'commit: '+commit)
text,count=re.subn(r'#   \* apps and composed delivery.*?(?=#   \* there is no)',
 '#   * composed delivery uses genuine v4.0.1 Composition B, whose signed tree binds\n'
 '#     apps and native inventory to Source A v4.0.0. Its complete window is5.0.0,6.0.0,7.0.0.\n'
 '#     Apps and inventory remain A; this reviewed pointer moves only composed delivery to B.\n',text,flags=re.S)
assert count==1
text=text.replace('# The resolved SHA of the genuine signed v4.0.0 Source A release.',
                  '# The resolved SHA of the genuine signed v4.0.1 Composition B release.')
subprocess.run(['git','-C',str(repo),'switch','-c','delivery-stage2-composed-B-20261004',commit],check=True)
path.write_text(text)
assert (repo/'gitops/flux-system/gotk-sync.yaml').read_bytes()==apps
assert (repo/'inventory/PROVENANCE.json').read_bytes()==provenance
assert git('diff','--name-only').splitlines()==['gitops/composed/composed-set.yaml']
print('Genuine B composed-only pointer prepared; apps/inventory remain A. Rerender and exact reviews required.')
