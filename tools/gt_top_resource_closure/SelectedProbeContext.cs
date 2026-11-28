// Real local reflection-probe context, authored inputs only.
#if UNITY_EDITOR
using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

public static partial class SelectedArrayUnity {
 [Serializable] public class ProbeScenario {
   public string scenario;public ProviderView[] views=new ProviderView[3];
   public int[] selected_local_counts=new int[3];
 }
 [Serializable] public class ProbeContextReceipt {public ProbeScenario[] scenarios=new ProbeScenario[3];}
 sealed class AuthoredProbes : IDisposable {
   public GameObject[] owners=new GameObject[2];public ReflectionProbe[] probes=new ReflectionProbe[2];
   public Cubemap[] textures=new Cubemap[2];
   public AuthoredProbes(float radius){
     try {
       for(int i=0;i<2;i++){
         var cube=new Cubemap(16,TextureFormat.RGBA32,true);
         textures[i]=cube;
         var color=i==0?new Color(.25f,.5f,.75f,1):new Color(.75f,.25f,.5f,1);
         var pixels=new Color[256];for(int n=0;n<pixels.Length;n++)pixels[n]=color;
         for(int face=0;face<6;face++)cube.SetPixels(pixels,(CubemapFace)face);
         cube.Apply(true,false);
         var g=new GameObject("GT authored reflection probe "+i);owners[i]=g;g.SetActive(false);
         g.transform.position=new Vector3((i==0?-.2f:.3f)*radius,0,0);
         var p=g.AddComponent<ReflectionProbe>();probes[i]=p;p.mode=ReflectionProbeMode.Custom;
         p.customBakedTexture=cube;p.boxProjection=true;p.size=Vector3.one*radius*(i==0?6f:8f);
         p.center=Vector3.zero;p.importance=1;p.blendDistance=radius*.25f;p.intensity=1f;
         p.cullingMask=1<<30;
         Need(p.customBakedTexture==cube&&p.boxProjection&&p.mode==ReflectionProbeMode.Custom);
       }
     }catch{Dispose();throw;}
   }
   public void Enable(bool on){foreach(var g in owners)if(g!=null)g.SetActive(on);}
   public int Selected(MeshRenderer r){
     var result=new List<ReflectionProbeBlendInfo>();r.GetClosestReflectionProbes(result);
     int count=0;
     foreach(var x in result)if((x.probe==probes[0]||x.probe==probes[1])&&x.weight>0f)count++;
     Need(count>=0&&count<=2);
     return count;
   }
   public void Dispose(){
     foreach(var g in owners)if(g!=null)UnityEngine.Object.DestroyImmediate(g);
     foreach(var t in textures)if(t!=null)UnityEngine.Object.DestroyImmediate(t);
   }
 }
 static void CaptureProbeContext(DrawInput cfg,DrawReceipt r,Camera camera,MeshRenderer renderer,RenderTexture rt,
                                  Material original,Material provider,float radius,Vector3[] views,string priv){
   var receipt=new ProbeContextReceipt();var saved=renderer.reflectionProbeUsage;
   string[] names={"baseline","local_probes","restored"};
   using(var probes=new AuthoredProbes(radius)){
     try{
       for(int s=0;s<3;s++){
         bool local=s==1;probes.Enable(local);
         renderer.reflectionProbeUsage=local?ReflectionProbeUsage.BlendProbes:saved;
         var record=new ProbeScenario{scenario=names[s]};receipt.scenarios[s]=record;
         for(int v=0;v<views.Length;v++){
           camera.transform.position=views[v].normalized*(radius*3+1);camera.transform.LookAt(Vector3.zero,Vector3.up);
           string prefix=Path.Combine(priv,names[s]+"-");
           Capture(camera,renderer,original,rt,prefix+"final-"+v+".f32");
           record.selected_local_counts[v]=probes.Selected(renderer);
           record.views[v]=CaptureProviderView(cfg,r,camera,renderer,rt,provider,v,priv,names[s]+"-");
         }
       }
     }finally{probes.Enable(false);renderer.reflectionProbeUsage=saved;}
   }
   File.WriteAllText(Path.Combine(priv,"probe-context-receipt.json"),JsonUtility.ToJson(receipt));
 }
}
#endif
