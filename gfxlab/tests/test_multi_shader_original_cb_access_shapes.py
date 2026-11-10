"""Synthetic source-free GFX051 DXBC b# operand and SPIR-V UBO access guards."""
import unittest,struct
from gfxlab.tools.multi_shader_original_cb_access_shapes import (
 scan_known_dxbc_cb_operands,spv_numeric_ubo_accesses,reflect_ubo_member_shapes,
 KNOWN_ARITHMETIC_ARITY)

def arg(t,indices=(),rep=(0,0)):
    head=(t<<12)|(len(indices)<<20)|2
    for n,r in enumerate(rep[:len(indices)]):head|=r<<(22+3*n)
    return [head]+list(indices)

def source(tokens):
    w=[0x50,0]+[x for i in tokens for x in i]
    w[1]=len(w)
    return struct.pack("<%dI"%len(w),*w)

def ins(op,ops):
    body=[x for operand in ops for x in operand]
    return [((1+len(body))<<24)|op]+body

class TestGFX051Synthetic(unittest.TestCase):
    def test_static_CB_vector_uses_only_from_supported_arity(self):
        mov=ins(54,[arg(0,[0]),arg(8,[2,4])])
        mul=ins(56,[arg(0,[0]),arg(8,[2,4]),arg(8,[2,7])])
        v,c=scan_known_dxbc_cb_operands(source([mov,mul]),{2:16})
        self.assertEqual(c["recognized_fixed_arity_arithmetic_instructions"],2)
        self.assertEqual(c["source_static_CB_vector_accesses_in_covered_arithmetic"],3)
        self.assertEqual(c["unique_static_CB_vec4_accesses_in_covered_arithmetic"],2)
        self.assertEqual(v[2],{4,7})

    def test_source_out_of_bounds_or_undeclared_never_counted_valid(self):
        with self.assertRaisesRegex(ValueError,"OUT_OF_RANGE"):
            scan_known_dxbc_cb_operands(source([ins(54,[arg(0,[0]),arg(8,[2,16])])]),{2:16})
        with self.assertRaisesRegex(ValueError,"UNDECLARED"):
            scan_known_dxbc_cb_operands(source([ins(54,[arg(0,[0]),arg(8,[3,0])])]),{2:16})

    def test_unsupported_opcode_is_unknown_not_no_access_claim(self):
        _,c=scan_known_dxbc_cb_operands(source([[2<<24|210,0]]),{})
        self.assertEqual(c["noncovered_source_instructions"],1)
        self.assertEqual(c["recognized_fixed_arity_arithmetic_instructions"],0)

    def test_dynamic_CB_vec_index_is_not_guessed(self):
        # Dim2: first immediate b2; second index relative to temp r0.
        cb=[(8<<12)|(2<<20)|(2<<25)|2,2]+arg(0,[0])
        mov=ins(54,[arg(0,[0]),cb])
        v,c=scan_known_dxbc_cb_operands(source([mov]),{2:8})
        self.assertEqual(v[2],set())
        self.assertEqual(c["source_dynamic_or_extended_CB_accesses_in_covered_arithmetic"],1)

    def test_truncated_source_op_and_header_rejected(self):
        raw=source([ins(54,[arg(0,[0]),arg(8,[1,2])])])
        with self.assertRaisesRegex(ValueError,"LENGTH_INVALID"):
            scan_known_dxbc_cb_operands(raw[:4]+b"\x00\x00\x00\x00"+raw[8:],{1:4})
        bad=list(struct.unpack("<%dI"%(len(raw)//4),raw))
        bad[2]=((len(bad)+1)<<24)|54
        with self.assertRaisesRegex(ValueError,"OVERRUN"):
            scan_known_dxbc_cb_operands(struct.pack("<%dI"%len(bad),*bad),{1:4})

    def test_reflected_member_shape_not_source_identity(self):
        r={"ubos":[{"type":"_x","block_size":64}],
           "types":{"_x":{"members":[{"type":"vec4","offset":0,"array":[4],"array_stride":16}]}}}
        result=reflect_ubo_member_shapes(r,{3:4})
        self.assertEqual(result["spv_reflected_members_with_explicit_offset"],1)
        self.assertEqual(result["spv_reflected_members_with_array_stride_16"],1)
        self.assertFalse(result["original_CB_member_offset_identity_from_spirv_layout_proven"])

    def test_spv_candidate_access_with_literal_constant_and_dynamic_index(self):
        dis=b"""
OpDecorate %10 DescriptorSet 0
OpDecorate %10 Binding 2
%1 = OpTypeInt 32 0
%5 = OpConstant %1 0
%6 = OpConstant %1 4
%10 = OpVariable %p Uniform
%20 = OpAccessChain %q %10 %5 %6
%21 = OpLoad %vec %20
%22 = OpAccessChain %q %10 %5 %dynamic
"""
        vectors,s=spv_numeric_ubo_accesses(dis,{2:8})
        self.assertEqual(vectors[2],{4})
        self.assertEqual(s["spv_access_chains_from_numeric_ubo_global_candidates"],2)
        self.assertEqual(s["spv_ubo_candidate_pointer_loads"],1)
        self.assertEqual(s["spv_access_chains_with_nonliteral_indices"],1)
        self.assertFalse(s["numeric_ubo_binding_proves_original_CB_identity"])

    def test_no_numeric_identity_if_set_differs(self):
        dis=b"OpDecorate %10 DescriptorSet 1\nOpDecorate %10 Binding 2\n%10 = OpVariable %p Uniform\n"
        _,s=spv_numeric_ubo_accesses(dis,{2:8})
        self.assertEqual(s["spv_uniform_global_candidates_with_same_source_b_binding"],0)

    def test_duplicate_binding_decorations_fail_closed(self):
        dis=b"OpDecorate %10 Binding 2\nOpDecorate %10 Binding 3\n%10 = OpVariable %p Uniform\n"
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            spv_numeric_ubo_accesses(dis,{2:8})
if __name__=="__main__":unittest.main()
