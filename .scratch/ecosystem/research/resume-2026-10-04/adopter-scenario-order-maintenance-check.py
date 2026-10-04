"""Finite genuine-tool and public-consumer checks for isolated maintenance sources."""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
import yaml
E=Path(__file__).resolve().parent
H=E.parents[3]
TOOLS='703eff6aee959843c4160aa54fd03413f62858cc'
PIN='5bc47331a536476f3580542be794908f5053f816'
GENERIC='974e73514e0d8d4cad2e6906acf51d1cc27028b3'
env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GITSIGN_REKOR_MODE='offline', PATH=str(H/'.venv/bin')+os.pathsep+os.environ['PATH'])
packet={'scope':'separate local maintenance; no release, live observation, quote or activation','checks':{},'adopters':{}}
out=E/'adopter-scenario-order-maintenance-checks.json'
def save():out.write_text(json.dumps(packet,indent=2,sort_keys=True)+'\n')
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a])
def sha(b):return hashlib.sha256(b).hexdigest()
def run(name,argv,cwd,extra=None):
 p=subprocess.run(argv,cwd=cwd,env={**env,**(extra or {})},capture_output=True,text=True)
 log=E/(name+'.log');log.write_text(p.stdout+p.stderr)
 packet['checks'][name]={'argv':argv,'cwd':str(cwd),'exit':p.returncode,'log':str(log),'log_sha256':sha(log.read_bytes())};save()
 assert p.returncode==0,p.stdout+p.stderr
 print('PASS:',name,flush=True)
 return p
for org in ('ludlow','tuppence'):
 R=Path(f'/private/tmp/pavf-{org}-maintenance-20261004-estate/{org}')
 base=git(R,'rev-parse','HEAD').decode().strip()
 assert git(R.parent/'platform-tools','rev-parse','HEAD').decode().strip()==TOOLS
 original={p:sha(git(R,'show',base+':'+p)) for p in git(R,'ls-tree','-r','--name-only',base).decode().splitlines()}
 row={'directory':str(R),'base':base,'tools_commit':TOOLS,'original_tracked_sha256':original}
 packet['adopters'][org]=row;save()
 for action in ('compose','verify'):
  r=run(org+'-scenario-order-'+action,[sys.executable,'.github/scripts/platform-tools.py','--adopter-dir','.',
        '--tools-dir','../platform-tools',action,'.','--estate-clone','..'],R)
  if action=='compose':assert json.loads(r.stdout)['outcome']=='composed'
  else:assert 'OK: composed artefact re-renders byte-for-byte' in r.stdout
 changed=git(R,'diff','--name-only',base).decode().splitlines()
 assert changed==['composed/HEADER.yaml','gitops/flux-system/gotk-sync.yaml','twin/verify-twin-scenarios.sh'],changed
 before=yaml.safe_load(git(R,'show',base+':composed/HEADER.yaml'))
 after=yaml.safe_load((R/'composed/HEADER.yaml').read_text())
 before['comparison-inputs']['after']=after['comparison-inputs']['after'];assert before==after
 for path,digest in original.items():
  if path not in changed:assert sha((R/path).read_bytes())==digest,path
 row.update(changed_tracked_paths=changed, HEADER_fingerprint_only=True, all_other_original_source_preserved=True)
 save()
 tests=run(org+'-scenario-order-public-tests',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],R,{'PAVF_REAL_ESTATE':str(R.parent)})
 assert 'RealCompilerLayout.test_composition_bytes_do_not_depend_on_checkout_prefix' in tests.stdout+tests.stderr
 assert 'skipped' not in (tests.stdout+tests.stderr).lower()
 row['public_test_count']=int(re.search(r'Ran (\d+) tests?',tests.stdout+tests.stderr).group(1));save()
with tempfile.TemporaryDirectory(prefix='pavf-scenario-order-public-check-') as t:
 clean=Path(t)/'hub'
 run('scenario-order-clean-hub-clone',['git','clone','--quiet','--no-hardlinks','--no-checkout',str(H/'.estate-publish/hub'),str(clean)],H)
 run('scenario-order-clean-hub-checkout',['git','-C',str(clean),'checkout','--quiet','--detach',PIN],H)
 copies=clean/'.estate-clone';copies.mkdir(exist_ok=True)
 feeds=copies/'feeds'
 run('scenario-order-real-feed-clone',['git','clone','--quiet','--no-hardlinks',str(Path('/private/tmp/pavf-ludlow-maintenance-20261004-estate/feeds')),str(feeds)],H)
 run('scenario-order-real-feed-checkout',['git','-C',str(feeds),'checkout','--quiet','--detach',GENERIC],H)
 for org in ('ludlow','tuppence'):
  R=Path(packet['adopters'][org]['directory']);copy=copies/org
  shutil.copytree(R,copy,ignore=shutil.ignore_patterns('.git','__pycache__'))
  r=run(org+'-scenario-order-actual-standing-checker',['bash',str(copy/'twin/verify-twin-scenarios.sh')],clean)
  assert 'declared consequence basis: native valuation grade 3, loss mechanism grade 3, admitted by pricing threshold 3' in r.stdout
  assert 'FAIL:' not in r.stdout
  assert 'byte-identically' in r.stdout
packet['no_remote_mutations']=True;save()
