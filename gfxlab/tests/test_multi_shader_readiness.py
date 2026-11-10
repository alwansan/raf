import unittest
from gfxlab.tools.multi_shader_readiness import shader_summary
class TestOriginalShaderReadiness(unittest.TestCase):
    def test_source_metadata_only(self):
        d={"m_ParsedForm":{"m_SubShaders":[{"m_Passes":[
          {"m_State":{},"progVertex":{"program":1},"progFragment":{"program":1}},
          {"m_ProgramMask":2}]},{"m_Passes":[{"m_State":{}}]}]}}
        s=shader_summary(d)
        self.assertEqual(s["per_subshader"],[2,1])
        self.assertEqual(s["state_metadata_passes"],2)
        self.assertEqual(s["vertex_metadata_passes"],1)
        self.assertFalse(s["original_android_compiled_program_verified"])
    def test_negative_control_rejects_malformed(self):
        for d in ({},{"m_ParsedForm":{"m_SubShaders":[]}},
                  {"m_ParsedForm":{"m_SubShaders":[{"m_Passes":[]}]}},
                  {"m_ParsedForm":{"m_SubShaders":[{"m_Passes":[None]}]}}):
            with self.subTest(d=d),self.assertRaises(ValueError):shader_summary(d)
    def test_unknown_program_never_assumed(self):
        s=shader_summary({"m_ParsedForm":{"m_SubShaders":[{"m_Passes":[{"unknown":True}]}]}})
        self.assertEqual(s["vertex_metadata_passes"],0)
        self.assertFalse(s["pass_render_state_equivalence_verified"])
