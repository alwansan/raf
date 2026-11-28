// SPDX-License-Identifier: GPL-3.0-only
// Disposable, exact object scoped native Texture2D preservation. No global cache change.
using AssetRipper.Assets;
using AssetRipper.Assets.Bundles;
using AssetRipper.Assets.Collections;
using AssetRipper.Export.UnityProjects.Project;
using AssetRipper.IO.Files;
using AssetRipper.IO.Files.SerializedFiles;
using AssetRipper.Processing.Textures;
using AssetRipper.SourceGenerated.Classes.ClassID_28;
using AssetRipper.SourceGenerated.Extensions;
using System.Security.Cryptography;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

internal sealed class RaftGTNativeMipExporter : IAssetExporter
{
    private readonly ITexture2D texture;
    private readonly SpriteInformationObject group;
    private readonly string payloadHash;
    private readonly YamlStreamedAssetExporter native = new();

    private RaftGTNativeMipExporter(ITexture2D t, SpriteInformationObject g, string hash)
    { texture=t; group=g; payloadHash=hash; }

    private static void Need(bool condition, string code)
    { if(!condition) throw new InvalidDataException(code); }

    private void Check()
    {
        Need(texture.ClassID==28 && texture.Collection is SerializedAssetCollection &&
             texture.Width_C28==64 && texture.Height_C28==64 && texture.ImageCount_C28==1 &&
             (int)texture.Format_C28E==4 && (int)texture.LightmapFormat_C28E==0 &&
             texture.MipCount_C28==7 && texture.CheckAssetIntegrity(),
             "selected_native_mip_texture_descriptor");
        Need(ReferenceEquals(texture.MainAsset,group) && ReferenceEquals(group.Texture,texture)
             && group.Sprites.Count==0,"selected_native_mip_group");
        var data=texture.GetImageData();
        Need(data.Length==21844 &&
             Convert.ToHexStringLower(SHA256.HashData(data))==payloadHash,
             "selected_native_mip_payload");
    }

    public static void Register(ProjectExporter project, GameBundle bundle,
                                Func<IUnityObjectBase,IExportCollection> existing)
    {
        string? approval=Environment.GetEnvironmentVariable("RAFT_GT_NATIVE_MIP_APPROVAL");
        if(string.IsNullOrEmpty(approval)) return;
        using var doc=JsonDocument.Parse(File.ReadAllBytes(approval));
        var root=doc.RootElement;
        string owner=root.GetProperty("owner").GetString()!;
        long id=root.GetProperty("path_id").GetInt64();
        string hash=root.GetProperty("payload_sha256").GetString()!;
        Need(id>0 && hash.Length==64 && root.GetProperty("payload_bytes").GetInt32()==21844,
             "native_mip_approval_shape");
        var selected=bundle.FetchAssets().Where(a=>a.Collection.Name==owner && a.PathID==id && a.ClassID==28).ToArray();
        Need(selected.Length==1 && selected[0] is ITexture2D,"native_mip_original_identity");
        var t=(ITexture2D)selected[0];
        Need(t.MainAsset is SpriteInformationObject,"native_mip_original_group");
        var g=(SpriteInformationObject)t.MainAsset!;
        var self=new RaftGTNativeMipExporter(t,g,hash);
        self.Check();
        // Ask the real configured exporter BEFORE registering this override.
        // The selection, not just a matching cache name, must be a redirect of
        // this exact source instance and its zero-sprite processor group.
        foreach(var a in new IUnityObjectBase[]{t,g})
        {
            IExportCollection prior=existing(a);
            Need(prior is RedirectExportCollection && !prior.Exportable &&
                 prior.Contains(t) && prior.Contains(g),"native_mip_prior_redirect_not_observed");
        }
        project.OverrideExporter<IUnityObjectBase>(self);
        Console.WriteLine("GT_NATIVE_MIP_EXACT_SOURCE_REDIRECT_ADMITTED=true");
    }

    public bool TryCreateCollection(IUnityObjectBase asset,[NotNullWhen(true)] out IExportCollection? collection)
    {
        if(!ReferenceEquals(asset,texture) && !ReferenceEquals(asset,group))
        { collection=null; return false; }
        Check();
        Need(native.TryCreateCollection(texture,out var inner) &&
             inner is YamlStreamedAssetExportCollection && inner.Exportable,
             "native_streamed_exporter_unavailable");
        collection=new GroupedNativeCollection(inner!,texture,group);
        return true;
    }

    public AssetType ToExportType(IUnityObjectBase asset)=>native.ToExportType(asset);
    public bool ToUnknownExportType(Type type,out AssetType assetType)
    { assetType=default;return false; }

    // Keep the actual native export collection, GUID, fileID, native importer,
    // YAML streaming implementation and export path. Queue the synthetic group
    // too, so no second redirect can replace the same texture's collection.
    // A reference to the synthetic group itself must fail rather than invent ID.
    private sealed class GroupedNativeCollection(IExportCollection inner,ITexture2D t,
        SpriteInformationObject g) : IExportCollection
    {
        public bool Export(IExportContainer container,string projectDirectory,FileSystem fs)
            =>inner.Export(container,projectDirectory,fs);
        public bool Contains(IUnityObjectBase a)=>ReferenceEquals(a,t)||ReferenceEquals(a,g);
        public long GetExportID(IExportContainer c,IUnityObjectBase a)
            =>ReferenceEquals(a,t)?inner.GetExportID(c,a):throw new InvalidDataException("synthetic_group_has_no_fileid");
        public MetaPtr CreateExportPointer(IExportContainer c,IUnityObjectBase a,bool local)
            =>ReferenceEquals(a,t)?inner.CreateExportPointer(c,a,local):throw new InvalidDataException("synthetic_group_has_no_pointer");
        public AssetCollection File=>inner.File;
        public TransferInstructionFlags Flags=>inner.Flags;
        public IEnumerable<IUnityObjectBase> Assets=>[t,g];
        public IEnumerable<IUnityObjectBase> ExportableAssets=>[t];
        public bool Exportable=>inner.Exportable;
        public string Name=>inner.Name;
    }
}
