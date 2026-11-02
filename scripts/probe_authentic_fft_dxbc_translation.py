"""Privately translate SHA-authenticated original Raft FFT DXBC, no Unity.

Reports structural SPIR-V and bindings only. Programs remain in TemporaryDirectory
and are never printed, committed, uploaded, or used as Unity replacements.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_directx_shader_bridge import inspect
from scripts.run_original_dxbc_translation_probe import version_tokens

OWNER = "sharedassets0.assets"
PATH_ID = 2456
ORIGINAL_OBJECT_SHA256 = "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247"
EXPECTED_CONTAINERS = 20
MAX_SPIRV_BYTES = 1024 * 1024


def spirv_resource_bindings(data):
    if not isinstance(data, bytes) or len(data) < 20 or len(data) % 4 or len(data) > MAX_SPIRV_BYTES:
        raise ValueError("Unbounded or truncated SPIR-V descriptor module")
    words = struct.unpack("<" + "I" * (len(data) // 4), data)
    if words[0] != 0x07230203 or words[4] != 0:
        raise ValueError("Invalid SPIR-V header")
    offset = 5
    bindings, sets = {}, {}
    while offset < len(words):
        word = words[offset]
        count = word >> 16
        opcode = word & 0xffff
        if count < 1 or offset + count > len(words):
            raise ValueError("Malformed SPIR-V instruction boundary")
        if opcode == 71 and count >= 4:
            target, decoration, literal = words[offset + 1:offset + 4]
            if decoration == 33:
                bindings[target] = literal
            elif decoration == 34:
                sets[target] = literal
        offset += count
    return {
        "descriptor_binding_pairs": sorted([[sets.get(target), value]
                                            for target, value in bindings.items()],
                                           key=lambda x: (x[0] is None, x[0] or 0, x[1])),
        "targets_with_explicit_binding": len(bindings),
        "targets_with_explicit_descriptor_set": len(sets),
        "resource_names_disclosed": False,
    }


def run(command, timeout=15):
    try:
        return subprocess.run(command, capture_output=True, timeout=timeout, check=False).returncode == 0
    except subprocess.TimeoutExpired:
        return False



def compare_roundtrip_contracts(original_reflection, original_bindings,
                                roundtrip_reflection, roundtrip_bindings):
    """Structural comparison only. Never calls this mathematical equivalence."""
    return {
        "compute_entrypoint_model_preserved":
            original_reflection["entrypoint_execution_models"] ==
            roundtrip_reflection["entrypoint_execution_models"],
        "compute_workgroup_shape_preserved":
            original_reflection["declared_local_workgroup_sizes"] ==
            roundtrip_reflection["declared_local_workgroup_sizes"],
        "descriptor_binding_pairs_preserved":
            original_bindings["descriptor_binding_pairs"] ==
            roundtrip_bindings["descriptor_binding_pairs"],
        "original_numeric_results_equal": False,
        "unity_gpu_execution_proven": False,
    }


def cross_compile_roundtrip(source_spv, original_reflection, original_bindings,
                            temporary, index):
    """Return exact stages independently; shader text remains private temp only."""
    result = {
        "spirv_cross_hlsl50_generated": False,
        "glslang_hlsl50_spirv_generated": False,
        "glslang_spirv_valid_for_vulkan_1_1": False,
        "cross_compile_semantically_verified": False,
        "authored_shaderlab_restored": False,
    }
    hlsl = temporary / ("fft_" + str(index) + ".hlsl")
    recomp = temporary / ("fft_" + str(index) + "_roundtrip.spv")
    if not run(["spirv-cross", str(source_spv), "--hlsl",
                "--shader-model", "50", "--output", str(hlsl)], timeout=25):
        return result
    if not hlsl.is_file() or not 0 < hlsl.stat().st_size < 512 * 1024:
        return result
    result["spirv_cross_hlsl50_generated"] = True
    if not run(["glslangValidator", "-V", "-D", "-S", "comp", "-e", "main",
                "-o", str(recomp), str(hlsl)], timeout=25):
        return result
    if not recomp.is_file() or not 0 < recomp.stat().st_size <= MAX_SPIRV_BYTES:
        return result
    try:
        module = recomp.read_bytes()
        parsed = inspect(module)
        bindings = spirv_resource_bindings(module)
    except (ValueError, struct.error):
        return result
    if parsed.get("container") != "SPIR-V":
        return result
    result["glslang_hlsl50_spirv_generated"] = True
    result["glslang_spirv_valid_for_vulkan_1_1"] = run(
        ["spirv-val", "--target-env", "vulkan1.1", str(recomp)], timeout=25)
    result.update(compare_roundtrip_contracts(
        original_reflection, original_bindings, parsed, bindings))
    return result


def probe(root):
    verify_sources(root)
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objs = [o for o in env.file.objects.values()
            if o.type.name == "ComputeShader" and int(o.path_id) == PATH_ID]
    if len(objs) != 1:
        raise ValueError("Original FFT candidate owner missing or ambiguous")
    raw = objs[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original FFT candidate object identity changed")
    containers = scan_blob(raw)["valid_dxbc_containers"]
    if len(containers) != EXPECTED_CONTAINERS:
        raise ValueError("Original FFT DXBC container inventory changed")

    reports = []
    with tempfile.TemporaryDirectory(prefix="raft-authentic-private-fft-") as folder:
        temp = Path(folder)
        for index, item in enumerate(containers):
            offset = item["offset_in_original_object"]
            data = raw[offset: offset + item["bytes"]]
            versions = version_tokens(data)
            if versions != [{"shader_stage_code": 5, "shader_model": [5, 0]}]:
                raise ValueError("Original FFT candidate DXBC stage/model changed")
            original = temp / ("candidate_" + str(index) + ".dxbc")
            spv = temp / ("candidate_" + str(index) + ".spv")
            original.write_bytes(data)
            compiled = run(["vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                            "-o", str(spv), str(original)])
            entry = {
                "dxbc_scan_position_not_proven_unity_kernel_index": index,
                "original_dxbc_sha256": item["binary_sha256"],
                "original_dxbc_bytes": len(data),
                "original_shader_model": "cs_5_0",
                "vkd3d_spirv_generated": False,
                "validated_for_vulkan_1_1": False,
                "original_fft_semantic_equivalence_verified": False,
            }
            if compiled and spv.is_file() and 0 < spv.stat().st_size <= MAX_SPIRV_BYTES:
                spv_bytes = spv.read_bytes()
                information = inspect(spv_bytes)
                if information["container"] != "SPIR-V":
                    raise ValueError("Invalid original FFT conversion output")
                entry["vkd3d_spirv_generated"] = True
                entry["spirv_version"] = information["version"]
                entry["compute_execution_models"] = information["entrypoint_execution_models"]
                entry["local_workgroups"] = information["declared_local_workgroup_sizes"]
                entry["instruction_count"] = information["instruction_count"]
                entry["bindings"] = spirv_resource_bindings(spv_bytes)
                entry["validated_for_vulkan_1_1"] = run(
                    ["spirv-val", "--target-env", "vulkan1.1", str(spv)])
                if entry["validated_for_vulkan_1_1"]:
                    entry["private_hlsl_roundtrip"] = cross_compile_roundtrip(
                        spv, information, entry["bindings"], temp, index)
            reports.append(entry)
    return {
        "original_owner": OWNER,
        "original_path_id": PATH_ID,
        "original_object_sha256": ORIGINAL_OBJECT_SHA256,
        "authentic_programs_inspected": len(reports),
        "vkd3d_spirv_generated_count": sum(x["vkd3d_spirv_generated"] for x in reports),
        "vulkan_1_1_validated_count": sum(x["validated_for_vulkan_1_1"] for x in reports),
        "programs": reports,
        "hlsl50_generated_count": sum(x.get("private_hlsl_roundtrip", {}).get(
            "spirv_cross_hlsl50_generated", False) for x in reports),
        "hlsl50_recompiled_spirv_valid_count": sum(x.get("private_hlsl_roundtrip", {}).get(
            "glslang_spirv_valid_for_vulkan_1_1", False) for x in reports),
        "roundtrip_workgroups_preserved_count": sum(x.get("private_hlsl_roundtrip", {}).get(
            "compute_workgroup_shape_preserved", False) for x in reports),
        "roundtrip_bindings_preserved_count": sum(x.get("private_hlsl_roundtrip", {}).get(
            "descriptor_binding_pairs_preserved", False) for x in reports),
        "original_kernel_indices_verified": False,
        "original_water_resource_contract_verified": False,
        "adreno_gpu_executed": False,
        "shader_programs_exported": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    print("RAFT_AUTHENTIC_FFT_DXBC_VKD3D_PROBE " + json.dumps(probe(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
