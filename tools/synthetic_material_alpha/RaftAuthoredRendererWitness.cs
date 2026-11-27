// Authored public-tool witness. Compiled into a disposable pinned public
// exporter checkout, never into the game. No game files or Unity editor.
using AssetRipper.Assets;
using AssetRipper.Assets.Bundles;
using AssetRipper.Assets.Collections;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Export.UnityProjects.Project;
using AssetRipper.Import.Structure.Assembly.Managers;
using AssetRipper.IO.Files;
using AssetRipper.Primitives;
using AssetRipper.Processing.Prefabs;
using AssetRipper.SourceGenerated;
using AssetRipper.SourceGenerated.Classes.ClassID_1;
using AssetRipper.SourceGenerated.Classes.ClassID_2;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

public static class RaftAuthoredRendererWitness
{
    private static void Require(bool condition, string reason)
    {
        if (!condition)
            throw new InvalidOperationException(reason);
    }

    private static IUnityObjectBase Add(ProcessedAssetCollection owner, int cls)
    {
        return owner.CreateAsset(cls, info =>
            AssetFactory.CreateSerialized(info, owner.Version)
                ?? throw new InvalidOperationException("authored_factory_class_unavailable"));
    }

    public static void Run(string root)
    {
        Require(!Directory.Exists(root), "fresh_witness_directory_required");
        Directory.CreateDirectory(root);
        var version = new UnityVersion(2021, 3, 45);
        GameBundle bundle = new();
        var generated = bundle.AddNewProcessedCollection("authored-hierarchies", version);
        var collections = new List<IExportCollection>();
        var expected = new Dictionary<(string Owner,long Path), (IUnityObjectBase Asset, IExportCollection Collection)>();
        var hidden = new List<IUnityObjectBase>();
        var scenes = new List<SceneExportCollection>();
        foreach (var name in new[]{"authored-A","authored-B"})
        {
            var owner = bundle.AddNewProcessedCollection(name, version);
            var scene = SceneDefinition.FromName(name);
            scene.AddCollection(owner);
            var hierarchy = generated.CreateAsset(1032, info => new SceneHierarchyObject(info, scene));
            var go = (IGameObject)Add(owner, 1);
            var meshFilter = (IComponent)Add(owner, 33);
            var meshRenderer = (IComponent)Add(owner, 23);
            var skinnedRenderer = (IComponent)Add(owner, 137);
            var hiddenRenderer = (IComponent)Add(owner, 23);
            hierarchy.GameObjects.Add(go);
            hierarchy.Components.AddRange(new[]{meshFilter, meshRenderer, skinnedRenderer, hiddenRenderer});
            hierarchy.HiddenAssets.Add(hiddenRenderer);
            hidden.Add(hiddenRenderer);
            var collection = new SceneExportCollection(new SceneYamlExporter(), hierarchy);
            collections.Add(collection);
            scenes.Add(collection);
            foreach (var obj in new IUnityObjectBase[]{go,meshFilter,meshRenderer,skinnedRenderer})
                expected.Add((obj.Collection.Name,obj.PathID),(obj,collection));
        }
        // Same source PathID exists in different owner collections, but they
        // must never be conflated or joined by a display name.
        Require(expected.Keys.GroupBy(k=>k.Path).Any(g=>g.Count()==2), "same_pathID_control_missing");
        var meshOwner = bundle.AddNewProcessedCollection("authored-mesh-owner", version);
        var mesh = Add(meshOwner,43);
        var meshCollection = new AssetExportCollection<IUnityObjectBase>(new DefaultYamlExporter(),mesh);
        collections.Add(meshCollection);
        var material = Add(meshOwner,21);
        var materialCollection = new AssetExportCollection<IUnityObjectBase>(new DefaultYamlExporter(),material);
        collections.Add(materialCollection);
        LibraryConfiguration settings = new();
        settings.SetProjectSettings(version);
        var exporter = new ProjectExporter(settings,new MonoManager(_ => throw new InvalidOperationException("unexpected_assembly_request")));
        var container = new ProjectAssetContainer(exporter,settings,collections.SelectMany(c=>c.Assets),collections);
        var materialPath = Path.Combine(root,"materials.private.json");
        var meshPath = Path.Combine(root,"meshes.private.json");
        var componentPath = Path.Combine(root,"components.private.json");
        Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LINEAGE",materialPath);
        Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_MESH_LINEAGE",meshPath);
        Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE",componentPath);
        Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE","1");
        try
        {
            RaftExportLineage.Capture(container,collections);
        }
        finally
        {
            foreach (var variable in new[]{"RAFT_PRIVATE_EXPORT_LINEAGE","RAFT_PRIVATE_EXPORT_MESH_LINEAGE","RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE","RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE"})
                Environment.SetEnvironmentVariable(variable,null);
        }
        using var mt = JsonDocument.Parse(File.ReadAllBytes(materialPath));
        using var gt = JsonDocument.Parse(File.ReadAllBytes(meshPath));
        using var ct = JsonDocument.Parse(File.ReadAllBytes(componentPath));
        var instance = mt.RootElement.GetProperty("export_instance").GetString();
        Require(instance is not null && instance.Length==32 &&
                instance==gt.RootElement.GetProperty("export_instance").GetString() &&
                instance==ct.RootElement.GetProperty("export_instance").GetString(),"mixed_instance");
        Require(mt.RootElement.GetProperty("objects").GetArrayLength()==1,"material_trace_count");
        Require(gt.RootElement.GetProperty("meshes").GetArrayLength()==1,"mesh_trace_count");
        var seen = new HashSet<(string,long)>();
        var globalPointers = new HashSet<(string,long)>();
        int localChecks=0, crossChecks=0;
        foreach (var row in ct.RootElement.GetProperty("components").EnumerateArray())
        {
            var source = row.GetProperty("source");
            var key = (source.GetProperty("owner").GetString()!,source.GetProperty("path_id").GetInt64());
            Require(seen.Add(key) && expected.ContainsKey(key),"unexpected_or_duplicate_component");
            var item=expected[key];
            Require(row.GetProperty("class_id").GetInt32()==item.Asset.ClassID &&
                row.GetProperty("exportable").GetBoolean() &&
                row.GetProperty("collection_type").GetString()==typeof(SceneExportCollection).FullName,"component_class_or_exportability");
            var global = item.Collection.CreateExportPointer(container,item.Asset,false);
            var traced = row.GetProperty("export");
            Require(!global.GUID.IsZero && global.AssetType==AssetType.Serialized &&
                global.FileID==item.Collection.GetExportID(container,item.Asset) &&
                traced.GetProperty("file_id").GetInt64()==global.FileID &&
                traced.GetProperty("guid").GetString()==global.GUID.ToString() &&
                traced.GetProperty("type").GetInt32()==2 &&
                globalPointers.Add((global.GUID.ToString(),global.FileID)),"global_component_pointer_mismatch");
            container.CurrentCollection=item.Collection;
            var local=container.CreateExportPointer(item.Asset);
            Require(local.GUID.IsZero && local.AssetType==AssetType.Serialized && local.FileID==global.FileID &&
                local.ToString()=="{fileID: "+global.FileID+"}","local_component_pointer_mismatch");
            localChecks++;
            container.CurrentCollection=scenes.Single(s=>s!=item.Collection);
            var cross=container.CreateExportPointer(item.Asset);
            Require(cross.Equals(global),"cross_scene_pointer_mismatch");
            crossChecks++;
        }
        Require(seen.Count==8 && expected.Count==8 && hidden.All(a=>!seen.Contains((a.Collection.Name,a.PathID))),
            "hidden_or_missing_component");
        // Test the actual hook refuses renderer capture without its mesh trace.
        var noMesh=Path.Combine(root,"without-mesh.private.json");
        Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LINEAGE",noMesh);
        Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE",Path.Combine(root,"unexpected.private.json"));
        bool rejected=false;
        try { RaftExportLineage.Capture(container,collections); }
        catch (InvalidOperationException e) when (e.Message=="Renderer lineage requires mesh lineage") { rejected=true; }
        finally {
            Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LINEAGE",null);
            Environment.SetEnvironmentVariable("RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE",null);
        }
        Require(rejected && !File.Exists(Path.Combine(root,"unexpected.private.json")),"missing_mesh_trace_not_rejected");
        foreach(var path in Directory.GetFiles(root))
            File.Delete(path);
        var receipt=new {
            status="PASS_PUBLIC_EXPORTER_AUTHORED_COMPONENT_POINTERS",
            public_tool_revision="036098ab525a3f9f693dc101edeb21faad4d32d8",
            actual_compiled_capture_executed=true,
            actual_SceneExportCollection_count=2,
            component_rows_verified=seen.Count,
            hidden_components_excluded=hidden.Count,
            global_component_pointers_verified=globalPointers.Count,
            local_pointer_serialized_type2_zero_guid_verified=localChecks,
            cross_scene_global_pointers_verified=crossChecks,
            same_source_pathID_different_owner_control=true,
            same_instance_material_mesh_component_traces=true,
            missing_mesh_trace_rejected=true,
            original_assets_read=false,
            serialized_original_source=false,
            Unity_render_executed=false,
            actual_scene_YAML_export_executed=false,
            production_renderer_parity_verified=false,
            XAPK=false
        };
        File.WriteAllText(Path.Combine(root,"receipt.json"),JsonSerializer.Serialize(receipt));
        Console.WriteLine("RAFT_AUTHORED_RENDERER_POINTER_WITNESS_PASS");
    }
}
