using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using Id=SyntheticNormalRouteValidation.Id;
using Manifest=SyntheticNormalRouteValidation.Manifest;

public static class SyntheticNormalRasterRoute
{
    const int W=32,H=16;
    const float Shift=.3125f;
    [Serializable] public class Mip { public int level; public float[] packed,normal; }
    [Serializable] public class Slot {
        public int slot,mip_count; public Id material,texture,shader;
        public int[] indices; public float[] uv_transform,uv_pixels,wrong_texture,wrong_uv,restored_packed;
        public bool alpha_transparency; public string format,graphics_format; public Mip[] mips;
    }
    [Serializable] public class Route {
        public string key;public Id mesh;public int vertex_count;public int[] index_counts,base_vertices;
        public float[] positions,uv0;public Slot[] slots;
    }
    [Serializable] public class Receipt {
        public string status,run_id,editor,backend,active_color_space,raster_manifest_sha256,error;
        public int width,height;public bool explicit_fragment_integer_repeat_load,exact_candidate_metadata_unchanged,original_assets_read;
        public Route[] routes;
    }
    static void Need(bool ok,string why){if(!ok)throw new InvalidOperationException(why);}
    static string Hash(byte[] b){using(var h=SHA256.Create())return string.Concat(h.ComputeHash(b).Select(x=>x.ToString("x2")));}
    static string Root(string p){return Path.Combine(Directory.GetParent(Application.dataPath).FullName,p);}
    static string Arg(string k){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,k);Need(i>=0&&i+1<a.Length,"missing_argument:"+k);return a[i+1];}
    static Id Identity(UnityEngine.Object o){
        Need(o!=null,"missing_route_asset");string g;long f;Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(o,out g,out f),"missing_route_identity");
        string p=AssetDatabase.GetAssetPath(o);return new Id{path=p,guid=g,file_id=f,sha256=Hash(File.ReadAllBytes(Root(p))),meta_sha256=Hash(File.ReadAllBytes(Root(p+".meta")))};
    }
    static void Match(Id a,Id b){Need(a.path==b.path&&a.guid==b.guid&&a.file_id==b.file_id&&a.sha256==b.sha256&&a.meta_sha256==b.meta_sha256,"same_route_identity_drift");}
    static T Load<T>(Id id) where T:UnityEngine.Object{var o=AssetDatabase.LoadAssetAtPath<T>(id.path);Match(Identity(o),id);return o;}
    static float[] Draw(Mesh mesh,Material mat,int slot,int pass,int mip,Texture overrideTex=null,Vector4? overrideST=null){
        var rt=new RenderTexture(W,H,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
        var rb=new Texture2D(W,H,TextureFormat.RGBAFloat,false,true);
        var cmd=new CommandBuffer();var previous=RenderTexture.active;bool previousSrgb=GL.sRGBWrite;
        try {
            Need(rt.Create()&&!rt.sRGB,"linear_float_RT_required");GL.sRGBWrite=false;
            var block=new MaterialPropertyBlock();block.SetFloat("_GTProbeMip",mip);
            if(overrideTex!=null)block.SetTexture("_MainTex",overrideTex);
            if(overrideST.HasValue)block.SetVector("_MainTex_ST",overrideST.Value);
            cmd.SetRenderTarget(rt);cmd.SetViewport(new Rect(0,0,W,H));cmd.ClearRenderTarget(false,true,new Color(-4,-4,-4,-4));
            cmd.DrawMesh(mesh,Matrix4x4.identity,mat,slot,pass,block);Graphics.ExecuteCommandBuffer(cmd);
            RenderTexture.active=rt;rb.ReadPixels(new Rect(0,0,W,H),0,0,false);rb.Apply(false,false);
            return rb.GetPixels().SelectMany(c=>new[]{c.r,c.g,c.b,c.a}).ToArray();
        } finally {RenderTexture.active=previous;GL.sRGBWrite=previousSrgb;cmd.Release();rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(rb);}
    }
    public static void Run(){
        int exit=2;string output=Arg("-gtNormalReport");
        var report=new Receipt{status="INCONCLUSIVE",editor=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),active_color_space=QualitySettings.activeColorSpace.ToString(),width=W,height=H,explicit_fragment_integer_repeat_load=true};
        var routes=new List<Route>();
        try {
            report.run_id=Arg("-gtNormalRunId");var raw=File.ReadAllBytes(Root("gt-normal-raster-manifest.json"));report.raster_manifest_sha256=Hash(raw);
            var m=JsonUtility.FromJson<Manifest>(System.Text.Encoding.UTF8.GetString(raw));
            Need(m.run_id==report.run_id&&m.routes.Length==2&&m.textures.Length==2,"fresh_manifest");
            Need(report.editor=="2021.3.45f2"&&report.backend=="Vulkan"&&report.active_color_space=="Linear","licensed_Vulkan_Linear_scope");
            Need(SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat)&&SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat),"float_readback_required");
            foreach(var t in m.textures){
                Need(Hash(File.ReadAllBytes(Root(t.path)))==t.sha256&&Hash(File.ReadAllBytes(Root(t.path+".meta")))==t.meta_sha256,"preimport_candidate_bytes");
                AssetDatabase.ImportAsset(t.path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach(var e in m.routes){
                var mesh=Load<Mesh>(e.mesh);var materials=e.materials.Select(Load<Material>).ToArray();
                var go=new GameObject("Authored V17 "+e.key);
                try {
                    var filter=go.AddComponent<MeshFilter>();filter.sharedMesh=mesh;
                    var renderer=go.AddComponent<MeshRenderer>();renderer.sharedMaterials=materials;
                    var actual=renderer.sharedMaterials;Need(actual.Length==2&&mesh.subMeshCount==2,"actual_submesh_population");
                    var slots=new List<Slot>();
                    for(int i=0;i<2;i++){
                        var mat=actual[i];var tex=mat.GetTexture("_MainTex") as Texture2D;
                        var imp=AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(tex)) as TextureImporter;
                        Need(imp!=null&&!imp.alphaIsTransparency&&mat.shader!=null&&mat.shader.isSupported&&!ShaderUtil.ShaderHasError(mat.shader)&&mat.passCount==3&&mat.HasProperty("_GTProbeMip"),"actual_imported_material_shader_or_policy");
                        var mi=Identity(mat);var ti=Identity(tex);var si=Identity(mat.shader);
                        Match(mi,e.materials[i]);Match(ti,e.textures[i]);Match(si,e.shaders[i]);
                        Need(tex.width==5&&tex.height==7&&tex.mipmapCount==3,"authored_mip_population");
                        var scale=mat.GetTextureScale("_MainTex");var offset=mat.GetTextureOffset("_MainTex");
                        var s=new Slot{slot=i,indices=mesh.GetIndices(i,true),material=mi,texture=ti,shader=si,uv_transform=new[]{scale.x,scale.y,offset.x,offset.y},
                            alpha_transparency=imp.alphaIsTransparency,mip_count=tex.mipmapCount,format=tex.format.ToString(),graphics_format=tex.graphicsFormat.ToString(),
                            uv_pixels=Draw(mesh,mat,i,0,0),mips=Enumerable.Range(0,3).Select(n=>new Mip{level=n,packed=Draw(mesh,mat,i,1,n),normal=Draw(mesh,mat,i,2,n)}).ToArray(),
                            wrong_texture=new float[0],wrong_uv=new float[0],restored_packed=new float[0]};
                        if(e.key=="level1"&&i==0){
                            var other=actual[1].GetTexture("_MainTex");Match(Identity(other),e.textures[1]);
                            s.wrong_texture=Draw(mesh,mat,i,1,0,other);
                            s.wrong_uv=Draw(mesh,mat,i,1,0,null,new Vector4(scale.x,scale.y,offset.x+Shift,offset.y));
                            s.restored_packed=Draw(mesh,mat,i,1,0);
                            Match(Identity(mat),mi);Match(Identity(mat.GetTexture("_MainTex")),ti);
                            Need(mat.GetTextureScale("_MainTex")==scale&&mat.GetTextureOffset("_MainTex")==offset,"in_memory_control_restore");
                        }
                        slots.Add(s);
                    }
                    routes.Add(new Route{key=e.key,mesh=Identity(filter.sharedMesh),vertex_count=mesh.vertexCount,index_counts=Enumerable.Range(0,2).Select(i=>(int)mesh.GetIndexCount(i)).ToArray(),base_vertices=Enumerable.Range(0,2).Select(i=>(int)mesh.GetBaseVertex(i)).ToArray(),
                        positions=mesh.vertices.SelectMany(v=>new[]{v.x,v.y,v.z}).ToArray(),uv0=mesh.uv.SelectMany(v=>new[]{v.x,v.y}).ToArray(),slots=slots.ToArray()});
                }finally{UnityEngine.Object.DestroyImmediate(go);}
            }
            report.exact_candidate_metadata_unchanged=m.textures.All(t=>Hash(File.ReadAllBytes(Root(t.path+".meta")))==t.meta_sha256&&Hash(File.ReadAllBytes(Root(t.path)))==t.sha256);
            Need(report.exact_candidate_metadata_unchanged,"postimport_candidate_bytes");report.status="OBSERVED_AUTHORED_DIRECT_RASTER_ROUTE";exit=0;
        }catch(Exception e){report.error=e.GetType().Name+":"+e.Message;Debug.LogError(report.error);}
        finally{report.routes=routes.ToArray();File.WriteAllText(output,JsonUtility.ToJson(report,true));}
        EditorApplication.Exit(exit);
    }
}
