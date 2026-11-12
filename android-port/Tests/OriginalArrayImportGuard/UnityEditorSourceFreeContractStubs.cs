// Compilation-only stand-ins. Never claim they prove Unity Editor importing a
// real AssetRipper Texture2DArray, color parity or GPU execution.
using System;
namespace UnityEngine
{
    public static class Application { public static string dataPath => "/tmp/Assets"; }
    public static class Debug { public static void Log(string message) { } }
    public static class JsonUtility { public static T FromJson<T>(string json) => default(T); }
    public sealed class Texture2DArray
    {
        public int width { get; set; }
        public int height { get; set; }
        public int depth { get; set; }
        public int mipmapCount { get; set; }
    }
}
namespace UnityEditor
{
    public enum TextureImporterShape { Texture2D = 1, TextureCube = 2, Texture2DArray = 4, Texture3D = 8 }
    public sealed class TextureImporterSettings
    {
        public TextureImporterShape textureShape { get; set; }
        public int flipbookRows { get; set; }
        public int flipbookColumns { get; set; }
    }
    public class AssetImporter { public static AssetImporter GetAtPath(string path) => null; }
    public sealed class TextureImporter : AssetImporter
    {
        public void ReadTextureSettings(TextureImporterSettings output) { }
    }
    public static class AssetDatabase
    {
        public static string GUIDToAssetPath(string guid) => null;
        public static T LoadAssetAtPath<T>(string path) where T : class => null;
    }
}
namespace UnityEditor.Build
{
    public sealed class BuildFailedException : Exception
    {
        public BuildFailedException(string message) : base(message) { }
    }
}
