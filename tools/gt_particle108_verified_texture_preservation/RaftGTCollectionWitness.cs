// SPDX-License-Identifier: GPL-3.0-only
// Authored retained-input remediation host, not a production exporter.
using AssetRipper.Assets;
using AssetRipper.Assets.Collections;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Export.UnityProjects.DeletedAssets;
using AssetRipper.Export.UnityProjects.EngineAssets;
using AssetRipper.Import.Configuration;
using AssetRipper.Import.Logging;
using AssetRipper.IO.Files;
using AssetRipper.SourceGenerated.Classes.ClassID_28;
using AssetRipper.SourceGenerated.Extensions;
using System.Security.Cryptography;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

public static class RaftGTCollectionWitness
{
    private const string Owner = "gt-collection-authored.assets";
    private static string? evidence;
    private static ITexture2D[]? expected;
    private static void Need(bool test, string why)
    {
        if (!test) throw new InvalidDataException(why);
    }
    private static void Save(string name, object data) =>
        File.WriteAllText(Path.Combine(evidence!, name), JsonSerializer.Serialize(data));

    public static void Run(string[] args)
    {
        Need(args.Length == 3, "expected authored input, destination and receipt dir");
        evidence = args[2];
        string[] paths = Directory.GetFiles(args[0]);
        Need(paths.Length == 1 && Path.GetFileName(paths[0]) == Owner, "authored-only inputs");
        using JsonDocument approval = JsonDocument.Parse(File.ReadAllBytes(Path.Combine(evidence!, "approval.json")));
        var auth = approval.RootElement;
        string ownerHash = auth.GetProperty("owner_sha256").GetString()!;
        Need(Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(paths[0]))) == ownerHash,
             "retained owner bytes drift");
        Logger.Add(new ConsoleLogger());
        LibraryConfiguration settings = new();
        settings.ImportSettings.ScriptContentLevel = ScriptContentLevel.Level1;
        settings.ImportSettings.IgnoreStreamingAssets = true;
        settings.ExportSettings.ScriptExportMode = ScriptExportMode.Decompiled;
        settings.ExportSettings.ShaderExportMode = ShaderExportMode.Yaml;
        ExportHandler handler = new(settings);
        var game = handler.Load(paths);
        var authored = game.GameBundle.FetchAssets().Where(x => x.Collection.Name == Owner).ToArray();
        var tex = authored.OfType<ITexture2D>().OrderBy(x => x.PathID).ToArray();
        expected = tex;
        Need(authored.Length == 9 && tex.Length == 4 && tex.Select(x => x.PathID).SequenceEqual(new long[] {821,822,823,824}),
             "actual loaded authored census");
        Need(tex.All(t => t.Collection is SerializedAssetCollection && t.CheckAssetIntegrity() && t.GetImageData().Length > 0),
             "nonempty typed payload");
        Need(tex[0].Name == tex[1].Name && tex[0].Width_C28 == tex[1].Width_C28 &&
             tex[0].Height_C28 == tex[1].Height_C28 &&
             !tex[0].GetImageData().AsSpan().SequenceEqual(tex[1].GetImageData()), "same key distinct payload");
        var hashes = auth.GetProperty("payload_sha256");
        foreach (var t in tex)
            Need(Convert.ToHexStringLower(SHA256.HashData(t.GetImageData())) ==
                 hashes.GetProperty(t.PathID.ToString()).GetString(), "retained typed texture hash mismatch");
        Save("typed.json", tex.Select(t => new {path_id=t.PathID, width=t.Width_C28, height=t.Height_C28,
             sha256=Convert.ToHexStringLower(SHA256.HashData(t.GetImageData())),
             integrity=t.CheckAssetIntegrity(), serialized=t.Collection is SerializedAssetCollection}).ToArray());

        // Only a synthetic metadata entry derived from an authored texture.
        // The known EGUID constant and a TEST-ONLY file ID are not a claimed
        // engine resource, game ID, real catalogue entry or pixel payload.
        PredefinedAssetCache cache = new();
        Need(cache.TryAdd(EngineAssetsFactory.Create(tex[0]), 12345678L, PredefinedAssetCache.EGUID, AssetType.Internal),
             "authored cache entry");
        EngineAssetsExporter engine = new(cache);
        for (int i=0;i<4;i++)
        {
            bool found = cache.Contains(tex[i], out _, out _, out _);
            Need(found == (i < 2), "actual metadata key match and name/size controls");
            bool selected = engine.TryCreateCollection(tex[i], out IExportCollection? collection);
            Need(selected == found && (!selected || (collection is not null && !collection.Exportable)),
                 "before-process collection selection");
        }
        handler.Process(game);
        Need(tex.All(t => game.GameBundle.FetchAssets().Any(a => ReferenceEquals(a,t))), "same loaded references after processing");

        // Explicitly preserve only the two previously demonstrated distinct
        // ordinary authored objects. All other assets keep the existing chain.
        var admitted = tex.Take(2).Select(t => KeyValuePair.Create(t,
            new VerifiedTexturePreservationExporter.Approval(Owner,t.PathID,t.Width_C28,t.Height_C28,
                hashes.GetProperty(t.PathID.ToString()).GetString()!))).ToArray();
        var preserve = new VerifiedTexturePreservationExporter(settings, admitted);
        for (int i=0;i<4;i++)
        {
            bool selected=preserve.TryCreateCollection(tex[i],out var collection);
            Need(selected==(i<2) && (!selected || collection!.Exportable),
                 "explicit instance scope and native exportability");
        }
        Need(Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(paths[0]))) == ownerHash,
             "retained owner changed after Process");
        // Do not bypass DeletedAssetsExporter or alter real engine records.
        settings.ExportRootPath = args[1];
        settings.SetProjectSettings(game.ProjectVersion);
        ProjectExporter exporter = new(settings, game.AssemblyManager);
        exporter.OverrideExporter<IUnityObjectBase>(engine);
        exporter.OverrideExporter<IUnityObjectBase>(preserve);
        exporter.OverrideExporter<IUnityObjectBase>(new DeletedAssetsExporter());
        exporter.Export(game.GameBundle, settings, LocalFileSystem.Instance);
        Need(File.Exists(Path.Combine(evidence!, "capture.json")), "same export capture missing");
        Console.WriteLine("GT_VERIFIED_TEXTURE_PRESERVATION_ACTUAL_EXPORT_COMPLETE");
    }

    // Called immediately after the real export's own ProjectAssetContainer
    // constructor. Read only; no changes to collections, assets or pointers.
    public static void Capture(ProjectAssetContainer container, IReadOnlyList<IExportCollection> collections)
    {
        Need(evidence is not null && expected is not null, "not the authored invocation");
        var rows = new List<object>();
        foreach (ITexture2D tex in expected!)
        {
            var matches = collections.Where(c => c.Assets.Any(a => ReferenceEquals(a,tex))).ToArray();
            Need(matches.Length == 1, "ambiguous actual collection");
            IExportCollection c = matches[0];
            MetaPtr ptr = container.CreateExportPointer(tex);
            Need(c.Exportable && c.GetType().Name=="TextureExportCollection", "actual final native collection");
            Need(ptr.GUID != PredefinedAssetCache.EGUID && ptr.GUID != PredefinedAssetCache.FGUID &&
                 ptr.FileID != 0 && ptr.AssetType == AssetType.Meta, "actual native texture pointer");
            rows.Add(new {path_id=tex.PathID, collection=c.GetType().Name, exportable=c.Exportable,
                pointer=new {fileID=ptr.FileID, guid=ptr.GUID.ToString(), type=(int)ptr.AssetType}});
        }
        Save("capture.json", rows);
    }
}
