"""Bounded, non-identifying local-writer candidates for private FFT SPIR-V fetch lanes.

Direct OpStore candidates are *not* reaching definitions. An indirect write,
control-flow merge or pointer alias may change the value observed by OpLoad.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import subprocess

IMAGE_LINKS = {"OpLoad", "OpImage", "OpSampledImage", "OpCopyObject"}
MAX_DEPTH = 12
MAX_STORES = 32


def read_module(text):
    types, values, decorations = {}, {}, {}
    stores, fetches = defaultdict(list), []
    for raw in text.splitlines():
        tokens = raw.split(";", 1)[0].split()
        if not tokens:
            continue
        if len(tokens) == 4 and tokens[0] == "OpDecorate" and tokens[2] in ("DescriptorSet", "Binding"):
            key = (tokens[1], tokens[2])
            if key in decorations:
                raise ValueError("Duplicate descriptor binding decoration")
            decorations[key] = tokens[3]
        elif len(tokens) >= 3 and tokens[1] == "=":
            name, _, op, *args = tokens
            if name in types or name in values:
                raise ValueError("Duplicate SPIR-V result id")
            if op.startswith("OpType"):
                types[name] = (op, args)
            else:
                values[name] = (op, args[0] if args else None, args[1:])
                if op == "OpImageFetch" and len(args) >= 3:
                    fetches.append((args[1], args[2]))
        elif tokens[0] == "OpStore" and len(tokens) >= 3:
            stores[tokens[1]].append(tokens[2])
    return types, values, decorations, stores, fetches


def type_shape(type_id, types):
    op, args = types.get(type_id, ("", []))
    width = 1
    if op == "OpTypeVector" and len(args) == 2:
        type_id, width = args[0], int(args[1])
        op, args = types.get(type_id, ("", []))
    if op == "OpTypeInt" and args in (["32", "0"], ["32", "1"]):
        return ("uint32" if args[1] == "0" else "sint32"), width
    if op == "OpTypeFloat" and args == ["32"]:
        return "float32", width
    return "unresolved", 0


def value_shape(value_id, values, types):
    return type_shape(values.get(value_id, ("", None, []))[1], types)


def image_role(root, values, decorations):
    seen = set()
    while root in values and values[root][0] in IMAGE_LINKS:
        if root in seen:
            raise ValueError("Cyclic image producer")
        seen.add(root)
        args = values[root][2]
        if not args:
            return "unresolved"
        root = args[0]
    if decorations.get((root, "DescriptorSet")) != "0":
        return "unresolved"
    return {"0": "source", "1": "butterfly"}.get(decorations.get((root, "Binding")), "unresolved")


def lane_predecessor(op, args, lane, width, values, types):
    if op in ("OpBitcast", "OpCopyObject") and len(args) == 1:
        return (args[0], lane) if value_shape(args[0], values, types)[1] == width else None
    if op == "OpCompositeConstruct":
        for source in args:
            n = value_shape(source, values, types)[1]
            if n <= 0:
                return None
            if lane < n:
                return source, lane
            lane -= n
    if op == "OpCompositeExtract" and len(args) == 2 and width == 1:
        try:
            return args[0], int(args[1])
        except ValueError:
            return None
    if op == "OpCompositeInsert" and len(args) == 3:
        try:
            return (args[0], 0) if lane == int(args[2]) else (args[1], lane)
        except ValueError:
            return None
    if op == "OpVectorShuffle" and len(args) > lane + 2:
        try:
            index = int(args[2 + lane])
        except ValueError:
            return None
        first = value_shape(args[0], values, types)[1]
        second = value_shape(args[1], values, types)[1]
        if first and second and 0 <= index < first + second:
            return (args[0], index) if index < first else (args[1], index - first)
    return None


def direct_writer_summary(pointer, values, types, stores):
    op, pointer_type, args = values.get(pointer, ("", None, []))
    p_op, p_args = types.get(pointer_type, ("", []))
    if op != "OpVariable" or p_op != "OpTypePointer" or not p_args or p_args[0] != "Function" or not args or args[0] != "Function":
        return {"boundary": "nonlocal_or_indirect_load", "reaching_definition_proven": False}
    candidates = stores.get(pointer, [])
    if len(candidates) > MAX_STORES:
        raise ValueError("Direct store count outside bound")
    op_counts, kind_counts = Counter(), Counter()
    for value in candidates:
        writer_op, _, _ = values.get(value, ("unresolved", None, []))
        if not writer_op.startswith("Op") or not writer_op[2:].isalnum():
            writer_op = "unresolved"
        op_counts[writer_op] += 1
        kind_counts[value_shape(value, values, types)[0]] += 1
    return {
        "boundary": "function_load", "direct_store_candidates": len(candidates),
        "writer_opcodes": dict(sorted(op_counts.items())),
        "writer_numeric_kinds": dict(sorted(kind_counts.items())),
        "reaching_definition_proven": False,
    }


def trace_lane(root, lane, values, types, stores):
    value = root
    seen = set()
    casts = Counter()
    for _ in range(MAX_DEPTH + 1):
        if value in seen:
            return {"boundary": "cycle", "reaching_definition_proven": False}
        seen.add(value)
        kind, width = value_shape(value, values, types)
        if not 0 <= lane < width:
            return {"boundary": "unresolved", "reaching_definition_proven": False}
        op, _, args = values.get(value, ("unresolved", None, []))
        if op == "OpBitcast" and len(args) == 1:
            source = value_shape(args[0], values, types)[0]
            casts[f"{source}_to_{kind}"] += 1
        if op == "OpLoad" and args:
            result = direct_writer_summary(args[0], values, types, stores)
            if casts:
                result["lane_bitcasts"] = dict(sorted(casts.items()))
            return result
        if op in ("OpConstant", "OpConstantComposite"):
            return {"boundary": "constant", "reaching_definition_proven": False}
        if op == "OpUndef":
            return {"boundary": "undefined", "reaching_definition_proven": False}
        next_lane = lane_predecessor(op, args, lane, width, values, types)
        if next_lane is None:
            safe_op = op if op.startswith("Op") and op[2:].isalnum() else "unresolved"
            result = {"boundary": "unresolved", "last_opcode": safe_op,
                      "reaching_definition_proven": False}
            if casts:
                result["lane_bitcasts"] = dict(sorted(casts.items()))
            return result
        value, lane = next_lane
    return {"boundary": "depth_limit", "reaching_definition_proven": False}


def analyze(text, *, require_original_layout=False):
    types, values, decorations, stores, fetches = read_module(text)
    if len(fetches) > 16:
        raise ValueError("Unexpected image fetch count")
    roles = [image_role(image, values, decorations) for image, _ in fetches]
    if require_original_layout and roles != ["source", "butterfly", "butterfly"]:
        raise ValueError("Unexpected private original slot0 image layout")
    sites = []
    for i, ((_, coordinate), role) in enumerate(zip(fetches, roles)):
        _, width = value_shape(coordinate, values, types)
        if width < 2:
            raise ValueError("Image fetch coordinate must be a vector")
        sites.append({"site": i, "role": role, "lanes": {
            axis: trace_lane(coordinate, lane, values, types, stores)
            for lane, axis in enumerate(("x", "y"))}})
    return {"direct_writers_are_static_candidates_only": True, "sites": sites}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private module outside bounded size")
        command = ["spirv-dis", "--raw-id", str(args.module)]
        disassembly = subprocess.run(command, check=True, capture_output=True,
                                     text=True, timeout=20)
        result = analyze(disassembly.stdout, require_original_layout=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private FFT local store candidate audit failed\n")
    print("RAFT_T1_FFT_LOCAL_STORE_CANDIDATES " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
