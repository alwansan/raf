"""Synthetic time-alignment guards for Unity diagnostics vs SurfaceFlinger gaps."""
from pathlib import Path
import json
import tempfile
import unittest
from scripts.t5_cl_unity_surface_bridge import (
    analyze, detail_fields, load_unity, stale_windows, valid_unity, millis,
)


def unity_row(sequence, utc="2026-11-05T20:02:10.0000000Z", *,
              fps=25, frames=125, scene="MainScene", overflow=0,
              orientation="Landscape", p95=60.5):
    d = {
        "interval_frames": frames, "fps": fps,
        "frame_samples": frames, "sample_capacity": 2048,
        "frame_sample_overflow": overflow, "frame_p95_ms": p95,
        "width": 2400, "height": 1080,
        "orientation": orientation, "scene": scene,
    }
    return {"utc": utc, "session": "synthetic", "sequence": sequence,
            "area": "performance", "operation": "sample",
            "detail": "; ".join(k+"="+str(v) for k,v in d.items())}


def sf_row(sample, utc_ms, stale=True):
    return {"sample": sample, "timestamp_unix_ms": utc_ms,
            "frame_telemetry_stale": stale, "state": "game_running"}


class BridgeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "unity.jsonl"

    def read(self, rows):
        self.path.write_text("".join(json.dumps(x)+"\n" for x in rows))
        return load_unity(self.path)

    def test_utc_alignment_with_stale_only(self):
        base = millis("2026-11-05T20:02:00.0000000Z")
        sf = [sf_row(1,base,True),sf_row(2,base+12000,True),
              sf_row(3,base+24000,True),sf_row(4,base+36000,False)]
        lines = self.read([unity_row(1,"2026-11-05T20:02:10.0000000Z"),
                           unity_row(2,"2026-11-05T20:02:40.0000000Z")])
        result = analyze(lines,sf,"unit")
        self.assertEqual(result["qualified_unity_intervals_during_sf_stale"],1)
        self.assertEqual(result["unity_during_sf_stale_by_scene"]["MainScene"]["intervals"],1)
        self.assertTrue(result["sf_stale_does_not_prove_game_freeze"])

    def test_multiple_stale_windows_do_not_bridge_nonstale_gap(self):
        sf = [sf_row(1,1000),sf_row(2,4000),sf_row(3,7000,False),
              sf_row(4,10000),sf_row(5,13000)]
        self.assertEqual(stale_windows(sf),[(1000,4000,2),(10000,13000,2)])

    def test_long_sample_gap_splits_stale_interval(self):
        self.assertEqual(stale_windows([sf_row(1,1000),sf_row(2,18000)]),
                         [(1000,1000,1),(18000,18000,1)])

    def test_startup_single_frame_excluded(self):
        self.assertFalse(valid_unity({"frames":1,"samples":1,"overflow":0,"fps":0.08,
                                     "p95_ms":12000,"width":2400,"height":1080,"orientation":"Landscape"}))

    def test_skips_orientation_change_without_overwriting_device_mode(self):
        self.assertFalse(valid_unity({"frames":40,"samples":40,"overflow":0,"fps":25,
                                     "p95_ms":55,"width":2400,"height":1080,"orientation":"Portrait"}))

    def test_no_frame_sample_overflow_accepted(self):
        self.assertFalse(valid_unity({"frames":40,"samples":40,"overflow":1,"fps":25,
                                     "p95_ms":55,"width":2400,"height":1080,"orientation":"Landscape"}))

    def test_nonfinite_sample_rejected_as_bad_source(self):
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            self.read([unity_row(1,fps=float("nan"))])

    def test_duplicate_unity_detail_key_refused(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            detail_fields("fps=23; fps=24")

    def test_malformed_detail_refused(self):
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            detail_fields("fps=23; notkeyvalue")

    def test_wrong_timezone_refused(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self.read([unity_row(1,utc="2026-11-05T20:02:10")])

    def test_nonmonotone_unity_record_refused(self):
        with self.assertRaisesRegex(ValueError, "Non-monotone"):
            self.read([unity_row(1),unity_row(1,utc="2026-11-05T20:02:11.0000000Z")])

    def test_wrong_ordered_unity_timestamps_refused(self):
        with self.assertRaisesRegex(ValueError, "Non-monotone"):
            self.read([unity_row(1,utc="2026-11-05T20:02:11.0000000Z"),
                       unity_row(2,utc="2026-11-05T20:02:10.0000000Z")])

    def test_scene_aggregate_not_frame_weighted_p95(self):
        u = self.read([unity_row(1,utc="2026-11-05T20:02:05.0000000Z",fps=20,p95=50),
                       unity_row(2,utc="2026-11-05T20:02:10.0000000Z",fps=30,p95=100)])
        start = millis("2026-11-05T20:02:00.0000000Z")
        report = analyze(u,[sf_row(1,start),sf_row(2,start+15000)],"test")
        stats = report["unity_during_sf_stale_by_scene"]["MainScene"]
        self.assertEqual(stats["median_fps"],25.0)
        self.assertEqual(stats["median_of_interval_frame_p95_ms"],75.0)
        self.assertTrue(report["unity_logged_frames_do_not_prove_presented_frames"])

    def test_oversized_unity_file_refused(self):
        self.path.write_bytes(b"x"*2_000_001)
        with self.assertRaisesRegex(ValueError,"oversized"):
            load_unity(self.path)

    def test_unity_symlink_refused(self):
        real=self.path.parent/"real.jsonl"
        real.write_text(json.dumps(unity_row(1))+"\n")
        try:self.path.symlink_to(real)
        except (OSError, NotImplementedError):self.skipTest("no symlink")
        with self.assertRaisesRegex(ValueError,"linked"):
            load_unity(self.path)


    @staticmethod
    def with_scene_provenance(record, *, start="MainScene", end="MainScene",
                              active_changes=0, content_events=0,
                              active_stable=True, content_stable=True):
        record["detail"] += ("; frame_window_start_scene=" + start
                             + "; frame_window_end_scene=" + end
                             + "; frame_window_active_scene_changes=" + str(active_changes)
                             + "; frame_window_content_scene_events=" + str(content_events)
                             + "; frame_window_active_scene_stable=" + str(active_stable)
                             + "; frame_window_content_stable=" + str(content_stable))
        return record

    def test_legacy_scene_samples_are_not_claimed_tagged_stable(self):
        a = self.read([unity_row(1)])
        assert a[0]["scene_window_provenance"] == "legacy_unlabeled"
        report = analyze(a, [], "old-APK")
        self.assertEqual(report["unity_qualified_scene_window_provenance"],
                         {"legacy_unlabeled":1,"tagged_stable_content":0,"tagged_mixed_loading":0})
        self.assertTrue(report["tagged_stable_scene_does_not_prove_same_world_or_camera"])

    def test_new_stable_scene_content_provenance(self):
        a = self.read([self.with_scene_provenance(unity_row(1))])
        self.assertEqual(a[0]["scene_window_provenance"], "tagged_stable_content")

    def test_menu_to_main_scene_crossing_is_labeled_mixed(self):
        a = self.read([self.with_scene_provenance(
            unity_row(1), start="MainMenuScene", end="MainScene",
            active_changes=1, content_events=2, active_stable=False,
            content_stable=False)])
        self.assertEqual(a[0]["scene_window_provenance"], "tagged_mixed_loading")
        self.assertEqual(analyze(a, [], "new-APK")[
            "unity_qualified_scene_window_provenance"]["tagged_stable_content"], 0)

    def test_additive_scene_load_marks_same_active_scene_non_stable(self):
        a = self.read([self.with_scene_provenance(
            unity_row(1), content_events=1, content_stable=False)])
        self.assertEqual(a[0]["scene_window_provenance"], "tagged_mixed_loading")

    def test_partial_telemetry_flags_fail_closed(self):
        row = unity_row(1)
        row["detail"] += "; frame_window_start_scene=MainScene"
        with self.assertRaisesRegex(ValueError, "Partial mixed-scene"):
            self.read([row])

    def test_contradictory_scene_stable_flags_fail_closed(self):
        row = self.with_scene_provenance(
            unity_row(1), start="MainMenuScene", end="MainScene",
            active_changes=1, active_stable=True, content_stable=True)
        with self.assertRaisesRegex(ValueError, "Contradictory"):
            self.read([row])

    def test_negative_scene_transition_counter_fail_closed(self):
        row = self.with_scene_provenance(unity_row(1), active_changes=-1)
        with self.assertRaisesRegex(ValueError, "Negative scene"):
            self.read([row])

    def test_end_scene_disagrees_with_existing_report_scene(self):
        row = self.with_scene_provenance(unity_row(1), end="OtherScene")
        with self.assertRaisesRegex(ValueError, "Invalid start/end"):
            self.read([row])


if __name__ == "__main__":
    unittest.main()
