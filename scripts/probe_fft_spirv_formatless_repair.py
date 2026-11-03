"""Private fail-closed SPIR-V experiment: restore formatless FFT output declaration.

Never stores originals, publishes shader programs, stages Unity assets, or
claims numerical equivalence / physical-device feature support.
"""
import struct
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_spirv_operation_profile import image_operation_profile


def restore_formatless_write(roundtrip, original_images, original_ops):
    if type(roundtrip) is not bytes or len(roundtrip) < 20 or len(roundtrip) > 1048576 or len(roundtrip) % 4:
        raise ValueError("Invalid roundtrip module")
    old = original_images["typed_image_declarations"]
    new = image_resource_contracts(roundtrip)["typed_image_declarations"]
    if len(old) != len(new):
        raise ValueError("Changed image descriptor count")
    mismatches = []
    for a, b in zip(old, new):
        if any(a.get(k) != b.get(k) for k in a if k != "format_enum"):
            raise ValueError("Changed image resource contract")
        if a["format_enum"] != b["format_enum"]:
            mismatches.append((a, b))
    if len(mismatches) != 1:
        raise ValueError("Missing or ambiguous format-only difference")
    a, b = mismatches[0]
    if (a["set"], a["binding"], a["sampled_enum"], a["format_enum"], b["format_enum"]) != (0, 2, 2, 0, 1):
        raise ValueError("Unexpected original storage image format")
    if not original_ops.get("storage_image_write_without_format_capability_declared"):
        raise ValueError("Original formatless write capability missing")
    op = image_operation_profile(roundtrip)
    if (op["storage_image_write_without_format_capability_declared"]
            or original_ops.get("op_image_write_count") != 1
            or original_ops.get("op_image_read_count") != 0
            or any(op[key] != original_ops[key] for key in
                   ("op_image_write_count", "op_image_read_count", "op_image_fetch_count"))):
        raise ValueError("Image operation / capability baseline changed")
    words = list(struct.unpack("<" + "I" * (len(roundtrip) // 4), roundtrip))
    if words[0] != 0x07230203 or not words[3] or words[4]:
        raise ValueError("Invalid module header")
    candidates = []
    offset = 5
    while offset < len(words):
        count, opcode = words[offset] >> 16, words[offset] & 65535
        if not count or offset + count > len(words):
            raise ValueError("Malformed SPIR-V instruction")
        if opcode == 25:
            if count not in (9, 10):
                raise ValueError("Unexpected OpTypeImage arity")
            if words[offset + 7] == 2 and words[offset + 8] == 1:
                candidates.append(offset + 8)
        offset += count
    if len(candidates) != 1:
        raise ValueError("Ambiguous output image type")
    words[candidates[0]] = 0
    words[5:5] = [(2 << 16) | 17, 56]  # OpCapability StorageImageWriteWithoutFormat
    restored = struct.pack("<" + "I" * len(words), *words)
    if image_resource_contracts(restored)["typed_image_declarations"] != old:
        raise ValueError("Restored image contract mismatch")
    restored_ops = image_operation_profile(restored)
    if not restored_ops["storage_image_write_without_format_capability_declared"]:
        raise ValueError("Capability insertion failed")
    for key in ("op_image_write_count", "op_image_read_count", "op_image_fetch_count"):
        if restored_ops[key] != original_ops[key]:
            raise ValueError("Repaired operation count mismatch")
    return restored
