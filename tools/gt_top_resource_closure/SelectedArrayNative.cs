// Runner-private native class187 BC3 array observation, not a game render.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

public static class SelectedArrayUnity {
 [Serializable] public class Input {
   public string run_id,asset_path,guid,native_payload_sha256,calibration_sha256,source_name;
   public long file_id;
   public int native_payload_bytes,source_ref_type,native_mip_ranges,source_graphics_format;
 }
 [Serializable] public class Receipt {
   public string status="INCONCLUSIVE",phase="environment",run_id,unity_version,backend,color_space,guid,failure_category;
   public long file_id;
   public int width,height,depth,mip_count,graphics_format;
   public bool private_log_guard,native_importer,srgb,name_matches,reference_probe,wrong_reference_rejected;
 }
 static void Need(bool ok) { if(!ok) throw new InvalidOperationException("GT native array observation"); }
 static string Arg(string name) { var a=Environment.GetCommandLineArgs(); int i=Array.IndexOf(a,name);return i>=0&&i+1<a.Length?a[i+1]:""; }
 static string Sha(byte[] raw) { using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(raw)).Replace("-","").ToLowerInvariant(); }
 static int MipBytes(int w,int h,int m) { return checked(((Math.Max(1,w>>m)+3)/4)*((Math.Max(1,h>>m)+3)/4)*16); }
 static Texture2DArray Make(byte[] raw,int w,int h,int d,int n,string name) {
   var tex=new Texture2DArray(w,h,d,TextureFormat.DXT5,true,false);
   Need(tex.mipmapCount==n && (int)tex.graphicsFormat==100 && tex.isReadable);
   tex.name=name;
   int cursor=0;
   for(int l=0;l<d;l++) for(int m=0;m<n;m++) {
     int size=MipBytes(w,h,m);
     Need(cursor+size<=raw.Length && tex.GetPixelData<byte>(m,l).Length==size);
     tex.SetPixelData(raw,m,l,cursor);cursor+=size;
   }
   Need(cursor==raw.Length);
   tex.Apply(false,false); // no regeneration, no discard of CPU BC3 bytes
   return tex;
 }
 static void Raw(Texture2DArray tex,string output) {
   using(var stream=new FileStream(output,FileMode.CreateNew,FileAccess.Write)) {
     for(int l=0;l<tex.depth;l++) for(int m=0;m<tex.mipmapCount;m++) {
       var data=tex.GetPixelData<byte>(m,l);
       Need(data.Length==MipBytes(tex.width,tex.height,m));
       stream.Write(data.ToArray(),0,data.Length);
     }
   }
 }
 static void Read(ComputeShader cs,Texture2DArray tex,int mip,string output) {
   int w=Math.Max(1,tex.width>>mip),h=Math.Max(1,tex.height>>mip),d=tex.depth,count=checked(w*h*d);
   int kernel=cs.FindKernel("ReadArray");
   using(var buf=new ComputeBuffer(count,16)) {
     cs.SetInt("_Width",w);cs.SetInt("_Height",h);cs.SetInt("_Depth",d);cs.SetInt("_Mip",mip);
     cs.SetTexture(kernel,"_Source",tex);cs.SetBuffer(kernel,"_Result",buf);
     cs.Dispatch(kernel,(w+7)/8,(h+7)/8,d);
     var values=new Vector4[count];buf.GetData(values);
     using(var stream=new FileStream(output,FileMode.CreateNew,FileAccess.Write))
     using(var writer=new BinaryWriter(stream)) foreach(var v in values) {writer.Write(v.x);writer.Write(v.y);writer.Write(v.z);writer.Write(v.w);}
   }
 }
 static bool Match(UnityEngine.Object obj,Input cfg) {
   return obj!=null && AssetDatabase.TryGetGUIDAndLocalFileIdentifier(obj,out string g,out long id)&&g==cfg.guid&&id==cfg.file_id;
 }
 static void ProbeReference(Texture2DArray tex,Input cfg,Receipt r,string root) {
   const string rel="Assets/GTArrayRef.mat";
   var shader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTArrayReference.shader");
   Need(shader!=null);
   var mat=new Material(shader);
   Need(mat.HasProperty("_GTArray"));
   mat.SetTexture("_GTArray",tex);
   AssetDatabase.CreateAsset(mat,rel);AssetDatabase.SaveAssets();
   AssetDatabase.ForceReserializeAssets(new[]{rel});
   string path=Path.Combine(root,rel),text=File.ReadAllText(path);
   var rx=new Regex(@"m_Texture: \{fileID: 18700000, guid: "+cfg.guid+@", type: ([23])\}");
   var hits=rx.Matches(text);Need(hits.Count==1);
   string exact=rx.Replace(text,"m_Texture: {fileID: 18700000, guid: "+cfg.guid+", type: "+cfg.source_ref_type+"}");
   File.WriteAllText(path,exact);
   AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
   var loaded=AssetDatabase.LoadAssetAtPath<Material>(rel);
   bool positive=loaded!=null && Match(loaded.GetTexture("_GTArray"),cfg) &&
     File.ReadAllText(path).Contains("guid: "+cfg.guid+", type: "+cfg.source_ref_type+"}");
   string wrongGuid=cfg.guid==new string('a',32)?new string('b',32):new string('a',32);
   Need(String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(wrongGuid)));
   File.WriteAllText(path,exact.Replace("guid: "+cfg.guid+", type:", "guid: "+wrongGuid+", type:"));
   AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
   loaded=AssetDatabase.LoadAssetAtPath<Material>(rel);
   r.wrong_reference_rejected=loaded!=null&&!Match(loaded.GetTexture("_GTArray"),cfg);
   File.WriteAllText(path,exact);
   AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
   loaded=AssetDatabase.LoadAssetAtPath<Material>(rel);
   r.reference_probe=positive&&r.wrong_reference_rejected&&loaded!=null&&Match(loaded.GetTexture("_GTArray"),cfg);
 }
 public static void Run() {
   var r=new Receipt{run_id=Arg("-gtArrayRunId"),unity_version=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),color_space=QualitySettings.activeColorSpace.ToString()};
   string privateRoot=Arg("-gtArrayPrivate");int code=2;
   Texture2DArray cal=null;
   try {
     Need(Application.isBatchMode&&r.unity_version=="2021.3.45f2"&&SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan&&
          QualitySettings.activeColorSpace==ColorSpace.Linear&&SystemInfo.supportsComputeShaders&&SystemInfo.supports2DArrayTextures&&SystemInfo.SupportsTextureFormat(TextureFormat.DXT5));
     r.phase="private_guard";
     Need(!String.IsNullOrEmpty(privateRoot)&&File.Exists(Path.Combine(privateRoot,"editor-output-private"))&&
          File.ReadAllText(Path.Combine(privateRoot,"editor-output-private")).Trim()==r.run_id);
     r.private_log_guard=true;r.phase="source";
     string root=Directory.GetParent(Application.dataPath).FullName;
     var cfg=JsonUtility.FromJson<Input>(File.ReadAllText(Path.Combine(root,"GTInput.json")));
     Need(cfg!=null&&cfg.run_id==r.run_id&&cfg.file_id==18700000&&cfg.source_graphics_format==100&&
          cfg.native_mip_ranges==22&&(cfg.source_ref_type==2||cfg.source_ref_type==3)&&
          Regex.IsMatch(cfg.guid,"^[0-9a-f]{32}$")&&cfg.asset_path.StartsWith("Assets/GTSource/",StringComparison.Ordinal));
     string dst=Path.GetFullPath(Path.Combine(root,cfg.asset_path));
     Need(Path.GetDirectoryName(dst)==Path.Combine(root,"Assets","GTSource")&&Path.GetExtension(dst)==".asset"&&!File.Exists(dst)&&!File.Exists(dst+".meta"));
     Need(String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(cfg.guid)));
     byte[] raw=File.ReadAllBytes(Path.Combine(privateRoot,"array.bc3.bytes"));
     Need(raw.Length==2796256&&raw.Length==cfg.native_payload_bytes&&Sha(raw)==cfg.native_payload_sha256);
     var tex=Make(raw,1024,1024,2,11,cfg.source_name);
     r.phase="save";
     // Generate Unity's actual native file and importer metadata at a disposable
     // path. Only transfer the serialized asset and exact GUID substitution.
     EditorSettings.serializationMode=SerializationMode.ForceText;
     const string scratch="Assets/GTNativeScratch";
     Directory.CreateDirectory(Path.Combine(root,scratch));
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     string temp=scratch+"/"+Path.GetFileName(dst);
     AssetDatabase.CreateAsset(tex,temp);AssetDatabase.SaveAssets();
     Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(tex,out string tempGuid,out long tempID)&&tempID==cfg.file_id);
     string tmp=Path.Combine(root,temp);
     byte[] serialized=File.ReadAllBytes(tmp);
     string meta=File.ReadAllText(tmp+".meta");
     Need(Directory.GetFiles(Path.Combine(root,scratch)).Length==2&&meta.Contains("NativeFormatImporter:"));
     var guidRx=new Regex(@"(?m)^guid: "+tempGuid+"\r?$");
     Need(guidRx.Matches(meta).Count==1);
     string destMeta=guidRx.Replace(meta,"guid: "+cfg.guid);
     Need(AssetDatabase.DeleteAsset(temp));
     Directory.CreateDirectory(Path.GetDirectoryName(dst));
     File.WriteAllBytes(dst,serialized);File.WriteAllText(dst+".meta",destMeta);
     r.phase="reload";
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     AssetDatabase.ImportAsset(cfg.asset_path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
     tex=AssetDatabase.LoadAssetAtPath<Texture2DArray>(cfg.asset_path);
     Need(Match(tex,cfg));
     Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(tex,out string guid,out long id));
     r.guid=guid;r.file_id=id;r.native_importer=AssetImporter.GetAtPath(cfg.asset_path)?.GetType().Name=="NativeFormatImporter";
     r.name_matches=tex.name==cfg.source_name;r.width=tex.width;r.height=tex.height;r.depth=tex.depth;r.mip_count=tex.mipmapCount;
     r.graphics_format=(int)tex.graphicsFormat;r.srgb=GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat);
     Need(r.native_importer&&r.name_matches&&r.width==1024&&r.height==1024&&r.depth==2&&r.mip_count==11&&r.graphics_format==100&&r.srgb&&tex.isReadable);
     r.phase="raw";Raw(tex,Path.Combine(privateRoot,"native-readback.bc3.bytes"));
     r.phase="gpu";
     var cs=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/GTSelectedArray.compute");Need(cs!=null);
     for(int m=0;m<11;m++) Read(cs,tex,m,Path.Combine(privateRoot,"mip-"+m+".f32"));
     r.phase="calibration";
     byte[] authored=File.ReadAllBytes(Path.Combine(privateRoot,"authored.bc3.bytes"));
     Need(Sha(authored)==cfg.calibration_sha256);
     cal=Make(authored,8,8,2,4,"Authored BC3 calibration");
     for(int m=0;m<4;m++) Read(cs,cal,m,Path.Combine(privateRoot,"cal-"+m+".f32"));
     r.phase="reference";
     try {ProbeReference(tex,cfg,r,root);} catch(Exception) {r.reference_probe=false;}
     r.phase="complete";r.status="OBSERVED";code=0;
   } catch(Exception e) {r.failure_category=e.GetType().Name;}
   finally {
     if(cal!=null) UnityEngine.Object.DestroyImmediate(cal);
     if(r.private_log_guard) File.WriteAllText(Path.Combine(privateRoot,"receipt.json"),JsonUtility.ToJson(r));
     EditorApplication.Exit(code);
   }
 }
}
#endif
