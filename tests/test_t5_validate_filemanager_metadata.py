"""Synthetic negative controls of T5 original metadata/IL aggregate boundary."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from scripts.t5_validate_filemanager_metadata import verify_report, main

def sample():
    edge = {
        "resolved": True, "declared_in_filemanager": True,
        "static_target": True, "has_il_body": True,
        "parameter_count": 1, "il_instruction_count": 7,
        "direct_system_io_call_sites": 1, "exception_handler_count": 0,
    }
    return {
        "schema_version": 1,
        "source": "SHA_PINNED_ORIGINAL_MANAGED_DLL",
        "original_dll_sha256_verified": True, "original_dll_bytes": 3211776,
        "read_direct_call_count": 1, "write_direct_call_count": 1,
        "same_target_metadata_token": False,
        "read": edge.copy(), "write": edge.copy(),
        "both_target_bodies_resolved": True,
        "inspected_compiled_il_not_decompiler_text": True,
        "file_write_readback_executed": False,
        "rgd_reopen_or_android_device_proven": False,
        "private_identifiers_or_il_published": False,
    }

class OriginalMetadataReportTests(unittest.TestCase):
    def assert_refused(self, report):
        with self.assertRaises(ValueError):
            verify_report(report)

    def test_valid_bounded_report(self):
        r = verify_report(sample())
        self.assertTrue(r["read_target_resolved"])
        self.assertFalse(r["rgd_save_or_device_proven"])

    def test_unknown_method_body_is_not_a_negative_proof(self):
        r = sample()
        r["read"]["il_instruction_count"] = None
        self.assert_refused(r)

    def test_spoofed_full_device_or_save_proof_refused(self):
        for field in ("file_write_readback_executed", "rgd_reopen_or_android_device_proven",
                      "private_identifiers_or_il_published"):
            r = sample()
            r[field] = True
            self.assert_refused(r)

    def test_wrong_length_and_source_authentication_rejected(self):
        for field, val in (("original_dll_bytes", 3211777),
                           ("original_dll_sha256_verified", False),
                           ("source", "UNTRUSTED")):
            r = sample()
            r[field] = val
            self.assert_refused(r)

    def test_ambiguous_read_or_write_call_rejected(self):
        for name in ("read_direct_call_count", "write_direct_call_count"):
            for val in (0, 2, None, True):
                r = sample()
                r[name] = val
                self.assert_refused(r)

    def test_read_write_alias_cannot_be_pretended_distinct(self):
        r = sample()
        r["same_target_metadata_token"] = True
        self.assert_refused(r)

    def test_method_resolution_requires_real_same_class_body(self):
        for name in ("resolved", "declared_in_filemanager", "static_target", "has_il_body"):
            r = sample()
            r["read"][name] = False
            self.assert_refused(r)

    def test_no_original_names_or_extra_data_in_report(self):
        r = sample()
        r["raw_method_name"] = "private-value"
        self.assert_refused(r)
        r = sample()
        r["write"]["member_token"] = "private-value"
        self.assert_refused(r)

    def test_negative_counts_and_bool_masquerade_refused(self):
        for value in (True, -1, 0, None):
            r = sample()
            r["read"]["il_instruction_count"] = value
            self.assert_refused(r)

    def test_cli_parses_only_expected_safe_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "result.json"
            file.write_text(json.dumps(sample()))
            self.assertEqual(main(["--report", str(file)]), 0)
            file.write_text("{not-json")
            self.assertEqual(main(["--report", str(file)]), 2)

    def test_cli_refuses_symlinked_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "safe.json"
            file.write_text(json.dumps(sample()))
            link = Path(tmp) / "alias.json"
            link.symlink_to(file)
            self.assertEqual(main(["--report", str(link)]), 2)

if __name__ == "__main__":
    unittest.main()
