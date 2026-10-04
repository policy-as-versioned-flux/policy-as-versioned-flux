"""The clock checkout has Python on PATH, without the hub's local virtualenv."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkloadLaneEntrypoint(unittest.TestCase):
    def test_both_wrappers_reach_adopter_instruments_without_a_local_virtualenv(self):
        for lane, instrument in (("served-workloads", "served_apps.py"),
                                 ("oscal-lane", "oscal_lane.py")):
            with self.subTest(lane=lane), tempfile.TemporaryDirectory() as tmp:
                hub = Path(tmp)
                for name in ("served-workloads", "oscal-lane"):
                    target = hub / "verify" / name
                    target.mkdir(parents=True)
                    shutil.copy(ROOT / "verify" / name / ("verify-" + name + ".sh"), target)
                for party in ("driftwood", "tuppence", "ludlow"):
                    drift = hub / ".estate-clone" / party / "drift"
                    drift.mkdir(parents=True)
                    (drift / instrument).write_text(
                        "from pathlib import Path\nimport sys\n"
                        "with (Path(__file__).parent / 'calls').open('a') as f:\n"
                        "    f.write(sys.argv[1] + '\\n')\n")
                env = dict(os.environ)
                env.pop("PYTHON", None)
                env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
                result = subprocess.run(["bash", str(hub / "verify" / lane /
                                        ("verify-" + lane + ".sh"))], env=env,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for party in ("driftwood", "tuppence", "ludlow"):
                    self.assertEqual((hub / ".estate-clone" / party / "drift" /
                                      "calls").read_text(), "selfcheck\ngrade\n")

    def test_explicit_unavailable_interpreter_still_refuses(self):
        env = {**os.environ, "PYTHON": "/no-such-workload-interpreter"}
        result = subprocess.run(["bash", str(ROOT / "verify/served-workloads/"
                                            "verify-served-workloads.sh")], env=env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn("SKIP: no hub interpreter", result.stdout)
        self.assertNotIn("==>", result.stdout)


if __name__ == "__main__":
    unittest.main()
