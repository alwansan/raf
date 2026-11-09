"""Regression: FFT dispatch trace sequences must have one ASCII canonical spelling."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "t1_fft_dispatch_pair_audit.py"
spec = importlib.util.spec_from_file_location("t1_fft_dispatch_pair_audit", MODULE)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


class CanonicalSequenceTest(unittest.TestCase):
    def row(self, event, sequence):
        return {"event": event, "message": "sequence=" + sequence}

    def test_ascii_canonical_pair(self):
        report = audit_module.audit([
            self.row(audit_module.BEFORE, "1"),
            self.row(audit_module.AFTER, "1")])
        self.assertEqual(report["missing_return_sequences"], [])
        self.assertEqual(report["errors"], [])

    def test_leading_zero_rejected(self):
        with self.assertRaises(ValueError):
            audit_module.audit([self.row(audit_module.BEFORE, "01")])

    def test_unicode_decimal_rejected(self):
        with self.assertRaises(ValueError):
            audit_module.audit([self.row(audit_module.BEFORE, "\u0661")])

    def test_zero_rejected(self):
        with self.assertRaises(ValueError):
            audit_module.audit([self.row(audit_module.BEFORE, "0")])


if __name__ == "__main__":
    unittest.main()
