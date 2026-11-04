"""W2 fail-closed tests for the compute-kernel inventory probe.

Synthetic only: provider/kernel aggregation, variant-row shape,
unexpected-field and empty-kernel hard-fails, variantMap depth check,
forbidden-key leak guard.
"""

from __future__ import annotations

import json
import unittest

from scripts.probe_w2_compute_kernel_inventory import (
    OWNERS,
    SCHEMA_VERSION,
    aggregate_provider,
)


def _kernel(name="Butterfly"):
    return {
        "name": name,
        "globalKeywords": [],
        "localKeywords": [],
        "variantMap": ["x"],
    }


def _provider(kernels):
    return {"m_Name": "DX11 FFT", "variants": [{"kernels": kernels, "constantBuffers": [], "globalKeywords": []}]}


class ContractTests(unittest.TestCase):
    def test_schema_and_owners(self):
        self.assertEqual(SCHEMA_VERSION, 1)
        self.assertEqual(
            OWNERS,
            ("sharedassets0.assets", "resources.assets", "sharedassets29.assets"),
        )

    def test_aggregate_counts_and_names(self):
        result = aggregate_provider("t", _provider([_kernel("A"), _kernel("A"), _kernel("B")]))
        self.assertEqual(result["kernelCount"], 3)
        self.assertEqual(result["distinctKernelNames"], 2)
        self.assertEqual(result["kernelNames"], ["A", "A", "B"])
        self.assertEqual(result["serializedConstantBuffers"], 0)

    def test_missing_kernels_fails_closed(self):
        with self.assertRaises(ValueError):
            aggregate_provider("t", _provider([]))

    def test_kernel_without_name_fails_closed(self):
        with self.assertRaises(ValueError):
            aggregate_provider("t", _provider([{"name": "", "variantMap": ["x"]}]))

    def test_unexpected_field_fails_closed(self):
        kernel = _kernel()
        kernel["surprise"] = 1
        with self.assertRaises(ValueError):
            aggregate_provider("t", _provider([kernel]))

    def test_variant_map_depth_deviation_fails_closed(self):
        kernel = _kernel()
        kernel["variantMap"] = ["x", "y"]
        with self.assertRaises(ValueError):
            aggregate_provider("t", _provider([kernel]))

    def test_non_single_variant_row_fails_closed(self):
        tree = {"m_Name": "x", "variants": [{"kernels": [_kernel()]}, {"kernels": []}]}
        with self.assertRaises(ValueError):
            aggregate_provider("t", tree)

    def test_no_forbidden_keys_in_output(self):
        result = aggregate_provider("t", _provider([_kernel("K")]))
        blob = json.dumps(result)
        for forbidden in ("m_PathID", "m_Shader", "stringTagMap", "m_ValidKeywords"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
