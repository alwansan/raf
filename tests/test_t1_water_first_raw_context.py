"""Source-free adversarial CL owner first Logcat context controls."""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.t1_water_first_raw_context import (
    authenticate_raw, classify_first_roots, combine, SEGMENT_SHA1, HINTS,
)
from scripts.t1_water_startup_order import SOURCE_CL_COMMIT

BASE = 1794145730000


def event(first, last, count=1):
    return {"count": count, "first_observed_unix_ms": BASE + first,
            "last_observed_unix_ms": BASE + last}


def summary():
    root = {
        "ultimate_water_invalid_pass": event(27_579, 291_986, 74_359),
        "water_fft_invalid_compute_kernel": event(27_581, 291_983, 11_165),
    }
    render = {"ultimate_water_invalid_pass_by_material": {
        "spectrum": 29_700, "foam_global": 44_659,
        "subsurface_blur": 0, "utility_noise": 0,
        "other_ultimate_water": 0,
    }, "invalid_kernel_index_root_lines": {"index_6": 11_165, "other_index": 0}}
    return {
        "schema": 1,
        "session": "20261108-164850-270",
        "target_package": "com.alwansan.raft.androidtest",
        "end_unix_ms": BASE + 300_000,
        "final_error_category_breakdown": root,
        "final_game_milestones": {
            "fmod_bootstrap_log_observed": event(11_759, 11_759),
            "raft_android_early_startup_log_observed": event(20_876, 20_876),
            "world_loaded_message_observed": event(92_065, 92_065),
        },
        "final_render_failure_breakdown": render,
        "stop_time_android_process_exit_info": {
            "final_error_groups": root,
            "final_render_failure_breakdown": render,
            "final_shader_pass_errors_total": 74_359,
            "final_compute_kernel_errors_total": 11_165,
        },
        "performance_statistics": {
            "shader_pass_errors_total_at_last_sample": 73_663,
            "compute_kernel_errors_total_at_last_sample": 11_049,
        },
    }


def synthetic_raw(include_context=True):
    rows = [
        b"11-08 16:49:17.579  123  124 E Unity: Shader Ultimate Water/Spectrum does not have a pass 0\n",
        b"11-08 16:49:17.581  123  124 E Unity: Kernel at index (6) is invalid\n",
        b"11-08 16:49:17.582  999  888 E Unity: at Dx11FFT.Elsewhere() ComputeShader.Dispatch\n",
    ]
    if include_context:
        rows.append(b"11-08 16:49:17.582  123  124 E Unity: at Dx11FFT.Process() / UnityEngine.ComputeShader.Dispatch\n")
    rows.append(b"11-08 16:49:17.583  123  124 E Unity: Ultimate Water Foam Global invalid pass\n")
    return b"".join(rows)


def gitblob(data):
    return hashlib.sha1(("blob %d\0" % len(data)).encode("ascii") + data).hexdigest()


class FirstRawLogcatContextTest(unittest.TestCase):
    def read(self, raw):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "segment.log"
            path.write_bytes(raw)
            authenticate_raw(path, expected_size=len(raw), expected_blob=gitblob(raw))
            return classify_first_roots(path, expected_size=len(raw))

    def test_expected_time_and_hints_without_callsite_proof(self):
        r = self.read(synthetic_raw())
        self.assertEqual(r["first"]["pass_spectrum"]["unix_ms"], BASE + 27_579)
        self.assertEqual(r["first"]["kernel_index_6"]["unix_ms"], BASE + 27_581)
        self.assertTrue(r["first"]["kernel_index_6"]
                        ["nearby_same_pid_tid_100ms_12lines_unattributed_hints"]["dx11fft"])
        self.assertTrue(r["first"]["kernel_index_6"]
                        ["nearby_same_pid_tid_100ms_12lines_unattributed_hints"]["unity_compute_dispatch"])
        self.assertFalse(r["actual_original_unity_dispatch_caller_proven"])
        self.assertNotIn("Dx11FFT.Process", json.dumps(r))
        self.assertEqual(combine(r, summary())["first_kernel_after_first_water_ms_from_raw_segment"], 2)

    def test_real_lograf_iso_date_without_pid_does_not_invent_thread_identity(self):
        raw = (b"2026-11-08 16:49:17.579 E SomeTag: Ultimate Water/Spectrum invalid pass\n"
               b"2026-11-08 16:49:17.581 E SomeTag: Kernel at index (6) is invalid\n"
               b"2026-11-08 16:49:17.582 E SomeTag: Dx11FFT / ComputeShader.Dispatch\n")
        r = self.read(raw)
        self.assertEqual(r["first"]["pass_spectrum"]["unix_ms"], BASE + 27_579)
        self.assertEqual(r["first"]["kernel_index_6"]["unix_ms"], BASE + 27_581)
        self.assertFalse(r["first"]["kernel_index_6"]["android_thread_id_proven"])
        self.assertFalse(r["first"]["kernel_index_6"]["nearby_same_pid_tid_100ms_12lines_unattributed_hints"]["dx11fft"])
        self.assertFalse(r["actual_original_unity_dispatch_caller_proven"])

    def test_first_segment_can_have_water_without_raw_kernel_and_not_fake_mapping(self):
        raw = (b"2026-11-08 16:49:17.579 E SomeTag: Ultimate Water/Spectrum invalid pass\n"
               b"2026-11-08 16:49:17.580 E SomeTag: Dx11FFT.SomeMethod\n")
        r = self.read(raw)
        report = combine(r, summary())
        self.assertFalse(report["first_segment_kernel_root_seen"])
        self.assertFalse(report["kernel_raw_root_vs_summary_verified"])
        self.assertIsNone(report["first_kernel6_unix_ms_from_raw_segment"])
        self.assertEqual(report["first_kernel6_unix_ms_from_pinned_summary_only"], BASE + 27_581)
        self.assertFalse(report["interpretation"]["absence_of_kernel_text_in_this_segment_proves_no_kernel_error"])

    def test_foamglobal_no_separator_is_named_foam_not_generic(self):
        raw = (b"2026-11-08 16:49:17.579 E SomeTag: Ultimate Water/FoamGlobal invalid pass\n"
               b"2026-11-08 16:49:17.581 E SomeTag: Kernel at index (6) is invalid\n")
        r = self.read(raw)
        self.assertEqual(r["observed_first_segment_category_counts"]["pass_foam_global"], 1)
        self.assertEqual(r["observed_first_segment_category_counts"]["pass_other_water"], 0)

    def test_lograf_high_precision_fraction_truncates_not_rounds(self):
        # Source-private LogRaft uses >3 fractional digits. The session
        # summary records integer milliseconds; do not round 999999 up.
        raw = (b"2026-11-08 16:49:17.579999 E SomeTag: Ultimate Water/Spectrum invalid pass\n"
               b"2026-11-08 16:49:17.581999999 E SomeTag: Kernel at index (6) is invalid\n")
        report = combine(self.read(raw), summary())
        self.assertEqual(report["first_water_unix_ms"], BASE + 27_579)
        self.assertEqual(report["first_kernel6_unix_ms_from_raw_segment"], BASE + 27_581)
        self.assertTrue(report["kernel_raw_root_vs_summary_verified"])

    def test_long_malformed_fraction_does_not_forge_timestamp(self):
        raw = (b"2026-11-08 16:49:17.5791234567 E SomeTag: Ultimate Water/Spectrum invalid pass\n"
               b"2026-11-08 16:49:17.581 E SomeTag: Kernel at index (6) is invalid\n")
        report = self.read(raw)
        self.assertEqual(report["unparseable_first_root_lines"], 1)
        with self.assertRaisesRegex(ValueError, "missing first original water"):
            combine(report, summary())

    def test_different_thread_must_not_join_stack_hint(self):
        r = self.read(synthetic_raw(include_context=False))
        self.assertFalse(r["first"]["kernel_index_6"]
                         ["nearby_same_pid_tid_100ms_12lines_unattributed_hints"]["dx11fft"])
        self.assertFalse(r["first"]["kernel_index_6"]
                         ["nearby_same_pid_tid_100ms_12lines_unattributed_hints"]["unity_compute_dispatch"])

    def test_same_line_hint_is_distinct_from_adjacent(self):
        raw = (b"11-08 16:49:17.579 123 124 E Unity: Ultimate Water/Spectrum invalid pass\n"
               b"11-08 16:49:17.581 123 124 E Unity: Dx11FFT: Kernel at index (6) is invalid\n")
        r = self.read(raw)
        self.assertTrue(r["first"]["kernel_index_6"]["direct_same_logcat_line_allowlist_hints"]["dx11fft"])
        # Same-line evidence is NOT counted again as a following-line hint.
        self.assertFalse(r["first"]["kernel_index_6"]["nearby_same_pid_tid_100ms_12lines_unattributed_hints"]["dx11fft"])
        self.assertFalse(r["actual_original_unity_findkernel_proven"])

    def test_small_raw_collector_timestamp_skew_is_reported_not_hidden(self):
        data = summary()
        data["final_error_category_breakdown"]["ultimate_water_invalid_pass"] = event(27_606, 291_986, 74_359)
        data["stop_time_android_process_exit_info"]["final_error_groups"] = data["final_error_category_breakdown"]
        result = combine(self.read(synthetic_raw()), data)
        self.assertEqual(result["first_water_collector_minus_raw_ms"], 27)
        self.assertTrue(result["raw_water_correlates_with_collector_within_250ms"])
        self.assertFalse(result["interpretation"]["raw_log_and_collector_same_exact_record_proven"])

    def test_large_raw_collector_timestamp_skew_rejected(self):
        data = summary()
        data["final_error_category_breakdown"]["ultimate_water_invalid_pass"] = event(27_830, 291_986, 74_359)
        data["stop_time_android_process_exit_info"]["final_error_groups"] = data["final_error_category_breakdown"]
        with self.assertRaisesRegex(ValueError, "too far"):
            combine(self.read(synthetic_raw()), data)

    def test_summary_timestamp_mismatch_rejected(self):
        data = summary()
        data["final_error_category_breakdown"]["water_fft_invalid_compute_kernel"] = event(27_583, 291_983, 11_165)
        data["stop_time_android_process_exit_info"]["final_error_groups"] = data["final_error_category_breakdown"]
        with self.assertRaisesRegex(ValueError, "disagree"):
            combine(self.read(synthetic_raw()), data)

    def test_segment_authentication_tamper_and_size(self):
        raw = synthetic_raw()
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "part.log"
            p.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                authenticate_raw(p, expected_size=len(raw), expected_blob="0" * 40)
            with self.assertRaisesRegex(ValueError, "size"):
                authenticate_raw(p, expected_size=len(raw) + 1, expected_blob=gitblob(raw))
            q = Path(directory) / "link.log"
            q.symlink_to(p)
            with self.assertRaises((ValueError, OSError)):
                authenticate_raw(q, expected_size=len(raw), expected_blob=gitblob(raw))
            q.unlink()
            if hasattr(os, "mkfifo"):
                os.mkfifo(q)
                with self.assertRaises(ValueError):
                    authenticate_raw(q, expected_size=len(raw), expected_blob=gitblob(raw))

    def test_oversize_physical_line_tail_skipped(self):
        raw = (b"A" * 32769
               + b"11-08 16:49:17.560 123 124 E Unity: Kernel at index (6) is invalid\n"
               + synthetic_raw())
        r = self.read(raw)
        self.assertEqual(r["first"]["kernel_index_6"]["unix_ms"], BASE + 27_581)
        self.assertEqual(r["oversize_physical_lines_skipped"], 1)

    def test_wrong_source_digest_blocks_fabricated_summary(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            combine(self.read(synthetic_raw()), summary(), "0" * 64)
        with self.assertRaisesRegex(ValueError, "missing first"):
            combine(self.read(b"11-08 16:49:17.581 123 124 E Unity: Kernel at index (6) is invalid\n"), summary())

    def test_no_implicit_pass_or_kernel_name_via_context(self):
        data = self.read(synthetic_raw())
        result = combine(data, summary())
        self.assertFalse(result["interpretation"]["on_phone_runtime_dispatch_proven"])
        self.assertTrue(result["interpretation"]["raw_log_line_neighborhood_not_proof_of_shared_callsite"])
        self.assertTrue(result["context"]["raw_root_text_exported"] is False)
        self.assertEqual(set(result["context"]["first"]["kernel_index_6"]
                             ["direct_same_logcat_line_allowlist_hints"]), set(HINTS))
        self.assertEqual(result["cl_commit"], SOURCE_CL_COMMIT)


if __name__ == "__main__":
    unittest.main()
