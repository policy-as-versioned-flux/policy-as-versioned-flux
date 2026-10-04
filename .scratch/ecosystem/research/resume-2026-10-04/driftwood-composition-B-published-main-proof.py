"""Local-only fresh B proof, requiring an actual authenticated published-main receipt.

Run after the ordinary atomic PR merge and a normal fetch. It creates no tags,
commits or remote actions. Cut/release is held for fresh exact-head reviews.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

p=argparse.ArgumentParser()
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--estate',type=Path,required=True)
p.add_argument('--main-receipt',type=Path,required=True)
args=p.parse_args()
DAY=Path(__file__).resolve().parent
repo,estate=args.repo.resolve(),args.estate.resolve()
atomic=json.loads((DAY/'driftwood-atomic-delivery-candidate.json').read_text())
receipt=json.loads(args.main_receipt.read_text())
head=receipt['sha']
assert receipt['commit']['verification']['verified'] is True
assert len(head)==40
get=lambda *argv:subprocess.check_output(['git','-C',str(repo),*argv],text=True).strip()
assert get('rev-parse','HEAD')==get('rev-parse','origin/main')==head
assert not get('status','--porcelain','--untracked-files=all')
assert get('merge-base',atomic['head'],head)==atomic['head']
assert get('rev-parse','HEAD^{tree}')==atomic['tree']
result={'scope':'Fresh composition B proof on actual published main; no tag/cut or remote mutation',
        'head':head,'tree':get('rev-parse','HEAD^{tree}'),'directory':str(repo),'estate':str(estate),
        'reviewed_atomic_source':atomic['head'],'GitHub_merge_signature_verified':True,
        'main_receipt_sha256':hashlib.sha256(args.main_receipt.read_bytes()).hexdigest(),
        'source_A_tag':atomic['apps_A_tag'],'source_A_commit':atomic['apps_A_commit'],
        'prospective_composition_release':'v4.0.1','cut_hold':'Fresh root Standards and Spec reviews of this exact published main required',
        'remote_mutations':False,'future_composition_B_tag_created':False,'checks':{}}
output=DAY/'driftwood-composition-B-published-main-candidate.json'
def save():output.write_text(json.dumps(result,indent=2)+'\n')
save()
env=dict(os.environ,GITSIGN_REKOR_MODE='offline')
for action in ('compose','verify'):
 argv=[sys.executable,str(repo/'.github/scripts/platform-tools.py'),'--adopter-dir',str(repo),
       '--tools-dir',str(estate/'platform-tools'),action,str(repo),'--estate-clone',str(estate)]
 done=subprocess.run(argv,cwd=repo,env=env,text=True,capture_output=True,timeout=240)
 log=DAY/f'driftwood-composition-B-published-main-{action}.log'
 log.write_text(done.stdout+done.stderr)
 result['checks'][action]={'argv':argv,'exit':done.returncode,'log':str(log),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
 save()
 assert done.returncode==0,(done.stdout+done.stderr)[-3500:]
 assert not get('status','--porcelain','--untracked-files=all')
 print('fresh normal',action,'PASS, no source/output diff',flush=True)
result['source_clean_after_fresh_rerender']=True
result['rendered_files_sha256']={str(path.relative_to(repo)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (repo/'composed').rglob('*') if path.is_file()}
reach=[sys.executable,str(repo/'scripts/render_composed.py'),'reach','--ref',atomic['apps_A_tag']]
gate_out=DAY/'driftwood-composition-B-published-main-gate.json'
gate_md=DAY/'driftwood-composition-B-published-main-gate.md'
gate=[sys.executable,str(repo/'.github/scripts/adopter-gate.py'),'compose',str(estate/'platform'),
      atomic['apps_A_tag'],'UNRELEASED-COMPOSITION-B','--adopter-dir',str(repo),
      '--base-ref',atomic['apps_A_commit'],'--head-ref',head,'--out',str(gate_out),'--markdown-out',str(gate_md)]
for label,argv in (('reach',reach),('gate',gate)):
 done=subprocess.run(argv,cwd=repo,env=env,text=True,capture_output=True,timeout=240)
 log=DAY/f'driftwood-composition-B-published-main-{label}.log'
 log.write_text(done.stdout+done.stderr)
 result['checks'][label]={'argv':argv,'exit':done.returncode,'log':str(log),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
 save()
 assert done.returncode==0,done.stdout+done.stderr
 if label=='gate':
  grade=json.loads(gate_out.read_text())['result']
  assert grade['declared_bump']==grade['composed_bump']=='none' and grade['added']==grade['retired']==[],grade
  result['checks'][label]['result']=grade
 save()
assert get('rev-parse','HEAD')==head and not get('status','--porcelain','--untracked-files=all')
result['local_proof_complete']=True
save()
print('Fresh actual-main B packet ready for exact reviews; no release action performed',flush=True)
