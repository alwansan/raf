"""Synthetic, nonproprietary adversarial export-fixture checks for B11."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.b11_restore_original_color_gamuts import patch_gamut_bytes, restore_gamut, main

HEADER = '%YAML 1.1\n--- !u!129 &1\nPlayerSettings:\n  m_ActiveColorSpace: 1\n'
TAIL = '  androidStartInFullscreen: 1\n'

def fixture(value='00000000', newline='\n'):
    return (HEADER + '  m_ColorGamuts: ' + value + '\n' + TAIL).replace('\n', newline).encode()

class ExportGamutTests(unittest.TestCase):
    def test_source_already_srgb_is_identical(self):
        before = fixture()
        result, observed = patch_gamut_bytes(before)
        self.assertEqual(result, before)
        self.assertEqual(observed, '00000000')

    def test_single_recognized_alternate_corrects_only_field(self):
        before = fixture('01000000')
        after, observed = patch_gamut_bytes(before)
        self.assertEqual(observed, '01000000')
        self.assertEqual(after, before.replace(b'm_ColorGamuts: 01000000', b'm_ColorGamuts: 00000000'))

    def test_other_enum_corrected_with_crlf(self):
        before = fixture('02000000', '\r\n')
        after, _ = patch_gamut_bytes(before)
        self.assertIn(b'm_ColorGamuts: 00000000\r\n', after)
        self.assertEqual(after.count(b'\r\n'), before.count(b'\r\n'))

    def test_missing_duplicate_or_different_format_rejected(self):
        for before in (fixture().replace(b'm_ColorGamuts', b'OtherValue'),
                       fixture() + b'  m_ColorGamuts: 00000000\n',
                       fixture('0000000000000000'), fixture('0'),
                       fixture('[0]'), fixture('00000000 # comment')):
            with self.subTest(raw=before[-45:]), self.assertRaises(ValueError):
                patch_gamut_bytes(before)

    def test_unexpected_gamut_or_unknown_endianness_rejected(self):
        for value in ('03000000', '00000001', 'FFFFFFFF', 'deadbeef'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                patch_gamut_bytes(fixture(value))

    def test_two_player_objects_and_malformed_utf8_rejected(self):
        for data in (fixture()+fixture(), fixture()+b'\xff', fixture()+b'\x00'):
            with self.assertRaises(ValueError):
                patch_gamut_bytes(data)

    def test_yaml_comment_is_ignored_but_duplicate_field_is_rejected(self):
        commented = fixture() + b'  # m_ColorGamuts: 01000000\n'
        self.assertEqual(patch_gamut_bytes(commented)[0], commented)
        duplicate = fixture() + b'  m_ColorGamuts: "00000000"\n'
        with self.assertRaises(ValueError):
            patch_gamut_bytes(duplicate)

    def _project(self, root, content):
        p = root / 'project' / 'ProjectSettings'
        p.mkdir(parents=True)
        target = p / 'ProjectSettings.asset'
        target.write_bytes(content)
        return root / 'project', target

    def test_apply_atomic_and_dry_run_preserve_other_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            project, target = self._project(Path(d), fixture('01000000'))
            before = target.read_bytes()
            self.assertEqual(restore_gamut(project)['changed'], False)
            self.assertEqual(target.read_bytes(), before)
            result = restore_gamut(project, apply=True)
            self.assertTrue(result['changed'])
            self.assertTrue(result['parity_after'])
            self.assertEqual(target.read_bytes(), before.replace(b'01000000', b'00000000'))
            self.assertFalse(restore_gamut(project, apply=True)['changed'])

    def test_no_mutation_on_unknown_gamut(self):
        with tempfile.TemporaryDirectory() as d:
            project, target = self._project(Path(d), fixture('deadbeef'))
            with self.assertRaises(ValueError):
                restore_gamut(project, apply=True)
            self.assertEqual(target.read_bytes(), fixture('deadbeef'))

    def test_target_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project, target = self._project(root, fixture('01000000'))
            outside = root / 'outside'
            outside.write_bytes(fixture('01000000'))
            target.unlink()
            try:
                target.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest('symlink unavailable')
            with self.assertRaises(ValueError):
                restore_gamut(project, apply=True)
            self.assertEqual(outside.read_bytes(), fixture('01000000'))

    def test_hardlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project, target = self._project(root, fixture('01000000'))
            outside = root / 'other'
            outside.hardlink_to(target)
            with self.assertRaises(ValueError):
                restore_gamut(project, apply=True)
            self.assertEqual(outside.read_bytes(), fixture('01000000'))

    def test_cli_pins_original_before_mutating(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); project,target=self._project(root, fixture('01000000'))
            original=root/'original';original.write_bytes(b'fake')
            with patch('scripts.b11_restore_original_color_gamuts.original_color_space', side_effect=ValueError('unverified')):
                with self.assertRaisesRegex(ValueError, 'unverified'):
                    main(['--original', str(original), '--project', str(project), '--apply'])
            self.assertEqual(target.read_bytes(), fixture('01000000'))

if __name__ == '__main__':
    unittest.main()
