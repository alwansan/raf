import io
import json
import unittest
from scripts.t4_analyze_mouse_lab_routes import analyze

def event(kind, detail):
    return json.dumps({"event": kind, "detail": detail}) + "\n"

class MouseRouteTests(unittest.TestCase):
    def test_capture_button_and_scroll(self):
        lines = [event("capture_request", "ON"),
                 event("input", "route=captured source=0x2002 action=ACTION_BUTTON_PRESS source=0x2002 buttonState=0x2 actionButton=0x2 vscroll=0 hscroll=0 captured=true"),
                 event("input", "route=captured source=0x2002 action=ACTION_SCROLL source=0x2002 buttonState=0x0 actionButton=0x0 vscroll=-1 hscroll=0 captured=true")]
        r = analyze(lines)
        self.assertEqual(r["phases"]["on"]["buttons_observed"], ["right"])
        self.assertEqual(r["phases"]["on"]["vertical_scroll_events"], 1)
        self.assertFalse(r["device_success_proven"])

    def test_uncaptured_and_bad_record(self):
        r = analyze([event("input", "route=activity_touch source=0x2002 action=ACTION_DOWN buttonState=0x1 actionButton=0x0 vscroll=0 hscroll=0 captured=false"), "{bad"])
        self.assertEqual(r["phases"]["off"]["buttons_observed"], ["left"])
        self.assertEqual(r["rejected_records"], 1)

    def test_held_state_is_not_button_press_or_release(self):
        lines = [
            event("input", "route=captured source=0x2002 action=ACTION_MOVE buttonState=0x1 actionButton=0x0 captured=true"),
            event("input", "route=captured source=0x2002 action=ACTION_BUTTON_PRESS buttonState=0x2 actionButton=0x2 captured=true"),
            event("input", "route=captured source=0x2002 action=ACTION_BUTTON_RELEASE buttonState=0x0 actionButton=0x2 captured=true"),
        ]
        group = analyze(lines)["phases"]["on"]
        self.assertEqual(group["buttons_observed"], ["left", "right"])
        self.assertEqual(group["button_presses_observed"], ["right"])
        self.assertEqual(group["button_releases_observed"], ["right"])

    def test_action_button_zero_does_not_invent_edge(self):
        group = analyze([event("input", "route=activity_touch source=0x2002 action=ACTION_DOWN buttonState=0x1 actionButton=0 captured=false")])["phases"]["off"]
        self.assertEqual(group["buttons_observed"], ["left"])
        self.assertEqual(group["button_presses_observed"], [])

    def test_non_scroll_motion_axis_does_not_prove_wheel(self):
        lines = [
            event("input", "route=captured source=0x2002 action=ACTION_MOVE buttonState=0 actionButton=0 vscroll=1 hscroll=-1 captured=true"),
            event("input", "route=captured source=0x2002 action=ACTION_SCROLL buttonState=0 actionButton=0 vscroll=-1 hscroll=2 captured=true"),
            event("input", "route=captured source=0x2002 action=ACTION_SCROLL buttonState=0 actionButton=0 vscroll=0 hscroll=0 captured=true"),
        ]
        group = analyze(lines)["phases"]["on"]
        self.assertEqual(group["vertical_scroll_events"], 1)
        self.assertEqual(group["horizontal_scroll_events"], 1)
        self.assertFalse(analyze(lines)["device_success_proven"])

    def test_touchscreen_cannot_prove_mouse_click(self):
        lines = [event("input", "route=activity_touch source=0x1002 action=ACTION_DOWN buttonState=0x1 actionButton=0x1 captured=false"),
                 event("input", "route=captured source=0x1002 action=ACTION_SCROLL vscroll=1 captured=true")]
        r = analyze(lines)
        self.assertEqual(r["phases"], {})
        self.assertEqual(r["rejected_records"], 2)

    def test_missing_source_cannot_prove_mouse_button(self):
        r = analyze([event("input", "route=captured action=ACTION_BUTTON_PRESS buttonState=1 actionButton=1 captured=true")])
        self.assertEqual(r["phases"], {})
        self.assertEqual(r["rejected_records"], 1)

    def test_relative_mouse_source_is_accepted(self):
        r = analyze([event("input", "route=captured source=0x20004 action=ACTION_BUTTON_PRESS buttonState=1 actionButton=1 captured=true")])
        self.assertEqual(r["phases"]["on"]["button_presses_observed"], ["left"])

    def test_nonfinite_scroll_is_not_wheel_evidence(self):
        r = analyze([event("input", "route=captured source=0x2002 action=ACTION_SCROLL vscroll=NaN hscroll=Infinity captured=true")])
        self.assertEqual(r["phases"]["on"]["vertical_scroll_events"], 0)
        self.assertEqual(r["phases"]["on"]["horizontal_scroll_events"], 0)

    def test_no_events_is_not_pass(self):
        r = analyze([event("capture_request", "ON")])
        self.assertEqual(r["phases"], {})
        self.assertFalse(r["device_success_proven"])

if __name__ == "__main__":
    unittest.main()
