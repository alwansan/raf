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
        private static void ReportFftDeviceCapabilities()
        {
            Write("water", "fft_device_compute_limits",
                "supports_compute=" + SystemInfo.supportsComputeShaders +
                "; max_group_invocations=" + SystemInfo.maxComputeWorkGroupSize +
                "; max_group_x=" + SystemInfo.maxComputeWorkGroupSizeX +
                "; max_group_y=" + SystemInfo.maxComputeWorkGroupSizeY +
                "; max_group_z=" + SystemInfo.maxComputeWorkGroupSizeZ +
                "; unity_compute_kernel_identity=unverified", true);
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
