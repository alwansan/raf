"""GT source BC3 array to true exported PNG flipbook color parity synthetic controls."""
import struct
import unittest

from scripts.gt_compare_original_bc3_to_flipbook_pixels import (
    dds_bc3,mip_range,evaluate,
)


def bc3_solid(rgb565):
    return bytes([255,255])+bytes(6)+struct.pack("<HHI",rgb565,rgb565,0)


class ExactBC3FlipbookParityTests(unittest.TestCase):
    def test_unambiguous_layer_major_compressed_source_images(self):
        from PIL import Image
        red=bc3_solid(0xF800)
        green=bc3_solid(0x07E0)
        raw=red+red+green+green  # layer0 mip0,mip1; layer1 mip0,mip1
        atlas=Image.new("RGBA",(8,4))
        atlas.paste(Image.new("RGBA",(4,4),(255,0,0,255)),(0,0))
        atlas.paste(Image.new("RGBA",(4,4),(0,255,0,255)),(4,0))
        original=evaluate(raw,atlas,2,2,4,4,2,"slice_major")
        guessed=evaluate(raw,atlas,2,2,4,4,2,"mip_major")
        self.assertEqual(original["exact_raw_orientation_match"],2)
        self.assertLess(guessed.get("exact_raw_orientation_match",0),2)

    def test_unambiguous_mip_major_compressed_source_images(self):
        from PIL import Image
        red=bc3_solid(0xF800)
        green=bc3_solid(0x07E0)
        raw=red+green+red+green
        atlas=Image.new("RGBA",(8,4))
        atlas.paste(Image.new("RGBA",(4,4),(255,0,0,255)),(0,0))
        atlas.paste(Image.new("RGBA",(4,4),(0,255,0,255)),(4,0))
        self.assertEqual(evaluate(raw,atlas,2,2,4,4,2,"mip_major")["exact_raw_orientation_match"],2)
        self.assertEqual(evaluate(raw,atlas,2,2,4,4,2,"slice_major").get("exact_raw_orientation_match",0),1)

    def test_raw_bc3_single_mip_cpu_decoder_never_invents_raw_bytes(self):
        actual=dds_bc3(bc3_solid(0xF800),4,4)
        self.assertEqual(actual.getpixel((0,0)),(255,0,0,255))
        self.assertEqual(actual.getpixel((3,3)),(255,0,0,255))
        with self.assertRaises(ValueError):
            dds_bc3(b"invalid",4,4)

    def test_mip_slice_range_formula_rejects_out_of_scope(self):
        self.assertEqual(mip_range(4,4,2,2,0,0,"slice_major"),(0,16))
        self.assertEqual(mip_range(4,4,2,2,1,0,"slice_major"),(32,16))
        self.assertEqual(mip_range(4,4,2,2,1,0,"mip_major"),(16,16))
        with self.assertRaises(Exception):
            mip_range(4,4,2,2,2,0,"slice_major")


if __name__=="__main__":
    unittest.main()
