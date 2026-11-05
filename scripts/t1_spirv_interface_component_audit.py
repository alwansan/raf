"""Audit direct 32-bit SPIR-V vertex-output/fragment-input linkage privately."""
import argparse
import json
from pathlib import Path
import subprocess


def interface(text, model, storage):
    entries, definitions, decorations = [], {}, {}
    builtin_members = {}
    for line in text.splitlines():
        words = line.split()
        if not words:
            continue
        if words[:2] == ["OpEntryPoint", model]:
            # Strip the quoted name without assuming it is a single token.
            fields = line.strip().split('"')
            if len(fields) != 3:
                raise ValueError("Unsupported private entry point")
            entries.append(fields[2].split())
        elif len(words) == 5 and words[0] == "OpMemberDecorate" and words[3] == "BuiltIn":
            builtin_members.setdefault(words[1], set()).add(int(words[2]))
        elif words[0] == "OpDecorate" and len(words) >= 3:
            target, kind = words[1:3]
            if kind in {"Location", "Component", "BuiltIn"}:
                if len(words) != 4 or (target, kind) in decorations:
                    raise ValueError("Invalid private interface decoration")
                decorations[target, kind] = words[3]
        elif len(words) >= 3 and words[1] == "=":
            definitions[words[0]] = (words[2], words[3:])
    if len(entries) != 1 or len(entries[0]) != len(set(entries[0])):
        raise ValueError("Expected one unambiguous private entry point")
    slots = {}
    for variable in entries[0]:
        op, args = definitions[variable]
        if op != "OpVariable" or len(args) < 2:
            raise ValueError("Invalid private interface variable")
        if args[1] != storage or (variable, "BuiltIn") in decorations:
            continue
        pointer_op, pointer = definitions[args[0]]
        if pointer_op != "OpTypePointer" or len(pointer) != 2 or pointer[0] != storage:
            raise ValueError("Invalid private interface pointer")
        pointee_op, members = definitions[pointer[1]]
        if (pointee_op == "OpTypeStruct" and members and
                builtin_members.get(pointer[1]) == set(range(len(members))) and
                (variable, "Location") not in decorations and
                (variable, "Component") not in decorations):
            continue
        if (variable, "Location") not in decorations:
            raise ValueError("Unsupported private interface without direct location")
        location = int(decorations[variable, "Location"])
        component = int(decorations.get((variable, "Component"), "0"))
        op, args = definitions[pointer[1]]
        lanes = 1
        if op == "OpTypeVector" and len(args) == 2:
            lanes = int(args[1])
            op, args = definitions[args[0]]
        if (op, args) == ("OpTypeFloat", ["32"]):
            kind = "float"
        elif op == "OpTypeInt" and args in (["32", "0"], ["32", "1"]):
            kind = "uint" if args[1] == "0" else "int"
        else:
            raise ValueError("Unsupported private interface type")
        if not (0 <= location <= 65535 and 0 <= component < 4 and 1 <= lanes <= 4
                and component + lanes <= 4):
            raise ValueError("Unsupported private component layout")
        for lane in range(component, component + lanes):
            key = (location, lane)
            if key in slots:
                raise ValueError("Overlapping private interface components")
            slots[key] = kind
    return slots


def audit(vertex, fragment):
    offered = interface(vertex, "Vertex", "Output")
    required = interface(fragment, "Fragment", "Input")
    if not required:
        raise ValueError("No direct fragment input components")
    shared = offered.keys() & required.keys()
    missing = len(required.keys() - offered.keys())
    mismatch = sum(offered[key] != required[key] for key in shared)
    return {"vertex_components": len(offered), "fragment_components": len(required),
            "missing_components": missing, "scalar_type_mismatches": mismatch,
            "unused_vertex_components": len(offered.keys() - required.keys()),
            "compatible_numeric_coverage": not (missing or mismatch)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vertex", type=Path)
    parser.add_argument("fragment", type=Path)
    args = parser.parse_args()
    try:
        modules = []
        for path in (args.vertex, args.fragment):
            if not 20 <= path.stat().st_size <= 1024 * 1024:
                raise ValueError("Private module outside bounds")
            modules.append(subprocess.run(["spirv-dis", "--raw-id", str(path)],
                check=True, capture_output=True, text=True, timeout=20).stdout)
        result = audit(*modules)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        parser.exit(2, "Unsupported or invalid private interface\n")
    print("RAFT_T1_SPIRV_INTERFACE " + json.dumps(result, sort_keys=True))
    if not result["compatible_numeric_coverage"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
