#!/usr/bin/env python3
"""Regression: kernel-6 context windows count physical lines, not only marker lines."""
import tempfile
import unittest
from pathlib import Path
from scripts.t1_kernel6_log_context import scan


class Kernel6PhysicalWindowTests(unittest.TestCase):
    def run_scan(self, lines, before=2, after=2):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "device.log"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return scan(path, "physical-window-fixture", before=before,
                        after=after, max_hits=1, errors_only=True)

    def test_distant_findkernel_not_in_before_context(self):
        result = self.run_scan([
            "FindKernel FFT",
            "unrelated 1",
            "unrelated 2",
            "unrelated 3",
            "ERROR invalid kernel index 6",
        ])
        self.assertEqual(result["counts"]["kernel6_error_lines"], 1)
        self.assertEqual(result["events"][0]["before"], [])

    def test_nearby_marker_preserved_without_raw_log(self):
        result = self.run_scan([
            "unrelated",
            "FindKernel FFT",
            "unrelated",
            "ERROR invalid kernel index 6",
            "unrelated",
            "Dispatch FFT",
        ])
        event = result["events"][0]
        self.assertEqual([m["line"] for m in event["before"]], [2])
        self.assertEqual([m["line"] for m in event["after"]], [6])
        self.assertNotIn("unrelated", str(event))

    def test_zero_before_still_excludes_prior(self):
        result = self.run_scan(["FindKernel FFT", "ERROR kernel index 6"], before=0)
        self.assertEqual(result["events"][0]["before"], [])


if __name__ == "__main__":
    unittest.main()
