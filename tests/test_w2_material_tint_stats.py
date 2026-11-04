"""W2 fail-closed tests for the original material color-tint aggregates probe.

Synthetic only: identity/non-identity classification, alpha<1, out-of-unit,
inf-vs-NaN policy, entry-shape enforcement and leak guards.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_material_tint_stats import (
    OWNERS,
    SCHEMA_VERSION,
    parse_owner,
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


def _tree_with(colors):
    return Obj(
        "Material",
        {"m_SavedProperties": {"m_Colors": colors, "m_TexEnvs": [], "m_Floats": [], "m_Ints": []}},
    )


class ContractTests(unittest.TestCase):
    def test_schema_and_owners(self):
        self.assertEqual(SCHEMA_VERSION, 1)
        self.assertEqual(OWNERS, ("resources.assets", "sharedassets0.assets"))

    def test_identity_vs_non_identity_and_alpha(self):
        env = _fake_env(
            [
                _tree_with([("_Color", {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0})]),
                _tree_with([("_Color", {"r": 0.5, "g": 1.0, "b": 1.0, "a": 0.8})]),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = parse_owner(Path(td) / "fake.assets")
        self.assertEqual(result["material_count"], 2)
        self.assertEqual(result["materials_with_non_default_tint"], 1)
        self.assertEqual(result["materials_only_identity_tint"], 1)
        stats = result["per_property_name"]["_Color"]
        self.assertEqual(stats["materials_using"], 2)
        self.assertEqual(stats["identity_tint"], 1)
        self.assertEqual(stats["non_identity_tint"], 1)
        self.assertEqual(stats["alpha_below_1"], 1)

    def test_out_of_unit_and_inf_counters(self):
        env = _fake_env(
            [
                _tree_with([("_EmissionColor", {"r": 2.0, "g": -1.0, "b": 0.0, "a": 1.0})]),
                _tree_with([("_ClipRect", {"r": float("inf"), "g": -32767.0, "b": 32767.0, "a": 1.0})]),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = parse_owner(Path(td) / "fake.assets")
        self.assertEqual(result["per_property_name"]["_EmissionColor"]["component_outside_unit"], 1)
        self.assertEqual(result["per_property_name"]["_ClipRect"]["non_finite_component"], 1)

    def test_nan_hard_fails(self):
        env = _fake_env(
            [_tree_with([("_Color", {"r": float("nan"), "g": 1.0, "b": 1.0, "a": 1.0})])]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_bad_entry_shape_hard_fails(self):
        env = _fake_env([_tree_with([("_Color", "nodict")])])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_missing_colors_hard_fails(self):
        env = _fake_env([Obj("Material", {"m_SavedProperties": {}})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_no_color_values_leak_into_output(self):
        env = _fake_env(
            [
                _tree_with([("_Color", {"r": 0.25, "g": 0.5, "b": 0.75, "a": 1.0})]),
                _tree_with([("_Tint", {"r": 0.1, "g": 0.2, "b": 0.3, "a": 0.4})]),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = parse_owner(Path(td) / "fake.assets")
        blob = json.dumps(result)
        # property NAMES are engine packaging metadata and appear in the
        # aggregate; the numeric VALUES themselves must never appear
        for forbidden in ("0.25", "0.75", "0.1", "0.4", "m_PathID", "m_Shader", "m_ValidKeywords", "stringTagMap"):
            self.assertNotIn(forbidden, blob)

    def test_leak_guard_rejects_nontrivial_floats(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                probe(Path(td))


if __name__ == "__main__":
    unittest.main()
