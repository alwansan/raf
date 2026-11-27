using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Experimental.Rendering;
using Id=SyntheticNormalRouteValidation.Id;
using Manifest=SyntheticNormalRouteValidation.Manifest;
using Route=SyntheticNormalRouteValidation.Route;
using SeenRoute=SyntheticNormalRouteValidation.SeenRoute;

public static class SyntheticNormalExporterReimport
{
    [Serializable] public class Mip { public int level,width,height; public string rgba_hex; public float max_unorm_error; }
    [Serializable] public class Imported {
        public Id identity;
        public bool alpha_transparency,readable,streaming,srgb,mipmap,runtime_readable,runtime_streaming;
        public int type,shape,filter,aniso,wrap_u,wrap_v,wrap_w,priority,max_size,npot,alpha_source,compression_quality,normal_filter,platform_format,platform_compression;
        public bool convert_normal,platform_override,graphics_srgb;
        public float bias,height_scale;
        public int width,height,mip_count,runtime_filter,runtime_aniso,runtime_wrap_u,runtime_wrap_v,runtime_wrap_w;
        public float runtime_bias;
        public string format,graphics_format,cpu_top_rgba_hex,cpu_status;
        public Mip[] mips;
    }
    [Serializable] public class Phase { public string name; public SeenRoute[] routes; public Imported[] textures; }
    [Serializable] public class Receipt {
        public string status,run_id,editor,backend,active_color_space,route_manifest_sha256,error;
        public bool original_assets_read,scene_route_replay,shader_adapter,exact_exporter_meta_unchanged,unfiltered_compute_load;
        public Phase[] phases;
    }
    static void Need(bool ok,string why) { if(!ok)throw new InvalidOperationException(why); }
    static string Hash(byte[] b) { using(var h=SHA256.Create())return string.Concat(h.ComputeHash(b).Select(x=>x.ToString("x2"))); }
    static string Root(string p) { return Path.Combine(Directory.GetParent(Application.dataPath).FullName,p); }
    static string Arg(string key) {var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,key);Need(i>=0&&i+1<a.Length,"missing_argument");return a[i+1];}
    static Id Identity(UnityEngine.Object o) {
        Need(o!=null,"null_route_asset");string g;long f;
        Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(o,out g,out f),"asset_identity_missing");
        string p=AssetDatabase.GetAssetPath(o);
        return new Id{path=p,guid=g,file_id=f,sha256=Hash(File.ReadAllBytes(Root(p))),meta_sha256=Hash(File.ReadAllBytes(Root(p+".meta")))};
    }
    static void Match(Id a,Id b,bool meta=true) {
        Need(a.path==b.path && a.guid==b.guid && a.file_id==b.file_id && a.sha256==b.sha256 && (!meta || a.meta_sha256==b.meta_sha256),"same_route_identity_drift");
    }
    static T Load<T>(Id id,bool meta=true) where T:UnityEngine.Object {
        var o=AssetDatabase.LoadAssetAtPath<T>(id.path);Match(Identity(o),id,meta);return o;
    }
    static void Reimport(string path) { AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate); }
    static string Bytes(Color32[] colors) {return string.Concat(colors.Select(c=>c.r.ToString("x2")+c.g.ToString("x2")+c.b.ToString("x2")+c.a.ToString("x2")));}
    static Mip ReadMip(Texture2D tex,ComputeShader shader,int n) {
        int w=Math.Max(1,tex.width>>n),h=Math.Max(1,tex.height>>n);
        var rows=new Vector4[w*h];
        var buffer=new ComputeBuffer(rows.Length,16,ComputeBufferType.Structured);
        try {
            int k=shader.FindKernel("ReadTexels");
            shader.SetTexture(k,"InputTexture",tex);shader.SetBuffer(k,"OutputTexels",buffer);
            shader.SetInt("Width",w);shader.SetInt("Height",h);shader.SetInt("Mip",n);
            shader.Dispatch(k,(w+7)/8,(h+7)/8,1);
            buffer.GetData(rows);
            var hex=new System.Text.StringBuilder();float maximum=0;
            foreach(var v in rows)for(int i=0;i<4;i++) {
                float f=v[i];Need(!float.IsNaN(f)&&!float.IsInfinity(f)&&f>=0&&f<=1,"invalid_exact_texel_load");
                int b=Mathf.RoundToInt(f*255f);float error=Mathf.Abs(f-b/255f);
                maximum=Math.Max(maximum,error);Need(error<=0.000001f,"actual_texel_not_UNorm8");
                hex.Append(b.ToString("x2"));
            }
            return new Mip{level=n,width=w,height=h,rgba_hex=hex.ToString(),max_unorm_error=maximum};
        } finally {buffer.Release();}
    }
    static Imported Observe(Texture2D tex,ComputeShader shader,bool alpha) {
        Id id=Identity(tex);var imp=AssetImporter.GetAtPath(id.path) as TextureImporter;
        Need(imp!=null && imp.alphaIsTransparency==alpha,"actual_alpha_policy_required");
        var s=new TextureImporterSettings();imp.ReadTextureSettings(s);var p=imp.GetDefaultPlatformTextureSettings();
        var o=new Imported{identity=id,alpha_transparency=imp.alphaIsTransparency,readable=s.readable,streaming=s.streamingMipmaps,srgb=s.sRGBTexture,mipmap=s.mipmapEnabled,
            type=(int)s.textureType,shape=(int)s.textureShape,filter=(int)s.filterMode,aniso=s.aniso,wrap_u=(int)s.wrapModeU,wrap_v=(int)s.wrapModeV,wrap_w=(int)s.wrapModeW,
            priority=s.streamingMipmapsPriority,max_size=imp.maxTextureSize,npot=(int)s.npotScale,alpha_source=(int)imp.alphaSource,compression_quality=imp.compressionQuality,
            normal_filter=(int)s.normalMapFilter,platform_format=(int)p.format,platform_compression=(int)p.textureCompression,convert_normal=s.convertToNormalMap,
            platform_override=p.overridden,bias=s.mipmapBias,height_scale=s.heightmapScale,width=tex.width,height=tex.height,mip_count=tex.mipmapCount,
            runtime_readable=tex.isReadable,runtime_streaming=tex.streamingMipmaps,graphics_srgb=GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat),
            runtime_filter=(int)tex.filterMode,runtime_aniso=tex.anisoLevel,runtime_wrap_u=(int)tex.wrapModeU,runtime_wrap_v=(int)tex.wrapModeV,runtime_wrap_w=(int)tex.wrapModeW,runtime_bias=tex.mipMapBias,
            format=tex.format.ToString(),graphics_format=tex.graphicsFormat.ToString(),cpu_top_rgba_hex="",cpu_status="not_readable_as_imported"};
        Need(tex.width>0&&tex.width<=32&&tex.height>0&&tex.height<=32&&tex.mipmapCount>0&&tex.mipmapCount<=6,"bounded_fixture");
        Need(tex.format==TextureFormat.RGBA32 && tex.graphicsFormat==GraphicsFormat.R8G8B8A8_UNorm,"V13_observed_UNorm8_format_required");
        if(tex.isReadable) {o.cpu_top_rgba_hex=Bytes(tex.GetPixels32(0));o.cpu_status="cpu_GetPixels32_observed";}
        o.mips=Enumerable.Range(0,tex.mipmapCount).Select(n=>ReadMip(tex,shader,n)).ToArray();return o;
    }
    static Phase ObservePhase(string name,Manifest m,ComputeShader shader,bool alpha) {
        var seen=new List<SeenRoute>();var textures=new Dictionary<string,Texture2D>();
        foreach(var route in m.routes) {
            var mesh=Load<Mesh>(route.mesh);var materials=route.materials.Select(x=>Load<Material>(x)).ToArray();
            var go=new GameObject("Authored route replay "+route.key);
            try {
                var filter=go.AddComponent<MeshFilter>();filter.sharedMesh=mesh;
                var renderer=go.AddComponent<MeshRenderer>();renderer.sharedMaterials=materials;
                var actual=renderer.sharedMaterials;Need(actual.Length==2&&mesh.subMeshCount==2,"route_submesh_count");
                var ids=new List<Id>();var texIds=new List<Id>();var shaderIds=new List<Id>();var uv=new List<float>();
                for(int i=0;i<2;i++) {
                    var mat=actual[i];Need(mat!=null&&mat.HasProperty("_MainTex")&&mat.shader!=null&&!ShaderUtil.ShaderHasError(mat.shader),"route_material_shader");
                    var tid=Identity(mat.GetTexture("_MainTex"));Match(tid,route.textures[i]);
                    var mid=Identity(mat);Match(mid,route.materials[i]);
                    var sid=Identity(mat.shader);Match(sid,route.shaders[i]);
                    textures[tid.guid]=(Texture2D)mat.GetTexture("_MainTex");
                    ids.Add(mid);texIds.Add(tid);shaderIds.Add(sid);
                    var scale=mat.GetTextureScale("_MainTex");var offset=mat.GetTextureOffset("_MainTex");uv.AddRange(new[]{scale.x,scale.y,offset.x,offset.y});
                }
                seen.Add(new SeenRoute{key=route.key,mesh=Identity(filter.sharedMesh),materials=ids.ToArray(),textures=texIds.ToArray(),shaders=shaderIds.ToArray(),
                    vertex_count=mesh.vertexCount,index_counts=Enumerable.Range(0,2).Select(i=>(int)mesh.GetIndexCount(i)).ToArray(),
                    base_vertices=Enumerable.Range(0,2).Select(i=>(int)mesh.GetBaseVertex(i)).ToArray(),uv=uv.ToArray()});
            } finally {UnityEngine.Object.DestroyImmediate(go);}
        }
        Need(textures.Count==2,"two_actual_textures");
        return new Phase{name=name,routes=seen.ToArray(),textures=m.textures.Select(x=>Observe(textures[x.guid],shader,alpha)).ToArray()};
    }
    public static void Run() {
        var report=new Receipt{status="INCONCLUSIVE",editor=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),
            active_color_space=QualitySettings.activeColorSpace.ToString(),shader_adapter=true,scene_route_replay=true,unfiltered_compute_load=true};
        string output=Arg("-gtNormalReport");int exit=2;
        var phases=new List<Phase>();
        try {
            report.run_id=Arg("-gtNormalRunId");
            var raw=File.ReadAllBytes(Root("gt-normal-route-manifest.json"));
            report.route_manifest_sha256=Hash(raw);
            var m=JsonUtility.FromJson<Manifest>(System.Text.Encoding.UTF8.GetString(raw));
            Need(m.run_id==report.run_id && m.routes.Length==2 && m.textures.Length==2,"manifest_binding");
            Need(report.editor=="2021.3.45f2"&&report.backend=="Vulkan"&&report.active_color_space=="Linear"&&SystemInfo.supportsComputeShaders,"exact_licensed_Unity_compute_scope");
            // Never write an importer field or metadata. Reimport the actual
            // exporter-created PNG/meta pair, preserving the current GUID.
            foreach(var t in m.textures) {
                Need(Hash(File.ReadAllBytes(Root(t.path)))==t.sha256 && Hash(File.ReadAllBytes(Root(t.path+".meta")))==t.meta_sha256,"exported_candidate_bytes_drift_before_import");
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach(var t in m.textures) Reimport(t.path);
            var shader=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/GTNormalProbe/NormalTexelLoad.compute");Need(shader!=null,"compute_shader_missing");
            phases.Add(ObservePhase("exporter_candidate",m,shader,false));
            report.exact_exporter_meta_unchanged=m.textures.All(t=>Hash(File.ReadAllBytes(Root(t.path+".meta")))==t.meta_sha256);
            Need(report.exact_exporter_meta_unchanged,"exporter_meta_drift_after_import");
            report.status="OBSERVED_AUTHORED_DIRECT_EXPORTER_REIMPORT";exit=0;
        } catch(Exception e) {report.error=e.GetType().Name+":"+e.Message;Debug.LogError(report.error);}
        finally {report.phases=phases.ToArray();File.WriteAllText(output,JsonUtility.ToJson(report,true));}
        EditorApplication.Exit(exit);
    }
}
