Shader "Hidden/GfxLab/ChannelProbe"
{
    Properties
    {
        _MainTex ("Original source texture diagnostic", 2D) = "white" {}
        _Channel ("Raw sampled channel: 0=RGB, 1=R, 2=G, 3=B, 4=A", Float) = 0
    }
    SubShader
    {
        Tags { "Queue" = "Overlay" "RenderType" = "Opaque" }
        Pass
        {
            ZTest Always
            ZWrite Off
            Cull Off
            Blend Off
            ColorMask RGBA
            CGPROGRAM
            #pragma target 3.0
            #pragma vertex vert_img
            #pragma fragment frag
            #include "UnityCG.cginc"
            sampler2D _MainTex;
            float _Channel;
            fixed4 frag(v2f_img i) : SV_Target
            {
                fixed4 sampled = tex2D(_MainTex, i.uv);
                if (_Channel > 3.5) return fixed4(sampled.aaa, 1.0);
                if (_Channel > 2.5) return fixed4(sampled.bbb, 1.0);
                if (_Channel > 1.5) return fixed4(sampled.ggg, 1.0);
                if (_Channel > 0.5) return fixed4(sampled.rrr, 1.0);
                return fixed4(sampled.rgb, 1.0);
            }
            ENDCG
        }
    }
    Fallback Off
}
