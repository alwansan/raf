"""Synthetic isolated SPIR-V arithmetic census; no original game shader bytes."""
import struct
import unittest
from scripts.probe_fft_spirv_math_profile import numeric_opcode_profile, compare_numeric_opcode_profiles


def spv(ops):
    words = [0x07230203, 0x10000, 0, 100, 0]
    for op, operands in ops:
        words.extend([(len(operands) + 1) << 16 | op, *operands])
    return struct.pack("<" + "I" * len(words), *words)


class MathOpcodeCensusTests(unittest.TestCase):
    def test_counts_numeric_conversion_extended_and_control_without_private_identifiers(self):
        m = spv([(129, [1, 8, 5, 7]), (129, [1, 9, 6, 8]),
                 (133, [1, 10, 8, 9]), (115, [1, 11, 10]),
                 (12, [1, 12, 17, 23, 5]), (169, [1, 13, 4, 7, 8]),
                 (250, [18, 24, 25])])
        result = numeric_opcode_profile(m)
        self.assertEqual(result["numeric_opcode_counts"], {
            "f_convert": 1, "float_add": 2, "float_mul": 1})
        self.assertEqual(result["control_opcode_counts"],
                         {"branch_conditional": 1, "select": 1})
        self.assertEqual(result["extended_instruction_count"], 1)
        self.assertFalse(result["private_names_or_operands_disclosed"])
        self.assertFalse(result["shader_numerical_equivalence_or_gpu_execution_proven"])
        self.assertNotIn("17", str(result))
        self.assertNotIn("23", str(result))

    def test_add_replaced_with_sub_is_detected_even_when_total_equal(self):
        a = numeric_opcode_profile(spv([(129, [1, 8, 5, 7])]))
        b = numeric_opcode_profile(spv([(131, [1, 8, 5, 7])]))
        result = compare_numeric_opcode_profiles(a, b)
        self.assertFalse(result["same_tracked_opcode_profile"])
        self.assertEqual({x["opcode"] for x in result["numeric_opcode_count_differences"]},
                         {"float_add", "float_sub"})
        self.assertFalse(result["mathematical_or_shader_semantic_equivalence_proven"])

    def test_same_opcode_histogram_different_operands_never_proves_math(self):
        a = numeric_opcode_profile(spv([(129, [1, 8, 5, 7])]))
        b = numeric_opcode_profile(spv([(129, [1, 8, 5, 5])]))
        result = compare_numeric_opcode_profiles(a, b)
        self.assertTrue(result["same_tracked_opcode_profile"])
        self.assertFalse(result["mathematical_or_shader_semantic_equivalence_proven"])

    def test_extension_or_branch_count_drift_detected(self):
        a = numeric_opcode_profile(spv([(12, [1, 2, 4, 6]), (249, [9])]))
        b = numeric_opcode_profile(spv([(250, [9, 10, 11])]))
        result = compare_numeric_opcode_profiles(a, b)
        self.assertFalse(result["same_extended_instruction_count"])
        self.assertFalse(result["same_control_opcode_counts"])
        self.assertFalse(result["same_tracked_opcode_profile"])

    def test_invalid_binary_and_malformed_tracked_op_fails_closed(self):
        with self.assertRaises(ValueError):
            numeric_opcode_profile(b"BAD!" + spv([])[4:])
        with self.assertRaises(ValueError):
            numeric_opcode_profile(spv([])[:-2])
        with self.assertRaises(ValueError):
            numeric_opcode_profile(spv([(129, [1])]))
        with self.assertRaises(ValueError):
            numeric_opcode_profile(spv([(12, [1, 3, 4])]))
        with self.assertRaises(ValueError):
            numeric_opcode_profile(spv([(245, [1, 2])]))

    def test_profile_dictionary_rejects_bad_counts(self):
        valid = numeric_opcode_profile(spv([]))
        damaged = dict(valid, numeric_opcode_counts={"float_add": True})
        with self.assertRaises(ValueError):
            compare_numeric_opcode_profiles(damaged, valid)
        with self.assertRaises(ValueError):
            compare_numeric_opcode_profiles(valid, dict(valid, extended_instruction_count=-1))


if __name__ == "__main__":
    unittest.main()
