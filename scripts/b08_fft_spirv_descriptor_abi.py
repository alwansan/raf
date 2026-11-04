"""B08: exact numeric SPIR-V image descriptor ABI for authenticated original FFT.

This complements B18's 2-sampled/1-storage image-class verification.  It
rejects drift across all 20 source-authenticated compiled programs before an
authentic private runtime stage may use those bindings.  No guess is made that
one sampled descriptor is DXBC t0 rather than t1, or that compiled position is
a Unity runtime FindKernel ID. No proprietary bytecode/name is published.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.b18_fft_spirv_binding_roles import check_image_role_classes
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_spirv_image_flow import image_slot_dataflow
from scripts.probe_fft_variant_table import (
    correlate_original_variant_bytecode, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
)
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)
from scripts.verify_targeted_lfs_compute_sources import (
    EXPECTED as ORIGINAL_OWNERS, verify_sources,
)

SOURCE_COMMIT = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
IMAGE_FIELDS = ("set", "binding", "scalar_kind", "scalar_bits",
                "format_enum", "access_enum")
EXPECTED_COUNT = 20


def _entry(row):
    """Publish bounded descriptor parameters, not private source identifiers."""
    if not isinstance(row, dict):
        raise ValueError("Invalid translated image descriptor")
    values = [row[k] for k in IMAGE_FIELDS]
    if (type(values[0]) is not int or not 0 <= values[0] <= 65535
            or type(values[1]) is not int or not 0 <= values[1] <= 65535
            or values[2] not in ("float", "sint", "uint")
            or type(values[3]) is not int or values[3] not in (16, 32, 64)
            or type(values[4]) is not int or not 0 <= values[4] <= 65535
            or values[5] is not None and (type(values[5]) is not int
                                         or not 0 <= values[5] <= 65535)):
        raise ValueError("Ambiguous translated image descriptor ABI")
    return tuple(values)


def describe_pair(original_dxbc: bytes, translated_spirv: bytes):
    """A verified original-source role count plus a typed *numeric* target ABI."""
    parity = check_image_role_classes(original_dxbc, translated_spirv)
    if (not parity["workgroup_dimensions_preserved"]
            or parity["individual_original_register_to_spirv_descriptor_mapping_verified"]):
        raise ValueError("Original role parity cannot establish numeric ABI")
    items = image_resource_contracts(translated_spirv)["typed_image_declarations"]
    if len(items) != 3:
        raise ValueError("Expected three original FFT image descriptors")
    reads, writes = [], []
    for row in items:
        if (row["dimension_enum"] != 1 or row["arrayed"] != 0
                or row["multisampled"] != 0):
            raise ValueError("Translated image shape changed")
        descriptor = _entry(row)
        if row["sampled_enum"] == 1:
            reads.append(descriptor)
        elif row["sampled_enum"] == 2:
            writes.append(descriptor)
        else:
            raise ValueError("Unexpected translated image class")
    if len(reads) != 2 or len(writes) != 1:
        raise ValueError("Expected two sampled images and one storage image")
    reads.sort(key=lambda r: (r[0], r[1]))
    return {
        "sampled_image_descriptor_candidates_unordered_t0_t1": reads,
        "storage_output_image_descriptor_from_unique_uav_class": writes[0],
        "src_t0_vs_t1_mapping_verified": False,
        "runtime_unity_kernel_id_mapping_verified": False,
    }


def check_executable_image_roles(converted_spirv: bytes, numeric_profile: dict):
    """Prove *use* of both declared sampled descriptors and written storage.

    This is SPIR-V SSA image operand lineage, not original DXBC t0 versus t1
    semantic identity or a complete instruction/bitwise equivalence proof.
    """
    flow = image_slot_dataflow(converted_spirv)
    if not flow["all_image_operations_uniquely_traced"]:
        raise ValueError("Unresolved or ambiguous SPIR-V executable image operand")
    wanted_reads = {
        tuple(row[:2])
        for row in numeric_profile["sampled_image_descriptor_candidates_unordered_t0_t1"]
    }
    wanted_write = tuple(numeric_profile[
        "storage_output_image_descriptor_from_unique_uav_class"][:2])
    if len(wanted_reads) != 2 or wanted_write in wanted_reads:
        raise ValueError("Ambiguous declared numeric read/write ABI")
    uses = flow["image_operand_slot_uses"]

    def counts(names):
        result = {}
        for name in names:
            record = uses[name]
            if record["unresolved_count"] or record["ambiguous_count"]:
                raise ValueError("Ambiguous active SPIR-V image resource use")
            for row in record["resolved_slot_counts"]:
                key = (row["descriptor_set"], row["binding"])
                result[key] = result.get(key, 0) + row["calls"]
        return result

    actual_reads = counts(("fetch", "read", "sample", "gather"))
    actual_writes = counts(("write",))
    if (set(actual_reads) != wanted_reads
            or any(actual_reads[slot] < 1 for slot in wanted_reads)
            or set(actual_writes) != {wanted_write}
            or actual_writes[wanted_write] < 1):
        raise ValueError("Original FFT declared image not used in expected SPIR-V read/write role")
    # Queries/texel-pointer operations are not ignored just to make coverage
    # appear complete: they must at least resolve to one declared descriptor.
    other_uses = counts(("query", "texel_pointer"))
    if not set(other_uses).issubset(wanted_reads | {wanted_write}):
        raise ValueError("Unexpected executable image helper operation resource")
    return {
        "both_sampled_descriptor_candidates_actively_read": True,
        "sole_storage_output_descriptor_actively_written": True,
        "all_image_operations_uniquely_traced": True,
        "source_DXBC_t0_t1_semantic_binding_verified": False,
    }


def require_shared_abi(profiles):
    """Reject any unproven cross-slot descriptor rewrite with deterministic ABI."""
    if not isinstance(profiles, list) or len(profiles) != EXPECTED_COUNT:
        raise ValueError("Original FFT compiled slot coverage incomplete")
    first = profiles[0]
    for row in profiles:
        if (not isinstance(row, dict)
                or row.get("src_t0_vs_t1_mapping_verified") is not False
                or row.get("runtime_unity_kernel_id_mapping_verified") is not False):
            raise ValueError("Forged source-register or Unity-runtime identity claim")
        sampled = row.get("sampled_image_descriptor_candidates_unordered_t0_t1")
        storage = row.get("storage_output_image_descriptor_from_unique_uav_class")
        if (not isinstance(sampled, list) or len(sampled) != 2
                or any(not isinstance(v, tuple) or len(v) != len(IMAGE_FIELDS)
                       for v in sampled)
                or not isinstance(storage, tuple)
                or len(storage) != len(IMAGE_FIELDS)):
            raise ValueError("Unverified translated numeric descriptor ABI shape")
        keys = [(v[0], v[1]) for v in sampled] + [(storage[0], storage[1])]
        if len(set(keys)) != 3 or keys[:2] != sorted(keys[:2]):
            raise ValueError("Aliased or unordered numerical image descriptor ABI")
    if any(row != first for row in profiles):
        raise ValueError("Original FFT translated numeric descriptor ABI differs by compiled slot")
    safe = {
        "sampled_image_descriptor_candidates_unordered_t0_t1":
            [list(v) for v in first["sampled_image_descriptor_candidates_unordered_t0_t1"]],
        "storage_output_image_descriptor_from_unique_uav_class":
            list(first["storage_output_image_descriptor_from_unique_uav_class"]),
    }
    digest = hashlib.sha256(
        json.dumps(safe, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "original_fft_compiled_slots_checked": EXPECTED_COUNT,
        "identical_numeric_image_descriptor_abi_across_compiled_slots": True,
        "verified_numeric_descriptor_abi_sha256": digest,
        "numeric_descriptor_abi": safe,
        "sampled_t0_t1_roles_interchangeable_without_proof": False,
        "source_t0_to_descriptor_identity_verified": False,
        "source_t1_to_descriptor_identity_verified": False,
        "storage_u0_identity_inferred_by_unique_output_class_only": True,
        "unity_findkernel_runtime_mapping_verified": False,
        "original_authored_android_compute_source_restored": False,
        "unity_or_android_gpu_executed": False,
        "private_programs_or_names_disclosed": False,
    }


def inspect_original(root: Path):
    """Only original SHA-pinned source; compile in ephemeral private scratch."""
    if EXPECTED_CONTAINERS != EXPECTED_COUNT:
        raise ValueError("Original FFT expected slot count pin changed")
    if verify_sources(root, expected={OWNER: ORIGINAL_OWNERS[OWNER]})[
        "authenticated_owners"] != 1:
        raise ValueError("Unverified original owner")
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objects = [obj for obj in env.file.objects.values()
               if obj.type.name == "ComputeShader" and int(obj.path_id) == PATH_ID]
    if len(objects) != 1:
        raise ValueError("Original FFT compute object absent or duplicated")
    raw = objects[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original FFT ComputeShader object changed")
    scanned = scan_blob(raw)["valid_dxbc_containers"]
    correlated = correlate_original_variant_bytecode(
        objects[0].read_typetree(), scanned,
        EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT)
    if correlated.get("authentic_compiled_variants_verified_in_original_order") != EXPECTED_COUNT:
        raise ValueError("Original typed compiled program order unverified")
    profiles = []
    with tempfile.TemporaryDirectory(prefix="raft-b08-fft-abi-private-") as tmp:
        work = Path(tmp)
        for index, item in enumerate(scanned):
            at = item["offset_in_original_object"]
            source = raw[at:at + item["bytes"]]
            if hashlib.sha256(source).hexdigest() != item["binary_sha256"]:
                raise ValueError("Original compiled program SHA verification failed")
            dx_path, spv_path = work / "original.dxbc", work / "translated.spv"
            dx_path.write_bytes(source)
            try:
                converted = subprocess.run(
                    ["vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                     "-o", str(spv_path), str(dx_path)],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, timeout=25, check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                raise ValueError("Private original DXBC conversion unavailable") from None
            if (converted.returncode or not spv_path.is_file()
                    or not 0 < spv_path.stat().st_size <= 1048576):
                raise ValueError("Private original DXBC conversion failed")
            converted = spv_path.read_bytes()
            profile = describe_pair(source, converted)
            check_executable_image_roles(converted, profile)
            profiles.append(profile)
            dx_path.unlink()
            spv_path.unlink()
    return {
        "zip2_source_commit": SOURCE_COMMIT,
        "original_owner_sha256": ORIGINAL_OWNERS[OWNER][1],
        "original_compute_shader_object_sha256": ORIGINAL_OBJECT_SHA256,
        "original_compiled_program_sha_and_order_authenticated": True,
        **require_shared_abi(profiles),
        "source_authentic_spirv_programs_with_both_sampled_image_reads": len(profiles),
        "source_authentic_spirv_programs_with_storage_output_writes": len(profiles),
        "all_spirv_image_operations_uniquely_traced": True,
        "source_dxbc_t0_t1_operand_correspondence_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = inspect_original(args.source)
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        print("RAFT_B08_FFT_SPV_DESCRIPTOR_ABI " + json.dumps({
            "status": "REJECTED", "reason": "AUTH_OR_ABI_CONTRACT_FAILED",
            "numeric_descriptor_abi_verified": False,
            "runtime_kernel_id_verified": False,
        }, sort_keys=True))
        return 2
    print("RAFT_B08_FFT_SPV_DESCRIPTOR_ABI " + json.dumps(
        {"status": "PASS", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
