// Authored synthetic fixture. No game textures, materials or shader programs.
Shader "Hidden/RAFT/SyntheticMaterialAlpha"
{
    Properties
    {
        [NoScaleOffset] _MainTex ("Synthetic linear texture", 2D) = "white" {}
        // Vector deliberately stores raw linear components; SetColor still
        // exercises the material API without an inspector sRGB color property.
        _Tint ("Synthetic linear tint", Vector) = (1, 1, 1, 1)
        _SrcBlend ("RGB source blend", Float) = 5
        _DstBlend ("RGB destination blend", Float) = 10
    }
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Pass
        {
            Cull Off
            ZWrite Off
            ZTest Always
            Blend [_SrcBlend] [_DstBlend], One OneMinusSrcAlpha
            ColorMask RGBA
            HLSLPROGRAM
            #pragma target 3.5
            #pragma only_renderers vulkan
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            Texture2D<float4> _MainTex;
            SamplerState sampler_MainTex;
            float4 _Tint;
            struct Input { float4 vertex : POSITION; float2 uv : TEXCOORD0; };
            struct Varying { float4 position : SV_POSITION; float2 uv : TEXCOORD0; };
            Varying vert(Input input)
            {
                Varying output;
                output.position = UnityObjectToClipPos(input.vertex);
                output.uv = input.uv;
                return output;
            }
            float4 frag(Varying input) : SV_Target
            {
                return _MainTex.Sample(sampler_MainTex, input.uv) * _Tint;
            }
            ENDHLSL
        }
    }
    Fallback Off
}
