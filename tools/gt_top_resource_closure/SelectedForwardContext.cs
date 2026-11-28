// Compare exact source pass tag spelling against canonical Unity ForwardBase.
#if UNITY_EDITOR
using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEngine.Rendering;

public static partial class SelectedArrayUnity {
 [Serializable] public class PassContextReceipt {public int views,scenarios,typed_properties,shader_errors;}
 static Shader ImportContextShader(string root,string priv,string blob,string hash,string rel){
   byte[] raw=File.ReadAllBytes(Path.Combine(priv,blob));Need(Sha(raw)==hash);
   string dst=AssetPath(root,rel);Directory.CreateDirectory(Path.GetDirectoryName(dst));Need(!File.Exists(dst));
   File.WriteAllBytes(dst,raw);
   AssetDatabase.ImportAsset(rel,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
   var shader=AssetDatabase.LoadAssetAtPath<Shader>(rel);
   Need(shader!=null&&shader.isSupported&&shader.passCount==1&&ShaderErrors(shader)==0);
   return shader;
 }
 static void CapturePassContext(DrawInput cfg,DrawReceipt r,Camera cam,MeshRenderer rend,RenderTexture rt,
                                Material original,Light light,float radius,Vector3[] views,string priv){
   string root=Directory.GetParent(Application.dataPath).FullName;
   Material rawTap=null,canonTap=null,canon=null,control=null;
   var receipt=new PassContextReceipt();Color savedColor=light.color;float savedIntensity=light.intensity;Quaternion savedRotation=light.transform.rotation;
   try{
     var cs=ImportContextShader(root,priv,"canonical-pass-shader.bytes",cfg.canonical_pass_sha,"Assets/GTDraw/Diagnostics/CanonicalPass.shader");
     var ts=ImportContextShader(root,priv,"canonical-tap-shader.bytes",cfg.canonical_tap_sha,"Assets/GTDraw/Diagnostics/CanonicalTap.shader");
     var ps=ImportContextShader(root,priv,"engine-light-control.bytes",cfg.engine_light_control_sha,"Assets/GTDraw/Diagnostics/EngineLight.shader");
     var array=original.GetTexture(cfg.selected_property) as Texture2DArray;Need(array!=null&&ObjectId(array,cfg.array_guid,18700000));
     rawTap=PrepareProvider(cfg,r,original);
     canonTap=TypedTapClone(original,ts,array,cfg.selected_property,cfg.tap_expected_properties,out int tc);
     canon=TypedTapClone(original,cs,array,cfg.selected_property,cfg.tap_expected_properties,out int fc,false);
     receipt.typed_properties=r.provider_typed_properties+tc+fc;Need(tc==cfg.tap_expected_properties&&fc==tc);
     control=new Material(ps);Need(control.HasProperty("_GTControlMode"));
     string[] scenarios={"first","second","restored"};
     for(int s=0;s<3;s++){
       light.color=s==1?new Color(.2f,.7f,.4f,1):new Color(.8f,.3f,.15f,1);
       light.intensity=s==1?.55f:1.25f;
       light.transform.rotation=s==1?Quaternion.Euler(-15,75,0):Quaternion.Euler(40,25,0);
       for(int v=0;v<views.Length;v++){
         cam.transform.position=views[v].normalized*(radius*3+1);cam.transform.LookAt(Vector3.zero,Vector3.up);
         string prefix=Path.Combine(priv,scenarios[s]+"-"+v+"-");
         for(int i=0;i<4;i++){
           control.SetFloat("_GTControlMode",i);
           Capture(cam,rend,control,rt,prefix+"control-"+i+".f32");
         }
         Material[] taps={rawTap,canonTap};Material[] finals={original,canon};string[] names={"raw","canonical"};
         for(int m=0;m<2;m++){
           Capture(cam,rend,finals[m],rt,prefix+names[m]+"-final.f32");
           for(int i=0;i<cfg.provider_rows.Length+2;i++){
             TapMode(taps[m],i);Capture(cam,rend,taps[m],rt,prefix+names[m]+"-"+i+".f32");
           }
         }
       }
       receipt.scenarios++;
     }
     receipt.views=views.Length;receipt.shader_errors=ShaderErrors(original.shader)+ShaderErrors(rawTap.shader)+ShaderErrors(cs)+ShaderErrors(ts)+ShaderErrors(ps);
     Need(receipt.shader_errors==0);
     File.WriteAllText(Path.Combine(priv,"pass-context-receipt.json"),JsonUtility.ToJson(receipt));
   }finally{
     light.color=savedColor;light.intensity=savedIntensity;light.transform.rotation=savedRotation;
     foreach(var mat in new[]{rawTap,canonTap,canon,control})if(mat!=null)UnityEngine.Object.DestroyImmediate(mat);
   }
 }
}
#endif
