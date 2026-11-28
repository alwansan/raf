import unittest
from types import SimpleNamespace
from tools.gt_skybox_shader_program import audit as a
def pp(f,i=-18):return {"m_FileID":f,"m_PathID":i}
def ext(*n):return [SimpleNamespace(path=x) for x in n]
class TestSkyboxShader(unittest.TestCase):
    def test_local(self):
        self.assertEqual(a.source_target("sharedassets0.assets",ext("resources.assets"),pp(0),a.catalog()),("sharedassets0.assets",-18))
    def test_exact_external_slot(self):
        self.assertEqual(a.source_target("sharedassets0.assets",ext("resources.assets","sharedassets1.assets"),pp(2),a.catalog()),("sharedassets1.assets",-18))
    def test_builtin(self):
        self.assertEqual(a.source_target("sharedassets0.assets",ext("Resources/unity_builtin_extra"),pp(1),a.catalog()),("Resources/unity_builtin_extra",-18))
    def test_external_missing(self):
        with self.assertRaisesRegex(a.Rejected,"slot_missing"):a.source_target("sharedassets0.assets",ext("resources.assets"),pp(2),a.catalog())
    def test_unknown_owner(self):
        with self.assertRaisesRegex(a.Rejected,"outside_catalog"):a.source_target("sharedassets0.assets",ext("missing.assets"),pp(1),a.catalog())
    def test_pointer_types(self):
        g="ab"*16
        self.assertEqual(a.shader_pointer({"fileID":4800000,"guid":g,"type":3}),(4800000,g,"3"))
        with self.assertRaisesRegex(a.Rejected,"transport"):a.shader_pointer({"fileID":4800000,"guid":g,"type":2})
        e="0000000000000000f000000000000000"
        self.assertEqual(a.shader_pointer({"fileID":6,"guid":e,"type":0}),(6,e,"0"))
    def test_dummy_not_program_proof(self):
        text='//DummyShaderTextExporter\nShader "Authored" { SubShader { Pass {} } }'
        self.assertEqual(a.classify_program({"linked_d3d11_stage_slots":2},text)["status"],"ORIGINAL_PROGRAMS_PRESENT_EXPORTED_DUMMY")
        self.assertFalse(a.classify_program({"linked_d3d11_stage_slots":2},text)["program_authenticity_proven"])
    def test_non_dummy_not_authentic(self):
        text='Shader "Authored" { SubShader { Pass { HLSLPROGRAM\nfloat x;\nENDHLSL } } }'
        self.assertEqual(a.classify_program({"linked_d3d11_stage_slots":2},text)["status"],"NON_DUMMY_STRUCTURE_ONLY")
        self.assertFalse(a.classify_program({"linked_d3d11_stage_slots":2},text)["program_authenticity_proven"])
    def test_missing_program_schema(self):
        self.assertFalse(a.source_programs({})["source_program_schema_complete"])
    def test_program_counts_empty_valid(self):
        data={"m_ParsedForm":{"m_SubShaders":[{"m_Passes":[{"progVertex":{},"progFragment":{}}]}]}}
        p=a.source_programs(data)
        self.assertEqual(p["source_passes"],1);self.assertTrue(p["source_program_schema_complete"])
    def test_counts_detect_swap_and_extra(self):
        self.assertEqual(a.map_counts({"x":1,"y":2},{"x":2,"z":1}),{"source":2,"export":2,"equal":0,"changed":1,"missing":1,"extra":1})
    def test_keyword_disagreement(self):
        p=a.properties({"m_ValidKeywords":["ONE"]},{"m_ValidKeywords":["TWO"]})
        self.assertFalse(p["m_ValidKeywords"]["equal"])
        self.assertEqual(p["colors"]["status"],"UNKNOWN_SCHEMA")
    def test_trace_identity_not_name(self):
        key=("sharedassets0.assets",-18)
        w={"objects":[{"class_id":48,"source":{"owner":key[0],"path_id":key[1]}}]}
        self.assertEqual(a.exact_row(w,key,48),w["objects"][0])
        with self.assertRaisesRegex(a.Rejected,"identity_missing"):a.exact_row(w,(key[0],18),48)
