"""The readiness CLI's admission seam must refuse contamination and changed bytes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('smoke', Path(__file__).with_name('smoke.py'))
assert spec is not None and spec.loader is not None
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

class AdmissionTests(unittest.TestCase):
    def test_hidden_reference_cannot_enter_prompt(self):
        with self.assertRaisesRegex(ValueError, 'input-only'):
            smoke.make_prompt({'statement': 'A headline', 'source': 'publisher', 'candidates': [], 'expected': {'steep': 'social'}})

    def test_changed_weight_refused_before_runtime_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            import hashlib
            names = ['LICENSE', 'config.json', 'generation_config.json',
                     'model.safetensors.index.json', 'tokenizer.json',
                     'tokenizer_config.json', 'merges.txt', 'vocab.json',
                     'model-00001-of-00003.safetensors',
                     'model-00002-of-00003.safetensors',
                     'model-00003-of-00003.safetensors']
            files = []
            for name in names:
                (root / name).write_bytes(b'original')
                files.append({'path': name, 'bytes': 8,
                              'sha256': hashlib.sha256(b'original').hexdigest()})
            manifest = {'model_id': smoke.MODEL, 'revision': smoke.REVISION, 'files': files}
            smoke.verify_assets(root, manifest)
            (root / 'model-00001-of-00003.safetensors').write_bytes(b'altered!')
            with self.assertRaisesRegex(ValueError, 'asset integrity: model-00001'):
                smoke.verify_assets(root, manifest)

    def test_actual_kernel_network_cage_required(self):
        import subprocess
        import sys
        import platform
        if platform.system() != 'Darwin':
            self.skipTest('Mac kernel cage control; Linux requires its own cage')
        script = str(Path(__file__).with_name('smoke.py'))
        refused = subprocess.run([sys.executable, script, '--probe-only'], capture_output=True)
        self.assertNotEqual(refused.returncode, 0)
        denied = subprocess.run(['/usr/bin/sandbox-exec', '-p',
                                 '(version 1)(allow default)(deny network*)',
                                 sys.executable, script, '--probe-only'], capture_output=True)
        self.assertEqual(denied.returncode, 0, denied.stderr.decode())
        self.assertIn(b'EPERM', denied.stdout)

if __name__ == '__main__':
    unittest.main()
