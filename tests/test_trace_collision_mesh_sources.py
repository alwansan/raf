import unittest
from collections import Counter

from scripts.trace_collision_mesh_sources import failing_meshes, summary


class ColliderHeaderTraceTests(unittest.TestCase):
    def test_extract_mesh_names_without_leaking_coordinates(self):
        log = """
Failed extracting collision mesh because vertex at index 2 contains a non-finite value (nan, 0, 0). Mesh asset path "Assets/Mesh/BigRock3.asset" Mesh name "BigRock3"
Failed extracting collision mesh because vertex at index 2 contains a non-finite value (nan, 0, 0). Mesh asset path "Assets/Mesh/BigRock3.asset" Mesh name "BigRock3"
Failed extracting collision mesh because vertex at index 5 contains a non-finite value (0, nan, 0). Mesh asset path "Assets/Mesh/Ramp_2.asset" Mesh name "Ramp_2"
"""
        self.assertEqual(failing_meshes(log), Counter({"BigRock3": 2, "Ramp_2": 1}))

    def test_missing_and_ambiguous_counts_do_not_assert_data_loss(self):
        rows = {"BigRock3": [
            {"source": "sharedassets29.assets", "stream_status": "lfs-pointer"},
            {"source": "sharedassets30.assets", "stream_status": "available-range"}],
            "Ramp_2": [{"source": "sharedassets24.assets", "stream_status": "lfs-pointer"}]}
        report = summary(Counter({"BigRock3": 10, "Ramp_2": 1, "Missing": 7}), rows,
                         {"skipped_lfs_header_files": ["resources.assets"],
                          "parse_errors": {}})
        self.assertEqual(report["failure_log_lines"], 18)
        self.assertEqual(report["distinct_failed_names"], 3)
        self.assertEqual(report["matched_distinct_names"], 2)
        self.assertEqual(report["unmatched_distinct_names"], 1)
        self.assertEqual(report["ambiguous_names"], 1)
        self.assertEqual(report["matched_stream_status"]["lfs-pointer"], 2)
        self.assertEqual(report["skipped_lfs_original_header_count"], 1)

    def test_no_errors_is_not_pretended_success(self):
        with self.assertRaises(ValueError):
            summary(Counter(), {}, {"skipped_lfs_header_files": [], "parse_errors": {}})


if __name__ == "__main__":
    unittest.main()
