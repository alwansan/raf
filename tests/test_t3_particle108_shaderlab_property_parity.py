"""Synthetic source-authored / exact-export ShaderLab property parity regressions."""
import json
import unittest
from scripts import t3_particle108_shaderlab_property_parity as m

DATA=[
    '_Color ("Tint", Color) = (1,1,1,1)',
    '_Fade ("Fade", Range(0,1)) = 0.5',
    '_Scroll ("Scroll", Vector) = (0,0,0,0)',
    '_Strength ("Strength", Float) = 1',
    '_Roughness ("Roughness", Float) = 0',
    '_Depth ("Depth", Float) = 0',
    '_Emission ("Emission", Color) = (1,0,0,1)',
    '_Ramp ("Ramp", 2D) = "white" {}',
    '_Mask ("Mask", 2D) = "black" {}',
    '_Scale ("Scale", Float) = 1',
    '_Speed ("Speed", Float) = 0',
    '_Distort ("Distort", Vector) = (0,0,0,0)',
    '_Soft ("Soft", Float) = 1',
]
SRC="Properties {\n"+"\n".join(DATA)+"\n}"
def shader(props=DATA, prefix="", suffix="SubShader { Pass { CGPROGRAM\nvoid f() {}\nENDCG } }"):
    return prefix+'Shader "Synthetic/Particle" {\nProperties {\n'+"\n".join(props)+"\n}\n"+suffix+"\n}"
class ExactAuthoredPropertyTests(unittest.TestCase):
    def test_exact_13_authored_2_textures_same_name_types(self):
        out=m.compare(SRC,shader())
        self.assertTrue(out["original_authored_property_names_types_exact"])
        c=out["counts"]
        self.assertEqual(c["source_authored_property_count"],13)
        self.assertEqual(c["source_authored_texture_property_count"],2)
        self.assertEqual(c["exported_texture_property_count"],2)
        self.assertEqual(c["original_authored_property_names_missing_in_export"],0)
        self.assertEqual(c["matched_name_different_type"],0)
        self.assertFalse(out["original_shader_program_resource_binding_or_Android_pixel_proven"])

    def test_missing_original_color_property_rejected(self):
        out=m.compare(SRC,shader([x for x in DATA if not x.startswith("_Color")]))
        self.assertFalse(out["original_authored_property_names_types_exact"])
        self.assertEqual(out["counts"]["original_authored_property_names_missing_in_export"],1)
        self.assertNotIn("_Color",json.dumps(out))

    def test_missing_original_texture_property_rejected(self):
        out=m.compare(SRC,shader(DATA[:-1][:7]+DATA[8:]))
        self.assertFalse(out["original_authored_property_names_types_exact"])
        self.assertEqual(out["counts"]["source_authored_texture_property_count"],2)
        self.assertEqual(out["counts"]["exported_texture_property_count"],1)

    def test_same_name_but_texture_changed_to_float_rejected(self):
        x=[row.replace('2D) = "white" {}','Float) = 1') if row.startswith("_Ramp") else row for row in DATA]
        out=m.compare(SRC,shader(x))
        self.assertFalse(out["original_authored_property_names_types_exact"])
        self.assertEqual(out["counts"]["matched_name_different_type"],1)
        self.assertEqual(out["counts"]["original_authored_property_names_missing_in_export"],0)

    def test_exported_extra_fake_property_is_not_authored_parity(self):
        rows=DATA+['_Unexpected ("Extra", Float) = 1']
        out=m.compare(SRC,shader(rows))
        self.assertEqual(out["counts"]["exported_property_names_not_authored_in_source"],1)
        self.assertFalse(out["original_authored_property_names_types_exact"])
        self.assertNotIn("_Unexpected",json.dumps(out))

    def test_duplicate_property_key_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_DUPLICATE_OR_UNSUPPORTED"):
            m.compare(SRC,shader(DATA+[DATA[0]]))

    def test_comment_properties_and_string_names_do_not_invent_new_blocks(self):
        code=shader(prefix='/* Shader "Fake" { Properties {\n_Q ("Q", Float)=0\n} } */\n',
                    suffix='// Properties { _Fake ("Fake", 2D) = "white" {} }\n'
                           'SubShader { Pass { CGPROGRAM\nvoid f() {}\nENDCG } }')
        out=m.compare(SRC,code)
        self.assertTrue(out["original_authored_property_names_types_exact"])

    def test_two_valid_shader_roots_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_ROOT_OR_BLOCK_TOPOLOGY"):
            m.compare(SRC,shader()+"\n"+shader())

    def test_properties_under_subshader_are_not_original_authored(self):
        code='Shader "S" { SubShader { Properties { '+DATA[0]+' } } }'
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_ROOT_OR_BLOCK_TOPOLOGY"):
            m.compare(SRC,code)

    def test_no_actual_property_block_fails_even_if_comment_has_fake_one(self):
        code='Shader "S" { /* Properties { '+DATA[0]+' } */ SubShader { Pass {} } }'
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_ROOT_OR_BLOCK_TOPOLOGY"):
            m.compare(SRC,code)

    def test_property_only_inside_string_cannot_prove_authored_export(self):
        code='Shader "S" { SubShader { Pass { CGPROGRAM\n// Properties { foo }\nENDCG } } }'
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_ROOT_OR_BLOCK_TOPOLOGY"):
            m.compare(SRC,code)

    def test_unparseable_line_or_missing_default_is_rejected(self):
        bad=DATA[:]
        bad[0]='_Color ("Tint", Color)'
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_DECLARATION_UNSUPPORTED"):
            m.compare(SRC,shader(bad))

    def test_attributes_on_same_line_or_separate_line_are_supported(self):
        rows=DATA[:]
        rows[0]='[HDR] '+rows[0]
        rows.insert(1,'[Toggle]')
        self.assertTrue(m.compare(SRC,shader(rows))["original_authored_property_names_types_exact"])

    def test_malformed_original_fragment_and_oversized_source_fail(self):
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_SOURCE_FRAGMENT"):
            m.compare("Shader X"+SRC,shader())
        with self.assertRaisesRegex(ValueError,"T3_PROPERTY_OVERSIZE_OR_INVALID"):
            m.compare(SRC,shader()+"\n"+"x"*m.MAX_SHADERLAB)

if __name__=="__main__":
    unittest.main()
