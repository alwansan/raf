"""Inventory pass-zero HLSL input read sites without disclosing shader text."""
import argparse
import json
from pathlib import Path
import re

from scripts.t1_fft_unity_gpu_resource_bridge import translated_image_symbols


def inventory(text):
    clean = re.sub(r"/\*[\s\S]*?\*/|//[^\r\n]*", " ", text)
    symbols = translated_image_symbols(clean)
    counts = {}
    for role in ("source", "butterfly"):
        name = re.escape(symbols[role])
        uses = len(re.findall(rf"\b{name}\b", clean))
        loads = len(re.findall(rf"\b{name}\s*\.\s*Load\s*\(", clean))
        if not loads or uses != loads + 1:
            raise ValueError("Unsupported private texture access")
        counts[role] = loads
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
