"""Fail-closed regression for ambiguous retained delivery manifests."""
import json
import stat
import unittest
import zipfile
from scripts.t5_verify_retained_delivery_archive import _reject_duplicate_json_keys, _regular_zip_member


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


class RetainedZipMemberTypes(unittest.TestCase):
    def member(self, file_type, create_system=3):
        info = zipfile.ZipInfo("delivery.json")
        info.create_system = create_system
        info.external_attr = (file_type | 0o644) << 16
        return info

    def test_regular_unix_file_allowed(self):
        self.assertTrue(_regular_zip_member(self.member(stat.S_IFREG)))

    def test_unix_symlink_rejected(self):
        self.assertFalse(_regular_zip_member(self.member(stat.S_IFLNK)))

    def test_unix_device_rejected(self):
        self.assertFalse(_regular_zip_member(self.member(stat.S_IFCHR)))

    def test_directory_rejected(self):
        self.assertFalse(_regular_zip_member(zipfile.ZipInfo("subdir/")))

    def test_non_unix_regular_member_allowed(self):
        self.assertTrue(_regular_zip_member(self.member(stat.S_IFREG, create_system=0)))


if __name__ == "__main__":
    unittest.main()
