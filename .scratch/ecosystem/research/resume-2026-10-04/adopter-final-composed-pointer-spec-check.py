"""Read-only source/object checks for a signed final composed-B pointer.

Authentic normal compose/verify/gate/run receipts need separate review. This
finite helper only reads local objects and writes the requested review receipt.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess

import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--org', required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--head', required=True)
    parser.add_argument('--base', help='Actual candidate parent; defaults to released B')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    day = Path(__file__).resolve().parent
    adopter = args.directory
    source_a = json.loads((day / (args.org + '-source-A-authentic-release.json')).read_text())
    source_b = json.loads((day / (args.org + '-composition-B-authentic-release.json')).read_text())
    def released_commit(release):
        return release['peeled_commit'] if 'peeled_commit' in release else release['commit']

    released_b = released_commit(source_b)
    base = args.base or released_b

    def git(*argv):
        return subprocess.check_output(['git', '-C', str(adopter), *argv])

    def obj(ref, path):
        return git('show', ref + ':' + path)

    def digest(data):
        return hashlib.sha256(data).hexdigest()

    assert args.head == git('rev-parse', 'HEAD').decode().strip()
    assert base == git('rev-parse', 'HEAD^').decode().strip()
    subprocess.run(['git', '-C', str(adopter), 'merge-base', '--is-ancestor',
                    released_b, base], check=True)
    assert not git('status', '--porcelain')
    subprocess.run(['git', '-C', str(adopter), 'verify-commit', args.head],
                   check=True, capture_output=True)
    paths = git('diff', '--name-only', base, args.head).decode().splitlines()
    assert set(paths) == {'composed/HEADER.yaml', 'gitops/composed/composed-set.yaml'}
    for release in (source_a, source_b):
        if 'signature' in release:
            signature = release['signature']
            assert all(signature[key] is True for key in ('Git', 'Rekor', 'certificate'))
            assert signature['exact_identity'] == (
                'https://github.com/policy-as-versioned-' + args.org + '/' + args.org
                + '/.github/workflows/cut-release.yml@refs/heads/main')
            assert signature['issuer'] == 'https://token.actions.githubusercontent.com'
        else:
            assert release['git_signature'] and release['rekor_entry'] and release['certificate_claims']
        live_flags = [release[key] for key in ('live_delivery_claimed', 'live_activation_claimed')
                      if key in release]
        if live_flags:
            assert all(value is False for value in live_flags)
        else:
            assert release['scope'] == (
                'Authentic approved Composition B signed release, no live observation claimed')
        ref = 'refs/tags/' + release['tag']
        assert git('rev-parse', ref).decode().strip() == release['tag_object']
        assert git('rev-parse', ref + '^{}').decode().strip() == released_commit(release)

    apps = list(yaml.safe_load_all(obj(args.head, 'gitops/flux-system/gotk-sync.yaml')))
    apps_repo = next(d for d in apps if d and d.get('kind') == 'GitRepository')
    assert apps_repo['spec']['ref'] == {'tag': source_a['tag'], 'commit': source_a['peeled_commit']}
    composed = list(yaml.safe_load_all(obj(args.head, 'gitops/composed/composed-set.yaml')))
    composed_repo = next(d for d in composed if d and d.get('kind') == 'GitRepository')
    assert composed_repo['spec']['ref'] == {'tag': source_b['tag'], 'commit': released_b}
    resources = next(d for d in composed if d and d.get('kind') == 'ResourceSet')
    assert resources['spec']['inputs'][0]['versions'] == [
        {'version': v} for v in ('5.0.0', '6.0.0', '7.0.0')]
    assert composed_repo['metadata']['annotations']['policy-as-versioned.dev/gitsign-gates'] == (
        'flux-system/composed-v5-0-0,flux-system/composed-v6-0-0,'
        'flux-system/composed-v7-0-0,flux-system/composed-machinery')
    old_header = yaml.safe_load(obj(base, 'composed/HEADER.yaml'))
    header = yaml.safe_load(obj(args.head, 'composed/HEADER.yaml'))
    fingerprint = header['comparison-inputs']['after']
    old_header['comparison-inputs'].pop('after')
    header['comparison-inputs'].pop('after')
    assert old_header == header
    assert header['declared-engine']['version'] == '1.18.2'

    tools = adopter.parent / 'platform-tools'
    assert subprocess.check_output(['git', '-C', str(tools), 'rev-parse', 'HEAD'],
                                   text=True).strip() == '703eff6aee959843c4160aa54fd03413f62858cc'
    spec = importlib.util.spec_from_file_location('spec_inventory', tools / 'wargamer/inventory.py')
    inventory_api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory_api)
    inventory = json.loads(obj(args.head, 'inventory/images.json'))
    provenance = json.loads(obj(args.head, 'inventory/PROVENANCE.json'))
    inventory_api.validate(adopter, inventory)
    assert provenance['apps_source']['tag'] == source_a['tag']
    assert provenance['apps_source']['commit'] == source_a['peeled_commit']
    assert provenance['apps_source']['tag_object'] == source_a['tag_object']
    assert obj(args.head, 'inventory/PROVENANCE.json') == obj(base, 'inventory/PROVENANCE.json')
    assert obj(args.head, 'inventory/images.json') == obj(base, 'inventory/images.json')
    assert digest(obj(args.head, 'inventory/images.json')) == provenance['inventory_sha256']
    for row in provenance['images']:
        raw = Path(row['raw_report'])
        if not raw.is_absolute():
            raw = day.parents[3] / raw
        data = raw.read_bytes()
        assert digest(data) == row['raw_report_sha256']
        trimmed = inventory_api.trim(row['requested_image'], json.loads(data), provenance['scanner']['version'])
        assert trimmed == next(x for x in inventory['images'] if x['image'] == row['requested_image'])
    result = {
        'source_checks': 'PASS', 'normal_receipt_review': 'pending',
        'institution': args.org, 'head': args.head,
        'tree': git('rev-parse', 'HEAD^{tree}').decode().strip(),
        'candidate_parent': base, 'base_B': released_b, 'source_A': source_a, 'source_B': source_b,
        'changed_paths': paths,
        'changed_file_sha256': {p: digest(obj(args.head, p)) for p in paths},
        'normal_SSH_signature': 'G', 'clean': True,
        'HEADER_only_delta': 'comparison-inputs.after', 'comparison_after': fingerprint,
        'apps_and_primary_provenance_A_preserved': True, 'primary_trim_equal': True,
        'served_images': inventory_api.served_images(adopter),
        'policy_versions': ['5.0.0', '6.0.0', '7.0.0'],
        'four_gitsign_gates_preserved': True, 'engine': '1.18.2',
        'reviewer_source_edits': False, 'reviewer_external_mutations': False,
    }
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('source_checks', 'head', 'tree', 'changed_paths')}, indent=2))


if __name__ == '__main__':
    main()
