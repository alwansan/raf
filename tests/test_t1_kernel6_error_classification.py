"""Regression: kernel index mentions are not automatically error messages."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t1_kernel6_log_context.py"
spec = importlib.util.spec_from_file_location("t1_kernel6_log_context", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Kernel6ErrorClassification(unittest.TestCase):
    def test_mixed_error_and_nonerror_mentions(self):
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "test.log"
            log.write_text(
                "FindKernel returned kernel index 6\\n"
                "water_fft_invalid_compute_kernel: invalid kernel index 6\\n"
                "Dispatch kernel 6 successful\\n"
                "ComputeShader error kernel 7\\n", encoding="utf-8"
            )
            result = module.scan(log, "fixture-001")
            self.assertEqual(result["counts"]["kernel6_lines"], 3)
            self.assertEqual(result["counts"]["kernel6_error_lines"], 1)
            self.assertEqual(result["counts"]["kernel6_nonerror_mentions"], 2)
            self.assertFalse(result["original_kernel_identity_proven"])
            self.assertNotIn("returned kernel", str(result["events"]))

    def test_error_on_other_line_does_not_contaminate(self):
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "test.log"
            log.write_text("error: shader initialization\\nFindKernel kernel index 6\\n", encoding="utf-8")
            result = module.scan(log, "fixture-002")
            self.assertEqual(result["counts"]["kernel6_error_lines"], 0)


if __name__ == "__main__":
    unittest.main()
