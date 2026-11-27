// Authored public AssetRipper fixture: actual native YAML writer and trace.
// No original files, no Unity editor, no production exporter auto-selection.
using AssetRipper.Assets;
using AssetRipper.Assets.Bundles;
using AssetRipper.Assets.Collections;
using AssetRipper.Assets.Generics;
using AssetRipper.Assets.Metadata;
using AssetRipper.Export.UnityProjects.Configuration;
using AssetRipper.Export.UnityProjects.Project;
using AssetRipper.Export.UnityProjects.Shaders;
using AssetRipper.Import.Structure.Assembly.Managers;
using AssetRipper.IO.Files;
using AssetRipper.IO.Files.ResourceFiles;
using System.Security.Cryptography;
using AssetRipper.Primitives;
using AssetRipper.Processing.Prefabs;
using AssetRipper.SourceGenerated;
using AssetRipper.SourceGenerated.Classes.ClassID_1;
using AssetRipper.SourceGenerated.Classes.ClassID_2;
using AssetRipper.SourceGenerated.Classes.ClassID_21;
using AssetRipper.SourceGenerated.Classes.ClassID_25;
using AssetRipper.SourceGenerated.Classes.ClassID_28;
using AssetRipper.SourceGenerated.Subclasses.GLTextureSettings;
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

    // Generated Material property names vary by version. Only accept the
    // exact modern typed list from the actual object; never synthesize a
    // source contract if the factory lacks the corresponding field.
    private static string[] SetAndCaptureState(IMaterial mat,string stem,params string[] entries)
    {
        var matches=mat.GetType().GetInterfaces().SelectMany(t=>t.GetProperties())
            .Where(p=>(p.Name==stem || p.Name==stem+"_C21") &&
                p.GetIndexParameters().Length==0 &&
                typeof(AssetList<Utf8String>).IsAssignableFrom(p.PropertyType))
            .Select(p=>p.GetValue(mat)).OfType<AssetList<Utf8String>>()
            .Distinct<AssetList<Utf8String>>(ReferenceEqualityComparer.Instance).ToArray();
        Require(matches.Length==1,"authored_material_state_field_unavailable:"+stem);
        var list=matches[0];
        Require(list.Count==0,"authored_material_state_not_empty:"+stem);
        foreach(var entry in entries) list.Add((Utf8String)entry);
        var result=new string[list.Count];
        for(int n=0;n<list.Count;n++) result[n]=list[n].String;
        Require(result.SequenceEqual(entries),"authored_material_state_capture_drift:"+stem);
        return result;
    }

    // Numeric dimension property names differ among generated versions.
    // Resolve a concrete field setter, read it back, and reject ambiguity.
    private static int SetTextureDimension(ITexture2D tex)
    {
        var properties=tex.GetType().GetInterfaces().SelectMany(t=>t.GetProperties())
            .Where(p=>p.CanRead && p.CanWrite &&
              (p.Name=="TextureDimension_C28" || p.Name=="Dimension_C28" ||
               p.Name=="TextureDimension_C28E" || p.Name=="Dimension_C28E"))
            .OrderBy(p=>p.Name.EndsWith("E")?1:0).ToArray();
        Require(properties.Length>0,"authored_texture_dimension_field_missing");
        var property=properties[0];
        object value=property.PropertyType.IsEnum?Enum.ToObject(property.PropertyType,2):
            Convert.ChangeType(2,property.PropertyType);
        property.SetValue(tex,value);
        int captured=Convert.ToInt32(property.GetValue(tex));
        Require(captured==2,"authored_texture_dimension_capture_drift");
        return captured;
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
        const string providerName="authored-textures.resS";
        var providerData=Enumerable.Repeat((byte)0xA7,61).ToArray();
        var providerRoot=Path.Combine(root,"providers");
        Directory.CreateDirectory(providerRoot);
        var providerPath=Path.Combine(providerRoot,providerName);
        var mats=new List<IMaterial>();
        for(int i=0;i<2;i++)
        {
            var owner=i==0?matOwnerA:matOwnerB;
            var mat=(IMaterial)Add(owner,21,"AuthoredMaterial"+i);
            var shader=(IShader)Add(owner,48,"AuthoredShader"+i);
            var tex=(ITexture2D)Add(texOwner,28,"AuthoredTexture"+i);
            // Two complete mip levels, asymmetric RGB and varying alpha.
            // These are native serialized bytes, not decoded GPU pixels.
            tex.Width_C28=2;tex.Height_C28=2;
            tex.Format_C28E=AssetRipper.SourceGenerated.Enums.TextureFormat.RGBA32;
            tex.MipCount_C28=2;tex.ImageCount_C28=1;
            int dimension=SetTextureDimension(tex);
            // Typed generated GLTextureSettings, including distinct U/V/W.
            // Different interface aliases must resolve to the same instance.
            var samplerProps=tex.GetType().GetInterfaces().SelectMany(t=>t.GetProperties())
                .Where(p=>p.CanRead && typeof(IGLTextureSettings).IsAssignableFrom(p.PropertyType)).ToArray();
            var settings=samplerProps.Select(p=>p.GetValue(tex)).OfType<IGLTextureSettings>().ToArray();
            Require(settings.Length>0 && settings.All(s=>ReferenceEquals(s,settings[0])),
                "authored_texture_sampler_not_unique");
            var sampler=settings[0];
            sampler.FilterMode=1+i;
            sampler.Aniso=2+i*6;
            sampler.MipBias=i==0?-.625f:.375f;
            sampler.WrapU=i;sampler.WrapV=2-i;sampler.WrapW=3-i;
            Require(sampler.FilterMode==1+i && sampler.Aniso==2+i*6 &&
                sampler.MipBias==(i==0?-.625f:.375f) && sampler.WrapU==i &&
                sampler.WrapV==2-i && sampler.WrapW==3-i,"authored_sampler_capture_drift");
            var mipBytes=new byte[]{(byte)(32+64*i),64,192,0,
                128,(byte)(96+32*i),32,255,18,172,93,127,207,9,55,64,
                (byte)(90+32*i),66,33,171};
            int extent=7+27*i;
            Buffer.BlockCopy(mipBytes,0,providerData,extent,mipBytes.Length);
            tex.ImageData_C28=[];
            if(tex.Has_CompleteImageSize_C28_UInt32()) tex.CompleteImageSize_C28_UInt32=(uint)mipBytes.Length;
            else tex.CompleteImageSize_C28_Int32=mipBytes.Length;
            Require(tex.StreamData_C28 is not null,"authored_texture_stream_field_missing");
            tex.StreamData_C28!.SetValues((Utf8String)providerName,(ulong)extent,(uint)mipBytes.Length);
            tex.StreamData_C28.GetValues(out Utf8String streamPath,out ulong streamOffset,out uint streamSize);
            Require(tex.ImageData_C28.Length==0 && streamPath.String==providerName &&
                streamOffset==(ulong)extent && streamSize==(uint)mipBytes.Length,"authored_texture_stream_capture_drift");
            mat.Shader_C21P=shader;
            var props=mat.SavedProperties_C21;
            Require(props.Has_TexEnvs_AssetDictionary_Utf8String_UnityTexEnv_5(),"unexpected_authored_texenv_layout");
            var pair=props.TexEnvs_AssetDictionary_Utf8String_UnityTexEnv_5.AddNew();
            pair.Key="_MainTex";
            var env=pair.Value;
            env.Texture.SetAsset(mat.Collection,tex);
            env.Scale.X=1+i;env.Scale.Y=.75f;
            env.Offset.X=.125f*(i+1);env.Offset.Y=.25f;
            // Non-identical finite saved values, including HDR/negative color
            // components and int32 values beyond exact float32 precision.
            Require(props.Has_Colors_AssetDictionary_Utf8String_ColorRGBAf() &&
                props.Has_Floats_AssetDictionary_Utf8String_Single() && props.Has_Ints(),
                "unexpected_authored_material_value_layout");
            var tint=props.Colors_AssetDictionary_Utf8String_ColorRGBAf.AddNew();
            tint.Key="_AuthoredTint";
            tint.Value.R=.125f+i*.25f;tint.Value.G=.5f;tint.Value.B=1.5f+i;tint.Value.A=.625f-i*.25f;
            var vector=props.Colors_AssetDictionary_Utf8String_ColorRGBAf.AddNew();
            vector.Key="_AuthoredVector";
            vector.Value.R=-.375f;vector.Value.G=2.25f+i;vector.Value.B=.0625f;vector.Value.A=0;
            var scalar=props.Floats_AssetDictionary_Utf8String_Single.AddNew();
            scalar.Key="_AuthoredFloat";scalar.Value=.375f+i*.125f;
            var scalar2=props.Floats_AssetDictionary_Utf8String_Single.AddNew();
            scalar2.Key="_AuthoredNegative";scalar2.Value=-2.5f-i;
            var integer=props.Ints.AddNew();integer.Key="_AuthoredInteger";integer.Value=16777217+i;
            var integer2=props.Ints.AddNew();integer2.Key="_AuthoredSigned";integer2.Value=-17-i;
            // Distinct per-material lanes; not a claim that authored shader
            // code actually declares or uses these names at runtime.
            var valid=SetAndCaptureState(mat,"ValidKeywords","AUTHORED_SHARED",
                i==0?"AUTHORED_FOAM":"AUTHORED_ALPHA");
            var invalid=SetAndCaptureState(mat,"InvalidKeywords",
                i==0?"AUTHORED_UNUSED_A":"AUTHORED_UNUSED_B");
            var disabled=SetAndCaptureState(mat,"DisabledShaderPasses",
                i==0?"AuthoredDepth":"AuthoredShadow");
            Require(mat.Shader_C21P==shader,"authored_shader_binding_failed");
            mats.Add(mat);
            collections.Add(new AssetExportCollection<IUnityObjectBase>(native,mat));
            collections.Add(new YamlShaderExportCollection(new YamlShaderExporter(),shader));
            collections.Add(new YamlStreamedAssetExportCollection(new YamlStreamedAssetExporter(),tex));
            // AssetDictionary exposes multiple enumerable interfaces; use
            // explicit indexed reads of the generated objects, not LINQ
            // inference or reconstructed literals from exported YAML.
            var colors=props.Colors_AssetDictionary_Utf8String_ColorRGBAf;
            var floats=props.Floats_AssetDictionary_Utf8String_Single;
            var ints=props.Ints;
            var capturedColors=new object[colors.Count];
            var capturedFloats=new object[floats.Count];
            var capturedInts=new object[ints.Count];
            for(int n=0;n<colors.Count;n++)
            {
                var c=colors.GetValue(n);
                capturedColors[n]=new object[]{colors.GetKey(n).String,new {r=c.R,g=c.G,b=c.B,a=c.A}};
            }
            for(int n=0;n<floats.Count;n++)
                capturedFloats[n]=new object[]{floats.GetKey(n).String,floats.GetValue(n)};
            for(int n=0;n<ints.Count;n++)
                capturedInts[n]=new object[]{ints.GetKey(n).String,ints.GetValue(n)};
            rows.Add(Row(mat,new {m_Shader=Ref(mat,shader),m_ValidKeywords=valid,
                m_InvalidKeywords=invalid,disabledShaderPasses=disabled,m_SavedProperties=new {
                m_Colors=capturedColors,
                m_Floats=capturedFloats,
                m_Ints=capturedInts,
                m_TexEnvs=new object[]{new object[]{"_MainTex",new {m_Texture=Ptr(env.Texture),
                    m_Scale=new {x=env.Scale.X,y=env.Scale.Y},m_Offset=new {x=env.Offset.X,y=env.Offset.Y}}}}
            }}));
            rows.Add(Row(shader,null));
            rows.Add(Row(tex,new Dictionary<string,object>{
                ["m_Width"]=tex.Width_C28,["m_Height"]=tex.Height_C28,
                ["m_TextureFormat"]=(int)tex.Format_C28E,["m_MipCount"]=tex.MipCount_C28,
                ["m_TextureSettings"]=new {m_FilterMode=sampler.FilterMode,m_Aniso=sampler.Aniso,
                    m_MipBias=sampler.MipBias,m_WrapU=sampler.WrapU,m_WrapV=sampler.WrapV,m_WrapW=sampler.WrapW},
                ["m_ImageCount"]=tex.ImageCount_C28,["m_TextureDimension"]=dimension,
                ["m_CompleteImageSize"]=tex.Has_CompleteImageSize_C28_UInt32()?
                    (long)tex.CompleteImageSize_C28_UInt32:tex.CompleteImageSize_C28_Int32,
                ["image data"]=tex.ImageData_C28.Select(b=>(int)b).ToArray(),
                ["m_StreamData"]=new {path=streamPath.String,offset=streamOffset,size=streamSize}
            }));
        }
        // Actual file-backed ResourceFile consumed by the pinned exporter.
        File.WriteAllBytes(providerPath,providerData);
        bundle.AddResource(new ResourceFile(providerPath,providerName));
        Require(bundle.ResolveResource(providerName) is not null,"authored_provider_not_resolved");
        string providerSHA=Convert.ToHexString(SHA256.HashData(providerData)).ToLowerInvariant();
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
        var source=new {schema_version=7,authored_generated_objects=true,objects=rows,externals,
            providers=new[]{new {name=providerName,bytes=providerData.Length,sha256=providerSHA}},
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
            authored_native_shader_programs_verified=false,authored_file_backed_streamed_texture_collections=2,
            Android_device=false,XAPK=false
        }));
        Console.WriteLine("RAFT_AUTHORED_SCENE_YAML_EXPORT_OBSERVED");
    }
}
