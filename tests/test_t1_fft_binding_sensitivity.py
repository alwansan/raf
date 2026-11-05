"""Source-free independent T1 FFT runtime experiment controls."""
import json
import unittest

from scripts.t1_fft_binding_sensitivity import (
    MARKER, PROFILES, assess, read_fingerprint, render_host,
)


class T1BindingSensitivity(unittest.TestCase):
    def test_original_role_swaps_can_be_distinguished(self):
        result = assess({"baseline": "100", "swap_first": "101",
                         "swap_second": "102"})
        self.assertTrue(result["first_pass_input_swap_changes_original_result"])
        self.assertTrue(result["second_pass_input_swap_changes_original_result"])

    def test_equal_outputs_do_not_fabricate_sensitivity(self):
        result = assess({"baseline": "100", "swap_first": "100",
                         "swap_second": "100"})
        self.assertFalse(result["first_pass_input_swap_changes_original_result"])
        self.assertFalse(result["second_pass_input_swap_changes_original_result"])

    def test_no_missing_or_fabricated_modes(self):
        for modes in ({}, {"baseline": "10", "swap_first": "11"},
                      {"baseline": "10", "swap_first": "11",
                       "swap_second": "12", "swap_both": "13"}):
            with self.assertRaises(ValueError):
                assess(modes)

    def test_negative_numeric_report_controls(self):
        valid = {"profile": "baseline", "checksum": "155", "same_source_comparator": True}
        self.assertEqual(read_fingerprint(MARKER + json.dumps(valid), "baseline"), "155")
        corrupt = [
            {"profile": "wrong", "checksum": "155", "same_source_comparator": True},
            {"profile": "baseline", "checksum": "NaN", "same_source_comparator": True},
            {"profile": "baseline", "checksum": "-5", "same_source_comparator": True},
            {"profile": "baseline", "checksum": "0", "same_source_comparator": True},
            {"profile": "baseline", "checksum": "18446744073709551616",
             "same_source_comparator": True},
            {"profile": "baseline", "checksum": "155", "same_source_comparator": False},
            {"profile": "baseline", "checksum": "155", "same_source_comparator": True,
             "unity_gpu_verified": True},
        ]
        for row in corrupt:
            with self.subTest(row=row), self.assertRaises(ValueError):
                read_fingerprint(MARKER + json.dumps(row), "baseline")
        with self.assertRaises(ValueError):
            read_fingerprint((MARKER + json.dumps(valid) + "\n") * 2, "baseline")

    def test_bounded_source_transform_rejects_unexpected_harness(self):
        with self.assertRaises(ValueError):
            render_host("some tiny file")
        with self.assertRaises(ValueError):
            render_host("p" * 120_000)

    def test_real_inherited_harness_anchors_only(self):
        from pathlib import Path
        path = Path("scripts/a1_fft_two_pass_vulkan.cpp")
        if path.is_file():
            original = path.read_text()
            transformed = render_host(original)
            self.assertIn("swap_first", transformed)
            self.assertIn("swap_second", transformed)
            self.assertEqual(transformed.count("RAFT_T1_BINDING_FINGERPRINT"), 1)
            self.assertEqual(original.count("RAFT_T1_BINDING_FINGERPRINT"), 0)


if __name__ == "__main__":
    unittest.main()
