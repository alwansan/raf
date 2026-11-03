"""A14 synthetic failure injection for external built-in shader backup staging.

Uses no game data, no network and no Unity. Fails before the intended source fix.
"""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import restore_builtin_shaders as restore


class BackupWriteIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / "project"
        self.assets = self.project / "Assets"
        self.assets.mkdir(parents=True)
        self.backup = self.root / "private-original-backup"
        self.shaders = {}
        self.files = {}
        self.originals = {}
        for folder, basename, name in (
            ("Materials", "A.shader", "Fixture/BuiltinA"),
            ("Particles", "B.shader", "Fixture/BuiltinB"),
        ):
            path = self.assets / folder / basename
            path.parent.mkdir(parents=True)
            original = ('Shader "' + name + '" { SubShader { Pass {} } }\n').encode()
            metadata = ('fileFormatVersion: 2\nguid: ' + ('1' if folder == "Materials" else '2') * 32 + '\n').encode()
            path.write_bytes(original)
            Path(str(path) + ".meta").write_bytes(metadata)
            vendor_path = "DefaultResources/" + basename
            self.shaders[name] = vendor_path
            self.files[vendor_path] = 'Shader "' + name + '" { SubShader { Pass { ColorMask RGBA } } }\n'
            self.originals[path] = (original, metadata)

    def restore(self):
        return restore.restore_project(self.project, self.backup, self.shaders, self.files, b"fixture MIT notice")

    def assert_originals_unchanged(self):
        for path, (raw, metadata) in self.originals.items():
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(Path(str(path) + ".meta").read_bytes(), metadata)
        self.assertFalse((self.project / restore.NOTICE).exists())
        self.assertFalse((self.project / restore.ROOT).exists())

    def inject_partial_write(self, target):
        original_open = io.open
        def failing_open(file, mode="r", *args, **kwargs):
            if Path(file) == target and mode in ("wb", "xb"):
                stream = original_open(file, mode, *args, **kwargs)
                try:
                    stream.write(b"partial")
                finally:
                    stream.close()
                raise OSError("A14 injected backup write failure")
            return original_open(file, mode, *args, **kwargs)
        return patch("io.open", side_effect=failing_open)

    def test_partial_second_meta_failure_removes_new_backup_without_mutating_originals(self):
        target = self.backup / "Particles/B.shader.meta"
        with self.inject_partial_write(target):
            with self.assertRaisesRegex(OSError, "A14 injected backup"):
                self.restore()
        self.assertFalse(self.backup.exists(), "newly-created incomplete private backup must be removed")
        self.assert_originals_unchanged()

    def test_partial_first_backup_failure_does_not_leave_exposed_bytes(self):
        target = self.backup / "Materials/A.shader"
        with self.inject_partial_write(target):
            with self.assertRaisesRegex(OSError, "A14 injected backup"):
                self.restore()
        self.assertFalse(self.backup.exists())
        self.assert_originals_unchanged()

    def test_success_keeps_exact_external_original_backups_and_original_meta(self):
        self.assertEqual(self.restore(), 2)
        for path, (raw, meta) in self.originals.items():
            out = self.backup / path.relative_to(self.assets)
            self.assertEqual(out.read_bytes(), raw)
            self.assertEqual(Path(str(out) + ".meta").read_bytes(), meta)
            self.assertEqual(Path(str(path) + ".meta").read_bytes(), meta)
            self.assertNotEqual(path.read_bytes(), raw)

    def test_preexisting_backup_is_never_deleted_or_overwritten(self):
        self.backup.mkdir()
        marker = self.backup / "KEEP"
        marker.write_bytes(b"owner's file")
        with self.assertRaises(FileExistsError):
            self.restore()
        self.assertEqual(marker.read_bytes(), b"owner's file")
        self.assert_originals_unchanged()


if __name__ == "__main__":
    unittest.main()
