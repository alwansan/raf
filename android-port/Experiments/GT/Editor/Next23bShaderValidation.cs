using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    public static class Next23bShaderValidation
    {
        private static readonly int[] Counts = { 512, 4, 128, 512 };
        private static readonly PassType[] Passes = {
            PassType.ForwardBase, PassType.ForwardAdd, PassType.Deferred, PassType.ShadowCaster
        };
        [Serializable] private sealed class Variant { public string[] keywords; }
        [Serializable] private sealed class PassRoutes { public string passType; public Variant[] variants; }
        [Serializable] private sealed class RouteManifest
        {
            public int schema_version;
            public string candidate_sha256;
            public string source_manifest_sha256;
            public PassRoutes[] passes;
        }

        [Serializable]
        private sealed class Result
        {
            public string unityVersion;
            public string failureType;
            public string checkpoint;
            public int passCount;
            public int registeredRoutes;
            public int errors;
            public string[] compilerErrorGroups;
            public bool androidVulkanOnly;
            public bool privateBundleCompiled;
            public int receiptSchemaVersion;
            public string candidateSha256;
            public string engineRouteManifestSha256;
            public string sourceManifestSha256;
            public string bundleSha256;
            public long bundleBytes;
        }

        public static void Validate()
        {
            var result = new Result { receiptSchemaVersion = 2,
                unityVersion = Application.unityVersion, failureType = "" };
            var output = Path.Combine(Directory.GetParent(Application.dataPath).FullName, "ProbeResults");
            Directory.CreateDirectory(output);
            var receiptPath = Path.Combine(output, "gt-next23b-unity-safe.json");
            var bundleDirectory = Path.Combine(output, "Private");
            int exitCode = 1;
            try
            {
                result.checkpoint = "fresh_output";
                if (File.Exists(receiptPath) || Directory.Exists(bundleDirectory) || File.Exists(bundleDirectory))
                    throw new InvalidOperationException("Next23bOutputAlreadyExists");
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("UnexpectedEditorVersion");
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
                result.androidVulkanOnly = PlayerSettings.GetGraphicsAPIs(BuildTarget.Android)
                    .SequenceEqual(new[] { GraphicsDeviceType.Vulkan });
                const string shaderPath = "Assets/GTNext23b.shader";
                var candidatePath = Path.Combine(Application.dataPath, "GTNext23b.shader");
                result.candidateSha256 = HashFile(candidatePath);
                const string collectionPath = "Assets/GTNext23b.shadervariants";
                result.checkpoint = "import";
                AssetDatabase.ImportAsset(shaderPath,
                    ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                var shader = AssetDatabase.LoadAssetAtPath<Shader>(shaderPath);
                if (shader == null)
                    throw new InvalidOperationException("Next23bShaderMissing");
                result.passCount = shader.passCount;
                var counts = Counts;
                var passes = new PassType[counts.Length];
                if (result.passCount != counts.Length)
                    throw new InvalidOperationException("Next23bShaderPassCountMismatch");

                result.checkpoint = "register";
                var routePath = Path.Combine(Directory.GetParent(Application.dataPath).FullName,
                    "Next23bEngineRoutes.json");
                var routeInfo = new FileInfo(routePath);
                if (!routeInfo.Exists || routeInfo.Length <= 0 || routeInfo.Length > 16L * 1024 * 1024)
                    throw new InvalidOperationException("Next23bRouteFileSizeInvalid");
                var routeBytes = File.ReadAllBytes(routePath);
                if (routeBytes.Length != routeInfo.Length)
                    throw new InvalidOperationException("Next23bRouteFileSizeChanged");
                result.engineRouteManifestSha256 = HashBytes(routeBytes);
                var routeManifest = JsonUtility.FromJson<RouteManifest>(
                    new UTF8Encoding(false, true).GetString(routeBytes));
                if (routeManifest == null || routeManifest.schema_version != 2 ||
                    routeManifest.candidate_sha256 != result.candidateSha256 ||
                    !IsSha256(routeManifest.source_manifest_sha256))
                    throw new InvalidOperationException("Next23bRouteCommitmentMismatch");
                // Carried commitment only: Unity does not authenticate the private source packet.
                result.sourceManifestSha256 = routeManifest.source_manifest_sha256;
                var routes = routeManifest.passes;
                if (routes == null || (routes.Length != counts.Length ||
                    routes.Where((pass, index) => pass == null || pass.variants == null ||
                        pass.variants.Length != counts[index]).Any()))
                    throw new InvalidOperationException("Next23bEngineRouteCountMismatch");
                for (int pass = 0; pass < routes.Length; ++pass)
                {
                    PassType actual;
                    if (!Enum.TryParse(routes[pass].passType, out actual) ||
                        actual.ToString() != routes[pass].passType ||
                        !new[] { PassType.Normal, PassType.ForwardBase, PassType.ForwardAdd,
                            PassType.Deferred, PassType.ShadowCaster }.Contains(actual))
                        throw new InvalidOperationException("Next23bUnprovedPassType");
                    passes[pass] = actual;
                }
                var collection = new ShaderVariantCollection();
                for (int pass = 0; pass < passes.Length; ++pass)
                {
                    for (int variant = 0; variant < counts[pass]; ++variant)
                    {
                        var keywords = routes[pass].variants[variant].keywords;
                        if (keywords == null || keywords.Any(key => key.StartsWith("GT_ORIGINAL_921_")) ||
                            keywords.Distinct().Count() != keywords.Length)
                            throw new InvalidOperationException("Next23bSyntheticOrDuplicateKeyword");
                        if (!collection.Add(new ShaderVariantCollection.ShaderVariant(shader, passes[pass], keywords)))
                            throw new InvalidOperationException("Next23bVariantNotRegistered");
                        ++result.registeredRoutes;
                    }
                }
                AssetDatabase.CreateAsset(collection, collectionPath);
                const string materialPath = "Assets/GTNext23bInstanced.mat";
                var material = new Material(shader) { enableInstancing = true };
                AssetDatabase.CreateAsset(material, materialPath);
                AssetDatabase.SaveAssets();

                const string bundleName = "gt-next23b";
                Directory.CreateDirectory(bundleDirectory);
                var bundle = new AssetBundleBuild {
                    assetBundleName = bundleName, assetNames = new[] { shaderPath, collectionPath, materialPath }
                };
                result.checkpoint = "compile";
                var manifest = BuildPipeline.BuildAssetBundles(bundleDirectory, new[] { bundle },
                    BuildAssetBundleOptions.ForceRebuildAssetBundle | BuildAssetBundleOptions.StrictMode,
                    BuildTarget.Android);
                result.checkpoint = "compiler_results";
                var errors = ShaderUtil.GetShaderMessages(shader)
                    .Where(message => message.severity.ToString() == "Error").ToArray();
                result.errors = errors.Length;
                result.compilerErrorGroups = errors
                    .GroupBy(message => ErrorCategory(message.message))
                    .OrderByDescending(group => group.Count())
                    .ThenBy(group => group.Min(message => message.line))
                    .Take(16)
                    .Select(group => $"{group.Key} firstLine={group.Min(message => message.line)} count={group.Count()}")
                    .ToArray();
                var artifact = new FileInfo(Path.Combine(bundleDirectory, bundleName));
                if (manifest == null || !artifact.Exists || artifact.Length <= 0 ||
                    artifact.Length > 512L * 1024 * 1024 || result.errors != 0 ||
                    ShaderUtil.ShaderHasError(shader) || !result.androidVulkanOnly ||
                    result.registeredRoutes != counts.Sum())
                    throw new InvalidOperationException("Next23bBundleNotVerified");
                result.checkpoint = "byte_commitments";
                if (HashFile(candidatePath) != result.candidateSha256 ||
                    HashFile(routePath) != result.engineRouteManifestSha256)
                    throw new InvalidOperationException("Next23bInputChangedDuringBuild");
                result.bundleSha256 = HashFile(artifact.FullName, out result.bundleBytes);
                result.checkpoint = "verified";
                result.privateBundleCompiled = true;
                exitCode = 0;
            }
            catch (Exception exception)
            {
                result.failureType = exception.GetType().Name;
                result.privateBundleCompiled = false;
                exitCode = 1;
            }
            File.WriteAllText(receiptPath,
                JsonUtility.ToJson(result, true));
            Debug.Log("GT_ORIGINAL_921_UNITY_SAFE " + JsonUtility.ToJson(result));
            EditorApplication.Exit(exitCode);
        }

        private static bool IsSha256(string text)
        {
            return text != null && text.Length == 64 && text.All(c =>
                (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'));
        }

        private static string HashBytes(byte[] bytes)
        {
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        private static string HashFile(string path)
        {
            long length;
            return HashFile(path, out length);
        }

        private static string HashFile(string path, out long length)
        {
            using (var input = File.OpenRead(path))
            using (var hash = SHA256.Create())
            {
                length = input.Length;
                if (length <= 0)
                    throw new InvalidOperationException("Next23bEmptyCommitmentFile");
                var digest = hash.ComputeHash(input);
                if (input.Length != length || input.Position != length)
                    throw new InvalidOperationException("Next23bCommitmentFileSizeChanged");
                return BitConverter.ToString(digest).Replace("-", "").ToLowerInvariant();
            }
        }

        private static string ErrorCategory(string message)
        {
            string[] categories = {
                "entry point", "undeclared identifier", "redefinition", "already defined",
                "no matching", "cannot convert", "cannot map", "invalid semantic", "duplicate",
                "unsupported", "unexpected token", "syntax error", "unrecognized",
                "out of bounds", "overlapping", "failed to compile",
                "packoffset", "constant buffer", "cbuffer", "overlap", "not supported",
                "not allowed", "invalid", "expected", "missing", "unimplemented", "conflict"
            };
            // Unity includes private identifiers in many messages. Report only
            // diagnostic phrases from this source-controlled vocabulary.
            var matches = categories.Where(category =>
                message.IndexOf(category, StringComparison.OrdinalIgnoreCase) >= 0).ToArray();
            return matches.Length == 0 ? "other" : String.Join(", ", matches);
        }
    }
}
