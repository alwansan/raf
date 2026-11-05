import unittest
from scripts.t3_stream_extent_guard import validate_extents

class StreamExtentTests(unittest.TestCase):
    def test_exact_end(self):
        self.assertEqual(validate_extents({"p": 10}, [("p", 7, 3)])["extents"], 1)
    def test_missing_provider(self):
        with self.assertRaises(ValueError): validate_extents({"p": 10}, [("q", 0, 1)])
    def test_overrun(self):
        with self.assertRaises(ValueError): validate_extents({"p": 10}, [("p", 9, 2)])
    def test_negative(self):
        with self.assertRaises(ValueError): validate_extents({"p": 10}, [("p", -1, 1)])
    def test_zero(self):
        with self.assertRaises(ValueError): validate_extents({"p": 10}, [("p", 0, 0)])
    def test_bool_not_int(self):
        with self.assertRaises(ValueError): validate_extents({"p": 10}, [("p", True, 1)])
    def test_partial_overlap(self):
        self.assertEqual(validate_extents({"p": 20}, [("p", 1, 8), ("p", 7, 3)])["partial_overlaps"], 1)
    def test_shared_exact_range(self):
        self.assertEqual(validate_extents({"p": 20}, [("p", 1, 8), ("p", 1, 8)])["duplicate_ranges"], 1)
    def test_nested_exact_repeat_is_duplicate_not_second_overlap(self):
        result = validate_extents({"p": 30}, [
            ("p", 0, 20), ("p", 3, 5), ("p", 3, 5)
        ])
        self.assertEqual(result["partial_overlaps"], 1)
        self.assertEqual(result["duplicate_ranges"], 1)

    def test_nested_distinct_overlap(self):
        result = validate_extents({"p": 30}, [
            ("p", 0, 20), ("p", 3, 5), ("p", 4, 5)
        ])
        self.assertEqual(result["partial_overlaps"], 2)
        self.assertEqual(result["duplicate_ranges"], 0)

    def test_provider_separation(self):
        self.assertEqual(validate_extents({"a": 10, "b": 10}, [("a", 0, 4), ("b", 0, 4)])["partial_overlaps"], 0)

if __name__ == "__main__":
    unittest.main()
