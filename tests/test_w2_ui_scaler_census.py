"""W2 fail-closed tests for the UI-scaler census probe (synthetic only).

Covers: cross-file script resolution via externals, script-registry reuse,
record byte-length histograms only (no value decoding), pointer-path absence
from outputs, fail-closed rejections and leak guards.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from scripts.probe_w2_ui_scaler_census import (
    SCHEMA_VERSION,
    SCRIPT_HOST,
    TARGET_CLASSES,
    build_script_registry,
    owner_name_ok,
    record_byte_length,
    scan_owner,
)


class FakeObj:
    def __init__(self, type_name, path_id, tree=None, raw=None, raise_read=False):
        self.type = types.SimpleNamespace(name=type_name)
        self.path_id = path_id
        self._tree = tree
        self._raw = raw
        self._raise = raise_read

    def read_typetree(self, check_read=True):
        if self._raise:
            raise ValueError("Expected to read 132 bytes, but only read 60 bytes")
        return self._tree

    def get_raw_data(self):
        if self._raise or self._raw is None:
            raise ValueError("raw unavailable")
        return self._raw


def fake_env(objects, externals=()):
    env = types.SimpleNamespace(objects=objects)
    env.file = types.SimpleNamespace(
        externals=[types.SimpleNamespace(path=p) for p in externals])
    return env


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


def script(type_name, path_id, class_name):
    return FakeObj(type_name, path_id, {"m_ClassName": class_name})


def behaviour(path_id, file_id, raw=b"x" * 80):
    return FakeObj("MonoBehaviour", path_id,
                   {"m_Script": {"m_FileID": file_id, "m_PathID": path_id}}, raw)


class ContractTests(unittest.TestCase):
    def test_schema_and_targets(self):
        self.assertEqual(SCHEMA_VERSION, 1)
        self.assertEqual(TARGET_CLASSES, ("CanvasScaler", "Settings",
                                          "GraphicsSettingsBox", "ControlsSettingsBox"))
        self.assertEqual(SCRIPT_HOST, "globalgamemanagers.assets")

    def test_registry_counts_undecodable_skipped(self):
        env = fake_env([
            script("MonoScript", 1, "CanvasScaler"),
            FakeObj("MonoScript", 2, None, raise_read=True),
            script("MonoScript", 3, "Settings"),
            FakeObj("Transform", 4, {}),
        ])
        registry, undec = build_script_registry(env)
        self.assertEqual(registry, {1: "CanvasScaler", 3: "Settings"})
        self.assertEqual(undec, 1)

    def test_scan_resolves_cross_file_and_same_file(self):
        lookup = {1: "CanvasScaler", 2: "Settings", 3: "OtherComponent"}
        env = fake_env(
            [
                behaviour(1, 1, b"a" * 80),          # external 1 = ggm -> CanvasScaler
                behaviour(2, 1, b"b" * 80),          # external 1 = ggm -> Settings
                behaviour(3, 2, b"c" * 17),          # external 2 = sharedassets3.assets
            ],
            externals=("globalgamemanagers.assets", "sharedassets3.assets"))
        # registry lookup for path ids used above; only target-class keys appear
        # in recordByteLengthHistograms
        result = scan_owner(env, lookup)
        self.assertEqual(result["behaviours"], 3)
        self.assertEqual(result["targetCounts"]["CanvasScaler"], 1)
        self.assertEqual(result["targetCounts"]["Settings"], 1)
        self.assertEqual(result["scriptReferenceBuckets"],
                         {"external:globalgamemanagers.assets": 2,
                          "external:sharedassets3.assets": 1})
        self.assertEqual(result["recordByteLengthHistograms"]["CanvasScaler"], {80: 1})
        self.assertEqual(result["recordByteLengthHistograms"]["GraphicsSettingsBox"], {})
        # non-target resolution is simply not counted in targetCounts
        self.assertEqual(sum(result["targetCounts"].values()), 2)

    def test_scan_counts_undecodable_and_raw_unavailable(self):
        registry = {7: "CanvasScaler", 8: "CanvasScaler"}
        result = scan_owner(fake_env([
            FakeObj("MonoBehaviour", 1, None, raise_read=True),
            FakeObj("MonoBehaviour", 9, {"m_Script": {"m_FileID": 1, "m_PathID": 7}}),
        ], externals=(SCRIPT_HOST,)), registry)
        self.assertEqual(result["behaviours"], 2)
        self.assertEqual(result["undecodable_behaviours"], 1)
        self.assertEqual(result["raw_unavailable_target_behaviours"], 1)

    def test_malformed_and_missing_script_pptr(self):
        env = fake_env([
            FakeObj("MonoBehaviour", 1, {}),
            FakeObj("MonoBehaviour", 2, {"m_Script": "not-a-dict"}),
            FakeObj("MonoBehaviour", 3, {"m_Script": {"m_FileID": "9", "m_PathID": 1}}),
        ])
        result = scan_owner(env, {1: "CanvasScaler"})
        self.assertEqual(result["otherPptrBuckets"],
                         {"<malformed-script-pptr>": 1, "<no-script-pptr>": 2})

    def test_out_of_range_external_bucket(self):
        env = fake_env([behaviour(1, 9, b"z" * 5)], externals=())
        result = scan_owner(env, {1: "CanvasScaler"})
        self.assertEqual(result["scriptReferenceBuckets"], {"external:<out-of-range>": 1})
        self.assertEqual(result["targetCounts"]["CanvasScaler"], 0)

    def test_record_byte_length_failures(self):
        self.assertEqual(record_byte_length(FakeObj("MonoBehaviour", 1, {}, raise_read=True)), -1)
        self.assertEqual(record_byte_length(FakeObj("MonoBehaviour", 2, {})), -1)

    def test_owner_name_guard(self):
        self.assertTrue(owner_name_ok("resources.assets"))
        self.assertTrue(owner_name_ok("level12"))
        self.assertFalse(owner_name_ok("a/b.assets"))
        self.assertFalse(owner_name_ok("../x"))
        self.assertFalse(owner_name_ok("levelx"))

    def test_no_value_or_pointer_leak_in_scan_output(self):
        registry = {1: "CanvasScaler"}
        env = fake_env([behaviour(1, 1, b"\x33" * 80)], externals=(SCRIPT_HOST,))
        result = scan_owner(env, registry)
        blob = json.dumps(result)
        for forbidden in ("m_PathID", "m_GameObject", "scaleFactor", "referenceResolution"):
            self.assertNotIn(forbidden, blob)
        # no raw record bytes ever appear; the histogram key is the length only
        self.assertEqual(result["recordByteLengthHistograms"]["CanvasScaler"], {80: 1})


if __name__ == "__main__":
    unittest.main()
