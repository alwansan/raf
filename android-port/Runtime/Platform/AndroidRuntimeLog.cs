#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using System.IO;
using System.Diagnostics;
using UnityEngine;

namespace RaftAndroid.Diagnostics
{
    public static class AndroidRuntimeLog
    {
        private static PersistentDiagnosticLog sink;
        private static readonly RepeatedDiagnosticMessages repeated = new RepeatedDiagnosticMessages();
        public static bool UnityMessage(string type, string detail, bool critical)
        {
            if ((critical || type == "Warning") && !repeated.First(type, detail, DateTime.UtcNow)) return false;
            Write("unity", type, detail, critical);
            return true;
        }
        public static void SummarizeRepeated()
        {
            repeated.Summarize((area, operation, detail) => Write(area, operation, detail));
        }
        public static string LogDirectory { get; private set; }
        public static string StorageError { get; private set; }

        public static void Initialize()
        {
            if (sink != null || StorageError != null) return;
            try
            {
                LogDirectory = Path.Combine(Application.persistentDataPath, "raft-logs");
                sink = new PersistentDiagnosticLog(LogDirectory);
                Write("startup", "logger.ready", "version=" + Application.version + "; unity=" + Application.unityVersion +
                    "; package=" + Application.identifier + "; device=" + SystemInfo.deviceModel +
                    "; os=" + SystemInfo.operatingSystem + "; gpu=" + SystemInfo.graphicsDeviceName +
                    "; graphics=" + SystemInfo.graphicsDeviceType + "; driver=" + SystemInfo.graphicsDeviceVersion +
                    "; gpu_vendor=" + SystemInfo.graphicsDeviceVendor + "; compute=" + SystemInfo.supportsComputeShaders +
                    "; shader_level=" + SystemInfo.graphicsShaderLevel + "; cpu=" + SystemInfo.processorType +
                    "; cpu_count=" + SystemInfo.processorCount + "; system_memory_mb=" + SystemInfo.systemMemorySize, true);
                // Lightweight, read-only FFT hardware contract for APK diagnostics.
                // A supported format does NOT prove that a recovered Unity kernel exists.
                try { ReportFftDeviceCapabilities(); }
                catch (Exception ex)
                {
                    Write("water", "fft_device_capabilities.unavailable", ex.GetType().Name, true);
                }
            }
            catch (Exception ex) { StorageError = ex.GetType().Name + ": " + ex.Message; }
        }

        // Original GpuFFT uses RGHalf/RGFloat/ARGBHalf/ARGBFloat targets. Report
        // only Unity's queried capability flags; never allocate a RenderTexture,
        // change a fallback format, or infer a working shader from these values.
        // MaxComputeWorkGroupSize is local-group INVOCATIONS. The X/Y/Z values
        // are max DISPATCH GROUP COUNTS on Unity 2021, not local [numthreads]
        // dimensions (see Unity 2021.3 SystemInfo API). Never interchange them.
        private static int? QueryPositiveLimit(Func<int> query)
        {
            try
            {
                int value = query();
                return value > 0 ? (int?)value : null;
            }
            catch (Exception) { return null; }
        }

        private static string ReportLimit(int? value)
        {
            return value.HasValue
                ? value.Value.ToString(System.Globalization.CultureInfo.InvariantCulture)
                : "unavailable";
        }

        // Original SHA-authenticated FFT compiled slots (B48 source+serial proof)
        // request local group sizes 64,128,256,512,1024 with Y=Z=1 at
        // resolutions 32,64,128,256,512. They are COMPILED candidates, not
        // proven Unity FindKernel IDs or active settings on this device.
        private static void ReportFftDeviceCapabilities()
        {
            bool? supportsCompute = null;
            try { supportsCompute = SystemInfo.supportsComputeShaders; }
            catch (Exception) { }
            int? maxLocalInvocations = QueryPositiveLimit(() => SystemInfo.maxComputeWorkGroupSize);
            int? maxDispatchX = QueryPositiveLimit(() => SystemInfo.maxComputeWorkGroupSizeX);
            int? maxDispatchY = QueryPositiveLimit(() => SystemInfo.maxComputeWorkGroupSizeY);
            int? maxDispatchZ = QueryPositiveLimit(() => SystemInfo.maxComputeWorkGroupSizeZ);
            Write("water", "fft_device_compute_limits",
                "supports_compute=" + (supportsCompute.HasValue ? supportsCompute.ToString() : "unavailable") +
                "; max_group_invocations=" + ReportLimit(maxLocalInvocations) +
                "; max_dispatch_groups_x=" + ReportLimit(maxDispatchX) +
                "; max_dispatch_groups_y=" + ReportLimit(maxDispatchY) +
                "; max_dispatch_groups_z=" + ReportLimit(maxDispatchZ) +
                "; reported_max_is_theoretical=true" +
                "; original_runtime_kernel_mapping=unverified", true);

            int[] originalFftLocalGroupX = { 64, 128, 256, 512, 1024 };
            foreach (int groupX in originalFftLocalGroupX)
            {
                string assessment = !maxLocalInvocations.HasValue ? "unavailable" :
                    groupX > maxLocalInvocations.Value ? "exceeds_reported_theoretical_invocation_limit" :
                    "within_reported_theoretical_invocation_limit";
                Write("water", "fft_original_compiled_group_limit",
                    "original_source_resolution=" + (groupX / 2) +
                    "; compiled_local_group_x=" + groupX +
                    "; compiled_local_group_y=1; compiled_local_group_z=1" +
                    "; theoretical_invocation_assessment=" + assessment +
                    "; actual_unity_kernel_mapping=unverified" +
                    "; actual_fft_dispatch=unverified", true);
            }

            RenderTextureFormat[] formats = {
                RenderTextureFormat.RGHalf,
                RenderTextureFormat.RGFloat,
                RenderTextureFormat.ARGBHalf,
                RenderTextureFormat.ARGBFloat
            };
            foreach (RenderTextureFormat format in formats)
            {
                string supported = "unavailable";
                string randomWrite = "unavailable";
                try { supported = SystemInfo.SupportsRenderTextureFormat(format).ToString(); }
                catch (Exception) { }
                try { randomWrite = SystemInfo.SupportsRandomWriteOnRenderTextureFormat(format).ToString(); }
                catch (Exception) { }
                Write("water", "fft_device_target_format",
                    "original_requested_format=" + format +
                    "; render_texture_supported=" + supported +
                    "; random_write_supported=" + randomWrite +
                    "; actual_image_view=unverified; actual_fft_dispatch=unverified", true);
            }
        }

        public static void Write(string area, string operation, string detail = "", bool critical = false)
        {
            sink?.Write(area, operation, detail, critical);
        }

        public static void Stage(string operation, Action action)
        {
            Initialize();
            Write("audio", operation + ".begin", "", true);
            try { action(); Write("audio", operation + ".ok", "", true); }
            catch (Exception ex) { Write("audio", operation + ".failed", ex.ToString(), true); throw; }
        }

        public static void Flush() { SummarizeRepeated(); sink?.Flush(); }
        public static long BeginOperation(string area, string operation, string detail)
        {
            Write(area, operation + ".enter", detail, true);
            return Stopwatch.GetTimestamp();
        }
        public static void EndOperation(string area, string operation, long started, bool failed)
        {
            double ms = (Stopwatch.GetTimestamp() - started) * 1000.0 / Stopwatch.Frequency;
            Write(area, operation + ".exit", "exceptionEscaped=" + failed + "; elapsed_ms=" +
                ms.ToString("F3", System.Globalization.CultureInfo.InvariantCulture), true);
        }
        public static string Status => StorageError ?? sink?.LastError ?? "ready";
        public static void Shutdown() { SummarizeRepeated(); sink?.Dispose(); sink = null; }
    }
}
#endif
