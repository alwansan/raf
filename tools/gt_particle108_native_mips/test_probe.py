import unittest
from tools.gt_particle108_native_mips import probe as p
from scripts import gt_texture_route_payload as n

def descriptor():
    return dict(zip(p.FIELDS,p.EXPECTED))|{"m_MipsStripped":0,"m_LightmapFormat":0,"m_ColorSpace":1}

class Controls(unittest.TestCase):
    def test_unique_exact_source_shape(self):
        a=descriptor();b=descriptor();b["m_MipCount"]=1
        self.assertEqual(p.select({("a",1):a,("b",2):b}),("a",1))
    def test_ambiguous_or_stripped_source(self):
        for rows in ({1:descriptor(),2:descriptor()},{1:descriptor()|{"m_MipsStripped":1}},
                     {1:descriptor()|{"m_ColorSpace":0}},{1:descriptor()|{"m_TextureFormat":12}}):
            with self.assertRaises(ValueError):p.select(rows)
    def test_seven_exact_levels_and_mutated_smallest(self):
        d=descriptor()|{"m_StreamData":{"path":"","size":0,"offset":0},"image data":bytes(21844)}
        a=n.proof(d)
        self.assertEqual(a.mip_lengths,(16384,4096,1024,256,64,16,4))
        self.assertEqual(n.compare(a,n.proof(d)),(21844,7))
        d["image data"]=bytes(21843)+b"\x01"
        with self.assertRaises(n.Mismatch):n.compare(a,n.proof(d))
    def test_reject_truncated_or_regenerated_payload(self):
        d=descriptor()|{"m_StreamData":{"path":"","size":0,"offset":0},"image data":bytes(16384)}
        with self.assertRaises(n.Unproven):n.proof(d)
if __name__=="__main__":unittest.main()
