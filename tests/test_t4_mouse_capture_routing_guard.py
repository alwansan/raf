#!/usr/bin/env python3
"""Source-only guard for the physical Android mouse routing contract.

Does not assert Android device behavior or substitute for Unity compilation.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"


class PhysicalMouseRoutingGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.android = cls.source.split("#elif UNITY_5_3_OR_NEWER", 1)[0]

    def test_nonmove_callback_does_not_consume_native_buttons(self):
        callback = self.android.split("public bool onCapturedPointer(", 1)[1].split(
            "private bool RecordCapturedMotion(", 1
        )[0]
        self.assertRegex(callback, r"if\s*\(action\s*!=\s*PhysicalMouseMotionSource\.ActionMove\)")
        self.assertIn("owner.RecordCapturedAction(", callback)
        self.assertRegex(callback, r"owner\.RecordCapturedAction\([^;]+;\s*}\s*return false;",)
        self.assertIn("motionEvent.Call<int>(\"getActionButton\")", callback)
        self.assertIn("motionEvent.Call<int>(\"getButtonState\")", callback)

    def test_only_authored_locked_physical_mouse_can_request(self):
        self.assertIn('mouse.name != VirtualTouchMouse', self.android)
        self.assertRegex(self.android, r"shouldCapture\s*=\s*!paused\s*&&\s*focused\s*&&\s*authoredLocked\s*&&\s*physicalPresent")
        self.assertIn("if (!shouldCapture)", self.android)
        self.assertIn("ReleaseCapture();", self.android)

    def test_native_first_all_three_buttons_and_wheel(self):
        for method, native in (
            ("GetMouseButton", "Input.GetMouseButton(index)"),
            ("GetMouseButtonDown", "Input.GetMouseButtonDown(index)"),
            ("GetMouseButtonUp", "Input.GetMouseButtonUp(index)"),
        ):
            part = self.android.split("public static bool " + method + "(", 1)[1].split("\n        }", 1)[0]
            self.assertIn(native, part)
            self.assertIn("if (legacy)", part)
            self.assertIn("TryCapturedFrame(out frame)", part)
        wheel = self.android.split("public static Vector2 GetMouseScrollDelta(", 1)[1].split("\n        }", 1)[0]
        self.assertIn("Input.mouseScrollDelta", wheel)
        self.assertIn("TryCapturedFrame(out frame)", wheel)
        self.assertIn('axis == "Mouse ScrollWheel"', self.android)

    def test_focus_pause_disable_release_and_keyboard_untouched(self):
        for hook in ("OnApplicationPause(bool value)", "OnApplicationFocus(bool value)", "OnDisable()"):
            body = self.android.split("private void " + hook, 1)[1].split("\n        }", 1)[0]
            self.assertIn("ReleaseCapture();", body)
        self.assertNotRegex(self.android, r"InputSystem\.Queue|Keyboard\.current\..*WriteValue")
        self.assertIn("Cursor.lockState = mode;", self.android)


if __name__ == "__main__":
    unittest.main()
