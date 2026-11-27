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
using System.Security.Cryptography;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

public static class RaftAuthoredSerializedRendererRoute
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

    public static void Run(string[] args)
    {
        Need(args.Length==3,"expected input owner, export destination and evidence directory");
        string input=args[0],output=args[1],evidence=args[2];
        Need(Path.GetFileName(input)=="authored.assets","unexpected authored file");
        var inputBytes=File.ReadAllBytes(input);
        using (var raw=SerializedFile.FromFile(input))
        {
            var objects=raw.Objects.ToArray();
            Save(evidence,"raw-parser.json",new {generation=(int)raw.Generation,
                owner=raw.NameFixed,version=raw.Version.ToString(),embedded_type_tree=raw.HasTypeTree,
                owner_sha256=Convert.ToHexStringLower(SHA256.HashData(inputBytes)),
                objects=objects.Select(x=>new {path_id=x.FileID,class_id=x.TypeID,bytes=x.ByteSize,
                    sha256=Convert.ToHexStringLower(SHA256.HashData(x.ObjectData!))}).ToArray()});
            Need((int)raw.Generation==22 && objects.Length==14,"unexpected actual raw object table");
        }
        Logger.Add(new ConsoleLogger());
        LibraryConfiguration settings=new();
        settings.ImportSettings.ScriptContentLevel=ScriptContentLevel.Level1;
        settings.ImportSettings.IgnoreStreamingAssets=true;
        settings.ExportSettings.ScriptExportMode=ScriptExportMode.Decompiled;
        // Public supported option: identity-only serialized shader YAML.
        // This authored empty program is not a restored shader or runtime shader.
        settings.ExportSettings.ShaderExportMode=ShaderExportMode.Yaml;
        ExportHandler handler=new(settings);
        var gameData=handler.Load([input]);
        var authored=gameData.GameBundle.FetchAssets().Where(x=>x.Collection.Name=="authored.assets").ToArray();
        Save(evidence,"typed-load.json",new {phase="actual_handler_load_before_processing",
            objects=authored.Select(x=>new {path_id=x.PathID,class_id=x.ClassID,
                owner=x.Collection.Name,type=x.GetType().FullName,typed=Typed(x),
                serialized_collection=x.Collection is SerializedAssetCollection}).ToArray()});
        Need(authored.Length==14 && authored.All(x=>Typed(x) && x.Collection is SerializedAssetCollection),
            "actual typed authored object population mismatch");
        var refs=authored.ToDictionary(x=>x.PathID);
        handler.Process(gameData);
        var after=gameData.GameBundle.FetchAssets().Where(x=>x.Collection.Name=="authored.assets").ToArray();
        Need(authored.All(x=>after.Any(y=>ReferenceEquals(x,y))),"authored object reference lost during processing");
        RaftExportLineage.AuthoredLoadedRoute=refs;
        handler.Export(gameData,output);
        Console.WriteLine("GT_ACTUAL_SERIALIZED_ROUTE_EXPORT_COMPLETE");
    }
}
