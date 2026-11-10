"""Regression: a size-limited GUID audit must never imply full coverage."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_unity_guid_link_audit.py"
spec = importlib.util.spec_from_file_location("t3_guid_audit_coverage", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CoverageTests(unittest.TestCase):
    def test_oversized_yaml_and_meta_report_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "large.mat").write_text("0123456789", encoding="utf-8")
            (root / "large.mat.meta").write_text("guid: " + "a" * 32, encoding="utf-8")
            with patch.object(module, "MAX_BYTES", 5):
                result = module.inspect(root)
            self.assertEqual(result["oversized_yaml_files_skipped"], 1)
            self.assertEqual(result["oversized_meta_files_skipped"], 1)
            self.assertFalse(result["coverage_complete_for_size_limit"])
            self.assertEqual(result["yaml_files_scanned"], 0)

    def test_small_valid_pair_reports_complete_size_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "small.mat").write_text("{}", encoding="utf-8")
            (root / "small.mat.meta").write_text("guid: " + "b" * 32, encoding="utf-8")
            result = module.inspect(root)
            self.assertTrue(result["coverage_complete_for_size_limit"])
            self.assertEqual(result["oversized_yaml_files_skipped"], 0)
            self.assertEqual(result["oversized_meta_files_skipped"], 0)


if __name__ == "__main__":
    unittest.main()
