"""Synthetic fail-closed provenance tests; no original Raft game bytes."""
import hashlib
import struct
import unittest
from unittest.mock import patch

from scripts.verify_original_fft_array_provenance import correlate, COMPONENT_SIZE


class FftArrayCorrelatorTests(unittest.TestCase):
    @staticmethod
    def fixture():
        raw = b"\x00" * (COMPONENT_SIZE - 16) + struct.pack("<i", 1) + struct.pack("<iq", 0, 2456)
        mono = {
            "original_monobehaviour_script_link_verified": True,
            "original_monoscript_raw_sha256":
                "a0ae3f9edfd39bfc4a4df2af896d40ffb4fa0e81963f06c2ee0589e0bf2ad979",
            "original_monoscript_class_name_sha256":
                "cb4d4c048bb81a9c6260539769f50e73b91b44ae5d6ccc048038d342154ed687",
            "original_script_pointer_file_id": 1,
            "original_monoscript_path_id": 2305,
            "external_original_owner_basename": "globalgamemanagers.assets",
        }
        managed = {
            "original_class_csharp_source_sha256":
                "2e56c01c13c84b2bb908a628be6ab5378be7b702185fac9fe906545b602d3893",
            "original_direct_compute_shader_array_declarations": 1,
            "original_field_type_compute_shader_declarations": 0,
        }
        caller = {"original_literal_matches_serialized_fft_asset_name": 1}
        return raw, mono, managed, caller

    def test_authenticated_tail_keeps_kernel_indices_unverified(self):
        raw, mono, managed, caller = self.fixture()
        with patch("scripts.verify_original_fft_array_provenance.COMPONENT_SHA",
                   hashlib.sha256(raw).hexdigest()):
            report = correlate(raw, mono, managed, caller)
        self.assertTrue(report["original_one_element_fft_array_tail_correlated"])
        self.assertFalse(report["serialized_field_type_tree_verified"])
        self.assertFalse(report["unity_fft_runtime_kernel_indices_verified"])

    def test_corruption_and_unrelated_array_refused(self):
        raw, mono, managed, caller = self.fixture()
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            correlate(raw, mono, managed, caller)
        altered = raw[:-16] + struct.pack("<i", 3) + raw[-12:]
        with patch("scripts.verify_original_fft_array_provenance.COMPONENT_SHA",
                   hashlib.sha256(altered).hexdigest()):
            with self.assertRaisesRegex(ValueError, "array tail"):
                correlate(altered, mono, managed, caller)

    def test_original_monoscript_and_managed_caller_both_required(self):
        raw, mono, managed, caller = self.fixture()
        with patch("scripts.verify_original_fft_array_provenance.COMPONENT_SHA",
                   hashlib.sha256(raw).hexdigest()):
            mono["original_script_pointer_file_id"] = 2
            with self.assertRaisesRegex(ValueError, "MonoScript"):
                correlate(raw, mono, managed, caller)
            mono["original_script_pointer_file_id"] = 1
            managed["original_direct_compute_shader_array_declarations"] = 0
            with self.assertRaisesRegex(ValueError, "CSharp"):
                correlate(raw, mono, managed, caller)
            managed["original_direct_compute_shader_array_declarations"] = 1
            caller["original_literal_matches_serialized_fft_asset_name"] = 0
            with self.assertRaisesRegex(ValueError, "literal"):
                correlate(raw, mono, managed, caller)


if __name__ == "__main__":
    unittest.main()
