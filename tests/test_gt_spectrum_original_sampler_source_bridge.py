"""Source-free regression tests for authenticated original Spectrum DXBC sampler naming."""
from __future__ import annotations

import unittest

from scripts.gt_spectrum_original_sampler_source_bridge import source_bind_stage


def proof(*, stage=0, tex=2, samplers=2, uavs=0, parity=True):
    return {
        "stage":stage,
        "compiled_counts":{"texture":tex,"sampler":samplers,"uav":uavs},
        "numeric_slot_parity":{
            "texture":parity,"sampler":parity,"uav":parity},
    }


class OriginalSpectrumSamplerBridgeTests(unittest.TestCase):
    def test_exact_original_resource_registers_and_names_preserved(self):
        original = ("Texture2D texture_t0 : register(t0);\n"
                    "Texture2D texture_t1 : register(t1);\n"
                    "SamplerState sampler_s0 : register(s0);\n"
                    "SamplerState sampler_s1 : register(s1);\n"
                    "float4 main():SV_Target{return 0;}")
        def rebinder(hlsl, _program, _names):
            return (hlsl.replace("texture_t0","_SourceTexA")
                    .replace("texture_t1","_SourceTexB")
                    .replace("sampler_s0","sampler_SourceTexA")
                    .replace("sampler_s1","sampler_SourceTexB"),
                    {"renamed_textures":2,"renamed_samplers":2})
        actual, stats=source_bind_stage(
            original, {}, b"fake-original-DXBC", 0, [],
            abi_checker=lambda _p,_raw,s: proof(stage=s),
            symbol_rebinder=rebinder)
        self.assertIn("sampler_SourceTexA",actual)
        self.assertIn("register(s1)",actual)
        self.assertEqual(stats["source_authenticated_sampler_names"],2)
        self.assertTrue(stats["original_register_annotations_preserved"])
        self.assertFalse(stats["original_sampler_filter_wrap_or_exported_Material_binding_proven"])

    def test_compiled_vs_serialized_abi_drift_refused(self):
        with self.assertRaisesRegex(ValueError,"resource_parity_unproven"):
            source_bind_stage("float4 main(){}", {}, b"x", 0, [],
                abi_checker=lambda *_: proof(parity=False),
                symbol_rebinder=lambda *args: ("",{}))

    def test_original_uav_or_unsupported_resource_not_guessed(self):
        with self.assertRaisesRegex(ValueError,"resource_parity_unproven"):
            source_bind_stage("float4 main(){}", {}, b"x", 0, [],
                abi_checker=lambda *_: proof(uavs=1),
                symbol_rebinder=lambda *args: ("",{}))

    def test_rebinder_must_not_rewrite_register_class_or_slot(self):
        with self.assertRaisesRegex(ValueError,"name_or_register_mismatch"):
            source_bind_stage("SamplerState sampler_s0 : register(s0);",
                {}, b"x", 0, [],
                abi_checker=lambda *_: proof(tex=0,samplers=1),
                symbol_rebinder=lambda *_: (
                    "SamplerState fake : register(s1);",
                    {"renamed_textures":0,"renamed_samplers":1}))

    def test_must_map_all_source_declared_samplers(self):
        with self.assertRaisesRegex(ValueError,"name_or_register_mismatch"):
            source_bind_stage("SamplerState sampler_s0 : register(s0);",
                {}, b"x", 0, [],
                abi_checker=lambda *_: proof(tex=0,samplers=2),
                symbol_rebinder=lambda *_: (
                    "SamplerState sampler_A : register(s0);",
                    {"renamed_textures":0,"renamed_samplers":1}))

    def test_empty_vertex_resources_allowed_only_when_source_has_none(self):
        hlsl="float4 main():SV_Position{return 0;}"
        actual,counts=source_bind_stage(hlsl,{},b"x",1,[],
            abi_checker=lambda *_: proof(stage=1,tex=0,samplers=0),
            symbol_rebinder=lambda x,*_: (
                x,{"renamed_textures":0,"renamed_samplers":0}))
        self.assertEqual(actual,hlsl)
        self.assertEqual(counts["source_authenticated_sampler_names"],0)

    def test_bad_input_type_rejected(self):
        with self.assertRaisesRegex(ValueError,"argument_invalid"):
            source_bind_stage("float4 main(){}", {}, b"x", True, [])


if __name__=="__main__":
    unittest.main()
