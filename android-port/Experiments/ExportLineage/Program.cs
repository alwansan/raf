using AssetRipper.Export.UnityProjects;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Import.Configuration;
using AssetRipper.Import.Logging;

if (args.Length == 1 && args[0] == "--probe-tool")
{
    Console.WriteLine("RAFT_EXPORTER_HOST exactSource=036098ab sameExportHandler=true");
    return;
}
if (args.Length != 2)
    throw new ArgumentException("Expected original source and private export destination");
Logger.Add(new ConsoleLogger());
LibraryConfiguration settings = new();
settings.ImportSettings.ScriptContentLevel = ScriptContentLevel.Level1;
settings.ImportSettings.IgnoreStreamingAssets = true;
settings.ExportSettings.ScriptExportMode = ScriptExportMode.Decompiled;
// This is the CLI's unchanged Load -> Process -> ProjectExporter -> PostExport
// pipeline, with typed arguments and no GUI/localization build dependency.
ExportHandler handler = new(settings);
// The cache is a bounded provider set, not a complete install with Raft.exe and
// globalgamemanagers. Load its authenticated files explicitly so game-directory
// discovery cannot silently select an empty bundle.
string[] files = Directory.GetFiles(Path.Combine(args[0], "Raft_Data"), "*", SearchOption.AllDirectories);
var gameData = handler.LoadAndProcess(files);
var counts = gameData.GameBundle.FetchAssets().GroupBy(asset => asset.ClassID)
    .ToDictionary(group => group.Key, group => group.Count());
Console.WriteLine($"RAFT_LINEAGE_LOADED materials={counts.GetValueOrDefault(21)} shaders={counts.GetValueOrDefault(48)}");
if (counts.GetValueOrDefault(21) == 0 || counts.GetValueOrDefault(48) == 0)
    throw new InvalidDataException("No original material/shader graph loaded");
handler.Export(gameData, args[1]);
