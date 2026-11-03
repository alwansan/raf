"""W2 fail-closed tests for the original material property-statistics probe.

Synthetic only (no original payload): verifies enum-free int requirements,
aggregate-only output (no names/keywords/IDs), and the verified-source gate.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_material_property_stats import (
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


def _material_tree(**overrides):
    base = {
        "m_CustomRenderQueue": -1,
        "m_LightmapFlags": 4,
        "m_EnableInstancingVariants": False,
        "m_DoubleSidedGI": False,
        "m_ValidKeywords": [],
        "disabledShaderPasses": [],
        "m_SavedProperties": {
            "m_TexEnvs": [],
            "m_Floats": [],
            "m_Ints": [],
            "m_Colors": [],
        },
    }
    base.update(overrides)
    return base


class ContractTests(unittest.TestCase):
    def test_schema_and_owners(self):
        self.assertEqual(SCHEMA_VERSION, 1)
        self.assertEqual(OWNERS, ("resources.assets", "sharedassets0.assets"))

    def test_aggregates_no_names_no_keywords(self):
        env = _fake_env(
            [
                Obj(
                    "Material",
                    _material_tree(
                        m_ValidKeywords=["_EMISSION", "_METALLICGLOSSMAP"],
                        disabledShaderPasses=["SHADOWCASTER"],
                        m_SavedProperties={
                            "m_TexEnvs": [{"x": 1}],
                            "m_Floats": [{"x": 1}, {"x": 2}],
                            "m_Ints": [],
                            "m_Colors": [{"x": 1}, {"x": 2}, {"x": 3}],
                        },
                    ),
                ),
                Obj("Material", _material_tree(m_EnableInstancingVariants=True)),
                Obj("Texture2D", {"m_ColorSpace": 1}),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = parse_owner(Path(td) / "fake.assets")
        self.assertEqual(result["material_count"], 2)
        self.assertEqual(result["instancing_enabled_materials"], 1)
        self.assertEqual(result["distinct_custom_render_queue_values"], 1)
        self.assertEqual(result["custom_render_queue_distribution"], [{"value": -1, "count": 2}])
        dist = dict(
            (kv["value"], kv["count"])
            for kv in result["valid_keywords_materials_distribution"]
        )
        self.assertEqual(dist, {0: 1, 2: 1})
        colors = dict(
            (kv["value"], kv["count"])
            for kv in result["saved_colors_entry_distribution"]
        )
        self.assertEqual(colors, {0: 1, 3: 1})
        blob = json.dumps(result)
        for forbidden in ("_EMISSION", "SHADOWCASTER", "m_Name", "m_PathID", "m_ValidKeywords", "stringTagMap"):
            self.assertNotIn(forbidden, blob)

    def test_non_int_render_queue_hard_fails(self):
        env = _fake_env([Obj("Material", _material_tree(m_CustomRenderQueue="Transparent"))])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_non_int_lightmap_flags_hard_fails(self):
        env = _fake_env([Obj("Material", _material_tree(m_LightmapFlags="baked"))])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_missing_saved_properties_hard_fails(self):
        env = _fake_env([Obj("Material", {"m_CustomRenderQueue": -1, "m_LightmapFlags": 0})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_keywords_not_list_hard_fails(self):
        env = _fake_env([Obj("Material", _material_tree(m_ValidKeywords="bad"))])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_non_material_objects_ignored(self):
        env = _fake_env([Obj("Shader", {"m_Script": "x"}), Obj("Material", _material_tree())])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = parse_owner(Path(td) / "fake.assets")
        self.assertEqual(result["material_count"], 1)


class ProbeGateTests(unittest.TestCase):
    def test_probe_requires_verified_sources(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                probe(Path(td))


if __name__ == "__main__":
    unittest.main()
