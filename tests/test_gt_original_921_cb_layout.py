import unittest

from scripts.gt_original_921_cb_layout import bind_constant_buffers, constant_buffer_lanes


class ConstantBufferLayoutTests(unittest.TestCase):
    def test_original_slot_comes_from_array_symbol_and_not_descriptor_or_type(self):
        source = """
cbuffer cb16_1 : register(b2)
{
    float4 cb7_0_1_m0[2] : packoffset(c0);
};
cbuffer SPIRV_Cross_VertexInfo
{
    int SPIRV_Cross_BaseVertex;
    int SPIRV_Cross_BaseInstance;
};
"""
        common = {
            "m_ConstantBufferBindings": [{"m_Index": 7, "m_NameIndex": 0}],
            "m_ConstantBuffers": [],
        }
        layout = {
            "resources": [],
            "groups": [{"name": "Original", "used_size": 64, "members": [], "structs": []}],
        }
        binding, = bind_constant_buffers(source, common, {0: "Original"}, layout)
        self.assertEqual(binding["source_slot"], 7)
        self.assertEqual(binding["translated_binding"], 2)
        self.assertEqual(binding["translated_register_span_bytes"], 32)
        self.assertEqual(binding["variant_size_bytes"], 64)
        layout["resources"].append({"kind": 1, "index": 7, "name": "Conflicting"})
        with self.assertRaisesRegex(ValueError, "conflicting_original"):
            bind_constant_buffers(source, common, {0: "Original"}, layout)

    def test_struct_array_offsets_and_unassigned_lanes(self):
        member = {"name": "gain", "type": 0, "rows": 1, "columns": 1,
                  "matrix": False, "index": 4, "array_size": 0}
        struct = {"name": "lights", "index": 16, "size": 16,
                  "array_size": 2, "members": [member]}
        buffer = {"variant_size_bytes": 48, "members": [], "structs": [struct]}
        lanes = constant_buffer_lanes(buffer)
        self.assertIsNone(lanes[4])
        self.assertEqual(lanes[5]["path"], ["lights", 0, "gain"])
        self.assertEqual(lanes[9]["path"], ["lights", 1, "gain"])
        struct["members"].append({**member, "name": "overlapping"})
        with self.assertRaisesRegex(ValueError, "lane_conflict"):
            constant_buffer_lanes(buffer)
