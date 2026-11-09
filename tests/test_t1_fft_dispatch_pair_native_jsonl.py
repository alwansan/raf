"""Real PersistentDiagnosticLog operation/detail envelope, synthetic values only.

This is a source-contract test of the T1 hook's emitted JSONL shape; NO Unity,
GPU or Android phone execution is claimed.
"""
import unittest

from scripts.t1_fft_dispatch_pair_audit import AFTER, BEFORE, audit


def native(event, seq=1, session="20261109T000000000-abcd1234", log_seq=90,
           before_suffix="", after_suffix=""):
    if event == BEFORE:
        detail = (
            f"sequence={seq}; source_sha_prefix=8aa32937d423"
            "; original_findkernel_callsite_present=false"
            "; shader_instance_session_local=-9; shader_present=True"
            "; original_exponent=8; inferred_bank_only=source_bank0_candidate"
            "; pass_offset=0; numeric_kernel_argument=6"
            "; group_xyz=1,256,1; unity_compute_supported=True"
            "; frame=199; realtime_s=64.050"
            "; original_runtime_mapping=unverified; gpu_result=unverified"
            + before_suffix
        )
    else:
        detail = (
            f"sequence={seq}; managed_dispatch_call_returned=true"
            "; unity_error_callback_may_follow=true"
            "; gpu_result=unverified; water_rendering=unverified"
            + after_suffix
        )
    return {"utc": "2026-11-09T00:00:00Z", "session": session,
            "sequence": log_seq, "thread": 1, "area": "water",
            "operation": event, "detail": detail}


class NativeLoggerContract(unittest.TestCase):
    def test_actual_persisted_envelope_is_counted_not_ignored(self):
        before = native(BEFORE, log_seq=101)
        after = native(AFTER, log_seq=104)
        report = audit([
            {"operation": "fft_device_compute_limits", "detail": "x=y"},
            before, after,
        ])
        self.assertEqual(report["before_count"], 1)
        self.assertEqual(report["returned_count"], 1)
        self.assertEqual(report["paired_count"], 1)
        self.assertEqual(report["errors"], [])
        self.assertFalse(report["gpu_execution_proven"])
        self.assertFalse(report["runtime_kernel_identity_proven"])

    def test_global_logger_sequence_never_replaces_dispatch_call_sequence(self):
        report = audit([native(BEFORE, seq=2, log_seq=900),
                        native(AFTER, seq=2, log_seq=904)])
        self.assertEqual(report["paired_count"], 1)
        self.assertEqual(report["missing_return_sequences"], [])

    def test_top_level_logger_session_rejects_cross_session_pair(self):
        report = audit([native(BEFORE, session="first"),
                        native(AFTER, session="second")])
        self.assertEqual(report["paired_count"], 0)
        self.assertIn("cross_session_provenance:session_id:1", report["errors"])
        self.assertIn("identity_mismatch:1:session_id", report["errors"])

    def test_late_session_change_invalidates_earlier_native_pairs(self):
        report = audit([
            native(BEFORE, seq=1, session="first", log_seq=1),
            native(AFTER, seq=1, session="first", log_seq=2),
            native(BEFORE, seq=2, session="second", log_seq=3),
            native(AFTER, seq=2, session="second", log_seq=4),
        ])
        self.assertEqual(report["paired_count"], 0)
        self.assertEqual(report["missing_return_sequences"], [1, 2])

    def test_synthetic_after_cannot_close_real_before(self):
        before = native(BEFORE, session="first")
        after = {"event": AFTER, "message": "sequence=1;session_id=first"}
        report = audit([before, after])
        self.assertEqual(report["paired_count"], 0)
        self.assertIn("identity_mismatch:1:__trace_schema", report["errors"])

    def test_original_derived_sha_marker_is_checked(self):
        before = native(BEFORE)
        before["detail"] = before["detail"].replace("source_sha_prefix=8aa32937d423",
                                                      "source_sha_prefix=abcdef123456")
        with self.assertRaisesRegex(ValueError, "source marker drift"):
            audit([before])

    def test_missing_original_logger_session_fails_closed(self):
        before = native(BEFORE)
        del before["session"]
        with self.assertRaisesRegex(ValueError, "missing original logger session"):
            audit([before])

    def test_bad_group_shape_fails_closed(self):
        before = native(BEFORE)
        before["detail"] = before["detail"].replace("group_xyz=1,256,1",
                                                      "group_xyz=2,256,1")
        with self.assertRaisesRegex(ValueError, "before group_xyz"):
            audit([before])

    def test_real_hook_event_with_wrong_area_is_not_a_water_event(self):
        before = native(BEFORE)
        before["area"] = "input"
        with self.assertRaisesRegex(ValueError, "logger area"):
            audit([before])

    def test_conflicting_synthetic_and_persisted_envelopes_fail_closed(self):
        before = native(BEFORE)
        before["event"] = BEFORE
        with self.assertRaisesRegex(ValueError, "mixed trace envelopes"):
            audit([before])


if __name__ == "__main__":
    unittest.main()
