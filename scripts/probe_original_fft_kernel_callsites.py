"""Audit SHA-pinned original Raft FFT managed callsite kernel arguments.

No original game code, shader names, identifier text, source expressions or
decompiled DLLs are emitted. Numeric kernel literals, arg counts and hashed
identifier expressions are structural diagnostics, NOT runtime kernel mapping.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256

CALL = re.compile(r"\b(Dispatch|SetTexture|SetBuffer|FindKernel)\s*\(")
RECEIVER = re.compile(r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\.\s*$")
SIMPLE_ID = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*")
INTEGER = re.compile(r"(?:0|[1-9]\d{0,7})")
MAX_CALLS = 40
MAX_SOURCE_CHARS = 700_000


def sha(text):
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def parse_original_args(source, start):
    """Bounded balanced call parser with nested expressions and strings."""
    if source[start] != "(":
        raise ValueError("Expected CSharp call opening parenthesis")
    start_offset = start
    level = 0
    square = 0
    curly = 0
    quote = None
    escaped = False
    arg_start = start + 1
    args = []
    for idx in range(start, min(len(source), start + 16_384)):
        char = source[idx]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ('"', "'"):
            quote = char
        elif char == "(":
            level += 1
        elif char == ")":
            level -= 1
            if level == 0:
                last = source[arg_start:idx].strip()
                if last:
                    args.append(last)
                if len(args) > 20:
                    raise ValueError("Original CSharp API argument count out of bounds")
                return args, idx
            if level < 0:
                break
        elif char == "[":
            square += 1
        elif char == "]":
            square -= 1
        elif char == "{":
            curly += 1
        elif char == "}":
            curly -= 1
        elif char == "," and level == 1 and square == 0 and curly == 0:
            args.append(source[arg_start:idx].strip())
            arg_start = idx + 1
    raise ValueError("Unterminated original compute API call at " + str(start_offset))


def sanitized_argument(arg):
    arg = arg.strip()
    if INTEGER.fullmatch(arg):
        return {"kind": "numeric_literal", "value": int(arg), "source_expression_disclosed": False}
    if SIMPLE_ID.fullmatch(arg):
        return {"kind": "identifier_or_member", "sha256": sha(arg),
                "source_expression_disclosed": False}
    if re.fullmatch(r'"[^"\\\r\n]{0,160}"', arg):
        return {"kind": "literal_string", "sha256": sha(arg[1:-1]),
                "source_expression_disclosed": False}
    return {"kind": "expression", "sha256": sha(re.sub(r"\s+", "", arg)),
            "source_expression_disclosed": False}


def analyze_source(source, expected_sha):
    if not isinstance(source, str) or len(source) > MAX_SOURCE_CHARS:
        raise ValueError("Original managed FFT code outside size bound")
    if sha(source) != expected_sha:
        raise ValueError("Original managed FFT callsite source SHA256 mismatch")
    rows = []
    for match in CALL.finditer(source):
        if len(rows) >= MAX_CALLS:
            raise ValueError("Unbounded original compute API calls")
        op = match.group(1)
        args, end = parse_original_args(source, match.end()-1)
        previous = source[max(0, match.start()-180):match.start()]
        receiver_match = RECEIVER.search(previous)
        rows.append({
            "call_kind": op,
            "original_callsite_line_number": source.count("\n", 0, match.start()) + 1,
            "argument_count": len(args),
            "receiver_identifier_sha256": sha(receiver_match.group(1))
                if receiver_match else None,
            "kernel_or_first_arg": sanitized_argument(args[0]) if args else None,
            "second_arg": sanitized_argument(args[1]) if len(args) > 1 else None,
            "last_arg": sanitized_argument(args[-1]) if args else None,
            "caller_original_code_disclosed": False,
            "runtime_shader_kernel_indices_proven": False,
        })
    return {
        "original_source_sha256_verified": True,
        "calls_by_api": dict(sorted(Counter(row["call_kind"] for row in rows).items())),
        "compute_api_callsites": rows,
        "runtime_kernel_index_to_serialized_program_proven": False,
        "original_source_or_binary_exported": False,
    }


def inspect(path):
    result = {}
    for name, expected in ORIGINAL_SOURCE_SHA256.items():
        files = list(path.rglob(name + ".cs"))
        if len(files) != 1 or files[0].is_symlink() or not files[0].is_file():
            raise ValueError("Original managed FFT caller missing or ambiguous")
        source = files[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        result[name] = analyze_source(source, expected)
    return {"callers": result, "source_only_ci": True,
            "actual_android_execution": False,
            "project_or_original_sources_modified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    print("RAFT_ORIGINAL_FFT_CALLSITE_KERNEL_ARGUMENTS " +
          json.dumps(inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
