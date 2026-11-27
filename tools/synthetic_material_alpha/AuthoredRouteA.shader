Shader "RAFT/Authored/RouteA"
{
 Properties { _MainTex ("Texture", 2D) = "white" {} _Tint ("Tint", Color) = (1,1,1,1) }
 SubShader {
  Tags { "Queue"="Geometry" "RenderType"="Opaque" }
  Pass {
   Cull Off ZWrite Off ZTest Always Blend One Zero
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma target 3.5
   #include "UnityCG.cginc"
   Texture2D _MainTex; SamplerState sampler_MainTex;
   float4 _MainTex_ST; float4 _Tint;
   struct Input { float4 vertex : POSITION; float2 uv : TEXCOORD0; };
   struct Varying { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };
   Varying vert(Input v) { Varying o; o.pos=UnityObjectToClipPos(v.vertex); o.uv=v.uv*_MainTex_ST.xy+_MainTex_ST.zw; return o; }
   float4 frag(Varying i) : SV_Target { float4 t=_MainTex.Sample(sampler_MainTex,i.uv); return float4(t.rgb*_Tint.rgb,1); }
   ENDHLSL
  }
 }
 Fallback Off
}
