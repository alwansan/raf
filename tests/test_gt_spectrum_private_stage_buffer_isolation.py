"""Strict source-free regression against actual Unity cb0_0_m0 cross-stage alias."""
from __future__ import annotations

import unittest

from scripts.gt_spectrum_private_stage_buffer_isolation import isolate
from scripts.w1_depth_shaderlab import stage_body


def candidate(passes=7):
    text=['Shader "Dummy/Synthetic" {','Properties {}','SubShader {']
    for i in range(passes):
        vertex=("float4 cb0_0_m0[4];\n"
                "float4 main():SV_Position{return cb0_0_m0[0];}\n")
        fragment=("float4 cb0_0_m0[%d];\n"
                  "float4 main():SV_Target{return cb0_0_m0[0];}\n" % (i+4))
        text.extend(["Pass {","HLSLPROGRAM","#pragma vertex main",
                     "#pragma fragment main",
                     "Texture2D t0 : register(t0);",
                     stage_body(vertex,fragment),"ENDHLSL","}"])
    text.extend(["}","}"])
    return "\n".join(text)


class SpectrumStageBuffers(unittest.TestCase):
    def test_all_seven_disjoint_stage_cbuffer_symbols_and_exact_reverse(self):
        original=candidate()
        transformed, report=isolate(original)
        self.assertEqual(report["private_vertex_cbuffer_identifiers_disambiguated"],14)
        self.assertEqual(report["private_fragment_cbuffer_identifiers_disambiguated"],14)
        self.assertIn("GT_PRIVATE_VS_cb0_0_m0[4]",transformed)
        self.assertIn("GT_PRIVATE_PS_cb0_0_m0[10]",transformed)
        self.assertEqual(original.count("register(t0)"),transformed.count("register(t0)"))
        self.assertFalse(report["sampler_binding_material_parity_proven"])
        self.assertFalse(report["Unity_2021_Android_compilation_proven"])
        self.assertFalse(report["Adreno_pixels_proven"])

    def test_optional_varying_uniform_block_names_is_stage_local_and_reversible(self):
        original = candidate().replace(
            "float4 cb0_0_m0[4];",
            "struct cb4_struct { float4 x; };\n"
            "cbuffer cb4 : register(b4) { float4 pos; };\n"
            "float4 cb0_0_m0[4];")
        transformed, report = isolate(original, stage_uniform_blocks=True)
        self.assertTrue(report["private_uniform_block_stage_alias_mode"])
        self.assertGreater(report["private_vertex_uniform_block_identifiers_disambiguated"],0)
        self.assertGreater(report["private_fragment_uniform_block_identifiers_disambiguated"],0)
        self.assertIn("struct GT_PRIVATE_VS_cb4_struct",transformed)
        self.assertIn("cbuffer GT_PRIVATE_VS_cb4 : register(b4)",transformed)
        self.assertEqual(original.count("register(b4)"),transformed.count("register(b4)"))
        self.assertFalse(report["Unity_2021_Android_compilation_proven"])
        self.assertFalse(report["sampler_binding_material_parity_proven"])

    def test_default_stage_cbuffer_isolation_does_not_change_uniform_block_names(self):
        raw=candidate().replace("float4 cb0_0_m0[4];",
            "cbuffer cb4 : register(b4) { float4 pos; };\nfloat4 cb0_0_m0[4];")
        transformed, report=isolate(raw)
        self.assertIn("cbuffer cb4 : register(b4)",transformed)
        self.assertFalse(report["private_uniform_block_stage_alias_mode"])
        self.assertEqual(report["private_vertex_uniform_block_identifiers_disambiguated"],0)

    def test_only_original_seven_passes_accepted(self):
        for count in (0,1,6,8):
            with self.subTest(count=count), self.assertRaisesRegex(
                    ValueError,"exact_seven"):
                isolate(candidate(count))

    def test_never_apply_two_consecutive_diagnostic_rewrites(self):
        renamed,_=isolate(candidate())
        with self.assertRaisesRegex(ValueError,"unsupported_private"):
            isolate(renamed)

    def test_unrecognized_preprocessor_branch_fails_closed(self):
        broken=candidate().replace(
            "#elif defined(SHADER_STAGE_FRAGMENT)",
            "#else // fragment",1)
        with self.assertRaisesRegex(ValueError,"exact_seven"):
            isolate(broken)

    def test_missing_real_cbuffer_symbols_is_not_a_fabricated_fix(self):
        plain=candidate().replace("cb0_0_m0","foobar")
        with self.assertRaisesRegex(ValueError,"not_reversible"):
            isolate(plain)

    def test_does_not_change_identical_nonbuffer_identifiers(self):
        base=candidate()
        transformed,_=isolate(base)
        self.assertEqual(base.count("Texture2D t0"),transformed.count("Texture2D t0"))
        self.assertEqual(base.count("float4 main()"),transformed.count("float4 main()"))


if __name__=="__main__":
    unittest.main()
