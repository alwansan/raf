"""Synthetic, source-free negative controls for Foam RHS classifier."""
import unittest
from scripts.t2_foam_rhs_origin_guard import classify_rhs


class FoamRhsOriginGuardTests(unittest.TestCase):
    def test_single_producers(self):
        for op, expected in [
            ("ldnull", "NULL"), ("newobj", "CONSTRUCTOR"),
            ("ldfld", "FIELD_READ"), ("ldsfld", "STATIC_FIELD_READ"),
            ("call", "CALL_RESULT"), ("callvirt", "CALL_RESULT"),
            ("ldloc", "LOCAL_READ"), ("ldarg", "ARGUMENT_READ")
        ]:
            with self.subTest(op=op):
                self.assertEqual(classify_rhs(["nop", op, "castclass"],\n                                              call_returns_value=(op in {"call", "callvirt"})), expected)

    def test_ambiguous_or_control_flow_fails_closed(self):
        for ops in [
            [], ["newobj", "newobj"], ["ldloc", "call"],
            ["br.s", "newobj"], ["switch", "ldfld"],
            ["ldnull", "ret"], ["ldfld", "stfld"],
            ["ldloc.0"], ["ldc.i4.0"], ["ldfld", "pop"],
            ["call", "throw"], ["newobj", "leave.s"],
            ["newobj", "beq.s"], ["newobj", "unknown"],
            ["dup", "newobj"], ["newobj", "dup"],
            ["castclass", "newobj"], ["castclass", "ldfld"],
            ["nop", "castclass", "ldnull"],
            [None], "newobj"
        ]:
            with self.subTest(ops=ops):
                self.assertEqual(classify_rhs(ops), "UNKNOWN")

    def test_calls_require_original_nonvoid_signature(self):
        for opcode in ("call", "callvirt"):
            with self.subTest(opcode=opcode):
                self.assertEqual(classify_rhs([opcode]), "UNKNOWN")
                self.assertEqual(classify_rhs([opcode], call_returns_value=False), "UNKNOWN")
                self.assertEqual(classify_rhs([opcode], call_returns_value=True), "CALL_RESULT")
                self.assertEqual(classify_rhs([opcode], call_returns_value="yes"), "UNKNOWN")
        # A void call followed by a field read is not an RHS producer slice.
        self.assertEqual(classify_rhs(["call", "ldfld"], call_returns_value=True), "UNKNOWN")

    def test_post_producer_cast_is_allowed_without_identity_proof(self):
        self.assertEqual(classify_rhs(["nop", "ldfld", "castclass", "nop"]), "FIELD_READ")

    def test_no_object_identity_claim(self):
        # Two distinct SSA reads can alias the same runtime Texture.
        self.assertEqual(classify_rhs(["ldfld"]), "FIELD_READ")
        self.assertEqual(classify_rhs(["ldfld"]), "FIELD_READ")
        # Category equality must never be interpreted as instance equality.


if __name__ == "__main__":
    unittest.main()
