import unittest
from types import SimpleNamespace
from gfxlab.tools.multi_shader_binary_links import code_family,count_variant_links
class TestBinaryOriginalLinks(unittest.TestCase):
    def test_known_magic_and_nonexposure(self):
        self.assertEqual(code_family(b"DXBC"+b"\0"*8),"dxbc_at_start")
        self.assertEqual(code_family(b"abcdDXBC"+b"\0"*8),"dxbc_with_header")
        self.assertEqual(code_family(bytes.fromhex("03022307")+"x".encode()),"spirv_at_start")
        self.assertEqual(code_family(b"// header\n#version 300 es\n"),"glsl_text_marker")
        self.assertEqual(code_family(b"\x00\x01\x02"),"binary_unknown")
    def test_variant_to_binary_type_match_and_mismatch(self):
        prog=[SimpleNamespace(m_ProgramType=SimpleNamespace(name="DX11Vertex",__int__=lambda s:4),
                              m_ProgramCode=b"DXBCxxxx")]
        # Use IntEnum as real UnityPy ShaderGpuProgramType
        from enum import IntEnum
        class K(IntEnum):DX11Vertex=4
        prog[0].m_ProgramType=K.DX11Vertex
        d={"progVertex":{"m_PlayerSubPrograms":[{"m_BlobIndex":0,"m_GpuProgramType":4}]},
           "progFragment":{"m_PlayerSubPrograms":[{"m_BlobIndex":0,"m_GpuProgramType":5}]}}
        r=count_variant_links(d,prog)
        self.assertEqual(r["valid_source_blob_index_links"],2)
        self.assertEqual(r["metadata_program_type_equal"],1)
        self.assertEqual(r["metadata_program_type_mismatch"],1)
        self.assertFalse(r["android_gles_semantic_equivalence_verified"])
    def test_out_of_bounds_index_is_counted(self):
        from enum import IntEnum
        class K(IntEnum):GLES3=8
        p=[SimpleNamespace(m_ProgramType=K.GLES3,m_ProgramCode=b"#version 300 es")]
        r=count_variant_links({"progVertex":{"m_PlayerSubPrograms":[{"m_BlobIndex":7}]},
            "progFragment":{"m_PlayerSubPrograms":[]}},p)
        self.assertEqual(r["invalid_source_blob_index_links"],1)
        self.assertEqual(r["valid_source_blob_index_links"],0)
