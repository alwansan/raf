"""Trace where SHA-pinned original Dx11FFT computes its two-pass kernel index.

Original CSharp source stays only in temporary CI. Reports immutable SHA,
integer constants and expression shapes; does not execute or publish game code.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256
from scripts.probe_original_fft_kernel_callsites import (
    CALL, SIMPLE_ID, parse_original_args, sha
)

MAX_ASSIGNMENTS = 24
MAX_SOURCE = 700_000


def classify_index_rhs(expression):
    """No expression text in report, and definitely no evaluation."""
    result = {
        "original_expression_sha256": sha(re.sub(r"\s+", "", expression)),
        "integer_constants": [int(x) for x in re.findall(
            r"(?<![A-Za-z_.])\d{1,6}(?![A-Za-z_])", expression)][:12],
        "mathf_log2_call": bool(re.search(r"\bMathf\s*\.\s*Log\s*\(", expression)),
        "mathf_pow_call": bool(re.search(r"\bMathf\s*\.\s*Pow\s*\(", expression)),
        "has_conditional_operator": "?" in expression and ":" in expression,
        "has_addition": "+" in expression,
        "has_subtraction": "-" in expression,
        "has_multiplication": "*" in expression,
        "has_shift": "<<" in expression or ">>" in expression,
        "has_array_lookup": "[" in expression and "]" in expression,
        "original_expression_published": False,
    }
    return result


def index_source_links(original, expected):
    if not isinstance(original, str) or len(original) > MAX_SOURCE or sha(original) != expected:
        raise ValueError("Original Dx11FFT managed source hash changed or too large")
    kernel_args = []
    for match in CALL.finditer(original):
        if match.group(1) not in ("Dispatch", "SetTexture"):
            continue
        args, _ = parse_original_args(original, match.end()-1)
        if len(args) >= 3:
            kernel_args.append(args[0].strip())
    base = next((v for v in kernel_args if SIMPLE_ID.fullmatch(v)), None)
    if base is None:
        raise ValueError("Original first-pass FFT index variable not identifiable")
    ref_regex = re.compile(r"\b(?:int\s+|var\s+)?(?:this\s*\.\s*)?" +
                           re.escape(base) + r"\s*(=|\+=|-=)\s*([^;]{1,600})\s*;")
    assignments = []
    for m in ref_regex.finditer(original):
        if len(assignments) >= MAX_ASSIGNMENTS:
            raise ValueError("Too many original FFT index assignments")
        assignments.append({
            "source_line": original.count("\n", 0, m.start()) + 1,
            "operator": m.group(1),
            "right_hand_side": classify_index_rhs(m.group(2)),
        })
    param_declaration = bool(re.search(r"\bint\s+" + re.escape(base) + r"\s*[,)]", original))
    # Detect references without reporting proprietary field identifiers.
    occurrences = len(re.findall(r"\b" + re.escape(base) + r"\b", original))
    return {
        "original_dx11fft_source_sha256_verified": True,
        "first_pass_index_identifier_sha256": sha(base),
        "first_pass_index_source_occurrences": occurrences,
        "first_pass_index_int_parameter_declaration_detected": param_declaration,
        "index_assignment_count": len(assignments),
        "index_assignments": assignments,
        "first_and_second_pass_index_runtime_values_verified": False,
        "original_game_expressions_or_identifiers_published": False,
        "android_gpu_execution_proven": False,
    }


def inspect(root):
    paths = list(root.rglob("Dx11FFT.cs"))
    if len(paths) != 1 or paths[0].is_symlink() or not paths[0].is_file():
        raise ValueError("Original Dx11FFT caller source missing")
    original = paths[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return index_source_links(original, ORIGINAL_SOURCE_SHA256["Dx11FFT"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    a = p.parse_args()
    print("RAFT_ORIGINAL_DX11FFT_INDEX_DERIVATION " +
          json.dumps(inspect(a.source), sort_keys=True))


if __name__ == "__main__":
    main()
