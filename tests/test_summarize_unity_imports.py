import unittest
from scripts.summarize_unity_imports import summarize


class ImportSummaryTests(unittest.TestCase):
    def test_repeated_import_identity_and_completed_artifact(self):
        line = '2026-10-31T16:00:00.123Z Start importing Assets/Scenes/Test.unity using Guid(abc) Importer(NativeImporter) -> (artifact id: hidden) in 1 seconds'
        r = summarize([line, line])
        self.assertEqual(r['distinct_import_paths'], 1)
        self.assertEqual(r['asset_import_events'], 2)
        self.assertEqual(r['artifact_or_done_events'], 2)
        self.assertEqual(r['repeated_path_events'], 1)
        self.assertEqual(r['last_imports'][0]['timestamp'], '2026-10-31T16:00:00.123Z')
        self.assertNotIn('hidden', str(r))

    def test_stack_frames_are_not_imported_assets(self):
        r = summarize(['UnityEditor.AssetImporter:SaveAndReimport ()',
                       'UnityEditor.AssetDatabase:Refresh ()'])
        self.assertEqual(r['asset_import_events'], 0)
        self.assertEqual(r['import_method_occurrences']['UnityEditor.AssetImporter:SaveAndReimport'], 1)

    def test_unrecognized_lines_do_not_leak_messages(self):
        r = summarize(['unknown importing secret-token https://secret.example/source',
                       '##[group]echo Start importing Assets/Secret.asset using Guid(x)',
                       'Start importing Assets/../Secret.asset using Guid(x)'])
        self.assertEqual(r['asset_import_events'], 0)
        self.assertNotIn('secret-token', str(r))
        self.assertNotIn('Secret.asset', str(r))

    def test_absent_native_result_is_not_implied_success(self):
        r = summarize(['2026-10-31T16:00:00Z Restarting refresh',
                       '2026-10-31T16:00:01Z The operation was canceled.'])
        self.assertEqual(r['patterns']['refresh_restart']['count'], 1)
        self.assertEqual(r['patterns']['cancel']['count'], 1)
        self.assertEqual(r['distinct_import_paths'], 0)

    def test_engine_diagnostics_redact_arguments(self):
        r = summarize(["Assertion failed on expression: 'secret expression' 123 0xABC"])
        self.assertNotIn('secret expression', str(r))
        self.assertEqual(sum(r['diagnostic_headers'].values()), 1)
