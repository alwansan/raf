"""Source contract for bounded Android physical-mouse epoch diagnostics.

No Android device or Unity runtime is emulated here. This test protects
generation attribution and the non-invasive nature of the logging change.
"""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"


class MouseEpochTelemetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_request_generation_assigned_before_logging(self):
        block = self.source.split("private void RequestCapture()", 1)[1].split(
            "private static void ReportReleaseOutcome", 1
        )[0]
        self.assertLess(block.index("currentEpoch = ++epoch;"), block.index(
            '"physical_mouse_capture_requested"'
        ))
        self.assertIn('"epoch=" + currentEpoch', block)
        self.assertRegex(block, r'"physical_mouse_capture_retry",[\s\S]*?"epoch=" \+ currentEpoch')
        self.assertIn('nativeAccepted=unknown', block)
        self.assertIn('(attempt & (attempt - 1)) == 0', block)

    def test_relative_marker_uses_callback_epoch_not_latest_request(self):
        capture = self.source.split("private bool RecordCapturedMotion(", 1)[1].split(
            "public static CursorLockMode", 1
        )[0]
        self.assertIn("Volatile.Write(ref lastMotionEpoch, listenerEpoch);", capture)
        marker = self.source.split('"physical_mouse_relative"', 1)[1].split(");", 1)[0]
        self.assertIn("Volatile.Read(ref lastMotionEpoch)", marker)
        self.assertNotIn("Volatile.Read(ref epoch)", marker)

    def test_diagnostics_do_not_change_input_fallback(self):
        axis = self.source.split("private static float Axis(", 1)[1].split(
            "private void OnEnable()", 1
        )[0]
        self.assertIn("return raw ? Input.GetAxisRaw(axis) : Input.GetAxis(axis);", axis)
        self.assertIn("if (current.requested && current.nativeCaptured && current.nativeHasMotion)", axis)


if __name__ == "__main__":
    unittest.main()
