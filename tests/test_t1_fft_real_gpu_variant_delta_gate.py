"""Adversarial source-only fake job log controls; not a private original GPU run."""
import copy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.t1_fft_real_gpu_variant_delta_gate import compare, main


def profile(mismatch, zx, zy):
    return {
        "status": "private_actual_original_spirv_vs_unity_declared_keyed_input_join",
        "actual_direct_original_spirv_trace_source_declared_by_private_producer": True,
        "actual_gpu_copy_input_report_required": True,
        "actual_physical_input_pairs_sha_bound_to_original_private_sidecar": True,
        "android_adreno_water_proven": False,
        "original_runtime_findkernel_mapping_proven": False,
        "unity_gpu_shader_compiled_binary_attested_independently": False,
        "original_and_unity_keyed_trace_site_coverage": [64, 256, 64],
        "diagnostics": [
            {"site": i, "paired_invocations": count,
             "reference_only_invocations": 0, "unity_only_invocations": 0,
             "coordinate_mismatching_invocations": mismatch[i],
             "value_comparison_skipped_after_coordinate_drift": mismatch[i],
             "coordinate_zero_collapse_by_axis": {"x": zx[i], "y": zy[i], "mip": 0},
             "other_coordinate_drift_by_axis": {"x": 0, "y": 0, "mip": 0}}
            for i, count in enumerate((64, 256, 64))],
    }


PRODUCER = {
    "status": "private_original_derived_unity_fft_producer_stage_and_candidate_hashes_checked",
    "private_unity_producer_complete_stage_file_verified": True,
    "private_unity_trace_shader_and_output_physically_sha_bound": True,
    "reported_unity_copyinput_identity_required": True,
    "unity_compiler_shader_binary_independently_attested": False,
    "unity_nunit_stage_file_is_signed_attestation": False,
    "original_authored_runtime_findkernel_proven": False,
    "android_adreno_water_proven": False,
    "original_derived_candidate_slots_physically_sha_bound": 2,
}
IDENTITY = {"unity_backend": "OpenGLCore", "texels_per_input": 32768,
            "source_mismatches": 0, "butterfly_mismatches": 0}
OUTPUT = {"match": True, "compared_written_pixels": 64,
          "write_coverage_mismatch_pixels": 0, "nonfinite_pixels": 0,
          "outside_tolerance_pixels": 0}


def markers(mismatch, zx, zy, variant=False):
    result = {
      "RAFT_T1_REPLAY_LAST_ENTERED_STAGE": "stage=complete",
      "RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN": profile(mismatch, zx, zy),
      "RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER": copy.deepcopy(PRODUCER),
      "RAFT_T1_INPUT_IDENTITY": copy.deepcopy(IDENTITY),
      "RAFT_T1_UNITY_TRACE_OUTPUT_PARITY": copy.deepcopy(OUTPUT),
    }
    if variant:
        result["RAFT_T1_SLOT0_VARIANT"] = "mode=integer_source untouched_vulkan_reference=true"
    return result


def encode(events):
    result = "2026-11-06T20:00:00.000Z Start private engine test\n"
    for key, value in events.items():
        row = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
        result += "2026-11-06T20:36:01.003Z " + key + " " + row + "\n"
    return result


class ActualVariantSafeDeltaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base, self.variant = self.root / "baseline.log", self.root / "integer.log"
        self.a = markers([63, 252, 64], [63, 252, 63], [0, 0, 64])
        self.b = markers([0, 252, 64], [0, 252, 63], [0, 0, 64], variant=True)
        self.save()

    def save(self):
        self.base.write_text(encode(self.a))
        self.variant.write_text(encode(self.b))

    def check(self):
        return compare(self.base, self.variant)

    def test_detect_site0_restored_but_not_full_parity(self):
        x = self.check()
        self.assertEqual(x["baseline_coordinate_mismatch_by_site"], [63, 252, 64])
        self.assertEqual(x["variant_coordinate_mismatch_by_site"], [0, 252, 64])
        self.assertEqual(x["site_coordinate_mismatch_delta_variant_minus_baseline"], [-63, 0, 0])
        self.assertTrue(x["site0_source_integer_variant_reduces_coordinate_drift"])
        self.assertFalse(x["all_three_sites_coordinate_parity_observed"])
        self.assertFalse(x["runtime_findkernel_and_android_adreno_water_proven"])

    def test_variant_no_improvement_is_valid_negative(self):
        self.b["RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN"] = profile([63, 252, 64], [63, 252, 63], [0, 0, 64])
        self.save()
        x = self.check()
        self.assertFalse(x["site0_source_integer_variant_reduces_coordinate_drift"])
        self.assertEqual(x["site_coordinate_mismatch_delta_variant_minus_baseline"], [0, 0, 0])

    def test_regression_is_reported_not_claimed_fixed(self):
        self.b["RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN"] = profile([64, 253, 64], [64, 253, 63], [0, 0, 64])
        self.save()
        x = self.check()
        self.assertFalse(x["variant_not_worse_on_any_site"])
        self.assertEqual(x["site_coordinate_mismatch_delta_variant_minus_baseline"], [1, 1, 0])

    def test_all_required_markers(self):
        for key in list(self.b):
            original = self.b.pop(key)
            self.save()
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check()
            self.b[key] = original

    def test_reject_fake_counterfactual_mode_or_baseline_variant(self):
        for mode in ("mode=promoted_only untouched_vulkan_reference=true",
                     "mode=integer_source untouched_vulkan_reference=false"):
            self.b["RAFT_T1_SLOT0_VARIANT"] = mode
            self.save()
            with self.assertRaises(ValueError):
                self.check()
        self.b["RAFT_T1_SLOT0_VARIANT"] = "mode=integer_source untouched_vulkan_reference=true"
        self.a["RAFT_T1_SLOT0_VARIANT"] = self.b["RAFT_T1_SLOT0_VARIANT"]
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_actual_gpu_identity_must_match(self):
        for field, bad in (("source_mismatches", 1), ("butterfly_mismatches", 2),
                           ("unity_backend", "Vulkan"), ("texels_per_input", 8192)):
            self.b["RAFT_T1_INPUT_IDENTITY"][field] = bad
            self.save()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check()
            self.b["RAFT_T1_INPUT_IDENTITY"][field] = IDENTITY[field]

    def test_direct_spirv_and_candidate_sha_required(self):
        for marker, field, bad in (
            ("RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN",
             "actual_direct_original_spirv_trace_source_declared_by_private_producer", False),
            ("RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER",
             "original_derived_candidate_slots_physically_sha_bound", 1),
            ("RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER",
             "private_unity_trace_shader_and_output_physically_sha_bound", False),
        ):
            old = self.b[marker][field]
            self.b[marker][field] = bad
            self.save()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check()
            self.b[marker][field] = old

    def test_nunit_complete_and_unmodified_unity_output_required(self):
        self.b["RAFT_T1_REPLAY_LAST_ENTERED_STAGE"] = "stage=private_shader_load"
        self.save()
        with self.assertRaises(ValueError):
            self.check()
        self.b["RAFT_T1_REPLAY_LAST_ENTERED_STAGE"] = "stage=complete"
        self.b["RAFT_T1_UNITY_TRACE_OUTPUT_PARITY"]["outside_tolerance_pixels"] = 2
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_incomplete_or_impossible_site_census_rejected(self):
        self.b["RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN"]["diagnostics"][1]["paired_invocations"] = 255
        self.save()
        with self.assertRaises(ValueError):
            self.check()
        self.b["RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN"]["diagnostics"][1]["paired_invocations"] = 256
        self.b["RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN"]["diagnostics"][1]["coordinate_zero_collapse_by_axis"]["x"] = 254
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_duplicates_and_nonfinite_json_rejected(self):
        text = self.variant.read_text()
        self.variant.write_text(text.replace('"unity_backend": "OpenGLCore"',
                                             '"unity_backend": "OpenGLCore", "unity_backend": "OpenGLCore"'))
        with self.assertRaises(ValueError):
            self.check()
        self.variant.write_text(text + text.splitlines()[2] + "\n")
        with self.assertRaises(ValueError):
            self.check()
        self.variant.write_text(text.replace('"texels_per_input": 32768', '"texels_per_input": NaN'))
        with self.assertRaises(ValueError):
            self.check()

    def test_disallow_aliased_logs_and_symlinks(self):
        self.variant.unlink()
        self.variant.hardlink_to(self.base)
        with self.assertRaises(ValueError):
            self.check()
        self.variant.unlink()
        self.variant.symlink_to(self.base)
        with self.assertRaises(ValueError):
            self.check()

    def test_cli_redacts_source_and_run_log(self):
        out = io.StringIO()
        with patch("sys.argv", ["t1-delta", "--baseline-job-log", str(self.base),
                                "--integer-job-log", str(self.variant)]), redirect_stdout(out):
            main()
        text = out.getvalue()
        self.assertIn("RAFT_T1_REAL_GPU_INTEGER_DELTA", text)
        self.assertNotIn(str(self.root), text)
        self.assertNotIn("SV_DispatchThreadID", text)

    def test_cli_failure_never_prints_private_marker(self):
        self.b["RAFT_T1_REPLAY_LAST_ENTERED_STAGE"] = "stage=private_original_compute_secret"
        self.save()
        err = io.StringIO()
        with patch("sys.argv", ["t1-delta", "--baseline-job-log", str(self.base),
                                "--integer-job-log", str(self.variant)]), redirect_stderr(err):
            with self.assertRaises(SystemExit) as failed:
                main()
        self.assertEqual(failed.exception.code, 2)
        self.assertNotIn("private_original_compute_secret", err.getvalue())
        self.assertNotIn(str(self.root), err.getvalue())


if __name__ == "__main__":
    unittest.main()
