"""Synthetic format footprint and lifecycle audit tests; no original data."""
import hashlib
import unittest
from scripts.probe_original_fft_cache_lifetime import footprint, scan_cache, QUALITY_CAPS

SAMPLE = """class RenderTexturesCache {
 RenderTextureFormat format;
 void Start() {
   var tex = new RenderTexture(32,32,0,format,RenderTextureReadWrite.Linear);
   tex.enableRandomWrite = true;
   tex.Create();
 }
 void Finish() {tex.Release();}
}"""


def owned(text):
    return scan_cache(text, hashlib.sha256(text.encode()).hexdigest())


class CacheMemoryTests(unittest.TestCase):
    def test_one_texture_expected_bytes(self):
        self.assertEqual(footprint(512, "ARGBFloat")["estimated_one_target_storage_bytes"], 16777216)
        self.assertEqual(footprint(512, "RGHalf")["estimated_one_target_storage_bytes"], 4194304)
        self.assertEqual(footprint(256, "ARGBHalf")["estimated_one_target_storage_bytes"], 2097152)

    def test_repeat_quality_caps_preserved_without_claiming_runtime_quality(self):
        self.assertEqual(QUALITY_CAPS, (32, 64, 256, 512, 512, 256, 256))
        self.assertFalse(footprint(512, "RGFloat")["actual_memory_allocated_or_target_count_proven"])

    def test_invalid_resolution_or_unknown_format_fails(self):
        for n in (0, 12, 31, 33, 1024, True):
            with self.subTest(n=n), self.assertRaises(ValueError):
                footprint(n, "ARGBFloat")
        with self.assertRaises(ValueError):
            footprint(32, "Rgba32f")

    def test_lexical_release_is_not_proof_of_lifetime(self):
        r = owned(SAMPLE)
        self.assertEqual(r["bounded_callsite_counts"]["texture_release"], 1)
        self.assertEqual(r["bounded_callsite_counts"]["render_texture_construct"], 1)
        self.assertFalse(r["no_memory_leak_proven"])
        self.assertFalse(r["actual_gpu_allocation_count_or_release_reachability_proven"])

    def test_comment_fake_release_and_mismatched_source_rejected(self):
        text = SAMPLE.replace("tex.Release();", "// tex.Release();")
        self.assertEqual(owned(text)["bounded_callsite_counts"]["texture_release"], 0)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            scan_cache(SAMPLE, "0" * 64)


if __name__ == "__main__":
    unittest.main()
