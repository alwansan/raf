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
        public bool syntheticCompileError;
        public int[] serializedPassCounts;
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
    public sealed class ShaderData
    {
        public sealed class Subshader
        {
            public int PassCount { get; set; }
        }
        private readonly int[] passes;
        public ShaderData(int[] passes) { this.passes = passes; }
        public int SerializedSubshaderCount => passes.Length;
        public Subshader GetSerializedSubshader(int index) => new Subshader { PassCount = passes[index] };
    }
    public static class ShaderUtil
    {
        public static bool ShaderHasError(UnityEngine.Shader shader)
        {
            return shader.syntheticCompileError;
        }
        public static ShaderData GetShaderData(UnityEngine.Shader shader)
        {
            return new ShaderData(shader.serializedPassCounts);
        }
    }
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

    private static void RequireDepthBlocked(string message)
    {
        try
        {
            RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalDepthTopology();
        }
        catch (InvalidOperationException)
        {
            return;
        }
        throw new InvalidOperationException(message);
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

            // Production hard gate must reject dummy one-pass even when
            // synthetic AssetDatabase reports that it isSupported.
            bool blocked = false;
            try
            {
                RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalSpectrumSevenPasses();
            }
            catch (InvalidOperationException) { blocked = true; }
            Require(blocked, "native sevenpass guard accepted dummy source");

            var spectrumShader=UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEngine.Shader>(
                "Assets/Water/Spectrum.shader");
            spectrumShader.passCount=7;
            File.WriteAllText(spectrum, "Shader \"synthetic\" { SubShader { Pass {} } }");
            RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalSpectrumSevenPasses();
            Require(UnityEngine.Debug.Lines.Any(x => x.StartsWith(
                "GT_NATIVE_SPECTRUM_UNITY_IMPORT_GATE oneOriginalShader=True")
                && x.Contains("accepted=True") &&
                x.Contains("AdrenoPixelsVerified=false")),
                "production original source gate positive structural control failed");

            spectrumShader.syntheticCompileError=true;
            blocked=false;
            try
            {
                RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalSpectrumSevenPasses();
            }
            catch (InvalidOperationException) { blocked=true; }
            Require(blocked, "shader compiler failures incorrectly accepted");
            spectrumShader.syntheticCompileError=false;

            var foamShader=UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEngine.Shader>(
                "Assets/Water/Foam.shader");
            RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalFoamTwoPasses();
            Require(UnityEngine.Debug.Lines.Any(x => x.StartsWith(
                "GT_NATIVE_FOAM_UNITY_IMPORT_GATE oneOriginalShader=True") &&
                x.Contains("twoImportedPasses=True") && x.Contains("accepted=True") &&
                x.Contains("AdrenoPixelsVerified=false")),
                "original Foam synthetic source gate positive two-pass case failed");
            foamShader.passCount=1;
            bool foamBlocked=false;
            try
            {
                RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalFoamTwoPasses();
            }
            catch (InvalidOperationException) { foamBlocked=true; }
            Require(foamBlocked, "native accepted original Foam one pass instead of two");
            foamShader.passCount=2;
            foamShader.syntheticCompileError=true;
            foamBlocked=false;
            try
            {
                RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalFoamTwoPasses();
            }
            catch (InvalidOperationException) { foamBlocked=true; }
            Require(foamBlocked, "native accepted original Foam compiler errors");
            foamShader.syntheticCompileError=false;
            File.WriteAllText(foam, "//DummyShaderTextExporter\nShader \"synthetic\" {}");
            foamBlocked=false;
            try
            {
                RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalFoamTwoPasses();
            }
            catch (InvalidOperationException) { foamBlocked=true; }
            Require(foamBlocked, "native accepted original Foam dummy ShaderLab");
            File.WriteAllText(foam, "Shader \"synthetic\" { SubShader { Pass {} Pass {} } }");

            RequireDepthBlocked("missing original Depth Copy was accepted");
            var depthShader = new UnityEngine.Shader
            {
                name = "UltimateWater/Depth/Depth Copy",
                passCount = 3,
                serializedPassCounts = new[] { 6, 3 },
            };
            UnityEditor.AssetDatabase.Register("synthetic-depth", "Assets/Water/Depth.shader", depthShader);
            RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalDepthTopology();
            depthShader.serializedPassCounts = new[] { 3, 6 };
            RequireDepthBlocked("reordered original Depth Copy SubShaders were accepted");
            depthShader.serializedPassCounts = new[] { 6, 3 };
            depthShader.syntheticCompileError = true;
            RequireDepthBlocked("original Depth Copy compiler errors were accepted");
            depthShader.syntheticCompileError = false;
            UnityEditor.AssetDatabase.Register("synthetic-depth-duplicate", "Assets/Water/OtherDepth.shader", depthShader);
            RequireDepthBlocked("duplicate original Depth Copy was accepted");

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
            blocked=false;
            try
            {
                RaftAndroid.Editor.GTOriginalWaterPassImportProbe.RequireOriginalSpectrumSevenPasses();
            }
            catch (InvalidOperationException) { blocked=true; }
            Require(blocked, "duplicate or escaped shader identity accepted for production");

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
