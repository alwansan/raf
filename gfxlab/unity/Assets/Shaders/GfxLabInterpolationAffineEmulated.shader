// GFX-MULTI-041 — synthetic-only, mathematically affine/no-perspective emulator.
// Does not use any Raft Shader48 code. Standard GLES perspective interpolation:
// weightedColor = [Σ lambda_i (color_i*w_i)/w_i]/[Σ lambda_i/w_i]
// weightedW     = [Σ lambda_i (w_i)/w_i]/[Σ lambda_i/w_i]
// ratio = Σ lambda_i color_i (correct affine interpolation in screen space).
Shader "Hidden/GfxLab/InterpolationAffineEmulated"
{
    SubShader
    {
        Tags { "Queue"="Geometry" "RenderType"="Opaque" }
        Pass
        {
            Cull Off
            ZWrite Off
            ZTest Always
            Blend Off
            ColorMask RGBA
            CGPROGRAM
            #pragma target 3.0
            #pragma vertex vert
            #pragma fragment frag
            struct appdata
            {
                float4 vertex : POSITION;
                float4 color : COLOR0;
                float2 uv : TEXCOORD0;
            };
            struct v2f
            {
                float4 pos : SV_POSITION;
                float3 weightedProbe : TEXCOORD0;
                float clipW : TEXCOORD1;
            };
            v2f vert(appdata v)
            {
                v2f o;
                float w=max(0.1,v.uv.x);
                o.pos=float4(v.vertex.xy*w,0.25*w,w);
                o.weightedProbe=v.color.rgb*w;
                o.clipW=w;
                return o;
            }
            float4 frag(v2f i) : SV_Target
            {
                float3 affine=i.weightedProbe/max(i.clipW,0.00001);
                return float4(affine,1.0);
            }
            ENDCG
        }
    }
    Fallback Off
}
