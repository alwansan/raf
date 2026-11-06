"""Fail-closed adversarial controls for the private source-only FFT coordinate rewrite.

No game assets or shader binaries are included. These synthetic inputs test
ambiguity handling, not Vulkan/Unity correctness or original shader identity.
"""
import unittest

from scripts.t1_fft_source_integer_coordinates import rewrite
ASSEMBLY = """OpDecorate %image DescriptorSet 0
OpDecorate %image Binding 0
OpDecorate %other DescriptorSet 0
OpDecorate %other Binding 1
%i = OpTypeInt 32 1
%f = OpTypeFloat 32
%iv = OpTypeVector %i 2
%fv = OpTypeVector %f 2
%address = OpLoad %iv %pointer
%carrier = OpBitcast %fv %address
%swapped = OpVectorShuffle %fv %carrier %carrier 1 0
%coord = OpBitcast %iv %swapped
%a = OpImageFetch %fv %image %coord Lod %zero
%b = OpImageFetch %fv %other %coord Lod %zero
"""


class SourceIntegerRewriteAdversarialTests(unittest.TestCase):
    def test_two_source_fetches_are_ambiguous(self):
        extra = "%second = OpImageFetch %fv %image %coord Lod %zero\n"
        with self.assertRaisesRegex(ValueError, "one unmodified source fetch"):
            rewrite(ASSEMBLY + extra)

    def test_missing_source_binding_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "one unmodified source fetch"):
            rewrite(ASSEMBLY.replace("OpDecorate %image Binding 0\n", ""))

    def test_rewriting_twice_is_rejected(self):
        patched = rewrite(ASSEMBLY)
        with self.assertRaisesRegex(ValueError, "one unmodified source fetch"):
            rewrite(patched)

    def test_unresolved_float_load_is_not_assumed_integer(self):
        changed = ASSEMBLY.replace(
            "%carrier = OpBitcast %fv %address",
            "%carrier = OpLoad %fv %float_pointer",
        )
        with self.assertRaisesRegex(ValueError, "Unresolved private coordinate lane"):
            rewrite(changed)

    def test_non_source_fetch_retains_original_coordinate(self):
        patched = rewrite(ASSEMBLY)
        self.assertEqual(
            patched.count("%b = OpImageFetch %fv %other %coord Lod %zero"), 1
        )
        self.assertEqual(patched.count("%t1_integer_coord = OpCompositeConstruct"), 1)


if __name__ == "__main__":
    unittest.main()
