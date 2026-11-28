// Isolated original native asset import plus authored Vulkan alpha adapter.
// Never writes original data, raw receipt is private and never uploaded.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

public static class NativeMipValidation {
 [Serializable] public class Input { public string run_id,asset_path,guid; public long file_id; }
 [Serializable] public class Mip {
   public int level,size,cpu_bytes;
   public string cpu_sha256;
   public float[] alpha;
 }
 [Serializable] public class Receipt {
   public string status="INCONCLUSIVE",phase="start",run_id,unity_version,backend,device,color_space,
     guid,texture_format,graphics_format,failure_category;
   public long file_id;
   public int width,height,mip_count,filter_mode,aniso,wrap_u,wrap_v,wrap_w;
   public float mip_bias;
   public bool native_importer,readable,srgb;
   public List<Mip> mips=new List<Mip>();
   public float[] force_zero,force_one;
 }
 static void Need(bool x) { if(!x) throw new InvalidOperationException("GT native mip gate"); }
 static string Arg(string name) { var a=Environment.GetCommandLineArgs(); int i=Array.IndexOf(a,name); return i>=0 && i+1<a.Length?a[i+1]:""; }
 static string Sha(byte[] data) { using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(data)).Replace("-","").ToLowerInvariant(); }
 public static void Run() {
   var r=new Receipt {unity_version=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),
     device=SystemInfo.graphicsDeviceName,color_space=QualitySettings.activeColorSpace.ToString(),run_id=Arg("-gtNativeRunId")};
   string output=Arg("-gtNativeReport"); int code=2;
   var owned=new List<UnityEngine.Object>(); bool async=ShaderUtil.allowAsyncCompilation,srgb=GL.sRGBWrite;
   var old=RenderTexture.active;
   try {
     r.phase="environment";
     Need(Application.isBatchMode && r.unity_version=="2021.3.45f2" &&
       SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan &&
       QualitySettings.activeColorSpace==ColorSpace.Linear && GraphicsSettings.currentRenderPipeline==null);
     Need(SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat) &&
       SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat,FormatUsage.Render) &&
       SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat,FormatUsage.Blend));
     r.phase="import";
     Input input=JsonUtility.FromJson<Input>(File.ReadAllText(Path.Combine(Directory.GetParent(Application.dataPath).FullName,"GTInput.json")));
     Need(input!=null && input.run_id==r.run_id);
     ShaderUtil.allowAsyncCompilation=false;
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(input.asset_path); Need(tex!=null);
     Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(tex,out string guid,out long local));
     r.guid=guid;r.file_id=local;
     var importer=AssetImporter.GetAtPath(input.asset_path);
     r.native_importer=importer!=null && importer.GetType().FullName=="UnityEditor.NativeFormatImporter";
     r.width=tex.width;r.height=tex.height;r.mip_count=tex.mipmapCount;r.texture_format=tex.format.ToString();
     r.graphics_format=tex.graphicsFormat.ToString();r.srgb=GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat);
     r.readable=tex.isReadable;r.filter_mode=(int)tex.filterMode;r.aniso=tex.anisoLevel;r.mip_bias=tex.mipMapBias;
     r.wrap_u=(int)tex.wrapModeU;r.wrap_v=(int)tex.wrapModeV;r.wrap_w=(int)tex.wrapModeW;
     Need(guid==input.guid && local==input.file_id && r.native_importer &&
       tex.width==64 && tex.height==64 && tex.mipmapCount==7 && tex.format==TextureFormat.RGBA32);
     r.phase="adapter";
     Shader shader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTNativeMipAlpha.shader");
     Need(shader!=null && shader.isSupported && !ShaderUtil.ShaderHasError(shader));
     EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
     var mat=new Material(shader);owned.Add(mat);mat.SetTexture("_MainTex",tex);
     Need(mat.GetTexture("_MainTex")==tex);
     var go=new GameObject("GT diagnostic camera");owned.Add(go);
     var cam=go.AddComponent<Camera>();cam.enabled=false;cam.transform.position=new Vector3(0,0,-2);
     cam.orthographic=true;cam.orthographicSize=1;cam.aspect=1;cam.nearClipPlane=.1f;cam.farClipPlane=10;
     cam.clearFlags=CameraClearFlags.Nothing;cam.renderingPath=RenderingPath.Forward;
     cam.allowMSAA=false;cam.allowHDR=true;cam.useOcclusionCulling=false;
     var quad=new GameObject("GT diagnostic quad");owned.Add(quad);
     var mesh=new Mesh();owned.Add(mesh);
     mesh.vertices=new[]{new Vector3(-1,-1,0),new Vector3(1,-1,0),new Vector3(1,1,0),new Vector3(-1,1,0)};
     mesh.uv=new[]{new Vector2(0,0),new Vector2(1,0),new Vector2(1,1),new Vector2(0,1)};
     mesh.triangles=new[]{0,1,2,0,2,3};mesh.RecalculateBounds();
     quad.AddComponent<MeshFilter>().sharedMesh=mesh;
     var renderer=quad.AddComponent<MeshRenderer>();renderer.shadowCastingMode=ShadowCastingMode.Off;
     renderer.receiveShadows=false;renderer.sharedMaterial=mat;
     r.phase="all_mips";
     for(int i=0;i<7;i++) {
       int size=64>>i;var m=new Mip{level=i,size=size};
       // Do not toggle readability, compression, color space, or sampler on the imported asset.
       if(tex.isReadable) { var bytes=tex.GetPixelData<byte>(i).ToArray();m.cpu_bytes=bytes.Length;m.cpu_sha256=Sha(bytes); }
       m.alpha=Render(cam,renderer,mat,tex,i,size,-1);
       r.mips.Add(m);
     }
     r.phase="controls";
     r.force_zero=Render(cam,renderer,mat,tex,6,1,0);
     r.force_one=Render(cam,renderer,mat,tex,6,1,1);
     Need(!ShaderUtil.ShaderHasError(shader));
     r.status="OBSERVED";r.phase="complete";code=0;
   } catch(Exception e) {r.failure_category=e.GetType().Name;}
   finally {
     RenderTexture.active=old;GL.sRGBWrite=srgb;ShaderUtil.allowAsyncCompilation=async;
     for(int i=owned.Count-1;i>=0;i--) if(owned[i]!=null) UnityEngine.Object.DestroyImmediate(owned[i]);
   }
   try {Need(!String.IsNullOrEmpty(output));File.WriteAllText(output,JsonUtility.ToJson(r,true)+"\n");
     Debug.Log("GT_NATIVE_MIP_EDITOR "+r.status+" "+r.phase);}
   catch {code=2;}
   EditorApplication.Exit(code);
 }
 static float[] Render(Camera cam,MeshRenderer renderer,Material mat,Texture2D tex,int level,int size,float force) {
   Need(renderer.sharedMaterial==mat && mat.GetTexture("_MainTex")==tex);
   mat.SetFloat("_GTLod",level);mat.SetFloat("_GTForce",force);
   var rt=new RenderTexture(size,size,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
   var read=new Texture2D(size,size,TextureFormat.RGBAFloat,false,true);
   try {
     rt.antiAliasing=1;rt.useMipMap=false;rt.autoGenerateMips=false;rt.filterMode=FilterMode.Point;
     Need(rt.Create() && !rt.sRGB && rt.graphicsFormat==GraphicsFormat.R32G32B32A32_SFloat);
     cam.targetTexture=rt;cam.aspect=1;
     RenderTexture.active=rt;GL.sRGBWrite=false;GL.Clear(false,true,new Color(.125f,.25f,.5f,.25f));
     cam.Render();RenderTexture.active=rt;read.ReadPixels(new Rect(0,0,size,size),0,0,false);
     var colors=read.GetPixels();Need(colors.Length==size*size);
     return colors.Select(c=>c.a).ToArray();
   } finally {cam.targetTexture=null;RenderTexture.active=null;rt.Release();
     UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(read);}
 }
}
#endif
