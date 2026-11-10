import unittest,struct
from gfxlab.tools.multi_shader_dxbc_rdef_shape import rdef_summary
def synthetic_dx(container_len=128):
    a=bytearray(container_len)
    a[:4]=b"DXBC"
    struct.pack_into("<I",a,24,container_len)
    struct.pack_into("<I",a,28,1)
    struct.pack_into("<I",a,32,36)
    a[36:40]=b"RDEF"
    struct.pack_into("<I",a,40,container_len-44)
    struct.pack_into("<4I",a,44,1,16,1,40)
    return bytes(a)
class TestRdefBounds(unittest.TestCase):
    def test_source_count_only(self):
        x=rdef_summary(synthetic_dx())
        self.assertEqual(x["constant_buffers"],1)
        self.assertEqual(x["resource_binding_descriptors"],1)
        self.assertTrue(x["rdef_structures_bounds_checked"])
    def test_bad_header_reject(self):
        with self.assertRaises(ValueError):rdef_summary(b"DXBC")
    def test_bad_reference_offset_reject(self):
        x=bytearray(synthetic_dx())
        struct.pack_into("<I",x,32,999)
        with self.assertRaises(ValueError):rdef_summary(bytes(x))
    def test_missing_binding_table_reject(self):
        x=bytearray(synthetic_dx())
        struct.pack_into("<I",x,56,999)
        with self.assertRaises(ValueError):rdef_summary(bytes(x))
