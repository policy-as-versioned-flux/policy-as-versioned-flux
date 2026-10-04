"""Refresh the six published foundation/app main references without changing worktrees."""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
from pathlib import Path
import subprocess

E=Path(__file__).parent
p=E/'publication-foundation-current-source-manifest.json'
original=json.loads(p.read_text())
def refresh(item):
    name,row=item
    directory=row['directory']
    before=subprocess.check_output(['git','-C',directory,'status','--porcelain'])
    subprocess.run(['git','-C',directory,'fetch','origin','main'],check=True,capture_output=True)
    commit=subprocess.check_output(['git','-C',directory,'rev-parse','origin/main'],text=True).strip()
    tree=subprocess.check_output(['git','-C',directory,'rev-parse','origin/main^{tree}'],text=True).strip()
    assert before==subprocess.check_output(['git','-C',directory,'status','--porcelain'])
    assert commit==row['commit'],'Unexpected external source change: '+name
    return name,dict(row,commit=commit,tree=tree,scope='Fresh normal remote main read; worktree preserved; release trust receipts remain separate')
with ThreadPoolExecutor(max_workers=2) as pool:
    records=dict(pool.map(refresh,original['repositories'].items()))
result={'observed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'repositories':records}
(E/'publication-foundation-refreshed-source-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: six actual foundation/application mains unchanged; all source worktrees preserved')
