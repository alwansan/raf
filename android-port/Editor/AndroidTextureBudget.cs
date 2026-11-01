#if UNITY_EDITOR
using System;
using UnityEditor;
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
            int examined = 0, large = 0, changed = 0, explicitOverrides = 0;
            int unknownDimensions = 0;
            foreach (string guid in AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null || importer.textureType != TextureImporterType.Default)
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
                      " unknownSourceDimensions=" + unknownDimensions +
                      " originalFilesUnchanged=true gpuVerified=false packageSizeVerified=false");
        }
    }
}
#endif
