// SPDX-License-Identifier: GPL-3.0-only
// Optional narrowly scoped exporter override for independently authorized,
// explicitly admitted ordinary texture instances. No engine cache mutation,
// invented pointer or global name bypass. Not wired into production.
using AssetRipper.Assets;
using AssetRipper.Assets.Collections;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Export.UnityProjects.Textures;
using AssetRipper.IO.Files;
using AssetRipper.Processing.Textures;
using AssetRipper.SourceGenerated;
using AssetRipper.SourceGenerated.Classes.ClassID_28;
using AssetRipper.SourceGenerated.Extensions;
using System.Security.Cryptography;

namespace AssetRipper.Export.UnityProjects;

public sealed class VerifiedTexturePreservationExporter : IAssetExporter
{
    public sealed record Approval(string Owner, long PathID, int Width, int Height, string PayloadSha256);
    private readonly TextureAssetExporter native;
    private readonly Dictionary<ITexture2D, Approval> approved = new(ReferenceEqualityComparer.Instance);

    // Caller must already authenticate rights, exact source owner and object
    // bytes, the processed instance and the need to preserve this object.
    // No caller should derive approval from a cache name/dim match alone.
    public VerifiedTexturePreservationExporter(LibraryConfiguration settings,
        IEnumerable<KeyValuePair<ITexture2D, Approval>> admitted)
    {
        native = new TextureAssetExporter(settings);
        foreach (var item in admitted)
        {
            Check(item.Key, item.Value);
            approved.Add(item.Key, item.Value);
        }
        if (approved.Count == 0)
            throw new InvalidDataException("empty explicit texture preservation approval");
    }

    private static void Check(ITexture2D t, Approval a)
    {
        if (t.ClassID != ClassIDType.Texture2D ||
            t.Collection is not SerializedAssetCollection ||
            t.Collection.Name != a.Owner || t.PathID != a.PathID ||
            SpecialFileNames.IsDefaultResourceOrBuiltinExtra(t.Collection.Name) ||
            SpecialFileNames.IsEditorResource(t.Collection.Name) ||
            SpecialFileNames.IsEngineGeneratedF(t.Collection.Name) ||
            t.Width_C28 != a.Width || t.Height_C28 != a.Height ||
            a.Width <= 0 || a.Height <= 0 ||
            t.ImageCount_C28 != 1 || (int)t.Format_C28E != 4 ||
            (int)t.LightmapFormat_C28E != 0 ||
            t.MipCount_C28 != 1 || !t.CheckAssetIntegrity())
            throw new InvalidDataException("unsupported or drifted approved ordinary RGBA32 single-mip texture");
        var bytes = t.GetImageData();
        if (bytes.LongLength != checked(4L * a.Width * a.Height) ||
            Convert.ToHexStringLower(SHA256.HashData(bytes)) != a.PayloadSha256)
            throw new InvalidDataException("approved texture payload drift");
    }

    public bool TryCreateCollection(IUnityObjectBase asset, [NotNullWhen(true)] out IExportCollection? collection)
    {
        // Processor groups even nonsprite textures in SpriteInformationObject.
        // Select only a verified object or its exact zero-sprite group.
        ITexture2D? t = asset as ITexture2D ?? (asset as SpriteInformationObject)?.Texture;
        if (t is null || !approved.TryGetValue(t, out Approval? approval))
        {
            collection = null;
            return false;
        }
        Check(t, approval);
        if (t.MainAsset is not SpriteInformationObject group ||
            !ReferenceEquals(group.Texture, t) || group.Sprites.Count != 0 ||
            !(ReferenceEquals(asset, t) || ReferenceEquals(asset, group)))
            throw new InvalidDataException("approved texture has unsupported sprite/atlas grouping");
        // Use the existing actual exporter/collection; do not manufacture any
        // GUID or fileID, and never silently fall back on approved failures.
        if (!native.TryCreateCollection(t, out collection) ||
            collection is not TextureExportCollection || !collection.Exportable)
            throw new InvalidDataException("approved native texture collection unavailable");
        var members = collection.Assets.ToArray();
        if (members.Length != 2 ||
            members.Count(x => ReferenceEquals(x,t)) != 1 ||
            members.Count(x => ReferenceEquals(x,group)) != 1)
            throw new InvalidDataException("approved collection membership drift");
        return true;
    }

    public AssetType ToExportType(IUnityObjectBase asset) => native.ToExportType(asset);
    public bool ToUnknownExportType(Type type, out AssetType assetType)
    {
        assetType = default;
        return false;
    }
}
