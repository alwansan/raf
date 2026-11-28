// Authored numeric storage conversion only, no proprietary shader or game draw.
Shader "Hidden/GTFFTExactStore" {
 SubShader {
  Pass {
   ZTest Always ZWrite Off Cull Off Blend Off
   HLSLPROGRAM
   #pragma vertex vert_img
   #pragma fragment frag
   #pragma target 4.5
   #pragma only_renderers vulkan
   #include "UnityCG.cginc"
   Texture2D<float4> _MainTex;
   float4 frag(v2f_img i) : SV_Target {
     return _MainTex.Load(int3(int2(i.pos.xy),0));
   }
   ENDHLSL
  }
 }
 Fallback Off
}
