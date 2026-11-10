"""Regression checks for the source-free T2 original-operand gate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t2_foam_original_operand_gate import classify_original_operand_rhs as check


class OriginalOperandGateTests(unittest.TestCase):
    def test_unverified_local_arg_rejected(self):
        for op in ("ldloc", "ldarg", "ldloc.s", "ldarg.s"):
            with self.subTest(op=op):
                self.assertEqual("UNKNOWN", check([op], complete_slice=True))

    def test_verified_local_arg_categorized(self):
        for op, result in (("ldloc", "LOCAL_READ"),
                           ("ldloc.s", "LOCAL_READ"),
                           ("ldarg", "ARGUMENT_READ"),
                           ("ldarg.s", "ARGUMENT_READ")):
            with self.subTest(op=op):
                self.assertEqual(result, check([op], complete_slice=True,
                                               operand_verified=True))

    def test_short_forms_do_not_need_operand_flag(self):
        for op in ("ldloc.0", "ldloc.3", "ldarg.0", "ldarg.3"):
            with self.subTest(op=op):
                self.assertNotEqual("UNKNOWN", check([op], complete_slice=True))

    def test_incomplete_and_multiple_producers_rejected(self):
        self.assertEqual("UNKNOWN", check(["ldloc.0"]))
        self.assertEqual("UNKNOWN", check(["ldloc.0", "ldarg.1"],
                                          complete_slice=True))
        self.assertEqual("UNKNOWN", check(["ldloc.s", "ldarg.0"],
                                          complete_slice=True,
                                          operand_verified=True))

    def test_unknown_and_nonboolean_flags_rejected(self):
        self.assertEqual("UNKNOWN", check(["ldloc.0", "dup"],
                                          complete_slice=True))
        self.assertEqual("UNKNOWN", check(["ldloc.0"],
                                          complete_slice=1))
        self.assertEqual("UNKNOWN", check(["ldloc.s"],
                                          complete_slice=True,
                                          operand_verified=1))

    def test_call_and_field_require_other_evidence(self):
        self.assertEqual("UNKNOWN", check(["call"], complete_slice=True))
        self.assertEqual("CALL_RESULT", check(["call"],
                                             complete_slice=True,
                                             call_returns_value=True))
        self.assertEqual("UNKNOWN", check(["ldfld"], complete_slice=True))
        self.assertEqual("FIELD_READ", check(["ldfld"],
                                            complete_slice=True,
                                            receiver_verified=True))


if __name__ == "__main__":
    unittest.main()
