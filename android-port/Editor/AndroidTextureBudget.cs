#if UNITY_EDITOR
using System;
using UnityEditor;
using UnityEditor.Android;
using UnityEditor.Build;
using System.IO;
using System.Linq;
using UnityEngine;

namespace RaftAndroid.Editor
{
    // A bounded Android-only response to the observed 3.79 GB Gradle asset
    // packaging failure. The restored source images and their GUIDs remain intact.
    // This is a quality trade-off, NOT a claim that the 2 GB packaging limit
    // or the phone's GPU OOM is solved until a native/device run proves it.
    internal static class AndroidTextureBudget
    {
        private const int MaxDimension = 2048;

        internal static void Apply()
        {
            int examined = 0, large = 0, changed = 0, explicitOverrides = 0, alreadyBounded = 0;
            int unknownDimensions = 0;
            foreach (string guid in AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null || importer.textureType != TextureImporterType.Default ||
                    importer.textureShape != TextureImporterShape.Texture2D)
                    continue;
                // HDR sources and special importers need separate fidelity analysis.
                if (path.EndsWith(".hdr", StringComparison.OrdinalIgnoreCase) ||
                    path.EndsWith(".exr", StringComparison.OrdinalIgnoreCase))
                    continue;
                examined++;
                int width, height;
                try
                {
                    importer.GetSourceTextureWidthAndHeight(out width, out height);
                }
                catch (Exception)
                {
                    unknownDimensions++;
                    continue;
                }
                if (Math.Max(width, height) <= MaxDimension)
                    continue;
                large++;
                var settings = importer.GetPlatformTextureSettings("Android");
                // Original explicit platform overrides are not silently replaced.
                if (settings.overridden)
                {
                    explicitOverrides++;
                    continue;
                }
                // If the source importer already caps the effective texture to
                // <=2048, forcing ASTC would change its format without saving
                // additional resolution or solving the large-texture problem.
                if (importer.maxTextureSize <= MaxDimension)
                {
                    alreadyBounded++;
                    continue;
                }
                settings.name = "Android";
                settings.overridden = true;
                settings.maxTextureSize = Math.Min(importer.maxTextureSize, MaxDimension);
                settings.format = TextureImporterFormat.ASTC_6x6;
                settings.textureCompression = TextureImporterCompression.Compressed;
                importer.SetPlatformTextureSettings(settings);
                importer.SaveAndReimport();
                changed++;
            }
            Debug.Log("RAFT_ANDROID_TEXTURE_BUDGET defaultExamined=" + examined +
                      " sourceOver2048=" + large + " astc6x6Overrides=" + changed +
                      " originalOverridesPreserved=" + explicitOverrides +
                      " alreadyBoundedPreserved=" + alreadyBounded +
                      " unknownSourceDimensions=" + unknownDimensions +
                      " originalFilesUnchanged=true gpuVerified=false packageSizeVerified=false");
        }
    }

    // Observe generated Gradle payload sizes BEFORE Android Gradle tries to
    // allocate a Java byte[] for an oversized asset. Aggregate sizes only:
    // no proprietary asset paths or content are printed.
    public sealed class AndroidGradleAssetAudit : IPostGenerateGradleAndroidProject
    {
        public int callbackOrder { get { return 1000; } }

        public void OnPostGenerateGradleAndroidProject(string path)
        {
            string assets = Path.Combine(path, "src/main/assets");
            if (!Directory.Exists(assets))
            {
                Debug.LogWarning("RAFT_ANDROID_GRADLE_ASSET_AUDIT unavailable=true");
                return;
            }
            long[] sizes = Directory.EnumerateFiles(assets, "*", SearchOption.AllDirectories)
                .Select(file => new FileInfo(file).Length)
                .OrderByDescending(size => size).ToArray();
            long largest = sizes.Length == 0 ? 0 : sizes[0];
            long total = sizes.Sum();
            int oversized = sizes.Count(size => size > int.MaxValue);
            Debug.Log("RAFT_ANDROID_GRADLE_ASSET_AUDIT fileCount=" + sizes.Length +
                      " largestBytes=" + largest + " totalBytes=" + total +
                      " topFiveBytes=" + string.Join(",", sizes.Take(5)) +
                      " overJavaArrayLimit=" + oversized + " fileNamesLogged=false");
            if (oversized != 0)
                throw new BuildFailedException(
                    "Android Gradle assets include a file larger than Java's ~2 GiB array limit. " +
                    "Refuse packaging without reducing/splitting the generated payload; " +
                    "original game assets remain unchanged.");
        }
    }

}
#endif
