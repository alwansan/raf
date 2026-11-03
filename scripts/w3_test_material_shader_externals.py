#!/usr/bin/env python3
"""W3 synthetic model tests for Material->Shader external PPtr resolution.

These tests exercise the resolver/classifier logic on synthetic external tables.
They never touch original game bytes; the real-data probe authenticates SHA-256
pinned owners before any parse and runs fail-closed separately.
"""
from __future__ import annotations

import unittest
from types import SimpleNamespace

from probe_w3_material_shader_externals import (
    UnresolvedMaterialShaderLink,
    classify_pptr,
    resolve_owner_by_fileid,
)


def ext(path):
    return SimpleNamespace(path=path)


TABLE = [ext("globalgamemanagers.assets"), ext("sharedassets0.assets"),
         ext("Library/unity default resources"), ext("Resources/unity_builtin_extra")]


class TestResolveOwnerByFileID(unittest.TestCase):
    def test_fileid_maps_one_based(self):
        self.assertEqual(resolve_owner_by_fileid(TABLE, 1), "globalgamemanagers.assets")
        self.assertEqual(resolve_owner_by_fileid(TABLE, 2), "sharedassets0.assets")
        self.assertEqual(resolve_owner_by_fileid(TABLE, 3), "Library/unity default resources")
        self.assertEqual(resolve_owner_by_fileid(TABLE, 4), "Resources/unity_builtin_extra")

    def test_fileid_zero_is_same_file(self):
        self.assertIsNone(resolve_owner_by_fileid(TABLE, 0))

    def test_negative_fileid_rejected(self):
        with self.assertRaises(UnresolvedMaterialShaderLink):
            resolve_owner_by_fileid(TABLE, -1)

    def test_out_of_range_fileid_rejected(self):
        with self.assertRaises(UnresolvedMaterialShaderLink):
            resolve_owner_by_fileid(TABLE, len(TABLE) + 1)

    def test_empty_externals_nonzero_fileid_rejected(self):
        with self.assertRaises(UnresolvedMaterialShaderLink):
            resolve_owner_by_fileid([], 1)


class TestClassifyPPtr(unittest.TestCase):
    def test_same_file_has_no_owner(self):
        info = classify_pptr(TABLE, 0, 123)
        self.assertEqual(info["kind"], "same_file")
        self.assertEqual(info["path_id"], 123)

    def test_game_owner_is_owner_resolveable(self):
        info = classify_pptr(TABLE, 2, 2416)
        self.assertEqual(info["kind"], "owner_resolveable")
        self.assertEqual(info["owner_path"], "sharedassets0.assets")
        self.assertEqual(info["path_id"], 2416)

    def test_engine_transport_flagged_unresolved_not_resolved(self):
        for fid in (3, 4):
            info = classify_pptr(TABLE, fid, 10101)
            self.assertEqual(info["kind"], "owner_resolveable")
            self.assertIn(info["owner_path"],
                          ("Library/unity default resources", "Resources/unity_builtin_extra"))

    def test_classifier_never_fabricates_names(self):
        info = classify_pptr(TABLE, 2, 2416)
        self.assertNotIn("name", info)


if __name__ == "__main__":
    unittest.main()
