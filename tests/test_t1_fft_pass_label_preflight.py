"""T1 private FFT manifest preflight must reject ambiguous labels before pixel reads."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import t1_fft_first_divergence as module


class PassLabelPreflightTests(unittest.TestCase):
    def _run(self, names):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "ref.bin").write_bytes(bytes(16))
            (root / "obs.bin").write_bytes(bytes(16))
            manifest = root / "passes.json"
            manifest.write_text(json.dumps([
                {"name": name, "reference": "ref.bin", "observed": "obs.bin"}
                for name in names
            ]), encoding="utf-8")
            with patch.object(sys, "argv", ["t1_fft_first_divergence.py", str(manifest)]), \
                 patch.object(module, "read_private_capture", side_effect=AssertionError("private pixels read")) as read:
                with self.assertRaises(SystemExit) as raised:
                    module.main()
                self.assertEqual(raised.exception.code, 2)
                read.assert_not_called()

    def test_duplicate_label_rejected_before_capture(self):
        self._run(["FFT_H", "FFT_H"])

    def test_blank_label_rejected_before_capture(self):
        self._run(["FFT_H", ""])


if __name__ == "__main__":
    unittest.main()
