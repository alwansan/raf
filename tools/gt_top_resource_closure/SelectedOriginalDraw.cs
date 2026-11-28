// Authored diagnostic harness; original programs/assets arrive only under private editor guard.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static partial class SelectedArrayUnity {
 [Serializable] public class DrawAsset { public string path,blob,meta_blob,guid,sha256,meta_sha256; public long file_id; }
 [Serializable] public class DrawSlot { public string name,guid; public long file_id; public int cls; public float[] uv; }
 [Serializable] public class DrawNumber { public string name,kind; public float[] value; }
 [Serializable] public class DrawMaterial { public string name,blob,sha256; }
 [Serializable] public class DrawInput {
   public string run_id,shader_path,shader_guid,mesh_path,mesh_guid,vertex_sha,index_sha,array_guid,array_path,array_name,array_sha,selected_property,wrong_guid;
   public bool tap_available,provider_probe; public string tap_shader_sha; public int tap_expected_properties,tap_source_sample_sites;
   public ProviderRow[] provider_rows;public int provider_transport_version;
   public long mesh_id; public int vertex_count,vertex_bytes,index_bytes,index_format,mesh_stride,views,size;
   public int[] sampler; public float mip_bias;
   public DrawAsset[] assets; public DrawSlot[] slots; public DrawNumber[] numbers; public DrawMaterial[] materials;
 }
 [Serializable] public class DrawReceipt {
   public string run_id,status="INCONCLUSIVE",phase="environment",unity_version,backend,color_space,failure_category="";
   public bool private_log_guard,shader_identity,shader_supported,mesh_identity,mesh_vertex_bytes_match,mesh_index_bytes_match,mesh_descriptor_match,
      array_identity,array_raw_bytes_match,array_sampler_match,material_shader_identity,reference_controls_expected,all_four_nonnull_type2,
      all_six_serialized_UV_type2,all_material_YAML_unchanged;
   public bool authored_array_overrides_bound,tap_shader_compiled,tap_imported,tap_shader_supported,tap_materials_ready;
   public string tap_failure_category="",tap_phase="not_started";
   public int causal_override_views,causal_tap_views,tap_shader_errors=-1,tap_shader_passes;
   public int tap_copied_properties_source,tap_copied_properties_red,tap_copied_properties_green;
   public bool basis_ready; public string basis_phase="not_started",basis_failure_category="";
   public int basis_array_payloads,basis_original_clones,basis_typed_clones,basis_views,basis_site_pairs;
   public int provider_typed_properties,provider_views,provider_observations,provider_class_captures;
   public int shader_errors,shader_passes,source_asset_identities,source_asset_bytes_unchanged,source_asset_meta_bytes_unchanged,
      saved_float_runtime_matches,saved_color_runtime_matches,saved_float_runtime_declared,saved_color_runtime_declared,rendered_views;
 }
 static bool ObjectId(UnityEngine.Object obj,string guid,long id) {
   return obj!=null && AssetDatabase.TryGetGUIDAndLocalFileIdentifier(obj,out string g,out long f)&&g==guid&&f==id;
 }
 static string AssetPath(string root,string rel) {
   Need(rel.StartsWith("Assets/GTDraw/",StringComparison.Ordinal));
   string abs=Path.GetFullPath(Path.Combine(root,rel));
   Need(abs.StartsWith(Path.Combine(root,"Assets","GTDraw")+Path.DirectorySeparatorChar,StringComparison.Ordinal));
   return abs;
 }
 static bool FloatBits(float x,float y) {return BitConverter.ToInt32(BitConverter.GetBytes(x),0)==BitConverter.ToInt32(BitConverter.GetBytes(y),0);}
 static bool UV(Vector2 a,Vector2 b,float[] uv) {
   return uv!=null&&uv.Length==4&&FloatBits(a.x,uv[0])&&FloatBits(a.y,uv[1])&&FloatBits(b.x,uv[2])&&FloatBits(b.y,uv[3]);
 }
 static int ShaderErrors(Shader s) {return ShaderUtil.GetShaderMessages(s).Count(x=>x.severity.ToString()=="Error");}
 static void ImportExact(DrawInput cfg,string root,string priv,DrawReceipt r) {
   Need(cfg.assets!=null&&cfg.assets.Length==5);
   foreach(var asset in cfg.assets) {
     Need(String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(asset.guid)));
     string dst=AssetPath(root,asset.path);
     byte[] raw=File.ReadAllBytes(Path.Combine(priv,asset.blob)),meta=File.ReadAllBytes(Path.Combine(priv,asset.meta_blob));
     Need(Sha(raw)==asset.sha256&&Sha(meta)==asset.meta_sha256&&!File.Exists(dst)&&!File.Exists(dst+".meta"));
     Directory.CreateDirectory(Path.GetDirectoryName(dst));
     File.WriteAllBytes(dst,raw);File.WriteAllBytes(dst+".meta",meta);
   }
   AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   foreach(var asset in cfg.assets) {
     string dst=AssetPath(root,asset.path);
     var obj=AssetDatabase.LoadMainAssetAtPath(asset.path);
     if(ObjectId(obj,asset.guid,asset.file_id))r.source_asset_identities++;
     if(Sha(File.ReadAllBytes(dst))==asset.sha256)r.source_asset_bytes_unchanged++;
     if(File.Exists(dst+".meta")&&Sha(File.ReadAllBytes(dst+".meta"))==asset.meta_sha256)r.source_asset_meta_bytes_unchanged++;
   }
 }
 static bool SerializedSlot(Material mat,DrawSlot slot, bool matchOriginal, out bool uv) {
   uv=false;
   var entries=new SerializedObject(mat).FindProperty("m_SavedProperties.m_TexEnvs");
   if(entries==null||!entries.isArray)return false;
   int count=0;bool match=false;
   for(int i=0;i<entries.arraySize;i++){
     var e=entries.GetArrayElementAtIndex(i);
     var name=e.FindPropertyRelative("first");
     if(name==null||name.stringValue!=slot.name)continue;
     count++;
     var ptr=e.FindPropertyRelative("second.m_Texture");
     var scale=e.FindPropertyRelative("second.m_Scale");
     var offset=e.FindPropertyRelative("second.m_Offset");
     if(ptr!=null)match=matchOriginal?ObjectId(ptr.objectReferenceValue,slot.guid,slot.file_id):ptr.objectReferenceValue==null;
     if(scale!=null&&offset!=null)uv=UV(scale.vector2Value,offset.vector2Value,slot.uv);
   }
   return count==1&&match;
 }
 static Material[] DrawMaterials(DrawInput cfg,string root,string priv,Shader shader,DrawReceipt r) {
   string[] names={"type3","type2","wrong_guid","wrong_fileid"};
   Need(cfg.materials.Length==4&&cfg.slots.Length==6&&String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(cfg.wrong_guid)));
   var mats=new Material[4];r.all_material_YAML_unchanged=true;r.material_shader_identity=true;r.reference_controls_expected=true;
   int correct=0,uvs=0;
   for(int i=0;i<4;i++){
     var item=cfg.materials[i];Need(item.name==names[i]);
     string rel="Assets/GTDraw/Materials/"+names[i]+".mat",path=AssetPath(root,rel);
     byte[] raw=File.ReadAllBytes(Path.Combine(priv,item.blob));Need(Sha(raw)==item.sha256);
     Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,raw);
     AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
     var mat=AssetDatabase.LoadAssetAtPath<Material>(rel);Need(mat!=null);
     mats[i]=mat;r.all_material_YAML_unchanged &= Sha(File.ReadAllBytes(path))==item.sha256;
     r.material_shader_identity &= mat.shader==shader;
     foreach(var slot in cfg.slots){
       bool selected=slot.name==cfg.selected_property,positive=slot.file_id!=0&&(!selected||i==1);
       bool serialized=SerializedSlot(mat,slot,positive,out bool uv);
       bool declared=mat.HasProperty(slot.name);
       bool runtime=declared&&ObjectId(mat.GetTexture(slot.name),slot.guid,slot.file_id);
       if(selected)r.reference_controls_expected &= declared&&serialized&&(runtime==(i==1));
       if(i==1){
         if(slot.file_id!=0&&serialized&&runtime)correct++;
         if(serialized&&uv)uvs++;
       }
     }
   }
   r.all_four_nonnull_type2=correct==4;r.all_six_serialized_UV_type2=uvs==6;
   foreach(var num in cfg.numbers){
     if(!mats[1].HasProperty(num.name))continue;
     if(num.kind=="float"){
       r.saved_float_runtime_declared++;
       if(FloatBits(mats[1].GetFloat(num.name),num.value[0]))r.saved_float_runtime_matches++;
     }else if(num.kind=="color"){
       r.saved_color_runtime_declared++;var c=mats[1].GetColor(num.name);
       if(FloatBits(c.r,num.value[0])&&FloatBits(c.g,num.value[1])&&FloatBits(c.b,num.value[2])&&FloatBits(c.a,num.value[3]))r.saved_color_runtime_matches++;
     }
   }
   return mats;
 }
 static void ObserveMesh(Mesh mesh,DrawInput cfg,DrawReceipt r) {
   r.mesh_identity=ObjectId(mesh,cfg.mesh_guid,cfg.mesh_id);
   r.mesh_descriptor_match=mesh.vertexCount==cfg.vertex_count&&mesh.subMeshCount==1&&mesh.vertexBufferCount==1&&
       mesh.GetVertexBufferStride(0)==cfg.mesh_stride&&(int)mesh.indexFormat==cfg.index_format;
   try {
     using(var data=Mesh.AcquireReadOnlyMeshData(mesh)){
       var d=data[0];byte[] v=d.GetVertexData<byte>(0).ToArray();byte[] idx;
       if(mesh.indexFormat==IndexFormat.UInt16){var a=d.GetIndexData<ushort>().ToArray();idx=new byte[a.Length*2];Buffer.BlockCopy(a,0,idx,0,idx.Length);}
       else {var a=d.GetIndexData<uint>().ToArray();idx=new byte[a.Length*4];Buffer.BlockCopy(a,0,idx,0,idx.Length);}
       r.mesh_vertex_bytes_match=v.Length==cfg.vertex_bytes&&Sha(v)==cfg.vertex_sha;
       r.mesh_index_bytes_match=idx.Length==cfg.index_bytes&&Sha(idx)==cfg.index_sha;
     }
   } catch(Exception) {} // preserve diagnostic draw separately from raw parity
 }
 static void Capture(Camera cam,MeshRenderer rend,Material mat,RenderTexture rt,string path) {
   rend.enabled=mat!=null;if(mat!=null)rend.sharedMaterial=mat;
   cam.Render();var old=RenderTexture.active;RenderTexture.active=rt;
   var read=new Texture2D(rt.width,rt.height,TextureFormat.RGBAFloat,false,true);
   try {
     read.ReadPixels(new Rect(0,0,rt.width,rt.height),0,0,false);
     var pixels=read.GetPixels();
     using(var output=new BinaryWriter(new FileStream(path,FileMode.CreateNew,FileAccess.Write)))
       foreach(var p in pixels){output.Write(p.r);output.Write(p.g);output.Write(p.b);output.Write(p.a);}
   }finally{RenderTexture.active=old;UnityEngine.Object.DestroyImmediate(read);}
 }
 static void DrawViews(DrawInput cfg,DrawReceipt r,Mesh mesh,Material[] mats,string priv) {
   var go=new GameObject("GT isolated selected mesh");var cameraGO=new GameObject("GT diagnostic camera");var lightGO=new GameObject("GT diagnostic light");
   var rt=new RenderTexture(cfg.size,cfg.size,24,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
   var dummyShader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTDrawControl.shader");
   Need(dummyShader!=null&&dummyShader.isSupported);var dummy=new Material(dummyShader);
   CausalControls causal=null;Material provider=null;ProviderReceipt providerReceipt=new ProviderReceipt();
   try {
     Need(cfg.views==3&&cfg.size==128&&rt.Create());
     go.layer=30;go.transform.position=-mesh.bounds.center;go.AddComponent<MeshFilter>().sharedMesh=mesh;
     var rend=go.AddComponent<MeshRenderer>();rend.shadowCastingMode=ShadowCastingMode.Off;rend.receiveShadows=false;
     var cam=cameraGO.AddComponent<Camera>();cam.enabled=false;cam.targetTexture=rt;cam.clearFlags=CameraClearFlags.SolidColor;
     cam.backgroundColor=new Color(.173f,.217f,.389f,.67f);cam.orthographic=true;cam.aspect=1;cam.cullingMask=1<<30;
     cam.allowHDR=true;cam.allowMSAA=false;cam.renderingPath=RenderingPath.Forward;
     float radius=mesh.bounds.extents.magnitude;Need(radius>0&&!float.IsNaN(radius)&&!float.IsInfinity(radius));
     cam.orthographicSize=radius*1.25f;cam.nearClipPlane=Mathf.Max(.001f,radius*.01f);cam.farClipPlane=radius*10+1;
     var light=lightGO.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1;light.color=Color.white;
     light.cullingMask=1<<30;light.shadows=LightShadows.None;lightGO.transform.rotation=Quaternion.Euler(40,25,0);
     if(cfg.provider_probe)provider=PrepareProvider(cfg,r,mats[1]);
     else causal=PrepareCausal(cfg,r,mats[1],Directory.GetParent(Application.dataPath).FullName,priv);
     Vector3[] views={new Vector3(1,1,-2),new Vector3(-2,.7f,-1),new Vector3(0,2,1)};
     string[] cases={"type3","type2","wrong_guid","wrong_fileid"};
     for(int v=0;v<views.Length;v++){
       cam.transform.position=views[v].normalized*(radius*3+1);cam.transform.LookAt(Vector3.zero,Vector3.up);
       string prefix=Path.Combine(priv,"view-"+v+"-");
       Capture(cam,rend,null,rt,prefix+"clear.f32");Capture(cam,rend,dummy,rt,prefix+"dummy.f32");
       for(int i=0;i<4;i++)Capture(cam,rend,mats[i],rt,prefix+cases[i]+".f32");
       Capture(cam,rend,mats[1],rt,prefix+"type2_repeat.f32");
       if(cfg.provider_probe)providerReceipt.views[v]=CaptureProviderView(cfg,r,cam,rend,rt,provider,v,priv);
       else { CausalCapture(cam,rend,rt,causal,r,prefix); CaptureBasis(cam,rend,rt,causal,r,cfg,prefix); }
       r.rendered_views++;
     }
     if(cfg.provider_probe)File.WriteAllText(Path.Combine(priv,"provider-receipt.json"),JsonUtility.ToJson(providerReceipt));
   }finally {
     if(provider!=null)UnityEngine.Object.DestroyImmediate(provider);
     if(causal!=null)causal.Dispose();
     rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(dummy);
     UnityEngine.Object.DestroyImmediate(go);UnityEngine.Object.DestroyImmediate(cameraGO);UnityEngine.Object.DestroyImmediate(lightGO);
   }
 }
 public static void Run(){
   var r=new DrawReceipt{run_id=Arg("-gtArrayRunId"),unity_version=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),color_space=QualitySettings.activeColorSpace.ToString()};
   string priv=Arg("-gtArrayPrivate");int code=2;bool priorAsync=ShaderUtil.allowAsyncCompilation;
   try {
     Need(Application.isBatchMode&&r.unity_version=="2021.3.45f2"&&SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan&&
       QualitySettings.activeColorSpace==ColorSpace.Linear&&SystemInfo.supports2DArrayTextures&&SystemInfo.SupportsTextureFormat(TextureFormat.DXT5));
     r.phase="private_guard";Need(!String.IsNullOrEmpty(priv)&&File.Exists(Path.Combine(priv,"editor-output-private"))&&
       File.ReadAllText(Path.Combine(priv,"editor-output-private")).Trim()==r.run_id);r.private_log_guard=true;
     string root=Directory.GetParent(Application.dataPath).FullName;
     string json=File.ReadAllText(Path.Combine(root,"GTInput.json"));Need(json==File.ReadAllText(Path.Combine(priv,"expected.json")));
     var cfg=JsonUtility.FromJson<DrawInput>(json);Need(cfg!=null&&cfg.run_id==r.run_id);
     ShaderUtil.allowAsyncCompilation=false;
     r.phase="source_assets";ImportExact(cfg,root,priv,r);
     var shader=AssetDatabase.LoadAssetAtPath<Shader>(cfg.shader_path);Need(shader!=null);
     r.shader_identity=ObjectId(shader,cfg.shader_guid,4800000);r.shader_supported=shader.isSupported;r.shader_passes=shader.passCount;r.shader_errors=ShaderErrors(shader);
     Need(r.shader_identity&&r.shader_supported&&r.shader_passes==1&&r.shader_errors==0);
     r.phase="native_array";
     byte[] raw=File.ReadAllBytes(Path.Combine(priv,"array.bc3.bytes"));Need(raw.Length==2796256&&Sha(raw)==cfg.array_sha);
     var tex=Make(raw,1024,1024,2,11,cfg.array_name);
     Need(cfg.sampler.Length==5);
     tex.filterMode=(FilterMode)cfg.sampler[0];tex.anisoLevel=cfg.sampler[1];tex.wrapModeU=(TextureWrapMode)cfg.sampler[2];
     tex.wrapModeV=(TextureWrapMode)cfg.sampler[3];tex.wrapModeW=(TextureWrapMode)cfg.sampler[4];tex.mipMapBias=cfg.mip_bias;
     EditorSettings.serializationMode=SerializationMode.ForceText;
     Directory.CreateDirectory(Path.GetDirectoryName(AssetPath(root,cfg.array_path)));
     Directory.CreateDirectory(Path.Combine(root,"Assets","GTDraw","Scratch"));
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     var transferred=TransferNative(tex,root,"Assets/GTDraw/Scratch/array.asset",cfg.array_path,cfg.array_guid,18700000,
        cfg.array_name,1024,1024,2,11,new Transfer());
     Need(transferred!=null);r.array_identity=ObjectId(transferred,cfg.array_guid,18700000);
     string rb=Path.Combine(priv,"draw-array-readback.bytes");Raw(transferred,rb);r.array_raw_bytes_match=Sha(File.ReadAllBytes(rb))==cfg.array_sha;
     r.array_sampler_match=(int)transferred.filterMode==cfg.sampler[0]&&transferred.anisoLevel==cfg.sampler[1]&&
        (int)transferred.wrapModeU==cfg.sampler[2]&&(int)transferred.wrapModeV==cfg.sampler[3]&&(int)transferred.wrapModeW==cfg.sampler[4]&&FloatBits(transferred.mipMapBias,cfg.mip_bias);
     r.phase="materials";var mats=DrawMaterials(cfg,root,priv,shader,r);
     ImportTap(cfg,r,root,priv);
     r.phase="mesh";var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(cfg.mesh_path);Need(mesh!=null);ObserveMesh(mesh,cfg,r);
     r.phase="render";DrawViews(cfg,r,mesh,mats,priv);
     r.shader_errors=ShaderErrors(shader);
     if(r.tap_shader_compiled){var t=Shader.Find("Hidden/GTSelectedArrayTap");r.tap_shader_errors=t==null?-1:ShaderErrors(t);}
     r.phase="complete";r.status="OBSERVED";code=0;
   }catch(Exception e){r.failure_category=e.GetType().Name;}
   finally{
     ShaderUtil.allowAsyncCompilation=priorAsync;
     if(r.private_log_guard)File.WriteAllText(Path.Combine(priv,"draw-receipt.json"),JsonUtility.ToJson(r));
     EditorApplication.Exit(code);
   }
 }
}
#endif
