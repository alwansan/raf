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


def coordinate_profile(root, values):
    pending = [(root, 0)]
    seen, counts = set(), {}
    while pending:
        value, depth = pending.pop(0)
        if value in seen:
            continue
        seen.add(value)
        if len(seen) > 256:
            raise ValueError("Private coordinate slice exceeds node limit")
        op, args = values.get(value, ("unresolved", ()))
        inputs = ()
        if op in ALL_VALUE_INPUTS:
            inputs = args
        elif op == "OpPhi":
            inputs = args[::2]
        elif op in ("OpCompositeExtract", "OpVectorShuffle"):
            inputs = args[:1 if op == "OpCompositeExtract" else 2]
        elif op not in LEAF_OPS:
            op = "unresolved"
        counts[op] = counts.get(op, 0) + 1
        if depth < 4:
            pending.extend((operand, depth + 1) for operand in reversed(inputs))
        elif inputs:
            counts["depth_boundary"] = counts.get("depth_boundary", 0) + 1
    return counts


def analyze(disassembly, *, coordinates=False):
    decorations, definitions, operations = {}, {}, []
    values = {}
    for line in disassembly.splitlines():
        tokens = line.split()
        if len(tokens) == 4 and tokens[0] == "OpDecorate" and tokens[2] in ("Binding", "DescriptorSet"):
            key = (tokens[1], tokens[2])
            if key in decorations:
                raise ValueError("Duplicate descriptor decoration")
            decorations[key] = int(tokens[3])
        if len(tokens) >= 5 and tokens[1] == "=":
            result, _, op, _, image = tokens[:5]
            if coordinates:
                values[result] = (op, tokens[4:])
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
            coordinate_sites.append({"role": role, "producer_opcodes": coordinate_profile(coordinate, values)})
    if coordinates:
        report["coordinate_sites"] = coordinate_sites
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    parser.add_argument("--coordinates", action="store_true")
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private module outside size bounds")
        disassembly = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                                     check=True, capture_output=True, text=True, timeout=20)
        report = analyze(disassembly.stdout, coordinates=args.coordinates)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private SPIR-V operand audit failed\n")
    print("RAFT_T1_PASS0_SPIRV_PROVENANCE " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
