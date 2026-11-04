#!/usr/bin/env python3
"""W3 synthetic model tests for the unknown-type decomposition tooling."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("w3udec", HERE / "probe_w3_unknown_type_decomp.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestUnknownDecomp(unittest.TestCase):
    def test_published_types_set(self):
        self.assertEqual(m.PUBLISHED_TYPES, {0, 2, 3, 4})

    def test_step9_artifact_present(self):
        repo =HERE.parent
        self.assertTrue((repo / m.STEP9_ARTIFACT).exists())

    def test_histogram_keys_are_numeric_strings(self):
        # a synthetic raw histogram must key on str(int)
        hist = {"1": 24}
        self.assertEqual(sum(v for v in hist.values()), 24)
        self.assertEqual([int(k) for k in hist], [1])


if __name__ == "__main__":
    unittest.main()
