"""W2 fail-closed tests for the full resource-census probe.

Synthetic only: census counting, zero-object rejection, unsafe owner
names, class-key publication policy and leak guards.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_resource_census import (
    OWNER_NAME_OK,
    SCHEMA_VERSION,
    census_owner,
)


class Obj:
    def __init__(self, type_name):
        self.type = type("T", (), {"name": type_name})()


def _fake_env(counted_types):
    objects = []
    for type_name, n in counted_types.items():
        objects.extend(Obj(type_name) for _ in range(n))
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
    def test_schema_version(self):
        self.assertEqual(SCHEMA_VERSION, 1)

    def test_census_counts_and_total(self):
        env = _fake_env({"GameObject": 3, "Transform": 2, "Mesh": 1})
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = census_owner(Path(td) / "fake.assets")
        self.assertEqual(result["totalObjects"], 6)
        self.assertEqual(result["typeCounts"], {"GameObject": 3, "Mesh": 1, "Transform": 2})

    def test_zero_object_owner_fails_closed(self):
        env = _fake_env({})
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            with self.assertRaises(ValueError):
                census_owner(Path(td) / "fake.assets")

    def test_unsafe_owner_names(self):
        self.assertFalse(OWNER_NAME_OK.match("../assets"))
        self.assertFalse(OWNER_NAME_OK.match("a/b.assets"))
        self.assertTrue(OWNER_NAME_OK.match("resources.assets"))
        self.assertTrue(OWNER_NAME_OK.match("level12"))
        self.assertFalse(OWNER_NAME_OK.match("levelx"))

    def test_no_payload_keys(self):
        env = _fake_env({"GameObject": 1})
        with tempfile.TemporaryDirectory() as td, fake_unitypy(env):
            result = census_owner(Path(td) / "fake.assets")
        blob = json.dumps(result)
        for forbidden in ("m_PathID", "m_Shader", "stringTagMap"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
