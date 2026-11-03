import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import w1_install_depth_copy as subject


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.assets = self.project / 'Assets'
        self.assets.mkdir(parents=True)
        self.target = self.assets / 'export.shader'
        self.original = ('Shader "' + subject.TARGET + '" { SubShader {} }').encode()
        self.target.write_bytes(self.original)
        self.meta = Path(str(self.target) + '.meta')
        self.metadata = b'fileFormatVersion: 2\nguid: 1234567890abcdef1234567890abcdef\n'
        self.meta.write_bytes(self.metadata)
        self.source = self.root / 'private.shader'
        self.content = self.original + b'\n// synthetic reconstruction fixture\n'
        self.source.write_bytes(self.content)
        self.backup = self.root / 'backup'
        self.pin = patch.object(subject, 'WRAPPER_SHA256', hashlib.sha256(self.content).hexdigest())
        self.pin.start()
        self.addCleanup(self.pin.stop)

    def run_install(self):
        return subject.install(self.project, self.source, self.backup)

    def test_preserves_guid_and_other_assets(self):
        other = self.assets / 'unrelated.mat'
        other.write_bytes(b'unchanged')
        self.assertEqual(self.run_install()['installed_targets'], 1)
        self.assertEqual(self.target.read_bytes(), self.content)
        self.assertEqual(self.meta.read_bytes(), self.metadata)
        self.assertEqual(other.read_bytes(), b'unchanged')
        self.assertEqual((self.backup / 'original.shader').read_bytes(), self.original)

    def test_bad_pin_rejected_before_mutation(self):
        self.source.write_bytes(b'wrong')
        with self.assertRaises(ValueError): self.run_install()
        self.assertEqual(self.target.read_bytes(), self.original)
        self.assertFalse(self.backup.exists())

    def test_duplicate_identity_rejected(self):
        (self.assets / 'duplicate.shader').write_bytes(self.original)
        with self.assertRaises(ValueError): self.run_install()
        self.assertFalse(self.backup.exists())

    def test_missing_identity_rejected(self):
        self.target.write_text('Shader "unrelated" {}')
        with self.assertRaises(ValueError): self.run_install()

    def test_missing_meta_rejected(self):
        self.meta.unlink()
        with self.assertRaises(OSError): self.run_install()
        self.assertEqual(self.target.read_bytes(), self.original)

    def test_backup_inside_project_rejected(self):
        self.backup = self.project / 'backup'
        with self.assertRaises(ValueError): self.run_install()

    def test_partial_write_restores_original(self):
        write = Path.write_bytes
        failed = False
        def partial(path, content):
            nonlocal failed
            if path == self.target and not failed:
                failed = True
                write(path, b'partial')
                raise OSError('synthetic write failure')
            return write(path, content)
        with patch.object(Path, 'write_bytes', partial):
            with self.assertRaises(OSError): self.run_install()
        self.assertEqual(self.target.read_bytes(), self.original)
        self.assertEqual(self.meta.read_bytes(), self.metadata)

    def test_redirect_rejected(self):
        self.target.unlink()
        self.target.symlink_to(self.source)
        with self.assertRaises(ValueError): self.run_install()


if __name__ == '__main__': unittest.main()
