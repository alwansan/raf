import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/"gfxlab/unity/Assets/Scripts"
VIEWER=RUNTIME/"GfxMultiViewer.cs"
RECORDER=RUNTIME/"GfxSessionRecorder.cs"
EXPORTER=RUNTIME/"GfxDownloadsZipExporter.cs"
ANDROID=ROOT/"gfxlab/unity/Assets/Plugins/Android/GfxDownloadsBridge.java"
BUILDER=ROOT/"gfxlab/unity/Assets/Editor/GfxMultiAndroidBuilder.cs"

@unittest.skipUnless(
    all(p.is_file() for p in (VIEWER,RECORDER,EXPORTER,ANDROID,BUILDER)),
    "Unity Assets intentionally omitted from source-only sparse checkout"
)
class TestAutomaticDeviceLogExportContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.viewer=VIEWER.read_text()
        cls.recorder=RECORDER.read_text()
        cls.exporter=EXPORTER.read_text()
        cls.android=ANDROID.read_text()
        cls.builder=BUILDER.read_text()

    def test_all_user_selectable_diagnostic_transitions_recorded(self):
        for reason in (
            "model_selected","material_mode_changed","role_changed",
            "channel_changed","sampling_mode_changed",
            "material_surface_changed","spin_toggled","camera_reset",
            "helpers_toggled","export_all_zip_button","periodic_15s_state",
        ):
            with self.subTest(reason=reason):
                self.assertIn(reason,self.viewer)
        self.assertIn('sessionRecorder.RecordState(reason,report)',self.viewer)
        self.assertIn('sessionRecorder.RecordExportResult(ok,exportStatus)',self.viewer)

    def test_threadsafe_unity_log_with_full_error_stacks(self):
        self.assertIn("Application.logMessageReceivedThreaded+=OnUnityLogThreaded",self.recorder)
        self.assertIn("Application.logMessageReceivedThreaded-=OnUnityLogThreaded",self.recorder)
        self.assertIn("lock(queueGate)",self.recorder)
        self.assertIn("stackTrace=item.stackTrace",self.recorder) if "stackTrace=item.stackTrace" in self.recorder else self.assertIn("item.stackTrace",self.recorder)
        self.assertIn("LogType.Exception",self.recorder)
        self.assertIn("LogType.Warning",self.recorder)
        self.assertIn("messagesDropped",self.recorder)
        self.assertIn("SNAPSHOT_WRITE_FAILED",self.recorder)
        self.assertIn("OnApplicationPause(bool paused)",self.recorder)

    def test_jsonl_and_multisession_zip_integrity(self):
        for source in ("events.jsonl","snapshots.jsonl","summary.json"):
            self.assertIn(source,self.recorder)
        self.assertIn("Directory.GetFiles(sessions",self.exporter)
        self.assertIn("SearchOption.AllDirectories",self.exporter)
        self.assertIn("ZipArchiveMode.Create",self.exporter)
        self.assertIn("ZipArchiveMode.Read",self.exporter)
        self.assertIn("sessions/",self.exporter)
        self.assertIn("multi-report.json",self.exporter)
        self.assertIn("Original Shader48 restored: false",self.exporter)

    def test_exact_public_android_downloads_path_not_root_storage(self):
        self.assertIn("Download/Games/cl/test/g/",self.android)
        self.assertIn("/storage/emulated/0/Download/Games/cl/test/g/",self.exporter)
        self.assertIn("MediaStore.Downloads.EXTERNAL_CONTENT_URI",self.android)
        self.assertIn("MediaStore.MediaColumns.RELATIVE_PATH",self.android)
        self.assertIn("MediaStore.MediaColumns.IS_PENDING",self.android)
        self.assertIn("MediaStore.MediaColumns.SIZE",self.android)
        self.assertIn("MEDIASTORE_WRONG_TARGET_PATH",self.android)
        self.assertIn("MEDIASTORE_EXPORTED_ZIP_TRUNCATED",self.android)
        self.assertIn("resolver.delete(uri, null, null)",self.android)
        self.assertNotIn("MANAGE_EXTERNAL_STORAGE",self.android+self.exporter)
        self.assertNotIn("Environment.getExternalStoragePublicDirectory",self.android)

    def test_fallback_keeps_archive_and_reports_failure(self):
        self.assertIn("Private copy retained",self.exporter)
        self.assertIn("DOWNLOADS_ZIP_EXPORT_FAILED",self.exporter)
        self.assertIn("PlatformNotSupportedException",self.exporter)
        self.assertIn("EXPORT FAILED: ",self.viewer)
        self.assertIn("ZIP SAVED: ",self.viewer)

    def test_builder_includes_recorder_and_android_bridge(self):
        self.assertIn("cameraGo.AddComponent<GfxSessionRecorder>()",self.builder)
        self.assertIn("viewer.sessionRecorder=automaticRecorder",self.builder)
        self.assertIn("com.alwansan.raft.graphicslab.autologs",self.builder)
        self.assertIn("GfxLab-Multi-Six-AutoLogs.apk",self.builder)
        self.assertIn('PlayerSettings.bundleVersion="0.5.0"',self.builder)

    def test_diagnostic_shader_is_not_claimed_original(self):
        self.assertIn('private const string Experiment="GFX-MULTI-031"',self.viewer)
        self.assertIn('originalShaderRestored=m.exactShaderRestored',self.viewer)
        self.assertIn("originalShaderRestored=false",self.recorder)
        self.assertIn("devicePixelParityVerified=false",self.recorder)
        self.assertIn("GfxLabChannelDiagnosticNotOriginalShader",self.builder)
