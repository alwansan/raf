"""Verify same original FFT SPIR-V variable identity across two explicit maps.

Input SPIR-V modules come only from SHA-pinned original DXBC compiled with
explicit vkd3d resource maps. The only sanctioned difference is a literal in
OpDecorate Binding (33) or DescriptorSet (34) for the three image variables.
No original resource names, bytecode, tokens or SSA IDs are printed.
This is structural variable/algorithm parity, NOT runtime numerical proof.
"""
import struct

from scripts.b18_fft_spirv_descriptor_identity import INTERFACES

SPV_MAGIC = 0x07230203
MAX_SPIRV_BYTES = 1048576


def normalized_image_decorations(module: bytes, profile: str) -> tuple[tuple, dict]:
    if profile not in INTERFACES or not isinstance(module, bytes):
        raise ValueError("Unrecognized original FFT explicit interface profile")
    if not 20 <= len(module) <= MAX_SPIRV_BYTES or len(module) % 4:
        raise ValueError("Missing or unbounded SPIR-V module")
    words = list(struct.unpack("<" + "I" * (len(module)//4), module))
    if words[0] != SPV_MAGIC or not words[3] or words[4] != 0:
        raise ValueError("Invalid SPIR-V module header")
    by_id = {}
    variables = set()
    offset = 5
    while offset < len(words):
        n, op = words[offset] >> 16, words[offset] & 0xffff
        if n < 1 or n > 1024 or offset+n > len(words):
            raise ValueError("Invalid SPIR-V instruction bounds")
        if op == 59 and n in (4, 5):
            if words[offset + 2] in variables:
                raise ValueError("Repeated SPIR-V image variable declaration")
            variables.add(words[offset + 2])
        if op == 71 and n >= 3 and words[offset+2] in (33, 34):
            if n != 4 or not 0 < words[offset+1] < words[3]:
                raise ValueError("Invalid SPIR-V image descriptor decoration")
            target, kind, value = words[offset+1:offset+4]
            metadata = by_id.setdefault(target, {})
            if kind in metadata or value > 65535:
                raise ValueError("Repeated or out-of-range descriptor decoration")
            metadata[kind] = value
            # Mask ONLY the mapped descriptor literal; no source instructions,
            # type declarations, IDs or other decorations may be changed.
            words[offset+3] = 0
        offset += n
    desired = INTERFACES[profile]
    if len(by_id) != 3 or any(set(v) != {33,34} for v in by_id.values()):
        raise ValueError("Incomplete explicit FFT image descriptor pairs")
    if not set(by_id).issubset(variables):
        raise ValueError("Descriptor does not decorate a declared variable")
    by_location = {(d[34], d[33]): var_id for var_id,d in by_id.items()}
    if len(by_location) != 3 or set(by_location) != set(desired.values()):
        raise ValueError("Actual SPIR-V image variable locations differ from chosen profile")
    source_ids = {source: by_location[target] for source,target in desired.items()}
    if len(set(source_ids.values())) != 3:
        raise ValueError("Ambiguous same-class image variable identity")
    return tuple(words), source_ids


def verify_pair(a: bytes, b: bytes) -> dict:
    normalized_a, ids_a = normalized_image_decorations(a, "A")
    normalized_b, ids_b = normalized_image_decorations(b, "B")
    if normalized_a != normalized_b:
        raise ValueError("Non-descriptor SPIR-V program or variable IDs changed")
    if ids_a != ids_b:
        raise ValueError("Input image variable identity changed across explicit maps")
    return {
        "source_register_keys_proven_distinct": 3,
        "different_target_mapping_preserves_input_variable_identities": True,
        "full_spirv_program_equivalent_after_only_descriptor_literal_mask": True,
        "original_source_names_or_bytecode_exposed": False,
        "runtime_t0_t1_input_values_independently_tested": False,
        "unity_or_android_gpu_verified": False,
    }
