// Deliberately diagnostic material clones; never modify staged source assets.
#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

public static partial class SelectedArrayUnity {
 sealed class CausalControls : IDisposable {
   public Material source,red,green,tapSource,tapRed,tapGreen;
   public Shader tap;
   public Texture2DArray redArray,greenArray;
   public Texture2DArray[] basisArrays;public Material[] basisOriginal,basisTap;
   public void Dispose(){
     foreach(var mat in new[]{source,red,green,tapSource,tapRed,tapGreen})
       if(mat!=null)UnityEngine.Object.DestroyImmediate(mat);
     if(redArray!=null)UnityEngine.Object.DestroyImmediate(redArray);
     if(greenArray!=null)UnityEngine.Object.DestroyImmediate(greenArray);
     foreach(var group in new[]{basisOriginal,basisTap})if(group!=null)
       foreach(var mat in group)if(mat!=null)UnityEngine.Object.DestroyImmediate(mat);
     if(basisArrays!=null)foreach(var tex in basisArrays)if(tex!=null)UnityEngine.Object.DestroyImmediate(tex);
   }
 }
 static readonly int[] BasisMasks={0,15,1,2,4,8,14,13,11,7};
 static Texture2DArray ConstantBC3(DrawInput cfg,bool red) {return ConstantBC3Mask(cfg,red?9:10,false);}
 static Texture2DArray ConstantBC3Mask(DrawInput cfg,int mask,bool verifyRaw) {
   // Exact same shape, BC3 sRGB, all 22 ranges; uniform RGB565 endpoint
   // avoids filtering, layer, mip and interpolation ambiguity in controls.
   var raw=new byte[2796256];
   Need(mask>=0&&mask<=15);
   ushort color=(ushort)(((mask&1)!=0?0xf800:0)|((mask&2)!=0?0x07e0:0)|((mask&4)!=0?0x001f:0));
   for(int i=0;i<raw.Length;i+=16){
     raw[i]=(byte)((mask&8)!=0?255:0);raw[i+1]=0;raw[i+8]=(byte)(color&255);raw[i+9]=(byte)(color>>8);
   }
   var tex=Make(raw,1024,1024,2,11,"GT authored RGBA endpoint "+mask);
   if(verifyRaw){
     try {
       int pos=0;
       for(int layer=0;layer<2;layer++)for(int mip=0;mip<11;mip++){
         var data=tex.GetPixelData<byte>(mip,layer);Need(pos+data.Length<=raw.Length);
         for(int j=0;j<data.Length;j++)Need(data[j]==raw[pos+j]);
         pos+=data.Length;
       }
       Need(pos==raw.Length);
     }catch{UnityEngine.Object.DestroyImmediate(tex);throw;}
   }
   tex.filterMode=(FilterMode)cfg.sampler[0];tex.anisoLevel=cfg.sampler[1];
   tex.wrapModeU=(TextureWrapMode)cfg.sampler[2];tex.wrapModeV=(TextureWrapMode)cfg.sampler[3];
   tex.wrapModeW=(TextureWrapMode)cfg.sampler[4];tex.mipMapBias=cfg.mip_bias;
   return tex;
 }
 static Material ArrayClone(Material original,Shader shader,Texture2DArray tex,string prop) {
   var mat=new Material(original);
   if(mat.shader!=shader){mat.shader=shader;mat.CopyPropertiesFromMaterial(original);}
   Need(mat.shader==shader&&mat.HasProperty(prop));
   mat.SetTexture(prop,tex);Need(mat.GetTexture(prop)==tex);
   return mat;
 }
 static void ImportTap(DrawInput cfg,DrawReceipt r,string root,string priv) {
   if(!cfg.tap_available)return;
   try {
     r.tap_phase="verify_private_bytes";
     byte[] raw=File.ReadAllBytes(Path.Combine(priv,"array-tap-shader.bytes"));Need(Sha(raw)==cfg.tap_shader_sha);
     string rel="Assets/GTDraw/Diagnostics/ArrayTap.shader",dst=AssetPath(root,rel);
     Directory.CreateDirectory(Path.GetDirectoryName(dst));Need(!File.Exists(dst));File.WriteAllBytes(dst,raw);
     r.tap_phase="import_shader";
     AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
     var shader=AssetDatabase.LoadAssetAtPath<Shader>(rel);
     r.tap_imported=shader!=null;Need(r.tap_imported);
     r.tap_phase="validate_shader";
     r.tap_shader_errors=ShaderErrors(shader);r.tap_shader_supported=shader.isSupported;r.tap_shader_passes=shader.passCount;
     Need(r.tap_shader_supported&&r.tap_shader_passes==1&&r.tap_shader_errors==0);
     r.tap_shader_compiled=true;r.tap_phase="shader_ready";
   }catch(Exception e){r.tap_failure_category=e.GetType().Name;}
 }
 static bool VectorBits(Vector4 a,Vector4 b) {
   return FloatBits(a.x,b.x)&&FloatBits(a.y,b.y)&&FloatBits(a.z,b.z)&&FloatBits(a.w,b.w);
 }
 static Material TypedTapClone(Material source,Shader shader,Texture2DArray tex,string prop,int expected,out int copied,bool diagnostic=true) {
   copied=0;
   // Construct directly on the target shader; do not rely on shader-switch
   // CopyPropertiesFromMaterial to transfer typed values or keyword state.
   var m=new Material(shader);
   try {
     var ss=source.shader;
     Need(ss.GetPropertyCount()==expected&&shader.GetPropertyCount()==expected+(diagnostic?1:0));
     Need(source.HasProperty(prop)&&m.HasProperty(prop)&&!source.HasProperty("_GTSelectedTapMode"));
     for(int i=0;i<ss.GetPropertyCount();i++){
       string name=ss.GetPropertyName(i);int j=shader.FindPropertyIndex(name);
       Need(j>=0&&ss.GetPropertyType(i)==shader.GetPropertyType(j));
       switch(ss.GetPropertyType(i).ToString()){
         case "Texture":
           Need(ss.GetPropertyTextureDimension(i)==shader.GetPropertyTextureDimension(j));
           Texture target=name==prop?tex:source.GetTexture(name);
           m.SetTexture(name,target);
           m.SetTextureScale(name,source.GetTextureScale(name));m.SetTextureOffset(name,source.GetTextureOffset(name));
           Need(m.GetTexture(name)==target&&
                m.GetTextureScale(name)==source.GetTextureScale(name)&&m.GetTextureOffset(name)==source.GetTextureOffset(name));
           break;
         case "Color":
           m.SetColor(name,source.GetColor(name));Need(VectorBits(m.GetColor(name),source.GetColor(name)));break;
         case "Vector":
           m.SetVector(name,source.GetVector(name));Need(VectorBits(m.GetVector(name),source.GetVector(name)));break;
         case "Float":case "Range":
           m.SetFloat(name,source.GetFloat(name));Need(FloatBits(m.GetFloat(name),source.GetFloat(name)));break;
         default:throw new InvalidOperationException("GT typed tap property schema");
       }
       copied++;
     }
     Need(copied==expected&&m.GetTexture(prop)==tex);
     m.renderQueue=source.renderQueue;m.enableInstancing=source.enableInstancing;
     Need(m.renderQueue==source.renderQueue&&m.enableInstancing==source.enableInstancing);
     if(diagnostic)TapMode(m,2);
     return m;
   }catch{UnityEngine.Object.DestroyImmediate(m);throw;}
 }
 static void TapMode(Material m,float mode) {
   Need(m!=null&&m.HasProperty("_GTSelectedTapMode"));
   m.SetFloat("_GTSelectedTapMode",mode);Need(FloatBits(m.GetFloat("_GTSelectedTapMode"),mode));
 }
 static bool SameBasisMaterial(Material original,Material clone,Texture2DArray tex,string prop,int count) {
   if(clone.shader!=original.shader||clone.shader.GetPropertyCount()!=count||
      clone.renderQueue!=original.renderQueue||clone.enableInstancing!=original.enableInstancing)return false;
   var a=original.shaderKeywords;var b=clone.shaderKeywords;
   Array.Sort(a,StringComparer.Ordinal);Array.Sort(b,StringComparer.Ordinal);
   if(a.Length!=b.Length)return false;for(int k=0;k<a.Length;k++)if(a[k]!=b[k])return false;
   for(int i=0;i<count;i++){
     string n=original.shader.GetPropertyName(i);
     switch(original.shader.GetPropertyType(i).ToString()){
       case "Texture":
         if(clone.GetTexture(n)!=(n==prop?tex:original.GetTexture(n))||
            clone.GetTextureScale(n)!=original.GetTextureScale(n)||clone.GetTextureOffset(n)!=original.GetTextureOffset(n))return false;
         break;
       case "Color": if(!VectorBits(clone.GetColor(n),original.GetColor(n)))return false;break;
       case "Vector": if(!VectorBits(clone.GetVector(n),original.GetVector(n)))return false;break;
       case "Float":case "Range":if(!FloatBits(clone.GetFloat(n),original.GetFloat(n)))return false;break;
       default:return false;
     }
   }
   return true;
 }
 static void PrepareBasis(DrawInput cfg,DrawReceipt r,Material original,CausalControls cc) {
   if(!r.tap_materials_ready)return;
   try {
     r.basis_phase="prepare";
     Need(cfg.tap_source_sample_sites>0&&cfg.tap_source_sample_sites<=8);
     int n=BasisMasks.Length;
     cc.basisArrays=new Texture2DArray[n];cc.basisOriginal=new Material[n];cc.basisTap=new Material[n];
     for(int i=0;i<n;i++){
       r.basis_phase="raw_endpoint";
       var tex=ConstantBC3Mask(cfg,BasisMasks[i],true);cc.basisArrays[i]=tex;
       Need((int)tex.filterMode==cfg.sampler[0]&&tex.anisoLevel==cfg.sampler[1]&&
            (int)tex.wrapModeU==cfg.sampler[2]&&(int)tex.wrapModeV==cfg.sampler[3]&&
            (int)tex.wrapModeW==cfg.sampler[4]&&FloatBits(tex.mipMapBias,cfg.mip_bias));
       r.basis_array_payloads++;
       r.basis_phase="original_clone";
       cc.basisOriginal[i]=ArrayClone(original,original.shader,tex,cfg.selected_property);
       Need(SameBasisMaterial(original,cc.basisOriginal[i],tex,cfg.selected_property,cfg.tap_expected_properties));
       r.basis_original_clones++;
       r.basis_phase="typed_clone";
       cc.basisTap[i]=TypedTapClone(original,cc.tap,tex,cfg.selected_property,cfg.tap_expected_properties,out int count);
       Need(count==cfg.tap_expected_properties);r.basis_typed_clones++;
     }
     r.basis_ready=true;r.basis_phase="ready";
   }catch(Exception e){r.basis_failure_category=e.GetType().Name;}
 }
 static void CaptureBasis(Camera cam,MeshRenderer rend,RenderTexture rt,CausalControls cc,DrawReceipt r,DrawInput cfg,string prefix) {
   if(!r.basis_ready)return;
   try {
     for(int i=0;i<BasisMasks.Length;i++){
       string p=prefix+"basis-"+BasisMasks[i]+"-";
       r.basis_phase="original_draw";Capture(cam,rend,cc.basisOriginal[i],rt,p+"final.f32");
       r.basis_phase="site_calibration";TapMode(cc.basisTap[i],2);Capture(cam,rend,cc.basisTap[i],rt,p+"cal.f32");
       for(int site=0;site<cfg.tap_source_sample_sites;site++){
         r.basis_phase="site_hit";TapMode(cc.basisTap[i],3+2*site);Capture(cam,rend,cc.basisTap[i],rt,p+"hit-"+site+".f32");
         r.basis_phase="site_sample";TapMode(cc.basisTap[i],4+2*site);Capture(cam,rend,cc.basisTap[i],rt,p+"sample-"+site+".f32");
         r.basis_site_pairs++;
       }
     }
     r.basis_views++;r.basis_phase="complete";
   }catch(Exception e){r.basis_failure_category=e.GetType().Name;r.basis_ready=false;}
 }
 static CausalControls PrepareCausal(DrawInput cfg,DrawReceipt r,Material original,string root,string priv) {
   var cc=new CausalControls();
   try{
     var actual=original.GetTexture(cfg.selected_property) as Texture2DArray;Need(actual!=null&&ObjectId(actual,cfg.array_guid,18700000));
     cc.redArray=ConstantBC3(cfg,true);cc.greenArray=ConstantBC3(cfg,false);
     cc.source=ArrayClone(original,original.shader,actual,cfg.selected_property);
     cc.red=ArrayClone(original,original.shader,cc.redArray,cfg.selected_property);
     cc.green=ArrayClone(original,original.shader,cc.greenArray,cfg.selected_property);
     r.authored_array_overrides_bound=true;
     if(r.tap_shader_compiled){
       try{
         r.tap_phase="load_imported_shader";
         cc.tap=AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTDraw/Diagnostics/ArrayTap.shader");
         Need(cc.tap!=null&&cc.tap.isSupported&&cc.tap.passCount==1&&ShaderErrors(cc.tap)==0);
         r.tap_phase="typed_source_clone";
         cc.tapSource=TypedTapClone(original,cc.tap,actual,cfg.selected_property,cfg.tap_expected_properties,out int sourceCount);
         r.tap_copied_properties_source=sourceCount;
         r.tap_phase="typed_red_clone";
         cc.tapRed=TypedTapClone(original,cc.tap,cc.redArray,cfg.selected_property,cfg.tap_expected_properties,out int redCount);
         r.tap_copied_properties_red=redCount;
         r.tap_phase="typed_green_clone";
         cc.tapGreen=TypedTapClone(original,cc.tap,cc.greenArray,cfg.selected_property,cfg.tap_expected_properties,out int greenCount);
         r.tap_copied_properties_green=greenCount;
         r.tap_materials_ready=true;r.tap_phase="materials_ready";
       }catch(Exception e){r.tap_failure_category=e.GetType().Name;}
     }
     PrepareBasis(cfg,r,original,cc);
     return cc;
   }catch{cc.Dispose();throw;}
 }
 static void CausalCapture(Camera cam,MeshRenderer rend,RenderTexture rt,CausalControls cc,DrawReceipt r,string prefix){
   Capture(cam,rend,cc.source,rt,prefix+"override_source.f32");
   Capture(cam,rend,cc.red,rt,prefix+"override_red.f32");
   Capture(cam,rend,cc.green,rt,prefix+"override_green.f32");
   r.causal_override_views++;
   if(r.tap_materials_ready){
     try{
       r.tap_phase="capture_calibration";
       TapMode(cc.tapSource,2);
       Capture(cam,rend,cc.tapSource,rt,prefix+"tap_cal.f32");
       var mats=new[]{cc.tapSource,cc.tapRed,cc.tapGreen};string[] names={"source","red","green"};
       for(int i=0;i<3;i++){
         r.tap_phase="capture_hit";TapMode(mats[i],0);Capture(cam,rend,mats[i],rt,prefix+"tap_hit_"+names[i]+".f32");
         r.tap_phase="capture_sample";TapMode(mats[i],1);Capture(cam,rend,mats[i],rt,prefix+"tap_"+names[i]+".f32");
       }
       r.causal_tap_views++;r.tap_phase="capture_complete";
     }catch(Exception e){r.tap_failure_category=e.GetType().Name;r.tap_materials_ready=false;}
   }
 }
}
#endif
