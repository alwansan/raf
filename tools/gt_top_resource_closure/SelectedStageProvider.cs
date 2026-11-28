// Source-derived external member diagnostics; no original-game provider claim.
#if UNITY_EDITOR
using System;
using System.IO;
using UnityEngine;

public static partial class SelectedArrayUnity {
 [Serializable] public class ProviderRow {
   public string name,role,kind,numeric_type,texture_kind;
   public int mode,lanes,row,element;
 }
 [Serializable] public class ProviderExpectation {
   public int mode,compare_lanes;public bool known;public float[] value=new float[4];
 }
 [Serializable] public class ProviderView {public int view;public ProviderExpectation[] expected;}
 [Serializable] public class ProviderReceipt {public ProviderView[] views=new ProviderView[3];}
 static ProviderExpectation ExpectedProvider(ProviderRow p,Camera camera,MeshRenderer renderer){
   var e=new ProviderExpectation{mode=p.mode};
   Matrix4x4 m=Matrix4x4.identity;bool matrix=true;
   switch(p.kind){
     case "object_to_world":m=renderer.localToWorldMatrix;break;
     case "world_to_object":m=renderer.worldToLocalMatrix;break;
     case "view":m=camera.worldToCameraMatrix;break;
     case "inverse_view":m=camera.worldToCameraMatrix.inverse;break;
     case "view_projection":m=GL.GetGPUProjectionMatrix(camera.projectionMatrix,true)*camera.worldToCameraMatrix;break;
     default:matrix=false;break;
   }
   if(matrix){
     Need(p.lanes==4&&p.row>=0&&p.row<4);var v=m.GetRow(p.row);
     e.value=new[]{v.x,v.y,v.z,v.w};e.compare_lanes=4;e.known=true;return e;
   }
   if(p.kind=="camera_position"){
     var v=camera.transform.position;e.value=new[]{v.x,v.y,v.z,0f};e.compare_lanes=3;e.known=true;
   }else if(p.kind=="texture_dimensions"){
     // API presence and dimensions only; matching does not prove texture identity.
     var t=Shader.GetGlobalTexture(p.name);
     if(t==null)return e;
     float depth=0;
     if(p.texture_kind=="Texture2DArray"){var a=t as Texture2DArray;if(a==null)return e;depth=a.depth;}
     else if(p.texture_kind=="Texture3D"){var a=t as Texture3D;if(a==null)return e;depth=a.depth;}
     else if(p.texture_kind=="TextureCube"&&t.dimension!=UnityEngine.Rendering.TextureDimension.Cube)return e;
     else if(p.texture_kind=="Texture2D"&&t.dimension!=UnityEngine.Rendering.TextureDimension.Tex2D)return e;
     e.value=new[]{(float)t.width,(float)t.height,depth,0f};e.compare_lanes=p.lanes;e.known=true;
   }
   return e;
 }
 static Material PrepareProvider(DrawInput cfg,DrawReceipt r,Material original){
   Need(cfg.provider_probe&&r.tap_shader_compiled&&cfg.provider_rows!=null&&cfg.provider_rows.Length>0&&cfg.provider_rows.Length<=192);
   var shader=UnityEditor.AssetDatabase.LoadAssetAtPath<Shader>("Assets/GTDraw/Diagnostics/ArrayTap.shader");
   Need(shader!=null&&shader.isSupported&&ShaderErrors(shader)==0);
   var actual=original.GetTexture(cfg.selected_property) as Texture2DArray;
   Need(actual!=null&&ObjectId(actual,cfg.array_guid,18700000));
   var mat=TypedTapClone(original,shader,actual,cfg.selected_property,cfg.tap_expected_properties,out int count);
   r.provider_typed_properties=count;
   Need(count==cfg.tap_expected_properties);
   return mat;
 }
 static ProviderView CaptureProviderView(DrawInput cfg,DrawReceipt r,Camera camera,MeshRenderer renderer,RenderTexture rt,Material mat,int view,string priv){
   var v=new ProviderView{view=view,expected=new ProviderExpectation[cfg.provider_rows.Length]};
   string prefix=Path.Combine(priv,"provider-"+view+"-");
   for(int mode=0;mode<2;mode++){
     TapMode(mat,mode);Capture(camera,renderer,mat,rt,prefix+mode+".f32");
   }
   for(int i=0;i<cfg.provider_rows.Length;i++){
     var p=cfg.provider_rows[i];Need(p.mode==i+2);
     TapMode(mat,p.mode);Capture(camera,renderer,mat,rt,prefix+p.mode+".f32");
     v.expected[i]=ExpectedProvider(p,camera,renderer);r.provider_observations++;
   }
   Need(ShaderErrors(mat.shader)==0);r.provider_views++;
   return v;
 }
}
#endif
