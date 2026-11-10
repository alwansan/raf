import unittest
from gfxlab.tools.multi_shader_compiled_platform import scalar_first,safe_kind
class TestCompressedPlatformParser(unittest.TestCase):
    def test_nested_unity_blob_lengths(self):
        self.assertEqual(scalar_first([[[64]]]),64)
        self.assertEqual(scalar_first(42),42)
        with self.assertRaises(ValueError):scalar_first([])
    def test_signature_family_without_exporting_programs(self):
        self.assertEqual(safe_kind(b"DXBC"+b"x"*20),"dxbc")
        self.assertEqual(safe_kind(bytes.fromhex("03022307")+"x".encode()),"spirv")
        self.assertEqual(safe_kind(b"#version 300 es\nvoid main(){}"),"glsl_or_text")
        self.assertEqual(safe_kind(b"something private"),"other")
        self.assertEqual(safe_kind(None),"other")
