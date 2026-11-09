"""Regression tests for T5's offline PNG byte integrity gate (no Android/Unity)."""
import hashlib
import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "t5_verify_png_bytes.py"
spec = importlib.util.spec_from_file_location("t5_verify_png_bytes", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def chunk(kind, payload=b""):
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))


def png():
    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    scanline = b"\x00\xff\x00\x00\xff"
    return gate.SIGNATURE + chunk(b"IHDR", header) + chunk(
        b"IDAT", zlib.compress(scanline)) + chunk(b"IEND")


class PngIntegrityRegression(unittest.TestCase):
    def test_valid_png(self):
        self.assertEqual(gate.validate_png(png()), (1, 1))

    def test_signature_rejected(self):
        with self.assertRaisesRegex(ValueError, "signature"):
            gate.validate_png(b"X" + png()[1:])

    def test_crc_rejected(self):
        bad = bytearray(png())
        bad[29] ^= 1  # IHDR CRC byte
        with self.assertRaisesRegex(ValueError, "CRC"):
            gate.validate_png(bytes(bad))

    def test_truncated_chunk_rejected(self):
        with self.assertRaises(ValueError):
            gate.validate_png(png()[:-5])

    def test_trailing_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, "trailing"):
            gate.validate_png(png() + b"unexpected")

    def test_missing_idat_rejected(self):
        header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "IEND"):
            gate.validate_png(gate.SIGNATURE + chunk(b"IHDR", header) + chunk(b"IEND"))

    def test_duplicate_ihdr_rejected(self):
        raw = png()
        header_chunk = raw[8:33]
        with self.assertRaisesRegex(ValueError, "duplicate IHDR"):
            gate.validate_png(raw[:33] + header_chunk + raw[33:])

    def test_summary_matches_six_local_files(self):
        raw = png()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            results = []
            for i in range(1, 7):
                case = f"T3-{i:02d}"
                (folder / f"{case}-proof.png").write_bytes(raw)
                results.append({"case_id": case, "result": {"observed":
                    f"png_sha256={hashlib.sha256(raw).hexdigest()} png_bytes={len(raw)}"}})
            self.assertEqual(gate.verify({"results": results}, folder), [])
            (folder / "T3-03-proof.png").write_bytes(raw + b"bad")
            self.assertTrue(any("T3-03" in e for e in gate.verify({"results": results}, folder)))

    def test_duplicate_summary_case_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            records = [{"case_id": "T3-01", "result": {"observed": ""}}] * 2
            errors = gate.verify({"results": records}, Path(temp))
            self.assertTrue(any("T3-01: expected exactly one" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
