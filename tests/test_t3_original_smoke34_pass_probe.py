"""Source-free regressions for the unique authenticated smoke-name Shader48 probe."""
import json
import unittest

from scripts.t3_original_smoke34_pass_probe import (
    choose_smoke_shader, inspect_smoke_parsed,
)
from test_t3_original_particle_shader_state import state


class Smoke34SelectionTests(unittest.TestCase):
    def setUp(self):
        self.smoke = ("private_src", 401)
        self.fire34 = ("private_src", 402)
        self.ranks = {
            ("private_src", 400): 108, self.smoke: 34,
            self.fire34: 34, ("private_src", 403): 20,
            ("private_src", 404): 16, ("private_src", 405): 3,
        }
        self.rows = [(("scene_private", i), self.smoke, 2)
                     for i in range(17)]

    def test_same_rank_other_fire_shader_never_selected(self):
        self.assertEqual(choose_smoke_shader(self.rows, self.ranks), self.smoke)
        self.assertNotEqual(
            choose_smoke_shader(self.rows, self.ranks), self.fire34
        )

    def test_split_equal_rank_targets_rejected(self):
        rows = list(self.rows)
        rows[0] = (rows[0][0], self.fire34, 2)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            choose_smoke_shader(rows, self.ranks)

    def test_duplicate_renderer_rejected(self):
        rows = list(self.rows)
        rows[1] = (rows[0][0], self.smoke, 2)
        with self.assertRaises(ValueError):
            choose_smoke_shader(rows, self.ranks)

    def test_wrong_renderer_count_or_slot_count_rejected(self):
        with self.assertRaises(ValueError):
            choose_smoke_shader(self.rows[:-1], self.ranks)
        rows = list(self.rows)
        rows[0] = (rows[0][0], self.smoke, 1)
        with self.assertRaises(ValueError):
            choose_smoke_shader(rows, self.ranks)

    def test_missing_private_target_or_changed_source_rank_rejected(self):
        rows = list(self.rows)
        rows[0] = (rows[0][0], ("private_src", 999), 2)
        with self.assertRaises(ValueError):
            choose_smoke_shader(rows, self.ranks)
        ranks = dict(self.ranks)
        ranks[self.smoke] = 35
        with self.assertRaises(ValueError):
            choose_smoke_shader(self.rows, ranks)

    def test_bad_schema_rejected_without_key_dump(self):
        with self.assertRaises(ValueError) as context:
            choose_smoke_shader([("PRIVATE_ID",)], self.ranks)
        self.assertNotIn("PRIVATE_ID", str(context.exception))


class SmokePassParsedTests(unittest.TestCase):
    def parsed(self):
        return {"m_Name": "NEVER_PUBLISH_PRIVATE_SHADER_NAME",
                "m_SubShaders": [
                    {"m_Passes": [{"m_Type": 0, "m_State": state()}]}
                ]}

    def test_real_existing_state_classifier_proves_alpha_categories(self):
        result = inspect_smoke_parsed(self.parsed())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["original_pass_color_blend_category"],
                         "ALPHA_DEPENDENT")
        self.assertEqual(result[0]["original_pass_alpha_channel_blend_category"],
                         "REPLACE")
        self.assertEqual(result[0]["original_pass_depth_write_category"],
                         "OFF")
        self.assertNotIn("NEVER_PUBLISH_PRIVATE_SHADER_NAME", json.dumps(result))

    def test_non_normal_or_empty_pass_is_inconclusive(self):
        p = self.parsed()
        p["m_SubShaders"][0]["m_Passes"][0]["m_Type"] = 1
        with self.assertRaises(ValueError):
            inspect_smoke_parsed(p)
        p["m_SubShaders"][0]["m_Passes"] = []
        with self.assertRaises(ValueError):
            inspect_smoke_parsed(p)

    def test_two_original_passes_are_ordered_without_names(self):
        p = self.parsed()
        p["m_SubShaders"].append(
            {"m_Passes": [{"m_Type": 0, "m_State": state()}]})
        rows = inspect_smoke_parsed(p)
        self.assertEqual([(x["subshader_index"], x["pass_index"])
                          for x in rows], [(0, 0), (1, 0)])

    def test_private_classifier_label_not_exported(self):
        with self.assertRaises(ValueError):
            inspect_smoke_parsed(self.parsed(), classifier=lambda _: {
                "private_original_shader_name": "SHOULD_NOT_LEAK"})

    def test_state_is_not_device_or_same_export_proof(self):
        row = inspect_smoke_parsed(self.parsed())[0]
        self.assertTrue(row["native_ShaderLab_or_Android_pixels_not_verified"])
        self.assertTrue(row["original_fragment_alpha_output_or_discard_not_verified"])


if __name__ == "__main__":
    unittest.main()
