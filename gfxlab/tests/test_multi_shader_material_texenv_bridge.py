import unittest
from gfxlab.tools.multi_shader_material_texenv_bridge import pass_name_table,compare_one_program

class TestOriginalUnityShaderParameters(unittest.TestCase):
    def test_pass_shader_name_index_inversion(self):
        d=pass_name_table([{"first":"SomeProperty","second":17},
             {"m_First":"SecondProperty","m_Second":18}])
        self.assertEqual(d[17],"SomeProperty")
        self.assertEqual(d[18],"SecondProperty")
    def test_ambiguous_property_indices_rejected(self):
        with self.assertRaises(ValueError):
            pass_name_table([["A",5],["B",5]])
    def test_original_texture_slot_name_sampler_material_link(self):
        meta={"m_Parameters":{"m_TextureParams":[
            {"m_NameIndex":19,"m_Index":4,"m_SamplerIndex":8}],
            "m_ConstantBufferBindings":[{"m_Index":0}]}}
        result=compare_one_program(meta,
            {"resource":{4},"sampler":{8},"constant_buffer":{0}},
            {19:"_MainTex"},[{"_MainTex"}],[{"_MainTex"}],{"_MainTex"})
        self.assertEqual(result["exact_source_property_t_sampler_to_material_bridges"],1)
        self.assertTrue(result["program_metadata_full_property_resolution"])
        self.assertFalse(result["source_material_to_gpu_texture_semantics_verified"])
    def test_same_name_without_actual_source_texture_fails_bridge(self):
        meta={"m_Parameters":{"m_TextureParams":[
            {"m_NameIndex":19,"m_Index":5,"m_SamplerIndex":8}],
            "m_ConstantBufferBindings":[]}}
        d=compare_one_program(meta,
            {"resource":{4},"sampler":{8},"constant_buffer":set()},
            {19:"_MainTex"},[{"_MainTex"}],[{"_MainTex"}],{"_MainTex"})
        self.assertFalse(d["program_metadata_full_property_resolution"])
        self.assertEqual(d["exact_source_property_t_sampler_to_material_bridges"],0)
    def test_missing_name_metadata_does_not_guess(self):
        meta={"m_Parameters":{"m_TextureParams":[
            {"m_NameIndex":9,"m_Index":4,"m_SamplerIndex":8}],
            "m_ConstantBufferBindings":[]}}
        d=compare_one_program(meta,
            {"resource":{4},"sampler":{8},"constant_buffer":set()},
            {},[{"_MainTex"}],[{"_MainTex"}],{"_MainTex"})
        self.assertEqual(d["exact_source_property_t_sampler_to_material_bridges"],0)
        self.assertEqual(d["unresolved_pass_property_name_indices"],1)
