"""T2: synthetic, source-only regression for the published Foam JSON producer.

This is NOT an authentic DXBC/SPIR-V identity or GPU test.
"""
import json
import unittest

from scripts.t2_foam_texture_identity import compare_private_names


ALLOWED = frozenset({
    "source_texture_count",
    "original_complete_numeric_pairs",
    "original_distinct_numeric_pairs",
    "numeric_pair_identity_to_spirv_verified",
    "translated_image_count",
    "literal_original_to_spirv_image_name_matches",
    "original_numeric_field_presence_counts",
    "original_multisampled_field_present_count",
    "literal_name_equality_is_shaderlab_upload_proof",
    "original_texture_index_unit_or_sampler_state_verified",
    "private_source_names_disclosed",
})
ALLOWED_PRESENCE = frozenset(("m_Index", "m_SamplerIndex", "m_Dim", "m_ArraySize"))


class FoamJSONProductGuard(unittest.TestCase):
    def _row(self, name, pair):
        return {
            "_private_name": name,
            "_private_numeric_pair": pair,
            "_field_presence": {k: True for k in ALLOWED_PRESENCE},
            "_multisample_present": False,
        }

    def test_producer_json_has_only_allowlisted_public_schema(self):
        # Small-domain values deliberately make a public digest reversible.
        source = [self._row("PrivateOriginalSymbolA", (3, 2)),
                  self._row("PrivateOriginalSymbolB", (7, -1))]
        report = compare_private_names(source, ["TranslatedSymbolA", "TranslatedSymbolB"])
        product = json.loads(json.dumps(report, sort_keys=True))
        self.assertEqual(set(product), ALLOWED)
        self.assertEqual(set(product["original_numeric_field_presence_counts"]),
                         ALLOWED_PRESENCE)
        self.assertEqual(product["original_complete_numeric_pairs"], 1)
        self.assertEqual(product["original_distinct_numeric_pairs"], 1)
        self.assertFalse(product["numeric_pair_identity_to_spirv_verified"])
        self.assertFalse(product["literal_name_equality_is_shaderlab_upload_proof"])
        serialized = json.dumps(product, sort_keys=True)
        for secret in ("PrivateOriginalSymbolA", "PrivateOriginalSymbolB",
                       "TranslatedSymbolA", "TranslatedSymbolB",
                       "_private_numeric_pair", "digest", "sha256", "hash"):
            self.assertNotIn(secret, serialized.lower() if secret in ("digest", "sha256", "hash") else serialized)
        self.assertFalse(any(isinstance(v, (list, tuple, dict))
                             for k, v in product.items()
                             if k != "original_numeric_field_presence_counts"))

    def test_missing_numeric_field_cannot_claim_pair(self):
        row = self._row("PrivateA", (3, 2))
        row["_field_presence"]["m_Index"] = False
        with self.assertRaises(ValueError):
            compare_private_names([row], ["TranslatedA"])
        row = self._row("PrivateA", (3, 2))
        row["_field_presence"]["m_SamplerIndex"] = False
        with self.assertRaises(ValueError):
            compare_private_names([row], ["TranslatedA"])

    def test_present_numeric_field_requires_bounded_integer(self):
        for pair in ((None, 2), (3, None), (True, 2), (3, False),
                     (-1, 2), (3, -2), (65536, 2), (3, 65536)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                compare_private_names([self._row("PrivateA", pair)], ["TranslatedA"])

    def test_absent_fields_with_none_are_not_fabricated_pairs(self):
        row = self._row("PrivateA", (None, None))
        row["_field_presence"]["m_Index"] = False
        row["_field_presence"]["m_SamplerIndex"] = False
        report = compare_private_names([row], ["TranslatedA"])
        self.assertEqual(report["original_complete_numeric_pairs"], 0)
        self.assertEqual(report["original_distinct_numeric_pairs"], 0)

    def test_empty_stage_is_safe_and_does_not_claim_binding(self):
        product = json.loads(json.dumps(compare_private_names([], [])))
        self.assertEqual(set(product), ALLOWED)
        self.assertEqual(product["source_texture_count"], 0)
        self.assertEqual(product["original_complete_numeric_pairs"], 0)
        self.assertFalse(product["numeric_pair_identity_to_spirv_verified"])


if __name__ == "__main__":
    unittest.main()
