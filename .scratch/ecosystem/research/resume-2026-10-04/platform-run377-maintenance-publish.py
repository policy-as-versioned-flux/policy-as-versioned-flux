"""Normal branch push and PR for the exact reviewed defensive fixture/lint source."""
import json
from pathlib import Path
import subprocess

day = Path(__file__).resolve().parent
proof = json.loads((day/'platform-run377-maintenance-remote-preflight.json').read_text())
packet = json.loads((day/'platform-run377-maintenance-candidate.json').read_text())
repo = Path(packet['directory'])
assert proof['head'] == packet['head'] == '0547a5fa7babe34227be5085ff63b1cf196d8cae'
assert proof['public'] and proof['admin'] and proof['negative_high_confidence_secret_scan']
assert subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip() == packet['head']
branch = packet['branch']
subprocess.run(['git', '-C', str(repo), 'push', 'origin', 'HEAD:refs/heads/'+branch], check=True)
url = subprocess.check_output(['gh', 'pr', 'create', '--repo', proof['destination'],
    '--base', 'main', '--head', branch,
    '--title', 'Preserve authentic apps history in composition fixtures and lint actual machinery',
    '--body-file', proof['body']], text=True).strip()
number = url.rsplit('/', 1)[1]
pr = json.loads(subprocess.check_output(['gh', 'api', 'repos/'+proof['destination']+'/pulls/'+number], text=True))
assert pr['head']['sha'] == packet['head']
result = {'url': url, 'number': pr['number'], 'head': pr['head']['sha'],
          'destination': proof['destination'], 'branch': branch, 'state': pr['state'],
          'actual_CI_pending': True, 'normal_matching_head_review_merge_pending': True,
          'release_required': False}
(day/'platform-run377-maintenance-public-PR.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
