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

    def test_padded_unknown_format_cannot_bypass_drift_guard(self):
        items = [row(False) for _ in range(30)] + [row() for _ in range(76)]
        for item in items:
            item["source_srgb"] = False
        for sentinel in (" UNKNOWN ", " unknown ", "\tUnknown\n"):
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

    def test_joint_strata_partition_and_unknown(self):
        items = [row(False) for _ in range(30)] + [row() for _ in range(76)]
        items[0]["format"] = "BC7"
        items[0]["source_srgb"] = True
        result = classify({"pairs": items})
        self.assertEqual(sum(x["exact"] for x in result["joint_strata"]), 76)
        self.assertEqual(sum(x["rgb_drift"] for x in result["joint_strata"]), 30)
        self.assertEqual(len(result["joint_strata"]), 2)
        self.assertIn({"format": "BC7", "source_srgb": "true",
                       "importer_srgb": "true", "exact": 0, "rgb_drift": 1},
                      result["joint_strata"])
        self.assertIn({"format": "DXT5", "source_srgb": "UNKNOWN",
                       "importer_srgb": "true", "exact": 76, "rgb_drift": 29},
                      result["joint_strata"])

    def test_wrong_cohort_precedes_metadata_diagnosis(self):
        # One unpaired RGB-drift sample must fail provenance first, even if
        # source_srgb is absent and a strict metadata gate was requested.
        items = [row(False) for _ in range(29)] + [row() for _ in range(76)]
        with self.assertRaisesRegex(ValueError, "baseline count mismatch"):
            classify({"pairs": items}, require_drift_metadata=True,
                     require_metadata=True)
        # Exploratory cohorts remain permitted only with the explicit
        # non-baseline API flag; the metadata error then remains meaningful.
        with self.assertRaisesRegex(ValueError, "RGB-drift pairs"):
            classify({"pairs": items}, strict_baseline=False,
                     require_drift_metadata=True)

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
