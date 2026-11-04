"""B20 safe-number fixture and negative controls; no original programs."""
import copy
import unittest

from scripts.b20_foam_cb_size_parity import compare, ORIGINAL_PARTIAL_CB_SIZE


OBSERVED_SAFE_NUMBERS = {
    (0, 1): {0: 96, 1: 64, 2: 336},
    (0, 0): {0: 128},
    (1, 1): {0: 160, 1: 64, 2: 336},
    (1, 0): {0: 112},
}


def source_fixture():
    stages = []
    for key, reflected_sizes in OBSERVED_SAFE_NUMBERS.items():
        slots = list(ORIGINAL_PARTIAL_CB_SIZE[key])
        stages.append({
            "pass": key[0], "stage_code": key[1],
            "original_source_cb_slots": slots,
            "hlsl_explicit_cbuffer_b_slots": slots,
            "hlsl_source_slot_set_coincides": True,
            "spirv_set0_binding_set_coincides": True,
            "spirv_reflected_ubos": [
                {"set": 0, "binding": slot, "bytes": reflected_sizes[slot]}
                for slot in slots],
        })
    return {
        "status": "genuine_foam_cb_reflection_observed",
        "authenticated_original_foam_stage_count": 4,
        "original_source_cb_links": 8,
        "all_hlsl_b_slots_numerically_coincide": True,
        "all_spirv_set0_bindings_numerically_coincide": True,
        "original_cb0_name_to_hlsl_alias_verified": False,
        "original_material_constant_buffer_upload_verified": False,
        "private_hlsl_spirv_names_or_binaries_published": False,
        "stages": stages,
    }


class OriginalFoamCBSizeParityControls(unittest.TestCase):
    def test_safe_numeric_source_fixture_exact_seven_differences(self):
        result = compare(source_fixture())
        self.assertEqual(result["original_cb_links_compared"], 8)
        self.assertEqual(result["exact_numeric_size_matches"], 1)
        self.assertEqual(result["different_numeric_size_pairs"], 7)
        self.assertFalse(result["source_and_translated_sizes_are_semantically_interchangeable_proven"])
        self.assertFalse(result["original_cb0_name_alias_verified"])
        self.assertFalse(result["android_gpu_pixels_verified"])
        self.assertNotIn("name", str(result))

    def test_swapped_stage_order_rejected(self):
        source = source_fixture()
        source["stages"][0], source["stages"][1] = source["stages"][1], source["stages"][0]
        with self.assertRaises(ValueError):
            compare(source)

    def test_missing_reflected_cb_rejected(self):
        source = source_fixture()
        source["stages"][0]["spirv_reflected_ubos"].pop()
        with self.assertRaises(ValueError):
            compare(source)

    def test_duplicate_reflected_cb_slot_rejected(self):
        source = source_fixture()
        source["stages"][0]["spirv_reflected_ubos"][1]["binding"] = 0
        with self.assertRaises(ValueError):
            compare(source)

    def test_forged_cb0_alias_status_rejected(self):
        source = source_fixture()
        source["original_cb0_name_to_hlsl_alias_verified"] = True
        with self.assertRaises(ValueError):
            compare(source)

    def test_forged_unity_upload_status_rejected(self):
        source = source_fixture()
        source["original_material_constant_buffer_upload_verified"] = True
        with self.assertRaises(ValueError):
            compare(source)

    def test_missing_source_identity_rejected(self):
        source = source_fixture()
        source["authenticated_original_foam_stage_count"] = 3
        with self.assertRaises(ValueError):
            compare(source)

    def test_nonzero_set_and_boolean_size_rejected(self):
        for field, val in (("set", 1), ("bytes", True), ("bytes", -1)):
            source = source_fixture()
            source["stages"][0]["spirv_reflected_ubos"][0][field] = val
            with self.subTest(field=field, val=val), self.assertRaises(ValueError):
                compare(source)

    def test_false_slot_identity_rejected(self):
        source = source_fixture()
        source["all_spirv_set0_bindings_numerically_coincide"] = False
        with self.assertRaises(ValueError):
            compare(source)


if __name__ == "__main__":
    unittest.main()
