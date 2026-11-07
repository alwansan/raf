import unittest
from scripts.t3_dxbc_spirv_contract_join import check_contract

class JoinTests(unittest.TestCase):
    def setUp(self):
        self.dx = [{"stage":"vertex","family":"texture","register":3,"count":4}]
        self.spv = [{"stage":"vertex","family":"texture","set":2,"binding":9,"count":4}]
        self.mapping = [{"stage":"vertex","family":"texture","register":3,"set":2,"binding":9,"count":4}]

    def check(self, dx=None, spv=None, mapping=None):
        return check_contract(self.dx if dx is None else dx,
                              self.spv if spv is None else spv,
                              self.mapping if mapping is None else mapping)


    def test_malformed_numeric_reflection_fails_closed(self):
        for group_index, field in ((0, "register"), (0, "count"),
                                   (1, "set"), (1, "binding"), (1, "count"),
                                   (2, "register"), (2, "set"), (2, "binding"),
                                   (2, "count")):
            for invalid in ([], {}, None, True):
                groups = [[dict(x) for x in group]
                          for group in (self.dx, self.spv, self.mapping)]
                groups[group_index][0][field] = invalid
                with self.subTest(group=group_index, field=field, invalid=invalid):
                    expected = "invalid_count" if field == "count" else "invalid_coordinate"
                    self.assertEqual([expected], check_contract(*groups))

    def test_explicit_nonidentity_remap(self):
        self.assertEqual([], self.check())

    def test_no_provenance_even_if_numbers_match(self):
        spv = [dict(self.spv[0], set=0, binding=3)]
        self.assertIn("missing_or_extra_provenance", self.check(spv=spv, mapping=[]))

    def test_array_expansion_not_silent(self):
        self.assertIn("array_span_mismatch", self.check(spv=[dict(self.spv[0], count=1)]))

    def test_stage_is_not_interchangeable(self):
        self.assertIn("target_missing", self.check(spv=[dict(self.spv[0], stage="fragment")]))

    def test_unmapped_extra_descriptor(self):
        extra = dict(self.spv[0], binding=10)
        self.assertIn("unmapped_or_extra_descriptor", self.check(spv=self.spv+[extra]))

    def test_duplicate_target(self):
        duplicate = dict(self.mapping[0], register=4)
        self.assertIn("duplicate_target", self.check(mapping=self.mapping+[duplicate]))

    def test_invalid_zero_span(self):
        self.assertIn("invalid_count", self.check(dx=[dict(self.dx[0], count=0)]))

    def test_boolean_array_span_rejected(self):
        self.assertIn("invalid_count", self.check(dx=[dict(self.dx[0], count=True)]))

    def test_negative_dxbc_register_rejected(self):
        self.assertIn("invalid_coordinate", self.check(dx=[dict(self.dx[0], register=-1)]))

    def test_boolean_spv_binding_rejected(self):
        self.assertIn("invalid_coordinate", self.check(spv=[dict(self.spv[0], binding=False)]))

    def test_fractional_provenance_set_rejected(self):
        self.assertIn("invalid_coordinate", self.check(mapping=[dict(self.mapping[0], set=2.5)]))

    def test_negative_provenance_register_rejected(self):
        self.assertIn("invalid_coordinate", self.check(mapping=[dict(self.mapping[0], register=-3)]))

    def test_missing_dxbc_register_is_schema_error(self):
        self.assertEqual(["invalid_schema"], self.check(dx=[{"stage":"vertex","family":"texture","count":4}]))

    def test_missing_spirv_binding_is_schema_error(self):
        self.assertEqual(["invalid_schema"], self.check(spv=[{"stage":"vertex","family":"texture","set":2,"count":4}]))

    def test_missing_provenance_set_is_schema_error(self):
        self.assertEqual(["invalid_schema"], self.check(mapping=[{"stage":"vertex","family":"texture","register":3,"binding":9,"count":4}]))

    def test_non_mapping_record_is_schema_error(self):
        self.assertEqual(["invalid_schema"], self.check(dx=[None]))

if __name__ == "__main__":
    unittest.main()
