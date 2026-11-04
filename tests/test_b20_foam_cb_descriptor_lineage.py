"""B20 source-free CB0 descriptor ABI negative controls; synthetic only."""
import unittest

from scripts.b20_foam_cb_descriptor_lineage import (
    hlsl_cb_slots, reflected_ubos, analyze_pair,
)


def fake_text(slots):
    return "\n".join(
        "cbuffer Synthetic%d : register(b%d) { float4 x%d; }" % (i, slot, i)
        for i, slot in enumerate(slots)
    )


def fake_spv(slots):
    return {"ubos": [{"name": "synthetic%d" % i,
                      "set": 0, "binding": slot, "block_size": 160}
                     for i, slot in enumerate(slots)]}


class B20CBDescriptorLineageTest(unittest.TestCase):
    def test_numeric_three_original_vertex_slots(self):
        actual = analyze_pair(fake_text((0, 1, 2)), fake_spv((0, 1, 2)),
                              expected_slots=(0, 1, 2))
        self.assertTrue(actual["hlsl_source_slot_set_coincides"])
        self.assertTrue(actual["spirv_set0_binding_set_coincides"])
        self.assertFalse(actual["original_name_to_hlsl_cb0_identifier_verified"])
        self.assertFalse(actual["unity_original_constant_buffer_upload_verified"])
        self.assertNotIn("synthetic", str(actual))

    def test_numeric_fragment_cb0_slot(self):
        actual = analyze_pair(fake_text((0,)), fake_spv((0,)), expected_slots=(0,))
        self.assertEqual(actual["hlsl_explicit_cbuffer_b_slots"], [0])
        self.assertTrue(actual["spirv_set0_binding_set_coincides"])

    def test_comments_and_string_cannot_forge_cbuffer(self):
        text = (
            '/* cbuffer Fake : register(b2) { x } */\n'
            '// cbuffer AlsoFake : register(b3) { x }\n'
            '"cbuffer Quote : register(b4) { x }"\n'
            + fake_text((0,)))
        self.assertEqual(hlsl_cb_slots(text), (0,))

    def test_duplicate_b_register_is_rejected_not_deduplicated(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            hlsl_cb_slots(fake_text((0, 0)))

    def test_reflection_duplicate_bindings_rejected(self):
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            reflected_ubos(fake_spv((0, 0)))

    def test_reflection_negative_and_non_numeric_rejected(self):
        for entry in ({"set": -1, "binding": 0, "block_size": 160},
                      {"set": 0, "binding": "0", "block_size": 160},
                      {"set": True, "binding": 0, "block_size": 160}):
            with self.subTest(entry=entry), self.assertRaises(ValueError):
                reflected_ubos({"ubos": [entry]})

    def test_ambiguous_missing_cb_is_not_promoted_to_verified_alias(self):
        actual = analyze_pair("", {"ubos": []}, expected_slots=(0,))
        self.assertFalse(actual["hlsl_source_slot_set_coincides"])
        self.assertFalse(actual["spirv_set0_binding_set_coincides"])
        self.assertFalse(actual["original_name_to_hlsl_cb0_identifier_verified"])

    def test_reflection_nonzero_descriptor_set_is_not_identity(self):
        actual = analyze_pair(fake_text((0,)),
                              {"ubos": [{"set": 2, "binding": 0, "block_size": 160}]},
                              expected_slots=(0,))
        self.assertTrue(actual["hlsl_source_slot_set_coincides"])
        self.assertFalse(actual["spirv_set0_binding_set_coincides"])

    def test_numeric_mismatch_does_not_infer_source_register(self):
        actual = analyze_pair(fake_text((1,)), fake_spv((1,)), expected_slots=(0,))
        self.assertFalse(actual["hlsl_source_slot_set_coincides"])
        self.assertFalse(actual["spirv_set0_binding_set_coincides"])

    def test_unbounded_or_bad_ubo_schema_rejected(self):
        for row in ({"ubos": "unknown"}, {"ubos": [None]},
                    {"ubos": fake_spv(range(17))["ubos"]}):
            with self.subTest(row=row), self.assertRaises(ValueError):
                reflected_ubos(row)

    def test_report_never_exposes_names(self):
        data = reflected_ubos({"ubos": [{
            "name": "SyntheticPrivateIdentifier", "type": "Synthetic",
            "binding": 0, "set": 0, "block_size": 176}]})
        self.assertEqual(data, [{"set": 0, "binding": 0, "bytes": 176}])


if __name__ == "__main__":
    unittest.main()
