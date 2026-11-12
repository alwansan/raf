"""Synthetic DXBC original SAMPLE pair controls. No source game data."""
import struct
import unittest

from scripts.gt_particle108_source_sampling_pairs import (
    SampleProofError, sample_operand_pairs, source_texture_slots,
)

def operand(kind, slot, indirect=False):
    # D3D10/11 tokenized operand: type[12..19], index dimension 1D[20..21],
    # index mode immediate32[22..24]=0 or relative[22..24]=2.
    token=(kind<<12)|(1<<20)|2
    if indirect:
        token |= (2<<22)
        return [token, (0<<12)|(1<<20)|2, slot]
    return [token,slot]

def fixture(opcode=69, tex=5, sampler=2, resource_indirect=False):
    declarations=[(3<<24)|90,*operand(6,sampler)]
    source=[
        *operand(0,0),
        *operand(0,1),
        *operand(7,tex,indirect=resource_indirect),
        *operand(6,sampler),
    ]
    if opcode in (70,71,72,74):
        source += [(4<<12)|1,0]  # one-component literal
    if opcode==73:
        source += [(4<<12)|1,0,(4<<12)|1,0]
    instruction=[((1+len(source))<<24)|opcode,*source]
    words=[0x00000050,0]+declarations+instruction
    words[1]=len(words)
    body=struct.pack("<"+"I"*len(words),*words)
    chunk=b"SHDR"+struct.pack("<I",len(body))+body
    total=36+len(chunk)
    header=b"DXBC"+b"\x00"*16+struct.pack("<IIII",1,total,1,36)
    return header+chunk

class SourceSampleTests(unittest.TestCase):
    def test_direct_original_source_sample_resource_and_sampler_pair(self):
        self.assertEqual(sample_operand_pairs(fixture()),((5,2,69),))

    def test_all_six_sample_variants_are_parsed_without_descriptor_guess(self):
        for opcode in range(69,75):
            with self.subTest(opcode=opcode):
                self.assertEqual(sample_operand_pairs(fixture(opcode)),((5,2,opcode),))

    def test_indirect_resource_rejected(self):
        with self.assertRaisesRegex(SampleProofError,"REGISTER_INDIRECT"):
            sample_operand_pairs(fixture(resource_indirect=True))

    def test_undocumented_sample_opcode_size_fails_closed(self):
        wrong=bytearray(fixture())
        offset=36+8+8+12  # SHDR header + two program words + sampler declaration
        token=struct.unpack_from("<I",wrong,offset)[0]
        struct.pack_into("<I",wrong,offset,(token&0x00FFFFFF)|(8<<24))
        with self.assertRaises(SampleProofError):
            sample_operand_pairs(bytes(wrong))

    def test_serialized_texture_indices_only_not_sampler_name_guess(self):
        valid={"m_CommonParameters":{"m_TextureParams":[{"m_Index":5}]}}
        self.assertEqual(source_texture_slots(valid),{5})
        with self.assertRaisesRegex(SampleProofError,"AMBIGUOUS"):
            source_texture_slots({"m_CommonParameters":{
                "m_TextureParams":[{"m_Index":5},{"m_Index":5}]}})
        with self.assertRaises(SampleProofError):
            source_texture_slots({"m_CommonParameters":{}})

if __name__=="__main__":
    unittest.main()
