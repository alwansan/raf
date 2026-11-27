import unittest
from unittest.mock import patch
from scripts import gt_patch_dxt5nm_png_alpha_policy as p
from scripts import gt_authored_dxt5nm_alpha_exporter_witness as w

class SelectivePolicy(unittest.TestCase):
    def test_pinned_input_required(self):
        with self.assertRaises(ValueError):p.repair(p.ANCHOR)
    def test_unique_anchor_required(self):
        for raw in (b"none",p.ANCHOR*2):
            with patch.object(p,"PIN",p.git_blob(raw)):
                with self.assertRaises(ValueError):p.repair(raw)
    def test_one_source_replacement(self):
        raw=b"start\n"+p.ANCHOR+b"\nend"
        with patch.object(p,"PIN",p.git_blob(raw)):
            got=p.repair(raw)
        self.assertEqual(got,b"start\n"+p.REPLACEMENT+b"\nend")
        self.assertIn(b"TextureUsageMode.NormalmapDXT5nm",got)
        self.assertIn(b"TextureImporterType.NormalMap",got)
        self.assertIn(b"ImageExportFormat.Png",got)
        self.assertIn(b".Sprites.Count == 0",got)
    def test_exact_metadata(self):
        a=b"guid: "+b"a"*32+b"\ntimeCreated: 123\nTextureImporter:\n  alphaIsTransparency: 1\n  compressionQuality: 50\n"
        b=a.replace(b"a"*32,b"b"*32).replace(b"123",b"456").replace(b"alphaIsTransparency: 1",b"alphaIsTransparency: 0")
        self.assertIsInstance(w.compare_meta(a,b,True),int)
        with self.assertRaises(ValueError):w.compare_meta(a,b.replace(b"50",b"51"),True)
    def test_ordinary_unchanged(self):
        a=b"guid: "+b"a"*32+b"\ntimeCreated: 123\nTextureImporter:\n  alphaIsTransparency: 1\n"
        self.assertIsNone(w.compare_meta(a,a,False))
        with self.assertRaises(ValueError):w.compare_meta(a,a.replace(b"alphaIsTransparency: 1",b"alphaIsTransparency: 0"),False)
