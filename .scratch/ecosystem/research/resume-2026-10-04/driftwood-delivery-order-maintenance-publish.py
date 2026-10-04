"""Normal public push/PR for the exact reviewed four-path maintenance commit."""
import json
from pathlib import Path
import subprocess

day = Path(__file__).resolve().parent
proof = json.loads((day/'driftwood-delivery-order-maintenance-remote-preflight.json').read_text())
packet = json.loads((day/'driftwood-delivery-order-maintenance-candidate.json').read_text())
repo = Path(packet['directory'])
assert proof['head'] == packet['head'] == '8d9ae2ec514ca75c2c460b4f057a3a741e69b21a'
assert proof['public'] and proof['admin']
branch = packet['branch']
assert subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip() == packet['head']
subprocess.run(['git', '-C', str(repo), 'push', 'origin', 'HEAD:refs/heads/'+branch], check=True)
url = subprocess.check_output(['gh', 'pr', 'create', '--repo', proof['destination'],
    '--base', 'main', '--head', branch,
    '--title', 'Order native apps after the composed policy window',
    '--body-file', proof['body']], text=True).strip()
number = url.rsplit('/', 1)[1]
pr = json.loads(subprocess.check_output(['gh', 'api', 'repos/'+proof['destination']+'/pulls/'+number], text=True))
assert pr['head']['sha'] == packet['head']
result = {'url': url, 'number': pr['number'], 'head': pr['head']['sha'],
          'destination': proof['destination'], 'branch': branch, 'state': pr['state'],
          'actual_CI_pending': True, 'normal_matching_head_review_merge_pending': True}
(day/'driftwood-delivery-order-maintenance-public-PR.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
