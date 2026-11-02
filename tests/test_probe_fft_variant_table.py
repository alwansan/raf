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


    def test_private_variant_tuple_keeps_numeric_tags_and_redacts_program_bytes(self):
        value = ("HiddenKernel", 5, b"DXBC" + b"\x01" * 16)
        from scripts.probe_fft_variant_table import private_variant_element_shape
        shape = private_variant_element_shape(value)
        self.assertEqual(shape["kind"], "tuple")
        self.assertEqual(shape["items"][1], {"kind": "integer", "value": 5})
        self.assertTrue(shape["items"][2]["begins_with_dxbc_magic"])
        self.assertEqual(shape["items"][2]["bytes"], 20)
        self.assertNotIn("HiddenKernel", str(shape))
        self.assertNotIn("DXBC", str(shape))

    def test_long_original_byte_tuple_is_hashed_not_dumped(self):
        from scripts.probe_fft_variant_table import private_variant_element_shape
        binary = b"DXBC" + bytes(range(128))
        record = private_variant_element_shape(tuple(binary))
        self.assertEqual(record["kind"], "byte_valued_sequence")
        self.assertEqual(record["bytes"], len(binary))
        self.assertTrue(record["begins_with_dxbc_magic"])
        self.assertFalse(record["shader_byte_values_published"])
        self.assertNotIn(str(list(binary)), str(record))

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
