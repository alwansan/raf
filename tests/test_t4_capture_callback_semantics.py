#!/usr/bin/env python3
"""Source-only safety contract for captured Android mouse callbacks; not device proof."""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"


class CaptureCallbackSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = SOURCE.read_text(encoding="utf-8")
        cls.android = source.split("#elif UNITY_5_3_OR_NEWER", 1)[0]
        cls.callback = cls.android.split("public bool onCapturedPointer(", 1)[1].split(
            "private bool RecordCapturedMotion(", 1)[0]
        cls.actions = cls.android.split("private void RecordCapturedAction(", 1)[1].split(
            "private void LogCapturedActions(", 1)[0]

    def test_nonmove_actions_are_forwarded_but_not_consumed(self):
        callback = self.callback
        branch = callback.split("if (action != PhysicalMouseMotionSource.ActionMove)", 1)[1].split(
            "int source = motionEvent.Call<int>(\"getSource\")", 1)[0]
        self.assertIn("PhysicalMouseActionEvidence.IsAction(action)", branch)
        self.assertIn("owner.RecordCapturedAction(", branch)
        self.assertRegex(branch, r"owner\.RecordCapturedAction\([\s\S]*?\);\s*}\s*return false;")
        self.assertIn("getActionButton", branch)
        self.assertIn("getButtonState", branch)
        self.assertIn("getEventTime", branch)
        self.assertIn("getDeviceId", branch)

    def test_scroll_axis_only_read_on_scroll_action(self):
        branch = self.callback.split("if (action != PhysicalMouseMotionSource.ActionMove)", 1)[1].split(
            "return false;", 1)[0]
        self.assertRegex(branch, r"action == PhysicalMouseActionEvidence\.Scroll\s*\?\s*motionEvent\.Call<float>\(\"getAxisValue\", PhysicalMouseActionEvidence\.VScroll\)")
        self.assertRegex(branch, r"action == PhysicalMouseActionEvidence\.Scroll\s*\?\s*motionEvent\.Call<float>\(\"getAxisValue\", PhysicalMouseActionEvidence\.HScroll\)")

    def test_epoch_guard_and_physical_filter_before_fallback(self):
        self.assertIn("PhysicalMouseMotionSource.AcceptEpoch(listenerEpoch,epoch,requested)", self.actions)
        self.assertIn("buttonWheel.Record(action,source,changedButton,heldButton,vertical,horizontal,eventTimeMs,deviceId)", self.actions)
        self.assertRegex(self.actions, r"if\s*\(buttonWheel\.Record\([\s\S]*?\)\)\s*nativeCaptured\s*=\s*true;")
        self.assertNotIn("InputSystem.QueueStateEvent", self.actions)
        self.assertNotIn("Input.GetKey", self.actions)

    def test_non_mouse_axes_preserve_legacy_keyboard_route(self):
        axis = self.android.split("private static float Axis(string axis, bool raw)", 1)[1].split(
            "private void OnEnable()", 1)[0]
        self.assertIn('axis == "Mouse X" || axis == "Mouse Y"', axis)
        self.assertIn('axis == "Mouse ScrollWheel"', axis)
        self.assertIn("return raw ? Input.GetAxisRaw(axis) : Input.GetAxis(axis);", axis)


if __name__ == "__main__":
    unittest.main()
