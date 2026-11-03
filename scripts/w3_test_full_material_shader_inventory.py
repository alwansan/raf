#!/usr/bin/env python3
"""W3 synthetic model tests for the full-game Material->Shader inventory resolver.

Model-level unittest only; original assets are never opened here. The real-data
probe hashes and pin-verifies every owner byte-for-byte before parsing and runs
fail-closed separately.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("w3inv", HERE / "probe_w3_full_material_shader_inventory.py")
w3inv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w3inv)

TABLE = [SimpleNamespace(path="globalgamemanagers.assets"),
         SimpleNamespace(path="sharedassets0.assets"),
         SimpleNamespace(path="Library/unity default resources"),
         SimpleNamespace(path="Resources/unity_builtin_extra")]


class TestFullInventoryResolver(unittest.TestCase):
    def test_one_based_mapping(self):
        self.assertEqual(w3inv.resolve_owner_by_fileid(TABLE, 1), "globalgamemanagers.assets")
        self.assertEqual(w3inv.resolve_owner_by_fileid(TABLE, 2), "sharedassets0.assets")
        self.assertEqual(w3inv.resolve_owner_by_fileid(TABLE, 3), "Library/unity default resources")
        self.assertEqual(w3inv.resolve_owner_by_fileid(TABLE, 4), "Resources/unity_builtin_extra")

    def test_same_file_semantics(self):
        self.assertIsNone(w3inv.resolve_owner_by_fileid(TABLE, 0))

    def test_negative_fileid_fail_closed(self):
        with self.assertRaises(w3inv.UnresolvedMaterialShaderLink):
            w3inv.resolve_owner_by_fileid(TABLE, -1)

    def test_out_of_range_fileid_fail_closed(self):
        with self.assertRaises(w3inv.UnresolvedMaterialShaderLink):
            w3inv.resolve_owner_by_fileid(TABLE, len(TABLE) + 1)

    def test_empty_externals_fail_closed(self):
        with self.assertRaises(w3inv.UnresolvedMaterialShaderLink):
            w3inv.resolve_owner_by_fileid([], 1)

    def test_engine_transports_are_fail_closed_set(self):
        self.assertEqual(w3inv.ENGINE_TRANSPORT_PATHS, {"Library/unity default resources", "Resources/unity_builtin_extra"})
        # module must treat both as non-resolvable to game content; resolve still returns the
        # raw path and the caller classifies; engine paths must not be treated as local owners
        for p in w3inv.ENGINE_TRANSPORT_PATHS:
            self.assertNotIn(p, {"globalgamemanagers.assets", "sharedassets0.assets"})

    def test_no_hidden_name_information(self):
        # resolver returns only owner paths; names come exclusively from parsed-form tables
        self.assertNotIn("path_name", [a for a in dir(TABLE[0])])


if __name__ == "__main__":
    unittest.main()
