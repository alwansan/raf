// Authored diagnostic adapter, NOT the original Particle108 shader.
Shader "Hidden/GT/NativeMipAlpha" {
 Properties { _MainTex ("Native texture", 2D) = "white" {} _GTLod ("Explicit mip", Float) = 0 _GTForce ("Forced alpha", Float) = -1 }
 SubShader {
  Tags { "Queue"="Transparent" "RenderType"="Transparent" }
  Pass {
   Cull Off ZWrite Off ZTest Always
   Blend SrcAlpha OneMinusSrcAlpha, One OneMinusSrcAlpha
   ColorMask RGBA
   HLSLPROGRAM
   #pragma target 3.5
   #pragma only_renderers vulkan
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   Texture2D<float4> _MainTex;
   SamplerState sampler_MainTex;
   float _GTLod, _GTForce;
   struct Input { float4 vertex : POSITION; float2 uv : TEXCOORD0; };
   struct Varying { float4 position : SV_POSITION; float2 uv : TEXCOORD0; };
   Varying vert(Input i) { Varying o; o.position=UnityObjectToClipPos(i.vertex); o.uv=i.uv; return o; }
   float4 frag(Varying i) : SV_Target {
     float a=_MainTex.SampleLevel(sampler_MainTex,i.uv,_GTLod).a;
     if(_GTForce>=0) a=_GTForce;
     return float4(1,1,1,a);
   }
   ENDHLSL
  }
 }
 Fallback Off
}
