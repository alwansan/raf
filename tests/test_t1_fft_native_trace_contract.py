"""Regression tests for bounded original FFT logger evidence, not GPU proof."""
import unittest
from scripts.t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER, THREW

SESSION = "t1-device-session"
BASE = ("sequence=1;source_sha_prefix=8aa32937d423;"
        "original_findkernel_callsite_present=false;"
        "original_runtime_mapping=unverified;gpu_result=unverified;"
        "numeric_kernel_argument=0;original_exponent=8;"
        "shader_instance_session_local=1;pass_offset=0;")
def native(event, detail):
    return {"operation": event, "detail": detail, "area": "water", "session": SESSION}

class NativeTraceContractTests(unittest.TestCase):
    def test_valid_native_return_is_not_gpu_proof(self):
        rows = [native(BEFORE, BASE + "group_xyz=1,8,1"),
                native(AFTER, "sequence=1;managed_dispatch_call_returned=true;gpu_result=unverified")]
        result = audit(rows)
        self.assertEqual(result["paired_count"], 1)
        self.assertFalse(result["gpu_execution_proven"])
        self.assertFalse(result["runtime_kernel_identity_proven"])

    def test_invalid_native_dispatch_groups_rejected(self):
        for group in ("1,0,1", "1,-1,1", "0,8,1", "1,8,0", "1,8", "a,8,1"):
            with self.subTest(group=group):
                with self.assertRaisesRegex(ValueError, "group_xyz"):
                    audit([native(BEFORE, BASE + "group_xyz=" + group)])

    def test_cross_session_native_return_is_not_accepted(self):
        before = native(BEFORE, BASE + "group_xyz=1,8,1")
        after = native(AFTER, "sequence=1;managed_dispatch_call_returned=true;gpu_result=unverified")
        after["session"] = "another-session"
        result = audit([before, after])
        self.assertEqual(result["paired_count"], 0)
        self.assertTrue(any("cross_session_provenance" in e for e in result["errors"]))

    def test_native_return_requires_unverified_gpu(self):
        with self.assertRaisesRegex(ValueError, "returned marker"):
            audit([native(AFTER, "sequence=1;managed_dispatch_call_returned=true;gpu_result=success")])

if __name__ == "__main__":
    unittest.main()
