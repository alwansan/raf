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
        private AndroidTouchGamepadOverlay touchGamepad;
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
            host.AddComponent<AndroidTouchGamepadOverlay>();
            host.AddComponent<AndroidTouchUiPanel>();
            host.AddComponent<AndroidTouchPointer>();
            ReportPriorExits();
            Debug.Log("RAFT_ANDROID_DEVICE_TEST earlyStartupCandidate=true gameplayVerified=false");
        }

        private static void Capture(string message, string stack, LogType type)
        {
            message = message ?? "";
            stack = stack ?? "";
            bool critical = type == LogType.Error || type == LogType.Exception || type == LogType.Assert;
            bool raftMarker = message.StartsWith("RAFT_", StringComparison.Ordinal);
            // Filter ordinary informational spam before the persistent disk sink.
            // Always retain warnings and critical failures, plus RAFT_ milestones.
            if (!critical && type != LogType.Warning && !raftMarker) return;
            if (!RaftAndroid.Diagnostics.AndroidRuntimeLog.UnityMessage(type.ToString(),
                message + "\n" + stack, critical)) return;
            if (!critical && !raftMarker) return;
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


        private string hud = "FPS: collecting | RAM: collecting | CPU/GPU: unavailable";
        private ulong previousCpuTotal, previousCpuIdle;
        private string SystemCpu()
        {
            try
            {
                string[] values;
                foreach (string line in System.IO.File.ReadLines("/proc/stat"))
                {
                    if (!line.StartsWith("cpu ", StringComparison.Ordinal)) continue;
                    values = line.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                    ulong total = 0;
                    // guest fields are already included in user/nice.
                    for (int i = 1; i < Math.Min(values.Length, 9); i++) total += ulong.Parse(values[i], CultureInfo.InvariantCulture);
                    ulong idle = ulong.Parse(values[4]) + (values.Length > 5 ? ulong.Parse(values[5]) : 0);
                    ulong elapsed = total >= previousCpuTotal ? total - previousCpuTotal : 0;
                    ulong idleElapsed = idle >= previousCpuIdle ? idle - previousCpuIdle : 0;
                    string result = previousCpuTotal > 0 && elapsed > 0 && idleElapsed <= elapsed
                        ? Number(100.0 * (elapsed - idleElapsed) / elapsed) + "%" : "unavailable";
                    previousCpuTotal = total; previousCpuIdle = idle;
                    return result;
                }
            }
            catch (Exception) { }
            return "unavailable";
        }
        private static string MemoryHud()
        {
            try
            {
                using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                using (var manager = activity.Call<AndroidJavaObject>("getSystemService", "activity"))
                using (var info = new AndroidJavaObject("android.app.ActivityManager$MemoryInfo"))
                {
                    manager.Call("getMemoryInfo", info);
                    long total = info.Get<long>("totalMem"), available = info.Get<long>("availMem");
                    return "RAM system used/total: " + Number((total - available) / 1048576.0) + "/" + Number(total / 1048576.0) +
                        " MiB | available: " + Number(available / 1048576.0) + " MiB | game PSS: " + ProcessPss() + " | RSS: " + ProcessRss();
                }
            }
            catch (Exception) { return "RAM: unavailable"; }
        }
        private float nextSample;
        private bool skipNextFrame = true;
        private readonly float[] frameSamples = new float[2048];
        private readonly FrameTiming[] timings = new FrameTiming[1];
        private int sampleCount, intervalFrames;
        private double intervalSeconds;
        private float nextGraphicsMemoryProbe;
        private string lastAndroidGraphicsKb = "unavailable";
        private static string Number(double value) => value.ToString("F2", CultureInfo.InvariantCulture);
        private static string Timing(double value) => value > 0 && !double.IsNaN(value) && !double.IsInfinity(value)
            ? Number(value) : "unavailable";
        // Android's self-process Debug.MemoryInfo can omit protected GPU allocations.
        // Treat this as a diagnostic memory-summary field, never as total GPU VRAM.
        private static string AndroidGraphicsMemoryKb()
        {
            try
            {
                using (var version = new AndroidJavaClass("android.os.Build$VERSION"))
                    if (version.GetStatic<int>("SDK_INT") < 23) return "unavailable";
                using (var debug = new AndroidJavaClass("android.os.Debug"))
                using (var info = new AndroidJavaObject("android.os.Debug$MemoryInfo"))
                {
                    debug.CallStatic("getMemoryInfo", info);
                    string value = info.Call<string>("getMemoryStat", "summary.graphics");
                    return string.IsNullOrEmpty(value) ? "unavailable" : value;
                }
            }
            catch (Exception) { return "unavailable"; }
        }

        // Unity 2021 only exposes this counter in development players.
        // A zero from a release player must not be reported as measured zero.
        private static string UnityGraphicsDriverBytes()
        {
            if (!Debug.isDebugBuild) return "unavailable";
            try
            {
                long bytes = Profiler.GetAllocatedMemoryForGraphicsDriver();
                return bytes >= 0 ? bytes.ToString(CultureInfo.InvariantCulture) : "unavailable";
            }
            catch (Exception) { return "unavailable"; }
        }

        private string PerformanceSample()
        {
            if (Time.realtimeSinceStartup >= nextGraphicsMemoryProbe)
            {
                lastAndroidGraphicsKb = AndroidGraphicsMemoryKb();
                nextGraphicsMemoryProbe = Time.realtimeSinceStartup + 10f;
            }
            Array.Sort(frameSamples, 0, sampleCount);
            Func<double, string> percentile = p => sampleCount == 0 ? "unavailable" :
                Number(frameSamples[Math.Min(sampleCount - 1, (int)Math.Ceiling(sampleCount * p) - 1)]);
            uint available = FrameTimingManager.GetLatestTimings(1, timings);
            hud = "FPS: " + (intervalSeconds > 0 ? Number(intervalFrames / intervalSeconds) : "unavailable") +
                " | frame p95: " + percentile(0.95) + " ms | CPU system: " + SystemCpu() +
                " | GPU: unavailable (no reliable counter)\n" + MemoryHud();
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
                 "; android_debug_graphics_kb=" + lastAndroidGraphicsKb +
                 "; unity_driver_graphics_bytes=" + UnityGraphicsDriverBytes() +
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
        // Capture existing partial process/driver counters at infrequent scene
        // boundaries. Neither counter is total GPU allocation or proof of OOM
        // causality; absent development-build data must remain "unavailable".
        private static string GraphicsMemoryAtBoundary()
        {
            return "process_pss=" + ProcessPss() + "; process_rss=" + ProcessRss() +
                "; android_debug_graphics_kb=" + AndroidGraphicsMemoryKb() +
                "; unity_driver_graphics_bytes=" + UnityGraphicsDriverBytes();
        }

        private static void LowMemory()
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("memory", "unity.low_memory", AndroidMemory() +
                "; " + GraphicsMemoryAtBoundary(), true);
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
        private void SceneLoaded(Scene scene, LoadSceneMode mode)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("scene", "loaded",
                scene.name + "; mode=" + mode + "; " + GraphicsMemoryAtBoundary(), true);
            // Diagnostic only. Do not sample or instantiate materials every frame.
            StartCoroutine(ReportSceneShaderSnapshot(scene));
        }
        // One bounded read-only quality sample per loaded scene. Never call
        // SetQualityLevel or mutate texture quality, shadows, or user Settings:
        // these values provide evidence against the authenticated original
        // five-tier baseline, not a forced Android visual configuration.
        private static string OriginalQualityStateSnapshot()
        {
            try
            {
                string[] levels = QualitySettings.names;
                int tierCount = levels == null ? -1 : levels.Length;
                return "; quality_level_index=" + QualitySettings.GetQualityLevel() +
                    "; quality_tier_count=" + tierCount +
                    "; pixel_light_count=" + QualitySettings.pixelLightCount +
                    "; master_texture_limit=" + QualitySettings.masterTextureLimit +
                    "; anti_aliasing=" + QualitySettings.antiAliasing +
                    "; shadow_mode=" + QualitySettings.shadows +
                    "; shadow_distance=" + QualitySettings.shadowDistance.ToString("R", CultureInfo.InvariantCulture);
            }
            catch (Exception ex)
            {
                // Preserve B12 renderer/shader evidence even if an unexpected
                // platform quality getter fails on a particular Android GPU.
                return "; quality_snapshot_error_type=" + ex.GetType().Name;
            }
        }
        private System.Collections.IEnumerator ReportSceneShaderSnapshot(Scene scene)
        {
            yield return new WaitForSecondsRealtime(3f);
            if (!scene.isLoaded) yield break;
            try
            {
                // Cap traversal work BEFORE collecting renderers. An entire Raft
                // hierarchy can have far more than 512 components; creating a
                // root.GetComponentsInChildren<Renderer>(true) array first was
                // not memory-bounded even when the result loop was truncated.
                const int RootLimit = 1024;
                const int TransformLimit = 4096;
                const int PendingLimit = 1024;
                const int RendererLimit = 512;
                const int MaterialLimit = 4096;
                int rootCount = scene.rootCount;
                int visitedTransforms = 0, sampled = 0, empty = 0, slots = 0;
                int nullMaterials = 0, nullShaders = 0, unsupported = 0;
                int zeroPass = 0, errorShaders = 0, meshRenderers = 0;
                int missingMeshFilters = 0, missingMeshAssets = 0;
                int skinnedRenderers = 0, missingSkinnedMeshes = 0;
                bool truncated = false;
                string limitReason = "none";
                if (rootCount > RootLimit)
                {
                    // Do not fetch an unbounded scene root array merely to
                    // sample a small subset; report an explicitly partial scan.
                    truncated = true;
                    limitReason = "root_limit";
                }
                else
                {
                    var roots = new List<GameObject>(rootCount);
                    scene.GetRootGameObjects(roots);
                    var pending = new Transform[PendingLimit];
                    var renderers = new List<Renderer>(4);
                    foreach (GameObject root in roots)
                    {
                        if (!root || !root.activeInHierarchy) continue;
                        int pendingCount = 0;
                        pending[pendingCount++] = root.transform;
                        while (pendingCount > 0)
                        {
                            Transform current = pending[--pendingCount];
                            pending[pendingCount] = null;
                            if (!current || !current.gameObject.activeInHierarchy) continue;
                            if (visitedTransforms >= TransformLimit)
                            {
                                truncated = true;
                                limitReason = "transform_limit";
                                break;
                            }
                            visitedTransforms++;
                            // Unity's list overload reuses this collection;
                            // do not call GetComponentsInChildren on whole roots.
                            renderers.Clear();
                            current.GetComponents<Renderer>(renderers);
                            foreach (Renderer renderer in renderers)
                            {
                                if (!renderer || !renderer.enabled ||
                                    !renderer.gameObject.activeInHierarchy) continue;
                                if (sampled >= RendererLimit)
                                {
                                    truncated = true;
                                    limitReason = "renderer_limit";
                                    break;
                                }
                                sampled++;
                                MeshRenderer meshRenderer = renderer as MeshRenderer;
                                if (meshRenderer != null)
                                {
                                    meshRenderers++;
                                    MeshFilter filter = meshRenderer.GetComponent<MeshFilter>();
                                    if (!filter) missingMeshFilters++;
                                    else if (!filter.sharedMesh) missingMeshAssets++;
                                }
                                SkinnedMeshRenderer skinnedRenderer = renderer as SkinnedMeshRenderer;
                                if (skinnedRenderer != null)
                                {
                                    skinnedRenderers++;
                                    if (!skinnedRenderer.sharedMesh) missingSkinnedMeshes++;
                                }
                                // No material/mesh instance or geometry readback.
                                Material[] materials = renderer.sharedMaterials;
                                if (materials == null || materials.Length == 0)
                                {
                                    empty++;
                                    continue;
                                }
                                foreach (Material material in materials)
                                {
                                    if (slots >= MaterialLimit)
                                    {
                                        truncated = true;
                                        limitReason = "material_limit";
                                        break;
                                    }
                                    slots++;
                                    if (!material) { nullMaterials++; continue; }
                                    Shader shader = material.shader;
                                    if (!shader) { nullShaders++; continue; }
                                    if (!shader.isSupported) unsupported++;
                                    if (material.passCount == 0) zeroPass++;
                                    if (shader.name == "Hidden/InternalErrorShader") errorShaders++;
                                }
                                if (truncated) break;
                            }
                            if (truncated) break;
                            // Explicit fixed-size stack also prevents allocation
                            // growth in extremely wide hierarchies.
                            for (int child = current.childCount - 1; child >= 0; child--)
                            {
                                if (pendingCount >= PendingLimit)
                                {
                                    truncated = true;
                                    limitReason = "pending_limit";
                                    break;
                                }
                                pending[pendingCount++] = current.GetChild(child);
                            }
                            if (truncated) break;
                        }
                        if (truncated) break;
                    }
                }
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("render", "scene_shader_snapshot",
                    "scene=" + scene.name + "; delay_seconds=3; root_count=" + rootCount +
                    "; root_limit=" + RootLimit + "; visited_transforms=" + visitedTransforms +
                    "; transform_limit=" + TransformLimit + "; pending_limit=" + PendingLimit +
                    "; renderer_limit=" + RendererLimit + "; material_limit=" + MaterialLimit +
                    "; visible_renderers_sampled=" + sampled + "; truncated=" + truncated +
                    "; limit_reason=" + limitReason +
                    "; empty_material_renderers=" + empty + "; material_slots=" + slots +
                    "; null_materials=" + nullMaterials + "; null_shaders=" + nullShaders +
                    "; unsupported_shaders=" + unsupported + "; zero_pass_materials=" + zeroPass +
                    "; internal_error_shaders=" + errorShaders +
                    "; mesh_renderers=" + meshRenderers + "; missing_mesh_filters=" + missingMeshFilters +
                    "; missing_mesh_assets=" + missingMeshAssets +
                    "; skinned_renderers=" + skinnedRenderers + "; missing_skinned_meshes=" + missingSkinnedMeshes +
                    OriginalQualityStateSnapshot() +
                    "; color_space=" + QualitySettings.activeColorSpace +
                    "; ambient_mode=" + RenderSettings.ambientMode + "; fog=" + RenderSettings.fog +
                    "; skybox_assigned=" + (RenderSettings.skybox != null) +
                    "; original_shader_pixels_verified=false", true);
            }
            catch (Exception ex)
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("render", "scene_shader_snapshot.unavailable",
                    "scene=" + scene.name + "; error_type=" + ex.GetType().Name, true);
            }
        }
        private static void SceneUnloaded(Scene scene)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("scene", "unloaded",
                scene.name + "; " + GraphicsMemoryAtBoundary(), true);
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
            if (touchGamepad == null) touchGamepad = GetComponent<AndroidTouchGamepadOverlay>();
            float scale = Mathf.Max(1f, Screen.height / 720f);
            Rect safe = Screen.safeArea;
            // Screen.safeArea uses a bottom-left origin; IMGUI uses top-left.
            // Convert before applying the same scale to the entire overlay.
            Rect safeGui = new Rect(safe.xMin / scale,
                (Screen.height - safe.yMax) / scale,
                safe.width / scale, safe.height / scale);
            safeGui.yMin += 70f;
            float buttonWidth = Mathf.Min(145f, Mathf.Max(0f, safeGui.width - 16f));
            if (buttonWidth < 48f || safeGui.height < 60f) return;

            Matrix4x4 previous = GUI.matrix;
            try
            {
                GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1));
                Color oldColor = GUI.color;
                try
                {
                    GUI.color = Color.black;
                    GUI.DrawTexture(new Rect(safeGui.xMin, safeGui.yMin - 70f, safeGui.width, 66f), Texture2D.whiteTexture);
                    GUI.color = Color.white;
                    GUI.Label(new Rect(safeGui.xMin + 8f, safeGui.yMin - 68f, safeGui.width - 16f, 64f), hud);
                }
                finally { GUI.color = oldColor; }
                var touchPanel = GetComponent<AndroidTouchUiPanel>();
                if (touchPanel != null && touchPanel.Ready) return;
                if (touchGamepad != null)
                {
                    if (GUI.Button(new Rect(safeGui.xMin + 8f, safeGui.yMin + 56f, buttonWidth, 44f), touchGamepad.Visible ? "Hide Xbox" : "Show Xbox"))
                        touchGamepad.SetVisible(!touchGamepad.Visible);
                    if (touchGamepad.Visible && GUI.Button(new Rect(safeGui.xMin + 8f, safeGui.yMin + 104f, buttonWidth, 44f), "Xbox layout"))
                    { touchGamepad.SetLayoutEditMode(true); opened = true; }
                }
                if (GUI.Button(new Rect(safeGui.xMin + 8f, safeGui.yMin + 8f,
                    buttonWidth, 44f), opened ? "Close test report" : "Test report"))
                    opened = !opened;
                if (opened)
                {
                    float panelTop = safeGui.yMin + 154f;
                    float panelHeight = Mathf.Max(0f, safeGui.yMax - panelTop - 8f);
                    float panelWidth = Mathf.Max(0f, safeGui.width - 16f);
                    if (panelHeight >= 44f && panelWidth >= 48f)
                    {
                        GUILayout.BeginArea(new Rect(safeGui.xMin + 8f, panelTop,
                            panelWidth, panelHeight), GUI.skin.box);
                        try
                        {
                            GUILayout.Label("Early Android test: startup and diagnostics. Singleplayer and touch controls are still being integrated.");
                            RefreshReport();
                            if (GUILayout.Button("Copy test report", GUILayout.Height(44)))
                                GUIUtility.systemCopyBuffer = fullReport;
                            if (touchGamepad != null && GUILayout.Button(touchGamepad.Visible ? "Hide touch gamepad" : "Enable touch gamepad", GUILayout.Height(44)))
                                touchGamepad.SetVisible(!touchGamepad.Visible);
                            if (touchGamepad != null && touchGamepad.Visible)
                            {
                                if (GUILayout.Button(touchGamepad.Editing ? "Finish touch layout" : "Edit touch layout", GUILayout.Height(44)))
                                {
                                    bool startEdit = !touchGamepad.Editing;
                                    if (touchGamepad.SetLayoutEditMode(startEdit) && startEdit)
                                        opened = false; // Drag controls with report panel closed.
                                }
                                if (touchGamepad.Editing)
                                {
                                    GUILayout.Label("Selected: " + touchGamepad.SelectedControl);
                                    GUILayout.Label("Xbox opacity (all controls)");
                                    float opacity = GUILayout.HorizontalSlider(touchGamepad.GlobalOpacity, 0.2f, 0.95f);
                                    if (Mathf.Abs(opacity - touchGamepad.GlobalOpacity) > 0.005f) touchGamepad.SetGlobalOpacity(opacity);
                                    GUILayout.BeginHorizontal();
                                    if (GUILayout.Button("Size -")) touchGamepad.AdjustSelectedSize(-15f);
                                    if (GUILayout.Button("Size +")) touchGamepad.AdjustSelectedSize(15f);
                                    GUILayout.EndHorizontal();
                                    GUILayout.BeginHorizontal();
                                    if (GUILayout.Button("Opacity -")) touchGamepad.AdjustSelectedOpacity(-0.1f);
                                    if (GUILayout.Button("Opacity +")) touchGamepad.AdjustSelectedOpacity(0.1f);
                                    GUILayout.EndHorizontal();
                                    GUILayout.Label("Virtual binding: " + touchGamepad.SelectedBinding);
                                    GUILayout.BeginHorizontal();
                                    if (GUILayout.Button("Binding <")) touchGamepad.CycleSelectedBinding(-1);
                                    if (GUILayout.Button("Binding >")) touchGamepad.CycleSelectedBinding(1);
                                    GUILayout.EndHorizontal();
                                    if (GUILayout.Button("Reset touch layout")) touchGamepad.ResetLayout();
                                }
                            }
                            scroll = GUILayout.BeginScrollView(scroll);
                            GUILayout.Label(visibleReport);
                            GUILayout.EndScrollView();
                        }
                        finally { GUILayout.EndArea(); }
                    }
                }
            }
            finally { GUI.matrix = previous; }
        }

        public string TouchReportPreview() { RefreshReport(); return visibleReport; }
        public void CopyTouchReport() { RefreshReport(); GUIUtility.systemCopyBuffer = fullReport; }
    }
}
#endif

