import tempfile
import unittest
from pathlib import Path

from scripts.normalize_csharp_namespaces import convert, process

class NamespaceCompatibilityTests(unittest.TestCase):
    def test_convert_file_scoped_to_block_scoped(self):
        src="using System;\n\nnamespace Unity.Collections;\npublic class Example {}\n"
        result, changed = convert(src)
        self.assertTrue(changed)
        self.assertIn("namespace Unity.Collections\n{\n", result)
        self.assertIn("public class Example {}",result)
        self.assertTrue(result.endswith("}\n"))
        self.assertNotIn("namespace Unity.Collections;",result)
    def test_preserves_existing_namespace(self):
        src="namespace Raft { public class Example {} }\n"
        self.assertEqual(convert(src),(src,False))
    def test_crlf(self):
        src="namespace Unity.Mathematics;\r\npublic struct float2 {}\r\n"
        new, changed = convert(src)
        self.assertTrue(changed)
        self.assertIn("\r\n{\r\n",new)
    def test_reject_multiple_scoped_namespaces(self):
        with self.assertRaises(ValueError):
            convert("namespace A;\nnamespace B;\nclass T {}")
    def test_ignores_comment(self):
        src="// namespace A;\nclass T {}\n"
        self.assertEqual(convert(src),(src,False))
    def test_keeps_cs_meta_identity_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"Sample.cs").write_text("namespace A;\npublic class Sample {}\n")
            meta=root/"Sample.cs.meta"
            original=b"fileFormatVersion: 2\nguid: c2788eeed0000cdef0001ca5c0001000\n"
            meta.write_bytes(original)
            report=process(root,True)
            self.assertEqual(report["converted"],1)
            self.assertEqual(meta.read_bytes(),original)
            self.assertFalse(process(root,False).get("converted",0))

if __name__=="__main__":
    unittest.main()
