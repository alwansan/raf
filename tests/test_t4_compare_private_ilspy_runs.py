"""Source-free negative controls for T4 private original decompiler output repeatability."""
import tempfile
import unittest
from pathlib import Path

from scripts.t4_compare_private_ilspy_runs import (
    compare_roots, source_profile,
)

BASE = """using System.Collections;
public class Raft_Network {
 public IEnumerator WorldHasBeenLoaded() {
   var fake = "WorldHasBeenRecieved = true; Helper.BroadCastToScene(5);";
   Helper.BroadCastToScene(7);
   if (ready) WorldHasBeenRecieved = true;
   yield return null;
 }
}
"""


class OriginalIlspyRepeatabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.a = Path(self.tmp.name) / "a"
        self.b = Path(self.tmp.name) / "b"
        self.a.mkdir()
        self.b.mkdir()
        self.write(self.a, BASE)
        self.write(self.b, BASE)

    @staticmethod
    def write(root, body):
        (root / "Raft_Network.cs").write_text(body, encoding="utf-8")

    def test_identical_source_and_body_repeats(self):
        report = compare_roots(self.a, self.b)
        self.assertTrue(report["class_sha_equal"])
        self.assertTrue(report["method_body_sha_equal"])
        self.assertTrue(report["masked_executable_body_sha_equal"])
        self.assertFalse(report["same_original_dll_proven_by_caller"])
        self.assertFalse(report["source_published"])

    def test_comment_diff_changes_class_but_not_method_body(self):
        self.write(self.b, "// generated metadata\n" + BASE)
        r = compare_roots(self.a, self.b)
        self.assertFalse(r["class_sha_equal"])
        self.assertTrue(r["method_body_sha_equal"])

    def test_string_literal_diff_can_change_body_but_not_masked_code(self):
        old_literal = '"WorldHasBeenRecieved = true; Helper.BroadCastToScene(5);"'
        replacement_literal = '"' + 'x' * (len(old_literal) - 2) + '"'
        self.assertEqual(len(old_literal), len(replacement_literal))
        self.write(self.b, BASE.replace(old_literal, replacement_literal))
        r = compare_roots(self.a, self.b)
        self.assertFalse(r["method_body_sha_equal"])
        self.assertTrue(r["masked_executable_body_sha_equal"])

    def test_executable_difference_is_detected(self):
        self.write(self.b, BASE.replace("Helper.BroadCastToScene(7)", "Helper.BroadCastToScene(8)"))
        r = compare_roots(self.a, self.b)
        self.assertFalse(r["method_body_sha_equal"])
        self.assertFalse(r["masked_executable_body_sha_equal"])

    def test_wrong_original_pair_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unrecognized"):
            compare_roots(self.a, self.b, allowed_pairs={("0" * 64, "1" * 64)})

    def test_duplicate_source_files_rejected(self):
        nest = self.b / "elsewhere"
        nest.mkdir()
        (nest / "Raft_Network.cs").write_text(BASE)
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            compare_roots(self.a, self.b)

    def test_missing_source_rejected(self):
        (self.b / "Raft_Network.cs").unlink()
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            compare_roots(self.a, self.b)

    def test_wrong_iterator_type_rejected(self):
        self.write(self.b, BASE.replace("IEnumerator WorldHasBeenLoaded", "void WorldHasBeenLoaded"))
        with self.assertRaisesRegex(ValueError, "return type"):
            source_profile(self.b)

    def test_comment_only_completion_does_not_pass(self):
        self.write(self.b, BASE.replace("if (ready) WorldHasBeenRecieved = true;",
            'if (ready) Other(); // WorldHasBeenRecieved = true;'))
        with self.assertRaisesRegex(ValueError, "Missing original scene"):
            source_profile(self.b)

    def test_comment_only_broadcast_does_not_pass(self):
        self.write(self.b, BASE.replace("Helper.BroadCastToScene(7);",
            "Other(); // Helper.BroadCastToScene(7);"))
        with self.assertRaisesRegex(ValueError, "Missing original scene"):
            source_profile(self.b)


if __name__ == "__main__":
    unittest.main()
