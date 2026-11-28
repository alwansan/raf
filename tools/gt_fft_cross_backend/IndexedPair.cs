// Isolated source-derived dispatch, no game or player.
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Experimental.Rendering;
public static class GTIndexedPair {
 const int Size=512, Count=Size*Size, Stages=8; const float Sentinel=8192f;
 const string Priv="/github/workspace/gt-fft-bank-private";
 [Serializable] public class Row {public int slot,group;public string file,sha256,source_property,butterfly_property,target_property,dxbc_sha256;}
 [Serializable] public class Config {public string run_id,object_sha,indexed_sha,table_float_sha,table_half_sha;public Row[] rows;}
 [Serializable] public class Case {
   public int first_slot,seed,dispatches,bindings,sentinel_checks,nonfinite_components,snapshots;public bool injected_gpu_exact,replay_gpu_exact;
   public string format,input_mode,outcome="MANAGED_FAILURE",failure_type,failure_phase;public bool target_format_exact,table_gpu_exact,input_gpu_exact;
   public int[] indexed_class_counts=new int[32],reference_class_counts=new int[32],class_mismatch=new int[2],native_vs_converted_class_mismatch=new int[2],gpu_vs_native_class_mismatch=new int[2],finite_different=new int[2],finite_over_tolerance=new int[2],raw_bit_different=new int[2];
   public int[] indexed_written=new int[2],reference_written=new int[2],coverage_mismatch=new int[2],different_over_tolerance=new int[2],exact_different=new int[2];
 }
 [Serializable] public class Receipt {
   public string status="INCONCLUSIVE",phase="environment",run_id,config_sha256,failure_type;
   public bool private_guard,vulkan,private_source_hashes_match;
   public int registration_count,class_control_pixels;public bool class_control_verified;public string class_control_sha256;public Case[] cases=new Case[4];public string graphics_device_version;
 }
 [Serializable] public class Progress {public string run_id,phase,operation;public int first_slot=-1,seed=-1,pass=-1,variant=-1,bindings,dispatches;}
 static Progress progress;
 static void Mark(string phase,string operation,int first=-1,int seed=-1,int pass=-1,int variant=-1,int binds=0,int dispatches=0){
   if(progress==null)return;
   progress.phase=phase;progress.operation=operation;progress.first_slot=first;progress.seed=seed;progress.pass=pass;
   progress.variant=variant;progress.bindings=binds;progress.dispatches=dispatches;
   string file=Path.Combine(Priv,"progress.json"),tmp=file+".tmp";
   File.WriteAllText(tmp,JsonUtility.ToJson(progress));
   if(File.Exists(file))File.Replace(tmp,file,null);else File.Move(tmp,file);
 }
 static void Need(bool ok){if(!ok)throw new InvalidOperationException();}
 static string Sha(string p){using(var s=SHA256.Create())using(var f=File.OpenRead(p))return BitConverter.ToString(s.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
 static string Arg(string name){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,name);Need(i>=0&&i+1<a.Length);return a[i+1];}
 static void Copy(string file,string hash){
   string src=Path.Combine(Priv,file),dst=Path.Combine(Application.dataPath,"Private",file);
   Need(Sha(src)==hash&&!File.Exists(dst));File.Copy(src,dst);Need(Sha(dst)==hash);
 }
 static bool Finite(float x){return !float.IsNaN(x)&&!float.IsInfinity(x);}
 static Texture2D ExactTexture(string path,int height) {
   Need(BitConverter.IsLittleEndian);
   byte[] bytes=File.ReadAllBytes(path);Need(bytes.Length==Size*height*16);
   var t=new Texture2D(Size,height,TextureFormat.RGBAFloat,false,true);
   try {
     t.filterMode=FilterMode.Point;t.wrapMode=TextureWrapMode.Clamp;
     Need(t.graphicsFormat==GraphicsFormat.R32G32B32A32_SFloat&&t.mipmapCount==1);
     uint[] data=new uint[bytes.Length/4];Buffer.BlockCopy(bytes,0,data,0,bytes.Length);
     t.SetPixelData(data,0);t.Apply(false,false);
     var gpu=NativeBits(t);Need(gpu.Length==data.Length);
     for(int i=0;i<data.Length;i++)Need(gpu[i]==data[i]);
     return t;
   }catch{Dispose(t);throw;}
 }
 static Texture2D Seed(int seed,int role,string mode,Case r){
   Need(seed==19&&role==0&&(mode=="signed"||mode=="zero"));
   var t=ExactTexture(Path.Combine(Priv,"source-"+mode+".rgba32f"),Size);
   r.input_gpu_exact=true;return t;
 }
 static GraphicsFormat Expected(string f){
   switch(f){case "RGHalf":return GraphicsFormat.R16G16_SFloat;case "RGFloat":return GraphicsFormat.R32G32_SFloat;
   case "ARGBHalf":return GraphicsFormat.R16G16B16A16_SFloat;case "ARGBFloat":return GraphicsFormat.R32G32B32A32_SFloat;default:throw new InvalidOperationException();}
 }
 static RenderTexture Target(RenderTextureFormat f,GraphicsFormat expected){
   var t=new RenderTexture(Size,Size,0,f,RenderTextureReadWrite.Linear);
   t.enableRandomWrite=true;t.filterMode=FilterMode.Point;t.wrapMode=TextureWrapMode.Clamp;
   if(!t.Create()||t.graphicsFormat!=expected){t.Release();UnityEngine.Object.DestroyImmediate(t);throw new InvalidOperationException();}
   return t;
 }
 static Texture2D Table(Config m,bool half,Case r){
   Need(!half);string path=Path.Combine(Priv,"table-float.f32");Need(Sha(path)==m.table_float_sha);
   var t=ExactTexture(path,Stages);r.table_gpu_exact=true;return t;
 }
 static Color[] Read(RenderTexture t){
   var req=AsyncGPUReadback.Request(t,0,TextureFormat.RGBAFloat);req.WaitForCompletion();Need(!req.hasError);
   return req.GetData<Color>().ToArray();
 }
 static int Lanes(Case r){return r.format=="RGHalf"||r.format=="RGFloat"?2:4;}
 static bool Written(Color c,Case r){for(int i=0;i<Lanes(r);i++)if(c[i]!=Sentinel)return true;return false;}
 static void Clear(RenderTexture t,Case r){
   var old=RenderTexture.active;try{RenderTexture.active=t;GL.Clear(true,true,new Color(Sentinel,Sentinel,Sentinel,Sentinel));}
   finally{RenderTexture.active=old;}
   var a=Read(t);Need(a.Length==Count);foreach(var c in a)Need(!Written(c,r));r.sentinel_checks++;
 }
 static void Dispatch(ComputeShader shader,int kernel,string source,string butterfly,string target,Texture input,Texture b,RenderTexture output,Case r,int pass,int variant){
   Need(input!=null&&b!=null&&output!=null&&input!=b&&input!=output&&b!=output);
   Mark("paired_dispatch","bind_source",r.first_slot,r.seed,pass,variant,r.bindings,r.dispatches);
   shader.SetTexture(kernel,source,input);r.bindings++;
   Mark("paired_dispatch","bind_butterfly",r.first_slot,r.seed,pass,variant,r.bindings,r.dispatches);
   shader.SetTexture(kernel,butterfly,b);r.bindings++;
   Mark("paired_dispatch","bind_target",r.first_slot,r.seed,pass,variant,r.bindings,r.dispatches);
   shader.SetTexture(kernel,target,output);r.bindings++;
   Mark("paired_dispatch","dispatch",r.first_slot,r.seed,pass,variant,r.bindings,r.dispatches);
   shader.Dispatch(kernel,1,Size,1);r.dispatches++;
   Mark("paired_dispatch","dispatch_returned",r.first_slot,r.seed,pass,variant,r.bindings,r.dispatches);
 }
 static bool Diff(float a,float b){return Mathf.Abs(a-b)>Mathf.Max(1e-5f,1e-5f*Mathf.Max(Mathf.Abs(a),Mathf.Abs(b)));}
 static ComputeShader classifier;
 static uint Bits(float x){return unchecked((uint)BitConverter.SingleToInt32Bits(x));}
 static int Class(uint b){return (b&0x7f800000u)!=0x7f800000u?0:((b&0x007fffffu)!=0?1:((b&0x80000000u)==0?2:3));}
 static uint[] NativeBits(Texture t){var req=AsyncGPUReadback.Request(t,0);req.WaitForCompletion();Need(!req.hasError);return req.GetData<uint>().ToArray();}
 static uint[] GpuClasses(Texture t){
   var buffer=new ComputeBuffer(Count*4,4);
   try{int k=classifier.FindKernel("Classify");classifier.SetTexture(k,"InputTex",t);classifier.SetBuffer(k,"Classes",buffer);
     classifier.Dispatch(k,Size/8,Size/8,1);var values=new uint[Count*4];buffer.GetData(values);return values;
   }finally{buffer.Release();}
 }
 static void ClassControl(Receipt r){
   classifier=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/Editor/Classify.compute");Need(classifier!=null);
   r.class_control_sha256=Sha(Path.Combine(Application.dataPath,"Editor/Classify.compute"));
   var t=new Texture2D(Size,Size,TextureFormat.RGBAFloat,false,true);
   try{
     uint[] raw=new uint[Count*4];for(int i=0;i<Count;i++){raw[4*i]=0x3f800000;raw[4*i+1]=0x7fc12345;raw[4*i+2]=0x7f800000;raw[4*i+3]=0xff800000;}
     t.SetPixelData(raw,0);t.Apply(false,false);var native=NativeBits(t);var gpu=GpuClasses(t);
     Need(native.Length==raw.Length&&gpu.Length==raw.Length);
     for(int i=0;i<raw.Length;i++)Need(Class(native[i])==i%4&&gpu[i]==(uint)(i%4));
     r.class_control_pixels=Count;r.class_control_verified=true;
   }finally{Dispose(t);}
 }
 static void Compare(RenderTexture indexed,RenderTexture reference,Case r,int pass){
   var a=Read(indexed);var b=Read(reference);Need(a.Length==Count&&b.Length==Count);
   var ab=NativeBits(indexed);var bb=NativeBits(reference);var ac=GpuClasses(indexed);var bc=GpuClasses(reference);
   Need(ab.Length==Count*4&&bb.Length==ab.Length&&ac.Length==ab.Length&&bc.Length==ab.Length);
   for(int i=0;i<a.Length;i++){
     Color x=a[i],y=b[i];bool u=Written(x,r),v=Written(y,r);
     if(u)r.indexed_written[pass]++;if(v)r.reference_written[pass]++;
     if(u!=v)r.coverage_mismatch[pass]++;
     bool different=false,exact=false;
     for(int c=0;c<Lanes(r);c++){
       int k=i*4+c,ix=Class(ab[k]),iy=Class(bb[k]);
       r.indexed_class_counts[pass*16+c*4+ix]++;r.reference_class_counts[pass*16+c*4+iy]++;
       if(ix!=Class(Bits(x[c])))r.native_vs_converted_class_mismatch[pass]++;
       if(iy!=Class(Bits(y[c])))r.native_vs_converted_class_mismatch[pass]++;
       if(ac[k]!=(uint)ix)r.gpu_vs_native_class_mismatch[pass]++;
       if(bc[k]!=(uint)iy)r.gpu_vs_native_class_mismatch[pass]++;
       if(ab[k]!=bb[k])r.raw_bit_different[pass]++;
       if(ix!=iy)r.class_mismatch[pass]++;
       if(ix!=0||iy!=0)r.nonfinite_components++;
       else {if(x[c]!=y[c]){r.finite_different[pass]++;exact=true;}if(Diff(x[c],y[c])){r.finite_over_tolerance[pass]++;different=true;}}
     }
     if(exact)r.exact_different[pass]++;if(different)r.different_over_tolerance[pass]++;
   }
 }
 static void Dispose(UnityEngine.Object o){if(o is RenderTexture t)t.Release();if(o!=null)UnityEngine.Object.DestroyImmediate(o);}
 static string Snapshot(RenderTexture t,Case r,string label) {
   uint[] raw=NativeBits(t);Need(raw.Length==Count*4);
   for(int i=0;i<Count;i++)Need(raw[4*i]!=0x46000000u||raw[4*i+1]!=0x46000000u||raw[4*i+2]!=0x46000000u||raw[4*i+3]!=0x46000000u);
   byte[] bytes=new byte[raw.Length*4];Buffer.BlockCopy(raw,0,bytes,0,bytes.Length);
   string path=Path.Combine(Priv,"unity-"+r.first_slot+"-"+r.input_mode+"-"+label+".rgba32f");
   Need(!File.Exists(path));File.WriteAllBytes(path,bytes);r.snapshots++;return path;
 }
 static Case Pair(ComputeShader indexed,ComputeShader[] refs,Config m,int offset,string mode){
   const string format="ARGBFloat";const int seed=19;var rows=m.rows;
   var r=new Case{first_slot=rows[offset].slot,seed=seed,format=format,input_mode=mode};
   Texture2D a=null,b=null,cpu=null,ownI=null,ownJ=null;
   var targets=new RenderTexture[8];
   try {
     r.failure_phase="allocate";Mark("cross_dispatch","allocate",r.first_slot,r.seed);
     var f=RenderTextureFormat.ARGBFloat;var expected=Expected(format);
     if(!SystemInfo.SupportsRenderTextureFormat(f)||!SystemInfo.IsFormatSupported(expected,FormatUsage.LoadStore)){r.outcome="UNSUPPORTED";return r;}
     r.failure_phase="exact_source_table";a=Seed(seed,0,mode,r);b=Table(m,false,r);
     for(int i=0;i<targets.Length;i++){targets[i]=Target(f,expected);Clear(targets[i],r);}r.target_format_exact=true;
     r.failure_phase="first_dispatch";var p0=rows[offset];var p1=rows[offset+1];var j0=refs[offset];var j1=refs[offset+1];
     Dispatch(indexed,p0.slot,"_SourceTex","_ButterflyTex","_TargetTex",a,b,targets[0],r,0,0);
     Dispatch(j0,j0.FindKernel("main"),p0.source_property,p0.butterfly_property,p0.target_property,a,b,targets[1],r,0,1);
     // Synchronous native readback is the explicit completion point before any second-stage dispatch.
     r.failure_phase="first_snapshot";string firstI=Snapshot(targets[0],r,"indexed0"),firstJ=Snapshot(targets[1],r,"standalone0");
     Texture[] inputs={targets[0],targets[1],null,null,null,null};
     string[] labels={"indexed-chain","standalone-chain","indexed-cpu","standalone-cpu","indexed-replay","standalone-replay"};
     for(int i=0;i<inputs.Length;i++){
       // Preserve both chained and CPU-fed observations even if NaN payloads
       // cannot be uploaded losslessly to a Texture2D during own-stage replay.
       if(i==2){
         r.failure_phase="exact_cpu_replay_upload";Mark("cross_dispatch",r.failure_phase,r.first_slot,r.seed,1,i,r.bindings,r.dispatches);
         cpu=ExactTexture(Path.Combine(Priv,"cpu-"+r.first_slot+"-"+mode+"-p0.rgba32f"),Size);
         r.injected_gpu_exact=true;inputs[2]=inputs[3]=cpu;
       }
       if(i==4){
         r.failure_phase="exact_unity_replay_upload";Mark("cross_dispatch",r.failure_phase,r.first_slot,r.seed,1,i,r.bindings,r.dispatches);
         ownI=ExactTexture(firstI,Size);ownJ=ExactTexture(firstJ,Size);
         r.replay_gpu_exact=true;inputs[4]=ownI;inputs[5]=ownJ;
       }
       r.failure_phase=labels[i];
       if(i%2==0)Dispatch(indexed,p1.slot,"_SourceTex","_ButterflyTex","_TargetTex",inputs[i],b,targets[i+2],r,1,i);
       else Dispatch(j1,j1.FindKernel("main"),p1.source_property,p1.butterfly_property,p1.target_property,inputs[i],b,targets[i+2],r,1,i);
       Snapshot(targets[i+2],r,labels[i]);
     }
     r.failure_phase=null;r.outcome="OBSERVED";return r;
   }catch(Exception e){r.failure_type=e.GetType().Name;return r;}
   finally {foreach(var o in targets)Dispose(o);foreach(var o in new UnityEngine.Object[]{a,b,cpu,ownI,ownJ})Dispose(o);}
 }
 public static void Run(){
   var r=new Receipt();try{
     r.run_id=Arg("-gtFftRunId");
     Need(Application.isBatchMode&&Application.unityVersion=="2021.3.45f2"&&File.ReadAllText(Path.Combine(Priv,"editor-output-private")).Trim()==r.run_id);
     r.private_guard=true;progress=new Progress{run_id=r.run_id};Mark("environment","managed_entry");
     r.vulkan=SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan;
     Need(r.vulkan&&SystemInfo.supportsComputeShaders&&SystemInfo.supportsAsyncGPUReadback);
     r.phase="private_import";Mark("private_import","copy");
     string cfg=Path.Combine(Priv,"config.json");r.config_sha256=Sha(cfg);var m=JsonUtility.FromJson<Config>(File.ReadAllText(cfg));
     Need(m.run_id==r.run_id&&m.object_sha=="9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247"&&m.rows.Length==4);
     Directory.CreateDirectory(Path.Combine(Application.dataPath,"Private"));Copy("indexed.compute",m.indexed_sha);
     int[] slots={6,7,16,17};for(int i=0;i<4;i++){Need(m.rows[i].slot==slots[i]&&m.rows[i].group==512);Copy(m.rows[i].file,m.rows[i].sha256);}
     Mark("private_import","refresh");AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     Mark("private_import","load_indexed");var shader=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/Private/indexed.compute");Need(shader!=null);
     Mark("private_import","register");for(int i=0;i<20;i++){
       string n="RaftFftSlot"+i.ToString("00");Need(shader.HasKernel(n)&&shader.FindKernel(n)==i);
       shader.GetKernelThreadGroupSizes(i,out uint x,out uint y,out uint z);Need(x==(64u<<(i%10/2))&&y==1&&z==1);r.registration_count++;
     }
     Mark("private_import","load_references");var refs=new ComputeShader[4];
     for(int i=0;i<4;i++){
       refs[i]=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/Private/"+m.rows[i].file);Need(refs[i]!=null&&refs[i].HasKernel("main"));
       refs[i].GetKernelThreadGroupSizes(refs[i].FindKernel("main"),out uint x,out uint y,out uint z);Need(x==512&&y==1&&z==1);
     }
     r.graphics_device_version=SystemInfo.graphicsDeviceVersion;
     r.phase="paired_dispatch";int index=0;
     foreach(int offset in new[]{0,2})foreach(string mode in new[]{"signed","zero"})r.cases[index++]=Pair(shader,refs,m,offset,mode);
     r.phase="identity";Mark("identity","validate");
     Need(Sha(Path.Combine(Application.dataPath,"Private","indexed.compute"))==m.indexed_sha);
     foreach(var row in m.rows)Need(Sha(Path.Combine(Application.dataPath,"Private",row.file))==row.sha256);
     foreach(var s in new[]{shader,refs[0],refs[1],refs[2],refs[3]})foreach(var e in ShaderUtil.GetComputeShaderMessages(s))Need(e.severity.ToString()!="Error");
     r.private_source_hashes_match=true;r.phase="complete";r.status="PASS";Mark("complete","receipt");
   }catch(Exception e){r.failure_type=e.GetType().Name;}
   File.WriteAllText(Path.Combine(Priv,"receipt.json"),JsonUtility.ToJson(r));
   EditorApplication.Exit(r.status=="PASS"?0:2);
 }
}
