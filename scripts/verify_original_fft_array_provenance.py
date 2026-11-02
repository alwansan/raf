"""SHA-pinned provenance gate: original water component ComputeShader[] -> FFT.

Pure CPU/source validation. Correlates Unity bytes, MonoScript, managed source,
and caller literal in one run. Never claims runtime kernel correctness.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.probe_original_fft_serialized_refs import (
    candidate_offsets, raw_tail_array_shape, summarize_monobehaviour_script,
)
from scripts.probe_fft_monoscript_field import inspect as inspect_monoscript
from scripts.probe_fft_managed_asset_links import inspect as inspect_callers

OWNER = "sharedassets0.assets"
COMPONENT_PATH_ID = 23172
COMPONENT_SIZE = 272
COMPONENT_SHA = "de71d828e84ce3960008a31cf82f0e0253bad89600f81a1ec9670d619eab7245"
FFT_PATH_ID = 2456
FFT_SHA = "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247"
FFT_NAME_SHA = "60c1b5ee2352bd6e303aa5fc68c88f61031cf21234f524d54ec02334a8e142d1"
MONOSCRIPT_SHA = "a0ae3f9edfd39bfc4a4df2af896d40ffb4fa0e81963f06c2ee0589e0bf2ad979"
MONOSCRIPT_NAME_SHA = "cb4d4c048bb81a9c6260539769f50e73b91b44ae5d6ccc048038d342154ed687"
MANAGED_CLASS_SHA = "2e56c01c13c84b2bb908a628be6ab5378be7b702185fac9fe906545b602d3893"


def correlate(raw, mono, managed, caller):
    if not isinstance(raw, bytes) or hashlib.sha256(raw).hexdigest() != COMPONENT_SHA:
        raise ValueError("Original component SHA256 mismatch")
    if len(raw) != COMPONENT_SIZE or candidate_offsets(raw, FFT_PATH_ID) != [260]:
        raise ValueError("Original component local PPtr layout changed")
    if not raw_tail_array_shape(raw, [260])[0]["one_item_array_tail_shape_only"]:
        raise ValueError("Original one-item array tail not present")
    if (not mono.get("original_monobehaviour_script_link_verified")
            or mono.get("original_monoscript_raw_sha256") != MONOSCRIPT_SHA
            or mono.get("original_monoscript_class_name_sha256") != MONOSCRIPT_NAME_SHA
            or mono.get("original_script_pointer_file_id") != 1
            or mono.get("original_monoscript_path_id") != 2305
            or mono.get("external_original_owner_basename") != "globalgamemanagers.assets"):
        raise ValueError("Original external MonoScript identity mismatch")
    if (managed.get("original_class_csharp_source_sha256") != MANAGED_CLASS_SHA
            or managed.get("original_direct_compute_shader_array_declarations") != 1
            or managed.get("original_field_type_compute_shader_declarations") != 0):
        raise ValueError("Original CSharp ComputeShader[] declaration mismatch")
    if caller.get("original_literal_matches_serialized_fft_asset_name") != 1:
        raise ValueError("Original WavesRendererFFT asset name literal mismatch")
    return {
        "original_water_monoscript_provenance_verified": True,
        "original_compute_shader_array_source_verified": True,
        "original_one_element_fft_array_tail_correlated": True,
        "original_caller_name_identity_correlated": True,
        "serialized_field_type_tree_verified": False,
        "unity_fft_runtime_kernel_indices_verified": False,
        "android_gpu_executed": False,
    }


def verify(source: Path, managed: Path):
    verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    import UnityPy
    env = UnityPy.load(str(source / OWNER))
    components = [o for o in env.file.objects.values()
                  if o.type.name == "MonoBehaviour" and int(o.path_id) == COMPONENT_PATH_ID]
    computes = [o for o in env.file.objects.values()
                if o.type.name == "ComputeShader" and int(o.path_id) == FFT_PATH_ID]
    if len(components) != 1 or len(computes) != 1:
        raise ValueError("Original component or FFT compute object missing")
    compute = computes[0]
    if hashlib.sha256(compute.get_raw_data()).hexdigest() != FFT_SHA:
        raise ValueError("Original FFT compiled object SHA256 mismatch")
    name = compute.read_typetree().get("m_Name")
    if not isinstance(name, str) or hashlib.sha256(name.encode()).hexdigest() != FFT_NAME_SHA:
        raise ValueError("Original FFT shader name hash mismatch")
    component = components[0]
    mono = summarize_monobehaviour_script(
        component.read_typetree(check_read=False), env.file, source)
    csharp = inspect_monoscript(managed)
    if not csharp["original_managed_type_matched"] or len(csharp["matches"]) != 1:
        raise ValueError("Original MonoScript CSharp identity not uniquely matched")
    caller = inspect_callers(managed)["callers"]["WavesRendererFFT"]
    result = correlate(component.get_raw_data(), mono, csharp["matches"][0], caller)
    return {
        "authenticated_owner": OWNER,
        "original_component_path_id": COMPONENT_PATH_ID,
        "original_fft_compute_path_id": FFT_PATH_ID,
        "original_component_sha256": COMPONENT_SHA,
        "original_compute_object_sha256": FFT_SHA,
        "original_managed_source_sha256": MANAGED_CLASS_SHA,
        **result,
        "source_or_original_asset_modified": False,
        "unity_or_android_build_executed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--managed-source", type=Path, required=True)
    args = p.parse_args()
    print("RAFT_AUTHENTIC_FFT_ARRAY_PROVENANCE " + json.dumps(
        verify(args.source, args.managed_source), sort_keys=True))


if __name__ == "__main__":
    main()
