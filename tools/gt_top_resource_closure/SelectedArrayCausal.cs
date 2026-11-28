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
   public void Dispose(){
     foreach(var mat in new[]{source,red,green,tapSource,tapRed,tapGreen})
       if(mat!=null)UnityEngine.Object.DestroyImmediate(mat);
     if(redArray!=null)UnityEngine.Object.DestroyImmediate(redArray);
     if(greenArray!=null)UnityEngine.Object.DestroyImmediate(greenArray);
   }
 }
 static Texture2DArray ConstantBC3(DrawInput cfg,bool red) {
   // Exact same shape, BC3 sRGB, all 22 ranges; uniform RGB565 endpoint
   // avoids filtering, layer, mip and interpolation ambiguity in controls.
   var raw=new byte[2796256];
   ushort color=(ushort)(red?0xf800:0x07e0);
   for(int i=0;i<raw.Length;i+=16){
     raw[i]=255;raw[i+1]=0;raw[i+8]=(byte)(color&255);raw[i+9]=(byte)(color>>8);
   }
   var tex=Make(raw,1024,1024,2,11,red?"GT authored red array":"GT authored green array");
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
 static CausalControls PrepareCausal(DrawInput cfg,DrawReceipt r,Material original,string root,string priv) {
   var cc=new CausalControls();
   try{
     var actual=original.GetTexture(cfg.selected_property) as Texture2DArray;Need(actual!=null&&ObjectId(actual,cfg.array_guid,18700000));
     cc.redArray=ConstantBC3(cfg,true);cc.greenArray=ConstantBC3(cfg,false);
     cc.source=ArrayClone(original,original.shader,actual,cfg.selected_property);
     cc.red=ArrayClone(original,original.shader,cc.redArray,cfg.selected_property);
     cc.green=ArrayClone(original,original.shader,cc.greenArray,cfg.selected_property);
     r.authored_array_overrides_bound=true;
     if(cfg.tap_available){
       try{
         byte[] raw=File.ReadAllBytes(Path.Combine(priv,"array-tap-shader.bytes"));Need(Sha(raw)==cfg.tap_shader_sha);
         string rel="Assets/GTDraw/Diagnostics/ArrayTap.shader",dst=AssetPath(root,rel);
         Directory.CreateDirectory(Path.GetDirectoryName(dst));Need(!File.Exists(dst));File.WriteAllBytes(dst,raw);
         AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
         cc.tap=AssetDatabase.LoadAssetAtPath<Shader>(rel);
         r.tap_shader_errors=cc.tap==null?-1:ShaderErrors(cc.tap);
         Need(cc.tap!=null&&cc.tap.isSupported&&cc.tap.passCount==1&&r.tap_shader_errors==0);
         cc.tapSource=ArrayClone(original,cc.tap,actual,cfg.selected_property);
         cc.tapRed=ArrayClone(original,cc.tap,cc.redArray,cfg.selected_property);
         cc.tapGreen=ArrayClone(original,cc.tap,cc.greenArray,cfg.selected_property);
         Need(cc.tapSource.HasProperty("_GTSelectedTapMode")&&cc.tapRed.HasProperty("_GTSelectedTapMode")&&cc.tapGreen.HasProperty("_GTSelectedTapMode"));
         r.tap_shader_compiled=true;
       }catch(Exception e){r.tap_failure_category=e.GetType().Name;}
     }
     return cc;
   }catch{cc.Dispose();throw;}
 }
 static void CausalCapture(Camera cam,MeshRenderer rend,RenderTexture rt,CausalControls cc,DrawReceipt r,string prefix){
   Capture(cam,rend,cc.source,rt,prefix+"override_source.f32");
   Capture(cam,rend,cc.red,rt,prefix+"override_red.f32");
   Capture(cam,rend,cc.green,rt,prefix+"override_green.f32");
   r.causal_override_views++;
   if(r.tap_shader_compiled){
     try{
       string mode="_GTSelectedTapMode";
       cc.tapSource.SetFloat(mode,2);
       Capture(cam,rend,cc.tapSource,rt,prefix+"tap_cal.f32");
       var mats=new[]{cc.tapSource,cc.tapRed,cc.tapGreen};string[] names={"source","red","green"};
       for(int i=0;i<3;i++){
         mats[i].SetFloat(mode,0);Capture(cam,rend,mats[i],rt,prefix+"tap_hit_"+names[i]+".f32");
         mats[i].SetFloat(mode,1);Capture(cam,rend,mats[i],rt,prefix+"tap_"+names[i]+".f32");
       }
       r.causal_tap_views++;
     }catch(Exception e){r.tap_failure_category=e.GetType().Name;}
   }
 }
}
#endif
