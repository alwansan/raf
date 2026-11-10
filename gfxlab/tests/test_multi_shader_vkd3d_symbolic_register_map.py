import unittest
from gfxlab.tools.multi_shader_vkd3d_symbolic_register_map import (
    private_register_from_name,symbolic_binding_evidence)

class TestGeneratedRegisterNames(unittest.TestCase):
    def test_vkd3d_t_s_cb_syntax(self):
        self.assertEqual(private_register_from_name("resource","t17"),17)
        self.assertEqual(private_register_from_name("sampler","s4"),4)
        self.assertEqual(private_register_from_name("constant_buffer","cb3_20"),3)
        self.assertEqual(private_register_from_name("resource","t0_7"),7)
        self.assertIsNone(private_register_from_name("resource","t2_7"))
        self.assertIsNone(private_register_from_name("sampler","sampler-7"))
        self.assertIsNone(private_register_from_name("resource","t65536"))
    def test_full_symbolic_mapping_keeps_original_vs_binding_separate(self):
        d=symbolic_binding_evidence({2,4},[
            {"name":"t2","set":0,"binding":17},
            {"name":"t4","set":0,"binding":18}],"resource")
        self.assertTrue(d["all_original_registers_matched_by_vkd3d_name"])
        self.assertEqual(d["numeric_binding_remapped_registers"],2)
        self.assertEqual(d["vkd3d_symbolically_matched_registers"],2)
        self.assertFalse(d["exact_material_texture_property_parity_verified"])
        self.assertFalse(d["original_register_ids_or_opnames_exported"])
    def test_mismatch_name_fails_closed(self):
        d=symbolic_binding_evidence({5},[{"name":"t3","binding":9}],"resource")
        self.assertFalse(d["all_original_registers_matched_by_vkd3d_name"])
        self.assertEqual(d["out_of_source_generated_names"],1)
    def test_empty_groups_complete_but_not_semantically_proven(self):
        d=symbolic_binding_evidence([],[],"sampler")
        self.assertTrue(d["all_original_registers_matched_by_vkd3d_name"])
        self.assertFalse(d["sampler_texture_use_site_semantics_verified"] if "sampler_texture_use_site_semantics_verified" in d else d["exact_material_texture_property_parity_verified"])
    def test_duplicated_bindings_fail(self):
        d=symbolic_binding_evidence({1,2},[
            {"name":"s1","set":0,"binding":20},
            {"name":"s2","set":0,"binding":20}],"sampler")
        self.assertFalse(d["all_original_registers_matched_by_vkd3d_name"])
        self.assertEqual(d["duplicate_descriptor_bindings"],1)
