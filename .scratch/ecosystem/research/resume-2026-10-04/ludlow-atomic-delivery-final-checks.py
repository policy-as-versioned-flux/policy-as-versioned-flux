"""Normal exact-commit gate and enabled public tests for LU atomic delivery."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

HUB = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
E = HUB/'.scratch/ecosystem/research/resume-2026-10-04'
ESTATE = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/ludlow-estate')
A = ESTATE/'ludlow'
BASE = 'c5f33cc8982fc9bfeb7fcc2068ea8de0dda63dae'
HEAD = '6de0d00ce850ea820777f46fbea5c93a3238ea68'
TREE = 'deff0089ff3c28f68d7fb0d097c926d7de4f6b63'

def git(*args):
    return subprocess.check_output(['git','-C',str(A),*args])

assert git('rev-parse','HEAD').decode().strip()==HEAD
assert git('rev-parse','HEAD^{tree}').decode().strip()==TREE
assert not git('status','--porcelain','--untracked-files=all').strip()
assert git('log','-1','--format=%G?').decode().strip()=='G'
signature=subprocess.run(['git','-C',str(A),'verify-commit',HEAD],capture_output=True,text=True,check=True)
(E/'ludlow-atomic-delivery-source-signature.log').write_text(signature.stdout+signature.stderr)
(E/'ludlow-atomic-delivery.patch').write_bytes(git('diff','--binary',BASE,HEAD))
identity=r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'
gate_argv=[sys.executable,str(A/'.github/scripts/adopter_gate.py'),
           '--platform-dir',str(ESTATE/'platform'),'--ludlow-dir',str(A),
           '--old-ref',BASE,'--new-ref',HEAD,'--composed-base-ref',BASE,'--composed-head-ref',HEAD,
           '--identity-regexp',identity,'--issuer','https://token.actions.githubusercontent.com',
           '--out-comment',str(E/'ludlow-atomic-delivery-gate.md')]
result={'head':HEAD,'tree':TREE,'base':BASE,'branch':'delivery-stage2-atomic-20261004',
        'normal_SSH_signature':'G','source_clean':True,'checks':{},'remote_mutations':False,
        'future_source_B_tag_created':False}
path=E/'ludlow-atomic-delivery-final-checks.json'
if path.exists():
    previous=json.loads(path.read_text())
    assert previous['head']==HEAD and previous['tree']==TREE
    result['checks']=previous['checks']
def save():
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
save()
environment=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PAVF_REAL_ESTATE=str(ESTATE))
tests=[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v']
for name,argv in [('gate',gate_argv),('postcommit_real_estate_public_tests',tests)]:
    log=E/('ludlow-atomic-delivery-'+name+'.log')
    saved=result['checks'].get(name)
    if saved and saved['exit']==0:
        assert saved['argv']==argv
        assert saved['log_sha256']==hashlib.sha256(log.read_bytes()).hexdigest()
        output=log.read_text()
    else:
        run=subprocess.run(argv,cwd=A,env=environment,capture_output=True,text=True)
        output=run.stdout+run.stderr
        log.write_text(output)
        result['checks'][name]={'argv':argv,'cwd':str(A),'PAVF_REAL_ESTATE':str(ESTATE),
                              'exit':run.returncode,'log':str(log),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
        save()
        if run.returncode:
            print(output)
            raise SystemExit(run.returncode)
    if name=='gate':
        markdown=(E/'ludlow-atomic-delivery-gate.md').read_text()
        assert '| bump | **none** | **none** |' in markdown
        assert 'platform pin unchanged in this PR.' in markdown
        assert git('show',BASE+':composed/evidence.json')==git('show',HEAD+':composed/evidence.json')
        result['checks'][name]['measured_declared_bump']='none'
        result['checks'][name]['measured_composed_bump']='none'
        result['checks'][name]['same_pin_early_return']=True
        result['checks'][name]['composed_evidence_independently_byte_equal']=True
        result['checks'][name]['normal_markdown_sha256']=hashlib.sha256(markdown.encode()).hexdigest()
    else:
        assert 'RealCompilerLayout.test_composition_bytes_do_not_depend_on_checkout_prefix' in output
        assert 'skipped' not in output.lower()
        count=re.search(r'Ran (\d+) tests?',output)
        assert count is not None
        result['checks'][name]['test_count']=int(count.group(1))
        result['checks'][name]['skips']=0
    save()
    print('PASS:',name,flush=True)
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert not git('status','--porcelain','--untracked-files=all').strip()
result['source_still_clean']=True
save()
