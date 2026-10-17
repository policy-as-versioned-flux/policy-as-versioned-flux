#!/usr/bin/env python3
"""Cloud package delivery and spec-only KinD admission, with a citable trigger.

Offline replay is a separate self-proof. Default exits 3 until a modern,
signed e2e4 clock record and a signed tuppence tag reaching the cloud paths
exist. It never contacts a cluster before those preconditions. No AWS or
provider-authentication code exists here; server dry-run never reconciles.
"""
from __future__ import annotations
import argparse
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
PLATFORM = ROOT / '.estate-clone/platform'
TUPPENCE = ROOT / '.estate-clone/tuppence'
PACKAGE = PLATFORM / 'implementations/cloud'
LABEL = 'policy-as-versioned.dev/policy-version'
CLOUD_IDENTITY = r'^https://github\.com/policy-as-versioned-platform/platform/\.github/workflows/cloud-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'
TUPPENCE_IDENTITY = r'^https://github\.com/policy-as-versioned-tuppence/tuppence/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$'


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, 'cloud module could not be loaded: ' + str(path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def declarations() -> tuple[dict, list[dict]]:
    package = yaml.safe_load((PACKAGE / 'package.yaml').read_text())
    assert package['version'] == (PACKAGE / 'VERSION').read_text().strip()
    party = yaml.safe_load((PLATFORM / 'party.yaml').read_text())
    assert any(row['kind'] == 'implementations' and row['path'] == 'implementations/cloud' for row in party['publishes'])
    members = [yaml.safe_load((PACKAGE / path).read_text()) for path in package['members']]
    assert len(members) == 4 and sum(d['kind'] == 'MutatingPolicy' for d in members) == 2
    assert all(d['spec'].get('validationActions', ['Audit']) == ['Audit'] for d in members), 'cloud has a Deny-shaped gate'
    dials = yaml.safe_load((PACKAGE / 'crossplane-dials.yaml').read_text())['tiers']
    assert list(dials) == ['baseline', 'restricted', 'quarantine', 'isolated']
    retention = [row['backupRetentionPeriod'] for row in dials.values()]
    assert retention == sorted(retention) and all(1 <= value <= 35 for value in retention)
    for row in dials.values():
        assert row['publiclyAccessible'] is False and row['storageEncrypted'] is True
    cd = json.loads((PACKAGE / 'component-definition.json').read_text())['component-definition']
    assert cd['metadata']['version'] == package['version']
    claims = cd['components'][0]['control-implementations'][0]['implemented-requirements']
    assert {r['control-id'] for r in claims} == {'cp-10', 'sc-28'}
    assert {r['props'][0]['value'] for r in claims} <= {d['metadata']['name'] for d in members}
    workload = [d for d in yaml.safe_load_all((TUPPENCE / 'gitops/cloud/claims.yaml').read_text()) if d]
    assert {d['kind'] for d in workload} == {'Instance', 'BucketServerSideEncryptionConfiguration'}
    versions = next(d for d in yaml.safe_load_all((TUPPENCE / 'gitops/composed/composed-set.yaml').read_text()) if d and d['kind'] == 'ResourceSet')['spec']['inputs'][0]['versions']
    served = {row['version'] for row in versions}
    for doc in workload:
        assert doc['metadata']['namespace'] == 'tuppence' and doc['metadata']['labels'][LABEL] in served
        assert 'mycompany.com/policy-version' not in doc['metadata']['labels']
        assert 'providerConfigRef' not in doc['spec']
    routes = list(yaml.safe_load_all((TUPPENCE / 'gitops/cloud/cloud-delivery.yaml').read_text()))
    assert [d['metadata']['name'] for d in routes] == ['crossplane-crds', 'cloud-policies', 'cloud-claims']
    assert all(d['spec']['sourceRef'] == {'kind': 'GitRepository', 'name': 'tuppence-composed'} for d in routes)
    assert routes[1]['spec']['dependsOn'][0]['name'] == 'crossplane-crds'
    assert routes[2]['spec']['dependsOn'] == [{'name': 'cloud-policies'}] and routes[2]['spec']['wait'] is False
    return package, routes


def run(*args: str, data: str | None = None) -> dict:
    command = ['kubectl', '--context', os.environ.get('CLOUD_PLANE_CONTEXT', 'kind-tuppence'), *args]
    completed = subprocess.run(command, input=data, capture_output=True, text=True, timeout=30)
    if completed.returncode:
        raise ValueError('KinD admission command failed: ' + completed.stderr.strip())
    return json.loads(completed.stdout)


def declared_equal(expected, observed) -> bool:
    """Compare declared fields; live server defaults are not source drift."""
    if isinstance(expected, dict):
        return isinstance(observed, dict) and all(key in observed and declared_equal(value, observed[key]) for key, value in expected.items())
    if isinstance(expected, list):
        return isinstance(observed, list) and len(expected) == len(observed) and all(declared_equal(left, right) for left, right in zip(expected, observed))
    return type(expected) is type(observed) and expected == observed


def admission(routes: list[dict], source_pin: dict, package: Path) -> None:
    context = os.environ.get('CLOUD_PLANE_CONTEXT', 'kind-tuppence')
    if not context.startswith('kind-'):
        raise ValueError('cloud proof is KinD-only')
    source = run('get', 'gitrepository', 'tuppence-composed', '-n', 'flux-system', '-o', 'json')
    assert any(c['type'] == 'Ready' and c['status'] == 'True' for c in source['status']['conditions'])
    assert source['spec']['url'] == source_pin['spec']['url'], 'live cloud source URL differs from its publisher declaration'
    assert source['spec']['ref'] == source_pin['spec']['ref'], 'live cloud source differs from its immutable declaration'
    assert not source['spec'].get('verify'), 'a second OpenPGP/SSH signer is not the gitsign proof'
    annotations = source['metadata'].get('annotations', {})
    expected_annotations = source_pin['metadata']['annotations']
    prefix = 'policy-as-versioned.dev/'
    assert annotations.get(prefix + 'gitsign-verified') == 'true', 'cloud source has no true source-boundary signature verdict'
    assert annotations.get(prefix + 'gitsign-identity-regexp') == expected_annotations[prefix + 'gitsign-identity-regexp']
    assert annotations.get(prefix + 'gitsign-issuer') == expected_annotations[prefix + 'gitsign-issuer']
    gates = set(annotations.get(prefix + 'gitsign-gates', '').split(','))
    assert {f'flux-system/{route["metadata"]["name"]}' for route in routes} <= gates, 'cloud routes escape the source-verification gates'
    revision = source['status']['artifact']['revision']
    assert revision.endswith(source_pin['spec']['ref']['commit'])
    pin = source_pin['spec']['ref']['commit']
    def pinned(path: str) -> str:
        return subprocess.check_output(['git', '-C', str(TUPPENCE), 'show', f'{pin}:{path}'], text=True)
    policy_path = routes[1]['spec']['path'].removeprefix('./')
    membership = yaml.safe_load(pinned(policy_path + '/kustomization.yaml'))
    for filename in membership['resources']:
        doc = yaml.safe_load(pinned(policy_path + '/' + filename))
        resource = doc['kind'].removesuffix('Policy').lower() + 'policies.policies.kyverno.io'
        live = run('get', resource, doc['metadata']['name'], '-o', 'json')
        assert declared_equal(doc['spec'], live['spec']), 'live cloud body differs from the signed composed member'
        status = live.get('status')
        condition_status = status.get('conditionStatus') if isinstance(status, dict) else None
        if not isinstance(condition_status, dict) or condition_status.get('ready') is not True:
            raise ValueError(f'live cloud policy {resource}/{doc["metadata"]["name"]} is not ready')
    names = ['instances.rds.aws.m.upbound.io', 'bucketserversideencryptionconfigurations.s3.aws.m.upbound.io']
    for name in names:
        crd = run('get', 'crd', name, '-o', 'json')
        assert any(c['type'] == 'Established' and c['status'] == 'True' for c in crd['status']['conditions'])
        expected = yaml.safe_load(pinned(routes[0]['spec']['path'].removeprefix('./') + '/' + name + '.yaml'))
        assert declared_equal(expected['spec'], crd['spec']), 'live cloud CRD differs from its signed vendor schema'
    for route in routes:
        live = run('get', 'kustomization', route['metadata']['name'], '-n', 'flux-system', '-o', 'json')
        assert any(c['type'] == 'Ready' and c['status'] == 'True' for c in live['status']['conditions'])
        assert live['status']['lastAppliedRevision'] == revision, 'cloud route has not applied the pinned source revision'
        assert live['status'].get('inventory', {}).get('entries'), 'cloud route has no Flux inventory'
    workload_path = routes[2]['spec']['path'].removeprefix('./') + '/claims.yaml'
    workload = [doc for doc in yaml.safe_load_all(pinned(workload_path)) if doc]
    declared_workload = [doc for doc in yaml.safe_load_all((TUPPENCE / 'gitops/cloud/claims.yaml').read_text()) if doc]
    assert workload == declared_workload, 'signed cloud workload differs from the current declared incumbent lift'
    namespace = run('get', 'namespace', 'tuppence', '-o', 'json')
    labels = namespace['metadata']['labels']
    assert labels.get('policy-as-versioned.dev/governed') == 'true'
    tier = labels.get('posture.acme.io/tier', 'isolated')
    table = yaml.safe_load((package / 'crossplane-dials.yaml').read_text())['tiers']
    tier = tier if tier in table else 'isolated'
    sys.path.insert(0, str(package))
    replay = module('cloud_replay', package / 'replay.py')
    # The actual three lifted resources are observed as well as the bottom-rung
    # probes below. An UPDATE dry-run can judge names that Flux already created.
    for before in workload:
        live = run('get', before['kind'], before['metadata']['name'], '-n', 'tuppence', '-o', 'json')
        assert declared_equal(before['metadata']['labels'], live['metadata']['labels'])
        provider = before['spec']['forProvider']
        row = table[tier]
        expected = {'tier': tier, 'multiAz': row['multiAz'] or provider.get('multiAz', False),
                    'backupRetentionPeriod': max(row['backupRetentionPeriod'], provider.get('backupRetentionPeriod', 0)),
                    'sseAlgorithm': 'AES256'}
        case = {'name': before['metadata']['name'], 'kind': before['kind'], 'expected': expected}
        replay.check_fields(before, live, case)
        after = run('apply', '--server-side', '--force-conflicts', '--dry-run=server', '-f', '-', '-o', 'json', data=yaml.safe_dump(before))
        replay.check_fields(before, after, case)
    for kind in ('Instance', 'BucketServerSideEncryptionConfiguration'):
        for claim in ('5.0.0', None, '99.0.0'):
            actual_tier = tier if claim == '5.0.0' else 'isolated'
            row = table[actual_tier]
            expected = {'tier': actual_tier, 'multiAz': row['multiAz'],
                        'backupRetentionPeriod': row['backupRetentionPeriod'], 'sseAlgorithm': 'AES256'}
            case = {'name': 'cloud-admission-' + ('rds' if kind == 'Instance' else 's3'),
                    'kind': kind, 'tier': tier, 'claim': claim, 'expected': expected}
            before = replay.resource(case)
            before['metadata']['namespace'] = 'tuppence'
            after = run('create', '--dry-run=server', '-f', '-', '-o', 'json', data=yaml.safe_dump(before))
            replay.check_fields(before, after, case)
    print('LIMIT: server dry-run judged CR specs; no AWS resource or reconciliation was observed; isolated carries service dials, not a claim of AWS reach isolation')


def verify_tag(repository: Path, tag: str, commit: str, identity: str) -> None:
    resolved = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', tag + '^{commit}'], text=True).strip()
    if resolved != commit:
        raise ValueError('cloud proof tag and immutable commit disagree')
    verified = subprocess.run(['gitsign', 'verify-tag', tag,
                               '--certificate-identity-regexp=' + identity,
                               '--certificate-oidc-issuer=https://token.actions.githubusercontent.com'],
                              cwd=repository, env=dict(os.environ, GITSIGN_REKOR_MODE='offline'),
                              capture_output=True, text=True, timeout=30)
    if verified.returncode:
        raise ValueError('cloud proof tag failed identity-pinned offline signature verification')


def cloud_parent(source: dict, destination: Path) -> tuple[dict, Path]:
    """Use the source package the signed composed artefact actually names."""
    pin = source['spec']['ref']
    if source['spec']['url'].removesuffix('.git').rstrip('/') != 'https://github.com/policy-as-versioned-tuppence/tuppence':
        raise ValueError('cloud composed source URL names a different publisher')
    if not re.fullmatch(r'v\d+\.\d+\.\d+', pin['tag']) or not re.fullmatch(r'[0-9a-f]{40}', pin['commit']):
        raise ValueError('cloud composed source requires an exact tag and full commit')
    annotations = source['metadata']['annotations']
    if annotations['policy-as-versioned.dev/gitsign-identity-regexp'] != TUPPENCE_IDENTITY or annotations['policy-as-versioned.dev/gitsign-issuer'] != 'https://token.actions.githubusercontent.com':
        raise ValueError('cloud source declares a different signer')
    gates = set(annotations['policy-as-versioned.dev/gitsign-gates'].split(','))
    if not {'flux-system/crossplane-crds', 'flux-system/cloud-policies', 'flux-system/cloud-claims'} <= gates:
        raise ValueError('cloud routes are absent from the composed source signature gates')
    verify_tag(TUPPENCE, pin['tag'], pin['commit'], TUPPENCE_IDENTITY)
    raw = subprocess.check_output(['git', '-C', str(TUPPENCE), 'show', pin['commit'] + ':composed/CLOUD-PARENT.json'], text=True)
    parent = json.loads(raw)
    if (parent.get('party'), parent.get('kind'), parent.get('name'), parent.get('path')) != ('platform', 'implementations', 'cloud', 'implementations/cloud'):
        raise ValueError('cloud parent receipt names a different package')
    if not re.fullmatch(r'cloud/v\d+\.\d+\.\d+', parent['tag']) or not re.fullmatch(r'[0-9a-f]{40}', parent['sha']) or parent.get('signature_identity') != CLOUD_IDENTITY:
        raise ValueError('cloud parent receipt has no exact signed source')
    verify_tag(PLATFORM, parent['tag'], parent['sha'], CLOUD_IDENTITY)
    archive = subprocess.check_output(['git', '-C', str(PLATFORM), 'archive', parent['sha'], 'implementations/cloud'])
    with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
        tree.extractall(destination, filter='data')
    package = destination / 'implementations/cloud'
    if (package / 'VERSION').read_text().strip() != parent['tag'].removeprefix('cloud/v'):
        raise ValueError('cloud package VERSION disagrees with its tag')
    return parent, package


def selfcheck() -> None:
    declarations()
    assert declared_equal({'false': False, 'nested': [1]}, {'false': False, 'nested': [1], 'default': 'x'})
    assert not declared_equal({'false': False}, {'false': 0})
    assert not declared_equal({'nested': [1]}, {'nested': [1, 2]})
    trigger = module('cloud_trigger', PACKAGE / 'trigger.py')
    with tempfile.TemporaryDirectory(prefix='cloud-trigger-selfcheck-') as tmp:
        directory = Path(tmp)
        (directory / 'captures').mkdir()
        metadata = {'id': 151000, 'head_sha': 'a' * 40, 'path': '.github/workflows/truth.yml', 'status': 'completed'}
        truth = 'TRUTH 2026-10-03T12:00Z run=151000 hub=aaaaaaa units=[p=1] pass=1 fail=0 skip=0 excluded=0 total=1 ceiling=1'
        output = trigger.CHECK + '  PASS\n' + truth + '\n'
        (directory / 'run_metadata.json').write_text(json.dumps(metadata))
        (directory / 'truth.txt').write_text(output)
        (directory / 'captures' / trigger.CAPTURE).write_text('PASS: observed signed-source reconciliation\n')
        assert trigger.check(directory)['run'] == 151000
        for changed in (output.replace('  PASS', '  SKIP'), output + truth + '\n', output.replace(' units=', ' fixture=1 units='), output.replace('hub=aaaaaaa', 'hub=bbbbbbb')):
            (directory / 'truth.txt').write_text(changed)
            try:
                trigger.check(directory)
            except ValueError:
                pass
            else:
                raise AssertionError('false trigger was accepted')
        (directory / 'truth.txt').write_text(output)
        (directory / 'captures' / trigger.CAPTURE).write_text('SKIP: no cluster\n')
        try:
            trigger.check(directory)
        except ValueError:
            pass
        else:
            raise AssertionError('SKIP capture was accepted')
    print('PASS: cloud selfcheck fixtures reject missing, duplicate, local/fixture and false step-4 triggers; declarations are coherent; no live admission claimed')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selfcheck', action='store_true')
    parser.add_argument('--preflight', action='store_true', help='Check signed delivery prerequisites without contacting a cluster')
    args = parser.parse_args()
    try:
        if args.selfcheck:
            selfcheck()
            return 0
        _, routes = declarations()
        trigger = module('cloud_trigger', PACKAGE / 'trigger.py').find(ROOT)
        if trigger is None:
            print('SKIP: cloud plane waits for a citable e2e step 4 PASS on its registered question (tickets 157 and 161); offline cloud replay is a separate self-proof')
            return 3
        source = next(d for d in yaml.safe_load_all((TUPPENCE / 'gitops/composed/composed-set.yaml').read_text()) if d and d['kind'] == 'GitRepository')
        pin = source['spec']['ref']['commit']
        for route in routes:
            path = route['spec']['path'].removeprefix('./') + '/kustomization.yaml'
            result = subprocess.run(['git', '-C', str(TUPPENCE), 'cat-file', '-e', f'{pin}:{path}'], capture_output=True)
            if result.returncode:
                print('SKIP: cloud plane waits for tuppence\'s signed composed tag to carry all cloud delivery paths')
                return 3
        with tempfile.TemporaryDirectory(prefix='cloud-proof-source-') as tmp:
            parent, package = cloud_parent(source, Path(tmp))
            if args.preflight:
                print(f'PASS: cloud admission prerequisites are signed and published at {parent["sha"]}; no cluster observation claimed')
                return 0
            admission(routes, source, package)
        print(f'PASS: cloud claims admitted on KinD from tuppence composed delivery after signed e2e4 trigger {trigger["record_commit"]}')
        return 0
    except (AssertionError, ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print('FAIL: cloud plane: ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
