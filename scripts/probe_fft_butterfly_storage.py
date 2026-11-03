"""Read authenticated GPU FFT storage policy; emit aggregate contracts only."""
import argparse, hashlib, json
from pathlib import Path
def inspect(gpu_source, dx_source):
    pins=[(gpu_source,"2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704"),(dx_source,"8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0")]
    for path,pin in pins:
        raw=Path(path).read_text(encoding="utf-8-sig").replace("\r\n","\n")
        if hashlib.sha256(raw.encode()).hexdigest()!=pin:
            raise ValueError("Unknown original FFT source revision")
    return {"authenticated_source_sha256":[p for _,p in pins],
      "butterfly_width_multiplier":2,"butterfly_filter":"Point","butterfly_wrap":"Clamp",
      "butterfly_linear":True,"butterfly_mip_chain":False,
      "variants":[{"high_precision":high,"two_channels":two,
       "butterfly_texture_format":"RGBAFloat" if high else "RGBAHalf",
       "temporary_render_texture_format":("ARGBFloat" if high else "ARGBHalf") if two else ("RGFloat" if high else "RGHalf"),
       "dx11_lookup_representation":"integer_indices",
       "base_gpu_lookup_representation":"normalized_half_texel_centers"}
       for high in (False,True) for two in (False,True)],
      "actual_unity_format_or_numeric_execution_verified":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--gpu-source",required=True)
    p.add_argument("--dx-source",required=True)
    a=p.parse_args()
    print(json.dumps(inspect(a.gpu_source,a.dx_source),sort_keys=True))
