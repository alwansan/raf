"""Original SHA-pinned FFT slot0 third-butterfly Y: SPIR-V vs HLSL50 roundtrip.

Bounded structural comparison only. No original shader/SSA operands, literals,
raw pixels or compiler errors are output. Does NOT prove Unity/Android parity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.t1_fft_site2_y_cfg import analyze as site2y
from scripts.t1_fft_site2_y_phi_inputs import analyze as phi_census
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS)
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_original_fft_two_pass_software_vulkan import validate_original_compiled_pairs
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

LABELS = (
    "site", "role", "status", "value_origin_boundary", "coordinate_lane_structure",
    "last_writer_evidence_available", "final_writer_categories_possible",
    "static_writer_categories", "conditional_predicate_producers_seen_on_paths_by_final_writer",
    "abstract_states_at_load", "unknown_final_writer_path_possible",
    "uninitialized_final_path_possible", "pointer_escape_seen_on_any_cfg_path",
)

def summary(record):
    if type(record) is not dict or record.get("site") != 2 or record.get("role") != "butterfly":
        raise ValueError("Original third butterfly identity unresolved")
    return {name: record[name] for name in LABELS if name in record}

def pair(original_asm, derived_asm):
    original = site2y(original_asm, require_original=True)
    if not (
        original.get("value_origin_boundary") == "load"
        and original.get("coordinate_lane_structure", {}).get("typed_bitcasts")
            == ["float32_to_sint32:nonload"]
        and original.get("status") == "bounded_cfg_may_path_witnesses"
        and original.get("last_writer_evidence_available") is True
        and original.get("final_writer_categories_possible") == ["float32_constant"]
        and original.get("unknown_final_writer_path_possible") is False
        and original.get("pointer_escape_seen_on_any_cfg_path") is False
        and original.get("uninitialized_final_path_possible") is False
    ):
        raise ValueError("Source-original third fetch Y does not match pinned structural baseline")
    a = summary(original)
    try:
        candidate = summary(site2y(derived_asm, require_original=True))
        comparable = True
    except (ValueError, TypeError, IndexError, KeyError):
        candidate = None
        comparable = False
    if candidate is not None:
        same_boundary = a.get("value_origin_boundary") == candidate.get("value_origin_boundary")
        same_cast = (a.get("coordinate_lane_structure", {}).get("typed_bitcasts")
                     == candidate.get("coordinate_lane_structure", {}).get("typed_bitcasts"))
        same_writer = (candidate.get("last_writer_evidence_available") is True
                       and a.get("final_writer_categories_possible")
                           == candidate.get("final_writer_categories_possible"))
    else:
        same_boundary = same_cast = same_writer = None
    return {
        "status": "authenticated_original_vs_hlsl50_roundtrip_site2_y_static_pair",
        "original": a, "roundtrip": candidate,
        "translated_site2_y_roles_and_cfg_identifiable": comparable,
        "same_coordinate_source_boundary": same_boundary,
        "same_coordinate_typed_bitcast_chain": same_cast,
        "same_cfg_last_writer_categories": same_writer,
        "structural_signature_all_equal": (
            all((same_boundary, same_cast, same_writer)) if comparable else None),
        "source_and_roundtrip_binary_independently_attested": False,
        "structural_identity_proves_numeric_equivalence": False,
        "unity_gpu_compiler_or_runtime_tested": False,
        "authored_game_kernel_mapping_proven": False,
        "android_water_proven": False,
        "private_shader_or_pixel_data_exported": False,
    }

def stage_original_dxbc(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe original source")
    if verify_sources(root, expected={OWNER: EXPECTED[OWNER]})["authenticated_owners"] != 1:
        raise ValueError("SHA-authenticated ZIP2 original missing")
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    matches = [o for o in env.file.objects.values()
               if o.type.name == "ComputeShader" and int(o.path_id) == PATH_ID]
    if len(matches) != 1:
        raise ValueError("Original ComputeShader identity ambiguous")
    obj = matches[0]
    raw = obj.get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original ComputeShader object SHA mismatch")
    containers = scan_blob(raw)["valid_dxbc_containers"]
    if (len(containers) != EXPECTED_CONTAINERS
            or len(validate_original_compiled_pairs(obj.read_typetree(), containers)) != 10):
        raise ValueError("Original compiled pair identity changed")
    slot0 = containers[0]
    start, size = slot0["offset_in_original_object"], slot0["bytes"]
    if (type(start) is not int or type(size) is not int or start < 0
            or not 36 <= size <= 1024 * 1024 or start + size > len(raw)):
        raise ValueError("Original FFT compiled slot0 byte bounds invalid")
    dxbc = raw[start:start + size]
    if hashlib.sha256(dxbc).hexdigest() != slot0["binary_sha256"]:
        raise ValueError("Original DXBC digest mismatch")
    return dxbc

def inspect(original_data):
    dxbc = stage_original_dxbc(original_data)
    with tempfile.TemporaryDirectory(prefix="t1-fft-site2-y-pair-private-") as temp:
        root = Path(temp)
        source, original, hlsl, derived = (
            root/"original.dxbc", root/"original.spv", root/"private.hlsl", root/"derived.spv")
        source.write_bytes(dxbc)
        private_command(["vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                         "-o", str(original), str(source)], timeout=30)
        private_command(["spirv-val", "--target-env", "vulkan1.1", str(original)], timeout=25)
        private_command(["spirv-cross", str(original), "--hlsl", "--shader-model",
                         "50", "--output", str(hlsl)], timeout=30)
        if hlsl.is_symlink() or not hlsl.is_file() or not 0 < hlsl.stat().st_size <= 512*1024:
            raise ValueError("No bounded original-derived HLSL50")
        private_command(["glslangValidator", "-V", "-D", "-S", "comp", "-e", "main",
                         "-o", str(derived), str(hlsl)], timeout=30)
        private_command(["spirv-val", "--target-env", "vulkan1.1", str(derived)], timeout=25)
        outputs = []
        for file in (original, derived):
            run = subprocess.run(["spirv-dis", "--raw-id", str(file)],
                                 check=True, capture_output=True, text=True, timeout=25)
            if not 0 < len(run.stdout) <= 4*1024*1024:
                raise ValueError("Disassembled private shader outside bound")
            outputs.append(run.stdout)
        comparison = pair(*outputs)
        phi_inputs = phi_census(outputs[1], require_original=True)
        if phi_inputs.get("status") != "verified_translated_site2_y_phi_incoming_cfg":
            raise ValueError("Translated third-Y Phi input paths remain unverified")
        comparison["derived_site2_y_phi_inputs"] = phi_inputs
    return {
        "original_owner_and_serialized_compute_sha_verified": True,
        "original_compiled_slots_verified": 20,
        "original_two_pass_pairs_verified": 10,
        "original_dxbc_slot0_sha_verified": True,
        "both_spirv_modules_validated": True,
        **comparison,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-data", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.original_data)
    except (OSError, ValueError, TypeError, KeyError, IndexError,
            subprocess.SubprocessError):
        parser.exit(2, "RAFT_T1_SITE2Y_HLSL_PAIR private_stage_or_source_unverified=true\n")
    print("RAFT_T1_SITE2Y_HLSL_PAIR " + json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
