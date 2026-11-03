import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.adapt_android_offline_startup import fingerprint
from scripts.adapt_android_offline_startup import adapt, apply, enter, replace_exact


class AndroidOfflineStartupTests(unittest.TestCase):

    def test_original_android_touch_emulation_is_not_reenabled_as_left_mouse(self):
        # The Android explicit left-touch bridge takes ownership of non-UI touch events.
        # Original CustomInputConfig disabled legacy left-click emulation; the
        # old adapter flipped that setting to true for local sessions.
        original = ('class CustomInputConfig { void OnEnable() { '
                    'Input.simulateMouseWithTouches = false; } }')
        with patch('scripts.adapt_android_offline_startup.PINS',
                   {'CustomInputConfig': fingerprint(original)}):
            changed = adapt('CustomInputConfig', original)
        self.assertEqual(changed, original)
        self.assertNotIn('Input.simulateMouseWithTouches = RaftAndroid.Platform.LocalPlayerIdentity.Enabled', changed)

    def test_touch_policy_refuses_unrecognized_original_assignment(self):
        original = 'class CustomInputConfig { void OnEnable() { Input.simulateMouseWithTouches = true; } }'
        with patch('scripts.adapt_android_offline_startup.PINS',
                   {'CustomInputConfig': fingerprint(original)}):
            with self.assertRaisesRegex(ValueError, 'touch-to-left-mouse policy drift'):
                adapt('CustomInputConfig', original)

    def test_unknown_original_revision_is_refused(self):
        with self.assertRaises(ValueError):
            adapt('SteamManager', 'class SteamManager {}')

    def test_method_anchor_requires_unique_original_signature(self):
        with self.assertRaises(ValueError):
            enter('void Start() {} void Start() {}', 'Start', 'return;')

    def test_call_count_drift_refused(self):
        with self.assertRaises(ValueError):
            replace_exact('native(); native();', 'native();', 'local();')

    def test_later_missing_original_leaves_prior_files_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'project/Assets'
            assets.mkdir(parents=True)
            path = assets / 'SteamManager.cs'
            path.write_text('unrecognized original')
            path.with_suffix('.cs.meta').write_text('original metadata')
            with self.assertRaises(ValueError):
                apply(root / 'project', root / 'backup', True)
            self.assertEqual(path.read_text(), 'unrecognized original')
            self.assertFalse((root / 'backup').exists())

    def test_local_delivery_remains_before_added_remote_boundary(self):
        text = 'void RPC() { DeliverLocal(); if (RemoteConnected()) SendRemote(); }'
        changed = replace_exact(text, 'if (RemoteConnected())', 'if (!LocalEnabled && RemoteConnected())')
        self.assertLess(changed.index('DeliverLocal();'), changed.index('!LocalEnabled'))
        self.assertEqual(changed.count('DeliverLocal();'), 1)

    def test_sdk_homonym_and_absent_helper_meta_are_preserved(self):
        original = 'class Settings { int v = SteamApps.GetAppBuildId(); }'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game = root / 'project/Assets/Scripts/Assembly-CSharp/Settings.cs'
            sdk = root / 'project/Assets/Scripts/SomeSdk/Settings.cs'
            for p in (game, sdk): p.parent.mkdir(parents=True, exist_ok=True)
            game.write_text(original)
            sdk.write_text('unrelated SDK source')
            with patch('scripts.adapt_android_offline_startup.PINS', {'Settings': fingerprint(original)}):
                report = apply(root / 'project', root / 'backup', True)
            self.assertEqual(sdk.read_text(), 'unrelated SDK source')
            self.assertFalse(game.with_suffix('.cs.meta').exists())
            self.assertEqual(report['manufacturedMetas'], 0)
            self.assertEqual((root / 'backup/Settings.cs').read_text(), original)


    def test_symlinked_assets_root_cannot_redirect_original_offline_source(self):
        original = 'class Settings { int v = SteamApps.GetAppBuildId(); }'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / 'project'
            project.mkdir()
            external = root / 'external-game' / 'Scripts' / 'Assembly-CSharp'
            external.mkdir(parents=True)
            source = external / 'Settings.cs'
            meta = source.with_suffix('.cs.meta')
            source.write_text(original)
            meta.write_bytes(b'guid: synthetic-offline\n')
            try:
                (project / 'Assets').symlink_to(external.parent.parent, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            backup = root / 'backup'
            with patch('scripts.adapt_android_offline_startup.PINS',
                       {'Settings': fingerprint(original)}):
                with self.assertRaisesRegex(ValueError, 'Unsafe.*Assets'):
                    apply(project, backup, True)
            self.assertEqual(source.read_text(), original)
            self.assertEqual(meta.read_bytes(), b'guid: synthetic-offline\n')
            self.assertFalse(backup.exists())

    def test_dangling_backup_leaf_cannot_redirect_original_offline_source(self):
        original = 'class Settings { int v = SteamApps.GetAppBuildId(); }'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/Settings.cs'
            source.parent.mkdir(parents=True)
            source.write_text(original)
            meta = source.with_suffix('.cs.meta')
            meta.write_bytes(b'guid: synthetic-settings\n')
            backup = root / 'backup'
            backup.mkdir()
            outside = root / 'outside-settings.cs'
            try:
                (backup / 'Settings.cs').symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest('File symlinks unavailable')
            self.assertFalse((backup / 'Settings.cs').exists())
            self.assertTrue((backup / 'Settings.cs').is_symlink())
            with patch('scripts.adapt_android_offline_startup.PINS',
                       {'Settings': fingerprint(original)}):
                with self.assertRaisesRegex(ValueError, 'backup'):
                    apply(root / 'project', backup, True)
            self.assertFalse(outside.exists())
            self.assertEqual(source.read_text(), original)
            self.assertEqual(meta.read_bytes(), b'guid: synthetic-settings\n')
