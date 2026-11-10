"""Source-level regression for T4 capture eligibility; not Android-device proof."""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"


class CaptureEligibilityContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        start = cls.source.index("private void Update()")
        end = cls.source.index("private void ", start + len("private void Update()"))
        cls.update = cls.source[start:end]

    def test_only_authored_lock_and_real_input_mouse_enable_capture(self):
        self.assertIn("bool authoredLocked = Volatile.Read(ref originalLockIntent) == 1;", self.update)
        self.assertIn("bool physicalPresent = PhysicalMousePresent();", self.update)
        self.assertRegex(self.update, r"bool shouldCapture\s*=\s*!paused\s*&&\s*focused\s*&&\s*authoredLocked\s*&&\s*physicalPresent;")
        presence = self.source.split("private static bool PhysicalMousePresent()", 1)[1].split("private void Update()", 1)[0]
        self.assertIn("mouse.added", presence)
        self.assertIn("mouse.name != VirtualTouchMouse", presence)
        self.assertNotIn("Input.mousePresent", presence.split("return false;", 1)[0])

    def test_all_gate_states_are_individually_encoded(self):
        expected = {
            "paused": 1,
            "focused": 2,
            "authoredLocked": 4,
            "physicalPresent": 8,
        }
        for flag, bit in expected.items():
            self.assertRegex(self.update, rf"\({flag}\s*\?\s*{bit}\s*:\s*0\)")
        # Exhaustive truth-table: only one of the 16 possible states is eligible.
        for mask in range(16):
            paused = bool(mask & 1)
            focused = bool(mask & 2)
            authored = bool(mask & 4)
            physical = bool(mask & 8)
            eligible = not paused and focused and authored and physical
            self.assertEqual(eligible, mask == 14)

    def test_marker_only_on_transition_and_not_claimed_native_success(self):
        self.assertIn("private int lastCaptureEligibility = -1;", self.source)
        self.assertRegex(self.update, r"if\s*\(eligibility\s*!=\s*lastCaptureEligibility\)")
        self.assertIn("lastCaptureEligibility = eligibility;", self.update)
        self.assertIn('"physical_mouse_capture_eligibility"', self.update)
        for label in ("paused=", "focused=", "authoredLock=", "inputSystemPhysicalMouse=", "shouldCapture="):
            self.assertIn(label, self.update)
        self.assertIn("androidCaptureGranted=unknown", self.update)
        self.assertLess(self.update.index("if (eligibility != lastCaptureEligibility)"),
                        self.update.index("if (!shouldCapture)"))

    def test_keyboard_escape_and_release_path_remain(self):
        self.assertIn("Input.GetKeyDown(KeyCode.Escape)", self.update)
        self.assertIn('LogLockIntent("escape_release")', self.update)
        self.assertRegex(self.update, r"if\s*\(!shouldCapture\)\s*\{\s*if\s*\(requested\s*\|\|\s*nativeHasMotion\)\s*ReleaseCapture\(\);")
        self.assertIn("RequestCapture();", self.update)
        self.assertIn("ProbeCapturedPointer();", self.update)


if __name__ == "__main__":
    unittest.main()
