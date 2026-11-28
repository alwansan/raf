// Authored-only import and actual raster probe. No game source, device or build.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

public static class PreservedTextureAlphaValidation {
    const string ShaderPath = "Assets/GT_PreservedTextureAlpha.shader";
    static readonly Color BG = new Color(.125f,.25f,.5f,.25f);
    [Serializable] public class Input {
        public string run_id, archive_sha256;
        public Row[] rows;
    }
    [Serializable] public class Row {
        public int path_id,width,height;
        public string material_path,material_guid,texture_path,texture_guid;
        public long material_file_id,texture_file_id;
        public float[] scale,offset;
        public int[] rgba;
    }
    [Serializable] public class Observation {
        public int path_id,width,height,mip_count;
        public string phase,meta_sha256;
        public string material_guid,texture_guid,shader_guid,texture_format,graphics_format,
            alpha_source,compression,filter_mode;
        public long material_file_id,texture_file_id;
        public bool readable,srgb,alpha_is_transparency;
        public float[] scale,offset;
        public int[] imported_rgba8;
    }
    [Serializable] public class Draw {
        public string name,material_guid,bound_texture_guid,filter_mode;
        public int width,height;
        public float[] rgba;
    }
    [Serializable] public class Receipt {
        public string run_id,archive_sha256,status="NOT_RUN",reason="not_started",
            unity_version,backend,device,color_space;
        public List<Observation> imported=new List<Observation>();
        public List<Draw> draws=new List<Draw>();
        public bool authored_only=true,original_assets_read=false,Android_device=false,
            production=false,XAPK=false;
    }
    static void Need(bool b,string why) { if(!b) throw new InvalidOperationException(why); }
    static string Arg(string name) {
        var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,name);
        return i>=0 && i+1<a.Length ? a[i+1] : "";
    }
    static float[] V(Vector2 v)=>new[]{v.x,v.y};
    static string Guid(UnityEngine.Object o) {
        Need(o!=null,"null asset");
        Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(o,out string g,out long id),"asset identity");
        return g;
    }
    public static void Run() {
        var r=new Receipt {unity_version=Application.unityVersion,
          backend=SystemInfo.graphicsDeviceType.ToString(),device=SystemInfo.graphicsDeviceName,
          color_space=QualitySettings.activeColorSpace.ToString(),run_id=Arg("-gtPreservedRunId")};
        string output=Arg("-gtPreservedReport");
        int code=2; bool async=ShaderUtil.allowAsyncCompilation;
        bool srgb=GL.sRGBWrite; var old=RenderTexture.active;
        var owned=new List<UnityEngine.Object>();
        try {
            Need(Application.isBatchMode && Application.unityVersion=="2021.3.45f2","exact batch editor required");
            Need(SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan,"Vulkan unavailable");
            Need(QualitySettings.activeColorSpace==ColorSpace.Linear && GraphicsSettings.currentRenderPipeline==null,"linear built-in pipeline required");
            Need(SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat) &&
              SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat,FormatUsage.Render) &&
              SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat,FormatUsage.Blend),"float render/blend unavailable");
            string root=Directory.GetParent(Application.dataPath).FullName;
            Input input=JsonUtility.FromJson<Input>(File.ReadAllText(Path.Combine(root,"GTInput.json")));
            Need(input.run_id==r.run_id && input.rows.Length==4,"input run/population");
            r.archive_sha256=input.archive_sha256;
            ShaderUtil.allowAsyncCompilation=false;
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Shader shader=AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
            Need(shader!=null && shader.isSupported && !ShaderUtil.ShaderHasError(shader),"adapter compile");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var cameraObj=new GameObject("GT authored camera");owned.Add(cameraObj);
            var cam=cameraObj.AddComponent<Camera>();cam.enabled=false;
            cam.transform.position=new Vector3(0,0,-2);cam.orthographic=true;cam.orthographicSize=1;
            cam.nearClipPlane=.1f;cam.farClipPlane=10;cam.clearFlags=CameraClearFlags.Nothing;
            cam.renderingPath=RenderingPath.Forward;cam.allowMSAA=false;cam.allowHDR=true;cam.useOcclusionCulling=false;
            var quad=new GameObject("GT authored quad");owned.Add(quad);
            var mesh=new Mesh();owned.Add(mesh);quad.AddComponent<MeshFilter>().sharedMesh=mesh;
            var renderer=quad.AddComponent<MeshRenderer>();renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;
            foreach(string phase in new[]{"baseline","alpha-off"}) {
                if(phase=="alpha-off") {
                    foreach(var row in input.rows) {
                        string path=Path.Combine(root,row.texture_path+".meta");
                        byte[] raw=File.ReadAllBytes(path);
                        string before=Encoding.UTF8.GetString(raw);
                        Need(Encoding.UTF8.GetBytes(before).SequenceEqual(raw),"meta roundtrip");
                        var pattern=new Regex(@"(?m)^([ \t]*alphaIsTransparency:[ \t]*)1([ \t]*\r?)$");
                        Need(pattern.Matches(before).Count==1,"one exact alphaIsTransparency field");
                        string after=pattern.Replace(before,m=>m.Groups[1].Value+"0"+m.Groups[2].Value);
                        File.WriteAllBytes(path,Encoding.UTF8.GetBytes(after));
                    }
                    AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
                    foreach(var row in input.rows)
                        AssetDatabase.ImportAsset(row.texture_path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
                }
                var materials=Capture(input,shader,r,root,phase);
                foreach(var row in input.rows) Render(phase+"-"+row.path_id,row,materials[row.path_id],row.material_guid,
                    cam,renderer,mesh,r);
                Row a=input.rows.Single(x=>x.path_id==821);
                var swapped=new Material(materials[821]);owned.Add(swapped);
                swapped.SetTexture("_MainTex",materials[822].GetTexture("_MainTex"));
                Render(phase+"-swap",a,swapped,a.material_guid,cam,renderer,mesh,r);
                var opaque=new Material(materials[821]);owned.Add(opaque);opaque.SetFloat("_GTForceOpaque",1);
                Render(phase+"-opaque",a,opaque,a.material_guid,cam,renderer,mesh,r);
                renderer.sharedMaterial=null;
            }
            Need(!ShaderUtil.ShaderHasError(shader),"shader error after draw");
            r.status="OBSERVED";r.reason="actual baseline and single importer policy counterfactual, filtered raster cases captured";code=0;
        } catch(Exception e) {r.status="FAIL";r.reason=e.GetType().Name+": "+e.Message;}
        finally {
            RenderTexture.active=old;GL.sRGBWrite=srgb;ShaderUtil.allowAsyncCompilation=async;
            for(int i=owned.Count-1;i>=0;i--) if(owned[i]!=null) UnityEngine.Object.DestroyImmediate(owned[i]);
        }
        try { Need(!String.IsNullOrWhiteSpace(output),"receipt path");File.WriteAllText(output,JsonUtility.ToJson(r,true)+"\n");
            Debug.Log("GT_PRESERVED_ALPHA_OBSERVED "+r.status+" "+r.reason); }
        catch(Exception e) {Debug.LogError(e.Message);code=2;}
        EditorApplication.Exit(code);
    }
    static string Digest(byte[] raw) {
        using(var sha=SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(raw)).Replace("-","").ToLowerInvariant();
    }
    static Dictionary<int,Material> Capture(Input input,Shader shader,Receipt r,string root,string phase) {
        var materials=new Dictionary<int,Material>();
            foreach(var row in input.rows) {
                Material mat=AssetDatabase.LoadAssetAtPath<Material>(row.material_path);
                Texture2D tex=AssetDatabase.LoadAssetAtPath<Texture2D>(row.texture_path);
                Need(mat!=null && tex!=null && mat.shader==shader,"imported actual material/shader");
                Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(mat,out string mg,out long mf) &&
                   mg==row.material_guid && mf==row.material_file_id,"material GUID/fileID");
                Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(tex,out string tg,out long tf) &&
                   tg==row.texture_guid && tf==row.texture_file_id,"texture GUID/fileID");
                // No SetTexture on the four baselines: the imported .mat resolves its own PPtr.
                Need(mat.GetTexture("_MainTex")==tex,"actual imported material texture PPtr");
                Need(mat.GetTextureScale("_MainTex")==new Vector2(row.scale[0],row.scale[1]) &&
                   mat.GetTextureOffset("_MainTex")==new Vector2(row.offset[0],row.offset[1]),"actual imported UV");
                Need(tex.width==row.width && tex.height==row.height && tex.isReadable &&
                   tex.mipmapCount==1 && tex.filterMode==FilterMode.Point,"actual imported texture dimensions/filter/readability");
                var imp=AssetImporter.GetAtPath(row.texture_path) as TextureImporter;
                Need(imp!=null && !imp.sRGBTexture && !GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat),"actual linear importer");
                Need(imp.alphaIsTransparency==(phase=="baseline"),"actual single policy setting");
                r.imported.Add(new Observation {phase=phase,meta_sha256=Digest(File.ReadAllBytes(Path.Combine(root,row.texture_path+".meta"))),path_id=row.path_id,width=tex.width,height=tex.height,
                    mip_count=tex.mipmapCount,material_guid=mg,material_file_id=mf,texture_guid=tg,texture_file_id=tf,
                    shader_guid=Guid(shader),texture_format=tex.format.ToString(),graphics_format=tex.graphicsFormat.ToString(),
                    alpha_source=imp.alphaSource.ToString(),compression=imp.textureCompression.ToString(),
                    filter_mode=tex.filterMode.ToString(),readable=tex.isReadable,srgb=imp.sRGBTexture,
                    alpha_is_transparency=imp.alphaIsTransparency,scale=V(mat.GetTextureScale("_MainTex")),
                    offset=V(mat.GetTextureOffset("_MainTex")),
                    imported_rgba8=tex.GetPixels32().SelectMany(c=>new int[]{c.r,c.g,c.b,c.a}).ToArray()});
                materials.Add(row.path_id,mat);
            }
        return materials;
    }
    static void Render(string name,Row row,Material material,string materialGuid,Camera cam,MeshRenderer renderer,Mesh mesh,Receipt r) {
        int w=2*row.width-1,h=2*row.height-1;
        var tex=material.GetTexture("_MainTex") as Texture2D;
        Need(tex!=null && tex.width==row.width && tex.height==row.height,"draw texture extent");
        FilterMode original=tex.filterMode;
        Need(original==FilterMode.Point,"retained importer filter before draw");
        var rt=new RenderTexture(w,h,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
        var read=new Texture2D(w,h,TextureFormat.RGBAFloat,false,true);
        try {
            rt.antiAliasing=1;rt.useMipMap=false;rt.autoGenerateMips=false;rt.filterMode=FilterMode.Point;
            Need(rt.Create() && !rt.sRGB && rt.graphicsFormat==GraphicsFormat.R32G32B32A32_SFloat,"actual float RT");
            tex.filterMode=FilterMode.Bilinear;
            Need(tex.filterMode==FilterMode.Bilinear,"actual draw filter");
            float aspect=(float)w/h;cam.aspect=aspect;cam.targetTexture=rt;
            mesh.Clear();mesh.vertices=new[]{new Vector3(-aspect,-1,0),new Vector3(aspect,-1,0),
                new Vector3(aspect,1,0),new Vector3(-aspect,1,0)};
            // Inverse of the independently parsed retained UV transform; shader uses actual material _MainTex_ST.
            // Output centers are at every retained texel center and every midpoint.
            float ux=.25f/row.width,vy=.25f/row.height;
            float u0=(ux-row.offset[0])/row.scale[0],u1=(1-ux-row.offset[0])/row.scale[0];
            float v0=(vy-row.offset[1])/row.scale[1],v1=(1-vy-row.offset[1])/row.scale[1];
            mesh.uv=new[]{new Vector2(u0,v0),new Vector2(u1,v0),new Vector2(u1,v1),new Vector2(u0,v1)};
            mesh.triangles=new[]{0,1,2,0,2,3};mesh.RecalculateBounds();
            renderer.sharedMaterial=material;
            Need(renderer.sharedMaterial==material,"actual renderer material");
            RenderTexture.active=rt;GL.sRGBWrite=false;GL.Clear(false,true,BG);cam.Render();
            RenderTexture.active=rt;read.ReadPixels(new Rect(0,0,w,h),0,0,false);
            Color[] colors=read.GetPixels();Need(colors.Length==w*h,"readback size");
            r.draws.Add(new Draw {name=name,material_guid=materialGuid,bound_texture_guid=Guid(renderer.sharedMaterial.GetTexture("_MainTex")),
                width=w,height=h,filter_mode=tex.filterMode.ToString(),rgba=colors.SelectMany(c=>new[]{c.r,c.g,c.b,c.a}).ToArray()});
        } finally {tex.filterMode=original;cam.targetTexture=null;RenderTexture.active=null;rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(read);}
    }
}
#endif
