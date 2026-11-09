#!/usr/bin/env python3
"""Regression: capture request alone cannot prove a captured Android mouse callback."""
import json
import unittest
from scripts.t4_analyze_mouse_lab_routes import analyze


def record(event, detail):
    return json.dumps({"event": event, "detail": detail})


class CapturePhaseEvidenceTest(unittest.TestCase):
    def test_request_without_capture_flag_is_unknown(self):
        rows = [
            record("capture_request", "ON"),
            record("input", "route=view_generic source=0x2002 action=ACTION_BUTTON_PRESS actionButton=1 buttonState=1"),
        ]
        result = analyze(rows)
        self.assertNotIn("on", result["phases"])
        self.assertEqual(result["phases"]["unknown"]["button_presses_observed"], ["left"])
        self.assertFalse(result["device_success_proven"])

    def test_explicit_capture_true_is_separate_from_request(self):
        rows = [
            record("capture_request", "OFF"),
            record("input", "route=captured source=0x20004 captured=true action=ACTION_BUTTON_PRESS actionButton=1 buttonState=1"),
            record("input", "route=view_generic source=0x2002 captured=false action=ACTION_SCROLL vscroll=1"),
        ]
        result = analyze(rows)
        self.assertEqual(result["phases"]["on"]["button_presses_observed"], ["left"])
        self.assertEqual(result["phases"]["off"]["vertical_scroll_events"], 1)
        self.assertFalse(result["device_success_proven"])


if __name__ == "__main__":
    unittest.main()
