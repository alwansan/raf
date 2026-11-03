"""Bounded, privacy-preserving public GLSL.std.450 OpExtInst numeric census.

Module shape and import references are validated independently of the caller's
spirv-val. Never emit private import names, shader operands or raw source. A
matching operation histogram is NOT equivalent to matching shader numerics.
"""
import struct

MAX_SPIRV_SIZE = 1048576
PUBLIC_SET = b"GLSL.std.450"


def extended_instruction_profile(module):
    if type(module) is not bytes or not 20 <= len(module) <= MAX_SPIRV_SIZE or len(module) % 4:
        raise ValueError("Invalid SPIR-V extension census length")
    words = struct.unpack("<" + "I" * (len(module) // 4), module)
    if words[0] != 0x07230203 or words[3] == 0 or words[4] != 0:
        raise ValueError("Invalid SPIR-V extension census header")
    imports = {}
    public_counts = {}
    nonpublic_uses = 0
    total = 0
    offset = 5
    while offset < len(words):
        n, op = words[offset] >> 16, words[offset] & 65535
        if not 1 <= n <= 1024 or offset + n > len(words):
            raise ValueError("Invalid SPIR-V extension census instruction")
        a = words[offset + 1:offset + n]
        if op == 11:  # OpExtInstImport result-id, literal NUL-terminated string
            if n < 3 or not 0 < a[0] < words[3] or a[0] in imports:
                raise ValueError("Invalid or duplicate extended instruction import")
            text = struct.pack("<" + "I" * (len(a) - 1), *a[1:])
            if b"\x00" not in text or any(text[text.index(b"\x00") + 1:]):
                raise ValueError("Malformed extended instruction import")
            imports[a[0]] = text.split(b"\x00", 1)[0] == PUBLIC_SET
        elif op == 12:  # OpExtInst result-type, result-id, set-id, opcode, args...
            if n < 5:
                raise ValueError("Truncated extended instruction")
            set_id, instruction = a[2], a[3]
            if set_id not in imports:
                raise ValueError("Unresolved extended instruction import")
            total += 1
            if imports[set_id]:
                public_counts[instruction] = public_counts.get(instruction, 0) + 1
            else:
                # Cannot safely compare numeric opcode values across private sets.
                nonpublic_uses += 1
        offset += n
    return {
        "glsl_std_450_numeric_opcode_counts": {
            str(k): public_counts[k] for k in sorted(public_counts)
        },
        "glsl_std_450_instruction_total": sum(public_counts.values()),
        "unclassified_extended_instruction_total": nonpublic_uses,
        "all_extended_instruction_count": total,
        "all_instruction_sets_public_and_classified": nonpublic_uses == 0,
        "raw_import_names_or_instruction_operands_disclosed": False,
        "semantic_or_gpu_equivalence_proven": False,
    }


def compare_extended_instruction_profiles(original, roundtrip):
    keys = ("glsl_std_450_numeric_opcode_counts", "glsl_std_450_instruction_total",
            "unclassified_extended_instruction_total", "all_extended_instruction_count")
    for obj in (original, roundtrip):
        if type(obj) is not dict or any(k not in obj for k in keys):
            raise ValueError("Invalid extended instruction profile")
        counts = obj[keys[0]]
        if (type(counts) is not dict or len(counts) > 1024
                or any(type(k) is not str or not k.isdecimal()
                       or str(int(k)) != k or type(v) is not int or v <= 0
                       for k, v in counts.items())):
            raise ValueError("Invalid public extended opcode counts")
        if any(type(obj[k]) is not int or obj[k] < 0 for k in keys[1:]):
            raise ValueError("Invalid extended instruction totals")
        if sum(counts.values()) != obj[keys[1]] or obj[keys[1]] + obj[keys[2]] != obj[keys[3]]:
            raise ValueError("Inconsistent extended instruction totals")
    a, b = original[keys[0]], roundtrip[keys[0]]
    drift = [{"public_opcode": int(k), "original": a.get(k, 0),
              "roundtrip": b.get(k, 0)}
             for k in sorted(set(a) | set(b), key=int)
             if a.get(k, 0) != b.get(k, 0)]
    has_unknown = bool(original[keys[2]] or roundtrip[keys[2]])
    return {
        "public_glsl_std_450_opcode_differences": drift,
        "same_public_glsl_std_450_counts": not drift,
        "original_unclassified_extended_count": original[keys[2]],
        "roundtrip_unclassified_extended_count": roundtrip[keys[2]],
        "same_total_extended_instruction_count": original[keys[3]] == roundtrip[keys[3]],
        "all_extended_opcode_identities_comparable": not has_unknown,
        "same_fully_classified_extended_opcode_profile": (
            not drift and not has_unknown and original[keys[3]] == roundtrip[keys[3]]
        ),
        "mathematical_or_shader_semantic_equivalence_proven": False,
        "device_gpu_execution_proven": False,
    }
