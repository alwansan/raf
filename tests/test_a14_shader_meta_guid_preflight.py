"""A14 CPU-only original exported .meta GUID regression fixtures (synthetic)."""
import tempfile
import unittest
from pathlib import Path
from scripts import restore_builtin_shaders as restorer


class OriginalShaderGuidPreflightTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.project = Path(self.t.name) / "project"
        self.assets = self.project / "Assets"
        self.assets.mkdir(parents=True)
        self.backup = Path(self.t.name) / "external-backup"
        self.shaders, self.files, self.originals = {}, {}, {}
        for letter, guid in (("A", "a"*32), ("B", "b"*32)):
            path = self.assets / "Synthetic" / (letter + ".shader")
            path.parent.mkdir(exist_ok=True)
            name = "Fixture/" + letter
            vendor = "DefaultResources/" + letter + ".shader"
            shader = ('Shader "' + name + '" { SubShader { Pass {} } }\n').encode()
            meta = ("fileFormatVersion: 2\nguid: " + guid +
                    "\nShaderImporter:\n  externalObjects: {}\n").encode()
            path.write_bytes(shader)
            Path(str(path)+".meta").write_bytes(meta)
            self.originals[path] = [shader, meta]
            self.shaders[name] = vendor
            self.files[vendor] = ('Shader "' + name +
                '" { SubShader { Pass { ColorMask RGB } } }\n')

    def set_meta(self, letter, value):
        path = self.assets / "Synthetic" / (letter + ".shader")
        Path(str(path)+".meta").write_bytes(value)
        self.originals[path][1] = value

    def run_restore(self):
        return restorer.restore_project(
            self.project, self.backup, self.shaders, self.files, b"fixture license")

    def assert_unmodified(self):
        self.assertFalse(self.backup.exists())
        self.assertFalse((self.project/restorer.ROOT).exists())
        self.assertFalse((self.project/restorer.NOTICE).exists())
        for path, (shader, meta) in self.originals.items():
            self.assertEqual(path.read_bytes(), shader)
            self.assertEqual(Path(str(path)+".meta").read_bytes(), meta)

    def test_valid_unique_guids_preserve_exact_meta(self):
        self.set_meta("A", b"fileFormatVersion: 2\r\nguid: " + b"A"*32 +
            b"\r\nShaderImporter:\r\n  externalObjects:\r\n    - guid: " + b"c"*32 + b"\r\n")
        self.assertEqual(self.run_restore(), 2)
        for path, (_, meta) in self.originals.items():
            saved = self.backup / path.relative_to(self.assets)
            self.assertEqual(Path(str(saved)+".meta").read_bytes(), meta)
            self.assertEqual(Path(str(path)+".meta").read_bytes(), meta)

    def test_duplicate_casefold_guid_refused_before_backup(self):
        self.set_meta("B", b"fileFormatVersion: 2\nguid: " + b"A"*32 + b"\n")
        with self.assertRaisesRegex(ValueError, "Duplicate original shader metadata GUID"):
            self.run_restore()
        self.assert_unmodified()

    def test_malformed_guid_refused_before_backup(self):
        self.set_meta("B", b"fileFormatVersion: 2\nguid: invalid\n")
        with self.assertRaisesRegex(ValueError, "Malformed original shader metadata GUID"):
            self.run_restore()
        self.assert_unmodified()

    def test_missing_guid_refused_before_backup(self):
        self.set_meta("B", b"fileFormatVersion: 2\nShaderImporter:\n")
        with self.assertRaisesRegex(ValueError, "Missing or ambiguous original shader metadata GUID"):
            self.run_restore()
        self.assert_unmodified()

    def test_repeated_guid_refused_before_backup(self):
        self.set_meta("B", b"guid: " + b"b"*32 + b"\nguid: " + b"c"*32 + b"\n")
        with self.assertRaisesRegex(ValueError, "Missing or ambiguous original shader metadata GUID"):
            self.run_restore()
        self.assert_unmodified()


if __name__ == "__main__":
    unittest.main()
