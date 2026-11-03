"""A12 CPU-only red/green controls; synthetic Shader names, never game assets."""
import json
import unittest

from scripts.a12_probe_original_vendor_identity_overlap import analyse_rows


VENDOR = {"Standard": "synthetic/Standard.shader", "UI/Default": "synthetic/UI.shader"}


class A12VendorIdentityOverlapTests(unittest.TestCase):
    def test_exact_original_serialized_name_matches_only_exact_vendor_identity(self):
        got = analyse_rows([("owner-A", 10, "Standard", "Standard"),
                            ("owner-A", 11, "Raft/Synthetic", "Raft/Synthetic")], VENDOR)
        self.assertEqual(got["original_shader_objects"], 2)
        self.assertEqual(got["exact_vendor_identity_objects"], 1)
        self.assertEqual(got["exact_vendor_objects_with_both_names"], 1)
        self.assertEqual(got["unique_exact_vendor_names"], 1)
        self.assertEqual(got["nonvendor_identity_objects"], 1)
        self.assertFalse(got["full_original_export_provenance_verified"])
        self.assertFalse(got["ready_for_build"])

    def test_basename_suffix_and_case_are_not_vendor_equivalences(self):
        got = analyse_rows([("owner", 1, "Raft/Standard", "Raft/Standard"),
                            ("owner", 2, "standard", "standard"),
                            ("owner", 3, "Default", "Default")], VENDOR)
        self.assertEqual(got["exact_vendor_identity_objects"], 0)
        self.assertEqual(got["nonvendor_identity_objects"], 3)

    def test_conflicting_original_names_are_ambiguous_not_vendor_hits(self):
        got = analyse_rows([("owner", 1, "Standard", "Raft/Original"),
                            ("owner", 2, "Raft/Original", "Standard")], VENDOR)
        self.assertEqual(got["conflicting_serialized_names"], 2)
        self.assertEqual(got["exact_vendor_identity_objects"], 0)
        self.assertEqual(got["usable_serialized_names"], 0)

    def test_missing_names_do_not_infer_negative_coverage(self):
        got = analyse_rows([("owner", 1, "", None),
                            ("owner", 2, None, "")], VENDOR)
        self.assertEqual(got["missing_serialized_names"], 2)
        self.assertEqual(got["exact_vendor_identity_objects"], 0)
        self.assertEqual(got["usable_serialized_names"], 0)
        self.assertFalse(got["asset_ripper_140_shader_export_identity_verified"])

    def test_serialized_fallback_is_reported_separately(self):
        got = analyse_rows([("owner", 1, None, "UI/Default")], VENDOR)
        self.assertEqual(got["exact_vendor_identity_objects"], 1)
        self.assertEqual(got["exact_vendor_objects_fallback_only"], 1)
        self.assertEqual(got["exact_vendor_objects_with_both_names"], 0)

    def test_duplicate_identity_is_not_duplicate_object(self):
        got = analyse_rows([("owner", 1, "Standard", "Standard"),
                            ("owner", 2, "Standard", "Standard")], VENDOR)
        self.assertEqual(got["exact_vendor_identity_objects"], 2)
        self.assertEqual(got["unique_exact_vendor_names"], 1)
        self.assertEqual(got["repeated_identity_objects"], 1)

    def test_duplicate_owner_object_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Duplicated"):
            analyse_rows([("owner", 1, "Standard", ""),
                          ("owner", 1, "Raft/Synthetic", "")], VENDOR)

    def test_invalid_types_and_empty_inventory_fail(self):
        for rows in ([], [("owner", 1, b"Standard", None)],
                     [("owner", True, "Standard", "Standard")],
                     [("", 1, "Standard", "Standard")],
                     [("owner", 1, "Standard")]):
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    analyse_rows(rows, VENDOR)
        with self.assertRaises(ValueError):
            analyse_rows([("owner", 1, "Standard", "Standard")], {})

    def test_inventory_digest_changes_with_owner_or_path_id(self):
        base = analyse_rows([("owner-A", 1, "Standard", "Standard")], VENDOR)
        other_owner = analyse_rows([("owner-B", 1, "Standard", "Standard")], VENDOR)
        other_id = analyse_rows([("owner-A", 2, "Standard", "Standard")], VENDOR)
        self.assertNotEqual(base["whole_inventory_sha256"], other_owner["whole_inventory_sha256"])
        self.assertNotEqual(base["whole_inventory_sha256"], other_id["whole_inventory_sha256"])

    def test_no_names_or_per_object_details_are_published(self):
        private = "Raft/SyntheticSecretName"
        got = analyse_rows([("private-owner", 27, private, private)], VENDOR)
        serialized = json.dumps(got, sort_keys=True)
        for token in (private, "private-owner", "Standard", "UI/Default"):
            self.assertNotIn(token, serialized)
        self.assertEqual(len(got["whole_inventory_sha256"]), 64)
        self.assertEqual(got["exact_vendor_identity_objects"], 0)


if __name__ == "__main__":
    unittest.main()
