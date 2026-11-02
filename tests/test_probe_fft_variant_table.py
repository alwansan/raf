"""Variant metadata fixtures; not real proprietary shader contents."""
import unittest
from scripts.probe_fft_variant_table import summarize_variant_tree


class FftVariantTableTests(unittest.TestCase):
    def test_name_repeats_do_not_mean_multiple_runtime_kernels(self):
        tree = {"variants": [{"kernels": [
            {"name": "FFT", "variantMap": [1], "globalKeywords": ["size64"],
             "localKeywords": ["horizontal"], "code": b"a"},
            {"name": "FFT", "variantMap": [2], "globalKeywords": ["size128"],
             "localKeywords": ["vertical"], "code": b"b"},
        ]}]}
        result = summarize_variant_tree(tree, expected_kernels=2)
        self.assertEqual(result["original_compiled_entries"], 2)
        self.assertEqual(result["variants"][0]["unique_compiled_kernel_name_hashes"], 1)
        self.assertEqual(result["variants"][0]["unique_variant_map_digests"], 2)
        self.assertEqual(result["variants"][0]["unique_combined_keyword_bundles"], 2)
        self.assertNotIn("size64", str(result))
        self.assertNotIn("horizontal", str(result))
        self.assertFalse(result["original_kernel_lookup_index_order_verified"])
        self.assertNotIn("FFT", str(result))
        self.assertNotIn("b'a'", str(result))

    def test_changed_count_and_invalid_map_rejected(self):
        tree = {"variants": [{"kernels": [{"name": "X", "variantMap": [], "globalKeywords": [],
                                                  "localKeywords": []}]}]}
        with self.assertRaisesRegex(ValueError, "count changed"):
            summarize_variant_tree(tree, expected_kernels=2)
        tree["variants"][0]["kernels"][0]["variantMap"] = None
        with self.assertRaisesRegex(ValueError, "variant map invalid"):
            summarize_variant_tree(tree, expected_kernels=1)
        with self.assertRaisesRegex(ValueError, "variants"):
            summarize_variant_tree({"variants": []}, expected_kernels=0)


if __name__ == "__main__":
    unittest.main()
