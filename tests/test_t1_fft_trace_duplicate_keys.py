"""Source-only negative controls for T1 Unity FFT trace JSON provenance."""
import json
import unittest

from scripts.t1_fft_trace_consistency import reject_duplicate_keys


class DuplicateTraceKeysTests(unittest.TestCase):
    def parse(self, raw):
        return json.loads(raw, object_pairs_hook=reject_duplicate_keys)

    def test_reject_duplicate_kernel_name(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
            self.parse('{"kernel_name":"FFT_A","kernel_name":"FFT_B"}')

    def test_reject_duplicate_find_kernel_index(self):
        with self.assertRaises(ValueError):
            self.parse('{"find_kernel_index":6,"find_kernel_index":7}')

    def test_reject_nested_duplicate(self):
        with self.assertRaises(ValueError):
            self.parse('{"outer":{"compute_shader_guid":"a","compute_shader_guid":"b"}}')

    def test_accept_unique_fields(self):
        self.assertEqual(self.parse('{"kernel_name":"FFT_A","find_kernel_index":6}'),
                         {"kernel_name":"FFT_A","find_kernel_index":6})

    def test_duplicate_after_unicode_escape(self):
        with self.assertRaises(ValueError):
            self.parse('{"kernel_name":"A","kernel\\u005fname":"B"}')


if __name__ == "__main__":
    unittest.main()
