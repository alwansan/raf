"""GFX054 purely synthetic source-free Shader48 property/register evidence gates."""
import unittest
from gfxlab.tools.multi_shader_property_register_evidence_gate import build_gate, ZIP2_SHA

def docs():
    m={"experiment":"GFX-MULTI-020","source_sha":ZIP2_SHA,
       "source_stages":14,"source_shader_passes":7,
       "original_material_slot_count":7,"source_property_name_count":27,
       "material_bound_texenv_slots":21,
       "one_source_material_texture_parameter_t_sampler_bridge_proven":False,
       "original_shader_program_parameter_metadata_totals":{
          "exact_source_property_t_sampler_to_material_bridges":0,
          "stages_with_serialized_parameters":0}}
    t={"experiment":"GFX-MULTI-021","source_sha":ZIP2_SHA,
       "material_slots":7,"original_shader_serialized_property_count":27,
       "original_material_shader_property_name_parity":{"bound_texenv_slots":21},
       "original_shader_text_evidence":{"original_embedded_script_field_present":False,
           "hlsl_or_cg_program_markers_found":False,"register_syntax_marker_found":False}}
    v={"experiment":"GFX-MULTI-022","source_sha":ZIP2_SHA,
       "material_slots":7,"pass_count":7,"exact_keyword_tier_matched_pairs":524,
       "unique_referenced_stage_programs":1275,
       "all_original_variant_link_rows":{"variant_link_rows":1435,
           "texture_parameter_entries":0,"constant_buffer_binding_entries":0,
           "rdef_present_stage_programs":0,"rdef_absent_stage_programs":1275,
           "rdef_constant_buffer_descriptors":0}}
    d={"experiment":"GFX-MULTI-037","original_zip2_sha":ZIP2_SHA,
       "source_shader48_passes":7,"original_shader48_declared_property_count":27,
       "source_linked_program_counts":{"stage_link_rows":1435,
          "exact_matched_vs_fs_variant_pairs":524,
          "unique_dx11_stage_programs":1275,
          "programs_with_rdef_chunk":0,
          "programs_with_alternate_debug_or_reflection_chunk":0,
          "programs_with_original_property_tokens_in_alternate_chunk":0}}
    return m,t,v,d

class TestGFX054EvidenceGate(unittest.TestCase):
    def test_all_source_channels_absent_blocked_no_fake_mapping(self):
        r=build_gate(*docs())
        self.assertFalse(r["original_shader48_property_to_DXBC_t_s_binding_evidence_available"])
        self.assertIn("BLOCKED_",r["original_property_to_DXBC_binding_evidence_state"])
        self.assertFalse(r["originalShaderRestored"])
        self.assertFalse(r["original_property_to_DXBC_b_register_and_individual_member_byte_offsets_proven"])
        self.assertEqual(r["unique_linked_original_DX11_stage_programs"],1275)

    def test_script_markers_alone_do_not_prove_property_to_register(self):
        m,t,v,d=docs()
        t["original_shader_text_evidence"]={"original_embedded_script_field_present":True,
            "hlsl_or_cg_program_markers_found":True,"register_syntax_marker_found":True}
        r=build_gate(m,t,v,d)
        self.assertFalse(r["original_shader48_property_to_DXBC_t_s_binding_evidence_available"])

    def test_debug_text_property_name_hit_alone_does_not_prove_binding(self):
        m,t,v,d=docs()
        d["source_linked_program_counts"]["programs_with_alternate_debug_or_reflection_chunk"]=2
        d["source_linked_program_counts"]["programs_with_original_property_tokens_in_alternate_chunk"]=1
        r=build_gate(m,t,v,d)
        self.assertFalse(r["original_shader48_property_to_DXBC_t_s_binding_evidence_available"])

    def test_source_texenv_parameter_can_prove_one_exact_edge_not_all_CB(self):
        m,t,v,d=docs()
        m["original_shader_program_parameter_metadata_totals"]["exact_source_property_t_sampler_to_material_bridges"]=1
        m["original_shader_program_parameter_metadata_totals"]["stages_with_serialized_parameters"]=1
        m["one_source_material_texture_parameter_t_sampler_bridge_proven"]=True
        v["all_original_variant_link_rows"]["texture_parameter_entries"]=1
        r=build_gate(m,t,v,d)
        self.assertTrue(r["original_shader48_property_to_DXBC_t_s_binding_evidence_available"])
        self.assertFalse(r["original_property_to_DXBC_b_register_and_individual_member_byte_offsets_proven"])
        self.assertFalse(r["originalShaderRestored"])

    def test_direct_bridge_boolean_without_source_parameter_is_rejected(self):
        m,t,v,d=docs()
        m["one_source_material_texture_parameter_t_sampler_bridge_proven"]=True
        with self.assertRaisesRegex(ValueError,"CONTRADICTION"):
            build_gate(m,t,v,d)

    def test_mismatched_original_source_link_count_rejected(self):
        m,t,v,d=docs();d["source_linked_program_counts"]["stage_link_rows"]=1434
        with self.assertRaisesRegex(ValueError,"DRIFT"):
            build_gate(m,t,v,d)

    def test_wrong_sha_rejected(self):
        m,t,v,d=docs();v["source_sha"]="unverified"
        with self.assertRaisesRegex(ValueError,"SHA_PIN_MISMATCH"):
            build_gate(m,t,v,d)

    def test_rdef_census_conflict_rejected(self):
        m,t,v,d=docs()
        d["source_linked_program_counts"]["programs_with_rdef_chunk"]=1
        with self.assertRaisesRegex(ValueError,"RDEF_SOURCE_SWEEP_CONFLICT"):
            build_gate(m,t,v,d)

    def test_property_name_count_not_padded(self):
        m,t,v,d=docs();t["original_shader_serialized_property_count"]=28
        with self.assertRaisesRegex(ValueError,"DRIFT"):
            build_gate(m,t,v,d)

    def test_script_hlsl_without_embedded_script_rejected(self):
        m,t,v,d=docs();t["original_shader_text_evidence"]["hlsl_or_cg_program_markers_found"]=True
        with self.assertRaisesRegex(ValueError,"SCRIPT_MARKER_WITHOUT"):
            build_gate(m,t,v,d)

if __name__=="__main__":unittest.main()
