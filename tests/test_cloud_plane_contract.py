"""Local call-site proofs of cloud readiness and hosted-clock selection; no live claim."""
from __future__ import annotations

import ast
import copy
import importlib.util
import io
import json
from contextlib import redirect_stderr, redirect_stdout
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('cloud_contract_reader', ROOT / 'verify/cloud-plane/cloud_plane.py')
assert SPEC is not None and SPEC.loader is not None
cloud = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cloud)

# Actual prior 1.18.2 status capture SHA2565bd35e09e3fe6432f17d8125e02999c75ad9a98123a08f4e46e940280a08c96e.
# Pinned install.yaml SHA2563dcd43eaf11f0719084217148cd0c82a8fa49faa9b1a783ea5bea2cf84041bda
# declares this shape for both policy kinds and serves it on v1/v1alpha1/v1beta1.
READY = {'conditionStatus': {'conditions': [
    {'lastTransitionTime': '2026-10-03T14:38:40Z', 'message': 'Webhook configured.',
     'reason': 'Succeeded', 'status': 'True', 'type': 'WebhookConfigured'},
    {'lastTransitionTime': '2026-10-03T14:38:40Z', 'message': 'Policy is ready for reporting.',
     'reason': 'Succeeded', 'status': 'True', 'type': 'RBACPermissionsGranted'}],
    'message': '', 'ready': True}, 'generated': False}


class ReachedCRDGate(Exception):
    """The local transport stops after the actual policy readiness reads."""


class CloudReadiness(unittest.TestCase):
    def observe(self, status, *, omit_status=False, wrong_body=False):
        prefix = 'policy-as-versioned.dev/'
        names = ['crossplane-crds', 'cloud-policies', 'cloud-claims']
        routes = [{'metadata': {'name': name}, 'spec': {'path': './fixture/' + name}} for name in names]
        pin = {'metadata': {'annotations': {
            prefix + 'gitsign-identity-regexp': cloud.TUPPENCE_IDENTITY,
            prefix + 'gitsign-issuer': 'https://token.actions.githubusercontent.com',
            prefix + 'gitsign-gates': ','.join('flux-system/' + name for name in names)}},
            'spec': {'url': 'https://github.com/policy-as-versioned-tuppence/tuppence',
                     'ref': {'tag': 'v1.0.0', 'commit': 'a' * 40}}}
        source = copy.deepcopy(pin)
        source['metadata']['annotations'][prefix + 'gitsign-verified'] = 'true'
        source['status'] = {'conditions': [{'type': 'Ready', 'status': 'True'}],
                            'artifact': {'revision': 'v1.0.0@sha1:' + 'a' * 40}}
        docs = [{'apiVersion': 'policies.kyverno.io/v1', 'kind': kind,
                 'metadata': {'name': name}, 'spec': {'failurePolicy': 'Fail'}}
                for kind, name in [('ValidatingPolicy', 'fixture-validate'), ('MutatingPolicy', 'fixture-mutate')]]
        files = {'fixture/cloud-policies/kustomization.yaml': {'resources': ['validate.yaml', 'mutate.yaml']},
                 'fixture/cloud-policies/validate.yaml': docs[0], 'fixture/cloud-policies/mutate.yaml': docs[1]}
        def pinned(command, **kwargs):
            self.assertEqual(command[:4], ['git', '-C', '/local-fixture/tuppence', 'show'])
            ref, path = command[4].split(':', 1)
            self.assertEqual(ref, 'a' * 40)
            return yaml.safe_dump(files[path])
        def transport(*args, **kwargs):
            if args[:2] == ('get', 'gitrepository'):
                return source
            if args[1] in ('validatingpolicies.policies.kyverno.io', 'mutatingpolicies.policies.kyverno.io'):
                result = copy.deepcopy(next(d for d in docs if d['metadata']['name'] == args[2]))
                if not omit_status:
                    result['status'] = copy.deepcopy(status)
                if wrong_body:
                    result['spec']['failurePolicy'] = 'Ignore'
                return result
            self.assertEqual(args[:2], ('get', 'crd'))
            raise ReachedCRDGate()
        with patch.object(cloud, 'TUPPENCE', Path('/local-fixture/tuppence')), \
             patch.object(cloud, 'run', side_effect=transport), \
             patch.object(cloud.subprocess, 'check_output', side_effect=pinned), \
             patch.dict(os.environ, {'CLOUD_PLANE_CONTEXT': 'kind-local-fixture-never-contacted'}):
            cloud.admission(routes, pin, Path('/unused-package'))

    def test_native_ready_both_policy_kinds_reach_the_unchanged_crd_gate(self):
        with self.assertRaises(ReachedCRDGate):
            self.observe(READY)

    def test_absent_false_malformed_and_flat_policy_status_fail_closed_by_name(self):
        cases = [None, [], 'ready', {}, {'conditionStatus': None}, {'conditionStatus': []},
                 {'conditionStatus': {}}, {'conditionStatus': {'ready': False}},
                 {'conditionStatus': {'ready': 'true'}}, {'conditionStatus': {'ready': 1}},
                 {'conditions': [{'type': 'Ready', 'status': 'True'}]}]
        for status in cases:
            with self.subTest(status=status), self.assertRaisesRegex(
                    ValueError, 'live cloud policy validatingpolicies.policies.kyverno.io/fixture-validate is not ready'):
                self.observe(status)
        with self.assertRaisesRegex(ValueError, 'fixture-validate is not ready'):
            self.observe(None, omit_status=True)

    def test_ready_status_does_not_accept_a_different_signed_body(self):
        with self.assertRaisesRegex(AssertionError, 'live cloud body differs from the signed composed member'):
            self.observe(READY, wrong_body=True)


def selected(expression, event, opt_in, can_record):
    """Evaluate only the extracted workflow's Boolean expression, refusing new syntax."""
    expression = (expression.replace('github.event_name', 'event').replace('inputs.cloud_admission', 'opt_in')
                  .replace('env.CAN_RECORD', 'can_record').replace('always()', 'True')
                  .replace('&&', ' and ').replace('||', ' or '))
    tree = ast.parse(expression, mode='eval')
    allowed = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.Compare, ast.Eq, ast.Name, ast.Load, ast.Constant)
    if not all(isinstance(node, allowed) for node in ast.walk(tree)):
        raise AssertionError('unsupported workflow selector syntax')
    return bool(eval(compile(tree, '<actual cloud workflow selector>', 'eval'), {'__builtins__': {}},
                     {'event': event, 'opt_in': opt_in, 'can_record': can_record}))


class CloudClockSelection(unittest.TestCase):
    def test_actual_guard_and_prepare_cleanup_select_default_clocks_and_opt_in_previews(self):
        workflow = yaml.load((ROOT / '.github/workflows/truth.yml').read_text(), Loader=yaml.BaseLoader)
        steps = workflow['jobs']['gate']['steps']
        guard = next(step for step in steps if 'echo "CAN_RECORD=${can}"' in step.get('run', ''))
        prepare = next(step for step in steps if step.get('run') == 'bash verify/cloud-plane/hosted-admission.sh')
        cleanup = next(step for step in steps if 'kind delete cluster --name "cloud-tuppence-' in step.get('run', ''))
        self.assertLess(steps.index(guard), steps.index(prepare))
        self.assertEqual(guard['env']['DEFAULT_BRANCH'], '${{ github.event.repository.default_branch }}')
        self.assertIn('always()', cleanup['if'])
        with tempfile.TemporaryDirectory(prefix='cloud-selector-selfcheck-') as directory:
            repo = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', '-C', str(repo), *args], text=True)
            git('init', '-q', '-b', 'trunk')
            git('-c', 'commit.gpgsign=false', '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid',
                'commit', '--allow-empty', '-qm', 'local selector fixture')
            git('remote', 'add', 'origin', str(repo)) # filesystem only; the real nondefault guard fetches
            for branch in ('trunk', 'preview'):
                env_file = repo / ('env-' + branch)
                env = dict(os.environ, DEFAULT_BRANCH='trunk', GITHUB_REF_NAME=branch, GITHUB_ENV=str(env_file))
                result = subprocess.run(['bash', '-c', guard['run']], cwd=repo, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                values = dict(line.split('=', 1) for line in env_file.read_text().splitlines())
                can_record = values['CAN_RECORD']
                self.assertEqual(can_record, 'yes' if branch == 'trunk' else 'no')
                for event in ('push', 'schedule', 'workflow_dispatch'):
                    for opt_in in (False, True):
                        expected = branch == 'trunk' or (event == 'workflow_dispatch' and opt_in)
                        with self.subTest(branch=branch, event=event, opt_in=opt_in):
                            self.assertEqual(selected(prepare['if'], event, opt_in, can_record), expected)
                            self.assertEqual(selected(cleanup['if'], event, opt_in, can_record), expected)
        for can_record in ('', 'no'):
            self.assertFalse(selected(prepare['if'], 'schedule', False, can_record))
            self.assertFalse(selected(cleanup['if'], 'schedule', False, can_record))
            self.assertTrue(selected(prepare['if'], 'workflow_dispatch', True, can_record))
            self.assertTrue(selected(cleanup['if'], 'workflow_dispatch', True, can_record))


# Recorded immutable cloud package d314b8df0b19c42ea816c0a6ada41913b7940fbe.
# Exact resource/check_fields function bytes; this is a local fixture, not a signature proof.
RECORDED_CHECKER = '''import copy
LABEL = 'policy-as-versioned.dev/policy-version'

def resource(case: dict) -> dict:
    kind = case['kind']
    group = 'rds' if kind == 'Instance' else 's3'
    md = {'name': case['name'], 'namespace': 'cloud-proof', 'labels': {'app.kubernetes.io/name': 'ledger'}}
    if case.get('claim', '5.0.0') is not None:
        md['labels'][LABEL] = case.get('claim', '5.0.0')
    if 'workload_tier' in case:
        md['labels']['posture.acme.io/tier'] = case['workload_tier']
    provider = {'region': 'eu-west-1'}
    if kind == 'Instance':
        provider.update({'engine': 'postgres', 'instanceClass': 'db.t3.micro',
                         'allocatedStorage': 20, 'username': 'ledger',
                         'publiclyAccessible': True, 'storageEncrypted': False, 'multiAz': False})
    provider.update(copy.deepcopy(case.get('provider', {})))
    if kind != 'Instance' and not any(key in provider for key in ('bucket', 'bucketRef', 'bucketSelector')):
        provider['bucketRef'] = {'name': 'ledger-data'}
    return {'apiVersion': f'{group}.aws.m.upbound.io/v1beta1', 'kind': kind,
            'metadata': md, 'spec': {'forProvider': provider}}


def check_fields(before: dict, after: dict, case: dict) -> None:
    expected = case['expected']
    labels = after['metadata']['labels']
    assert labels['posture.acme.io/tier'] == expected['tier'], case['name']
    assert labels['posture.acme.io/caged'] == 'true', case['name']
    for key, value in before['metadata'].get('labels', {}).items():
        if key not in ('posture.acme.io/tier', 'posture.acme.io/caged'):
            assert labels[key] == value, (case['name'], key)
    fp = after['spec']['forProvider']
    assert fp['region'] == before['spec']['forProvider']['region']
    if case['kind'] == 'Instance':
        assert fp['publiclyAccessible'] is False and fp['storageEncrypted'] is True
        for key in ('multiAz', 'backupRetentionPeriod'):
            assert fp[key] == expected[key], (case['name'], key, fp[key])
        for key, value in before['spec']['forProvider'].items():
            if key not in ('publiclyAccessible', 'storageEncrypted', 'multiAz', 'backupRetentionPeriod'):
                assert fp[key] == value, (case['name'], key)
    else:
        for key, value in before['spec']['forProvider'].items():
            if key != 'rule':
                assert fp[key] == value, (case['name'], key)
        for rule in fp['rule']:
            assert rule['applyServerSideEncryptionByDefault']['sseAlgorithm'] == expected['sseAlgorithm']
            if 'kmsMasterKeyId' in expected:
                assert rule['applyServerSideEncryptionByDefault']['kmsMasterKeyId'] == expected['kmsMasterKeyId']
            if 'bucketKeyEnabled' in expected:
                assert rule['bucketKeyEnabled'] == expected['bucketKeyEnabled']
'''


class CloudFieldObservation(unittest.TestCase):
    """Exercise the actual admission caller with local transport responses only."""

    def observe(self, fault_stage=None, *, assertion=False, malformed=False, fault_kind=None, via_main=False):
        prefix = 'policy-as-versioned.dev/'
        names = ['crossplane-crds', 'cloud-policies', 'cloud-claims']
        routes = [{'metadata': {'name': name}, 'spec': {'path': './fixture/' + name}} for name in names]
        pin = {'metadata': {'annotations': {
            prefix + 'gitsign-identity-regexp': cloud.TUPPENCE_IDENTITY,
            prefix + 'gitsign-issuer': 'https://token.actions.githubusercontent.com',
            prefix + 'gitsign-gates': ','.join('flux-system/' + name for name in names)}},
            'spec': {'url': 'https://github.com/policy-as-versioned-tuppence/tuppence',
                     'ref': {'tag': 'v1.0.0', 'commit': 'a' * 40}}}
        source = copy.deepcopy(pin)
        source['metadata']['annotations'][prefix + 'gitsign-verified'] = 'true'
        revision = 'v1.0.0@sha1:' + 'a' * 40
        ready = [{'type': 'Ready', 'status': 'True'}]
        source['status'] = {'conditions': ready, 'artifact': {'revision': revision}}
        policy = {'kind': 'MutatingPolicy', 'metadata': {'name': 'fixture-policy'}, 'spec': {'failurePolicy': 'Fail'}}
        crd = {'spec': {'group': 'schema-fixture'}, 'status': {'conditions': [{'type': 'Established', 'status': 'True'}]}}
        with tempfile.TemporaryDirectory(prefix='cloud-field-local-caller-') as directory:
            work = Path(directory)
            package = work / 'package'
            package.mkdir()
            (package / 'replay.py').write_text(RECORDED_CHECKER)
            reader = cloud.module('recorded_cloud_fields', package / 'replay.py')
            before = reader.resource({'name': 'fixture-rds', 'kind': 'Instance'})
            before['metadata']['namespace'] = 'tuppence'
            # Deliberately private fixture values must never enter the diagnostic.
            before['metadata']['labels']['private.example/key'] = 'private-label-sentinel'
            before['metadata']['annotations'] = {'private.example/key': 'private-annotation-sentinel'}
            before['spec']['forProvider']['username'] = 'private-username-sentinel'
            claims = [before]
            (work / 'gitops/cloud').mkdir(parents=True)
            (work / 'gitops/cloud/claims.yaml').write_text(yaml.safe_dump_all(claims))
            (work / 'gitops/composed').mkdir()
            (work / 'gitops/composed/composed-set.yaml').write_text(yaml.safe_dump({'kind': 'GitRepository', **pin}))
            row = {'multiAz': True, 'backupRetentionPeriod': 35}
            (package / 'crossplane-dials.yaml').write_text(yaml.safe_dump({'tiers': {'isolated': row}}))
            files = {'fixture/cloud-policies/kustomization.yaml': {'resources': ['policy.yaml']},
                     'fixture/cloud-policies/policy.yaml': policy,
                     'fixture/cloud-claims/claims.yaml': claims}
            for name in ['instances.rds.aws.m.upbound.io', 'bucketserversideencryptionconfigurations.s3.aws.m.upbound.io']:
                files['fixture/crossplane-crds/' + name + '.yaml'] = crd

            def pinned(command, **kwargs):
                self.assertEqual(command[:4], ['git', '-C', str(work), 'show'])
                ref, path = command[4].split(':', 1)
                self.assertEqual(ref, 'a' * 40)
                value = files[path]
                return yaml.safe_dump_all(value) if isinstance(value, list) else yaml.safe_dump(value)

            responses = []

            def response(obj, stage):
                after = copy.deepcopy(obj)
                after['metadata']['labels'].update({'posture.acme.io/tier': 'isolated', 'posture.acme.io/caged': 'true'})
                provider = after['spec']['forProvider']
                if obj['kind'] == 'Instance':
                    provider.update({'publiclyAccessible': False, 'storageEncrypted': True, **row})
                else:
                    provider['rule'] = [{'applyServerSideEncryptionByDefault': {
                        'sseAlgorithm': 'AES256', 'kmsMasterKeyId': 'private-kms-sentinel'}, 'bucketKeyEnabled': True}]
                if fault_stage == stage and (fault_kind is None or fault_kind == obj['kind']):
                    if malformed:
                        after['metadata']['labels']['posture.acme.io/tier'] = []
                    elif assertion:
                        after['metadata']['labels']['posture.acme.io/tier'] = 'baseline'
                    else:
                        del after['metadata']['labels']['posture.acme.io/tier']
                responses.append(after)
                return after

            def transport(*args, data=None):
                if args[:2] == ('get', 'gitrepository'):
                    return source
                if args[:2] == ('get', 'mutatingpolicies.policies.kyverno.io'):
                    return {**copy.deepcopy(policy), 'status': copy.deepcopy(READY)}
                if args[:2] == ('get', 'crd'):
                    return copy.deepcopy(crd)
                if args[:2] == ('get', 'kustomization'):
                    return {'status': {'conditions': ready, 'lastAppliedRevision': revision,
                                       'inventory': {'entries': [{'id': 'local-fixture'}]}}}
                if args[:2] == ('get', 'namespace'):
                    return {'metadata': {'labels': {prefix + 'governed': 'true', 'posture.acme.io/tier': 'isolated'}}}
                if args[:2] == ('get', 'Instance'):
                    return response(before, 'live get')
                self.assertIn(args[0], ('apply', 'create'))
                self.assertIn('--dry-run=server', args)
                return response(yaml.safe_load(data), 'UPDATE serverdryrun' if args[0] == 'apply' else 'CREATE serverdryrun')

            self.reader_calls = []
            self.reader_exception = None
            load_module = cloud.module

            def loading(name, path):
                if name == 'cloud_trigger':
                    return SimpleNamespace(find=lambda root: {'record_commit': 'local-fixture'})
                loaded = load_module(name, path)
                if name == 'cloud_replay':
                    original_checker = loaded.check_fields

                    def checking(before, after, case):
                        inputs = (before, after, case)
                        snapshot = copy.deepcopy(inputs)
                        self.reader_calls.append(inputs)
                        self.assertIs(after, responses[-1], 'delegate must receive the exact observed response')
                        try:
                            original_checker(*inputs)
                        except (KeyError, AssertionError) as exc:
                            self.reader_exception = exc
                            raise
                        finally:
                            self.assertEqual(inputs, snapshot, 'diagnostics must not change checker inputs')

                    loaded.check_fields = checking
                return loaded

            output = io.StringIO()
            stdout = io.StringIO()
            with patch.object(cloud, 'module', side_effect=loading), patch.object(cloud, 'TUPPENCE', work), patch.object(cloud, 'run', side_effect=transport), \
                 patch.object(cloud.subprocess, 'check_output', side_effect=pinned), \
                 patch.dict(os.environ, {'CLOUD_PLANE_CONTEXT': 'kind-local-fixture-never-contacted'}), \
                 patch.object(cloud, 'declarations', return_value=({}, routes)), \
                 patch.object(cloud, 'cloud_parent', return_value=({}, package)), \
                 patch.object(cloud.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), \
                 patch.object(cloud.sys, 'argv', ['cloud_plane.py']), \
                 redirect_stderr(output), redirect_stdout(stdout):
                try:
                    if via_main:
                        self.main_exit = cloud.main()
                    else:
                        cloud.admission(routes, pin, package)
                finally:
                    self.context_output = output.getvalue()
                    self.main_output = stdout.getvalue()

    def test_actual_live_field_failure_keeps_keyerror_and_reports_safe_context(self):
        with self.assertRaisesRegex(KeyError, 'posture.acme.io/tier') as caught:
            self.observe('live get')
        self.assertIs(caught.exception, self.reader_exception)
        self.assertIn('cloud field context: ', self.context_output,
                      'actual admission field failure lacks the required observation context')
        context = json.loads(self.context_output.split('cloud field context: ', 1)[1])
        self.assertEqual(context['stage'], 'live get')
        self.assertEqual(context['source_revision'], 'v1.0.0@sha1:' + 'a' * 40)
        self.assertEqual(context['observed']['labels']['posture.acme.io/tier'], {'missing': True})
        self.assertEqual(context['before']['name'], 'fixture-rds')
        self.assertEqual(context['observed']['namespace'], 'tuppence')
        self.assertEqual(context['expected']['tier'], 'isolated')
        self.assertNotIn('private-', self.context_output)


    def test_actual_update_and_create_field_failures_name_their_distinct_stages(self):
        for stage in ('UPDATE serverdryrun', 'CREATE serverdryrun'):
            with self.subTest(stage=stage):
                with self.assertRaisesRegex(KeyError, 'posture.acme.io/tier') as caught:
                    self.observe(stage)
                self.assertIs(caught.exception, self.reader_exception)
                context = json.loads(self.context_output.split('cloud field context: ', 1)[1])
                self.assertEqual(context['stage'], stage)
                self.assertEqual(context['source_revision'], 'v1.0.0@sha1:' + 'a' * 40)
                self.assertEqual(context['observed']['labels']['posture.acme.io/tier'], {'missing': True})
                self.assertEqual(context['observed']['mutation']['backupRetentionPeriod'], 35)

    def test_immutable_field_assertion_and_malformed_scalar_remain_failures(self):
        for malformed in (False, True):
            with self.subTest(malformed=malformed), self.assertRaisesRegex(AssertionError, 'fixture-rds') as caught:
                self.observe('live get', assertion=True, malformed=malformed)
            self.assertIs(caught.exception, self.reader_exception)
            context = json.loads(self.context_output.split('cloud field context: ', 1)[1])
            value = {'type': 'list'} if malformed else 'baseline'
            self.assertEqual(context['observed']['labels']['posture.acme.io/tier'], value)
            self.assertEqual(context['expected']['tier'], 'isolated')

    def test_s3_failure_reports_only_public_encryption_fields(self):
        with self.assertRaisesRegex(KeyError, 'posture.acme.io/tier'):
            self.observe('CREATE serverdryrun', fault_kind='BucketServerSideEncryptionConfiguration')
        context = json.loads(self.context_output.split('cloud field context: ', 1)[1])
        self.assertEqual(context['observed']['kind'], 'BucketServerSideEncryptionConfiguration')
        self.assertEqual(context['observed']['encryption'], [{'sseAlgorithm': 'AES256', 'bucketKeyEnabled': True}])
        for forbidden in ('private-', 'username', 'kmsMasterKeyId', 'bucketRef', 'annotations', 'managedFields'):
            self.assertNotIn(forbidden, self.context_output)

    def test_unchanged_positive_checker_observations_emit_no_failure_context(self):
        self.observe()
        self.assertEqual(self.context_output, '')
        self.assertEqual(len(self.reader_calls), 8)  # one incumbent GET/UPDATE and six CREATE probes
        self.assertEqual({before['kind'] for before, _, _ in self.reader_calls},
                         {'Instance', 'BucketServerSideEncryptionConfiguration'})


    def test_actual_main_retains_the_original_failure_line_and_exit_one(self):
        self.observe('live get', via_main=True)
        self.assertEqual(self.main_exit, 1)
        self.assertEqual(self.main_output, "FAIL: cloud plane: 'posture.acme.io/tier'\n")
        self.assertIn('cloud field context: ', self.context_output)


class CloudDocumentRevision(unittest.TestCase):
    """Both CLI modes admit a publisher's independent OSCAL document revision."""

    def declaration_tree(self, root, revision='1.0.0', *, missing_revision=False):
        platform = root / 'platform'
        package = platform / 'implementations/cloud'
        tuppence = root / 'tuppence'
        def write(path, value):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(value, sort_keys=False))
        members = [('validate-rds', 'ValidatingPolicy'), ('validate-s3', 'ValidatingPolicy'),
                   ('mutate-rds', 'MutatingPolicy'), ('mutate-s3', 'MutatingPolicy')]
        write(platform / 'party.yaml', {'publishes': [{'kind': 'implementations', 'path': 'implementations/cloud'}]})
        write(package / 'package.yaml', {'version': '1.0.1', 'members': [name + '.yaml' for name, _ in members]})
        (package / 'VERSION').write_text('1.0.1\n')
        for name, kind in members:
            write(package / (name + '.yaml'), {'kind': kind, 'metadata': {'name': name}, 'spec': {'validationActions': ['Audit']}})
        # Labelled synthetic dials satisfy the existing declaration contract.
        dials = {tier: {'backupRetentionPeriod': index, 'publiclyAccessible': False, 'storageEncrypted': True}
                 for index, tier in enumerate(('baseline', 'restricted', 'quarantine', 'isolated'), 1)}
        write(package / 'crossplane-dials.yaml', {'tiers': dials})
        component = {'component-definition': {'metadata': {'version': revision}, 'components': [{
            'control-implementations': [{'implemented-requirements': [
                {'control-id': 'cp-10', 'props': [{'value': 'validate-rds'}]},
                {'control-id': 'sc-28', 'props': [{'value': 'validate-s3'}]}]}]}]}}
        if missing_revision:
            del component['component-definition']['metadata']['version']
        (package / 'component-definition.json').write_text(json.dumps(component))
        claims = [{'kind': kind, 'metadata': {'namespace': 'tuppence', 'labels': {cloud.LABEL: '5.0.0'}}, 'spec': {}}
                  for kind in ('Instance', 'BucketServerSideEncryptionConfiguration')]
        claim_path = tuppence / 'gitops/cloud/claims.yaml'
        claim_path.parent.mkdir(parents=True, exist_ok=True)
        claim_path.write_text(yaml.safe_dump_all(claims))
        write(tuppence / 'gitops/composed/composed-set.yaml', {'kind': 'ResourceSet', 'spec': {'inputs': [{'versions': [{'version': '5.0.0'}]}]}})
        routes = [{'metadata': {'name': name}, 'spec': {'sourceRef': {'kind': 'GitRepository', 'name': 'tuppence-composed'}}}
                  for name in ('crossplane-crds', 'cloud-policies', 'cloud-claims')]
        routes[1]['spec']['dependsOn'] = [{'name': 'crossplane-crds'}]
        routes[2]['spec'].update(dependsOn=[{'name': 'cloud-policies'}], wait=False)
        (tuppence / 'gitops/cloud/cloud-delivery.yaml').write_text(yaml.safe_dump_all(routes))
        return platform, package, tuppence

    def invoke(self, revision, arguments, *, missing_revision=False):
        with tempfile.TemporaryDirectory(prefix='cloud-document-revision-') as tmp:
            platform, package, tuppence = self.declaration_tree(Path(tmp), revision, missing_revision=missing_revision)
            output = io.StringIO()
            # A genuine absent trigger remains a declared wait. The source and
            # substrate boundaries must not be touched by this declaration test.
            with patch.object(cloud, 'PLATFORM', platform), patch.object(cloud, 'PACKAGE', package), \
                 patch.object(cloud, 'TUPPENCE', tuppence), \
                 patch.object(cloud, 'module', return_value=SimpleNamespace(find=lambda root: None)), \
                 patch.object(cloud, 'run', side_effect=AssertionError('no native calls permitted')), \
                 patch.object(cloud, 'verify_tag', side_effect=AssertionError('no signature calls permitted')), \
                 patch.object(cloud.sys, 'argv', ['cloud_plane.py', *arguments]), redirect_stdout(output):
                result = cloud.main()
            return result, output.getvalue()

    def test_package_patch_does_not_require_an_oscal_document_revision_bump(self):
        for arguments in ([], ['--preflight']):
            with self.subTest(arguments=arguments):
                result, output = self.invoke('1.0.0', arguments)
                self.assertEqual(result, 3, output)
                self.assertIn('SKIP: cloud plane waits for a citable e2e step 4 PASS', output)

    def test_non_semver_publisher_document_revision_is_accepted(self):
        for arguments in ([], ['--preflight']):
            with self.subTest(arguments=arguments):
                result, output = self.invoke('publisher-revision-2026-10', arguments)
                self.assertEqual(result, 3, output)
                self.assertTrue(output.startswith('SKIP:'), output)

    def test_missing_or_malformed_document_revision_refuses_in_both_modes(self):
        for arguments in ([], ['--preflight']):
            for revision in (None, False, True, 0, 1, 1.0, [], {}, '', ' \t\n'):
                with self.subTest(arguments=arguments, revision=revision):
                    result, output = self.invoke(revision, arguments)
                    self.assertEqual(result, 1, output)
                    self.assertIn('FAIL: cloud plane:', output)
                    self.assertNotIn('SKIP:', output)
            with self.subTest(arguments=arguments, missing=True):
                result, output = self.invoke(None, arguments, missing_revision=True)
                self.assertEqual(result, 1, output)
                self.assertIn('FAIL: cloud plane:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
