"""GT synthetic controls: compiler-only inline sampler workaround is NEVER original fidelity."""
import re
import unittest

from scripts.gt_particle108_unbound_inline_samplers import inline_trial

def original_derived_fixture(samplers=None, branches=4):
    if samplers is None:
        samplers=("SamplerState samplers0 : register(s0);\n"
                  "float4 main():SV_Target{return 1;}\n")
    stage=(
        "#if defined(SHADER_STAGE_VERTEX)\n"
        "SamplerState samplers0 : register(s0);\n"
        "float4 cb1_0_m0[5];\n"
        "#elif defined(SHADER_STAGE_FRAGMENT)\n"
        +samplers+
        "float4 cb1_0_m0[21];\n"
        "#else\n#error Unsupported_stage\n#endif\n"
    )
    return ('Shader "Synthetic/Particle" { SubShader { Pass {\n'
            'HLSLPROGRAM\n#pragma vertex main\n#pragma fragment main\n'
            '#pragma multi_compile __ LOCAL_ALPHA\n'
            '#pragma multi_compile __ LOCAL_BETA\n'
            +stage*branches+'ENDHLSL\n} } }\n')

class InlineSamplerApproximationControls(unittest.TestCase):
    def test_private_aliases_are_literal_unity_inline_sampler_conventions(self):
        original=original_derived_fixture()
        rewritten,counts=inline_trial(original)
        self.assertEqual(counts["source_private_VS_sampler_declarations_rewritten"],4)
        self.assertEqual(counts["source_private_PS_sampler_declarations_rewritten"],4)
        self.assertIn("GT_Unbound_VS_samplers0_Linear_Repeat",rewritten)
        self.assertIn("GT_Unbound_PS_samplers0_Linear_Repeat",rewritten)
        self.assertNotIn("SamplerState samplers0",rewritten)
        self.assertEqual(re.findall(r'\bregister\s*\([^)]*\)',rewritten),
                         re.findall(r'\bregister\s*\([^)]*\)',original))
        self.assertEqual(rewritten.count("HLSLPROGRAM"),1)
        self.assertEqual(rewritten.count("ENDHLSL"),1)
        self.assertEqual(original.count("samplers0"),8)

    def test_multiple_samplers_are_distinct_and_no_registers_swapped(self):
        multi=("SamplerState samplers0 : register(s0);\n"
               "SamplerState samplers2 : register(s2);\n"
               "float4 main():SV_Target{return 1;}\n")
        s,c=inline_trial(original_derived_fixture(multi))
        self.assertIn("GT_Unbound_PS_samplers0_Linear_Repeat",s)
        self.assertIn("GT_Unbound_PS_samplers2_Linear_Repeat",s)
        self.assertEqual(c["source_private_PS_sampler_declarations_rewritten"],8)
        self.assertEqual(s.count("register(s2)"),4)

    def test_unbound_or_comparison_sampler_never_fake_compiles(self):
        for bad in ("SamplerState samplers0;\n",
                    "SamplerComparisonState samplers0 : register(s0);\n",
                    "SamplerState samplers0 : register(s0, space1);\n",
                    "SamplerState samplers0 : register(s0);\nSamplerState samplers0 : register(s0);\n"):
            with self.subTest(source=bad):
                with self.assertRaisesRegex(ValueError,"private_sampler"):
                    inline_trial(original_derived_fixture(bad))

    def test_missing_early_shader_or_exact_four_branches_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"source_original_four_private_stage_branches_required"):
            inline_trial(original_derived_fixture(branches=3))
        with self.assertRaisesRegex(ValueError,"private_sampler_shaderlab_invalid"):
            inline_trial(original_derived_fixture().replace("HLSLPROGRAM",""))
        with self.assertRaisesRegex(ValueError,"private_sampler_source_invalid"):
            inline_trial("")

if __name__=="__main__":
    unittest.main()
