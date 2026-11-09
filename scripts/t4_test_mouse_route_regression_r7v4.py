#!/usr/bin/env python3
"""T4 INPUT-005: source-only regressions; not an Android/Unity device test."""
import unittest
from t4_analyze_mouse_lab_routes import analyze
import json


def event(detail, kind="input"):
    return json.dumps({"event": kind, "detail": detail})


def mouse(route="captured", captured="true", action="ACTION_BUTTON_PRESS",
          button="1", state="1", source="0x2002", **extra):
    values = dict(route=route, captured=captured, source=source, action=action,
                  actionButton=button, buttonState=state, vscroll="0", hscroll="0")
    values.update(extra)
    return event(" ".join(f"{k}={v}" for k, v in values.items()))


class MouseRouteRegression(unittest.TestCase):
    def test_valid_captured_buttons_and_scroll(self):
        lines = [event("ON", "capture_request"),
                 mouse(button="1", state="1"),
                 mouse(action="ACTION_BUTTON_RELEASE", button="1", state="0"),
                 mouse(action="ACTION_BUTTON_PRESS", button="2", state="2"),
                 mouse(action="ACTION_BUTTON_RELEASE", button="2", state="0"),
                 mouse(action="ACTION_BUTTON_PRESS", button="4", state="4"),
                 mouse(action="ACTION_BUTTON_RELEASE", button="4", state="0"),
                 mouse(action="ACTION_SCROLL", button="0", state="0",
                       vscroll="1.0", hscroll="-0.5")]
        result = analyze(lines)
        phase = result["phases"]["on"]
        self.assertEqual(phase["samples"], 7)
        self.assertEqual(phase["button_presses_observed"], ["left", "middle", "right"])
        self.assertEqual(phase["button_releases_observed"], ["left", "middle", "right"])
        self.assertEqual((phase["vertical_scroll_events"], phase["horizontal_scroll_events"]), (1, 1))
        self.assertFalse(result["device_success_proven"])

    def test_capture_request_does_not_grant_capture(self):
        result = analyze([event("ON", "capture_request"),
                          mouse(route="activity_generic", captured="false")])
        self.assertNotIn("on", result["phases"])
        self.assertEqual(result["phases"]["off"]["samples"], 1)

    def test_contradictory_route_and_capture_rejected_both_directions(self):
        result = analyze([mouse(route="activity_generic", captured="true"),
                          mouse(route="captured", captured="false")])
        self.assertEqual(result["capture_route_conflicts"], 2)
        self.assertEqual(result["rejected_records"], 2)
        self.assertFalse(result["phases"])

    def test_malformed_envelopes_and_negative_masks_rejected(self):
        result = analyze(['null', '[]', '{"event":"input","detail":null}',
                          mouse(button="-1"), mouse(state="-1"),
                          mouse(source="-1")])
        self.assertEqual(result["rejected_records"], 6)
        self.assertFalse(result["phases"])

    def test_touch_and_nonfinite_scroll_not_counted(self):
        result = analyze([mouse(source="0x1002"),
                          mouse(action="ACTION_SCROLL", button="0", state="0",
                                vscroll="NaN", hscroll="Infinity")])
        self.assertEqual(result["rejected_records"], 1)
        self.assertEqual(result["phases"]["on"]["vertical_scroll_events"], 0)
        self.assertEqual(result["phases"]["on"]["horizontal_scroll_events"], 0)


if __name__ == "__main__":
    unittest.main()
