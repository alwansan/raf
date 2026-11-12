"""Replay timestamped Raft excerpts and count explicit water failure roots."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

HEADER = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\s+")
BLIT = re.compile(r'Invalid pass number \((\d+)\) for Graphics\.Blit \(Material "([^"]+)" with (\d+) passes?\)')
DRAW = re.compile(r"RenderingCommandBuffer: shader ([^:]+): invalid pass index (\d+) in (\w+)")
KERNEL = re.compile(r"Invalid kernelIndex \((-?\d+)\) passed, must be non-negative less than (\d+)\.")
FFT_FRAME = re.compile(r"^\s*(?:at )?UltimateWater\.Internal\.Dx11FFT\.ComputeFFT\s*\(")
MATERIALS = {
    "UltimateWater/Spectrum/Water Spectrum": "spectrum",
    "UltimateWater/Foam/Global": "foam_global",
    "UltimateWater/Utilities/Blur (Subsurface Scattering)": "subsurface_blur",
    "UltimateWater/Depth/Depth Copy": "depth_copy",
    "Hidden/BilateralBlur": "bilateral_blur",
}


def scan(lines):
    counts = Counter()
    pending_kernel = None
    fft_frame_seen = False

    def flush():
        if pending_kernel is not None:
            index, bound = pending_kernel
            scope = "fft_stack" if fft_frame_seen else "unattributed_kernel"
            counts[(scope, "kernel_index", index, bound)] += 1

    for line in lines:
        if not HEADER.match(line):
            if pending_kernel is not None and FFT_FRAME.match(line):
                fft_frame_seen = True
            continue
        flush()
        pending_kernel = None
        fft_frame_seen = False
        if match := BLIT.search(line):
            index, material, bound = match.groups()
            if material in MATERIALS:
                counts[(MATERIALS[material], "Graphics.Blit", int(index), int(bound))] += 1
        elif match := DRAW.search(line):
            material, index, operation = match.groups()
            if material in MATERIALS and operation == "DrawMesh":
                counts[(MATERIALS[material], "CommandBuffer.DrawMesh", int(index), None)] += 1
        elif match := KERNEL.search(line):
            pending_kernel = tuple(map(int, match.groups()))
    flush()
    return [
        {"family": family, "operation": operation, "index": index, "reported_upper_bound": bound, "root_lines": count}
        for (family, operation, index, bound), count in sorted(counts.items())
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path, nargs="+")
    args = parser.parse_args()
    result = {}
    for path in args.logs:
        if path.name in result:
            parser.error(f"Duplicate log basename: {path.name}")
        with path.open(encoding="utf-8-sig", errors="strict") as log:
            result[path.name] = scan(log)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
