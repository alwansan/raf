"""Synthetic-only SPIR-V image op/capability profile tests."""
import struct
import unittest
from scripts.probe_fft_spirv_operation_profile import (
    image_operation_profile, compare_image_operation_profiles)


def spv(commands, bound=30):
    words = [0x07230203, 0x00010000, 0, bound, 0]
    for op, values in commands:
        words.extend([(len(values) + 1) << 16 | op, *values])
    return struct.pack("<" + "I" * len(words), *words)


def original_module():
    return spv([
        (17, [56]), (22, [1, 32]),
        (25, [2, 1, 1, 0, 0, 0, 2, 0]),
        (99, [8, 12, 18]),
        (95, [3, 4, 6, 7]),
    ])


class OriginalSpirvOperationTests(unittest.TestCase):
    def test_original_unknown_storage_write_capability(self):
        result = image_operation_profile(original_module())
        self.assertEqual(result["unknown_format_storage_image_type_count"], 1)
        self.assertEqual(result["op_image_write_count"], 1)
        self.assertEqual(result["op_image_fetch_count"], 1)
        self.assertTrue(result["storage_image_write_without_format_capability_declared"])
        self.assertTrue(result["module_contains_unknown_storage_and_image_write"])
        self.assertFalse(result["enabled_device_feature_or_exact_operand_binding_proven"])

    def test_roundtrip_explicit_format_is_reported_not_equated(self):
        rewritten = spv([
            (17, [1]), (22, [1, 32]),
            (25, [2, 1, 1, 0, 0, 0, 2, 1]), (99, [8, 12, 18])
        ])
        diff = compare_image_operation_profiles(
            image_operation_profile(original_module()),
            image_operation_profile(rewritten))
        self.assertFalse(diff["same_image_operation_and_capability_counts"])
        self.assertFalse(diff["shader_equivalence_or_device_execution_verified"])
        self.assertIn("storage_image_write_without_format_capability_declared",
                      [entry["field"] for entry in diff["numeric_profile_drift"]])

    def test_no_write_does_not_imply_formatless_write(self):
        m = spv([(25, [2, 1, 1, 0, 0, 0, 2, 0])])
        d = image_operation_profile(m)
        self.assertFalse(d["module_contains_unknown_storage_and_image_write"])

    def test_invalid_boundary_magic_and_capability_fail_closed(self):
        for data in (
            b"hello",
            original_module()[:-4],
            b"WHAT" + original_module()[4:],
            spv([(17, [1, 2])]),
        ):
            with self.subTest(data=data[:8]), self.assertRaises(ValueError):
                image_operation_profile(data)

    def test_image_write_instruction_count_guard(self):
        with self.assertRaisesRegex(ValueError, "operation"):
            image_operation_profile(spv([(99, [1, 2])]))

    def test_profiles_agree_when_identical_but_not_gpu_proof(self):
        p = image_operation_profile(original_module())
        comparison = compare_image_operation_profiles(p, p)
        self.assertTrue(comparison["same_image_operation_and_capability_counts"])
        self.assertFalse(comparison["shader_equivalence_or_device_execution_verified"])


if __name__ == "__main__":
    unittest.main()
