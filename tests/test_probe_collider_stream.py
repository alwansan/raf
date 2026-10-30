import unittest
from scripts.probe_collider_stream import geometry_counts


class GeometryCountsTests(unittest.TestCase):
    def test_valid_triangle(self):
        self.assertTrue(geometry_counts([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)], 3)["valid"])

    def test_nonfinite_and_out_of_range_are_not_success(self):
        result = geometry_counts([(float("nan"), 0, 0), (float("inf"), 0, 0)], [(0, 1, 2)], 2)
        self.assertEqual(result["nonfinite_or_invalid_vertices"], 2)
        self.assertEqual(result["invalid_triangles"], 1)
        self.assertFalse(result["valid"])

    def test_empty_or_truncated_geometry_is_not_success(self):
        self.assertFalse(geometry_counts([], [], 0)["valid"])
        self.assertFalse(geometry_counts([(0, 0, 0)], [(0, 0, 0)], 3)["valid"])
