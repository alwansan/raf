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
 [Serializable] class Input {public string run_id,shader_path,material_path,texture_path,shader_guid,material_guid,texture_guid,selected_property,raw_sha;public long texture_id;
   public Asset[] assets;public Slot[] slots;public Number[] numbers;public int[] sampler;public float bias;}
 [Serializable] class Requirement {public string semantic;public int index,mask,used_mask,component_type;}
 [Serializable] class Case {public int index,material_count;public string path,blob,sha;public int[] streams;public bool custom_streams,original_self_active;}
 [Serializable] class Config {public string run_id;public Case[] scenes;public Requirement[] vertex_requirements;}
 [Serializable] class Bake {public int particles,particles_read,positive_size_lifetime,vertices=-1,indices=-1,submeshes=-1,required_present,required_width;public bool finite,nondegenerate,bake_completed;public string failure_category="";}
 [Serializable] class ProbeLane {public int index,width,format;public Vector4[] cpu;}
 [Serializable] class ProbeData {public int index,vertices,indices;public ProbeLane[] lanes;public bool completed;public string failure_category="";}
 [Serializable] class RenderPath {public string path,phase="start",failure_category="";public int submissions;public bool completed,material_restored,streams_unchanged,particles_unchanged,blocks_restored;public int override_submissions;}
 [Serializable] class RenderEvidence {public int index,particles,vertices,indices;public string mode;public bool clone_payload_verified,clone_format_sampler_verified;public RenderPath[] paths;}
 [Serializable] class ControlCase {public int material_kind,method;public Bake empty,one,before_roundtrip;public bool roundtrip_state_equal;public string failure_category="";}
 [Serializable] class Row {public int index,empty_vertices=-1,empty_particles=-1,natural_particles,natural_vertices;
   public bool imported,materials_match,billboard,active_streams_read,streams_match,scene_bytes_unchanged;public Bake forced,natural,roundtrip;public bool roundtrip_state_equal;public int direct_method=-1;public string failure_category="";}
 [Serializable] class Receipt {public string run_id,phase="guard",status="INCONCLUSIVE",unity_version,backend,failure_category="";
   public bool private_log_guard,control_verified,source_assets_unchanged,shader_supported,material_shader_match,native_identity,native_descriptor,native_sampler,resources_bytes_match;
   public int asset_identities,assets_written,scenes_written,scenes_imported,shader_errors=-1,slots_declared,slots_matched,uv_matched,numeric_saved,numeric_declared,numeric_matched,numeric_undeclared;public Row[] rows;public ControlCase[] calibration_cases;public bool lane_control_completed;public int selected_calibration_method=-1;}
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
 static Vector4[] CpuValues(Mesh m,VertexAttribute a){
   if(a==VertexAttribute.Position)return m.vertices.Select(v=>new Vector4(v.x,v.y,v.z,0)).ToArray();
   if(a==VertexAttribute.Normal)return m.normals.Select(v=>new Vector4(v.x,v.y,v.z,0)).ToArray();
   if(a==VertexAttribute.Tangent)return m.tangents;
   if(a==VertexAttribute.Color)return m.colors.Select(v=>new Vector4(v.r,v.g,v.b,v.a)).ToArray();
   int index=(int)a-(int)VertexAttribute.TexCoord0;Need(index>=0&&index<8);
   var uv=new List<Vector4>();m.GetUVs(index,uv);return uv.ToArray();
 }
 static void WriteProbePixels(RenderTexture rt,string file){
   var old=RenderTexture.active;var t=new Texture2D(rt.width,rt.height,TextureFormat.RGBAFloat,false,true);
   try{RenderTexture.active=rt;t.ReadPixels(new Rect(0,0,rt.width,rt.height),0,0,false);
     using(var w=new BinaryWriter(new FileStream(file,FileMode.CreateNew,FileAccess.Write)))
       foreach(var p in t.GetPixels()){w.Write(p.r);w.Write(p.g);w.Write(p.b);w.Write(p.a);}
   }finally{RenderTexture.active=old;UnityEngine.Object.DestroyImmediate(t);}
 }
 static ProbeData ProbeMesh(Mesh mesh,Requirement[] req,string priv,int index){
   var p=new ProbeData{index=index,vertices=mesh.vertexCount,indices=mesh.subMeshCount>0?(int)mesh.GetIndexCount(0):0};
   Material m=null;RenderTexture rt=null;bool srgb=GL.sRGBWrite;
   try{
     Need(p.vertices==4&&p.indices==6&&req.Length==3);
     var shader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTEmitterLaneProbe.shader");
     Need(shader!=null&&shader.isSupported&&shader.passCount==1&&ShaderUtil.GetShaderMessages(shader).All(x=>x.severity.ToString()!="Error"));
     var lanes=new List<ProbeLane>();
     for(int i=0;i<req.Length;i++){
       Need(Attribute(req[i],out VertexAttribute a)&&mesh.HasVertexAttribute(a));
       int width=mesh.GetVertexAttributeDimension(a);
       var cpu=CpuValues(mesh,a);Need(cpu.Length==p.vertices&&width>=1&&width<=4);
       lanes.Add(new ProbeLane{index=i,width=width,format=(int)mesh.GetVertexAttributeFormat(a),cpu=cpu});
     }
     p.lanes=lanes.ToArray();m=new Material(shader);
     rt=new RenderTexture(16,16,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
     Need(rt.Create()&&!rt.sRGB&&rt.graphicsFormat==GraphicsFormat.R32G32B32A32_SFloat);
     GL.sRGBWrite=false;
     // No modification of source mesh vertices, channel formats or indices.
     // The probe vertex shader places existing vertices by ID on screen.
     for(int i=-1;i<req.Length;i++){
       var b=new CommandBuffer{name="GT emitter input diagnostic"};
       try{
         var props=new MaterialPropertyBlock();props.SetFloat("_GTInputIndex",i);
         b.SetRenderTarget(rt);b.SetViewport(new Rect(0,0,16,16));
         b.ClearRenderTarget(false,true,new Color(-19,-23,-29,-31));
         b.SetViewProjectionMatrices(Matrix4x4.identity,Matrix4x4.identity);
         b.DrawMesh(mesh,Matrix4x4.identity,m,0,0,props);
         Graphics.ExecuteCommandBuffer(b);
         WriteProbePixels(rt,Path.Combine(priv,"lane-"+index+"-"+i+".f32"));
       }finally{b.Release();}
     }
     p.completed=true;
   }catch(Exception e){p.failure_category=e.GetType().Name;}
   finally{
     GL.sRGBWrite=srgb;
     if(rt!=null){rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
     if(m!=null)UnityEngine.Object.DestroyImmediate(m);
     File.WriteAllText(Path.Combine(priv,"lane-"+index+".json"),JsonUtility.ToJson(p));
   }
   return p;
 }
 static bool ProbeControl(Requirement[] req,string priv){
   var m=new Mesh();
   try{
     // Known authored diagnostic only, distinct from the 12 real meshes.
     m.vertices=new[]{new Vector3(.125f,.25f,.375f),new Vector3(.5f,.625f,.75f),new Vector3(.875f,.125f,.25f),new Vector3(.375f,.5f,.625f)};
     m.colors=Enumerable.Repeat(new Color(.25f,.5f,.75f,1f),4).ToArray();
     m.normals=Enumerable.Repeat(new Vector3(.125f,.25f,.5f),4).ToArray();
     m.tangents=Enumerable.Repeat(new Vector4(.125f,.25f,.5f,1f),4).ToArray();
     for(int i=0;i<8;i++)m.SetUVs(i,new List<Vector2>{new Vector2(.125f,.25f),new Vector2(.375f,.5f),new Vector2(.625f,.75f),new Vector2(.875f,1f)});
     m.triangles=new[]{0,1,2,2,1,3};
     return ProbeMesh(m,req,priv,-1).completed;
   }finally{UnityEngine.Object.DestroyImmediate(m);}
 }
 static bool ParticleStateEqual(ParticleSystem ps,ParticleSystem.Particle[] before){
   if(ps.particleCount!=before.Length)return false;
   var after=new ParticleSystem.Particle[before.Length];
   if(ps.GetParticles(after)!=before.Length)return false;
   for(int i=0;i<after.Length;i++)if(!SameParticleState(before[i],after[i]))return false;
   return true;
 }
 static void Frame(Camera cam,Bounds bounds){
   Need(Fin(bounds.center)&&Fin(bounds.extents)&&bounds.extents.x>=0&&bounds.extents.y>=0&&bounds.extents.z>=0);
   float extent=Mathf.Max(bounds.extents.x,bounds.extents.y);Need(extent>1e-7f&&extent<1e8f);
   float distance=Mathf.Max(2f,bounds.extents.z+2f);
   cam.transform.position=bounds.center-new Vector3(0,0,distance);
   cam.orthographic=true;cam.orthographicSize=extent*1.4f;cam.aspect=1;
   cam.nearClipPlane=.01f;cam.farClipPlane=distance+bounds.extents.z+4f;
   cam.allowHDR=true;cam.allowMSAA=false;cam.clearFlags=CameraClearFlags.SolidColor;
 }
 static Bounds MeshBounds(Mesh mesh){
   var v=mesh.vertices;Need(v.Length>0&&v.All(x=>Fin(x)));
   var b=new Bounds(v[0],Vector3.zero);foreach(var x in v)b.Encapsulate(x);return b;
 }
 static Bounds LiveWorldBounds(ParticleSystem ps,ParticleSystem.Particle[] particles){
   var main=ps.main;var tr=ps.transform;Transform space=null;
   if(main.simulationSpace==ParticleSystemSimulationSpace.Local)space=tr;
   else if(main.simulationSpace==ParticleSystemSimulationSpace.Custom){space=main.customSimulationSpace;Need(space!=null);}
   else Need(main.simulationSpace==ParticleSystemSimulationSpace.World);
   Vector3 scale=Vector3.one;
   if(main.scalingMode==ParticleSystemScalingMode.Hierarchy)scale=tr.lossyScale;
   else if(main.scalingMode==ParticleSystemScalingMode.Local)scale=tr.localScale;
   else Need(main.scalingMode==ParticleSystemScalingMode.Shape);
   float factor=Mathf.Max(Mathf.Abs(scale.x),Mathf.Abs(scale.y),Mathf.Abs(scale.z));
   Need(Fin(factor)&&factor>0&&particles.Length>0);
   Bounds bounds=new Bounds();bool first=true;
   foreach(var p in particles){
     Vector3 world=space==null?p.position:space.TransformPoint(p.position);
     var size=p.GetCurrentSize3D(ps);
     float extent=Mathf.Max(Mathf.Abs(size.x),Mathf.Abs(size.y),Mathf.Abs(size.z))*factor;
     Need(Fin(world)&&Fin(size)&&Fin(extent)&&extent>1e-7f&&extent<1e8f);
     // Conservative square billboard envelope, centered on the actual live particle.
     var part=new Bounds(world,Vector3.one*extent*2f);
     if(first){bounds=part;first=false;}else bounds.Encapsulate(part);
   }
   return bounds;
 }
 static void DirectReferenceClear(RenderTexture rt,Color bg,string path){
   var b=new CommandBuffer{name="GT independent linear reference clear"};
   try{
     b.SetRenderTarget(rt);b.SetViewport(new Rect(0,0,rt.width,rt.height));
     b.ClearRenderTarget(true,true,bg);Graphics.ExecuteCommandBuffer(b);WriteProbePixels(rt,path);
   }finally{b.Release();}
 }
 static bool SameSampler(Texture2D t,Input c){
   return c.sampler.Length==5&&(int)t.filterMode==c.sampler[0]&&t.anisoLevel==c.sampler[1]&&
      (int)t.wrapModeU==c.sampler[2]&&(int)t.wrapModeV==c.sampler[3]&&(int)t.wrapModeW==c.sampler[4]&&Eq(t.mipMapBias,c.bias);
 }
 static Texture2D AlphaClone(Input c,byte[] raw,int alpha){
   var t=new Texture2D(64,64,TextureFormat.RGBA32,true,false);
   try{
     t.filterMode=(FilterMode)c.sampler[0];t.anisoLevel=c.sampler[1];t.wrapModeU=(TextureWrapMode)c.sampler[2];t.wrapModeV=(TextureWrapMode)c.sampler[3];t.wrapModeW=(TextureWrapMode)c.sampler[4];t.mipMapBias=c.bias;
     int pos=0;
     for(int m=0;m<7;m++){
       int n=64>>m;var bytes=new byte[n*n*4];Buffer.BlockCopy(raw,pos,bytes,0,bytes.Length);pos+=bytes.Length;
       if(alpha>=0)for(int k=3;k<bytes.Length;k+=4)bytes[k]=(byte)alpha;
       t.SetPixelData(bytes,m);
     }
     Need(pos==raw.Length);t.Apply(false,false);return t;
   }catch{UnityEngine.Object.DestroyImmediate(t);throw;}
 }
 static bool AlphaClonePayload(Texture2D t,byte[] raw,int alpha){
   int pos=0;
   for(int m=0;m<7;m++){
     var b=t.GetPixelData<byte>(m);int n=64>>m;if(b.Length!=n*n*4)return false;
     for(int i=0;i<b.Length;i++)if(b[i]!=(alpha>=0&&i%4==3?(byte)alpha:raw[pos+i]))return false;
     pos+=b.Length;
   }
   return pos==raw.Length;
 }
 static void RenderEmitterCase(Camera cam,ParticleSystemRenderer ren,Mesh mesh,Material original,Material marker,
                               Material[] mats,bool rendererPath,string kind,RenderTexture rt,string path,MaterialPropertyBlock block,string property,Texture target){
   var b=new CommandBuffer{name="GT generated billboard draw"};
   var clear=new CommandBuffer{name="GT explicit linear camera clear"};bool installed=false;
   try{
     Need(ren.sharedMaterials.SequenceEqual(mats)&&mats.All(x=>x==original)&&!ren.HasPropertyBlock());
     Need((block!=null)==(target!=null));
     if(block!=null)Need(block.GetTexture(property)==target&&original.HasProperty(property));
     ren.enabled=rendererPath&&kind!="clear";
     if(rendererPath&&kind=="marker")ren.sharedMaterials=mats.Select(x=>marker).ToArray();
     if(rendererPath&&block!=null){
       ren.SetPropertyBlock(block);installed=true;var check=new MaterialPropertyBlock();ren.GetPropertyBlock(check);Need(check.GetTexture(property)==target);
     }
     if(!rendererPath&&kind!="clear")b.DrawMesh(mesh,Matrix4x4.identity,kind=="marker"?marker:original,0,0,block);
     // Camera background color may be converted by the editor. Use an explicit
     // GPU clear before any opaque/transparent particle rendering, and verify
     // its output against a separately measured direct clear.
     clear.SetRenderTarget(BuiltinRenderTextureType.CameraTarget);
     clear.ClearRenderTarget(true,true,cam.backgroundColor);
     cam.AddCommandBuffer(CameraEvent.BeforeForwardOpaque,clear);
     cam.AddCommandBuffer(CameraEvent.BeforeForwardAlpha,b);cam.Render();
     WriteProbePixels(rt,path);
   }finally{
     cam.RemoveCommandBuffer(CameraEvent.BeforeForwardOpaque,clear);clear.Release();
     cam.RemoveCommandBuffer(CameraEvent.BeforeForwardAlpha,b);b.Release();
     if(installed)ren.SetPropertyBlock(null);
     ren.sharedMaterials=mats;ren.enabled=true;
   }
 }
 static RenderPath RenderPathCases(ParticleSystem ps,ParticleSystemRenderer ren,Mesh mesh,Camera cam,Material original,
                                  Material marker,string priv,int index,string mode,bool rendererPath,Input input,Texture2D[] textures){
   var r=new RenderPath{path=rendererPath?"renderer":"baked"};
   var mats=ren.sharedMaterials;var streams=new List<ParticleSystemVertexStream>();ren.GetActiveVertexStreams(streams);
   var before=new ParticleSystem.Particle[ps.particleCount];
   var oldPos=cam.transform.position;float oldSize=cam.orthographicSize,oldNear=cam.nearClipPlane,oldFar=cam.farClipPlane,oldAspect=cam.aspect;
   int oldMask=cam.cullingMask;Color oldColor=cam.backgroundColor;bool oldEnabled=ren.enabled,oldHdr=cam.allowHDR,oldMsaa=cam.allowMSAA;
   RenderTexture rt=null;bool srgb=GL.sRGBWrite;
   try{
     r.phase="frame";
     Need(before.Length>0&&before.Length<=256&&ps.GetParticles(before)==before.Length&&mats.Length==2&&mats.All(x=>x==original));
     Need(original!=null&&marker!=null&&original.shader!=marker.shader&&original.passCount==1&&marker.passCount==1);
     Need(!ren.HasPropertyBlock()&&textures.Length==4&&original.GetTexture(input.selected_property)==textures[0]);
     Frame(cam,rendererPath?LiveWorldBounds(ps,before):MeshBounds(mesh));
     cam.cullingMask=rendererPath?1<<ren.gameObject.layer:0;
     rt=new RenderTexture(64,64,24,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
     Need(rt.Create()&&!rt.sRGB&&rt.graphicsFormat==GraphicsFormat.R32G32B32A32_SFloat);
     cam.targetTexture=rt;GL.sRGBWrite=false;
     var backgrounds=new[]{new Color(.125f,.25f,.5f,.25f),new Color(.625f,.375f,.125f,.75f)};
     for(int bg=0;bg<2;bg++){
       cam.backgroundColor=backgrounds[bg];
       r.phase="reference";DirectReferenceClear(rt,backgrounds[bg],Path.Combine(priv,"emitter-"+index+"-"+mode+"-"+r.path+"-"+bg+"-reference.f32"));r.submissions++;
       foreach(var kind in new[]{"clear","native","repeat","marker","source","clone","zero","one","restored"}){
         r.phase=kind;var names=new[]{"source","clone","zero","one"};int ti=Array.IndexOf(names,kind);
         Texture2D target=ti<0?null:textures[ti];MaterialPropertyBlock block=null;
         if(target!=null){block=new MaterialPropertyBlock();block.SetTexture(input.selected_property,target);Need(block.GetTexture(input.selected_property)==target);}
         RenderEmitterCase(cam,ren,mesh,original,marker,mats,rendererPath,kind,rt,Path.Combine(priv,"emitter-"+index+"-"+mode+"-"+r.path+"-"+bg+"-"+kind+".f32"),block,input.selected_property,target);
         r.submissions++;if(block!=null)r.override_submissions++;
         Need(!ren.HasPropertyBlock()&&original.GetTexture(input.selected_property)==textures[0]);
       }
     }
     r.phase="post_draw";
     r.material_restored=ren.sharedMaterials.SequenceEqual(mats);
     var afterStreams=new List<ParticleSystemVertexStream>();ren.GetActiveVertexStreams(afterStreams);
     r.streams_unchanged=streams.SequenceEqual(afterStreams);r.particles_unchanged=ParticleStateEqual(ps,before);
     r.blocks_restored=!ren.HasPropertyBlock()&&original.GetTexture(input.selected_property)==textures[0];
     r.completed=r.submissions==20&&r.override_submissions==8&&r.blocks_restored&&r.material_restored&&r.streams_unchanged&&r.particles_unchanged;
     r.phase="complete";
   }catch(Exception e){r.failure_category=e.GetType().Name;}
   finally{
     cam.targetTexture=null;GL.sRGBWrite=srgb;ren.sharedMaterials=mats;ren.enabled=oldEnabled;
     cam.transform.position=oldPos;cam.orthographicSize=oldSize;cam.nearClipPlane=oldNear;cam.farClipPlane=oldFar;cam.aspect=oldAspect;
     cam.cullingMask=oldMask;cam.backgroundColor=oldColor;cam.allowHDR=oldHdr;cam.allowMSAA=oldMsaa;
     if(rt!=null){rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
   }
   return r;
 }
 static void RenderGenerated(ParticleSystem ps,ParticleSystemRenderer ren,Mesh mesh,Camera cam,Material original,string priv,int index,string mode,Input input){
   var ev=new RenderEvidence{index=index,mode=mode,particles=ps.particleCount,vertices=mesh.vertexCount,indices=(int)mesh.GetIndexCount(0)};
   Material marker=null;var textures=new Texture2D[4];
   try{
     var shader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTEmitterDrawMarker.shader");
     Need(shader!=null&&shader.isSupported&&shader.passCount==1&&ShaderUtil.GetShaderMessages(shader).All(x=>x.severity.ToString()!="Error"));
     marker=new Material(shader);
     textures[0]=original.GetTexture(input.selected_property) as Texture2D;
     Need(Id(textures[0],input.texture_guid,input.texture_id)&&SameSampler(textures[0],input));
     var raw=File.ReadAllBytes(Path.Combine(priv,"native-rgba.bytes"));Need(raw.Length==21844&&Sha(raw)==input.raw_sha);
     int[] alpha={-1,0,255};
     for(int k=0;k<3;k++)textures[k+1]=AlphaClone(input,raw,alpha[k]);
     ev.clone_payload_verified=Enumerable.Range(0,3).All(k=>AlphaClonePayload(textures[k+1],raw,alpha[k]));
     ev.clone_format_sampler_verified=textures.All(t=>t!=null&&t.width==64&&t.height==64&&t.mipmapCount==7&&t.graphicsFormat==textures[0].graphicsFormat&&SameSampler(t,input));
     Need(ev.clone_payload_verified&&ev.clone_format_sampler_verified);
     ev.paths=new[]{RenderPathCases(ps,ren,mesh,cam,original,marker,priv,index,mode,true,input,textures),
                    RenderPathCases(ps,ren,mesh,cam,original,marker,priv,index,mode,false,input,textures)};
   }catch(Exception){/* missing paths remain inconclusive in the independent verifier */}
   finally{
     if(marker!=null)UnityEngine.Object.DestroyImmediate(marker);
     for(int k=1;k<textures.Length;k++)if(textures[k]!=null)UnityEngine.Object.DestroyImmediate(textures[k]);
     File.WriteAllText(Path.Combine(priv,"emitter-"+index+"-"+mode+".json"),JsonUtility.ToJson(ev));
   }
 }
 static Bake Measure(ParticleSystem ps,ParticleSystemRenderer ren,Camera cam,Requirement[] req,bool renderBefore=false,string priv=null,int probeIndex=-2,Material drawMaterial=null,string drawMode=null,Input drawInput=null){
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
     if(priv!=null&&probeIndex>=0&&b.vertices==4&&b.indices==6&&drawMode!="natural")ProbeMesh(mesh,req,priv,probeIndex);
     if(priv!=null&&probeIndex>=0&&drawMaterial!=null&&drawMode!=null&&b.finite&&b.nondegenerate&&b.particles>0&&b.vertices==4*b.particles&&b.indices==6*b.particles)RenderGenerated(ps,ren,mesh,cam,drawMaterial,priv,probeIndex,drawMode,drawInput);
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
   if(method==5){
     ps.Play(false);ps.Clear(false);ps.Emit(1);ps.Simulate(1f/60f,false,false,false);ps.Pause(false);return;
   }
   // Seeded particle is a diagnostic of BakeMesh independent of Emit; never
   // admit it as proof of original emitter generation.
   Need(method==4);
   ps.Play(false);ps.Clear(false);ps.Pause(false);
   var p=new ParticleSystem.Particle{position=Vector3.zero,startLifetime=10f,remainingLifetime=10f,startSize=1f,startColor=new Color32(255,255,255,255),randomSeed=1};
   ps.SetParticles(new[]{p},1);
 }
 static bool SameParticleState(ParticleSystem.Particle a,ParticleSystem.Particle b){
   return a.position.Equals(b.position)&&a.velocity.Equals(b.velocity)&&a.axisOfRotation.Equals(b.axisOfRotation)
     &&a.rotation3D.Equals(b.rotation3D)&&a.angularVelocity3D.Equals(b.angularVelocity3D)
     &&a.startSize3D.Equals(b.startSize3D)&&a.startColor.Equals(b.startColor)&&Eq(a.startLifetime,b.startLifetime)
     &&Eq(a.remainingLifetime,b.remainingLifetime)&&a.randomSeed==b.randomSeed;
 }
 static bool Roundtrip(ParticleSystem ps){
   if(ps.particleCount!=1)return false;
   var emitted=new ParticleSystem.Particle[1];if(ps.GetParticles(emitted)!=1)return false;
   // Pass exactly the returned array without editing any particle field.
   var before=emitted[0];ps.SetParticles(emitted,1);
   var reread=new ParticleSystem.Particle[1];
   return ps.particleCount==1&&ps.GetParticles(reread)==1&&SameParticleState(before,reread[0]);
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
     if(method==6){
       EmitOne(ps,0);row.before_roundtrip=Measure(ps,ren,cam,req);
       row.roundtrip_state_equal=Roundtrip(ps);
     }else if(method==7){
       em.enabled=true;em.rateOverTime=0f;em.rateOverDistance=0f;
       em.SetBursts(new[]{new ParticleSystem.Burst(.05f,(short)1)});
       ps.Simulate(.2f,false,true,false);
     }else EmitOne(ps,method);
     row.one=Measure(ps,ren,cam,req,method==3);
   }catch(Exception e){row.failure_category=e.GetType().Name;}
   finally{if(cam!=null)UnityEngine.Object.DestroyImmediate(cam.gameObject);if(go!=null)UnityEngine.Object.DestroyImmediate(go);}
   return row;
 }
 static Row Observe(Case item,Input c,Config cfg,Material mat,string root,int method,string priv){
   var row=new Row{index=item.index,direct_method=method};Camera cam=null;
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
     ps.Simulate(1f,false,true,true);row.natural=Measure(ps,ren,cam,cfg.vertex_requirements,false,priv,item.index,mat,"natural",c);
     row.natural_particles=row.natural.particles;row.natural_vertices=row.natural.vertices;
     EmitOne(ps,method);row.forced=Measure(ps,ren,cam,cfg.vertex_requirements,method==3,priv,item.index,mat,"forced",c);
     if(row.forced.particles==1){
       row.roundtrip_state_equal=Roundtrip(ps);
       row.roundtrip=Measure(ps,ren,cam,cfg.vertex_requirements);
     }
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
       for(int k=0;k<2;k++)for(int m=0;m<8;m++){cases.Add(Control(k==0?mat:marker,cfg.vertex_requirements,k,m));r.calibration_cases=cases.ToArray();}
       foreach(int m in new[]{0,1,2,3,5}){
         var both=cases.Where(x=>x.method==m).ToArray();
         if(both.Length==2&&both.All(x=>Empty(x.empty)&&One(x.one))){r.selected_calibration_method=m;break;}
       }
       r.control_verified=r.selected_calibration_method>=0;
     }finally{if(marker!=null)UnityEngine.Object.DestroyImmediate(marker);}
     // Never promote manual seed or roundtrip to ordinary emission proof.
     r.phase="vertex_lane_control";r.lane_control_completed=ProbeControl(cfg.vertex_requirements,priv);
     r.phase="geometry";int method=r.control_verified?r.selected_calibration_method:0;
     r.rows=cfg.scenes.Select(x=>Observe(x,c,cfg,mat,root,method,priv)).ToArray();
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
