"""Bounded numeric SPIR-V image operation/capability profile; no shader bytes.

Module-wide instruction counts do not establish which descriptor is dynamically
accessed, numerical correctness, physical device enabled features or Unity GPU use.
"""
import struct

SPIRV_MAGIC = 0x07230203
MAX_BYTES = 1024 * 1024
KNOWN_OPS = {95: "image_fetch", 98: "image_read", 99: "image_write"}
CAPABILITIES = {
    49: "storage_image_extended_formats",
    55: "storage_image_read_without_format",
    56: "storage_image_write_without_format",
}


def image_operation_profile(module):
    if type(module) is not bytes or not 20 <= len(module) <= MAX_BYTES or len(module) % 4:
        raise ValueError("Invalid SPIR-V profile module length")
    words = struct.unpack("<" + "I" * (len(module) // 4), module)
    if words[0] != SPIRV_MAGIC or words[3] == 0 or words[4] != 0:
        raise ValueError("Invalid SPIR-V profile header")
    declared_caps = set()
    op_counts = {name: 0 for name in KNOWN_OPS.values()}
    image_formats = []
    index = 5
    while index < len(words):
        head = words[index]
        length, op = head >> 16, head & 65535
        if length < 1 or index + length > len(words):
            raise ValueError("Invalid SPIR-V profile instruction boundary")
        args = words[index + 1:index + length]
        if op == 17:  # OpCapability
            if length != 2:
                raise ValueError("Malformed SPIR-V capability declaration")
            declared_caps.add(args[0])
        if op == 25:  # OpTypeImage result-id, sampled-type, dim, ..., format
            if length not in (9, 10):
                raise ValueError("Malformed SPIR-V image type")
            image_formats.append({"sampled_enum": args[6], "format_enum": args[7]})
        if op in KNOWN_OPS:
            if length < (4 if op == 99 else 5):
                raise ValueError("Malformed SPIR-V image operation")
            op_counts[KNOWN_OPS[op]] += 1
        index += length
    unknown_storage = any(
        r["sampled_enum"] == 2 and r["format_enum"] == 0 for r in image_formats)
    # A module-wide statement only; do not guess dynamic operand provenance.
    return {
        "op_image_fetch_count": op_counts["image_fetch"],
        "op_image_read_count": op_counts["image_read"],
        "op_image_write_count": op_counts["image_write"],
        "storage_image_extended_formats_capability_declared": 49 in declared_caps,
        "storage_image_read_without_format_capability_declared": 55 in declared_caps,
        "storage_image_write_without_format_capability_declared": 56 in declared_caps,
        "unknown_format_storage_image_type_count": sum(
            r["sampled_enum"] == 2 and r["format_enum"] == 0 for r in image_formats),
        "module_contains_unknown_storage_and_image_write": bool(
            unknown_storage and op_counts["image_write"]),
        "enabled_device_feature_or_exact_operand_binding_proven": False,
        "gpu_numerical_equivalence_proven": False,
        "private_source_or_instruction_payload_disclosed": False,
    }


def compare_image_operation_profiles(original, roundtrip):
    fields = ("op_image_fetch_count", "op_image_read_count", "op_image_write_count",
              "storage_image_extended_formats_capability_declared",
              "storage_image_read_without_format_capability_declared",
              "storage_image_write_without_format_capability_declared",
              "unknown_format_storage_image_type_count")
    return {
        "numeric_profile_drift": [
            {"field": f, "original": original[f], "roundtrip": roundtrip[f]}
            for f in fields if original[f] != roundtrip[f]
        ],
        "same_image_operation_and_capability_counts": all(
            original[f] == roundtrip[f] for f in fields),
        "shader_equivalence_or_device_execution_verified": False,
    }
