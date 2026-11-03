"""Synthetic-only cases for private original texture cache implementation probe."""
import tempfile
from pathlib import Path
import unittest
from scripts.probe_original_fft_cache_implementation import inspect_type, inspect_source_tree


CACHE = """
class RenderTexturesCache {
  // new RenderTexture(1,1,0,RenderTextureFormat.ARGBFloat);
  string x = "RenderTexture.GetTemporary(2,2)";
  RenderTexture GetCache(int w,int h,int depth,RenderTextureFormat format) {
     return new RenderTexture(w,h,depth,format);
  }
}
"""
SET = """
class RenderTexturesSet {
 void CreateTextures() {
   var a = new RenderTexture(64,64,0,RenderTextureFormat.RGHalf);
   a.enableRandomWrite = true;
   a.filterMode = FilterMode.Point;
   a.Create();
 }
}
"""


class FftCacheProvenanceTests(unittest.TestCase):
    def test_ignores_comment_and_string_allocators(self):
        r = inspect_type(CACHE, "RenderTexturesCache")
        self.assertEqual(r["get_cache_call_count"], 1)
        self.assertEqual(len(r["render_texture_allocations"]), 1)
        self.assertEqual(r["render_texture_allocations"][0]["argument_count"], 4)
        self.assertFalse(r["runtime_format_or_creation_proven"])
        self.assertNotIn("string x", str(r))

    def test_reports_concrete_format_and_random_write_without_guessing_runtime(self):
        r = inspect_type(SET, "RenderTexturesSet")
        self.assertEqual(r["enable_random_write_assignment_count"], 1)
        self.assertEqual(r["render_texture_create_call_count"], 1)
        self.assertEqual(r["filter_mode_assignment_count"], 1)
        self.assertEqual(r["render_texture_allocations"][0]["explicit_unity_format_tokens"][0]["public_enum"], "RGHalf")

    def test_tree_bounds_and_ambiguous_target_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/"Cache.cs").write_text(CACHE)
            (root/"Set.cs").write_text(SET)
            result = inspect_source_tree(root)
            self.assertEqual(result["source_files_examined"], 2)
            self.assertIsNotNone(result["type_reports"]["RenderTexturesCache"])
            (root/"Duplicate.cs").write_text(CACHE)
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                inspect_source_tree(root)

    def test_symlink_target_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/"Cache.cs").write_text(CACHE)
            (root/"bad.cs").symlink_to(root/"Cache.cs")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                inspect_source_tree(root)

    def test_hidden_private_format_enum_is_hashed(self):
        src = "class RenderTexturesCache { var x=new RenderTexture(1,2,3,RenderTextureFormat.PrivateSentinel); }"
        report = inspect_type(src, "RenderTexturesCache")
        self.assertIsNone(report["render_texture_allocations"][0]["explicit_unity_format_tokens"][0]["public_enum"])
        self.assertNotIn("PrivateSentinel", str(report))


if __name__ == "__main__":
    unittest.main()
