"""No original Raft content: synthetic OpExtInstImport/OpExtInst fixtures only."""
import struct
import unittest
from scripts.probe_fft_spirv_extinst_profile import (
    extended_instruction_profile, compare_extended_instruction_profiles)


def string_words(name):
    data = name.encode("utf-8") + b"\x00"
    data += b"\x00" * (-len(data) % 4)
    return list(struct.unpack("<" + "I" * (len(data) // 4), data))


def spv(ops):
    words = [0x07230203, 0x10000, 0, 100, 0]
    for opcode, operands in ops:
        words.extend([(len(operands) + 1) << 16 | opcode, *operands])
    return struct.pack("<" + "I" * len(words), *words)


def imported(instruction_ids, set_id=10, name="GLSL.std.450"):
    ops = [(11, [set_id, *string_words(name)])]
    ops += [(12, [1, 20 + i, set_id, ext_op, 77 + i])
            for i, ext_op in enumerate(instruction_ids)]
    return spv(ops)


class ExtInstProfileTests(unittest.TestCase):
    def test_counts_public_instruction_numbers_not_only_total(self):
        p = extended_instruction_profile(imported([13, 13, 27]))
        self.assertEqual(p["glsl_std_450_numeric_opcode_counts"],
                         {"13": 2, "27": 1})
        self.assertEqual(p["glsl_std_450_instruction_total"], 3)
        self.assertEqual(p["unclassified_extended_instruction_total"], 0)
        self.assertFalse(p["semantic_or_gpu_equivalence_proven"])

    def test_same_total_different_public_opcode_must_be_detected(self):
        a = extended_instruction_profile(imported([13, 27]))
        b = extended_instruction_profile(imported([13, 28]))
        result = compare_extended_instruction_profiles(a, b)
        self.assertTrue(result["same_total_extended_instruction_count"])
        self.assertFalse(result["same_fully_classified_extended_opcode_profile"])
        self.assertEqual(result["public_glsl_std_450_opcode_differences"], [
            {"public_opcode": 27, "original": 1, "roundtrip": 0},
            {"public_opcode": 28, "original": 0, "roundtrip": 1}])

    def test_same_opcode_ids_but_different_operands_not_numeric_proof(self):
        a = extended_instruction_profile(imported([13], set_id=10))
        b = extended_instruction_profile(imported([13], set_id=42))
        result = compare_extended_instruction_profiles(a, b)
        self.assertTrue(result["same_fully_classified_extended_opcode_profile"])
        self.assertFalse(result["mathematical_or_shader_semantic_equivalence_proven"])

    def test_nonstandard_set_never_leaks_name_or_claims_full_comparability(self):
        payload = imported([13], name="PRIVATE_SET_TOKEN")
        p = extended_instruction_profile(payload)
        self.assertEqual(p["unclassified_extended_instruction_total"], 1)
        self.assertEqual(p["glsl_std_450_numeric_opcode_counts"], {})
        self.assertNotIn("PRIVATE_SET_TOKEN", str(p))
        result = compare_extended_instruction_profiles(p, p)
        self.assertFalse(result["same_fully_classified_extended_opcode_profile"])
        self.assertFalse(result["all_extended_opcode_identities_comparable"])

    def test_mixed_public_and_private_set_is_not_fully_classified(self):
        m = spv([(11, [10, *string_words("GLSL.std.450")]),
                 (11, [11, *string_words("Private")]),
                 (12, [1, 20, 10, 18]), (12, [1, 21, 11, 18])])
        p = extended_instruction_profile(m)
        self.assertEqual(p["all_extended_instruction_count"], 2)
        self.assertEqual(p["glsl_std_450_numeric_opcode_counts"], {"18": 1})
        self.assertFalse(p["all_instruction_sets_public_and_classified"])

    def test_forward_import_unresolved_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unresolved extended instruction import"):
            extended_instruction_profile(spv([(12, [1, 20, 10, 18]),
                                              (11, [10, *string_words("GLSL.std.450")])]))

    def test_import_collision_invalid_name_and_bad_header_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate extended instruction"):
            extended_instruction_profile(spv([(11, [10, *string_words("GLSL.std.450")]),
                                              (11, [10, *string_words("PRIVATE")])]))
        with self.assertRaisesRegex(ValueError, "Malformed extended instruction import"):
            extended_instruction_profile(spv([(11, [10, 0x41414141])]))
        with self.assertRaisesRegex(ValueError, "Invalid SPIR-V extension census header"):
            extended_instruction_profile(b"NOPE" + spv([])[4:])
        with self.assertRaisesRegex(ValueError, "Truncated extended instruction"):
            extended_instruction_profile(spv([(11, [10, *string_words("GLSL.std.450")]),
                                              (12, [1, 20, 10])]))

    def test_comparison_rejects_inconsistent_and_boolean_census(self):
        p = extended_instruction_profile(imported([13]))
        with self.assertRaisesRegex(ValueError, "Invalid public"):
            compare_extended_instruction_profiles(p, dict(p, glsl_std_450_numeric_opcode_counts={"13": True}))
        with self.assertRaisesRegex(ValueError, "Inconsistent extended"):
            compare_extended_instruction_profiles(p, dict(p, all_extended_instruction_count=20))


if __name__ == "__main__":
    unittest.main()
