// Isolated actual imported original array. No original material or shader draw.
// All editor output and full texel receipts remain runner-private.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

public static class SelectedArrayUnity {
 [Serializable] public class Input { public string run_id,asset_path,guid,asset_sha256,meta_sha256; public long file_id; }
 [Serializable] public class Receipt {
   public string status="INCONCLUSIVE",phase="environment",run_id,unity_version,backend,color_space,guid,texture_format,graphics_format,failure_category;
   public long file_id;
   public int width,height,depth,mip_count,texture_shape;
   public bool texture_importer,srgb,readable,mipmap_enabled,private_log_guard;
 }
 static void Need(bool ok) { if(!ok) throw new InvalidOperationException("GT selected array observation"); }
 static string Arg(string name) { var a=Environment.GetCommandLineArgs(); int i=Array.IndexOf(a,name);return i>=0 && i+1<a.Length?a[i+1]:""; }
 static string Sha(string path) { using(var h=SHA256.Create()) using(var s=File.OpenRead(path)) return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant(); }
 public static void Run() {
   var r=new Receipt{run_id=Arg("-gtArrayRunId"),unity_version=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),color_space=QualitySettings.activeColorSpace.ToString()};
   string privateRoot=Arg("-gtArrayPrivate");int code=2;
   Texture2DArray cal=null;
   try {
     Need(Application.isBatchMode && r.unity_version=="2021.3.45f2" &&
          SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan &&
          QualitySettings.activeColorSpace==ColorSpace.Linear &&
          SystemInfo.supportsComputeShaders && SystemInfo.supports2DArrayTextures);
     r.phase="private_guard";
     Need(!String.IsNullOrEmpty(privateRoot) && File.Exists(Path.Combine(privateRoot,"editor-output-private")) &&
          File.ReadAllText(Path.Combine(privateRoot,"editor-output-private")).Trim()==r.run_id);
     r.private_log_guard=true;
     r.phase="private_stage";
     string root=Directory.GetParent(Application.dataPath).FullName;
     var cfg=JsonUtility.FromJson<Input>(File.ReadAllText(Path.Combine(root,"GTInput.json")));
     Need(cfg!=null && cfg.run_id==r.run_id && cfg.file_id==18700000 &&
          cfg.asset_path.StartsWith("Assets/GTSource/",StringComparison.Ordinal));
     string dst=Path.GetFullPath(Path.Combine(root,cfg.asset_path));
     Need(Path.GetDirectoryName(dst)==Path.Combine(root,"Assets","GTSource") && !File.Exists(dst) && !File.Exists(dst+".meta"));
     string png=Path.Combine(privateRoot,"array.png.bytes"),meta=Path.Combine(privateRoot,"array.meta.bytes");
     Need(Sha(png)==cfg.asset_sha256 && Sha(meta)==cfg.meta_sha256);
     Directory.CreateDirectory(Path.GetDirectoryName(dst));
     File.Copy(png,dst,false);File.Copy(meta,dst+".meta",false);
     r.phase="refresh";
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     var tex=AssetDatabase.LoadAssetAtPath<Texture2DArray>(cfg.asset_path);
     Need(tex!=null);
     r.phase="identity";
     Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(tex,out string guid,out long id));
     r.guid=guid;r.file_id=id;Need(guid==cfg.guid && id==cfg.file_id);
     var importer=AssetImporter.GetAtPath(cfg.asset_path) as TextureImporter;
     r.texture_importer=importer!=null;Need(importer!=null);
     r.texture_shape=(int)importer.textureShape;
     r.phase="descriptor";
     r.width=tex.width;r.height=tex.height;r.depth=tex.depth;r.mip_count=tex.mipmapCount;
     r.texture_format=tex.format.ToString();r.graphics_format=tex.graphicsFormat.ToString();
     r.srgb=GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat);
     r.readable=tex.isReadable;r.mipmap_enabled=importer.mipmapEnabled;
     Need(r.texture_shape==4 && r.width==1024 && r.height==1024 && r.depth==2);
     r.phase="compute";
     var cs=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/GTSelectedArray.compute");Need(cs!=null);
     Read(cs,tex,Path.Combine(privateRoot,"top.f32"));
     r.phase="calibration";
     cal=new Texture2DArray(4,4,2,TextureFormat.RGBA32,false,true);
     for(int l=0;l<2;l++) {
       var c=new Color32[16];
       for(int y=0;y<4;y++) for(int x=0;x<4;x++)
         c[y*4+x]=new Color32((byte)(13+70*l+11*x+3*y),(byte)(21+20*l+5*x+9*y),
                             (byte)(31+50*l+2*x+7*y),(byte)(41+30*l+9*x+13*y));
       cal.SetPixels32(c,l,0);
     }
     cal.Apply(false,false);
     Read(cs,cal,Path.Combine(privateRoot,"calibration.f32"));
     r.phase="complete";r.status="OBSERVED";code=0;
   } catch(Exception e) {r.failure_category=e.GetType().Name;}
   finally {
     if(cal!=null) UnityEngine.Object.DestroyImmediate(cal);
     if(r.private_log_guard) File.WriteAllText(Path.Combine(privateRoot,"receipt.json"),JsonUtility.ToJson(r));
     EditorApplication.Exit(code);
   }
 }
 static void Read(ComputeShader cs,Texture2DArray tex,string output) {
   int w=tex.width,h=tex.height,d=tex.depth,count=checked(w*h*d);
   int kernel=cs.FindKernel("ReadArray");
   using(var buf=new ComputeBuffer(count,16)) {
     cs.SetInt("_Width",w);cs.SetInt("_Height",h);cs.SetInt("_Depth",d);
     cs.SetTexture(kernel,"_Source",tex);cs.SetBuffer(kernel,"_Result",buf);
     cs.Dispatch(kernel,(w+7)/8,(h+7)/8,d);
     var values=new Vector4[count];buf.GetData(values);
     using(var stream=new FileStream(output,FileMode.CreateNew,FileAccess.Write))
     using(var writer=new BinaryWriter(stream)) {
       foreach(var v in values){writer.Write(v.x);writer.Write(v.y);writer.Write(v.z);writer.Write(v.w);}
     }
   }
 }
}
#endif
