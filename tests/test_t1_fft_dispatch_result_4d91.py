"""T1 FFT Dispatch API return status regressions; no GPU execution claims."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER


def pair(status=None):
    first = {"event": BEFORE, "message": "sequence=1;kernel=FFT_H"}
    suffix = "" if status is None else ";result=" + status
    second = {"event": AFTER, "message": "sequence=1;kernel=FFT_H" + suffix}
    return audit([first, second])


class DispatchReturnStatusTests(unittest.TestCase):
    def test_explicit_return_is_pair_not_gpu_proof(self):
        result = pair("returned")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["missing_return_sequences"], [])
        self.assertFalse(result["gpu_execution_proven"])

    def test_exception_is_not_normal_return(self):
        result = pair("exception")
        self.assertIn("dispatch_result_failure:1", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [1])

    def test_error_is_not_normal_return(self):
        result = pair("error")
        self.assertIn("dispatch_result_failure:1", result["errors"])

    def test_legacy_missing_result_remains_parseable(self):
        result = pair()
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["runtime_kernel_identity_proven"])


if __name__ == "__main__":
    unittest.main()
