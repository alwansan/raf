"""Strict preconditions for applying synthetic Foam RHS categories to original CIL."""
import unittest
from scripts.t2_foam_rhs_origin_guard import classify_verified_rhs


class VerifiedRhsPreconditions(unittest.TestCase):
    def test_missing_complete_slice_rejected(self):
        for ops in (["ldfld"], ["ldsfld"], ["newobj"], ["call"]):
            self.assertEqual(classify_verified_rhs(ops), "UNKNOWN")

    def test_instance_field_requires_receiver_evidence(self):
        self.assertEqual(classify_verified_rhs(["ldfld"], complete_slice=True), "UNKNOWN")
        self.assertEqual(classify_verified_rhs(["ldfld"], complete_slice=True,
                                               receiver_verified=True), "FIELD_READ")

    def test_static_field_does_not_require_receiver(self):
        self.assertEqual(classify_verified_rhs(["ldsfld"], complete_slice=True),
                         "STATIC_FIELD_READ")

    def test_call_requires_signature_and_complete_slice(self):
        self.assertEqual(classify_verified_rhs(["call"], complete_slice=True), "UNKNOWN")
        self.assertEqual(classify_verified_rhs(["call"], call_returns_value=True), "UNKNOWN")
        self.assertEqual(classify_verified_rhs(["call"], complete_slice=True,
                                               call_returns_value=True), "CALL_RESULT")

    def test_invalid_evidence_flags_fail_closed(self):
        for flags in ({"complete_slice": 1}, {"receiver_verified": "yes"},
                      {"call_returns_value": 1}):
            self.assertEqual(classify_verified_rhs(["ldfld"], **flags), "UNKNOWN")

    def test_control_flow_is_not_accepted_by_flag(self):
        self.assertEqual(classify_verified_rhs(["br.s", "ldfld"],
                                               complete_slice=True,
                                               receiver_verified=True), "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
