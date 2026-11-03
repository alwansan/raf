"""Original FFT cache lifetime lexical audit and lower-bound texture footprint.

CPU only. Reports SHA-verified source API categories and bytes for ONE texture,
not the number of simultaneous render targets, active quality, heap usage, FPS
or proof of a leak. No original CSharp/source snippets are printed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from scripts.probe_original_android_display_paths import mask_csharp_noncode
from scripts.probe_original_fft_target_formats import analyze as original_formats
from scripts.probe_original_fft_cache_dataflow import source_contract, ORIGINAL_SHA

# Source-verified requested quality maximums, not actual Android active resolution.
QUALITY_CAPS = (32, 64, 256, 512, 512, 256, 256)
BPP = {"RGHalf": 4, "RGFloat": 8, "ARGBHalf": 8, "ARGBFloat": 16}
CALLS = {
    "render_texture_construct": r"\bnew\s+RenderTexture\s*\(",
    "render_texture_create": r"\.\s*Create\s*\(",
    "texture_release": r"\.\s*Release\s*\(",
    "dispose_call": r"\.\s*Dispose\s*\(",
    "destroy_call": r"\b(?:Object\s*\.\s*)?Destroy(?:Immediate)?\s*\(",
    "collection_clear": r"\.\s*Clear\s*\(",
    "collection_remove": r"\.\s*Remove\s*\(",
    "cache_get": r"\bGetCache\s*\(",
}


def footprint(one_requested_resolution, fmt):
    if type(one_requested_resolution) is not int or one_requested_resolution < 32 or one_requested_resolution > 512 or (one_requested_resolution & (one_requested_resolution - 1)):
        raise ValueError("Requested FFT resolution not an accepted tested power of two")
    if fmt not in BPP:
        raise ValueError("Unrecognized original FFT target format")
    dimension = one_requested_resolution * 2
    return {"fft_resolution": one_requested_resolution, "render_target_dimension": [dimension, dimension],
            "requested_format": fmt, "estimated_one_target_storage_bytes": dimension * dimension * BPP[fmt],
            "format_bytes_per_pixel": BPP[fmt],
            "actual_memory_allocated_or_target_count_proven": False}


def scan_cache(source, expected=ORIGINAL_SHA):
    if not isinstance(source, str) or len(source) > 750000 or hashlib.sha256(source.encode()).hexdigest() != expected:
        raise ValueError("Original cache lifecycle source fingerprint mismatch")
    source_contract(source, expected)
    code = mask_csharp_noncode(source)
    counts = {name: len(re.findall(pattern, code)) for name, pattern in CALLS.items()}
    return {
        "source_sha256": expected,
        "bounded_callsite_counts": counts,
        "source_lexical_lifetime_reviewed": True,
        "no_memory_leak_proven": False,
        "actual_gpu_allocation_count_or_release_reachability_proven": False,
        "unity_or_phone_executed": False,
    }


def inspect(root):
    gpu = list(root.rglob("GpuFFT.cs"))
    cache = list(root.rglob("RenderTexturesCache.cs"))
    if len(gpu) != 1 or len(cache) != 1 or any(p.is_symlink() for p in gpu + cache):
        raise ValueError("Original FFT lifecycle sources missing or ambiguous")
    original = original_formats(gpu[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n"))
    lifetime = scan_cache(cache[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n"))
    modes = [m["render_texture_format"] for m in original["formats"]]
    if set(modes) != set(BPP) or len(modes) != 4:
        raise ValueError("Original FFT quality/format modes changed")
    estimates = []
    for n in QUALITY_CAPS:
        estimates.append({"maximum_quality_cap_only": n,
                          "per_target": [footprint(n, fmt) for fmt in sorted(BPP)]})
    return {
        "cache_lifetime_calls": lifetime,
        "source_gpu_sha256": original["source_sha256"],
        "quality_cap_sequence_from_separate_authenticated_resource_report": list(QUALITY_CAPS),
        "single_target_footprints": estimates,
        "full_render_texture_cache_footprint_or_active_quality_proven": False,
        "resource_count_lifetime_device_memory_proven": False,
        "build_ready": False,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    print("RAFT_ORIGINAL_FFT_LIFETIME_FOOTPRINT " + json.dumps(inspect(p.parse_args().source), sort_keys=True))
