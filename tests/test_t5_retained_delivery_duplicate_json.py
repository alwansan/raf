"""Fail-closed regression for ambiguous retained delivery manifests."""
import json
import unittest
from scripts.t5_verify_retained_delivery_archive import _reject_duplicate_json_keys


class RetainedManifestDuplicateKeys(unittest.TestCase):
    def test_unique_nested_metadata_is_accepted(self):
        value = json.loads('{"files":[{"name":"a","parts":[{"sha256":"x"}]}]}',
                           object_pairs_hook=_reject_duplicate_json_keys)
        self.assertEqual(value["files"][0]["parts"][0]["sha256"], "x")

    def test_duplicate_top_level_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate delivery JSON key"):
            json.loads('{"package":"original","package":"other"}',
                       object_pairs_hook=_reject_duplicate_json_keys)

    def test_duplicate_nested_part_hash_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate delivery JSON key"):
            json.loads('{"files":[{"parts":[{"sha256":"first","sha256":"second"}]}]}',
                       object_pairs_hook=_reject_duplicate_json_keys)

    def test_case_sensitive_distinct_keys(self):
        value = json.loads('{"sha256":"a","SHA256":"b"}',
                           object_pairs_hook=_reject_duplicate_json_keys)
        self.assertEqual(len(value), 2)


if __name__ == "__main__":
    unittest.main()
