import unittest
from scripts.t4_filemanager_declaration_shapes import classify

class TestDeclarationShapes(unittest.TestCase):
    def test_block(self):
        r = classify("public class FileManager {\\n public static Stream Open(string p) { return null; }\\n}", "Open")
        self.assertEqual(r["block_candidate"], 1)
        self.assertFalse(r["runtime_callability_proven"])

    def test_expression(self):
        r = classify("public static Stream Open(string p) => File.OpenRead(p);", "Open")
        self.assertEqual(r["expression_candidate"], 1)

    def test_multiline_return(self):
        r = classify("public static Dictionary<string, List<int>>\\n Open(string p) { return null; }", "Open")
        self.assertEqual(r["block_candidate"], 1)

    def test_call_not_declaration(self):
        r = classify("public void F() { var x = Open(p); }", "Open")
        self.assertEqual(r["call_like_token"], 1)
        self.assertEqual(r["block_candidate"], 0)

    def test_comment_masked(self):
        r = classify("public class F { // public static Stream Open(string p) {}\\n }", "Open")
        self.assertEqual(r["block_candidate"], 0)

    def test_invalid_target(self):
        with self.assertRaises(ValueError): classify("public void F() {}", "F();evil")

    def test_abstract_declaration_unresolved(self):
        r = classify("public abstract Stream Open(string p);", "Open")
        self.assertEqual(r["declaration_unresolved"], 1)

    def test_never_proves_absence(self):
        r = classify("public class FileManager {}", "Open")
        self.assertFalse(r["target_absence_proven"])

if __name__ == "__main__": unittest.main()
