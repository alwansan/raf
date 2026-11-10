"""GFX088 source-free strict DXBC dcl_input overlap and SPV UBO b provenance."""
import struct,json,unittest
from gfxlab.tools.multi_shader_spv_dxbc_input_ubo_overlap088 import (
    authenticated_spv_CB_index_iadd_source_provenance088
)
from gfxlab.tests.test_multi_shader_spv_index_local_store_value077 import dis,idxread,AUTH

# D3D10 DCL_INPUT=95; operand type INPUT=1, one immediate32 index.
def source_input(slot=2,opcode=95):
    return struct.pack("<5I",0,5,(3<<24)|opcode,(1<<12)|(1<<20),slot)

def body(location="2",binding="2",offset="0"):
    return [
       "%101 = OpTypePointer Input %1",
       "%102 = OpTypeStruct %1",
       "%103 = OpTypePointer Uniform %102",
       f"OpDecorate %104 Location {location}",
       f"OpDecorate %105 Binding {binding}",
       "OpDecorate %105 DescriptorSet 0",
       "OpDecorate %102 Block",
       f"OpMemberDecorate %102 0 Offset {offset}",
       "%104 = OpVariable %101 Input",
       "%105 = OpVariable %103 Uniform",
       "%90 = OpLoad %1 %104",
       "%106 = OpAccessChain %ptr %105 %2",
       "%91 = OpLoad %1 %106",
       "%80 = OpIAdd %1 %90 %91",
       "%81 = OpBitcast %1 %80",
       "%71 = OpInBoundsAccessChain %ptr %5 %3",
       "%72 = OpInBoundsAccessChain %ptr %5 %3",
       "OpStore %71 %81",
       "%66 = OpLoad %1 %72",
       "%70 = OpConstant %1 3",
       "%40 = OpIMul %1 %66 %70",
       "%41 = OpBitcast %1 %40",
       "%7 = OpInBoundsAccessChain %ptr %5 %3",
       "%8 = OpInBoundsAccessChain %ptr %5 %3",
       "OpStore %7 %41",*idxread("%8")
    ]
def count(lines=None,slot=2,authed=True,cb=None,shdr=None):
    auth=dict(AUTH)
    if authed:auth["%105"]=(2,0,16,8)
    if cb is None:cb={2:8}
    return authenticated_spv_CB_index_iadd_source_provenance088(
      dis(body() if lines is None else lines),auth,
      source_input(slot) if shdr is None else shdr,cb
    )

class TestGFX088OriginalCBAndInputDeclarationProvenance(unittest.TestCase):
    def test_private_overlap_and_source_cb_auth_member_offset(self):
        d=count()
        self.assertEqual(d["SPV_input_numeric_source_dcl_location_overlap_candidate_numeric_location_overlaps_source_vreg"],1)
        self.assertEqual(d["SPV_uniform_global_original_source_b_authentication_source_b_global_symbolic_auth"],1)
        self.assertEqual(d["SPV_uniform_selected_member_offset_vs_authenticated_layout_member_offset_unique_matches_source_auth"],1)
        self.assertFalse(d["SPV_numeric_Location_overlap_proves_DXBC_input_semantic_match"])
        self.assertFalse(d["SPV_original_b_global_auth_proves_Unity_Material_CB_member_bytes"])
        self.assertFalse(d["SPV_selected_member_Offset_match_proves_runtime_binding_correct"])

    def test_different_source_dcl_input_slot_not_claimed_equal(self):
        d=count(slot=3)
        self.assertEqual(d["SPV_input_numeric_source_dcl_location_overlap_candidate_no_numeric_location_overlap"],1)
        self.assertEqual(d["SPV_uniform_global_original_source_b_authentication_source_b_global_symbolic_auth"],1)

    def test_source_has_no_dcl_input(self):
        d=count(shdr=struct.pack("<2I",0,2))
        self.assertEqual(d["SPV_input_numeric_source_dcl_location_overlap_candidate_original_dcl_input_absent"],1)

    def test_malformed_source_program_fails_closed(self):
        d=count(shdr=struct.pack("<5I",0,6,(3<<24)|95,(1<<12)|(1<<20),2))
        self.assertEqual(d["SPV_input_numeric_source_dcl_location_overlap_candidate_unresolved"],1)

    def test_spv_uniform_global_without_prior_auth_not_faked(self):
        d=count(authed=False)
        self.assertEqual(d["SPV_uniform_global_original_source_b_authentication_no_prior_source_b_global_authentication"],1)
        self.assertEqual(d["SPV_uniform_selected_member_offset_vs_authenticated_layout_no_source_auth"],1)

    def test_source_cb_mismatch_blocks_global_auth(self):
        d=count(cb={8:8})
        self.assertEqual(d["SPV_uniform_global_original_source_b_authentication_malformed_or_missing_source_b_auth"],1)

    def test_binding_numeric_conflict_blocks_source_b_proof(self):
        d=count(lines=body(binding="7"))
        self.assertEqual(d["SPV_uniform_global_original_source_b_authentication_binding_conflicts_source_b_auth"],1)
        self.assertEqual(d["SPV_uniform_selected_member_offset_vs_authenticated_layout_unverified"],1)

    def test_selected_member_offset_differs_from_auth(self):
        d=count(lines=body(offset="4"))
        self.assertEqual(d["SPV_uniform_selected_member_offset_vs_authenticated_layout_member_offset_unique_differs_source_auth"],1)

    def test_missing_binding_does_not_pass_auth(self):
        lines=[x for x in body() if x!="OpDecorate %105 Binding 2"]
        d=count(lines=lines)
        self.assertEqual(d["SPV_uniform_global_original_source_b_authentication_missing_or_ambiguous_binding_vs_source_b"],1)

    def test_private_identifiers_and_numeric_slots_never_exported(self):
        d=count()
        output=json.dumps(d)
        for private in ("%104","%105","%106","%90","%91"):
            self.assertNotIn(private,output)
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])

if __name__=="__main__": unittest.main()
