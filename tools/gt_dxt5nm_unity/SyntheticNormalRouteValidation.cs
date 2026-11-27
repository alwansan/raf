using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Experimental.Rendering;

public static class SyntheticNormalRouteValidation
{
    [Serializable] public class Id { public string path,guid; public long file_id; public string sha256,meta_sha256; }
    [Serializable] public class Route { public string key; public Id mesh; public Id[] materials,textures; public int vertex_count; public int[] index_counts,base_vertices; public float[] uv; }
    [Serializable] public class Manifest { public Id[] textures; public Route[] routes; public string run_id; }
    [Serializable] public class Mip { public int width,height,level; public float[] packed,normal; }
    [Serializable] public class Imported {
        public Id identity;
        public int type,shape,filter,aniso,wrap_u,wrap_v,wrap_w,priority,max_size,npot,alpha_source,compression_quality,normal_filter,platform_format,platform_compression;
        public bool srgb,mipmap,readable,streaming,alpha_transparency,convert_normal,platform_override;
        public float bias,height_scale;
        public int width,height,mip_count,runtime_filter,runtime_aniso,runtime_wrap_u,runtime_wrap_v,runtime_wrap_w;
        public float runtime_bias;
        public bool runtime_readable,runtime_streaming,graphics_srgb;
        public string format,graphics_format,readback_status,cpu_top_rgba_hex;
        public Mip[] mips;
    }
    [Serializable] public class SeenRoute { public string key; public Id mesh; public Id[] materials,textures; public int vertex_count; public int[] index_counts,base_vertices; public float[] uv; }
    [Serializable] public class Receipt {
        public string status,run_id,editor,backend,active_color_space,manifest_sha256,error;
        public Imported[] textures; public SeenRoute[] routes; public bool original_assets_read,shader_adapter,scene_route_replay;
    }
    static void Need(bool ok,string why) { if(!ok) throw new InvalidOperationException(why); }
    static string Hash(string path) { using(var h=SHA256.Create()) return string.Concat(h.ComputeHash(File.ReadAllBytes(path)).Select(b=>b.ToString("x2"))); }
    static string Arg(string key) {
        var a=Environment.GetCommandLineArgs(); int i=Array.IndexOf(a,key);
        Need(i>=0 && i+1<a.Length,"missing_argument"); return a[i+1];
    }
    static string Root(string p) { return Path.Combine(Directory.GetParent(Application.dataPath).FullName,p); }
    static Id Identity(UnityEngine.Object o) {
        Need(o!=null,"null_asset");
        string g; long f;
        Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(o,out g,out f),"missing_imported_asset_identity");
        string p=AssetDatabase.GetAssetPath(o);
        return new Id{path=p,guid=g,file_id=f,sha256=Hash(Root(p)),meta_sha256=Hash(Root(p+".meta"))};
    }
    static T Load<T>(Id id) where T:UnityEngine.Object {
        var o=AssetDatabase.LoadAssetAtPath<T>(id.path);
        var a=Identity(o);
        Need(a.guid==id.guid && a.file_id==id.file_id && a.path==id.path,"asset_identity_drift");
        return o;
    }
    static float[] Floats(Color[] colors) {
        var a=new float[colors.Length*4];for(int i=0;i<colors.Length;i++) {
            a[4*i]=colors[i].r;a[4*i+1]=colors[i].g;a[4*i+2]=colors[i].b;a[4*i+3]=colors[i].a;
        } return a;
    }
    static float[] Sample(Texture2D tex,Material probe,int level,int w,int h,int pass) {
        var rt=new RenderTexture(w,h,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
        var rb=new Texture2D(w,h,TextureFormat.RGBAFloat,false,true);
        var prev=RenderTexture.active; bool prevSrgb=GL.sRGBWrite;
        try {
            Need(rt.Create() && !rt.sRGB,"linear_float_RT_unavailable");
            probe.SetFloat("_Mip",level);GL.sRGBWrite=false;
            Graphics.Blit(tex,rt,probe,pass);
            RenderTexture.active=rt;rb.ReadPixels(new Rect(0,0,w,h),0,0,false);rb.Apply(false,false);
            return Floats(rb.GetPixels());
        } finally { RenderTexture.active=prev;GL.sRGBWrite=prevSrgb;rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(rb); }
    }
    static Imported Observe(Texture2D tex,Material probe) {
        var id=Identity(tex);
        var imp=AssetImporter.GetAtPath(id.path) as TextureImporter;
        Need(imp!=null,"actual_TextureImporter_required");
        var s=new TextureImporterSettings();imp.ReadTextureSettings(s);
        var p=imp.GetDefaultPlatformTextureSettings();
        var row=new Imported {
            identity=id,type=(int)s.textureType,shape=(int)s.textureShape,srgb=s.sRGBTexture,mipmap=s.mipmapEnabled,
            readable=s.readable,streaming=s.streamingMipmaps,priority=s.streamingMipmapsPriority,
            filter=(int)s.filterMode,aniso=s.aniso,bias=s.mipmapBias,wrap_u=(int)s.wrapModeU,wrap_v=(int)s.wrapModeV,wrap_w=(int)s.wrapModeW,
            max_size=imp.maxTextureSize,npot=(int)s.npotScale,alpha_source=(int)imp.alphaSource,alpha_transparency=imp.alphaIsTransparency,
            compression_quality=imp.compressionQuality,convert_normal=s.convertToNormalMap,height_scale=s.heightmapScale,normal_filter=(int)s.normalMapFilter,
            platform_format=(int)p.format,platform_compression=(int)p.textureCompression,platform_override=p.overridden,
            width=tex.width,height=tex.height,mip_count=tex.mipmapCount,format=tex.format.ToString(),graphics_format=tex.graphicsFormat.ToString(),
            runtime_readable=tex.isReadable,runtime_streaming=tex.streamingMipmaps,graphics_srgb=GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat),
            runtime_filter=(int)tex.filterMode,runtime_aniso=tex.anisoLevel,runtime_bias=tex.mipMapBias,
            runtime_wrap_u=(int)tex.wrapModeU,runtime_wrap_v=(int)tex.wrapModeV,runtime_wrap_w=(int)tex.wrapModeW,
            readback_status="not_readable_as_imported",cpu_top_rgba_hex=""
        };
        if(tex.isReadable) {
            try { var colors=tex.GetPixels32(0);row.cpu_top_rgba_hex=string.Concat(colors.Select(c=>c.r.ToString("x2")+c.g.ToString("x2")+c.b.ToString("x2")+c.a.ToString("x2")));row.readback_status="cpu_GetPixels32_observed"; }
            catch(UnityException) {row.readback_status="cpu_GetPixels32_unsupported";}
        }
        Need(tex.width>0 && tex.width<=32 && tex.height>0 && tex.height<=32 && tex.mipmapCount>0 && tex.mipmapCount<=6,"bounded_imported_texture_required");
        row.mips=new Mip[tex.mipmapCount];
        for(int n=0;n<row.mips.Length;n++) {
            int w=Math.Max(1,tex.width>>n),h=Math.Max(1,tex.height>>n);
            row.mips[n]=new Mip{level=n,width=w,height=h,packed=Sample(tex,probe,n,w,h,0),normal=Sample(tex,probe,n,w,h,1)};
        }
        return row;
    }
    public static void Run() {
        var report=new Receipt{status="INCONCLUSIVE",editor=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),
            active_color_space=QualitySettings.activeColorSpace.ToString(),shader_adapter=true,scene_route_replay=true};
        int exit=2;string output=Arg("-gtNormalReport");
        var owned=new List<UnityEngine.Object>();
        try {
            report.run_id=Arg("-gtNormalRunId");string mp=Root("gt-normal-route-manifest.json");
            report.manifest_sha256=Hash(mp);
            var m=JsonUtility.FromJson<Manifest>(File.ReadAllText(mp));
            Need(m.run_id==report.run_id && m.routes.Length==2 && m.textures.Length==2,"fresh_manifest_identity");
            Need(report.editor=="2021.3.45f2" && SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan && QualitySettings.activeColorSpace==ColorSpace.Linear,"exact_editor_vulkan_linear_required");
            Need(SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat) && SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat),"float_readback_required");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var shader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTNormalProbe/NormalRouteProbe.shader");
            Need(shader!=null && shader.isSupported && !ShaderUtil.ShaderHasError(shader),"normal_probe_shader_unavailable");
            var probe=new Material(shader);owned.Add(probe);
            var observed=new List<SeenRoute>();var textures=new Dictionary<string,Texture2D>();
            foreach(var route in m.routes) {
                var mesh=Load<Mesh>(route.mesh);
                var materials=route.materials.Select(Load<Material>).ToArray();
                var go=new GameObject("Authored route replay "+route.key);owned.Add(go);
                var filter=go.AddComponent<MeshFilter>();filter.sharedMesh=mesh;
                var renderer=go.AddComponent<MeshRenderer>();renderer.sharedMaterials=materials;
                var actual=renderer.sharedMaterials;
                Need(actual.Length==mesh.subMeshCount && actual.Length==2,"submesh_material_count");
                var ids=new List<Id>();var texIds=new List<Id>();var uv=new List<float>();
                for(int i=0;i<actual.Length;i++) {
                    Need(actual[i]!=null && actual[i].HasProperty("_MainTex"),"actual_material_MainTex_missing");
                    var tex=actual[i].GetTexture("_MainTex") as Texture2D;
                    var tid=Identity(tex);ids.Add(Identity(actual[i]));texIds.Add(tid);
                    Need(tid.guid==route.textures[i].guid && tid.file_id==route.textures[i].file_id,"material_texture_route_drift");
                    textures[tid.guid]=tex;
                    var scale=actual[i].GetTextureScale("_MainTex");var offset=actual[i].GetTextureOffset("_MainTex");
                    uv.AddRange(new[]{scale.x,scale.y,offset.x,offset.y});
                }
                observed.Add(new SeenRoute{key=route.key,mesh=Identity(filter.sharedMesh),materials=ids.ToArray(),textures=texIds.ToArray(),
                    vertex_count=mesh.vertexCount,index_counts=Enumerable.Range(0,mesh.subMeshCount).Select(i=>(int)mesh.GetIndexCount(i)).ToArray(),
                    base_vertices=Enumerable.Range(0,mesh.subMeshCount).Select(i=>(int)mesh.GetBaseVertex(i)).ToArray(),uv=uv.ToArray()});
            }
            report.routes=observed.ToArray();
            Need(textures.Count==2,"distinct_same_route_texture_population");
            report.textures=m.textures.Select(id=>Observe(textures[id.guid],probe)).ToArray();
            report.status="OBSERVED_AUTHORED_UNITY_REIMPORT";exit=0;
        } catch(Exception e) { report.error=e.GetType().Name+":"+e.Message;Debug.LogError(report.error); }
        finally {
            foreach(var o in owned) if(o!=null) UnityEngine.Object.DestroyImmediate(o);
            File.WriteAllText(output,JsonUtility.ToJson(report,true));
        }
        EditorApplication.Exit(exit);
    }
}
