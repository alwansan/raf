import unittest
import tempfile
from pathlib import Path
from scripts.t3_render_state_pair_diff import compare, FIELDS, load_summary

class StateDiffTests(unittest.TestCase):
    def setUp(self):
        self.a = dict.fromkeys(FIELDS, "on")
    def test_match(self):
        self.assertEqual(compare(self.a, dict(self.a))["status"], "MATCH")
    def test_blend_change(self):
        b = dict(self.a, blend_dst="zero")
        self.assertEqual(compare(self.a, b)["changed_fields"], ["blend_dst"])
    def test_missing_rejected(self):
        with self.assertRaises(ValueError):
            compare(self.a, {})
    def test_unknown_not_pass(self):
        self.assertEqual(compare(self.a, dict(self.a, alpha_clip=None))["status"], "INCONCLUSIVE")
    def test_known_difference_not_masked_by_unrelated_unknown(self):
        b = dict(self.a, alpha_clip=None, blend_dst="zero")
        result = compare(self.a, b)
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(result["changed_fields"], ["blend_dst"])
        self.assertEqual(result["unknown_fields"], ["alpha_clip"])
        self.assertEqual(result["compared_fields"], len(FIELDS) - 1)

    def test_unknown_is_not_proven_difference(self):
        b = dict(self.a, alpha_clip=None)
        result = compare(self.a, b)
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["changed_fields"], [])
        self.assertEqual(result["unknown_fields"], ["alpha_clip"])

    def test_both_unknown_not_proven_difference(self):
        a = dict(self.a, alpha_clip=None)
        b = dict(a)
        result = compare(a, b)
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["changed_fields"], [])

    def test_bool_integer_alias_not_false_match(self):
        a = dict(self.a, zwrite=True)
        b = dict(a, zwrite=1)
        result = compare(a, b)
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(result["changed_fields"], ["zwrite"])

    def test_equal_integer_state_matches(self):
        a = dict(self.a, render_queue=3000)
        self.assertEqual(compare(a, dict(a))["status"], "MATCH")

    def test_type_mismatch_not_hidden_by_unknown(self):
        a = dict(self.a, zwrite=False)
        b = dict(a, zwrite=0, alpha_clip=None)
        result = compare(a, b)
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(result["changed_fields"], ["zwrite"])
        self.assertEqual(result["unknown_fields"], ["alpha_clip"])

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "states.json"
            path.write_text('{"blend_src":"one","blend_src":"zero"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate_json_field"):
                load_summary(path)

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "states.json"
            path.write_text('{"blend_src":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nonfinite_json_value"):
                load_summary(path)

    def test_valid_summary_file(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "states.json"
            path.write_text(json.dumps(self.a), encoding="utf-8")
            self.assertEqual(compare(load_summary(path), self.a)["status"], "MATCH")

    def test_private_extra_rejected(self):
        with self.assertRaises(ValueError):
            compare(dict(self.a, shader_name="private"), self.a)
    def test_nested_rejected(self):
        with self.assertRaises(ValueError):
            compare(self.a, dict(self.a, blend_dst={"raw":"private"}))

if __name__ == "__main__":
    unittest.main()
