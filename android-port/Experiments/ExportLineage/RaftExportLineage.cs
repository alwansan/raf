// Diagnostic instrumentation compiled into the exact disposable exporter.
// No asset mutation, GUID assignment or replacement exporter is performed.
using AssetRipper.Assets;
using AssetRipper.SourceGenerated.Classes.ClassID_21;
using AssetRipper.SourceGenerated.Classes.ClassID_128;
using System.Security.Cryptography;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

internal static class RaftExportLineage
{
    internal static void Capture(ProjectAssetContainer container, IReadOnlyList<IExportCollection> collections)
    {
        string? path = Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LINEAGE");
        if (string.IsNullOrEmpty(path))
            return;
        // Exclusive creation prevents mixing GUIDs from two export instances.
        using FileStream output = new(path, FileMode.CreateNew, FileAccess.Write);
        using Utf8JsonWriter json = new(output);
        json.WriteStartObject();
        json.WriteNumber("schema_version", 1);
        json.WriteString("export_instance", Guid.NewGuid().ToString("N"));
        json.WriteStartArray("objects");
        // Leave the production Material/Shader-only lineage unchanged unless
        // GT explicitly opts in for a temporary, private Texture matching run.
        bool includeTextureObjects = Environment.GetEnvironmentVariable(
            "RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE") == "1";
        foreach (IExportCollection collection in collections)
        {
            container.CurrentCollection = collection;
            foreach (IUnityObjectBase asset in collection.Assets)
            {
                if (asset.ClassID is not (21 or 48) &&
                    !(includeTextureObjects &&
                      asset.ClassID is (28 or 84 or 89 or 117 or 187)))
                    continue;
                json.WriteStartObject();
                json.WriteNumber("class_id", asset.ClassID);
                Identity(json, "source", asset);
                json.WriteString("collection_type", collection.GetType().FullName);
                json.WriteBoolean("exportable", collection.Exportable);
                Pointer(json, "export", collection.CreateExportPointer(container, asset, false));
                if (asset is IMaterial material)
                {
                    if (asset.MainAsset is IFont font && collection.GetType().FullName == "AssetRipper.Export.UnityProjects.Miscellaneous.FontAssetExportCollection")
                    {
                        Identity(json, "font_source", font);
                        Pointer(json, "font_export", collection.CreateExportPointer(container, font, false));
                        json.WriteString("font_data_sha256", Convert.ToHexStringLower(SHA256.HashData(font.FontData)));
                    }
                    // Resolve the actual source PPtr, not a name/property guess.
                    IUnityObjectBase? shader = material.Shader_C21P;
                    if (shader is null)
                        json.WriteNull("shader_source");
                    else
                    {
                        Identity(json, "shader_source", shader);
                        Pointer(json, "shader_export", container.CreateExportPointer(shader));
                    }
                }
                json.WriteEndObject();
            }
        }
        json.WriteEndArray();
        json.WriteEndObject();
        json.Flush();
    }

    private static void Identity(Utf8JsonWriter json, string key, IUnityObjectBase asset)
    {
        json.WriteStartObject(key);
        json.WriteString("owner", asset.Collection.Name);
        json.WriteNumber("path_id", asset.PathID);
        json.WriteEndObject();
    }

    private static void Pointer(Utf8JsonWriter json, string key, MetaPtr pointer)
    {
        json.WriteStartObject(key);
        json.WriteNumber("file_id", pointer.FileID);
        json.WriteString("guid", pointer.GUID.ToString());
        json.WriteNumber("type", (int)pointer.AssetType);
        json.WriteEndObject();
    }
}
