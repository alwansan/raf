"""Cheap source-policy checks for the Android-only local test overlay.

These tests do not substitute for a Unity/Android runtime or frame profiler.
"""
from pathlib import Path
import unittest


SOURCE = (Path(__file__).resolve().parents[1] /
          "android-port/Runtime/Platform/AndroidTestDiagnostics.cs")


class AndroidDiagnosticsPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_only_android_player_compiles_overlay(self):
        self.assertTrue(self.source.startswith("#if UNITY_ANDROID && !UNITY_EDITOR"))
        self.assertIn("Application.logMessageReceivedThreaded += Capture;", self.source)

    def test_overlay_uses_cached_bounded_preview(self):
        ui = self.source.split("private void OnGUI()", 1)[1]
        self.assertIn("RefreshReport();", ui)
        self.assertIn("GUILayout.Label(visibleReport);", ui)
        self.assertNotIn("GUILayout.Label(Report());", ui)
        self.assertNotIn("new StringBuilder()", ui)
        self.assertIn("VisibleReportLimit = 8000", self.source)
        self.assertIn("fullReport.Substring(fullReport.Length - VisibleReportLimit)", self.source)

    def test_clipboard_keeps_full_report(self):
        self.assertIn("GUIUtility.systemCopyBuffer = fullReport;", self.source)
        self.assertIn("if (reportRevision == version && reportScene == scene) return;", self.source)
        self.assertIn("snapshot = events.ToArray();", self.source)
        self.assertIn("reportRevision = version;", self.source)
        self.assertIn("reportScene = scene;", self.source)

    def test_pause_event_is_persisted_before_flush(self):
        pause = self.source.split("private void OnApplicationPause(bool paused)", 1)[1]
        pause = pause.split("private void OnApplicationFocus", 1)[0]
        self.assertLess(pause.index('AndroidRuntimeLog.Write("lifecycle", "pause"'),
                        pause.index("AndroidRuntimeLog.Flush();"))
        self.assertIn("if (!paused) EnforceLandscape();", pause)

    def test_bounded_thread_safe_capture(self):
        self.assertIn("if (entry.Length > 3000) entry = entry.Substring(0, 3000);", self.source)
        self.assertIn("while (events.Count > 48) events.Dequeue();", self.source)
        self.assertGreaterEqual(self.source.count("eventRevision++;"), 2)
        self.assertIn("lock (gate)", self.source)
        self.assertIn('message = message ?? "";', self.source)
        self.assertIn('stack = stack ?? "";', self.source)


    def test_gpu_memory_diagnostics_are_per_app_and_explicitly_bounded(self):
        # Android Debug.MemoryInfo may exclude protected graphics allocations.
        # This is a process summary, NOT total GPU usage or the MIUIScout value.
        self.assertIn('new AndroidJavaObject("android.os.Debug$MemoryInfo")', self.source)
        self.assertIn('debug.CallStatic("getMemoryInfo", info);', self.source)
        self.assertIn('info.Call<string>("getMemoryStat", "summary.graphics")', self.source)
        self.assertIn('if (version.GetStatic<int>("SDK_INT") < 23)', self.source)
        self.assertIn('"; android_debug_graphics_kb=" + lastAndroidGraphicsKb', self.source)
        self.assertIn('"; android_debug_graphics_kb=" + AndroidGraphicsMemoryKb()', self.source)
        self.assertIn('nextGraphicsMemoryProbe = Time.realtimeSinceStartup + 10f;', self.source)
        self.assertIn('if (Time.realtimeSinceStartup >= nextGraphicsMemoryProbe)', self.source)
        self.assertIn('if (!Debug.isDebugBuild) return "unavailable";', self.source)
        self.assertIn('Profiler.GetAllocatedMemoryForGraphicsDriver()', self.source)
        self.assertIn('"; unity_driver_graphics_bytes=" + UnityGraphicsDriverBytes()', self.source)


if __name__ == "__main__":
    unittest.main()
