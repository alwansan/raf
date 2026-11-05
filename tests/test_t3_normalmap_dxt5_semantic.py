"""Adversarial C# BGRA UnpackNormal equivalence controls, synthetic RGBA only."""
import unittest
from PIL import Image
from scripts.t3_normalmap_dxt5_semantic import (
    _z_blue_table, unpack_original_dxt5nm_rgba, semantic_rgba_input)
from scripts.t3_decoded_texture_pixel_parity import compare_pair

class NormalSemantic(unittest.TestCase):
    def test_csharp_bgra_lane_mapping_and_truncation_at_clamped_corner(self):
        src=Image.new("RGBA",(1,1),(10,255,33,255))
        result=unpack_original_dxt5nm_rgba(src)
        self.assertEqual(result.getpixel((0,0)),(255,255,127,10))
        self.assertEqual(src.getpixel((0,0)),(10,255,33,255))
    def test_reconstructed_z_at_neutral_normal_is_floored_not_rounded(self):
        src=Image.new("RGBA",(1,1),(44,128,123,128))
        result=unpack_original_dxt5nm_rgba(src)
        self.assertEqual(result.getpixel((0,0)),(128,128,254,44))
        self.assertEqual(_z_blue_table()[(128<<8)|128],254)
    def test_old_packed_blue_is_ignored_by_upstream_normal_unwrap(self):
        first=Image.new("RGBA",(1,1),(4,100,0,200))
        second=Image.new("RGBA",(1,1),(4,100,255,200))
        a=unpack_original_dxt5nm_rgba(first)
        b=unpack_original_dxt5nm_rgba(second)
        self.assertEqual(a.tobytes(),b.tobytes())
    def test_multiphoto_data_flow_and_identity_scoped_semantics(self):
        raw=Image.new("RGBA",(2,1))
        raw.putdata([(10,255,33,255),(44,128,123,128)])
        expected=Image.new("RGBA",(2,1))
        expected.putdata([(255,255,127,10),(128,128,254,44)])
        self.assertEqual(compare_pair(raw,expected,original_id="G",exported_id="G",authenticated=True),"RGB_DRIFT")
        after=semantic_rgba_input(raw,format_code=12,color_space=0,lightmap_format=3)
        self.assertEqual(compare_pair(after,expected,original_id="G",exported_id="G",authenticated=True),"EXACT")
    def test_not_normalmap_dxt5nm_never_automatically_changes_source(self):
        im=Image.new("RGBA",(1,1),(10,20,30,40))
        r=semantic_rgba_input(im,format_code=12,color_space=0,lightmap_format=0)
        self.assertIs(r,im)
        self.assertEqual(r.getpixel((0,0)),(10,20,30,40))
    def test_wrong_usage_codec_color_space_fail_closed(self):
        im=Image.new("RGBA",(1,1),(1,2,3,4))
        for fmt,cs,mode in ((10,0,3),(12,1,3),(12,0,"3"),(12,0,True),
                            (12,2,3),(12,0,-1),(12,0,100)):
            with self.subTest(fmt=fmt,cs=cs,mode=mode),self.assertRaises(ValueError):
                semantic_rgba_input(im,format_code=fmt,color_space=cs,lightmap_format=mode)
    def test_untrusted_or_wrong_mode_pixels_refused(self):
        for im in (None,Image.new("RGB",(1,1)),Image.new("RGBA",(0,1))):
            with self.subTest(img=repr(im)),self.assertRaises(ValueError):
                unpack_original_dxt5nm_rgba(im)
    def test_no_raw_original_bytes_or_names_in_normalmap_helpers(self):
        image=Image.new("RGBA",(1,1),(200,1,2,3))
        result=unpack_original_dxt5nm_rgba(image)
        self.assertEqual(result.mode,"RGBA")
        self.assertEqual(result.size,image.size)
        self.assertNotEqual(result.tobytes(),image.tobytes())
        self.assertEqual(image.getpixel((0,0)),(200,1,2,3))
if __name__=="__main__":unittest.main()
