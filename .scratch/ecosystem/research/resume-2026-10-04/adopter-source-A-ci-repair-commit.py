"""Sign and export the narrow actual-CI repairs, retaining historical SourceA proof."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

DAY = Path(__file__).resolve().parent
loc = json.loads((DAY / 'adopter-stage2-isolated.json').read_text())
old = json.loads((DAY / 'adopter-stage2-final-source-A-candidates.json').read_text())
checks = json.loads((DAY / 'adopter-source-A-ci-repair-checks.json').read_text())
proof = json.loads((DAY / 'driftwood-source-A-real-completer.json').read_text())
assert proof['exit'] == proof['verify']['exit'] == 0
assert proof['old_v1_before_sha256'] == proof['old_v1_after_sha256']
assert proof['expected_v2_sha256'] == proof['actual_v2_sha256']
rows = {}
for org in ('driftwood', 'ludlow'):
    repo = Path(loc['adopters'][org]['dir'])
    assert all(record['exit'] == 0 for record in checks[org].values())
    git = lambda *args: subprocess.check_output(['git','-C',str(repo),*args], text=True).strip()
    before = git('rev-parse','HEAD')
    assert before == old[org]['head']
    subprocess.run(['git','-C',str(repo),'diff','--check'], check=True)
    subprocess.run(['git','-C',str(repo),'add','--all'], check=True)
    message = ('Keep immutable apps inputs and history available in CI\n\n'
               'Use full adopter history in both history-reading jobs and retain it across '
               'refetches; expose composer refusals in real-layout test diagnostics. '
               + ('Bind feed completion to the published twin hub pin and current emitter major, '
                  'then compose after twin derivation so the result replays. ' if org == 'driftwood' else '')
               + '\n\nPrepared-by: Codex agent; no human was present during preparation.')
    subprocess.run(['git','-C',str(repo),'commit','-m',message], check=True)
    head = git('rev-parse','HEAD')
    assert git('log','-1','--format=%G?') == 'G'
    signature = subprocess.run(['git','-C',str(repo),'verify-commit',head], text=True, capture_output=True)
    assert signature.returncode == 0, signature.stderr
    siglog = DAY / f'{org}-source-A-ci-repair-ssh-signature.log'
    siglog.write_text(signature.stdout + signature.stderr)
    assert not git('status','--porcelain')
    full_patch = DAY / f'{org}-source-A-ci-repaired.patch'
    narrow_patch = DAY / f'{org}-source-A-ci-repair-followup.patch'
    for base, path in ((old[org]['base'],full_patch),(before,narrow_patch)):
        path.write_bytes(subprocess.check_output(['git','-C',str(repo),'diff','--binary','--full-index',base,head]))
        subprocess.run(['git','-C',str(repo),'apply','--reverse','--check',str(path)], check=True, capture_output=True)
    paths = git('diff','--name-only',before,head).splitlines()
    rows[org] = {**old[org], 'head': head, 'tree': git('rev-parse','HEAD^{tree}'), 'previous_reviewed_head': before,
                 'clean': True, 'signature_log': str(siglog), 'ssh_signature': 'G',
                 'stat': git('diff','--shortstat',old[org]['base'],head),
                 'changed_paths': git('diff','--name-status',old[org]['base'],head).splitlines(),
                 'followup_changed_paths': paths,
                 'followup_blob_sha256': {name: hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in paths},
                 'patch': str(full_patch), 'patch_sha256': hashlib.sha256(full_patch.read_bytes()).hexdigest(),
                 'followup_patch': str(narrow_patch), 'followup_patch_sha256': hashlib.sha256(narrow_patch.read_bytes()).hexdigest(),
                 'validation_receipts': ['adopter-source-A-ci-repair-checks.json','driftwood-source-A-real-completer.json'],
                 'publication_hold': 'Fresh independent exact-head review, successful actual PR CI, then root normal merge/cut; no activation yet.'}
    (DAY / 'adopter-source-A-ci-repaired-candidates.json').write_text(json.dumps(rows, indent=2)+'\n')
    print(org, head, rows[org]['tree'], flush=True)
