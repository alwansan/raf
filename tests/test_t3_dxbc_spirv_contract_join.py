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

if __name__ == "__main__":
    unittest.main()
