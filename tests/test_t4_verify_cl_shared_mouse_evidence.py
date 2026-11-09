"""T4 real CL Android mouse source contract; all fixtures synthetic."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.t4_verify_cl_shared_mouse_evidence import (
    count_events, fields, physical_mouse, finite_axis, read_jsonl
)


def item(action, route="activity_generic", event_time=100, source="0x2002",
         captured="false", button_state="0x0", action_button="0x0",
         vscroll="0.0", hscroll="0.0", x="0", y="0"):
    detail = (f"route={route} action={action} source={source} "
              f"buttonState={button_state} actionButton={action_button} "
              f"vscroll={vscroll} hscroll={hscroll} eventTime={event_time} "
              f"x={x} y={y} captured={captured}")
    return {"event": "input", "detail": detail}


class ClRealEvidenceTests(unittest.TestCase):
    def test_activity_view_duplicate_even_with_coordinates_transformed(self):
        a = item("ACTION_SCROLL", route="activity_generic", x="900", y="500",
                 event_time=4, vscroll="2.0")
        b = item("ACTION_SCROLL", route="view_generic", x="200", y="50",
                 event_time=4, vscroll="2.0")
        r = count_events([a, b])
        self.assertEqual(r["raw_physical_mouse_callback_records"], 2)
        self.assertEqual(r["unique_android_motion_events"], 1)
        self.assertEqual(r["multi_route_duplicates_removed"], 1)
        self.assertEqual(r["scroll_axes_unique"]["vertical_positive"], 1)

    def test_physical_mouse_button_edges_only_not_down_held(self):
        rows = [
            item("ACTION_DOWN", button_state="0x1", event_time=1),
            item("ACTION_HOVER_MOVE", button_state="0x1", event_time=2),
            item("ACTION_BUTTON_PRESS", button_state="0x1", action_button="0x1", event_time=3),
            item("ACTION_BUTTON_RELEASE", action_button="0x1", event_time=4),
            item("ACTION_UP", event_time=5),
        ]
        r = count_events(rows)
        self.assertEqual(r["press_edges_action_button"], {"left": 1})
        self.assertEqual(r["release_edges_action_button"], {"left": 1})

    def test_missing_captured_callback_cannot_be_proof_even_with_capture_on_request(self):
        r = count_events([
            {"event": "capture_request", "detail": "ON"},
            item("ACTION_BUTTON_PRESS", captured="false", button_state="0x1", action_button="0x1"),
        ], {"results": [{"case_id": "T4-09", "result": {"status": "EVIDENCE_READY"}}]})
        self.assertEqual(r["capture_requests"], {"ON": 1})
        self.assertEqual(r["captured_callback_unique"], 0)
        self.assertFalse(r["device_input_capture_verified"])
        self.assertFalse(r["t4_09_game_bridge_accepted"])
        self.assertFalse(r["gameplay_fixed"])

    def test_captured_callback_is_only_android_proof_not_unity_success(self):
        r = count_events([
            {"event": "capture_request", "detail": "ON"},
            item("ACTION_BUTTON_PRESS", "captured", event_time=2,
                 captured="true", button_state="0x2", action_button="0x2")
        ])
        self.assertEqual(r["press_edges_action_button"], {"right": 1})
        self.assertTrue(r["device_input_capture_verified"])
        self.assertFalse(r["unity_legacy_mouse_delivery_proven"])

    def test_touchscreen_events_rejected(self):
        r = count_events([item("ACTION_BUTTON_PRESS", "activity_touch",
                               source="0x1002", action_button="0x1")])
        self.assertEqual(r["rejected_nonmouse_input_records"], 1)
        self.assertEqual(r["press_edges_action_button"], {})
        self.assertFalse(physical_mouse("0x1002"))
        self.assertTrue(physical_mouse("0x2002"))
        self.assertTrue(physical_mouse("0x20004"))

    def test_axis_only_scroll_and_finite(self):
        r = count_events([
            item("ACTION_MOVE", event_time=1, vscroll="1.0", hscroll="4.0"),
            item("ACTION_SCROLL", event_time=2, vscroll="-1.0", hscroll="NaN"),
            item("ACTION_SCROLL", event_time=3, vscroll="1.0", hscroll="0.0"),
        ])
        self.assertEqual(r["scroll_axes_unique"], {"vertical_negative": 1, "vertical_positive": 1})
        self.assertEqual(finite_axis("Infinity"), 0.0)
        self.assertEqual(finite_axis("NaN"), 0.0)

    def test_no_source_or_bad_button_mask_is_fail_closed(self):
        bad = item("ACTION_BUTTON_PRESS", event_time=1, action_button="invalid")
        with self.assertRaises(ValueError):
            count_events([bad])
        missing = item("ACTION_BUTTON_PRESS", event_time=1)
        missing["detail"] = missing["detail"].replace("source=0x2002 ", "")
        self.assertEqual(count_events([missing])["raw_physical_mouse_callback_records"], 0)
        self.assertEqual(count_events([missing])["rejected_nonmouse_input_records"], 1)

    def test_missing_device_action_cannot_be_rebranded(self):
        r = count_events([{"event": "manual_mouse_summary", "detail": "T4-09 buttons=58 scroll=87"}],
                         {"results": [{"case_id": "T4-09", "result": {"status": "EVIDENCE_READY"}}]})
        self.assertEqual(r["t4_09_saved_status"], "EVIDENCE_READY")
        self.assertEqual(r["unique_android_motion_events"], 0)
        self.assertFalse(r["t4_09_game_bridge_accepted"])
        self.assertFalse(r["gameplay_fixed"])

    def test_real_style_same_clock_down_up_are_not_extra_clicks(self):
        rows = [
            item("ACTION_HOVER_MOVE", event_time=99, button_state="0x0"),
            item("ACTION_DOWN", route="activity_touch", event_time=100,
                 button_state="0x1", action_button="0x0"),
            item("ACTION_BUTTON_PRESS", route="activity_generic", event_time=100,
                 button_state="0x1", action_button="0x1"),
            item("ACTION_BUTTON_RELEASE", route="activity_generic", event_time=200,
                 button_state="0x0", action_button="0x1"),
            item("ACTION_UP", route="activity_touch", event_time=200,
                 button_state="0x0", action_button="0x0"),
        ]
        result = count_events(rows)
        corr = result["implicit_down_up_correlation"]
        self.assertEqual(result["press_edges_action_button"], {"left": 1})
        self.assertEqual(result["release_edges_action_button"], {"left": 1})
        self.assertEqual(corr["actionbutton_zero"], {"press": 1, "release": 1})
        self.assertEqual(corr["matched_to_explicit_same_eventtime"],
                         {"press_left": 1, "release_left": 1})
        self.assertEqual(corr["unpaired_ambiguous_not_click_proof"], {})
        self.assertEqual(corr["additional_clicks_inferred"], 0)
        self.assertFalse(corr["unity_delivery_proven"])

    def test_implicit_without_explicit_or_different_clock_is_ambiguous(self):
        rows = [
            item("ACTION_DOWN", event_time=100, button_state="0x1"),
            item("ACTION_BUTTON_PRESS", event_time=101, button_state="0x1",
                 action_button="0x1"),
            item("ACTION_UP", event_time=200, button_state="0x0"),
            item("ACTION_BUTTON_RELEASE", event_time=201, button_state="0x0",
                 action_button="0x1"),
        ]
        corr = count_events(rows)["implicit_down_up_correlation"]
        self.assertEqual(corr["matched_to_explicit_same_eventtime"], {})
        self.assertEqual(corr["unpaired_ambiguous_not_click_proof"],
                         {"press": 1, "release": 1})
        self.assertEqual(corr["additional_clicks_inferred"], 0)

    def test_implicit_captured_mismatch_and_conflicting_edge_fail_closed(self):
        rows = [
            item("ACTION_DOWN", event_time=10, button_state="0x1",
                 captured="true", route="captured"),
            item("ACTION_BUTTON_PRESS", event_time=10, button_state="0x1",
                 action_button="0x1", captured="false"),
            item("ACTION_UP", event_time=20, button_state="0x0",
                 captured="true", route="captured"),
            item("ACTION_BUTTON_RELEASE", event_time=20, button_state="0x0",
                 action_button="0x1", captured="false"),
        ]
        corr = count_events(rows)["implicit_down_up_correlation"]
        self.assertEqual(corr["matched_to_explicit_same_eventtime"], {})
        self.assertEqual(corr["unpaired_ambiguous_not_click_proof"],
                         {"press": 1, "release": 1})
        self.assertFalse(corr["unity_delivery_proven"])

    def test_sourceless_and_bad_action_button_never_infer_edges(self):
        rows = [item("ACTION_DOWN", event_time=100, button_state="0x1")]
        rows[0]["detail"] = rows[0]["detail"].replace("eventTime=100 ", "")
        corr = count_events(rows)["implicit_down_up_correlation"]
        self.assertEqual(corr["unpaired_ambiguous_not_click_proof"], {"press": 1})
        self.assertEqual(corr["additional_clicks_inferred"], 0)
        bad = item("ACTION_DOWN", event_time=100)
        bad["detail"] = bad["detail"].replace("buttonState=0x0", "buttonState=nope")
        with self.assertRaises(ValueError):
            count_events([bad])

    def test_local_jsonl_parser_bounds_and_content(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "events.jsonl"
            p.write_text(json.dumps(item("ACTION_SCROLL"))+"\n")
            self.assertEqual(len(read_jsonl(p)), 1)
            p.write_text("{notjson")
            with self.assertRaises(json.JSONDecodeError):
                read_jsonl(p)
            try:
                p.unlink()
                p.symlink_to(Path(t)/"missing")
            except OSError:
                return
            with self.assertRaises(ValueError):
                read_jsonl(p)


if __name__ == "__main__":
    unittest.main()
