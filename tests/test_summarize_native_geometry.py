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

    def test_actual_scene_reembedding_audit_is_retained_without_inventing_native_result(self):
        payload = {'applied': True, 'scene_bound_assets': 129,
                   'serialized_objects_before': 1203064, 'serialized_objects_after': 1203064}
        report, _, _ = inspect_log(['RAFT_SCENE_BOUND_ASSET_REEMBED ' + json.dumps(payload)])
        self.assertEqual(report['source_geometry']['RAFT_SCENE_BOUND_ASSET_REEMBED'], payload)
        self.assertIsNone(report['native_result'])

    def test_threaded_scene_errors_are_counted_in_actual_lines(self):
        report, _, _ = inspect_log(['Do not use ReadObjectThreaded on scene objects!'])
        self.assertEqual(report['counts']['threaded_scene_object_error_lines'], 1)

    def test_float_cache_and_buildreport_kv_markers_are_retained(self):
        report, _, _ = inspect_log([
            'RAFT_MICROSPLAT_PROPERTY_TEXTURES originalTables=3 regeneratedFloatCaches=3 originalValuesUnchanged=true',
            'RAFT_BUILDREPORT_DIAGNOSTIC_CLASSES messageOccurrences=20 categories=shader:12,other:8 notEquivalentToSummaryTotalErrors=true'])
        self.assertEqual(report['source_geometry']['RAFT_MICROSPLAT_PROPERTY_TEXTURES']['originalTables'], '3')
        self.assertEqual(report['source_geometry']['RAFT_BUILDREPORT_DIAGNOSTIC_CLASSES']['categories'], 'shader:12,other:8')

    def test_fmod_evidence_preserves_compression_and_device_boundary(self):
        payload = {'arm64RuntimeLibraries': 3, 'requiredExports': True,
                   'javaDescriptorPresent': True, 'exactOriginalStreamingFiles': 9,
                   'compressedBankFiles': 5, 'deviceAudioVerified': False}
        report, _, _ = inspect_log([
            '2026-11-01T02:26:23Z RAFT_FMOD_APK_AUDIT ' + json.dumps(payload),
            'RAFT_FMOD_ORIGINAL_CONFIGURATION version=131605 androidUseOBB=False importType=StreamingAssets bankSubfolderEmpty=True',
            'RAFT_FMOD_PLATFORM_RESOURCE_LOOKUP candidates=15 loaded=15 strategy=exact-original-filenames',
            'RAFT_FMOD_ORIGINAL_SETTINGS settingsPresent=True resourcePlatforms=15 androidPlatforms=1 defaultPlatforms=1 manufacturedSettings=0',
            'RAFT_FMOD_ANDROID_IMPORTERS arm64Libraries=3 editorEnabled=0 originalProvidersPreserved=true'])
        evidence = report['source_geometry']
        self.assertEqual(evidence['RAFT_FMOD_APK_AUDIT'], payload)
        self.assertEqual(evidence['RAFT_FMOD_ORIGINAL_CONFIGURATION']['version'], '131605')
        self.assertEqual(evidence['RAFT_FMOD_PLATFORM_RESOURCE_LOOKUP']['loaded'], '15')
        self.assertEqual(evidence['RAFT_FMOD_ORIGINAL_SETTINGS']['manufacturedSettings'], '0')
        self.assertEqual(evidence['RAFT_FMOD_ANDROID_IMPORTERS']['editorEnabled'], '0')
        self.assertIsNone(report['native_result'])

    def test_echoed_fmod_audit_is_not_execution_evidence(self):
        report, _, _ = inspect_log(['2026-11-01T02:26:23Z print("RAFT_FMOD_APK_AUDIT {}")'])
        self.assertNotIn('RAFT_FMOD_APK_AUDIT', report['source_geometry'])
