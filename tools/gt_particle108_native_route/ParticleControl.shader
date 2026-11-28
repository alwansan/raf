Shader "Hidden/GTParticleControl" {
SubShader {
Pass {
Cull Off
ZWrite Off
ZTest Always
Blend Off
ColorMask RGBA
CGPROGRAM
#pragma vertex vert
#pragma fragment frag
float4 vert(float4 v:POSITION):SV_POSITION {return float4(v.xy*0.75,0.5,1);}
float4 frag():SV_Target {return float4(0.91,0.07,0.61,1);}
ENDCG
}
}
Fallback Off
}
