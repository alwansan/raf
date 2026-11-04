#!/usr/bin/env python3
"""W3 synthetic model tests for the full byte census tooling."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("w3cens", HERE / "probe_w3_full_byte_census.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestByteCensus(unittest.TestCase):
    def test_owner_regexes_and_year(self):
        self.assertTrue(m.ASSETS_RE.match("globalgamemanagers.assets"))
        self.assertTrue(m.LEVEL_RE.fullmatch("level29"))
        self.assertFalse(m.LEVEL_RE.fullmatch("level29.resS"))
        self.assertFalse(m.ASSETS_RE.match("level0"))

    def test_sha256_file_known_vector(self):
        import hashlib, tempfile, os
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(b"W3 byte census\n")
            path = t.name
        try:
            size, digest = m.sha256_file(Path(path))
        finally:
            os.unlink(path)
        self.assertEqual(size, 15)
        self.assertEqual(digest, hashlib.sha256(b"W3 byte census\n").hexdigest())


if __name__ == "__main__":
    unittest.main()
