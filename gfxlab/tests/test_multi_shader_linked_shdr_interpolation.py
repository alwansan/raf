import struct
import unittest
from gfxlab.tools.multi_shader_linked_shdr_interpolation import (
    inspect_interpolation,DCL_INPUT_PS,DCL_INPUT_PS_SGV,DCL_INPUT_PS_SIV,
    MODES,
)

def shdr(instructions):
    words=[0x50,0]
    for opcode,mode,length in instructions:
        words.append((length<<24)|(mode<<11)|opcode)
        words.extend([0]*(length-1))
    words[1]=len(words)
    return struct.pack("<%dI"%len(words),*words)


class TestOriginalLinkedSHDRInterpolation(unittest.TestCase):
    def test_exact_documented_interpolation_modes(self):
        for mode,label in MODES.items():
            with self.subTest(mode=mode):
                d=inspect_interpolation(shdr([(DCL_INPUT_PS,mode,2)]),"Pixel")
                self.assertEqual(d["pixel_interpolation_declaration_total"],1)
                self.assertEqual(d["interpolation_"+label],1)
                self.assertEqual(d["ordinary_input_ps_declarations"],1)

    def test_system_interpreted_is_interpolated_but_generated_is_not(self):
        d=inspect_interpolation(shdr([
            (DCL_INPUT_PS_SIV,3,3),
            (DCL_INPUT_PS_SGV,0,3)]),"Pixel")
        self.assertEqual(d["system_value_input_ps_interpolated_declarations"],1)
        self.assertEqual(d["system_generated_input_ps_declarations"],1)
        self.assertEqual(d["interpolation_linear_centroid"],1)
        self.assertEqual(d["pixel_interpolation_declaration_total"],1)

    def test_vertex_shdr_cannot_contain_pixel_input_declaration(self):
        with self.assertRaisesRegex(ValueError,"VERTEX_CONTAINS_PIXEL"):
            inspect_interpolation(shdr([(DCL_INPUT_PS,2,2)]),"Vertex")
        d=inspect_interpolation(shdr([(101,0,2)]),"Vertex")
        self.assertEqual(d["pixel_interpolation_declaration_total"],0)

    def test_reject_undocumented_interpolation_mode(self):
        with self.assertRaisesRegex(ValueError,"UNDOCUMENTED"):
            inspect_interpolation(shdr([(DCL_INPUT_PS,15,2)]),"Pixel")

    def test_reject_truncated_and_zero_instruction(self):
        with self.assertRaisesRegex(ValueError,"BAD_TOKEN_SIZE"):
            inspect_interpolation(b"NO","Pixel")
        bad=bytearray(shdr([(DCL_INPUT_PS,2,2)]))
        struct.pack_into("<I",bad,4,100)
        with self.assertRaisesRegex(ValueError,"BAD_DECLARED_LENGTH"):
            inspect_interpolation(bytes(bad),"Pixel")
        bad=shdr([(DCL_INPUT_PS,2,1)])
        with self.assertRaisesRegex(ValueError,"TOO_SHORT"):
            inspect_interpolation(bad,"Pixel")

    def test_reject_wrong_stage_and_customdata_length(self):
        with self.assertRaisesRegex(ValueError,"STAGE_TYPE_INVALID"):
            inspect_interpolation(shdr([(DCL_INPUT_PS,2,2)]),"Compute")
        bad=shdr([(53,0,2)])
        with self.assertRaisesRegex(ValueError,"CUSTOMDATA_LENGTH_INVALID"):
            inspect_interpolation(bad,"Pixel")

    def test_non_interpolation_resource_opcodes_are_not_promoted(self):
        d=inspect_interpolation(shdr([(88,0,2),(89,0,2),(90,0,2)]),"Pixel")
        self.assertEqual(d["all_instruction_tokens"],3)
        self.assertEqual(d["pixel_interpolation_declaration_total"],0)
        self.assertEqual(d["interpolation_linear"],0)
