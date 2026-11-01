from pathlib import Path
import tempfile
import unittest
from scripts.restore_fmod_resource_layout import restore

class LayoutTests(unittest.TestCase):
    def make(self, root):
        resources = root / 'Assets/Resources'
        resources.mkdir(parents=True)
        (resources / 'FMODStudioSettings.asset').write_text('original settings')
        for suffix in [''] + ['_' + str(i) for i in range(14)]:
            name = 'FMODStudioSettingsPlatform' + suffix + '.asset'
            (resources / name).write_text('original data ' + suffix)
            (resources / (name + '.meta')).write_text('guid: original ' + suffix)
        return resources

    def test_exact_move_preserves_every_byte_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); resources = self.make(root)
            original = {p.name: p.read_bytes() for p in resources.iterdir()}
            restore(root, True)
            self.assertEqual((resources / 'FMODStudioSettings.asset').read_bytes(), original['FMODStudioSettings.asset'])
            for name, content in original.items():
                if name != 'FMODStudioSettings.asset':
                    self.assertEqual((resources / 'FMODStudioSettings' / name).read_bytes(), content)
            self.assertEqual(restore(root, True)['platforms'], 15)

    def test_missing_meta_refuses_before_any_move(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); resources = self.make(root)
            (resources / 'FMODStudioSettingsPlatform_13.asset.meta').unlink()
            with self.assertRaises(ValueError): restore(root, True)
            self.assertEqual(len(list(resources.glob('*.asset'))), 16)

    def test_conflict_refuses_before_any_move(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); resources = self.make(root)
            target = resources / 'FMODStudioSettings'; target.mkdir()
            (target / 'FMODStudioSettingsPlatform_13.asset').write_text('conflict')
            with self.assertRaises(ValueError): restore(root, True)
            self.assertEqual(len(list(resources.glob('*.asset'))), 16)

    def test_missing_platform_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); resources = self.make(root)
            (resources / 'FMODStudioSettingsPlatform_13.asset').unlink()
            with self.assertRaises(ValueError): restore(root, True)
