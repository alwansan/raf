using System;
using System.IO;
using System.Linq;
using UnityEngine.Experimental.Rendering;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    public static class GTNativeArrayMipValidation
    {
        public static void Validate()
        {
            // Match the SHA-verified original PlayerSettings used by the native pipeline.
            PlayerSettings.colorSpace = ColorSpace.Linear;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
            var guids = AssetDatabase.FindAssets("t:Texture2DArray", new[] { "Assets/Texture2DArray" });
            var linearDepths = new System.Collections.Generic.List<int>();
            var srgbDepths = new System.Collections.Generic.List<int>();
            var paths = new string[guids.Length];
            int sourceEmptyArrays = 0;
            Debug.Log($"GT_NATIVE_ARRAY_IMPORTED_COUNT count={guids.Length}");
            for (int i = 0; i < guids.Length; i++)
            {
                var path = AssetDatabase.GUIDToAssetPath(guids[i]);
                var texture = AssetDatabase.LoadAssetAtPath<Texture2DArray>(path);
                if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(texture, out string guid, out long id)
                    || guid != guids[i] || id != 18700000)
                    throw new InvalidOperationException("Native array identity changed");
                paths[i] = path;
                Debug.Log($"GT_NATIVE_ARRAY_IMPORTED shape={texture.width}x{texture.height} " +
                    $"depth={texture.depth} mips={texture.mipmapCount} format={texture.graphicsFormat}");
                // The bundle verifier authenticates the depth-two array's metadata
                // and zero-byte payload independently against its source owner.
                if (texture.depth == 2)
                {
                    ++sourceEmptyArrays;
                    continue;
                }
                if (texture.width != 1024 || texture.height != 1024 || texture.mipmapCount != 11)
                    throw new InvalidOperationException("Native BC3 array shape or mip count changed");
                switch (texture.graphicsFormat)
                {
                    case GraphicsFormat.RGBA_DXT5_UNorm:
                        linearDepths.Add(texture.depth);
                        break;
                    case GraphicsFormat.RGBA_DXT5_SRGB:
                        srgbDepths.Add(texture.depth);
                        break;
                    default:
                        throw new InvalidOperationException("Native array BC3 graphics format changed");
                }
            }
            var expectedDepths = new[] { 5, 6, 6, 8 };
            if (sourceEmptyArrays != 1 || !linearDepths.OrderBy(depth => depth).SequenceEqual(expectedDepths)
                || !srgbDepths.OrderBy(depth => depth).SequenceEqual(expectedDepths))
                throw new InvalidOperationException("Native array sample population changed");
            var output = Path.Combine(Directory.GetParent(Application.dataPath).FullName, "GTNativeArrayBundle");
            Directory.CreateDirectory(output);
            var build = new AssetBundleBuild { assetBundleName = "native-arrays", assetNames = paths };
            if (!BuildPipeline.BuildAssetBundles(output, new[] { build },
                    BuildAssetBundleOptions.StrictMode, BuildTarget.Android))
                throw new InvalidOperationException("Native array bundle construction failed");
            Debug.Log("GT_NATIVE_ARRAY_UNITY arrays=9 populatedLayers=50 sourceEmptyLayers=2");
        }
    }
}
