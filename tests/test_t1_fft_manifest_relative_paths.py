import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

class TestManifestRelativePaths(unittest.TestCase):
    def test_relative_capture_paths(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = struct.pack('<4f', 1, 2, 3, 4)
            (root / 'reference.bin').write_bytes(data)
            (root / 'observed.bin').write_bytes(data)
            manifest = root / 'passes.json'
            manifest.write_text(json.dumps([{'name': 'pass0', 'reference': 'reference.bin', 'observed': 'observed.bin'}]))
            result = subprocess.run([sys.executable, '-m', 'scripts.t1_fft_first_divergence', str(manifest)], cwd=repo, env={**os.environ, 'PYTHONPATH': str(repo)}, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)['all_match'])
