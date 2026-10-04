"""Read public metadata and exact reviewed source before normal maintenance PR."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

day = Path(__file__).resolve().parent
packet = json.loads((day/'platform-run377-maintenance-candidate.json').read_text())
repo = Path(packet['directory'])
destination = 'policy-as-versioned-platform/platform'

def command(argv):
    return subprocess.check_output(argv, text=True).strip()

for name in ('independent-standards-review', 'spec-review'):
    proof = json.loads((day/f'platform-run377-maintenance-{name}.json').read_text())
    assert proof['verdict'] == 'PASS' and proof['head'] == packet['head']
assert command(['git', '-C', str(repo), 'rev-parse', 'HEAD']) == packet['head']
assert not command(['git', '-C', str(repo), 'status', '--porcelain'])
metadata = json.loads(command(['gh', 'api', 'repos/'+destination]))
assert metadata['full_name'] == destination and not metadata['private']
assert metadata['permissions']['admin'] is True
main = json.loads(command(['gh', 'api', 'repos/'+destination+'/commits/main']))
subprocess.run(['git', '-C', str(repo), 'fetch', '--quiet', 'origin', 'main'], check=True)
assert command(['git', '-C', str(repo), 'rev-parse', 'origin/main']) == main['sha']
subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', packet['base'], main['sha']], check=True)
delta = command(['git', '-C', str(repo), 'diff', '--name-only', packet['base'], main['sha']]).splitlines()
assert not delta, delta
credential = re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}')
source_bytes = 0
for path in packet['changed_paths']:
    data = (repo/path).read_bytes()
    assert not credential.search(data), 'High-confidence credential pattern in reviewed source'
    source_bytes += len(data)
body = day/'platform-run377-maintenance-PR-body.md'
assert not credential.search(body.read_bytes())
result = {'destination': destination, 'public': True, 'admin': True,
          'head': packet['head'], 'tree': packet['tree'], 'main': main['sha'],
          'base_to_current_main': delta, 'reviewed_paths': packet['changed_paths'],
          'body': str(body), 'body_sha256': hashlib.sha256(body.read_bytes()).hexdigest(),
          'negative_high_confidence_secret_scan': True,
          'source_bytes': source_bytes, 'source_clean': True, 'remote_mutations': False}
(day/'platform-run377-maintenance-remote-preflight.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
