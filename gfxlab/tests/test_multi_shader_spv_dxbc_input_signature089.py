"""GFX089 source-free DXBC input variant and signature parser negatives."""
import struct,json,unittest
from gfxlab.tests.test_multi_shader_spv_dxbc_input_ubo_overlap088 import body,source_input,AUTH,dis
from gfxlab.tools.multi_shader_spv_dxbc_input_signature089 import (
  source_dcl_input_private,input_signature_private,
  input_interface_source_semantic089,
)

def fake_container(tag=b"ISGN",reg=2,system=0,mask=15,invalid=False):
    name=b"TEXCOORD\x00"
    prefix=(b"" if tag==b"ISGN" else struct.pack("<I",0))
    entry=struct.pack("<5IBBH",8+(24 if tag==b"ISGN" else 32),
                      0,system,3,reg,mask,mask,0)
    if tag==b"ISG1":entry=prefix+entry+struct.pack("<I",0)
    data=struct.pack("<2I",1,8)+entry+name
    if invalid:data=data[:-3]
    chunk=tag+struct.pack("<I",len(data))+data
    size=36+len(chunk)
    return (b"DXBC"+bytes(16)+struct.pack("<I",0)+
            struct.pack("<III",size,1,36)+chunk)

def check(shdr=None,dxbc=None,stage="vertex",lines=None):
    auth=dict(AUTH);auth["%105"]=(2,0,16,8)
    return input_interface_source_semantic089(
        dis(body() if lines is None else lines),auth,
        source_input() if shdr is None else shdr,{2:8},
        fake_container() if dxbc is None else dxbc,stage)

class TestGFX089OriginalInputSignature(unittest.TestCase):
    def test_original_plain_dcl_and_ISGN_user_semantic_mask(self):
        d=check()
        self.assertEqual(d["source_Input_global_count"],1)
        self.assertEqual(d["source_Input_global_numeric_dcl_kind_dcl_plain"],1)
        self.assertEqual(d["source_Input_global_signature_signature_user_semantic_full_mask_ISGN"],1)
        self.assertEqual(d["source_Input_global_SPV_interpolation_class_no_interpolation_decoration"],1)
        self.assertFalse(d["GFX089_source_signature_and_SPV_decor_prove_component_mask_parity"])
    def test_pixel_shader_interpolation_token_not_assumed_equal_spv(self):
        shdr=struct.pack("<5I",0,5,(3<<24)|98|(2<<11),
                         (1<<12)|(1<<20),2)
        d=check(shdr=shdr,stage="fragment",lines=[
            *["OpDecorate %104 Flat"],*body()])
        self.assertEqual(d["source_Input_global_numeric_dcl_kind_dcl_pixel_plain"],1)
        self.assertEqual(d["source_Input_global_dcl_interpolation_linear"],1)
        self.assertEqual(d["source_Input_global_SPV_interpolation_class_Flat"],1)
        self.assertFalse(d["GFX089_DXBC_decl_variant_and_SPV_interp_prove_runtime_interpolation"])
    def test_original_PS_SIV_requires_extra_system_semantic_token(self):
        shdr=struct.pack("<6I",0,6,(4<<24)|100|(1<<11),
                         (1<<12)|(1<<20),2,1)
        parsed=source_dcl_input_private(shdr,"fragment")
        self.assertEqual(parsed[2],("pixel_siv","constant"))
    def test_ISG1_offset_structure_and_system_value(self):
        dx=fake_container(tag=b"ISG1",system=1,mask=3)
        d=check(dxbc=dx)
        self.assertEqual(d["source_Input_global_signature_signature_system_semantic_partial_mask_ISG1"],1)
        self.assertFalse(d["GFX089_stage_global_location_equals_original_semantic_proven"])
    def test_absent_signature_is_fail_closed(self):
        d=check(dxbc=b"DXBCinvalid")
        self.assertEqual(d["source_Input_global_signature_source_signature_unavailable_or_untrusted"],1)
    def test_signature_register_mismatch_is_not_proof(self):
        d=check(dxbc=fake_container(reg=9))
        self.assertEqual(d["source_Input_global_signature_signature_register_no_match"],1)
    def test_original_dcl_register_mismatch_not_upgraded(self):
        d=check(shdr=source_input(slot=7))
        self.assertEqual(d["source_Input_global_numeric_dcl_kind_no_numeric_dcl_match"],1)
    def test_truncated_signature_no_raw_leak(self):
        d=check(dxbc=fake_container(invalid=True))
        self.assertEqual(d["source_Input_global_signature_source_signature_unavailable_or_untrusted"],1)
        self.assertNotIn("TEXCOORD",json.dumps(d))
        self.assertNotIn("%104",json.dumps(d))
    def test_malformed_dcl_program_fails_closed(self):
        shdr=struct.pack("<5I",0,6,(3<<24)|95,
                         (1<<12)|(1<<20),2)
        d=check(shdr=shdr)
        self.assertEqual(d["source_Input_global_numeric_dcl_kind_source_dcl_parse_unresolved"],1)
    def test_signature_multiple_chunks_fail_closed(self):
        original=fake_container()
        chunk=original[36:]
        two=(b"DXBC"+bytes(16)+struct.pack("<I",0)+
             struct.pack("<IIII",40+len(chunk)*2,2,40,40+len(chunk))+
             chunk+chunk)
        d=check(dxbc=two)
        self.assertEqual(d["source_Input_global_signature_source_signature_unavailable_or_untrusted"],1)
    def test_all_semantic_parity_claims_explicit_false(self):
        d=check()
        self.assertEqual(d["GFX089_previous_427_authenticated_source_CB_reads"],1)
        self.assertFalse(d["GFX089_original_pixel_parity_proven"])
        self.assertFalse(d["GFX089_original_source_CB_material_bytes_proven"])
        self.assertFalse(d["GFX089_originalShaderRestored"])

if __name__=="__main__":unittest.main()
