import unittest
from scripts.t3_render_state_pair_diff import compare, FIELDS

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
    def test_private_extra_rejected(self):
        with self.assertRaises(ValueError):
            compare(dict(self.a, shader_name="private"), self.a)
    def test_nested_rejected(self):
        with self.assertRaises(ValueError):
            compare(self.a, dict(self.a, blend_dst={"raw":"private"}))

if __name__ == "__main__":
    unittest.main()
