"""T2 synthetic 2 original authored Foam properties and two-pass safety."""
import copy
import unittest
from scripts.b24_original_foam_stage_translation import TARGET
from scripts.t2_foam_private_shaderlab_candidate import assemble,serialize_properties,properties_shape


def fixture():
    def p(name,typ,values,texture=None):
        return {"m_Name":name,"m_Description":"Synthetic source",
                "m_Attributes":[],"m_Type":typ,"m_Flags":0,
                **{"m_DefValue[%d]"%i:values[i] for i in range(4)},
                "m_DefTexture":texture or {"m_DefaultName":"","m_TexDim":0}}
    parsed={"m_Name":TARGET,"m_PropInfo":{"m_Props":[
        p("_DemoTex",4,[0.0]*4,{"m_DefaultName":"white","m_TexDim":2}),
        p("_DemoFloat",2,[0.75,0.0,0.0,0.0])]},
        "m_SubShaders":[{"m_LOD":200,"m_Tags":{"tags":[]},
                         "m_Passes":[{"m_Type":0},{"m_Type":0}]}],
        "m_FallbackName":"","m_CustomEditorName":""}
    vs="float4 main(float3 x:POSITION):SV_Position{return float4(x,1);}"
    fs="float4 main():SV_Target{return float4(1,1,1,1);}"
    return parsed,{(0,1):vs,(0,0):fs,(1,1):vs,(1,0):fs},["ZWrite Off","ZWrite Off"]


class TestFoamCandidate(unittest.TestCase):
    def test_complete_private_two_pass_candidate(self):
        p,st,states=fixture()
        text,shape=assemble(p,st,states)
        self.assertEqual(text.count("HLSLPROGRAM"),2)
        self.assertEqual(shape["authored_texture_properties"],1)
        self.assertNotIn("DummyShaderTextExporter",text)

    def test_scalar_vector_color_and_range_source_numeric_defaults(self):
        for code,values,label in ((0,[1,0,0,1],"Color"),(1,[1,2,3,4],"Vector"),
                                  (2,[0.75,0,0,0],"Float"),(3,[0.75,0,1,0],"Range")):
            p,_,_=fixture()
            v=p["m_PropInfo"]["m_Props"][1]
            v["m_Type"]=code
            for i,n in enumerate(values):v["m_DefValue[%d]"%i]=n
            body,_=serialize_properties(p)
            self.assertIn(label,body)

    def test_six_false_authored_textures_rejected(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"]*=3
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_unknown_flag_rejected(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"][1]["m_Flags"]=16
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_original_attributes_not_silently_dropped(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"][0]["m_Attributes"]=["HDR"]
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_duplicate_name_rejected(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"][1]["m_Name"]="_DemoTex"
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_float_unexplained_default_rejected(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"][1]["m_DefValue[2]"]=1
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_invalid_range_rejected(self):
        p,_,_=fixture()
        a=p["m_PropInfo"]["m_Props"][1];a["m_Type"]=3
        a["m_DefValue[1]"],a["m_DefValue[2]"]=2,1
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_unhandled_numeric_type_rejected(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"][1]["m_Type"]=5
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_injection_label_rejected(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"][0]["m_Description"]="bad\nPass {"
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_nontexture_extra_texture_rejected(self):
        p,_,_=fixture();p["m_PropInfo"]["m_Props"][1]["m_DefTexture"]["m_DefaultName"]="white"
        with self.assertRaises(ValueError):serialize_properties(p)

    def test_missing_stage_or_state_rejected(self):
        p,st,states=fixture();st.pop((1,0))
        with self.assertRaises(ValueError):assemble(p,st,states)
        p,st,states=fixture()
        with self.assertRaises(ValueError):assemble(p,st,states[:1])

    def test_wrong_pass_count_rejected(self):
        p,st,states=fixture();p["m_SubShaders"][0]["m_Passes"].append({"m_Type":0})
        with self.assertRaises(ValueError):assemble(p,st,states)

    def test_original_properties_not_mutated(self):
        p,st,states=fixture();before=copy.deepcopy(p)
        assemble(p,st,states);self.assertEqual(before,p)

    def test_safe_schema_no_private_values(self):
        p,_,_=fixture()
        safe=properties_shape(p)
        self.assertNotIn("_DemoTex",str(safe))
        self.assertNotIn("0.75",str(safe))


if __name__=="__main__":
    unittest.main()
