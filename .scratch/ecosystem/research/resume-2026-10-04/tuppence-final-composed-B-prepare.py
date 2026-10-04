"""Move only the composed source to authentic released B; apps remain A."""
from pathlib import Path
import json
import subprocess

E = Path(__file__).parent
A = Path('/private/tmp/pavf-adopter-stage2-20261004-IEvZk7/tuppence-estate/tuppence')
B = 'dbaa026f6510fe5c0042f33f29081f3840ea59c3'
SOURCE_A = 'f575dc12de130c444d98a831de0ca21fd68b9c46'
def git(*args):
    return subprocess.check_output(['git','-C',str(A),*args])
release = json.loads((E/'tuppence-composition-B-authentic-release.json').read_text())
assert release['peeled_commit']==B and release['tag']=='v4.0.1'
assert all(release[k] is True for k in ('git_signature','rekor_entry','certificate_claims','final_composed_pointer_edits_may_begin'))
assert git('rev-parse','HEAD').decode().strip()==B
assert git('rev-parse','origin/main').decode().strip()==B
assert git('rev-parse','refs/tags/v4.0.1').decode().strip()==release['tag_object']
assert git('rev-parse','refs/tags/v4.0.1^{commit}').decode().strip()==B
assert not git('status','--porcelain','--untracked-files=all').strip()
git('switch','-c','delivery-stage2-composed-B-20261004',B)
p = A/'gitops/composed/composed-set.yaml'
text = p.read_text()
before = '''#   * the tag is v4.0.0, the same genuine Source A release as the apps source in
#     gitops/flux-system/gotk-sync.yaml. Its composed tree carries policies 5.0.0, 6.0.0 and 7.0.0.
#     The coupled self-pin, inventory binding, array and verification gates move in one reviewed
#     change; renovate.json tracks publisher parents rather than these self-pins.'''
after = '''#   * composed delivery uses the genuine v4.0.1 Composition B release, whose signed tree
#     binds the apps source and native inventory to Source A v4.0.0. Its complete policy window
#     is 5.0.0, 6.0.0 and 7.0.0. Apps and inventory stay bound to Source A; this reviewed pointer
#     moves composed delivery to B. Renovate tracks publisher parents rather than self-pins.'''
assert text.count(before)==1
text = text.replace(before,after)
before_ref = f'''    tag: v4.0.0
    commit: {SOURCE_A}
    # The resolved SHA of the genuine signed v4.0.0 Source A release (2026-10-04).'''
after_ref = f'''    tag: v4.0.1
    commit: {B}
    # The resolved SHA of the genuine signed v4.0.1 Composition B release (2026-10-04).'''
assert text.count(before_ref)==1
text = text.replace(before_ref,after_ref)
text = text.replace('# The signed v4.0.0 tree carries all three versions,', '# The signed v4.0.1 tree carries all three versions,')
p.write_text(text)
assert git('diff','--name-only').decode().splitlines()==['gitops/composed/composed-set.yaml']
print('Prepared genuine B pointer; apps and inventory remain A')
