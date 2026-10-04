"""Replay two genuine run377 integration faults; no scheduled pass is inferred."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--hub', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
hub = args.hub.resolve()
env = dict(os.environ)
env.pop('PYTHON', None)
env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env.get('PATH', '')
assert not (hub / '.venv/bin/python').exists(), 'repro needs the real clock checkout layout'
subprocess.run(['python3', '-c', 'import yaml'], env=env, check=True, capture_output=True)
runtime = {}
for lane in ('served-workloads', 'oscal-lane'):
    script = hub / 'verify' / lane / ('verify-' + lane + '.sh')
    result = subprocess.run(['bash', str(script)], cwd=hub, env=env,
                            text=True, capture_output=True, timeout=30)
    runtime[lane] = {'exit': result.returncode,
                     'no_hub_interpreter': 'no hub interpreter' in result.stdout,
                     'output': result.stdout.strip()}
spec = importlib.util.spec_from_file_location('run377_truth_manifest', hub / 'talk/truth_manifest.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
entries = module.load_manifest(str(hub / 'talk/verify-manifest.txt'))
required = ['verify/cve-inventory/verify-cve-inventory.sh',
            'verify/engine-pairing/verify-engine-pairing.sh',
            'verify/twin-cage/verify-twin-cage.sh']
missing = [path for path in required if path not in entries]
counter = module.summarise(entries, [(required[0], 'PASS',
    'PASS: ludlow served CVE line prices its digest-matched inventory intersection')])
receipt = {'runtime': runtime, 'missing_manifest_rows': missing,
           'genuine_CVE_PASS_output_counted_as_fail': counter.failed,
           'genuine_CVE_PASS_output_counted_as_pass': counter.passed,
           'manifest_explanation': counter.extra_rows,
           'live_or_scheduled_observation_claimed': False}
args.out.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
raise SystemExit(1 if missing or counter.failed or any(
    row['no_hub_interpreter'] for row in runtime.values()) else 0)
