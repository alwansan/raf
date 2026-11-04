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


    def test_cheat_original_steam_object_guard_is_local_only_and_preserves_others(self):
        from scripts.probe_original_scene_audio import method_body
        original = (
            'public class Cheat {\n'
            '  public bool AllowCheatsForLocalPlayer() { '
            'string comment = "SteamUser.GetSteamID()"; '
            'return SteamUser.GetSteamID() == LocalPlayer.SteamID; } '
            'public bool Other() { return SteamUser.GetSteamID() == RemoteId; } }'
        )
        body = method_body(original, 'AllowCheatsForLocalPlayer')[1]
        with patch.dict('scripts.adapt_android_offline_startup.PINS',
                        {'Cheat': fingerprint(original)}, clear=True), patch(
                'scripts.adapt_android_offline_startup.CHEAT_METHOD_SHA256', fingerprint(body)):
            changed = adapt('Cheat', original)
        guard = '(RaftAndroid.Platform.LocalPlayerIdentity.Enabled ? ' + (
            'new Steamworks.CSteamID(RaftAndroid.Platform.LocalPlayerIdentity.Current) : '
            'SteamUser.GetSteamID())')
        self.assertIn('return ' + guard + ' == LocalPlayer.SteamID;', changed)
        self.assertIn('public bool Other() { return SteamUser.GetSteamID() == RemoteId; }', changed)
        self.assertIn('"SteamUser.GetSteamID()"', changed)
        self.assertEqual(changed.count(guard), 1)
        self.assertEqual(changed.replace(guard, 'SteamUser.GetSteamID()', 1), original)

    def test_cheat_unknown_original_method_and_duplicate_real_calls_are_refused(self):
        from scripts.probe_original_scene_audio import method_body
        original = (
            'public class Cheat {\n'
            '  public bool AllowCheatsForLocalPlayer() { '
            'var left = SteamUser.GetSteamID(); '
            'var right = SteamUser.GetSteamID(); return left == right; } }'
        )
        body = method_body(original, 'AllowCheatsForLocalPlayer')[1]
        with patch.dict('scripts.adapt_android_offline_startup.PINS',
                        {'Cheat': fingerprint(original)}, clear=True):
            with self.assertRaisesRegex(ValueError, 'Unrecognized original Cheat'):
                adapt('Cheat', original)
            with patch('scripts.adapt_android_offline_startup.CHEAT_METHOD_SHA256', fingerprint(body)):
                with self.assertRaisesRegex(ValueError, 'Cheat Steam identity callsite drift'):
                    adapt('Cheat', original)

    def test_cheat_nonboolean_method_type_is_rejected_even_when_source_digest_matches(self):
        from scripts.probe_original_scene_audio import method_body
        original = (
            'public class Cheat {\n'
            '  public int AllowCheatsForLocalPlayer() { '
            'var sid = SteamUser.GetSteamID(); return 0; } }'
        )
        body = method_body(original, 'AllowCheatsForLocalPlayer')[1]
        with patch.dict('scripts.adapt_android_offline_startup.PINS',
                        {'Cheat': fingerprint(original)}, clear=True), patch(
                'scripts.adapt_android_offline_startup.CHEAT_METHOD_SHA256', fingerprint(body)):
            with self.assertRaisesRegex(ValueError, 'Unrecognized original Cheat'):
                adapt('Cheat', original)


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

    def test_b13_partial_backup_copy_failure_is_retriable_without_source_changes(self):
        from scripts import adapt_android_offline_startup as stage
        import shutil
        originals = {
            'Settings': 'class Settings { int v = SteamApps.GetAppBuildId(); }',
            'RGD_Settings_Character': 'class RGD_Settings_Character { string n = SteamFriends.GetPersonaName(); }',
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'project/Assets/Assembly-CSharp'
            assets.mkdir(parents=True)
            for name, content in originals.items():
                (assets / (name + '.cs')).write_text(content)
                (assets / (name + '.cs.meta')).write_text('guid: synthetic-' + name)
            backup = root / 'backup'
            real_copy = shutil.copy2
            calls = 0

            def partial_copy(src, dst, *args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 3:
                    Path(dst).write_bytes(b'partial synthetic backup')
                    raise OSError('injected backup failure')
                return real_copy(src, dst, *args, **kwargs)

            with patch.dict('scripts.adapt_android_offline_startup.PINS',
                            {n: fingerprint(s) for n, s in originals.items()}, clear=True):
                with patch('scripts.adapt_android_offline_startup.shutil.copy2', side_effect=partial_copy):
                    with self.assertRaisesRegex(OSError, 'injected backup failure'):
                        stage.apply(root / 'project', backup, write=True)
                self.assertFalse(backup.exists(), 'stale partial backups block safe retry')
                for name, content in originals.items():
                    self.assertEqual((assets / (name + '.cs')).read_text(), content)
                    self.assertEqual((assets / (name + '.cs.meta')).read_text(),
                                     'guid: synthetic-' + name)
                report = stage.apply(root / 'project', backup, write=True)
                self.assertTrue(report['applied'])
                self.assertEqual(len(list(backup.iterdir())), 4)
                self.assertEqual((backup / 'Settings.cs').read_text(), originals['Settings'])

    def test_b13_partial_source_write_failure_restores_all_origins_and_removes_backups(self):
        from scripts import adapt_android_offline_startup as stage
        originals = {
            'Settings': 'class Settings { int v = SteamApps.GetAppBuildId(); }',
            'RGD_Settings_Character': 'class RGD_Settings_Character { string n = SteamFriends.GetPersonaName(); }',
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'project/Assets/Assembly-CSharp'
            assets.mkdir(parents=True)
            for name, content in originals.items():
                (assets / (name + '.cs')).write_text(content)
                (assets / (name + '.cs.meta')).write_text('guid: synthetic-' + name)
            backup = root / 'backup'
            real_write = Path.write_bytes
            failed = False
            def broken_write(path, data):
                nonlocal failed
                if path.name == 'RGD_Settings_Character.cs' and not failed:
                    failed = True
                    real_write(path, b'partial synthetic source')
                    raise OSError('injected source failure')
                return real_write(path, data)
            with patch.dict('scripts.adapt_android_offline_startup.PINS',
                            {n: fingerprint(s) for n, s in originals.items()}, clear=True):
                with patch.object(Path, 'write_bytes', broken_write):
                    with self.assertRaisesRegex(OSError, 'injected source failure'):
                        stage.apply(root / 'project', backup, write=True)
                self.assertTrue(failed)
                self.assertFalse(backup.exists())
                for name, content in originals.items():
                    self.assertEqual((assets / (name + '.cs')).read_text(), content)
                    self.assertEqual((assets / (name + '.cs.meta')).read_text(),
                                     'guid: synthetic-' + name)
                self.assertTrue(stage.apply(root / 'project', backup, write=True)['applied'])

    def test_b13_rollback_write_failure_retains_original_backups(self):
        from scripts import adapt_android_offline_startup as stage
        original = 'class Settings { int v = SteamApps.GetAppBuildId(); }'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/Settings.cs'
            source.parent.mkdir(parents=True)
            source.write_text(original)
            source.with_suffix('.cs.meta').write_text('guid: synthetic-settings')
            backup = root / 'backup'
            real_write = Path.write_bytes
            calls = 0
            def broken_write(path, data):
                nonlocal calls
                if path == source:
                    calls += 1
                    if calls == 1:
                        real_write(path, b'partial synthetic source')
                        raise OSError('injected installation failure')
                    if calls == 2:
                        raise OSError('injected rollback failure')
                return real_write(path, data)
            with patch.dict('scripts.adapt_android_offline_startup.PINS',
                            {'Settings': fingerprint(original)}, clear=True):
                with patch.object(Path, 'write_bytes', broken_write):
                    with self.assertRaisesRegex(OSError, 'injected rollback failure'):
                        stage.apply(root / 'project', backup, write=True)
            self.assertEqual((backup / 'Settings.cs').read_text(), original)
            self.assertEqual((backup / 'Settings.cs.meta').read_text(), 'guid: synthetic-settings')
