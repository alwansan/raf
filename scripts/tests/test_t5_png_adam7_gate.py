#!/usr/bin/env python3
"""Regression for fail-closed Adam7 gate; no game assets or phone evidence."""
import importlib.util
import struct
import unittest
import zlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "t5_verify_png_bytes.py"
spec = importlib.util.spec_from_file_location("t5_verify_png_bytes", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def png(interlace, pixels):
    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, interlace)
    return module.SIGNATURE + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


class Adam7GateTests(unittest.TestCase):
    def test_noninterlaced_one_pixel_valid(self):
        self.assertEqual(module.validate_png(png(0, b"\\x00\\xff\\x00\\x00\\xff")), (1, 1))

    def test_interlaced_one_pixel_must_not_claim_verified(self):
        with self.assertRaisesRegex(ValueError, "Adam7"):
            module.validate_png(png(1, b"\\x00\\xff\\x00\\x00\\xff"))

    def test_interlaced_truncated_pixel_must_not_claim_verified(self):
        with self.assertRaises(ValueError):
            module.validate_png(png(1, b"\\x00"))

    def test_noninterlaced_truncated_pixel_rejected(self):
        with self.assertRaisesRegex(ValueError, "scanline payload size"):
            module.validate_png(png(0, b"\\x00"))


if __name__ == "__main__":
    unittest.main()
