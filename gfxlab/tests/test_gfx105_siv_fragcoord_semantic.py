"""GFX105 source-free DXBC POSITION→SPIR-V FragCoord→GLSL candidate tests."""
import struct
import unittest
from gfxlab.tools.gfx105_siv_fragcoord_semantic import (
    dxbc_ps_siv_noperspective_semantic_counts,
    spirv_fragment_builtin_inputs,generated_glsl_fragcoord_use,
    classify_siv_builtin_bridge,SPIRV_MAGIC)

def chunk(op,*args):
    return [((1+len(args))<<16)|op,*args]
def shdr(system_name=1,mode=4,opcode=100):
    # Instruction length 4: opcode, input operand token, register index, NameToken
    instr=[opcode|(mode<<11)|(4<<24),0x0,0,system_name]
    words=[0x50,2+len(instr),*instr]
    return struct.pack("<%dI"%len(words),*words)
def spv(name=15,storage=1,member=False):
    words=[SPIRV_MAGIC,0x00010300,0,100,0]
    insns=[chunk(32,3,1,5),chunk(59,3,8,storage)]
    if member:
        insns.append(chunk(72,5,0,11,name))
    else:insns.append(chunk(71,8,11,name))
    for row in insns:words.extend(row)
    return struct.pack("<%dI"%len(words),*words)

class GFX105SemanticTests(unittest.TestCase):
    def test_dxbc_noperspective_system_position_name(self):
        d=dxbc_ps_siv_noperspective_semantic_counts(shdr())
        self.assertEqual(d["siv_noperspective_position_name"],1)
        self.assertEqual(d["siv_noperspective_other_system_name"],0)
        self.assertFalse(d["siv_position_to_fragcoord_semantics_verified"])
    def test_dxbc_other_system_name_not_position(self):
        d=dxbc_ps_siv_noperspective_semantic_counts(shdr(2))
        self.assertEqual(d["siv_noperspective_position_name"],0)
        self.assertEqual(d["siv_noperspective_other_system_name"],1)
    def test_dxbc_siv_linear_does_not_need_native_np(self):
        d=dxbc_ps_siv_noperspective_semantic_counts(shdr(mode=2))
        self.assertEqual(d["siv_noperspective_declarations"],0)
    def test_spirv_fragcoord_direct_input_exact_built_in(self):
        d=spirv_fragment_builtin_inputs(spv())
        self.assertEqual(d["input_builtin_fragcoord"],1)
        self.assertEqual(d["input_builtin_other"],0)
        self.assertFalse(d["semantic_identity_to_source_dxbc_verified"])
    def test_spirv_builtin_non_fragcoord_is_separate(self):
        d=spirv_fragment_builtin_inputs(spv(name=17))
        self.assertEqual(d["input_builtin_fragcoord"],0)
        self.assertEqual(d["input_builtin_other"],1)
    def test_spirv_member_builtin_fragcoord(self):
        d=spirv_fragment_builtin_inputs(spv(member=True))
        self.assertEqual(d["input_builtin_fragcoord"],1)
    def test_spirv_output_not_counted_input(self):
        d=spirv_fragment_builtin_inputs(spv(storage=3))
        self.assertEqual(d["input_builtin_fragcoord"],0)
    def test_glsl_comments_strings_do_not_create_false_gl_fragcoord(self):
        for src in ("#version 310 es\n// gl_FragCoord\nvoid main(){}\n",
                    '#version 310 es\n/* gl_FragCoord */\nvoid main(){}\n',
                    '#version 310 es\nconst char*s="gl_FragCoord";\n'):
            self.assertFalse(generated_glsl_fragcoord_use(src))
        self.assertTrue(generated_glsl_fragcoord_use(
            "#version 310 es\nvoid main(){vec4 c=gl_FragCoord;}\n"))
    def test_three_way_candidate_requires_all_semantic_witnesses(self):
        good=classify_siv_builtin_bridge(shdr(),spv(),
            "#version 310 es\nvoid main(){vec4 p=gl_FragCoord;}\n")
        self.assertTrue(good["source_position_spirv_fragcoord_glsl_candidate"])
        self.assertFalse(good["source_ssa_register_mapping_verified"])
        self.assertFalse(good["originalShaderRestored"])
        for bad_name,bad_builtin,bad_source in (
            (2,15,"gl_FragCoord"),
            (1,17,"gl_FragCoord"),
            (1,15,"// gl_FragCoord")):
            bad=classify_siv_builtin_bridge(shdr(system_name=bad_name),spv(name=bad_builtin),
                "#version 310 es\n"+bad_source+"\n")
            self.assertFalse(bad["source_position_spirv_fragcoord_glsl_candidate"])
    def test_invalid_spirv_and_shdr_rejected(self):
        with self.assertRaisesRegex(ValueError,"GFX105_SHDR"):
            dxbc_ps_siv_noperspective_semantic_counts(shdr()[:-1])
        with self.assertRaisesRegex(ValueError,"GFX105_SPV"):
            spirv_fragment_builtin_inputs(b"short")
    def test_invalid_instruction_bounds_rejected(self):
        raw=bytearray(shdr())
        raw[8:12]=(0).to_bytes(4,"little")
        with self.assertRaisesRegex(ValueError,"GFX105_BAD_INSTRUCTION_BOUNDARY"):
            dxbc_ps_siv_noperspective_semantic_counts(bytes(raw))
    def test_grouped_decoration_blocks_proof(self):
        raw=spv()
        extra=struct.pack("<2I",(2<<16)|73,9)
        info=spirv_fragment_builtin_inputs(raw+extra)
        self.assertTrue(info["group_decorations_unhandled"])
        self.assertFalse(classify_siv_builtin_bridge(shdr(),raw+extra,"gl_FragCoord")[
            "source_position_spirv_fragcoord_glsl_candidate"])

if __name__=="__main__":
    unittest.main()
