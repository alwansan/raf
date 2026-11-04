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


    def test_scene_boundaries_and_low_memory_capture_partial_gpu_counters(self):
        # The 5-second/10-second periodic samples can miss a short-lived
        # allocation spike around a scene switch or a low-memory callback.
        # These callbacks must not claim total VRAM, remove scene events,
        # mutate resource ownership or introduce per-frame GPU JNI probes.
        helper = self.source.split("private static string GraphicsMemoryAtBoundary()", 1)[1]
        helper = helper.split("private static void LowMemory()", 1)[0]
        self.assertIn('"; android_debug_graphics_kb=" + AndroidGraphicsMemoryKb()', helper)
        self.assertIn('"; unity_driver_graphics_bytes=" + UnityGraphicsDriverBytes()', helper)
        self.assertIn('"; process_rss=" + ProcessRss()', helper)
        self.assertIn('partial process/driver counters', self.source)
        scenes = self.source.split("private void SceneLoaded(Scene scene, LoadSceneMode mode)", 1)[1]
        scenes = scenes.split("private void OnApplicationPause(", 1)[0]
        self.assertEqual(scenes.count("GraphicsMemoryAtBoundary()"), 2)
        self.assertIn('AndroidRuntimeLog.Write("scene", "loaded"', scenes)
        self.assertIn('AndroidRuntimeLog.Write("scene", "unloaded"', scenes)
        # SceneLoaded is intentionally an instance callback: the bounded
        # renderer/material/mesh snapshot runs as a coroutine, not in a static
        # callback or per-frame loop. Do not "fix" CI by removing the snapshot.
        self.assertIn('StartCoroutine(ReportSceneShaderSnapshot(scene));', scenes)
        self.assertIn('private System.Collections.IEnumerator ReportSceneShaderSnapshot(Scene scene)', scenes)
        snapshot = scenes.split("private System.Collections.IEnumerator ReportSceneShaderSnapshot(Scene scene)", 1)[1]
        snapshot = snapshot.split("private static void SceneUnloaded(", 1)[0]
        self.assertIn('yield return new WaitForSecondsRealtime(3f);', snapshot)
        self.assertIn('if (!scene.isLoaded) yield break;', snapshot)
        self.assertIn('const int RendererLimit = 512;', snapshot)
        self.assertIn('renderer.sharedMaterials', snapshot)
        self.assertIn('"scene_shader_snapshot"', snapshot)
        self.assertNotIn('GraphicsMemoryAtBoundary()', snapshot)
        low = self.source.split("private static void LowMemory()", 1)[1]
        low = low.split("private static string ProcessRss()", 1)[0]
        self.assertIn('"; " + GraphicsMemoryAtBoundary(), true)', low)
        self.assertLess(low.index('GraphicsMemoryAtBoundary()'), low.index('AndroidRuntimeLog.Flush();'))
        periodic = self.source.split("private string PerformanceSample()", 1)[1]
        periodic = periodic.split("private static void ReportPriorExits()", 1)[0]
        self.assertNotIn("GraphicsMemoryAtBoundary()", periodic)
        self.assertIn('if (!Debug.isDebugBuild) return "unavailable";', self.source)

    def test_overlay_respects_landscape_notch_safe_area(self):
        ui = self.source.split("private void OnGUI()", 1)[1]
        self.assertIn("Rect safe = Screen.safeArea;", ui)
        self.assertIn("safe.xMin / scale", ui)
        self.assertIn("(Screen.height - safe.yMax) / scale", ui)
        self.assertIn("safe.width / scale, safe.height / scale", ui)
        self.assertIn("safeGui.xMin + 8f, safeGui.yMin + 8f", ui)
        self.assertIn("safeGui.yMax - panelTop - 8f", ui)
        self.assertIn("Mathf.Min(145f, Mathf.Max(0f, safeGui.width - 16f))", ui)
        self.assertIn("finally { GUI.matrix = previous; }", ui)
        self.assertIn("finally { GUILayout.EndArea(); }", ui)
        self.assertNotIn("GUI.Button(new Rect(8, 8, 145, 44)", ui)
        # A diagnostic overlay is not a substitute for original gameplay touch controls.



    def test_info_spam_is_filtered_before_persistent_disk_logging(self):
        capture = self.source.split("private static void Capture(", 1)[1]
        capture = capture.split("private void RefreshReport()", 1)[0]
        self.assertIn('bool critical = type == LogType.Error || type == LogType.Exception || type == LogType.Assert;', capture)
        self.assertIn('bool raftMarker = message.StartsWith("RAFT_", StringComparison.Ordinal);', capture)
        guard = 'if (!critical && type != LogType.Warning && !raftMarker) return;'
        sink = 'AndroidRuntimeLog.UnityMessage(type.ToString(),'
        self.assertIn(guard, capture)
        self.assertLess(capture.index(guard), capture.index(sink))
        # Keep non-RAFT warnings in persistent evidence, but not the small UI preview.
        self.assertIn('if (!critical && !raftMarker) return;', capture)
        self.assertIn('message + "\\n" + stack, critical)', capture)


if __name__ == "__main__":
    unittest.main()

class PerformanceHudContract(unittest.TestCase):
    def test_visible_hud_retains_metric_scope_and_unavailability(self):
        text = (Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidTestDiagnostics.cs").read_text()
        for marker in ("RAM system used/total:", "game PSS:", "CPU system:", "GPU: unavailable", "Texture2D.whiteTexture", "Color.black", "Color.white"):
            self.assertIn(marker, text)
