"""Real PersistentDiagnosticLog operation/detail envelope, synthetic values only.

This is a source-contract test of the T1 hook's emitted JSONL shape; NO Unity,
GPU or Android phone execution is claimed.
"""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.t1_fft_dispatch_pair_audit import AFTER, BEFORE, THREW, MAX_LOG_BYTES, audit, main


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
    elif event == THREW:
        detail = (
            f"sequence={seq}; managed_dispatch_threw=true"
            "; exception_kind=argument"
            "; original_runtime_mapping=unverified"
            "; gpu_result=unverified; water_rendering=unverified"
            + after_suffix
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


    def test_cli_accepts_real_logger_segment_over_legacy_one_mib(self):
        # Persisted Raft segments rotate at 4 MiB, not the former 1 MiB
        # command-line audit limit. Unrelated log rows must be ignored.
        unrelated = json.dumps({"operation": "unrelated", "detail": "x" * 40})
        lines = [unrelated] * 16000 + [
            json.dumps(native(BEFORE, log_seq=16001)),
            json.dumps(native(AFTER, log_seq=16005)),
        ]
        payload = "\n".join(lines) + "\n"
        self.assertGreater(len(payload.encode("utf-8")), 1 * 1024 * 1024)
        self.assertLess(len(payload.encode("utf-8")), MAX_LOG_BYTES)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "raft-one-session.jsonl"
            path.write_text(payload, encoding="utf-8")
            with patch.object(sys, "argv", ["audit", str(path)]):
                output = io.StringIO()
                with redirect_stdout(output):
                    main()
        result = json.loads(output.getvalue())
        self.assertEqual(result["paired_count"], 1)
        self.assertFalse(result["gpu_execution_proven"])

    def test_cli_rejects_segment_larger_than_logger_four_mib_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "oversized.jsonl"
            path.write_bytes(b"x" * (MAX_LOG_BYTES + 1))
            with patch.object(sys, "argv", ["audit", str(path)]):
                with self.assertRaisesRegex(ValueError, "4 MiB"):
                    main()


    def test_persisted_original_exception_is_classified_as_synchronous_failure(self):
        r = audit([native(BEFORE, log_seq=20), native(THREW, log_seq=21)])
        self.assertEqual(r["synchronous_thrown_sequences"], [1])
        self.assertEqual(r["returned_count"], 0)
        self.assertEqual(r["unresolved_no_terminal_sequences"], [])
        self.assertEqual(r["paired_count"], 0)
        self.assertFalse(r["gpu_execution_proven"])

    def test_real_thrown_marker_prevents_fabricated_exception_text_or_kind(self):
        for suffix in ("; exception_kind=OriginalClassName",
                       "; managed_dispatch_threw=false",
                       "; gpu_result=pass",
                       "; original_runtime_mapping=verified"):
            with self.subTest(suffix=suffix):
                bad = native(THREW)
                bad["detail"] += suffix
                with self.assertRaisesRegex(ValueError, "duplicate trace field"):
                    audit([native(BEFORE), bad])
        bad = native(THREW)
        bad["detail"] = bad["detail"].replace("exception_kind=argument",
                                               "exception_kind=CustomNativeShaderException")
        with self.assertRaisesRegex(ValueError, "thrown marker"):
            audit([native(BEFORE), bad])

    def test_real_thrown_wrong_area_or_session_rejected(self):
        thrown = native(THREW)
        thrown["area"] = "diagnostics"
        with self.assertRaisesRegex(ValueError, "logger area"):
            audit([native(BEFORE), thrown])
        thrown = native(THREW, session="other")
        r = audit([native(BEFORE), thrown])
        self.assertEqual(r["paired_count"], 0)
        self.assertIn("cross_session_provenance:session_id:1", r["errors"])

if __name__ == "__main__":
    unittest.main()
