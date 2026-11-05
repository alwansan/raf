import unittest
from PIL import Image
from scripts.t3_decoded_texture_pixel_parity import compare_pair, aggregate


class TestDecodedTextureParity(unittest.TestCase):
    def setUp(self):
        self.a = Image.new("RGBA", (3, 2))
        self.a.putdata([(10, 20, 30, 255), (40, 50, 60, 0), (70, 80, 90, 255),
                        (100, 110, 120, 255), (130, 140, 150, 255), (160, 170, 180, 255)])

    def check(self, b, expected, **kw):
        self.assertEqual(compare_pair(self.a, b, original_id="verified-guid",
                                      exported_id=kw.pop("exported_id", "verified-guid"),
                                      authenticated=kw.pop("authenticated", True)), expected)

    def test_exact(self):
        self.check(self.a.copy(), "EXACT")

    def test_vertical(self):
        self.check(self.a.transpose(Image.Transpose.FLIP_TOP_BOTTOM), "VERTICAL_FLIP")

    def test_horizontal(self):
        self.check(self.a.transpose(Image.Transpose.FLIP_LEFT_RIGHT), "HORIZONTAL_FLIP")

    def test_both(self):
        self.check(self.a.transpose(Image.Transpose.ROTATE_180), "BOTH_AXES_FLIP")

    def test_alpha(self):
        b = self.a.copy()
        b.putpixel((0, 0), (10, 20, 30, 2))
        self.check(b, "ALPHA_ONLY_DRIFT")

    def test_rgb(self):
        b = self.a.copy()
        b.putpixel((0, 0), (11, 20, 30, 255))
        self.check(b, "RGB_DRIFT")

    def test_transparent_rgb_must_not_be_ignored(self):
        b = self.a.copy()
        b.putpixel((1, 0), (41, 50, 60, 0))
        self.check(b, "RGB_DRIFT")

    def test_dimension(self):
        self.check(Image.new("RGBA", (2, 3)), "DIMENSION_MISMATCH")

    def test_mode(self):
        self.check(self.a.convert("RGB"), "UNSUPPORTED_MODE")

    def test_identity(self):
        self.check(self.a, "UNVERIFIED_IDENTITY", exported_id="other")
        self.check(self.a, "UNVERIFIED_IDENTITY", authenticated=False)

    def test_aggregate_fail_closed(self):
        self.assertTrue(aggregate(["EXACT"] * 2, expected=2)["decoded_pixel_exact"])
        self.assertFalse(aggregate(["EXACT", "RGB_DRIFT"], expected=2)["decoded_pixel_exact"])
        with self.assertRaises(ValueError):
            aggregate(["EXACT"], expected=2)
        with self.assertRaises(ValueError):
            aggregate(["SECRET"], expected=1)


if __name__ == "__main__":
    unittest.main()
