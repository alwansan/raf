#!/usr/bin/env python3
"""Regression: invalid negative masks must not fabricate physical mouse evidence."""
import json
import unittest
from t4_analyze_mouse_lab_routes import analyze

def event(source="0x2002", state="0", action_button="0", action="ACTION_BUTTON_PRESS"):
    return json.dumps({"event":"input","detail":f"route=captured captured=true source={source} action={action} buttonState={state} actionButton={action_button}"})

class NegativeMouseMasks(unittest.TestCase):
    def test_negative_source_rejected(self):
        result = analyze([event(source="-1", state="1", action_button="1")])
        self.assertEqual(result["rejected_records"], 1)
        self.assertEqual(result["phases"], {})

    def test_negative_button_state_rejected(self):
        result = analyze([event(state="-1", action_button="1")])
        self.assertEqual(result["rejected_records"], 1)
        self.assertEqual(result["phases"], {})

    def test_negative_action_button_rejected(self):
        result = analyze([event(state="1", action_button="-1")])
        self.assertEqual(result["rejected_records"], 1)
        self.assertEqual(result["phases"], {})

    def test_valid_captured_press_preserved(self):
        result = analyze([event(state="1", action_button="1")])
        self.assertEqual(result["rejected_records"], 0)
        self.assertEqual(result["phases"]["on"]["button_presses_observed"], ["left"])

if __name__ == "__main__":
    unittest.main()
