"""T2: synthetic public-report boundary regression; never loads private game assets."""
import json
import unittest

from scripts.t2_foam_texture_identity import original_texture_rows, compare_private_names


class FoamPublicReportBoundaryTests(unittest.TestCase):
    def test_serialized_report_has_only_expected_public_fields(self):
        original = {"m_CommonParameters": {"m_TextureParams": [
            {"m_NameIndex": 1, "m_Index": 3, "m_SamplerIndex": 2},
            {"m_NameIndex": 2, "m_Index": 4, "m_SamplerIndex": -1},
        ]}}
        rows = original_texture_rows(original, {1: "PRIVATE_TEXTURE_ALPHA",
                                                 2: "PRIVATE_TEXTURE_BETA"}, 2)
        report = compare_private_names(rows, ["PRIVATE_TRANSLATED_X", "PRIVATE_TRANSLATED_Y"])
        serialized = json.dumps(report, sort_keys=True)
        self.assertEqual(set(report), {
            "source_texture_count", "original_complete_numeric_pairs",
            "original_distinct_numeric_pairs", "numeric_pair_identity_to_spirv_verified",
            "translated_image_count", "literal_original_to_spirv_image_name_matches",
            "original_numeric_field_presence_counts",
            "original_multisampled_field_present_count",
            "literal_name_equality_is_shaderlab_upload_proof",
            "original_texture_index_unit_or_sampler_state_verified",
            "private_source_names_disclosed",
        })
        self.assertEqual(report["original_complete_numeric_pairs"], 1)
        self.assertFalse(report["numeric_pair_identity_to_spirv_verified"])
        for secret in ("PRIVATE_TEXTURE_ALPHA", "PRIVATE_TEXTURE_BETA",
                       "PRIVATE_TRANSLATED_X", "PRIVATE_TRANSLATED_Y",
                       "_private_numeric_pair", "digest", "sha256", "hmac"):
            self.assertNotIn(secret, serialized.lower() if secret in ("digest", "sha256", "hmac") else serialized)

    def test_disabled_sampler_cannot_be_promoted_by_serialization(self):
        rows = original_texture_rows(
            {"m_CommonParameters": {"m_TextureParams": [
                {"m_NameIndex": 1, "m_Index": 3, "m_SamplerIndex": -1}]}},
            {1: "SECRET"}, 1)
        roundtrip = json.loads(json.dumps(compare_private_names(rows, ["OTHER"])))
        self.assertEqual(roundtrip["original_complete_numeric_pairs"], 0)
        self.assertEqual(roundtrip["original_distinct_numeric_pairs"], 0)
        self.assertIs(roundtrip["numeric_pair_identity_to_spirv_verified"], False)


if __name__ == "__main__":
    unittest.main()
