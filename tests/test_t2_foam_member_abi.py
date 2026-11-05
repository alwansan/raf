"""T2 source-free Foam member layout adversarial unit tests."""
import unittest
from scripts.t2_foam_member_abi import (
    bounded_parameter, original_members, reflected_members, compare, EXPECTED_EXTENTS,
    translated_private_cbuffer_names, private_name_parity
)


def reflect(offsets=(0, 16), *, size=96, slot=0):
    return {
        "ubos": [{"set": 0, "binding": slot, "block_size": size,
                  "type": "_23", "name": "PRIVATE_SHADER_SYMBOL"}],
        "types": {"_23": {"name": "PRIVATE_TYPE",
                          "members": [{"offset": off, "name": "PRIVATE_MEMBER", "type": "vec4"}
                                      for off in offsets]}},
    }


def original():
    return {"partial_declared_bytes": 160,
            "vector_members": [{"kind": "vector", "index": 0},
                               {"kind": "vector", "index": 1}],
            "matrix_members": []}


class T2FoamMemberAbiTests(unittest.TestCase):
    def test_original_indices_not_mislabelled_bytes(self):
        obj = bounded_parameter({"m_Index": 3, "m_ArraySize": 2,
                                 "m_Type": 0, "m_Dim": 4,
                                 "m_NameIndex": 31, "m_Name": "PRIVATE"}, "vector")
        self.assertEqual(obj["index"], 3)
        self.assertEqual(obj["arraysize"], 2)
        self.assertNotIn("name", str(obj).lower())
        self.assertNotIn("PRIVATE", str(obj))

    def test_missing_and_boolean_original_index_rejected(self):
        for value in ({}, {"m_Index": True}, {"m_Index": -1},
                      {"m_Index": 65536}, {"m_Index": "12"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bounded_parameter(value, "vector")

    def test_numeric_source_field_overflow_and_bool_rejected(self):
        for row in ({"m_Index": 0, "m_ArraySize": 65536},
                    {"m_Index": 0, "m_Dim": True}):
            with self.assertRaises(ValueError):
                bounded_parameter(row, "vector")

    def test_source_member_count_bounded(self):
        with self.assertRaises(ValueError):
            original_members({"m_Size": 160, "m_VectorParams": [{"m_Index": 0}] * 129,
                              "m_MatrixParams": []})

    def test_missing_source_member_list_rejected(self):
        with self.assertRaises(ValueError):
            original_members({"m_Size": 160, "m_VectorParams": []})

    def test_reflected_members_only_numeric(self):
        row = reflected_members(reflect(), 0)
        self.assertEqual(row["reflected_offsets_bytes"], [0, 16])
        self.assertEqual(row["reflected_member_count"], 2)
        self.assertNotIn("PRIVATE", str(row))

    def test_reflected_duplicate_ubo_rejected(self):
        obj = reflect()
        obj["ubos"].append(dict(obj["ubos"][0]))
        with self.assertRaises(ValueError):
            reflected_members(obj, 0)

    def test_reflected_missing_type_rejected(self):
        obj = reflect()
        obj["types"] = {}
        with self.assertRaises(ValueError):
            reflected_members(obj, 0)

    def test_reflected_no_offset_or_duplicate_offset_rejected(self):
        for offsets in ((0, 0), (0, -1), (0, 3), (0, 96)):
            with self.subTest(offsets=offsets), self.assertRaises(ValueError):
                reflected_members(reflect(offsets), 0)
        bad = reflect()
        del bad["types"]["_23"]["members"][0]["offset"]
        with self.assertRaises(ValueError):
            reflected_members(bad, 0)

    def test_reflected_wrong_descriptor_set_rejected(self):
        obj = reflect()
        obj["ubos"][0]["set"] = 1
        with self.assertRaises(ValueError):
            reflected_members(obj, 0)

    def test_genuine_known_extents_are_pinned(self):
        self.assertEqual(len(EXPECTED_EXTENTS), 8)
        self.assertEqual(sum(a == b for a, b in EXPECTED_EXTENTS.values()), 1)
        self.assertEqual(sum(a != b for a, b in EXPECTED_EXTENTS.values()), 7)

    def test_candidate_intersection_does_not_claim_alias(self):
        obj = compare(original(), reflect(), 0, (0, 1, 0))
        self.assertEqual(obj["candidate_register16_offset_intersection_count"], 2)
        self.assertFalse(obj["original_index_unit_verified"])
        self.assertFalse(obj["source_to_translated_member_identity_verified"])
        self.assertNotIn("PRIVATE", str(obj))

    def test_mismatch_extent_rejected_not_repaired(self):
        with self.assertRaises(ValueError):
            compare(original(), reflect(size=160), 0, (0, 1, 0))

    def test_reflected_unbounded_members_rejected(self):
        with self.assertRaises(ValueError):
            reflected_members(reflect(tuple(range(129))), 0)

    def test_reflection_bool_offset_rejected(self):
        with self.assertRaises(ValueError):
            reflected_members(reflect((True,)), 0)

    def test_translated_cbuffer_name_extraction_ignores_comments_and_strings(self):
        hlsl = (
            '// cbuffer Wrong : register(b4) { float4 a; }\n'
            '/* cbuffer Ghost : register(b5) { float4 a; } */\n'
            '"cbuffer Quote : register(b6) { float4 a; }"\n'
            'cbuffer Generated0 : register(b0) { float4 x; }\n'
            'cbuffer Generated1 : register(b1) { float4 x; }\n'
        )
        self.assertEqual(translated_private_cbuffer_names(hlsl),
                         {0: "Generated0", 1: "Generated1"})

    def test_duplicate_or_unbounded_private_cbuffer_register_fails(self):
        for hlsl in (
            'cbuffer A : register(b0) { float4 x; } cbuffer B : register(b0) { float4 y; }',
            'cbuffer A : register(b32) { float4 x; }',
            'void main(){}' * 100000,
        ):
            with self.subTest(hlsl_len=len(hlsl)), self.assertRaises(ValueError):
                translated_private_cbuffer_names(hlsl)

    def test_private_name_three_way_mismatch_must_not_become_upload_proof(self):
        reflection = reflect()
        reflection["ubos"][0]["name"] = "Generated0"
        result = private_name_parity("Original_Compiler_0", "Generated0", reflection, 0)
        self.assertTrue(result["translated_hlsl_name_equals_spirv_name"])
        self.assertFalse(result["source_name_equals_translated_hlsl"])
        self.assertFalse(result["source_name_equals_spirv_name"])
        self.assertFalse(result["unity_original_cb_upload_alias_verified"])
        self.assertNotIn("Original_Compiler_0", str(result))
        self.assertNotIn("Generated0", str(result))

    def test_private_literal_name_equality_is_still_not_upload_proof(self):
        reflection = reflect()
        reflection["ubos"][0]["name"] = "ExactCB"
        result = private_name_parity("ExactCB", "ExactCB", reflection, 0)
        self.assertTrue(result["source_name_literal_hlsl_usable"])
        self.assertTrue(result["source_name_equals_spirv_name"])
        self.assertFalse(result["unity_original_cb_upload_alias_verified"])

    def test_private_invalid_name_and_ambiguous_reflection_fails(self):
        reflection = reflect()
        reflection["ubos"][0]["name"] = "Generated0"
        for original_name, hlsl_name in (("", "Generated0"), ("Original", "Bad-name")):
            with self.subTest(name=hlsl_name), self.assertRaises(ValueError):
                private_name_parity(original_name, hlsl_name, reflection, 0)
        broken = reflect()
        broken["ubos"][0].pop("name")
        with self.assertRaises(ValueError):
            private_name_parity("Original", "Generated0", broken, 0)
        broken = reflect()
        broken["ubos"].append(dict(broken["ubos"][0]))
        with self.assertRaises(ValueError):
            private_name_parity("Original", "Generated0", broken, 0)


if __name__ == "__main__":
    unittest.main()
