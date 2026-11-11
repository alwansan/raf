#!/usr/bin/env python3
"""Read-only CL session-summary first-observed evidence gate; no raw game assets."""
import argparse
import json
from pathlib import Path

def _count(value, label):
    # bool is an int subclass, but a JSON true is not an event count.
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value

def analyze(s):
    cats=s["final_error_category_breakdown"]
    milestones=s["final_game_milestones"]
    water=cats["ultimate_water_invalid_pass"]
    fft=cats["water_fft_invalid_compute_kernel"]
    loaded=milestones["world_loaded_message_observed"]
    parts=s["final_render_failure_breakdown"]
    mats=parts["ultimate_water_invalid_pass_by_material"]
    kernels=parts["invalid_kernel_index_root_lines"]
    water_count = _count(water["count"], "water count")
    fft_count = _count(fft["count"], "FFT count")
    material_counts = {key: _count(value, "material count") for key, value in mats.items()}
    kernel_counts = {key: _count(value, "kernel count") for key, value in kernels.items()}
    if water_count == 0 or fft_count == 0:
        raise ValueError("first-observed water/FFT events require positive counts")
    if sum(material_counts.values()) != water_count or sum(kernel_counts.values()) != fft_count:
        raise ValueError("inconsistent material or kernel category partition")
    if _count(loaded["count"], "world-loaded count") < 1:
        raise ValueError("no world-loaded marker")
    w,k,l=[int(x["first_observed_unix_ms"]) for x in (water,fft,loaded)]
    if not w <= k < l:
        raise ValueError("water/FFT-before-world ordering not observed")
    return dict(session=s["session"],first_water_ms=w,first_fft_ms=k,world_loaded_ms=l,
                fft_after_water_ms=k-w,water_before_world_ms=l-w,fft_before_world_ms=l-k,
                water_errors=water_count,fft_errors=fft_count,spectrum=material_counts["spectrum"],
                foam_global=material_counts["foam_global"],kernel_index_6=kernel_counts["index_6"],
                evidence_scope="first-observed ordering only; no kernel identity or causal proof")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("summaries",nargs="+",type=Path)
    args=p.parse_args()
    print(json.dumps([analyze(json.loads(path.read_text())) for path in args.summaries],indent=2))

if __name__=="__main__":
    main()
