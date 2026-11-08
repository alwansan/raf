"""T4 assists T3: PNG decoder/black screenshot proof synthetic tests."""
import binascii
import hashlib
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from scripts.t4_support_t3_visual_png_audit import (
    PNG_MAGIC, color_stats, png_rgba_rows, verify_original_blob
)


def chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", binascii.crc32(kind + payload) & 0xffffffff))


def make_png(width, height, pixels, *, kind=6, filter_mode=0):
    depth = {6: 4, 2: 3}[kind]
    scan = bytearray()
    last = bytes(width * depth)
    for row in range(height):
        raw = bytearray()
        for p in pixels[row]:
            raw.extend(p[:depth])
        if filter_mode == 1:
            filtered = bytes((raw[i] - (raw[i - depth] if i >= depth else 0)) & 255
                             for i in range(len(raw)))
        elif filter_mode == 2:
            filtered = bytes((b - last[i]) & 255 for i, b in enumerate(raw))
        else:
            filtered = bytes(raw)
        scan.extend([filter_mode])
        scan.extend(filtered)
        last = raw
    head = struct.pack(">IIBBBBB", width, height, 8, kind, 0, 0, 0)
    return (PNG_MAGIC + chunk(b"IHDR", head) +
            chunk(b"IDAT", zlib.compress(bytes(scan))) + chunk(b"IEND", b""))


class ClPngAuditTests(unittest.TestCase):
    def test_three_color_stripes_visible_in_center(self):
        colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)]
        pixels = [[colors[min(2, x * 3 // 30)] for x in range(30)]
                  for _ in range(20)]
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "frame.png"
            file.write_bytes(make_png(30, 20, pixels))
            report = color_stats(file)
            self.assertGreater(report["center"]["red_pct"], 10)
            self.assertGreater(report["center"]["green_pct"], 10)
            self.assertGreater(report["center"]["blue_pct"], 10)
            self.assertLess(report["center"]["nearly_black_pct"], 1)
            self.assertEqual(report["width"], 30)
            self.assertEqual(report["height"], 20)

    def test_black_image_must_not_look_like_rgb_stripes(self):
        pixels = [[(0, 0, 0, 255)] * 20 for _ in range(12)]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "black.png"
            f.write_bytes(make_png(20, 12, pixels))
            r = color_stats(f)
            self.assertEqual(r["center"]["nearly_black_pct"], 100)
            self.assertEqual(r["center"]["red_pct"], 0)
            self.assertEqual(r["center"]["green_pct"], 0)
            self.assertEqual(r["center"]["blue_pct"], 0)

    def test_png_byte_filters_sub_and_up_rgba(self):
        rgba = [[((x * 21) % 256, (y * 9) % 256, 170, 255)
                 for x in range(9)] for y in range(6)]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "frame.png"
            for fmode in (0, 1, 2):
                p.write_bytes(make_png(9, 6, rgba, filter_mode=fmode))
                decoded = list(png_rgba_rows(p))
                self.assertEqual(decoded[0][3], rgba[0])
                self.assertEqual(decoded[-1][3], rgba[-1])

    def test_rgb_no_alpha(self):
        rgb = [[(255, 0, 0)] * 8 for _ in range(8)]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "rgb.png"
            p.write_bytes(make_png(8, 8, rgb, kind=2))
            rows = list(png_rgba_rows(p))
            self.assertEqual(rows[2][3][3], (255, 0, 0, 255))

    def test_truncated_crc_or_inflate_refused(self):
        pixels = [[(200, 0, 0, 255)] * 5 for _ in range(5)]
        image = make_png(5, 5, pixels)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.png"
            for data in (image[:-2], image[:-20] + image[-12:],
                         image[:34] + b"bad" + image[37:]):
                p.write_bytes(data)
                with self.assertRaises(ValueError):
                    list(png_rgba_rows(p))

    def test_symlink_refused(self):
        pixels = [[(255, 255, 255, 255)] * 3 for _ in range(4)]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "good.png"
            p.write_bytes(make_png(3, 4, pixels))
            link = Path(d) / "alias.png"
            try:
                link.symlink_to(p)
            except OSError:
                return
            with self.assertRaises(ValueError):
                list(png_rgba_rows(link))

    def test_original_blob_sha_pin(self):
        pixels = [[(0, 0, 255, 255)] * 2 for _ in range(2)]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sha.png"
            p.write_bytes(make_png(2, 2, pixels))
            b = p.read_bytes()
            sha = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
            verify_original_blob(p, sha)
            with self.assertRaises(ValueError):
                verify_original_blob(p, "0" * 40)

    def test_no_original_game_or_user_data_output(self):
        pixels = [[(40, 40, 40, 255)] * 7 for _ in range(4)]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "frame.png"
            p.write_bytes(make_png(7, 4, pixels))
            values = color_stats(p)
            self.assertNotIn("pixels", values)
            self.assertIn("center", values)


if __name__ == "__main__":
    unittest.main()
