"""B18: verify explicit vkd3d DXBC t0/t1/u0 -> SPIR-V descriptor interfaces.

Private original DXBC, converted SPIR-V, temporary executable and all private
diagnostic text remain in runner temp. This tests compiler API mapping and
destination descriptor types; it is not proof of shader HLSL names, Unity
FindKernel, original color/water pixel equivalence or Adreno functionality.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.b18_fft_compiled_rdef_bindings import compiled_shex_registers, ROLE_KEYS
from scripts.b18_fft_spirv_binding_roles import check_image_role_classes
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_variant_table import (
    EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
    correlate_original_variant_bytecode,
)
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256,
)
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

# These are *our chosen* public converter interface bindings, never original
# game naming claims. Distinct layouts disallow accepting the default mapping.
INTERFACES = {
    "A": {("input", 0): (3, 11), ("input", 1): (3, 17),
          ("output", 0): (3, 23)},
    "B": {("input", 0): (4, 29), ("input", 1): (4, 13),
          ("output", 0): (4, 31)},
}


def verify_explicit_descriptor_layout(source_dxbc: bytes, translated_spv: bytes,
                                      interface_name: str) -> dict:
    if interface_name not in INTERFACES:
        raise ValueError("Unapproved B18 DXBC interface profile")
    original, group = compiled_shex_registers(source_dxbc)
    if set(original) != ROLE_KEYS:
        raise ValueError("Authenticated source DXBC register inventory changed")
    prior = check_image_role_classes(source_dxbc, translated_spv)
    if not prior["workgroup_dimensions_preserved"]:
        raise ValueError("Original FFT group changed")
    images = image_resource_contracts(translated_spv)["typed_image_declarations"]
    if len(images) != 3:
        raise ValueError("Compiled interface must contain exactly three images")
    roles = {}
    for image in images:
        address = (image["set"], image["binding"])
        if any(type(x) is not int or x < 0 or x > 65535 for x in address):
            raise ValueError("Missing numeric SPIR-V descriptor set or binding")
        if address in roles:
            raise ValueError("Duplicate explicit SPIR-V binding")
        if image["dimension_enum"] != 1 or image["arrayed"] or image["multisampled"]:
            raise ValueError("Translated descriptor is not a two-dimensional image")
        if image["sampled_enum"] == 1:
            kind = "input"
        elif image["sampled_enum"] == 2:
            kind = "output"
        else:
            raise ValueError("SPIR-V descriptor has ambiguous read/write role")
        roles[address] = kind
    expected = {value: key[0] for key, value in INTERFACES[interface_name].items()}
    if roles != expected:
        raise ValueError("Targeted vkd3d interface descriptor sets/bindings were not respected")
    return {
        "compiler_interface_profile": interface_name,
        "original_fft_register_roles": ["t0", "t1", "u0"],
        "explicit_descriptor_set_binding_presence_matched": True,
        "read_write_image_types_preserved": True,
        "workgroup_xyz": group,
        "true_vkd3d_interface_register_contract_requested": True,
        "same_class_input_image_behavior_distinguished": False,
        "unity_runtime_kernel_id_mapping_verified": False,
        "android_gpu_pixels_verified": False,
    }


def inspect_original(root: Path, executable: Path) -> dict:
    if not executable.is_file() or executable.is_symlink():
        raise ValueError("Private explicit interface translation tool unavailable")
    verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objs = [o for o in env.file.objects.values()
            if o.type.name == "ComputeShader" and int(o.path_id) == PATH_ID]
    if len(objs) != 1:
        raise ValueError("Original FFT ComputeShader pathID not unique")
    obj = objs[0]
    raw = obj.get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original FFT ComputeShader object SHA mismatch")
    candidates = scan_blob(raw)["valid_dxbc_containers"]
    registry = correlate_original_variant_bytecode(
        obj.read_typetree(), candidates, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT
    )
    if registry["authentic_compiled_variants_verified_in_original_order"] != 20:
        raise ValueError("Original typed compiled slot inventory changed")
    verified = {key: 0 for key in INTERFACES}
    with tempfile.TemporaryDirectory(prefix="raft-b18-private-explicit-spv-") as tmp:
        folder = Path(tmp)
        for n, item in enumerate(candidates):
            start = item["offset_in_original_object"]
            original = raw[start:start + item["bytes"]]
            if hashlib.sha256(original).hexdigest() != item["binary_sha256"]:
                raise ValueError("Original DXBC per-slot SHA mismatch")
            src = folder / (str(n) + ".dxbc")
            src.write_bytes(original)
            for profile in INTERFACES:
                dst = folder / (str(n) + "-" + profile + ".spv")
                try:
                    proc = subprocess.run(
                        [str(executable), str(src), str(dst), profile],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, check=False, timeout=25
                    )
                except (subprocess.TimeoutExpired, OSError):
                    raise ValueError("Private vkd3d interface compiler unavailable") from None
                if proc.returncode or not dst.is_file() or dst.is_symlink() or not 20 <= dst.stat().st_size <= 1048576:
                    raise ValueError("Explicit compiler translation failed or module malformed")
                verify_explicit_descriptor_layout(original, dst.read_bytes(), profile)
                verified[profile] += 1
    if verified != {"A": 20, "B": 20}:
        raise ValueError("Not all original FFT programs met explicit interface mapping")
    return {
        "original_object_sha256": ORIGINAL_OBJECT_SHA256,
        "pinned_zip2_commit": "15964ea8f246b6e076ce26b60931ee2e1a9a2385",
        "source_authenticated_compiled_fft_programs": 20,
        "explicit_interface_A_programs_verified": verified["A"],
        "explicit_interface_B_programs_verified": verified["B"],
        "two_distinct_target_descriptor_layouts_honored": True,
        "per_class_original_t0_t1_u0_source_roles_verified": True,
        "same_class_t0_t1_runtime_input_behavior_independently_proven": False,
        "unity_runtime_compute_import_verified": False,
        "android_device_water_pixels_verified": False,
        "private_shader_names_code_or_pixel_buffers_disclosed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--compiler", type=Path, required=True)
    args = p.parse_args()
    try:
        result = inspect_original(args.source, args.compiler)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        # Only literal, source-free failure codes may leave the private runner.
        reason = {
            "Private explicit interface translation tool unavailable": "COMPILER_MISSING",
            "Original FFT ComputeShader pathID not unique": "SOURCE_OBJECT_MISSING",
            "Original FFT ComputeShader object SHA mismatch": "SOURCE_OBJECT_SHA",
            "Original typed compiled slot inventory changed": "SOURCE_COMPILED_ORDER",
            "Original DXBC per-slot SHA mismatch": "SOURCE_SLOT_SHA",
            "Private vkd3d interface compiler unavailable": "COMPILER_INVOCATION",
            "Explicit compiler translation failed or module malformed": "COMPILER_TRANSLATION",
            "Targeted vkd3d interface descriptor sets/bindings were not respected": "SPIRV_BINDING_MAP_DIFFERENT",
            "Missing numeric SPIR-V descriptor set or binding": "SPIRV_DESCRIPTOR_ABSENT",
            "Duplicate explicit SPIR-V binding": "SPIRV_DESCRIPTOR_DUPLICATE",
            "Original FFT group changed": "SPIRV_GROUP_MISMATCH",
            "Translated descriptor is not a two-dimensional image": "SPIRV_IMAGE_DIMENSION",
            "SPIR-V descriptor has ambiguous read/write role": "SPIRV_IMAGE_ACCESS",
            "Compiled interface must contain exactly three images": "SPIRV_IMAGE_COUNT",
            "Not all original FFT programs met explicit interface mapping": "PROGRAM_COUNT",
        }.get(str(exc), type(exc).__name__)
        print("RAFT_B18_FFT_EXPLICIT_MAP " + json.dumps({
            "status": "REJECTED", "reason_code": reason,
            "original_explicit_mapping_proven": False
        }, sort_keys=True))
        return 2
    print("RAFT_B18_FFT_EXPLICIT_MAP " + json.dumps({"status": "PASS", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
