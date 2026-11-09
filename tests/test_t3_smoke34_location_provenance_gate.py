import unittest
from scripts.t3_smoke34_location_provenance_gate import validate


class ProvenanceGateTests(unittest.TestCase):
    def setUp(self):
        self.o = [("opaque0", 0), ("opaque0", 1)]
        self.r = [(3, 0), (3, 1)]
        self.m = [("opaque0", 0, 3, 0), ("opaque0", 1, 3, 1)]

    def test_structural_only_not_ready(self):
        self.assertEqual(validate(self.o, self.r, self.m)["status"], "STRUCTURAL_BIJECTION_ONLY")

    def test_missing_mapping(self):
        self.assertEqual(validate(self.o, self.r, [])["reason"], "missing_provenance")

    def test_ambiguous_mapping(self):
        bad = [self.m[0], self.m[0]]
        self.assertEqual(validate(self.o, self.r, bad)["reason"], "source_mismatch_or_ambiguous")

    def test_wrong_location(self):
        bad = [self.m[0], ("opaque0", 1, 5, 1)]
        self.assertEqual(validate(self.o, self.r, bad)["reason"], "location_mismatch_or_ambiguous")

    def test_missing_used_lane(self):
        self.assertEqual(validate(self.o, self.r, self.m[:1])["reason"], "incomplete_coverage")

    def test_duplicate_source(self):
        self.assertEqual(validate(self.o + self.o[:1], self.r, self.m)["reason"], "duplicate_source_lane")

    def test_reject_boolean_location(self):
        self.assertEqual(validate(self.o, [(True, 0)], self.m)["reason"], "invalid_input")

    def test_reject_malformed(self):
        self.assertEqual(validate(self.o, self.r, [["oops"]])["status"], "INCONCLUSIVE")

    def test_no_private_ids_in_output(self):
        self.assertNotIn("opaque0", str(validate(self.o, self.r, self.m)))


if __name__ == "__main__":
    unittest.main()
