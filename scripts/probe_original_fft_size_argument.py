"""SHA-pinned, redacted lexical trace of original FFT constructor size.
No original identifiers/code or shader bytes leave CI; not runtime type/dataflow proof.
"""
import argparse
import json
from pathlib import Path
import re
from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256
from scripts.probe_original_fft_kernel_callsites import parse_original_args, sha, SIMPLE_ID
from scripts.probe_original_android_display_paths import mask_csharp_noncode

def classify_rhs(rhs):
    compact = re.sub(r"\s+", "", rhs)
    if len(compact) > 1000:
        raise ValueError("Unbounded FFT size expression")
    if re.fullmatch(r"\d{1,9}", compact):
        kind, literal = "integer_literal", int(compact)
    elif SIMPLE_ID.fullmatch(compact):
        kind, literal = "identifier_or_member", None
    elif re.search(r"\b[A-Za-z_]\w*\s*\(", compact):
        kind, literal = "call_or_cast_expression", None
    elif re.search(r"[+*/%<>-]", compact):
        kind, literal = "arithmetic_expression", None
    else:
        kind, literal = "other_expression", None
    return {"rhs_kind": kind, "integer_literal": literal,
            "rhs_compact_sha256": sha(compact), "private_expression_disclosed": False}

def analyze(caller, expected_sha):
    if not isinstance(caller, str) or len(caller) > 700000 or sha(caller) != expected_sha:
        raise ValueError("Original FFT caller source fingerprint mismatch")
    masked = mask_csharp_noncode(caller)
    constructors = list(re.finditer(r"\bnew\s+Dx11FFT\s*\(", masked))
    if len(constructors) != 1:
        raise ValueError("Original FFT constructor call count changed")
    args, _ = parse_original_args(caller, constructors[0].end()-1)
    if len(args) != 4:
        raise ValueError("Original FFT constructor arity changed")
    second = re.sub(r"\s+", "", args[1])
    if not SIMPLE_ID.fullmatch(second):
        raise ValueError("Original FFT size argument is no longer a simple reference")
    name = second.split(".")[-1]
    decl = re.compile(r"\b(int|uint|long|float|double|var)\s+" + re.escape(name) + r"\b")
    writes = re.compile(r"(?<![\w])(?:this\s*\.\s*)?" + re.escape(name)
                        + r"\s*(\+=|-=|\*=|/=|=(?!=))\s*([^;]{1,1000});")
    declarations = [{"line": masked.count("\n", 0, m.start())+1,
                     "declared_type_kind": m.group(1)} for m in decl.finditer(masked)]
    if len(declarations) > 32:
        raise ValueError("Unbounded FFT size declarations")
    changes = []
    for m in writes.finditer(masked):
        if len(changes) >= 32:
            raise ValueError("Unbounded FFT size writes")
        changes.append({"line": masked.count("\n", 0, m.start())+1,
                        "assignment_operator": m.group(1),
                        **classify_rhs(caller[m.start(2):m.end(2)])})
    return {
        "original_waves_renderer_sha256": expected_sha,
        "constructor_call_count": len(constructors),
        "constructor_line": masked.count("\n", 0, constructors[0].start())+1,
        "size_argument_identifier_sha256": sha(second),
        "size_argument_has_member_access": "." in second,
        "size_argument_declarations": declarations,
        "size_argument_lexical_writes": changes,
        "source_level_size_value_proven": False,
        "runtime_resolution_or_unity_kernel_mapping_verified": False,
        "original_identifiers_or_expressions_published": False,
        "unity_or_device_execution": False,
    }

def inspect(root):
    paths = list(root.rglob("WavesRendererFFT.cs"))
    if len(paths) != 1 or paths[0].is_symlink() or not paths[0].is_file():
        raise ValueError("Original WavesRendererFFT source missing or ambiguous")
    source = paths[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return analyze(source, ORIGINAL_SOURCE_SHA256["WavesRendererFFT"])

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    print("RAFT_ORIGINAL_FFT_SIZE_ARGUMENT " + json.dumps(inspect(p.parse_args().source), sort_keys=True))
