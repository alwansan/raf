import unittest
from PIL import Image,ImageOps
from tools.gt_top_resource_closure import selected_array as a
from scripts.gt_compare_original_bc3_to_flipbook_pixels import dds_bc3
import struct

class SelectedArrayTests(unittest.TestCase):
    def test_grid_exact_two_digits_only(self):
        guid="a"*32
        raw=("guid: "+guid+"\nTextureImporter:\n  textureShape: 4\n  flipbookRows: 0\n  flipbookColumns: 0\n  other: 9\n").encode()
        expected=raw.replace(b"Rows: 0",b"Rows: 2").replace(b"Columns: 0",b"Columns: 1")
        self.assertEqual(a.repair_bytes(raw,guid,2,1),expected)
        for bad in (raw.replace(b"Shape: 4",b"Shape: 1"),raw+b"  flipbookRows: 0\n",raw.replace(b"Rows: 0",b"Rows: 3")):
            with self.assertRaises(ValueError):
                a.repair_bytes(bad,guid,2,1)
        with self.assertRaises(ValueError):
            a.repair_bytes(raw,"b"*32,2,1)

    def test_full_top_cells_wrong_layer_order(self):
        red=bytes([255,255])+bytes(6)+struct.pack("<HHI",0xf800,0xf800,0)
        blue=bytes([255,255])+bytes(6)+struct.pack("<HHI",0x001f,0x001f,0)
        # Distinct authored layer colors; complete two-mip per-layer extent.
        raw=red+blue+blue+red
        atlas=Image.new("RGBA",(4,8))
        atlas.paste(ImageOps.flip(dds_bc3(red,4,4)),(0,0))
        atlas.paste(ImageOps.flip(dds_bc3(blue,4,4)),(0,4))
        r=a.compare_layers(raw,atlas,4,4,2,2)
        self.assertEqual(r["top_mip_layers_exact"],2)
        self.assertEqual(r["all_mip_byte_extents_verified"],4)
        self.assertTrue(r["layer_order_distinguished"])
        self.assertFalse(r["orientation_distinguished"])
        self.assertFalse(r["full_lower_mip_pixel_equivalence"])
        self.assertFalse(a.compare_layers(raw,ImageOps.flip(atlas),4,4,2,2)["all_top_mip_layers_exact"])
        with self.assertRaises(ValueError):
            a.compare_layers(raw[:-1],atlas,4,4,2,2)

    def test_exact_inline_source_extent_and_stream(self):
        tree=dict(m_Width=1024,m_Height=1024,m_Depth=2,m_MipCount=11,m_Format=100,
                  m_StreamData={"size":0,"offset":0,"path":""},m_ImageData=bytes(2796256))
        self.assertEqual(len(a.exact_inline(tree)[1]),2796256)
        tree["m_StreamData"]["size"]=1
        with self.assertRaises(ValueError):
            a.exact_inline(tree)

if __name__=="__main__":
    unittest.main()
