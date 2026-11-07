#!/usr/bin/env python3
"""Regression for explicit scene lifecycle boundaries in T5 interval cohorts."""
import unittest
from t5_unity_interval_epoch import analyze_rows


def sample(fps, scene="Raft"):
    return {
        "area": "performance", "operation": "sample",
        "detail": (
            f"scene={scene};refresh_hz=120;frame_samples=60;fps={fps};"
            "frame_p50_ms=30;frame_p95_ms=45;width=2400;height=1080"
        ),
    }


class SceneEpochBoundaryTest(unittest.TestCase):
    def test_return_to_same_scene_is_new_epoch(self):
        rows = [sample(24), {"area": "scene", "operation": "loaded", "detail": "scene=MainMenu"},
                {"area": "scene", "operation": "loaded", "detail": "scene=Raft"}, sample(12)]
        result = analyze_rows(rows)
        self.assertEqual(result["performance_intervals"], 2)
        self.assertEqual(len(result["epochs"]), 2)
        self.assertEqual([x["median_interval_fps"] for x in result["epochs"]], [24, 12])

    def test_non_scene_records_do_not_split(self):
        rows = [sample(24), {"area": "other", "operation": "sample"}, sample(12)]
        result = analyze_rows(rows)
        self.assertEqual(len(result["epochs"]), 1)
        self.assertEqual(result["epochs"][0]["median_interval_fps"], 18)

    def test_scene_unload_also_splits(self):
        rows = [sample(24), {"area": "scene", "operation": "unloaded"}, sample(12)]
        self.assertEqual(len(analyze_rows(rows)["epochs"]), 2)


if __name__ == "__main__":
    unittest.main()
