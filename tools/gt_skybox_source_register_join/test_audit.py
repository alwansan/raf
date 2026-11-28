"""Authored controls for original register identity and stage interface anchors."""
import unittest
from tools.gt_skybox_source_register_join import audit as a
from tools.gt_light_same_export.audit import Rejected
from tools.gt_skybox_offset_differential.audit import isolated_body

V={1:("vec4",1),3:("vec4",3),4:("vec2",4)}
F={3:("vec4",3),4:("vec2",4)}

class RegisterControls(unittest.TestCase):
    def test_exact_register_join(self):
        row=a.join(V,F,V,F)
        self.assertTrue(row["all_original_registers_linked"])
        self.assertTrue(row["absolute_original_vulkan_locations_preserved"])

    def test_bijective_compaction_not_original_absolute_locations(self):
        v={1:("vec4",0),3:("vec4",1),4:("vec2",2)}
        f={3:("vec4",1),4:("vec2",2)}
        row=a.join(v,f,V,F)
        self.assertTrue(row["all_original_registers_linked"])
        self.assertFalse(row["absolute_original_vulkan_locations_preserved"])

    def test_equal_type_wrong_original_register_rejected(self):
        v={1:("vec4",0),3:("vec4",1),4:("vec2",2)}
        f={3:("vec4",0),4:("vec2",2)}
        self.assertFalse(a.join(v,f,V,F)["all_original_registers_linked"])

    def test_type_drift_rejected(self):
        self.assertFalse(a.join(V,{3:("vec3",3),4:("vec2",4)},V,F)["all_original_registers_linked"])

    def test_extra_consumer_rejected(self):
        self.assertFalse(a.join(V,{**F,1:("vec4",1)},V,F)["all_original_registers_linked"])

    def test_missing_consumer_rejected(self):
        self.assertFalse(a.join(V,{3:("vec4",3)},V,F)["all_original_registers_linked"])

    def test_actual_reflection_register_join(self):
        x={"outputs":[{"name":"@entryPointOutput.o3","location":1,"type":"vec4"}]}
        self.assertEqual(a.reflected_registers(x,"outputs","o"),{3:("vec4",1)})

    def test_ambiguous_reflection_rejected(self):
        for rows in ([{"name":"not_a_register","location":0,"type":"vec4"}],
                     [{"name":"x.o3","location":1,"type":"vec4"},{"name":"y.o3","location":2,"type":"vec4"}],
                     [{"name":"x.o3","location":1,"type":"vec4"},{"name":"x.o4","location":1,"type":"vec4"}]):
            with self.assertRaises(Rejected):
                a.reflected_registers({"outputs":rows},"outputs","o")

    def test_stage_body_exact(self):
        self.assertEqual(a.split_body(isolated_body("vertex","fragment")),("vertex","fragment"))

    def test_source_anchor_preserves_existing_fields(self):
        vs="struct SPIRV_Cross_Output {\n    float4 o1 : TEXCOORD1;\n    float4 o3 : TEXCOORD3;\n    float2 o4 : TEXCOORD4;\n};"
        fs="struct SPIRV_Cross_Input {\n    float4 v3 : TEXCOORD3;\n    float2 v4 : TEXCOORD4;\n};\nfloat x = input.v3.x;"
        changed,n=a.align_fragment(vs,fs,V,F)
        self.assertEqual(n,1)
        self.assertIn("float4 v1 : TEXCOORD1;",changed)
        self.assertEqual(changed.replace("    float4 v1 : TEXCOORD1;\n",""),fs)

    def test_source_anchor_rejects_existing_symbol_use(self):
        vs="struct SPIRV_Cross_Output {\n    float4 o1 : TEXCOORD1;\n    float4 o3 : TEXCOORD3;\n    float2 o4 : TEXCOORD4;\n};"
        fs="struct SPIRV_Cross_Input {\n    float4 v3 : TEXCOORD3;\n    float2 v4 : TEXCOORD4;\n};\nfloat v1;"
        with self.assertRaises(Rejected):
            a.align_fragment(vs,fs,V,F)

    def test_original_register_ambiguity_rejected(self):
        row={"register":1,"system_value":0}
        with self.assertRaises(Rejected):
            a.original_registers([row,row])


if __name__=="__main__":
    unittest.main()
