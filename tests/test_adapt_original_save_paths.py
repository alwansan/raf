from collections import Counter
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest
from scripts.adapt_original_save_paths import adapt, apply, fingerprint, SUFFIX


class SavePathTests(unittest.TestCase):
    def test_path_expression_preserves_literal_and_every_other_source_character(self):
        text = 'var path = root + "World\\\\"; var extension = ".rgd";'
        result = adapt(text, fingerprint(text), Counter({'World\\': 1}))
        self.assertEqual(result.replace(SUFFIX, ''), text)
        self.assertIn('"World\\\\"' + SUFFIX, result)
        self.assertEqual(adapt(result, fingerprint(text), Counter({'World\\': 1})), result)

    def test_comment_and_verbatim_content_are_not_path_expressions(self):
        text = '// "C:\\\\example"\n/* "\\\\" */ var a = @"C:\test"; var b = "\\\\";'
        result = adapt(text, fingerprint(text), Counter({'\\': 1}))
        self.assertEqual(result.count(SUFFIX), 1)

    def test_unknown_source_and_path_inventory_fail(self):
        text = 'var path = "World\\\\";'
        with self.assertRaises(ValueError):
            adapt(text)
        with self.assertRaises(ValueError):
            adapt(text, fingerprint(text), Counter({'Player\\': 1}))

    def test_misplaced_existing_adaptation_fails(self):
        text = 'var path = "World\\\\";'
        with self.assertRaises(ValueError):
            adapt(text + SUFFIX, fingerprint(text), Counter({'World\\': 1}))


    def test_symlinked_assets_root_is_rejected_before_original_save_source_is_touched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'project'
            project.mkdir()
            external = root / 'external-originals' / 'Assembly-CSharp'
            external.mkdir(parents=True)
            source = external / 'SaveAndLoad.cs'
            metadata = source.with_suffix('.cs.meta')
            original = b'class SaveAndLoad { /* synthetic only */ }\n'
            meta_bytes = b'guid: synthetic-original\n'
            source.write_bytes(original)
            metadata.write_bytes(meta_bytes)
            try:
                (project / 'Assets').symlink_to(external.parent, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            backup = root / 'backup'
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// synthetic adapted'):
                with self.assertRaisesRegex(ValueError, 'Unsafe.*Assets'):
                    apply(project, backup, write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(metadata.read_bytes(), meta_bytes)
            self.assertFalse(backup.exists())

    def test_dangling_backup_leaf_cannot_redirect_original_save_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            source.write_bytes(b'class SaveAndLoad {}\n')
            meta = source.with_suffix('.cs.meta')
            meta.write_bytes(b'guid: synthetic-save\n')
            backup = root / 'backup'
            backup.mkdir()
            outside = root / 'outside-source.cs'
            try:
                (backup / 'SaveAndLoad.cs').symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest('File symlinks unavailable')
            self.assertFalse((backup / 'SaveAndLoad.cs').exists())
            self.assertTrue((backup / 'SaveAndLoad.cs').is_symlink())
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// synthetic adapted'):
                with self.assertRaisesRegex(ValueError, 'backup'):
                    apply(root / 'project', backup, write=True)
            self.assertFalse(outside.exists())
            self.assertEqual(source.read_bytes(), b'class SaveAndLoad {}\n')
            self.assertEqual(meta.read_bytes(), b'guid: synthetic-save\n')

    def test_successful_original_backup_is_complete_and_guid_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            before = b'class SaveAndLoad {}\n'
            meta_before = b'guid: original-guid-must-not-change\n'
            source.write_bytes(before)
            meta = source.with_suffix('.cs.meta')
            meta.write_bytes(meta_before)
            backup = root / 'backup/original-save'
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                result = apply(root / 'project', backup, write=True)
            self.assertTrue(result['changed'])
            self.assertEqual((backup / source.name).read_bytes(), before)
            self.assertEqual((backup / meta.name).read_bytes(), meta_before)
            self.assertEqual(meta.read_bytes(), meta_before)
            self.assertIn(b'// adapted', source.read_bytes())
            self.assertEqual(len(list(backup.iterdir())), 2)

    def test_interrupted_metadata_backup_has_no_partial_backup_and_can_retry(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            before = b'class SaveAndLoad {}\n'
            source.write_bytes(before)
            meta = source.with_suffix('.cs.meta')
            meta_before = b'guid: genuine\n'
            meta.write_bytes(meta_before)
            backup = root / 'backups/original-save'
            original_copy = shutil.copy2
            copies = 0

            def fail_second_copy(*args, **kwargs):
                nonlocal copies
                copies += 1
                if copies == 2:
                    raise OSError('synthetic second original backup copy failure')
                return original_copy(*args, **kwargs)

            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with patch('scripts.adapt_original_save_paths.shutil.copy2',
                           side_effect=fail_second_copy):
                    with self.assertRaisesRegex(OSError, 'second original backup'):
                        apply(root / 'project', backup, write=True)
                self.assertFalse(backup.exists())
                self.assertEqual(list(backup.parent.iterdir()), [])
                self.assertEqual(source.read_bytes(), before)
                self.assertEqual(meta.read_bytes(), meta_before)
                apply(root / 'project', backup, write=True)
            self.assertEqual((backup / source.name).read_bytes(), before)
            self.assertEqual((backup / meta.name).read_bytes(), meta_before)

    def test_source_write_failure_rolls_back_and_allows_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            before = b'class SaveAndLoad {}\n'
            source.write_bytes(before)
            meta = source.with_suffix('.cs.meta')
            meta_before = b'guid: unmodified\n'
            meta.write_bytes(meta_before)
            backup = root / 'backup'
            original_write = Path.write_bytes
            failed = False

            def torn_write(path, data):
                nonlocal failed
                if path == source and b'// adapted' in data and not failed:
                    failed = True
                    original_write(path, b'partial')
                    raise OSError('synthetic partial source install')
                return original_write(path, data)

            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with patch.object(Path, 'write_bytes', torn_write):
                    with self.assertRaisesRegex(OSError, 'partial source install'):
                        apply(root / 'project', backup, write=True)
                self.assertEqual(source.read_bytes(), before)
                self.assertEqual(meta.read_bytes(), meta_before)
                self.assertFalse(backup.exists())
                apply(root / 'project', backup, write=True)
            self.assertIn(b'// adapted', source.read_bytes())
            self.assertEqual((backup / meta.name).read_bytes(), meta_before)

    def test_existing_empty_backup_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            original = b'class SaveAndLoad {}\n'
            source.write_bytes(original)
            source.with_suffix('.cs.meta').write_bytes(b'guid: original\n')
            backup = root / 'backup'
            backup.mkdir()
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with self.assertRaisesRegex(ValueError, 'backup already exists'):
                    apply(root / 'project', backup, write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(list(backup.iterdir()), [])


    def test_linked_project_root_cannot_redirect_save_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            real = root / 'real-project'
            source = real / 'Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            original = b'class SaveAndLoad {}'
            source.write_bytes(original)
            source.with_suffix('.cs.meta').write_bytes(b'guid: synthetic\\n')
            alias = root / 'linked-project'
            try:
                alias.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            self.assertFalse((alias / 'Assets').is_symlink())
            with self.assertRaisesRegex(ValueError, 'project root'):
                apply(alias, root / 'backup', write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse((root / 'backup').exists())

    def test_linked_backup_root_cannot_redirect_save_backups(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            original = b'class SaveAndLoad {}'
            source.write_bytes(original)
            source.with_suffix('.cs.meta').write_bytes(b'guid: synthetic\\n')
            outside = root / 'outside'
            outside.mkdir()
            backup = root / 'linked-backup'
            try:
                backup.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            with self.assertRaisesRegex(ValueError, 'backup root'):
                apply(root / 'project', backup, write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(list(outside.iterdir()), [])

    def test_linked_backup_ancestor_rejected_before_source_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'project'
            (project / 'Assets').mkdir(parents=True)
            outside = root / 'outside'
            outside.mkdir()
            linked = root / 'linked-parent'
            try:
                linked.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            with self.assertRaisesRegex(ValueError, 'backup root'):
                apply(project, linked / 'backup-folder', write=True)
            self.assertFalse((outside / 'backup-folder').exists())
