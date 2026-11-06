"""Count authenticated SPIR-V fetch/query sites by descriptor binding."""
import argparse
import json
from pathlib import Path
import subprocess


OPERATIONS = {
    "OpImageFetch": "fetch",
    "OpImageQuerySize": "query_size",
    "OpImageQuerySizeLod": "query_size_lod",
}
ROOT_EDGES = {"OpLoad", "OpImage", "OpSampledImage", "OpCopyObject"}


# Only these operations expose value inputs to this bounded SSA walk.
ALL_VALUE_INPUTS = {
    "OpCompositeConstruct", "OpIAdd", "OpISub", "OpIMul", "OpUDiv", "OpSDiv",
    "OpUMod", "OpSRem", "OpSMod", "OpBitwiseAnd", "OpBitwiseOr", "OpBitwiseXor",
    "OpShiftLeftLogical", "OpShiftRightLogical", "OpShiftRightArithmetic",
    "OpBitcast", "OpSConvert", "OpUConvert", "OpConvertFToS", "OpConvertFToU",
    "OpCopyObject", "OpSelect",
}
LEAF_OPS = {"OpLoad", "OpConstant", "OpConstantNull", "OpFunctionCall", "OpUndef"}
# Only fixed syntax-level opcode families may be printed on a private stop.
# Do not emit arbitrary instruction names, SSA IDs or literal operands.
SAFE_STOP_OPS = {
    "OpPhi", "OpSelect", "OpIAdd", "OpISub", "OpIMul", "OpUDiv",
    "OpSDiv", "OpUMod", "OpSMod", "OpSRem", "OpFAdd", "OpFSub",
    "OpFMul", "OpFDiv", "OpCompositeExtract", "OpCompositeInsert",
    "OpVectorShuffle", "OpConvertFToS", "OpConvertFToU",
    "OpConvertSToF", "OpConvertUToF", "OpSConvert", "OpUConvert",
    "OpBitcast", "OpCopyObject", "OpFunctionCall", "OpImageFetch",
}


def numeric_kind(type_id, types):
    op, args = types.get(type_id, ("", ()))
    if op == "OpTypeVector" and len(args) == 2:
        op, args = types.get(args[0], ("", ()))
    if op == "OpTypeFloat" and args == ["32"]:
        return "float32"
    if op == "OpTypeInt" and args in (["32", "0"], ["32", "1"]):
        return "uint32" if args[1] == "0" else "sint32"
    return "unresolved"


def bitcast_kind(value, values, types):
    _, destination, args = values[value]
    source_op, source_type, source_args = values.get(args[0], ("", None, ())) if args else ("", None, ())
    storage = "nonload"
    if source_op == "OpLoad":
        _, pointer_type, _ = values.get(source_args[0], ("", None, ())) if source_args else ("", None, ())
        pointer_op, pointer_args = types.get(pointer_type, ("", ()))
        known = {"Function", "Private", "Input", "Uniform", "UniformConstant",
                 "StorageBuffer", "Workgroup", "PushConstant"}
        storage = (pointer_args[0] if pointer_op == "OpTypePointer"
                   and pointer_args and pointer_args[0] in known else "unresolved_load")
    return f"{numeric_kind(source_type, types)}_to_{numeric_kind(destination, types)}:{storage}"


def coordinate_profile(root, values, types, max_depth):
    pending = [(root, 0)]
    seen, counts, bitcasts = set(), {}, {}
    while pending:
        value, depth = pending.pop(0)
        if value in seen:
            continue
        seen.add(value)
        if len(seen) > 256:
            raise ValueError("Private coordinate slice exceeds node limit")
        op, _, args = values.get(value, ("unresolved", None, ()))
        if op == "OpBitcast":
            kind = bitcast_kind(value, values, types)
            bitcasts[kind] = bitcasts.get(kind, 0) + 1
        inputs = ()
        if op in ALL_VALUE_INPUTS:
            inputs = args
        elif op == "OpPhi":
            inputs = args[::2]
        elif op in ("OpCompositeExtract", "OpCompositeInsert", "OpVectorShuffle"):
            inputs = args[:1 if op == "OpCompositeExtract" else 2]
        elif op not in LEAF_OPS:
            op = "unresolved"
        counts[op] = counts.get(op, 0) + 1
        if depth < max_depth:
            pending.extend((operand, depth + 1) for operand in reversed(inputs))
        elif inputs:
            counts["depth_boundary"] = counts.get("depth_boundary", 0) + 1
    return counts, bitcasts


def lane_count(value, values, types):
    _, type_id, _ = values.get(value, ("", None, ()))
    op, args = types.get(type_id, ("", ()))
    if op == "OpTypeVector":
        return int(args[1])
    return int(numeric_kind(type_id, types) != "unresolved")


def lane_input(op, args, lane, width, values, types):
    if op == "OpVectorShuffle":
        index = int(args[2 + lane])
        first_width = lane_count(args[0], values, types)
        second_width = lane_count(args[1], values, types)
        if first_width and second_width and 0 <= index < first_width + second_width:
            return (args[0], index) if index < first_width else (args[1], index - first_width)
    elif op == "OpCompositeInsert" and len(args) == 3:
        return (args[0], 0) if lane == int(args[2]) else (args[1], lane)
    elif op == "OpCompositeExtract" and len(args) == 2 and width == 1:
        return args[0], int(args[1])
    elif op == "OpCompositeConstruct":
        for operand in args:
            operand_width = lane_count(operand, values, types)
            if not operand_width:
                return None
            if lane < operand_width:
                return operand, lane
            lane -= operand_width
    elif op in ("OpBitcast", "OpCopyObject") and len(args) == 1:
        if lane_count(args[0], values, types) == width:
            return args[0], lane
    return None


def coordinate_lane(root, lane, values, types, max_depth):
    bitcasts = []
    boundary = "depth_limit"
    stop = None
    value = root
    for _ in range(max_depth + 1):
        width = lane_count(value, values, types)
        if not 0 <= lane < width:
            boundary = "unresolved"
            stop = {"stop_opcode": "other_opcode", "stop_numeric_kind": "unresolved"}
            break
        op, type_id, args = values.get(value, ("unresolved", None, []))
        if op == "OpBitcast":
            bitcasts.append(bitcast_kind(value, values, types))
        following = lane_input(op, args, lane, width, values, types)
        if following is None:
            boundary = {"OpLoad": "load", "OpConstant": "constant",
                        "OpConstantNull": "constant", "OpUndef": "undefined"}.get(op, "unresolved")
            if boundary == "unresolved":
                kind = numeric_kind(type_id, types)
                stop = {
                    "stop_opcode": op if op in SAFE_STOP_OPS else "other_opcode",
                    "stop_numeric_kind": kind if kind in ("float32", "sint32", "uint32")
                                         else "unresolved",
                }
            break
        value, lane = following
    report = {"typed_bitcasts": bitcasts, "boundary": boundary}
    if stop is not None:
        report.update(stop)
    return report


def analyze(disassembly, *, coordinates=False, coordinate_depth=4):
    if not 1 <= coordinate_depth <= 12:
        raise ValueError("Private coordinate slice depth outside bounds")
    decorations, definitions, operations = {}, {}, []
    values, types = {}, {}
    for line in disassembly.splitlines():
        tokens = line.split()
        if len(tokens) == 4 and tokens[0] == "OpDecorate" and tokens[2] in ("Binding", "DescriptorSet"):
            key = (tokens[1], tokens[2])
            if key in decorations:
                raise ValueError("Duplicate descriptor decoration")
            decorations[key] = int(tokens[3])
        if coordinates and len(tokens) >= 3 and tokens[1] == "=":
            result, _, op, *args = tokens
            if op.startswith("OpType"):
                types[result] = (op, args)
            elif args:
                values[result] = (op, args[0], args[1:])
        if len(tokens) >= 5 and tokens[1] == "=":
            result, _, op, _, image = tokens[:5]
            if op in ROOT_EDGES:
                definitions[result] = image
            elif op in OPERATIONS:
                operations.append((OPERATIONS[op], image, tokens[5] if len(tokens) > 5 else None))

    report = {role: dict.fromkeys(OPERATIONS.values(), 0)
              for role in ("source", "butterfly", "unresolved")}
    coordinate_sites = []
    for operation, root, coordinate in operations:
        seen = set()
        while root in definitions:
            if root in seen:
                raise ValueError("Cyclic image provenance")
            seen.add(root)
            root = definitions[root]
        role = "unresolved"
        if decorations.get((root, "DescriptorSet")) == 0:
            role = {0: "source", 1: "butterfly"}.get(decorations.get((root, "Binding")), role)
        report[role][operation] += 1
        if coordinates and operation == "fetch":
            counts, bitcasts = coordinate_profile(coordinate, values, types, coordinate_depth)
            site = {"role": role, "producer_opcodes": counts}
            if bitcasts:
                site["typed_coordinate_bitcasts"] = bitcasts
            if lane_count(coordinate, values, types) >= 2:
                site["coordinate_lanes"] = {
                    axis: coordinate_lane(coordinate, lane, values, types, coordinate_depth)
                    for lane, axis in enumerate(("x", "y"))
                }
            coordinate_sites.append(site)
    if coordinates:
        report["coordinate_sites"] = coordinate_sites
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    parser.add_argument("--coordinates", action="store_true")
    parser.add_argument("--coordinate-depth", type=int, default=4)
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private module outside size bounds")
        disassembly = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                                     check=True, capture_output=True, text=True, timeout=20)
        report = analyze(disassembly.stdout, coordinates=args.coordinates,
                         coordinate_depth=args.coordinate_depth)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private SPIR-V operand audit failed\n")
    print("RAFT_T1_PASS0_SPIRV_PROVENANCE " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
