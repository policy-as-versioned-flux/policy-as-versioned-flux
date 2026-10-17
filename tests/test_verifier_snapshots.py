"""Temporary adopter probes retain immutable apps objects and dated Git history."""
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    # These are disposable authored fixtures, never delivery commits.
    return subprocess.check_output([
        "git", "-C", str(repo), "-c", "commit.gpgsign=false",
        "-c", "tag.gpgsign=false", "-c", "core.hooksPath=/dev/null",
        "-c", "user.name=Snapshot fixture", "-c", "user.email=fixture@example.invalid",
        *args], stderr=subprocess.PIPE, text=True).strip()


class VerifierSnapshots(unittest.TestCase):
    def test_mixed_policy_window_still_has_unsupported_pairings(self):
        engine = load("partial_support_engine", "verify/engine-pairing/engine_pairing.py")
        table = ["1.18.2", "1.19.1"]
        self.assertEqual(engine.unsupported_pairing_engines(table, {
            "5.0.0": ["1.18.2"], "6.0.0": ["1.18.2"],
            "7.0.0": ["1.18.2", "1.19.1"]}), ["1.19.1"])
        self.assertEqual(engine.unsupported_pairing_engines(table, {
            "7.0.0": ["1.18.2", "1.19.1"]}), [])
        self.assertEqual(engine.unsupported_pairing_engines(table, {}), [])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "estate" / "fixture"
        self.repo.mkdir(parents=True)
        git(self.repo, "init", "-q")
        git(self.repo, "remote", "add", "origin",
            "https://github.com/policy-as-versioned-fixture/fixture.git")
        (self.repo / "apps.yaml").write_text("served digest\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "Served apps fixture")
        self.served = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "tag", "apps/v1.0.0")
        git(self.repo, "update-ref", "refs/remotes/origin/main", self.served)
        git(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        git(self.repo, "checkout", "-qb", "candidate-source")
        (self.repo / "apps.yaml").write_text("proposed digest\n")
        git(self.repo, "commit", "-qam", "Proposed source fixture")
        self.head = git(self.repo, "rev-parse", "HEAD")
        # The observed clock is reachable only through a remote-tracking ref,
        # newer than the local candidate branch. It must survive the local clone.
        git(self.repo, "checkout", "--detach", self.served)
        (self.repo / "clock.fixture").write_text("Authored fixture, not a live observation\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "Remote-only clock object fixture")
        self.remote_main = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "update-ref", "refs/remotes/origin/main", self.remote_main)
        git(self.repo, "checkout", "candidate-source")
        (self.repo / "apps.yaml").write_text("uncommitted bytes must stay out\n")

    def assert_snapshot(self, directory):
        self.assertEqual(git(directory, "rev-parse", "--show-toplevel"), str(directory.resolve()))
        self.assertEqual(git(directory, "rev-parse", "HEAD"), self.head)
        self.assertEqual(git(directory, "remote", "get-url", "origin"),
                         git(self.repo, "remote", "get-url", "origin"))
        self.assertEqual(git(directory, "rev-parse", "apps/v1.0.0^{commit}"), self.served)
        self.assertEqual(git(directory, "show", "apps/v1.0.0:apps.yaml"), "served digest")
        self.assertEqual(git(directory, "rev-parse", "refs/remotes/origin/main"), self.remote_main)
        self.assertEqual(git(directory, "show", "origin/main:clock.fixture"),
                         "Authored fixture, not a live observation")
        self.assertEqual(git(directory, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/"),
                         git(self.repo, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/"))
        self.assertEqual(git(directory, "symbolic-ref", "refs/remotes/origin/HEAD"),
                         "refs/remotes/origin/main")
        self.assertEqual((directory / "apps.yaml").read_text(), "proposed digest\n")

    def test_engine_adopter_probe_preserves_its_real_object_context(self):
        engine = load("snapshot_engine", "verify/engine-pairing/engine_pairing.py")
        estate = engine.Estate.__new__(engine.Estate)
        estate.root, estate.work = self.repo.parent, self.root / "work"
        copied = estate.adopter_copy("fixture", "forward")
        self.assert_snapshot(copied)
        self.assertEqual((self.repo / "apps.yaml").read_text(), "uncommitted bytes must stay out\n")

    def test_a_source_without_origin_does_not_gain_an_identity(self):
        snapshot = load("snapshot_without_origin", "verify/_snapshot.py")
        git(self.repo, "remote", "remove", "origin")
        dest = self.root / "without-origin"
        snapshot.committed_repository(self.repo, dest)
        self.assertEqual(git(dest, "rev-parse", "HEAD"), self.head)
        self.assertEqual(git(dest, "show", "apps/v1.0.0:apps.yaml"), "served digest")
        origin = subprocess.run(["git", "-C", str(dest), "remote", "get-url", "origin"],
                                capture_output=True, text=True)
        self.assertNotEqual(origin.returncode, 0)
        self.assertEqual((self.repo / "apps.yaml").read_text(), "uncommitted bytes must stay out\n")

    def test_reprice_probe_preserves_context_before_calling_the_composer(self):
        reprice = load("snapshot_reprice", "verify/e2e/step2_reprice.py")

        class BoundaryReached(Exception):
            pass

        def composer(directory, _out, _label):
            self.assert_snapshot(Path(directory))
            raise BoundaryReached

        with patch.object(reprice, "ESTATE", str(self.repo.parent)), \
             patch.object(reprice, "compose", composer), \
             self.assertRaises(BoundaryReached):
            reprice.try_bump("fixture", {"name": "threat-register", "party": "fixture"}, "v1", "v2")


class CompilerForward(unittest.TestCase):
    """Actual grader/CLI/Git seam; composer output is explicitly synthetic, unsigned fixture data."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.estate = self.root / 'estate'
        self.platform, self.adopter = self.estate / 'platform', self.estate / 'fixture'
        self.engine = load('forward_engine', 'verify/engine-pairing/engine_pairing.py')
        for path in [self.platform, self.adopter]:
            path.mkdir(parents=True)
            git(path, 'init', '-q')
        git(self.platform, 'remote', 'add', 'origin', 'https://github.com/fixture/platform.git')
        self.write('platform/engine/kyverno/engine-table.yaml', json.dumps({'versions': []}))
        self.metadata('1.18.2', 'accepted')
        git(self.platform, 'add', '.')
        git(self.platform, 'commit', '-qm', 'Unsigned accepted parent fixture')
        self.accepted = git(self.platform, 'rev-parse', 'HEAD')
        git(self.platform, 'tag', 'v5.0.0')
        self.metadata('1.19.1', 'upstream')
        self.write('platform/compose/composition.py', '''import json, pathlib, subprocess, sys
args = sys.argv
parent = pathlib.Path(args[args.index('--estate-clone')+1]) / 'platform'
pin = json.loads(pathlib.Path('gitops/platform/platform-pin.yaml').read_text())['spec']['ref']
actual = subprocess.check_output(['git','-C',str(parent),'rev-parse','HEAD'],text=True).strip()
if actual != pin['commit']:
    print(json.dumps({'outcome':'refused','refusals':['synthetic wrong implementation parent']})); raise SystemExit(1)
out = pathlib.Path(args[args.index('--out')+1]) / 'composed'
(out/'policies/v5.0.0').mkdir(parents=True)
(out/'HEADER.yaml').write_text(json.dumps({'declared-engine':{'version':'1.19.1'}}))
for file,name in [('policies/v5.0.0/member.yaml','member-5-0-0'),('guard.yaml','guard')]:
    (out/file).write_text(json.dumps({'kind':'ValidatingPolicy','metadata':{'name':name}}))
print(json.dumps({'outcome':'composed','engine':{},'deltas':[
    {'kind':'unsupported-engine','line':line,'perspective':'fixture','engine':{'version':'1.19.1'},
     'controls':[{'source':'nist','control_id':control}], 'amount':None}
    for line,control in [('5.0.0','accepted-policy'),('machinery','accepted-machinery')]]}))
''')
        git(self.platform, 'add', '.')
        git(self.platform, 'commit', '-qm', 'Unsigned upstream compiler fixture')
        self.upstream = git(self.platform, 'rev-parse', 'HEAD')
        self.write('fixture/party.yaml', json.dumps({'party':'fixture','inherits':[{'party':'nist','kind':'controls'}]}))
        self.write('fixture/gitops/engine/kyverno.yaml', json.dumps({'version':'1.19.1'}))
        self.pin = {'kind':'GitRepository','spec':{'url':'https://github.com/fixture/platform',
                    'ref':{'tag':'v5.0.0','commit':self.accepted}}}
        self.save_pin()

    def write(self, path, text):
        target = self.estate / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def metadata(self, engine, prefix):
        support = {'scope':'every-served-body-v1','kyverno':[engine]}
        self.write('platform/distribution/versions.yaml', json.dumps({'spec':{'inputs':[{'versions':[
            {'version':'5.0.0','tested_engines':support}]}]}}))
        self.write('platform/distribution/machinery.yaml', json.dumps({'tested_engines':support}))
        self.write('platform/oscal/component-definition.json', json.dumps({'component-definition':{'components':[
            {'control-implementations':[{'source':'../nist/catalog.json','implemented-requirements':[
                {'control-id':prefix+'-'+label,'props':[{'name':'Check_Id','value':body}]}
                for label,body in [('policy','member'),('machinery','guard')]]}]}]}}))

    def save_pin(self):
        self.write('fixture/gitops/platform/platform-pin.yaml', json.dumps(self.pin))
        git(self.adopter, 'add', '.')
        git(self.adopter, 'commit', '-qm', 'Unsigned adopter source fixture')

    def forward(self):
        with tempfile.TemporaryDirectory(dir=self.root) as temporary:
            estate = self.engine.Estate(self.estate, Path(temporary))
            capture = io.StringIO()
            with patch.object(self.engine, 'ADOPTERS', ('fixture',)), \
                 patch.object(self.engine, 'PLANTED', 'absent-fixture'), contextlib.redirect_stdout(capture):
                self.engine.planted_and_forward(estate)
            self.assertEqual(git(self.platform, 'rev-parse', 'HEAD'), self.upstream)
            self.assertEqual(git(self.adopter, 'status', '--porcelain'), '')
            return capture.getvalue()

    def test_compiler_and_expected_policy_and_machinery_use_the_accepted_parent(self):
        output = self.forward()
        self.assertIn('PASS: fixture (forward', output)
        self.assertIn('unsupported-engine 5.0.0 amount null', output)
        self.assertIn('unsupported-engine machinery amount null', output)
        self.assertNotIn('FAIL:', output)
        # Keep the real grader but restore only its old expected-source choice.
        real_expect = self.engine._expect
        with patch.object(self.engine, '_expect', lambda _tree, *args: real_expect(self.platform, *args)):
            self.assertIn('FAIL: fixture (forward', self.forward())
        real_claimed = self.engine._claimed
        with patch.object(self.engine, '_claimed', lambda _tree, bodies: real_claimed(self.platform, bodies)):
            self.assertIn('FAIL: fixture (forward', self.forward())

    def test_unavailable_or_mismatched_parent_never_falls_back_to_upstream(self):
        for case in ['absent-pin', 'absent-tag', 'mismatched-commit', 'absent-origin', 'wrong-origin']:
            with self.subTest(case=case):
                original = json.loads(json.dumps(self.pin))
                if case == 'absent-pin':
                    git(self.adopter, 'rm', 'gitops/platform/platform-pin.yaml')
                    git(self.adopter, 'commit', '-qm', 'Absent fixture pin')
                elif case == 'absent-tag':
                    self.pin['spec']['ref']['tag'] = 'v99.0.0'; self.save_pin()
                elif case == 'mismatched-commit':
                    self.pin['spec']['ref']['commit'] = self.upstream; self.save_pin()
                elif case == 'absent-origin':
                    git(self.platform, 'remote', 'remove', 'origin')
                else:
                    git(self.platform, 'remote', 'set-url', 'origin', 'https://github.com/other/platform')
                try:
                    output = self.forward()
                    self.assertIn('SKIP: fixture (forward', output)
                    self.assertNotIn('FAIL:', output)
                    self.assertNotIn('PASS: fixture', output)
                finally:
                    self.pin = original
                    self.save_pin_if_changed()
                    if case == 'absent-origin':
                        git(self.platform, 'remote', 'add', 'origin', 'https://github.com/fixture/platform.git')
                    elif case == 'wrong-origin':
                        git(self.platform, 'remote', 'set-url', 'origin', 'https://github.com/fixture/platform.git')

    def save_pin_if_changed(self):
        target = self.adopter / 'gitops/platform/platform-pin.yaml'
        expected = json.dumps(self.pin)
        if not target.exists() or target.read_text() != expected:
            self.save_pin()

    def test_real_retirement_still_refuses_the_original_upstream_parent_experiment(self):
        """Actual production refusal before any external verification; no signature-success stand-in."""
        estate = Path(os.environ.get('PAVC_ESTATE_CLONE', str(ROOT / '.estate-clone')))
        platform, ludlow = estate / 'platform', estate / 'ludlow'
        reader = platform / 'compose/consumer_retirement.py'
        if not reader.exists() or not (ludlow / '.git').exists():
            self.skipTest('real platform retirement reader and Ludlow Git source unavailable')
        paths = git(ludlow, 'ls-tree', '-r', '--name-only', 'HEAD', 'implementation-retirements').splitlines()
        if not paths:
            self.skipTest('real Ludlow source carries no consumer retirement')
        record = yaml.safe_load(git(ludlow, 'show', 'HEAD:' + paths[0]))
        parent = record['parent']
        if git(platform, 'rev-parse', 'HEAD') == parent['commit']:
            self.skipTest('served compiler tree already equals the accepted parent; no changed-parent case')
        retirement = load('real_forward_retirement', reader)

        def no_external_verification(*args, **kwargs):
            raise AssertionError('wrong-parent refusal must precede external verification')

        with self.assertRaisesRegex(retirement.InvalidRetirement,
                                    'consumer retirement requires the unchanged pinned implementation tree'):
            retirement.select(ludlow, record, record['party'], record['publisher'],
                              parent['version'], parent['commit'], platform, parent['window'],
                              official=no_external_verification, verify_signature=no_external_verification,
                              verify_tag=no_external_verification)


if __name__ == "__main__":
    unittest.main()
