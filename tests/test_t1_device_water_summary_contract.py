import unittest
from scripts.t1_device_water_summary_contract import validate_bundle

S1 = "LogRaft-20261105-220911-559"
S2 = "LogRaft-20261105-230108-327"


def record(session):
    return dict(session=session, invalid_pass_total=3, invalid_kernel_total=2,
                invalid_pass_by_material={"spectrum": 1, "foam_global": 2},
                invalid_kernel_by_index={"index_6": 2, "other_index": 0},
                kernel_index_6_is_fft_proven=False,
                source_to_unity_kernel_mapping_proven=False,
                android_water_rendering_restored=False)


class TestContract(unittest.TestCase):
    def test_valid_pair(self):
        self.assertEqual(len(validate_bundle([record(S1), record(S2)], [S2, S1])["validated_sessions"]), 2)

    def test_duplicate(self):
        with self.assertRaises(ValueError): validate_bundle([record(S1), record(S1)], [S1])

    def test_missing(self):
        with self.assertRaises(ValueError): validate_bundle([record(S1)], [S1, S2])

    def test_bad_identifier(self):
        with self.assertRaises(ValueError): validate_bundle([record("../fake")], [S1])

    def test_forged_proof(self):
        r = record(S1); r["kernel_index_6_is_fft_proven"] = True
        with self.assertRaises(ValueError): validate_bundle([r], [S1])

    def test_boolean_count(self):
        r = record(S1); r["invalid_kernel_total"] = True
        with self.assertRaises(ValueError): validate_bundle([r], [S1])

    def test_inconsistent_count(self):
        r = record(S1); r["invalid_pass_total"] = 4
        with self.assertRaises(ValueError): validate_bundle([r], [S1])

    def test_empty(self):
        with self.assertRaises(ValueError): validate_bundle([], [S1])


if __name__ == "__main__":
    unittest.main()
