"""Normal exact-source final-pointer proof and signed candidate, no remote writes."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import yaml

E = Path(__file__).parent
A = Path('/private/tmp/pavf-driftwood-atomic-20261004-fm_sqsq7/driftwood-estate/driftwood')
BASE = '872d5c7f44801b496731b11cd40881f304f8a09a'
SOURCE_A = '1cd446f62a531c0aeee7e50c0a59a11ac5d00d67'
def git(*args):
    return subprocess.check_output(['git','-C',str(A),*args])
def sha(data):
    return hashlib.sha256(data).hexdigest()
env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PAVF_REAL_ESTATE=str(A.parent),GITSIGN_REKOR_MODE='offline')
packet = {'scope':'Reviewed final composed-only pointer to genuine released B; apps stay A; no activation',
          'directory':str(A),'base':BASE,'branch':'delivery-stage2-composed-B-20261004',
          'apps_A_commit':SOURCE_A,'composed_B_tag':'v4.0.1','composed_B_commit':BASE,
          'composed_B_tag_object':'1faa6914677d8da75ecf5fd4f03c7e338282c789','remote_mutations':False,'checks':{}}
path = E/'driftwood-final-composed-B-candidate.json'
def save():
    path.write_text(json.dumps(packet,indent=2,sort_keys=True)+'\n')
def run(name,argv):
    p = subprocess.run(argv,cwd=A,env=env,capture_output=True,text=True,timeout=300)
    log = E/f'driftwood-final-composed-B-{name}.log'
    log.write_text(p.stdout+p.stderr)
    packet['checks'][name]={'argv':argv,'exit':p.returncode,'log':str(log),'log_sha256':sha(log.read_bytes())}
    save()
    assert p.returncode==0,p.stdout+p.stderr
    print('PASS:',name,flush=True)
    return p
assert git('branch','--show-current').decode().strip()==packet['branch']
assert git('rev-parse','HEAD').decode().strip()==BASE
assert git('rev-parse','origin/main').decode().strip()==BASE
assert git('rev-parse','refs/tags/v4.0.1').decode().strip()==packet['composed_B_tag_object']
assert git('rev-parse','refs/tags/v4.0.1^{commit}').decode().strip()==BASE
assert subprocess.check_output(['git','-C',str(A.parent/'platform-tools'),'rev-parse','HEAD'],text=True).strip()=='703eff6aee959843c4160aa54fd03413f62858cc'
for action in ('compose','verify'):
    r=run(action,[sys.executable,'.github/scripts/platform-tools.py','--adopter-dir','.',
                  '--tools-dir','../platform-tools',action,'.','--estate-clone','..'])
    if action=='compose':
        result=json.loads(r.stdout)
        assert result['outcome']=='composed' and result.get('refusals',[])==[]
    else:
        assert 'OK: composed artefact re-renders byte-for-byte' in r.stdout
run('reach',[sys.executable,'scripts/render_composed.py','reach','--ref','v4.0.1'])
paths = git('diff','--name-only',BASE).decode().splitlines()
assert paths==['composed/HEADER.yaml','gitops/composed/composed-set.yaml'],paths
before=yaml.safe_load(git('show',BASE+':composed/HEADER.yaml'))
after=yaml.safe_load((A/'composed/HEADER.yaml').read_text())
before['comparison-inputs']['after']=after['comparison-inputs']['after']
assert before==after
docs=list(yaml.safe_load_all((A/'gitops/composed/composed-set.yaml').read_text()))
composed=next(d for d in docs if d['kind']=='GitRepository')
assert composed['spec']['ref']=={'tag':'v4.0.1','commit':BASE}
assert 'verify' not in composed['spec']
apps=next(d for d in yaml.safe_load_all((A/'gitops/flux-system/gotk-sync.yaml').read_text()) if d['kind']=='GitRepository')
assert apps['spec']['ref']=={'tag':'v4.0.0','commit':SOURCE_A}
assert json.loads((A/'inventory/PROVENANCE.json').read_text())['apps_source']['commit']==SOURCE_A
assert next(d for d in docs if d['kind']=='ResourceSet')['spec']['inputs'][0]['versions']==[{'version':v} for v in ('5.0.0','6.0.0','7.0.0')]
assert composed['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates'].split(',')==[
    'flux-system/composed-v5-0-0','flux-system/composed-v6-0-0','flux-system/composed-v7-0-0','flux-system/composed-machinery']
for p in git('ls-tree','-r','--name-only',BASE).decode().splitlines():
    if p not in paths:
        assert (A/p).read_bytes()==git('show',BASE+':'+p),p
packet['changed_paths']=paths
packet['apps_inventory_all_other_bytes_preserved']=True
packet['HEADER_fingerprint_only']=True
git('add','--',*paths)
git('commit','-m','Deliver verified composition B while preserving apps source A\n\nMove only composed delivery to genuine signed and published v4.0.1; rerender its comparison identity with authenticated tools5. Preserve apps Source A, primary inventory, the complete policies5/6/7 window, engine and cloud declarations.\n\nPrepared-by: Codex agent; no human was present during preparation.')
head=git('rev-parse','HEAD').decode().strip()
packet.update(head=head,tree=git('rev-parse','HEAD^{tree}').decode().strip(),normal_SSH_signature=git('log','-1','--format=%G?').decode().strip(),
              file_sha256={p:sha((A/p).read_bytes()) for p in paths})
assert packet['normal_SSH_signature']=='G'
assert not git('status','--porcelain','--untracked-files=all').strip()
run('source-signature',['git','verify-commit',head])
save()
(E/'driftwood-final-composed-B.patch').write_bytes(git('diff','--binary',BASE,head))
pin=E/'driftwood-final-composed-B-old-platform-pin.yaml'
pin.write_bytes(git('show',BASE+':gitops/platform/platform-pin.yaml'))
out=E/'driftwood-final-composed-B-gate.json'
run('gate',[sys.executable,'.github/scripts/adopter-gate.py','--platform-dir',str(A.parent/'platform'),
    '--new-pin-yaml','gitops/platform/platform-pin.yaml','--old-pin-yaml',str(pin),
    '--identity-regexp',r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$',
    '--issuer','https://token.actions.githubusercontent.com','--adopter-dir',str(A),
    '--base-ref',BASE,'--head-ref',head,'--out',str(out)])
grade=json.loads(out.read_text())
assert grade['declared']==grade['composed']=='none' and grade['added']==grade['retired']==[]
packet['checks']['gate']['result']=grade
save()
run('postcommit-real-layout',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_platform_tools.py','-v'])
assert git('rev-parse','HEAD').decode().strip()==head
assert not git('status','--porcelain','--untracked-files=all').strip()
packet['source_clean']=True
assert 'skipped' not in (E/'driftwood-final-composed-B-postcommit-real-layout.log').read_text()
packet['patch_sha256']=sha((E/'driftwood-final-composed-B.patch').read_bytes())
packet['authentic_release_receipt']=str(E/'driftwood-composition-B-authentic-release.json')
packet['authentic_release_receipt_sha256']=sha((E/'driftwood-composition-B-authentic-release.json').read_bytes())
save()
(E/'driftwood-final-composed-B-PR-body.md').write_text('''Move composed delivery to the genuine signed and published v4.0.1 Composition B release, whose tree binds apps and the native inventory to v4.0.0 Source A. Apps and inventory retain their genuine A source, and policies 5.0.0, 6.0.0 and 7.0.0 retain all four signature gates.

Only the composed source reference and its explanatory comments change, with a fresh derived HEADER comparison fingerprint. All remaining source bytes are preserved. The signed v5.0.0 tools re-render and verify byte-for-byte; reach against authentic v4.0.1, the exact-head institutional none gate, and enabled real-estate public layout tests pass. Engine 1.18.2 and the existing cloud declaration are preserved. Live reconciliation is established by the scheduled observer, not this PR.
''')
print('Candidate ready:',head,flush=True)
