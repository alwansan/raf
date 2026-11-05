"""Synthetic adversarial tests: T2 private original Foam texture literal identity."""
import unittest

from scripts.t2_foam_texture_identity import (
    original_texture_rows, translated_image_names, compare_private_names,
)


def program(rows):
    return {"m_CommonParameters": {"m_TextureParams": rows}}


def tex(index=0, **extra):
    return {"m_NameIndex": index, "m_Index": index, "m_SamplerIndex": -1,
            "m_Dim": 2, "m_MultiSampled": False, **extra}


def reflection(rows):
    return {"separate_images": rows}


class OriginalFoamTextureIdentityTests(unittest.TestCase):
    def test_literal_identity_only_without_emitting_names(self):
        rows = original_texture_rows(program([tex(4), tex(5)]),
                                     {4: "PrivateSourceA", 5: "PrivateSourceB"}, 2)
        images = translated_image_names(reflection([
            {"name": "PrivateSourceB", "set": 0, "binding": 7},
            {"name": "GeneratedTarget", "set": 0, "binding": 6}]),
            2, (("separate_images", 0, 6), ("separate_images", 0, 7)))
        out = compare_private_names(rows, images)
        self.assertEqual(out["literal_original_to_spirv_image_name_matches"], 1)
        self.assertEqual(out["original_numeric_field_presence_counts"]["m_SamplerIndex"], 2)
        self.assertFalse(out["original_texture_index_unit_or_sampler_state_verified"])
        self.assertFalse(out["literal_name_equality_is_shaderlab_upload_proof"])
        self.assertNotIn("PrivateSource", str(out))
        self.assertNotIn("GeneratedTarget", str(out))

    def test_zero_literal_match_is_finding_not_binding_fix(self):
        rows = original_texture_rows(program([tex()]), {0: "OriginalTex"}, 1)
        out = compare_private_names(rows, ["CompilerGeneratedTex"])
        self.assertEqual(out["literal_original_to_spirv_image_name_matches"], 0)
        self.assertFalse(out["literal_name_equality_is_shaderlab_upload_proof"])

    def test_missing_or_unknown_original_name_index_rejected(self):
        for row in ({}, {"m_NameIndex": 22}, {"m_NameIndex": True},
                    {"m_NameIndex": "0"}):
            with self.subTest(row=row), self.assertRaises(ValueError):
                original_texture_rows(program([row]), {0: "A"}, 1)

    def test_original_duplicate_symbols_rejected(self):
        with self.assertRaises(ValueError):
            original_texture_rows(program([tex(0), tex(1)]),
                                  {0: "Shared", 1: "Shared"}, 2)

    def test_original_invalid_numeric_shapes_rejected(self):
        for row in (
            {"m_NameIndex": 0, "m_Index": True},
            {"m_NameIndex": 0, "m_Index": -1},
            {"m_NameIndex": 0, "m_SamplerIndex": -2},
            {"m_NameIndex": 0, "m_ArraySize": 65536},
            {"m_NameIndex": 0, "m_Dim": "2"},
            {"m_NameIndex": 0, "m_MultiSampled": 1},
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                original_texture_rows(program([row]), {0: "A"}, 1)

    def test_missing_common_or_texture_list_rejected(self):
        for obj in ({}, {"m_CommonParameters": {}},
                    {"m_CommonParameters": {"m_TextureParams": {}}}):
            with self.subTest(obj=obj), self.assertRaises(ValueError):
                original_texture_rows(obj, {0: "A"}, 1)

    def test_source_count_drift_rejected(self):
        with self.assertRaises(ValueError):
            original_texture_rows(program([tex()]), {0: "A"}, 0)

    def test_missing_optional_original_numeric_fields_accepted_as_unknown(self):
        rows = original_texture_rows(program([{"m_NameIndex": 3}]), {3: "A"}, 1)
        out = compare_private_names(rows, ["A"])
        self.assertEqual(out["original_numeric_field_presence_counts"]["m_Index"], 0)
        self.assertEqual(out["original_multisampled_field_present_count"], 0)

    def test_translated_image_name_absent_or_malformed_rejected(self):
        for obj in ({"set": 0, "binding": 6},
                    {"set": 0, "binding": 6, "name": ""},
                    {"set": 0, "binding": 6, "name": 5},
                    {"set": True, "binding": 6, "name": "A"},
                    {"set": 0, "binding": 6.0, "name": "A"}):
            with self.subTest(obj=obj), self.assertRaises(ValueError):
                translated_image_names(reflection([obj]), 1,
                                       (("separate_images", 0, 6),))

    def test_duplicate_translated_image_name_rejected(self):
        with self.assertRaises(ValueError):
            translated_image_names(reflection([
                {"set": 0, "binding": 6, "name": "A"},
                {"set": 0, "binding": 7, "name": "A"}]), 2,
                (("separate_images", 0, 6), ("separate_images", 0, 7)))

    def test_image_binding_shift_rejected(self):
        with self.assertRaises(ValueError):
            translated_image_names(reflection([
                {"set": 0, "binding": 12, "name": "A"}]), 1,
                (("separate_images", 0, 6),))

    def test_reflection_image_count_drift_rejected(self):
        with self.assertRaises(ValueError):
            translated_image_names(reflection([]), 1,
                                   (("separate_images", 0, 6),))

    def test_zero_resource_vertex_stage_valid(self):
        rows = original_texture_rows(program([]), {}, 0)
        images = translated_image_names(reflection([]), 0, ())
        self.assertEqual(compare_private_names(rows, images)["source_texture_count"], 0)

    def test_mismatched_identity_lists_rejected(self):
        rows = original_texture_rows(program([tex()]), {0: "A"}, 1)
        with self.assertRaises(ValueError):
            compare_private_names(rows, [])

    def test_repeated_original_numeric_pair_is_not_claimed_as_identity(self):
        rows = original_texture_rows(program([
            {"m_NameIndex": 1, "m_Index": 3, "m_SamplerIndex": 2},
            {"m_NameIndex": 2, "m_Index": 3, "m_SamplerIndex": 2},
        ]), {1: "SourceA", 2: "SourceB"}, 2)
        out = compare_private_names(rows, ["CompiledA", "CompiledB"])
        self.assertEqual(out["original_complete_numeric_pairs"], 2)
        self.assertEqual(out["original_distinct_numeric_pairs"], 1)
        self.assertFalse(out["numeric_pair_identity_to_spirv_verified"])
        self.assertNotIn("SourceA", str(out))

    def test_missing_numeric_pair_excluded_from_complete_count(self):
        rows = original_texture_rows(program([
            {"m_NameIndex": 1, "m_Index": 3},
            {"m_NameIndex": 2, "m_Index": 3, "m_SamplerIndex": -1},
        ]), {1: "SourceA", 2: "SourceB"}, 2)
        out = compare_private_names(rows, ["CompiledA", "CompiledB"])
        self.assertEqual(out["original_complete_numeric_pairs"], 1)
        self.assertEqual(out["original_distinct_numeric_pairs"], 1)
        self.assertEqual(out["original_numeric_field_presence_counts"]["m_SamplerIndex"], 1)
        self.assertFalse(out["numeric_pair_identity_to_spirv_verified"])

    def test_numeric_digest_is_order_independent_within_stage(self):
        rows = original_texture_rows(program([
            {"m_NameIndex": 1, "m_Index": 3, "m_SamplerIndex": 2},
            {"m_NameIndex": 2, "m_Index": 5, "m_SamplerIndex": -1},
        ]), {1: "SourceA", 2: "SourceB"}, 2)
        forward = compare_private_names(rows, ["CompiledA", "CompiledB"])
        backward = compare_private_names(list(reversed(rows)), ["CompiledB", "CompiledA"])
        self.assertEqual(forward["original_numeric_pair_digest_sha256"],
                         backward["original_numeric_pair_digest_sha256"])
        self.assertFalse(forward["numeric_pair_identity_to_spirv_verified"])

    def test_reflection_malformed_kind_rejected(self):
        with self.assertRaises(ValueError):
            translated_image_names({"separate_images": "bad"}, 1, ())
        with self.assertRaises(ValueError):
            translated_image_names(None, 0, ())


if __name__ == "__main__":
    unittest.main()
