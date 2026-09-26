#!/usr/bin/env python3
"""Independent verifier driver. Uses a byte-identical copy of engine_compatibility.py.

modes:
  check   <binary> <outdir> <repo>
  row     <binary> <outdir> <repo>            -- _published_row with the array's 5.0.0 entry
  variant <binary> <outdir> <tree>            -- _matrix on a scratch COPY of <tree>, both families
"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
import engine_compatibility as ec

mode, binary, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
calls = []
_orig = ec._run


def _run(args, **kw):
    r = _orig(args, **kw)
    if len(args) > 1 and args[1] == 'test':
        fam = Path(args[2]).name
        (out / f'{fam}.kyverno-test.out').write_text(r.stdout + r.stderr)
        (out / f'{fam}.manifest.yaml').write_text((Path(args[2]) / 'kyverno-test.yaml').read_text())
        calls.append((fam, r.returncode))
    return r


ec._run = _run

if mode == 'check':
    res = ec.check(Path(sys.argv[4]), binary)
elif mode == 'row':
    repo = Path(sys.argv[4])
    doc = yaml.safe_load((repo / 'distribution/versions.yaml').read_text())
    entry = [e for e in doc['spec']['inputs'][0]['versions'] if e.get('version') == '5.0.0'][0]
    res = ec._published_row(repo, entry, binary)
elif mode == 'variant':
    with tempfile.TemporaryDirectory() as t:
        root = Path(t) / 'tree'
        shutil.copytree(sys.argv[4], root)
        res = {'matrices': [ec._matrix(root, '5.0.0', f, binary) for f in ec.FAMILIES]}
else:
    raise SystemExit('bad mode')

(out / 'result.json').write_text(json.dumps(res, indent=2))
rows = res.get('rows', [res]) if mode == 'check' else [res]
print('outcome:', res.get('outcome'), res.get('reason', ''))
for row in rows:
    if 'matrices' not in row:
        print('  row', row.get('policy_version'), row.get('outcome'), row.get('reason'))
        continue
    if 'tag_commit' in row:
        print('  tag_commit', row['tag_commit'], 'array_commit', row['array_commit'], 'apis', row['api_versions'])
    for m in row['matrices']:
        print(f"  {m['family']}: {m['outcome']} passed={m['passed_assertions']} failed={m['failed_assertions']} exit={m['exit_code']}")
