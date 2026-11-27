// Authored public AssetRipper fixture: actual native YAML writer and trace.
// No original files, no Unity editor, no production exporter auto-selection.
using AssetRipper.Assets;
using AssetRipper.Assets.Bundles;
using AssetRipper.Assets.Collections;
using AssetRipper.Assets.Metadata;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Export.UnityProjects.Project;
using AssetRipper.Export.UnityProjects.Shaders;
using AssetRipper.Import.Structure.Assembly.Managers;
using AssetRipper.IO.Files;
using AssetRipper.Primitives;
using AssetRipper.Processing.Prefabs;
using AssetRipper.SourceGenerated;
using AssetRipper.SourceGenerated.Classes.ClassID_1;
using AssetRipper.SourceGenerated.Classes.ClassID_2;
using AssetRipper.SourceGenerated.Classes.ClassID_21;
using AssetRipper.SourceGenerated.Classes.ClassID_25;
using AssetRipper.SourceGenerated.Classes.ClassID_28;
using AssetRipper.SourceGenerated.Classes.ClassID_33;
using AssetRipper.SourceGenerated.Classes.ClassID_43;
using AssetRipper.SourceGenerated.Classes.ClassID_48;
using AssetRipper.SourceGenerated.Extensions;
using System.Text.Json;

namespace AssetRipper.Export.UnityProjects;

public static class RaftAuthoredSceneRouteWitness
{
    private static void Require(bool condition, string reason)
    {
        if(!condition) throw new InvalidOperationException(reason);
    }

    private static IUnityObjectBase Add(ProcessedAssetCollection owner,int cls,string name)
    {
        var obj=owner.CreateAsset(cls,info=>AssetFactory.CreateSerialized(info,owner.Version)
            ?? throw new InvalidOperationException("authored_factory_class_unavailable"));
        obj.OriginalDirectory="Assets/AuthoredRouteWitness";
        obj.OriginalName=name;
        return obj;
    }

    // Query actual generated raw PPtr field (base and derived interfaces can
    // alias it); require a single concrete pointer, not a guessed field name.
    private static IPPtr Link(IUnityObjectBase source,string stem,IUnityObjectBase target)
    {
        var values=source.GetType().GetInterfaces().SelectMany(t=>t.GetProperties())
            .Where(p=>p.Name.StartsWith(stem,StringComparison.Ordinal) &&
                typeof(IPPtr).IsAssignableFrom(p.PropertyType) && p.GetIndexParameters().Length==0)
            .Select(p=>p.GetValue(source)).OfType<IPPtr>()
            .Distinct<IPPtr>(ReferenceEqualityComparer.Instance).ToArray();
        Require(values.Length==1,"authored_raw_pointer_ambiguous:"+stem);
        var raw=values[0];
        var setters=raw.GetType().GetInterfaces().Where(t=>t.IsGenericType &&
            t.GetGenericTypeDefinition()==typeof(IPPtr<>) &&
            t.GetGenericArguments()[0].IsInstanceOfType(target)).ToArray();
        Require(setters.Length==1,"authored_raw_pointer_setter_ambiguous:"+stem);
        setters[0].GetMethod("SetAsset")!.Invoke(raw,new object[]{source.Collection,target});
        var expected=source.Collection.CreatePPtr(target);
        Require(raw.FileID==expected.FileID && raw.PathID==expected.PathID,"authored_raw_pointer_drift:"+stem);
        return raw;
    }

    private static object Ptr(IPPtr p)=>new {m_FileID=p.FileID,m_PathID=p.PathID};
    private static object Ref(IUnityObjectBase owner,IUnityObjectBase target)
    {
        var p=owner.Collection.CreatePPtr(target);
        return new {m_FileID=p.FileID,m_PathID=p.PathID};
    }
    private static object Row(IUnityObjectBase obj,object? tree)=>new {
        owner=obj.Collection.Name,path_id=obj.PathID,class_id=obj.ClassID,tree
    };

    public static void Run(string root)
    {
        Require(!Directory.Exists(root),"fresh_authored_route_root_required");
        Directory.CreateDirectory(root);
        string project=Path.Combine(root,"project");
        Directory.CreateDirectory(Path.Combine(project,"Assets"));
        var version=new UnityVersion(2021,3,45);
        GameBundle bundle=new();
        var generated=bundle.AddNewProcessedCollection("authored-hierarchies",version);
        var meshOwner=bundle.AddNewProcessedCollection("sharedassets0.assets",version);
        var matOwnerA=bundle.AddNewProcessedCollection("sharedassets1.assets",version);
        var matOwnerB=bundle.AddNewProcessedCollection("sharedassets2.assets",version);
        var texOwner=bundle.AddNewProcessedCollection("sharedassets3.assets",version);
        var owners=new List<ProcessedAssetCollection>{meshOwner,matOwnerA,matOwnerB,texOwner};
        var collections=new List<IExportCollection>();
        var rows=new List<object>();
        var native=new DefaultYamlExporter();

        var mesh=(IMesh)Add(meshOwner,43,"AuthoredMesh");
        mesh.SetIndexFormat(AssetRipper.SourceGenerated.Enums.IndexFormat.UInt16);
        mesh.SetProcessedIndexBuffer(new uint[]{0,1,2,0,2,1});
        mesh.VertexData.VertexCount=6;
        for(int i=0;i<14;i++)
        {
            var ch=mesh.VertexData.Channels.AddNew();
            ch.Stream=0; ch.Offset=(byte)(i==4?12:0); ch.Format=0;
            ch.Dimension=(byte)(i==0?3:i==4?2:0);
        }
        // Interleaved XYZ + UV, real inline authored payload.
        float[] vertices={
            -2,-1,0,0,0, -.5f,-1,0,1,0, -2,1,0,0,1,
            -.5f,-1,0,1,0, 2,-1,0,0,0, 2,1,0,0,1
        };
        byte[] vb=new byte[vertices.Length*sizeof(float)];
        Buffer.BlockCopy(vertices,0,vb,0,vb.Length);
        mesh.VertexData.Data=vb;
        for(uint slot=0;slot<2;slot++)
        {
            var sub=mesh.SubMeshes.AddNew();
            sub.FirstByte=slot*6;sub.IndexCount=3;sub.BaseVertex=slot*3;
            sub.FirstVertex=slot*3;sub.VertexCount=3;sub.SetTopology(AssetRipper.SourceGenerated.Enums.MeshTopology.Triangles);
        }
        collections.Add(new YamlStreamedAssetExportCollection(new YamlStreamedAssetExporter(),mesh));
        rows.Add(Row(mesh,new {
            m_VertexData=new {m_VertexCount=mesh.VertexData.VertexCount,
                m_Channels=mesh.VertexData.Channels.Select(ch=>new {stream=ch.Stream,offset=ch.Offset,format=ch.Format,dimension=ch.Dimension}).ToArray(),
                m_DataSize=mesh.VertexData.Data.Select(b=>(int)b).ToArray()},
            // This generated fixture has no compressed or external payload.
            m_CompressedMesh=new {m_UVInfo=0},m_MeshCompression=0,
            m_StreamData=new {path="",offset=0,size=0},
            m_IndexFormat=(int)mesh.GetIndexFormat(),m_IndexBuffer=mesh.IndexBuffer.Select(b=>(int)b).ToArray(),
            m_SubMeshes=mesh.SubMeshes.Select(sub=>new {firstByte=sub.FirstByte,indexCount=sub.IndexCount,
                topology=(int)sub.GetTopology(),baseVertex=sub.BaseVertex,firstVertex=sub.FirstVertex,vertexCount=sub.VertexCount}).ToArray()
        }));
        var mats=new List<IMaterial>();
        for(int i=0;i<2;i++)
        {
            var owner=i==0?matOwnerA:matOwnerB;
            var mat=(IMaterial)Add(owner,21,"AuthoredMaterial"+i);
            var shader=(IShader)Add(owner,48,"AuthoredShader"+i);
            var tex=(ITexture2D)Add(texOwner,28,"AuthoredTexture"+i);
            // Native YAML targets prove object identity only; not usable
            // shader programs or imported texture pixel parity.
            tex.Width_C28=2;tex.Height_C28=1;
            tex.ImageData_C28=new byte[]{(byte)(32+64*i),64,192,255,128,(byte)(96+32*i),32,255};
            mat.Shader_C21P=shader;
            var props=mat.SavedProperties_C21;
            Require(props.Has_TexEnvs_AssetDictionary_Utf8String_UnityTexEnv_5(),"unexpected_authored_texenv_layout");
            var pair=props.TexEnvs_AssetDictionary_Utf8String_UnityTexEnv_5.AddNew();
            pair.Key="_MainTex";
            var env=pair.Value;
            env.Texture.SetAsset(mat.Collection,tex);
            env.Scale.X=1+i;env.Scale.Y=.75f;
            env.Offset.X=.125f*(i+1);env.Offset.Y=.25f;
            Require(mat.Shader_C21P==shader,"authored_shader_binding_failed");
            mats.Add(mat);
            collections.Add(new AssetExportCollection<IUnityObjectBase>(native,mat));
            collections.Add(new YamlShaderExportCollection(new YamlShaderExporter(),shader));
            collections.Add(new AssetExportCollection<IUnityObjectBase>(native,tex));
            rows.Add(Row(mat,new {m_Shader=Ref(mat,shader),m_SavedProperties=new {
                m_TexEnvs=new object[]{new object[]{"_MainTex",new {m_Texture=Ptr(env.Texture),
                    m_Scale=new {x=env.Scale.X,y=env.Scale.Y},m_Offset=new {x=env.Offset.X,y=env.Offset.Y}}}}
            }}));
            rows.Add(Row(shader,null));rows.Add(Row(tex,null));
        }
        // Independent scene owners with identical PathIDs. Material owners
        // also share a PathID, and dependency order differs across scenes.
        var hidden=new List<IUnityObjectBase>();
        var sceneRenderers=new List<IRenderer>();
        var scenes=new List<SceneExportCollection>();
        foreach(var name in new[]{"level1","level2"})
        {
            var owner=bundle.AddNewProcessedCollection(name,version);
            owners.Add(owner);
            var scene=SceneDefinition.FromName(name);
            scene.AddCollection(owner);
            var hierarchy=generated.CreateAsset(1032,info=>new SceneHierarchyObject(info,scene));
            var go=(IGameObject)Add(owner,1,"AuthoredGameObject");
            var mf=(IMeshFilter)Add(owner,33,"AuthoredMeshFilter");
            var renderer=(IRenderer)Add(owner,23,"AuthoredMeshRenderer");
            var hiddenRenderer=(IRenderer)Add(owner,23,"AuthoredHiddenRenderer");
            var goF=Link(mf,"GameObject",go);
            var goR=Link(renderer,"GameObject",go);
            var meshRef=Link(mf,"Mesh",mesh);
            go.AddComponent(ClassIDType.MeshFilter,mf);
            go.AddComponent(ClassIDType.MeshRenderer,renderer);
            var ordered=name=="level1"?mats.ToArray():mats.AsEnumerable().Reverse().ToArray();
            var materialList=renderer.Materials_C25P;
            materialList.AddRange(ordered);
            Require(renderer.Materials_C25P.SequenceEqual(ordered) && mf.MeshP==mesh,"authored_scene_bindings_failed");
            hierarchy.GameObjects.Add(go);
            hierarchy.Components.AddRange(new IComponent[]{mf,renderer,hiddenRenderer});
            hierarchy.HiddenAssets.Add(hiddenRenderer);
            hidden.Add(hiddenRenderer);sceneRenderers.Add(renderer);
            var col=new SceneExportCollection(new SceneYamlExporter(),hierarchy);
            scenes.Add(col);collections.Add(col);
            rows.Add(Row(go,new {m_Component=go.FetchComponents().Select(p=>new {component=Ptr(p)}).ToArray()}));
            rows.Add(Row(mf,new {m_GameObject=Ptr(goF),m_Mesh=Ptr(meshRef)}));
            rows.Add(Row(renderer,new {m_GameObject=Ptr(goR),
                m_Materials=renderer.Materials_C25P.Select(m=>Ref(renderer,m!)).ToArray()}));
        }
        Require(sceneRenderers[0].PathID==sceneRenderers[1].PathID &&
            mats[0].PathID==mats[1].PathID && mats[0].Collection!=mats[1].Collection,"same_pathID_control_missing");
        var externals=owners.ToDictionary(o=>o.Name,o=>o.Dependencies.Skip(1).Select(d=>d?.Name).ToArray());
        // The source contract is captured from generated objects before any
        // export or trace. It is not reconstructed from exported YAML.
        var source=new {schema_version=2,authored_generated_objects=true,objects=rows,externals,
            hidden=hidden.Select(o=>new {owner=o.Collection.Name,path_id=o.PathID,class_id=o.ClassID}).ToArray()};
        File.WriteAllText(Path.Combine(root,"source.json"),JsonSerializer.Serialize(source));
        LibraryConfiguration settings=new();settings.SetProjectSettings(version);
        var exporter=new ProjectExporter(settings,new MonoManager(_=>throw new InvalidOperationException("unexpected_assembly_request")));
        var container=new ProjectAssetContainer(exporter,settings,collections.SelectMany(c=>c.Assets),collections);
        var envs=new Dictionary<string,string>{
            ["RAFT_PRIVATE_EXPORT_LINEAGE"]=Path.Combine(root,"materials.json"),
            ["RAFT_PRIVATE_EXPORT_MESH_LINEAGE"]=Path.Combine(root,"meshes.json"),
            ["RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE"]=Path.Combine(root,"components.json"),
            ["RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE"]="1"
        };
        try {
            foreach(var pair in envs)Environment.SetEnvironmentVariable(pair.Key,pair.Value);
            RaftExportLineage.Capture(container,collections);
        } finally {
            foreach(var key in envs.Keys)Environment.SetEnvironmentVariable(key,null);
        }
        int exported=0;
        foreach(var col in collections)
        {
            container.CurrentCollection=col;
            Require(col.Export(container,project,LocalFileSystem.Instance),"actual_public_collection_export_failed:"+col.GetType().Name);
            exported++;
        }
        Require(exported==9,"unexpected_authored_export_collection_count");
        File.WriteAllText(Path.Combine(root,"producer.json"),JsonSerializer.Serialize(new {
            status="OBSERVED_AUTHORED_PUBLIC_YAML_EXPORT",actual_public_export_collections=exported,
            actual_scene_collections=scenes.Count,source_objects=rows.Count,hidden_components=hidden.Count,
            public_tool_revision="036098ab525a3f9f693dc101edeb21faad4d32d8",
            original_assets_read=false,original_serialized_source=false,production_auto_exporter_selection=false,
            authored_native_shader_programs_verified=false,Android_device=false,XAPK=false
        }));
        Console.WriteLine("RAFT_AUTHORED_SCENE_YAML_EXPORT_OBSERVED");
    }
}
