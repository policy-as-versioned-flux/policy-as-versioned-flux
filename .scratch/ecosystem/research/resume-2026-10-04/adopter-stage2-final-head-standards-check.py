"""Read immutable source-A blobs and exercise the actual owned-schema helper block."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

ROOT = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
EVIDENCE = ROOT / '.scratch/ecosystem/research/resume-2026-10-04'
PLATFORM = ROOT / '.estate-publish/platform'
TOOLS = '703eff6aee959843c4160aa54fd03413f62858cc'
HUB = '5bc47331a536476f3580542be794908f5053f816'
EXPECTED = {
    'driftwood': 'eac40457ffb4b593dfbe17015c525db3f0914f5f',
    'tuppence': 'd1dbe766e09bb8112efa609836af0aa95cbe0ee4',
    'ludlow': '926d6b38384fd9b532305c668313920ff943653a',
}
EXPORT = json.loads((EVIDENCE / 'adopter-stage2-final-source-A-candidates.json').read_text())
OLD = json.loads((EVIDENCE / 'adopter-stage2-final-source-standards-review.json').read_text())
RESTORED = json.loads((EVIDENCE / 'adopter-stage2-corrected-standards-review.json').read_text())
PRODUCERS = json.loads((EVIDENCE / 'adopter-stage2-final-producers.json').read_text())
EXTENSIONS = {
    'rests_on_grade': {'type': 'integer', 'enum': [1, 2, 3]},
    'valuation': {
        'type': 'object',
        'required': ['amount', 'currency', 'native_amount', 'native_currency', 'party_fact', 'fx'],
        'properties': {
            'amount': {'type': 'number'}, 'currency': {'type': 'string'},
            'native_amount': {'type': 'number'}, 'native_currency': {'type': 'string'},
            'party_fact': {'type': 'string'}, 'fx': {'type': ['object', 'null']},
        },
        'additionalProperties': False,
    },
}


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def blob(repo: Path, ref: str, path: str) -> bytes:
    return git(repo, 'show', f'{ref}:{path}')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


CANONICAL_BYTES = blob(PLATFORM, TOOLS, 'feeds/forward-intel.payload.schema.json')
CANONICAL = json.loads(CANONICAL_BYTES)
result: dict = {
    'observed_at': datetime.now(timezone.utc).isoformat(),
    'scope': 'Independent read-only exact source-A review; no release, clock or activation claim',
    'canonical_schema_sha256': digest(CANONICAL_BYTES),
    'frozen_publisher_trees': {},
    'adopters': {},
}
for version in ['5.0.0', '6.0.0']:
    path = 'distribution/policies/v' + version
    frozen = git(PLATFORM, 'rev-parse', f'policy/v{version}:{path}').decode().strip()
    current = git(PLATFORM, 'rev-parse', f'{TOOLS}:{path}').decode().strip()
    assert frozen == current, version
    result['frozen_publisher_trees'][version] = {'tree': current, 'equals_authentic_version_tag': True}

for org, head in EXPECTED.items():
    export = EXPORT[org]
    repo = Path(export['directory'])
    before = OLD['adopters'][org]['head']
    baseline = export['base']
    assert git(repo, 'rev-parse', 'HEAD').decode().strip() == head
    assert git(repo, 'rev-parse', head + '^{tree}').decode().strip() == export['tree']
    assert not git(repo, 'status', '--porcelain')
    signature = git(repo, 'show', '-s', '--format=%G?', head).decode().strip()
    assert signature == 'G', (org, signature)
    entry: dict = {'head': head, 'tree': export['tree'], 'signature': signature, 'worktree_clean': True}
    critical = {p: digest(blob(repo, head, p)) for p in export['critical_file_sha256']}
    assert critical == export['critical_file_sha256'], org
    entry['critical_blob_sha256'] = critical
    restored_apps = [x['path'] for x in RESTORED['adopters'][org]['upstream_byte_checks'] if x['path'].startswith('apps/')]
    for p in restored_apps:
        assert blob(repo, head, p) == blob(repo, baseline, p), (org, p)
    entry['published_app_sources_preserved'] = restored_apps
    inherited = [x['path'] for x in RESTORED['adopters'][org]['upstream_byte_checks'] if not x['path'].startswith('apps/')]
    entry['upstream_only_paths_retained'] = [
        {'path': p, 'equals_upstream_bytes': blob(repo, head, p) == blob(repo, baseline, p)} for p in inherited
    ]
    for p in ['drift/samples.jsonl', 'observations/twin-sweep.jsonl']:
        assert blob(repo, head, p) == blob(repo, baseline, p), (org, p)
    entry['historical_clock_records_byte_exact'] = True
    for p in ['inventory/images.json', 'inventory/PROVENANCE.json', 'gitops/engine/kyverno.yaml']:
        assert blob(repo, head, p) == blob(repo, before, p), (org, p)
    inventory = json.loads(blob(repo, head, 'inventory/PROVENANCE.json'))
    assert inventory['apps_source']['commit'] == baseline and inventory['apps_source']['tag'] == 'v3.0.1'
    assert digest(blob(repo, head, 'inventory/images.json')) == inventory['inventory_sha256']
    for image in inventory['images']:
        assert digest((ROOT / image['raw_report']).read_bytes()) == image['raw_report_sha256']
    entry['inventory_bootstrap_and_primary_hashes_unchanged'] = True
    engine = yaml.safe_load(blob(repo, head, 'gitops/engine/kyverno.yaml'))
    assert engine['version'] == '1.18.2'
    entry['engine'] = engine['version']
    party = yaml.safe_load(blob(repo, head, 'party.yaml'))
    assert party['appetite']['pricing_threshold'] == 3
    pin = yaml.safe_load(blob(repo, head, 'twin/PIN.yaml'))
    assert pin['hub_commit'] == HUB and pin['tag_cut'] is False
    entry['published_hub_pin'] = pin
    pins: dict = {}
    for rel, publisher in [('.github/platform-tools-pin.yaml', 'platform-tools'),
                           ('gitops/platform/platform-pin.yaml', 'platform'),
                           ('gitops/flux-system/gotk-sync-feeds.yaml', 'feeds'),
                           ('gitops/flux-system/gotk-sync-fx.yaml', 'feeds'),
                           ('gitops/flux-system/gotk-sync.yaml', org)]:
        docs = list(yaml.safe_load_all(blob(repo, head, rel)))
        ref = next(x for x in docs if x and x.get('kind') == 'GitRepository')['spec']['ref']
        publisher_repo = repo if publisher == org else repo.parent / publisher
        target = git(publisher_repo, 'rev-parse', ref['tag'] + '^{commit}').decode().strip()
        assert target == ref['commit'], (org, rel)
        pins[rel] = {'ref': ref, 'tag_object': git(publisher_repo, 'rev-parse', ref['tag']).decode().strip(), 'pair_matches': True}
    entry['pins'] = pins
    assert pins['gitops/flux-system/gotk-sync-feeds.yaml']['ref']['commit'] == '974e73514e0d8d4cad2e6906acf51d1cc27028b3'
    assert git(repo.parent / 'feeds', 'rev-parse', 'HEAD').decode().strip() == pins['gitops/flux-system/gotk-sync-feeds.yaml']['ref']['commit']
    if org == 'ludlow':
        assert pins['gitops/flux-system/gotk-sync-fx.yaml']['ref']['commit'] == '8c84a66951ce89834f33e008380b2c47f054b7c0'
        assert pins['gitops/flux-system/gotk-sync-fx.yaml']['tag_object'] == 'f6edadce94b98a01479a517a1babda92ce8b2243'
    schema = json.loads(blob(repo, head, 'twin/forward-intel/payload.schema.json'))
    base = copy.deepcopy(schema)
    for key, expected in EXTENSIONS.items():
        assert base['properties'].pop(key) == expected
        assert key not in base['required']
    assert base == CANONICAL, org
    helper = blob(repo, head, 'verify-twin-overlay.sh').decode()
    python_part = helper.split("<<'PY'\n", 1)[1].split('\nPY\n', 1)[0]
    syntax = ast.parse(python_part)
    block = next(node for node in syntax.body if isinstance(node, ast.If) and isinstance(node.test, ast.Call)
                 and ast.unparse(node.test) == 'os.path.isfile(CANONICAL)')
    actual = compile(ast.Module(body=[block], type_ignores=[]), 'committed-schema-helper', 'exec')
    variants = {'canonical_plus_owned': copy.deepcopy(schema)}
    variants['base_property_removed'] = copy.deepcopy(schema)
    variants['base_property_removed']['properties'].pop(next(iter(CANONICAL['properties'])))
    variants['base_requirement_removed'] = copy.deepcopy(schema)
    variants['base_requirement_removed']['required'].pop()
    variants['base_type_changed'] = copy.deepcopy(schema)
    variants['base_type_changed']['properties'][next(iter(CANONICAL['properties']))] = {'type': 'null'}
    variants['closed_base_opened'] = copy.deepcopy(schema)
    variants['closed_base_opened']['additionalProperties'] = True
    variants['unknown_owned_property'] = copy.deepcopy(schema)
    variants['unknown_owned_property']['properties']['unapproved'] = {'type': 'number'}
    variants['optional_addition_required'] = copy.deepcopy(schema)
    variants['optional_addition_required']['required'].append('valuation')
    variants['extension_grade_widened'] = copy.deepcopy(schema)
    variants['extension_grade_widened']['properties']['rests_on_grade']['enum'].append(5)
    verdicts = {}
    with tempfile.TemporaryDirectory(prefix='pavf-schema-review-') as tmp:
        canonical_path = Path(tmp) / 'canonical.json'; canonical_path.write_bytes(CANONICAL_BYTES)
        owned_path = Path(tmp) / 'owned.json'
        for name, variant in variants.items():
            owned_path.write_text(json.dumps(variant)); observed = []
            env = {'json': json, 'os': __import__('os'), 'CANONICAL': str(canonical_path), 'VENDORED': str(owned_path),
                   'out': lambda status, message: observed.append(status)}
            exec(actual, env)
            expected_status = 'PASS' if name == 'canonical_plus_owned' else 'FAIL'
            assert observed == [expected_status], (org, name, observed)
            verdicts[name] = observed[0]
    entry['actual_helper_negative_cases'] = verdicts
    major = '2' if org == 'driftwood' else '1'
    feed_path = f'twin/forward-intel/v{major}/feed.json'
    feed_bytes = blob(repo, head, feed_path); feed = json.loads(feed_bytes)
    assert not list(Draft7Validator(schema).iter_errors(feed['payload']))
    assert feed['payload']['rests_on_grade'] == 3
    assert feed['payload']['valuation'] == PRODUCERS['adopters'][org]['valuation']
    assert any(x['path'] == feed_path and x['sha256'] == digest(feed_bytes) for x in PRODUCERS['adopters'][org]['generated'])
    entry['committed_feed_sha256_matches_measured_producer'] = digest(feed_bytes)
    entry['rests_on_grade'] = 3
    entry['valuation'] = feed['payload']['valuation']
    if org == 'ludlow':
        fx = feed['payload']['valuation']['fx']
        assert fx['period'] == '2025-12' and fx['valuation_date'] == party['size']['as_of'] == '2025-12-31'
        assert fx['from_rate'] == 1.3126 and fx['version'] == '2.0.0'
        assert math.isclose(feed['payload']['valuation']['amount'], 8475000000 / 1.3126)
    else:
        assert feed['payload']['valuation']['fx'] is None
    entry['schema_validation'] = 'PASS'
    invalid = copy.deepcopy(feed['payload']); invalid['rests_on_grade'] = 5
    assert list(Draft7Validator(schema).iter_errors(invalid))
    invalid = copy.deepcopy(feed['payload']); invalid['valuation']['amount'] = 'invented'
    assert list(Draft7Validator(schema).iter_errors(invalid))
    entry['invalid_grade_and_nonmoney_rejected'] = True
    assert blob(repo, head, 'gitops/composed/composed-set.yaml') == blob(repo, baseline, 'gitops/composed/composed-set.yaml')
    entry['served_version_array_still_historical'] = True
    assert 'cloud' not in yaml.safe_load(blob(repo, head, 'gitops/apps/kustomization.yaml'))['resources']
    entry['cloud_route_not_active'] = True
    acceptance = yaml.safe_load(blob(repo, head, 'accepted-majors/platform-7.0.0.yaml'))
    assert str(acceptance['version']) == '7.0.0' and 'delegated' in acceptance['accepted_by']
    assert "you tell me, you control them all, you don't need me to answer" in acceptance['accepted_by']
    entry['delegated_major_acceptance_preserved'] = True
    changed = git(repo, 'diff', '--name-only', baseline, head).decode().splitlines()
    patterns = {
        'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
        'github_token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
        'aws_access_id': re.compile(rb'\bAKIA[A-Z0-9]{16}\b'),
    }
    matches = []
    for rel in changed:
        try:
            body = blob(repo, head, rel)
        except subprocess.CalledProcessError:
            continue
        matches += [{'path': rel, 'pattern': name} for name, pattern in patterns.items() if pattern.search(body)]
    assert not matches, (org, matches)
    entry['changed_source_high_confidence_secret_matches'] = matches
    result['adopters'][org] = entry

result['status'] = 'PASS: exact source-A Standards review; root full-window gates and normal publication remain separate'
result['tests_scope'] = 'Actual committed schema-comparison block: 3 positive +21 negative cases; actual payloads and 6 invalid payloads; no broad test rerun'
(EVIDENCE / 'adopter-stage2-final-head-standards-review.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'heads': EXPECTED, 'schema_cases': result['tests_scope'],
                  'preserved_app_sources': sum(len(x['published_app_sources_preserved']) for x in result['adopters'].values()),
                  'retained_upstream_only_paths': sum(len(x['upstream_only_paths_retained']) for x in result['adopters'].values())}, indent=2))
