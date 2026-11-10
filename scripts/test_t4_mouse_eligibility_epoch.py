#!/usr/bin/env python3
"""Regression tests for T4 mouse eligibility epoch attribution."""
import unittest
from t4_diagnose_mouse_eligibility import diagnose

YES = "physical_mouse_capture_eligibility paused=false focused=true authoredLock=true inputSystemPhysicalMouse=true shouldCapture=true\n"
NO = "physical_mouse_capture_eligibility paused=false focused=true authoredLock=true inputSystemPhysicalMouse=false shouldCapture=false\n"

class MouseEpochTests(unittest.TestCase):
    def test_old_callback_does_not_prove_latest_epoch(self):
        result = diagnose([YES, "physical_mouse_capture_requested\n",
                           "physical_mouse_captured_action_callbacks\n", NO, YES])
        self.assertEqual(result["classification"], "ELIGIBLE_NO_REQUEST_OBSERVED")
        self.assertEqual(result["observed_markers"]["requests"], 1)
        self.assertEqual(result["last_gate_epoch_markers"]["requests"], 0)
        self.assertFalse(result["device_success_proven"])

    def test_request_without_callback_in_current_epoch(self):
        result = diagnose([YES, "physical_mouse_capture_requested\n"])
        self.assertEqual(result["classification"], "REQUEST_NO_CALLBACK_MARKER_OBSERVED")

    def test_current_epoch_callback_still_not_device_success(self):
        result = diagnose([YES, "physical_mouse_capture_requested\n",
                           "physical_mouse_captured_action_callbacks\n"])
        self.assertEqual(result["classification"], "CALLBACK_MARKER_PRESENT_UNVERIFIED_GAMEPLAY")
        self.assertFalse(result["device_success_proven"])

    def test_missing_gate_not_credited_from_callback(self):
        result = diagnose(["physical_mouse_capture_requested\n"])
        self.assertEqual(result["classification"], "NO_ELIGIBILITY_TELEMETRY")

if __name__ == "__main__":
    unittest.main()
