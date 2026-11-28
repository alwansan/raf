// Isolated exact exported ParticleSystem/Renderer documents; no replacement quad or alpha replay.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Experimental.Rendering;
public static class NativeMipValidation {
 [Serializable] class Asset {public string path,blob,guid,sha,meta_sha;public long file_id;}
 [Serializable] class Slot {public string name,guid;public long file_id;public float[] uv;}
 [Serializable] class Number {public string name,kind;public float[] value;}
 [Serializable] class Input {public string run_id,shader_path,material_path,texture_path,shader_guid,material_guid,texture_guid,selected_property;public long texture_id;
   public Asset[] assets;public Slot[] slots;public Number[] numbers;public int[] sampler;public float bias;}
 [Serializable] class Requirement {public string semantic;public int index,mask,used_mask,component_type;}
 [Serializable] class Case {public int index,material_count;public string path,blob,sha;public int[] streams;public bool custom_streams,original_self_active;}
 [Serializable] class Config {public string run_id;public Case[] scenes;public Requirement[] vertex_requirements;}
 [Serializable] class Bake {public int particles,particles_read,positive_size_lifetime,vertices=-1,indices=-1,submeshes=-1,required_present,required_width;public bool finite,nondegenerate,bake_completed;public string failure_category="";}
 [Serializable] class ControlCase {public int material_kind,method;public Bake empty,one;public string failure_category="";}
 [Serializable] class Row {public int index,empty_vertices=-1,empty_particles=-1,natural_particles,natural_vertices;
   public bool imported,materials_match,billboard,active_streams_read,streams_match,scene_bytes_unchanged;public Bake forced;public string failure_category="";}
 [Serializable] class Receipt {public string run_id,phase="guard",status="INCONCLUSIVE",unity_version,backend,failure_category="";
   public bool private_log_guard,control_verified,source_assets_unchanged,shader_supported,material_shader_match,native_identity,native_descriptor,native_sampler,resources_bytes_match;
   public int asset_identities,assets_written,scenes_written,scenes_imported,shader_errors=-1,slots_declared,slots_matched,uv_matched,numeric_saved,numeric_declared,numeric_matched,numeric_undeclared;public Row[] rows;public ControlCase[] calibration_cases;public int selected_calibration_method=-1;}
 static void Need(bool x){if(!x)throw new InvalidOperationException("GT emitter geometry gate");}
 static string Arg(string n){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,n);return i>=0&&i+1<a.Length?a[i+1]:"";}
 static string Sha(byte[] x){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(x)).Replace("-","").ToLowerInvariant();}
 static bool Id(UnityEngine.Object obj,string g,long f){return obj!=null&&AssetDatabase.TryGetGUIDAndLocalFileIdentifier(obj,out string gg,out long ff)&&gg==g&&ff==f;}
 static bool Eq(float a,float b){return BitConverter.ToInt32(BitConverter.GetBytes(a),0)==BitConverter.ToInt32(BitConverter.GetBytes(b),0);}
 static bool Fin(float v){return !float.IsNaN(v)&&!float.IsInfinity(v);}
 static bool Fin(Vector3 v){return Fin(v.x)&&Fin(v.y)&&Fin(v.z);}
 static bool AssetsSame(Input c,string root){
   return c.assets.All(a=>Sha(File.ReadAllBytes(Path.Combine(root,a.path)))==a.sha&&Sha(File.ReadAllBytes(Path.Combine(root,a.path)+".meta"))==a.meta_sha);
 }
 static bool MaterialSame(Input c,Material mat,Shader shader,Texture2D tex,Receipt r){
   r.material_shader_match=Id(mat,c.material_guid,2100000)&&Id(shader,c.shader_guid,4800000)&&mat.shader==shader;
   r.native_identity=Id(tex,c.texture_guid,c.texture_id)&&mat.GetTexture(c.selected_property)==tex;
   r.native_descriptor=tex.width==64&&tex.height==64&&tex.mipmapCount==7&&tex.format==TextureFormat.RGBA32&&GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat);
   r.native_sampler=c.sampler!=null&&c.sampler.Length==5&&(int)tex.filterMode==c.sampler[0]&&tex.anisoLevel==c.sampler[1]&&(int)tex.wrapModeU==c.sampler[2]&&(int)tex.wrapModeV==c.sampler[3]&&(int)tex.wrapModeW==c.sampler[4]&&Eq(tex.mipMapBias,c.bias);
   r.slots_declared=c.slots.Length;r.slots_matched=0;r.uv_matched=0;
   foreach(var slot in c.slots){if(!mat.HasProperty(slot.name))continue;
     if(Id(mat.GetTexture(slot.name),slot.guid,slot.file_id))r.slots_matched++;
     var st=mat.GetTextureScale(slot.name);var off=mat.GetTextureOffset(slot.name);
     if(slot.uv.Length==4&&Eq(st.x,slot.uv[0])&&Eq(st.y,slot.uv[1])&&Eq(off.x,slot.uv[2])&&Eq(off.y,slot.uv[3]))r.uv_matched++;
   }
   r.numeric_saved=c.numbers.Length;r.numeric_declared=0;r.numeric_matched=0;r.numeric_undeclared=0;
   foreach(var num in c.numbers){
     // Same measured contract as the calibrated draw: distinguish saved-but-undeclared
     // values rather than treating them as a numeric match or an automatic import failure.
     if(!mat.HasProperty(num.name)){r.numeric_undeclared++;continue;}
     r.numeric_declared++;
     bool match=false;
     if(num.kind=="float"&&num.value.Length==1)match=Eq(mat.GetFloat(num.name),num.value[0]);
     if(num.kind=="color"&&num.value.Length==4){var v=mat.GetColor(num.name);match=Eq(v.r,num.value[0])&&Eq(v.g,num.value[1])&&Eq(v.b,num.value[2])&&Eq(v.a,num.value[3]);}
     if(match)r.numeric_matched++;
   }
   return r.material_shader_match&&r.native_identity&&r.native_descriptor&&r.native_sampler&&r.slots_declared==2&&r.slots_matched==2&&r.uv_matched==2
       &&r.numeric_declared==11&&r.numeric_matched==11&&r.numeric_saved==r.numeric_declared+r.numeric_undeclared;
 }
 static bool Attribute(Requirement q,out VertexAttribute a){
   a=VertexAttribute.Position;
   if(q.semantic=="POSITION"&&q.index==0)return true;
   if(q.semantic=="NORMAL"&&q.index==0){a=VertexAttribute.Normal;return true;}
   if(q.semantic=="TANGENT"&&q.index==0){a=VertexAttribute.Tangent;return true;}
   if(q.semantic=="COLOR"&&q.index==0){a=VertexAttribute.Color;return true;}
   if(q.semantic=="TEXCOORD"&&q.index>=0&&q.index<=7){a=(VertexAttribute)((int)VertexAttribute.TexCoord0+q.index);return true;}
   return false;
 }
 static Bake Measure(ParticleSystem ps,ParticleSystemRenderer ren,Camera cam,Requirement[] req,bool renderBefore=false){
   var b=new Bake{particles=ps.particleCount};
   var mesh=new Mesh();RenderTexture rt=null;
   try {
     var live=new ParticleSystem.Particle[Math.Min(ps.particleCount,256)];
     b.particles_read=ps.GetParticles(live);
     for(int i=0;i<b.particles_read;i++){
       float size=live[i].GetCurrentSize(ps);
       if(Fin(size)&&size>0&&Fin(live[i].remainingLifetime)&&live[i].remainingLifetime>0)b.positive_size_lifetime++;
     }
     if(renderBefore){
       rt=new RenderTexture(64,64,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Linear);
       Need(rt.Create());cam.targetTexture=rt;cam.Render();cam.targetTexture=null;
     }
     ren.BakeMesh(mesh,cam,false);
     b.bake_completed=true;b.vertices=mesh.vertexCount;b.submeshes=mesh.subMeshCount;
     var ii=mesh.subMeshCount>0?mesh.GetIndices(0):new int[0];
     b.indices=ii.Length;var vv=mesh.vertices;
     b.finite=vv.Length==b.vertices&&vv.All(x=>Fin(x))&&ii.All(i=>i>=0&&i<vv.Length);
     b.nondegenerate=b.finite&&ii.Length>0&&ii.Length%3==0;
     if(b.nondegenerate)for(int i=0;i<ii.Length;i+=3){
       var cross=Vector3.Cross(vv[ii[i+1]]-vv[ii[i]],vv[ii[i+2]]-vv[ii[i]]);
       if(!Fin(cross)||cross.sqrMagnitude<=1e-20f){b.nondegenerate=false;break;}}
     foreach(var q in req){if(!Attribute(q,out VertexAttribute va)||!mesh.HasVertexAttribute(va))continue;b.required_present++;
       int mask=q.used_mask!=0?q.used_mask:q.mask, width=0;while(mask>0){width++;mask>>=1;}
       if(mesh.GetVertexAttributeDimension(va)>=width)b.required_width++;}
   }catch(Exception e){b.failure_category=e.GetType().Name;}
   finally{cam.targetTexture=null;if(rt!=null){rt.Release();UnityEngine.Object.DestroyImmediate(rt);}UnityEngine.Object.DestroyImmediate(mesh);}
   return b;
 }
 static bool Empty(Bake b){return b!=null&&b.bake_completed&&b.particles==0&&b.particles_read==0&&b.vertices==0&&b.indices==0;}
 static bool One(Bake b){return b!=null&&b.bake_completed&&b.particles==1&&b.particles_read==1&&b.positive_size_lifetime==1&&b.vertices==4&&b.indices==6&&b.finite&&b.nondegenerate;}
 static Camera CameraFor(Vector3 p){
   Need(Fin(p));var go=new GameObject("GT isolated bake camera");var cam=go.AddComponent<Camera>();
   go.transform.position=p+new Vector3(0,0,-8);go.transform.rotation=Quaternion.identity;
   cam.enabled=false;cam.orthographic=true;cam.orthographicSize=4;cam.aspect=1;cam.nearClipPlane=.1f;cam.farClipPlane=100f;
   cam.clearFlags=CameraClearFlags.SolidColor;cam.useOcclusionCulling=false;cam.allowMSAA=false;cam.renderingPath=RenderingPath.Forward;
   return cam;
 }
 static void EmitOne(ParticleSystem ps,int method){
   ps.Stop(false,ParticleSystemStopBehavior.StopEmittingAndClear);
   if(method==0){ps.Emit(1);return;}
   if(method==1||method==3){
     ps.Play(false);ps.Clear(false);ps.Emit(1);ps.Pause(false);return;
   }
   if(method==2){
     ps.Simulate(0f,false,true,true);ps.Clear(false);ps.Emit(1);return;
   }
   // Seeded particle is a diagnostic of BakeMesh independent of Emit; never
   // admit it as proof of original emitter generation.
   Need(method==4);
   ps.Play(false);ps.Clear(false);ps.Pause(false);
   var p=new ParticleSystem.Particle{position=Vector3.zero,startLifetime=10f,remainingLifetime=10f,startSize=1f,startColor=new Color32(255,255,255,255),randomSeed=1};
   ps.SetParticles(new[]{p},1);
 }
 static ControlCase Control(Material mat,Requirement[] req,int materialKind,int method){
   var row=new ControlCase{material_kind=materialKind,method=method};
   GameObject go=null;Camera cam=null;
   try{
     go=new GameObject("GT authored particle calibration");var ps=go.AddComponent<ParticleSystem>();var ren=go.GetComponent<ParticleSystemRenderer>();
     cam=CameraFor(Vector3.zero);Need(ren!=null&&mat!=null);
     go.layer=30;cam.cullingMask=1<<30;
     ren.sharedMaterial=mat;ren.renderMode=ParticleSystemRenderMode.Billboard;ren.enabled=true;
     ren.SetActiveVertexStreams(new List<ParticleSystemVertexStream>{ParticleSystemVertexStream.Position,ParticleSystemVertexStream.Color,ParticleSystemVertexStream.UV});
     var main=ps.main;main.playOnAwake=false;main.startLifetime=10f;main.startSize=1f;main.startSpeed=0f;main.maxParticles=64;
     var em=ps.emission;em.enabled=false;var sh=ps.shape;sh.enabled=false;
     ps.Stop(false,ParticleSystemStopBehavior.StopEmittingAndClear);
     row.empty=Measure(ps,ren,cam,req,method==3);
     EmitOne(ps,method);row.one=Measure(ps,ren,cam,req,method==3);
   }catch(Exception e){row.failure_category=e.GetType().Name;}
   finally{if(cam!=null)UnityEngine.Object.DestroyImmediate(cam.gameObject);if(go!=null)UnityEngine.Object.DestroyImmediate(go);}
   return row;
 }
 static Row Observe(Case item,Input c,Config cfg,Material mat,string root,int method){
   var row=new Row{index=item.index};Camera cam=null;
   try{
     var scene=EditorSceneManager.OpenScene(item.path,OpenSceneMode.Single);
     var roots=scene.GetRootGameObjects().Where(x=>x.GetComponent<ParticleSystem>()!=null).ToArray();
     Need(roots.Length==1);var go=roots[0];var ps=go.GetComponent<ParticleSystem>();var ren=go.GetComponent<ParticleSystemRenderer>();
     Need(ps!=null&&ren!=null&&go.activeInHierarchy);row.imported=true;row.billboard=ren.renderMode==ParticleSystemRenderMode.Billboard;
     var mats=ren.sharedMaterials;row.materials_match=mats.Length==item.material_count&&mats.All(m=>m==mat&&Id(m,c.material_guid,2100000));
     var streams=new List<ParticleSystemVertexStream>();ren.GetActiveVertexStreams(streams);row.active_streams_read=streams.Count>0;
     row.streams_match=streams.Select(x=>(int)x).SequenceEqual(item.streams);
     Need(row.billboard&&row.materials_match&&row.active_streams_read);cam=CameraFor(go.transform.position);
     // Diagnostic fixture activation and explicit emission do not represent original gameplay.
     ren.enabled=true;ps.Stop(false,ParticleSystemStopBehavior.StopEmittingAndClear);
     var zero=Measure(ps,ren,cam,cfg.vertex_requirements,method==3);row.empty_particles=zero.bake_completed?zero.particles:-1;row.empty_vertices=zero.bake_completed?zero.vertices:-1;
     ps.Simulate(1f,false,true,true);var natural=Measure(ps,ren,cam,cfg.vertex_requirements);
     row.natural_particles=natural.particles;row.natural_vertices=natural.vertices;
     EmitOne(ps,method);row.forced=Measure(ps,ren,cam,cfg.vertex_requirements,method==3);
     row.scene_bytes_unchanged=Sha(File.ReadAllBytes(Path.Combine(root,item.path)))==item.sha;
   }catch(Exception e){row.failure_category=e.GetType().Name;}
   finally{if(cam!=null)UnityEngine.Object.DestroyImmediate(cam.gameObject);}
   return row;
 }
 public static void Run(){
   var r=new Receipt{run_id=Arg("-gtNativeRunId"),unity_version=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString()};
   string priv=Arg("-gtNativePrivate");int code=2;bool async=ShaderUtil.allowAsyncCompilation;
   try{
     Need(Application.isBatchMode&&r.unity_version=="2021.3.45f2"&&SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan&&QualitySettings.activeColorSpace==ColorSpace.Linear&&GraphicsSettings.currentRenderPipeline==null);
     Need(!String.IsNullOrEmpty(priv)&&File.Exists(Path.Combine(priv,"editor-output-private"))&&File.ReadAllText(Path.Combine(priv,"editor-output-private")).Trim()==r.run_id);r.private_log_guard=true;
     string root=Directory.GetParent(Application.dataPath).FullName;
     string input=File.ReadAllText(Path.Combine(root,"GTInput.json"));Need(input==File.ReadAllText(Path.Combine(priv,"expected.json")));
     string conf=File.ReadAllText(Path.Combine(root,"GTEmitterInput.json"));Need(conf==File.ReadAllText(Path.Combine(priv,"emitter-input.json")));
     var c=JsonUtility.FromJson<Input>(input);var cfg=JsonUtility.FromJson<Config>(conf);
     Need(c.run_id==cfg.run_id&&cfg.run_id==r.run_id&&c.assets.Length==4&&cfg.scenes.Length==12&&cfg.vertex_requirements.Length>0);
     ShaderUtil.allowAsyncCompilation=false;
     r.phase="asset_staging";
     foreach(var a in c.assets){
       string path=Path.GetFullPath(Path.Combine(root,a.path));Need(path.StartsWith(Path.Combine(root,"Assets","GTParticle")+Path.DirectorySeparatorChar,StringComparison.Ordinal)&&!File.Exists(path)&&!File.Exists(path+".meta"));
       Need(String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(a.guid)));
       var data=File.ReadAllBytes(Path.Combine(priv,a.blob+".bytes"));var meta=File.ReadAllBytes(Path.Combine(priv,a.blob+".meta.bytes"));
       Need(Sha(data)==a.sha&&Sha(meta)==a.meta_sha);Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,data);File.WriteAllBytes(path+".meta",meta);r.assets_written++;
     }
     r.phase="asset_refresh";AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     r.phase="asset_identity";
     foreach(var a in c.assets)if(Id(AssetDatabase.LoadMainAssetAtPath(a.path),a.guid,a.file_id))r.asset_identities++;
     r.resources_bytes_match=AssetsSame(c,root);
     Need(r.asset_identities==4&&r.resources_bytes_match);
     r.phase="shader_load";
     var shader=AssetDatabase.LoadAssetAtPath<Shader>(c.shader_path);
     r.shader_supported=shader!=null&&shader.isSupported&&shader.passCount==1;
     if(shader!=null)r.shader_errors=ShaderUtil.GetShaderMessages(shader).Count(x=>x.severity.ToString()=="Error");
     Need(r.shader_supported&&r.shader_errors==0);
     r.phase="material_texture_load";
     var mat=AssetDatabase.LoadAssetAtPath<Material>(c.material_path);var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(c.texture_path);
     Need(mat!=null&&tex!=null);
     r.phase="material_contract";
     bool materialOk=MaterialSame(c,mat,shader,tex,r);
     r.phase="material_identity";Need(r.material_shader_match&&r.native_identity);
     r.phase="texture_descriptor_sampler";Need(r.native_descriptor&&r.native_sampler);
     r.phase="texture_refs_uv";Need(r.slots_declared==2&&r.slots_matched==2&&r.uv_matched==2);
     r.phase="numeric_properties";Need(materialOk);
     r.phase="scene_staging";
     foreach(var x in cfg.scenes){
       string path=Path.GetFullPath(Path.Combine(root,x.path));
       Need(path.StartsWith(Path.Combine(root,"Assets","GTEmitter")+Path.DirectorySeparatorChar,StringComparison.Ordinal)&&!File.Exists(path));
       var data=File.ReadAllBytes(Path.Combine(priv,x.blob));Need(Sha(data)==x.sha);Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,data);r.scenes_written++;
     }
     r.phase="scene_refresh";AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     foreach(var x in cfg.scenes)if(AssetDatabase.LoadAssetAtPath<SceneAsset>(x.path)!=null)r.scenes_imported++;
     Need(r.scenes_imported==12&&r.scenes_written==12);
     r.phase="calibration";EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
     Need(mat!=null);
     var markerShader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTParticleControl.shader");
     Need(markerShader!=null&&markerShader.isSupported&&ShaderUtil.GetShaderMessages(markerShader).All(x=>x.severity.ToString()!="Error"));
     var marker=new Material(markerShader);
     try{
       var cases=new List<ControlCase>();
       for(int k=0;k<2;k++)for(int m=0;m<5;m++){cases.Add(Control(k==0?mat:marker,cfg.vertex_requirements,k,m));r.calibration_cases=cases.ToArray();}
       for(int m=0;m<4;m++){
         var both=cases.Where(x=>x.method==m).ToArray();
         if(both.Length==2&&both.All(x=>Empty(x.empty)&&One(x.one))){r.selected_calibration_method=m;break;}
       }
       r.control_verified=r.selected_calibration_method>=0;
     }finally{if(marker!=null)UnityEngine.Object.DestroyImmediate(marker);}
     Need(r.control_verified);
     r.phase="geometry";r.rows=cfg.scenes.Select(x=>Observe(x,c,cfg,mat,root,r.selected_calibration_method)).ToArray();
     r.phase="post_geometry_asset_contract";r.source_assets_unchanged=AssetsSame(c,root)&&MaterialSame(c,mat,shader,tex,r);
     r.phase="complete";r.status="OBSERVED";code=0;
   }catch(Exception e){r.failure_category=e.GetType().Name;}
   finally{
     ShaderUtil.allowAsyncCompilation=async;
     if(r.private_log_guard)File.WriteAllText(Path.Combine(priv,"geometry-receipt.json"),JsonUtility.ToJson(r));
     EditorApplication.Exit(code);
   }
 }
}
#endif
