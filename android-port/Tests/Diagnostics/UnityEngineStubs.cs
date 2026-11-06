// Test-only, synthetic Unity API surface. Never imported by Unity game staging.
// Compile the real AndroidRuntimeLog.cs source under UNITY_ANDROID in .NET8.
namespace UnityEngine
{
    public static class Application
    {
        public static string persistentDataPath { get; set; }
        public static string version => "synthetic-0";
        public static string unityVersion => "2021.3.45f2-test-stub";
        public static string identifier => "test.local.raft";
    }

    public enum RenderTextureFormat { RGHalf, RGFloat, ARGBHalf, ARGBFloat }

    public static class SystemInfo
    {
        public static string deviceModel => "synthetic-test";
        public static string operatingSystem => "synthetic-test";
        public static string graphicsDeviceName => "synthetic-gpu";
        public static string graphicsDeviceType => "Vulkan-test";
        public static string graphicsDeviceVersion => "synthetic";
        public static string graphicsDeviceVendor => "synthetic";
        public static bool supportsComputeShaders => true;
        public static int graphicsShaderLevel => 50;
        public static string processorType => "synthetic-cpu";
        public static int processorCount => 8;
        public static int systemMemorySize => 8192;
        public static int maxComputeWorkGroupSize => 1024;
        public static int maxComputeWorkGroupSizeX => 65535;
        public static int maxComputeWorkGroupSizeY => 65535;
        public static int maxComputeWorkGroupSizeZ => 65535;
        public static bool SupportsRenderTextureFormat(RenderTextureFormat format) => true;
        public static bool SupportsRandomWriteOnRenderTextureFormat(RenderTextureFormat format) => true;
    }
}
