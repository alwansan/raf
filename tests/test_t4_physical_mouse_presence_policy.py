"""Source policy regression for Android physical mouse discovery.

This test does not emulate Unity/Android or claim hardware pointer capture.
Run: python3 -m unittest tests/test_t4_physical_mouse_presence_policy.py
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"


def physical_present(legacy_mouse_present, mice):
    """Model the intended Input System gate; legacy flag is deliberately ignored."""
    return any(added and name != "RaftAndroidTouchLeft" for name, added in mice)


class PhysicalMousePresencePolicy(unittest.TestCase):
    def test_legacy_false_with_real_input_system_mouse(self):
        self.assertTrue(physical_present(False, [("USB Mouse", True)]))

    def test_virtual_touch_does_not_trigger_capture(self):
        self.assertFalse(physical_present(True, [("RaftAndroidTouchLeft", True)]))
        self.assertFalse(physical_present(False, [("RaftAndroidTouchLeft", True)]))

    def test_unadded_or_absent_mouse_does_not_trigger_capture(self):
        self.assertFalse(physical_present(True, [("USB Mouse", False)]))
        self.assertFalse(physical_present(True, []))

    def test_real_mouse_with_virtual_touch(self):
        self.assertTrue(physical_present(False, [("RaftAndroidTouchLeft", True), ("USB Mouse", True)]))

    def test_source_keeps_input_system_and_virtual_exclusion_without_legacy_gate(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("private static bool PhysicalMousePresent()", source)
        body = source.split("private static bool PhysicalMousePresent()", 1)[1].split("private void Update()", 1)[0]
        self.assertIn("Mouse.all", body)
        self.assertIn("mouse.added", body)
        self.assertIn("mouse.name != VirtualTouchMouse", body)
        self.assertNotIn("if (!Input.mousePresent)", body)
        self.assertIn("Input.GetKeyDown(KeyCode.Escape)", source)
        self.assertIn("RaftAndroidTouchLeft", source)


if __name__ == "__main__":
    unittest.main()
