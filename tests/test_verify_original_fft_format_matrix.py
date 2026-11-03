"""Synthetic format matrix tests; no original proprietary game assets."""
import unittest
from scripts.verify_original_fft_format_matrix import analyze_formats

MODES = [
    dict(two_channels=False, high_precision=False, render_texture_format="RGHalf"),
    dict(two_channels=False, high_precision=True, render_texture_format="RGFloat"),
    dict(two_channels=True, high_precision=False, render_texture_format="ARGBHalf"),
    dict(two_channels=True, high_precision=True, render_texture_format="ARGBFloat"),
]


class FftStorageFormatMatrixTests(unittest.TestCase):
    def test_roundtrip_rgba32f_does_not_certify_other_three(self):
        result = analyze_formats(MODES, 1)
        self.assertEqual(result["exact_typed_view_format_candidates"], ["ARGBFloat"])
        self.assertEqual(set(result["typed_format_not_exact_for_original_modes"]),
                         {"RGHalf", "RGFloat", "ARGBHalf"})
        self.assertFalse(result["build_ready"])
        self.assertFalse(result["adreno_supported_features_proven"])

    def test_other_typed_storage_formats_have_distinct_candidates(self):
        for enum, name in ((7, "RGHalf"), (6, "RGFloat"), (2, "ARGBHalf")):
            with self.subTest(enum=enum):
                self.assertEqual(analyze_formats(MODES, enum)["exact_typed_view_format_candidates"], [name])

    def test_formatless_storage_output_requires_gpu_feature_check(self):
        result = analyze_formats(MODES, 0)
        self.assertTrue(result["untyped_output_requires_formatless_storage_image_feature_check"])
        self.assertEqual(result["exact_typed_view_format_candidates"], [])
        self.assertFalse(result["requested_unity_format_equals_actual_vk_image_view_format_proven"])

    def test_spirv_capability_and_vulkan_device_feature_are_not_conflated(self):
        modes = analyze_formats(MODES, 6)["mode_matrix"]
        self.assertEqual([m["requested_unity_format"] for m in modes
                          if m["spirv_storage_image_extended_formats_capability"]],
                         ["RGHalf", "RGFloat"])
        self.assertEqual([m["requested_unity_format"] for m in modes
                          if m["vulkan_extended_formats_feature_guarantees_storage_support"]],
                         ["RGHalf"])
        self.assertEqual([m["requested_unity_format"] for m in modes
                          if m["vulkan_core_mandatory_storage_format"]],
                         ["RGFloat", "ARGBHalf", "ARGBFloat"])
        self.assertEqual([m["requested_unity_format"] for m in modes
                          if m["per_format_storage_query_if_vulkan_feature_absent"]],
                         ["RGHalf"])

    def test_reject_duplicate_and_forged_mode(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            analyze_formats(MODES[:3] + [MODES[2]], 1)
        invalid = [dict(x) for x in MODES]
        invalid[0]["render_texture_format"] = "ARGBFloat"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            analyze_formats(invalid, 1)

    def test_reject_unknown_image_enum_and_boolean_ints(self):
        with self.assertRaises(ValueError):
            analyze_formats(MODES, 999)
        invalid = [dict(x) for x in MODES]
        invalid[0]["two_channels"] = 0
        with self.assertRaisesRegex(ValueError, "Invalid"):
            analyze_formats(invalid, 1)


if __name__ == "__main__":
    unittest.main()
