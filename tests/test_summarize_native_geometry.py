import json
import unittest
from scripts.summarize_native_geometry import inspect_log, compare, target_names, comparison_targets


class NativeGeometrySummaryTests(unittest.TestCase):
    def test_global_recovery_targets_every_previous_failure_including_unmatched_headers(self):
        self.assertEqual(comparison_targets({}, 'all', {'A', 'Unknown'}), {'A', 'Unknown'})

    def test_select_actual_incremental_stream_not_historical_target(self):
        matches = {'A': [{'source': 'sharedassets24.assets', 'stream_file': 'sharedassets24.assets.resS'}],
                   'B': [{'source': 'sharedassets29.assets', 'stream_file': 'sharedassets29.assets.resS'}]}
        self.assertEqual(target_names(matches, 'sharedassets24.assets.resS'), {'A'})

    def test_nonfinite_names_and_lines_are_distinct(self):
        line = 'Failed extracting collision mesh because vertex contains a non-finite value (nan). Mesh asset path "Assets/Mesh/A.asset"'
        report, broad, bad = inspect_log([line, line, 'Mesh asset path "Assets/Mesh/B.asset"'])
        self.assertEqual(report['counts']['nonfinite_lines'], 2)
        self.assertEqual(bad, {'A'})
        self.assertEqual(broad, {'A', 'B'})

    def test_shell_echo_is_not_a_native_build_result(self):
        report, _, _ = inspect_log(['2026-10-30T20:00:00Z echo RAFT_ANDROID_NATIVE_RESULT result=Succeeded errors=0 bytes=1'])
        self.assertIsNone(report['native_result'])

    def test_native_report_size_is_separate_from_apk_bytes(self):
        apk = {'apk_bytes': 50, 'apk_sha256': 'a' * 64, 'abis': ['arm64-v8a'],
               'arm64_il2cpp': True, 'fmod_native_library_present': False, 'unity_data_files': 2}
        report, _, _ = inspect_log(['RAFT_ANDROID_NATIVE_RESULT result=Succeeded errors=12 bytes=100',
                                    'RAFT_ANDROID_APK_STRUCTURE ' + json.dumps(apk)])
        self.assertEqual(report['native_result']['build_report_bytes'], 100)
        self.assertEqual(report['apk_structure']['apk_bytes'], 50)

    def test_diff_tracks_regressions_and_targeted_residual_errors(self):
        before = ({}, {'A', 'B'}, {'A', 'B'})
        after = ({}, {'B', 'C'}, {'B', 'C'})
        report = compare(before, after, {'A', 'B'})
        self.assertEqual(report['removed_nonfinite_names'], 1)
        self.assertEqual(report['new_nonfinite_names'], 1)
        self.assertEqual(report['targeted_nonfinite_names_after'], 1)
        self.assertEqual(report['new_nonfinite_names_already_failed_other_categories'], 0)

    def test_new_nonfinite_category_does_not_mean_a_new_failed_mesh(self):
        report = compare(({}, {'A', 'B'}, {'A'}), ({}, {'B'}, {'B'}), {'A'})
        self.assertEqual(report['new_nonfinite_names'], 1)
        self.assertEqual(report['new_nonfinite_names_already_failed_other_categories'], 1)
        self.assertEqual(report['new_broad_error_names'], 0)
