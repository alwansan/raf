// Only actual typed objects returned by the pinned public binary loader.
using AssetRipper.Assets;
using AssetRipper.Assets.Collections;
using AssetRipper.IO.Files.SerializedFiles;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Import.Configuration;
using AssetRipper.Import.Logging;
using AssetRipper.SourceGenerated.Classes.ClassID_1;
using AssetRipper.SourceGenerated.Classes.ClassID_4;
using AssetRipper.SourceGenerated.Classes.ClassID_21;
using AssetRipper.SourceGenerated.Classes.ClassID_23;
using AssetRipper.SourceGenerated.Classes.ClassID_28;
using AssetRipper.SourceGenerated.Classes.ClassID_33;
using AssetRipper.SourceGenerated.Classes.ClassID_43;
using AssetRipper.SourceGenerated.Classes.ClassID_48;
using AssetRipper.SourceGenerated.Extensions;
using AssetRipper.SourceGenerated.Enums;
using System.Security.Cryptography;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

public static class RaftAuthoredExternalPPtrRoute
{
    private static void Need(bool condition,string reason)
    {
        if (!condition) throw new InvalidDataException(reason);
    }
    private static bool Typed(IUnityObjectBase a) => a.ClassID switch {
        1 => a is IGameObject, 4 => a is ITransform, 21 => a is IMaterial,
        23 => a is IMeshRenderer, 28 => a is ITexture2D, 33 => a is IMeshFilter,
        43 => a is IMesh, 48 => a is IShader, _ => false
    };
    private static void Save(string root,string name,object data) =>
        File.WriteAllText(Path.Combine(root,name),JsonSerializer.Serialize(data));

    internal static readonly HashSet<string> Owners = new(StringComparer.Ordinal) {
        "sharedassets30.assets","sharedassets31.assets","sharedassets32.assets","sharedassets33.assets"
    };
    public static void Run(string[] args)
    {
        Need(args.Length==3,"expected authored input directory, export destination and evidence directory");
        string output=args[1],evidence=args[2];
        string[] paths=Directory.GetFiles(args[0]).OrderBy(x=>x,StringComparer.Ordinal).ToArray();
        const string providerName="gt-authored-textures.resS";
        string provider=Path.Combine(args[0],providerName);
        Need(paths.Length==Owners.Count+1 && File.Exists(provider) &&
             Owners.SetEquals(paths.Where(p=>Path.GetFileName(p)!=providerName).Select(Path.GetFileName)!),
             "unexpected authored file set");
        byte[] providerBytes=File.ReadAllBytes(provider);
        Need(providerBytes.Length==171,"unexpected authored provider extent");
        Need((int)ColorSpace.Linear==1 && (int)ColorSpace.Gamma==0 && (int)TextureFormat.DXT5==12 && (int)TextureUsageMode.NormalmapDXT5nm==3,"BC3/normalmap ABI drift");
        Save(evidence,"raw-provider.json",new {name=providerName,bytes=providerBytes.Length,
            sha256=Convert.ToHexStringLower(SHA256.HashData(providerBytes)),color_space_linear=(int)ColorSpace.Linear,color_space_gamma=(int)ColorSpace.Gamma,bc3_format=(int)TextureFormat.DXT5,dxt5nm_usage=(int)TextureUsageMode.NormalmapDXT5nm});
        var rawRows=new List<object>();
        foreach(string input in paths.Where(p=>Path.GetFileName(p)!=providerName))
        {
            byte[] bytes=File.ReadAllBytes(input);
            using var raw=SerializedFile.FromFile(input);
            var objects=raw.Objects.ToArray();
            rawRows.Add(new {generation=(int)raw.Generation,owner=raw.NameFixed,
                version=raw.Version.ToString(),embedded_type_tree=raw.HasTypeTree,
                owner_sha256=Convert.ToHexStringLower(SHA256.HashData(bytes)),
                externals=raw.Dependencies.ToArray().Select(d=>new {path=d.PathNameOrigin,
                    resolved_name=d.PathName,type=(int)d.Type,guid=d.Guid.ToString(),asset_path=d.AssetPath}).ToArray(),
                objects=objects.Select(x=>new {path_id=x.FileID,class_id=x.TypeID,bytes=x.ByteSize,
                    sha256=Convert.ToHexStringLower(SHA256.HashData(x.ObjectData!))}).ToArray()});
            Need((int)raw.Generation==22 && objects.Length==4,"unexpected actual raw object table");
        }
        Save(evidence,"raw-parser.json",rawRows);
        Logger.Add(new ConsoleLogger());
        LibraryConfiguration settings=new();
        settings.ImportSettings.ScriptContentLevel=ScriptContentLevel.Level1;
        settings.ImportSettings.IgnoreStreamingAssets=true;
        settings.ExportSettings.ScriptExportMode=ScriptExportMode.Decompiled;
        settings.ExportSettings.ShaderExportMode=ShaderExportMode.Yaml;
        ExportHandler handler=new(settings);
        var gameData=handler.Load(paths);
        var authored=gameData.GameBundle.FetchAssets().Where(x=>Owners.Contains(x.Collection.Name)).ToArray();
        Save(evidence,"typed-load.json",new {phase="actual_handler_load_before_processing",
            objects=authored.Select(x=>new {path_id=x.PathID,class_id=x.ClassID,
                owner=x.Collection.Name,type=x.GetType().FullName,typed=Typed(x),
                serialized_collection=x.Collection is SerializedAssetCollection}).ToArray(),
            collections=authored.Select(a=>a.Collection).Distinct().Select(c=>new {owner=c.Name,
                dependencies=c.Dependencies.Select(d=>d?.Name).ToArray()}).ToArray()});
        Need(authored.Length==16 && authored.All(x=>Typed(x) && x.Collection is SerializedAssetCollection),
            "actual typed authored object population mismatch");
        var refs=authored.ToDictionary(x=>(x.Collection.Name,x.PathID));
        var edges=new List<object>();
        foreach(var asset in authored)
        {
            // Traverse actual generated raw pointer fields, before any processing.
            foreach(var (field,ptr) in asset.FetchDependencies())
            {
                if(ptr.FileID==0 || ptr.PathID==0) continue;
                var target=asset.Collection.TryGetAsset(ptr.FileID,ptr.PathID);
                Need(target is not null && refs.TryGetValue((target.Collection.Name,target.PathID),out var expected) &&
                    ReferenceEquals(target,expected),"actual external pointer unresolved or wrong instance");
                edges.Add(new {owner=asset.Collection.Name,path_id=asset.PathID,field,
                    file_id=ptr.FileID,target_owner=target!.Collection.Name,target_path_id=target.PathID,
                    target_class_id=target.ClassID,reference_equal=true});
            }
        }
        Save(evidence,"typed-external-edges.json",edges);
        Need(edges.Count==10,"unexpected actual nonnull external PPtr population");
        var streams=new List<object>();
        foreach(var tex in authored.OfType<ITexture2D>())
        {
            var stream=tex.StreamData_C28;
            Need(tex.ImageData_C28.Length==0 && stream is not null &&
                stream.Path.ToString()==providerName && stream.IsSet(),"expected actual external-only texture");
            ulong offset=stream!.GetOffset();
            uint size=stream.Size;
            Need(offset+size<=(ulong)providerBytes.Length,"stream extent out of bounds");
            byte[] data=tex.GetImageData();
            Need(data.Length==size && data.AsSpan().SequenceEqual(providerBytes.AsSpan((int)offset,(int)size)),
                "actual exporter texture resource bytes differ from independent provider slice");
            streams.Add(new {owner=tex.Collection.Name,path_id=tex.PathID,path=stream.Path.ToString(),
                offset,size,inline_bytes=tex.ImageData_C28.Length,loaded_bytes=data.Length,
                sha256=Convert.ToHexStringLower(SHA256.HashData(data)),integrity=tex.CheckAssetIntegrity(),
                color_space=(int)tex.ColorSpace_C28E,mip_count=tex.MipCount_C28,
                texture_format=(int)tex.Format_C28E,usage=(int)tex.LightmapFormat_C28E,
                readable=tex.IsReadable_C28,streaming=tex.StreamingMipmaps_C28,
                priority=tex.StreamingMipmapsPriority_C28});
        }
        Save(evidence,"typed-streams.json",streams);
        Need(streams.Count==2,"unexpected streamed texture population");
        handler.Process(gameData);
        var after=gameData.GameBundle.FetchAssets().Where(x=>Owners.Contains(x.Collection.Name)).ToArray();
        Need(authored.All(x=>after.Any(y=>ReferenceEquals(x,y))),"authored object reference lost during processing");
        RaftExportLineage.AuthoredLoadedExternalRoute=refs;
        handler.Export(gameData,output);
        Console.WriteLine("GT_ACTUAL_EXTERNAL_PPTR_EXPORT_COMPLETE");
    }
}
