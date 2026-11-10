import struct,unittest
from gfxlab.tools.multi_shader_one_pass_spirv import dxbc_containers,exact_pairs,key
def fake_dxbc():
    # Synthetic DXBC-shaped container, never genuine game data.
    data=bytearray(48)
    data[0:4]=b"DXBC"
    struct.pack_into("<I",data,24,48)
    struct.pack_into("<I",data,28,1)
    struct.pack_into("<I",data,32,36)
    data[36:40]=b"SHEX"
    struct.pack_into("<I",data,40,4)
    return bytes(data)
class TestOnePassPair(unittest.TestCase):
    def test_bounded_dxbc_header(self):
        self.assertEqual(len(dxbc_containers(b"HEADER"+fake_dxbc())),1)
        self.assertEqual(dxbc_containers(b"FAKE_DXBC_NO_HEADER"),[])
        corrupt=bytearray(fake_dxbc());struct.pack_into("<I",corrupt,24,9000000)
        self.assertEqual(dxbc_containers(corrupt),[])
    def test_exact_bucket_and_keywords_no_guessed_pair(self):
        v={"m_PlayerSubPrograms":[[{"m_BlobIndex":1,"m_GlobalKeywords":["A"],"m_ShaderHardwareTier":1}]]}
        f={"m_PlayerSubPrograms":[[{"m_BlobIndex":2,"m_GlobalKeywords":["A"],"m_ShaderHardwareTier":1}]]}
        self.assertEqual(len(exact_pairs({"progVertex":v,"progFragment":f})),1)
        f["m_PlayerSubPrograms"][0][0]["m_GlobalKeywords"]=["B"]
        self.assertEqual(len(exact_pairs({"progVertex":v,"progFragment":f})),0)
    def test_ambiguous_same_stage_variant_is_rejected(self):
        same={"m_BlobIndex":1,"m_GlobalKeywords":["A"]}
        v={"m_PlayerSubPrograms":[[same,dict(same)]]}
        f={"m_PlayerSubPrograms":[[{"m_BlobIndex":2,"m_GlobalKeywords":["A"]}]]}
        self.assertEqual(len(exact_pairs({"progVertex":v,"progFragment":f})),0)
