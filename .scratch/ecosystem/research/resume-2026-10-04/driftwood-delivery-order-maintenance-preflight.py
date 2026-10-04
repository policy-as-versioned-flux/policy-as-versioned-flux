"""Read actual public metadata/main for the exact reviewed maintenance payload."""
import hashlib
import json
from pathlib import Path
import subprocess

day = Path(__file__).resolve().parent
packet = json.loads((day/'driftwood-delivery-order-maintenance-candidate.json').read_text())
repo = Path(packet['directory'])
destination = 'policy-as-versioned-driftwood/driftwood'
head = packet['head']

def command(argv):
    return subprocess.check_output(argv, text=True).strip()

for name in ('independent-review', 'spec-review'):
    proof = json.loads((day/f'driftwood-delivery-order-maintenance-{name}.json').read_text())
    assert proof['verdict'] == 'PASS' and proof['head'] == head
assert command(['git', '-C', str(repo), 'rev-parse', 'HEAD']) == head
assert not command(['git', '-C', str(repo), 'status', '--porcelain'])
metadata = json.loads(command(['gh', 'api', 'repos/'+destination]))
assert metadata['full_name'] == destination and not metadata['private']
assert metadata['permissions']['admin'] is True
main = json.loads(command(['gh', 'api', 'repos/'+destination+'/commits/main']))
subprocess.run(['git', '-C', str(repo), 'fetch', '--quiet', 'origin', 'main'], check=True)
assert command(['git', '-C', str(repo), 'rev-parse', 'origin/main']) == main['sha']
subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', packet['base'], main['sha']], check=True)
delta = command(['git', '-C', str(repo), 'diff', '--name-only', packet['base'], main['sha']]).splitlines()
assert not delta or all(p.startswith(('drift/', 'observations/')) and p.endswith('.jsonl') for p in delta), delta
body = day/'driftwood-delivery-order-maintenance-PR-body.md'
result = {'destination': destination, 'public': True, 'admin': True,
          'head': head, 'tree': packet['tree'], 'main': main['sha'],
          'base_to_current_main': delta, 'reviewed_paths': packet['changed_paths'],
          'body': str(body), 'body_sha256': hashlib.sha256(body.read_bytes()).hexdigest(),
          'source_clean': True, 'remote_mutations': False}
(day/'driftwood-delivery-order-maintenance-remote-preflight.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
