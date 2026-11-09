"""Regression: CRC-valid PNG chunks must not conceal corrupt IDAT streams."""
import importlib.util
import struct
import unittest
import zlib
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t5_verify_png_bytes.py"
spec = importlib.util.spec_from_file_location("t5_png_bytes", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def chunk(name, payload):
    return struct.pack(">I", len(payload)) + name + payload + struct.pack(">I", zlib.crc32(name + payload) & 0xffffffff)


def png(payload):
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return module.SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", payload) + chunk(b"IEND", b"")


class TestIdatIntegrity(unittest.TestCase):
    def test_valid_zlib_payload(self):
        self.assertEqual(module.validate_png(png(zlib.compress(bytes((0, 255, 0, 0))))), (1, 1))

    def test_invalid_zlib_payload_even_with_valid_crc(self):
        with self.assertRaisesRegex(ValueError, "IDAT"):
            module.validate_png(png(b"not a zlib stream"))

    def test_truncated_zlib_stream(self):
        with self.assertRaisesRegex(ValueError, "IDAT"):
            module.validate_png(png(zlib.compress(bytes((0, 255, 0, 0)))[:-2]))

    def test_trailing_zlib_payload(self):
        with self.assertRaisesRegex(ValueError, "IDAT"):
            module.validate_png(png(zlib.compress(bytes((0, 255, 0, 0))) + b"junk"))


if __name__ == "__main__":
    unittest.main()
