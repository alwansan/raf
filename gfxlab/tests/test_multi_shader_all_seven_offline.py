import unittest
from gfxlab.tools.multi_shader_all_seven_offline import all_seven_complete
class TestSevenPassOffline(unittest.TestCase):
    def test_all_keys_required_for_every_pass(self):
        keys=("original_dxbc_pair_extract_verified","vertex_spirv_vulkan11_valid",
            "fragment_spirv_vulkan11_valid","vertex_glsl_es310_offline_compiled",
            "fragment_glsl_es310_offline_compiled","vertex_fragment_location_type_parity")
        rows=[{k:True for k in keys} for _ in range(7)]
        self.assertTrue(all_seven_complete(rows))
        self.assertFalse(all_seven_complete(rows[:6]))
        rows[3]["vertex_fragment_location_type_parity"]=False
        self.assertFalse(all_seven_complete(rows))
    def test_not_conflate_source_syntax_with_gpu_execution(self):
        self.assertFalse(all_seven_complete([{"original_dxbc_pair_extract_verified":True}]*7))
