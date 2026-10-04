"""Fetch immutable public primary capture files for the 25 real FAIL grades."""
from pathlib import Path
import hashlib
import json
import subprocess
E = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
C = E / 'hub-run377-captures'
C.mkdir(exist_ok=True)
ref = '48324860b8b9f7dc4762e9c9f841206881a28705'
rows = [line.split('\t', 2) for line in (E / 'hub-run377-grades.tsv').read_text().splitlines() if '\tFAIL\t' in line]
assert len(rows) == 25
report = {'ref': ref, 'clock_run': 377, 'read_only': True, 'capture_reads': []}
out = E / 'hub-run377-capture-reads.json'
for script, grade, lastline in rows:
    slug = script.removeprefix('./').replace('/', '_').removesuffix('.sh')
    path = 'talk/captures/' + slug + '.out'
    argv = ['gh', 'api', '-H', 'Accept: application/vnd.github.raw+json',
        f'repos/policy-as-versioned-flux/policy-as-versioned-flux/contents/{path}?ref={ref}']
    run = subprocess.run(argv, capture_output=True, timeout=25)
    row = {'script': script, 'grade': grade, 'grade_lastline': lastline, 'path': path, 'exit': run.returncode}
    if run.returncode == 0:
        saved = C / (slug + '.out')
        saved.write_bytes(run.stdout)
        row.update({'local_file': str(saved), 'bytes': len(run.stdout), 'sha256': hashlib.sha256(run.stdout).hexdigest()})
    else:
        row['error'] = run.stderr.decode().strip()
    report['capture_reads'].append(row)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('READ:', script, run.returncode, flush=True)
print('Saved immutable capture reads for25 actual FAIL grades.', flush=True)
