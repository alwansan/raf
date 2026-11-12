#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace RaftAndroid.Editor
{
    // GT source-authentic Texture2DArray importer acceptance gate.
    // This does not repair or fabricate texture pixels. Python's SHA-pinned
    // ZIP2/source→AssetRipper proof produces the manifest in the private
    // reconstructed Editor project. This code asks Unity itself whether it
    // imported all nine original arrays as the correct native asset class.
    public static class OriginalTextureArrayImportGuard
    {
        [Serializable]
        private sealed class ExpectedArray
        {
            public string guid;
            public int width;
            public int height;
            public int depth;
            public int mipmap_count;
            public bool has_original_source_pixels;
        }

        [Serializable]
        private sealed class ExpectedContract
        {
            public string schema;
            public ExpectedArray[] arrays;
        }

        public static void Validate()
        {
            string file = Path.Combine(Application.dataPath,
                "Editor/RaftAndroid/GTOriginalArrayImportContract.json");
            if (!File.Exists(file))
                throw new BuildFailedException("GT missing SHA-authentic original Texture2DArray Editor contract.");
            ExpectedContract source;
            try
            {
                source = JsonUtility.FromJson<ExpectedContract>(File.ReadAllText(file));
            }
            catch (Exception error)
            {
                throw new BuildFailedException("GT unreadable original Texture2DArray Editor contract: " +
                    error.GetType().Name);
            }
            if (source == null || source.schema != "GT_ORIGINAL_UNITY_TEXTURE2DARRAY_IMPORT_CONTRACT_V1" ||
                source.arrays == null || source.arrays.Length != 9)
                throw new BuildFailedException("GT invalid original Texture2DArray source contract.");

            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            int logicalLayers = 0;
            int originalPixelLayers = 0;
            int imported = 0;
            foreach (ExpectedArray array in source.arrays)
            {
                if (array == null || String.IsNullOrEmpty(array.guid) ||
                    array.guid.Length != 32 || !seen.Add(array.guid) ||
                    array.width < 1 || array.height < 1 || array.depth < 1 ||
                    array.mipmap_count < 1)
                    throw new BuildFailedException("GT invalid or duplicate original array identity or dimensions.");
                // Do not log or publish the GUID; the manifest is runner-private.
                string path = AssetDatabase.GUIDToAssetPath(array.guid);
                if (String.IsNullOrEmpty(path))
                    throw new BuildFailedException("GT original array GUID missing after Unity import.");
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null)
                    throw new BuildFailedException("GT original Class187 array has no Unity TextureImporter.");
                var settings = new TextureImporterSettings();
                importer.ReadTextureSettings(settings);
                if (settings.textureShape != TextureImporterShape.Texture2DArray ||
                    settings.flipbookRows < 1 || settings.flipbookColumns < 1 ||
                    settings.flipbookRows * settings.flipbookColumns != array.depth)
                    throw new BuildFailedException("GT Unity importer did not preserve original array slice shape.");

                var importedArray = AssetDatabase.LoadAssetAtPath<Texture2DArray>(path);
                if (importedArray == null || importedArray.width != array.width ||
                    importedArray.height != array.height || importedArray.depth != array.depth ||
                    importedArray.mipmapCount != array.mipmap_count)
                    throw new BuildFailedException("GT Unity imported Texture2DArray class/depth/mip contract mismatch.");

                logicalLayers += array.depth;
                if (array.has_original_source_pixels)
                    originalPixelLayers += array.depth;
                imported++;
            }
            if (seen.Count != 9 || imported != 9 || logicalLayers != 52 ||
                originalPixelLayers != 50)
                throw new BuildFailedException("GT original class187 arrays or source pixel layers incomplete.");
            Debug.Log("GT_UNITY_IMPORTED_ORIGINAL_ARRAYS arrays=9 originalLayers=52 sourcePixelLayers=50 " +
                "nativeClass187=true importedMipCountChecked=true originalGUIDsPreserved=true " +
                "pixelColorOnAndroidVerified=false sourceEmptyArrayPixelsInvented=false");
        }
    }
}
#endif
