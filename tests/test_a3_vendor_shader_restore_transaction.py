"""A3 RENDER-002 synthetic restore transaction regressions (no Unity/vendor downloads).

Exercise the *production* shared restore() used by TMP, PostFX and volumetric
shaders. Original shaders and .meta GUIDs must survive every failed restore.
"""
from pathlib import Path
import hashlib
import tempfile
import unittest
from unittest.mock import patch

from scripts.restore_tmp_shaders import restore, ROOT, generated_vendor_shader_meta


class A3VendorShaderTransactionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'project'
        self.backup = self.root / 'backup'
        folder = self.project / 'Assets/Shaders'
        folder.mkdir(parents=True)
        self.targets = []
        self.shaders = {}
        for i, name in enumerate(('TextMeshPro/Fixture A', 'TextMeshPro/Fixture B')):
            target = folder / ('fixture' + str(i) + '.shader')
            source = 'Shader "' + name + '" { SubShader { Pass { } } }\n'
            target.write_text(source, encoding='utf-8')
            Path(str(target) + '.meta').write_bytes(('guid: ' + str(i+1) * 32 + '\n').encode())
            self.targets.append(target)
            self.shaders[name] = 'Shader "' + name + '" {\n#include "Fixture.cginc"\n}\n'
        self.include = self.project / ROOT / 'Fixture.cginc'
        self.notice = self.project / ROOT / 'LICENSE.md'
        self.original = {p: (p.read_bytes(), Path(str(p)+'.meta').read_bytes()) for p in self.targets}

    def add_missing_vendor(self):
        name = 'TextMeshPro/Mobile/Synthetic additional'
        self.shaders[name] = 'Shader "' + name + '" { SubShader { Pass {} } }'
        path = self.project / ROOT / ('vendor-' + hashlib.sha256(name.encode()).hexdigest()[:16] + '.shader')
        return name, path

    def run_restore(self):
        return restore(self.project, self.backup, self.shaders,
                       {'Fixture.cginc': '// synthetic include only\n'}, b'synthetic-license')

    def assert_originals_intact(self):
        for path, (original, meta) in self.original.items():
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(Path(str(path) + '.meta').read_bytes(), meta)

    def test_normal_two_shader_restore_keeps_meta_and_exclusive_backup(self):
        self.assertEqual(self.run_restore(), 2)
        for target, (original, meta) in self.original.items():
            self.assertEqual(Path(str(target) + '.meta').read_bytes(), meta)
            self.assertEqual((self.backup / target.relative_to(self.project/'Assets')).read_bytes(), original)
            self.assertIn(ROOT + 'Fixture.cginc', target.read_text())
        self.assertEqual(self.include.read_bytes(), b'// synthetic include only\n')
        self.assertEqual(self.notice.read_bytes(), b'synthetic-license')

    def test_include_parent_symlink_is_rejected_without_touching_outside(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.project / 'Assets/RaftAndroid').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, '(?i)unsafe|symlink'):
            self.run_restore()
        self.assert_originals_intact()
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse(self.backup.exists())

    def test_later_shader_write_failure_restores_originals_and_removes_new_dependencies(self):
        fail_target = self.targets[1]
        original_write_text = Path.write_text
        def inject(path, *args, **kwargs):
            if path == fail_target:
                raise OSError('synthetic second-shader write failure')
            return original_write_text(path, *args, **kwargs)
        with patch.object(Path, 'write_text', inject):
            with self.assertRaisesRegex(OSError, 'second-shader'):
                self.run_restore()
        self.assert_originals_intact()
        self.assertFalse(self.include.exists(), 'failed restore left an include that can shadow real shader imports')
        self.assertFalse(self.notice.exists(), 'failed restore left a partial vendor notice')

    def test_partial_backup_failure_cleans_own_backup_before_mutating_export(self):
        bad_backup_meta = self.backup / 'Shaders/fixture1.shader.meta'
        original_write_bytes = Path.write_bytes
        def inject(path, data):
            if path == bad_backup_meta:
                raise OSError('synthetic backup write failure')
            return original_write_bytes(path, data)
        with patch.object(Path, 'write_bytes', inject):
            with self.assertRaisesRegex(OSError, 'backup write'):
                self.run_restore()
        self.assert_originals_intact()
        self.assertFalse(self.backup.exists(), 'incomplete external backup could block safe retry')
        self.assertFalse(self.include.exists())

    def test_existing_byte_identical_include_is_preserved_on_failed_restore(self):
        self.include.parent.mkdir(parents=True)
        self.include.write_bytes(b'// synthetic include only\n')
        fail_target = self.targets[1]
        original_write_text = Path.write_text
        def inject(path, *args, **kwargs):
            if path == fail_target:
                raise OSError('synthetic failure after original include')
            return original_write_text(path, *args, **kwargs)
        with patch.object(Path, 'write_text', inject):
            with self.assertRaises(OSError):
                self.run_restore()
        self.assert_originals_intact()
        self.assertEqual(self.include.read_bytes(), b'// synthetic include only\n')
        self.assertFalse(self.notice.exists())

    def test_missing_vendor_shader_and_meta_are_a_stable_pair(self):
        name, path = self.add_missing_vendor()
        self.assertEqual(self.run_restore(), 2)
        self.assertTrue(path.is_file())
        guid, meta = generated_vendor_shader_meta(name, ROOT)
        self.assertEqual(Path(str(path) + '.meta').read_bytes(), meta)
        self.assertEqual(len(guid), 32)
        for original, (_, old_meta) in self.original.items():
            self.assertEqual(Path(str(original) + '.meta').read_bytes(), old_meta)
        # Retrying the same temporary export must not treat added vendor files as originals.
        self.assertEqual(restore(self.project, self.root / 'retry-backup', self.shaders,
                                 {'Fixture.cginc': '// synthetic include only\n'}, b'synthetic-license'), 2)
        self.assertEqual(Path(str(path) + '.meta').read_bytes(), meta)

    def test_original_meta_guid_collision_rejected_before_backup(self):
        name, path = self.add_missing_vendor()
        guid, _ = generated_vendor_shader_meta(name, ROOT)
        other = self.project / 'Assets' / 'unrelated.asset.meta'
        other.write_text('fileFormatVersion: 2\nguid: ' + guid + '\n')
        with self.assertRaisesRegex(ValueError, 'GUID collision'):
            self.run_restore()
        self.assert_originals_intact()
        self.assertFalse(self.backup.exists())
        self.assertFalse(path.exists())
        self.assertFalse(Path(str(path) + '.meta').exists())

    def test_conflicting_existing_generated_meta_rejected_without_writes(self):
        _, path = self.add_missing_vendor()
        path.parent.mkdir(parents=True)
        meta = Path(str(path) + '.meta')
        meta.write_text('guid: ' + 'f'*32 + '\n')
        with self.assertRaisesRegex(ValueError, 'Conflicting vendor'):
            self.run_restore()
        self.assert_originals_intact()
        self.assertFalse(self.backup.exists())
        self.assertFalse(path.exists())
        self.assertEqual(meta.read_text(), 'guid: ' + 'f'*32 + '\n')

    def test_late_shader_failure_removes_generated_shader_and_meta(self):
        _, path = self.add_missing_vendor()
        fail_target = self.targets[1]
        original_write_text = Path.write_text
        def inject(target, *args, **kwargs):
            if target == fail_target:
                raise OSError('synthetic failure after generated sidecar')
            return original_write_text(target, *args, **kwargs)
        with patch.object(Path, 'write_text', inject):
            with self.assertRaisesRegex(OSError, 'generated sidecar'):
                self.run_restore()
        self.assert_originals_intact()
        self.assertFalse(path.exists())
        self.assertFalse(Path(str(path) + '.meta').exists())



if __name__ == '__main__':
    unittest.main()
