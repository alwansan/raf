using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    /// <summary>
    /// Diagnostic only: compile a SINGLE SHA-original-derived Spectrum 7-pass
    /// private ShaderLab candidate for Unity 2021.3 Android Vulkan.
    /// The real original keyword routing, game Material GUID, samplers, CB
    /// uploads and Adreno rendered pixels are NOT authenticated by this test.
    /// No game scenes, original shader .meta or original assets are edited.
    /// </summary>
    public static class OriginalSpectrumSevenPassValidation
    {
        [Serializable]
        private sealed class Safe
        {
            public string status;
            public string unityVersion;
            public string failureType;
            public int originalSourcePasses;
            public int isolatedVariantIndex;
            public int shaderPassCount;
            public int shaderErrorCount;
            public int shaderMessageCount;
            public long privateAndroidVulkanShaderBundleBytes;
            public bool importedPrivateShader;
            public bool privateAndroidVulkanBundleBuilt;
            public bool editorShaderImportAndCompilationProven;
            public bool sourceOriginalKeywordRoutingProven;
            public bool originalMaterialGuidOrSamplerBindingProven;
            public bool originalAndroidGameModified;
            public bool gamePlayerBuilt;
            public bool AdrenoPixelsVerified;
            public bool originalShaderBytecodeOrNamesPublished;
        }

        public static void Validate()
        {
            var result = new Safe {
                status = "INCONCLUSIVE",
                originalSourcePasses = 7,
                isolatedVariantIndex = 0,
                unityVersion = Application.unityVersion,
                sourceOriginalKeywordRoutingProven = false,
                originalMaterialGuidOrSamplerBindingProven = false,
                originalAndroidGameModified = false,
                gamePlayerBuilt = false,
                AdrenoPixelsVerified = false,
                originalShaderBytecodeOrNamesPublished = false,
            };
            int exit = 1;
            string root = Directory.GetParent(Application.dataPath).FullName;
            string safeDir = Path.Combine(root, "ProbeResults");
            Directory.CreateDirectory(safeDir);
            try
            {
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("UnsupportedUnityEditorVersion");
                // A runner-private numeric variant selector. No source keywords,
                // original Material GUID or shader bytecode are embedded here.
                string variant = File.ReadAllText(Path.Combine(
                    root, "GTPrivateSpectrumVariant.txt")).Trim();
                if (variant != "0" && variant != "1")
                    throw new InvalidOperationException("InvalidPrivateVariantSelector");
                result.isolatedVariantIndex = variant == "1" ? 1 : 0;
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                    new[] { GraphicsDeviceType.Vulkan });
                if (!PlayerSettings.GetGraphicsAPIs(BuildTarget.Android)
                    .SequenceEqual(new[] { GraphicsDeviceType.Vulkan }))
                    throw new InvalidOperationException("PrivateVulkanTargetUnavailable");

                const string asset = "Assets/GTPrivateSpectrum.shader";
                AssetDatabase.ImportAsset(asset,
                    ImportAssetOptions.ForceSynchronousImport |
                    ImportAssetOptions.ForceUpdate);
                Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(asset);
                if (shader == null)
                    throw new InvalidOperationException("PrivateShaderImportMissing");
                result.importedPrivateShader = true;
                Material m = new Material(shader);
                try
                {
                    result.shaderPassCount = m.passCount;
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(m);
                }
                if (result.shaderPassCount != 7)
                    throw new InvalidOperationException("OriginalSevenPassTopologyNotImported");
                string target = Path.Combine(safeDir, "original-private-spectrum-bundle");
                Directory.CreateDirectory(target);
                string bundleName = "gt-private-spectrum-source-variant" +
                    result.isolatedVariantIndex;
                var manifest = BuildPipeline.BuildAssetBundles(target,
                    new[] { new AssetBundleBuild {
                        assetBundleName = bundleName,
                        assetNames = new[] { asset }
                    }},
                    BuildAssetBundleOptions.ForceRebuildAssetBundle |
                    BuildAssetBundleOptions.StrictMode,
                    BuildTarget.Android);
                var bundle = Path.Combine(target, bundleName);
                result.privateAndroidVulkanBundleBuilt =
                    manifest != null && File.Exists(bundle);
                result.privateAndroidVulkanShaderBundleBytes = File.Exists(bundle)
                    ? new FileInfo(bundle).Length : 0;
                var messages = ShaderUtil.GetShaderMessages(shader);
                result.shaderMessageCount = messages.Length;
                result.shaderErrorCount = messages.Count(
                    message => message.severity.ToString() == "Error");
                result.editorShaderImportAndCompilationProven =
                    result.privateAndroidVulkanBundleBuilt &&
                    result.privateAndroidVulkanShaderBundleBytes > 0 &&
                    result.shaderErrorCount == 0 &&
                    !ShaderUtil.ShaderHasError(shader);
                if (result.editorShaderImportAndCompilationProven)
                {
                    result.status = "PRIVATE_ORIGINAL_SPECTRUM_VARIANT" +
                        result.isolatedVariantIndex +
                        "_SEVEN_PASS_UNITY_ANDROID_VULKAN_BUNDLE_COMPILED";
                    exit = 0;
                }
            }
            catch (Exception error)
            {
                result.failureType = error.GetType().Name;
            }
            string summary = JsonUtility.ToJson(result, true);
            File.WriteAllText(Path.Combine(
                safeDir, "gt-spectrum-sevenpass-unity-safe.json"), summary);
            Debug.Log("GT_SPECTRUM_SEVENPASS_UNITY_SAFE " + JsonUtility.ToJson(result));
            EditorApplication.Exit(exit);
        }
    }
}
