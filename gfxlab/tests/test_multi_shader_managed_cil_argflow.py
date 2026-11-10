"""GFX-MULTI-045 synthetic-only straight-line IL argument stack tests."""
import unittest
from gfxlab.tools.multi_shader_managed_cil_argflow import _interpret, parse_member_signature

P = {"_SyntheticBase", "_SyntheticNormal"}
B = {"_SyntheticNormal"}
M = ("Material", "SetTexture", 2, True, "string", "void")
MI = ("Material", "SetTexture", 2, True, "i4", "void")
PTID = ("Shader", "PropertyToID", 1, False, "string", "i4")

class TestCILFlow(unittest.TestCase):
    def test_direct_name_to_first_argument(self):
        r = _interpret([("ldarg.0", None), ("ldstr", "_SyntheticNormal"),
                        ("ldarg.1", None), ("callvirt", M), ("ret", None)], P, B)
        self.assertTrue(r["eligible"])
        self.assertEqual(r["direct"], {"_SyntheticNormal"})
        self.assertEqual(r["bound"], {"_SyntheticNormal"})
        self.assertEqual(r["verified_calls"], 1)

    def test_true_property_to_id_flow(self):
        r = _interpret([("ldarg.0", None), ("ldstr", "_SyntheticBase"),
                        ("call", PTID), ("ldarg.1", None),
                        ("callvirt", MI)], P, B)
        self.assertEqual(r["id"], {"_SyntheticBase"})
        self.assertEqual(r["verified_calls"], 1)

    def test_wrong_stack_argument_does_not_verify_adjacency(self):
        r = _interpret([("ldarg.0", None), ("ldstr", "_SyntheticBase"),
                        ("pop", None), ("ldstr", "_SomeoneElse"),
                        ("ldarg.1", None), ("callvirt", M)], P, B)
        self.assertTrue(r["eligible"])
        self.assertEqual(r["verified_calls"], 0)

    def test_wrong_overload_does_not_verify_property_marker(self):
        r = _interpret([("ldarg.0", None), ("ldstr", "_SyntheticBase"),
                        ("ldarg.1", None), ("callvirt", MI)], P, B)
        self.assertEqual(r["verified_calls"], 0)

    def test_branch_poison_even_when_literal_call_adjacent(self):
        r = _interpret([("ldarg.0", None), ("ldstr", "_SyntheticBase"),
                        ("ldarg.1", None), ("callvirt", M),
                        ("br.s", None)], P, B)
        self.assertFalse(r["eligible"])
        self.assertEqual(r["verified_calls"], 0)

    def test_unsupported_opcode_poison_even_after_valid_call(self):
        r = _interpret([("ldarg.0", None), ("ldstr", "_SyntheticBase"),
                        ("ldarg.1", None), ("callvirt", M),
                        ("stobj", None)], P, B)
        self.assertFalse(r["eligible"])
        self.assertEqual(r["direct"], set())

    def test_unresolved_call_poison(self):
        r = _interpret([("ldstr", "_SyntheticBase"),
                        ("call", None)], P, B)
        self.assertFalse(r["eligible"])

    def test_local_roundtrip_and_wrong_property(self):
        a = _interpret([("ldstr", "_SyntheticBase"), ("stloc.0", None),
                        ("ldarg.0", None), ("ldloc.0", None),
                        ("ldarg.1", None), ("callvirt", M)], P, B)
        self.assertEqual(a["direct"], {"_SyntheticBase"})
        b = _interpret([("ldarg.0", None), ("ldstr", "_NotSource"),
                        ("ldarg.1", None), ("callvirt", M)], P, B)
        self.assertEqual(b["verified_calls"], 0)

    def test_invalid_callvirt_receiver_fails_closed(self):
        a = _interpret([("ldstr", "_SyntheticBase"), ("ldarg.1", None),
                        ("callvirt", M)], P, B)
        self.assertFalse(a["eligible"])
        self.assertEqual(a["verified_calls"], 0)

    def test_signature_methodref_exactness(self):
        # static Shader.PropertyToID(string) -> i4
        self.assertEqual(parse_member_signature(bytes([0, 1, 8, 14])),
                         (1, False, "string", "i4"))
        # instance Material.SetTexture(string, class Texture) -> void
        self.assertEqual(parse_member_signature(bytes([0x20, 2, 1, 14, 0x12, 1])),
                         (2, True, "string", "void"))
        self.assertIsNone(parse_member_signature(bytes([0x20, 2, 1, 14])))
        self.assertIsNone(parse_member_signature(bytes([0x10, 1, 1, 14])))

if __name__ == "__main__":
    unittest.main()
