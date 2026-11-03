using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftW1
{
    // Deliberately builds ONE private shader asset bundle, never a Player/APK.
    public static class DepthShaderValidation
    {
        [Serializable]
        private sealed class Result
        {
            public string unityVersion;
            public string shaderSha256;
            public string messageDigest;
            public int shaderMessages;
            public int shaderErrors;
            public int observedMaterialPassCount;
            public long privateBundleBytes;
            public bool shaderImported;
            public bool androidVulkanOnly;
            public bool privateShaderBundleBuilt;
            public bool shaderLabUnityValidated;
            public bool numericOrVisualEquivalence;
            public bool gameOrApkBuilt;
            public string failureType;
        }

        private static string Hash(byte[] bytes)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        public static void Validate()
        {
            var result = new Result { unityVersion = Application.unityVersion };
            string root = Directory.GetParent(Application.dataPath).FullName;
            string reports = Path.Combine(root, "ProbeResults");
            Directory.CreateDirectory(reports);
            int exitCode = 1;
            try
            {
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("PinnedUnityVersionMismatch");
                string path = "Assets/W1Depth.shader";
                result.shaderSha256 = Hash(File.ReadAllBytes(Path.Combine(root, path)));
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
                result.androidVulkanOnly = PlayerSettings.GetGraphicsAPIs(BuildTarget.Android).SequenceEqual(new[] { GraphicsDeviceType.Vulkan });
                AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
                result.shaderImported = shader != null;
                if (shader == null) throw new InvalidOperationException("ShaderImportFailed");
                using (var material = new DisposableMaterial(shader))
                    result.observedMaterialPassCount = material.Value.passCount;
                string destination = Path.Combine(reports, "private-shader-bundles");
                Directory.CreateDirectory(destination);
                var build = new AssetBundleBuild { assetBundleName = "w1-depth-private", assetNames = new[] { path } };
                var manifest = BuildPipeline.BuildAssetBundles(destination, new[] { build },
                    BuildAssetBundleOptions.ForceRebuildAssetBundle | BuildAssetBundleOptions.StrictMode,
                    BuildTarget.Android);
                string bundle = Path.Combine(destination, "w1-depth-private");
                result.privateShaderBundleBuilt = manifest != null && File.Exists(bundle);
                result.privateBundleBytes = File.Exists(bundle) ? new FileInfo(bundle).Length : 0;
                var messages = ShaderUtil.GetShaderMessages(shader);
                result.shaderMessages = messages.Length;
                result.shaderErrors = messages.Count(m => m.severity.ToString() == "Error");
                // Keep compiler contents private: report only count and commitment.
                result.messageDigest = Hash(Encoding.UTF8.GetBytes(string.Join("\n", messages.Select(m => m.message))));
                result.shaderLabUnityValidated = result.shaderImported && result.androidVulkanOnly &&
                    result.privateShaderBundleBuilt && result.privateBundleBytes > 0 && result.shaderErrors == 0 && !ShaderUtil.ShaderHasError(shader);
                exitCode = result.shaderLabUnityValidated ? 0 : 1;
            }
            catch (Exception exception)
            {
                result.failureType = exception.GetType().Name;
            }
            File.WriteAllText(Path.Combine(reports, "w1-unity-result.json"), JsonUtility.ToJson(result, true));
            Debug.Log("RAFT_W1_UNITY_SHADER_PROBE " + JsonUtility.ToJson(result));
            EditorApplication.Exit(exitCode);
        }

        private sealed class DisposableMaterial : IDisposable
        {
            public Material Value { get; private set; }
            public DisposableMaterial(Shader shader) { Value = new Material(shader); }
            public void Dispose() { UnityEngine.Object.DestroyImmediate(Value); }
        }
    }
}
