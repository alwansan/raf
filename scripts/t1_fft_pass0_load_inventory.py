"""Inventory pass-zero HLSL input read sites without disclosing shader text."""
import argparse
import json
from pathlib import Path
import re

from scripts.t1_fft_unity_gpu_resource_bridge import IMAGE, translated_image_symbols


def inventory(text):
    clean = re.sub(r"/\*[\s\S]*?\*/|//[^\r\n]*", " ", text)
    symbols = translated_image_symbols(clean)
    declarations = {m.start(2) for m in IMAGE.finditer(clean)}
    counts = {}
    for role in ("source", "butterfly"):
        name = re.escape(symbols[role])
        counts[role] = dict(load=0, dimensions=0, subscript=0, unclassified=0,
                            argument_reference=0, coordinate_constructor=0)
        row = counts[role]
        for ref in re.finditer(rf"\b{name}\b", clean):
            if ref.start() in declarations:
                continue
            tail = clean[ref.end():].lstrip()
            load = re.match(r"\.\s*Load\s*\(\s*", tail)
            if load:
                row["load"] += 1
                if re.match(r"u?int[234]\s*\(", tail[load.end():]):
                    row["coordinate_constructor"] += 1
            elif re.match(r"\.\s*GetDimensions\s*\(", tail):
                row["dimensions"] += 1
            elif tail.startswith("["):
                row["subscript"] += 1
            elif clean[:ref.start()].rstrip().endswith(("(", ",")) and tail.startswith((",", ")")):
                row["argument_reference"] += 1
            else:
                row["unclassified"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    try:
        path = args.project / "Assets/T1OriginalDerived/FFT_Candidate_00.compute"
        report = inventory(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        parser.exit(2, "Private pass-zero load inventory could not complete\n")
    print("RAFT_T1_PASS0_LOAD_INVENTORY " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
