#!/usr/bin/env python3
"""Regression for first-observed millisecond timestamps in CL water chronology."""
import copy
import unittest
from t1_water_startup_order import analyze


def fixture():
    return {
        "session": "synthetic",
        "final_error_category_breakdown": {
            "ultimate_water_invalid_pass": {"count": 3, "first_observed_unix_ms": 1000},
            "water_fft_invalid_compute_kernel": {"count": 2, "first_observed_unix_ms": 1002},
        },
        "final_game_milestones": {
            "world_loaded_message_observed": {"count": 1, "first_observed_unix_ms": 1100}
        },
        "final_render_failure_breakdown": {
            "ultimate_water_invalid_pass_by_material": {"spectrum": 1, "foam_global": 2},
            "invalid_kernel_index_root_lines": {"index_6": 2}
        }
    }


class TimestampContract(unittest.TestCase):
    def test_valid_order(self):
        self.assertEqual(analyze(fixture())["fft_after_water_ms"], 2)

    def test_malformed_timestamps_rejected_for_each_event(self):
        paths = (
            ("final_error_category_breakdown", "ultimate_water_invalid_pass"),
            ("final_error_category_breakdown", "water_fft_invalid_compute_kernel"),
            ("final_game_milestones", "world_loaded_message_observed"),
        )
        for section, key in paths:
            for bad in (True, False, None, 0, -1, 1000.5, "1000", [], {}):
                with self.subTest(section=section, key=key, bad=repr(bad)):
                    s = fixture()
                    s[section][key]["first_observed_unix_ms"] = bad
                    with self.assertRaisesRegex(ValueError, "positive integer"):
                        analyze(s)

    def test_missing_timestamp_rejected(self):
        s = fixture()
        del s["final_error_category_breakdown"]["ultimate_water_invalid_pass"]["first_observed_unix_ms"]
        with self.assertRaisesRegex(ValueError, "positive integer"):
            analyze(s)


if __name__ == "__main__":
    unittest.main()
