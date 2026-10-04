"""Bind genuine byte verification to the final signed CI-repair heads."""
import json
import os
from pathlib import Path
import subprocess
import sys
DAY = Path(__file__).resolve().parent
rows = json.loads((DAY/'adopter-source-A-ci-repaired-candidates.json').read_text())
loc = json.loads((DAY/'adopter-stage2-isolated.json').read_text())
results = {}
for org,row in rows.items():
    repo = Path(row['directory'])
    estate = Path(loc['adopters'][org]['estate'])
    assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'], text=True).strip() == row['head']
    env = dict(os.environ, PAVF_REAL_ESTATE=str(estate), PYTHONPATH=str(repo/'tests'), GITSIGN_REKOR_MODE='offline')
    argv = [sys.executable,'-m','unittest','test_platform_tools.WorkflowHistory','test_platform_tools.RealCompilerLayout']
    done = subprocess.run(argv,cwd=repo,env=env,text=True,capture_output=True,timeout=240)
    log = DAY/f'{org}-source-A-ci-repaired-postcommit-layout.log'
    log.write_text(done.stdout+done.stderr)
    results[org] = {'head':row['head'],'tree':row['tree'],'argv':argv,'cwd':str(repo),'PAVF_REAL_ESTATE':str(estate),'exit':done.returncode,'log':str(log),'stdout':done.stdout,'stderr':done.stderr}
    (DAY/'adopter-source-A-ci-repaired-postcommit-layout.json').write_text(json.dumps(results,indent=2)+'\n')
    assert done.returncode == 0, done.stdout+done.stderr
    assert 'skipped' not in done.stderr
    assert not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip()
    print(org,'signed exact-head real layout and byte replay PASS',flush=True)
