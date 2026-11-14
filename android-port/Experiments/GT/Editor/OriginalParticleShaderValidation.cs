using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    /// <summary>
    /// Compiles original-derived private particle shader candidates in Unity.
    /// Never updates Raft Materials, original scene data or original Shader GUIDs.
    /// Neither original HLSL nor private keyword names leave the runner as a report.
    /// </summary>
    public static class OriginalParticleShaderValidation
    {
        [Serializable]
        private sealed class SafeResult
        {
            public string status;
            public string unityVersion;
            public string candidateShaderSha256;
            public string failureType;
            public int sourceKeywordDimensions;
            public int sourceKeywordCombinations;
            public int registeredKeywordVariants;
            public int materialPassCount;
            public int shaderMessageCount;
            public int shaderErrorCount;
            public long privateBundleBytes;
            public bool importedPrivateOriginalShader;
            public bool androidVulkanOnly;
            public bool privateAndroidShaderBundleBuilt;
            public bool unityEditorShaderImportAndCompilationProven;
            public bool originalMaterialBindingProven;
            public bool originalRuntimeKeywordSelectionParityProven;
            public bool originalAndroidAdrenoPixelsProven;
            public bool originalGameShadersOrGUIDsChanged;
            public bool gamePlayerBuilt;
            public bool originalShaderNamesOrBytecodePublished;
        }

        private static string[] KeywordNames(string source, int dimensions)
        {
            var names = Regex.Matches(source,
                @"(?m)^[ \t]*#pragma multi_compile __ ([A-Za-z_][A-Za-z_0-9]*)[ \t]*$")
                .Cast<Match>().Select(m => m.Groups[1].Value).ToArray();
            if (names.Length != dimensions || names.Distinct().Count() != dimensions)
                throw new InvalidOperationException("PrivateSourceKeywordDimensionChanged");
            return names;
        }

        public static void Validate()
        {
            var result = new SafeResult {
                status = "INCONCLUSIVE",
                unityVersion = Application.unityVersion,
                originalMaterialBindingProven = false,
                originalRuntimeKeywordSelectionParityProven = false,
                originalAndroidAdrenoPixelsProven = false,
                originalGameShadersOrGUIDsChanged = false,
                gamePlayerBuilt = false,
                originalShaderNamesOrBytecodePublished = false
            };
            string root = Directory.GetParent(Application.dataPath).FullName;
            string evidence = Path.Combine(root, "ProbeResults");
            Directory.CreateDirectory(evidence);
            bool smoke34 = File.Exists(Path.Combine(evidence, "smoke34"));
            bool candle16 = File.Exists(Path.Combine(evidence, "candle16"));
            int exitCode = 1;
            try
            {
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("UnpinnedUnityVersion");
                const string shaderAsset = "Assets/GTPrivateOriginal.shader";
                string shaderPath = Path.Combine(root, shaderAsset);
                var keywords = KeywordNames(File.ReadAllText(shaderPath), smoke34 || candle16 ? 1 : 2);
                using (var sha256 = SHA256.Create())
                using (var stream = File.OpenRead(shaderPath))
                {
                    result.candidateShaderSha256 = BitConverter.ToString(sha256.ComputeHash(stream))
                        .Replace("-", "").ToLowerInvariant();
                }
                result.sourceKeywordDimensions = keywords.Length;
                result.sourceKeywordCombinations = 1 << keywords.Length;

                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                    new[] { GraphicsDeviceType.Vulkan });
                result.androidVulkanOnly =
                    PlayerSettings.GetGraphicsAPIs(BuildTarget.Android)
                    .SequenceEqual(new[] { GraphicsDeviceType.Vulkan });
                if (!result.androidVulkanOnly)
                    throw new InvalidOperationException("OriginalPrivateVulkanTargetUnavailable");

                AssetDatabase.ImportAsset(shaderAsset,
                    ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                var shader = AssetDatabase.LoadAssetAtPath<Shader>(shaderAsset);
                result.importedPrivateOriginalShader = shader != null;
                if (shader == null)
                    throw new InvalidOperationException("PrivateOriginalShaderImportMissing");
                var material = new Material(shader);
                try { result.materialPassCount = material.passCount; }
                finally { UnityEngine.Object.DestroyImmediate(material); }
                if (result.materialPassCount != 1)
                    throw new InvalidOperationException("OriginalParticleOnePassNotImported");

                // Unity 2021 ShaderVariantCollection derives from UnityEngine.Object,
                // not ScriptableObject; construct with its public constructor.
                var collection = new ShaderVariantCollection();
                var names = new HashSet<string>();
                for (int bits = 0; bits < result.sourceKeywordCombinations; ++bits)
                {
                    var enabled = keywords.Where((value, i) =>
                        (bits & (1 << i)) != 0).ToArray();
                    if (!names.Add(string.Join("|", enabled)))
                        throw new InvalidOperationException("DuplicateOriginalVariantSelection");
                    var variant = new ShaderVariantCollection.ShaderVariant(
                        shader, PassType.Normal, enabled);
                    if (!collection.Add(variant))
                        throw new InvalidOperationException("OriginalPrivateVariantNotRegistered");
                    result.registeredKeywordVariants++;
                }
                if (result.registeredKeywordVariants != result.sourceKeywordCombinations)
                    throw new InvalidOperationException("IncompleteOriginalKeywordMatrix");
                const string variantsAsset = "Assets/GTPrivateOriginal.shadervariants";
                AssetDatabase.CreateAsset(collection, variantsAsset);
                AssetDatabase.SaveAssets();

                var target = Path.Combine(evidence, "private-android-particle-bundle");
                Directory.CreateDirectory(target);
                var build = new AssetBundleBuild {
                    assetBundleName = "gt-private-original-particle",
                    assetNames = new[] { shaderAsset, variantsAsset }
                };
                var manifest = BuildPipeline.BuildAssetBundles(target,
                    new[] { build },
                    BuildAssetBundleOptions.ForceRebuildAssetBundle |
                    BuildAssetBundleOptions.StrictMode,
                    BuildTarget.Android);
                var file = Path.Combine(target, "gt-private-original-particle");
                result.privateAndroidShaderBundleBuilt =
                    manifest != null && File.Exists(file);
                result.privateBundleBytes = File.Exists(file)
                    ? new FileInfo(file).Length : 0;

                var messages = ShaderUtil.GetShaderMessages(shader);
                result.shaderMessageCount = messages.Length;
                result.shaderErrorCount =
                    messages.Count(m => m.severity.ToString() == "Error");
                result.unityEditorShaderImportAndCompilationProven =
                    result.privateAndroidShaderBundleBuilt &&
                    result.privateBundleBytes > 0 &&
                    result.shaderErrorCount == 0 &&
                    !ShaderUtil.ShaderHasError(shader);
                result.status = result.unityEditorShaderImportAndCompilationProven
                    ? (smoke34 ? "ORIGINAL_PRIVATE_SMOKE34_ANDROID_VULKAN_SHADER_BUNDLE_COMPILED"
                               : candle16 ? "ORIGINAL_PRIVATE_CANDLE16_ANDROID_VULKAN_SHADER_BUNDLE_COMPILED"
                               : "ORIGINAL_PRIVATE_PARTICLE108_ANDROID_VULKAN_SHADER_BUNDLE_COMPILED")
                    : "INCONCLUSIVE";
                if (result.unityEditorShaderImportAndCompilationProven)
                    exitCode = 0;
            }
            catch (Exception exception)
            {
                // Exception TYPE only; original names, HLSL and shader errors
                // must not enter the JSON or Debug.Log.
                result.failureType = exception.GetType().Name;
            }
            File.WriteAllText(Path.Combine(evidence, "gt-particle108-private-unity-safe.json"),
                JsonUtility.ToJson(result, true));
            Debug.Log("GT_PRIVATE_PARTICLE108_UNITY_SAFE " + JsonUtility.ToJson(result));
            EditorApplication.Exit(exitCode);
        }
    }
}
