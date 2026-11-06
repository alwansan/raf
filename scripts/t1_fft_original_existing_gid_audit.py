"""Classify an EXISTING GlobalInvocationId declaration in private original SPIR-V.

Result contains only fixed type/interface/usage categories; never operand IDs,
original bytes, source shader disassembly, literal bit patterns or coordinates.
This read-only audit is not an original GPU invocation readback.
"""
import argparse
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import read_module, type_shape
from scripts.t1_fft_original_keyed_preflight import _decorations, _input_var_shape

MAX_BYTES = 1024 * 1024
MAX_DECLS = 4


def _kind(kind):
    if kind == "uint32":
        return kind
    if kind == "sint32":
        return kind
    if kind == "float32":
        return kind
    return "other_type"


def _item_shape(type_id, types):
    kind, width = type_shape(type_id, types)
    return {"numeric_kind": _kind(kind), "width": width if width in (1, 2, 3, 4) else 0}


def analyze(text):
    types, values, _, _, _ = read_module(text)
    _, direct, members, interfaces = _decorations(text)
    if not direct and not members:
        return {"status": "builtin_not_declared", "direct_count": 0,
                "member_count": 0, "private_identifiers_exported": False}
    if len(direct) + len(members) > MAX_DECLS:
        raise ValueError("Too many original builtin declarations")

    direct_report = []
    for var in sorted(direct):
        op, type_id, args = values.get(var, ("unknown", None, []))
        type_op, type_args = types.get(type_id, ("unknown", []))
        ptype = _input_var_shape(var, types, values)
        loaded = sum(op2 == "OpLoad" and len(args2) >= 1 and args2[0] == var
                     for op2, _, args2 in values.values())
        direct_report.append({
            "in_compute_entry_interface": var in interfaces,
            "declaration_form": ("input_variable" if ptype else
                                 "other_variable" if op == "OpVariable" else
                                 "not_variable"),
            "pointer_storage_class": (type_args[0] if type_op == "OpTypePointer"
                                      and type_args and type_args[0] in
                                      ("Input", "Output", "Private", "Function", "Uniform") else "other"),
            "value_type": _item_shape(ptype, types) if ptype else {
                "numeric_kind": "unresolved", "width": 0},
            "direct_load_user_count": min(loaded, 1024),
        })

    members_report = []
    for struct_id, member_index in sorted(members):
        type_op, type_args = types.get(struct_id, ("unknown", []))
        if type_op != "OpTypeStruct" or not 0 <= member_index < len(type_args):
            raise ValueError("Invalid decorated GlobalInvocationId struct member")
        struct_inputs = [var for var in interfaces
                         if _input_var_shape(var, types, values) == struct_id]
        other_input_vars = [var for var in values
                            if _input_var_shape(var, types, values) == struct_id]
        members_report.append({
            "member_type": _item_shape(type_args[member_index], types),
            "input_struct_var_count": min(len(other_input_vars), 32),
            "input_struct_in_entry_interface": bool(struct_inputs),
            "other_member_count": min(len(type_args), 32),
        })

    direct_usable = any(x["declaration_form"] == "input_variable"
                        and x["in_compute_entry_interface"]
                        and x["value_type"] == {"numeric_kind": "uint32", "width": 3}
                        for x in direct_report)
    member_usable = any(x["input_struct_in_entry_interface"]
                        and x["member_type"] == {"numeric_kind": "uint32", "width": 3}
                        for x in members_report)
    return {
        "status": "existing_builtin_declaration_shape_only",
        "direct_count": len(direct),
        "member_count": len(members),
        "direct_declarations": direct_report,
        "member_declarations": members_report,
        "already_accessible_as_standard_input": direct_usable or member_usable,
        "original_spirv_instrumented": False,
        "original_gpu_invocation_capture_proven": False,
        "private_identifiers_exported": False,
        "numeric_original_vs_candidate_parity_proven": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= MAX_BYTES:
            raise ValueError("Private module outside byte cap")
        process = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                                 check=True, capture_output=True, text=True, timeout=20)
        report = analyze(process.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private original GlobalInvocationId declaration audit failed\n")
    print("RAFT_T1_ORIGINAL_EXISTING_GID_SHAPE " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
