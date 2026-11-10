"""GFX-MULTI-042 deterministic 256px PNG/CPU analytical GPU proof regression.

Only synthetic triangle, mathematical RGB and an independently constructed
PNG8 RGBA writer. Never include owner device ZIP/PNG/screenshots in unit fixtures.
"""
import struct
import unittest
import zlib
from functools import lru_cache

from gfxlab.tools.affine_fullframe_owner_zip_audit import (
    decode_rgba_png, verify_all_pixels, reference_rgb, paeth, SIG,W,H,
)

def chunk(tag,body):
    return struct.pack(">I",len(body))+tag+body+struct.pack(">I",zlib.crc32(tag+body)&0xffffffff)


def synth_rgba_frames():
    out={k:bytearray(W*H*4) for k in (
        "linear","flat","noperspective","affineemulated")}
    for row in range(H):
        for col in range(W):
            affine,perspective=reference_rgb(col,row)
            inside=min(affine)>=0
            base=4*(row*W+col)
            for key,colours in (
                ("linear",perspective),
                ("noperspective",perspective),
                ("flat",(0,0,1)),
                ("affineemulated",affine)):
                pixel=(
                    bytes(max(0,min(255,round(x*255))) for x in colours)+b"\xff"
                    if inside else b"\0\0\0\xff"
                )
                out[key][base:base+4]=pixel
    return {k:bytes(v) for k,v in out.items()}


@lru_cache(maxsize=1)
def frames():
    return synth_rgba_frames()


def encode_png_filter_cycle(rgba):
    """Synthetic PNG builder exercising every reconstruction filter 0..4."""
    prev=bytearray(W*4)
    raw=bytearray()
    stride=W*4
    for y in range(H):
        row=rgba[y*stride:(y+1)*stride]
        filtr=y%5
        raw.append(filtr)
        for x,value in enumerate(row):
            left=row[x-4] if x>=4 else 0
            up=prev[x]
            upperleft=prev[x-4] if x>=4 else 0
            predictor=(0,left,up,(left+up)//2,paeth(left,up,upperleft))[filtr]
            raw.append((value-predictor)&255)
        prev=row
    head=struct.pack(">IIBBBBB",W,H,8,6,0,0,0)
    return SIG+chunk(b"IHDR",head)+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")


class TestGfx042AllPixels(unittest.TestCase):
    def test_synthetic_png_roundtrip_all_five_filters(self):
        pixels=frames()["affineemulated"]
        self.assertEqual(decode_rgba_png(encode_png_filter_cycle(pixels)),pixels)

    def test_full_frame_cpu_model_matches_both_shader_classes(self):
        result=verify_all_pixels(frames())
        self.assertEqual(result["interior_pixel_count"],20212)
        self.assertTrue(result["flat_produces_constant_blue_full_interior"])
        self.assertTrue(result["linear_and_native_noperspective_frames_exactly_identical"])
        self.assertTrue(result["cpu_affine_matches_gpu_qualifier_workaround_all_frame"])
        self.assertTrue(result["cpu_perspective_matches_native_gpu_smooth_all_frame"])
        self.assertLess(result["mean_absolute_rgb_errors"]["linear_cpu_perspective"],.002)
        self.assertLess(result["mean_absolute_rgb_errors"]["affine_cpu_affine"],.002)
        self.assertGreater(result["mean_absolute_rgb_errors"]["affine_cpu_perspective"],.10)
        self.assertFalse(result["original_shader48_restored"])

    def test_wrong_affine_shader_must_not_pass(self):
        bad=dict(frames())
        bad["affineemulated"]=bad["linear"]
        result=verify_all_pixels(bad)
        self.assertFalse(result["cpu_affine_matches_gpu_qualifier_workaround_all_frame"])
        self.assertTrue(result["linear_and_native_noperspective_frames_exactly_identical"])

    def test_swapped_perspective_and_affine_must_not_pass(self):
        bad=dict(frames())
        bad["linear"],bad["affineemulated"]=bad["affineemulated"],bad["linear"]
        result=verify_all_pixels(bad)
        self.assertFalse(result["cpu_perspective_matches_native_gpu_smooth_all_frame"])
        self.assertFalse(result["cpu_affine_matches_gpu_qualifier_workaround_all_frame"])

    def test_png_crc_and_size_guards_fail_closed(self):
        png=bytearray(encode_png_filter_cycle(frames()["flat"]))
        png[-1]^=0x3a
        with self.assertRaisesRegex(ValueError,"CRC_INVALID"):
            decode_rgba_png(bytes(png))
        with self.assertRaisesRegex(ValueError,"MISSING_END|TRUNCATED|BOUNDS_INVALID"):
            decode_rgba_png(bytes(png[:-12]))
        with self.assertRaisesRegex(ValueError,"SIGNATURE_OR_SIZE_INVALID"):
            decode_rgba_png(b"notpng")

    def test_png_rejects_unsupported_interlace_and_dimension(self):
        png=bytearray(encode_png_filter_cycle(frames()["flat"]))
        png[20:24]=struct.pack(">I",512)
        png[29:33]=struct.pack(">I",zlib.crc32(png[12:29])&0xffffffff)
        with self.assertRaisesRegex(ValueError,"NOT_RGBA_256"):
            decode_rgba_png(bytes(png))
        with self.assertRaisesRegex(ValueError,"EXACT_FOUR_FRAMES_REQUIRED"):
            verify_all_pixels({"linear":frames()["linear"]})
