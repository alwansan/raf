"""A4 owner->cache source probe adversarial fixtures; no original game code."""
from pathlib import Path
import tempfile
import unittest

from scripts.a4_gpu_cache_owner_callpaths import inspect_owner_source, inspect_root

OWNER = """class WavesRendererFFT {
    private RenderTexturesCache cache;
    private void Construct() { cache = new RenderTexturesCache(); }
    private void OnDisable() { cache.Release(); }
    private void OnDestroy() { /* cache.Release(); */ }
    private void Update() { string note = "cache.Dispose();"; }
}
"""


class OriginalGpuCacheOwnerTests(unittest.TestCase):
    def test_captures_typed_cache_release_in_lifecycle(self):
        data = inspect_owner_source(OWNER, "WavesRendererFFT")
        self.assertEqual(data["typed_cache_fields_detected"], 1)
        disable = next(x for x in data["structural_relevant_methods"]
                       if x["name_category"] == "OnDisable")
        self.assertEqual(disable["calls"]["release"], 1)
        self.assertTrue(disable["typed_cache_field_release_call"])
        destroy = next(x for x in data["structural_relevant_methods"]
                       if x["name_category"] == "OnDestroy")
        self.assertNotIn("release", destroy["calls"])
        self.assertFalse(destroy["typed_cache_field_release_call"])
        self.assertFalse(data["resolved_cleanup_reachability"])

    def test_only_lifecycle_vocabulary_not_original_method_text_emitted(self):
        renamed = OWNER.replace("Construct", "SecretMethodFromOriginalGame")
        data = inspect_owner_source(renamed, "WavesRendererFFT")
        self.assertNotIn("SecretMethodFromOriginalGame", str(data))
        self.assertNotIn("private RenderTexturesCache cache", str(data))
        self.assertIn("OnDisable", str(data))

    def test_no_claim_of_cleanup_on_same_spelling_in_comment_or_string(self):
        changed = OWNER.replace("cache.Release(); }\n    private void OnDestroy",
                                'string token = "cache.Release();"; }\n    private void OnDestroy')
        data = inspect_owner_source(changed, "WavesRendererFFT")
        disable = next(x for x in data["structural_relevant_methods"]
                       if x["name_category"] == "OnDisable")
        self.assertNotIn("release", disable["calls"])
        self.assertFalse(disable["typed_cache_field_release_call"])

    def test_missing_type_and_unsafe_source_root_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "type"):
            inspect_owner_source(OWNER.replace("WavesRendererFFT", "Other"), "WavesRendererFFT")
        with self.assertRaisesRegex(ValueError, "Unknown"):
            inspect_owner_source(OWNER, "PrivateUnknownType")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "Required"):
                inspect_root(root)

    def test_no_invented_device_release_or_water_readiness(self):
        data = inspect_owner_source(OWNER, "WavesRendererFFT")
        self.assertFalse(data["original_runtime_or_android_gpu_executed"])
        self.assertFalse(data["resolved_cleanup_reachability"])
        self.assertFalse(data["original_source_text_disclosed"])


if __name__ == "__main__":
    unittest.main()
