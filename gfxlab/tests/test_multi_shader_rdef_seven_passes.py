import unittest,struct
from gfxlab.tools.multi_shader_rdef_seven_passes import chunk_counts
from gfxlab.tools.multi_shader_dxbc_rdef_shape import rdef_summary

def synthetic_dxbc(tag=b"SHEX",n=4):
    data=bytearray(44+n)
    data[:4]=b"DXBC"
    struct.pack_into("<I",data,24,len(data))
    struct.pack_into("<I",data,28,1)
    struct.pack_into("<I",data,32,36)
    data[36:40]=tag
    struct.pack_into("<I",data,40,n)
    return bytes(data)

class TestAllSevenRdef(unittest.TestCase):
    def test_valid_source_stage_chunk_counted(self):
        self.assertEqual(chunk_counts(synthetic_dxbc()),{"SHEX":1})
    def test_unknown_chunk_not_accepted_as_real_shader(self):
        with self.assertRaises(ValueError):chunk_counts(synthetic_dxbc(b"ABCD"))
    def test_overlong_chunk_rejected(self):
        d=bytearray(synthetic_dxbc());struct.pack_into("<I",d,40,1234)
        with self.assertRaises(ValueError):chunk_counts(bytes(d))
    def test_missing_rdef_is_unknown_null(self):
        d=rdef_summary(synthetic_dxbc())
        self.assertIsNone(d["constant_buffers"])
        self.assertIsNone(d["resource_binding_descriptors"])
        self.assertTrue(d["rdef_missing_in_source"])
