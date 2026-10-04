"""Apply only the coupled delivery declarations to genuine released Source A."""
from pathlib import Path
import json
import subprocess

ADOPTER = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/tuppence-estate/tuppence')
EVIDENCE = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/research/resume-2026-10-04')
COMMIT = 'f575dc12de130c444d98a831de0ca21fd68b9c46'
assert subprocess.check_output(['git','-C',str(ADOPTER),'rev-parse','HEAD'],text=True).strip() == COMMIT
assert not subprocess.check_output(['git','-C',str(ADOPTER),'status','--porcelain'],text=True).strip()

path = ADOPTER/'gitops/flux-system/gotk-sync.yaml'
text = path.read_text()
assert text.count('tag: v3.0.1') == 1
assert text.count('commit: d8dead25e0e5e275172640b1a637562e45edb15d') == 1
text = text.replace('tag: v3.0.1', 'tag: v4.0.0').replace('commit: d8dead25e0e5e275172640b1a637562e45edb15d', 'commit: '+COMMIT)
text = text.replace("tuppence's own signed v3.0.1 apps release", "tuppence's own signed v4.0.0 apps release")
path.write_text(text)

path = ADOPTER/'inventory/PROVENANCE.json'
provenance = json.loads(path.read_text())
before = json.loads(json.dumps(provenance))
source = provenance['apps_source']
assert source['tag'] == 'v3.0.1'
source.update(tag='v4.0.0', commit=COMMIT, tag_object='17070ad568397bb7c394f80cb0d51ebcf560089e')
source['signature'].update(tlog_index='3077499916', rekor_entry='https://rekor.sigstore.dev/api/v1/log/entries?logIndex=3077499916')
assert {k:v for k,v in before.items() if k!='apps_source'} == {k:v for k,v in provenance.items() if k!='apps_source'}
path.write_text(json.dumps(provenance, indent=2, sort_keys=True)+'\n')

path = ADOPTER/'gitops/composed/composed-set.yaml'
text = path.read_text()
old = '''#   * the tag is v3.0.0, not the v1.0.0 in gitops/flux-system/gotk-sync.yaml. v1.0.0 predates
#     composed/ and does not carry the tree this reconciles. A self-pin bump is a reviewed PR that
#     moves tag and commit together (renovate.json's customManagers track nist and platform, not
#     the self-pin).'''
new = '''#   * the tag is v4.0.0, the same genuine Source A release as the apps source in
#     gitops/flux-system/gotk-sync.yaml. Its composed tree carries policies 5.0.0, 6.0.0 and 7.0.0.
#     The coupled self-pin, inventory binding, array and verification gates move in one reviewed
#     change; renovate.json tracks publisher parents rather than these self-pins.'''
assert old in text
text = text.replace(old,new)
assert text.count('tag: v3.0.0') == 1
assert text.count('commit: 3d64a4d65d5eb5d81deedc10a0826c8b02d0ad39') == 1
text = text.replace('tag: v3.0.0', 'tag: v4.0.0').replace('commit: 3d64a4d65d5eb5d81deedc10a0826c8b02d0ad39','commit: '+COMMIT)
text = text.replace('# The resolved SHA tuppence\'s own v3.0.0 tag points to (`git rev-parse \'v3.0.0^{}\'`,\n    # 2026-09-24). Belt-and-braces immutability, ADR-0001.', '# The resolved SHA of the genuine signed v4.0.0 Source A release (2026-10-04).\n    # Belt-and-braces immutability, ADR-0001.')
text = text.replace('policy-as-versioned.dev/gitsign-gates: flux-system/composed-v5-0-0,flux-system/composed-machinery','policy-as-versioned.dev/gitsign-gates: flux-system/composed-v5-0-0,flux-system/composed-v6-0-0,flux-system/composed-v7-0-0,flux-system/composed-machinery')
old = '''        - { version: "5.0.0" }
        # v3.0.0 carries composed/policies/v5.0.0 only, and every machinery allow-list at that
        # tag admits ['5.0.0'] only. It was composed under platform v4.0.0, which retires policy
        # 4.0.0 (owner-instructed 2026-09-24). Every in-currency workload tuppence declares
        # claims 5.0.0 (Phase B, 2026-09-24). teller-stale in reset/workloads.yaml claims 1.0.0
        # on purpose; the orphan cage takes it.'''
new = '''        - { version: "5.0.0" }
        - { version: "6.0.0" }
        - { version: "7.0.0" }
        # The signed v4.0.0 tree carries all three versions, and its machinery admits exactly
        # this complete window. Current workload declarations claim 7.0.0; the deliberately
        # stale claim in reset/workloads.yaml remains subject to the orphan cage.'''
assert old in text
text = text.replace(old,new)
path.write_text(text)

(EVIDENCE/'tuppence-atomic-delivery-edit-checkpoint.json').write_text(json.dumps({'base':COMMIT,'branch':'delivery-stage2-atomic-20261004','paths':['gitops/flux-system/gotk-sync.yaml','inventory/PROVENANCE.json','gitops/composed/composed-set.yaml'],'remote_actions':False,'source_A_branch_preserved':True},indent=2)+'\n')
print('Prepared coupled apps/provenance/composed delivery declarations')
