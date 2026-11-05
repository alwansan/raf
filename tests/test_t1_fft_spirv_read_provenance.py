import unittest

from scripts.t1_fft_spirv_read_provenance import analyze


class SpirvReadProvenanceTests(unittest.TestCase):
    def test_fetch_and_queries_follow_input_roots(self):
        report = analyze("""
        OpDecorate %1 DescriptorSet 0
        OpDecorate %1 Binding 0
        OpDecorate %2 DescriptorSet 0
        OpDecorate %2 Binding 1
        %3 = OpLoad %20 %1
        %4 = OpLoad %20 %2
        %5 = OpSampledImage %21 %4 %99
        %6 = OpImage %20 %5
        %7 = OpImageFetch %22 %6 %30
        %8 = OpImageQuerySizeLod %23 %3 %31
        %9 = OpImageQuerySize %23 %4
        """)
        self.assertEqual(report["source"]["query_size_lod"], 1)
        self.assertEqual(report["butterfly"]["fetch"], 1)
        self.assertEqual(report["butterfly"]["query_size"], 1)
        self.assertEqual(sum(report["unresolved"].values()), 0)

    def test_unknown_root_does_not_inherit_known_binding(self):
        report = analyze("OpDecorate %1 Binding 0\n%2 = OpImageFetch %3 %1 %4")
        self.assertEqual(report["unresolved"]["fetch"], 1)

    def test_cycles_rejected(self):
        with self.assertRaises(ValueError):
            analyze("%1 = OpCopyObject %2 %1\n%3 = OpImageFetch %2 %1 %4")
