"""Fresh public destination/main metadata; no branch or publication mutation."""
from pathlib import Path
import json,subprocess
E=Path(__file__).resolve().parent
adopters=json.loads((E/'adopter-scenario-order-maintenance-candidates.json').read_text())['adopters']
insurer=json.loads((E/'insurer-compatible-platform-pin-candidate.json').read_text())
rows={**adopters,'insurer':insurer};result={}
for org,row in rows.items():
 repo='policy-as-versioned-'+org+'/'+org
 metadata=json.loads(subprocess.check_output(['gh','repo','view',repo,'--json','nameWithOwner,isPrivate,viewerPermission,defaultBranchRef,url'],text=True))
 main=json.loads(subprocess.check_output(['gh','api','repos/'+repo+'/git/ref/heads/main'],text=True))
 assert metadata['isPrivate'] is False and metadata['viewerPermission']=='ADMIN'
 result[org]={'metadata':metadata,'actual_remote_main':main['object']['sha'],'candidate_base':row['base'],
              'base_matches_remote':main['object']['sha']==row['base'],'head':row['head']}
 (E/'maintenance-source-readonly-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
 print(org,main['object']['sha'],'matches candidate base',result[org]['base_matches_remote'],flush=True)
