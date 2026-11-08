"""Full-schema, source-free Foam join tests; never patch the original validator.

This fixture is synthetic, NOT an authenticated original extraction or GPU proof.
"""
import unittest
from copy import deepcopy

from scripts.t2_foam_pass_crosscheck import reconcile
from tests.test_t2_foam_shaderfind_return_report import baseline
from tests.test_t2_foam_pass_crosscheck import aggregate, sites


def full_safe_fixture():
    # Complete safe schema supplied by the existing original validator fixture.
    original = baseline()
    prefix = "field_api_"
    original[prefix + "exact_original_material_field_sites_scanned"] = 2
    original["material_linear_original_material_alias_instructions_inspected"] = 2
    original["material_linear_original_material_field_stores"] = 1
    original["material_linear_original_material_unique_field_definition_resolved"] = 1
    original["material_linear_original_material_field_read_instructions"] = 2
    original["material_linear_original_material_field_distinct_reader_methods"] = 1
    original[prefix + "straightline_sites_with_typed_Material_parameter"] = 2
    original[prefix + "straightline_sites_with_Graphics_Material_parameter"] = 2
    original[prefix + "Graphics_material_sites_Blit"] = 2
    original[prefix + "Graphics_Blit_sites_ExplicitPass"] = 2
    original.update(aggregate("RenderTexture", "unknown",
                              "RenderTexture", "unknown"))
    return original


class UnmockedOriginalFoamIntegrationTests(unittest.TestCase):
    def test_complete_safe_schema_reconciles(self):
        original = full_safe_fixture()
        result = reconcile(original, sites("RenderTexture", "unknown",
                                           "RenderTexture", "unknown"))
        self.assertTrue(result["independent_summaries_agree"])
        self.assertEqual(result["pass0"], {"source": "RenderTexture",
                                            "destination": "RenderTexture"})
        self.assertEqual(result["pass1"], {"source": "unknown",
                                            "destination": "unknown"})

    def test_original_authentication_flag_fails_closed(self):
        original = full_safe_fixture()
        original["original_Assembly_CSharp_SHA_authenticated"] = False
        with self.assertRaisesRegex(ValueError, "unauthenticated_original"):
            reconcile(original, sites("RenderTexture", "unknown",
                                      "RenderTexture", "unknown"))

    def test_original_pass_count_fails_closed(self):
        original = full_safe_fixture()
        original["field_api_Graphics_Blit_explicit_sites_pass_literal1"] = 0
        with self.assertRaises(ValueError):
            reconcile(original, sites("RenderTexture", "unknown",
                                      "RenderTexture", "unknown"))

    def test_independent_per_pass_disagreement_fails_closed(self):
        original = full_safe_fixture()
        with self.assertRaisesRegex(ValueError, "disagreement"):
            reconcile(original, sites("RenderTexture", "Texture",
                                      "RenderTexture", "unknown"))

    def test_original_unexpected_field_fails_closed(self):
        original = full_safe_fixture()
        original["raw_private_il"] = "never accepted"
        with self.assertRaisesRegex(ValueError, "unexpected_original_safe_report_shape"):
            reconcile(original, sites("RenderTexture", "unknown",
                                      "RenderTexture", "unknown"))


if __name__ == "__main__":
    unittest.main()
