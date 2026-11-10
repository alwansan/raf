"""Synthetic regression for kernel index 6 punctuation variants; no GPU identity claim."""
import tempfile
import unittest
from pathlib import Path
from scripts.t1_kernel6_log_context import scan

class Kernel6PunctuationTests(unittest.TestCase):
    def test_parenthesized_and_hash_forms(self):
        lines = [
            "ComputeShader invalid kernel index (6)",
            "Dispatch kernel #6 failed",
            "FindKernel kernel index: 6 success",
            "kernel index (60) invalid",
            "kernel index 16 invalid",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.log"
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            result = scan(p, "synthetic-k6-punctuation", before=0, after=0, errors_only=True)
        self.assertEqual(result["counts"]["kernel6_lines"], 3)
        self.assertEqual(result["counts"]["kernel6_error_lines"], 2)
        self.assertEqual(result["counts"]["kernel6_nonerror_mentions"], 1)
        self.assertEqual([x["line"] for x in result["events"]], [1, 2])
        self.assertFalse(result["original_kernel_identity_proven"])

if __name__ == "__main__":
    unittest.main()
