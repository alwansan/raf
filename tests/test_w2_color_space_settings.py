"""W2 fail-closed tests for the original color-space settings probe.

All tests are synthetic (no original payload is read) and verify that the
probe never guesses: missing input, out-of-enum color-space values, malformed
gamut lists, missing PlayerSettings and non-aggregate output keys must fail.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.probe_w2_color_space_settings import (
    SCHEMA_VERSION,
    VALID_COLOR_SPACES,
    read_color_space,
)


class Obj:
    def __init__(self, type_name, tree):
        self.type = type("T", (), {"name": type_name})()
        self._tree = tree

    def read_typetree(self):
        return self._tree


def _fake_env(objects):
    return type("Env", (), {"objects": objects})()


class ValidColorSpaceTests(unittest.TestCase):
    def test_enum_table_is_exhaustive_g_zero_linear_one(self):
        self.assertEqual(VALID_COLOR_SPACES, {0: "Gamma", 1: "Linear"})

    def test_schema_version_pin(self):
        self.assertEqual(SCHEMA_VERSION, 1)


class ReadColorSpaceFailClosedTests(unittest.TestCase):
    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                read_color_space(Path(td) / "globalgamemanagers")

    def test_correct_linear_value(self):
        env = _fake_env(
            [
                Obj(
                    "PlayerSettings",
                    {"m_ActiveColorSpace": 1, "m_ColorGamuts": [0]},
                ),
                Obj("BuildSettings", {"m_Version": "2021.3.45f2"}),
                Obj(
                    "QualitySettings",
                    {
                        "m_QualitySettings": [
                            {"textureQuality": 3, "pixelLightCount": 0, "antiAliasing": 0}
                        ]
                    },
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                result = read_color_space(fake)
        self.assertEqual(result["active_color_space"]["value"], 1)
        self.assertEqual(result["active_color_space"]["enum_name"], "Linear")
        self.assertEqual(result["engine_version"], "2021.3.45f2")
        self.assertEqual(result["quality_tier_count"], 1)
        self.assertNotIn("m_PathID", json.dumps(result))

    def test_out_of_enum_value_hard_fails(self):
        env = _fake_env(
            [Obj("PlayerSettings", {"m_ActiveColorSpace": 2, "m_ColorGamuts": [0]})]
        )
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                with self.assertRaises(ValueError):
                    read_color_space(fake)

    def test_missing_playersettings_hard_fails(self):
        env = _fake_env([Obj("BuildSettings", {"m_Version": "x"})])
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                with self.assertRaises(ValueError):
                    read_color_space(fake)

    def test_duplicate_playersettings_hard_fails(self):
        tree = {"m_ActiveColorSpace": 1, "m_ColorGamuts": [0]}
        env = _fake_env([Obj("PlayerSettings", tree), Obj("PlayerSettings", tree)])
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                with self.assertRaises(ValueError):
                    read_color_space(fake)

    def test_missing_typetree_key_hard_fails(self):
        env = _fake_env([Obj("PlayerSettings", {"m_ColorGamuts": [0]})])
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                with self.assertRaises(ValueError):
                    read_color_space(fake)

    def test_malformed_gamuts_hard_fails(self):
        env = _fake_env(
            [Obj("PlayerSettings", {"m_ActiveColorSpace": 1, "m_ColorGamuts": "bad"})]
        )
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                with self.assertRaises(ValueError):
                    read_color_space(fake)

    def test_gamut_value_zero_preserved_and_no_path_ids(self):
        env = _fake_env(
            [Obj("PlayerSettings", {"m_ActiveColorSpace": 0, "m_ColorGamuts": [0]})]
        )
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                result = read_color_space(fake)
        self.assertEqual(result["color_gamuts"], [0])
        blob = json.dumps(result)
        self.assertNotIn("m_PathID", blob)
        self.assertNotIn("m_Script", blob)

    def test_object_names_never_in_output(self):
        env = _fake_env(
            [Obj("PlayerSettings", {"m_ActiveColorSpace": 1, "m_ColorGamuts": [0]})]
        )
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "globalgamemanagers"
            fake.write_bytes(b"")
            with patch("scripts.probe_w2_color_space_settings.UnityPy.load", return_value=env):
                result = read_color_space(fake)
        blob = json.dumps(result).lower()
        for forbidden in ("skin_amplify", "glasswater", "speedtree"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
