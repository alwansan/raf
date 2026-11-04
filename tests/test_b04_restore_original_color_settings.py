"""Adversarial synthetic tests for the B04 original Linear project-setting boundary."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import b04_restore_original_color_settings as mod

YAML = b"%YAML 1.1\n--- !u!129 &1\nPlayerSettings:\n  m_ObjectHideFlags: 0\n  m_ActiveColorSpace: 0\n  m_CompanyName: Game\n"


class ColorParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "ExportedProject"
        (self.project / "ProjectSettings").mkdir(parents=True)
        self.path = self.project / "ProjectSettings" / "ProjectSettings.asset"
        self.path.write_bytes(YAML)

    def test_exact_one_byte_gamma_to_linear(self):
        report = mod.restore_color_space(self.project, 1, apply=True)
        after = self.path.read_bytes()
        self.assertEqual(report["exported_color_space_before"], 0)
        self.assertTrue(report["changed"])
        self.assertTrue(report["parity_after"])
        self.assertEqual(len(after), len(YAML))
        self.assertEqual(sum(a != b for a, b in zip(YAML, after)), 1)
        self.assertIn(b"m_CompanyName: Game", after)

    def test_dry_run_reports_without_edit(self):
        self.assertFalse(mod.restore_color_space(self.project, 1)["parity_after"])
        self.assertEqual(self.path.read_bytes(), YAML)

    def test_idempotence(self):
        self.assertTrue(mod.restore_color_space(self.project, 1, apply=True)["changed"])
        self.assertFalse(mod.restore_color_space(self.project, 1, apply=True)["changed"])

    def test_crlf_and_non_ascii_bytes_unchanged(self):
        sample = YAML.replace(b"\n", b"\r\n") + "  m_Other: عين\r\n".encode()
        out, seen = mod.patch_settings_bytes(sample, 1)
        self.assertEqual(seen, 0)
        self.assertEqual(len(out), len(sample))
        self.assertEqual(sum(a != b for a, b in zip(sample, out)), 1)

    def test_malformed_or_ambiguous_yaml_rejected_without_mutation(self):
        cases = [
            YAML.replace(b"m_ActiveColorSpace:", b"m_Unknown:"),
            YAML + b"  m_ActiveColorSpace: 1\n",
            YAML.replace(b"m_ActiveColorSpace: 0", b"m_ActiveColorSpace: 2"),
            YAML.replace(b"m_ActiveColorSpace: 0", b"# m_ActiveColorSpace: 0"),
            YAML.replace(b"m_ActiveColorSpace: 0", b"m_ActiveColorSpace: 0 # fake"),
            YAML.replace(b"PlayerSettings:", b"MonoBehaviour:"),
            YAML + b"PlayerSettings:\n",
        ]
        for sample in cases:
            with self.subTest(synthetic_case=len(sample)):
                self.path.write_bytes(sample)
                with self.assertRaises(ValueError):
                    mod.restore_color_space(self.project, 1, apply=True)
                self.assertEqual(self.path.read_bytes(), sample)

    def test_symlink_and_hardlink_rejected(self):
        external = Path(self.temp.name) / "keep"
        external.write_bytes(YAML)
        self.path.unlink()
        self.path.symlink_to(external)
        with self.assertRaises(ValueError):
            mod.restore_color_space(self.project, 1, apply=True)
        self.path.unlink()
        self.path.hardlink_to(external)
        with self.assertRaises(ValueError):
            mod.restore_color_space(self.project, 1, apply=True)
        self.assertEqual(external.read_bytes(), YAML)

    def test_invalid_encoding_nulls_and_size_rejected(self):
        for case in (b"\x00"+YAML, b"\xff"+YAML, b"x"*(mod.MAX_PROJECT_SETTINGS_BYTES+1)):
            with self.subTest(size=len(case)), self.assertRaises(ValueError):
                mod.patch_settings_bytes(case, 1)

    def test_original_digest_and_size_fail_closed(self):
        original = Path(self.temp.name) / "globalgamemanagers"
        original.write_bytes(b"synthetic")
        with self.assertRaises(ValueError):
            mod.original_color_space(original)
        with mock.patch.object(mod, "ORIGINAL_SIZE", 9):
            with self.assertRaises(ValueError):
                mod.original_color_space(original)

    def test_original_typetree_must_match_linear_and_version(self):
        original = Path(self.temp.name) / "globalgamemanagers"
        original.write_bytes(b"synthetic")
        pinned = hashlib.sha256(original.read_bytes()).hexdigest()
        valid = {"active_color_space": {"value": 1},
                 "engine_version": "2021.3.45f2", "color_gamuts": [0]}
        with mock.patch.object(mod, "ORIGINAL_SIZE", len(b"synthetic")), \
             mock.patch.object(mod, "ORIGINAL_SHA256", pinned):
            with mock.patch("scripts.probe_w2_color_space_settings.read_color_space", return_value=valid):
                self.assertEqual(mod.original_color_space(original), 1)
            for invalid in ({**valid, "active_color_space": {"value": 0}},
                            {**valid, "engine_version": "other"},
                            {**valid, "color_gamuts": [1]}):
                with mock.patch("scripts.probe_w2_color_space_settings.read_color_space", return_value=invalid):
                    with self.assertRaises(ValueError):
                        mod.original_color_space(original)


if __name__ == "__main__":
    unittest.main()
