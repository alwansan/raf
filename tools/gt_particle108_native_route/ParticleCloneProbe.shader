Shader "Hidden/GTParticleCloneProbe" {
Properties {
_GTProbeTex ("Diagnostic texture", 2D) = "white" {}
_GTProbeLevel ("Diagnostic level", Float) = 0
_GTProbeMode ("Diagnostic mode", Float) = 0
}
SubShader {
Pass {
Cull Off
ZWrite Off
ZTest Always
Blend Off
ColorMask RGBA
CGPROGRAM
#pragma target 4.5
#pragma vertex vert_img
#pragma fragment frag
#include "UnityCG.cginc"
Texture2D<float4> _GTProbeTex;
SamplerState sampler_GTProbeTex;
float _GTProbeLevel;
float _GTProbeMode;
float4 frag(v2f_img i) : SV_Target {
    if (_GTProbeMode > 1.5) return float4(0.125,0.375,0.625,1);
    int level=(int)_GTProbeLevel;
    if (_GTProbeMode < 0.5) {
        int size=64 >> level;
        int2 coord=clamp((int2)floor(i.uv*size),int2(0,0),int2(size-1,size-1));
        return _GTProbeTex.Load(int3(coord,level));
    }
    return _GTProbeTex.SampleLevel(sampler_GTProbeTex,i.uv,_GTProbeLevel);
}
ENDCG
}
}
Fallback Off
}
