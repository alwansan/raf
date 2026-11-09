"""T2 Foam original texture/sampler resources vs translated ABI, synthetic controls."""
import unittest

from scripts.t2_foam_resource_abi import (
    STAGES, safe_compiled_resources, combine,
    verify_genuine_texture_sampler_pair_count, ORIGINAL_TEXTURES_PER_STAGE,
    COMPILED_NUMERIC_RESOURCE_BINDINGS,
)


def source(row=0):
    return {
        "table_rows": {"m_TextureParams": row, "m_SamplerParams": 0},
        "descriptor_rows": row,
        "numeric_descriptor_sha256": "a" * 64,
    }


def inputs():
    return {key: source(1 if key == (0, 0) else 0) for key in STAGES}


def reflect():
    return {key: {"textures": [
        {"set": 0, "binding": 1, "name": "PRIVATE_NAME",
         "type": "PRIVATE_TYPE"}]} if key == (0, 0) else {}
        for key in STAGES}


class T2FoamResourceAbiTests(unittest.TestCase):
    def test_synthetic_valid_original_and_compiled_are_only_numeric(self):
        result = combine(inputs(), reflect())
        self.assertEqual(result["original_stages"], 4)
        self.assertEqual(result["source_stage_descriptor_rows"], 1)
        self.assertEqual(result["compiled_non_cb_descriptors"], 1)
        self.assertFalse(result["original_name_register_join_verified"])
        self.assertFalse(result["shaderlab_or_unity_import_verified"])
        self.assertNotIn("PRIVATE", str(result))

    def test_reflection_rejects_bool_set_or_binding(self):
        for malformed in ({"set": True, "binding": 1},
                          {"set": 0, "binding": False},
                          {"set": -1, "binding": 1},
                          {"set": 0, "binding": 256},
                          {"set": "0", "binding": 1}):
            with self.subTest(row=malformed), self.assertRaises(ValueError):
                safe_compiled_resources({"textures": [malformed]})

    def test_duplicate_same_kind_reflected_binding_rejected(self):
        row = {"set": 0, "binding": 2}
        with self.assertRaises(ValueError):
            safe_compiled_resources({"textures": [row, dict(row)]})

    def test_same_numeric_slot_different_category_not_false_join(self):
        result = safe_compiled_resources({
            "textures": [{"set": 0, "binding": 3}],
            "separate_samplers": [{"set": 0, "binding": 3}]})
        self.assertEqual(len(result), 2)

    def test_strings_names_are_never_reported(self):
        obj = {"separate_images": [
            {"set": 2, "binding": 5, "name": "FORBIDDEN_PRIVATE_NAME",
             "type": "GameTexture"}]}
        self.assertEqual(safe_compiled_resources(obj),
                         [{"category": "separate_images", "set": 2, "binding": 5}])
        self.assertNotIn("PRIVATE", str(safe_compiled_resources(obj)))

    def test_invalid_unbounded_reflection_rejected(self):
        for obj in ({"images": "bad"}, {"textures": [None]},
                    {"images": [{"set": 0, "binding": 0}] * 129}):
            with self.subTest(obj=str(obj)[:60]), self.assertRaises(ValueError):
                safe_compiled_resources(obj)

    def test_original_unexpected_table_or_count_rejected(self):
        p = inputs()
        p[(0, 0)]["table_rows"]["m_FakeTexture"] = 1
        with self.assertRaises(ValueError):
            combine(p, reflect())
        p = inputs()
        p[(0, 0)]["descriptor_rows"] = 3
        with self.assertRaises(ValueError):
            combine(p, reflect())

    def test_missing_original_stage_is_not_four_stage_proof(self):
        p = inputs()
        p.pop((1, 0))
        with self.assertRaises(ValueError):
            combine(p, reflect())

    def test_missing_translated_stage_rejected(self):
        c = reflect()
        c.pop((0, 1))
        with self.assertRaises(ValueError):
            combine(inputs(), c)

    def test_reflection_accepts_numeric_nonzero_set_without_unity_assumption(self):
        rows = safe_compiled_resources({"images": [{"set": 3, "binding": 4}]})
        self.assertEqual(rows, [{"category": "images", "set": 3, "binding": 4}])

    def test_reflection_float_binding_rejected(self):
        with self.assertRaises(ValueError):
            safe_compiled_resources({"separate_samplers": [{"set": 0, "binding": 1.0}]})

    def test_original_zero_rows_does_not_imply_no_runtime_resources(self):
        result = combine({key: source(0) for key in STAGES}, reflect())
        self.assertEqual(result["source_stage_descriptor_rows"], 0)
        self.assertEqual(result["compiled_non_cb_descriptors"], 1)
        self.assertFalse(result["original_name_register_join_verified"])


    def test_exact_original_six_textures_map_to_six_image_sampler_pairs(self):
        profile = {}
        resources = {}
        for key in STAGES:
            count = ORIGINAL_TEXTURES_PER_STAGE[key]
            profile[key] = {
                "table_rows": {"m_TextureParams": count, "m_Samplers": 0,
                               "m_UAVParams": 0},
                "descriptor_rows": count,
                "numeric_descriptor_sha256": "a" * 64,
            }
            resources[key] = {
                "separate_images": [{"set": ds, "binding": binding}
                    for category, ds, binding in COMPILED_NUMERIC_RESOURCE_BINDINGS[key]
                    if category == "separate_images"],
                "separate_samplers": [{"set": ds, "binding": binding}
                    for category, ds, binding in COMPILED_NUMERIC_RESOURCE_BINDINGS[key]
                    if category == "separate_samplers"]
            }
        genuine = verify_genuine_texture_sampler_pair_count(combine(profile, resources))
        self.assertTrue(genuine["original_to_compiled_resource_cardinality_verified"])
        self.assertEqual(genuine["authenticated_original_texture_rows"], 6)
        self.assertEqual(genuine["authenticated_translated_sampled_images"], 6)
        self.assertEqual(genuine["authenticated_translated_separate_samplers"], 6)
        self.assertFalse(genuine["original_texture_to_hlsl_sampler_identity_verified"])
        return profile, resources

    def test_missing_genuine_sampler_pair_fails_closed(self):
        profile, resources = self.test_exact_original_six_textures_map_to_six_image_sampler_pairs()
        resources[(0, 0)]["separate_samplers"].pop()
        with self.assertRaises(ValueError):
            verify_genuine_texture_sampler_pair_count(combine(profile, resources))

    def test_source_texture_count_drift_fails_closed(self):
        profile, resources = self.test_exact_original_six_textures_map_to_six_image_sampler_pairs()
        profile[(1, 0)]["table_rows"]["m_TextureParams"] = 0
        profile[(1, 0)]["descriptor_rows"] = 0
        with self.assertRaises(ValueError):
            verify_genuine_texture_sampler_pair_count(combine(profile, resources))

    def test_translated_sampler_binding_drift_fails_closed(self):
        profile, resources = self.test_exact_original_six_textures_map_to_six_image_sampler_pairs()
        resources[(1, 0)]["separate_samplers"][0]["binding"] = 22
        with self.assertRaises(ValueError):
            verify_genuine_texture_sampler_pair_count(combine(profile, resources))

    def test_translated_resource_category_drift_fails_closed(self):
        profile, resources = self.test_exact_original_six_textures_map_to_six_image_sampler_pairs()
        resources[(0, 0)]["separate_images"][0]["set"] = 1
        with self.assertRaises(ValueError):
            verify_genuine_texture_sampler_pair_count(combine(profile, resources))


    def test_tampered_report_binding_types_fail_closed(self):
        profile, resources = self.test_exact_original_six_textures_map_to_six_image_sampler_pairs()
        for replacement in (True, "6", 6.0, -1, 256, None):
            with self.subTest(binding=replacement):
                report = combine(profile, resources)
                report["rows"][1]["translated_resource_bindings"][0]["binding"] = replacement
                with self.assertRaises(ValueError):
                    verify_genuine_texture_sampler_pair_count(report)

    def test_tampered_report_duplicate_binding_fails_closed(self):
        profile, resources = self.test_exact_original_six_textures_map_to_six_image_sampler_pairs()
        report = combine(profile, resources)
        first = dict(report["rows"][1]["translated_resource_bindings"][0])
        report["rows"][1]["translated_resource_bindings"].append(first)
        with self.assertRaises(ValueError):
            verify_genuine_texture_sampler_pair_count(report)


if __name__ == "__main__":
    unittest.main()
