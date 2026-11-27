Shader "Hidden/GT/V13/NormalRouteProbe" {
 Properties { _MainTex ("Input", 2D) = "white" {} _Mip ("Mip", Float)=0 }
 SubShader { Cull Off ZWrite Off ZTest Always
  Pass {
   CGPROGRAM
   #pragma vertex vert_img
   #pragma fragment frag
   #pragma target 3.0
   #include "UnityCG.cginc"
   sampler2D _MainTex; float _Mip;
   float4 frag(v2f_img i):SV_Target { return tex2Dlod(_MainTex,float4(i.uv,0,_Mip)); }
   ENDCG
  }
  Pass {
   CGPROGRAM
   #pragma vertex vert_img
   #pragma fragment frag
   #pragma target 3.0
   #include "UnityCG.cginc"
   sampler2D _MainTex; float _Mip;
   float4 frag(v2f_img i):SV_Target {
    float3 n=UnpackNormal(tex2Dlod(_MainTex,float4(i.uv,0,_Mip)));
    #if defined(UNITY_NO_DXT5nm)
     return float4(n,1);
    #else
     return float4(n,0);
    #endif
   }
   ENDCG
  }
 }
}
