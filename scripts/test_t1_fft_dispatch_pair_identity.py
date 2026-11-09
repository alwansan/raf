"""Regression tests for bounded T1 dispatch pair metadata (no GPU claims)."""
import unittest
from t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER


def row(event, message):
    return {"event": event, "message": message}


class DispatchPairIdentityTests(unittest.TestCase):
    def test_consistent_kernel_pairs(self):
        result = audit([row(BEFORE, "sequence=1;kernel=FFT_H;groups_x=8"),
                        row(AFTER, "sequence=1;kernel=FFT_H;groups_x=8;result=returned")])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["missing_return_sequences"], [])
        self.assertFalse(result["gpu_execution_proven"])

    def test_different_kernel_does_not_pair(self):
        result = audit([row(BEFORE, "sequence=1;kernel=FFT_H"),
                        row(AFTER, "sequence=1;kernel=FFT_V")])
        self.assertIn("identity_mismatch:1:kernel", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [1])

    def test_different_group_does_not_pair(self):
        result = audit([row(BEFORE, "sequence=2;groups_x=8"),
                        row(AFTER, "sequence=2;groups_x=16")])
        self.assertIn("identity_mismatch:2:groups_x", result["errors"])

    def test_empty_key_or_value_rejected(self):
        for message in ("sequence=1;=bad", "sequence=1;kernel=  "):
            with self.subTest(message=message), self.assertRaises(ValueError):
                audit([row(BEFORE, message)])


if __name__ == "__main__":
    unittest.main()
