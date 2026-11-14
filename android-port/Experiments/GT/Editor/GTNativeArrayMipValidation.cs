using System;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT
{
    public static class GTNativeArrayMipValidation
    {
        public static void Validate()
        {
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
            var guids = AssetDatabase.FindAssets("t:Texture2DArray", new[] { "Assets/Texture2DArray" });
            int layers = 0;
            var paths = new string[guids.Length];
            for (int i = 0; i < guids.Length; i++)
            {
                var path = AssetDatabase.GUIDToAssetPath(guids[i]);
                var texture = AssetDatabase.LoadAssetAtPath<Texture2DArray>(path);
                if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(texture, out string guid, out long id)
                    || guid != guids[i] || id != 18700000
                    || texture.width != 1024 || texture.height != 1024 || texture.mipmapCount != 11)
                    throw new InvalidOperationException("Native array identity or mip count changed");
                layers += texture.depth;
                paths[i] = path;
            }
            if (paths.Length != 4 || layers != 28)
                throw new InvalidOperationException("Native array sample population changed");
            var output = Path.GetFullPath("Temp/GTNativeArrayBundle");
            Directory.CreateDirectory(output);
            var build = new AssetBundleBuild { assetBundleName = "native-arrays", assetNames = paths };
            if (!BuildPipeline.BuildAssetBundles(output, new[] { build },
                    BuildAssetBundleOptions.StrictMode, BuildTarget.Android))
                throw new InvalidOperationException("Native array bundle construction failed");
            Debug.Log("GT_NATIVE_ARRAY_UNITY arrays=4 layers=28 levels=11");
        }
    }
}
