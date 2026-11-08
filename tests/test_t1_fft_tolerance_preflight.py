"""Invalid FFT tolerances must be rejected before any private pixel capture read."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import t1_fft_first_divergence as module

class TolerancePreflightTests(unittest.TestCase):
    def test_invalid_thresholds_do_not_read_private_captures(self):
        for flag, value in (("--atol", "nan"), ("--rtol", "inf"), ("--atol", "-0.01")):
            with self.subTest(flag=flag, value=value), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                (root / "ref.bin").write_bytes(bytes(16))
                (root / "obs.bin").write_bytes(bytes(16))
                manifest = root / "passes.json"
                manifest.write_text(json.dumps([{"name": "FFT_H", "reference": "ref.bin", "observed": "obs.bin"}]))
                with patch.object(sys, "argv", ["t1_fft_first_divergence.py", str(manifest), flag, value]), \
                     patch.object(module, "read_private_capture", side_effect=AssertionError("capture read")) as reader:
                    with self.assertRaises(SystemExit) as caught:
                        module.main()
                    self.assertEqual(caught.exception.code, 2)
                    reader.assert_not_called()

if __name__ == "__main__":
    unittest.main()
