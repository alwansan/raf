#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace RaftAndroid.Editor
{
    /// <summary>
    /// Read-only imported Unity shader topology diagnostic. This is NOT proof
    /// of source-equivalent DXBC, original GUID, runtime binding or GPU pixels.
    /// Never edits .shader, .meta, Material or scene; safe in owner-native builds.
    /// </summary>
    public static class GTOriginalWaterPassImportProbe
    {
        private struct Expected
        {
            public string Label;
            public string ExactShaderName;
            public int OriginalSourcePasses;
            public int LoggedPassLowerBound;
            public Expected(string label, string shader, int sourcePasses, int logFloor)
            {
                Label = label;
                ExactShaderName = shader;
                OriginalSourcePasses = sourcePasses;
                LoggedPassLowerBound = logFloor;
            }
        }

        // Source authentic: Spectrum B09 original 7 passes/28 VS+FS stage variants;
        // Foam B24 original 2 passes. Log floor of 6 Spectrum is NOT full parity.
        private static readonly Expected[] Targets =
        {
            new Expected("spectrum", "UltimateWater/Spectrum/Water Spectrum", 7, 6),
            new Expected("foam_global", "UltimateWater/Foam/Global", 2, 2),
        };

        /// <summary>
        /// Production-only hard gate after original ZIP2-backed Spectrum
        /// ShaderLab installation. Source authenticity / unchanged .meta GUID
        /// is verified by the preceding private Python stage, NOT by this
        /// method. This checks one real imported seven-pass shader with no
        /// ShaderUtil-reported compile error; never claim Android GPU pixels.
        /// </summary>
        public static void RequireOriginalSpectrumSevenPasses()
        {
            const string originalName = "UltimateWater/Spectrum/Water Spectrum";
            string[] shaderIds = AssetDatabase.FindAssets("t:Shader", new[] { "Assets" });
            int matching = 0;
            int wrongPasses = 0;
            int compilerErrors = 0;
            int invalidFiles = 0;
            int dummy = 0;
            foreach (string id in shaderIds)
            {
                string path = AssetDatabase.GUIDToAssetPath(id);
                if (string.IsNullOrEmpty(path) ||
                    !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                    !path.EndsWith(".shader", StringComparison.OrdinalIgnoreCase))
                    continue;
                Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
                if (shader == null ||
                    !string.Equals(shader.name, originalName, StringComparison.Ordinal))
                    continue;
                matching++;
                if (shader.passCount != 7) wrongPasses++;
                if (ShaderUtil.ShaderHasError(shader)) compilerErrors++;
                try
                {
                    string assets = Path.GetFullPath(Application.dataPath);
                    string absolute = Path.GetFullPath(Path.Combine(
                        assets, path.Substring("Assets/".Length).Replace(
                            '/', Path.DirectorySeparatorChar)));
                    if (!absolute.StartsWith(
                        assets + Path.DirectorySeparatorChar, StringComparison.Ordinal))
                    {
                        invalidFiles++;
                        continue;
                    }
                    FileInfo file = new FileInfo(absolute);
                    if (!file.Exists || file.Length < 1 ||
                        file.Length > 16 * 1024 * 1024)
                    {
                        invalidFiles++;
                        continue;
                    }
                    string content = File.ReadAllText(absolute);
                    if (content.Contains("//DummyShaderTextExporter") ||
                        content.Contains("// No subprograms found"))
                        dummy++;
                }
                catch (IOException) { invalidFiles++; }
                catch (UnauthorizedAccessException) { invalidFiles++; }
            }
            bool valid = matching == 1 && wrongPasses == 0 &&
                         compilerErrors == 0 && invalidFiles == 0 && dummy == 0;
            Debug.Log("GT_NATIVE_SPECTRUM_UNITY_IMPORT_GATE oneOriginalShader=" +
                      (matching == 1) + " sevenImportedPasses=" +
                      (matching == 1 && wrongPasses == 0) +
                      " shaderUtilCompilerErrors=" + compilerErrors +
                      " invalidSourceFiles=" + invalidFiles +
                      " originalDummyMarkers=" + dummy +
                      " accepted=" + valid +
                      " originalGUIDSourceVerifiedInPriorStage=true" +
                      " runtimeKeywordMaterialCB0SamplerParityVerified=false" +
                      " AdrenoPixelsVerified=false");
            if (!valid)
                throw new InvalidOperationException(
                    "GT_Native_Spectrum_original_seven_pass_import_or_compile_not_verified");
        }

        public static void Report()
        {
            // Search only local exported project shader assets. No names, GUIDs,
            // HLSL, asset paths or serialized shader source are emitted.
            string[] shaderIds = AssetDatabase.FindAssets("t:Shader", new[] { "Assets" });
            foreach (Expected target in Targets)
            {
                int found = 0;
                int placeholders = 0;
                int supported = 0;
                int minPasses = int.MaxValue;
                int maxPasses = -1;
                int invalidPaths = 0;
                foreach (string id in shaderIds)
                {
                    string path = AssetDatabase.GUIDToAssetPath(id);
                    if (string.IsNullOrEmpty(path) ||
                        !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                        !path.EndsWith(".shader", StringComparison.OrdinalIgnoreCase))
                        continue;
                    Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
                    if (shader == null || !string.Equals(
                            shader.name, target.ExactShaderName, StringComparison.Ordinal))
                        continue;
                    found++;
                    int passCount = shader.passCount;
                    minPasses = Math.Min(minPasses, passCount);
                    maxPasses = Math.Max(maxPasses, passCount);
                    if (shader.isSupported)
                        supported++;
                    // The XML-like metadata or source marker is diagnostic only.
                    // A shader without Dummy marker still needs program/GUID proof.
                    try
                    {
                        // Unity may be launched from a directory different from
                        // its -projectPath. Never resolve Assets relative to cwd.
                        string assetRoot = Path.GetFullPath(Application.dataPath);
                        string absolute = Path.GetFullPath(Path.Combine(
                            assetRoot,
                            path.Substring("Assets/".Length).Replace(
                                '/', Path.DirectorySeparatorChar)));
                        if (!absolute.StartsWith(
                                assetRoot + Path.DirectorySeparatorChar,
                                StringComparison.Ordinal))
                        {
                            invalidPaths++;
                            continue;
                        }
                        FileInfo file = new FileInfo(absolute);
                        if (!file.Exists || file.Length > 8 * 1024 * 1024 ||
                            file.Length < 1)
                        {
                            invalidPaths++;
                            continue;
                        }
                        if (File.ReadAllText(absolute).Contains("//DummyShaderTextExporter"))
                            placeholders++;
                    }
                    catch (IOException)
                    {
                        invalidPaths++;
                    }
                    catch (UnauthorizedAccessException)
                    {
                        invalidPaths++;
                    }
                }
                bool structuralCandidate =
                    found == 1 && invalidPaths == 0 && placeholders == 0 &&
                    minPasses == target.OriginalSourcePasses;
                Debug.Log("GT_WATER_IMPORTED_PASS_DIAGNOSTIC family=" + target.Label +
                    " exactNamedExportedShaders=" + found +
                    " editorPassesMin=" + (found == 0 ? -1 : minPasses) +
                    " editorPassesMax=" + maxPasses +
                    " originalSourcePasses=" + target.OriginalSourcePasses +
                    " logRequiredMinimum=" + target.LoggedPassLowerBound +
                    " importerDummyMarkerCount=" + placeholders +
                    " importerInvalidFiles=" + invalidPaths +
                    " supportedOnEditorHost=" + supported +
                    " sourceStructureCandidateOnly=" + structuralCandidate +
                    " sourceGUIDAndMaterialVerified=false" +
                    " shaderProgramKeywordParityVerified=false" +
                    " AndroidGpuAndPhonePixelsVerified=false");
            }
        }
    }
}
#endif
