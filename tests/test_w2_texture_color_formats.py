"""W2 fail-closed tests for the original texture color/format aggregate probe.

Synthetic only: the real two-owner parse is exercised by its own CI run on
SHA-pinned sources. Here the probe contract is verified — engine-enum bounds,
int format requirement, aggregate-only output fields (no names/path IDs), and
verified-source gating calls.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_texture_color_formats import (
    OWNERS,
    SCHEMA_VERSION,
    VALID_TEXTURE_COLOR_SPACES,
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


class ContractTests(unittest.TestCase):
    def test_schema_and_enum_tables(self):
        self.assertEqual(SCHEMA_VERSION, 1)
        self.assertEqual(VALID_TEXTURE_COLOR_SPACES, {0: "Gamma", 1: "Linear"})
        self.assertEqual(OWNERS, ("resources.assets", "sharedassets0.assets"))

    def test_aggregate_counts_no_names(self):
        env = _fake_env(
            [
                Obj(
                    "Texture2D",
                    {
                        "m_ColorSpace": 1,
                        "m_TextureFormat": 12,
                        "m_Width": 512,
                        "m_Height": 512,
                        "m_Name": "Skin_Amplify_diffuse",
                    },
                ),
                Obj(
                    "Texture2D",
                    {
                        "m_ColorSpace": 0,
                        "m_TextureFormat": 12,
                        "m_Width": 512,
                        "m_Height": 512,
                        "m_Name": "Skin_Amplify_normal",
                    },
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = parse_owner(Path(td) / "fake.assets")
        self.assertEqual(result["texture_count"], 2)
        pairs = {
            (p["format"], p["colorspace"]): p["count"]
            for p in result["format_colorspace_pairs"]
        }
        self.assertEqual(pairs[(12, 1)], 1)
        self.assertEqual(pairs[(12, 0)], 1)
        blob = json.dumps(result)
        self.assertNotIn("m_Name", blob)
        self.assertNotIn("Skin_Amplify", blob)
        self.assertNotIn("m_PathID", blob)

    def test_out_of_enum_colorspace_hard_fails(self):
        env = _fake_env(
            [Obj("Texture2D", {"m_ColorSpace": 2, "m_TextureFormat": 1, "m_Width": 8, "m_Height": 8})]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_non_int_format_hard_fails(self):
        env = _fake_env(
            [Obj("Texture2D", {"m_ColorSpace": 0, "m_TextureFormat": "BC7", "m_Width": 8, "m_Height": 8})]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                parse_owner(Path(td) / "fake.assets")

    def test_non_texture_objects_ignored(self):
        env = _fake_env(
            [
                Obj("Material", {"m_Name": "x"}),
                Obj(
                    "Texture2D",
                    {"m_ColorSpace": 1, "m_TextureFormat": 4, "m_Width": 4, "m_Height": 4},
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = parse_owner(Path(td) / "fake.assets")
        self.assertEqual(result["texture_count"], 1)


class ProbeGateTests(unittest.TestCase):
    def test_probe_requires_verified_sources(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                probe(Path(td))


if __name__ == "__main__":
    unittest.main()
