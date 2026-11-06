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


class SourceIntegerCoordinateTests(unittest.TestCase):
    def test_rewrites_only_source_and_preserves_swizzle(self):
        patched = rewrite(ASSEMBLY)
        self.assertIn("%t1_integer_lane_0 = OpCompositeExtract %i %address 1", patched)
        self.assertIn("%t1_integer_lane_1 = OpCompositeExtract %i %address 0", patched)
        self.assertIn("%a = OpImageFetch %fv %image %t1_integer_coord Lod %zero", patched)
        self.assertIn("%b = OpImageFetch %fv %other %coord Lod %zero", patched)

    def test_rejects_unresolved_lane(self):
        with self.assertRaises(ValueError):
            rewrite(ASSEMBLY.replace("%carrier = OpBitcast %fv %address",
                                     "%carrier = OpLoad %fv %pointer"))
