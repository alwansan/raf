"""Synthetic ownership reconciliation tests; no Raft shader bytes."""
import unittest
from scripts.probe_authenticated_water_compute_inventory import reconcile


class ReconciliationTests(unittest.TestCase):
    def fixture(self):
        scan = [{"owner": "resources.assets", "original_path_id": i,
                 "original_object_sha256": str(i), "valid_dxbc_containers": []} for i in range(9)]
        meta = [{"owner": "resources.assets", "object_path_id": i,
                 "original_object_sha256": str(i), "metadata": {}} for i in range(9)]
        return {"unavailable_lfs_owners": [], "compute_objects": scan,
                "all_nine_original_compute_objects_examined": True}, {"compute_objects": meta}

    def test_nine_exact_identities_correlate_but_fft_not_inferred(self):
        scan, meta = self.fixture()
        result = reconcile(scan, meta)
        self.assertEqual(result["original_compute_shader_objects_correlated"], 9)
        self.assertFalse(result["fft_kernel_index_order_verified"])
        self.assertFalse(result["water_compute_owner_verified"])
        self.assertFalse(result["android_gpu_execution_verified"])

    def test_unverified_lfs_fails_closed(self):
        scan, meta = self.fixture()
        scan["unavailable_lfs_owners"] = ["sharedassets0.assets"]
        with self.assertRaisesRegex(ValueError, "Not all original LFS"):
            reconcile(scan, meta)

    def test_omitted_or_swapped_identity_fails_closed(self):
        scan, meta = self.fixture()
        meta["compute_objects"][0]["original_object_sha256"] = "tampered"
        with self.assertRaisesRegex(ValueError, "not corroborated"):
            reconcile(scan, meta)
        scan, meta = self.fixture()
        scan["compute_objects"].pop()
        with self.assertRaisesRegex(ValueError, "not corroborated"):
            reconcile(scan, meta)


if __name__ == "__main__":
    unittest.main()
