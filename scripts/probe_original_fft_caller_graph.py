"""SHA-pinned original Dx11FFT caller link survey without exposing decompiled code.

Recover method signatures using the exact private original DLL and locate
potential WavesRendererFFT callsites. This is lexical evidence, not CSharp
type-resolved control flow or proof of Unity runtime kernel index mapping.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256
from scripts.probe_original_fft_kernel_callsites import (
    parse_original_args, sanitized_argument, sha, SIMPLE_ID,
)

METHOD = re.compile(
    r"\b(?:public|private|protected|internal)\s+"
    r"(?:(?:static|virtual|override|new|sealed|unsafe|async)\s+)*"
    r"(?:(?:[A-Za-z_]\w*(?:[.<>\[\],?]\w*)*)\s+)?"
    r"([A-Za-z_]\w*)\s*\("
)
MAX_DECL = 100
MAX_CALLS = 50


def read_pin(root, name):
    expected = ORIGINAL_SOURCE_SHA256[name]
    matching = list(root.rglob(name + ".cs"))
    if len(matching) != 1 or matching[0].is_symlink() or not matching[0].is_file():
        raise ValueError("Original managed source absent or ambiguous")
    raw = matching[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if sha(raw) != expected:
        raise ValueError("Original managed FFT source SHA256 changed")
    return raw


def source_declarations(text):
    definitions = []
    for m in METHOD.finditer(text):
        if len(definitions) >= MAX_DECL:
            raise ValueError("Unbounded original FFT CSharp method declarations")
        params, end = parse_original_args(text, m.end() - 1)
        # Valid declaration has body or semicolon immediately after argument list.
        if not re.match(r"\s*(?:\{|;|:\s*(?:this|base)\s*\()", text[end+1:end+90]):
            continue
        indexed = [i for i, arg in enumerate(params)
                   if re.search(r"\b(?:kernelIndex|KernelIndex)\b", arg)]
        definitions.append({
            "name": m.group(1),
            "params": params,
            "kernel_index_parameter_positions": indexed,
        })
    return definitions


def find_original_calls(caller, definitions):
    names = {item["name"] for item in definitions
             if item["kernel_index_parameter_positions"]}
    result = []
    for name in sorted(names):
        pattern = re.compile(r"\b" + re.escape(name) + r"\s*\(")
        for match in pattern.finditer(caller):
            if len(result) >= MAX_CALLS:
                raise ValueError("Too many possible original cross-file FFT calls")
            args, end = parse_original_args(caller, match.end() - 1)
            # Ambiguous lexical calls are labelled potential; not type-resolved.
            result.append({
                "original_method_name_sha256": sha(name),
                "caller_line": caller.count("\n", 0, match.start())+1,
                "argument_count": len(args),
                "arguments": [sanitized_argument(a) for a in args[:12]],
                "cross_file_runtime_target_verified": False,
            })
    return result



def private_signature_shape(parameters):
    """Report only primitive type kinds and hashed private identifiers."""
    output = []
    for parameter in parameters:
        parts = parameter.split("=", 1)[0].strip().split()
        if len(parts) < 2 or not SIMPLE_ID.fullmatch(parts[-1]):
            output.append({"kind": "unparsed", "sha256": sha(parameter)})
            continue
        kind = (parts[-2] if parts[-2] in (
            "int", "float", "bool", "ComputeShader", "RenderTexture", "Texture",
            "Vector2", "Vector3", "Material") else "other")
        output.append({"kind": kind, "identifier_sha256": sha(parts[-1]),
                       "original_parameter_declaration_disclosed": False})
    return output


def argument_syntax(arg):
    """Reveal numeric index shape, never original resource/variable names."""
    value = arg.strip()
    index = re.fullmatch(
        r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\[\s*(\d{1,5})\s*\]", value)
    if index:
        return {"kind": "array_item_with_literal_index",
                "array_identifier_sha256": sha(index.group(1)),
                "array_index": int(index.group(2)),
                "private_identifier_disclosed": False}
    numerals = [int(n) for n in re.findall(r"(?<![A-Za-z_])\d+(?![A-Za-z_])", value)]
    return {"kind": "other_expression",
            "array_index_syntax_present": "[" in value and "]" in value,
            "arithmetic_syntax_present": bool(re.search(r"[+*/%-]", value)),
            "numeric_literals": numerals[:8],
            "private_expression_disclosed": False}


def inspect(root):
    source = read_pin(root, "Dx11FFT")
    caller = read_pin(root, "WavesRendererFFT")
    methods = source_declarations(source)
    kernels = [m for m in methods if m["kernel_index_parameter_positions"]]
    if len(kernels) > 12:
        raise ValueError("Unexpected number of kernel parameter methods")
    new_constructor_calls = []
    for match in re.finditer(r"\bnew\s+Dx11FFT\s*\(", caller):
        args, end = parse_original_args(caller, match.end()-1)
        if len(new_constructor_calls) >= MAX_CALLS:
            raise ValueError("Too many original FFT constructor sites")
        new_constructor_calls.append({
            "caller_line": caller.count("\n",0,match.start())+1,
            "arguments": [sanitized_argument(a) for a in args[:12]],
            "argument_syntax": [argument_syntax(a) for a in args[:12]],
            "argument_count": len(args),
            "constructor_target_type_known": True,
        })
    return {
        "original_sources_sha256_verified": True,
        "dx11fft_method_declarations": len(methods),
        "dx11fft_constructor_signatures": [
            {"argument_count": len(m["params"]), "parameters": private_signature_shape(m["params"])}
            for m in methods if m["name"] == "Dx11FFT"
        ],
        "dx11fft_kernel_parameter_method_signatures": [
            {"method_name_sha256": sha(m["name"]),
             "argument_count": len(m["params"]),
             "kernel_parameter_indices": m["kernel_index_parameter_positions"]}
            for m in kernels],
        "waves_renderer_potential_kernel_method_calls": find_original_calls(caller, kernels),
        "waves_renderer_new_dx11fft_calls": new_constructor_calls,
        "unity_runtime_kernel_mapping_verified": False,
        "actual_android_gpu_executed": False,
        "original_source_expressions_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_ORIGINAL_FFT_CALLER_GRAPH " + json.dumps(
        inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
