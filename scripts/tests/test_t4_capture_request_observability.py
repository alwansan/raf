"""Capture request is an attempt, not Android's pointer capture grant."""
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from t4_analyze_mouse_lab_routes import analyze


def rec(event, detail):
    return json.dumps({"event": event, "detail": detail})


class CaptureRequestObservability(unittest.TestCase):
    def test_requested_without_callback_is_not_granted(self):
        out = analyze([rec("capture_request", "ON"), rec("capture_request", "OFF")])
        self.assertEqual(out["capture_requests"], {"on": 1, "off": 1})
        self.assertTrue(out["capture_requested_but_no_confirmed_callbacks"])
        self.assertEqual(out["phases"], {})
        self.assertFalse(out["device_success_proven"])

    def test_confirmed_callback_is_distinct_from_request(self):
        out = analyze([rec("capture_request", "ON"), rec("input",
            "route=captured source=0x2002 captured=true action=ACTION_MOVE buttonState=0 actionButton=0")])
        self.assertEqual(out["phases"]["on"]["samples"], 1)
        self.assertFalse(out["capture_requested_but_no_confirmed_callbacks"])
        self.assertFalse(out["device_success_proven"])

    def test_off_or_invalid_request_not_counted_as_on(self):
        out = analyze([rec("capture_request", "OFF"), rec("capture_request", "maybe")])
        self.assertEqual(out["capture_requests"], {"on": 0, "off": 1})
        self.assertFalse(out["capture_requested_but_no_confirmed_callbacks"])

    def test_uncaptured_callback_does_not_prove_grant(self):
        out = analyze([rec("capture_request", "ON"), rec("input",
            "route=activity_generic source=0x2002 captured=false action=ACTION_SCROLL vscroll=1")])
        self.assertEqual(out["phases"]["off"]["vertical_scroll_events"], 1)
        self.assertTrue(out["capture_requested_but_no_confirmed_callbacks"])


if __name__ == "__main__":
    unittest.main()
