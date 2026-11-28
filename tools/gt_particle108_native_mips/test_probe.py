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
    def test_exact_native_class_anchor_and_meta(self):
        import tempfile
        from pathlib import Path
        guid="1234567890abcdef1234567890abcdef"
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);assets=root/"Assets";assets.mkdir()
            asset=assets/"fixture.texture2D";meta=assets/"fixture.texture2D.meta"
            asset.write_text("%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!28 &2800000\nTexture2D:\n  m_Width: 64\n")
            meta.write_text("fileFormatVersion: 2\nguid: "+guid+"\nNativeFormatImporter:\n  mainObjectFileID: 2800000\n")
            self.assertEqual(p.actual_body(root,(2800000,guid,2)),{"m_Width":64})
            with self.assertRaises(ValueError):p.actual_body(root,(2800001,guid,2))
            with self.assertRaises(ValueError):p.actual_body(root,(2800000,guid,3))
            asset.write_text(asset.read_text().replace("!u!28","!u!21"))
            with self.assertRaises(ValueError):p.actual_body(root,(2800000,guid,2))
            asset.write_text(asset.read_text().replace("!u!21","!u!28"))
            (assets/"duplicate.asset.meta").write_text(meta.read_text())
            with self.assertRaises(ValueError):p.actual_body(root,(2800000,guid,2))
if __name__=="__main__":unittest.main()
