"""Source-free regression for duplicate JSON keys in Foam role attestations."""
import json
import unittest

from scripts.t2_foam_pass_role_gate import unique_keys, validate


class FoamRoleDuplicateJSONTests(unittest.TestCase):
    def test_valid_two_pass_roles(self):
        payload = '{"sites":[{"pass":0,"source":"RenderTexture","destination":"RenderTexture"},{"pass":1,"source":"unknown","destination":"unknown"}]}'
        roles = validate(json.loads(payload, object_pairs_hook=unique_keys))
        self.assertEqual(roles[0], ("RenderTexture", "RenderTexture"))
        self.assertEqual(roles[1], ("unknown", "unknown"))

    def test_duplicate_source_rejected_before_validation(self):
        payload = '{"sites":[{"pass":0,"source":"unknown","source":"RenderTexture","destination":"unknown"},{"pass":1,"source":"unknown","destination":"unknown"}]}'
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            validate(json.loads(payload, object_pairs_hook=unique_keys))

    def test_duplicate_nested_pass_rejected(self):
        payload = '{"sites":[{"pass":1,"pass":0,"source":"unknown","destination":"unknown"},{"pass":1,"source":"unknown","destination":"unknown"}]}'
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            validate(json.loads(payload, object_pairs_hook=unique_keys))

    def test_duplicate_top_level_rejected(self):
        payload = '{"sites":[],"sites":[{"pass":0,"source":"unknown","destination":"unknown"},{"pass":1,"source":"unknown","destination":"unknown"}]}'
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            validate(json.loads(payload, object_pairs_hook=unique_keys))


if __name__ == "__main__":
    unittest.main()
