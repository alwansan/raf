"""Source-free failure controls for exact original Particle108 property/state fragment."""
import copy
import json
import unittest

from scripts.t3_particle108_source_propstate import (
    PrivateContractError, source_fragment, serialize_properties, STATUS,
)
from test_t3_original_particle_shader_state import state, v

def prop(name, typ, values, default=None, dim=0):
    return {
        "m_Name":name, "m_Description":"Synthetic source",
        "m_Attributes":[], "m_Type":typ,"m_Flags":0,
        **{"m_DefValue[%d]"%i:values[i] for i in range(4)},
        "m_DefTexture":{"m_DefaultName":default if default is not None else "",
                        "m_TexDim":dim},
    }

def original():
    s=state()
    s["rtBlend0"]["colMask"]=v(14)
    s["culling"]=v(0)
    return {
        "m_Name":"PRIVATE_PARTICLE_UNRELEASED_NAME",
        "m_PropInfo":{"m_Props":[
            prop("_PRIVATE_TEXTURE",4,[0,0,0,0],"white",2),
            prop("_PRIVATE_COLOR",0,[1,0.5,0,1]),
            prop("_PRIVATE_RANGE",3,[0.5,0,1,0]),
            prop("_PRIVATE_FLOAT",2,[0.2,0,0,0]),
        ]},
        "m_SubShaders":[{
            "m_LOD":100,"m_Tags":{"tags":[]},
            "m_Passes":[{"m_Type":0,"m_State":s}],
        }],
    }

class OriginalPrivateParticleProps(unittest.TestCase):
    def test_private_property_fragment_and_state_do_not_claim_real_program(self):
        p=original(); saved=copy.deepcopy(p)
        text,result=source_fragment(p)
        self.assertEqual(p,saved)
        self.assertEqual(result["status"],STATUS)
        self.assertEqual(result["original_authored_property_count"],4)
        self.assertTrue(result["original_fixed_function_selective_RGB_colormask_preserved"])
        self.assertTrue(result["source_fragment_is_intentionally_not_a_compilable_Unity_shader"])
        self.assertNotIn("HLSLPROGRAM",text)
        self.assertNotIn("DummyShaderTextExporter",text)
        self.assertIn("ColorMask RGB",text)
        self.assertIn("ZWrite Off",text)
        self.assertIn("Cull Off",text)
        self.assertNotIn("_PRIVATE_COLOR",json.dumps(result))
        self.assertNotIn("PRIVATE_PARTICLE_UNRELEASED_NAME",json.dumps(result))
    def test_invalid_property_name_rejected(self):
        p=original();p["m_PropInfo"]["m_Props"][0]["m_Name"]="x\nPass {}"
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_NAME")
    def test_property_description_injection_rejected(self):
        p=original();p["m_PropInfo"]["m_Props"][1]["m_Description"]="bad\nPass {}"
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_DESCRIPTION")
    def test_duplicate_property_identity_rejected(self):
        p=original();p["m_PropInfo"]["m_Props"][0]["m_Name"]="_PRIVATE_COLOR"
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_DUPLICATE")
    def test_flags_not_silently_lost(self):
        p=original();p["m_PropInfo"]["m_Props"][0]["m_Flags"]=16
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_FLAGS_OR_ATTRIBUTES")
    def test_attributes_not_silently_lost(self):
        p=original();p["m_PropInfo"]["m_Props"][0]["m_Attributes"]=["HDR"]
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_FLAGS_OR_ATTRIBUTES")
    def test_unexpected_extra_property_field_rejected(self):
        p=original();p["m_PropInfo"]["m_Props"][0]["Untrusted"]=""
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_FIELD_SCHEMA")
    def test_bad_range_default_and_nonfinite_rejected(self):
        p=original();p["m_PropInfo"]["m_Props"][2]["m_DefValue[1]"]=0.9
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_RANGE")
        p=original();p["m_PropInfo"]["m_Props"][2]["m_DefValue[0]"]=float("nan")
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_DEFAULT_NUMERIC")
    def test_unknown_property_type_rejected(self):
        p=original();p["m_PropInfo"]["m_Props"][2]["m_Type"]=5
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_TYPE_UNSUPPORTED")
    def test_bad_texture_default_rejected(self):
        p=original();p["m_PropInfo"]["m_Props"][0]["m_DefTexture"]["m_DefaultName"]="PRIVATE"
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_TEXTURE_DEFAULT")
    def test_nontexture_default_never_assumed(self):
        p=original();p["m_PropInfo"]["m_Props"][1]["m_DefTexture"]["m_DefaultName"]="white"
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"PROPERTY_NON_TEXTURE_DEFAULT")
    def test_wrong_pass_kind_rejected(self):
        p=original();p["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1
        with self.assertRaises(ValueError):source_fragment(p)
    def test_incorrect_colormask_rejected(self):
        p=original();p["m_SubShaders"][0]["m_Passes"][0]["m_State"]["rtBlend0"]["colMask"]=v(15)
        with self.assertRaises(PrivateContractError) as e:source_fragment(p)
        self.assertEqual(e.exception.category,"SOURCE_STATE")
    def test_missing_authored_properties_fail_closed(self):
        p=original();p.pop("m_PropInfo")
        with self.assertRaises(PrivateContractError) as e:serialize_properties(p)
        self.assertEqual(e.exception.category,"PROPERTY_TABLE_SCHEMA")

if __name__=="__main__":
    unittest.main()
