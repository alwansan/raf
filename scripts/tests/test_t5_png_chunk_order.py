"""PNG chunk-order regression fixtures; synthetic data, no game assets."""
import struct
import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from t5_verify_png_bytes import validate_png


def chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))


def make_png(split=False, ancillary=False):
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    compressed = zlib.compress(b"\x00\x11\x22\x33")
    middle = chunk(b"tEXt", b"key\x00value") if ancillary else b""
    if split:
        payload = chunk(b"IDAT", compressed[:3]) + middle + chunk(b"IDAT", compressed[3:])
    else:
        payload = chunk(b"IDAT", compressed) + middle
    return signature + ihdr + payload + chunk(b"IEND", b"")


class ChunkOrderTests(unittest.TestCase):
    def test_single_idat(self):
        self.assertEqual(validate_png(make_png()), (1, 1))

    def test_ancillary_after_complete_idat(self):
        self.assertEqual(validate_png(make_png(ancillary=True)), (1, 1))

    def test_split_contiguous_idat(self):
        self.assertEqual(validate_png(make_png(split=True)), (1, 1))

    def test_noncontiguous_idat_rejected(self):
        with self.assertRaisesRegex(ValueError, "noncontiguous PNG IDAT"):
            validate_png(make_png(split=True, ancillary=True))


if __name__ == "__main__":
    unittest.main()
