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

    def test_coverage_and_metadata_guard(self):
        items = [row(False) for _ in range(30)] + [row() for _ in range(76)]
        result = classify({"pairs": items})
        self.assertEqual(result["metadata_coverage"],
                         {"format": 106, "source_srgb": 0, "importer_srgb": 106})
        with self.assertRaisesRegex(ValueError, "missing per-pair metadata"):
            classify({"pairs": items}, require_metadata=True)
        for item in items:
            item["source_srgb"] = False
        self.assertEqual(classify({"pairs": items}, require_metadata=True)
                         ["metadata_coverage"]["source_srgb"], 106)

    def test_drift_only_metadata_guard(self):
        items = [row(False) for _ in range(30)] + [row() for _ in range(76)]
        for item in items[30:]:
            item["source_srgb"] = True
        result = classify({"pairs": items}, require_metadata=True)
        self.assertEqual(result["metadata_coverage"]["source_srgb"], 76)
        self.assertEqual(result["rgb_drift_metadata_coverage"]["source_srgb"], 0)
        with self.assertRaisesRegex(ValueError, "RGB-drift pairs"):
            classify({"pairs": items}, require_drift_metadata=True)
        for item in items[:30]:
            item["source_srgb"] = False
        self.assertEqual(classify({"pairs": items}, require_drift_metadata=True)
                         ["rgb_drift_metadata_coverage"]["source_srgb"], 30)

    def test_partial_drift_metadata_rejected(self):
        items = [row(False) for _ in range(30)] + [row() for _ in range(76)]
        for item in items:
            item["source_srgb"] = False
        items[0]["source_srgb"] = None
        with self.assertRaisesRegex(ValueError, "RGB-drift pairs"):
            classify({"pairs": items}, require_drift_metadata=True)

    def test_drift_format_missing_even_when_exact_complete(self):
        items = [row(False) for _ in range(30)] + [row() for _ in range(76)]
        for item in items:
            item["source_srgb"] = False
        items[0]["format"] = None
        self.assertEqual(classify({"pairs": items}, require_metadata=True)
                         ["metadata_coverage"]["format"], 105)
        with self.assertRaisesRegex(ValueError, "RGB-drift pairs"):
            classify({"pairs": items}, require_drift_metadata=True)

    def test_unknown_format_sentinel_cannot_bypass_drift_guard(self):
        items = [row(False) for _ in range(30)] + [row() for _ in range(76)]
        for item in items:
            item["source_srgb"] = False
        for sentinel in ("UNKNOWN", "unknown", "Unknown"):
            items[0]["format"] = sentinel
            result = classify({"pairs": items})
            self.assertEqual(result["rgb_drift_metadata_coverage"]["format"], 29)
            self.assertEqual(result["strata"]["format"]["UNKNOWN"]["rgb_drift"], 1)
            with self.assertRaisesRegex(ValueError, "RGB-drift pairs"):
                classify({"pairs": items}, require_drift_metadata=True)

    def test_rejects_nonboolean_srgb_metadata(self):
        item = row(False)
        for key in ("source_srgb", "importer_srgb"):
            for invalid in ("false", 0, 1, [], {}):
                candidate = dict(item)
                candidate[key] = invalid
                with self.subTest(key=key, invalid=repr(invalid)):
                    with self.assertRaisesRegex(ValueError, "invalid srgb flag"):
                        classify({"pairs": [candidate]}, strict_baseline=False)

    def test_rejects_unverified_alpha_and_dimensions(self):
        for key in ("alpha_equal", "dimensions_ok"):
            candidate = row(False)
            candidate[key] = False
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "unverified identity/dimensions/alpha parity"):
                    classify({"pairs": [candidate]}, strict_baseline=False)

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
