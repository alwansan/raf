"""Read-only original Raft water GPU contract inspection (no Unity, no LFS).

Decompile only the already-tracked managed DLL in the existing cheap source CI.
Reject unknown original script revisions. Do not copy or print source bodies.
Kernel names are narrow shader API identifiers, not programs or game assets.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ORIGINAL_SOURCE_SHA256 = {
    "Dx11FFT": "8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0",
    "WavesRendererFFT": "e7f6b8fd477f321120fc626781f0653fe1168f0e86daad0cdf8d9c4e56b323e9",
}
CALLS = {
    "find_kernel": r"\bFindKernel\s*\(",
    "dispatch": r"\bDispatch\s*\(",
    "set_texture": r"\bSetTexture\s*\(",
    "set_buffer": r"\bSetBuffer\s*\(",
    "blit": r"\b(?:Graphics|CommandBuffer)\s*\.\s*Blit\s*\(",
}
FIND_LITERAL = re.compile(r'\bFindKernel\s*\(\s*"([A-Za-z_][\w]{0,79})"\s*\)')
FIND_ALL = re.compile(CALLS["find_kernel"])
KERNEL_INDEX = re.compile(r'\b(?:(?:_?KernelIndex)|(?:kernelIndex))\b')


def inspect(root: Path, expected=ORIGINAL_SOURCE_SHA256):
    if not root.is_dir():
        raise ValueError("Private original CSharp project missing")
    result = {}
    for stem, pinned in expected.items():
        matches = list(root.rglob(stem + ".cs"))
        if len(matches) != 1 or matches[0].is_symlink() or not matches[0].is_file():
            raise ValueError("Require exactly one original " + stem + " source")
        raw = matches[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        digest = hashlib.sha256(raw.encode()).hexdigest()
        if digest != pinned:
            raise ValueError("Unknown original " + stem + " source revision")
        counters = {name: len(re.findall(pattern, raw)) for name, pattern in CALLS.items()}
        if stem == "Dx11FFT" and counters["dispatch"] == 0:
            raise ValueError("Dx11FFT original compute dispatch contract missing")
        named = FIND_LITERAL.findall(raw)
        if len(named) > 32 or len(named) != len(set(named)):
            raise ValueError("Ambiguous literal FindKernel calls")
        result[stem] = {
            "source_sha256": digest,
            "csharp_chars": len(raw),
            "calls": counters,
            "kernel_index_references": len(KERNEL_INDEX.findall(raw)),
            "find_kernel_literal_identifiers": named,
            "find_kernel_dynamic_calls": counters["find_kernel"] - len(named),
            "source_modified": False,
        }
    if result["Dx11FFT"]["calls"]["dispatch"] < 1:
        raise ValueError("No original compute dispatch")
    return {
        "scripts": result,
        "expected_original_serialized_compute_objects": 9,
        "restored_authentic_water_compute_source_verified": False,
        "render_kernel_execution_verified": False,
        "unity_compiled": False,
        "source_modified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_ORIGINAL_WATER_COMPUTE_CONTRACT " +
          json.dumps(inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
