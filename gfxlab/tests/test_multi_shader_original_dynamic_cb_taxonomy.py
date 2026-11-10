"""Source-free GFX063 DXBC relative CB operand and real SPV dynamic OpLoad controls."""
import unittest
import struct
from gfxlab.tools.multi_shader_original_dynamic_cb_taxonomy import (
    original_cb_source_dynamic_taxonomy,spv_authenticated_dynamic_cb_pointer_loads,CATEGORIES,
)

def arg(typ, indices=(),reps=(),mod=False):
    head=(typ<<12)|(len(reps)<<20)|2|(0x80000000 if mod else 0)
    for k,r in enumerate(reps):head|=r<<(22+3*k)
    out=[head]+([0] if mod else [])
    for r,v in zip(reps,indices):
        if r==0:out.append(v)
        elif r==1:out.extend([0,v])
        elif r==2:out.extend(arg(0,(0,),(0,)))
        elif r==3:out.extend([v]+arg(0,(0,),(0,)))
        elif r==4:out.extend([0,v]+arg(0,(0,),(0,)))
        else:raise ValueError("bad synthetic rep")
    return out

def cb(reps=(0,0),mod=False,b=2,vec=3):
    return arg(8,(b,vec),reps,mod)

def mov(s):
    dst=arg(0,(0,),(0,))
    w=dst+s
    return [((len(w)+1)<<24)|54]+w

def shdr(ops):
    w=[0x50,0]+[x for op in ops for x in op]
    w[1]=len(w)
    return struct.pack("<%dI"%len(w),*w)

def tax(ops,cb_decl=None):
    return original_cb_source_dynamic_taxonomy(shdr(ops),{2:8} if cb_decl is None else cb_decl)

def synthetic_spv(path="%20 = OpAccessChain %ptr %10 %zero %dyn",load=True):
    return ("\n".join([
       "%uint = OpTypeInt 32 0", "%zero = OpConstant %uint 0",
       "%two = OpConstant %uint 2", "%10 = OpVariable %ubo Uniform",
       "%dyn = OpIAdd %uint %input %two",path,
       "%30 = OpLoad %vec %20" if load else "",
    ])+"\n").replace("%uint","%1").replace("%zero","%2").replace("%two","%3").replace("%dyn","%4").replace("%input","%5").encode()

class TestGFX063SourceDynamics(unittest.TestCase):
    def test_static_index_is_not_unknown(self):
        c=tax([mov(cb())])
        self.assertEqual(c["source_CB_static_unmodified_operand_occurrences"],1)
        self.assertEqual(c["source_CB_unresolved_dynamic_or_extended_occurrences"],0)

    def test_immediate_relative_vec_index_shapes_all_partition(self):
        ops=[mov(cb((0,rep))) for rep in (2,3,4)]
        c=tax(ops)
        self.assertEqual(c["dynamic_vec_relative"],1)
        self.assertEqual(c["dynamic_vec_immediate32_plus_relative"],1)
        self.assertEqual(c["dynamic_vec_immediate64_plus_relative"],1)
        self.assertEqual(c["source_CB_unresolved_dynamic_or_extended_occurrences"],3)

    def test_dynamic_register_and_both_indices_cannot_use_literal_cb_identity(self):
        c=tax([mov(cb((2,0))),mov(cb((2,2)))])
        self.assertEqual(c["dynamic_b_only"],1)
        self.assertEqual(c["dynamic_b_and_vec"],1)

    def test_extended_modifier_with_static_indices_is_unresolved_not_dynamic_vec(self):
        c=tax([mov(cb(mod=True))])
        self.assertEqual(c["extended_modifier_but_literal_indices"],1)
        self.assertEqual(c["source_CB_unresolved_dynamic_or_extended_occurrences"],1)
        self.assertEqual(c["dynamic_vec_relative"],0)

    def test_relative_and_extension_are_one_unresolved_occurrence(self):
        c=tax([mov(cb((0,2),mod=True))])
        self.assertEqual(c["dynamic_vec_relative"],1)
        self.assertEqual(c["source_CB_unresolved_dynamic_or_extended_occurrences"],1)
        self.assertEqual(sum(c[k] for k in CATEGORIES),1)

    def test_out_of_range_or_undeclared_literal_cb_fails(self):
        with self.assertRaisesRegex(ValueError,"OUT_OF_BOUNDS"):
            tax([mov(cb(vec=9))])
        with self.assertRaisesRegex(ValueError,"UNDECLARED"):
            tax([mov(cb(b=3))])

    def test_unsupported_dx_opcode_is_not_claimed_covered(self):
        c=tax([[2<<24|210,0]])
        self.assertEqual(c["source_arithmetic_instructions_not_covered"],1)
        self.assertEqual(c["source_CB_unresolved_dynamic_or_extended_occurrences"],0)

    def test_bad_original_DXBC_size_and_malformed_instruction_fail_closed(self):
        raw=shdr([mov(cb())])
        with self.assertRaisesRegex(ValueError,"LENGTH_INVALID"):
            original_cb_source_dynamic_taxonomy(raw[:4]+b"\0\0\0\0"+raw[8:],{2:8})
        words=list(struct.unpack("<%dI"%(len(raw)//4),raw))
        words[2]=(127<<24)|54
        with self.assertRaisesRegex(ValueError,"OVERRUN"):
            original_cb_source_dynamic_taxonomy(struct.pack("<%dI"%len(words),*words),{2:8})

class TestGFX063SPVLoadProvenance(unittest.TestCase):
    def rooted(self,s):
        return spv_authenticated_dynamic_cb_pointer_loads(s,{"%10":(2,0,16,8)})

    def test_real_dynamic_vec_pointer_opload_required_for_bounded_provenance(self):
        r=self.rooted(synthetic_spv())
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_access_chains"],1)
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],1)
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_global_roots_with_loads"],1)
        self.assertFalse(r["dynamic_source_CB_operand_to_SPV_dynamic_expression_parity_proven"])

    def test_missing_opload_is_not_any_dynamic_read_evidence(self):
        r=self.rooted(synthetic_spv(load=False))
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],0)
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_access_chains_without_load"],1)

    def test_literal_index_must_not_count_as_dynamic(self):
        r=self.rooted(synthetic_spv(path="%20 = OpAccessChain %ptr %10 %2 %3"))
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],0)

    def test_undefined_dynamic_index_is_unproven(self):
        r=self.rooted(synthetic_spv(path="%20 = OpAccessChain %ptr %10 %2 %99"))
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],0)
        self.assertGreaterEqual(r["spv_invalid_struct_member_or_unsupported_index_chains"],1)

    def test_dynamic_struct_member_does_not_gain_ubo_array_provenance(self):
        r=self.rooted(synthetic_spv(path="%20 = OpAccessChain %ptr %10 %4 %3"))
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],0)

    def test_pointer_copy_propagates_but_phi_or_select_never_inferred(self):
        s=synthetic_spv().replace(b"%30 = OpLoad %vec %20",
            b"%21 = OpCopyObject %ptr %20\n%22 = OpLoad %vec %21\n"
            b"%23 = OpSelect %ptr %condition %20 %other\n%24 = OpLoad %vec %23")
        r=self.rooted(s)
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],1)
        self.assertEqual(r["spv_unproven_select_phi_aliases"],1)

    def test_wrong_original_authentication_no_dynamic_cb_proof(self):
        s=synthetic_spv()
        r=spv_authenticated_dynamic_cb_pointer_loads(s,{"%11":(2,0,16,8)})
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],0)
        with self.assertRaisesRegex(ValueError,"LAYOUT_INVALID"):
            spv_authenticated_dynamic_cb_pointer_loads(s,{"%10":(2,0,32,8)})

    def test_nested_array_dynamic_vector_component_load(self):
        s=synthetic_spv(path="%20 = OpAccessChain %ptr %10 %2\n%21 = OpAccessChain %ptr %20 %4\n%22 = OpAccessChain %ptr %21 %3").replace(b"%30 = OpLoad %vec %20",b"%30 = OpLoad %float %22")
        r=self.rooted(s)
        self.assertEqual(r["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"],1)

if __name__=="__main__":unittest.main()
