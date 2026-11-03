"""Synthetic bounded original water module teardown graph tests."""
import hashlib
import unittest
from scripts.a4_gpu_cache_destroy_callgraph import inspect_source

SOURCE = """class WavesRendererFFT {
  void OnDestroy() { PrivateTearDown(); }
  void PrivateTearDown() { Dispose(); }
  void Dispose() { texture.Release(); }
}
"""


def owned(s):
    return inspect_source(s, hashlib.sha256(s.encode()).hexdigest())


class RendererTeardownGraphTests(unittest.TestCase):
    def test_indirect_self_dispose_reachable_but_not_a_runtime_proof(self):
        data = owned(SOURCE)
        self.assertFalse(data["on_destroy_direct_self_dispose"])
        self.assertTrue(data["on_destroy_transitive_self_dispose_lexical"])
        self.assertEqual(data["on_destroy_direct_self_call_count"], 1)
        self.assertFalse(data["leak_fixed"])
        self.assertFalse(data["on_device_lifetime_or_oom_verified"])

    def test_unqualified_and_this_dispose_are_traced(self):
        direct = SOURCE.replace("PrivateTearDown();", "this.Dispose();")
        result = owned(direct)
        self.assertTrue(result["on_destroy_direct_self_dispose"])
        self.assertTrue(result["on_destroy_transitive_self_dispose_lexical"])

    def test_comment_literal_and_unrelated_member_do_not_fake_self_call(self):
        for call in ('"Dispose();"', '/* Dispose(); */', 'other.Dispose();'):
            changed = SOURCE.replace("PrivateTearDown();", call)
            result = owned(changed)
            self.assertFalse(result["on_destroy_direct_self_dispose"])
            self.assertFalse(result["on_destroy_transitive_self_dispose_lexical"])

    def test_member_cleanup_is_measured_separately_from_self_call(self):
        changed = SOURCE.replace("PrivateTearDown();", "other.Release();")
        data = owned(changed)
        self.assertEqual(data["on_destroy_direct_member_cleanup_calls"], 1)
        self.assertFalse(data["on_destroy_transitive_self_dispose_lexical"])

    def test_source_identity_and_missing_dispose_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            inspect_source(SOURCE, "0" * 64)
        with self.assertRaisesRegex(ValueError, "method identity"):
            owned(SOURCE.replace("void Dispose()", "void Other()"))
        with self.assertRaisesRegex(ValueError, "type ambiguous"):
            owned(SOURCE.replace("WavesRendererFFT", "PrivateWaterType"))


if __name__ == "__main__":
    unittest.main()
