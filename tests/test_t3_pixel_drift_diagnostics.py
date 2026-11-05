"""Synthetic negative controls for T3 authentic decoded pixel diagnostic."""
import unittest
from PIL import Image
from scripts.t3_pixel_drift_diagnostics import classify, aggregate

class PixelDriftDiagnosticTests(unittest.TestCase):
    def test_exact_opaque(self):
        a = Image.new("RGBA", (2, 2), (20, 30, 40, 255))
        r = classify(a, a.copy(), texture_format="DXT1", srgb="true")
        self.assertEqual(r["max_rgb_delta_bin"], "EXACT")
        self.assertEqual(r["format"], "DXT1")
        self.assertEqual(r["color_space"], "SRGB")
        self.assertEqual(r["alpha_occupancy"], "OPAQUE")

    def test_rgb_drift_under_zero_alpha_not_hidden(self):
        a = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        b = Image.new("RGBA", (1, 1), (255, 0, 0, 0))
        r = classify(a, b)
        self.assertEqual(r["max_rgb_delta_bin"], "RGB_65_255")
        self.assertEqual(r["alpha_occupancy"], "TRANSPARENT")
        self.assertEqual(r["alpha_delta"], "NONE")

    def test_small_drift_bin(self):
        a = Image.new("RGBA", (1, 1), (100, 100, 100, 255))
        b = Image.new("RGBA", (1, 1), (101, 103, 105, 254))
        r = classify(a, b)
        self.assertEqual(r["max_rgb_delta_bin"], "RGB_5_16")
        self.assertEqual(r["alpha_delta"], "NONZERO")

    def test_reject_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            classify(Image.new("RGBA", (1, 1)), Image.new("RGBA", (2, 2)))

    def test_aggregate_only_marginals(self):
        a = Image.new("RGBA", (1, 1), (1, 2, 3, 255))
        result = aggregate([classify(a, a)], expected=1)
        self.assertEqual(result["scope"], 1)
        self.assertNotIn("rows", result)
        self.assertFalse(result["device_validated"])

    def test_aggregate_fail_closed(self):
        with self.assertRaises(ValueError):
            aggregate([], expected=106)
        with self.assertRaises(ValueError):
            aggregate([{"format": "SECRET"}], expected=1)

if __name__ == "__main__":
    unittest.main()
