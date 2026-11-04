"""B18: original FFT DXBC read/write declarations vs translated SPIR-V image roles.

Checks SHA-pinned original SHEX t0/t1/u0 and workgroup against Vulkan
SPIR-V sampled/storage image classes. No private program, source, identifier,
disassembly, converter stdout/stderr, or image pixels leave the runner.
A resource-class/count match is NOT an exact descriptor-to-DXBC-register
identity, Unity FindKernel mapping, Unity import, or Android GPU proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.b18_fft_compiled_rdef_bindings import compiled_shex_registers, ROLE_KEYS
from scripts.probe_directx_shader_bridge import inspect
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_variant_table import (
    correlate_original_variant_bytecode, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
)
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_authentic_fft_dxbc_translation import OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources


def check_image_role_classes(source_dxbc: bytes, converted_spirv: bytes) -> dict:
    """Compare executable source resource roles to converted module *classes*."""
    declared, source_group = compiled_shex_registers(source_dxbc)
    if set(declared) != ROLE_KEYS or not source_group:
        raise ValueError("Missing original FFT DXBC resource declarations")
    module = inspect(converted_spirv)
    if module.get("container") != "SPIR-V":
        raise ValueError("Missing translated SPIR-V module")
    if module.get("entrypoint_execution_models") != {5: 1}:
        raise ValueError("Translated stage not one compute entrypoint")
    if module.get("declared_local_workgroup_sizes") != [source_group]:
        raise ValueError("Translated compute threadgroup changed")
    contract = image_resource_contracts(converted_spirv)
    image_rows = contract["typed_image_declarations"]
    if len(image_rows) != len(ROLE_KEYS):
        raise ValueError("Translated image count differs from original declared roles")
    classes = {"read": 0, "write": 0}
    seen = set()
    for row in image_rows:
        descriptor = (row["set"], row["binding"])
        if (any(type(value) is not int or not 0 <= value <= 65535
                for value in descriptor) or descriptor in seen):
            raise ValueError("Translated image descriptor set/binding ambiguous")
        seen.add(descriptor)
        if row["dimension_enum"] != 1 or row["arrayed"] != 0 or row["multisampled"] != 0:
            raise ValueError("Translated image dimensionality differs from source Texture2D")
        if row["sampled_enum"] == 1:
            classes["read"] += 1
        elif row["sampled_enum"] == 2:
            classes["write"] += 1
        else:
            raise ValueError("Translated image sampled/storage type ambiguous")
    if classes != {"read": 2, "write": 1}:
        raise ValueError("Translated image read/write class count differs from original")
    return {
        "original_compiled_read_registers": [0, 1],
        "original_compiled_write_registers": [0],
        "translated_sampled_texture2d_count": 2,
        "translated_storage_texture2d_count": 1,
        "workgroup_dimensions_preserved": True,
        "individual_original_register_to_spirv_descriptor_mapping_verified": False,
        "original_resource_names_proven_by_compiler": False,
        "unity_runtime_kernel_mapping_verified": False,
        "android_pixels_verified": False,
    }


def inspect_original(root: Path) -> dict:
    verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objects = [o for o in env.file.objects.values()
               if o.type.name == "ComputeShader" and int(o.path_id) == PATH_ID]
    if len(objects) != 1:
        raise ValueError("Pinned FFT original object absent or duplicated")
    raw = objects[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Pinned original FFT object SHA changed")
    scanned = scan_blob(raw)["valid_dxbc_containers"]
    matched = correlate_original_variant_bytecode(
        objects[0].read_typetree(), scanned, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT
    )
    if matched.get("authentic_compiled_variants_verified_in_original_order") != 20:
        raise ValueError("Original typed/compiled program mapping not verified")
    samples = 0
    with tempfile.TemporaryDirectory(prefix="raft-b18-fft-spv-private-") as tmp:
        folder = Path(tmp)
        for index, item in enumerate(scanned):
            first = item["offset_in_original_object"]
            original = raw[first:first + item["bytes"]]
            if hashlib.sha256(original).hexdigest() != item["binary_sha256"]:
                raise ValueError("Private DXBC source program fingerprint mismatch")
            dxbc = folder / ("source-" + str(index) + ".dxbc")
            spv = folder / ("converted-" + str(index) + ".spv")
            dxbc.write_bytes(original)
            try:
                p = subprocess.run(
                    ["vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                     "-o", str(spv), str(dxbc)],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=False, timeout=25
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ValueError("Private DXBC conversion tool failed") from None
            if p.returncode != 0 or not spv.is_file() or not 0 < spv.stat().st_size <= 1048576:
                raise ValueError("Private DXBC-to-SPIRV conversion rejected program")
            parity = check_image_role_classes(original, spv.read_bytes())
            if not parity["workgroup_dimensions_preserved"]:
                raise ValueError("FFT program workgroup parity not established")
            samples += 1
    if samples != 20:
        raise ValueError("Insufficient source-authentic FFT compiled samples")
    return {
        "pinned_zip2_commit": "15964ea8f246b6e076ce26b60931ee2e1a9a2385",
        "original_object_sha256": ORIGINAL_OBJECT_SHA256,
        "source_authenticated_program_count": 20,
        "spv_translated_source_image_class_and_workgroup_parity": samples,
        "source_read_t0_t1_and_write_u0_role_counts_preserved": True,
        "individual_dxbc_register_to_spv_descriptor_identity_verified": False,
        "compiled_resource_names_verified": False,
        "unity_editor_or_android_gpu_executed": False,
        "original_shader_bytes_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    try:
        result = inspect_original(args.source)
    except (ValueError, OSError, TypeError, KeyError, subprocess.SubprocessError):
        # Do NOT print private converter diagnostic strings or source names.
        print("RAFT_B18_FFT_SPV_ROLES " + json.dumps({
            "status": "REJECTED", "original_spv_roles_proven": False
        }, sort_keys=True))
        return 2
    print("RAFT_B18_FFT_SPV_ROLES " + json.dumps({
        "status": "PASS", **result
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
