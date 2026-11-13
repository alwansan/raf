import hashlib
import json
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
        self.trace = self.root / 'private-trace.json'
        self.lineage = {
            'schema_version': 1,
            'export_instance': 'a' * 32,
            'objects': [{
                'class_id': 48,
                'source': {'owner': subject.SOURCE_IDENTITY[0], 'path_id': subject.SOURCE_IDENTITY[1]},
                'exportable': True,
                'export': {'file_id': 4800000, 'guid': '1234567890abcdef1234567890abcdef', 'type': 3},
            }],
        }
        self.trace.write_text(json.dumps(self.lineage))
        self.pin = patch.object(subject, 'WRAPPER_SHA256', hashlib.sha256(self.content).hexdigest())
        self.pin.start()
        self.addCleanup(self.pin.stop)

    def run_install(self):
        return subject.install(self.project, self.source, self.backup, self.trace)

    def test_preserves_guid_and_other_assets(self):
        other = self.assets / 'unrelated.mat'
        other.write_bytes(b'unchanged')
        report = self.run_install()
        self.assertEqual(report['installed_targets'], 1)
        self.assertTrue(report['source_shader_guid_matches_same_instance_trace'])
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

    def test_trace_mismatch_rejected_before_mutation(self):
        self.lineage['objects'][0]['export']['guid'] = 'b' * 32
        self.trace.write_text(json.dumps(self.lineage))
        with self.assertRaisesRegex(ValueError, 'does not match the traced source GUID'):
            self.run_install()
        self.assertEqual(self.target.read_bytes(), self.original)
        self.assertFalse(self.backup.exists())

    def test_another_shader_cannot_share_the_traced_guid(self):
        original = self.lineage['objects'][0]
        self.lineage['objects'].append({
            **original, 'source': {**original['source'], 'path_id': subject.SOURCE_IDENTITY[1] + 1},
        })
        self.trace.write_text(json.dumps(self.lineage))
        with self.assertRaisesRegex(ValueError, 'Ambiguous original Depth Copy export GUID'):
            self.run_install()
        self.assertEqual(self.target.read_bytes(), self.original)
        self.assertFalse(self.backup.exists())

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
