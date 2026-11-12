using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    /// <summary>
    /// Disposable synthetic Unity 2021 global/local keyword control ONLY.
    /// No original Raft Shader, Material, GUID, source program or keyword name.
    /// </summary>
    public static class GTKeywordScopeControl
    {
        [Serializable]
        private sealed class Safe
        {
            public string status = "INCONCLUSIVE";
            public string unityVersion;
            public string failureType;
            public bool globalKeywordIsOverridable;
            public bool localKeywordIsOverridable;
            public bool globalAndLocalShadersImported;
            public bool androidVulkanBundleBuilt;
            public long androidBundleBytes;
            public int shaderErrorCount;
            public bool originalGameAssetsModified = false;
            public bool originalSourceKeywordFlagMeaningProven = false;
            public bool AdrenoPixelsVerified = false;
        }

        private static bool GetOverrideFlag(Shader shader, string expectedName)
        {
            var entries = shader.keywordSpace.keywords
                .Where(k => k.name == expectedName).ToArray();
            if (entries.Length != 1)
                throw new InvalidOperationException("SyntheticKeywordSpaceAmbiguous");
            return entries[0].isOverridable;
        }

        public static void Validate()
        {
            var r = new Safe { unityVersion = Application.unityVersion };
            int code = 1;
            string root = Directory.GetParent(Application.dataPath).FullName;
            string output = Path.Combine(root, "ProbeResults");
            Directory.CreateDirectory(output);
            try
            {
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("UnityVersionUnpinned");

                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                    new [] { GraphicsDeviceType.Vulkan });
                if (!PlayerSettings.GetGraphicsAPIs(BuildTarget.Android)
                    .SequenceEqual(new [] { GraphicsDeviceType.Vulkan }))
                    throw new InvalidOperationException("VulkanTargetUnpinned");

                const string globalPath = "Assets/GTScopeGlobal.shader";
                const string localPath = "Assets/GTScopeLocal.shader";
                AssetDatabase.ImportAsset(globalPath, ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
                AssetDatabase.ImportAsset(localPath, ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
                Shader global = AssetDatabase.LoadAssetAtPath<Shader>(globalPath);
                Shader local = AssetDatabase.LoadAssetAtPath<Shader>(localPath);
                if (global == null || local == null)
                    throw new InvalidOperationException("SyntheticShaderImportMissing");
                r.globalAndLocalShadersImported = true;
                r.globalKeywordIsOverridable =
                    GetOverrideFlag(global, "GT_SCOPE_PROBE");
                r.localKeywordIsOverridable =
                    GetOverrideFlag(local, "GT_SCOPE_PROBE");

                r.shaderErrorCount = ShaderUtil.GetShaderMessages(global).Count(
                    m => m.severity.ToString() == "Error") +
                    ShaderUtil.GetShaderMessages(local).Count(
                    m => m.severity.ToString() == "Error");
                if (!r.globalKeywordIsOverridable || r.localKeywordIsOverridable
                    || r.shaderErrorCount != 0 || ShaderUtil.ShaderHasError(global)
                    || ShaderUtil.ShaderHasError(local))
                    throw new InvalidOperationException("SyntheticScopeControlMismatch");

                string outFolder = Path.Combine(output, "gt-scope-bundles");
                Directory.CreateDirectory(outFolder);
                var builds = new[] { new AssetBundleBuild {
                    assetBundleName = "gt-scope-control",
                    assetNames = new [] { globalPath, localPath }
                }};
                var build = BuildPipeline.BuildAssetBundles(outFolder, builds,
                    BuildAssetBundleOptions.StrictMode |
                    BuildAssetBundleOptions.ForceRebuildAssetBundle,
                    BuildTarget.Android);
                string bundle = Path.Combine(outFolder, "gt-scope-control");
                r.androidVulkanBundleBuilt = build != null && File.Exists(bundle);
                r.androidBundleBytes = File.Exists(bundle)
                    ? new FileInfo(bundle).Length : 0L;
                if (!r.androidVulkanBundleBuilt || r.androidBundleBytes < 1L)
                    throw new InvalidOperationException("SyntheticAndroidScopeBundleEmpty");

                r.status = "SYNTHETIC_UNITY2021_KEYWORD_SCOPE_CONTROL_BUNDLE";
                code = 0;
            }
            catch (Exception e)
            {
                r.failureType = e.GetType().Name;
            }

            File.WriteAllText(Path.Combine(output, "gt-scope-unity-safe.json"),
                JsonUtility.ToJson(r, true));
            Debug.Log("GT_SYNTHETIC_SCOPE_UNITY_SAFE " + JsonUtility.ToJson(r));
            EditorApplication.Exit(code);
        }
    }
}
