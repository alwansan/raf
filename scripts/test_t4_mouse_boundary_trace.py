#!/usr/bin/env python3
"""Source-only regression checks for INPUT-005 boundary trace correlation.

Run: python3 -m unittest discover -s scripts -p 'test_t4_mouse_boundary_trace.py'
No Android device or Raft runtime is simulated.
"""
import unittest

from t4_mouse_boundary_trace import analyze, self_test


class MouseBoundaryTraceTests(unittest.TestCase):
    def test_embedded_self_test(self):
        self_test()

    def test_stage_order_and_cross_frame_are_not_device_proof(self):
        report = analyze([
            "T4_MOUSE_STAGE frame=100 stage=android button=left",
            "T4_MOUSE_STAGE frame=101 stage=unity button=left",
            "T4_MOUSE_STAGE frame=102 stage=raft button=left",
        ])
        self.assertEqual(report["buttons"]["left"]["observed_frames"], 3)
        self.assertEqual(report["buttons"]["left"]["stage_frames"],
                         {"android": 1, "unity": 1, "raft": 1})
        self.assertFalse(report["device_success_proven"])
        self.assertFalse(report["buttons"]["left"]["device_success_proven"])

    def test_duplicate_markers_in_same_frame_not_double_counted(self):
        marker = "T4_MOUSE_STAGE frame=3 stage=android button=right"
        report = analyze([marker, marker])
        self.assertEqual(report["buttons"]["right"]["observed_frames"], 1)
        self.assertEqual(report["buttons"]["right"]["stage_frames"]["android"], 1)

    def test_all_four_controls_and_malformed_marker(self):
        lines = [
            "T4_MOUSE_STAGE frame=1 stage=android button=left",
            "T4_MOUSE_STAGE frame=2 stage=android button=right",
            "T4_MOUSE_STAGE frame=3 stage=android button=middle",
            "T4_MOUSE_STAGE frame=4 stage=android button=wheel",
            "T4_MOUSE_STAGE frame=bad stage=android button=left",
        ]
        report = analyze(lines)
        for button in ("left", "right", "middle", "wheel"):
            self.assertEqual(report["buttons"][button]["stage_frames"]["android"], 1)
        self.assertEqual(report["malformed_markers"], 1)

    def test_identical_frame_numbers_across_sessions_do_not_merge(self):\n        report = analyze([\n            "T4_MOUSE_STAGE session=A frame=8 stage=android button=left",\n            "T4_MOUSE_STAGE session=B frame=8 stage=unity button=left",\n            "T4_MOUSE_STAGE session=A frame=8 stage=android button=left",\n        ])\n        self.assertEqual(report["frames_with_markers"], 2)\n        self.assertEqual(report["buttons"]["left"]["observed_frames"], 2)\n        self.assertEqual(report["buttons"]["left"]["uncorrelated_same_frame"], {\n            "android_without_unity_same_frame": 1,\n            "unity_without_raft_same_frame": 1,\n        })\n        self.assertFalse(report["device_success_proven"])\n\n    def test_legacy_markers_remain_supported(self):\n        report = analyze(["T4_MOUSE_STAGE frame=8 stage=android button=middle"])\n        self.assertEqual(report["frames_with_markers"], 1)\n        self.assertEqual(report["buttons"]["middle"]["stage_frames"]["android"], 1)\n\n    def test_no_markers_is_unknown_not_success(self):
        report = analyze(["ordinary Unity log", "physical mouse present"])
        self.assertEqual(report["frames_with_markers"], 0)
        self.assertFalse(report["device_success_proven"])
        self.assertEqual(report["malformed_markers"], 0)


if __name__ == "__main__":
    unittest.main()
