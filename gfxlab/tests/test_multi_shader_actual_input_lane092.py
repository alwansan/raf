import json,struct,unittest
from gfxlab.tools.multi_shader_actual_input_lane092 import audit_actual_input_lanes092,private_source_input_use_summary
from gfxlab.tests.test_multi_shader_spv_dxbc_input_ubo_overlap088 import body,source_input,AUTH,dis
from gfxlab.tests.test_multi_shader_spv_dxbc_input_signature089 import fake_container

def shdr(lane=2,reg=2,op=54):
    # mov r0.x, v[reg].<selected lane> (public synthetic operands only).
    dest=2|(1<<4)|(1<<20)
    src=2|(2<<2)|(lane<<4)|(1<<12)|(1<<20)
    w=[0,10,(3<<24)|95,(1<<12)|(1<<20),reg,(5<<24)|op,dest,0,src,reg]
    return struct.pack('<%dI'%len(w),*w)

def audit(mask=4,source=None,lines=None,dx=None):
    auth=dict(AUTH);auth['%105']=(2,0,16,8)
    return audit_actual_input_lanes092(dis(body() if lines is None else lines),auth,
        shdr() if source is None else source,{2:8},fake_container(mask=mask) if dx is None else dx,'vertex')

class TestActualInputLanes092(unittest.TestCase):
    def test_nonfirst_lane_and_absent_component_not_inferred_x(self):
        d=audit()
        self.assertEqual(d['actual_input_candidates'],1)
        self.assertEqual(d['source_single_lane_nonfirst'],1)
        self.assertEqual(d['target_Component_absent_lane_identity_unproven'],1)
        self.assertEqual(d['matched_register_only_signature_lane_selected'],1)
        self.assertFalse(d['source_lane_to_translated_value_identity_proven'])
    def test_explicit_equal_component_is_only_candidate(self):
        d=audit(lines=['OpDecorate %104 Component 2',*body()])
        self.assertEqual(d['explicit_Component_equals_source_lane_candidate'],1)
        self.assertFalse(d['source_lane_to_translated_value_identity_proven'])
    def test_explicit_mismatch(self):
        d=audit(lines=['OpDecorate %104 Component 0',*body()])
        self.assertEqual(d['explicit_Component_differs_source_lane'],1)
    def test_component_conflict(self):
        d=audit(lines=['OpDecorate %104 Component 0','OpDecorate %104 Component 2',*body()])
        self.assertEqual(d['target_Component_ambiguous_or_invalid'],1)
    def test_source_use_different_lane(self):
        d=audit(source=shdr(lane=1))
        self.assertEqual(d['matched_register_signature_lane_not_selected'],1)
    def test_other_register_not_conflated(self):
        d=audit(source=shdr(reg=3))
        self.assertEqual(d['candidate_without_covered_source_input_uses'],1)
    def test_invalid_signature(self):
        d=audit(dx=b'DXBCinvalid')
        self.assertEqual(d['no_unique_single_component_source_mask'],1)
    def test_multiple_signature_lanes_not_scalar_equivalence(self):
        d=audit(mask=3)
        self.assertEqual(d['no_unique_single_component_source_mask'],1)
    def test_unsupported_opcode_never_counted_no_use_proof(self):
        d=audit(source=shdr(op=400))
        self.assertEqual(d['unsupported_instructions_not_scanned'],1)
        self.assertFalse(d['complete_DXBC_input_use_coverage'])
    def test_bad_length_rejected(self):
        raw=bytearray(shdr());struct.pack_into('<I',raw,4,99)
        with self.assertRaises(ValueError):private_source_input_use_summary(bytes(raw),2,4)
    def test_mask_empty_or_multi_rejected(self):
        for m in (0,3,16):
            with self.assertRaises(ValueError):private_source_input_use_summary(shdr(),2,m)
    def test_no_private_identifiers_published(self):
        text=json.dumps(audit())
        for value in ('%104','TEXCOORD','component_mask','source_register'):
            self.assertNotIn(value,text)
        self.assertFalse(audit()['originalShaderRestored'])

if __name__=='__main__':unittest.main()
