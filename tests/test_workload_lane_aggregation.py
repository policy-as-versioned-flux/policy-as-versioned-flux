"""Actual shell wrapper and manifest judge; labelled synthetic lane programs only."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANUAL = 'SKIP: a workload lane run started by hand cannot establish a cited pass'
KNOWN = 'SKIP: no scheduled workload sample has landed for the registered instrument'
UNKNOWN = 'SKIP: labelled synthetic new reason which has not been declared'
CHECK = 'verify/served-workloads/verify-served-workloads.sh'


class WorkloadLaneAggregation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in (CHECK, 'talk/truth_manifest.py', 'talk/verify-manifest.txt'):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        for party in ('driftwood', 'tuppence', 'ludlow'):
            path = self.root / '.estate-clone' / party / 'drift/served_apps.py'
            path.parent.mkdir(parents=True)
            path.write_text(
                'import os,sys\n'
                "if sys.argv[1]=='selfcheck': print('ok labelled selfcheck');sys.exit(0)\n"
                f"rc,line=os.environ['LANE_{party.upper()}'].split('|',1)\n"
                'print(line);sys.exit(int(rc))\n')

    def run_wrapper(self, driftwood='0|PASS: synthetic driftwood',
                    tuppence='0|PASS: synthetic tuppence', ludlow='0|PASS: synthetic ludlow'):
        return subprocess.run(['bash', str(self.root / CHECK)], text=True, capture_output=True,
                              env={**os.environ, 'PYTHON': sys.executable,
                                   'PYTHONDONTWRITEBYTECODE': '1',
                                   'LANE_DRIFTWOOD': driftwood, 'LANE_TUPPENCE': tuppence,
                                   'LANE_LUDLOW': ludlow})

    def assert_judge(self, result, expected):
        judged = subprocess.run([sys.executable, str(self.root / 'talk/truth_manifest.py'),
                                 'judge', str(self.root / 'talk/verify-manifest.txt'), CHECK,
                                 result.stdout.splitlines()[-1]], text=True, capture_output=True)
        self.assertEqual(judged.returncode, expected, judged.stdout)

    def test_manual_middle_wait_survives_later_pass_and_is_declared(self):
        result = self.run_wrapper(tuppence='3|' + MANUAL)
        self.assertEqual(result.returncode, 3, result.stdout)
        self.assertIn('PASS: synthetic driftwood', result.stdout)
        self.assertIn('PASS: synthetic ludlow', result.stdout)
        self.assertEqual(result.stdout.splitlines()[-1], MANUAL)
        self.assert_judge(result, 0)

    def test_existing_middle_wait_survives_later_pass(self):
        result = self.run_wrapper(tuppence='3|' + KNOWN)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout.splitlines()[-1], KNOWN)
        self.assert_judge(result, 0)

    def test_all_parties_pass(self):
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.splitlines()[-1].startswith('PASS:'))

    def test_real_failure_dominates_manual_wait_and_later_pass(self):
        result = self.run_wrapper(driftwood='1|FAIL: synthetic actual observation false',
                                  tuppence='3|' + MANUAL)
        self.assertEqual(result.returncode, 1)
        self.assertIn('FAIL: synthetic actual observation false', result.stdout)
        self.assertTrue(result.stdout.splitlines()[-1].startswith('FAIL:'))

    def test_unknown_wait_is_not_admitted(self):
        result = self.run_wrapper(tuppence='3|' + UNKNOWN)
        self.assertEqual(result.returncode, 1)
        self.assertIn(UNKNOWN, result.stdout)

    def test_known_wait_cannot_hide_a_later_unknown_wait(self):
        result = self.run_wrapper(tuppence='3|' + KNOWN, ludlow='3|' + UNKNOWN)
        self.assertEqual(result.returncode, 1)

    def test_later_known_wait_cannot_hide_an_earlier_unknown_wait(self):
        result = self.run_wrapper(driftwood='3|' + UNKNOWN, tuppence='3|' + KNOWN)
        self.assertEqual(result.returncode, 1)

    def test_unexpected_nonzero_exit_is_a_failure(self):
        result = self.run_wrapper(tuppence='2|ERROR: synthetic bad invocation')
        self.assertEqual(result.returncode, 1)


if __name__ == '__main__':
    unittest.main()
