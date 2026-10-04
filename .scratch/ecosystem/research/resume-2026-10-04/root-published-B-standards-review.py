"""Root independent review of fresh actual published-main composition B."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

E = Path(__file__).parent
name = sys.argv[1]
assert name in ('driftwood','ludlow')
packet_path = E/f'{name}-composition-B-published-main-candidate.json'
packet = json.loads(packet_path.read_text())
atomic=json.loads((E/f'{name}-atomic-delivery-candidate.json').read_text())
a = Path(packet.get('directory',atomic['directory']))
def sha(data):
    return hashlib.sha256(data).hexdigest()
def git(*args):
    return subprocess.check_output(['git','-C',str(a),*args])
head = packet['head']
assert git('rev-parse','HEAD').decode().strip()==head
assert git('rev-parse','origin/main').decode().strip()==head
assert git('rev-parse','HEAD^{tree}').decode().strip()==packet['tree']
assert not git('status','--porcelain','--untracked-files=all').strip()
assert atomic['tree']==packet['tree']
assert not git('diff',atomic['head'],head).strip()
receipt=json.loads((E/f'{name}-composition-B-main-commit-verification.json').read_text())
assert receipt['sha']==head
verification=receipt.get('verification',receipt.get('commit',{}).get('verification',{}))
assert verification['verified'] is True and verification['reason']=='valid'
assert verification['payload'].startswith('tree '+packet['tree']+'\n')
if name=='ludlow':
    checks={'compose':packet['fresh_normal_compose'],'verify':packet['fresh_normal_verify'],
            'reach':dict(packet['genuine_source_A_reach'],log=str(E/f'{name}-composition-B-published-main-reach.log')),
            'gate':dict(packet['institutional_gate'],log=str(E/f'{name}-composition-B-published-main-gate.log'))}
else:
    checks=packet['checks']
for action in ('compose','verify','reach','gate'):
    check=checks[action]
    assert check['exit']==0
    log=Path(check['log'])
    assert sha(log.read_bytes())==check.get('sha256',check.get('log_sha256'))
assert json.loads(Path(checks['compose']['log']).read_text())['outcome']=='composed'
assert 'OK: composed artefact re-renders byte-for-byte' in Path(checks['verify']['log']).read_text()
grade=checks['gate'].get('result',checks['gate'])
assert grade.get('composed_bump',grade.get('composed'))==grade.get('declared_bump',grade.get('declared'))=='none'
if name=='ludlow':
    markdown=E/f'{name}-composition-B-published-main-gate.md'
    assert sha(markdown.read_bytes())==grade['markdown_sha256']
    assert '| bump | **none** | **none** |' in markdown.read_text()
    assert '> platform pin unchanged in this PR.' in markdown.read_text()
    assert grade['same_pin_early_return'] is True
    assert git('show',head+':composed/evidence.json')==git('show',atomic['base']+':composed/evidence.json')
else:
    assert grade['added']==grade['retired']==[]
rendered=packet['rendered_files_sha256']
assert set(rendered)==set(git('ls-tree','-r','--name-only',head,'--','composed').decode().splitlines())
for path,digest in rendered.items():
    assert sha(git('show',head+':'+path))==digest
    assert sha((a/path).read_bytes())==digest
assert git('rev-parse','refs/tags/v4.0.0^{commit}').decode().strip()==atomic['base']
result={'scope':'Root independent Standards review of fresh genuine render on exact actual published main before Composition B cut',
        'head':head,'tree':packet['tree'],'packet_sha256':sha(packet_path.read_bytes()),
        'actual_merge_signature_verified':True,'reviewed_atomic_tree_equals_actual_main':True,
        'fresh_compose_verify_reach_and_exact_none_gate_receipts_hash_joined':True,
        'rendered_files_independently_bound_to_committed_bytes':len(rendered),
        'source_clean':True,'source_A_release_still_genuine':True,'hard_findings':[],'result':'PASS',
        'cut_requires':'Independent fresh Spec PASS and ordinary immutable signed cut/release workflow'}
(E/f'{name}-composition-B-root-standards-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(name,head,'fresh published B Standards PASS')
