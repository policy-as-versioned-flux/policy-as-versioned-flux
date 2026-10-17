"""Local call-site proofs of cloud readiness and hosted-clock selection; no live claim."""
from __future__ import annotations

import ast
import copy
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
