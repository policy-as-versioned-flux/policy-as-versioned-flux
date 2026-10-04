"""A declared lane alone cannot establish ownership of a scheduled ledger."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("map_observation_ownership", ROOT / "verify/map-surface/map_surface.py")
assert spec is not None and spec.loader is not None
surface = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = surface
spec.loader.exec_module(surface)


class MapObservationOwnership(unittest.TestCase):
    def test_real_writer_defaults_own_unlanded_ledgers_but_declarations_do_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)

            def git(*args):
                return subprocess.check_output([
                    "git", "-C", str(repo), "-c", "commit.gpgsign=false",
                    "-c", "core.hooksPath=/dev/null", "-c", "user.name=Ownership fixture",
                    "-c", "user.email=fixture@example.invalid", *args], text=True).strip()

            git("init", "-q")
            workflows = repo / ".github/workflows"
            workflows.mkdir(parents=True)
            workflow = workflows / "sample.yml"
            workflow.write_text('env:\n  OBSERVATION_LANE: "drift/workload-samples.jsonl drift/oscal-samples.jsonl"\n'
                                'jobs:\n  sample:\n    steps:\n      - run: |\n'
                                '          python3 drift/served_apps.py sample\n'
                                '          python3 drift/oscal_lane.py collect\n')
            drift = repo / "drift"
            drift.mkdir()
            for name, ledger in (("served_apps.py", "workload-samples.jsonl"),
                                 ("oscal_lane.py", "oscal-samples.jsonl")):
                (drift / name).write_text('from pathlib import Path\nHERE = Path(__file__).resolve().parent\n'
                                         f'LOG = HERE / "{ledger}"\n')
            (drift / 'oscal_lane.py').write_text(
                'from pathlib import Path\nROOT = Path(__file__).resolve().parents[1]\n'
                'HERE = ROOT / "drift"\nLOG = HERE / "oscal-samples.jsonl"\n')
            git("add", ".")
            git("commit", "-qm", "Owned default writers fixture")
            git("update-ref", "refs/remotes/origin/main", "HEAD")
            self.assertEqual(surface.owned_lane_paths(repo),
                             {"drift/workload-samples.jsonl", "drift/oscal-samples.jsonl"})
            # The default is not used when the scheduled caller redirects the output.
            workflow.write_text(workflow.read_text().replace(' sample\n', ' sample --out other.jsonl\n'))
            git("commit", "-qam", "Redirected writer fixture")
            git("update-ref", "refs/remotes/origin/main", "HEAD")
            self.assertEqual(surface.owned_lane_paths(repo), {"drift/oscal-samples.jsonl"})
            # A working-copy change and a lane declaration cannot widen observed ownership.
            (drift / "oscal_lane.py").write_text('LOG = "drift/workload-samples.jsonl"\n')
            self.assertEqual(surface.owned_lane_paths(repo), {"drift/oscal-samples.jsonl"})
            git("commit", "-qam", "Missing directory-bound default fixture")
            git("update-ref", "refs/remotes/origin/main", "HEAD")
            self.assertEqual(surface.owned_lane_paths(repo), set())


if __name__ == "__main__":
    unittest.main()
