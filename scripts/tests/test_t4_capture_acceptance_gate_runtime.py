"""Executable fail-closed regression tests for T4 capture triage (source only)."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "t4_capture_acceptance_gate.py"
spec = importlib.util.spec_from_file_location("t4_capture_acceptance_gate_under_test", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def sample(**changes):
    phase = {
        "routes": ["captured"],
        "button_presses_observed": ["left", "right", "middle"],
        "button_releases_observed": ["left", "right", "middle"],
        "vertical_scroll_events": 2,
        "horizontal_scroll_events": 1,
    }
    phase.update(changes)
    return {"phases": {"on": phase}}


class CaptureGateRuntimeTests(unittest.TestCase):
    def test_complete_android_callbacks_never_prove_unity(self):
        result = gate.triage(sample())
        self.assertEqual(result["status"], "ANDROID_ONLY_UNITY_UNVERIFIED")
        self.assertEqual(result["unity"], "UNVERIFIED")
        self.assertIs(result["device_pass"], False)
        for button in ("left", "right", "middle"):
            self.assertEqual(result["android"][button], "CALLBACK_PAIR_ONLY")
        for axis in ("vertical_scroll", "horizontal_scroll"):
            self.assertEqual(result["android"][axis], "CALLBACK_ONLY")

    def test_missing_capture_is_not_a_pass(self):
        result = gate.triage({"phases": {}})
        self.assertEqual(result["status"], "NEEDS_CAPTURED_CALLBACKS")
        self.assertIs(result["device_pass"], False)

    def test_unpaired_button_not_accepted(self):
        result = gate.triage(sample(button_releases_observed=["left", "middle"]))
        self.assertEqual(result["android"]["right"], "NEEDS_CAPTURED_PRESS_RELEASE")
        self.assertIs(result["device_pass"], False)

    def test_missing_wheel_not_accepted(self):
        result = gate.triage(sample(vertical_scroll_events=0, horizontal_scroll_events=0))
        self.assertEqual(result["android"]["vertical_scroll"], "NEEDS_CAPTURED_SCROLL")
        self.assertEqual(result["android"]["horizontal_scroll"], "NEEDS_CAPTURED_SCROLL")

    def test_malformed_routes_rejected(self):
        for routes in ("captured", [], [None], ["uncaptured"]):
            with self.subTest(routes=routes), self.assertRaises(ValueError):
                gate.triage(sample(routes=routes))

    def test_bad_button_names_rejected(self):
        for value in (["LEFT"], ["left", 1], "left", [None]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                gate.triage(sample(button_presses_observed=value))

    def test_negative_boolean_and_float_scroll_rejected(self):
        for value in (-1, True, 1.5, "1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                gate.triage(sample(vertical_scroll_events=value))

    def test_invalid_report_envelope_rejected(self):
        for value in (None, [], {"phases": []}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                gate.triage(value)


if __name__ == "__main__":
    unittest.main()
