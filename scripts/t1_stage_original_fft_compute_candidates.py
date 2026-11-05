"""Stage 20 original-DXBC-derived FFT Unity .compute CANDIDATES privately.

This is a concrete recovered translation artifact for an isolated Unity
import experiment, not original authored Unity source and NOT runtime mapping.
Original bytecode, generated HLSL and all private resource identifiers remain
inside a disposable scratch project; only bounded SHA and counts are logged.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from scripts.b47_compute_kernel_contract import kernel_entrypoint_profile
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)
from scripts.probe_directx_shader_bridge import inspect
from scripts.probe_fft_variant_table import EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_original_fft_two_pass_software_vulkan import validate_original_compiled_pairs
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

MAX_DXBC = 1024 * 1024
MAX_HLSL = 512 * 1024
ENTRY = "main"
FILES = 20
ORIGINAL_FFT_OBJECT_SHA256 = ORIGINAL_OBJECT_SHA256  # Public pin alias for tests/manifest only.


def sanitize_translated_compute(hlsl: bytes, workgroup: int) -> bytes:
    """Require a real translated main with source-local group, no invented body.

    The only addition is a Unity import pragma; no private HLSL instructions
    or resource names are rewritten. This is NOT source authoring recovery.
    """
    if type(hlsl) is not bytes or not 0 < len(hlsl) <= MAX_HLSL or b"\x00" in hlsl:
        raise ValueError("Private translation HLSL absent, huge or binary")
    if type(workgroup) is not int or workgroup not in (64, 128, 256, 512, 1024):
        raise ValueError("Unexpected original FFT candidate workgroup")
    try:
        original_text = hlsl.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Reconstructed HLSL must be UTF-8") from exc
    if re.search(r"(?m)^\s*#\s*pragma\s+kernel\b", original_text):
        raise ValueError("Refuse to override translated shader kernel declarations")
    candidate = "#pragma kernel main\n" + original_text
    structure = kernel_entrypoint_profile(candidate)
    if not (structure["kernel_count"] == 1 and
            structure["kernels_with_structural_entrypoints"] == 1 and
            structure["all_kernel_entrypoints_structural"]):
        raise ValueError("SPIRV-Cross output not a structurally importable single Unity kernel")
    # Compare only explicitly authored local-size literals, not a guessed
    # compiled-slot-to-original-runtime-kernel lookup.
    compact = re.sub(r"\s+", "", original_text)
    if f"[numthreads({workgroup},1,1)]" not in compact:
        raise ValueError("Reconstructed Unity candidate local workgroup changed")
    return candidate.encode("utf-8")


def validate_import_candidate_manifest(manifest, source_dir: Path):
    """Metadata-only checker; no shader source is returned or printed."""
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version", "provenance", "original_fft_object_sha256",
        "candidate_count", "rows", "original_runtime_kernel_mapping_proven",
        "unity_import_proven", "android_gpu_proven",
    }:
        raise ValueError("Original-derived Unity candidate manifest invalid")
    if (manifest["schema_version"] != 1 or manifest["candidate_count"] != FILES or
            manifest["provenance"] != "DXBC_VKD3D_SPIRVCROSS_ROUNDTRIP_NOT_AUTHORED" or
            manifest["original_fft_object_sha256"] != ORIGINAL_OBJECT_SHA256 or
            manifest["original_runtime_kernel_mapping_proven"] is not False or
            manifest["unity_import_proven"] is not False or
            manifest["android_gpu_proven"] is not False):
        raise ValueError("Cannot promote candidate into original authored Unity shader proof")
    rows = manifest["rows"]
    if not isinstance(rows, list) or len(rows) != FILES:
        raise ValueError("Original compiled slot candidate count incorrect")
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {
            "compiled_slot", "compute_asset", "candidate_sha256",
            "original_dxbc_sha256", "expected_group_x", "runtime_kernel_identity_proven",
        }:
            raise ValueError("Unexpected FFT candidate row")
        if (type(row["compiled_slot"]) is not int or row["compiled_slot"] != index or
                type(row["expected_group_x"]) is not int or
                row["expected_group_x"] != EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[index] or
                row["runtime_kernel_identity_proven"] is not False):
            raise ValueError("Compiled slot/group misrepresented as runtime identity")
        asset = f"Assets/T1OriginalDerived/FFT_Candidate_{index:02d}.compute"
        if row["compute_asset"] != asset:
            raise ValueError("Unknown or traversing private FFT compute asset path")
        for label in ("candidate_sha256", "original_dxbc_sha256"):
            if not isinstance(row[label], str) or not re.fullmatch(r"[0-9a-f]{64}", row[label]):
                raise ValueError("Unverified FFT candidate digest")
        path = source_dir / row["compute_asset"]
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_HLSL + 64:
            raise ValueError("Private compute candidate missing")
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != row["candidate_sha256"]:
            raise ValueError("Private staged FFT compute candidate SHA drift")
        if not kernel_entrypoint_profile(body.decode("utf-8"))["all_kernel_entrypoints_structural"]:
            raise ValueError("Private staged Unity kernel structure changed")
    return {"candidate_slots_authenticated": FILES, "unity_import_proven": False,
            "runtime_mapping_proven": False, "private_source_published": False}


def stage_original_candidates(original_data: Path, destination: Path, *, keep_first_pair_spirv: bool = False):
    """All-or-nothing private Unity project staging from authenticated ZIP2 bytes."""
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError("Refusing to overwrite existing Unity private candidate project")
    if not destination.parent.is_dir() or destination.parent.is_symlink():
        raise ValueError("Choose an existing regular private staging parent")
    auth = verify_sources(original_data, expected={OWNER: EXPECTED[OWNER]})
    if auth["authenticated_owners"] != 1:
        raise ValueError("Original FFT owner fingerprint not authenticated")
    import UnityPy
    env = UnityPy.load(str(Path(original_data) / OWNER))
    items = [obj for obj in env.file.objects.values()
             if obj.type.name == "ComputeShader" and int(obj.path_id) == PATH_ID]
    if len(items) != 1:
        raise ValueError("Original FFT ComputeShader missing or ambiguous")
    raw = items[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original FFT serialized compute object digest mismatch")
    original = scan_blob(raw)["valid_dxbc_containers"]
    if len(original) != EXPECTED_CONTAINERS:
        raise ValueError("Authenticated FFT compiled candidate inventory drift")
    if len(validate_original_compiled_pairs(items[0].read_typetree(), original)) != 10:
        raise ValueError("Original two-pass compiled pair order unverified")

    # Files and private shader bytes are created only beneath a temporary
    # sibling; the requested project path becomes visible atomically after all
    # twenty authentic translations, checks and manifests pass.
    manifest = {
        "schema_version": 1,
        "provenance": "DXBC_VKD3D_SPIRVCROSS_ROUNDTRIP_NOT_AUTHORED",
        "original_fft_object_sha256": ORIGINAL_OBJECT_SHA256,
        "candidate_count": FILES, "rows": [],
        "original_runtime_kernel_mapping_proven": False,
        "unity_import_proven": False, "android_gpu_proven": False,
    }
    with tempfile.TemporaryDirectory(prefix=".t1-authentic-fft-", dir=str(destination.parent)) as tmp:
        root = Path(tmp)
        candidates = root / "Assets/T1OriginalDerived"
        candidates.mkdir(parents=True)
        (root / "Packages").mkdir()
        (root / "ProjectSettings").mkdir()
        (root / "Packages/manifest.json").write_text('{"dependencies":{}}\n')
        (root / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
        temp = root / "_private_compiler"
        temp.mkdir()
        vulkan = root / "_private_vulkan"
        if keep_first_pair_spirv:
            vulkan.mkdir(mode=0o700)
        for idx, item in enumerate(original):
            offset, count = item["offset_in_original_object"], item["bytes"]
            if (type(offset) is not int or type(count) is not int or
                    count < 32 or count > MAX_DXBC or
                    offset < 0 or offset + count > len(raw)):
                raise ValueError("Original DXBC slot byte range invalid")
            dxbc = raw[offset:offset + count]
            dxbc_sha = hashlib.sha256(dxbc).hexdigest()
            if dxbc_sha != item["binary_sha256"]:
                raise ValueError("Original compiled program SHA differs from serialization")
            input_path = temp / "original.dxbc"
            spv = temp / "original.spv"
            hlsl_path = temp / "private.hlsl"
            check_spv = temp / "roundtrip.spv"
            input_path.write_bytes(dxbc)
            private_command(["vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                             "-o", str(spv), str(input_path)], timeout=30)
            private_command(["spirv-val", "--target-env", "vulkan1.1", str(spv)], timeout=20)
            original_spv = inspect(spv.read_bytes())
            required_group = EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[idx]
            if original_spv["declared_local_workgroup_sizes"] != [[required_group, 1, 1]]:
                raise ValueError("Original compiled FFT workgroup changed on SPIR-V translation")
            private_command(["spirv-cross", str(spv), "--hlsl", "--shader-model", "50",
                             "--output", str(hlsl_path)], timeout=30)
            if not hlsl_path.is_file() or hlsl_path.is_symlink():
                raise ValueError("Original-derived HLSL not generated")
            source = sanitize_translated_compute(hlsl_path.read_bytes(), required_group)
            # GlSLang roundtrip tests translated HLSL independently. It does
            # NOT prove that Unity uses the same compiler or codegen.
            private_command(["glslangValidator", "-V", "-D", "-S", "comp",
                             "-e", "main", "-o", str(check_spv), str(hlsl_path)], timeout=30)
            private_command(["spirv-val", "--target-env", "vulkan1.1", str(check_spv)], timeout=20)
            roundtrip = inspect(check_spv.read_bytes())
            if roundtrip["declared_local_workgroup_sizes"] != [[required_group, 1, 1]]:
                raise ValueError("Original-derived HLSL recompiled with different workgroup size")
            relative = f"Assets/T1OriginalDerived/FFT_Candidate_{idx:02d}.compute"
            (root / relative).write_bytes(source)
            manifest["rows"].append({
                "compiled_slot": idx, "compute_asset": relative,
                "candidate_sha256": hashlib.sha256(source).hexdigest(),
                "original_dxbc_sha256": dxbc_sha,
                "expected_group_x": required_group,
                "runtime_kernel_identity_proven": False,
            })
            if keep_first_pair_spirv and idx in (0, 1):
                spv.replace(vulkan / f"slot{idx}.spv")
            for file in (input_path, spv, hlsl_path, check_spv):
                file.unlink(missing_ok=True)
        if len(manifest["rows"]) != FILES:
            raise ValueError("Unproven original compiled program count")
        (root / "Assets/T1OriginalDerived/PrivateCandidates.json").write_text(
            json.dumps(manifest, sort_keys=True), encoding="utf-8")
        result = validate_import_candidate_manifest(manifest, root)
        temp.rmdir()
        if destination.exists():
            raise ValueError("Concurrent private staging collision")
        root.rename(destination)
    return {**result, "original_fft_object_sha256": ORIGINAL_OBJECT_SHA256,
            "original_compiled_programs_reconstructed": FILES,
            "unity_compute_assets_staged_privately": FILES,
            "source_conversion": "original_DXBC_to_SPIRV_to_HLSL50_to_SPIRV",
            "actual_unity_editor_import": False, "adreno_device_test": False,
            "real_game_compute_asset_replaced": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-data", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--keep-first-pair-spirv", action="store_true",
                        help="Retain validated original-derived SPIR-V privately for Vulkan comparison")
    args = parser.parse_args()
    result = stage_original_candidates(args.original_data, args.project,
                                       keep_first_pair_spirv=args.keep_first_pair_spirv)
    print("RAFT_T1_ORIGINAL_DERIVED_UNITY_CANDIDATES " +
          json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
