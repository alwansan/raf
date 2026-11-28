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
 const string Priv="/github/workspace/gt-fft-format-private";
 [Serializable] public class Row {public int slot,group;public string file,sha256,source_property,butterfly_property,target_property,dxbc_sha256;}
 [Serializable] public class Config {public string run_id,object_sha,indexed_sha,table_float_sha,table_half_sha;public Row[] rows;}
 [Serializable] public class Case {
   public int first_slot,seed,dispatches,bindings,sentinel_checks,nonfinite_components;
   public string format,outcome="MANAGED_FAILURE",failure_type;public bool target_format_exact,table_gpu_exact;
   public int[] indexed_written=new int[2],reference_written=new int[2],coverage_mismatch=new int[2],different_over_tolerance=new int[2],exact_different=new int[2];
 }
 [Serializable] public class Receipt {
   public string status="INCONCLUSIVE",phase="environment",run_id,config_sha256,failure_type;
   public bool private_guard,vulkan,private_source_hashes_match;
   public int registration_count;public Case[] cases=new Case[8];
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
 static Texture2D Seed(int seed,int role){
   var t=new Texture2D(Size,Size,TextureFormat.RGBAFloat,false,true);
   t.filterMode=FilterMode.Point;t.wrapMode=TextureWrapMode.Clamp;
   var p=new Color[Count];
   for(int y=0;y<Size;y++)for(int x=0;x<Size;x++){
     int n=(x*17+y*29+seed*19+role*37+7)%1021;
     p[y*Size+x]=new Color((n-510)/1024f,(n%113-56)/256f,(n%59-29)/128f,1);
   }
   t.SetPixels(p);t.Apply(false,false);return t;
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
   string file=Path.Combine(Priv,half?"table-half.f32":"table-float.f32");
   Need(Sha(file)==(half?m.table_half_sha:m.table_float_sha));var pixels=new Color[Size*Stages];
   using(var stream=new BinaryReader(File.OpenRead(file))){
     Need(stream.BaseStream.Length==pixels.Length*16);
     for(int i=0;i<pixels.Length;i++)pixels[i]=new Color(stream.ReadSingle(),stream.ReadSingle(),stream.ReadSingle(),stream.ReadSingle());
   }
   var t=new Texture2D(Size,Stages,half?TextureFormat.RGBAHalf:TextureFormat.RGBAFloat,false,true);
   try{
     t.filterMode=FilterMode.Point;t.wrapMode=TextureWrapMode.Clamp;t.SetPixels(pixels);t.Apply(false,false);
     Need(t.graphicsFormat==(half?GraphicsFormat.R16G16B16A16_SFloat:GraphicsFormat.R32G32B32A32_SFloat)&&t.mipmapCount==1);
     var req=AsyncGPUReadback.Request(t,0,TextureFormat.RGBAFloat);req.WaitForCompletion();Need(!req.hasError);
     var data=req.GetData<Color>();Need(data.Length==pixels.Length);
     for(int i=0;i<pixels.Length;i++)for(int c=0;c<4;c++)Need(data[i][c]==pixels[i][c]);
     r.table_gpu_exact=true;return t;
   }catch{Dispose(t);throw;}
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
 static void Compare(RenderTexture indexed,RenderTexture reference,Case r,int pass){
   var a=Read(indexed);var b=Read(reference);Need(a.Length==Count&&b.Length==Count);
   for(int i=0;i<a.Length;i++){
     Color x=a[i],y=b[i];bool u=Written(x,r),v=Written(y,r);
     if(u)r.indexed_written[pass]++;if(v)r.reference_written[pass]++;
     if(u!=v)r.coverage_mismatch[pass]++;
     bool different=false,exact=false;
     for(int c=0;c<Lanes(r);c++){
       if(!Finite(x[c])||!Finite(y[c]))r.nonfinite_components++;
       if(x[c]!=y[c])exact=true;
       if(Diff(x[c],y[c]))different=true;
     }
     if(exact)r.exact_different[pass]++;if(different)r.different_over_tolerance[pass]++;
   }
 }
 static void Dispose(UnityEngine.Object o){if(o is RenderTexture t)t.Release();if(o!=null)UnityEngine.Object.DestroyImmediate(o);}
 static Case Pair(ComputeShader indexed,ComputeShader[] refs,Config m,int offset,string format){
   int seed=19;var rows=m.rows;var r=new Case{first_slot=rows[offset].slot,seed=seed,format=format};
   Texture2D a=null,b=null;RenderTexture i0=null,i1=null,j0=null,j1=null;
   try{
     Mark("paired_dispatch","allocate",r.first_slot,r.seed);
     var f=(RenderTextureFormat)Enum.Parse(typeof(RenderTextureFormat),format);var expected=Expected(format);
     if(!SystemInfo.SupportsRenderTextureFormat(f)||!SystemInfo.IsFormatSupported(expected,FormatUsage.LoadStore)){r.outcome="UNSUPPORTED";return r;}
     a=Seed(seed,0);b=Table(m,format.EndsWith("Half",StringComparison.Ordinal),r);
     i0=Target(f,expected);i1=Target(f,expected);j0=Target(f,expected);j1=Target(f,expected);r.target_format_exact=true;
     Mark("paired_dispatch","sentinel",r.first_slot,r.seed);
     Clear(i0,r);Clear(i1,r);Clear(j0,r);Clear(j1,r);
     for(int pass=0;pass<2;pass++){
       var row=rows[offset+pass];var reference=refs[offset+pass];
       Dispatch(indexed,row.slot,"_SourceTex","_ButterflyTex","_TargetTex",pass==0?(Texture)a:i0,b,pass==0?i0:i1,r,pass,0);
       Dispatch(reference,reference.FindKernel("main"),row.source_property,row.butterfly_property,row.target_property,pass==0?(Texture)a:j0,b,pass==0?j0:j1,r,pass,1);
       Mark("paired_dispatch","compare",r.first_slot,r.seed,pass,-1,r.bindings,r.dispatches);
       Compare(pass==0?i0:i1,pass==0?j0:j1,r,pass);
     }
     r.outcome="OBSERVED";return r;
   }catch(Exception e){r.failure_type=e.GetType().Name;return r;}
   finally{foreach(var o in new UnityEngine.Object[]{a,b,i0,i1,j0,j1})Dispose(o);}
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
     r.phase="paired_dispatch";int index=0;
     foreach(int offset in new[]{0,2})foreach(string format in new[]{"RGHalf","RGFloat","ARGBHalf","ARGBFloat"})r.cases[index++]=Pair(shader,refs,m,offset,format);
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
