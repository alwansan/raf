"""Negative and positive controls for the source-free T4 eligibility classifier."""
import unittest
from scripts.t4_diagnose_mouse_eligibility import diagnose

def gate(**values):
    defaults = dict(paused="false", focused="true", authoredLock="true",
                    inputSystemPhysicalMouse="true", shouldCapture="true")
    defaults.update(values)
    return "input physical_mouse_capture_eligibility " + "; ".join(
        f"{k}={v}" for k, v in defaults.items()) + "\n"

class EligibilityTriageTests(unittest.TestCase):
    def test_missing_trace_is_unknown(self):
        self.assertEqual(diagnose([])["classification"], "NO_ELIGIBILITY_TELEMETRY")

    def test_no_mouse_is_not_android_denial(self):
        result = diagnose([gate(inputSystemPhysicalMouse="false", shouldCapture="false")])
        self.assertEqual(result["classification"], "NO_INPUT_SYSTEM_PHYSICAL_MOUSE")
        self.assertFalse(result["device_success_proven"])

    def test_focus_and_lock_separate(self):
        self.assertEqual(diagnose([gate(focused="false", shouldCapture="false")])["classification"],
                         "FOCUS_OR_PAUSE_GATE")
        self.assertEqual(diagnose([gate(authoredLock="false", shouldCapture="false")])["classification"],
                         "NO_AUTHORED_LOCK")

    def test_eligible_request_not_equivalent_to_callback(self):
        result = diagnose([gate(), "physical_mouse_capture_requested epoch=3\n"])
        self.assertEqual(result["classification"], "REQUEST_NO_CALLBACK_MARKER_OBSERVED")
        self.assertFalse(result["device_success_proven"])

    def test_callback_marker_does_not_prove_click(self):
        result = diagnose([gate(), "physical_mouse_capture_requested epoch=3\n",
                           "physical_mouse_relative events=1; epoch=3\n"])
        self.assertEqual(result["classification"], "CALLBACK_MARKER_PRESENT_UNVERIFIED_GAMEPLAY")
        self.assertFalse(result["device_success_proven"])

    def test_malformed_marker_is_unknown(self):
        self.assertEqual(diagnose(["physical_mouse_capture_eligibility paused=unknown\n"])
                         ["classification"], "INCOMPLETE_ELIGIBILITY_MARKER")

    def test_last_transition_is_used(self):
        result = diagnose([gate(), gate(inputSystemPhysicalMouse="false", shouldCapture="false")])
        self.assertEqual(result["classification"], "NO_INPUT_SYSTEM_PHYSICAL_MOUSE")
        self.assertEqual(result["eligibility_transitions"], 2)

if __name__ == "__main__":
    unittest.main()
