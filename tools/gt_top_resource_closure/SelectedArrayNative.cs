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
   public string material_property,reference_shader_guid,reference_wrong_guid,material_shader_hash;
   public string[] material_variant_hashes;
 }
 [Serializable] public class Receipt {
   public string status="INCONCLUSIVE",phase="environment",run_id,unity_version,backend,color_space,guid,failure_category;
   public long file_id;
   public int width,height,depth,mip_count,graphics_format;
   public bool private_log_guard,native_importer,srgb,name_matches,reference_probe,wrong_reference_rejected;
   public bool presave_raw_written,presave_gpu_written,calibration_written,authored_reload_raw_written,authored_reload_gpu_written;
   public Transfer original_transfer=new Transfer(),authored_transfer=new Transfer();
   public RefCase[] selected_material_cases;
   public bool unorm_raw_written,unorm_gpu_written;
 }
 [Serializable] public class RefCase { public string name; public bool material_loaded,shader_matches,has_property,serialized_texture_matches,runtime_texture_matches,source_yaml_unchanged; public string failure_category=""; }
 [Serializable] public class Transfer {
   public string phase="not_started",failure_category="";
   public bool scratch_id_matches,scratch_name_matches,meta_guid_anchor,meta_written,
       path_guid_matches,guid_path_matches,loaded_array,object_guid_matches,object_id_matches,
       native_meta,importer_reports_native,name_matches,dimensions_match,mips_match,format_matches,srgb,readable,
       serialized_bytes_unchanged,accepted;
 }
 static void Need(bool ok) { if(!ok) throw new InvalidOperationException("GT native array observation"); }
 static string Arg(string name) { var a=Environment.GetCommandLineArgs(); int i=Array.IndexOf(a,name);return i>=0&&i+1<a.Length?a[i+1]:""; }
 static string Sha(byte[] raw) { using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(raw)).Replace("-","").ToLowerInvariant(); }
 static int MipBytes(int w,int h,int m) { return checked(((Math.Max(1,w>>m)+3)/4)*((Math.Max(1,h>>m)+3)/4)*16); }
 static Texture2DArray Make(byte[] raw,int w,int h,int d,int n,string name,bool linear=false) {
   var tex=new Texture2DArray(w,h,d,TextureFormat.DXT5,true,linear);
   Need(tex.mipmapCount==n && (int)tex.graphicsFormat==(linear?101:100) && tex.isReadable);
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
 static void SelectedMaterialReferences(Input cfg,Receipt r,string root,string privateRoot) {
   string[] names={"type3","type2","wrong_guid","wrong_fileid"};
   r.selected_material_cases=new RefCase[4];
   for(int i=0;i<4;i++) r.selected_material_cases[i]=new RefCase{name=names[i]};
   Need(cfg.material_variant_hashes!=null&&cfg.material_variant_hashes.Length==4&&Regex.IsMatch(cfg.material_property,"^[A-Za-z_][A-Za-z0-9_]{0,127}$"));
   Need(Regex.IsMatch(cfg.reference_shader_guid,"^[0-9a-f]{32}$")&&Regex.IsMatch(cfg.reference_wrong_guid,"^[0-9a-f]{32}$"));
   Need(String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(cfg.reference_shader_guid))&&String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(cfg.reference_wrong_guid)));
   const string folder="Assets/GTReferenceDifferential";
   Directory.CreateDirectory(Path.Combine(root,folder));
   string shaderRel=folder+"/probe.shader",shaderPath=Path.Combine(root,shaderRel);
   byte[] shaderBytes=File.ReadAllBytes(Path.Combine(privateRoot,"material-probe-shader.bytes"));
   Need(Sha(shaderBytes)==cfg.material_shader_hash);
   File.WriteAllBytes(shaderPath,shaderBytes);
   File.WriteAllText(shaderPath+".meta","fileFormatVersion: 2\nguid: "+cfg.reference_shader_guid+"\nShaderImporter:\n  externalObjects: {}\n  defaultTextures: []\n  nonModifiableTextures: []\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n");
   AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   var shader=AssetDatabase.LoadAssetAtPath<Shader>(shaderRel);
   Need(shader!=null&&AssetDatabase.TryGetGUIDAndLocalFileIdentifier(shader,out string sg,out long si)&&sg==cfg.reference_shader_guid&&si==4800000);
   for(int i=0;i<4;i++) {
     var row=r.selected_material_cases[i];
     try {
       string rel=folder+"/"+names[i]+".mat",path=Path.Combine(root,rel);
       byte[] raw=File.ReadAllBytes(Path.Combine(privateRoot,"material-"+names[i]+".bytes"));
       Need(Sha(raw)==cfg.material_variant_hashes[i]&&!File.Exists(path));
       File.WriteAllBytes(path,raw);
       AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
       var loaded=AssetDatabase.LoadAssetAtPath<Material>(rel);
       row.material_loaded=loaded!=null;
       row.source_yaml_unchanged=Sha(File.ReadAllBytes(path))==Sha(raw);
       if(loaded==null) continue;
       row.shader_matches=loaded.shader==shader;
       row.has_property=loaded.HasProperty(cfg.material_property);
       if(row.has_property) row.runtime_texture_matches=Match(loaded.GetTexture(cfg.material_property),cfg);
       var so=new SerializedObject(loaded);
       var entries=so.FindProperty("m_SavedProperties.m_TexEnvs");
       if(entries!=null&&entries.isArray) {
         int count=0;
         for(int e=0;e<entries.arraySize;e++){
           var entry=entries.GetArrayElementAtIndex(e);
           var name=entry.FindPropertyRelative("first");
           var ptr=entry.FindPropertyRelative("second.m_Texture");
           if(name!=null&&ptr!=null&&name.propertyType==SerializedPropertyType.String&&name.stringValue==cfg.material_property){
             count++;row.serialized_texture_matches=Match(ptr.objectReferenceValue,cfg);
           }
         }
         if(count!=1) row.serialized_texture_matches=false;
       }
     } catch(Exception e){row.failure_category=e.GetType().Name;}
   }
 }
 static Texture2DArray TransferNative(Texture2DArray tex,string root,string scratch,string target,string guid,long fileID,
     string name,int w,int h,int d,int n,Transfer t) {
   try {
     t.phase="scratch_create";
     Need(String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(guid)));
     string src=Path.Combine(root,scratch),dst=Path.Combine(root,target);
     Need(!File.Exists(src)&&!File.Exists(src+".meta")&&!File.Exists(dst)&&!File.Exists(dst+".meta"));
     AssetDatabase.CreateAsset(tex,scratch);
     // CreateAsset may change the object name to its filename; restore the exact
     // source name on the persistent object before writing and verify after reload.
     tex.name=name;EditorUtility.SetDirty(tex);AssetDatabase.SaveAssets();
     AssetDatabase.ForceReserializeAssets(new[]{scratch});
     t.phase="scratch_identity";
     Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(tex,out string generated,out long generatedId));
     t.scratch_id_matches=generatedId==fileID;t.scratch_name_matches=tex.name==name;
     Need(t.scratch_id_matches&&t.scratch_name_matches&&generated!=guid);
     byte[] asset=File.ReadAllBytes(src);
     string meta=File.ReadAllText(src+".meta");
     var rx=new Regex(@"(?m)^guid: "+generated+@"\r?$");
     t.meta_guid_anchor=rx.Matches(meta).Count==1&&meta.Contains("NativeFormatImporter:");
     Need(t.meta_guid_anchor);
     t.phase="target_write";
     string patched=rx.Replace(meta,"guid: "+guid);
     File.WriteAllBytes(dst,asset);File.WriteAllText(dst+".meta",patched);
     t.meta_written=File.ReadAllText(dst+".meta")==patched;
     Need(t.meta_written);
     t.phase="target_import";
     AssetDatabase.ImportAsset(target,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     t.phase="target_identity";
     t.path_guid_matches=AssetDatabase.AssetPathToGUID(target)==guid;
     t.guid_path_matches=AssetDatabase.GUIDToAssetPath(guid)==target;
     var loaded=AssetDatabase.LoadAssetAtPath<Texture2DArray>(target);
     t.loaded_array=loaded!=null;
     if(loaded!=null&&AssetDatabase.TryGetGUIDAndLocalFileIdentifier(loaded,out string g,out long id)) {
       t.object_guid_matches=g==guid;t.object_id_matches=id==fileID;
     }
     // The file's actual NativeFormatImporter declaration is authoritative for
     // native serialization; record the editor API importer type independently.
     string importedMeta=File.ReadAllText(dst+".meta");
     t.native_meta=importedMeta.Contains("NativeFormatImporter:")&&
       new Regex(@"(?m)^guid: "+guid+@"\r?$").Matches(importedMeta).Count==1;
     t.importer_reports_native=AssetImporter.GetAtPath(target)?.GetType().Name=="NativeFormatImporter";
     t.serialized_bytes_unchanged=Sha(File.ReadAllBytes(dst))==Sha(asset);
     t.phase="target_descriptor";
     if(loaded!=null) {
       t.name_matches=loaded.name==name;t.dimensions_match=loaded.width==w&&loaded.height==h&&loaded.depth==d;
       t.mips_match=loaded.mipmapCount==n;t.format_matches=(int)loaded.graphicsFormat==100;
       t.srgb=GraphicsFormatUtility.IsSRGBFormat(loaded.graphicsFormat);t.readable=loaded.isReadable;
     }
     t.accepted=t.path_guid_matches&&t.guid_path_matches&&t.loaded_array&&t.object_guid_matches&&t.object_id_matches&&
         t.native_meta&&t.name_matches&&t.dimensions_match&&t.mips_match&&t.format_matches&&t.srgb&&t.readable&&t.serialized_bytes_unchanged;
     t.phase=t.accepted?"complete":"target_rejected";
     return t.accepted?loaded:null;
   } catch(Exception e) { t.failure_category=e.GetType().Name;return null; }
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
     // Separate fresh native upload from serialization/reload. Keep both observations
     // in the private runner even if an identity assertion later fails.
     var cs=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/GTSelectedArray.compute");Need(cs!=null);
     byte[] authored=File.ReadAllBytes(Path.Combine(privateRoot,"authored.bc3.bytes"));
     Need(Sha(authored)==cfg.calibration_sha256);
     r.phase="calibration";
     cal=Make(authored,8,8,2,4,"GT authored BC3 calibration");
     for(int m=0;m<4;m++) Read(cs,cal,m,Path.Combine(privateRoot,"cal-"+m+".f32"));
     r.calibration_written=true;
     r.phase="presave";
     var tex=Make(raw,1024,1024,2,11,cfg.source_name);
     Raw(tex,Path.Combine(privateRoot,"presave.bc3.bytes"));r.presave_raw_written=true;
     for(int m=0;m<11;m++) Read(cs,tex,m,Path.Combine(privateRoot,"pre-mip-"+m+".f32"));
     r.presave_gpu_written=true;
     EditorSettings.serializationMode=SerializationMode.ForceText;
     const string scratch="Assets/GTNativeScratch";
     Directory.CreateDirectory(Path.Combine(root,scratch));
     Directory.CreateDirectory(Path.Combine(root,"Assets","GTSource"));
     Directory.CreateDirectory(Path.Combine(root,"Assets","GTAuthored"));
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     // Independent authored transfer: source name intentionally differs from both
     // filenames. Do not select an identity or orientation using original pixels.
     r.phase="authored_transfer";
     string ag=Guid.NewGuid().ToString("N");
     var authoredAsset=TransferNative(cal,root,scratch+"/authored-input.asset","Assets/GTAuthored/authored-reload.asset",
         ag,18700000,"GT authored BC3 calibration",8,8,2,4,r.authored_transfer);
     // CreateAsset owns cal once it is persistent; do not DestroyImmediate it.
     if(AssetDatabase.Contains(cal)) cal=null;
     if(authoredAsset!=null) {
       try {
         Raw(authoredAsset,Path.Combine(privateRoot,"authored-reload.bc3.bytes"));r.authored_reload_raw_written=true;
         for(int m=0;m<4;m++) Read(cs,authoredAsset,m,Path.Combine(privateRoot,"authored-reload-"+m+".f32"));
         r.authored_reload_gpu_written=true;
       } catch(Exception e) {r.authored_transfer.failure_category=e.GetType().Name;}
     }
     r.phase="original_transfer";
     // Keep the scratch asset alive with a distinct path and GUID during import;
     // this avoids deleting/recreating it under the same basename in one refresh.
     tex=TransferNative(tex,root,scratch+"/original-input.asset",cfg.asset_path,cfg.guid,cfg.file_id,
          cfg.source_name,1024,1024,2,11,r.original_transfer);
     if(tex==null) throw new InvalidOperationException("GT native transfer failed");
     Need(AssetDatabase.TryGetGUIDAndLocalFileIdentifier(tex,out string guid,out long id));
     r.guid=guid;r.file_id=id;r.native_importer=r.original_transfer.native_meta;
     r.name_matches=tex.name==cfg.source_name;r.width=tex.width;r.height=tex.height;r.depth=tex.depth;r.mip_count=tex.mipmapCount;
     r.graphics_format=(int)tex.graphicsFormat;r.srgb=GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat);
     r.phase="raw";Raw(tex,Path.Combine(privateRoot,"native-readback.bc3.bytes"));
     r.phase="gpu";
     for(int m=0;m<11;m++) Read(cs,tex,m,Path.Combine(privateRoot,"mip-"+m+".f32"));
     r.phase="reference";
     try {ProbeReference(tex,cfg,r,root);} catch(Exception) {r.reference_probe=false;}
     try {SelectedMaterialReferences(cfg,r,root,privateRoot);} catch(Exception) {}
     r.phase="unorm_differential";
     Texture2DArray linear=null;
     try {
       linear=Make(raw,1024,1024,2,11,"GT BC3 UNorm control",true);
       Raw(linear,Path.Combine(privateRoot,"unorm.bc3.bytes"));r.unorm_raw_written=true;
       for(int m=0;m<11;m++) Read(cs,linear,m,Path.Combine(privateRoot,"unorm-"+m+".f32"));
       r.unorm_gpu_written=true;
     } catch(Exception) {} finally {if(linear!=null) UnityEngine.Object.DestroyImmediate(linear);}
     r.phase="complete";r.status="OBSERVED";code=0;
   } catch(Exception e) {r.failure_category=e.GetType().Name;}
   finally {
     if(cal!=null&&!AssetDatabase.Contains(cal)) UnityEngine.Object.DestroyImmediate(cal);
     if(r.private_log_guard) File.WriteAllText(Path.Combine(privateRoot,"receipt.json"),JsonUtility.ToJson(r));
     EditorApplication.Exit(code);
   }
 }
}
#endif
