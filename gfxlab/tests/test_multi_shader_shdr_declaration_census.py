import unittest,struct
from gfxlab.tools.multi_shader_shdr_declaration_census import declaration_counts,source_shader_chunk
def make_words(*ops):
    w=[0x50,2+len(ops),*ops]
    return struct.pack("<%dI"%len(w),*w)
def fake_dx(blob):
    length=44+len(blob)
    data=bytearray(length)
    data[:4]=b"DXBC"
    struct.pack_into("<I",data,24,length)
    struct.pack_into("<I",data,28,1)
    struct.pack_into("<I",data,32,36)
    data[36:40]=b"SHDR"
    struct.pack_into("<I",data,40,len(blob))
    data[44:]=blob
    return bytes(data)
class TestRealDXBCTokenFormat(unittest.TestCase):
    def test_count_three_resource_declarations(self):
        src=make_words((1<<24)|88,(1<<24)|89,(1<<24)|90)
        found=declaration_counts(source_shader_chunk(fake_dx(src)))
        self.assertEqual(found["dcl_resource"],1)
        self.assertEqual(found["dcl_constant_buffer"],1)
        self.assertEqual(found["dcl_sampler"],1)
        self.assertEqual(found["total_instruction_tokens"],3)
    def test_invalid_instruction_length_fails(self):
        with self.assertRaises(ValueError):declaration_counts(make_words(88))
    def test_bad_instruction_length_overrun_fails(self):
        with self.assertRaises(ValueError):declaration_counts(make_words((9<<24)|88))
    def test_bad_claimed_shdr_total_fails(self):
        buf=bytearray(make_words((1<<24)|89))
        struct.pack_into("<I",buf,4,99)
        with self.assertRaises(ValueError):declaration_counts(bytes(buf))
    def test_customdata_skip_size(self):
        # Custom block length includes opcode + size word + payload.
        w=[0x50,6,53,4,0,0]
        src=struct.pack("<6I",*w)
        out=declaration_counts(src)
        self.assertEqual(out["custom_data_blocks"],1)
