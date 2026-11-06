"""Synthetic-only T3 D3D10/11 SHDR/SHEX token declaration reader controls."""
import json
import struct
import unittest
from scripts.t3_particle108_original_dxbc_declarations import (
    stage_declaration_counts,classify_original_pairs,shader_chunk,STATUS,
)

def instruction(opcode, extra=()):
    size=1+len(extra)
    return [opcode | (size<<24),*extra]

def dxbc(stage=1,instructions=None,tag=b"SHDR"):
    if instructions is None:
        instructions=(instruction(88,[2,3])+
                      instruction(89,[4])+
                      instruction(90,[5])+
                      instruction(156,[6])+
                      instruction(161,[7]))
    words=[(stage<<16)|(5<<4),2+len(instructions),*instructions]
    code=struct.pack("<"+"I"*len(words),*words)
    chunk=tag+struct.pack("<I",len(code))+code
    header=b"DXBC"+bytes(16)+struct.pack("<III",1,36+len(chunk),1)+struct.pack("<I",36)
    return header+chunk

def pairs():
    return [(dxbc(1),dxbc(0)) for _ in range(4)]

class TokenDeclarationTests(unittest.TestCase):
    def test_bounded_source_header_and_resource_opcode_families(self):
        tally=stage_declaration_counts(dxbc(1),1)
        self.assertEqual(tally["original_tokenized_shader_stages"],1)
        self.assertEqual(tally["original_dcl_srv_instructions"],2)
        self.assertEqual(tally["original_dcl_cbuffer_instructions"],1)
        self.assertEqual(tally["original_dcl_sampler_instructions"],1)
        self.assertEqual(tally["original_dcl_uav_instructions"],1)
        self.assertEqual(tally["original_tokenized_instructions"],5)

    def test_authentic_shdr_shex_tags_both_accepted_if_unique(self):
        self.assertTrue(shader_chunk(dxbc(tag=b"SHDR")))
        self.assertTrue(shader_chunk(dxbc(tag=b"SHEX")))

    def test_four_original_pairs_return_safe_aggregate_without_register_numbers(self):
        result=classify_original_pairs(pairs())
        self.assertEqual(result["status"],STATUS)
        self.assertEqual(result["counts"]["original_tokenized_shader_stages"],8)
        self.assertEqual(result["counts"]["original_source_vertex_fragment_keyword_pairs"],4)
        self.assertEqual(result["counts"]["original_dcl_srv_instructions"],16)
        self.assertEqual(result["counts"]["original_dcl_sampler_instructions"],8)
        self.assertIs(result["declaration_count_is_not_register_binding_layout"],True)
        self.assertFalse(result["original_binding_register_numbers_names_shader_bytes_or_GUIDs_published"])
        self.assertNotIn("_SECRET",json.dumps(result))

    def test_customdata_token_reads_second_word_length_not_op_length(self):
        source=dxbc(instructions=[53,3,0x1234]+instruction(90,[2]))
        tally=stage_declaration_counts(source,1)
        self.assertEqual(tally["original_customdata_blocks"],1)
        self.assertEqual(tally["original_dcl_sampler_instructions"],1)
        self.assertEqual(tally["original_tokenized_instructions"],2)

    def test_opcode_zero_length_rejected(self):
        source=dxbc(instructions=[88])
        with self.assertRaisesRegex(ValueError,"DXBC_DECL_OPCODE_LENGTH"):
            stage_declaration_counts(source,1)

    def test_opcode_overrun_rejected(self):
        source=dxbc(instructions=[88|(6<<24)])
        with self.assertRaisesRegex(ValueError,"DXBC_DECL_OPCODE_OVERRUN"):
            stage_declaration_counts(source,1)

    def test_customdata_short_or_overflow_rejected(self):
        for instruction_words,code in (([53,1],"DXBC_DECL_CUSTOMDATA_LENGTH"),
                                       ([53,999],"DXBC_DECL_OPCODE_OVERRUN"),
                                       ([53],"DXBC_DECL_CUSTOMDATA_LENGTH")):
            with self.subTest(words=instruction_words),self.assertRaisesRegex(ValueError,code):
                stage_declaration_counts(dxbc(instructions=instruction_words),1)

    def test_program_length_mismatch_rejected(self):
        data=bytearray(dxbc())
        struct.pack_into("<I",data,48,999)
        with self.assertRaisesRegex(ValueError,"DXBC_DECL_PROGRAM_LENGTH"):
            stage_declaration_counts(bytes(data),1)

    def test_source_shader_stage_identity_must_match(self):
        with self.assertRaisesRegex(ValueError,"DXBC_DECL_PROGRAM_STAGE"):
            stage_declaration_counts(dxbc(1),0)

    def test_chunk_integrity_rejected_before_tokenization(self):
        data=bytearray(dxbc())
        struct.pack_into("<I",data,40,2**32-1)
        with self.assertRaisesRegex(ValueError,"DXBC_DECL_CHUNK_SIZE"):
            stage_declaration_counts(bytes(data),1)

    def test_missing_shdr_shex_rejected(self):
        with self.assertRaisesRegex(ValueError,"DXBC_DECL_CODE_CHUNK_CARDINALITY"):
            stage_declaration_counts(dxbc(tag=b"ISGN"),1)

    def test_not_four_original_pairs_rejected(self):
        for sample in ([],pairs()[:3],pairs()+pairs()[:1]):
            with self.subTest(count=len(sample)),self.assertRaisesRegex(
                ValueError,"ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED"):
                classify_original_pairs(sample)

if __name__=="__main__":
    unittest.main()
