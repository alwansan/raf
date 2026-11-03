"""Original GPU cache lifecycle analyzer synthetic controls; no game source."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.a4_original_gpu_cache_lifecycle import inspect_source, inspect_root


FIXTURE = """class RenderTexturesCache {
    private RenderTexture cached;
    public void Allocate() {
        // string fake = "tex.Release();";
        cached = new RenderTexture(32, 32, 0, fmt, RenderTextureReadWrite.Linear);
        cached.Create();
    }
    public void Dispose() {
        try { Update(); }
        finally { cached.Release(); }
    }
}
"""


def verified(source):
    return inspect_source(source, hashlib.sha256(source.encode("utf-8")).hexdigest())


class OriginalGpuCacheLifecycleTests(unittest.TestCase):
    def test_real_allocator_and_finally_release_are_distinguished(self):
        result = verified(FIXTURE)
        self.assertEqual(result["aggregate_operations"]["gpu_ctor"], 1)
        self.assertEqual(result["aggregate_operations"]["gpu_create"], 1)
        self.assertEqual(result["aggregate_operations"]["gpu_release"], 1)
        self.assertTrue(any(x["api"] == "Dispose" and x["release_inside_finally_seen"]
                            for x in result["bounded_relevant_methods"]))
        self.assertFalse(result["exception_safe_cleanup_or_leak_proven"])
        self.assertFalse(result["game_gpu_allocation_runtime_or_phone_verified"])

    def test_comment_and_literal_fake_release_are_not_counted(self):
        changed = FIXTURE.replace("finally { cached.Release(); }",
                                  'finally { var fake = "cached.Release();"; /* x.Release(); */ }')
        result = verified(changed)
        self.assertEqual(result["aggregate_operations"]["gpu_release"], 0)
        self.assertFalse(any(x["release_inside_finally_seen"]
                             for x in result["bounded_relevant_methods"]))

    def test_missing_release_fails_as_unverified_not_claimed_leak(self):
        changed = FIXTURE.replace("finally { cached.Release(); }", "finally { Update(); }")
        result = verified(changed)
        self.assertEqual(result["aggregate_operations"]["gpu_release"], 0)
        self.assertFalse(result["exception_safe_cleanup_or_leak_proven"])
        self.assertFalse(result["build_ready"])

    def test_sha_mismatch_or_missing_original_class_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            inspect_source(FIXTURE, "0" * 64)
        with self.assertRaisesRegex(ValueError, "identity"):
            verified(FIXTURE.replace("RenderTexturesCache", "OtherType"))
        with self.assertRaisesRegex(ValueError, "allocator"):
            verified(FIXTURE.replace("new RenderTexture(", "GetExistingTexture("))

    def test_no_method_names_or_proprietary_source_are_emitted(self):
        text = FIXTURE.replace("Allocate", "PrivateProjectAllocationDetails")
        output = verified(text)
        self.assertEqual(output["bounded_relevant_methods"][0]["api"], "other")
        self.assertNotIn("PrivateProjectAllocationDetails", str(output))
        self.assertNotIn("cached", str(output))
        self.assertTrue(output["original_cache_sha256"])

    def test_fail_closed_unsafe_source_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "absent"):
                inspect_root(root)
            path = root / "RenderTexturesCache.cs"
            path.write_text(FIXTURE)
            # Synthetic file is not authorized to impersonate a real SHA.
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                inspect_root(root)
            path.unlink()
            path.symlink_to(root / "outside")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                inspect_root(root)


if __name__ == "__main__":
    unittest.main()
