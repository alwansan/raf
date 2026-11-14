#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftAndroid.Editor
{
    public sealed class GTIndexedFftValidation : ScriptableObject
    {
        private const string FixtureGuid = "9f14a6e4dd044e5282dca378746aa831";
        private const long ComputeFileId = 7200000L;
        private const string HolderPath = "Assets/IndexedFftReferenceFixture.asset";
        public ComputeShader[] shaders;

        private static bool ImportReference(string yaml, ComputeShader expected)
        {
            File.WriteAllText(HolderPath, yaml);
            AssetDatabase.ImportAsset(HolderPath,
                ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            var holder = AssetDatabase.LoadAssetAtPath<GTIndexedFftValidation>(HolderPath);
            return holder != null && holder.shaders != null && holder.shaders.Length == 1
                && holder.shaders[0] == expected;
        }

        private static bool ValidateReference(ComputeShader shader)
        {
            var serializationMode = EditorSettings.serializationMode;
            try
            {
                EditorSettings.serializationMode = SerializationMode.ForceText;
                var holder = CreateInstance<GTIndexedFftValidation>();
                holder.shaders = new[] { shader };
                AssetDatabase.CreateAsset(holder, HolderPath);
                AssetDatabase.SaveAssets();
                string yaml = File.ReadAllText(HolderPath);
                var pointer = new Regex(
                    @"(\{fileID:\s*" + ComputeFileId + @",\s*guid:\s*" + FixtureGuid + @",\s*type:\s*)3(\})");
                if (pointer.Matches(yaml).Count != 1)
                    throw new InvalidOperationException("Unexpected imported compute reference in fixture");
                if (ImportReference(yaml.Replace(FixtureGuid, "00000000000000000000000000000001"), shader))
                    throw new InvalidOperationException("Broken reference control resolved");
                bool originalTypeResolves = ImportReference(pointer.Replace(yaml, "${1}2${2}"), shader);
                if (!ImportReference(yaml, shader))
                    throw new InvalidOperationException("Imported compute reference did not resolve");
                return originalTypeResolves;
            }
            finally
            {
                AssetDatabase.DeleteAsset(HolderPath);
                EditorSettings.serializationMode = serializationMode;
            }
        }

        public static void Validate()
        {
            const string assetPath = "Assets/DX11 FFT.compute";
            int registered = 0;
            bool bundleBuilt = false;
            bool originalReferenceTypeResolves = false;
            bool importedReferenceResolves = false;
            try
            {
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
                AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(assetPath);
                if (shader == null)
                    throw new InvalidOperationException("Missing indexed compute import");
                if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(shader, out string guid, out long fileId)
                    || guid != FixtureGuid || fileId != ComputeFileId)
                    throw new InvalidOperationException("Indexed compute GUID or local file ID differs");
                originalReferenceTypeResolves = ValidateReference(shader);
                importedReferenceResolves = true;
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

                Debug.Log($"GT_INDEXED_FFT_UNITY registration={registered} fixtureGuidAndFileIdVerified=true importedReference={importedReferenceResolves} originalReferenceType2={originalReferenceTypeResolves} androidVulkanBundle={bundleBuilt} gpuParity=false");
                EditorApplication.Exit(0);
            }
            catch (Exception error)
            {
                Debug.LogError($"GT_INDEXED_FFT_UNITY registration={registered} importedReference={importedReferenceResolves} originalReferenceType2={originalReferenceTypeResolves} androidVulkanBundle={bundleBuilt} failure={error.GetType().Name}");
                EditorApplication.Exit(1);
            }
        }
    }
}
#endif
