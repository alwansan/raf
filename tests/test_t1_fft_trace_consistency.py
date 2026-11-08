"""Synthetic regression controls for recorded FFT kernel-index drift."""
import copy
import unittest
from scripts.t1_fft_trace_consistency import check

BASE = {
    "session": "phone-1", "compute_shader_guid": "a" * 32,
    "kernel_name": "FFT", "find_kernel_index": 6, "dispatch_kernel_index": 6,
    "numthreads": [8, 8, 1], "dispatch_groups": [2, 2, 1],
    "logical_extent": [16, 16, 1],
}

class TraceConsistencyTests(unittest.TestCase):
    def test_single_observation_is_not_proof(self):
        result = check([BASE])
        self.assertTrue(result["structural_consistency"])
        self.assertFalse(result["original_identity_proven"])
        self.assertFalse(result["gpu_execution_proven"])

    def test_duplicate_is_consistent(self):
        self.assertEqual(check([BASE, copy.deepcopy(BASE)])["identities"], 1)

    def test_same_session_kernel_index_drift_rejected(self):
        changed = copy.deepcopy(BASE)
        changed["find_kernel_index"] = 7
        changed["dispatch_kernel_index"] = 7
        with self.assertRaisesRegex(ValueError, "drift"):
            check([BASE, changed])

    def test_different_sessions_do_not_imply_stable_runtime_indices(self):
        changed = copy.deepcopy(BASE)
        changed["session"] = "phone-2"
        changed["find_kernel_index"] = 7
        changed["dispatch_kernel_index"] = 7
        self.assertEqual(check([BASE, changed])["sessions"], 2)

    def test_invalid_dispatch_rejected(self):
        changed = copy.deepcopy(BASE)
        changed["dispatch_groups"] = [1, 2, 1]
        with self.assertRaises(ValueError):
            check([changed])

if __name__ == "__main__":
    unittest.main()
