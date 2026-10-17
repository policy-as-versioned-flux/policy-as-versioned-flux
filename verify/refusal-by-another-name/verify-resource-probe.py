#!/usr/bin/env python3
"""Native resource-probe regressions; authored CRD mappings are not provider-schema proofs."""
from pathlib import Path
import shutil
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


if __name__ == '__main__':
    unittest.main()
