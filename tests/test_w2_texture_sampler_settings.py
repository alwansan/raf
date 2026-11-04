"""W2 fail-closed tests for the texture sampler-settings aggregates probe.

Synthetic (no original payload): enum range enforcement (wrap/filter/aniso),
non-finite mip bias, missing settings, identity overflow guard (m_MipBias
never published), unsafe owner names and aggregate-only output.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.probe_w2_texture_sampler_settings import (
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
    import types

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


def _tree(wrap=0, filt=1, aniso=1, bias=0.0, stripped=0):
    return Obj(
        "Texture2D",
        {
            "m_TextureSettings": {
                "m_WrapU": wrap,
                "m_WrapV": wrap,
                "m_WrapW": wrap,
                "m_FilterMode": filt,
                "m_Aniso": aniso,
                "m_MipBias": bias,
            },
            "m_MipsStripped": stripped,
        },
    )


class ContractTests(unittest.TestCase):
    def test_schema_version(self):
        self.assertEqual(SCHEMA_VERSION, 1)

    def test_aggregates_and_counts(self):
        env = _fake_env([_tree(wrap=1, filt=2, aniso=4, stripped=8), _tree()])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        self.assertEqual(result["texture_count"], 2)
        self.assertEqual(result["wrap_u"], {0: 1, 1: 1})
        self.assertEqual(result["filter_mode"], {1: 1, 2: 1})
        self.assertEqual(result["aniso"], {1: 1, 4: 1})
        self.assertEqual(result["mipbias_nonzero"], 0)
        self.assertEqual(result["mips_stripped"], 1)

    def test_wrap_out_of_enum_fails_closed(self):
        env = _fake_env([_tree(wrap=7)])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_filter_out_of_enum_fails_closed(self):
        env = _fake_env([_tree(filt=9)])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_aniso_above_16_fails_closed(self):
        env = _fake_env([_tree(aniso=32)])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_non_finite_mipbias_fails_closed(self):
        env = _fake_env([_tree(bias=float("nan"))])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_missing_settings_fails_closed(self):
        env = _fake_env([Obj("Texture2D", {"m_MipsStripped": 0})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                aggregate_owner(Path(td) / "fake.assets")

    def test_mipbias_value_never_published(self):
        env = _fake_env([_tree(bias=0.125), _tree(bias=-0.5)])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        blob = json.dumps(result)
        self.assertEqual(result["mipbias_nonzero"], 2)
        for forbidden in ("0.125", "-0.5", "MipBias", "m_MipBias"):
            self.assertNotIn(forbidden, blob)

    def test_non_texture_objects_ignored(self):
        env = _fake_env([_tree(), Obj("Material", {"m_SavedProperties": {}})])
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = aggregate_owner(Path(td) / "fake.assets")
        self.assertEqual(result["texture_count"], 1)

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
