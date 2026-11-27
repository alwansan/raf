// Actual authored Unity mesh/submesh/material/texture routing witness.
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

public static class SyntheticSubmeshRouteValidation
{
    const int Width=8, Height=4;
    const string ShaderA="Assets/AuthoredRouteA.shader", ShaderB="Assets/AuthoredRouteB.shader";
    const string PngA="Assets/AuthoredRouteA.png", PngB="Assets/AuthoredRouteB.png";
    const string MatA="Assets/AuthoredRouteA.mat", MatB="Assets/AuthoredRouteB.mat";
    const string MeshPath="Assets/AuthoredRoute.asset", DecoyPath="Assets/AuthoredRouteDecoy.asset";
    const string Probe="Assets/Editor/SyntheticSubmeshRouteValidation.cs";
    static readonly string[] Inputs={ShaderA,ShaderB,PngA,PngB,Probe};
    static readonly Color Background=new Color(.0625f,.125f,.1875f,.25f);
    static readonly Color TintA=new Color(.8f,.5f,.25f,1), TintB=new Color(.4f,.9f,.7f,1);
    static readonly Vector2 ScaleA=new Vector2(.58f,.65f), OffsetA=new Vector2(.09f,.07f);
    static readonly Vector2 ScaleB=new Vector2(.76f,.70f), OffsetB=new Vector2(.11f,.13f);
    [Serializable] sealed class Sample { public int x,y; public float[] observed; }
    [Serializable] sealed class Imported {
        public string path,guid,format,graphics_format,filter,wrap,shape,alpha_source,compression;
        public bool srgb,graphics_srgb,readable,mipmaps;
        public int width,height,mip_count;
        public int[] rgba8;
    }
    [Serializable] sealed class Binding {
        public string material,material_guid,shader,texture,texture_guid;
        public int material_instance;
        public float[] tint,scale,offset;
    }
    [Serializable] sealed class Case {
        public string name,mesh,mesh_guid;
        public int mesh_instance,submesh_count,vertex_count,checked_pixel_count;
        public int[] base_vertices,indices0,indices1;
        public float[] vertices,uv0;
        public Binding[] slots;
        public Sample[] pixels;
    }
    [Serializable] sealed class Receipt {
        public int schema_version=1;
        public string run_id,status="NOT_RUN",reason="not_started",Unity_version,backend,active_color_space,graphics_device_name;
        public string[] source_paths,source_sha256_before,source_sha256_after;
        public bool synthetic_only=true,Unity_render_executed,Android_device,production_pixels,XAPK;
        public List<Imported> imported=new List<Imported>();
        public List<Case> cases=new List<Case>();
    }
    sealed class Unavailable : Exception { public Unavailable(string message):base(message){} }

    public static void Run()
    {
        var result=new Receipt {
            run_id=Option("RAFT_SUBMESH_ROUTE_RUN_ID","-raftSubmeshRouteRunId"),
            Unity_version=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),
            active_color_space=QualitySettings.activeColorSpace.ToString(),graphics_device_name=SystemInfo.graphicsDeviceName
        };
        var owned=new List<UnityEngine.Object>();
        RenderTexture previous=RenderTexture.active;
        bool srgb=GL.sRGBWrite,async=ShaderUtil.allowAsyncCompilation;
        RenderTexture target=null;
        string output=null;
        int code=2;
        try {
            string root=Directory.GetParent(Application.dataPath).FullName;
            output=OutsideProjectReport(root);
            if (String.IsNullOrWhiteSpace(result.run_id)) throw new Unavailable("missing_run_id");
            result.source_paths=Inputs;
            result.source_sha256_before=Inputs.Select(p=>Hash(Path.Combine(root,p))).ToArray();
            CheckEnvironment();
            ShaderUtil.allowAsyncCompilation=false;
            var sa=LoadShader(ShaderA); var sb=LoadShader(ShaderB);
            var ta=Import(PngA,result); var tb=Import(PngB,result);
            var ma=CreateMaterial(MatA,sa,ta,TintA,ScaleA,OffsetA);
            var mb=CreateMaterial(MatB,sb,tb,TintB,ScaleB,OffsetB);
            var mesh=CreateMesh(MeshPath,false); var decoy=CreateMesh(DecoyPath,true);
            AssetDatabase.SaveAssets();
            ma=AssetDatabase.LoadAssetAtPath<Material>(MatA);
            mb=AssetDatabase.LoadAssetAtPath<Material>(MatB);
            mesh=AssetDatabase.LoadAssetAtPath<Mesh>(MeshPath);
            decoy=AssetDatabase.LoadAssetAtPath<Mesh>(DecoyPath);
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            target=Own(new RenderTexture(Width,Height,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear),owned);
            target.antiAliasing=1;target.useMipMap=false;target.autoGenerateMips=false;target.filterMode=FilterMode.Point;
            if (!target.Create() || target.sRGB || target.graphicsFormat!=GraphicsFormat.R32G32B32A32_SFloat)
                throw new Unavailable("exact_linear_float_render_target_unavailable");
            var readback=Own(new Texture2D(Width,Height,TextureFormat.RGBAFloat,false,true),owned);
            var co=Own(new GameObject("Authored camera"),owned);
            var camera=co.AddComponent<Camera>();
            camera.enabled=false;camera.transform.position=new Vector3(0,0,-2);
            camera.orthographic=true;camera.orthographicSize=1;camera.aspect=(float)Width/Height;
            camera.nearClipPlane=.1f;camera.farClipPlane=10;camera.clearFlags=CameraClearFlags.Nothing;
            camera.renderingPath=RenderingPath.Forward;camera.allowMSAA=false;camera.allowHDR=true;
            camera.allowDynamicResolution=false;camera.useOcclusionCulling=false;camera.targetTexture=target;
            var go=Own(new GameObject("Authored asymmetric submeshes"),owned);
            var filter=go.AddComponent<MeshFilter>();
            var renderer=go.AddComponent<MeshRenderer>();
            renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;
            void Baseline()
            {
                filter.sharedMesh=mesh;
                renderer.sharedMaterials=new[]{ma,mb};
                Configure(ma,sa,ta,TintA,ScaleA,OffsetA);
                Configure(mb,sb,tb,TintB,ScaleB,OffsetB);
            }
            void Draw(string name) { Capture(name,filter,renderer,camera,target,readback,result); }
            Baseline();Draw("baseline");
            Baseline();renderer.sharedMaterials=new[]{mb,ma};Draw("swapped_materials");
            Baseline();filter.sharedMesh=decoy;Draw("reversed_mesh_routes");
            Baseline();ma.SetTexture("_MainTex",tb);Draw("wrong_valid_texture");
            Baseline();ma.SetTexture("_MainTex",Texture2D.whiteTexture);Draw("white_texture");
            Baseline();ma.SetTexture("_MainTex",null);Draw("missing_texture");
            Baseline();ma.SetTextureOffset("_MainTex",new Vector2(.41f,.07f));Draw("UV_transform_drift");
            Baseline();Configure(ma,sb,ta,TintA,ScaleA,OffsetA);Draw("wrong_valid_shader");
            Baseline();ma.SetColor("_Tint",Color.white);Draw("tint_drift");
            Baseline();Draw("restored_baseline");
            if (ShaderUtil.ShaderHasError(sa)||ShaderUtil.ShaderHasError(sb))
                throw new InvalidOperationException("shader_compile_error_after_render");
            result.source_sha256_after=Inputs.Select(p=>Hash(Path.Combine(root,p))).ToArray();
            if (!result.source_sha256_before.SequenceEqual(result.source_sha256_after))
                throw new InvalidOperationException("authored_input_changed");
            result.status="OBSERVED";result.reason="ten_cases_captured_independent_oracle_required";code=0;
        }
        catch (Unavailable e) {result.status="NOT_RUN";result.reason=e.Message;}
        catch (Exception e) {result.status="FAIL";result.reason=e.GetType().Name+": "+e.Message;}
        finally {
            RenderTexture.active=previous;GL.sRGBWrite=srgb;ShaderUtil.allowAsyncCompilation=async;
            if(target!=null)target.Release();
            for(int i=owned.Count-1;i>=0;--i)if(owned[i]!=null)UnityEngine.Object.DestroyImmediate(owned[i]);
        }
        try {
            if(output==null)throw new IOException("outside_project_report_path_required");
            File.WriteAllText(output,JsonUtility.ToJson(result,true)+"\n");
            Debug.Log("RAFT_SUBMESH_ROUTE "+result.status+" "+result.reason);
        } catch(Exception e){Debug.LogError(e.Message);code=2;}
        EditorApplication.Exit(code);
    }

    static Shader LoadShader(string path)
    {
        AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);
        var shader=AssetDatabase.LoadAssetAtPath<Shader>(path);
        if(shader==null||!shader.isSupported||ShaderUtil.ShaderHasError(shader))
            throw new InvalidOperationException("authored_shader_unavailable");
        return shader;
    }

    static Texture2D Import(string path,Receipt result)
    {
        var importer=AssetImporter.GetAtPath(path) as TextureImporter;
        if(importer==null)throw new InvalidOperationException("actual_texture_importer_required");
        importer.textureType=TextureImporterType.Default;importer.textureShape=TextureImporterShape.Texture2D;
        importer.alphaSource=TextureImporterAlphaSource.FromInput;importer.alphaIsTransparency=false;
        importer.sRGBTexture=false;importer.isReadable=true;importer.mipmapEnabled=false;
        importer.npotScale=TextureImporterNPOTScale.None;importer.textureCompression=TextureImporterCompression.Uncompressed;
        importer.crunchedCompression=false;importer.maxTextureSize=32;
        importer.filterMode=FilterMode.Point;importer.wrapMode=TextureWrapMode.Clamp;importer.anisoLevel=0;
        importer.SaveAndReimport();
        var t=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        if(t==null||t.width!=4||t.height!=2||!t.isReadable||t.mipmapCount!=1)
            throw new InvalidOperationException("actual_imported_texture_unavailable");
        result.imported.Add(new Imported{
            path=AssetDatabase.GetAssetPath(t),guid=AssetDatabase.AssetPathToGUID(path),
            format=t.format.ToString(),graphics_format=t.graphicsFormat.ToString(),filter=t.filterMode.ToString(),
            wrap=t.wrapMode.ToString(),shape=importer.textureShape.ToString(),alpha_source=importer.alphaSource.ToString(),
            compression=importer.textureCompression.ToString(),srgb=importer.sRGBTexture,
            graphics_srgb=GraphicsFormatUtility.IsSRGBFormat(t.graphicsFormat),readable=t.isReadable,
            mipmaps=importer.mipmapEnabled,width=t.width,height=t.height,mip_count=t.mipmapCount,
            rgba8=t.GetPixels32().SelectMany(c=>new[]{(int)c.r,(int)c.g,(int)c.b,(int)c.a}).ToArray()
        });
        return t;
    }
    static void Configure(Material mat,Shader shader,Texture texture,Color tint,Vector2 scale,Vector2 offset)
    {
        mat.shader=shader;
        mat.SetTexture("_MainTex",texture);mat.SetColor("_Tint",tint);
        mat.SetTextureScale("_MainTex",scale);mat.SetTextureOffset("_MainTex",offset);
    }
    static Material CreateMaterial(string path,Shader shader,Texture texture,Color tint,Vector2 scale,Vector2 offset)
    {
        var m=new Material(shader);Configure(m,shader,texture,tint,scale,offset);
        AssetDatabase.CreateAsset(m,path);
        return m;
    }
    static Mesh CreateMesh(string path,bool reverse)
    {
        var m=new Mesh();
        m.vertices=new[]{new Vector3(-2,-1,0),new Vector3(-.5f,-1,0),new Vector3(-.5f,1,0),new Vector3(-2,1,0),
                         new Vector3(-.5f,-1,0),new Vector3(2,-1,0),new Vector3(2,1,0),new Vector3(-.5f,1,0)};
        m.uv=new[]{new Vector2(0,0),new Vector2(1,0),new Vector2(1,1),new Vector2(0,1),
                   new Vector2(1,0),new Vector2(0,0),new Vector2(0,1),new Vector2(1,1)};
        m.subMeshCount=2;
        int[] indices={0,1,2,0,2,3};
        m.SetIndices(indices,MeshTopology.Triangles,0,false,reverse?4:0);
        m.SetIndices(indices,MeshTopology.Triangles,1,false,reverse?0:4);
        m.RecalculateBounds();
        AssetDatabase.CreateAsset(m,path);
        return m;
    }
    static Binding ReadBinding(Material m)
    {
        string path=AssetDatabase.GetAssetPath(m);
        Texture t=m.GetTexture("_MainTex");
        string tp=t==null?"null":t==Texture2D.whiteTexture?"explicit_white":AssetDatabase.GetAssetPath(t);
        Vector2 scale=m.GetTextureScale("_MainTex"),offset=m.GetTextureOffset("_MainTex");
        return new Binding{material=path,material_guid=AssetDatabase.AssetPathToGUID(path),
            material_instance=m.GetInstanceID(),shader=AssetDatabase.GetAssetPath(m.shader),
            texture=tp,texture_guid=t==null||t==Texture2D.whiteTexture?"":AssetDatabase.AssetPathToGUID(tp),
            tint=Channels(m.GetColor("_Tint")),scale=new[]{scale.x,scale.y},offset=new[]{offset.x,offset.y}};
    }
    static void Capture(string name,MeshFilter filter,MeshRenderer renderer,Camera camera,RenderTexture target,Texture2D readback,Receipt result)
    {
        var mesh=filter.sharedMesh;var mats=renderer.sharedMaterials;
        if(mesh==null||mats.Length!=2||mesh.subMeshCount!=2||mesh.vertexCount!=8)
            throw new InvalidOperationException("actual_renderer_submesh_route_unavailable");
        string path=AssetDatabase.GetAssetPath(mesh);
        var row=new Case{name=name,mesh=path,mesh_guid=AssetDatabase.AssetPathToGUID(path),
            mesh_instance=mesh.GetInstanceID(),submesh_count=mesh.subMeshCount,vertex_count=mesh.vertexCount,
            base_vertices=new[]{(int)mesh.GetBaseVertex(0),(int)mesh.GetBaseVertex(1)},
            indices0=mesh.GetIndices(0,true),indices1=mesh.GetIndices(1,true),
            vertices=mesh.vertices.SelectMany(v=>new[]{v.x,v.y,v.z}).ToArray(),
            uv0=mesh.uv.SelectMany(v=>new[]{v.x,v.y}).ToArray(),
            slots=mats.Select(ReadBinding).ToArray()};
        RenderTexture.active=target;GL.sRGBWrite=false;GL.Clear(false,true,Background);
        camera.Render();RenderTexture.active=target;
        readback.ReadPixels(new Rect(0,0,Width,Height),0,0,false);
        Color[] pixels=readback.GetPixels();
        if(pixels.Length!=Width*Height)throw new InvalidOperationException("actual_pixel_count_mismatch");
        row.checked_pixel_count=pixels.Length;
        row.pixels=pixels.Select((c,i)=>new Sample{x=i%Width,y=i/Width,observed=Channels(c)}).ToArray();
        result.Unity_render_executed=true;result.cases.Add(row);
    }

    static void CheckEnvironment()
    {
        if (!Application.isBatchMode) throw new Unavailable("dedicated_batchmode_project_required");
        if (Application.unityVersion != "2021.3.45f2") throw new Unavailable("exact_Unity_2021_3_45f2_required");
        if (SystemInfo.graphicsDeviceType != GraphicsDeviceType.Vulkan) throw new Unavailable("real_Vulkan_backend_required");
        if (QualitySettings.activeColorSpace != ColorSpace.Linear) throw new Unavailable("active_linear_color_space_required");
        if (GraphicsSettings.currentRenderPipeline != null) throw new Unavailable("built_in_render_pipeline_required");
        if (!SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat)
            || !SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat)
            || !SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat, FormatUsage.Render)
            || !SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat, FormatUsage.Blend)
            || !SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat, FormatUsage.Sample))
            throw new Unavailable("float_texture_and_render_support_required");
    }

    static float[] Channels(Color color) { return new[] { color.r, color.g, color.b, color.a }; }
    static T Own<T>(T value, List<UnityEngine.Object> owned) where T : UnityEngine.Object
    { owned.Add(value); return value; }
    static string Hash(string path)
    {
        using (var hash = SHA256.Create())
        using (var stream = File.OpenRead(path))
            return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }
    static string OutsideProjectReport(string root)
    {
        string path = Option("RAFT_SUBMESH_ROUTE_REPORT", "-raftSubmeshRouteReport");
        if (String.IsNullOrWhiteSpace(path) || !Path.IsPathRooted(path))
            throw new Unavailable("absolute_report_path_required");
        path = Path.GetFullPath(path);
        string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        StringComparison comparison = Path.DirectorySeparatorChar == '\\' ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        if (path.StartsWith(prefix, comparison) || String.Equals(path, root, comparison))
            throw new Unavailable("report_must_be_outside_project");
        return path;
    }
    static string Option(string environment, string argument)
    {
        string value = Environment.GetEnvironmentVariable(environment);
        if (!String.IsNullOrWhiteSpace(value)) return value;
        string[] args = Environment.GetCommandLineArgs();
        for (int i = 0; i + 1 < args.Length; ++i)
            if (args[i] == argument) return args[i + 1];
        return null;
    }
}
#endif
