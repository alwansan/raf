// B06: execute the real Android logger against bounded synthetic Unity 2021 API stubs.
// Does not represent Unity/Adreno/device, imported kernels or pixels.
using System;
using System.Collections.Generic;
using System.Linq;
using RaftAndroid.Diagnostics;

namespace UnityEngine
{
    public enum RenderTextureFormat { RGHalf, RGFloat, ARGBHalf, ARGBFloat }
    public static class Application
    {
        public static string persistentDataPath => "/synthetic";
        public static string version => "test";
        public static string unityVersion => "2021.3.45f2";
        public static string identifier => "test";
    }
    public static class SystemInfo
    {
        public static bool FailLimits;
        public static string deviceModel => "synthetic";
        public static string operatingSystem => "synthetic";
        public static string graphicsDeviceName => "synthetic";
        public static string graphicsDeviceType => "synthetic";
        public static string graphicsDeviceVersion => "synthetic";
        public static string graphicsDeviceVendor => "synthetic";
        public static bool supportsComputeShaders => true;
        public static int graphicsShaderLevel => 45;
        public static string processorType => "synthetic";
        public static int processorCount => 8;
        public static int systemMemorySize => 1024;
        public static int maxComputeWorkGroupSize => FailLimits ? throw new NotSupportedException() : 1024;
        public static int maxComputeWorkGroupSizeX => 1024;
        public static int maxComputeWorkGroupSizeY => 1024;
        public static int maxComputeWorkGroupSizeZ => 64;
        public static bool SupportsRenderTextureFormat(RenderTextureFormat f) =>
            f == RenderTextureFormat.RGHalf ? throw new NotSupportedException() : true;
        public static bool SupportsRandomWriteOnRenderTextureFormat(RenderTextureFormat f) =>
            f == RenderTextureFormat.RGFloat ? throw new NotSupportedException() : f != RenderTextureFormat.ARGBHalf;
    }
}
namespace RaftAndroid.Diagnostics
{
    public sealed class PersistentDiagnosticLog : IDisposable
    {
        public static readonly List<(string Area, string Operation, string Detail)> Entries = new();
        public string LastError => null;
        public PersistentDiagnosticLog(string path) { }
        public void Write(string area, string operation, string detail, bool critical) =>
            Entries.Add((area, operation, detail));
        public void Flush() { }
        public void Dispose() { }
    }
    public sealed class RepeatedDiagnosticMessages
    {
        public bool First(string area, string detail, DateTime at) => true;
        public void Summarize(Action<string,string,string> output) { }
    }
}
internal static class Program
{
    static void Assert(bool test, string reason)
    {
        if (!test) throw new Exception(reason);
    }
    public static int Main()
    {
        var logs = PersistentDiagnosticLog.Entries;
        AndroidRuntimeLog.Initialize();
        var rows = logs.Where(x => x.Operation == "fft_device_target_format").ToArray();
        string[] names = { "RGHalf", "RGFloat", "ARGBHalf", "ARGBFloat" };
        Assert(logs.Count(x => x.Operation == "logger.ready") == 1, "Logger startup missing");
        Assert(logs.Count(x => x.Operation == "fft_device_compute_limits") == 1, "Compute limits missing");
        Assert(rows.Length == 4, "Not exactly four requested formats");
        for (int i = 0; i < 4; i++)
        {
            Assert(rows[i].Detail.Contains("original_requested_format=" + names[i] + ";"), "Wrong format order");
            Assert(rows[i].Detail.Contains("actual_image_view=unverified"), "Invented GPU image view");
            Assert(rows[i].Detail.Contains("actual_fft_dispatch=unverified"), "Invented dispatch proof");
        }
        Assert(rows[0].Detail.Contains("render_texture_supported=unavailable"), "Per-format failure not isolated");
        Assert(rows[1].Detail.Contains("random_write_supported=unavailable"), "Random-write failure not isolated");
        Assert(rows[2].Detail.Contains("random_write_supported=False"), "Unsupported format falsely positive");
        Assert(rows[3].Detail.Contains("random_write_supported=True"), "Supported format falsely negative");
        Assert(logs.Single(x => x.Operation == "fft_device_compute_limits").Detail.Contains("max_group_invocations=1024"), "Group limit absent");
        var before = logs.Count;
        AndroidRuntimeLog.Initialize();
        Assert(before == logs.Count, "Repeated startup probe");
        AndroidRuntimeLog.Shutdown();

        logs.Clear();
        UnityEngine.SystemInfo.FailLimits = true;
        AndroidRuntimeLog.Initialize();
        Assert(logs.Count(x => x.Operation == "logger.ready") == 1, "Main logger disabled by capability failure");
        Assert(logs.Count(x => x.Operation == "fft_device_capabilities.unavailable") == 1, "Missing failure diagnostic");
        Assert(AndroidRuntimeLog.Status == "ready", "Logger error from optional device probe");
        AndroidRuntimeLog.Write("test", "after_probe");
        Assert(logs.Any(x => x.Operation == "after_probe"), "Logger unusable after probe failure");
        AndroidRuntimeLog.Shutdown();
        Console.WriteLine("RAFT_B06_FFT_CAPABILITIES_SYNTHETIC success=true formats=4 failure_isolation=true logger_preserved=true unity_or_gpu_test=false");
        return 0;
    }
}
