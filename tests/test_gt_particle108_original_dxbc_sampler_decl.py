"""GT: strict synthetic controls for original RDEF-free SHDR sampler register declarations."""
import struct
import unittest

from scripts.gt_particle108_original_dxbc_sampler_decl import (
    dxbc_sampler_declarations, _original_serialized_sampler_set,
    _hlsl_sampler_set, SourceError,
)

def shader_chunk(dwords,kind=b"SHDR"):
    words=[0x50,len(dwords)+2,*dwords]
    data=struct.pack("<"+"I"*len(words),*words)
    return kind+struct.pack("<I",len(data))+data

def dxbc(chunks):
    table_len=32+4*len(chunks)
    offsets=[]
    data=b""
    for chunk in chunks:
        offsets.append(table_len+len(data))
        data+=chunk
    length=table_len+len(data)
    return (b"DXBC"+b"\0"*16+struct.pack("<III",1,length,len(chunks))
            +struct.pack("<"+"I"*len(offsets),*offsets)+data)

def sampler(slot,mode=0, operand_type=6, index_mode=0):
    return ((3<<24)|(mode<<11)|90,
            (operand_type<<12)|(1<<20)|(index_mode<<22),slot)

class OriginalDxbcSamplerTests(unittest.TestCase):
    def test_exact_legal_sampler_dcl_opcode_and_operand_registers(self):
        body=sampler(0)+sampler(3,1)+sampler(9,2)
        self.assertEqual(dxbc_sampler_declarations(dxbc([shader_chunk(body)])),
                         ((0,0),(3,1),(9,2)))

    def test_missing_RDEF_chunk_legal_and_real_Source_mode_supported(self):
        # There is no RDEF chunk in this synthetic DXBC. A complete SHDR
        # declaration still proves source bytecode sampler register count.
        code=dxbc([shader_chunk(sampler(5)),b"ISGN"+struct.pack("<I",4)+b"\0"*4])
        self.assertEqual(dxbc_sampler_declarations(code),((5,0),))

    def test_duplicate_source_sampler_slot_rejected(self):
        code=dxbc([shader_chunk(sampler(0)+sampler(0))])
        with self.assertRaisesRegex(SourceError,"DXBC_SOURCE_SAMPLER_DUPLICATED"):
            dxbc_sampler_declarations(code)

    def test_invalid_declaration_operand_cannot_forge_source_sampler(self):
        for seq in (sampler(3,mode=3),sampler(3,operand_type=7),
                    sampler(3,index_mode=2),sampler(4096)):
            with self.subTest(seq=seq):
                with self.assertRaisesRegex(SourceError,"DXBC_SOURCE_SAMPLER_DECL_UNSUPPORTED|DXBC_SOURCE_SAMPLER_DUPLICATED"):
                    dxbc_sampler_declarations(dxbc([shader_chunk(seq)]))

    def test_unsupported_instruction_length_fails_closed(self):
        bad=(0<<24)|90
        with self.assertRaisesRegex(SourceError,"DXBC_SOURCE_OPCODE_UNSUPPORTED"):
            dxbc_sampler_declarations(dxbc([shader_chunk((bad,))]))

    def test_source_container_length_and_overlap_rejected(self):
        code=dxbc([shader_chunk(sampler(0))])
        with self.assertRaisesRegex(SourceError,"DXBC_SOURCE_CONTAINER_INVALID"):
            dxbc_sampler_declarations(code[:-1])
        duplicate=bytearray(dxbc([shader_chunk(sampler(0)),shader_chunk(sampler(1))]))
        struct.pack_into("<I",duplicate,36,struct.unpack_from("<I",duplicate,32)[0])
        with self.assertRaisesRegex(SourceError,"DXBC_SOURCE_CHUNKS_INVALID"):
            dxbc_sampler_declarations(bytes(duplicate))

    def test_missing_or_multiple_code_programs_rejected(self):
        with self.assertRaisesRegex(SourceError,"DXBC_SOURCE_PROGRAM_MISSING"):
            dxbc_sampler_declarations(dxbc([b"ISGN"+struct.pack("<I",4)+b"\0"*4]))
        with self.assertRaisesRegex(SourceError,"DXBC_SOURCE_PROGRAM_DUPLICATED"):
            dxbc_sampler_declarations(dxbc([shader_chunk(sampler(0)),shader_chunk(sampler(1),b"SHEX")]))

    def test_source_serialized_sampler_table_zero_and_disabled_index(self):
        program={"m_CommonParameters":{"m_TextureParams":[
            {"m_SamplerIndex":2},{"m_SamplerIndex":65535},{"m_SamplerIndex":2}]}}
        self.assertEqual(_original_serialized_sampler_set(program),{2})
        with self.assertRaisesRegex(SourceError,"SOURCE_ORIGINAL_STAGE_METADATA_INVALID"):
            _original_serialized_sampler_set({"m_CommonParameters":{"m_TextureParams":[{"m_SamplerIndex":"2"}]}})

    def test_translated_sampler_census_refuses_unbound_or_duplicate(self):
        valid="SamplerState samples : register(s1); SamplerState samp : register(s2);"
        self.assertEqual(_hlsl_sampler_set(valid),{1,2})
        with self.assertRaisesRegex(SourceError,"TRANSLATOR_SAMPLER_STAGE_INVALID"):
            _hlsl_sampler_set("SamplerState samples;")
        with self.assertRaisesRegex(SourceError,"TRANSLATOR_SAMPLER_STAGE_INVALID"):
            _hlsl_sampler_set("SamplerState x:register(s0);SamplerState y:register(s0);")

if __name__=="__main__":
    unittest.main()
