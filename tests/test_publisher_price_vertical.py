"""Real producer→resolver→scorer→publisher→compose source proof, all data synthetic."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import builtins
import copy
import hashlib
import inspect
import os
import json
import yaml

from publisher_price_fixture import source_roots, signature_boundary, whole_fixture


class PublisherPriceVertical(unittest.TestCase):
    def test_self_controls_use_the_captured_catalogue_declaration_for_their_hole_price(self):
        actual = source_roots()
        with tempfile.TemporaryDirectory(prefix='synthetic-own-controls-') as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, signature_boundary(root)):
                fixture = whole_fixture(root, actual)
                ct, adopter = fixture['ct'], fixture['adopter']
                party = copy.deepcopy(fixture['party'])
                party['roles'].append('publisher')
                party['inherits'].append({'party': 'driftwood', 'kind': 'controls', 'version': '0.0.0'})
                party.setdefault('publishes', []).append({
                    'kind': 'controls', 'name': 'own-controls', 'path': 'own-controls'})
                party['overlay']['controls'] = ['driftwood:zz-1']
                workflows = adopter / '.github/workflows'
                workflows.mkdir(parents=True, exist_ok=True)
                for name in ('cut-release.yml', 'release.yml'):
                    (workflows / name).write_bytes((actual['platform'] / '.github/workflows' / name).read_bytes())
                ct._write_small_catalog(adopter, {'zz-1': {'scenario': 'scenarios/zz-1.json'}})
                (adopter / 'catalog').rename(adopter / 'own-controls')
                (adopter / 'scenarios').mkdir(exist_ok=True)
                scenario = {'version': 'v1', 'name': 'Synthetic own control',
                            'warn': {'lef': [1, 1, 1], 'lm': [5, 5, 5]},
                            'deny': {'lef': [0, 0, 0], 'lm': [5, 5, 5]}}
                (adopter / 'scenarios/zz-1.json').write_text(json.dumps(scenario))
                other_scenario = copy.deepcopy(scenario)
                other_scenario['warn']['lm'] = [6, 6, 6]
                other_scenario['deny']['lm'] = [6, 6, 6]
                (adopter / 'scenarios/zz-other.json').write_text(json.dumps(other_scenario))
                ct._write_small_catalog(adopter / 'other-catalog-stage', {
                    'zz-1': {'scenario': 'scenarios/zz-other.json'}})
                (adopter / 'other-catalog-stage/catalog').rename(adopter / 'other-controls')
                target = adopter / 'party.yaml'
                original = yaml.safe_dump(party).encode()
                target.write_bytes(original)
                stable, stable_rendered = ct.compose(adopter, fixture['trees'])
                self.assertEqual(stable['outcome'], 'composed', stable)
                hole = next(h for h in stable['holes'] if h['source'] == 'driftwood' and h['control_id'] == 'zz-1')
                self.assertEqual((hole['amount'], hole['currency']), (5, 'GBP'))
                changed = copy.deepcopy(party)
                changed['publishes'][-1]['path'] = 'other-controls'
                other, real_read = yaml.safe_dump(changed).encode(), Path.read_text

                def concurrent_read(path, *args, **kwargs):
                    caller = inspect.currentframe().f_back
                    if path == target and caller.f_code.co_name == '_catalog_dir':
                        target.write_bytes(other)
                        try:
                            return real_read(path, *args, **kwargs)
                        finally:
                            target.write_bytes(original)
                    return real_read(path, *args, **kwargs)

                with patch.object(Path, 'read_text', concurrent_read):
                    document, rendered = ct.compose(adopter, fixture['trees'])
                self.assertEqual(document['outcome'], 'composed', document)
                self.assertEqual(document['holes'], stable['holes'])
                self.assertEqual(document['prices'], stable['prices'])
                self.assertEqual(rendered, stable_rendered)
                self.assertEqual(target.read_bytes(), original)

    def test_comparison_identity_uses_the_same_captured_party_bytes_as_pricing(self):
        actual = source_roots()
        with tempfile.TemporaryDirectory(prefix='synthetic-comparison-capture-') as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, signature_boundary(root)):
                fixture = whole_fixture(root, actual)
                target = fixture['adopter'] / 'party.yaml'
                original = target.read_bytes()
                changed = copy.deepcopy(fixture['party'])
                changed['appetite']['tolerance']['amount'] = 1000
                other = yaml.safe_dump(changed).encode()
                stable, expected = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(stable['outcome'], 'composed', stable)
                real_read = Path.read_bytes

                def concurrent_identity_read(path, *args, **kwargs):
                    caller = inspect.currentframe().f_back
                    if (path == target and caller.f_code.co_name in ('identity', 'v330_identity')
                            and caller.f_globals.get('__name__') == 'comparison_history'):
                        target.write_bytes(other)
                        try:
                            return real_read(path, *args, **kwargs)
                        finally:
                            target.write_bytes(original)
                    return real_read(path, *args, **kwargs)

                with patch.object(Path, 'read_bytes', concurrent_identity_read):
                    document, rendered = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(document['outcome'], 'composed', document)
                self.assertEqual(target.read_bytes(), original)
                self.assertEqual(rendered['composed/HEADER.yaml'], expected['composed/HEADER.yaml'])

    def test_the_selected_tier_uses_the_captured_appetite_despite_an_interleaved_file_descriptor(self):
        actual = source_roots()
        with tempfile.TemporaryDirectory(prefix='synthetic-appetite-capture-') as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, signature_boundary(root)):
                fixture = whole_fixture(root, actual)
                target = fixture['adopter'] / 'party.yaml'
                original = target.read_bytes()
                changed = copy.deepcopy(fixture['party'])
                changed['appetite']['tolerance']['amount'] = 1000
                other = yaml.safe_dump(changed).encode()
                stable, _ = fixture['ct'].compose(fixture['adopter'], fixture['trees'])

                def effect(document):
                    self.assertEqual(document['outcome'], 'composed', document)
                    return next(p for p in document['prices'] if p.get('kind') == 'feed'
                                and p.get('source') == 'feeds'
                                and p.get('name') == 'threat-register')['publisher_reliability_effect']

                expected = effect(stable)
                self.assertEqual(expected['effective']['tier'], 'restricted')
                real_open = builtins.open

                def concurrent_open(file, *args, **kwargs):
                    caller = inspect.currentframe().f_back
                    if (isinstance(file, (str, bytes, os.PathLike)) and Path(file) == target
                            and caller.f_code.co_name == 'appetite_money'):
                        target.write_bytes(other)
                        stream = real_open(file, *args, **kwargs)
                        replacement = target.parent / 'restore-captured-party.yaml'
                        replacement.write_bytes(original)
                        os.replace(replacement, target)
                        return stream
                    return real_open(file, *args, **kwargs)

                with patch.object(builtins, 'open', concurrent_open):
                    document, _ = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(target.read_bytes(), original)
                self.assertEqual(effect(document), expected)

    def test_the_consumed_policy_and_recorded_blob_use_the_same_captured_bytes(self):
        actual = source_roots()
        with tempfile.TemporaryDirectory(prefix='synthetic-policy-capture-') as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, signature_boundary(root)):
                fixture = whole_fixture(root, actual)
                target = fixture['adopter'] / 'party.yaml'
                accepted = copy.deepcopy(fixture['party'])
                accepted['appetite']['publisher_reliability'][0]['bar'] = '-20'
                original = yaml.safe_dump(accepted).encode()
                changed = copy.deepcopy(accepted)
                changed['appetite']['publisher_reliability'][0]['bar'] = '-10'
                other = yaml.safe_dump(changed).encode()
                target.write_bytes(original)
                read_text = Path.read_text
                read_bytes = Path.read_bytes

                def concurrent_middle_read(read, path, caller, *args, **kwargs):
                    if (path == target and caller.f_code.co_name == 'load_document'
                            and caller.f_globals.get('__name__') == '_publisher_quality_party'):
                        # A controlled actual temporary-file edit, restored
                        # before the outer reader can observe a changed file.
                        target.write_bytes(other)
                        try:
                            return read(path, *args, **kwargs)
                        finally:
                            target.write_bytes(original)
                    return read(path, *args, **kwargs)

                def concurrent_text(path, *args, **kwargs):
                    return concurrent_middle_read(read_text, path, inspect.currentframe().f_back,
                                                  *args, **kwargs)

                def concurrent_bytes(path, *args, **kwargs):
                    return concurrent_middle_read(read_bytes, path, inspect.currentframe().f_back,
                                                  *args, **kwargs)

                with patch.object(Path, 'read_text', concurrent_text), patch.object(
                        Path, 'read_bytes', concurrent_bytes):
                    document, _ = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(document['outcome'], 'composed', document)
                entry = next(p for p in document['prices'] if p.get('kind') == 'feed'
                             and p.get('source') == 'feeds' and p.get('name') == 'threat-register')
                effect = entry['publisher_reliability_effect']
                self.assertEqual(target.read_bytes(), original)
                self.assertEqual(effect['bar'], '-20')
                self.assertEqual(effect['causes'], [])
                self.assertEqual(entry['amount'], 10)
                self.assertEqual(effect['policy_source']['git_blob'], hashlib.sha1(
                    b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest())

    def test_a_worse_full_distribution_consumes_the_publishers_target_in_actual_composition(self):
        actual = source_roots()
        with tempfile.TemporaryDirectory(prefix='synthetic-price-vertical-') as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, signature_boundary(root)):
                fixture = whole_fixture(root, actual)
                self.assertEqual(fixture['forecast']['distribution'], {
                    'kind': 'weighted-empirical/v1', 'total_count': 2,
                    'atoms': [{'value': '10', 'count': 2}]})
                self.assertEqual(fixture['resolution']['observed'], '30')
                self.assertEqual(fixture['report']['reports'][0]['score'],
                                 {'numerator': '-20', 'denominator': '1'})
                document, rendered = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(document['outcome'], 'composed', document)
                entry = next(p for p in document['prices'] if p.get('kind') == 'feed'
                             and p.get('source') == 'feeds' and p.get('name') == 'threat-register')
                effect = entry['publisher_reliability_effect']
                self.assertEqual(effect['causes'], ['score-below-bar'])
                self.assertEqual(effect['base']['uncaged_price'], '10')
                self.assertEqual(effect['effective']['uncaged_price'], '40')
                self.assertEqual(effect['base']['tier'], 'baseline')
                self.assertNotEqual(effect['effective']['tier'], 'baseline')
                self.assertEqual(effect['effective']['scenario']['warn']['lef'], [1, 1, 1])
                self.assertEqual(effect['financial_as_of'], '2019-11-02')
                self.assertEqual(effect['reliability_evidence_as_of'], '2021-02-01T00:00:00Z')
                self.assertEqual(entry['old_version'], entry['new_version'])
                self.assertEqual(entry['old_price'], entry['new_price'])
                self.assertIn('Publisher monetary quality', rendered['composed/HANDBOOK.md'])
                self.assertIn('score-below-bar', rendered['composed/HANDBOOK.md'])
                self.assertFalse(any(p.get('name') == 'publisher-reliability'
                                     for p in document['prices']))

                # The same authenticated report meets an equal bar; it also
                # supplies no score cause below the adopter's explicit min_n.
                policy = fixture['party']['appetite']['publisher_reliability'][0]
                for bar, minimum, state in [('-20', 1, 'accepted'), ('-10', 2, 'insufficient')]:
                    with self.subTest(bar=bar, minimum=minimum):
                        policy.update(bar=bar, minimum_cases=minimum)
                        (fixture['adopter'] / 'party.yaml').write_text(yaml.safe_dump(fixture['party']))
                        fresh, _ = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                        self.assertEqual(fresh['outcome'], 'composed', fresh)
                        selected = next(p for p in fresh['prices'] if p.get('source') == 'feeds'
                                        and p.get('kind') == 'feed' and p.get('name') == 'threat-register')
                        view = selected['publisher_reliability_effect']
                        self.assertEqual(view['state'], state)
                        self.assertEqual(view['causes'], [])
                        self.assertEqual(view['base']['uncaged_price'], '10')
                        self.assertEqual(view['effective']['uncaged_price'], '10')

                policy.update(bar='-10', minimum_cases=1)
                (fixture['adopter'] / 'party.yaml').write_text(yaml.safe_dump(fixture['party']))
                saved, files = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(saved['outcome'], 'composed', saved)
                for relative, content in files.items():
                    destination = fixture['adopter'] / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(content)
                offline = {key: value for key, value in fixture['trees'].items()
                           if key.startswith('fixture-')}
                self.assertEqual(fixture['ct'].verify(fixture['adopter'], offline), (True, []))
                closure = fixture['adopter'] / 'composed/publisher-reliability/sources.json'
                original = closure.read_bytes()
                corrupted = json.loads(original)
                corrupted['sources']['nist']['pack_sha256'] = '0' * 64
                closure.write_text(json.dumps(corrupted))
                ok, reasons = fixture['ct'].verify(fixture['adopter'], offline)
                self.assertFalse(ok, 'altered portable source evidence was accepted')
                self.assertIn('publisher-reliability', str(reasons))
                closure.write_bytes(original)

    def test_authentic_degraded_release_still_widens_without_any_resolved_case(self):
        actual = source_roots()
        with tempfile.TemporaryDirectory(prefix='synthetic-degraded-price-') as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, signature_boundary(root)):
                fixture = whole_fixture(root, actual, degraded=True, unresolved=True)
                row = fixture['report']['reports'][0]
                self.assertIsNone(row['score'])
                self.assertIsNone(row['loss'])
                self.assertEqual(row['counts']['eligible'], 0)
                document, _ = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(document['outcome'], 'composed', document)
                entry = next(p for p in document['prices'] if p.get('source') == 'feeds'
                             and p.get('kind') == 'feed' and p.get('name') == 'threat-register')
                view = entry['publisher_reliability_effect']
                self.assertEqual(view['causes'], ['release-degraded'])
                self.assertEqual(view['effective']['uncaged_price'], '40')
                self.assertIsNone(view['score'])

    def test_an_unauthenticated_predecessor_cannot_supply_the_native_release_proof(self):
        actual = source_roots()
        with tempfile.TemporaryDirectory(prefix='synthetic-price-predecessor-') as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, signature_boundary(root)):
                fixture = whole_fixture(root, actual)
                with patch.dict(os.environ, {'PAVC_SYNTHETIC_REJECT_TAG': 'threat-register/v3.0.0'}):
                    refused, _ = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(refused['outcome'], 'refused', refused)
                self.assertIn('pinned identity/issuer', str(refused['party_artefact_errors']))
                restored, _ = fixture['ct'].compose(fixture['adopter'], fixture['trees'])
                self.assertEqual(restored['outcome'], 'composed', restored)


if __name__ == '__main__':
    unittest.main()
