#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace RaftAndroid.Editor
{
    public static class MicroSplatPropertyTextureRecovery
    {
        private sealed class Plan
        {
            public UnityEngine.Object Data;
            public string Path;
            public string MetaHash;
            public string OtherFields;
            public FieldInfo ValuesField;
            public FieldInfo WidthField;
            public FieldInfo CacheField;
            public byte[] OriginalBytes;
            public int Width;
            public Texture2D Texture;
            public Texture2D OldTexture;
        }

        public static void Restore()
        {
            Type type = Type.GetType("JBooth.MicroSplat.MicroSplatPropData, JBooth.MicroSplat.Core", true);
            FieldInfo valuesField = type.GetField("values");
            FieldInfo widthField = type.GetField("maxTextures");
            FieldInfo cacheField = type.GetField("propTex");
            MethodInfo getter = type.GetMethod("GetTexture", Type.EmptyTypes);
            if (!typeof(ScriptableObject).IsAssignableFrom(type) || valuesField == null ||
                valuesField.FieldType != typeof(Color[]) || widthField == null ||
                widthField.FieldType != typeof(int) || cacheField == null ||
                cacheField.FieldType != typeof(Texture2D) || getter == null ||
                getter.ReturnType != typeof(Texture2D))
                throw new BuildFailedException("Original MicroSplat property schema changed.");
            string[] guids = AssetDatabase.FindAssets("t:MicroSplatPropData");
            if (guids.Length == 0)
                throw new BuildFailedException("No original MicroSplat property tables resolved after SDK binding.");
            if (!SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat))
                throw new BuildFailedException("RGBAFloat unavailable; refusing lossy terrain-property fallback.");

            var plans = new List<Plan>();
            int reused = 0;
            // Validate ALL source schemas, dimensions, finite values and paths
            // before mutating a single source asset. Unknown revisions fail.
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var data = AssetDatabase.LoadAssetAtPath(path, type);
                if (data == null || !path.EndsWith(".asset", StringComparison.OrdinalIgnoreCase) ||
                    !File.Exists(path + ".meta"))
                    throw new BuildFailedException("Property source must be an original persistent .asset.");
                int width = (int)widthField.GetValue(data);
                byte[] bytes = PropertyTextureCore.Encode(width, Flatten((Color[])valuesField.GetValue(data)));
                var old = cacheField.GetValue(data) as Texture2D;
                if (old != null && old.format == TextureFormat.RGBAFloat && old.isReadable &&
                    old.width == width && old.height == PropertyTextureCore.AttributeRows &&
                    PropertyTextureCore.Digest(old.GetRawTextureData()) == PropertyTextureCore.Digest(bytes))
                {
                    reused++;
                    continue;
                }
                plans.Add(new Plan {Data = data, Path = path,
                    MetaHash = PropertyTextureCore.Digest(File.ReadAllBytes(path + ".meta")),
                    OtherFields = NonCacheFields(data), ValuesField = valuesField, WidthField = widthField,
                    CacheField = cacheField, OriginalBytes = bytes, Width = width, OldTexture = old});
            }
            foreach (Plan plan in plans)
            {
                plan.Texture = new Texture2D(plan.Width, PropertyTextureCore.AttributeRows,
                    TextureFormat.RGBAFloat, false, true);
                plan.Texture.name = "OriginalFloatPropertyCache";
                plan.Texture.wrapMode = TextureWrapMode.Clamp;
                plan.Texture.filterMode = FilterMode.Point;
                plan.Texture.LoadRawTextureData(plan.OriginalBytes);
                plan.Texture.Apply(false, false);
                PropertyTextureCore.RequireEqual(plan.OriginalBytes, plan.Texture.GetRawTextureData());
            }
            string backup = Path.Combine(Path.GetTempPath(), "raft-original-property-assets-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(backup);
            for (int i = 0; i < plans.Count; i++)
            {
                File.Copy(plans[i].Path, Path.Combine(backup, i + ".asset"));
                File.Copy(plans[i].Path + ".meta", Path.Combine(backup, i + ".asset.meta"));
                if (PropertyTextureCore.Digest(File.ReadAllBytes(plans[i].Path)) !=
                    PropertyTextureCore.Digest(File.ReadAllBytes(Path.Combine(backup, i + ".asset"))))
                    throw new BuildFailedException("Original property asset backup failed before mutation.");
                if (PropertyTextureCore.Digest(File.ReadAllBytes(Path.Combine(backup, i + ".asset.meta"))) != plans[i].MetaHash)
                    throw new BuildFailedException("Original property metadata backup verification failed.");
            }
            // Append only a losslessly derived cache. Existing exported textures,
            // object identities, script metas and property fields are retained.
            foreach (Plan plan in plans)
            {
                AssetDatabase.AddObjectToAsset(plan.Texture, plan.Data);
                plan.CacheField.SetValue(plan.Data, plan.Texture);
                EditorUtility.SetDirty(plan.Texture);
                EditorUtility.SetDirty(plan.Data);
            }
            AssetDatabase.SaveAssets();
            foreach (Plan plan in plans)
            {
                AssetDatabase.ImportAsset(plan.Path, ImportAssetOptions.ForceSynchronousImport);
                plan.Data = AssetDatabase.LoadAssetAtPath(plan.Path, type);
                plan.Texture = plan.CacheField.GetValue(plan.Data) as Texture2D;
                if (plan.Texture == null || plan.Texture.format != TextureFormat.RGBAFloat)
                    throw new BuildFailedException("Saved float property cache did not reload correctly.");
                if (NonCacheFields(plan.Data) != plan.OtherFields ||
                    PropertyTextureCore.Digest(File.ReadAllBytes(plan.Path + ".meta")) != plan.MetaHash)
                    throw new BuildFailedException("Original property fields or GUID metadata changed.");
                byte[] after = PropertyTextureCore.Encode((int)plan.WidthField.GetValue(plan.Data),
                    Flatten((Color[])plan.ValuesField.GetValue(plan.Data)));
                PropertyTextureCore.RequireEqual(plan.OriginalBytes, after);
                // Exercise the REAL provider method used by terrain rendering,
                // not a substitute implementation. Original values stay intact.
                var texture = getter.Invoke(plan.Data, null) as Texture2D;
                if (texture != plan.Texture)
                    throw new BuildFailedException("Original SDK replaced the verified float property cache.");
                PropertyTextureCore.RequireEqual(plan.OriginalBytes, texture.GetRawTextureData());
                PropertyTextureCore.RequireEqual(plan.OriginalBytes,
                    PropertyTextureCore.Encode((int)plan.WidthField.GetValue(plan.Data),
                        Flatten((Color[])plan.ValuesField.GetValue(plan.Data))));
                if (NonCacheFields(plan.Data) != plan.OtherFields)
                    throw new BuildFailedException("Real SDK method altered original property fields.");
            }
            Debug.Log("RAFT_MICROSPLAT_PROPERTY_TEXTURES originalTables=" + guids.Length +
                      " regeneratedFloatCaches=" + plans.Count + " reusedFloatCaches=" + reused +
                      " originalValuesUnchanged=true originalMetaUnchanged=true rawFloatRoundtrip=true" +
                      " actualSdkGetterCalls=" + plans.Count + " originalTexturesRemoved=0");
        }

        private static float[] Flatten(Color[] colors)
        {
            if (colors == null) throw new InvalidDataException("Original property values are missing.");
            var rgba = new float[checked(colors.Length * 4)];
            for (int i = 0; i < colors.Length; i++)
            {
                rgba[i * 4] = colors[i].r;
                rgba[i * 4 + 1] = colors[i].g;
                rgba[i * 4 + 2] = colors[i].b;
                rgba[i * 4 + 3] = colors[i].a;
            }
            return rgba;
        }

        private static string NonCacheFields(UnityEngine.Object data)
        {
            string json = EditorJsonUtility.ToJson(data);
            var pattern = new Regex(@"(""propTex""\s*:\s*)\{[^{}]*\}");
            if (pattern.Matches(json).Count != 1)
                throw new BuildFailedException("Cannot verify original non-cache property fields.");
            return pattern.Replace(json, "$1null");
        }
    }
}
#endif
