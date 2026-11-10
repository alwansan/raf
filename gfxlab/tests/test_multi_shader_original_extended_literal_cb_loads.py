"""GFX064 synthetic-only original CB extended modifier, literal b/vec, SPV ranges."""
import struct,unittest
from gfxlab.tools.multi_shader_original_extended_literal_cb_loads import (
 source_extended_literal_CB_ranges,compare_private_source_extended_ranges_to_SPV,
)

def arg(t,indices=(),reps=(),modifiers=()):
    token=(t<<12)|(len(reps)<<20)|2
    for i,r in enumerate(reps):token|=r<<(22+3*i)
    if modifiers:token|=0x80000000
    chunks=[token]
    for i,kind in enumerate(modifiers):
        extra=kind|(0x80000000 if i+1<len(modifiers) else 0)
        chunks.append(extra)
    for i,r in enumerate(reps):
        x=indices[i]
        if r==0:chunks.append(x)
        elif r==1:chunks.extend([0,x])
        elif r==2:chunks.extend(arg(0,(0,),(0,)))
        elif r==3:chunks.extend([x]+arg(0,(0,),(0,)))
        elif r==4:chunks.extend([0,x]+arg(0,(0,),(0,)))
        else:raise ValueError("invalid synthetic operand index")
    return chunks

def instr(op,operands):
    body=[x for p in operands for x in p]
    return [((len(body)+1)<<24)|op]+body

def dxbc(inst):
    w=[0x50,0]+[v for op in inst for v in op];w[1]=len(w)
    return struct.pack("<%dI"%len(w),*w)

def mov(cb):
    return instr(54,[arg(0,(0,),(0,)),cb])

def parse(inst,decl=None):
    return source_extended_literal_CB_ranges(dxbc(inst),{2:8} if decl is None else decl)

class TestGFX064SourceLiteralModifier(unittest.TestCase):
    def test_extended_literal_index_is_source_range_candidate_not_semantic_parity(self):
        vectors,c=parse([mov(arg(8,(2,4),(0,0),(1,)))])
        self.assertEqual(vectors,{2:{4}})
        self.assertEqual(c["original_CB_extended_literal_index_operand_occurrences"],1)
        self.assertEqual(c["original_CB_true_dynamic_index_operand_occurrences"],0)
        self.assertEqual(c["original_CB_extended_modifier_token_type_1_occurrences"],1)

    def test_all_four_bounded_modifier_types_with_same_literal_b_vec_index(self):
        ops=[mov(arg(8,(2,3),(0,0),(i,))) for i in (0,1,2,3)]
        vectors,c=parse(ops)
        self.assertEqual(vectors,{2:{3}})
        self.assertEqual(c["original_CB_extended_literal_index_operand_occurrences"],4)
        self.assertEqual(c["original_extended_literal_CB_distinct_b_vec4_ranges"],1)
        self.assertEqual(sum(c["original_CB_extended_modifier_token_type_%d_occurrences"%i] for i in range(4)),4)

    def test_chained_bounded_modifier_keeps_literal_address_but_value_unknown(self):
        _,c=parse([mov(arg(8,(2,2),(0,0),(1,2)))])
        self.assertEqual(c["original_CB_extended_modifier_chained_operand_occurrences"],1)

    def test_nonextended_literal_not_added_to_extended_candidates(self):
        v,c=parse([mov(arg(8,(2,2),(0,0)))])
        self.assertEqual(v,{2:set()})
        self.assertEqual(c["original_CB_nonextended_literal_operand_occurrences"],1)

    def test_relative_and_extended_relative_not_promoted_to_literal(self):
        a=mov(arg(8,(2,3),(0,3)))
        b=mov(arg(8,(2,5),(0,2),(1,)))
        vectors,c=parse([a,b])
        self.assertEqual(vectors,{2:set()})
        self.assertEqual(c["original_CB_true_dynamic_index_operand_occurrences"],2)

    def test_immediate_64bit_b_and_vec4_literal_still_has_bounded_address(self):
        v,c=parse([mov(arg(8,(2,6),(1,1),(2,)))])
        self.assertEqual(v,{2:{6}})
        self.assertEqual(c["original_CB_extended_literal_index_operand_occurrences"],1)

    def test_unrecognized_operand_extension_never_silently_accepted(self):
        with self.assertRaisesRegex(ValueError,"PARSER_REJECTED"):
            parse([mov(arg(8,(2,2),(0,0),(5,)))])
        with self.assertRaisesRegex(ValueError,"PARSER_REJECTED"):
            parse([mov(arg(8,(2,2),(0,0),(0,1,2,3,0)))])

    def test_undeclared_or_out_of_bounds_original_literal_index_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNDECLARED"):
            parse([mov(arg(8,(3,2),(0,0),(1,)))])
        with self.assertRaisesRegex(ValueError,"OUTSIDE_DECLARED"):
            parse([mov(arg(8,(2,8),(0,0),(1,)))])

    def test_unsupported_opcode_is_not_claimed_to_have_zero_CB(self):
        _,c=parse([[2<<24|210,0]])
        self.assertEqual(c["original_noncovered_instructions"],1)
        self.assertEqual(c["original_CB_extended_literal_index_operand_occurrences"],0)

    def test_spv_vector_or_component_load_is_only_range_presence_not_value_parity(self):
        a=compare_private_source_extended_ranges_to_SPV({2:{4,6}},{2:{4}})
        self.assertEqual(a["extended_literal_source_distinct_CB_vec4_ranges"],2)
        self.assertEqual(a["extended_literal_source_distinct_ranges_with_SPV_OpLoad"],1)
        self.assertEqual(a["extended_literal_source_distinct_ranges_without_SPV_OpLoad"],1)
        self.assertFalse(a["extended_literal_range_presence_proves_source_modifier_value_semantics"])
        self.assertFalse(a["extended_literal_range_presence_proves_per_source_operand_read_equivalence"])

    def test_duplicate_extended_source_operand_counts_occurrences_not_duplicate_ranges(self):
        v,c=parse([mov(arg(8,(2,4),(0,0),(1,))),mov(arg(8,(2,4),(0,0),(1,)))])
        self.assertEqual(c["original_CB_extended_literal_index_operand_occurrences"],2)
        self.assertEqual(c["original_extended_literal_CB_distinct_b_vec4_ranges"],1)
        self.assertEqual(v,{2:{4}})

    def test_corrupt_DXBC_token_length_rejected(self):
        raw=dxbc([mov(arg(8,(2,3),(0,0),(1,)))])
        with self.assertRaisesRegex(ValueError,"LENGTH_MISMATCH"):
            source_extended_literal_CB_ranges(raw[:4]+b"\0"*4+raw[8:],{2:8})
        w=list(struct.unpack("<%dI"%(len(raw)//4),raw))
        w[2]=(127<<24)|54
        with self.assertRaisesRegex(ValueError,"OVERRUN"):
            source_extended_literal_CB_ranges(struct.pack("<%dI"%len(w),*w),{2:8})

if __name__=="__main__":unittest.main()
