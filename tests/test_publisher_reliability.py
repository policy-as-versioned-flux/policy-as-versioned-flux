"""Actual consumer calls with synthetic Git, reports and a verifier fixture.

These establish refusal paths, not genuine authentication or world outcomes.
"""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
READER = ROOT / 'verify/publisher-reliability/report_check.py'
ORIGIN = 'https://github.com/policy-as-versioned-nist/nist'
TAG = 'publisher-reliability/v1.0.0'
IDENTITY = (r'^https://github\.com/policy-as-versioned-nist/nist/\.github/'
            r'workflows/cut-release\.yml@refs/heads/main$')
ISSUER = 'https://token.actions.githubusercontent.com'
EMPTY: dict = {'kind': 'feed', 'name': 'publisher-reliability', 'version': '1.0.0',
         'published_by': 'nist', 'published_at': '2026-10-17T07:00:00Z',
         'payload': {'schema': 'publisher-reliability/report-v1', 'scorer': 'nist',
                     'as_of': '2026-10-17T07:00:00Z', 'status': 'unmeasured',
                     'claim_scope': {'binary_forecast_scores_only': True,
                                     'publisher_price_accuracy': False, 'price_eligible': False},
                     'counts': {'submitted': 0, 'eligible': 0, 'unscoreable': 0},
                     'losses': {'lower_is_better': True, 'brier': None, 'log_loss': None}}}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(['git', '-C', str(repo), *args], text=True, capture_output=True,
                          check=True, timeout=10).stdout.strip()


class PublisherReportConsumer(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix='report-consumer-fixture-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.repo = self.base / 'estate/nist'
        self.repo.mkdir(parents=True)
        git(self.repo, 'init', '-b', 'main')
        for key, value in [('user.name', 'Fixture'), ('user.email', 'fixture@example.invalid'),
                           ('commit.gpgsign', 'false'), ('tag.gpgsign', 'false')]:
            git(self.repo, 'config', key, value)
        git(self.repo, 'remote', 'add', 'origin', ORIGIN)
        (self.repo / 'README.md').write_text('Synthetic publisher; no actual release.\n')
        self.commit()

    def commit(self) -> None:
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-m', 'fixture')
        git(self.repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')

    def publish(self, value: dict | None = None, checker: str = 'raise SystemExit(0)\n') -> None:
        feed = self.repo / 'publisher-reliability/v1/feed.json'
        feed.parent.mkdir(parents=True, exist_ok=True)
        feed.write_text(json.dumps(EMPTY if value is None else value))
        (feed.parents[1] / 'report.py').write_text(checker)
        self.commit()
        git(self.repo, 'tag', '--no-sign', '-a', TAG, '-m', 'Unsigned verifier fixture')

    def verifier(self, *, code: int = 0, facts: bool = True, extra: str = '') -> dict[str, str]:
        directory = self.base / 'bin'
        directory.mkdir(exist_ok=True)
        output = ('Good signature from fixture\nValidated Git signature: true\n'
                  'Validated Rekor entry: true\nValidated Certificate claims: true\n') if facts else ''
        script = directory / 'gitsign'
        script.write_text(f'#!{sys.executable}\nimport json, os, pathlib, subprocess, sys\n'
                          f'pathlib.Path({str(self.base / "verifier-call.json")!r}).write_text('
                          "json.dumps({'args':sys.argv[1:],'mode':os.environ.get('GITSIGN_REKOR_MODE')}))\n"
                          + extra + f'\nprint({output!r})\nraise SystemExit({code})\n')
        script.chmod(0o755)
        return {**os.environ, 'PATH': str(directory) + os.pathsep + os.environ.get('PATH', '')}

    def publish_money(self, payload: dict, checker: str = 'raise SystemExit(0)\n') -> None:
        # Synthetic routing checker only; whole SDK/compose proof is separate.
        feed = self.repo / 'publisher-reliability/v2/feed.json'
        feed.parent.mkdir(parents=True, exist_ok=True)
        feed.write_text(json.dumps({'kind': 'feed', 'name': 'publisher-reliability',
            'version': '2.0.0', 'published_by': 'nist', 'published_at': payload['cutoff'],
            'payload_schema': 'publisher-reliability/price-payload.schema.json', 'payload': payload}))
        (feed.parents[1] / 'price_report.py').write_text(checker)
        self.commit()
        git(self.repo, 'tag', '--no-sign', '-a', 'publisher-reliability/v2.0.0',
            '-m', 'Unsigned monetary routing fixture')

    def invoke(self, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(READER), '--estate', str(self.repo.parent)],
                              text=True, capture_output=True, env=env, timeout=15)

    def verdict(self, result: subprocess.CompletedProcess[str], code: int, phrase: str) -> None:
        self.assertEqual(result.returncode, code, result.stderr + result.stdout)
        self.assertIn(phrase, result.stdout)
        self.assertTrue(result.stdout.strip().splitlines()[-1].startswith(
            'SKIP:' if code == 3 else 'PASS:' if code == 0 else 'FAIL:'))

    def test_no_report_tag_waits(self) -> None:
        self.verdict(self.invoke(), 3, 'signed publisher-reliability/v<semver> report tag')

    def test_catalogue_tag_does_not_count(self) -> None:
        git(self.repo, 'tag', 'v999.0.0')
        self.verdict(self.invoke(), 3, 'signed publisher-reliability/')

    def test_wrong_origin_cannot_hide_as_empty_wait(self) -> None:
        git(self.repo, 'remote', 'set-url', 'origin', 'https://github.com/foreign/nist')
        self.verdict(self.invoke(), 1, 'canonical NIST origin')

    def test_lightweight_report_tag_rejected(self) -> None:
        git(self.repo, 'tag', TAG)
        self.verdict(self.invoke(), 1, 'annotated and signed')

    def test_catalogue_tag_object_cannot_be_aliased_as_report_publication(self) -> None:
        self.publish()
        git(self.repo, 'tag', '--no-sign', '-a', 'v1.0.0', '-m', 'Synthetic catalogue tag')
        catalogue_object = git(self.repo, 'rev-parse', 'refs/tags/v1.0.0')
        git(self.repo, 'update-ref', 'refs/tags/' + TAG, catalogue_object)
        self.verdict(self.invoke(self.verifier()), 1, 'signed tag name differs')

    def test_tag_must_be_on_served_first_parent_history(self) -> None:
        first = git(self.repo, 'rev-parse', 'HEAD')
        self.publish()
        git(self.repo, 'update-ref', 'refs/remotes/origin/main', first)
        self.verdict(self.invoke(), 1, "served NIST main's first-parent history")

    def test_failed_verification_never_executes_publisher_code(self) -> None:
        marker = self.base / 'publisher-code-ran'
        self.publish(checker=f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        self.verdict(self.invoke(self.verifier(code=1)), 1, 'pinned signature')
        self.assertFalse(marker.exists())

    def test_zero_without_verification_facts_is_rejected(self) -> None:
        self.publish()
        self.verdict(self.invoke(self.verifier(facts=False)), 1, 'pinned signature')

    def test_missing_verifier_is_instrument_absence(self) -> None:
        self.publish()
        directory = self.base / 'only-git'
        directory.mkdir()
        executable = shutil.which('git')
        assert executable is not None
        (directory / 'git').symlink_to(executable)
        self.verdict(self.invoke({**os.environ, 'PATH': str(directory)}), 3, 'instrument missing: gitsign')

    def test_verified_empty_wait_and_exact_trust_arguments(self) -> None:
        self.publish()
        self.verdict(self.invoke(self.verifier()), 3, 'has n=0')
        call = json.loads((self.base / 'verifier-call.json').read_text())
        self.assertEqual(call, {'args': ['verify-tag', TAG,
                                        '--certificate-identity-regexp=' + IDENTITY,
                                        '--certificate-oidc-issuer=' + ISSUER], 'mode': 'offline'})

    def test_monetary_major_selects_its_own_checker_and_keeps_no_cohort_unmeasured(self) -> None:
        # Routing fixture only: this checker is not the whole SDK/compose proof.
        self.publish()
        value = {'kind': 'feed', 'name': 'publisher-reliability', 'version': '2.0.0',
                 'published_by': 'nist', 'published_at': '2026-10-18T17:00:00Z',
                 'payload': {'schema': 'publisher-reliability/price-report-set-v1',
                             'scorer': 'nist', 'cutoff': '2026-10-18T17:00:00Z',
                             'tool': {'source_files': [], 'generator_engine': {
                                 'party': 'platform', 'tag': 'synthetic/v1.0.0',
                                 'commit': '1' * 40, 'path': 'fair/fair.py', 'git_blob': '2' * 40}},
                             'inputs': {'schema': 'publisher-reliability/price-input-set-v1',
                                        'cohorts': []}, 'reports': [],
                             'reason': 'no declared monetary cohorts; no publisher-price accuracy measurement'}}
        feed = self.repo / 'publisher-reliability/v2/feed.json'
        feed.parent.mkdir()
        feed.write_text(json.dumps(value))
        marker = self.base / 'monetary-checker-ran'
        (feed.parents[1] / 'price_report.py').write_text(
            f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        (feed.parents[1] / 'report.py').write_text('raise SystemExit(99)\n')
        self.commit()
        git(self.repo, 'tag', '--no-sign', '-a', 'publisher-reliability/v2.0.0',
            '-m', 'Unsigned monetary routing fixture')
        self.verdict(self.invoke(self.verifier()), 3, 'has no declared monetary cohorts')
        self.assertTrue(marker.is_file(), 'selected immutable monetary checker did not run')

    def test_monetary_cohorts_recompute_without_becoming_a_pooled_adopter_decision(self) -> None:
        payload = json.loads((ROOT / 'tests/fixtures/publisher-reliability-money-synthetic.json').read_text())
        self.publish_money(payload)
        result = self.invoke(self.verifier())
        self.verdict(result, 0, '1 separate monetary cohorts')
        self.assertIn('no pooled score or automatic adopter acceptance',
                      result.stdout)

    def test_mutable_checkout_is_ignored(self) -> None:
        self.publish()
        (self.repo / 'publisher-reliability/v1/feed.json').write_text('invalid mutable JSON')
        (self.repo / 'publisher-reliability/report.py').write_text('raise SystemExit(99)\n')
        self.verdict(self.invoke(self.verifier()), 3, 'has n=0')

    def test_native_recomputation_failure_stays_failure(self) -> None:
        self.publish(checker='raise SystemExit(1)\n')
        self.verdict(self.invoke(self.verifier()), 1, 'provenance/recomputation check failed')

    def test_native_instrument_absence_is_distinct(self) -> None:
        self.publish(checker='raise SystemExit(3)\n')
        self.verdict(self.invoke(self.verifier()), 3, 'instrument unavailable')

    def test_tag_movement_during_verification_rejected(self) -> None:
        self.publish()
        commit = git(self.repo, 'rev-parse', 'HEAD')
        extra = f"subprocess.run(['git','update-ref','refs/tags/{TAG}',{commit!r}], check=True)\n"
        self.verdict(self.invoke(self.verifier(extra=extra)), 1, 'tag changed during signature verification')

    def test_verified_object_is_exact_despite_public_tag_change_and_restore(self) -> None:
        marker = self.base / 'native-A-ran'
        self.publish(checker=f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        captured = git(self.repo, 'rev-parse', 'refs/tags/' + TAG)
        (self.repo / 'publisher-reliability/report.py').write_text('raise SystemExit(99)\n')
        self.commit()
        git(self.repo, 'tag', '--no-sign', '-a', 'replacement', '-m', 'Different unsigned fixture tree')
        replacement = git(self.repo, 'rev-parse', 'refs/tags/replacement')
        log = self.base / 'verified-object.json'
        extra = (f"subprocess.run(['git','-C',{str(self.repo)!r},'update-ref','refs/tags/{TAG}',{replacement!r}], check=True)\n"
                 f"resolved = subprocess.check_output(['git','rev-parse','refs/tags/{TAG}'], text=True).strip()\n"
                 f"pathlib.Path({str(log)!r}).write_text(json.dumps({{'actual':resolved,'captured':{captured!r}}}))\n"
                 f"subprocess.run(['git','-C',{str(self.repo)!r},'update-ref','refs/tags/{TAG}',{captured!r}], check=True)\n")
        self.verdict(self.invoke(self.verifier(extra=extra)), 3, 'has n=0')
        objects = json.loads(log.read_text())
        self.assertEqual(objects['actual'], objects['captured'],
                         'verification and execution selected different tag objects')
        self.assertTrue(marker.is_file(), 'the captured native checker was not exercised')

    def test_selection_captures_object_before_first_parent_check(self) -> None:
        self.publish()
        served = git(self.repo, 'rev-parse', 'HEAD')
        value = copy.deepcopy(EMPTY)
        value['payload'].update(status='measured', counts={'submitted': 1, 'eligible': 1, 'unscoreable': 0},
                                losses={'lower_is_better': True, 'brier': 0.16, 'log_loss': 0.51})
        (self.repo / 'publisher-reliability/v1/feed.json').write_text(json.dumps(value))
        self.commit()
        git(self.repo, 'tag', '--no-sign', '-a', 'off-main', '-m', 'Off-main synthetic report')
        replacement = git(self.repo, 'rev-parse', 'refs/tags/off-main')
        git(self.repo, 'update-ref', 'refs/remotes/origin/main', served)
        env = self.verifier()
        executable = shutil.which('git')
        assert executable is not None
        proxy = self.base / 'bin/git'
        proxy.write_text(f'#!{sys.executable}\nimport subprocess, sys\n'
                         f'result = subprocess.run([{executable!r},*sys.argv[1:]], capture_output=True)\n'
                         "if 'rev-list' in sys.argv and '--first-parent' in sys.argv:\n"
                         f" subprocess.run([{executable!r},'-C',{str(self.repo)!r},'update-ref','refs/tags/{TAG}',{replacement!r}], check=True)\n"
                         'sys.stdout.buffer.write(result.stdout)\nsys.stderr.buffer.write(result.stderr)\n'
                         'raise SystemExit(result.returncode)\n')
        proxy.chmod(0o755)
        self.verdict(self.invoke(env), 3, 'has n=0')

    def test_price_claim_cannot_come_from_binary_report(self) -> None:
        for field in ('publisher_price_accuracy', 'price_eligible'):
            with self.subTest(field=field):
                value = copy.deepcopy(EMPTY)
                value['payload']['claim_scope'][field] = True
                if (self.repo / 'publisher-reliability').exists():
                    git(self.repo, 'tag', '-d', TAG)
                self.publish(value)
                self.verdict(self.invoke(self.verifier()), 1, 'publisher-price accuracy')

    def test_empty_cannot_be_measured_or_have_numeric_loss(self) -> None:
        for change in ({'status': 'measured'}, {'losses': {'lower_is_better': True, 'brier': 0, 'log_loss': 0}}):
            with self.subTest(change=change):
                value = copy.deepcopy(EMPTY)
                value['payload'].update(change)
                if (self.repo / 'publisher-reliability').exists():
                    git(self.repo, 'tag', '-d', TAG)
                self.publish(value)
                self.verdict(self.invoke(self.verifier()), 1, 'empty report must remain unmeasured')

    def test_binary_fixture_pass_preserves_price_boundary(self) -> None:
        value = copy.deepcopy(EMPTY)
        value['payload'].update(status='measured', counts={'submitted': 1, 'eligible': 1, 'unscoreable': 0},
                                losses={'lower_is_better': True, 'brier': 0.16, 'log_loss': 0.51})
        self.publish(value)
        self.verdict(self.invoke(self.verifier()), 0,
                     'publisher-price accuracy and price eligibility are not established')

    def test_registered_waits_do_not_hide_missing_instruments(self) -> None:
        for line, expected in [
            ("SKIP: publisher reliability waits for NIST's signed publisher-reliability/v<semver> report tag", 0),
            ('SKIP: publisher reliability waits for eligible independent forecast/outcome pairs; '
             'signed publisher-reliability/v1.0.0 has n=0, publisher-price accuracy remains unmeasured', 0),
            ('SKIP: publisher reliability instrument missing: gitsign', 1),
            ('SKIP: publisher reliability instrument unavailable in signed native checker', 1),
            ("SKIP: publisher reliability waits for NIST's signed publisher-reliability/v<semver> report tag; instrument missing", 1),
        ]:
            with self.subTest(line=line):
                result = subprocess.run([sys.executable, str(ROOT / 'talk/truth_manifest.py'), 'judge',
                                         str(ROOT / 'talk/verify-manifest.txt'),
                                         'verify/publisher-reliability/verify-publisher-reliability.sh', line],
                                        text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_registered_monetary_wait_names_only_genuine_population_absence(self) -> None:
        for message, expected in [
            ('has no declared monetary cohorts; publisher-price accuracy remains unmeasured', 0),
            ('has no eligible monetary forecast/resolution pairs; publisher-price accuracy remains unmeasured', 0),
            ('has no declared monetary cohorts; publisher-price accuracy remains unmeasured; verifier missing', 1),
        ]:
            with self.subTest(message=message):
                line = 'SKIP: publisher reliability signed publisher-reliability/v2.0.0 ' + message
                result = subprocess.run([sys.executable, str(ROOT / 'talk/truth_manifest.py'), 'judge',
                    str(ROOT / 'talk/verify-manifest.txt'),
                    'verify/publisher-reliability/verify-publisher-reliability.sh', line],
                    text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_actual_wrappers_name_absent_python_and_git(self) -> None:
        for name in ('verify-publisher-reliability.sh', 'verify-publisher-reliability-contract.sh'):
            with self.subTest(wrapper=name):
                copied = self.base / name / 'verify/publisher-reliability' / name
                copied.parent.mkdir(parents=True)
                shutil.copyfile(READER.parent / name, copied)
                binpath = self.base / name / 'bin'
                binpath.mkdir()
                dirname = shutil.which('dirname')
                assert dirname is not None
                (binpath / 'dirname').symlink_to(dirname)
                env = {**os.environ, 'PATH': str(binpath)}
                result = subprocess.run(['/bin/bash', str(copied)], env=env,
                                        text=True, capture_output=True, timeout=10)
                self.verdict(result, 3, 'Python 3')
                # The absolute preferred interpreter must not defeat the absence probe.
                python = self.base / name / '.venv/bin/python'
                python.parent.mkdir(parents=True)
                python.symlink_to(sys.executable)
                shutil.copyfile(READER, copied.parent / 'report_check.py')
                if name.endswith('-contract.sh'):
                    result = subprocess.run(['/bin/bash', str(copied)], env=env,
                                            text=True, capture_output=True, timeout=10)
                    self.verdict(result, 3, 'contract needs git')
                else:
                    estate = self.base / name / '.estate-clone/nist'
                    estate.mkdir(parents=True)
                    result = subprocess.run(['/bin/bash', str(copied)], env=env,
                                            text=True, capture_output=True, timeout=10)
                    self.verdict(result, 3, 'instrument missing: git')


if __name__ == '__main__':
    unittest.main()
