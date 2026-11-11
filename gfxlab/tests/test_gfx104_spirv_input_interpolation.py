"""GFX104 SPIR-V input decorations: independent synthetic binary proofs."""
import struct
import unittest
from gfxlab.tools.gfx104_spirv_input_interpolation import (
    inspect_spirv_input_interpolation as inspect,SPIRV_MAGIC)

def instr(op,*args):
    vals=((1+len(args))<<16)|op
    return [vals,*args]

def binary(*instructions):
    words=[SPIRV_MAGIC,0x00010300,0,256,0]
    for ins in instructions:words.extend(ins)
    return struct.pack("<%dI"%len(words),*words)

def direct(decoration=13):
    return binary(
        instr(32,3,1,5), # OpTypePointer: id3, storage Input, type5
        instr(59,3,8,1), # OpVariable: result id8, storage Input
        instr(71,8,decoration), # OpDecorate variable with semantic
    )

class GFX104OriginalFreeSPVTests(unittest.TestCase):
    def test_native_nonbuiltin_variable(self):
        data=inspect(direct())
        self.assertEqual(data["input_variables"],1)
        self.assertEqual(data["input_direct_noperspective_nonbuiltin"],1)
        self.assertEqual(data["input_direct_builtin_variables"],0)
        self.assertFalse(data["source_dxbc_ps_varying_identity_proven"])
        self.assertFalse(data["originalShaderRestored"])
    def test_builtin_is_not_native_ordinary_variable(self):
        data=inspect(binary(
            instr(32,3,1,5),instr(59,3,8,1),
            instr(71,8,11),instr(71,8,13)))
        self.assertEqual(data["input_direct_builtin_variables"],1)
        self.assertEqual(data["input_direct_noperspective_nonbuiltin"],0)
    def test_flat_not_miscounted_native(self):
        data=inspect(direct(14))
        self.assertEqual(data["input_direct_flat_nonbuiltin"],1)
        self.assertEqual(data["input_no_perspective_candidate_count"],0)
    def test_member_decorations_kept_separate(self):
        data=inspect(binary(
            instr(32,3,1,5),instr(59,3,8,1),
            instr(72,5,0,13),instr(72,5,1,11)))
        self.assertEqual(data["input_member_noperspective_decorations"],1)
        self.assertEqual(data["input_member_builtin_decorations"],1)
        self.assertEqual(data["input_direct_noperspective_nonbuiltin"],0)
        self.assertFalse(data["native_interface_identity_proven"])
    def test_missing_type_marks_unresolved(self):
        data=inspect(binary(instr(59,3,8,1),instr(71,8,13)))
        self.assertEqual(data["input_pointer_type_unresolved"],1)
        self.assertFalse(data["native_interface_identity_proven"])
    def test_group_decorations_warn_instead_of_claim_success(self):
        data=inspect(binary(instr(73,99),instr(32,3,1,5),instr(59,3,8,1)))
        self.assertTrue(data["group_decorations_unhandled"])
        self.assertFalse(data["source_dxbc_ps_varying_identity_proven"])
    def test_invalid_magic_and_truncated_instruction_rejected(self):
        bad=bytearray(direct());bad[0]=0
        with self.assertRaisesRegex(ValueError,"GFX104_SPIRV_HEADER"):
            inspect(bytes(bad))
        b=binary(instr(32,3,1,5))
        with self.assertRaisesRegex(ValueError,"GFX104_SPIRV_INSTRUCTION_BOUNDS"):
            inspect(b[:-4])
    def test_bad_input_length_rejected(self):
        with self.assertRaisesRegex(ValueError,"GFX104_SPIRV_SIZE"):
            inspect(b"SPV")
    def test_output_variable_not_counted_as_fragment_input(self):
        data=inspect(binary(instr(32,3,3,5),instr(59,3,8,3),instr(71,8,13)))
        self.assertEqual(data["input_variables"],0)
        self.assertEqual(data["input_no_perspective_candidate_count"],0)

if __name__=="__main__":unittest.main()
