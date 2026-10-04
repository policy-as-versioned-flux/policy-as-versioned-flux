"""Independent read-only Standards checks of the exact final composed B pointer."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

DAY=Path(__file__).resolve().parent
packet=DAY/'tuppence-final-composed-B-candidate.json'
c=json.loads(packet.read_text())
repo=Path(c['directory'])
assert c['head']=='b2abe26c155beea87366bcdf9775faae991f0803'
assert c['tree']=='5dcedc2fbc951c25251ee56b9c13bcf844ab044e'
git=lambda *args:subprocess.check_output(['git','-C',str(repo),*args])
assert git('rev-parse','HEAD').decode().strip()==c['head']
assert git('rev-parse','HEAD^{tree}').decode().strip()==c['tree']
assert not git('status','--porcelain','--untracked-files=all').strip()
signature=subprocess.run(['git','-C',str(repo),'verify-commit',c['head']],text=True,capture_output=True)
assert signature.returncode==0,signature.stderr
assert git('log','-1','--format=%G?').decode().strip()=='G'
(DAY/'tuppence-final-composed-B-independent-source-signature.log').write_text(signature.stdout+signature.stderr)
paths=git('diff','--name-only',c['base'],c['head']).decode().splitlines()
assert paths==['composed/HEADER.yaml','gitops/composed/composed-set.yaml']==c['changed_paths']
subprocess.run(['git','-C',str(repo),'diff','--check',c['base'],c['head']],check=True)
def tree(ref):
 rows={}
 for line in git('ls-tree','-rz',ref).split(b'\0'):
  if not line:continue
  meta,path=line.split(b'\t',1)
  rows[path.decode()]=meta.decode()
 return rows
old,new=tree(c['base']),tree(c['head'])
assert old.keys()==new.keys()
unchanged=[p for p in old if p not in paths]
assert all(old[p]==new[p] for p in unchanged)
old_header=yaml.safe_load(git('show',c['base']+':composed/HEADER.yaml'))
new_header=yaml.safe_load((repo/'composed/HEADER.yaml').read_text())
old_fingerprint=old_header['comparison-inputs'].pop('after')
new_fingerprint=new_header['comparison-inputs'].pop('after')
assert old_header==new_header and old_fingerprint!=new_fingerprint
apps=next(d for d in yaml.safe_load_all((repo/'gitops/flux-system/gotk-sync.yaml').read_text()) if d and d.get('kind')=='GitRepository')
provenance=json.loads((repo/'inventory/PROVENANCE.json').read_text())
assert apps['spec']['ref']=={'tag':'v4.0.0','commit':c['apps_A_commit']}
assert provenance['apps_source']['tag']=='v4.0.0' and provenance['apps_source']['commit']==c['apps_A_commit']
composed=list(yaml.safe_load_all((repo/'gitops/composed/composed-set.yaml').read_text()))
source=next(d for d in composed if d and d.get('kind')=='GitRepository')
resource=next(d for d in composed if d and d.get('kind')=='ResourceSet')
assert source['spec']['ref']=={'tag':'v4.0.1','commit':c['composed_B_commit']}
assert resource['spec']['inputs'][0]['versions']==[{'version':v} for v in ('5.0.0','6.0.0','7.0.0')]
assert source['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates']=='flux-system/composed-v5-0-0,flux-system/composed-v6-0-0,flux-system/composed-v7-0-0,flux-system/composed-machinery'
assert 'verify' not in source['spec']
release=json.loads((DAY/'tuppence-composition-B-authentic-release.json').read_text())
assert release['tag']==c['composed_B_tag'] and release['tag_object']==c['composed_B_tag_object']
assert release['peeled_commit']==c['composed_B_commit']==c['base']
assert release['draft'] is False and release['prerelease'] is False and release['published_at']
assert all(release[k] is True for k in ('git_signature','rekor_entry','certificate_claims','final_composed_pointer_edits_may_begin'))
assert git('rev-parse','refs/tags/v4.0.1').decode().strip()==release['tag_object']
assert git('rev-parse','refs/tags/v4.0.1^{commit}').decode().strip()==release['peeled_commit']
assert git('cat-file','tag','v4.0.1')==(DAY/'tuppence-composition-B-tag-object.txt').read_bytes()
log=(DAY/'tuppence-composition-B-tag-verification.log').read_text()
assert 'tlog index: '+release['tlog_index'] in log
assert 'Good signature from [https://github.com/policy-as-versioned-tuppence/tuppence/.github/workflows/cut-release.yml@refs/heads/main](https://token.actions.githubusercontent.com)' in log
assert all('Validated '+claim+': true' in log for claim in ('Git signature','Rekor entry','Certificate claims'))
assert git('rev-parse','v4.0.1:composed/policies')==git('rev-parse','HEAD:composed/policies')
tag_apps=next(d for d in yaml.safe_load_all(git('show','v4.0.1:gitops/flux-system/gotk-sync.yaml')) if d and d.get('kind')=='GitRepository')
assert tag_apps['spec']['ref']==apps['spec']['ref']
assert json.loads(git('show','v4.0.1:inventory/PROVENANCE.json'))==provenance
for name,row in c['checks'].items():
 assert row['exit']==0,(name,row)
 assert hashlib.sha256(Path(row['log']).read_bytes()).hexdigest()==row['log_sha256'],name
layout=Path(c['checks']['postcommit-real-layout']['log']).read_text()
assert 'RealCompilerLayout.test_composition_bytes_do_not_depend_on_checkout_prefix) ... ok' in layout
assert 'Ran 4 tests' in layout and '\nOK\n' in layout and 'skipped' not in layout
assert c['checks']['reach']['argv'][-1]=='v4.0.1'
gate=c['checks']['gate']
assert c['head'] in gate['argv'] and c['base'] in gate['argv']
assert gate['result']['declared']==gate['result']['composed']=='none'
assert gate['result']['added']==gate['result']['retired']==[]
for path,expected in c['file_sha256'].items():
 assert hashlib.sha256((repo/path).read_bytes()).hexdigest()==expected,path
assert git('rev-parse','HEAD').decode().strip()==c['head']
assert not git('status','--porcelain','--untracked-files=all').strip()
result={'result':'PASS','scope':'Independent read-only Standards review of the actual final B-pointer committed bytes and exact-head proof; no live adoption assertion',
        'head':c['head'],'tree':c['tree'],'base':c['base'],'changed_paths':paths,
        'packet_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),
        'normal_SSH_signature':'G','source_clean':True,'all_other_tracked_entries_unchanged':len(unchanged),
        'HEADER_only_delta':'comparison-inputs.after','prior_fingerprint':old_fingerprint,'new_fingerprint':new_fingerprint,
        'authentic_B_tag_object':release['tag_object'],'authentic_B_commit':release['peeled_commit'],
        'root_normal_crypto_measurement_joined_to_exact_local_tag':True,'tlog_index':release['tlog_index'],
        'apps_and_native_inventory_remain_A':True,'B_signed_tree_and_final_policy_tree_equal':True,
        'engine_and_cloud_declarations_unchanged':True,'array_and_all_signature_gates':'5/6/7 +machinery',
        'recorded_authentic_compose_verify_reach':'PASS','exact_postcommit_real_layout':'4PASS, no skips',
        'institutional_gate':'none/none, no added or retired versions','hard_findings':[],
        'source_edits':False,'external_actions':False,'active_sessions':[]}
(DAY/'tuppence-final-composed-B-independent-standards-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
