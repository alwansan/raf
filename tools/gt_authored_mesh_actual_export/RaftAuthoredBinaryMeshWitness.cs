// Authored-only diagnostic host; copied into disposable pinned public exporter.
// No factory or generated object construction: Load returns the actual Mesh.
using AssetRipper.Assets;
using AssetRipper.Assets.Collections;
using AssetRipper.IO.Files.SerializedFiles;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Import.Configuration;
using AssetRipper.Import.Logging;
using AssetRipper.SourceGenerated.Classes.ClassID_43;
using System.Security.Cryptography;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

public static class RaftAuthoredBinaryMeshWitness
{
    public static void Run(string[] args)
    {
        if (args.Length != 3)
            throw new ArgumentException("Expected authored input directory, export directory, load receipt");
        string[] paths = Directory.GetFiles(args[0]).OrderBy(x => x, StringComparer.Ordinal).ToArray();
        if (paths.Length is < 1 or > 2 || paths.Count(x => Path.GetFileName(x) == "authored.assets") != 1 ||
            paths.Any(x => Path.GetFileName(x) is not ("authored.assets" or "authored.resS")))
            throw new InvalidDataException("Unexpected authored input set");
        Logger.Add(new ConsoleLogger());
        LibraryConfiguration settings = new();
        settings.ImportSettings.ScriptContentLevel = ScriptContentLevel.Level1;
        settings.ImportSettings.IgnoreStreamingAssets = true;
        settings.ExportSettings.ScriptExportMode = ScriptExportMode.Decompiled;
        // Actual pinned binary container reader, independent of typed object factory.
        string ownerPath = paths.Single(x => Path.GetFileName(x) == "authored.assets");
        using (var serialized = SerializedFile.FromFile(ownerPath))
        {
            var raw = serialized.Objects.ToArray();
            var rawObjects = raw.Select(x => new {path_id=x.FileID, class_id=x.TypeID,
                bytes=x.ByteSize, sha256=Convert.ToHexStringLower(SHA256.HashData(x.ObjectData!))}).ToArray();
            File.WriteAllText(Path.Combine(Path.GetDirectoryName(args[2])!, "raw-parser.json"),
                JsonSerializer.Serialize(new {generation=(int)serialized.Generation, version=serialized.Version.ToString(),
                    owner=serialized.NameFixed, embedded_type_tree=serialized.HasTypeTree, objects=rawObjects}));
            if ((int)serialized.Generation != 22 || raw.Length != 1 || raw[0].FileID != 937 || raw[0].TypeID != 43)
                throw new InvalidDataException("Actual serialized container object table mismatch");
        }
        ExportHandler handler = new(settings);
        // Exact implementation of LoadAndProcess split at its public load boundary.
        var gameData = handler.Load(paths);
        // The upstream GameInitializer also injects built-in engine resources.
        // Census all Mesh objects; only the exact authored serialized owner
        // may witness this test. Do not treat injected built-in Meshes as input.
        var all = gameData.GameBundle.FetchAssets().ToArray();
        var authored = all.Where(x => x.Collection.Name == "authored.assets").ToArray();
        var meshes = authored.Where(x => x.ClassID == 43).ToArray();
        var census = all.Where(x => x.ClassID == 43 || x.Collection.Name == "authored.assets")
            .Select(x => new {owner=x.Collection.Name,path_id=x.PathID,class_id=x.ClassID,
                type=x.GetType().FullName,serialized_collection=x.Collection is SerializedAssetCollection}).ToArray();
        File.WriteAllText(Path.Combine(Path.GetDirectoryName(args[2])!, "load-census.json"),
            JsonSerializer.Serialize(new {authored_objects=authored.Length,all_meshes=all.Count(x=>x.ClassID==43),objects=census}));
        Console.WriteLine($"GT_ACTUAL_LOAD_CENSUS authored={authored.Length} class43={meshes.Length} allMeshes={all.Count(x=>x.ClassID==43)}");
        if (authored.Length != 1 || meshes.Length != 1 || meshes[0] is not IMesh || meshes[0].PathID != 937 ||
            meshes[0].Collection is not SerializedAssetCollection)
            throw new InvalidDataException("Actual authored serialized Class43 Mesh not loaded as typed object");
        IUnityObjectBase loaded = meshes[0];
        var inputs = paths.Select(p => new {name=Path.GetFileName(p), bytes=new FileInfo(p).Length,
            sha256=Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(p)))}).ToArray();
        File.WriteAllText(args[2], JsonSerializer.Serialize(new {
            phase="actual_handler_load_before_processing", source=new {owner=loaded.Collection.Name,path_id=loaded.PathID},
            class_id=loaded.ClassID, inputs, mesh_count=meshes.Length
        }));
        Console.WriteLine($"GT_ACTUAL_BINARY_MESH_LOADED owner={loaded.Collection.Name} path_id={loaded.PathID}");
        handler.Process(gameData);
        if (!gameData.GameBundle.FetchAssets().Any(x => ReferenceEquals(x,loaded)))
            throw new InvalidDataException("Loaded Mesh reference lost during processing");
        RaftExportLineage.AuthoredLoadedMesh = loaded;
        handler.Export(gameData,args[1]);
        Console.WriteLine("GT_ACTUAL_BINARY_MESH_EXPORT_COMPLETED");
    }
}
