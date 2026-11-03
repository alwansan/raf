using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftW1Full
{
    public static class FullEnginePointerValidation
    {
        [Serializable] private sealed class Expected { public Item[] items; }
        [Serializable] private sealed class Item
        {
            public string assetPath, wrongAssetPath, shaderName;
            public string[] properties;
        }
        [Serializable] private sealed class Result
        {
            public string unityVersion, failureType;
            public int requestedMaterials, matchedShaderNames, matchedPropertyLayouts;
            public int wrongPointerControlsDetected, shaderErrors;
            public bool androidVulkanOnly, privateBundleBuilt, passed;
            public long privateBundleBytes;
            public bool fullGameExportVerified, phoneRenderingVerified, apkBuilt;
        }

        private static bool Matches(Item item, string path, bool properties)
        {
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null || material.shader == null || material.shader.name != item.shaderName) return false;
            if (!properties) return true;
            var shader = material.shader;
            return Enumerable.Range(0, shader.GetPropertyCount()).Select(shader.GetPropertyName).SequenceEqual(item.properties);
        }

        public static void Validate()
        {
            var result = new Result { unityVersion = Application.unityVersion };
            string root = Directory.GetParent(Application.dataPath).FullName;
            string reports = Path.Combine(root, "ProbeResults");
            Directory.CreateDirectory(reports);
            try
            {
                if (Application.unityVersion != "2021.3.45f2") throw new InvalidOperationException("PinnedUnityVersionMismatch");
                var expected = JsonUtility.FromJson<Expected>(File.ReadAllText(Path.Combine(root, "engine-expected-private.json")));
                if (expected.items == null || expected.items.Length < 9 || expected.items.Length > 165) throw new InvalidOperationException("ProbeInventoryMismatch");
                result.requestedMaterials = expected.items.Length;
                PlayerSettings.colorSpace = ColorSpace.Linear;
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
                result.androidVulkanOnly = PlayerSettings.GetGraphicsAPIs(BuildTarget.Android).SequenceEqual(new[] { GraphicsDeviceType.Vulkan });
                foreach (var item in expected.items)
                {
                    if (Matches(item, item.assetPath, false)) result.matchedShaderNames++;
                    if (Matches(item, item.assetPath, true)) result.matchedPropertyLayouts++;
                    if (!Matches(item, item.wrongAssetPath, false)) result.wrongPointerControlsDetected++;
                }
                if (result.matchedShaderNames != result.requestedMaterials || result.matchedPropertyLayouts != result.requestedMaterials || result.wrongPointerControlsDetected != result.requestedMaterials)
                    throw new InvalidOperationException("ActualEnginePointerOrPropertyMismatch");
                string bundles = Path.Combine(reports, "private-bundles");
                Directory.CreateDirectory(bundles);
                var build = new AssetBundleBuild { assetBundleName = "w1-full-engine-private", assetNames = expected.items.Select(x => x.assetPath).ToArray() };
                var manifest = BuildPipeline.BuildAssetBundles(bundles, new[] { build }, BuildAssetBundleOptions.StrictMode | BuildAssetBundleOptions.ForceRebuildAssetBundle, BuildTarget.Android);
                string bundle = Path.Combine(bundles, build.assetBundleName);
                result.privateBundleBuilt = manifest != null && File.Exists(bundle);
                result.privateBundleBytes = File.Exists(bundle) ? new FileInfo(bundle).Length : 0;
                foreach (var item in expected.items)
                {
                    var shader = AssetDatabase.LoadAssetAtPath<Material>(item.assetPath).shader;
                    result.shaderErrors += ShaderUtil.GetShaderMessages(shader).Count(x => x.severity.ToString() == "Error");
                }
                result.passed = result.androidVulkanOnly && result.privateBundleBuilt && result.privateBundleBytes > 0 && result.shaderErrors == 0;
            }
            catch (Exception error) { result.failureType = error.GetType().Name; }
            File.WriteAllText(Path.Combine(reports, "w1-full-engine-unity-summary.json"), JsonUtility.ToJson(result, true));
            Debug.Log("RAFT_W1_FULL_ENGINE_UNITY " + JsonUtility.ToJson(result));
            EditorApplication.Exit(result.passed ? 0 : 1);
        }
    }
}

