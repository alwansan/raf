"""Bounded source-private prerequisite check for original FFT SPIR-V keyed capture.

This checks a candidate original shader module BEFORE any instrumentation; it
does NOT insert an SSBO, run the original shader, or prove Vulkan/Unity parity.
Never publishes original shader code, identifier names, constants, pixels or
the private bytecode. Public output uses only finite type/role categories.
"""
import argparse
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import (
    read_module, image_role, value_shape, type_shape,
)

MAX_LINES = 60000
MAX_FETCHES = 16
ALLOWED_KINDS = {"uint32", "sint32", "float32"}


def _decorations(text):
    desc, builtin_vars, builtin_members, interfaces = {}, set(), set(), set()
    count = 0
    for raw in text.splitlines():
        count += 1
        if count > MAX_LINES:
            raise ValueError("Private SPIR-V instruction count outside bound")
        tok = raw.split(";", 1)[0].split()
        if not tok:
            continue
        if len(tok) == 4 and tok[0] == "OpDecorate":
            if tok[2] in ("DescriptorSet", "Binding"):
                if not tok[3].isdecimal() or (tok[1], tok[2]) in desc:
                    raise ValueError("Invalid duplicate SPIR-V descriptor")
                desc[tok[1], tok[2]] = int(tok[3])
            if tok[2] == "BuiltIn" and tok[3] == "GlobalInvocationId":
                builtin_vars.add(tok[1])
        elif len(tok) == 5 and tok[0] == "OpMemberDecorate":
            if tok[3] == "BuiltIn" and tok[4] == "GlobalInvocationId":
                if not tok[2].isdecimal():
                    raise ValueError("Invalid built-in struct member index")
                builtin_members.add((tok[1], int(tok[2])))
        elif tok[0] == "OpEntryPoint" and len(tok) >= 4:
            if tok[1] == "GLCompute":
                # All interface IDs occur after the quoted entry name. Do not
                # expose them; only count whether referenced by an Input var.
                interfaces.update(tok[4:])
    return desc, builtin_vars, builtin_members, interfaces


def _input_var_shape(item, types, values):
    op, typ, args = values.get(item, ("", None, []))
    p_op, p_args = types.get(typ, ("", []))
    if (op != "OpVariable" or not args or args[0] != "Input" or
            p_op != "OpTypePointer" or len(p_args) != 2 or p_args[0] != "Input"):
        return None
    return p_args[1]


def _invocation_builtin(types, values, direct, members, interfaces):
    for item in sorted(direct & interfaces):
        ptype = _input_var_shape(item, types, values)
        if ptype and type_shape(ptype, types) == ("uint32", 3):
            return "direct_input"
    for item in sorted(interfaces):
        struct_id = _input_var_shape(item, types, values)
        if not struct_id:
            continue
        op, member_types = types.get(struct_id, ("", []))
        if op != "OpTypeStruct":
            continue
        for decorated_struct, index in members:
            if decorated_struct == struct_id and index < len(member_types):
                if type_shape(member_types[index], types) == ("uint32", 3):
                    return "struct_member_input"
    return "not_proven"


def analyze(text, *, require_original_layout=True):
    types, values, role_decor, _, fetches = read_module(text)
    if not 0 < len(fetches) <= MAX_FETCHES:
        raise ValueError("Unexpected source fetch census")
    desc, direct, members, interfaces = _decorations(text)
    roles = [image_role(image, values, role_decor) for image, _ in fetches]
    if require_original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected original FFT descriptor roles")
    sites = []
    for (_, coord), role in zip(fetches, roles):
        kind, width = value_shape(coord, values, types)
        if kind not in ("uint32", "sint32") or not 2 <= width <= 4:
            raise ValueError("ImageFetch coordinate must be integer vector")
        sites.append({"role": role, "coordinate_type": kind + "_vector",
                      "coordinate_width": width})
    # Result type is taken from the OpImageFetch result definition, not from the
    # coordinate. Check at most 16 relevant sites without logging their IDs.
    fetch_result_shapes = [
        value_shape(result, values, types)
        for result, (op, _, _) in values.items() if op == "OpImageFetch"
    ]
    if len(fetch_result_shapes) != len(fetches):
        raise ValueError("ImageFetch result count inconsistent")
    if any(kind not in ALLOWED_KINDS or not 1 <= width <= 4
           for kind, width in fetch_result_shapes):
        raise ValueError("Unsupported original ImageFetch value shape")
    for site, (kind, width) in zip(sites, fetch_result_shapes):
        site["fetched_value_type"] = kind + ("_scalar" if width == 1 else "_vector")
        site["fetched_value_width"] = width
    used_pairs = set()
    for (item, key), number in desc.items():
        if key == "DescriptorSet" and (item, "Binding") in desc:
            used_pairs.add((number, desc[item, "Binding"]))
    builtin_status = _invocation_builtin(types, values, direct, members, interfaces)
    return {
        "status": "original_spirv_keyed_capture_prerequisites_only",
        "roles": roles,
        "sites": sites,
        "global_invocation_id_input": builtin_status,
        "set0_storage_binding3_available": (0, 3) not in used_pairs,
        "set1_storage_binding3_available": (1, 3) not in used_pairs,
        "direct_original_spirv_instrumented": False,
        "candidate_keyed_capture_attached": False,
        "original_invocation_capture_proven": False,
        "paired_numeric_parity_proven": False,
        "private_identifiers_or_values_exported": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private FFT shader size outside bound")
        dis = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                             check=True, capture_output=True, text=True, timeout=20)
        report = analyze(dis.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private original FFT keyed capture prerequisites failed\n")
    print("RAFT_T1_ORIGINAL_KEYED_PREFLIGHT " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
