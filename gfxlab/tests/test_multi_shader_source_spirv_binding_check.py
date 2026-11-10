import unittest
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_compare

class TestDX11SPIRVPrivateBindingComparison(unittest.TestCase):
    def test_identical_numerical_set_not_semantic_equivalence(self):
        d=private_compare({0,1},[{"binding":0,"set":0},{"binding":1,"set":0}])
        self.assertTrue(d["source_and_spirv_counts_equal"])
        self.assertTrue(d["same_numeric_binding_set"])
        self.assertFalse(d["original_dx11_register_to_spirv_semantic_equivalence"])
    def test_same_resource_counts_can_have_remapped_numbers(self):
        d=private_compare({2,4},[{"binding":0,"set":0},{"binding":1,"set":0}])
        self.assertTrue(d["source_and_spirv_counts_equal"])
        self.assertFalse(d["same_numeric_binding_set"])
        self.assertEqual(d["same_numeric_slot_overlap_count"],0)
    def test_missing_binding_must_not_be_assumed(self):
        d=private_compare({0},[{"type":"texture"}])
        self.assertEqual(d["spirv_reflection_entries_without_binding"],1)
        self.assertFalse(d["same_numeric_binding_set"])
    def test_descriptor_set_collision_and_nonzero(self):
        d=private_compare({2},[{"binding":2,"set":1},{"binding":2,"set":1}])
        self.assertEqual(d["spirv_duplicate_descriptor_set_binding_pairs"],1)
        self.assertEqual(d["spirv_nonzero_descriptor_set_entry_count"],2)
