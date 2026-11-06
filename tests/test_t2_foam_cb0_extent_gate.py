"""Synthetic controls; never contain original private Foam shader data."""
import unittest
from scripts.t2_foam_cb0_extent_gate import cb0_integration_gate


def link(v=96, f=96):
    return {"vertex_bytes": v, "fragment_bytes": f,
            "authenticated_shared_coordinate": True}


class FoamCB0GateTests(unittest.TestCase):
    def test_original_style_two_pass_extent_mismatches_are_blocking(self):
        result = cb0_integration_gate([link(96, 128), link(64, 80)],
                                      member_abi_verified=True,
                                      unity_upload_verified=True)
        self.assertEqual(result["status"], "blocked_CB0_byte_extent_mismatch")
        self.assertEqual(result["mismatched_pass_count"], 2)

    def test_equal_extent_is_not_member_or_upload_proof(self):
        self.assertEqual(cb0_integration_gate([link()])["status"],
                         "blocked_CB0_member_ABI_unverified")
        self.assertEqual(cb0_integration_gate(
            [link()], member_abi_verified=True)["status"],
            "blocked_Unity_CB0_upload_unverified")

    def test_explicit_evidence_is_only_source_gate_not_device(self):
        self.assertEqual(cb0_integration_gate(
            [link()], member_abi_verified=True,
            unity_upload_verified=True)["status"],
            "source_gate_satisfied_not_Unity_or_device_verified")

    def test_missing_or_untrusted_coordinates_fail_closed(self):
        self.assertEqual(cb0_integration_gate([])["status"],
                         "blocked_missing_authenticated_CB0_links")
        row = link()
        row["authenticated_shared_coordinate"] = False
        self.assertEqual(cb0_integration_gate([row])["status"],
                         "blocked_invalid_CB0_link")

    def test_bool_float_negative_and_oversize_are_not_byte_extents(self):
        for invalid in (True, 96.0, 0, -1, 65537, None):
            with self.subTest(value=invalid):
                self.assertEqual(cb0_integration_gate(
                    [link(invalid, 96)])["status"], "blocked_invalid_CB0_link")

    def test_authenticated_two_pass_coverage_required(self):
        result = cb0_integration_gate(
            [link()], member_abi_verified=True, unity_upload_verified=True,
            expected_pass_count=2)
        self.assertEqual(result["status"], "blocked_CB0_pass_coverage_mismatch")
        self.assertEqual(result["observed_pass_count"], 1)
        self.assertEqual(result["expected_pass_count"], 2)
        self.assertEqual(cb0_integration_gate(
            [link(), link()], member_abi_verified=True,
            unity_upload_verified=True, expected_pass_count=2)["status"],
            "source_gate_satisfied_not_Unity_or_device_verified")

    def test_expected_pass_count_is_strict_bounded_integer(self):
        for invalid in (True, 2.0, 0, -1, 65, "2"):
            with self.subTest(value=invalid):
                self.assertEqual(cb0_integration_gate(
                    [link(), link()], expected_pass_count=invalid)["status"],
                    "blocked_invalid_expected_pass_count")

    def test_missing_keys_and_non_boolean_evidence_fail_closed(self):
        self.assertEqual(cb0_integration_gate(
            [{"vertex_bytes": 96}])["status"], "blocked_invalid_CB0_link")
        self.assertEqual(cb0_integration_gate(
            [link()], member_abi_verified=1)["status"],
            "blocked_invalid_evidence_flags")


if __name__ == "__main__":
    unittest.main()
