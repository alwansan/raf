"""Synthetic-only T3 original Particle Shader48 fixed-function state guards.

No original shader bytes, names, owner IDs or private export trace are loaded.
"""
import copy
import json
import unittest

from scripts import t3_original_particle_shader_state as t3
from scripts.w1_depth_shaderlab import color_mask, render_state


def v(x,name="<noninit>"):
    return {"name":name,"val":x}


def state(src=5,dst=10,zwrite=0):
    blend={"srcBlend":v(src),"destBlend":v(dst),
           "srcBlendAlpha":v(1),"destBlendAlpha":v(0),
           "blendOp":v(0),"blendOpAlpha":v(0),"colMask":v(15)}
    stencil={"comp":v(8),"pass":v(0),"fail":v(0),"zFail":v(0)}
    return {"m_Name":"","m_LOD":0,"m_Tags":{"tags":[]},
            "rtSeparateBlend":False,"rtBlend0":blend,
            "alphaToMask":v(0),"zClip":v(1),"zTest":v(4),
            "zWrite":v(zwrite),"culling":v(2),
            "offsetFactor":v(0),"offsetUnits":v(0),
            "fogMode":-1,
            "fogColor":{"name":"<noninit>",**{k:v(0) for k in "xyzw"}},
            "fogDensity":v(0),"fogStart":v(0),"fogEnd":v(0),
            "stencilRef":v(0),"stencilReadMask":v(255),
            "stencilWriteMask":v(255),
            "stencilOp":stencil,"stencilOpFront":copy.deepcopy(stencil),
            "stencilOpBack":copy.deepcopy(stencil),"lighting":False}


def parsed(s=None):
    return {"m_Name":"NEVER_EXPORT_PRIVATE_NAME",
            "m_SubShaders":[{"m_Passes":[{"m_Type":0,"m_State":s or state()}]}]}


class SourceOnlyParticlePassState(unittest.TestCase):
    def test_alpha_blended_zwrite_off_is_not_opaque_replace(self):
        result=t3.inspect_parsed(parsed())
        self.assertEqual(result["source_108_particle_shader_original_Pass_count"],1)
        self.assertEqual(result["original_pass_color_blend_category"],"ALPHA_DEPENDENT")
        self.assertEqual(result["original_pass_alpha_channel_blend_category"],"REPLACE")
        self.assertEqual(result["original_pass_depth_write_category"],"OFF")
        self.assertEqual(result["original_pass_color_mask_category"],"RGBA")
        self.assertTrue(result["original_pass_fixed_function_state_translator_accepted"])
        self.assertFalse(result["native_ShaderLab_or_Android_pixels_not_verified"] is False)

    def test_unity2021_colorwrite_16_masks_are_exact_rgba_not_webgpu_bits(self):
        bits=((8,"R"),(4,"G"),(2,"B"),(1,"A"))
        for mask in range(16):
            want="".join(name for bit,name in bits if mask & bit) or "0"
            with self.subTest(mask=mask):
                self.assertEqual(color_mask(v(mask)),want)
                src=state()
                src["rtBlend0"]["colMask"]=v(mask)
                text=render_state(src,allow_selective_color_mask=True)
                self.assertIn("ColorMask "+want,text)
                result=t3.classify_state(src)
                self.assertEqual(result["original_pass_color_mask_shaderlab_channels"],want)
                self.assertTrue(result["original_pass_opt_in_selective_colormask_translator_accepted"])
                if mask in (0,15):
                    self.assertTrue(result["original_pass_fixed_function_state_translator_accepted"])
                else:
                    self.assertFalse(result["original_pass_fixed_function_state_translator_accepted"])
        self.assertEqual(color_mask(v(1)),"A")
        self.assertEqual(color_mask(v(8)),"R")
        self.assertEqual(color_mask(v(14)),"RGB")
        self.assertEqual(color_mask(v(7)),"GBA")

    def test_selective_mask_legacy_unchanged_and_opt_in_binds_actual_channels(self):
        src=state()
        src["rtBlend0"]["colMask"]=v(7)
        result=t3.inspect_parsed(parsed(src))
        self.assertEqual(result["original_pass_color_mask_category"],"PARTIAL")
        self.assertEqual(result["original_pass_color_mask_shaderlab_channels"],"GBA")
        self.assertFalse(result["original_pass_fixed_function_state_translator_accepted"])
        self.assertTrue(result["original_pass_opt_in_selective_colormask_translator_accepted"])
        self.assertTrue(result["serialized_Unity2021_ColorWriteMask_ABGR_bits_not_reversed"])

    def test_bad_color_mask_source_value_cannot_be_emitted_as_shaderlab(self):
        for bad in (-1,16,True,False,7.3,float("nan"),float("inf"),"7"):
            src=state()
            src["rtBlend0"]["colMask"]=v(bad)
            with self.subTest(bad=repr(bad)),self.assertRaises(ValueError):
                t3.classify_state(src)

    def test_color_mask_dynamic_property_not_disclosed_as_shader_label(self):
        src=state()
        src["rtBlend0"]["colMask"]=v(0,"_SourcePrivateMask")
        summary=t3.classify_state(src)
        self.assertEqual(summary["original_pass_color_mask_shaderlab_channels"],
                         "PROPERTY_DRIVEN_UNRESOLVED")
        self.assertNotIn("_SourcePrivateMask",json.dumps(summary))
        self.assertTrue(summary["original_pass_opt_in_selective_colormask_translator_accepted"])

    def test_opaque_replace_and_depth_write_remain_distinct(self):
        result=t3.classify_state(state(1,0,1))
        self.assertEqual(result["original_pass_color_blend_category"],"REPLACE")
        self.assertEqual(result["original_pass_depth_write_category"],"ON")
        self.assertEqual(result["original_pass_alpha_to_coverage_category"],"OFF")

    def test_additive_no_alpha_factor_is_not_alpha_dependent(self):
        result=t3.classify_state(state(1,1,0))
        self.assertEqual(result["original_pass_color_blend_category"],"ADDITIVE_NO_ALPHA_FACTOR")

    def test_dynamic_blend_is_unknown_not_guessed(self):
        s=state()
        s["rtBlend0"]["srcBlend"]=v(5,"_PrivateProperty")
        r=t3.classify_state(s)
        self.assertEqual(r["original_pass_color_blend_category"],"PROPERTY_DRIVEN_UNRESOLVED")
        self.assertNotIn("_PrivateProperty",json.dumps(r))

    def test_separate_render_targets_not_inferred_from_rt0(self):
        s=state()
        s["rtSeparateBlend"]=True
        r=t3.classify_state(s)
        self.assertEqual(r["original_pass_color_blend_category"],"MULTI_RENDER_TARGET_UNRESOLVED")
        self.assertEqual(r["original_pass_alpha_channel_blend_category"],"MULTI_RENDER_TARGET_UNRESOLVED")

    def test_invalid_blend_factor_and_missing_state_rejected(self):
        for bad in (11,-1,True,"5"):
            s=state();s["rtBlend0"]["srcBlend"]=v(bad)
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                t3.classify_state(s)
        with self.assertRaisesRegex(ValueError,"missing_original_particle_rtBlend0"):
            t3.classify_state({"rtSeparateBlend":False})

    def test_multiple_or_missing_original_passes_are_inconclusive(self):
        for count in (0,2):
            p=parsed()
            p["m_SubShaders"][0]["m_Passes"]*=count
            with self.subTest(count=count),self.assertRaisesRegex(ValueError,"Pass_count"):
                t3.inspect_parsed(p)
        p=parsed();p["m_SubShaders"]*=2
        with self.assertRaisesRegex(ValueError,"SubShader_count"):
            t3.inspect_parsed(p)

    def test_non_normal_pass_kind_cannot_be_called_original_normal_pass(self):
        p=parsed()
        p["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1
        with self.assertRaisesRegex(ValueError,"non_normal_particle_source"):
            t3.inspect_parsed(p)

    def test_public_state_summary_contains_no_private_source_labels(self):
        r=t3.inspect_parsed(parsed())
        encoded=json.dumps(r,sort_keys=True)
        for secret in ("NEVER_EXPORT_PRIVATE_NAME","m_PathID","m_Name",
                       "_PrivateProperty","sharedassets0.assets",'"guid"'):
            self.assertNotIn(secret,encoded)
        self.assertTrue(r["original_fragment_alpha_output_or_discard_not_verified"])
        self.assertTrue(r["native_ShaderLab_or_Android_pixels_not_verified"])


if __name__=="__main__":
    unittest.main()
