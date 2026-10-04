"""Sign and measure the reviewed local atomic delivery; no remote writes or tags."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

DAY=Path(__file__).resolve().parent
loc=json.loads((DAY/'driftwood-atomic-delivery-checkout.json').read_text())
checks=json.loads((DAY/'driftwood-atomic-delivery-precommit-checks.json').read_text())
prepared=json.loads((DAY/'driftwood-atomic-delivery-local-preparation.json').read_text())
repo,estate=Path(loc['directory']),Path(loc['estate'])
base=loc['base']
assert all(c['exit']==0 for c in checks['checks'].values())
assert all(c['exit']==0 for c in prepared['checks'].values())
def git(*args):
 return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
if git('rev-parse','HEAD')==base:
 subprocess.run(['git','-C',str(repo),'diff','--check'],check=True)
 subprocess.run(['git','-C',str(repo),'add','--all'],check=True)
 message=('Deliver the genuine claim7 apps and complete composed window together\n\n'
          'Bind apps, retained primary inventory provenance and composed delivery to the authentic '
          'v4.0.0 release. Move the version array and signature gates to its complete5/6/7 tree; '
          'rerender the signed-source comparison identity with authenticated tools5. '
          'Keep all image and policy bytes, financial instruments, engine declaration and cloud gate as measured.\n\n'
          'Prepared-by: Codex agent; no human was present during preparation.')
 subprocess.run(['git','-C',str(repo),'commit','-m',message],check=True)
else:
 existing=json.loads((DAY/'driftwood-atomic-delivery-candidate.json').read_text())
 assert git('rev-parse','HEAD')==existing['head']
head,tree=git('rev-parse','HEAD'),git('rev-parse','HEAD^{tree}')
assert git('log','-1','--format=%G?')=='G'
sig=subprocess.run(['git','-C',str(repo),'verify-commit',head],text=True,capture_output=True)
assert sig.returncode==0,sig.stderr
siglog=DAY/'driftwood-atomic-delivery-source-signature.log'
siglog.write_text(sig.stdout+sig.stderr)
assert not git('status','--porcelain','--untracked-files=all')
patch=DAY/'driftwood-atomic-delivery.patch'
patch.write_bytes(subprocess.check_output(['git','-C',str(repo),'diff','--binary','--full-index',base,head]))
subprocess.run(['git','-C',str(repo),'apply','--reverse','--check',str(patch)],check=True,capture_output=True)
paths=git('diff','--name-only',base,head).splitlines()
assert set(paths)==set(checks['changed_paths'])
assert git('rev-parse',base+':composed/policies')==git('rev-parse','HEAD:composed/policies')
result={'directory':str(repo),'estate':str(estate),'base':base,'head':head,'tree':tree,
        'branch':git('branch','--show-current'),'normal_SSH_signature':'G','signature_log':str(siglog),
        'source_clean':True,'remote_mutations':False,'future_composition_B_tag_created':False,
        'apps_A_tag':prepared['source_A_tag'],'apps_A_commit':base,'apps_A_tag_object':prepared['source_A_tag_object'],
        'apps_tag_tlog_index':prepared['tlog_index'],'policy_versions':['5.0.0','6.0.0','7.0.0'],
        'policy_trees_unchanged_from_source_A':True,'changed_paths':paths,
        'file_sha256':{p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in paths},
        'patch':str(patch),'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),
        'inventory_sha256':prepared['inventory_sha256'],'primary_inventory_preserved':True,
        'engine_and_cloud_declarations_preserved':True,'source_A_branch_preserved':True,
        'checks':{},'publication_hold':'Independent exact-head review and root-coordinated normal PR/CI/merge; no live activation claim.'}
candidate=DAY/'driftwood-atomic-delivery-candidate.json'
def save(): candidate.write_text(json.dumps(result,indent=2)+'\n')
save()
env=dict(os.environ,PAVF_REAL_ESTATE=str(estate),PYTHONPATH=str(repo/'tests'),GITSIGN_REKOR_MODE='offline')
out=DAY/'driftwood-atomic-delivery-gate.json'
markdown=DAY/'driftwood-atomic-delivery-gate.md'
commands={
 'gate':[sys.executable,str(repo/'.github/scripts/adopter-gate.py'),'compose',str(estate/'platform'),
         'v4.0.0','UNRELEASED-ATOMIC-DELIVERY','--adopter-dir',str(repo),'--base-ref',base,'--head-ref',head,
         '--out',str(out),'--markdown-out',str(markdown)],
 'postcommit_real_layout':[sys.executable,'-m','unittest','test_platform_tools.WorkflowHistory','test_platform_tools.RealCompilerLayout']}
for name,argv in commands.items():
 p=subprocess.run(argv,cwd=repo,env=env,text=True,capture_output=True,timeout=300)
 log=DAY/f'driftwood-atomic-delivery-{name}.log'
 log.write_text(p.stdout+p.stderr)
 result['checks'][name]={'argv':argv,'exit':p.returncode,'log':str(log),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
 save()
 assert p.returncode==0,p.stdout+p.stderr
 if name=='gate':
  grade=json.loads(out.read_text())['result']
  assert grade['composed_bump']==grade['declared_bump']=='none' and grade['added']==grade['retired']==[],grade
  if 'acceptance' in grade: assert grade['acceptance']['admitted'] is True,grade
  result['checks'][name]['result']=grade
  result['measured_bump']='none'
  save()
 else: assert 'skipped' not in p.stderr
 print(name,'PASS',flush=True)
assert git('rev-parse','HEAD')==head and not git('status','--porcelain','--untracked-files=all')
result['source_still_clean']=True
save()
print(json.dumps({k:result[k] for k in ('head','tree','base','changed_paths','measured_bump','patch_sha256')},indent=2),flush=True)
