using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    public static class FFTUtilitiesShaderValidation
    {
        [Serializable] private sealed class Result
        {
            public int receiptSchemaVersion = 2;
            public string unityVersion;
            public long candidateBytes;
            public string sourceReceiptSha256;
            public long bundleBytes;
            public string bundleSha256;
            public string failureType;
            public string checkpoint;
            public string candidateSha256;
            public string compilerControl;
            public int passCount;
            public int registeredKeywordVariants;
            public int errors;
            public bool androidVulkanOnly;
            public bool privateBundleCompiled;
            public bool originalMaterialGuidProven;
            public bool gamePlayerBuilt;
            public bool devicePixelsProven;
        }

        private static string HashFile(string path, out long size)
        {
            using (var sha256 = SHA256.Create())
            using (var input = File.OpenRead(path))
            {
                size = input.Length;
                if (size <= 0) throw new InvalidOperationException("EmptyReceiptInput");
                string hash = BitConverter.ToString(sha256.ComputeHash(input))
                    .Replace("-", "").ToLowerInvariant();
                if (input.Length != size) throw new InvalidOperationException("ReceiptInputSizeChanged");
                return hash;
            }
        }

        public static void Validate()
        {
            var result = new Result { unityVersion = Application.unityVersion };
            string root = Directory.GetParent(Application.dataPath).FullName;
            string output = Path.Combine(root, "ProbeResults");
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
                const string shaderPath = "Assets/GTFFTUtilities.shader";
                string candidatePath = Path.Combine(Application.dataPath, "GTFFTUtilities.shader");
                string sourceReceiptPath = Path.Combine(root, "SourceReceipt.json");
                result.candidateSha256 = HashFile(candidatePath, out result.candidateBytes);
                result.sourceReceiptSha256 = HashFile(sourceReceiptPath, out long sourceReceiptBytes);
                if (result.candidateSha256 != File.ReadAllText(Path.Combine(root, "CandidateSha256.txt")).Trim())
                    throw new InvalidOperationException("SourceReceiptCandidateMismatch");
                result.compilerControl = File.ReadAllText(Path.Combine(root, "CandidateCompiler.txt")).Trim();
                if (result.compilerControl != "dxc" && result.compilerControl != "hlslcc")
                    throw new InvalidOperationException("UnsupportedCompilerControl");
                result.checkpoint = "import";
                AssetDatabase.ImportAsset(shaderPath,
                    ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                var shader = AssetDatabase.LoadAssetAtPath<Shader>(shaderPath);
                if (shader == null) throw new InvalidOperationException("PrivateShaderMissing");
                result.passCount = shader.passCount;
                if (result.passCount != 7) throw new InvalidOperationException("SevenSourcePassesRequired");
                result.checkpoint = "register";
                // SVC keys contain PassType and keywords, not a pass index.
                // One empty Normal variant covers all seven original Normal
                // passes. The independent bundle decoder checks every pass.
                var collection = new ShaderVariantCollection();
                if (!collection.Add(new ShaderVariantCollection.ShaderVariant(
                    shader, PassType.Normal, Array.Empty<string>())))
                    throw new InvalidOperationException("EmptyKeywordVariantNotRegistered");
                result.registeredKeywordVariants = collection.variantCount;
                if (result.registeredKeywordVariants != 1)
                    throw new InvalidOperationException("UnexpectedKeywordVariants");
                const string collectionPath = "Assets/GTFFTUtilities.shadervariants";
                const string materialPath = "Assets/GTFFTUtilities.mat";
                AssetDatabase.CreateAsset(collection, collectionPath);
                AssetDatabase.CreateAsset(new Material(shader), materialPath);
                AssetDatabase.SaveAssets();
                string directory = Path.Combine(output, "Private");
                Directory.CreateDirectory(directory);
                const string bundleName = "gt-fft-utilities";
                result.checkpoint = "compile";
                var manifest = BuildPipeline.BuildAssetBundles(directory, new[] {
                    new AssetBundleBuild { assetBundleName = bundleName,
                        assetNames = new[] { shaderPath, collectionPath, materialPath } }
                }, BuildAssetBundleOptions.ForceRebuildAssetBundle | BuildAssetBundleOptions.StrictMode,
                   BuildTarget.Android);
                result.checkpoint = "compiler_results";
                result.errors = ShaderUtil.GetShaderMessages(shader)
                    .Count(message => message.severity.ToString() == "Error");
                var artifact = new FileInfo(Path.Combine(directory, bundleName));
                bool compiled = manifest != null && artifact.Exists && artifact.Length > 0
                    && result.errors == 0 && !ShaderUtil.ShaderHasError(shader);
                if (compiled && result.androidVulkanOnly)
                {
                    if (HashFile(candidatePath, out long finalSourceBytes) != result.candidateSha256
                            || finalSourceBytes != result.candidateBytes
                            || HashFile(sourceReceiptPath, out long finalReceiptBytes) != result.sourceReceiptSha256
                            || finalReceiptBytes != sourceReceiptBytes)
                        throw new InvalidOperationException("ReceiptInputsChangedDuringCompile");
                    result.bundleSha256 = HashFile(artifact.FullName, out result.bundleBytes);
                    result.failureType = "";
                    result.privateBundleCompiled = true;
                    exitCode = 0;
                }
            }
            catch (Exception error) { result.failureType = error.GetType().Name; }
            File.WriteAllText(Path.Combine(output, "gt-fft-utilities-unity-safe.json"),
                JsonUtility.ToJson(result, true));
            Debug.Log("GT_FFT_UTILITIES_UNITY_SAFE " + JsonUtility.ToJson(result));
            EditorApplication.Exit(exitCode);
        }
    }
}
