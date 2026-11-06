import unittest
from scripts.t3_semantic_location_uniqueness import unique_bijection


class TestUniqueBijection(unittest.TestCase):
    def test_unique_permuted(self):
        self.assertEqual(unique_bijection({3: {7}, 1: {9}}), {1: 9, 3: 7})

    def test_duplicate_types_ambiguous(self):
        self.assertIsNone(unique_bijection({0: {2, 3}, 1: {2, 3}}))

    def test_hall_violation(self):
        self.assertIsNone(unique_bijection({0: {2}, 1: {2}, 3: {3, 4}}))

    def test_forced_unique_with_overlapping_candidates(self):
        self.assertEqual(unique_bijection({0: {2, 3}, 1: {3}}), {0: 2, 1: 3})

    def test_invalid_bool_and_out_of_range(self):
        for edges in ({True: {1}}, {0: {False}}, {65536: {0}}, {0: {-1}}):
            with self.assertRaises(ValueError):
                unique_bijection(edges)

    def test_unbalanced_domain(self):
        self.assertIsNone(unique_bijection({0: {1, 2}}))

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            unique_bijection({})


if __name__ == '__main__':
    unittest.main()
