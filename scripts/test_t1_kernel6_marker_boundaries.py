#!/usr/bin/env python3
"""Kernel-6 parser must not mistake prefixed words for Unity kernel indices."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("t1_kernel6_log_context", Path(__file__).with_name("t1_kernel6_log_context.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class KernelMarkerBoundary(unittest.TestCase):
    def test_prefix_boundary_and_case_insensitive_counters(self):
        lines = [
            "ERROR subkernel #6 invalid",
            "ERROR prekernel index (6) missing",
            "ERROR kernel #16 invalid",
            "ERROR kernel #60 invalid",
            "findkernel FFT",
            "DISPATCH FFT",
            "ULTIMATE_WATER_INVALID_PASS Spectrum",
            "ERROR kernel #6 invalid",
        ]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "device.log"
            p.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
            result = mod.scan(p, "t1-boundary", before=2, after=0, errors_only=True)
        self.assertEqual(result["counts"]["kernel6_lines"], 1)
        self.assertEqual(result["counts"]["kernel6_error_lines"], 1)
        self.assertEqual(result["counts"]["findkernel_lines"], 1)
        self.assertEqual(result["counts"]["dispatch_lines"], 1)
        self.assertEqual(result["counts"]["water_pass_lines"], 1)
        self.assertEqual(result["sampled_hits"], 1)
        self.assertEqual(result["events"][0]["line"], 8)
        self.assertFalse(result["original_kernel_identity_proven"])
        self.assertNotIn("subkernel", str(result))

if __name__ == "__main__":
    unittest.main()
