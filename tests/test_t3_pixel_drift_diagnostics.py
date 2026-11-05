"""Synthetic negative controls for T3 authentic decoded pixel diagnostic."""
import unittest
from PIL import Image
from scripts.t3_pixel_drift_diagnostics import classify, aggregate, original_texture_categories

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

    def test_alpha_only_drift_not_mislabeled_rgb(self):
        a = Image.new("RGBA", (1, 1), (100, 101, 102, 255))
        b = Image.new("RGBA", (1, 1), (100, 101, 102, 250))
        r = classify(a, b)
        self.assertEqual(r["max_rgb_delta_bin"], "ALPHA_ONLY")
        self.assertEqual(r["alpha_delta"], "NONZERO")
        self.assertEqual(aggregate([r], expected=1)["diagnostics"]["max_rgb_delta_bin"], {"ALPHA_ONLY": 1})

    def test_exact_transparent_channels_remain_exact(self):
        a = Image.new("RGBA", (1, 1), (200, 201, 202, 0))
        r = classify(a, a.copy())
        self.assertEqual(r["max_rgb_delta_bin"], "EXACT")
        self.assertEqual(r["alpha_delta"], "NONE")

    def test_reject_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            classify(Image.new("RGBA", (1, 1)), Image.new("RGBA", (2, 2)))

    def test_aggregate_only_marginals(self):
        a = Image.new("RGBA", (1, 1), (1, 2, 3, 255))
        result = aggregate([classify(a, a)], expected=1)
        self.assertEqual(result["scope"], 1)
        self.assertNotIn("rows", result)
        self.assertFalse(result["device_validated"])

    def test_format_drift_summary_and_rare_pooling(self):
        a = Image.new("RGBA", (1, 1), (10, 20, 30, 255))
        b = Image.new("RGBA", (1, 1), (11, 20, 30, 255))
        exact = classify(a, a, texture_format="DXT1")
        drift = classify(a, b, texture_format="DXT1")
        rare = classify(a, b, texture_format="BC7")
        rows = [exact] * 5 + [drift] * 2 + [rare]
        result = aggregate(rows, expected=8)
        self.assertEqual(result["format_drift_summary"]["DXT1"],
                         {"EXACT": 5, "ALPHA_ONLY": 0, "RGB_DRIFT": 2})
        self.assertEqual(result["format_drift_summary"]["POOLED_RARE_FORMATS"]["RGB_DRIFT"], 1)
        self.assertNotIn("BC7", result["format_drift_summary"])
        self.assertEqual(sum(sum(v.values()) for v in result["format_drift_summary"].values()), 8)
        self.assertNotIn("rows", result)

    def test_typed_original_TextureFormat_and_Gamma_Linear_source(self):
        self.assertEqual(original_texture_categories({"m_TextureFormat":10,"m_ColorSpace":0}),("DXT1","gamma"))
        self.assertEqual(original_texture_categories({"m_TextureFormat":12,"m_ColorSpace":1}),("DXT5","linear"))
        self.assertEqual(original_texture_categories({"m_TextureFormat":25,"m_ColorSpace":0}),("BC7","gamma"))
        self.assertEqual(original_texture_categories({"m_TextureFormat":4,"m_ColorSpace":1}),("RGBA32","linear"))
        self.assertEqual(original_texture_categories({"m_TextureFormat":999,"m_ColorSpace":0}),("OTHER_OR_UNKNOWN","gamma"))

    def test_malformed_authentic_texture_metadata_fails_closed(self):
        samples=({},{"m_TextureFormat":"10","m_ColorSpace":0},{"m_TextureFormat":10,"m_ColorSpace":"gamma"},
                 {"m_TextureFormat":True,"m_ColorSpace":0},{"m_TextureFormat":10,"m_ColorSpace":2},
                 {"m_TextureFormat":-1,"m_ColorSpace":1})
        for sample in samples:
            with self.subTest(sample=sample):
                with self.assertRaises(ValueError):
                    original_texture_categories(sample)

    def test_original_gamma_linear_color_space_x_rgb_drift(self):
        a=Image.new("RGBA",(1,1),(20,30,40,255))
        b=Image.new("RGBA",(1,1),(255,30,40,0))
        gamma=classify(a,a,texture_format="DXT1",srgb="gamma")
        linear=classify(a,b,texture_format="DXT5",srgb="linear")
        report=aggregate([gamma]*6+[linear]*6,expected=12)
        self.assertEqual(report["schema_version"],3)
        self.assertEqual(report["color_space_drift_summary"]["GAMMA"]["EXACT"],6)
        self.assertEqual(report["color_space_drift_summary"]["LINEAR"]["RGB_DRIFT"],6)
        self.assertEqual(report["format_drift_summary"]["DXT5"]["RGB_DRIFT"],6)
        self.assertFalse(report["device_validated"])

    def test_rare_color_spaces_and_formats_pool_without_identity_leak(self):
        a=Image.new("RGBA",(1,1),(12,24,36,255))
        typical=classify(a,a,texture_format="DXT1",srgb="gamma")
        rare=classify(a,a,texture_format="OTHER_OR_UNKNOWN",srgb="linear")
        summary=aggregate([typical]*6+[rare],expected=7)
        self.assertIn("POOLED_RARE_FORMATS",summary["format_drift_summary"])
        self.assertIn("POOLED_RARE_COLORSPACES",summary["color_space_drift_summary"])
        self.assertNotIn("LINEAR",summary["color_space_drift_summary"])
        self.assertNotIn("rows",summary)

    def test_aggregate_fail_closed(self):
        with self.assertRaises(ValueError):
            aggregate([], expected=106)
        with self.assertRaises(ValueError):
            aggregate([{"format": "SECRET"}], expected=1)

if __name__ == "__main__":
    unittest.main()
