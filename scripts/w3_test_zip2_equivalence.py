#!/usr/bin/env python3
"""W3 synthetic model tests for the zip2 equivalence probes."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


equiv = _load("probe_w3_zip2_hosted_copy_equiv")
bytes_probe = _load("probe_w3_zip2_pin_bytes")


class TestZip2Equivalence(unittest.TestCase):
    def test_owner_regexes(self):
        self.assertTrue(equiv.ASSETS_RE.match("resources.assets"))
        self.assertTrue(equiv.ASSETS_RE.match("sharedassets36.assets"))
        self.assertFalse(equiv.ASSETS_RE.match("level29.assets"))
        self.assertTrue(equiv.LEVEL_RE.fullmatch("level0"))
        self.assertFalse(equiv.LEVEL_RE.fullmatch("level0.assets"))
        self.assertFalse(equiv.LEVEL_RE.fullmatch("level0.resS"))

    def test_pinned_table_matches_published_values(self):
        expected = {
            "resources.assets": 111_533_516,
            "sharedassets0.assets": 115_978_112,
        }
        for owner, (size, sha) in bytes_probe.PINNED.items():
            self.assertEqual(size, expected[owner])
            self.assertEqual(len(sha), 64)


if __name__ == "__main__":
    unittest.main()
