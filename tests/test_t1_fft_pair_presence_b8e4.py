"""Regression for asymmetric optional FFT dispatch identity fields."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER


def row(event, message):
    return {"event": event, "message": message}


class PairPresence(unittest.TestCase):
    def test_missing_kernel_on_return_is_not_pair(self):
        result = audit([row(BEFORE, "sequence=1;kernel=4"), row(AFTER, "sequence=1")])
        self.assertEqual(result["missing_return_sequences"], [1])
        self.assertIn("identity_mismatch:1:kernel", result["errors"])

    def test_unexpected_resource_on_return_is_not_pair(self):
        result = audit([row(BEFORE, "sequence=1"), row(AFTER, "sequence=1;resource=FFT_A")])
        self.assertIn("identity_mismatch:1:resource", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [1])

    def test_identical_optional_fields_pair(self):
        result = audit([row(BEFORE, "sequence=1;kernel=4;groups_x=2"),
                        row(AFTER, "sequence=1;kernel=4;groups_x=2")])
        self.assertEqual(result["missing_return_sequences"], [])
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["gpu_execution_proven"])

    def test_sequence_only_legacy_trace_still_pairs_without_proof(self):
        result = audit([row(BEFORE, "sequence=1"), row(AFTER, "sequence=1")])
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["runtime_kernel_identity_proven"])


if __name__ == "__main__":
    unittest.main()
