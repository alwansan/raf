"""Synthetic original Shader m_ParsedForm pass-topology boundary."""
import unittest
from scripts import t3_original_shader_pass_topology as m

class OriginalShaderPasses(unittest.TestCase):
    def fixture(self):
        return {
            ("resources.assets",i):{"m_SubShaders":[{"m_Passes":[{"m_Name":"private"}]*(1+i%3)}]}
            for i in range(1,11)
        }
    def test_10_exact_original_shader_pass_records(self):
        x=m.summarize(self.fixture())
        self.assertEqual(x["selected_original_shader_count"],10)
        self.assertEqual(x["original_total_pass_records"],20)
        self.assertEqual(x["original_total_subshader_records"],10)
        self.assertEqual(x["original_shader_pass_record_histogram"],{1:3,2:4,3:3})
        self.assertFalse(x["real_same_export_shaderlab_pass_equivalence_verified"])
    def test_missing_one_original_shader_is_not_promoted(self):
        x=self.fixture();x.pop(("resources.assets",1))
        with self.assertRaisesRegex(ValueError,"incomplete_authentic"):m.summarize(x)
    def test_wrong_owner_identity_cannot_alias_original(self):
        x=self.fixture()
        x[("outside/resources.assets",1)]=x.pop(("resources.assets",1))
        with self.assertRaisesRegex(ValueError,"invalid_original_selected"):m.summarize(x)
    def test_missing_or_nonlist_original_subshaders_rejected(self):
        for malformed in ({},{"m_SubShaders":None},{"m_SubShaders":{}}):
            x=self.fixture();x[("resources.assets",1)]=malformed
            with self.assertRaisesRegex(ValueError,"invalid_original_SubShader"):m.summarize(x)
    def test_nested_passes_unknown_shape_rejected(self):
        for bad in (None,{},[1]):
            x=self.fixture();x[("resources.assets",1)]={"m_SubShaders":[{"m_Passes":bad}]}
            with self.assertRaises(ValueError):m.summarize(x)
    def test_empty_original_shaders_not_fake_executable(self):
        x=self.fixture();x[("resources.assets",1)]={"m_SubShaders":[]}
        r=m.summarize(x)
        self.assertEqual(r["original_shaders_with_no_passes"],1)
        self.assertTrue(r["original_parsed_pass_records_not_executable_programs"])
    def test_private_original_shader_names_not_exposed(self):
        r=str(m.summarize(self.fixture()))
        self.assertNotIn("private",r)
        self.assertNotIn("m_Passes",r)
        self.assertNotIn("m_Name",r)
        self.assertNotIn("path_id",r)
if __name__=="__main__":unittest.main()
