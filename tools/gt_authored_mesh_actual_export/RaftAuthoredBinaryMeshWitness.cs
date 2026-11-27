// Authored-only diagnostic host; copied into disposable pinned public exporter.
// No factory or generated object construction: Load returns the actual Mesh.
using AssetRipper.Assets;
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
        ExportHandler handler = new(settings);
        // Exact implementation of LoadAndProcess split at its public load boundary.
        var gameData = handler.Load(paths);
        var meshes = gameData.GameBundle.FetchAssets().Where(x => x.ClassID == 43).ToArray();
        if (meshes.Length != 1 || meshes[0] is not IMesh || meshes[0].PathID != 937)
            throw new InvalidDataException("Actual serialized Class43 Mesh not loaded");
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
