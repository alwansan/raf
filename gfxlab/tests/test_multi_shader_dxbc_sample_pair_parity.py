"""GFX-MULTI-047 synthetic original-free DXBC instruction pair decoder tests."""
import unittest,struct
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import operand,original_sample_pairs,private_spirv_sample_pairs,SAMPLE_LAYOUTS
from gfxlab.tools.multi_shader_spirv_sample_use import spv_sample_use

def op(typ,slot=0,components=2,dim=1,rep=0):
    return [(typ<<12)|(dim<<20)|(rep<<22)|components,slot] if dim else [(typ<<12)|components]

def make_prog(instructions):
    words=[0x00000050,0]+[w for instr in instructions for w in instr]
    words[1]=len(words)
    return struct.pack("<%dI"%len(words),*words)

def sample(opcode,t=2,s=3,extra=()):
    resource_at,sampler_at,nsrc=SAMPLE_LAYOUTS[opcode]
    src=[op(0,1) for _ in range(nsrc)]
    src[resource_at]=op(7,t)
    src[sampler_at]=op(6,s)
    if extra:
        src[-1]=extra
    words=[(1+sum(len(x) for x in src)+2)<<24|opcode]+op(0,0)
    for x in src:words+=x
    return words

class TestDXBCOriginalSampleOperands(unittest.TestCase):
    def test_exact_sample_and_gather_with_real_source_slot(self):
        instructions=[sample(0x45,2,3),sample(0x48,2,3),sample(0x6d,5,1)]
        pairs,count=original_sample_pairs(make_prog(instructions),{2,5},{3,1})
        self.assertEqual(pairs,[(2,3),(2,3),(5,1)])
        self.assertEqual(count["source_original_immediate_t_s_pairs"],3)
        self.assertEqual(count["source_distinct_pairs_within_stage"],2)
        self.assertEqual(count["original_gather_ops"],1)

    def test_sample_c_and_gradient_and_bias_have_declared_extra_operands(self):
        for opcode in (0x46,0x47,0x48,0x49,0x4a,0x7e,0x7f,0x80):
            with self.subTest(opcode=opcode):
                pairs,s=original_sample_pairs(make_prog([sample(opcode,7,4)]),{7},{4})
                self.assertEqual(pairs,[(7,4)])
                self.assertEqual(s["source_sample_or_gather_operations"],1)

    def test_dynamic_texture_index_not_assumed(self):
        instr=sample(0x45,2,3)
        # Resource index is relative (kind=2): relative nested temp operand.
        pos=1+len(op(0,0))+len(op(0,1))
        instr[pos]=(7<<12)|(1<<20)|(2<<22)|2
        instr[pos+1:pos+2]=op(0,0)
        instr[0]=((len(instr))<<24)|0x45
        pairs,c=original_sample_pairs(make_prog([instr]),{2},{3})
        self.assertEqual(pairs,[])
        self.assertEqual(c["source_original_unresolved_dynamic_t_s"],1)

    def test_undeclared_register_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNDECLARED"):
            original_sample_pairs(make_prog([sample(0x45,9,3)]),{2},{3})

    def test_wrong_resource_and_sampler_operand_types_rejected(self):
        instr=sample(0x45,2,3)
        # Dest/coord 2 DWORDs each; resource starts at token #5.
        instr[5]=(0<<12)|(1<<20)|2
        with self.assertRaisesRegex(ValueError,"WRONG_TYPE"):
            original_sample_pairs(make_prog([instr]),{2},{3})

    def test_truncated_instruction_and_bad_length_rejected(self):
        instr=sample(0x45,2,3)
        instr[0]=((len(instr)-1)<<24)|0x45
        with self.assertRaisesRegex(ValueError,"TERMINATION_MISMATCH|TRUNCATED"):
            original_sample_pairs(make_prog([instr]),{2},{3})
        data=bytearray(make_prog([sample(0x45,2,3)]))
        struct.pack_into("<I",data,4,999)
        with self.assertRaisesRegex(ValueError,"DECLARED_LENGTH"):
            original_sample_pairs(bytes(data),{2},{3})

    def test_immediate_operand_and_extended_opcodes_are_bounded(self):
        ext=[(1<<31)|((len(sample(0x45,2,3))+1)<<24)|0x45,1]+sample(0x45,2,3)[1:]
        pairs,c=original_sample_pairs(make_prog([ext]),{2},{3})
        self.assertEqual(pairs,[(2,3)])
        with self.assertRaisesRegex(ValueError,"OPERAND_INDEX_REP_UNSUPPORTED"):
            operand([(7<<12)|(1<<20)|(7<<22)|2,2],0,2)

    def test_private_translated_sample_uses_reconcile_without_exporting_pairs(self):
        dis=b"""
        %10 = OpVariable %ptr UniformConstant
        %12 = OpVariable %ptr UniformConstant
        %20 = OpLoad %image %10
        %22 = OpLoad %sampler %12
        %30 = OpSampledImage %sampled %20 %22
        %33 = OpImageSampleImplicitLod %vec %30 %uv
        %34 = OpImageSampleImplicitLod %vec %30 %uv
        """
        imgs={"%10":("resource",2)}
        samp={"%12":("sampler",3)}
        pairs,unknown=private_spirv_sample_pairs(dis,imgs,samp)
        public=spv_sample_use(dis,imgs,samp)
        self.assertEqual(pairs,[(2,3),(2,3)])
        self.assertEqual(unknown,0)
        self.assertEqual(len(pairs),public["sample_or_gather_with_strict_t_s_pair"])

    def test_never_confuse_pair_multiplicity_with_distinct_identity(self):
        instr=[sample(0x45,2,3),sample(0x45,2,3)]
        pairs,c=original_sample_pairs(make_prog(instr),{2},{3})
        self.assertEqual(c["source_distinct_pairs_within_stage"],1)
        self.assertEqual(len(pairs),2)
if __name__=="__main__":unittest.main()
