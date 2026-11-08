#!/usr/bin/env python3
"""Regression for reverse kernel index alias in one Unity ComputeShader session."""
import unittest
from scripts.t1_fft_trace_consistency import check

def obs(session="s1", guid="a" * 32, name="FFT_H", index=6):
    return {
        "session": session, "compute_shader_guid": guid,
        "kernel_name": name, "find_kernel_index": index,
        "dispatch_kernel_index": index, "numthreads": [8, 8, 1],
        "dispatch_groups": [2, 2, 1], "logical_extent": [16, 16, 1],
    }

class ReverseKernelIndexTests(unittest.TestCase):
    def test_same_index_different_names_rejected(self):
        with self.assertRaisesRegex(ValueError, "kernel index alias"):
            check([obs(), obs(name="FFT_V")])

    def test_same_index_different_sessions_allowed(self):
        self.assertTrue(check([obs(), obs(session="s2", name="FFT_V")])["structural_consistency"])

    def test_same_index_different_guids_allowed(self):
        self.assertTrue(check([obs(), obs(guid="b" * 32, name="FFT_V")])["structural_consistency"])

    def test_different_indices_same_shader_allowed(self):
        self.assertTrue(check([obs(), obs(name="FFT_V", index=7)])["structural_consistency"])

    def test_same_name_different_indices_still_rejected(self):
        with self.assertRaisesRegex(ValueError, "kernel index drift"):
            check([obs(), obs(index=7)])

    def test_case_normalized_guid_cannot_bypass_alias(self):
        with self.assertRaisesRegex(ValueError, "kernel index alias"):
            check([obs(guid="abcdef" * 5 + "ab"), obs(guid="ABCDEF" * 5 + "AB", name="FFT_V")])

if __name__ == "__main__":
    unittest.main()
