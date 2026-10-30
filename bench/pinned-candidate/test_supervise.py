"""The foreground invocation seam must stop its own child at the memory bound."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('supervise', Path(__file__).with_name('supervise.py'))
assert spec is not None and spec.loader is not None
supervise = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervise)

class ResourceCageTests(unittest.TestCase):
    def test_small_child_crossing_memory_cap_is_terminated(self):
        with tempfile.TemporaryDirectory() as directory:
            result = supervise.run(
                [sys.executable, '-c', 'import time; memory=bytearray(64*1024**2); time.sleep(10)'],
                Path(directory) / 'capture', rss_cap_bytes=48*1024**2, timeout_seconds=8)
            self.assertEqual(result['termination_reason'], 'rss-cap')
            self.assertNotEqual(result['returncode'], 0)
            self.assertGreater(result['peak_sampled_rss_bytes'], 48*1024**2)
            self.assertLess(result['wall_seconds'], 8)

if __name__ == '__main__':
    unittest.main()
