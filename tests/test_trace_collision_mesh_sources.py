import tempfile
import unittest
from pathlib import Path
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

    def test_lfs_priorities_come_from_pointer_size_not_guessed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"sharedassets24.assets.resS").write_text(
                "version https://git-lfs.github.com/spec/v1\n"
                "oid sha256:" + "a"*64 + "\nsize 104857600\n", encoding="ascii")
            (root/"sharedassets35.assets.resS").write_text(
                "version https://git-lfs.github.com/spec/v1\n"
                "oid sha256:" + "b"*64 + "\nsize 419430400\n", encoding="ascii")
            rows = {
                "First": [{"source": "sharedassets24.assets", "stream_status": "lfs-pointer",
                           "stream_file": "sharedassets24.assets.resS"}],
                "Second": [{"source": "sharedassets35.assets", "stream_status": "lfs-pointer",
                            "stream_file": "sharedassets35.assets.resS"}]
            }
            result=summary(Counter({"First": 7,"Second": 20}), rows,
                           {"skipped_lfs_header_files":[],"parse_errors":{}}, root)
            priorities=result["stream_lfs_priorities"]
            self.assertEqual(priorities[0]["stream"], "sharedassets24.assets.resS")
            self.assertEqual(priorities[0]["lfs_declared_bytes"], 104857600)
            self.assertEqual(priorities[0]["distinct_names_per_100_MiB"], 1.0)
            self.assertEqual(priorities[1]["distinct_names_per_100_MiB"], 0.25)

    def test_no_errors_is_not_pretended_success(self):
        with self.assertRaises(ValueError):
            summary(Counter(), {}, {"skipped_lfs_header_files": [], "parse_errors": {}})


if __name__ == "__main__":
    unittest.main()
