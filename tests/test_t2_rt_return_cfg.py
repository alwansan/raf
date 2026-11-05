"""Synthetic adversarial checks only; not original Unity evidence."""
import unittest
from scripts.t2_rt_return_cfg import classify

class ProvenanceTests(unittest.TestCase):
    def test_null_local(self):
        self.assertEqual(classify([("ldnull",),("stloc",0),("ldloc",0),("ret",)]),"null")
    def test_constructed_local(self):
        self.assertEqual(classify([("newobj_rt",),("stloc",2),("ldloc",2),("ret",)]),"constructed")
    def test_branch_agreement(self):
        self.assertEqual(classify([("ldcond",),("brtrue",4),("ldnull",),("br",5),("ldnull",),("ret",)]),"null")
    def test_branch_disagreement(self):
        self.assertEqual(classify([("ldcond",),("brtrue",4),("ldnull",),("br",5),("newobj_rt",),("ret",)]),"unknown")
    def test_unsupported(self):
        self.assertEqual(classify([("call_external",),("ret",)]),"unknown")
    def test_loop(self):
        self.assertEqual(classify([("br",0)],max_states=20),"unknown")
    def test_invalid_jump(self):
        self.assertEqual(classify([("br",5)]),"unknown")
    def test_mismatched_join_height_cannot_be_erased_by_store(self):
        # Both paths have a value for stloc, but one carries an extra
        # stack item. A later constructed RT must not mask invalid CIL.
        il = [
            ("ldcond",), ("brtrue", 5),
            ("ldnull",), ("ldnull",), ("br", 7),
            ("ldnull",), ("br", 7),
            ("stloc", 0), ("newobj_rt",), ("ret",),
        ]
        self.assertEqual(classify(il), "unknown")

    def test_huge_local_index_fails_closed(self):
        # A malformed IL local operand must not allocate billions of entries.
        self.assertEqual(classify([("ldnull",), ("stloc", 10**9), ("ldnull",), ("ret",)]), "unknown")
        self.assertEqual(classify([("ldloc", 10**9), ("ret",)]), "unknown")

    def test_local_limit_boundary(self):
        self.assertEqual(classify([("newobj_rt",), ("stloc", 3), ("ldloc", 3), ("ret",)], max_locals=4), "constructed")
        self.assertEqual(classify([("newobj_rt",), ("stloc", 4), ("ret",)], max_locals=4), "unknown")
        self.assertEqual(classify([("ldnull",), ("stloc", True), ("ret",)]), "unknown")

    def test_uninitialized(self):
        self.assertEqual(classify([("ldloc",0),("ret",)]),"unknown")

if __name__ == "__main__":
    unittest.main()
