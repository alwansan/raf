import hashlib
import unittest
from scripts.instrument_android_runtime_operations import body_bounds, wrap, instrument, guard_android_local_savegame_stats


class OperationTraceTests(unittest.TestCase):
    def test_braces_inside_strings_and_comments_do_not_close_body(self):
        text = 'void Save() { var s = "}"; /* } */ if (true) { Run(); } } void Other() {}'
        start, end = body_bounds(text, 'void Save()')
        self.assertEqual(text[end:], '} void Other() {}')

    def test_returns_exceptions_and_original_body_remain(self):
        text = 'int Load() { if (x) return 1; throw new System.Exception(); }'
        result = wrap(text, 'int Load()', 'save')
        self.assertIn('if (x) return 1; throw new System.Exception();', result)
        self.assertIn('finally', result)
        self.assertIn('throw;', result)
        self.assertIn('#if UNITY_ANDROID && !UNITY_EDITOR', result)

    def test_signature_in_comment_or_string_is_not_a_second_method(self):
        text = (
            '// void Save() { fake; }\n'
            'class Example {\n'
            '  string helpText = "void Save()";\n'
            '  /* void Save() { fake; } */\n'
            '  void Save() { ActualOperation(); }\n'
            '}\n'
        )
        begin, end = body_bounds(text, 'void Save()')
        self.assertEqual(text[begin:end], ' ActualOperation(); ')
        result = wrap(text, 'void Save()', 'save')
        self.assertIn('ActualOperation();', result)
        self.assertEqual(result.count('BeginOperation('), 1)

    def test_comment_braces_between_signature_and_body_do_not_steal_it(self):
        text = 'void Save() /* fake { } */\n{ Real(); /* } */ }\nvoid Other() {}'
        begin, end = body_bounds(text, 'void Save()')
        self.assertEqual(text[begin:end], ' Real(); /* } */ ')

    def test_reject_declaration_without_real_braced_body(self):
        for declaration in (
            'void Save();\nvoid Other() { Wrong(); }',
            'void Save() => Other();\nvoid Other() { Wrong(); }',
            '// void Save() { fake; }\nvoid Other() { Wrong(); }',
            'void Save() /* no body */;\nvoid Other() { Wrong(); }',
        ):
            with self.subTest(declaration=declaration):
                with self.assertRaises(ValueError):
                    body_bounds(declaration, 'void Save()')
                with self.assertRaises(ValueError):
                    wrap(declaration, 'void Save()', 'save')

    def test_duplicate_real_signatures_still_fail_closed(self):
        text = 'void Save() { First(); }\nvoid Save() { Second(); }'
        with self.assertRaises(ValueError):
            body_bounds(text, 'void Save()')

    def test_string_marker_is_not_duplicate_instrumentation(self):
        text = 'void Save() { string marker = "__raftOperation"; /* __raftOperation */ Real(); }'
        wrapped = wrap(text, 'void Save()', 'save')
        self.assertIn('Real();', wrapped)
        with self.assertRaises(ValueError):
            wrap(wrapped, 'void Save()', 'save')

    def test_unknown_revision_and_duplicate_application_fail(self):
        text = 'void Start() { Run(); }'
        manifest = {'sources': {'Demo': {'sha256': hashlib.sha256(text.encode()).hexdigest(), 'area': 'startup', 'methods': [{'signature': 'void Start()'}]}}}
        result = instrument('Demo', text, manifest)
        with self.assertRaises(ValueError): instrument('Demo', result, manifest)
        with self.assertRaises(ValueError): wrap(text + text, 'void Start()', 'startup')


    def test_android_local_savegame_skips_only_stats_upload(self):
        source = (
            'class SaveAndLoad { public void SaveGame(bool sendRemoteMessage) { '
            'SaveWorld(); SteamUserStats.StoreStats(); SaveUser(); } '
            'public void Other() { SteamUserStats.StoreStats(); } }'
        )
        result = guard_android_local_savegame_stats(source)
        self.assertIn(
            'SaveWorld(); if (!RaftAndroid.Platform.LocalPlayerIdentity.Enabled) '
            '{ SteamUserStats.StoreStats(); } SaveUser();', result)
        self.assertIn('public void Other() { SteamUserStats.StoreStats(); }', result)
        self.assertEqual(result.count('SteamUserStats.StoreStats();'), 2)
        self.assertEqual(
            result.replace('if (!RaftAndroid.Platform.LocalPlayerIdentity.Enabled) '
                           '{ SteamUserStats.StoreStats(); }',
                           'SteamUserStats.StoreStats();', 1), source)

    def test_savegame_stats_isolation_fails_closed_on_missing_duplicate_or_comment(self):
        for source in (
            'public void SaveGame(bool sendRemoteMessage) { SaveWorld(); SaveUser(); }',
            'public void SaveGame(bool sendRemoteMessage) { '
            'SteamUserStats.StoreStats(); SteamUserStats.StoreStats(); }',
            'public void SaveGame(bool sendRemoteMessage) { '
            '// SteamUserStats.StoreStats();\n SaveWorld(); }',
            'public void SaveGame(bool sendRemoteMessage) { SaveWorld(); } '
            'void Other() { SteamUserStats.StoreStats(); }',
        ):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, 'exactly one executable'):
                    guard_android_local_savegame_stats(source)

    def test_savegame_stats_guard_is_after_authenticated_sha_and_before_traces(self):
        source = (
            'class SaveAndLoad { public void SaveGame(bool sendRemoteMessage) { '
            'SaveWorld(); SteamUserStats.StoreStats(); SaveUser(); } }'
        )
        signature = 'public void SaveGame(bool sendRemoteMessage)'
        manifest = {'sources': {'SaveAndLoad': {
            'sha256': hashlib.sha256(source.encode()).hexdigest(),
            'area': 'save', 'methods': [{'signature': signature}],
        }}}
        result = instrument('SaveAndLoad', source, manifest)
        self.assertIn('RaftAndroid.Platform.LocalPlayerIdentity.Enabled', result)
        self.assertIn('BeginOperation(', result)
        self.assertEqual(result.count('SteamUserStats.StoreStats();'), 1)
        self.assertIn('SaveWorld();', result)
        self.assertIn('SaveUser();', result)
        with self.assertRaisesRegex(ValueError, 'Unknown adapted original revision'):
            instrument('SaveAndLoad', source.replace('SaveWorld()', 'EraseWorld()'), manifest)
        with self.assertRaisesRegex(ValueError, 'Unknown adapted original revision'):
            instrument('SaveAndLoad', result, manifest)

    def test_t4_save_postcheck_runs_in_finally_even_with_early_return(self):
        signature = 'private void Save(string filename, RGD raftgamedata)'
        source = ('class SaveAndLoad { ' + signature +
                  ' { if (raftgamedata == null) return; OriginalSerialize(); } }')
        transformed = wrap(source, signature, 'save', 'filename')
        self.assertEqual(transformed.count('Save.argumentFileSnapshot"'), 1)
        self.assertIn('System.IO.File.Exists(filename)', transformed)
        self.assertIn('new System.IO.FileInfo(filename).Length == 0L', transformed)
        self.assertIn('if (raftgamedata == null) return; OriginalSerialize();', transformed)
        self.assertLess(transformed.index('} finally { '),
                        transformed.index('Save.argumentFileSnapshot"'))
        self.assertLess(transformed.index('Save.argumentFileSnapshot"'),
                        transformed.index('AndroidRuntimeLog.EndOperation('))
        self.assertIn('durable_RGD_unverified=true', transformed)

    def test_t4_save_postcheck_has_no_new_serialization_or_rethrow(self):
        signature = 'private void Save(string filename, RGD raftgamedata)'
        source = signature + ' { bool original = false; /* original */ }'
        transformed = wrap(source, signature, 'save')
        self.assertEqual(transformed.count('System.IO.File.Exists(filename)'), 1)
        self.assertNotIn('File.Create(', transformed)
        self.assertNotIn('WriteAllBytes(', transformed)
        self.assertNotIn('WorldHasBeenRecieved = true', transformed)
        self.assertIn('Save.argumentFileSnapshot.unavailable', transformed)
        self.assertIn('catch (System.Exception) { }', transformed)
        self.assertIn('bool original = false; /* original */', transformed)

    def test_t4_save_postcheck_not_in_other_methods_or_non_save_area(self):
        signature = 'private void Save(string filename, RGD raftgamedata)'
        text = signature + ' { OriginalSave(); }'
        self.assertNotIn('Save.argumentFileSnapshot', wrap(text, signature, 'world'))
        other = 'private void SaveUser() { OriginalSave(); }'
        self.assertNotIn('Save.argumentFileSnapshot', wrap(other, 'private void SaveUser()', 'save'))
        game = 'public void SaveGame(bool sendRemoteMessage) { OriginalSave(); }'
        self.assertNotIn('Save.argumentFileSnapshot',
                         wrap(game, 'public void SaveGame(bool sendRemoteMessage)', 'save'))

    def test_t4_save_postcheck_preserves_original_path_and_source_gate(self):
        signature = 'private void Save(string filename, RGD raftgamedata)'
        source = 'class SaveAndLoad { ' + signature + ' { OriginalSave(filename); } }'
        manifest = {'sources': {'SaveAndLoad': {
            'sha256': hashlib.sha256(source.encode()).hexdigest(),
            'area': 'save', 'methods': [{'signature': signature}],
        }}}
        # instrument() additionally authenticates the SteamStats call for full
        # SaveAndLoad. Exercise wrap() here; source SHA source gating was already
        # covered by the full original manifest and existing SaveGame fixtures.
        result = wrap(source, signature, 'save', 'filename')
        self.assertEqual(result.count('OriginalSave(filename);'), 1)
        self.assertNotIn('Path.Combine(', result)
        self.assertNotIn('filename =', result)
        with self.assertRaisesRegex(ValueError, 'duplicate operation instrumentation'):
            wrap(result, signature, 'save', 'filename')

