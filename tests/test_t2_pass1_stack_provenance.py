"""Source-free controls for bounded pass-1 IL producer model."""
import unittest
from scripts.t2_pass1_stack_provenance import trace, Unresolved, Value

class Pass1StackTests(unittest.TestCase):
    def test_direct_render_texture(self):
        self.assertEqual(trace([("ldarg", (0, "RenderTexture"))]), (Value("RenderTexture", "arg:0"),))
    def test_local_copy_preserves_origin(self):
        self.assertEqual(trace([("ldarg", (1, "Texture")), ("stloc", 2), ("ldloc", 2)]), (Value("Texture", "arg:1"),))
    def test_dup_preserves_origin(self):
        self.assertEqual(trace([("ldarg", (0, "Texture")), ("dup", None)])[0], trace([("ldarg", (0, "Texture"))])[0])
    def test_null(self):
        self.assertEqual(trace([("ldnull", None)]), (Value("NULL", "null"),))
    def test_branch_rejected(self):
        with self.assertRaises(Unresolved): trace([("br.s", 2)])
    def test_callvirt_rejected(self):
        with self.assertRaises(Unresolved): trace([("callvirt", "GetTexture")])
    def test_field_alias_rejected(self):
        with self.assertRaises(Unresolved): trace([("ldfld", "source")])
    def test_uninitialized_local(self):
        with self.assertRaises(Unresolved): trace([("ldloc", 0)])
    def test_underflow(self):
        with self.assertRaises(Unresolved): trace([("dup", None)])
    def test_budget(self):
        with self.assertRaises(Unresolved): trace([("ldnull", None)] * 129)
    def test_bad_type(self):
        with self.assertRaises(Unresolved): trace([("ldarg", (0, "Unknown"))])
    def test_bad_shape(self):
        with self.assertRaises(Unresolved): trace([("ldarg",)])
if __name__ == "__main__":
    unittest.main()
