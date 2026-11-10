"""GFX090 per-actual-OpIAdd-input DXBC source declarations and SPV interp candidate."""
import struct,json,unittest
from gfxlab.tools.multi_shader_spv_actual_iadd_source_signature090 import authenticated_spv_CB_index_source_input_signature090
from gfxlab.tests.test_multi_shader_spv_dxbc_input_ubo_overlap088 import body,source_input,AUTH,dis
from gfxlab.tests.test_multi_shader_spv_dxbc_input_signature089 import fake_container

def audit(shdr=None,dxbc=None,stage="vertex",lines=None):
    auth=dict(AUTH);auth["%105"]=(2,0,16,8)
    return authenticated_spv_CB_index_source_input_signature090(
        dis(body() if lines is None else lines),auth,
        source_input() if shdr is None else shdr,{2:8},
        fake_container() if dxbc is None else dxbc,stage)

class TestGFX090PerActualInputSemanticCandidates(unittest.TestCase):
    def test_original_plain_vertex_actual_input_signature_candidate(self):
        d=audit()
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_DXBC_dcl_variant_plain"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_DXBC_input_signature_class_signature_user_semantic_full_mask_ISGN"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_DXBC_to_SPV_interpolation_candidate_vertex_plain_no_spv_interp"],1)
        self.assertFalse(d["GFX090_actual_input_signature_proves_Android_GPU_pixel_parity"])
    def test_source_PS_constant_and_SpV_Flat_consistent_but_unproven(self):
        src=struct.pack("<5I",0,5,(3<<24)|98|(1<<11),(1<<12)|(1<<20),2)
        d=audit(shdr=src,stage="fragment",lines=["OpDecorate %104 Flat",*body()])
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_DXBC_dcl_variant_pixel_plain"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_DXBC_to_SPV_interpolation_candidate_pixel_constant_to_Flat_candidate"],1)
        self.assertFalse(d["GFX090_pixel_constant_SPV_Flat_candidate_proves_original_interpolation"])
    def test_source_PS_linear_and_Flat_is_not_false_agreement(self):
        src=struct.pack("<5I",0,5,(3<<24)|98|(2<<11),(1<<12)|(1<<20),2)
        d=audit(shdr=src,stage="fragment",lines=["OpDecorate %104 Flat",*body()])
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_DXBC_to_SPV_interpolation_candidate_interpolation_mode_unresolved_or_mismatch"],1)
    def test_source_PS_linear_with_no_SPV_interpolation_decor_is_candidate(self):
        src=struct.pack("<5I",0,5,(3<<24)|98|(2<<11),(1<<12)|(1<<20),2)
        d=audit(shdr=src,stage="fragment")
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_DXBC_to_SPV_interpolation_candidate_pixel_linear_to_no_decoration_candidate"],1)
    def test_unmatched_source_input_register_not_promoted(self):
        d=audit(shdr=source_input(slot=99))
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_DXBC_dcl_variant_source_decl_register_absent"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_DXBC_to_SPV_interpolation_candidate_no_source_dcl_to_compare"],1)
    def test_missing_original_signature_fails_closed(self):
        d=audit(dxbc=b"DXBCgarbage")
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_DXBC_input_signature_class_signature_unavailable_or_untrusted"],1)
        self.assertFalse(d["GFX090_per_actual_OpIAdd_input_Location_DXBC_signature_proves_numeric_value"])
    def test_ISG1_user_system_semantic_only_structural(self):
        d=audit(dxbc=fake_container(tag=b"ISG1",system=1,mask=3))
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_DXBC_input_signature_class_signature_system_semantic_partial_mask_ISG1"],1)
        self.assertFalse(d["GFX090_per_actual_OpIAdd_input_Location_DXBC_signature_proves_numeric_value"])
    def test_spv_BuiltIn_conflict_blocks_interpolation_candidate(self):
        d=audit(lines=["OpDecorate %104 BuiltIn Position",*body()])
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_DXBC_to_SPV_interpolation_candidate_spv_builtin_or_conflicting_interp"],1)
    def test_raw_identifier_not_exported(self):
        d=audit()
        txt=json.dumps(d)
        for tok in ("%104","%105","TEXCOORD","%90","%91"):self.assertNotIn(tok,txt)
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])

if __name__=="__main__":unittest.main()
