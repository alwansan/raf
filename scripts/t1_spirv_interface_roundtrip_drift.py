"""Compare exact numeric interface keys and types across two private SPIR-V pairs."""
import argparse
import json
from pathlib import Path
import subprocess

from scripts.t1_spirv_interface_component_audit import interface


def compare(source_vertex, source_fragment, derived_vertex, derived_fragment):
    result = {}
    pairs = (("vertex", "Vertex", "Output", source_vertex, derived_vertex),
             ("fragment", "Fragment", "Input", source_fragment, derived_fragment))
    for name, model, storage, original, derived in pairs:
        a = interface(original, model, storage)
        b = interface(derived, model, storage)
        result[name] = {
            "source_components": len(a),
            "derived_components": len(b),
            "removed_component_keys": len(a.keys() - b.keys()),
            "added_component_keys": len(b.keys() - a.keys()),
            "changed_types_at_shared_keys": sum(a[k] != b[k] for k in a.keys() & b.keys()),
            "exact_numeric_map_match": a == b,
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source_vertex", "source_fragment", "derived_vertex", "derived_fragment"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    try:
        modules = []
        for path in vars(args).values():
            if not 20 <= path.stat().st_size <= 1024 * 1024:
                raise ValueError("Private module outside bounds")
            modules.append(subprocess.run(["spirv-dis", "--raw-id", str(path)], check=True,
                           capture_output=True, text=True, timeout=20).stdout)
        report = compare(*modules)
    except (OSError, KeyError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Unsupported or invalid private stage interface\n")
    print("RAFT_T1_SPIRV_ROUNDTRIP_INTERFACE " + json.dumps(report, sort_keys=True))
    if not all(row["exact_numeric_map_match"] for row in report.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
