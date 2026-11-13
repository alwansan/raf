using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    public static class Original921ShaderValidation
    {
        private static readonly int[] Counts = { 8, 13, 8, 4 };
        private static readonly PassType[] Passes = {
            PassType.ForwardBase, PassType.ForwardAdd, PassType.Deferred, PassType.ShadowCaster
        };

        [Serializable]
        private sealed class Result
        {
            public string unityVersion;
            public string failureType;
            public string checkpoint;
            public int passCount;
            public int registeredRoutes;
            public int errors;
            public bool androidVulkanOnly;
            public bool privateBundleCompiled;
        }

        public static void Validate()
        {
            var result = new Result { unityVersion = Application.unityVersion };
            var output = Path.Combine(Directory.GetParent(Application.dataPath).FullName, "ProbeResults");
            Directory.CreateDirectory(output);
            int exitCode = 1;
            try
            {
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("UnexpectedEditorVersion");
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
                result.androidVulkanOnly = PlayerSettings.GetGraphicsAPIs(BuildTarget.Android)
                    .SequenceEqual(new[] { GraphicsDeviceType.Vulkan });
                const string shaderPath = "Assets/GTOriginal921.shader";
                const string collectionPath = "Assets/GTOriginal921.shadervariants";
                result.checkpoint = "import";
                AssetDatabase.ImportAsset(shaderPath,
                    ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                var shader = AssetDatabase.LoadAssetAtPath<Shader>(shaderPath);
                if (shader == null)
                    throw new InvalidOperationException("Original921ShaderMissing");
                result.passCount = shader.passCount;
                if (result.passCount != Counts.Length)
                    throw new InvalidOperationException("Original921ShaderPassCountMismatch");

                result.checkpoint = "register";
                var collection = new ShaderVariantCollection();
                for (int pass = 0; pass < Passes.Length; ++pass)
                {
                    for (int variant = 0; variant < Counts[pass]; ++variant)
                    {
                        var keywords = variant == 0 ? Array.Empty<string>() :
                            new[] { $"GT_ORIGINAL_921_P{pass}_V{variant}" };
                        if (!collection.Add(new ShaderVariantCollection.ShaderVariant(shader, Passes[pass], keywords)))
                            throw new InvalidOperationException("Original921VariantNotRegistered");
                        ++result.registeredRoutes;
                    }
                }
                AssetDatabase.CreateAsset(collection, collectionPath);
                AssetDatabase.SaveAssets();

                const string bundleName = "gt-original-921";
                var bundleDirectory = Path.Combine(output, "Private");
                Directory.CreateDirectory(bundleDirectory);
                var bundle = new AssetBundleBuild {
                    assetBundleName = bundleName, assetNames = new[] { shaderPath, collectionPath }
                };
                result.checkpoint = "compile";
                var manifest = BuildPipeline.BuildAssetBundles(bundleDirectory, new[] { bundle },
                    BuildAssetBundleOptions.ForceRebuildAssetBundle | BuildAssetBundleOptions.StrictMode,
                    BuildTarget.Android);
                result.checkpoint = "compiler_results";
                result.errors = ShaderUtil.GetShaderMessages(shader)
                    .Count(message => message.severity.ToString() == "Error");
                var artifact = new FileInfo(Path.Combine(bundleDirectory, bundleName));
                result.privateBundleCompiled = manifest != null && artifact.Exists && artifact.Length > 0
                    && result.errors == 0 && !ShaderUtil.ShaderHasError(shader);
                exitCode = result.privateBundleCompiled && result.androidVulkanOnly ? 0 : 1;
            }
            catch (Exception exception)
            {
                result.failureType = exception.GetType().Name;
            }
            File.WriteAllText(Path.Combine(output, "gt-original-921-unity-safe.json"),
                JsonUtility.ToJson(result, true));
            Debug.Log("GT_ORIGINAL_921_UNITY_SAFE " + JsonUtility.ToJson(result));
            EditorApplication.Exit(exitCode);
        }
    }
}
