"""Synthetic controls only; not an original Foam shader or device test."""
import unittest
from scripts.t2_foam_alias_dataflow import (
    Value, NULL, UNKNOWN, fresh_value, join,
    same_instance_proven, different_instance_proven,
)

class AliasTests(unittest.TestCase):
    def test_same_ssa_value(self):
        v = fresh_value("unique-value-1")
        self.assertTrue(same_instance_proven(v, v))
        self.assertFalse(different_instance_proven(v, v))

    def test_different_allocations(self):
        a, b = fresh_value("allocation-A-instance"), fresh_value("allocation-B-instance")
        self.assertFalse(same_instance_proven(a, b))
        self.assertFalse(different_instance_proven(a, b))

    def test_distinct_ssa_tokens_can_alias_same_object(self):
        # Two independent loads from a field can return one RenderTexture.
        first_load = fresh_value("load-field-at-il-12")
        second_load = fresh_value("load-field-at-il-42")
        self.assertFalse(same_instance_proven(first_load, second_load))
        self.assertFalse(different_instance_proven(first_load, second_load))

    def test_branch_phi_distinct(self):
        a, b = fresh_value("a"), fresh_value("b")
        self.assertFalse(same_instance_proven(join(a, b), a))
        self.assertFalse(different_instance_proven(join(a, b), b))

    def test_branch_phi_same(self):
        a = fresh_value("a")
        self.assertTrue(same_instance_proven(join(a, a), a))

    def test_null_path(self):
        a = fresh_value("a")
        self.assertFalse(same_instance_proven(join(a, NULL), a))
        self.assertFalse(different_instance_proven(join(a, NULL), a))

    def test_unresolved_callee(self):
        a = fresh_value("a")
        self.assertFalse(same_instance_proven(join(a, UNKNOWN), a))
        self.assertFalse(same_instance_proven(UNKNOWN, UNKNOWN))

    def test_reassigned_field_same_name_not_identity(self):
        before, after = fresh_value("field-write-1"), fresh_value("field-write-2")
        self.assertFalse(same_instance_proven(before, after))

    def test_reused_allocation_site_not_same_runtime_instance(self):
        first, second = fresh_value("site0-invocation1"), fresh_value("site0-invocation2")
        self.assertFalse(same_instance_proven(first, second))

    def test_malformed(self):
        for invalid in (Value(frozenset(), unknown=True), None):
            if invalid is None:
                with self.assertRaises(ValueError):
                    same_instance_proven(invalid, NULL)
        with self.assertRaises(ValueError):
            join()
        with self.assertRaises(ValueError):
            fresh_value("")
        with self.assertRaises(ValueError):
            Value(frozenset(("a",)), may_be_null=1)

if __name__ == "__main__":
    unittest.main()
