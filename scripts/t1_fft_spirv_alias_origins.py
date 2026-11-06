"""Classify which private FFT SPIR-V pointer-alias stores may precede fetch loads.

Reports aggregate alias *forms* only; does not establish original integer
coordinate semantics or unaliased full memory reaching definitions. No SSA IDs,
offset literals, original shaders or pixel data are emitted.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

from scripts.t1_fft_local_store_writers import image_role, read_module
from scripts.t1_fft_spirv_reaching_stores import (
    MAX_BLOCKS, aliases, load_leaf, parse_functions,
)

ACCESS_OPS = {"OpAccessChain", "OpInBoundsAccessChain", "OpPtrAccessChain",
              "OpInBoundsPtrAccessChain"}


def pointer_form(candidate, target, values, types):
    if candidate == target:
        return "direct_pointer"
    seen = set()
    copy_hops = 0
    current = candidate
    for _ in range(64):
        if current in seen:
            return "unresolved_pointer"
        seen.add(current)
        op, typ, args = values.get(current, ("", None, []))
        if op == "OpCopyObject" and len(args) == 1:
            source = args[0]
            # Exact pointer copies require identical declared pointer type.
            if not typ or values.get(source, ("", None, []))[1] != typ:
                return "unresolved_pointer"
            copy_hops += 1
            current = source
        elif op in ACCESS_OPS and len(args) >= 2:
            if not aliases(args[0], target, values):
                return "unresolved_pointer"
            kinds = [values.get(x, ("", None, []))[0] for x in args[1:]]
            static = all(k in {"OpConstant", "OpConstantNull", "OpSpecConstant"} for k in kinds)
            return "indexed_access_static" if static else "indexed_access_dynamic"
        elif op == "OpPhi" and any(aliases(v, target, values) for v in args[::2]):
            return "phi_pointer_merge"
        elif op == "OpSelect" and len(args) == 3 and any(
                aliases(v, target, values) for v in args[1:]):
            return "select_pointer_merge"
        else:
            if current == target and copy_hops:
                return "exact_pointer_copy"
            return "unresolved_pointer"
    return "unresolved_pointer"


def path_categories(fun, pointer, load_id, values, types):
    blocks, edges = fun["blocks"], fun["edges"]
    load_location = [(block, idx) for block, ops in blocks.items()
                     for idx, (_, name, _) in enumerate(ops) if name == load_id]
    if len(load_location) != 1:
        raise ValueError("Missing or duplicate load location")
    load_block, load_index = load_location[0]
    static = Counter()
    for ops in blocks.values():
        for op, _, args in ops:
            if (op == "OpStore" and len(args) >= 2 and args[0] != pointer
                    and aliases(args[0], pointer, values)):
                static[pointer_form(args[0], pointer, values, types)] += 1

    def transfer(state, op, args):
        if op != "OpStore" or len(args) < 2:
            return state
        if args[0] == pointer:
            return set()
        if aliases(args[0], pointer, values):
            return state | {pointer_form(args[0], pointer, values, types)}
        return state

    in_states = {label: None for label in blocks}
    in_states[fun["entry"]] = set()
    for _ in range(MAX_BLOCKS * 2):
        updated = False
        for block, ops in blocks.items():
            if in_states[block] is None:
                continue
            current = set(in_states[block])
            for op, _, args in ops:
                current = transfer(current, op, args)
            for next_block in edges[block]:
                old = in_states[next_block]
                combined = current if old is None else old | current
                if old is None or old != combined:
                    in_states[next_block] = set(combined)
                    updated = True
        if not updated:
            break
    else:
        raise ValueError("Pointer-path analysis failed to converge")
    if in_states[load_block] is None:
        return {"status": "unreachable_load"}
    state = set(in_states[load_block])
    for op, _, args in blocks[load_block][:load_index]:
        state = transfer(state, op, args)
    return {"status": "bounded_alias_store_origins",
            "static_alias_store_candidates": sum(static.values()),
            "static_alias_pointer_forms": dict(sorted(static.items())),
            "preload_alias_pointer_forms": sorted(state),
            "full_reaching_definition_proven": False,
            "original_integer_origin_proven": False}


def analyze(text, *, original_layout=False):
    types, values, decorations, _, fetches = read_module(text)
    functions = parse_functions(text)
    if len(fetches) > 16:
        raise ValueError("Unexpected private FFT fetch count")
    roles = [image_role(image, values, decorations) for image, _ in fetches]
    if original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected original FFT fetch order")
    sites = []
    for site, ((_, coord), role) in enumerate(zip(fetches, roles)):
        lanes = {}
        for lane, axis in enumerate(("x", "y")):
            load_id, boundary = load_leaf(coord, lane, values, types)
            if load_id is None:
                lanes[axis] = {"status": boundary}
                continue
            op, _, args = values.get(load_id, ("", None, []))
            if op != "OpLoad" or not args:
                lanes[axis] = {"status": "unresolved_load"}
                continue
            pointer = args[0]
            var_op, pointer_type, var_args = values.get(pointer, ("", None, []))
            ty_op, ty_args = types.get(pointer_type, ("", []))
            if (var_op != "OpVariable" or not var_args or var_args[0] != "Function"
                    or ty_op != "OpTypePointer" or not ty_args or ty_args[0] != "Function"):
                lanes[axis] = {"status": "nonlocal_or_indirect_load"}
                continue
            owners = [fun for fun in functions if any(
                result == load_id for ops in fun["blocks"].values()
                for _, result, _ in ops)]
            if len(owners) != 1:
                raise ValueError("Original load ownership ambiguous")
            lanes[axis] = path_categories(owners[0], pointer, load_id, values, types)
        sites.append({"site": site, "role": role, "lanes": lanes})
    return {"scope": "may_precede_function_local_alias_stores",
            "raw_ssa_ids_exported": False, "original_integer_origin_proven": False,
            "sites": sites}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path)
    args = p.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private source object outside bounded size")
        d = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                           check=True, capture_output=True, text=True, timeout=20)
        report = analyze(d.stdout, original_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        p.exit(2, "Private FFT pointer alias origin audit failed\n")
    print("RAFT_T1_FFT_ALIAS_POINTER_ORIGINS " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
