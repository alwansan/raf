#!/usr/bin/env python3
"""Regression contract for bounded, redacted kernel-6 log-context sampling."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("t1_kernel6_log_context.py")
spec = importlib.util.spec_from_file_location("t1_kernel6_log_context", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ContextContract(unittest.TestCase):
    def run_scan(self, lines, **kwargs):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fixture.log"
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return mod.scan(p, "fixture-20261111", **kwargs)

    def test_physical_lines_and_error_only(self):
        lines = ["FindKernel kernel index 6"] + ["unrelated proprietary text"] * 9 + [
            "error kernel index (6) not found", "Dispatch kernel #6",
            "ultimate_water_invalid_pass Spectrum"]
        result = self.run_scan(lines, before=3, after=2, errors_only=True)
        self.assertEqual(result["counts"]["kernel6_lines"], 3)
        self.assertEqual(result["counts"]["kernel6_error_lines"], 1)
        self.assertEqual(result["counts"]["kernel6_nonerror_mentions"], 2)
        self.assertEqual(result["sampled_hits"], 1)
        event = result["events"][0]
        self.assertEqual(event["line"], 11)
        self.assertFalse(any(m["line"] == 1 for m in event["before"]))
        self.assertEqual([m["line"] for m in event["after"]], [12, 13])
        self.assertNotIn("unrelated proprietary text", str(result))
        self.assertFalse(result["original_kernel_identity_proven"])

    def test_index_boundary(self):
        r = self.run_scan(["error kernel #16", "error kernel #60", "error kernel #6"])
        self.assertEqual(r["counts"]["kernel6_lines"], 1)

if __name__ == "__main__":
    unittest.main()
