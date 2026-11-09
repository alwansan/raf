#!/usr/bin/env python3
"""Regression tests for PNG semantic scanline integrity (no game assets)."""
import struct
import unittest
import zlib
from t5_verify_png_bytes import validate_png

def chunk(name, data):
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xffffffff)

def png(scanlines, *, depth=8, color=2, width=1, height=1, interlace=0):
    ihdr = struct.pack(">IIBBBBB", width, height, depth, color, 0, 0, interlace)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(scanlines)) + chunk(b"IEND", b"")

class ScanlineTests(unittest.TestCase):
    def test_valid_rgb(self):
        self.assertEqual(validate_png(png(b"\x00\x01\x02\x03")), (1, 1))
    def test_truncated_scanline(self):
        with self.assertRaisesRegex(ValueError, "scanline payload size"):
            validate_png(png(b"\x00\x01\x02"))
    def test_extra_scanline_bytes(self):
        with self.assertRaisesRegex(ValueError, "scanline payload size"):
            validate_png(png(b"\x00\x01\x02\x03\x04"))
    def test_invalid_filter(self):
        with self.assertRaisesRegex(ValueError, "scanline filter"):
            validate_png(png(b"\x05\x01\x02\x03"))
    def test_invalid_color_depth_pair(self):
        with self.assertRaisesRegex(ValueError, "color type"):
            validate_png(png(b"\x00\x01\x02\x03", depth=4, color=2))
    def test_two_rows(self):
        self.assertEqual(validate_png(png(b"\x00\x01\x02\x03\x04\x04\x05\x06", height=2)), (1, 2))

if __name__ == "__main__":
    unittest.main()
