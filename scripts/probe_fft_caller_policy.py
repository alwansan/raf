"""Authenticated original FFT caller policy model, not Unity execution."""
import argparse, hashlib, itertools, json
from pathlib import Path
PIN="e7f6b8fd477f321120fc626781f0653fe1168f0e86daad0cdf8d9c4e56b323e9"
def inspect(path):
    raw=Path(path).read_text(encoding="utf-8-sig").replace("\r\n","\n")
    if hashlib.sha256(raw.encode()).hexdigest()!=PIN:
        raise ValueError("Unknown WavesRendererFFT source")
    rows=[]
    for n in (32,64,128,256,512,1024,2048):
        for force,shader,compute,requested in itertools.product((False,True),repeat=4):
            pixel=force or not shader or not compute or n>512
            high=requested or n>=2048
            # Independent invariants, not an assertion that the GPU ran.
            if not pixel and n>512: raise AssertionError("Compute size policy")
            if n>=2048 and not high: raise AssertionError("Large lookup precision")
            rows.append({"resolution":n,"force_pixel":force,"compute_shader_present":shader,
              "supports_compute":compute,"requested_high_precision":requested,
              "selected_path":"pixel" if pixel else "compute",
              "high_precision":high})
    return {"source_sha256":PIN,"case_count":len(rows),"rows":rows,
      "actual_runtime_configuration_known":False,
      "original_csharp_or_gpu_executed":False,
      "half_integer_lookup_negative_control_2048_reachable_by_this_compute_selector":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    print(json.dumps(inspect(p.parse_args().source),sort_keys=True))
