// Private diagnostic surface, original assets staged only after log guard.
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
   public Asset[] assets;public Slot[] slots;public Number[] numbers;public int[] sampler,sizes;public int backgrounds;public float bias;}
 [Serializable] class Receipt {public string run_id,phase="environment",status="INCONCLUSIVE",unity_version,backend,color_space,failure_category="";
   public bool private_log_guard,shader_identity,material_identity,material_shader_identity,native_identity,native_descriptor,native_sampler,
     texture_refs,uv_matches,numbers_match,clone_sampler_match,clone_payload_verified;
   public int asset_identities,asset_bytes_unchanged,meta_bytes_unchanged,shader_errors,numbers_declared,numbers_matched,draw_cases;}
 static void Need(bool x){if(!x)throw new InvalidOperationException("GT particle draw gate");}
 static string Arg(string n){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,n);return i>=0&&i+1<a.Length?a[i+1]:"";}
 static string Sha(byte[] x){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(x)).Replace("-","").ToLowerInvariant();}
 static bool Id(UnityEngine.Object obj,string g,long f){return obj!=null&&AssetDatabase.TryGetGUIDAndLocalFileIdentifier(obj,out string gg,out long ff)&&gg==g&&ff==f;}
 static bool Eq(float a,float b){return BitConverter.ToInt32(BitConverter.GetBytes(a),0)==BitConverter.ToInt32(BitConverter.GetBytes(b),0);}
 static int Errors(Shader s){return ShaderUtil.GetShaderMessages(s).Count(x=>x.severity.ToString()=="Error");}
 static bool Sampler(Texture2D t,Input c){return c.sampler.Length==5&&(int)t.filterMode==c.sampler[0]&&t.anisoLevel==c.sampler[1]&&
   (int)t.wrapModeU==c.sampler[2]&&(int)t.wrapModeV==c.sampler[3]&&(int)t.wrapModeW==c.sampler[4]&&Eq(t.mipMapBias,c.bias);}
 static Texture2D Clone(Input c,byte[] raw,int force){
   var t=new Texture2D(64,64,TextureFormat.RGBA32,true,false);
   t.filterMode=(FilterMode)c.sampler[0];t.anisoLevel=c.sampler[1];t.wrapModeU=(TextureWrapMode)c.sampler[2];t.wrapModeV=(TextureWrapMode)c.sampler[3];t.wrapModeW=(TextureWrapMode)c.sampler[4];t.mipMapBias=c.bias;
   int pos=0;
   for(int m=0;m<7;m++){int n=64>>m;byte[] b=new byte[n*n*4];Buffer.BlockCopy(raw,pos,b,0,b.Length);pos+=b.Length;
     if(force>=0)for(int i=3;i<b.Length;i+=4)b[i]=(byte)force;
     t.SetPixelData(b,m);}
   Need(pos==raw.Length);t.Apply(false,false);return t;
 }
 static bool VerifyClone(Texture2D t,byte[] raw,int force){int pos=0;for(int m=0;m<7;m++){
   byte[] b=t.GetPixelData<byte>(m).ToArray();int n=64>>m;if(b.Length!=n*n*4)return false;
   for(int i=0;i<b.Length;i++)if(b[i]!=(force>=0&&i%4==3?(byte)force:raw[pos+i]))return false;
   pos+=b.Length;}return pos==raw.Length;}
 static Material Override(Material mat,string prop,Texture2D t){var m=new Material(mat);m.SetTexture(prop,t);Need(m.GetTexture(prop)==t&&m.shader==mat.shader);return m;}
 static void Capture(Camera cam,MeshRenderer rend,Material mat,RenderTexture rt,string file){
   rend.enabled=mat!=null;if(mat!=null)rend.sharedMaterial=mat;cam.Render();
   var old=RenderTexture.active;RenderTexture.active=rt;var read=new Texture2D(rt.width,rt.height,TextureFormat.RGBAFloat,false,true);
   try{read.ReadPixels(new Rect(0,0,rt.width,rt.height),0,0,false);
     using(var w=new BinaryWriter(new FileStream(file,FileMode.CreateNew,FileAccess.Write)))
       foreach(var p in read.GetPixels()){w.Write(p.r);w.Write(p.g);w.Write(p.b);w.Write(p.a);}
   }finally{RenderTexture.active=old;UnityEngine.Object.DestroyImmediate(read);}
 }
 public static void Run(){
   var r=new Receipt{run_id=Arg("-gtNativeRunId"),unity_version=Application.unityVersion,backend=SystemInfo.graphicsDeviceType.ToString(),color_space=QualitySettings.activeColorSpace.ToString()};
   string priv=Arg("-gtNativePrivate");int code=2;bool async=ShaderUtil.allowAsyncCompilation,srgb=GL.sRGBWrite;
   var owned=new List<UnityEngine.Object>();
   try{
     Need(Application.isBatchMode&&r.unity_version=="2021.3.45f2"&&SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan&&QualitySettings.activeColorSpace==ColorSpace.Linear&&GraphicsSettings.currentRenderPipeline==null);
     Need(SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat,FormatUsage.Render)&&SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat,FormatUsage.Blend));
     r.phase="guard";Need(!String.IsNullOrEmpty(priv)&&File.Exists(Path.Combine(priv,"editor-output-private"))&&File.ReadAllText(Path.Combine(priv,"editor-output-private")).Trim()==r.run_id);r.private_log_guard=true;
     string root=Directory.GetParent(Application.dataPath).FullName;
     string input=File.ReadAllText(Path.Combine(root,"GTInput.json"));Need(input==File.ReadAllText(Path.Combine(priv,"expected.json")));
     var c=JsonUtility.FromJson<Input>(input);Need(c!=null&&c.run_id==r.run_id&&c.assets.Length==4&&c.slots.Length==2);
     ShaderUtil.allowAsyncCompilation=false;GL.sRGBWrite=false;
     r.phase="import";
     foreach(var a in c.assets){
       string path=Path.GetFullPath(Path.Combine(root,a.path));Need(path.StartsWith(Path.Combine(root,"Assets","GTParticle")+Path.DirectorySeparatorChar,StringComparison.Ordinal)&&!File.Exists(path)&&!File.Exists(path+".meta"));
       Need(String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(a.guid)));
       byte[] data=File.ReadAllBytes(Path.Combine(priv,a.blob+".bytes")),meta=File.ReadAllBytes(Path.Combine(priv,a.blob+".meta.bytes"));
       Need(Sha(data)==a.sha&&Sha(meta)==a.meta_sha);Directory.CreateDirectory(Path.GetDirectoryName(path));
       File.WriteAllBytes(path,data);File.WriteAllBytes(path+".meta",meta);
     }
     AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
     foreach(var a in c.assets){string path=Path.Combine(root,a.path);
       if(Id(AssetDatabase.LoadMainAssetAtPath(a.path),a.guid,a.file_id))r.asset_identities++;
       if(Sha(File.ReadAllBytes(path))==a.sha)r.asset_bytes_unchanged++;
       if(Sha(File.ReadAllBytes(path+".meta"))==a.meta_sha)r.meta_bytes_unchanged++;
     }
     var shader=AssetDatabase.LoadAssetAtPath<Shader>(c.shader_path);Need(shader!=null);
     r.shader_identity=Id(shader,c.shader_guid,4800000);r.shader_errors=Errors(shader);Need(r.shader_identity&&shader.isSupported&&shader.passCount==1&&r.shader_errors==0);
     var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(c.texture_path);Need(tex!=null);
     r.native_identity=Id(tex,c.texture_guid,c.texture_id);r.native_descriptor=tex.width==64&&tex.height==64&&tex.mipmapCount==7&&tex.format==TextureFormat.RGBA32&&GraphicsFormatUtility.IsSRGBFormat(tex.graphicsFormat);
     r.native_sampler=Sampler(tex,c);Need(r.native_identity&&r.native_descriptor&&r.native_sampler);
     r.phase="materials";var mat=AssetDatabase.LoadAssetAtPath<Material>(c.material_path);Need(mat!=null);
     r.material_identity=Id(mat,c.material_guid,2100000);r.material_shader_identity=mat.shader==shader;
     r.texture_refs=true;r.uv_matches=true;
     foreach(var slot in c.slots){Need(mat.HasProperty(slot.name));r.texture_refs &= Id(mat.GetTexture(slot.name),slot.guid,slot.file_id);
       var st=mat.GetTextureScale(slot.name);var off=mat.GetTextureOffset(slot.name);
       r.uv_matches &= slot.uv.Length==4&&Eq(st.x,slot.uv[0])&&Eq(st.y,slot.uv[1])&&Eq(off.x,slot.uv[2])&&Eq(off.y,slot.uv[3]);}
     foreach(var num in c.numbers){if(!mat.HasProperty(num.name))continue;r.numbers_declared++;
       bool match=false;if(num.kind=="float")match=Eq(mat.GetFloat(num.name),num.value[0]);
       if(num.kind=="color"){var v=mat.GetColor(num.name);match=Eq(v.r,num.value[0])&&Eq(v.g,num.value[1])&&Eq(v.b,num.value[2])&&Eq(v.a,num.value[3]);}
       if(match)r.numbers_matched++;}
     r.numbers_match=r.numbers_declared>0&&r.numbers_declared==r.numbers_matched;
     Need(r.material_identity&&r.material_shader_identity&&r.texture_refs&&r.uv_matches&&r.numbers_match&&mat.GetTexture(c.selected_property)==tex);
     r.phase="controls";byte[] raw=File.ReadAllBytes(Path.Combine(priv,"native-rgba.bytes"));Need(raw.Length==21844&&Sha(raw)==c.raw_sha);
     var exact=Clone(c,raw,-1);owned.Add(exact);var zero=Clone(c,raw,0);owned.Add(zero);var one=Clone(c,raw,255);owned.Add(one);
     r.clone_sampler_match=Sampler(exact,c)&&Sampler(zero,c)&&Sampler(one,c);
     r.clone_payload_verified=VerifyClone(exact,raw,-1)&&VerifyClone(zero,raw,0)&&VerifyClone(one,raw,255);
     Need(r.clone_sampler_match&&r.clone_payload_verified);
     var exactMat=Override(mat,c.selected_property,exact);owned.Add(exactMat);var zeroMat=Override(mat,c.selected_property,zero);owned.Add(zeroMat);var oneMat=Override(mat,c.selected_property,one);owned.Add(oneMat);
     var dummyShader=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTParticleControl.shader");Need(dummyShader!=null&&dummyShader.isSupported);
     var dummy=new Material(dummyShader);owned.Add(dummy);
     EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
     var camera=new GameObject("GT diagnostic camera");owned.Add(camera);var cam=camera.AddComponent<Camera>();cam.enabled=false;
     cam.transform.position=new Vector3(0,0,-2);cam.orthographic=true;cam.orthographicSize=1.1f;cam.aspect=1;cam.nearClipPlane=.1f;cam.farClipPlane=10;cam.clearFlags=CameraClearFlags.SolidColor;cam.allowHDR=true;cam.allowMSAA=false;cam.renderingPath=RenderingPath.Forward;
     var go=new GameObject("GT authored particle surface");owned.Add(go);var mesh=new Mesh();owned.Add(mesh);
     mesh.vertices=new[]{new Vector3(-1,-1,0),new Vector3(1,-1,0),new Vector3(1,1,0),new Vector3(-1,1,0)};
     mesh.normals=Enumerable.Repeat(Vector3.back,4).ToArray();mesh.tangents=Enumerable.Repeat(new Vector4(1,0,0,1),4).ToArray();mesh.colors=Enumerable.Repeat(Color.white,4).ToArray();
     var uv=new List<Vector4>{new Vector4(0,0,0,1),new Vector4(1,0,0,1),new Vector4(1,1,0,1),new Vector4(0,1,0,1)};
     for(int i=0;i<8;i++)mesh.SetUVs(i,uv);
     mesh.triangles=new[]{0,1,2,0,2,3};mesh.RecalculateBounds();go.AddComponent<MeshFilter>().sharedMesh=mesh;
     var rend=go.AddComponent<MeshRenderer>();rend.shadowCastingMode=ShadowCastingMode.Off;rend.receiveShadows=false;
     go.layer=30;cam.cullingMask=1<<30;
     r.phase="draw";Need(c.sizes.SequenceEqual(new[]{64,128})&&c.backgrounds==2);
     var colors=new[]{new Color(.125f,.25f,.5f,.25f),new Color(.625f,.375f,.125f,.75f)};
     string[] cases={"clear","dummy","native","repeat","clone","zero","one"};
     Material[] mats={null,dummy,mat,mat,exactMat,zeroMat,oneMat};
     foreach(int size in c.sizes){var rt=new RenderTexture(size,size,24,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear);owned.Add(rt);Need(rt.Create());cam.targetTexture=rt;
       for(int bg=0;bg<c.backgrounds;bg++){cam.backgroundColor=colors[bg];for(int i=0;i<cases.Length;i++){Capture(cam,rend,mats[i],rt,Path.Combine(priv,"draw-"+size+"-"+bg+"-"+cases[i]+".f32"));r.draw_cases++;}}
       cam.targetTexture=null;rt.Release();}
     r.shader_errors=Errors(shader);Need(r.shader_errors==0&&Sampler(tex,c)&&mat.GetTexture(c.selected_property)==tex);
     r.phase="complete";r.status="OBSERVED";code=0;
   }catch(Exception e){r.failure_category=e.GetType().Name;}
   finally{ShaderUtil.allowAsyncCompilation=async;GL.sRGBWrite=srgb;for(int i=owned.Count-1;i>=0;i--)if(owned[i]!=null)UnityEngine.Object.DestroyImmediate(owned[i]);
     if(r.private_log_guard)File.WriteAllText(Path.Combine(priv,"draw-receipt.json"),JsonUtility.ToJson(r));
     EditorApplication.Exit(code);}
 }
}
#endif
