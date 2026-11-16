using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    public static class Next7p33ShaderValidation
    {
        private static readonly int[] Counts = { 8, 13, 8, 4 };
        private static readonly PassType[] Passes = {
            PassType.ForwardBase, PassType.ForwardAdd, PassType.Deferred, PassType.ShadowCaster
        };
        [Serializable] private sealed class Variant { public string[] keywords; }
        [Serializable] private sealed class PassRoutes { public Variant[] variants; }
        [Serializable] private sealed class RouteManifest { public PassRoutes[] passes; }

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
            public string candidateSha256;
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
                const string shaderPath = "Assets/GTNext7p33.shader";
                using (var sha256 = SHA256.Create())
                using (var shaderInput = File.OpenRead(Path.Combine(Application.dataPath, "GTNext7p33.shader")))
                    result.candidateSha256 = BitConverter.ToString(sha256.ComputeHash(shaderInput))
                        .Replace("-", "").ToLowerInvariant();
                const string collectionPath = "Assets/GTNext7p33.shadervariants";
                result.checkpoint = "import";
                AssetDatabase.ImportAsset(shaderPath,
                    ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                var shader = AssetDatabase.LoadAssetAtPath<Shader>(shaderPath);
                if (shader == null)
                    throw new InvalidOperationException("Next7p33ShaderMissing");
                result.passCount = shader.passCount;
                var counts = Counts;
                var passes = Passes;
                if (result.passCount != counts.Length)
                    throw new InvalidOperationException("Next7p33ShaderPassCountMismatch");

                result.checkpoint = "register";
                var routePath = Path.Combine(Directory.GetParent(Application.dataPath).FullName,
                    "Next7p33EngineRoutes.json");
                var routes = File.Exists(routePath)
                    ? JsonUtility.FromJson<RouteManifest>(File.ReadAllText(routePath)).passes : null;
                if (routes != null && (routes.Length != counts.Length ||
                    routes.Where((pass, index) => pass.variants.Length != counts[index]).Any()))
                    throw new InvalidOperationException("Next7p33EngineRouteCountMismatch");
                var collection = new ShaderVariantCollection();
                for (int pass = 0; pass < passes.Length; ++pass)
                {
                    for (int variant = 0; variant < counts[pass]; ++variant)
                    {
                        var keywords = routes != null ? routes[pass].variants[variant].keywords :
                            variant == 0 ? Array.Empty<string>() :
                            new[] { $"GT_ORIGINAL_921_P{pass}_V{variant}" };
                        if (!collection.Add(new ShaderVariantCollection.ShaderVariant(shader, passes[pass], keywords)))
                            throw new InvalidOperationException("Next7p33VariantNotRegistered");
                        ++result.registeredRoutes;
                    }
                }
                AssetDatabase.CreateAsset(collection, collectionPath);
                const string materialPath = "Assets/GTNext7p33Instanced.mat";
                var material = new Material(shader) { enableInstancing = true };
                AssetDatabase.CreateAsset(material, materialPath);
                AssetDatabase.SaveAssets();

                const string bundleName = "gt-next7p33";
                var bundleDirectory = Path.Combine(output, "Private");
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
                result.privateBundleCompiled = manifest != null && artifact.Exists && artifact.Length > 0
                    && result.errors == 0 && !ShaderUtil.ShaderHasError(shader);
                exitCode = result.privateBundleCompiled && result.androidVulkanOnly ? 0 : 1;
            }
            catch (Exception exception)
            {
                result.failureType = exception.GetType().Name;
            }
            File.WriteAllText(Path.Combine(output, "gt-next7p33-unity-safe.json"),
                JsonUtility.ToJson(result, true));
            Debug.Log("GT_ORIGINAL_921_UNITY_SAFE " + JsonUtility.ToJson(result));
            EditorApplication.Exit(exitCode);
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
