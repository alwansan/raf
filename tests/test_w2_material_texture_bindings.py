"""W2 fail-closed tests for the material texture-binding aggregates probe.

Synthetic only: PPtr bound/null classification (m_FileID-only external
reference vs fully-null), slot name counters, entry/PPtr shape enforcement,
negative component hard-fail, leak guards (raw PPtr identifiers and object
names never published).
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_material_texture_bindings import (
    SCHEMA_VERSION,
    aggregate_owner,
    probe,
    validate_owner_names,
)


class Obj:
    def __init__(self, type_name, tree):
        self.type = type("T", (), {"name": type_name})()
        self._tree = tree

    def read_typetree(self):
        return self._tree


def _fake_env(objects):
    return type("Env", (), {"objects": objects})()


@contextlib.contextmanager
def fake_unitypy(env):
    fake = types.ModuleType("UnityPy")
    fake.load = lambda _path: env
    saved = sys.modules.get("UnityPy")
    sys.modules["UnityPy"] = fake
    try:
        yield
    finally:
        if saved is None:
            sys.modules.pop("UnityPy", None)
        else:
            sys.modules["UnityPy"] = saved


def _entry(name, fileid, pathid):
    return (name, {"m_Texture": {"m_FileID": fileid, "m_PathID": pathid}, "m_Scale": {"x": 1, "y": 1}, "m_Offset": {"x": 0, "y": 0}})


def _material(entries):
    return Obj("Material", {"m_SavedProperties": {"m_TexEnvs": entries}})


class ContractTests(unittest.TestCase):
    def test_schema_version(self):
        self.assertEqual(SCHEMA_VERSION, 1)

    def test_bound_null_classification(self):
        env = _fake_env(
            [
                _material([_entry("_MainTex", 2, 0), _entry("_DetailAlbedoMap", 0, 0)]),
                _material([_entry("_MainTex", 0, 7), _entry("_Texcoord", 0, 0)]),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        self.assertEqual(result["material_count"], 2)
        self.assertEqual(result["bound_by_slot"], {"_MainTex": 2})
        self.assertEqual(result["null_by_slot"], {"_DetailAlbedoMap": 1, "_Texcoord": 1})
        self.assertEqual(result["fileid_by_bound_slot"]["_MainTex"], {2: 1, 0: 1})
        self.assertEqual(result["fileid_total"], {0: 1, 2: 1})

    def test_missing_texenvs_fails_closed(self):
        env = _fake_env([Obj("Material", {"m_SavedProperties": {}})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_malformed_entry_fails_closed(self):
        env = _fake_env([_material([("_MainTex", "node")])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_missing_texture_pptr_fails_closed(self):
        env = _fake_env([_material([("_MainTex", {"m_Scale": {"x": 1, "y": 1}})])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_negative_pusr_component_fails_closed(self):
        env = _fake_env([_material([_entry("_MainTex", -1, 0)])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_non_material_ignored(self):
        env = _fake_env([_material([_entry("_MainTex", 1, 1)]), Obj("Shader", {"x": 1})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        self.assertEqual(result["material_count"], 1)

    def test_no_pptr_ids_or_payload_leak(self):
        env = _fake_env([_material([_entry("_MainTex", 2, 12345)])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        blob = json.dumps(result)
        for forbidden in ("m_PathID", "m_FileID", "12345", "m_Scale", "m_Offset", "stringTagMap"):
            self.assertNotIn(forbidden, blob)

    def test_unsafe_owner_names_rejected(self):
        for bad in ("../x.assets", "a/b.assets", "x/y", "x\\y.assets"):
            with self.assertRaises(ValueError):
                validate_owner_names([bad])

    def test_probe_rejects_missing_owner(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises((ValueError, OSError)):
                probe([Path(td) / "missing.assets"], None, "Raft/Raft_Data")


if __name__ == "__main__":
    unittest.main()
