"""Exact committed candidate checks, ordinary tools/trust, finite local-only."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
E=Path(__file__).resolve().parent
packet=json.loads((E/'adopter-scenario-order-current-clock-maintenance-candidates.json').read_text())
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GITSIGN_REKOR_MODE='offline')
identity=r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'
result={'adopters':{},'remote_mutations':False}
out=E/'adopter-scenario-order-current-clock-maintenance-postcommit.json'
def save():out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
for org,row in packet['adopters'].items():
 R=Path(row['directory']);base=row['base'];head=row['head']
 def git(*a):return subprocess.check_output(['git','-C',str(R),*a])
 assert git('rev-parse','HEAD').decode().strip()==head
 assert git('rev-parse','HEAD^{tree}').decode().strip()==row['tree']
 assert not git('status','--porcelain','--untracked-files=all').strip()
 current={'head':head,'tree':row['tree'],'base':base,'checks':{}}
 result['adopters'][org]=current;save()
 def run(name,argv):
  p=subprocess.run(argv,cwd=R,env={**env,'PAVF_REAL_ESTATE':str(R.parent)},capture_output=True,text=True)
  log=E/(org+'-scenario-order-current-clock-postcommit-'+name+'.log');log.write_text(p.stdout+p.stderr)
  current['checks'][name]={'argv':argv,'exit':p.returncode,'log':str(log),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()};save()
  assert p.returncode==0,p.stdout+p.stderr
  print('PASS:',org,name,flush=True)
  return p
 run('verify',[sys.executable,'.github/scripts/platform-tools.py','--adopter-dir','.',
       '--tools-dir','../platform-tools','verify','.','--estate-clone','..'])
 run('reach',[sys.executable,'scripts/render_composed.py','reach','--ref','v4.0.1'])
 if org=='ludlow':
  gate=E/(org+'-scenario-order-current-clock-postcommit-gate.md')
  run('gate',[sys.executable,'.github/scripts/adopter_gate.py','--platform-dir',str(R.parent/'platform'),
      '--ludlow-dir',str(R),'--old-ref',base,'--new-ref',head,'--composed-base-ref',base,'--composed-head-ref',head,
      '--identity-regexp',identity,'--issuer','https://token.actions.githubusercontent.com','--out-comment',str(gate)])
  text=gate.read_text();assert '| bump | **none** | **none** |' in text and 'platform pin unchanged in this PR.' in text
 else:
  oldpin=E/(org+'-scenario-order-current-clock-old-platform-pin.yaml');oldpin.write_bytes(git('show',base+':gitops/platform/platform-pin.yaml'))
  gate=E/(org+'-scenario-order-current-clock-postcommit-gate.json')
  run('gate',[sys.executable,'.github/scripts/adopter-gate.py','--platform-dir',str(R.parent/'platform'),
      '--new-pin-yaml','gitops/platform/platform-pin.yaml','--old-pin-yaml',str(oldpin),
      '--identity-regexp',identity,'--issuer','https://token.actions.githubusercontent.com','--adopter-dir',str(R),
      '--base-ref',base,'--head-ref',head,'--out',str(gate)])
  grade=json.loads(gate.read_text());assert grade['declared']==grade['composed']=='none' and grade['added']==grade['retired']==[]
 assert git('show',base+':composed/evidence.json')==git('show',head+':composed/evidence.json')
 current['checks']['gate'].update(declared='none',composed='none',same_pin_early_return=True,
      composed_evidence_independently_byte_equal=True,result_sha256=hashlib.sha256(gate.read_bytes()).hexdigest())
 test=run('public-tests',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'])
 text=test.stdout+test.stderr
 assert 'skipped' not in text.lower()
 count=int(re.search(r'Ran (\d+) tests?',text).group(1));assert count==47
 current['checks']['public-tests'].update(test_count=count,skips=0)
 assert not git('status','--porcelain','--untracked-files=all').strip()
 current['clean_after_checks']=True;save()
