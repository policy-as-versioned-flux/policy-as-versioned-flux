"""Independent exact committed-byte review of final DW/LU composed B pointers."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import yaml

name=sys.argv[1]
assert name in ('driftwood','ludlow')
E=Path(__file__).parent
suffix='final-composed-B-current-main' if name=='driftwood' else 'final-composed-B'
packet_path=E/f'{name}-{suffix}-candidate.json'
packet=json.loads(packet_path.read_text())
atomic=json.loads((E/f'{name}-atomic-delivery-candidate.json').read_text())
a=Path(packet.get('directory',atomic['directory']))
def git(*args):
    return subprocess.check_output(['git','-C',str(a),*args])
def sha(data):
    return hashlib.sha256(data).hexdigest()
head,base=packet['head'],packet['base']
assert git('rev-parse','HEAD').decode().strip()==head
assert git('rev-parse','HEAD^{tree}').decode().strip()==packet['tree']
assert git('log','-1','--format=%G?').decode().strip()=='G'
assert not git('status','--porcelain','--untracked-files=all').strip()
paths=git('diff','--name-only',base,head).decode().splitlines()
assert paths==['composed/HEADER.yaml','gitops/composed/composed-set.yaml']
for p in git('ls-tree','-r','--name-only',head).decode().splitlines():
    if p not in paths:
        assert git('show',base+':'+p)==git('show',head+':'+p),p
before=yaml.safe_load(git('show',base+':composed/HEADER.yaml'))
after=yaml.safe_load(git('show',head+':composed/HEADER.yaml'))
before['comparison-inputs']['after']=after['comparison-inputs']['after']
assert before==after
docs=list(yaml.safe_load_all(git('show',head+':gitops/composed/composed-set.yaml')))
composed=next(d for d in docs if d['kind']=='GitRepository')
auth=json.loads((E/f'{name}-composition-B-authentic-release.json').read_text())
release_commit=auth.get('peeled_commit',auth.get('commit'))
assert composed['spec']['ref']=={'tag':'v4.0.1','commit':release_commit}
assert git('merge-base','--is-ancestor',release_commit,base)==b''
assert 'verify' not in composed['spec']
assert next(d for d in docs if d['kind']=='ResourceSet')['spec']['inputs'][0]['versions']==[{'version':v} for v in ('5.0.0','6.0.0','7.0.0')]
assert composed['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates'].split(',')==[
    'flux-system/composed-v5-0-0','flux-system/composed-v6-0-0','flux-system/composed-v7-0-0','flux-system/composed-machinery']
apps=next(d for d in yaml.safe_load_all(git('show',head+':gitops/flux-system/gotk-sync.yaml')) if d['kind']=='GitRepository')
assert apps['spec']['ref']=={'tag':'v4.0.0','commit':atomic['base']}
assert auth['tag']=='v4.0.1'
if 'signature' in auth:
    assert all(auth['signature'][k] is True for k in ('Git','Rekor','certificate'))
    assert auth['cut_conclusion']==auth['release_conclusion']=='success'
else:
    assert all(auth[k] is True for k in ('git_signature','rekor_entry','certificate_claims','final_composed_pointer_edits_may_begin'))
assert git('rev-parse','refs/tags/v4.0.1').decode().strip()==auth['tag_object']
assert git('rev-parse','refs/tags/v4.0.1^{commit}').decode().strip()==release_commit
checks=packet.get('checks')
if checks is None:
    checks={'compose':packet['normal_tools_compose'],'verify':packet['normal_tools_verify'],**packet['exact_postcommit_checks']}
for check in checks.values():
    assert check['exit']==0
    log=Path(check['log'])
    assert sha(log.read_bytes())==check.get('log_sha256',check.get('sha256'))
assert json.loads(Path(checks['compose']['log']).read_text())['outcome']=='composed'
assert 'OK: composed artefact re-renders byte-for-byte' in Path(checks['verify']['log']).read_text()
if name=='ludlow':
    markdown=(E/'ludlow-final-composed-B-gate.md').read_bytes()
    assert sha(markdown)==checks['gate']['markdown_sha256']
    assert '| bump | **none** | **none** |' in markdown.decode()
    assert checks['postcommit_real_estate_public_tests']['test_count']==37
    assert checks['postcommit_real_estate_public_tests']['skips']==0
else:
    assert checks['gate']['result']['declared_bump']==checks['gate']['result']['composed_bump']=='none'
    assert 'Ran 3 tests' in Path(checks['postcommit-real-layout']['log']).read_text()
result={'scope':'Root independent Standards review of exact final composed-only B pointer and normal proof receipts',
        'head':head,'base':base,'tree':packet['tree'],'packet_sha256':sha(packet_path.read_bytes()),
        'source_clean':True,'SSH_signature':'G','changed_paths':paths,'hand_authored_diff_inspected':True,
        'HEADER_fingerprint_only':True,'all_other_committed_bytes_unchanged':True,'authentic_released_B_tag_object_and_peel_match':True,
        'apps_A_and_primary_inventory_preserved':True,'normal_check_receipts_hash_joined':True,
        'hard_findings':[],'result':'PASS','publication_requires':'Exact Spec PASS and normal CI/App matching-head review; user exact public authorization if required'}
(E/f'{name}-{suffix}-root-standards-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(name,head,'final pointer Standards PASS')
