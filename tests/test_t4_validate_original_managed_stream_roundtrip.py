"""Adversarial controls: a real original synthetic byte I/O run is not game save."""
import copy
import tempfile
import unittest
from pathlib import Path

from scripts.t4_validate_original_managed_stream_roundtrip import verify, main


def valid():
    return {
        "schema_version": 1,
        "source": "SHA_PINNED_ORIGINAL_FILEMANAGER_INVOKED",
        "original_managed_dll_authenticated": True,
        "original_read_write_edges_verified": True,
        "original_create_method_executed": True,
        "stream_closed_before_original_open": True,
        "original_open_method_executed": True,
        "synthetic_bytes_equal_after_reopen": True,
        "synthetic_file_size_equal": True,
        "temporary_file_cleanup_verified": True,
        "synthetic_filename_extension": ".rgd",
        "real_game_rgd_serialization_executed": False,
        "actual_android_app_storage_tested": False,
        "unity_or_il2cpp_executed": False,
        "private_game_data_or_identifiers_published": False,
    }


class OriginalManagedStreamSchema(unittest.TestCase):
    def test_valid_original_bounded_synthetic_stream_proof(self):
        r = verify(valid())
        self.assertEqual(r["status"], "AUTHENTIC_ORIGINAL_MANAGED_FILE_IO_ROUNDTRIP")
        self.assertFalse(r["real_rgd_game_save_proven"])

    def test_unknown_binary_rejected(self):
        x = valid(); x["original_managed_dll_authenticated"] = False
        with self.assertRaises(ValueError): verify(x)

    def test_synthetic_only_cannot_claim_game_save(self):
        x = valid(); x["real_game_rgd_serialization_executed"] = True
        with self.assertRaises(ValueError): verify(x)

    def test_cannot_claim_android_runtime(self):
        x = valid(); x["actual_android_app_storage_tested"] = True
        with self.assertRaises(ValueError): verify(x)

    def test_cannot_claim_unity_native(self):
        x = valid(); x["unity_or_il2cpp_executed"] = True
        with self.assertRaises(ValueError): verify(x)

    def test_cannot_expose_private_original_methods(self):
        x = valid(); x["private_game_data_or_identifiers_published"] = True
        with self.assertRaises(ValueError): verify(x)

    def test_missing_real_original_method_execution(self):
        x = valid(); x["original_create_method_executed"] = False
        with self.assertRaises(ValueError): verify(x)

    def test_fake_open_before_stream_closed(self):
        x = valid(); x["stream_closed_before_original_open"] = False
        with self.assertRaises(ValueError): verify(x)

    def test_missing_byte_equality(self):
        x = valid(); x["synthetic_bytes_equal_after_reopen"] = False
        with self.assertRaises(ValueError): verify(x)

    def test_missing_cleanup_rejected(self):
        x = valid(); x["temporary_file_cleanup_verified"] = False
        with self.assertRaises(ValueError): verify(x)

    def test_wrong_synthetic_extension(self):
        x = valid(); x["synthetic_filename_extension"] = ".user.rgd"
        with self.assertRaises(ValueError): verify(x)

    def test_unknown_source_claim(self):
        x = valid(); x["source"] = "SHA_ONLY_SOURCE_CENSUS"
        with self.assertRaises(ValueError): verify(x)

    def test_extra_private_data_field(self):
        x = valid(); x["original_game_bytes"] = "private"
        with self.assertRaises(ValueError): verify(x)

    def test_bool_schema_version_rejected(self):
        x = valid(); x["schema_version"] = True
        with self.assertRaises(ValueError): verify(x)

    def test_missing_report_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main(["--report", str(Path(d) / "absent.json")]), 2)


if __name__ == "__main__":
    unittest.main()
