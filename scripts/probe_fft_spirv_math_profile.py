"""Bounded SPIR-V numeric opcode census for private Raft FFT translation.

Tracks a PUBLIC opcode vocabulary without operands, SSA IDs, shader text or names.
Even identical opcode counts cannot establish identical arithmetic, floating
precision, control/data dependencies, GPU execution or a valid Unity program.
The original/roundtrip modules are independently validated with spirv-val by
the calling private experiment; synthetic fixtures do not claim that validation.
"""
import struct

MAX_BYTES = 1024 * 1024

# Khronos SPIR-V unified grammar, stable numeric opcodes. This selection is
# deliberately NOT the whole SPIR-V instruction set.
NUMERIC_OPS = {
    109: "convert_f_to_u", 110: "convert_f_to_s",
    111: "convert_s_to_f", 112: "convert_u_to_f",
    113: "u_convert", 114: "s_convert", 115: "f_convert",
    116: "quantize_f16", 124: "bitcast",
    126: "integer_negate", 127: "float_negate",
    128: "integer_add", 129: "float_add",
    130: "integer_sub", 131: "float_sub",
    132: "integer_mul", 133: "float_mul",
    134: "unsigned_div", 135: "signed_div", 136: "float_div",
    137: "unsigned_mod", 138: "signed_rem", 139: "signed_mod",
    140: "float_rem", 141: "float_mod",
    142: "vector_times_scalar", 143: "matrix_times_scalar",
    144: "vector_times_matrix", 145: "matrix_times_vector",
    146: "matrix_times_matrix", 147: "outer_product",
    148: "dot_product",
    149: "integer_add_carry", 150: "integer_sub_borrow",
    151: "unsigned_mul_extended", 152: "signed_mul_extended",
}
CONTROL_OPS = {
    169: "select", 245: "phi", 246: "loop_merge",
    247: "selection_merge", 249: "branch",
    250: "branch_conditional", 251: "switch",
}


def numeric_opcode_profile(module):
    if type(module) is not bytes or not 20 <= len(module) <= MAX_BYTES or len(module) % 4:
        raise ValueError("Invalid SPIR-V arithmetic census length")
    words = struct.unpack("<" + "I" * (len(module) // 4), module)
    if words[0] != 0x07230203 or words[3] == 0 or words[4] != 0:
        raise ValueError("Invalid SPIR-V arithmetic census header")
    counts, controls = {}, {}
    extensions = 0
    pos = 5
    while pos < len(words):
        n, op = words[pos] >> 16, words[pos] & 0xffff
        if not 1 <= n <= 1024 or pos + n > len(words):
            raise ValueError("Invalid SPIR-V arithmetic census instruction")
        if op in NUMERIC_OPS:
            if n < 4:
                raise ValueError("Truncated numeric opcode")
            name = NUMERIC_OPS[op]
            counts[name] = counts.get(name, 0) + 1
        elif op in CONTROL_OPS:
            if n < (5 if op == 245 else 2):
                raise ValueError("Truncated control opcode")
            name = CONTROL_OPS[op]
            controls[name] = controls.get(name, 0) + 1
        elif op == 12:  # OpExtInst: extension-set identity is not inferred.
            if n < 5:
                raise ValueError("Truncated extended instruction")
            extensions += 1
        pos += n
    return {
        "numeric_opcode_counts": dict(sorted(counts.items())),
        "tracked_numeric_opcode_total": sum(counts.values()),
        "control_opcode_counts": dict(sorted(controls.items())),
        "extended_instruction_count": extensions,
        "opcode_histogram_only_not_executable_semantics": True,
        "private_names_or_operands_disclosed": False,
        "shader_numerical_equivalence_or_gpu_execution_proven": False,
    }


def compare_numeric_opcode_profiles(original, roundtrip):
    keys = ("numeric_opcode_counts", "control_opcode_counts")
    for obj in (original, roundtrip):
        if not isinstance(obj, dict):
            raise ValueError("Invalid numeric profile")
        for key in keys:
            value = obj.get(key)
            if not isinstance(value, dict) or len(value) > len(NUMERIC_OPS) + len(CONTROL_OPS):
                raise ValueError("Invalid numeric profile dictionary")
            if any(not isinstance(k, str) or type(n) is not int or n < 0
                   for k, n in value.items()):
                raise ValueError("Invalid numeric profile count")
        if type(obj.get("extended_instruction_count")) is not int or obj["extended_instruction_count"] < 0:
            raise ValueError("Invalid extension census count")
    changes = {}
    for key in keys:
        changes[key] = [
            {"opcode": name, "original": original[key].get(name, 0),
             "roundtrip": roundtrip[key].get(name, 0)}
            for name in sorted(set(original[key]) | set(roundtrip[key]))
            if original[key].get(name, 0) != roundtrip[key].get(name, 0)
        ]
    same_ext = original["extended_instruction_count"] == roundtrip["extended_instruction_count"]
    return {
        "numeric_opcode_count_differences": changes["numeric_opcode_counts"],
        "control_opcode_count_differences": changes["control_opcode_counts"],
        "same_tracked_numeric_opcode_counts": not changes["numeric_opcode_counts"],
        "same_control_opcode_counts": not changes["control_opcode_counts"],
        "original_extended_instruction_count": original["extended_instruction_count"],
        "roundtrip_extended_instruction_count": roundtrip["extended_instruction_count"],
        "same_extended_instruction_count": same_ext,
        "same_tracked_opcode_profile": (not changes["numeric_opcode_counts"]
                                        and not changes["control_opcode_counts"] and same_ext),
        "mathematical_or_shader_semantic_equivalence_proven": False,
        "actual_gpu_execution_proven": False,
    }
