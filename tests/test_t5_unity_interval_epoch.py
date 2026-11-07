import unittest
import tempfile
from pathlib import Path
from scripts.t5_unity_interval_epoch import analyze_rows, parse_detail, load

def sample(scene="MainScene", refresh=120, frames=40, fps=24, p95=60, width=2400):
    return {"area":"performance", "operation":"sample",
            "detail":f"scene={scene};refresh_hz={refresh};frame_samples={frames};fps={fps};frame_p50_ms=30;frame_p95_ms={p95};width={width};height=1080"}

class EpochTests(unittest.TestCase):
    def test_scene_and_refresh_split_even_when_revisited(self):
        result=analyze_rows([sample(),sample(fps=30),sample("MainMenuScene"),
                             sample("MainMenuScene",60),sample()])
        self.assertEqual(len(result["epochs"]),4)
        self.assertEqual(result["epochs"][0]["median_interval_fps"],27)
        self.assertEqual(result["epochs"][3]["qualified_intervals"],1)
    def test_startup_excluded_and_p95_labeled(self):
        result=analyze_rows([sample(frames=2,fps=120),sample(fps=20,p95=70)])
        epoch=result["epochs"][0]
        self.assertEqual(epoch["startup_excluded"],1)
        self.assertEqual(epoch["median_interval_fps"],20)
        self.assertIn("not pooled",result["frame_p95_semantics"])
    def test_duplicate_detail_rejected(self):
        with self.assertRaises(ValueError): parse_detail("scene=a;scene=b")
    def test_nan_rejected(self):
        with self.assertRaises(ValueError): analyze_rows([sample(fps="nan")])
    def test_missing_scene_rejected(self):
        with self.assertRaises(ValueError): analyze_rows([{"area":"performance","operation":"sample","detail":"fps=10"}])
    def test_other_area_ignored(self):
        self.assertEqual(analyze_rows([{"area":"scene","operation":"sample"}])["performance_intervals"],0)
    def test_duplicate_jsonl_top_level_key_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "perf.jsonl"
            path.write_text('{"area":"performance","area":"scene","operation":"sample"}' + chr(10), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSONL key"):
                load(path)

    def test_duplicate_jsonl_nested_key_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "perf.jsonl"
            path.write_text('{"area":"scene","extra":{"fps":20,"fps":100}}' + chr(10), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSONL key"):
                load(path)

    def test_distinct_jsonl_keys_still_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "perf.jsonl"
            path.write_text('{"area":"scene","operation":"sample"}' + chr(10), encoding="utf-8")
            self.assertEqual(len(load(path)), 1)

    def test_resolution_change_is_epoch(self):
        self.assertEqual(len(analyze_rows([sample(),sample(width=1920)])["epochs"]),2)

if __name__=="__main__":
    unittest.main()
