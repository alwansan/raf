using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    /// <summary>
    /// PRIVATE source-derived single-seven-pass Spectrum keyword-index4
    /// diagnostic only. This does not prove global/local keyword flag scope,
    /// original game Material/GUID sampler CB0/RT upload or phone pixels.
    /// All source-derived names and ShaderLab are runner-private.
    /// </summary>
    public static class OriginalSpectrumKeywordRouterValidation
    {
        [Serializable]
        private sealed class Safe
        {
            public string status;
            public string unityVersion;
            public string failureType;
            public int sourceOriginalPasses;
            public int sourceOriginalKeywordIndex;
            public int keywordPragmas;
            public int importedPasses;
            public int ShaderVariantCollectionCount;
            public int shaderErrorCount;
            public int shaderMessageCount;
            public long privateAndroidVulkanBundleBytes;
            public bool importedPrivateShader;
            public bool registeredBothKeywordVariants;
            public bool privateAndroidVulkanBundleBuilt;
            public bool editorShaderImportAndCompilationProvisional;
            public bool exactOriginalKeywordScopeFlagsProven;
            public bool originalMaterialRuntimeKeywordSelectionProven;
            public bool originalMaterialGUIDSamplerCB0RenderTargetBindingProven;
            public bool originalGameShaderOrAssetsModified;
            public bool phoneAdrenoPixelsVerified;
            public bool originalShaderSourceOrKeywordPublished;
        }

        public static void Validate()
        {
            var result = new Safe {
                status = "INCONCLUSIVE",
                unityVersion = Application.unityVersion,
                sourceOriginalPasses = 7,
                sourceOriginalKeywordIndex = 4,
                exactOriginalKeywordScopeFlagsProven = false,
                originalMaterialRuntimeKeywordSelectionProven = false,
                originalMaterialGUIDSamplerCB0RenderTargetBindingProven = false,
                originalGameShaderOrAssetsModified = false,
                phoneAdrenoPixelsVerified = false,
                originalShaderSourceOrKeywordPublished = false
            };
            int exitCode = 1;
            string root = Directory.GetParent(Application.dataPath).FullName;
            string safeDir = Path.Combine(root, "ProbeResults");
            Directory.CreateDirectory(safeDir);
            try
            {
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("UnpinnedPrivateUnity");
                string keyword = File.ReadAllText(Path.Combine(root,
                    "GTPrivateOriginalKeyword.txt")).Trim();
                if (keyword.Length < 1 || keyword.Length > 128 ||
                    !Regex.IsMatch(keyword, @"^[_A-Za-z][_A-Za-z0-9]*$"))
                    throw new InvalidOperationException("PrivateOriginalKeywordInvalid");
                const string path = "Assets/GTPrivateSpectrumKeyword.shader";
                string source = File.ReadAllText(Path.Combine(root, path));
                var authored = Regex.Matches(source,
                    @"(?m)^[ \t]*#pragma multi_compile __ ([_A-Za-z][_A-Za-z0-9]*)[ \t]*$")
                    .Cast<Match>().Select(m => m.Groups[1].Value).ToArray();
                result.keywordPragmas = authored.Length;
                if (authored.Length != 7 || authored.Any(name => name != keyword))
                    throw new InvalidOperationException("OriginalPrivateSevenPassKeywordRoutingInvalid");

                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                    new [] { GraphicsDeviceType.Vulkan });
                if (!PlayerSettings.GetGraphicsAPIs(BuildTarget.Android)
                    .SequenceEqual(new [] { GraphicsDeviceType.Vulkan }))
                    throw new InvalidOperationException("PrivateAndroidVulkanTargetNotSet");
                AssetDatabase.ImportAsset(path,
                    ImportAssetOptions.ForceSynchronousImport |
                    ImportAssetOptions.ForceUpdate);
                Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
                if (shader == null)
                    throw new InvalidOperationException("PrivateUnifiedSpectrumShaderMissing");
                result.importedPrivateShader = true;
                Material material = new Material(shader);
                try
                {
                    result.importedPasses = material.passCount;
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(material);
                }
                if (result.importedPasses != 7)
                    throw new InvalidOperationException("PrivateUnifiedShaderSevenPassMismatch");
                var variants = new ShaderVariantCollection();
                var normal = new ShaderVariantCollection.ShaderVariant(
                    shader, PassType.Normal, Array.Empty<string>());
                var on = new ShaderVariantCollection.ShaderVariant(
                    shader, PassType.Normal, new[] { keyword });
                if (!variants.Add(normal) || !variants.Add(on))
                    throw new InvalidOperationException("OriginalPrivateKeywordVariantNotRegistered");
                result.ShaderVariantCollectionCount = variants.variantCount;
                result.registeredBothKeywordVariants =
                    result.ShaderVariantCollectionCount == 2;
                if (!result.registeredBothKeywordVariants)
                    throw new InvalidOperationException("OriginalPrivateKeywordMatrixIncomplete");
                const string variantsPath = "Assets/GTPrivateSpectrumKeyword.shadervariants";
                AssetDatabase.CreateAsset(variants, variantsPath);
                AssetDatabase.SaveAssets();
                var folder = Path.Combine(safeDir,"private-source-keyword-android-bundles");
                Directory.CreateDirectory(folder);
                var bundles = new[] { new AssetBundleBuild {
                    assetBundleName = "gt-private-spectrum-source-keyword-index4",
                    assetNames = new[] { path, variantsPath }
                }};
                var bundleResult = BuildPipeline.BuildAssetBundles(folder, bundles,
                    BuildAssetBundleOptions.StrictMode |
                    BuildAssetBundleOptions.ForceRebuildAssetBundle,
                    BuildTarget.Android);
                string file = Path.Combine(folder,
                    "gt-private-spectrum-source-keyword-index4");
                result.privateAndroidVulkanBundleBuilt =
                    bundleResult != null && File.Exists(file);
                result.privateAndroidVulkanBundleBytes = File.Exists(file)
                    ? new FileInfo(file).Length : 0;
                var errors = ShaderUtil.GetShaderMessages(shader);
                result.shaderMessageCount = errors.Length;
                result.shaderErrorCount = errors.Count(
                    message => message.severity.ToString() == "Error");
                // PROVISIONAL until strict SECOND JOB reads fully finalized
                // Unity Editor logs. ShaderUtil can miss GLSL link errors.
                result.editorShaderImportAndCompilationProvisional =
                    result.privateAndroidVulkanBundleBuilt &&
                    result.privateAndroidVulkanBundleBytes > 0 &&
                    result.shaderErrorCount == 0 &&
                    !ShaderUtil.ShaderHasError(shader);
                result.status = result.editorShaderImportAndCompilationProvisional
                    ? "PRIVATE_SPECTRUM_UNIFIED_ORIGINAL_INDEX4_KEYWORD_SEVEN_PASS_PROVISIONAL_UNITY_BUNDLE"
                    : "INCONCLUSIVE";
                if (result.editorShaderImportAndCompilationProvisional)
                    exitCode = 0;
            }
            catch (Exception failure)
            {
                // TYPE only; never original keyword name or ShaderLab source.
                result.failureType = failure.GetType().Name;
            }
            File.WriteAllText(Path.Combine(safeDir,
                "gt-spectrum-unified-keyword-unity-safe.json"),
                JsonUtility.ToJson(result,true));
            Debug.Log("GT_SPECTRUM_UNIFIED_KEYWORD_UNITY_SAFE " +
                JsonUtility.ToJson(result));
            EditorApplication.Exit(exitCode);
        }
    }
}
