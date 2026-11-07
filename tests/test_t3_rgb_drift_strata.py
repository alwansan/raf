import unittest
from t3_rgb_drift_strata import classify


def row(rgb=True):
    return dict(identity_ok=True, dimensions_ok=True, rgb_equal=rgb,
                alpha_equal=True, format="DXT5", source_srgb=None, importer_srgb=True)


class TestStrata(unittest.TestCase):
    def test_baseline_and_unknown(self):
        result = classify({"pairs": [row(False) for _ in range(30)] + [row() for _ in range(76)]})
        self.assertEqual((result["exact"], result["rgb_drift"]), (76, 30))
        self.assertEqual(result["strata"]["source_srgb"]["UNKNOWN"]["rgb_drift"], 30)

    def test_wrong_baseline(self):
        with self.assertRaises(ValueError):
            classify({"pairs": [row()]})

    def test_invalid_identity(self):
        item = row()
        item["identity_ok"] = False
        with self.assertRaises(ValueError):
            classify({"pairs": [item]}, strict_baseline=False)

    def test_rejects_raw_path_in_category(self):
        item = row()
        item["format"] = "/private/texture.png"
        with self.assertRaises(ValueError):
            classify({"pairs": [item]}, strict_baseline=False)

    def test_rejects_missing_flags(self):
        item = row()
        del item["alpha_equal"]
        with self.assertRaises(ValueError):
            classify({"pairs": [item]}, strict_baseline=False)


if __name__ == "__main__":
    unittest.main()
