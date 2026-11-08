#!/usr/bin/env python3
"""Regression: private FFT first-pass manifests must reject ambiguous JSON keys."""
import json
import unittest

from scripts.t1_fft_first_divergence import reject_duplicate_manifest_keys


class DuplicateManifestKeysTests(unittest.TestCase):
    def parse(self, source):
        return json.loads(source, object_pairs_hook=reject_duplicate_manifest_keys)

    def test_duplicate_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.parse('[{"name":"pass0","reference":"original.bin","reference":"other.bin","observed":"unity.bin"}]')

    def test_duplicate_observed_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.parse('[{"name":"pass0","reference":"original.bin","observed":"unity.bin","observed":"other.bin"}]')

    def test_duplicate_nested_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.parse('[{"name":"pass0","reference":"original.bin","observed":"unity.bin","meta":{"x":1,"x":2}}]')

    def test_distinct_passes_allowed(self):
        result = self.parse('[{"name":"pass0","reference":"a.bin","observed":"b.bin"},{"name":"pass1","reference":"c.bin","observed":"d.bin"}]')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["name"], "pass1")


if __name__ == "__main__":
    unittest.main()
