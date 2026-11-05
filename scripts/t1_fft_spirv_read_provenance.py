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


def analyze(disassembly):
    decorations, definitions, operations = {}, {}, []
    for line in disassembly.splitlines():
        tokens = line.split()
        if len(tokens) == 4 and tokens[0] == "OpDecorate" and tokens[2] in ("Binding", "DescriptorSet"):
            key = (tokens[1], tokens[2])
            if key in decorations:
                raise ValueError("Duplicate descriptor decoration")
            decorations[key] = int(tokens[3])
        if len(tokens) >= 5 and tokens[1] == "=":
            result, _, op, _, image = tokens[:5]
            if op in ROOT_EDGES:
                definitions[result] = image
            elif op in OPERATIONS:
                operations.append((OPERATIONS[op], image))

    report = {role: dict.fromkeys(OPERATIONS.values(), 0)
              for role in ("source", "butterfly", "unresolved")}
    for operation, root in operations:
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
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.module.stat().st_size <= 1024 * 1024:
            raise ValueError("Private module outside size bounds")
        disassembly = subprocess.run(["spirv-dis", "--raw-id", str(args.module)],
                                     check=True, capture_output=True, text=True, timeout=20)
        report = analyze(disassembly.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private SPIR-V operand audit failed\n")
    print("RAFT_T1_PASS0_SPIRV_PROVENANCE " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
