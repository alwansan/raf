"""Cross-sequence original FFT trace provenance regression (metadata only)."""
import unittest

from scripts.t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER

SOURCE = ("source_sha_prefix=8aa32937d423;"
          "original_findkernel_callsite_present=false;"
          "original_runtime_mapping=unverified;gpu_result=unverified;"
          "numeric_kernel_argument=6;original_exponent=8;"
          "shader_instance_session_local=1;pass_offset=0;group_xyz=1,8,1")


def row(operation, seq, build="build-a", session="phone-session"):
    if operation == BEFORE:
        detail = f"sequence={seq};build_sha={build};" + SOURCE
    else:
        detail = (f"sequence={seq};build_sha={build};"
                  "managed_dispatch_call_returned=true;gpu_result=unverified")
    return {"operation": operation, "detail": detail,
            "area": "water", "session": session}


class MultiPairProvenanceTests(unittest.TestCase):
    def test_two_valid_returns_still_do_not_prove_gpu(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1),
                        row(BEFORE, 2), row(AFTER, 2)])
        self.assertEqual(result["paired_count"], 2)
        self.assertFalse(result["gpu_execution_proven"])
        self.assertFalse(result["runtime_kernel_identity_proven"])

    def test_later_foreign_build_invalidates_earlier_valid_pair(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1),
                        row(BEFORE, 2, "build-b"), row(AFTER, 2, "build-b")])
        self.assertEqual(result["paired_count"], 0)
        self.assertTrue(any("cross_session_provenance:build_sha" in x
                            for x in result["errors"]))

    def test_duplicate_before_invalidates_that_sequence_only(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1),
                        row(BEFORE, 1), row(BEFORE, 2), row(AFTER, 2)])
        self.assertEqual(result["paired_count"], 1)
        self.assertTrue(any("duplicate_event:1" in x for x in result["errors"]))

    def test_later_foreign_session_invalidates_earlier_pair(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1),
                        row(BEFORE, 2, session="foreign"),
                        row(AFTER, 2, session="foreign")])
        self.assertEqual(result["paired_count"], 0)
        self.assertTrue(any("cross_session_provenance:session_id" in x
                            for x in result["errors"]))


if __name__ == "__main__":
    unittest.main()
