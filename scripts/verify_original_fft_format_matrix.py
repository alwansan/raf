"""CPU-only format gate for four authentic original GpuFFT RenderTexture modes.

Expected Vulkan/SPIR-V mappings are standards-based requirements, NOT evidence
of Unity's chosen VkImageView, Adreno features, or GPU execution.
No proprietary shader or CSharp body is emitted.
"""
import argparse
import json
from pathlib import Path
from scripts.probe_original_fft_target_formats import analyze as original_gpu_formats
from scripts.probe_original_fft_cache_dataflow import source_contract as original_cache_format

# Khronos SPIR-V ImageFormat enumerants, Unity requested format names.
# Actual underlying Unity GraphicsFormat/view still requires runtime verification.
FORMATS = {
    "RGHalf": (7, "VK_FORMAT_R16G16_SFLOAT", True),
    "RGFloat": (6, "VK_FORMAT_R32G32_SFLOAT", True),
    "ARGBHalf": (2, "VK_FORMAT_R16G16B16A16_SFLOAT", False),
    "ARGBFloat": (1, "VK_FORMAT_R32G32B32A32_SFLOAT", False),
}
ALL_MODES = {(two, high) for two in (False, True) for high in (False, True)}


def analyze_formats(original_modes, shader_output_format=1):
    if type(shader_output_format) is not int or shader_output_format not in (0, 1, 2, 6, 7):
        raise ValueError("Unknown or invalid FFT SPIR-V output ImageFormat")
    if not isinstance(original_modes, list) or len(original_modes) != 4:
        raise ValueError("Original FFT source modes incomplete")
    pairs = set()
    outputs = []
    for m in original_modes:
        if not isinstance(m, dict) or type(m.get("two_channels")) is not bool or type(m.get("high_precision")) is not bool:
            raise ValueError("Invalid original FFT channel/precision mode")
        pair = (m["two_channels"], m["high_precision"])
        if pair in pairs:
            raise ValueError("Duplicate original FFT mode")
        pairs.add(pair)
        name = m.get("render_texture_format")
        if name not in FORMATS:
            raise ValueError("Unknown original FFT target format")
        expected = "ARGB" if pair[0] else "RG"
        expected += "Float" if pair[1] else "Half"
        if expected != name:
            raise ValueError("Original FFT mode/format mismatch")
        image_enum, vk, extended = FORMATS[name]
        outputs.append({
            "two_channels": pair[0],
            "high_precision": pair[1],
            "requested_unity_format": name,
            "expected_spirv_storage_image_format": image_enum,
            "expected_vk_image_view_format": vk,
            "requires_storage_image_extended_formats_if_typed": extended,
            "roundtrip_r32g32b32a32f_output_can_exactly_match_requested_view":
                shader_output_format == image_enum if shader_output_format != 0 else False,
        })
    if pairs != ALL_MODES:
        raise ValueError("Original FFT mode set incomplete")
    outputs.sort(key=lambda m: (m["two_channels"], m["high_precision"]))
    exact = [m["requested_unity_format"] for m in outputs
             if shader_output_format == m["expected_spirv_storage_image_format"]]
    return {
        "original_mode_count": 4,
        "roundtrip_output_spirv_format_enum": shader_output_format,
        "exact_typed_view_format_candidates": exact if shader_output_format != 0 else [],
        "typed_format_not_exact_for_original_modes": [
            m["requested_unity_format"] for m in outputs
            if shader_output_format != 0 and m["requested_unity_format"] not in exact],
        "untyped_output_requires_formatless_storage_image_feature_check":
            shader_output_format == 0,
        "mode_matrix": outputs,
        "requested_unity_format_equals_actual_vk_image_view_format_proven": False,
        "adreno_supported_features_proven": False,
        "shader_output_numeric_equivalence_proven": False,
        "authentic_water_kernel_identity_verified": False,
        "build_ready": False,
    }


def inspect(root):
    gpu = list(root.rglob("GpuFFT.cs"))
    cache = list(root.rglob("RenderTexturesCache.cs"))
    if len(gpu) != 1 or len(cache) != 1 or gpu[0].is_symlink() or cache[0].is_symlink():
        raise ValueError("Original FFT source owners missing or ambiguous")
    target = original_gpu_formats(gpu[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n"))
    lineage = original_cache_format(cache[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n"))
    if lineage["format_reference_to_typed_declaration_lexical_hops"] != 0:
        raise ValueError("Original FFT cache direct-format source binding changed")
    result = analyze_formats(target["formats"], shader_output_format=1)
    result["original_gpu_source_sha256"] = target["source_sha256"]
    result["original_cache_source_sha256"] = lineage["source_sha256"]
    result["cache_direct_format_reference_source_verified"] = True
    result["format_mapping_reference"] = "Khronos SPIR-V/Vulkan Format Table"
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    print("RAFT_ORIGINAL_FFT_FORMAT_MATRIX " + json.dumps(inspect(parser.parse_args().source), sort_keys=True))
