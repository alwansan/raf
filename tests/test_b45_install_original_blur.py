"""B45 synthetic install/rollback tests: never read private game programs."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.a12_probe_original_blur_passes import TARGET
from scripts.b45_install_original_blur import install


META = "fileFormatVersion: 2\\nguid: " + "a" * 32 + "\\n"
PLACEHOLDER = 'Shader "' + TARGET + '" { SubShader { Pass { } } }\\n'
CANDIDATE = 'Shader "' + TARGET + '" { Properties { _Synthetic ("Test", 2D) = "white" {} } SubShader { Pass { } Pass { } } }\\n'


def fixture(root):
    root = Path(root)
    project = root / "Project"
    assets = project / "Assets" / "Shaders"
    assets.mkdir(parents=True)
    original = assets / "Blur.shader"
    original.write_text(PLACEHOLDER)
    (assets / "Blur.shader.meta").write_text(META)
    candidate = root / "original-derived-private.shader"
    candidate.write_text(CANDIDATE)
    backup = root / "pristine-backup"
    return project, original, candidate, backup


class OriginalBlurInstallTests(unittest.TestCase):
    def install_fixture(self, project, candidate, backup):
        with mock.patch("scripts.b45_install_original_blur.CANDIDATE_SHA256", hashlib.sha256(CANDIDATE.encode()).hexdigest()), \\
             mock.patch("scripts.b45_install_original_blur.CANDIDATE_BYTES", len(CANDIDATE.encode())):
            return install(project, candidate, backup)

    def test_install_and_original_guid_byte_for_byte_backup(self):
        with tempfile.TemporaryDirectory() as d:
            project, original, candidate, backup = fixture(d)
            before_meta = Path(str(original) + ".meta").read_bytes()
            result = self.install_fixture(project, candidate, backup)
            self.assertEqual(result["installed_exported_blur_targets"], 1)
            self.assertEqual(original.read_bytes(), CANDIDATE.encode())
            self.assertEqual(Path(str(original) + ".meta").read_bytes(), before_meta)
            self.assertEqual((backup / "original.shader").read_bytes(), PLACEHOLDER.encode())
            self.assertEqual((backup / "original.shader.meta").read_bytes(), before_meta)

    def test_unknown_sha_cannot_mutate_or_create_backup(self):
        with tempfile.TemporaryDirectory() as d:
            project, original, candidate, backup = fixture(d)
            candidate.write_text(CANDIDATE + "unexpected")
            with self.assertRaises(ValueError):
                self.install_fixture(project, candidate, backup)
            self.assertEqual(original.read_bytes(), PLACEHOLDER.encode())
            self.assertFalse(backup.exists())

    def test_missing_meta_and_duplicates_rejected(self):
        for case in ("missing_meta", "duplicated_identity"):
            with tempfile.TemporaryDirectory() as d:
                project, original, candidate, backup = fixture(d)
                if case == "missing_meta":
                    Path(str(original) + ".meta").unlink()
                else:
                    (original.parent / "Duplicate.shader").write_text(PLACEHOLDER)
                with self.subTest(case=case), self.assertRaises(ValueError):
                    self.install_fixture(project, candidate, backup)
                self.assertFalse(backup.exists())

    def test_backup_inside_project_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project, original, candidate, backup = fixture(d)
            with self.assertRaises(ValueError):
                self.install_fixture(project, candidate, project / "Assets" / "backup")
            self.assertEqual(original.read_bytes(), PLACEHOLDER.encode())

    def test_failed_atomic_replacement_preserves_pristine_original_and_backup(self):
        with tempfile.TemporaryDirectory() as d:
            project, original, candidate, backup = fixture(d)
            with mock.patch("scripts.b45_install_original_blur.os.replace", side_effect=OSError("synthetic")):
                with self.assertRaises(OSError):
                    self.install_fixture(project, candidate, backup)
            self.assertEqual(original.read_bytes(), PLACEHOLDER.encode())
            self.assertEqual((backup / "original.shader").read_bytes(), PLACEHOLDER.encode())
            self.assertFalse(list(original.parent.glob(".b45-blur-*")))

    def test_redirected_export_target_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project, original, candidate, backup = fixture(d)
            copied = Path(d) / "outside.shader"
            copied.write_text(PLACEHOLDER)
            original.unlink()
            original.symlink_to(copied)
            with self.assertRaises(ValueError):
                self.install_fixture(project, candidate, backup)
            self.assertEqual(copied.read_bytes(), PLACEHOLDER.encode())
            self.assertFalse(backup.exists())


if __name__ == "__main__":
    unittest.main()
