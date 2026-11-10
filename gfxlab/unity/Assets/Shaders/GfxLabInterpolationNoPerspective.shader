// GFX-MULTI-040: ORIGINAL-FREE diagnostic shader authored for this laboratory.
// Synthetic geometry only. NOT Raft Shader48 and NOT a PC-vs-Android parity claim.
Shader "Hidden/GfxLab/InterpolationNoPerspective"
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
            #pragma target 4.0
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
                noperspective float3 probe : TEXCOORD0;
            };
            v2f vert(appdata v)
            {
                v2f o;
                // Identical NDC geometry, deliberately *different clip W*
                // across vertices. Perspective vs noperspective MUST differ.
                float w = max(0.1, v.uv.x);
                o.pos = float4(v.vertex.xy * w, 0.25 * w, w);
                o.probe = v.color.rgb;
                return o;
            }
            float4 frag(v2f i) : SV_Target
            {
                return float4(i.probe, 1.0);
            }
            ENDCG
        }
    }
    Fallback Off
}
