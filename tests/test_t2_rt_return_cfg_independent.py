"""Independent, source-free branch/return safety controls for T2's CFG prototype.

These are synthetic instruction fixtures. They do not load Raft assemblies or
prove original Foam dataflow, Unity texture allocation, or Android rendering.
"""
import unittest

from scripts.t2_rt_return_cfg import classify


class IndependentCfgControls(unittest.TestCase):
    def test_conflicting_branch_local_assignments_fail_closed(self):
        il = [
            ("ldcond",), ("brtrue", 5),
            ("ldnull",), ("stloc", 0), ("br", 7),
            ("newobj_rt",), ("stloc", 0),
            ("ldloc", 0), ("ret",),
        ]
        self.assertEqual(classify(il), "unknown")

    def test_agreeing_constructed_branch_local_assignments(self):
        il = [
            ("ldcond",), ("brtrue", 5),
            ("newobj_rt",), ("stloc", 0), ("br", 7),
            ("newobj_rt",), ("stloc", 0),
            ("ldloc", 0), ("ret",),
        ]
        self.assertEqual(classify(il), "constructed")

    def test_disagreeing_multiple_return_sites_fail_closed(self):
        il = [
            ("ldcond",), ("brtrue", 4),
            ("ldnull",), ("ret",),
            ("newobj_rt",), ("ret",),
        ]
        self.assertEqual(classify(il), "unknown")

    def test_agreeing_multiple_return_sites(self):
        il = [
            ("ldcond",), ("brtrue", 4),
            ("ldnull",), ("ret",),
            ("ldnull",), ("ret",),
        ]
        self.assertEqual(classify(il), "null")

    def test_invalid_numeric_and_boolean_branch_operands(self):
        for bad in (-1, 99, 1.0, True, False, None):
            with self.subTest(target=repr(bad)):
                self.assertEqual(classify([("br", bad), ("ldnull",), ("ret",)]), "unknown")

    def test_invalid_local_operand_types_never_alias_valid_index(self):
        for bad in (-1, 2.0, "2", True, False, 10**9):
            with self.subTest(local=repr(bad)):
                self.assertEqual(
                    classify([("newobj_rt",), ("stloc", bad), ("ldloc", 0), ("ret",)]),
                    "unknown",
                )

    def test_unreachable_invalid_opcode_does_not_change_reachable_return(self):
        self.assertEqual(
            classify([("ldnull",), ("ret",), ("unsupported_unreachable",)]),
            "null",
        )

    def test_return_requires_exactly_one_stack_value(self):
        self.assertEqual(classify([("ret",)]), "unknown")
        self.assertEqual(classify([("ldnull",), ("ldnull",), ("ret",)]), "unknown")

    def test_low_execution_budget_is_not_a_positive_proof(self):
        il = [("newobj_rt",), ("ret",)]
        self.assertEqual(classify(il, max_states=1), "unknown")
        self.assertEqual(classify(il, max_states=2), "constructed")

    def test_nop_prefix_metamorphic_equivalence(self):
        original = [("ldnull",), ("stloc", 0), ("ldloc", 0), ("ret",)]
        self.assertEqual(classify(original), "null")
        self.assertEqual(classify([("nop",)] + original), classify(original))


if __name__ == "__main__":
    unittest.main()
