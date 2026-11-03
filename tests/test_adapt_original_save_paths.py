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
