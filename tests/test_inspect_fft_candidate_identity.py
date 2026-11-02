"""Synthetic tests only; never use or print authentic game program code."""
import unittest
from scripts.inspect_fft_candidate_identity import rank, identity_summary


class IdentityCandidateTests(unittest.TestCase):
    def test_selects_only_large_original_kernel_slots(self):
        rows = [{"owner": "resources.assets", "object_path_id": 905,
                 "metadata": {"metadata_array_totals": {"kernels": 12}}},
                {"owner": "sharedassets0.assets", "object_path_id": 2456,
                 "metadata": {"metadata_array_totals": {"kernels": 20}}},
                {"owner": "sharedassets29.assets", "object_path_id": 577,
                 "metadata": {"metadata_array_totals": {"kernels": 1}}}]
        self.assertEqual(rank(rows), [("resources.assets", 905), ("sharedassets0.assets", 2456)])
        rows[0]["metadata"]["metadata_array_totals"]["kernels"] = 0
        with self.assertRaisesRegex(ValueError, "candidate set changed"):
            rank(rows)

    def test_redacts_identifiers_but_preserves_all_original_slots(self):
        tree = {"m_Name": "OriginalFFTSecret", "variants": [{"kernels": [
            {"name": "SecretKernel6"}, {"name": "SecretKernel2"}, {}]}]}
        report = identity_summary(tree)
        self.assertEqual(report["original_serialized_kernel_count"], 3)
        self.assertTrue(report["asset_name_contains_fft"])
        self.assertNotIn("SecretKernel", str(report))
        self.assertNotIn("OriginalFFTSecret", str(report))
        self.assertEqual(len(report["kernel_identifier_sha256_by_original_slot"]), 3)
        self.assertNotEqual(report["kernel_identifier_sha256_by_original_slot"][0],
                            report["kernel_identifier_sha256_by_original_slot"][1])
        self.assertFalse(report["original_kernel_order_rewritten"])

    def test_rejects_invalid_kernel_table(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            identity_summary({"m_Name": "water"})
        with self.assertRaisesRegex(ValueError, "safe scope"):
            identity_summary({"variants": [{"kernels": [{}] * 65}]})


if __name__ == "__main__":
    unittest.main()
