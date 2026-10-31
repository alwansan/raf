import unittest
from scripts.build_mesh_range_manifest import merged_chunks


class MeshRangeManifestTests(unittest.TestCase):
    def test_overlap_adjacent_and_duplicate_ranges_are_not_downloaded_twice(self):
        self.assertEqual(merged_chunks([(10, 10), (15, 10), (10, 10), (25, 5), (40, 2)]),
                         [(10, 20), (40, 2)])

    def test_large_union_is_split_without_holes_or_extra_bytes(self):
        self.assertEqual(merged_chunks([(5, 15)], maximum=4), [(5, 4), (9, 4), (13, 4), (17, 3)])

    def test_invalid_ranges_are_refused(self):
        for value in [(-1, 4), (0, 0), (0, -1), (False, 3)]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                merged_chunks([value])
