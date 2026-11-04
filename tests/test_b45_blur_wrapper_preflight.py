"""Synthetic tests: never use original/private shader code."""
import unittest
from unittest.mock import patch

from scripts.b45_blur_wrapper_preflight import diagnose
from scripts.a12_probe_original_blur_passes import TARGET


def fixture():
    return {"m_Name": TARGET, "m_PropInfo": {"m_Props": []},
            "m_SubShaders": [{"m_Passes": [
                {"m_Type": 0, "m_State": {}}, {"m_Type": 0, "m_State": {}}]}]}


class OriginalBlurContract(unittest.TestCase):
    @patch("scripts.b45_blur_wrapper_preflight.wrapper", return_value="synthetic only")
    @patch("scripts.b45_blur_wrapper_preflight.render_state", return_value="state")
    def test_pinned_topology_positive(self, state, wrapper):
        result = diagnose(fixture())
        self.assertTrue(result["wrapper_diagnostic_completed"])
        self.assertEqual(len(result["render_state"]), 2)
        self.assertFalse(result["candidate_installation_eligible"])
        wrapper.assert_called_once()

    @patch("scripts.b45_blur_wrapper_preflight.wrapper")
    @patch("scripts.b45_blur_wrapper_preflight.render_state", side_effect=ValueError("PRIVATE DATA MUST NOT LEAK"))
    def test_failure_is_sanitized_without_source(self, state, wrapper):
        result = diagnose(fixture())
        self.assertFalse(result["wrapper_diagnostic_completed"])
        self.assertTrue(all(p["failure_type"] == "ValueError" for p in result["render_state"]))
        self.assertNotIn("PRIVATE DATA", repr(result))
        wrapper.assert_not_called()

    @patch("scripts.b45_blur_wrapper_preflight.wrapper")
    @patch("scripts.b45_blur_wrapper_preflight.render_state", return_value="state")
    def test_nonempty_original_properties_fail_closed(self, state, wrapper):
        value = fixture()
        value["m_PropInfo"]["m_Props"] = [{"private": "do not print"}]
        result = diagnose(value)
        self.assertFalse(result["wrapper_diagnostic_completed"])
        self.assertEqual(result["original_property_entries"], 1)
        self.assertNotIn("do not print", repr(result))
        wrapper.assert_not_called()

    @patch("scripts.b45_blur_wrapper_preflight.wrapper")
    @patch("scripts.b45_blur_wrapper_preflight.render_state", return_value="state")
    def test_wrong_pass_kind_fail_closed(self, state, wrapper):
        value = fixture()
        value["m_SubShaders"][0]["m_Passes"][1]["m_Type"] = 1
        result = diagnose(value)
        self.assertFalse(result["wrapper_diagnostic_completed"])
        wrapper.assert_not_called()

    def test_reject_mutated_identity_or_topology(self):
        cases = [fixture(), fixture(), fixture()]
        cases[0]["m_Name"] = "Other"
        cases[1]["m_SubShaders"][0]["m_Passes"].pop()
        cases[2]["m_SubShaders"].append({})
        for value in cases:
            with self.subTest(value=value["m_Name"]), self.assertRaises(ValueError):
                diagnose(value)


if __name__ == "__main__":
    unittest.main()
