"""Source-free fail-closed reconstruction of original six-Material Shader48 flags.

All synthetic names are test fixtures. The real SHA-owned attribute string and
original property names are never exported to GitHub artifacts.
"""
import unittest
from scripts.t3_particle108_source_propstate import (
    PrivateContractError, serialize_properties,
)


def original_record(*, flag=2, attrs=None, typ=0):
    return {
        "m_Name":"_PrivateSyntheticColor",
        "m_Description":"Synthetic six-material test",
        "m_Attributes":list(["OriginalColorDrawer(0, 1)"] if attrs is None else attrs),
        "m_Type":typ, "m_Flags":flag,
        "m_DefValue[0]":1.0, "m_DefValue[1]":0.2,
        "m_DefValue[2]":0.3, "m_DefValue[3]":1.0,
        "m_DefTexture":{"m_DefaultName":"","m_TexDim":0},
    }


def shader(**kwargs):
    return {"m_PropInfo":{"m_Props":[original_record(**kwargs)]}}


class SixMaterialShaderPropertyAttributes(unittest.TestCase):
    def test_original_per_renderer_data_and_drawer_are_source_owned(self):
        data=shader()
        with self.assertRaises(PrivateContractError) as failure:
            serialize_properties(data,allow_hidden_and_toggle=True)
        self.assertEqual(failure.exception.category,"PROPERTY_FLAGS_OR_ATTRIBUTES")
        text,counts=serialize_properties(
            data,allow_hidden_and_toggle=True,
            allow_original_per_renderer_and_drawer=True)
        self.assertEqual(counts["original_authored_property_count"],1)
        self.assertIn("[PerRendererData] [OriginalColorDrawer(0, 1)]",text)
        self.assertIn("_PrivateSyntheticColor",text)
        self.assertIn("Color",text)

    def test_only_syntactically_safe_original_drawer_survives(self):
        for raw in ("Source); Pass {}", "X\nShader", "[HDR]", "!", "Invalid(})"):
            with self.subTest(drawer=raw),self.assertRaises(PrivateContractError) as ctx:
                serialize_properties(
                    shader(attrs=[raw]),allow_original_per_renderer_and_drawer=True)
            self.assertEqual(ctx.exception.category,"PROPERTY_FLAGS_OR_ATTRIBUTES")

    def test_no_unproven_flags_or_multi_attributes_can_enter_shader(self):
        for flag in (3,4,8,16,32,256,-1):
            with self.subTest(flag=flag),self.assertRaises(PrivateContractError) as ctx:
                serialize_properties(
                    shader(flag=flag),allow_original_per_renderer_and_drawer=True)
            self.assertEqual(ctx.exception.category,"PROPERTY_FLAGS_OR_ATTRIBUTES")
        with self.assertRaises(PrivateContractError):
            serialize_properties(
                shader(attrs=["A","B"]),allow_original_per_renderer_and_drawer=True)

    def test_default_existing_hidden_toggle_contract_remains_unchanged(self):
        original=shader(flag=1,attrs=[])
        result,_=serialize_properties(
            original,allow_hidden_and_toggle=True)
        self.assertIn("[HideInInspector]",result)
        with self.assertRaises(PrivateContractError):
            serialize_properties(original)


if __name__=="__main__":
    unittest.main()
