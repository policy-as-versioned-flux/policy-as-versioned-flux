#!/usr/bin/env python3
"""Native resource-probe regressions; authored CRD mappings are not provider-schema proofs."""
from pathlib import Path
import shutil
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

import refusal_probe as rp


class NativeResourceProbe(unittest.TestCase):
    def setUp(self):
        self.binary = shutil.which('kyverno')
        self.assertIsNotNone(self.binary, 'native Kyverno CLI is required')
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.composed = self.root / 'adopter/composed'
        self.policy = self.composed / 'cloud/v1.0.0/mutation.yaml'
        self.policy.parent.mkdir(parents=True)
        self.schemas = self.composed / 'cloud-crds'
        self.schemas.mkdir()
        tiers = patch.object(rp, 'TIERS', ('baseline',))
        tiers.start()
        self.addCleanup(tiers.stop)

    def document(self, service='s3'):
        group, kind, plural = (
            ('rds.aws.m.upbound.io', 'Instance', 'instances') if service == 'rds' else
            ('s3.aws.m.upbound.io', 'BucketServerSideEncryptionConfiguration',
             'bucketserversideencryptionconfigurations'))
        schema = {'apiVersion': 'apiextensions.k8s.io/v1', 'kind': 'CustomResourceDefinition',
                  'metadata': {'name': f'{plural}.{group}'},
                  'spec': {'group': group, 'scope': 'Namespaced',
                           'names': {'kind': kind, 'plural': plural},
                           'versions': [{'name': 'v1beta1', 'served': True, 'storage': True,
                                         'schema': {'openAPIV3Schema': {'type': 'object',
                                                    'x-kubernetes-preserve-unknown-fields': True}}}]}}
        (self.schemas / 'mapping.yaml').write_text(yaml.safe_dump(schema))
        doc = {'apiVersion': 'policies.kyverno.io/v1', 'kind': 'MutatingPolicy',
               'metadata': {'name': f'typed-{service}'},
               'spec': {'matchConstraints': {'resourceRules': [{
                   'apiGroups': [group], 'apiVersions': ['v1beta1'],
                   'operations': ['CREATE', 'UPDATE'], 'resources': [plural]}]},
                   'mutations': [{'patchType': 'JSONPatch', 'jsonPatch': {'expression':
                       "[JSONPatch{op: 'add', path: '/metadata/labels/posture.acme.io~1caged', value: 'true'}]"}}]}}
        self.policy.write_text(yaml.safe_dump(doc))
        return doc, schema

    def probe(self, doc):
        return rp.probe(self.binary, doc, str(self.policy))

    def test_typed_write_then_second_application_is_stable(self):
        for service in ['rds', 's3']:
            with self.subTest(service=service):
                doc, _ = self.document(service)
                result = self.probe(doc)
                self.assertTrue(result.ok, result.detail)
                self.assertNotEqual(result.status, 'skip')

    def test_empty_unmatched_and_duplicate_append_still_fail(self):
        for defect in ['empty', 'unmatched', 'duplicate-append']:
            with self.subTest(defect=defect):
                doc, _ = self.document()
                if defect == 'empty':
                    doc['spec']['mutations'] = []
                elif defect == 'unmatched':
                    doc['spec']['matchConditions'] = [{'name': 'never', 'expression': 'false'}]
                else:
                    doc['spec']['mutations'][0]['jsonPatch']['expression'] = (
                        "[JSONPatch{op: 'add', path: '/spec/forProvider/rule', value: "
                        "object.spec.forProvider.rule + [{'applyServerSideEncryptionByDefault': "
                        "{'sseAlgorithm': 'AES256'}}]}]")
                result = self.probe(doc)
                self.assertFalse(result.ok, result.detail)
                self.assertNotEqual(result.status, 'skip', result.detail)
                if defect == 'duplicate-append':
                    self.assertIn('NOT identical', result.detail)

    def test_absent_wrong_and_ambiguous_mapping_are_unavailable(self):
        for defect in ['absent', 'wrong', 'ambiguous']:
            with self.subTest(defect=defect):
                doc, schema = self.document()
                mapping = self.schemas / 'mapping.yaml'
                if defect == 'absent':
                    mapping.unlink()
                elif defect == 'wrong':
                    schema['spec']['names']['kind'] = 'WrongKind'
                    mapping.write_text(yaml.safe_dump(schema))
                else:
                    (self.schemas / 'duplicate.yaml').write_text(yaml.safe_dump(schema))
                result = self.probe(doc)
                self.assertFalse(result.ok)
                self.assertEqual(result.status, 'skip', result.detail)
                self.assertIn('CRD', result.detail)
                (self.schemas / 'duplicate.yaml').unlink(missing_ok=True)

    def test_other_adopter_schema_is_not_a_fallback(self):
        doc, schema = self.document()
        (self.schemas / 'mapping.yaml').unlink()
        other = self.root / 'other/composed/cloud-crds'
        other.mkdir(parents=True)
        (other / 'mapping.yaml').write_text(yaml.safe_dump(schema))
        self.assertEqual(self.probe(doc).status, 'skip')

    def test_unknown_resource_has_no_Pod_fallback(self):
        doc, _ = self.document()
        doc['spec']['matchConstraints']['resourceRules'][0]['resources'] = ['unknowns']
        result = self.probe(doc)
        self.assertFalse(result.ok)
        self.assertEqual(result.status, 'skip', result.detail)

    def test_original_Pod_zero_and_typed_without_mapping_are_negative_controls(self):
        doc, _ = self.document()
        policy, _ = rp.declaw(doc)
        self.policy.write_text(yaml.safe_dump(policy))
        resource = self.root / 'input.yaml'
        values = self.root / 'values.yaml'
        values.write_text(yaml.safe_dump(rp._values('baseline')))
        resource.write_text(yaml.safe_dump(rp._pod('probe', None)))
        pod = rp._apply(self.binary, self.policy, resource, self.root / 'pod-output', values)
        self.assertFalse(pod.applied)
        typed = rp._pod('probe', None)
        typed.update(apiVersion='s3.aws.m.upbound.io/v1beta1',
                     kind='BucketServerSideEncryptionConfiguration',
                     spec={'forProvider': {'region': 'eu-west-1', 'bucketRef': {'name': 'probe'},
                                          'rule': [{'applyServerSideEncryptionByDefault': {
                                              'sseAlgorithm': 'garbage'}}]}})
        resource.write_text(yaml.safe_dump(typed))
        no_mapping = rp._apply(self.binary, self.policy, resource, self.root / 'unmapped-output', values)
        self.assertFalse(no_mapping.applied)
        self.assertIn('failed to map gvk to gvr', no_mapping.text.lower())


class WrapperVerdict(unittest.TestCase):
    """Actual shell aggregation; independent leg results are explicitly fixture data."""

    def run_wrapper(self, static, functional, *, actual_missing_crd=False,
                    collector=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relative = 'adopter/composed/cloud/v1.0.0/mutation.yaml'
            policy = root / '.estate-clone' / relative
            policy.parent.mkdir(parents=True)
            policy.write_text(yaml.safe_dump({
                'apiVersion': 'policies.kyverno.io/v1', 'kind': 'MutatingPolicy',
                'metadata': {'name': 'missing-crd-fixture'},
                'spec': {'matchConstraints': {'resourceRules': [{
                    'apiGroups': ['s3.aws.m.upbound.io'], 'apiVersions': ['v1beta1'],
                    'operations': ['CREATE', 'UPDATE'],
                    'resources': ['bucketserversideencryptionconfigurations']}]},
                    'mutations': []}}))
            wrapper = root / 'verify/refusal-by-another-name/verify-refusal-by-another-name.sh'
            wrapper.parent.mkdir(parents=True)
            wrapper.write_bytes(Path(__file__).with_name(wrapper.name).read_bytes())
            instrument = root / 'python-instrument'
            instrument.write_text('#!' + sys.executable + '\n' + r'''
import importlib.util, json, os
from pathlib import Path
import sys
from unittest.mock import patch
import yaml
target = Path(sys.argv[1]).name
if target == 'refusal_probe.py' and '--root' in sys.argv:
    if os.environ.get('ACTUAL_MISSING_CRD') == '1':
        spec = importlib.util.spec_from_file_location('actual_missing_crd', os.environ['PROBE_SOURCE'])
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        root = Path(os.environ['ISOLATED_ROOT'])
        relative = 'adopter/composed/cloud/v1.0.0/mutation.yaml'
        doc = yaml.safe_load((root/'.estate-clone'/relative).read_text())
        with patch.object(module, 'collect', return_value=[(doc, relative)]):
            raise SystemExit(module.main(['--root', str(root)]))
    code, text = json.loads(os.environ['FUNCTIONAL_RESULT'])
elif target == 'refusal_scan.py' and '--register' in sys.argv:
    code, text = json.loads(os.environ['STATIC_RESULT'])
else:
    raise SystemExit(0)
print(text)
raise SystemExit(code)
''')
            instrument.chmod(0o755)
            import json
            env = dict(os.environ, PYTHON=str(instrument), STATIC_RESULT=json.dumps(static),
                       FUNCTIONAL_RESULT=json.dumps(functional), ISOLATED_ROOT=str(root),
                       PROBE_SOURCE=str(Path(rp.__file__).resolve()),
                       ACTUAL_MISSING_CRD='1' if actual_missing_crd else '0')
            if collector is not None:
                binary = root / 'collector-bin/tee'
                binary.parent.mkdir()
                binary.write_text('#!/bin/sh\n' + collector)
                binary.chmod(0o755)
                env['PATH'] = str(binary.parent) + os.pathsep + env['PATH']
            return subprocess.run(['/bin/bash', str(wrapper)], env=env, capture_output=True, text=True)

    def test_actual_wrapper_preserves_skip_causes_and_failure_precedence(self):
        observed = (0, 'PASS: fixture observed')
        static_skip = (3, '  ?? static fixture: cloud UPDATE mutability unknown\nSKIP: static missing instrument')
        functional_skip = (3, '  ?? functional fixture: missing served CRD\nSKIP: functional missing instrument')
        cases = [
            (static_skip, observed, 3, ['cloud UPDATE mutability unknown']),
            (observed, functional_skip, 3, ['missing served CRD']),
            (static_skip, functional_skip, 3, ['cloud UPDATE mutability unknown', 'missing served CRD']),
            (observed, (0, 'SKIP: fixture false-green missing CRD'), 3, ['false-green missing CRD']),
            ((1, 'FAIL: fixture real mutation defect'), functional_skip, 1, ['real mutation defect']),
            (static_skip, (1, 'FAIL: fixture changed second output'), 1, ['changed second output']),
            (observed, observed, 0, []),
        ]
        for static, functional, code, reasons in cases:
            with self.subTest(static=static[0], functional=functional[0], code=code):
                result = self.run_wrapper(static, functional)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                last = result.stdout.strip().splitlines()[-1]
                self.assertTrue(last.startswith({0: 'PASS:', 1: 'FAIL:', 3: 'SKIP:'}[code]), last)
                for reason in reasons:
                    self.assertIn(reason, last)

    def test_real_production_missing_CRD_cause_reaches_consumed_line(self):
        result = self.run_wrapper((0, 'PASS: explicit static fixture'), (0, ''), actual_missing_crd=True)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        last = result.stdout.strip().splitlines()[-1]
        self.assertTrue(last.startswith('SKIP:'), last)
        self.assertIn('missing native resource instrument', last)
        self.assertIn('expected one served CRD', last)

    def test_failed_or_missing_capture_never_hides_emitted_skip(self):
        observed = (0, 'PASS: explicit observed fixture')
        emitted_skip = (0, 'SKIP: explicit producer missing served CRD')
        collectors = {
            'failed': '/bin/cat >/dev/null\nexit 1\n',
            'missing': '/bin/cat >/dev/null\nexit 0\n',
            'empty': '/bin/cat >"$1"\n: >"$1"\nexit 0\n',
            'failed-with-output': '/bin/cat >"$1"\nexit 1\n',
        }
        for name, collector in collectors.items():
            for static, functional in [(emitted_skip, observed),
                                       (observed, emitted_skip)]:
                with self.subTest(collector=name, static=static[1]):
                    result = self.run_wrapper(static, functional, collector=collector)
                    self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                    last = result.stdout.strip().splitlines()[-1]
                    self.assertTrue(last.startswith('SKIP:'), last)
                    self.assertIn('output capture unavailable', last)
                    self.assertNotIn('No such file', result.stderr)

    def test_native_failure_precedes_capture_failure(self):
        observed = (0, 'PASS: explicit observed fixture')
        failed = (1, 'FAIL: explicit native mutation defect')
        for static, functional, leg in [(failed, observed, 'static'),
                                         (observed, failed, 'functional')]:
            with self.subTest(leg=leg):
                result = self.run_wrapper(static, functional,
                                          collector='/bin/cat >/dev/null\nexit 1\n')
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                last = result.stdout.strip().splitlines()[-1]
                self.assertTrue(last.startswith('FAIL:'), last)
                self.assertIn(leg + ' mutation leg exited 1', last)
                self.assertIn('output capture unavailable', last)
                self.assertNotIn('No such file', result.stderr)

    def test_unavailable_capture_directory_is_named_skip(self):
        observed = (0, 'PASS: explicit observed fixture')
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / 'mktemp'
            binary.write_text('#!/bin/sh\nexit 1\n')
            binary.chmod(0o755)
            with patch.dict(os.environ, {'PATH': temporary + os.pathsep + os.environ['PATH']}):
                result = self.run_wrapper(observed, observed)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        last = result.stdout.strip().splitlines()[-1]
        self.assertTrue(last.startswith('SKIP:'), last)
        self.assertIn('output capture unavailable', last)
        self.assertIn('cannot create', last)

    def test_physically_absent_collector_is_named_skip(self):
        observed = (0, 'PASS: explicit observed fixture')
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for name in ('dirname', 'sed', 'mktemp', 'rm', 'kyverno'):
                executable = shutil.which(name)
                self.assertIsNotNone(executable, name)
                (directory / name).symlink_to(executable)
            with patch.dict(os.environ, {'PATH': temporary}):
                result = self.run_wrapper(observed, observed)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        last = result.stdout.strip().splitlines()[-1]
        self.assertTrue(last.startswith('SKIP:'), last)
        self.assertIn('tee', last)
        self.assertIn('output capture unavailable', last)

    def test_real_outer_entry_checks_collector_before_native_selfchecks(self):
        marker = 'PAVC_OUTER_COLLECTOR_ABSENCE_TEST'
        if os.environ.get(marker) == '1':
            self.skipTest('nested boundary probe; only its self-referential test is excluded')
        wrapper = Path(__file__).with_name('verify-refusal-by-another-name.sh')
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for name in ('dirname', 'sed', 'mktemp', 'rm', 'kyverno'):
                executable = shutil.which(name)
                self.assertIsNotNone(executable, name)
                (directory / name).symlink_to(executable)
            (directory / 'python3').symlink_to(sys.executable)
            env = dict(os.environ, PATH=temporary, PYTHON=sys.executable,
                       **{marker: '1'})
            for mode in ([], ['--selfcheck']):
                with self.subTest(mode=mode):
                    result = subprocess.run(['/bin/bash', str(wrapper), *mode], env=env,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                    last = result.stdout.strip().splitlines()[-1]
                    self.assertTrue(last.startswith('SKIP:'), last)
                    self.assertIn('tee', last)
            absent = subprocess.run(['/bin/bash', str(wrapper), '--inventory'], env=env,
                                    capture_output=True, text=True)
            collector = shutil.which('tee')
            self.assertIsNotNone(collector, 'installed collector is needed for the inventory control')
            (directory / 'tee').symlink_to(collector)
            installed = subprocess.run(['/bin/bash', str(wrapper), '--inventory'], env=env,
                                       capture_output=True, text=True)
            self.assertEqual((absent.returncode, absent.stdout, absent.stderr),
                             (installed.returncode, installed.stdout, installed.stderr))


if __name__ == '__main__':
    unittest.main()
