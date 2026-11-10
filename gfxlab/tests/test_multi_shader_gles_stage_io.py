import unittest
from gfxlab.tools.multi_shader_gles_stage_io import public_interfaces,resource_counters
class TestStageInterfaceNumbers(unittest.TestCase):
    def test_same_location_types(self):
        v={"outputs":[{"location":0,"type":"vec4"},{"location":1,"type":"vec2"}]}
        f={"inputs":[{"location":0,"type":"vec4"},{"location":1,"type":"vec2"}]}
        r=public_interfaces(v,f)
        self.assertTrue(r["location_type_parity"])
        self.assertEqual(r["matched_locations_and_types"],2)
        self.assertFalse(r["semantics_and_interpolation_verified"])
    def test_location_type_drift_rejected(self):
        v={"outputs":[{"location":0,"type":"vec3"}]}
        f={"inputs":[{"location":0,"type":"vec4"},{"location":1,"type":"float"}]}
        r=public_interfaces(v,f)
        self.assertEqual(r["different_type_same_location"],1)
        self.assertEqual(r["fragment_input_missing_vertex_output"],1)
        self.assertFalse(r["location_type_parity"])
    def test_duplicate_locations_counted_not_assumed(self):
        v={"outputs":[{"location":0,"type":"vec4"},{"location":0,"type":"vec4"}]}
        f={"inputs":[{"location":0,"type":"vec4"}]}
        self.assertEqual(public_interfaces(v,f)["duplicate_location_slots"],1)
        self.assertFalse(public_interfaces(v,f)["location_type_parity"])
    def test_resource_counts_generic(self):
        self.assertEqual(resource_counters({"ubos":[1],"textures":[1,2]})["textures"],2)
