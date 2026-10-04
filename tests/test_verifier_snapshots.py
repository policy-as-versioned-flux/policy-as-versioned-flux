"""Temporary adopter probes retain immutable apps objects and dated Git history."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


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
        (self.repo / "apps.yaml").write_text("served digest\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "Served apps fixture")
        self.served = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "tag", "apps/v1.0.0")
        git(self.repo, "update-ref", "refs/remotes/origin/main", self.served)
        (self.repo / "apps.yaml").write_text("proposed digest\n")
        git(self.repo, "commit", "-qam", "Proposed source fixture")
        self.head = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "apps.yaml").write_text("uncommitted bytes must stay out\n")

    def assert_snapshot(self, directory):
        self.assertEqual(git(directory, "rev-parse", "--show-toplevel"), str(directory.resolve()))
        self.assertEqual(git(directory, "rev-parse", "HEAD"), self.head)
        self.assertEqual(git(directory, "rev-parse", "apps/v1.0.0^{commit}"), self.served)
        self.assertEqual(git(directory, "show", "apps/v1.0.0:apps.yaml"), "served digest")
        self.assertEqual(git(directory, "rev-parse", "refs/remotes/origin/main"), self.served)
        self.assertEqual((directory / "apps.yaml").read_text(), "proposed digest\n")

    def test_engine_adopter_probe_preserves_its_real_object_context(self):
        engine = load("snapshot_engine", "verify/engine-pairing/engine_pairing.py")
        estate = engine.Estate.__new__(engine.Estate)
        estate.root, estate.work = self.repo.parent, self.root / "work"
        copied = estate.adopter_copy("fixture", "forward")
        self.assert_snapshot(copied)
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


if __name__ == "__main__":
    unittest.main()
