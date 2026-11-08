"""Full-schema, source-free Foam join tests; never patch the original validator.

This fixture is synthetic, NOT an authenticated original extraction or GPU proof.
"""
import unittest
from copy import deepcopy

from scripts.t2_foam_pass_crosscheck import reconcile
from scripts.t2_foam_shaderfind_return_report import NUMERIC, MATERIAL_NUMERIC, FLAGS_TRUE, FLAGS_FALSE, KINDS, MATERIAL_KINDS, STATUS

def baseline():
    r = {k: 0 for k in NUMERIC + MATERIAL_NUMERIC}
    r.update({k: True for k in FLAGS_TRUE})
    r.update({k: False for k in FLAGS_FALSE})
    r.update({"status": STATUS, "original_compiled_method_bodies_scanned": 19118,
              "original_compiled_IL_instructions_scanned": 491490,
              "original_typed_Shader_Find_calls": 81,
              "exact_source_Foam_name_direct_typed_Shader_Find_calls": 1,
              "original_Foam_source_field_to_Material_ctor_sites": 1})
    r.update({"return_consumer_" + k: int(k == "unproved") for k in KINDS})
    r.update({"material_result_consumer_" + k: int(k == "unproved") for k in MATERIAL_KINDS})
    return r

def aggregate(s0, s1, d0, d1):
    p = "field_api_Graphics_Blit_"
    r = {p + "explicit_sites_pass_" + k: int(k in ("literal0", "literal1"))
         for k in ("literal0", "literal1", "other_literal", "unknown", "mixed")}
    for role, categories, a, b in (("source", ("Texture", "RenderTexture", "unknown"), s0, s1),
                                    ("destination", ("RenderTexture", "null", "unknown"), d0, d1)):
        for k in categories:
            r[p + "explicit_" + role + "_" + k] = int(a == k) + int(b == k)
            r[p + "pass0_" + role + "_" + k] = int(a == k)
            r[p + "pass1_" + role + "_" + k] = int(b == k)
    return r

def sites(s0, s1, d0, d1):
    return {"sites": [{"pass": 0, "source": s0, "destination": d0},
                      {"pass": 1, "source": s1, "destination": d1}]}



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


    def test_original_material_field_read_census_mismatch_fails_closed(self):
        original = full_safe_fixture()
        original["field_api_exact_original_material_field_sites_scanned"] = 1
        with self.assertRaisesRegex(ValueError, "source_exact_original_material_field_API_sites_partial"):
            reconcile(original, sites("RenderTexture", "unknown",
                                      "RenderTexture", "unknown"))

    def test_original_pass0_role_partition_mismatch_fails_closed(self):
        original = full_safe_fixture()
        original["field_api_Graphics_Blit_pass0_source_RenderTexture"] = 0
        with self.assertRaisesRegex(ValueError, "Blit_pass_specific_role_partition_incomplete"):
            reconcile(original, sites("RenderTexture", "unknown",
                                      "RenderTexture", "unknown"))

    def test_original_global_role_partition_mismatch_fails_closed(self):
        original = full_safe_fixture()
        original["field_api_Graphics_Blit_explicit_destination_unknown"] = 0
        with self.assertRaisesRegex(ValueError, "Blit_direct_source_destination_partition_inconsistent"):
            reconcile(original, sites("RenderTexture", "unknown",
                                      "RenderTexture", "unknown"))


if __name__ == "__main__":
    unittest.main()
