"""Source-free synthetic aggregate controls, not an original GPU run."""
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr

from scripts import t1_fft_coordinate_axis_overlap_gate as mod

BASE = {"coordinate_mismatch_by_site": [63, 252, 64],
        "zero_collapse_x_by_site": [63, 252, 63],
        "zero_collapse_y_by_site": [0, 0, 64]}
VARIANT = {"coordinate_mismatch_by_site": [0, 252, 64],
           "zero_collapse_x_by_site": [0, 252, 63],
           "zero_collapse_y_by_site": [0, 0, 64]}


class FFTAxisOverlapTests(unittest.TestCase):
    def test_exact_site2_overlap_recovered_from_pinned_real_counts(self):
        out = mod.analyze_profiles(BASE, VARIANT)
        for tag in ("baseline_sites", "integer_source_variant_sites"):
            site = out[tag][2]
            self.assertEqual((site["x_y_zero_collapse_overlap_min"],
                              site["x_y_zero_collapse_overlap_max"]), (63, 63))
            self.assertEqual((site["x_or_y_zero_collapse_union_min"],
                              site["x_or_y_zero_collapse_union_max"]), (64, 64))
            self.assertTrue(site["all_coordinate_mismatches_include_y_zero_collapse"])
        self.assertFalse(out["full_fft_numeric_parity_or_android_water_proven"])

    def test_site1_x_only_and_site0_counterfactual(self):
        out = mod.analyze_profiles(BASE, VARIANT)
        self.assertEqual(out["baseline_sites"][1]["x_y_zero_collapse_overlap_max"], 0)
        self.assertTrue(out["baseline_sites"][1]["all_coordinate_mismatches_include_x_zero_collapse"])
        self.assertEqual(out["integer_source_variant_sites"][0]["x_or_y_zero_collapse_union_max"], 0)
        self.assertFalse(out["integer_source_variant_sites"][0]["all_coordinate_mismatches_include_y_zero_collapse"])

    def test_generic_ambiguous_interval_does_not_invent_joint_frequency(self):
        val = mod.bounds(10, 7, 6)
        self.assertEqual((val["x_y_zero_collapse_overlap_min"],
                          val["x_y_zero_collapse_overlap_max"]), (3, 6))
        self.assertFalse(val["overlap_determined_exactly"])

    def test_disjoint_overlaps_allowed(self):
        self.assertEqual(mod.bounds(12, 5, 7)["x_y_zero_collapse_overlap_min"], 0)
        self.assertEqual(mod.bounds(12, 5, 7)["x_or_y_zero_collapse_union_max"], 12)

    def test_overlapping_axis_totals_are_not_separate_mismatches(self):
        self.assertEqual(mod.bounds(64, 63, 64)["x_or_y_zero_collapse_union_max"], 64)

    def test_reject_bool_negative_and_impossible_counts(self):
        for triple in ((True, 1, 1), (10, True, 2), (10, 2, False),
                       (0, 1, 0), (3, 1, 4), (-1, 0, 0),
                       (4, 5, 0), (4, 0.0, 0)):
            with self.subTest(triple=triple), self.assertRaises(ValueError):
                mod.bounds(*triple)

    def test_reject_malformed_profile_shapes_and_missing_axes(self):
        for bad in ({}, {"coordinate_mismatch_by_site": [64]},
                    {**BASE, "zero_collapse_y_by_site": [0, 0]},
                    {**BASE, "zero_collapse_x_by_site": (63, 252, 63)},
                    {**BASE, "coordinate_mismatch_by_site": [63, 252, 65]}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                mod.analyze_profiles(bad, VARIANT)

    def test_logs_validated_via_existing_source_gate(self):
        pair = {"baseline_coordinate_mismatch_by_site": [63, 252, 64],
                "variant_coordinate_mismatch_by_site": [0, 252, 64]}
        with patch.object(mod, "compare", return_value=pair) as check, \
             patch.object(mod, "_profile", side_effect=[BASE, VARIANT]) as prof:
            result = mod.analyze_logs(Path("baseline"), Path("integer"))
            check.assert_called_once()
            self.assertEqual(prof.call_count, 2)
            self.assertTrue(result["integer_source_variant_sites"][2]["overlap_determined_exactly"])

    def test_reject_inconsistent_double_parse(self):
        pair = {"baseline_coordinate_mismatch_by_site": [1, 2, 3],
                "variant_coordinate_mismatch_by_site": [0, 252, 64]}
        with patch.object(mod, "compare", return_value=pair), \
             patch.object(mod, "_profile", side_effect=[BASE, VARIANT]):
            with self.assertRaises(ValueError):
                mod.analyze_logs("a", "b")

    def test_cli_redacts_private_paths_and_invalid_data(self):
        with patch("sys.argv", ["gate", "--baseline-job-log", "/private/secret-baseline",
                                "--integer-job-log", "/private/secret-integer"]), \
             patch.object(mod, "analyze_logs", side_effect=ValueError("PRIVATE PIXELS")), \
             redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as error:
                mod.main()
        self.assertEqual(error.exception.code, 2)
        self.assertNotIn("PRIVATE", err.getvalue())
        self.assertNotIn("secret", err.getvalue())

    def test_cli_safe_aggregate_and_limit_flags(self):
        report = mod.analyze_profiles(BASE, VARIANT)
        with patch("sys.argv", ["gate", "--baseline-job-log", "a",
                                "--integer-job-log", "b"]), \
             patch.object(mod, "analyze_logs", return_value=report), \
             redirect_stdout(io.StringIO()) as out:
            mod.main()
        marker, data = out.getvalue().strip().split(" ", 1)
        self.assertEqual(marker, "RAFT_T1_FFT_AXIS_OVERLAP")
        self.assertFalse(json.loads(data)["individual_shader_invocations_recovered"])


if __name__ == "__main__":
    unittest.main()
