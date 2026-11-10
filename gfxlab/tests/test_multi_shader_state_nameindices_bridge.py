import unittest
from gfxlab.tools.multi_shader_state_nameindices_bridge import (
    bounded_private_text_atoms,compare_state_sources
)

class TestShader48NameIndicesBridge(unittest.TestCase):
    def test_nested_same_pass_metadata_exact_match(self):
        atoms,meta=bounded_private_text_atoms([
            {"m_First":"_StatePrivate","m_Second":2},
            ("_AnotherPrivate",1)
        ])
        self.assertIn("_StatePrivate",atoms)
        self.assertEqual(meta["nodes"]>1,True)
        self.assertNotIn("_StatePrivate",str(meta))
    def test_fail_closed_unsupported_blob_or_deep_recursion(self):
        with self.assertRaises(ValueError):
            bounded_private_text_atoms(b"proprietary-raw-blob")
        deep="sample"
        for _ in range(17):
            deep=[deep]
        with self.assertRaises(ValueError):
            bounded_private_text_atoms(deep)
    def test_exact_no_case_alias_no_order_fallback(self):
        r=compare_state_sources("_Case",{"_case"},{""},[{"_Case":1}],set())
        self.assertTrue(r["parseable"])
        self.assertFalse(r["match_pass_nameindices"])
        self.assertEqual(r["match_original_material_float_slots"],1)
        self.assertFalse(r["effective_gpu_state_verified"])
    def test_shader_props_and_keyword_matches_separate(self):
        r=compare_state_sources("[_Property]",{"_Property"},{"_Property"},
           [{"_Property":1},{"_Other":0}],{"_Other"})
        self.assertTrue(r["match_pass_nameindices"])
        self.assertTrue(r["match_shader_property"])
        self.assertEqual(r["match_original_material_float_slots"],1)
        self.assertTrue(r["bracketed"])
        self.assertFalse(r["match_source_valid_keyword"])
    def test_unknown_name_metadata_fails_closed(self):
        r=compare_state_sources(None,set(),set(),[{}],set())
        self.assertFalse(r["parseable"])
        self.assertEqual(r["match_original_material_float_slots"],0)
        self.assertFalse(r["effective_gpu_state_verified"])
