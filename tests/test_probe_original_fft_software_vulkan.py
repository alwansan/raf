"""Schema and fail-closed controls for private A1 Vulkan execution results.

Never loads original game shaders or serialized LFS sources in unit tests.
"""
import json
import unittest
from scripts.probe_original_fft_software_vulkan import parse_private_numeric_result

PREFIX = "RAFT_A1_VULKAN_DIFF "


def example():
    return {
        "cpu_software_vulkan": True,
        "rgba32f_linear_only": True,
        "extent_width": 8,
        "extent_height": 1,
        "original_written_pixels": 8,
        "roundtrip_written_pixels": 8,
        "write_coverage_mismatch_pixels": 0,
        "nonfinite_components": 0,
        "max_abs_difference": 0.0,
        "relative_l2_difference": 0.0,
        "within_selected_tolerance": True,
        "synthetic_canary_verified": True,
        "unity_gpu_or_android_device_verified": False,
    }


def encoded(row):
    return PREFIX + json.dumps(row)


class PrivateExecutorResultTests(unittest.TestCase):
    def test_known_correct_synthetic_result_is_accepted_without_device_claim(self):
        row = parse_private_numeric_result(encoded(example()))
        self.assertTrue(row["cpu_software_vulkan"])
        self.assertFalse(row["unity_gpu_or_android_device_verified"])

    def test_known_wrong_synthetic_result_is_not_a_fake_match(self):
        row = dict(example(), max_abs_difference=0.5,
                   relative_l2_difference=0.25,
                   within_selected_tolerance=False)
        self.assertFalse(parse_private_numeric_result(encoded(row))[
            "within_selected_tolerance"])

    def test_missing_or_duplicate_records_are_rejected(self):
        for output in ("", "some log\n", encoded(example())+"\n"+encoded(example())):
            with self.subTest(output=output[:20]), self.assertRaises(ValueError):
                parse_private_numeric_result(output)

    def test_zero_writes_never_prove_numeric_equivalence(self):
        row = dict(example(), original_written_pixels=0)
        with self.assertRaisesRegex(ValueError, "image writes"):
            parse_private_numeric_result(encoded(row))
        row = dict(example(), roundtrip_written_pixels=0)
        with self.assertRaisesRegex(ValueError, "image writes"):
            parse_private_numeric_result(encoded(row))

    def test_invalid_platform_assertions_and_bool_numbers_rejected(self):
        for changed in (
            {"cpu_software_vulkan": False},
            {"rgba32f_linear_only": False},
            {"unity_gpu_or_android_device_verified": True},
            {"original_written_pixels": True},
            {"within_selected_tolerance": 1},
            {"extent_width": 999},
        ):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                parse_private_numeric_result(encoded(dict(example(), **changed)))

    def test_nonfinite_or_overflow_numeric_results_rejected(self):
        for changed in (
            {"relative_l2_difference": float("nan")},
            {"max_abs_difference": -1},
            {"max_abs_difference": float("inf")},
            {"relative_l2_difference": "0"},
        ):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                parse_private_numeric_result(encoded(dict(example(), **changed)))

    def test_false_tolerance_when_pixel_mismatch_reported(self):
        for changed in (
            {"write_coverage_mismatch_pixels": 1},
            {"nonfinite_components": 1},
            {"max_abs_difference": 0.9},
            {"relative_l2_difference": 0.1},
        ):
            with self.subTest(changed=changed), self.assertRaisesRegex(
                    ValueError, "Inconsistent"):
                parse_private_numeric_result(encoded(dict(example(), **changed)))

    def test_no_unknown_schema_fields_can_leak_private_data(self):
        row = dict(example(), original_shader_text="private shader body")
        with self.assertRaisesRegex(ValueError, "schema"):
            parse_private_numeric_result(encoded(row))


if __name__ == "__main__":
    unittest.main()
