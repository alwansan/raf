"""Synthetic tests for T1 kernel6 bounded context triage."""
import tempfile
import unittest
from pathlib import Path
from scripts.t1_kernel6_log_context import scan

class Kernel6ContextTests(unittest.TestCase):
    def test_separate_hits_and_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.log"
            p.write_text("FindKernel Spectrum\nDispatch Spectrum\nwater_fft_invalid_compute_kernel kernel index 6\n"
                         "ultimate_water_invalid_pass Foam Global\n"
                         "water_fft_invalid_compute_kernel kernel index 6\n", encoding="utf-8")
            result = scan(p, "synthetic-01", before=2, after=1, max_hits=1)
            self.assertEqual(result["counts"]["kernel6_lines"], 2)
            self.assertEqual(result["counts"]["water_pass_lines"], 1)
            self.assertEqual(result["sampled_hits"], 1)
            self.assertEqual(result["events"][0]["line"], 3)
            self.assertFalse(result["original_kernel_identity_proven"])
            self.assertTrue(result["source_sha256"])
    def test_reject_unsafe_session_and_bounds(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.log"
            p.write_text("kernel index 6\n")
            with self.assertRaises(ValueError):
                scan(p, "../mixed")
            with self.assertRaises(ValueError):
                scan(p, "s", max_hits=0)
    def test_errors_only_skips_benign_mentions_without_losing_counts(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.log"
            p.write_text("FindKernel kernel index 6\\nDispatch kernel index 6\\n"
                         "water_fft_invalid_compute_kernel kernel index 6\\n", encoding="utf-8")
            result = scan(p, "synthetic-errors", max_hits=1, errors_only=True)
            self.assertEqual(result["counts"]["kernel6_lines"], 3)
            self.assertEqual(result["counts"]["kernel6_nonerror_mentions"], 2)
            self.assertEqual(result["counts"]["kernel6_error_lines"], 1)
            self.assertEqual(result["sampled_hits"], 1)
            self.assertEqual(result["events"][0]["line"], 3)
            self.assertTrue(result["sample_errors_only"])
if __name__ == "__main__":
    unittest.main()
