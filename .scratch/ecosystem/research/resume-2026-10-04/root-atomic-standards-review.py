"""Independent root inspection of the exact DW/LU atomic candidates."""
from pathlib import Path
import hashlib
import json
import subprocess
import yaml

E = Path(__file__).parent
for name in ('driftwood', 'ludlow'):
    packet = json.loads((E/f'{name}-atomic-delivery-candidate.json').read_text())
    a = Path(packet['directory'])
    head, base = packet['head'], packet['base']
    def git(*args):
        return subprocess.check_output(['git', '-C', str(a), *args])
    def sha(data):
        return hashlib.sha256(data).hexdigest()
    def old(path):
        return git('show', base+':'+path)
    assert git('rev-parse', 'HEAD').decode().strip() == head
    assert git('rev-parse', 'HEAD^{tree}').decode().strip() == packet['tree']
    assert git('log', '-1', '--format=%G?').decode().strip() == 'G'
    assert not git('status', '--porcelain', '--untracked-files=all').strip()
    paths = git('diff', '--name-only', base, head).decode().splitlines()
    assert paths == ['composed/HEADER.yaml', 'gitops/composed/composed-set.yaml',
                     'gitops/flux-system/gotk-sync.yaml', 'inventory/PROVENANCE.json']
    file_hashes = {}
    for path in paths:
        data = (a/path).read_bytes()
        assert data == git('show', head+':'+path)
        file_hashes[path] = sha(data)
    before = yaml.safe_load(old('composed/HEADER.yaml'))
    after = yaml.safe_load((a/'composed/HEADER.yaml').read_text())
    before['comparison-inputs']['after'] = after['comparison-inputs']['after']
    assert before == after
    docs = list(yaml.safe_load_all((a/'gitops/composed/composed-set.yaml').read_text()))
    composed = next(d for d in docs if d['kind'] == 'GitRepository')
    apps = next(d for d in yaml.safe_load_all((a/'gitops/flux-system/gotk-sync.yaml').read_text()) if d['kind'] == 'GitRepository')
    assert apps['spec']['ref'] == composed['spec']['ref'] == {'tag':'v4.0.0', 'commit':base}
    assert 'verify' not in composed['spec']
    assert next(d for d in docs if d['kind']=='ResourceSet')['spec']['inputs'][0]['versions'] == [
        {'version':v} for v in ('5.0.0','6.0.0','7.0.0')]
    assert composed['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates'].split(',') == [
        'flux-system/composed-v5-0-0','flux-system/composed-v6-0-0','flux-system/composed-v7-0-0','flux-system/composed-machinery']
    prov = json.loads((a/'inventory/PROVENANCE.json').read_text())
    previous = json.loads(old('inventory/PROVENANCE.json'))
    assert {k:v for k,v in prov.items() if k!='apps_source'} == {k:v for k,v in previous.items() if k!='apps_source'}
    binding = prov['apps_source']
    assert binding['commit'] == base and binding['tag'] == 'v4.0.0'
    assert git('rev-parse','refs/tags/v4.0.0^{commit}').decode().strip() == base
    assert git('rev-parse','refs/tags/v4.0.0').decode().strip() == binding['tag_object']
    authentic = json.loads((E/f'{name}-source-A-authentic-release.json').read_text())
    assert authentic['tag_object'] == binding['tag_object']
    assert str(authentic['tlog_index']) == str(binding['signature']['tlog_index'])
    assert all(binding['signature'][k] is True for k in ('git','rekor','certificate_claims'))
    assert sha((a/'inventory/images.json').read_bytes()) == prov['inventory_sha256']
    for path in git('ls-tree','-r','--name-only',head).decode().splitlines():
        if path not in paths:
            assert git('show',head+':'+path) == old(path), path
    result = {'scope':'Root independent Standards review of actual committed atomic delivery bytes and final check receipts',
              'head':head,'base':base,'tree':packet['tree'],'source_clean':True,'SSH_signature':'G',
              'changed_paths':paths,'file_sha256':file_hashes,'hand_authored_diff_inspected':True,
              'native_inventory_and_primary_metadata_preserved':True,'genuine_source_A_provenance_matches_root_crypto_receipt':True,
              'composed_HEADER_fingerprint_only':True,'all_other_source_bytes_preserved':True,
              'packet_sha256':sha((E/f'{name}-atomic-delivery-candidate.json').read_bytes()),
              'hard_findings':[],'result':'PASS','publication_requires':'Exact Spec PASS plus actual ordinary PR CI and matching-head App review'}
    (E/f'{name}-atomic-delivery-root-standards-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(name, head, 'Standards PASS', flush=True)
