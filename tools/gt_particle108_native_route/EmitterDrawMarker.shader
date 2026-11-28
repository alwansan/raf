Shader "Hidden/GTEmitterDrawMarker" {
SubShader {
Pass {
Cull Off ZWrite Off ZTest Always Blend Off ColorMask RGBA
CGPROGRAM
#pragma vertex vert
#pragma fragment frag
#include "UnityCG.cginc"
float4 vert(float4 v:POSITION):SV_POSITION { return UnityObjectToClipPos(v); }
float4 frag():SV_Target { return float4(.91,.07,.61,1); }
ENDCG
}
}
Fallback Off
}
