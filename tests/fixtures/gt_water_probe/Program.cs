// Pure synthetic Unity API facsimile. Never a real GPU/Unity compilation proof.
// This harness exercises GTOriginalWaterPassImportProbe against fake imported
// Shader records, synthetic .shader text and hostile relative Asset paths.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace UnityEngine
{
    public sealed class Shader
    {
        public string name;
        public int passCount;
        public bool isSupported;
    }
    public static class Application
    {
        public static string dataPath;
    }
    public static class Debug
    {
        public static readonly List<string> Lines = new List<string>();
        public static void Log(object message)
        {
            Lines.Add(Convert.ToString(message));
        }
    }
}

namespace UnityEditor
{
    public static class AssetDatabase
    {
        private static readonly Dictionary<string, string> Paths =
            new Dictionary<string, string>(StringComparer.Ordinal);
        private static readonly Dictionary<string, UnityEngine.Shader> Shaders =
            new Dictionary<string, UnityEngine.Shader>(StringComparer.Ordinal);
        public static void Register(string id, string path, UnityEngine.Shader shader)
        {
            Paths.Add(id, path);
            Shaders.Add(path, shader);
        }
        public static string[] FindAssets(string search, string[] roots)
        {
            if (search != "t:Shader" || roots.Length != 1 || roots[0] != "Assets")
                throw new InvalidOperationException("Unexpected asset search");
            return Paths.Keys.ToArray();
        }
        public static string GUIDToAssetPath(string id)
        {
            return Paths[id];
        }
        public static T LoadAssetAtPath<T>(string path) where T : class
        {
            return Shaders[path] as T;
        }
    }
}

public static class Program
{
    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static string Row(string family)
    {
        return UnityEngine.Debug.Lines.Single(
            line => line.StartsWith(
                "GT_WATER_IMPORTED_PASS_DIAGNOSTIC family=" + family + " ",
                StringComparison.Ordinal));
    }

    public static void Main()
    {
        string tmp = Path.Combine(Path.GetTempPath(),
            "gt-probe-" + Guid.NewGuid().ToString("N"));
        string assets = Path.Combine(tmp, "Assets");
        Directory.CreateDirectory(Path.Combine(assets, "Water"));
        UnityEngine.Application.dataPath = assets;
        try
        {
            string spectrum = Path.Combine(assets, "Water", "Spectrum.shader");
            string foam = Path.Combine(assets, "Water", "Foam.shader");
            File.WriteAllText(spectrum, "//DummyShaderTextExporter\nShader \"synthetic\" {}");
            File.WriteAllText(foam, "Shader \"synthetic\" { SubShader { Pass {} Pass {} } }");
            UnityEditor.AssetDatabase.Register(
                "synthetic-spectrum", "Assets/Water/Spectrum.shader",
                new UnityEngine.Shader
                {
                    name = "UltimateWater/Spectrum/Water Spectrum",
                    passCount = 1, isSupported = true
                });
            UnityEditor.AssetDatabase.Register(
                "synthetic-foam", "Assets/Water/Foam.shader",
                new UnityEngine.Shader
                {
                    name = "UltimateWater/Foam/Global",
                    passCount = 2, isSupported = true
                });

            RaftAndroid.Editor.GTOriginalWaterPassImportProbe.Report();
            Require(UnityEngine.Debug.Lines.Count == 2, "expected two shader families");
            Require(Row("spectrum").Contains("editorPassesMin=1 "),
                "spectrum dummy one-pass not detected");
            Require(Row("spectrum").Contains("originalSourcePasses=7 logRequiredMinimum=6 "),
                "source exact 7 vs logged floor 6 lost");
            Require(Row("spectrum").Contains("importerDummyMarkerCount=1 "),
                "dummy marker was not found inside project root");
            Require(Row("spectrum").Contains("sourceStructureCandidateOnly=False "),
                "dummy must not be accepted");
            Require(Row("foam_global").Contains("editorPassesMin=2 "),
                "source Foam exact 2pass baseline missing");
            Require(Row("foam_global").Contains("sourceStructureCandidateOnly=True "),
                "synthetic non-dummy shape should be a candidate only");
            Require(Row("foam_global").Contains("AndroidGpuAndPhonePixelsVerified=false"),
                "false phone pixel acceptance");

            // A malicious/redirected asset path must never be read as a
            // local project .shader, even if it resolves to a real outer file.
            UnityEditor.AssetDatabase.Register(
                "synthetic-traversal", "Assets/../../escape.shader",
                new UnityEngine.Shader
                {
                    name = "UltimateWater/Spectrum/Water Spectrum",
                    passCount = 7, isSupported = true
                });
            UnityEngine.Debug.Lines.Clear();
            RaftAndroid.Editor.GTOriginalWaterPassImportProbe.Report();
            Require(Row("spectrum").Contains("importerInvalidFiles=1 "),
                "path traversal was not rejected");
            Require(Row("spectrum").Contains("exactNamedExportedShaders=2 "),
                "duplicate target candidates were not detected");
            Require(Row("spectrum").Contains("sourceStructureCandidateOnly=False "),
                "duplicate or untrusted source should not pass");

            Console.WriteLine(
                "GT_WATER_SYNTHETIC_IMPORT_PROBE_VALID dummyDetected=true " +
                "sevenOriginalPasses=true deviceLogLowerBoundSix=true " +
                "twoPassFoamCandidateOnly=true pathTraversalRejected=true " +
                "UnityEditor2021OrAndroidGPUVerified=false");
        }
        finally
        {
            Directory.Delete(tmp, true);
        }
    }
}
