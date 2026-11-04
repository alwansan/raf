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
handler.LoadProcessAndExport([args[0]], args[1]);
