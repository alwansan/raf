#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftAndroid.Editor
{
    public static class GTIndexedFftValidation
    {
        public static void Validate()
        {
            const string assetPath = "Assets/DX11 FFT.compute";
            int registered = 0;
            bool bundleBuilt = false;
            try
            {
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
                AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(assetPath);
                if (shader == null)
                    throw new InvalidOperationException("Missing indexed compute import");
                for (int slot = 0; slot < 20; slot++)
                {
                    string name = $"RaftFftSlot{slot:00}";
                    if (!shader.HasKernel(name) || shader.FindKernel(name) != slot)
                        throw new InvalidOperationException("Indexed compute registration differs");
                    shader.GetKernelThreadGroupSizes(slot, out uint x, out uint y, out uint z);
                    uint expected = 64u << (slot % 10 / 2);
                    if (x != expected || y != 1 || z != 1)
                        throw new InvalidOperationException("Indexed compute workgroup differs");
                    registered++;
                }
                string output = Path.Combine(Path.GetTempPath(), "raft-fft-" + Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(output);
                try
                {
                    var bundle = new AssetBundleBuild { assetBundleName = "private-fft", assetNames = new[] { assetPath } };
                    bundleBuilt = BuildPipeline.BuildAssetBundles(output, new[] { bundle },
                        BuildAssetBundleOptions.ForceRebuildAssetBundle | BuildAssetBundleOptions.StrictMode,
                        BuildTarget.Android) != null && new FileInfo(Path.Combine(output, "private-fft")).Length > 0;
                }
                finally
                {
                    Directory.Delete(output, recursive: true);
                }
                if (!bundleBuilt || ShaderUtil.GetComputeShaderMessages(shader).Any(
                        message => message.severity.ToString() == "Error"))
                    throw new InvalidOperationException("Indexed compute Android compilation failed");

                Debug.Log($"GT_INDEXED_FFT_UNITY registration={registered} androidVulkanBundle={bundleBuilt} gpuParity=false");
                EditorApplication.Exit(0);
            }
            catch (Exception error)
            {
                Debug.LogError($"GT_INDEXED_FFT_UNITY registration={registered} androidVulkanBundle={bundleBuilt} failure={error.GetType().Name}");
                EditorApplication.Exit(1);
            }
        }
    }
}
#endif
