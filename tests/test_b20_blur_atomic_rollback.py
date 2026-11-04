"""B20: failure-injected atomic rollback of transient original Blur export.

All shader text is synthetic and private source bytes are never read/logged.
"""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.a12_probe_original_blur_passes import TARGET
from scripts.b45_install_original_blur import install


ORIGINAL = ('Shader "' + TARGET + '" { SubShader { Pass {} } }\n').encode()
CANDIDATE = ('Shader "' + TARGET + '" { SubShader { Pass {} Pass {} } }\n').encode()
META = b"fileFormatVersion: 2\nguid: " + b"1" * 32 + b"\n"


def fixture(root):
    base = Path(root)
    project = base / "Export" ; (project / "Assets").mkdir(parents=True)
    target = project / "Assets" / "Blur.shader"
    target.write_bytes(ORIGINAL)
    Path(str(target) + ".meta").write_bytes(META)
    candidate = base / "private.shader"; candidate.write_bytes(CANDIDATE)
    return project, target, candidate, base / "pristine-backup"


class B20AtomicBlurRollback(unittest.TestCase):
    def attempt(self, project, candidate, backup):
        with mock.patch("scripts.b45_install_original_blur.CANDIDATE_SHA256",
                        hashlib.sha256(CANDIDATE).hexdigest()), \
             mock.patch("scripts.b45_install_original_blur.CANDIDATE_BYTES",
                        len(CANDIDATE)):
            return install(project, candidate, backup)

    def test_successful_install_preserves_meta_and_external_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            project, target, candidate, backup = fixture(temp)
            self.assertTrue(self.attempt(project, candidate, backup)["original_export_guid_unchanged"])
            self.assertEqual(target.read_bytes(), CANDIDATE)
            self.assertEqual(Path(str(target) + ".meta").read_bytes(), META)
            self.assertEqual((backup / "original.shader").read_bytes(), ORIGINAL)

    def test_corrupted_postpromote_candidate_rolls_back_by_atomic_rename(self):
        with tempfile.TemporaryDirectory() as temp:
            project, target, candidate, backup = fixture(temp)
            genuine_replace = os.replace
            destinations = []

            def corrupt_after_first_rename(source, destination):
                genuine_replace(source, destination)
                destinations.append(destination)
                if len(destinations) == 1:
                    Path(destination).write_bytes(b"simulated post-promotion corruption")

            with mock.patch("scripts.b45_install_original_blur.os.replace",
                            side_effect=corrupt_after_first_rename):
                with self.assertRaisesRegex(ValueError, "Installed original Blur"):
                    self.attempt(project, candidate, backup)
            self.assertEqual(len(destinations), 2)
            self.assertEqual(target.read_bytes(), ORIGINAL)
            self.assertEqual(Path(str(target) + ".meta").read_bytes(), META)
            self.assertEqual((backup / "original.shader").read_bytes(), ORIGINAL)
            self.assertFalse(list(target.parent.glob(".b20-blur-restore-*")))

    def test_failed_atomic_rollback_keeps_pristine_backup_and_exposes_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            project, target, candidate, backup = fixture(temp)
            genuine_replace = os.replace
            calls = []

            def fail_second_rename(source, destination):
                calls.append(destination)
                if len(calls) == 2:
                    raise OSError("synthetic rollback rename rejected")
                genuine_replace(source, destination)
                Path(destination).write_bytes(b"simulated post-promotion corruption")

            with mock.patch("scripts.b45_install_original_blur.os.replace",
                            side_effect=fail_second_rename):
                with self.assertRaisesRegex(RuntimeError, "rollback failed"):
                    self.attempt(project, candidate, backup)
            self.assertEqual(len(calls), 2)
            self.assertEqual((backup / "original.shader").read_bytes(), ORIGINAL)
            self.assertEqual((backup / "original.shader.meta").read_bytes(), META)
            self.assertNotEqual(target.read_bytes(), ORIGINAL)
            self.assertFalse(list(target.parent.glob(".b20-blur-restore-*")))

    def test_preinstall_failed_rename_never_mutates_exported_original(self):
        with tempfile.TemporaryDirectory() as temp:
            project, target, candidate, backup = fixture(temp)
            with mock.patch("scripts.b45_install_original_blur.os.replace",
                            side_effect=OSError("synthetic first rename rejection")):
                with self.assertRaises(OSError):
                    self.attempt(project, candidate, backup)
            self.assertEqual(target.read_bytes(), ORIGINAL)
            self.assertEqual((backup / "original.shader").read_bytes(), ORIGINAL)
            self.assertEqual(Path(str(target) + ".meta").read_bytes(), META)
            self.assertFalse(list(target.parent.glob(".b45-blur-*")))


if __name__ == "__main__":
    unittest.main()
