"""A13 no-LFS synthetic shader-inventory integrity tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.probe_builtin_export_coverage import inspect


class A13CoverageIntegrityTests(unittest.TestCase):
    def run_probe(self, root):
        archive = root / 'fake-vendor.zip'
        archive.write_bytes(b'synthetic archive placeholder')
        with patch('scripts.probe_builtin_export_coverage.archive_sources',
                   return_value=({'Standard': 'DefaultResourcesExtra/Standard.shader'}, {}, b'notice')):
            return inspect(root / 'export', archive)

    def fixture(self, root, source):
        directory = root / 'export'
        directory.mkdir()
        path = directory / 'a.shader'
        path.write_text(source, encoding='utf-8')
        return path

    def test_line_comment_vendor_identity_is_not_counted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, '// Shader "Standard"\nShader "Private/Water" {}')
            out = self.run_probe(root)
            self.assertEqual((out['counts']['parseable'], out['counts']['exact_vendor_matches'],
                              out['counts']['nonvendor']), (1, 0, 1))
            self.assertFalse(out['full_export_scope_verified'])
            self.assertFalse(out['original_game_identity_authenticated'])
            self.assertFalse(out['shader_names_or_sources_disclosed'])

    def test_block_comment_only_vendor_fails_to_count_as_parseable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, '/* Shader "Standard" */\n// synthetic only')
            out = self.run_probe(root)
            self.assertEqual(out['counts']['parseable'], 0)
            self.assertEqual(out['counts']['exact_vendor_matches'], 0)

    def test_actual_vendor_header_still_matches(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, 'Shader "Standard" { SubShader { Pass {} } }')
            out = self.run_probe(root)
            self.assertEqual(out['counts']['exact_vendor_matches'], 1)
            self.assertEqual(out['vendor_identity_count'], 1)

    def test_same_bytes_moved_changes_path_bound_but_not_old_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shader = self.fixture(root, 'Shader "Custom" {}')
            before = self.run_probe(root)
            folder = shader.parent / 'Moved'
            folder.mkdir()
            shader.rename(folder / shader.name)
            after = self.run_probe(root)
            self.assertEqual(before['ordered_content_digest'], after['ordered_content_digest'])
            self.assertNotEqual(before['path_bound_inventory_digest'], after['path_bound_inventory_digest'])

    def test_duplicate_header_count_only_no_identity_leak(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, 'Shader "Private/Shared" {}')
            (root / 'export/b.shader').write_text('Shader "Private/Shared" {}')
            out = self.run_probe(root)
            self.assertEqual(out['counts']['duplicate_declarations'], 1)
            self.assertNotIn('Private/Shared', str(out))

    def test_bad_utf8_is_not_treated_as_missing_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shader = self.fixture(root, 'Shader "Standard" {}')
            shader.write_bytes(b'\xff\xfe\x00')
            with self.assertRaises(UnicodeDecodeError):
                self.run_probe(root)

    def test_symlinked_shader_source_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.fixture(root, 'Shader "Standard" {}')
            path.unlink()
            outsider = root / 'outside.shader'
            outsider.write_text('Shader "Standard" {}')
            path.symlink_to(outsider)
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                self.run_probe(root)

    def test_empty_export_is_not_positive_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'export').mkdir()
            with self.assertRaisesRegex(ValueError, 'Empty shader inventory'):
                self.run_probe(root)

    def test_no_vendor_archive_substitution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, 'Shader "Standard" {}')
            archive = root / 'bad.zip'
            archive.write_bytes(b'wrong source')
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                inspect(root / 'export', archive)


if __name__ == '__main__':
    unittest.main()
