#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.Text;
using System.Globalization;
using UnityEngine.Profiling;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace RaftAndroid.Platform
{
    // Local-only report UI for the first device experiments. Nothing is uploaded.
    public sealed class AndroidTestDiagnostics : MonoBehaviour
    {
        private static readonly Queue<string> events = new Queue<string>();
        private static readonly object gate = new object();
        private static int eventRevision;
        private const int VisibleReportLimit = 8000;
        private bool opened;
        private Vector2 scroll;
        private int reportRevision = -1;
        private string reportScene = "";
        private string fullReport = "";
        private string visibleReport = "";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void CaptureBeforeAudioStartup()
        {
            EnforceLandscape();
            lock (gate)
            {
                events.Clear();
                eventRevision++;
            }
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Initialize();
            Application.logMessageReceivedThreaded -= Capture;
            Application.logMessageReceivedThreaded += Capture;
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void StartDiagnostics()
        {
            var host = new GameObject("RaftAndroidTestDiagnostics");
            DontDestroyOnLoad(host);
            host.AddComponent<AndroidTestDiagnostics>();
            ReportPriorExits();
            Debug.Log("RAFT_ANDROID_DEVICE_TEST earlyStartupCandidate=true gameplayVerified=false");
        }

        private static void Capture(string message, string stack, LogType type)
        {
            message = message ?? "";
            stack = stack ?? "";
            if (!RaftAndroid.Diagnostics.AndroidRuntimeLog.UnityMessage(type.ToString(), message + "\n" + stack,
                type == LogType.Error || type == LogType.Exception || type == LogType.Assert)) return;
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert &&
                !message.StartsWith("RAFT_", StringComparison.Ordinal)) return;
            string entry = DateTime.UtcNow.ToString("O") + " " + type + " " + message + "\n" + stack;
            if (entry.Length > 3000) entry = entry.Substring(0, 3000);
            lock (gate)
            {
                events.Enqueue(entry);
                while (events.Count > 48) events.Dequeue();
                eventRevision++;
            }
        }

        private void RefreshReport()
        {
            string scene = SceneManager.GetActiveScene().name;
            string[] snapshot;
            int version;
            lock (gate)
            {
                version = eventRevision;
                if (reportRevision == version && reportScene == scene) return;
                snapshot = events.ToArray();
            }

            var text = new StringBuilder();
            text.AppendLine("Raft Android early device test");
            text.AppendLine("Unity " + Application.unityVersion + "; scene " + scene);
            text.AppendLine(SystemInfo.deviceModel + "; " + SystemInfo.operatingSystem);
            text.AppendLine(SystemInfo.graphicsDeviceName + "; " + SystemInfo.graphicsDeviceType);
            text.AppendLine("Logs: " + RaftAndroid.Diagnostics.AndroidRuntimeLog.LogDirectory);
            text.AppendLine("Storage: " + RaftAndroid.Diagnostics.AndroidRuntimeLog.Status);
            text.AppendLine("This report does not verify gameplay, sound or save/load.");
            foreach (string entry in snapshot) text.AppendLine(entry);
            fullReport = text.ToString();
            visibleReport = fullReport.Length <= VisibleReportLimit
                ? fullReport
                : "Preview shows only the last 8000 characters. Copy test report includes all captured entries.\n"
                  + fullReport.Substring(fullReport.Length - VisibleReportLimit);
            reportRevision = version;
            reportScene = scene;
        }


        private float nextSample;
        private bool skipNextFrame = true;
        private readonly float[] frameSamples = new float[2048];
        private readonly FrameTiming[] timings = new FrameTiming[1];
        private int sampleCount, intervalFrames;
        private double intervalSeconds;
        private static string Number(double value) => value.ToString("F2", CultureInfo.InvariantCulture);
        private static string Timing(double value) => value > 0 && !double.IsNaN(value) && !double.IsInfinity(value)
            ? Number(value) : "unavailable";
        private string PerformanceSample()
        {
            Array.Sort(frameSamples, 0, sampleCount);
            Func<double, string> percentile = p => sampleCount == 0 ? "unavailable" :
                Number(frameSamples[Math.Min(sampleCount - 1, (int)Math.Ceiling(sampleCount * p) - 1)]);
            uint available = FrameTimingManager.GetLatestTimings(1, timings);
            string report = "interval_frames=" + intervalFrames + "; fps=" +
                (intervalSeconds > 0 ? Number(intervalFrames / intervalSeconds) : "unavailable") +
                "; frame_samples=" + sampleCount + "; sample_capacity=2048; frame_sample_overflow=" + Math.Max(0, intervalFrames - sampleCount) +
                "; frame_p50_ms=" + percentile(0.50) + "; frame_p95_ms=" + percentile(0.95) +
                "; frame_p99_ms=" + percentile(0.99) + "; frame_worst_ms=" + percentile(1) +
                "; cpu_latest_frame_ms=" + (available > 0 ? Timing(timings[0].cpuFrameTime) : "unavailable") +
                "; gpu_latest_frame_ms=" + (available > 0 ? Timing(timings[0].gpuFrameTime) : "unavailable") +
                "; process_cpu_percent=unavailable; managed_bytes=" + GC.GetTotalMemory(false) +
                "; unity_allocated_bytes=" + Profiler.GetTotalAllocatedMemoryLong() +
                "; unity_reserved_bytes=" + Profiler.GetTotalReservedMemoryLong() +
                "; unity_unused_reserved_bytes=" + Profiler.GetTotalUnusedReservedMemoryLong() +
                "; gc_gen0_total=" + GC.CollectionCount(0) + "; process_rss=" + ProcessRss() +
                "; process_pss=" + ProcessPss() + "; system_memory=" + AndroidMemory() +
                "; thermal=unavailable; draw_calls=unavailable" +
                "; width=" + Screen.width + "; height=" + Screen.height + "; orientation=" + Screen.orientation +
                "; refresh_hz=" + Screen.currentResolution.refreshRate + "; scene=" + SceneManager.GetActiveScene().name;
            intervalFrames = sampleCount = 0; intervalSeconds = 0;
            return report;
        }
        private static void ReportPriorExits()
        {
            try
            {
                using (var version = new AndroidJavaClass("android.os.Build$VERSION"))
                    if (version.GetStatic<int>("SDK_INT") < 30) return;
                using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                using (var manager = activity.Call<AndroidJavaObject>("getSystemService", "activity"))
                using (var exits = manager.Call<AndroidJavaObject>("getHistoricalProcessExitReasons", Application.identifier, 0, 4))
                {
                    int count = Math.Min(exits.Call<int>("size"), 4);
                    for (int i = 0; i < count; i++)
                    using (var exit = exits.Call<AndroidJavaObject>("get", i))
                        RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("startup", "previous_process_exit",
                            "reason_code=" + exit.Call<int>("getReason") + "; status=" + exit.Call<int>("getStatus") +
                            "; timestamp_unix_ms=" + exit.Call<long>("getTimestamp") +
                            "; pss_kb=" + exit.Call<long>("getPss") + "; rss_kb=" + exit.Call<long>("getRss"), true);
                }
            }
            catch (Exception ex)
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("startup", "previous_process_exit.unavailable", ex.GetType().Name);
            }
        }
        private static string AndroidMemory()
        {
            try
            {
                using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                using (var manager = activity.Call<AndroidJavaObject>("getSystemService", "activity"))
                using (var info = new AndroidJavaObject("android.app.ActivityManager$MemoryInfo"))
                {
                    manager.Call("getMemoryInfo", info);
                    return "available_bytes:" + info.Get<long>("availMem") + ",total_bytes:" + info.Get<long>("totalMem") +
                        ",low_memory:" + info.Get<bool>("lowMemory") + ",threshold_bytes:" + info.Get<long>("threshold");
                }
            }
            catch (Exception) { return "unavailable"; }
        }
        private static string ProcessPss()
        {
            try
            {
                foreach (string line in System.IO.File.ReadLines("/proc/self/smaps_rollup"))
                    if (line.StartsWith("Pss:", StringComparison.Ordinal)) return line.Substring(4).Trim();
            }
            catch (Exception) { }
            return "unavailable";
        }
        private static void LowMemory()
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("memory", "unity.low_memory", AndroidMemory() +
                "; process_pss=" + ProcessPss(), true);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Flush();
        }
        private static string ProcessRss()
        {
            try
            {
                foreach (string line in System.IO.File.ReadLines("/proc/self/status"))
                    if (line.StartsWith("VmRSS:", StringComparison.Ordinal)) return line.Substring(6).Trim();
            }
            catch (Exception) { }
            return "unavailable";
        }
        private void OnEnable()
        {
            Application.lowMemory += LowMemory;
            SceneManager.sceneLoaded += SceneLoaded;
            SceneManager.sceneUnloaded += SceneUnloaded;
            SceneManager.activeSceneChanged += ActiveSceneChanged;
        }
        private void OnDisable()
        {
            Application.lowMemory -= LowMemory;
            SceneManager.sceneLoaded -= SceneLoaded;
            SceneManager.sceneUnloaded -= SceneUnloaded;
            SceneManager.activeSceneChanged -= ActiveSceneChanged;
        }
        private static void SceneLoaded(Scene scene, LoadSceneMode mode)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("scene", "loaded", scene.name + "; mode=" + mode, true);
        }
        private static void SceneUnloaded(Scene scene)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("scene", "unloaded", scene.name, true);
        }
        private static void ActiveSceneChanged(Scene before, Scene after)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("scene", "active_changed", before.name + " -> " + after.name, true);
        }
        private void OnApplicationPause(bool paused)
        {
            if (!paused) EnforceLandscape();
            intervalFrames = sampleCount = 0; intervalSeconds = 0;
            skipNextFrame = true;
            // Persist the transition itself before flushing: the previous order
            // could omit the last pause event when Android kills the process.
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("lifecycle", "pause", paused.ToString(), true);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Flush();
        }
        private void OnApplicationFocus(bool focused)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("lifecycle", "focus", focused.ToString(), true);
        }
        private void OnApplicationQuit()
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("lifecycle", "quit", "", true);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Shutdown();
        }
        private static void EnforceLandscape()
        {
            Screen.autorotateToPortrait = false;
            Screen.autorotateToPortraitUpsideDown = false;
            Screen.autorotateToLandscapeLeft = true;
            Screen.autorotateToLandscapeRight = true;
            Screen.orientation = ScreenOrientation.AutoRotation;
        }
        private void Update()
        {
            if (skipNextFrame) { skipNextFrame = false; return; }
            float delta = Time.unscaledDeltaTime;
            intervalFrames++; intervalSeconds += delta;
            if (sampleCount < frameSamples.Length) frameSamples[sampleCount++] = delta * 1000f;
            FrameTimingManager.CaptureFrameTimings();
            if (Time.realtimeSinceStartup < nextSample) return;
            RaftAndroid.Diagnostics.AndroidRuntimeLog.SummarizeRepeated();
            nextSample = Time.realtimeSinceStartup + 5f;
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("performance", "sample", PerformanceSample());
        }

        private void OnGUI()
        {
            float scale = Mathf.Max(1f, Screen.height / 720f);
            Matrix4x4 previous = GUI.matrix;
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1));
            if (GUI.Button(new Rect(8, 8, 145, 44), opened ? "Close test report" : "Test report")) opened = !opened;
            if (opened)
            {
                float width = Screen.width / scale - 16;
                float height = Screen.height / scale - 70;
                GUILayout.BeginArea(new Rect(8, 60, width, height), GUI.skin.box);
                GUILayout.Label("Early Android test: startup and diagnostics. Singleplayer and touch controls are still being integrated.");
                RefreshReport();
                if (GUILayout.Button("Copy test report", GUILayout.Height(44))) GUIUtility.systemCopyBuffer = fullReport;
                scroll = GUILayout.BeginScrollView(scroll);
                GUILayout.Label(visibleReport);
                GUILayout.EndScrollView();
                GUILayout.EndArea();
            }
            GUI.matrix = previous;
        }
    }
}
#endif

