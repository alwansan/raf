"""GT no-source synthetic cases for original Spectrum m_KeywordFlags.

Fixtures deliberately do not contain any original source keyword names.
"""
import copy
import hashlib
import unittest

from scripts.gt_spectrum_original_keyword_flags import inspect_flags


def fake():
    return {
        "m_Name": "UltimateWater/Spectrum/Water Spectrum",
        "m_KeywordNames": ["_FAKE_0", "_FAKE_1", "_FAKE_2", "_FAKE_3", "_FAKE_4"],
        "m_KeywordFlags": [0, 1, 2, 3, 4],
        "m_SubShaders": [{"m_Passes": [{} for _ in range(7)]}],
    }


class OriginalKeywordFlagsTests(unittest.TestCase):
    def test_five_source_keyword_flags_are_index_aligned(self):
        result = inspect_flags(fake())
        self.assertEqual(result["original_keyword_index4_flag_byte"], 4)
        self.assertEqual(result["original_keyword_flags_count"], 5)
        self.assertEqual(result["original_passes"], 7)
        self.assertEqual(result["original_keyword_flag_bytes_sha256"],
                         hashlib.sha256(bytes([0, 1, 2, 3, 4])).hexdigest())
        self.assertFalse(result["original_flag_byte_to_global_local_semantics_proven"])
        self.assertFalse(result["original_material_keyword_selection_proven"])

    def test_unsigned_byte_array_is_accepted_without_interpreting_bits(self):
        f = fake()
        f["m_KeywordFlags"] = bytes([255, 0, 3, 1, 128])
        result = inspect_flags(f)
        self.assertEqual(result["original_keyword_index4_flag_byte"], 128)
        self.assertFalse(result["unity_or_adreno_pixels_verified"])

    def test_missing_flag_array_rejected(self):
        f = fake()
        del f["m_KeywordFlags"]
        with self.assertRaisesRegex(ValueError, "missing_or_wrong_length"):
            inspect_flags(f)

    def test_fewer_flag_rows_rejected(self):
        f = fake()
        f["m_KeywordFlags"] = [1, 2, 3, 4]
        with self.assertRaisesRegex(ValueError, "missing_or_wrong_length"):
            inspect_flags(f)

    def test_untrusted_flag_bytes_rejected(self):
        for invalid in (-1, 256, 2.5, True, "1"):
            with self.subTest(invalid=invalid):
                f = fake()
                f["m_KeywordFlags"][4] = invalid
                with self.assertRaisesRegex(ValueError, "outside_uint8"):
                    inspect_flags(f)

    def test_duplicate_names_rejected(self):
        f = fake()
        f["m_KeywordNames"][4] = f["m_KeywordNames"][3]
        with self.assertRaisesRegex(ValueError, "name_index_ambiguous"):
            inspect_flags(f)

    def test_original_name_invalid_rejected(self):
        f = fake()
        f["m_KeywordNames"][4] = ""
        with self.assertRaisesRegex(ValueError, "name_row_invalid"):
            inspect_flags(f)

    def test_only_seven_passes_accepted(self):
        f = fake()
        f["m_SubShaders"][0]["m_Passes"].pop()
        with self.assertRaisesRegex(ValueError, "pass_structure_changed"):
            inspect_flags(f)

    def test_unexpected_shader_rejected(self):
        f = fake()
        f["m_Name"] = "Fake"
        with self.assertRaisesRegex(ValueError, "identity_mismatch"):
            inspect_flags(f)


if __name__ == "__main__":
    unittest.main()
