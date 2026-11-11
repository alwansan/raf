#!/usr/bin/env python3
"""T4 captured-action route contract: source-only, never device acceptance."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs")


class CapturedActionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.android = cls.source.split("#elif UNITY_5_3_OR_NEWER", 1)[0]

    def test_button_scroll_callback_records_without_consuming(self):
        callback = self.android.split("public bool onCapturedPointer(", 1)[1].split(
            "private bool RecordCapturedMotion(", 1)[0]
        self.assertIn('motionEvent.Call<int>("getActionMasked")', callback)
        self.assertIn("PhysicalMouseActionEvidence.IsAction(action)", callback)
        self.assertIn('motionEvent.Call<int>("getActionButton")', callback)
        self.assertIn('motionEvent.Call<int>("getButtonState")', callback)
        self.assertIn("PhysicalMouseActionEvidence.VScroll", callback)
        self.assertIn("PhysicalMouseActionEvidence.HScroll", callback)
        self.assertIn('motionEvent.Call<long>("getEventTime")', callback)
        self.assertIn('motionEvent.Call<int>("getDeviceId")', callback)
        self.assertIn("owner.RecordCapturedAction(", callback)
        nonmove = callback.split("if (action != PhysicalMouseMotionSource.ActionMove)", 1)[1]
        self.assertRegex(nonmove, r"owner\\.RecordCapturedAction\\([\\s\\S]*?return false;")

    def test_callback_buffer_and_legacy_readers_share_one_snapshot(self):
        action = self.android.split("private void RecordCapturedAction(", 1)[1].split(
            "private void LogCapturedActions(", 1)[0]
        self.assertIn("lock(captureGate)", action)
        self.assertIn("buttonWheel.Record(", action)
        self.assertIn("nativeCaptured = true;", action)
        snapshot = self.android.split("private static bool TryCapturedFrame(", 1)[1].split(
            "private static void RecordLegacyReader(", 1)[0]
        self.assertIn("current.buttonWheel.Sample(Time.frameCount)", snapshot)
        self.assertIn("!current.requested || !current.nativeCaptured", snapshot)
        for method, accessor in (("GetMouseButton", "Held(index)"),
                                 ("GetMouseButtonDown", "Down(index)"),
                                 ("GetMouseButtonUp", "Up(index)")):
            body = self.android.split("public static bool " + method + "(", 1)[1].split(
                "\\n        }", 1)[0]
            self.assertIn("TryCapturedFrame(out frame)", body)
            self.assertIn("frame." + accessor, body)
        self.assertIn("frame.Horizontal, frame.Vertical", self.android)
        self.assertIn("capturedFrame.Vertical", self.android)

    def test_capture_loss_clears_stale_buttons(self):
        lost = self.android.split("private void ObserveNativeCapture(", 1)[1].split(
            "private static int ViewIdentity(", 1)[0]
        self.assertIn("if (!captured)", lost)
        self.assertIn("buttonWheel.Reset();", lost)
        self.assertIn("nativeHasMotion = false;", lost)
        self.assertIn("deltas.Reset();", lost)


if __name__ == "__main__":
    unittest.main()
