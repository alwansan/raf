"""Synthetic regressions for FFT pass and Unity kernel identity pairing."""
import unittest
from scripts.t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER


def row(event, extra):
    return {"event": event, "message": "sequence=1;kernel=FFT_H;" + extra}


class PassIdentityTests(unittest.TestCase):
    def test_different_pass_is_not_a_pair(self):
        result = audit([row(BEFORE, "pass_index=0;bank=0"),
                        row(AFTER, "pass_index=1;bank=0")])
        self.assertIn("identity_mismatch:1:pass_index", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [1])

    def test_different_bank_is_not_a_pair(self):
        result = audit([row(BEFORE, "pass_index=0;bank=0"),
                        row(AFTER, "pass_index=0;bank=1")])
        self.assertIn("identity_mismatch:1:bank", result["errors"])

    def test_different_findkernel_index_is_not_a_pair(self):
        result = audit([row(BEFORE, "find_kernel_result=3;dispatch_kernel=3"),
                        row(AFTER, "find_kernel_result=4;dispatch_kernel=3")])
        self.assertIn("identity_mismatch:1:find_kernel_result", result["errors"])

    def test_missing_dispatch_kernel_is_not_a_pair(self):
        result = audit([row(BEFORE, "dispatch_kernel=3"),
                        row(AFTER, "kernel_index=3")])
        self.assertIn("identity_mismatch:1:dispatch_kernel", result["errors"])

    def test_matching_pass_and_kernel_is_not_gpu_proof(self):
        fields = "pass_index=0;bank=1;fft_size=256;find_kernel_result=3;dispatch_kernel=3"
        result = audit([row(BEFORE, fields), row(AFTER, fields)])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["missing_return_sequences"], [])
        self.assertFalse(result["gpu_execution_proven"])
        self.assertFalse(result["runtime_kernel_identity_proven"])


if __name__ == "__main__":
    unittest.main()
