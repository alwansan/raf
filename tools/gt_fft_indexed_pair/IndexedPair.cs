// Isolated source-derived dispatch, no game or player.
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
public static class GTIndexedPair {
 const int Size=1024, Count=Size*Size; const float Sentinel=8192f;
 const string Priv="/github/workspace/gt-fft-pair-private";
 [Serializable] public class Row {public int slot,group;public string file,sha256,source_property,butterfly_property,target_property,dxbc_sha256;}
 [Serializable] public class Config {public string run_id,object_sha,indexed_sha;public Row[] rows;}
 [Serializable] public class Case {
   public int first_slot,seed,dispatches,bindings,sentinel_checks,nonfinite_components;
   public int[] indexed_written=new int[2],reference_written=new int[2],coverage_mismatch=new int[2],different_over_tolerance=new int[2],exact_different=new int[2];
 }
 [Serializable] public class Receipt {
   public string status="INCONCLUSIVE",phase="environment",run_id,config_sha256,failure_type;
   public bool private_guard,vulkan,private_source_hashes_match;
   public int registration_count;public Case[] cases=new Case[4];
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
 static RenderTexture Target(){
   var t=new RenderTexture(Size,Size,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);
   t.enableRandomWrite=true;t.filterMode=FilterMode.Point;t.wrapMode=TextureWrapMode.Clamp;Need(t.Create());return t;
 }
 static Color[] Read(RenderTexture t){
   var old=RenderTexture.active;var data=new Texture2D(Size,Size,TextureFormat.RGBAFloat,false,true);
   try{RenderTexture.active=t;data.ReadPixels(new Rect(0,0,Size,Size),0,0,false);data.Apply(false,false);return data.GetPixels();}
   finally{RenderTexture.active=old;UnityEngine.Object.DestroyImmediate(data);}
 }
 static bool Written(Color c){return c.r!=Sentinel||c.g!=Sentinel||c.b!=Sentinel||c.a!=Sentinel;}
 static void Clear(RenderTexture t,Case r){
   var old=RenderTexture.active;try{RenderTexture.active=t;GL.Clear(true,true,new Color(Sentinel,Sentinel,Sentinel,Sentinel));}
   finally{RenderTexture.active=old;}
   var a=Read(t);Need(a.Length==Count);foreach(var c in a)Need(!Written(c));r.sentinel_checks++;
 }
 static void Dispatch(ComputeShader shader,int kernel,string source,string butterfly,string target,Texture input,Texture b,RenderTexture output,Case r){
   Need(input!=null&&b!=null&&output!=null&&input!=b&&input!=output&&b!=output);
   shader.SetTexture(kernel,source,input);r.bindings++;
   shader.SetTexture(kernel,butterfly,b);r.bindings++;
   shader.SetTexture(kernel,target,output);r.bindings++;
   shader.Dispatch(kernel,1,2,1);r.dispatches++;
 }
 static bool Diff(float a,float b){return Mathf.Abs(a-b)>Mathf.Max(1e-5f,1e-5f*Mathf.Max(Mathf.Abs(a),Mathf.Abs(b)));}
 static void Compare(RenderTexture indexed,RenderTexture reference,Case r,int pass){
   var a=Read(indexed);var b=Read(reference);Need(a.Length==Count&&b.Length==Count);
   for(int i=0;i<a.Length;i++){
     Color x=a[i],y=b[i];bool u=Written(x),v=Written(y);
     if(u)r.indexed_written[pass]++;if(v)r.reference_written[pass]++;
     if(u!=v)r.coverage_mismatch[pass]++;
     bool different=false,exact=false;
     for(int c=0;c<4;c++){
       if(!Finite(x[c])||!Finite(y[c]))r.nonfinite_components++;
       if(x[c]!=y[c])exact=true;
       if(Diff(x[c],y[c]))different=true;
     }
     if(exact)r.exact_different[pass]++;if(different)r.different_over_tolerance[pass]++;
   }
 }
 static void Dispose(UnityEngine.Object o){if(o is RenderTexture t)t.Release();if(o!=null)UnityEngine.Object.DestroyImmediate(o);}
 static Case Pair(ComputeShader indexed,ComputeShader[] refs,Row[] rows,int offset,int seed){
   var r=new Case{first_slot=rows[offset].slot,seed=seed};
   Texture2D a=null,b=null;RenderTexture i0=null,i1=null,j0=null,j1=null;
   try{
     a=Seed(seed,0);b=Seed(seed,1);i0=Target();i1=Target();j0=Target();j1=Target();
     Clear(i0,r);Clear(i1,r);Clear(j0,r);Clear(j1,r);
     for(int pass=0;pass<2;pass++){
       var row=rows[offset+pass];var reference=refs[offset+pass];
       Dispatch(indexed,row.slot,"_SourceTex","_ButterflyTex","_TargetTex",pass==0?(Texture)a:i0,b,pass==0?i0:i1,r);
       Dispatch(reference,reference.FindKernel("main"),row.source_property,row.butterfly_property,row.target_property,pass==0?(Texture)a:j0,b,pass==0?j0:j1,r);
       Compare(pass==0?i0:i1,pass==0?j0:j1,r,pass);
     }
     return r;
   }finally{foreach(var o in new UnityEngine.Object[]{a,b,i0,i1,j0,j1})Dispose(o);}
 }
 public static void Run(){
   var r=new Receipt();try{
     r.run_id=Arg("-gtFftRunId");
     Need(Application.isBatchMode&&Application.unityVersion=="2021.3.45f2"&&File.ReadAllText(Path.Combine(Priv,"editor-output-private")).Trim()==r.run_id);
     r.private_guard=true;r.vulkan=SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan;
     Need(r.vulkan&&SystemInfo.supportsComputeShaders&&SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat));
     r.phase="private_import";
     string cfg=Path.Combine(Priv,"config.json");r.config_sha256=Sha(cfg);var m=JsonUtility.FromJson<Config>(File.ReadAllText(cfg));
     Need(m.run_id==r.run_id&&m.object_sha=="9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247"&&m.rows.Length==4);
     Directory.CreateDirectory(Path.Combine(Application.dataPath,"Private"));Copy("indexed.compute",m.indexed_sha);
     int[] slots={6,7,16,17};for(int i=0;i<4;i++){Need(m.rows[i].slot==slots[i]&&m.rows[i].group==512);Copy(m.rows[i].file,m.rows[i].sha256);}
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     var shader=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/Private/indexed.compute");Need(shader!=null);
     for(int i=0;i<20;i++){
       string n="RaftFftSlot"+i.ToString("00");Need(shader.HasKernel(n)&&shader.FindKernel(n)==i);
       shader.GetKernelThreadGroupSizes(i,out uint x,out uint y,out uint z);Need(x==(64u<<(i%10/2))&&y==1&&z==1);r.registration_count++;
     }
     var refs=new ComputeShader[4];
     for(int i=0;i<4;i++){
       refs[i]=AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/Private/"+m.rows[i].file);Need(refs[i]!=null&&refs[i].HasKernel("main"));
       refs[i].GetKernelThreadGroupSizes(refs[i].FindKernel("main"),out uint x,out uint y,out uint z);Need(x==512&&y==1&&z==1);
     }
     r.phase="paired_dispatch";int index=0;
     foreach(int offset in new[]{0,2})foreach(int seed in new[]{0,19})r.cases[index++]=Pair(shader,refs,m.rows,offset,seed);
     r.phase="identity";
     Need(Sha(Path.Combine(Application.dataPath,"Private","indexed.compute"))==m.indexed_sha);
     foreach(var row in m.rows)Need(Sha(Path.Combine(Application.dataPath,"Private",row.file))==row.sha256);
     foreach(var s in new[]{shader,refs[0],refs[1],refs[2],refs[3]})foreach(var e in ShaderUtil.GetComputeShaderMessages(s))Need(e.severity.ToString()!="Error");
     r.private_source_hashes_match=true;r.phase="complete";r.status="PASS";
   }catch(Exception e){r.failure_type=e.GetType().Name;}
   File.WriteAllText(Path.Combine(Priv,"receipt.json"),JsonUtility.ToJson(r));
   EditorApplication.Exit(r.status=="PASS"?0:2);
 }
}
