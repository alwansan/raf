"""W2 fail-closed tests for the material scalar-property usage probe.

Synthetic only: name-keyed usage counters, zero-scalar materials, entry
shape/NaN enforcement, inf sentinel counting, and leak guards (numerical
float values and object identifiers never published).
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_material_scalar_properties import (
    SCHEMA_VERSION,
    aggregate_owner,
    probe,
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


def _material(floats, ints=None):
    ints = ints or []
    return Obj("Material", {"m_SavedProperties": {"m_Floats": floats, "m_Ints": ints}})


class ContractTests(unittest.TestCase):
    def test_schema_version(self):
        self.assertEqual(SCHEMA_VERSION, 1)

    def test_usage_counters_and_zero_scalar_materials(self):
        env = _fake_env(
            [
                _material([("_Cutoff", 0.5), ("_Metallic", 1.0)]),
                _material([("_Cutoff", 0.25)]),
                _material([]),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        self.assertEqual(result["material_count"], 3)
        self.assertEqual(result["materials_without_scalars"], 1)
        self.assertEqual(result["floats_by_name"], {"_Cutoff": 2, "_Metallic": 1})
        self.assertEqual(result["float_names"], 2)

    def test_ints_counted_in_own_table(self):
        env = _fake_env([_material([], [("_Mode", 3), ("_Mode", 1), ("_Stencil", 0)])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        self.assertEqual(result["ints_by_name"], {"_Mode": 2, "_Stencil": 1})
        self.assertEqual(result["materials_without_scalars"], 0)

    def test_entry_shape_fails_closed(self):
        for bad in ([("_Cutoff",)], ["_Cutoff"], [("_Cutoff", "x")]):
            env = _fake_env([_material(bad)])
            with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
                with self.assertRaises(ValueError):
                    aggregate_owner(Path(td) / "fake.assets")

    def test_nan_fails_closed(self):
        env = _fake_env([_material([("_Cutoff", float("nan"))])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_inf_sentinel_counted(self):
        env = _fake_env([_material([("_ClipRect", float("inf"))])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        self.assertEqual(result["inf_floats_by_name"], {"_ClipRect": 1})

    def test_no_float_values_leak(self):
        env = _fake_env([_material([("_Cutoff", 0.125), ("_Glossiness", -0.5)])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        blob = json.dumps(result)
        for forbidden in ("0.125", "-0.5", "m_PathID", "m_Scale", "stringTagMap"):
            self.assertNotIn(forbidden, blob)

    def test_float_literals_rejected_from_output(self):
        from scripts.probe_w2_material_scalar_properties import assert_no_float_literals
        with self.assertRaises(ValueError):
            assert_no_float_literals('{"x": 0.25, "b": 7, "sha": "abcd"}')
        assert_no_float_literals('{"float_names": 2, "ints_by_name": {}}')

    def test_bad_saved_properties_fails_closed(self):
        env = _fake_env([Obj("Material", {"m_SavedProperties": {}})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")


if __name__ == "__main__":
    unittest.main()
