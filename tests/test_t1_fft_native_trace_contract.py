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

    def test_cross_build_native_return_is_not_accepted(self):
        before = native(BEFORE, BASE + "build_sha=build-a;group_xyz=1,8,1")
        after = native(AFTER, "sequence=1;build_sha=build-b;managed_dispatch_call_returned=true;gpu_result=unverified")
        result = audit([before, after])
        self.assertEqual(result["paired_count"], 0)
        self.assertFalse(result["gpu_execution_proven"])
        self.assertTrue(any("cross_session_provenance:build_sha" in e for e in result["errors"]))

    def test_native_return_cannot_drop_build_provenance(self):
        before = native(BEFORE, BASE + "build_sha=build-a;group_xyz=1,8,1")
        after = native(AFTER, "sequence=1;managed_dispatch_call_returned=true;gpu_result=unverified")
        result = audit([before, after])
        self.assertEqual(result["paired_count"], 0)
        self.assertTrue(any("cross_session_provenance_presence:build_sha" in e for e in result["errors"]))

    def test_native_synchronous_throw_never_counts_as_dispatch_success(self):
        before = native(BEFORE, BASE + "group_xyz=1,8,1")
        threw = native(THREW, "sequence=1;managed_dispatch_threw=true;"
                       "exception_kind=invalid_operation;original_runtime_mapping=unverified;"
                       "gpu_result=unverified;water_rendering=unverified")
        result = audit([before, threw])
        self.assertEqual(result["paired_count"], 0)
        self.assertEqual(result["synchronous_thrown_sequences"], [1])
        self.assertEqual(result["failed_return_sequences"], [1])
        self.assertFalse(result["gpu_execution_proven"])

    def test_native_return_then_throw_invalidates_previous_pair(self):
        before = native(BEFORE, BASE + "group_xyz=1,8,1")
        after = native(AFTER, "sequence=1;managed_dispatch_call_returned=true;gpu_result=unverified")
        threw = native(THREW, "sequence=1;managed_dispatch_threw=true;"
                       "exception_kind=other;original_runtime_mapping=unverified;"
                       "gpu_result=unverified;water_rendering=unverified")
        result = audit([before, after, threw])
        self.assertEqual(result["paired_count"], 0)
        self.assertTrue(any("conflicting_dispatch_terminal" in e for e in result["errors"]))

    def test_native_throw_then_return_cannot_resurrect_dispatch(self):
        before = native(BEFORE, BASE + "group_xyz=1,8,1")
        threw = native(THREW, "sequence=1;managed_dispatch_threw=true;"
                       "exception_kind=argument;original_runtime_mapping=unverified;"
                       "gpu_result=unverified;water_rendering=unverified")
        after = native(AFTER, "sequence=1;managed_dispatch_call_returned=true;gpu_result=unverified")
        result = audit([before, threw, after])
        self.assertEqual(result["paired_count"], 0)
        self.assertTrue(any("conflicting_dispatch_terminal" in e for e in result["errors"]))

    def test_native_return_cannot_claim_verified_findkernel(self):
        before = native(BEFORE, BASE + "group_xyz=1,8,1")
        after = native(AFTER, "sequence=1;managed_dispatch_call_returned=true;"
                       "gpu_result=unverified;original_runtime_mapping=verified")
        with self.assertRaisesRegex(ValueError, "contradictory original FFT evidence marker"):
            audit([before, after])

    def test_native_throw_cannot_claim_water_rendering_success(self):
        before = native(BEFORE, BASE + "group_xyz=1,8,1")
        threw = native(THREW, "sequence=1;managed_dispatch_threw=true;"
                       "exception_kind=other;original_runtime_mapping=unverified;"
                       "gpu_result=unverified;water_rendering=verified")
        with self.assertRaisesRegex(ValueError, "synchronous thrown marker"):
            audit([before, threw])

    def test_native_return_cannot_claim_findkernel_callsite_present(self):
        before = native(BEFORE, BASE + "group_xyz=1,8,1")
        after = native(AFTER, "sequence=1;managed_dispatch_call_returned=true;"
                       "gpu_result=unverified;original_findkernel_callsite_present=true")
        with self.assertRaisesRegex(ValueError, "contradictory original FFT evidence marker"):
            audit([before, after])

if __name__ == "__main__":
    unittest.main()
