"""New shared-program authored fixture, not an original shader."""
from tools.gt_next23b_translation_replay import author_windows as author
author.SOURCES={
 "vertex":("vs_5_0","float4 main(float4 p:POSITION):SV_Position{return p;}\n"),
 "shared_fragment":("ps_5_0", "Texture2D tex:register(t0); SamplerState samp:register(s0); cbuffer Params:register(b0){float4 tint;}; float4 main():SV_Target{return tex.Sample(samp,float2(0.25,0.75))*tint;}\n"),
}
if __name__=="__main__":author.main()
