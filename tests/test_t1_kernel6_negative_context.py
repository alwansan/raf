"""Regression: negative FindKernel results are errors, not benign mentions."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("t1_kernel6_log_context", ROOT / "scripts" / "t1_kernel6_log_context.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Kernel6NegativeContextTest(unittest.TestCase):
    def test_negative_lookup_and_success_are_separated(self):
        lines = [
            "FindKernel: kernel index 6 success",
            "kernel index 6 not found",
            "cannot find kernel index 6",
            "kernel index 6 missing",
            "Dispatch kernel index 6 success",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "synthetic.log"
            log.write_text("\n".join(lines) + "\n", encoding="utf-8")
            result = MODULE.scan(log, "synthetic-negative", before=0, after=0, errors_only=True)
        self.assertEqual(result["counts"]["kernel6_lines"], 5)
        self.assertEqual(result["counts"]["kernel6_error_lines"], 3)
        self.assertEqual(result["counts"]["kernel6_nonerror_mentions"], 2)
        self.assertEqual([event["line"] for event in result["events"]], [2, 3, 4])
        self.assertFalse(result["original_kernel_identity_proven"])


if __name__ == "__main__":
    unittest.main()
