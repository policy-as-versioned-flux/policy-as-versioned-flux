"""Check the exact atomic delivery source before its normal signed commit."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import yaml

DAY=Path(__file__).resolve().parent
locator=json.loads((DAY/'driftwood-atomic-delivery-checkout.json').read_text())
repo,estate=Path(locator['directory']),Path(locator['estate'])
base=locator['base']
git=lambda *args:subprocess.check_output(['git','-C',str(repo),*args])
assert git('rev-parse','HEAD').decode().strip()==base
changed=git('diff','--name-only').decode().splitlines()
assert set(changed)=={'gitops/flux-system/gotk-sync.yaml','gitops/composed/composed-set.yaml','inventory/PROVENANCE.json','composed/HEADER.yaml'},changed
subprocess.run(['git','-C',str(repo),'diff','--check'],check=True)
old=json.loads(git('show',base+':inventory/PROVENANCE.json'))
new=json.loads((repo/'inventory/PROVENANCE.json').read_text())
assert {k:v for k,v in old.items() if k!='apps_source'}=={k:v for k,v in new.items() if k!='apps_source'}
assert (repo/'inventory/images.json').read_bytes()==git('show',base+':inventory/images.json')
apps=next(d for d in yaml.safe_load_all((repo/'gitops/flux-system/gotk-sync.yaml').read_text()) if d and d.get('kind')=='GitRepository')
composed=list(yaml.safe_load_all((repo/'gitops/composed/composed-set.yaml').read_text()))
source=next(d for d in composed if d and d.get('kind')=='GitRepository')
versions=next(d for d in composed if d and d.get('kind')=='ResourceSet')['spec']['inputs'][0]['versions']
assert apps['spec']['ref']==source['spec']['ref']=={'tag':'v4.0.0','commit':base}
assert versions==[{'version':v} for v in ('5.0.0','6.0.0','7.0.0')]
assert source['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates']=='flux-system/composed-v5-0-0,flux-system/composed-v6-0-0,flux-system/composed-v7-0-0,flux-system/composed-machinery'
for name in ('gitops/engine/kyverno.yaml','twin/PIN.yaml','party.yaml','twin/forward-intel/v1/feed.json','twin/forward-intel/v2/feed.json'):
 assert (repo/name).read_bytes()==git('show',base+':'+name),name
result={'base':base,'directory':str(repo),'estate':str(estate),'changed_paths':changed,
        'engine_and_cloud_declarations_preserved':True,'inventory_and_primary_measurement_preserved':True,
        'coupled_target_and_gates_match':True,'checks':{}}
env=dict(os.environ,PAVF_REAL_ESTATE=str(estate),GITSIGN_REKOR_MODE='offline')
for label,argv in [('public-tests',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py']),('workflow-tests',[sys.executable,'-m','unittest','discover','-s','.github/tests','-p','test_*.py'])]:
 p=subprocess.run(argv,cwd=repo,env=env,text=True,capture_output=True,timeout=300)
 log=DAY/f'driftwood-atomic-delivery-{label}.log'
 log.write_text(p.stdout+p.stderr)
 result['checks'][label]={'argv':argv,'exit':p.returncode,'log':str(log),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
 (DAY/'driftwood-atomic-delivery-precommit-checks.json').write_text(json.dumps(result,indent=2)+'\n')
 assert p.returncode==0,p.stdout+p.stderr
 assert 'skipped' not in p.stderr
 print(label,'PASS, no skips',flush=True)
