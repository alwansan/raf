// Authored numeric storage conversion only; explicit source, fixed coordinates.
Shader "Hidden/GTFFTExactStore" {
 Properties {
  _InputTex ("Exact source", 2D) = "black" {}
  _FlipX ("Probe X flip", Float) = 0
  _FlipY ("Probe Y flip", Float) = 0
  _PreRound ("Probe explicit binary16 round", Float) = 0
 }
 SubShader {
  ZTest Always ZWrite Off Cull Off Blend Off
  HLSLINCLUDE
  #include "UnityCG.cginc"
  Texture2D<float4> _InputTex;
  float _FlipX, _FlipY, _PreRound;
  struct VOut { float4 pos : SV_POSITION; };
  VOut triangle(uint id : SV_VertexID) {
    VOut o;
    float2 uv=float2((id << 1)&2,id&2);
    o.pos=float4(uv*2.0-1.0,0,1);
    return o;
  }
  float4 Store(float4 pos) {
    int2 xy=int2(pos.xy);
    if(_FlipX>0.5)xy.x=511-xy.x;
    if(_FlipY>0.5)xy.y=511-xy.y;
    float4 v=_InputTex.Load(int3(xy,0));
    if(_PreRound>0.5)
      v=float4(f16tof32(f32tof16(v.x)),f16tof32(f32tof16(v.y)),f16tof32(f32tof16(v.z)),f16tof32(f32tof16(v.w)));
    return v;
  }
  float4 frag_triangle(VOut i) : SV_Target {return Store(i.pos);}
  float4 frag_blit(v2f_img i) : SV_Target {return Store(i.pos);}
  ENDHLSL
  Pass {
   HLSLPROGRAM
   #pragma vertex triangle
   #pragma fragment frag_triangle
   #pragma target 5.0
   #pragma only_renderers vulkan
   ENDHLSL
  }
  Pass {
   HLSLPROGRAM
   #pragma vertex vert_img
   #pragma fragment frag_blit
   #pragma target 5.0
   #pragma only_renderers vulkan
   ENDHLSL
  }
 }
 Fallback Off
}
