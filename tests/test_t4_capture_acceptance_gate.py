#!/usr/bin/env python3
import unittest
from scripts.t4_capture_acceptance_gate import triage

class CaptureAcceptanceGateTests(unittest.TestCase):
    def test_uncaptured_real_mouse_never_passes(self):
        r = triage({"phases": {"off": {"button_presses_observed": ["left"],
                                      "button_releases_observed": ["left"],
                                      "vertical_scroll_events": 55}}})
        self.assertEqual(r["status"], "NEEDS_CAPTURED_CALLBACKS")
        self.assertFalse(r["device_pass"])

    def test_capture_request_without_callback_never_passes(self):
        r = triage({"capture_requests": {"on": 1}, "phases": {}})
        self.assertEqual(r["status"], "NEEDS_CAPTURED_CALLBACKS")

    def test_captured_callbacks_still_do_not_prove_unity(self):
        r = triage({"phases": {"on": {"routes": ["captured"],
              "button_presses_observed": ["left", "right", "middle"],
              "button_releases_observed": ["left", "right", "middle"],
              "vertical_scroll_events": 4, "horizontal_scroll_events": 2}}})
        self.assertEqual(r["android"]["left"], "CALLBACK_PAIR_ONLY")
        self.assertEqual(r["android"]["horizontal_scroll"], "CALLBACK_ONLY")
        self.assertEqual(r["unity"], "UNVERIFIED")
        self.assertFalse(r["device_pass"])

    def test_partial_pair_remains_unverified(self):
        r = triage({"phases": {"on": {"routes": ["captured"],
              "button_presses_observed": ["right"],
              "button_releases_observed": [],
              "vertical_scroll_events": 0, "horizontal_scroll_events": 0}}})
        self.assertEqual(r["android"]["right"], "NEEDS_CAPTURED_PRESS_RELEASE")
        self.assertFalse(r["device_pass"])

    def test_rejects_fabricated_on_route(self):
        with self.assertRaises(ValueError):
            triage({"phases": {"on": {"routes": ["activity_generic"]}}})

if __name__ == "__main__":
    unittest.main()
