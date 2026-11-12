"""GT private only: do not infer Particle108 texture/sampler or cbuffer bindings."""
import unittest

from scripts.gt_particle108_unity_bindings import (
    BridgeError, original_names_and_registers, rebind_stage,
)

class OriginalParticleUnityBindingTests(unittest.TestCase):
    def setUp(self):
        self.indices=[("_MainTex",0),("_NoiseTex",1)]
        self.program={"m_CommonParameters":{"m_TextureParams":[
            {"m_Index":0,"m_NameIndex":0,"m_SamplerIndex":0},
            {"m_Index":1,"m_NameIndex":1,"m_SamplerIndex":1},
        ]}}
        self.code=(
            "Texture2D<float4> texture_t0 : register(t0);\n"
            "Texture2D<float4> texture_t1 : register(t1);\n"
            "SamplerState samplers0 : register(s0);\n"
            "SamplerState sampler_s1 : register(s1);\n"
            "float4 cb1_0_m0[5];\n"
            "float4 main() : SV_Target {return texture_t0.Sample(samplers0,float2(0,0))+"
            "texture_t1.Sample(sampler_s1,float2(0,0))+cb1_0_m0[0];}\n"
        )

    def test_explicit_spirv_cross_space_zero_preserved_for_samplers(self):
        spaced=self.code.replace("register(s0)", "register(s0, space0)")
        mapped,_=rebind_stage(spaced,self.program,self.indices,0)
        self.assertIn("sampler_MainTex : register(s0, space0)",mapped)

    def test_explicit_source_register_space_one_not_guessed_or_remapped(self):
        spaced=self.code.replace("register(s0)", "register(s0, space1)")
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SAMPLER_SPACE_NOT_ZERO"):
            rebind_stage(spaced,self.program,self.indices,0)

    def test_missing_translator_sampler_registration_not_replaced_by_fake_one(self):
        bad=self.code.replace("samplers0 : register(s0);","samplers0;").replace(
            "sampler_s1 : register(s1);","sampler_s1;")
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SAMPLER_DECLARATION_UNBOUND"):
            rebind_stage(bad,self.program,self.indices,0)

    def test_anonymous_sampler_name_needs_compiled_original_RDEF_source(self):
        from unittest.mock import patch
        code=self.code.replace("samplers0", "anonymousSampler")
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SYMBOL_SOURCE_REGISTER_ID_MISSING"):
            rebind_stage(code,self.program,self.indices,0)
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   return_value=((3,0,1),(3,1,1),(2,0,1),(2,1,1))):
            rebound,counts=rebind_stage(code,self.program,self.indices,0,
                                        original_dxbc=b"DXBC"+b"0"*40)
        self.assertIn("sampler_MainTex : register(s0)",rebound)
        self.assertEqual(counts["original_sampler_registers_mapped"],2)

    def test_different_original_RDEF_sampler_slot_can_never_authorize_fallback(self):
        from unittest.mock import patch
        code=self.code.replace("samplers0", "anonymousSampler")
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   return_value=((3,2,1),(3,1,1),(2,0,1),(2,1,1))):
            with self.assertRaisesRegex(BridgeError,"ORIGINAL_DXBC_RDEF_SLOT_UNPROVEN"):
                rebind_stage(code,self.program,self.indices,0,
                             original_dxbc=b"DXBC"+b"0"*40)

    def test_duplicate_original_RDEF_registers_refused(self):
        from unittest.mock import patch
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   return_value=((3,0,1),(3,0,1),(2,0,1))):
            with self.assertRaisesRegex(BridgeError,"ORIGINAL_DXBC_RDEF_AMBIGUOUS"):
                rebind_stage(self.code,self.program,self.indices,0,
                             original_dxbc=b"DXBC"+b"0"*40)

    def test_original_eight_dxbc_RDEF_absent_source_suffix_still_bound(self):
        # Real original Particle108 has 8/8 DXBC stages without RDEF.
        # Compiler-derived source suffix and same SHA-original Shader
        # serialized m_TextureParams must both be present. The parser's
        # precise ABSENT reason is distinct from malformed DXBC.
        from unittest.mock import patch
        changed=self.code.replace("texture_t0 : register(t0)","texture_t0 : register(t1)")
        changed=changed.replace("texture_t1 : register(t1)","texture_t1 : register(t0)")
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   side_effect=ValueError("DXBC_ORIGINAL_RDEF_ABSENT")):
            mapped,counts=rebind_stage(changed,self.program,self.indices,0,
                                       original_dxbc=b"DXBC"+b"0"*40)
        self.assertIn("_MainTex : register(t1)",mapped)
        self.assertIn("_NoiseTex : register(t0)",mapped)
        self.assertEqual(counts["source_DXBC_original_RDEF_verified_absent"],1)
        self.assertEqual(counts["source_to_translator_descriptor_register_drifts_authenticated"],2)

    def test_original_RDEF_absent_does_not_authorize_anonymous_translation(self):
        from unittest.mock import patch
        changed=self.code.replace("samplers0", "anonymousSampler")
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   side_effect=ValueError("DXBC_ORIGINAL_RDEF_ABSENT")):
            with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SYMBOL_SOURCE_REGISTER_ID_MISSING"):
                rebind_stage(changed,self.program,self.indices,0,
                             original_dxbc=b"DXBC"+b"0"*40)

    def test_malformed_original_DXBC_not_reclassified_as_absent_RDEF(self):
        from unittest.mock import patch
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   side_effect=ValueError("DXBC_SOURCE_CHUNK_TABLE_BOUNDS")):
            with self.assertRaisesRegex(BridgeError,"ORIGINAL_DXBC_RDEF_SLOT_UNPROVEN"):
                rebind_stage(self.code,self.program,self.indices,0,
                             original_dxbc=b"DXBC"+b"0"*40)

    def test_original_source_registers_source_bound_exact(self):
        t,s=original_names_and_registers(self.program,self.indices)
        self.assertEqual(t,{0:"_MainTex",1:"_NoiseTex"})
        self.assertEqual(s,{0:"sampler_MainTex",1:"sampler_NoiseTex"})

    def test_fragment_binding_preserves_registers_and_source_stage_isolation(self):
        code,report=rebind_stage(self.code,self.program,self.indices,0)
        self.assertIn("Texture2D<float4> _MainTex : register(t0);",code)
        self.assertIn("Texture2D<float4> _NoiseTex : register(t1);",code)
        self.assertIn("SamplerState sampler_MainTex : register(s0);",code)
        self.assertIn("SamplerState sampler_NoiseTex : register(s1);",code)
        self.assertIn("float4 GT_ORIGINAL_PS_cb1_0_m0[5]",code)
        self.assertEqual(report["original_sampler_registers_mapped"],2)
        self.assertTrue(report["original_register_annotations_preserved"])
        self.assertNotIn("samplers0",code)

    def test_vertex_buffer_stage_named_distinct(self):
        vs,_=rebind_stage(self.code,self.program,self.indices,1)
        fs,_=rebind_stage(self.code,self.program,self.indices,0)
        self.assertIn("GT_ORIGINAL_VS_cb1_0_m0",vs)
        self.assertIn("GT_ORIGINAL_PS_cb1_0_m0",fs)
        self.assertNotIn("GT_ORIGINAL_VS_cb1_0_m0",fs)

    def test_unknown_original_suffix_rejected_even_when_translated_slot_is_valid(self):
        changed=self.code.replace("texture_t0 : register(t0)", "texture_t3 : register(t0)")
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SOURCE_TEXTURE_SLOT_MISSING"):
            rebind_stage(changed,self.program,self.indices,1)

    def test_compiled_original_RDEF_authorizes_descriptor_renumber_without_rewriting_register(self):
        # SPIRV-Cross HLSL register() slots are NOT the original vkd3d
        # resource identity. Require source symbol suffix + original RDEF,
        # and preserve the emitted compiler binding annotations byte-for-byte.
        from unittest.mock import patch
        changed=self.code
        changed=changed.replace("texture_t0 : register(t0)","texture_t0 : register(t1)")
        changed=changed.replace("texture_t1 : register(t1)","texture_t1 : register(t0)")
        changed=changed.replace("samplers0 : register(s0)","samplers0 : register(s1)")
        changed=changed.replace("sampler_s1 : register(s1)","sampler_s1 : register(s0)")
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SYMBOL_REGISTER_ID_DRIFT"):
            rebind_stage(changed,self.program,self.indices,0)
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   return_value=((3,0,1),(3,1,1),(2,0,1),(2,1,1))):
            mapped,proof=rebind_stage(changed,self.program,self.indices,0,
                                      original_dxbc=b"DXBC"+b"0"*40)
        self.assertIn("_MainTex : register(t1)",mapped)
        self.assertIn("_NoiseTex : register(t0)",mapped)
        self.assertIn("sampler_MainTex : register(s1)",mapped)
        self.assertIn("sampler_NoiseTex : register(s0)",mapped)
        self.assertEqual(proof["source_to_translator_descriptor_register_drifts_authenticated"],4)

    def test_duplicate_source_suffix_cannot_hide_behind_distinct_translated_registers(self):
        from unittest.mock import patch
        changed=self.code.replace("texture_t1 : register(t1)","texture_t0 : register(t1)")
        with patch("scripts.gt_particle108_unity_bindings.source_rdef",
                   return_value=((3,0,1),(3,1,1),(2,0,1),(2,1,1))):
            with self.assertRaisesRegex(BridgeError,"TRANSLATOR_RESOURCE_COLLISION"):
                rebind_stage(changed,self.program,self.indices,0,
                             original_dxbc=b"DXBC"+b"0"*40)

    def test_missing_serialized_sampler_rejected(self):
        self.program["m_CommonParameters"]["m_TextureParams"][1]["m_SamplerIndex"]=65535
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SOURCE_SAMPLER_SLOT_MISSING"):
            rebind_stage(self.code,self.program,self.indices,0)

    def test_mismatched_original_shader_properties_fail_closed(self):
        self.indices=[("_MainTex",0)]
        with self.assertRaisesRegex(BridgeError,"ORIGINAL_TEXTURE_NAME_INDEX_MISSING"):
            rebind_stage(self.code,self.program,self.indices,0)

    def test_unreferenced_original_non_identifier_name_is_allowed(self):
        # Unity Shader m_NameIndices also contains symbolic engine/keyword
        # metadata. We must reject only a non-HLSL *texture* source name.
        self.indices.append(("Not an HLSL identifier",999))
        text,report=rebind_stage(self.code,self.program,self.indices,0)
        self.assertIn("sampler_MainTex",text)
        self.assertEqual(report["original_sampler_registers_mapped"],2)

    def test_non_identifier_original_texture_name_is_rejected(self):
        self.indices[0]=("not a valid texture property",0)
        with self.assertRaisesRegex(BridgeError,"ORIGINAL_TEXTURE_PARAMETER_NAME_NOT_IDENTIFIER"):
            rebind_stage(self.code,self.program,self.indices,0)

    def test_conflicting_source_name_index_collisions_refused(self):
        self.indices.append(("_Other",0))
        with self.assertRaisesRegex(BridgeError,"ORIGINAL_NAME_INDEX_COLLISION"):
            rebind_stage(self.code,self.program,self.indices,0)

    def test_identical_duplicate_source_name_index_is_no_op(self):
        self.indices.append(("_MainTex",0))
        code,_=rebind_stage(self.code,self.program,self.indices,0)
        self.assertIn("Texture2D<float4> _MainTex",code)

    def test_source_proven_textureless_vertex_stage_does_not_invent_sampler(self):
        # A genuinely sampler-free vertex stage must be compiled as-is:
        # no register may be synthesized from a fragment program.
        bare={"m_CommonParameters":{"m_TextureParams":[]}}
        vertex="float4 cb1_0_m0[5]; float4 main():SV_POSITION {return cb1_0_m0[0];}"
        fixed,proof=rebind_stage(vertex,bare,self.indices,1)
        self.assertIn("GT_ORIGINAL_VS_cb1_0_m0",fixed)
        self.assertEqual(proof["original_sampler_registers_mapped"],0)
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_NO_SOURCE_SAMPLER_DECLARATIONS"):
            rebind_stage(vertex,bare,self.indices,0)

    def test_vertex_with_source_sampler_metadata_but_no_declaration_fails(self):
        vertex="float4 cb1_0_m0[5]; float4 main():SV_POSITION {return cb1_0_m0[0];}"
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_NO_SOURCE_SAMPLER_DECLARATIONS"):
            rebind_stage(vertex,self.program,self.indices,1)

    def test_shared_original_sampler_with_distinct_textures_rejected(self):
        self.program["m_CommonParameters"]["m_TextureParams"][1]["m_SamplerIndex"]=0
        with self.assertRaisesRegex(BridgeError,"ORIGINAL_SAMPLER_REGISTER_AMBIGUOUS"):
            rebind_stage(self.code,self.program,self.indices,0)

    def test_resource_symbol_without_original_suffix_fails_closed(self):
        changed=self.code.replace("samplers0", "unknownSampler")
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SYMBOL_SOURCE_REGISTER_ID_MISSING"):
            rebind_stage(changed,self.program,self.indices,1)

    def test_source_register_slot_absent_even_if_symbol_matches_is_rejected(self):
        changed=self.code.replace("texture_t1 : register(t1)", "texture_t2 : register(t2)")
        with self.assertRaisesRegex(BridgeError,"TRANSLATOR_SOURCE_TEXTURE_SLOT_MISSING"):
            rebind_stage(changed,self.program,self.indices,1)

    def test_invalid_or_empty_private_hlsl_fails_closed(self):
        for wrong in ("",123,None):
            with self.subTest(wrong=wrong):
                with self.assertRaises(BridgeError):
                    rebind_stage(wrong,self.program,self.indices,0)

    def test_original_provenance_does_not_fabricate_texture_param(self):
        self.program["m_CommonParameters"]["m_TextureParams"]=[]
        with self.assertRaises(BridgeError):
            rebind_stage(self.code,self.program,self.indices,0)

if __name__=="__main__":
    unittest.main()
