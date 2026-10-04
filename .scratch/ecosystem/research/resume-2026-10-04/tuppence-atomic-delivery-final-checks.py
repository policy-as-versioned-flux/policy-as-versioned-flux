"""Bind normal postcommit checks to the exact local atomic delivery candidate."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

HUB = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
EVIDENCE = HUB/'.scratch/ecosystem/research/resume-2026-10-04'
ESTATE = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/tuppence-estate')
ADOPTER = ESTATE/'tuppence'
BASE = 'f575dc12de130c444d98a831de0ca21fd68b9c46'
HEAD = '0dd1cf6987f04484a00141b2a962a3e69af200f8'
TREE = 'f8ad854469bfe76f591c72746d76334e7d1fa290'

def git(*args):
    return subprocess.check_output(['git','-C',str(ADOPTER),*args])

assert git('rev-parse','HEAD').decode().strip() == HEAD
assert git('rev-parse','HEAD^{tree}').decode().strip() == TREE
assert not git('status','--porcelain','--untracked-files=all').strip()
assert git('log','-1','--format=%G?').decode().strip() == 'G'
signature = subprocess.run(['git','-C',str(ADOPTER),'verify-commit',HEAD],capture_output=True,text=True,check=True)
(EVIDENCE/'tuppence-atomic-delivery-source-signature.log').write_text(signature.stdout+signature.stderr)
(EVIDENCE/'tuppence-atomic-delivery.patch').write_bytes(git('diff','--binary',BASE,HEAD))
pin = EVIDENCE/'tuppence-atomic-delivery-old-platform-pin.yaml'
pin.write_bytes(git('show',BASE+':gitops/platform/platform-pin.yaml'))
identity = r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'
out = EVIDENCE/'tuppence-atomic-delivery-gate.json'
gate_argv = [sys.executable,str(ADOPTER/'.github/scripts/adopter-gate.py'),
             '--platform-dir',str(ESTATE/'platform'), '--new-pin-yaml',str(ADOPTER/'gitops/platform/platform-pin.yaml'),
             '--old-pin-yaml',str(pin),'--identity-regexp',identity,'--issuer','https://token.actions.githubusercontent.com',
             '--adopter-dir',str(ADOPTER),'--base-ref',BASE,'--head-ref',HEAD,'--out',str(out)]
result = {'head':HEAD,'tree':TREE,'base':BASE,'branch':'delivery-stage2-atomic-20261004','normal_SSH_signature':'G',
          'source_clean':True,'remote_mutations':False,'future_source_B_tag_created':False,'checks':{}}
result_path = EVIDENCE/'tuppence-atomic-delivery-final-checks.json'
def save():
    result_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
save()
environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PAVF_REAL_ESTATE=str(ESTATE))
for name, argv in [('gate',gate_argv),('postcommit_real_layout',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_platform_tools.py','-v'])]:
    run = subprocess.run(argv,cwd=ADOPTER,env=environment,capture_output=True,text=True)
    log = EVIDENCE/('tuppence-atomic-delivery-'+name+'.log')
    log.write_text(run.stdout+run.stderr)
    result['checks'][name] = {'argv':argv,'exit':run.returncode,'log':str(log),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
    save()
    if run.returncode:
        print(run.stdout+run.stderr)
        raise SystemExit(run.returncode)
    if name=='gate':
        grade=json.loads(out.read_text())
        assert grade['declared']==grade['composed']=='none' and grade['added']==grade['retired']==[]
        result['checks'][name]['result']=grade
        save()
    print('PASS:',name,flush=True)
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert not git('status','--porcelain','--untracked-files=all').strip()
result['source_still_clean']=True
save()
