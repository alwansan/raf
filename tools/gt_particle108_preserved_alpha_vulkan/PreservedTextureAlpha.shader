// Authored test adapter only. Not the original particle shader.
Shader "Hidden/GT/PreservedTextureAlpha"
{
    Properties
    {
        _MainTex ("Imported texture", 2D) = "white" {}
        _GTForceOpaque ("Negative control", Float) = 0
    }
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Pass
        {
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
            float4 _MainTex_ST;
            float _GTForceOpaque;
            struct Input { float4 vertex : POSITION; float2 uv : TEXCOORD0; };
            struct Varying { float4 position : SV_POSITION; float2 uv : TEXCOORD0; };
            Varying vert(Input input) {
                Varying o;
                o.position = UnityObjectToClipPos(input.vertex);
                o.uv = input.uv * _MainTex_ST.xy + _MainTex_ST.zw;
                return o;
            }
            float4 frag(Varying i) : SV_Target {
                float4 c = _MainTex.SampleLevel(sampler_MainTex, i.uv, 0);
                if (_GTForceOpaque > 0.5) c.a = 1;
                return c;
            }
            ENDHLSL
        }
    }
    Fallback Off
}
