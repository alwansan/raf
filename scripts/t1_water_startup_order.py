#!/usr/bin/env python3
"""Read-only CL session-summary first-observed evidence gate; no raw game assets."""
import argparse
import json
from pathlib import Path

def analyze(s):
    cats=s["final_error_category_breakdown"]
    milestones=s["final_game_milestones"]
    water=cats["ultimate_water_invalid_pass"]
    fft=cats["water_fft_invalid_compute_kernel"]
    loaded=milestones["world_loaded_message_observed"]
    parts=s["final_render_failure_breakdown"]
    mats=parts["ultimate_water_invalid_pass_by_material"]
    kernels=parts["invalid_kernel_index_root_lines"]
    if sum(mats.values()) != water["count"] or sum(kernels.values()) != fft["count"]:
        raise ValueError("inconsistent material or kernel category partition")
    if loaded["count"] < 1:
        raise ValueError("no world-loaded marker")
    w,k,l=[int(x["first_observed_unix_ms"]) for x in (water,fft,loaded)]
    if not w <= k < l:
        raise ValueError("water/FFT-before-world ordering not observed")
    return dict(session=s["session"],first_water_ms=w,first_fft_ms=k,world_loaded_ms=l,
                fft_after_water_ms=k-w,water_before_world_ms=l-w,fft_before_world_ms=l-k,
                water_errors=water["count"],fft_errors=fft["count"],spectrum=mats["spectrum"],
                foam_global=mats["foam_global"],kernel_index_6=kernels["index_6"],
                evidence_scope="first-observed ordering only; no kernel identity or causal proof")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("summaries",nargs="+",type=Path)
    args=p.parse_args()
    print(json.dumps([analyze(json.loads(path.read_text())) for path in args.summaries],indent=2))

if __name__=="__main__":
    main()
