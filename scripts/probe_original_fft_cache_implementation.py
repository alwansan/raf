"""Bounded private CSharp9 audit of original FFT RenderTexturesCache allocation paths.

Only named known class identity, source SHA, public Unity API names and numeric
counts leave CI. Does not prove runtime allocation, active branch or GPU format.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from scripts.probe_original_android_display_paths import mask_csharp_noncode
from scripts.probe_original_fft_kernel_callsites import parse_original_args

TARGETS = ("RenderTexturesCache", "RenderTexturesSet")
DECL = re.compile(r"\b(?:class|struct)\s+(RenderTexturesCache|RenderTexturesSet)\b")
MAX_FILES = 12000
MAX_BYTES = 750000
ALLOC = {
    "render_texture_ctor": re.compile(r"\bnew\s+(?:UnityEngine\s*\.\s*)?RenderTexture\s*\("),
    "render_texture_temporary": re.compile(r"\b(?:UnityEngine\s*\.\s*)?RenderTexture\s*\.\s*GetTemporary\s*\("),
    "render_texture_descriptor": re.compile(r"\bnew\s+RenderTextureDescriptor\s*\("),
}
SAFE_FORMAT = {"RGHalf", "RGFloat", "ARGBHalf", "ARGBFloat",
               "Default", "DefaultHDR", "ARGB32", "RHalf", "RFloat"}
FORMAT = re.compile(r"\bRenderTextureFormat\s*\.\s*([A-Za-z_]\w*)\b")


def digest(source):
    return hashlib.sha256(source.encode()).hexdigest()


def inspect_type(source, type_name):
    if len(source) > MAX_BYTES or type_name not in TARGETS:
        raise ValueError("Unbounded cache implementation")
    code = mask_csharp_noncode(source)
    declared = [m.group(1) for m in DECL.finditer(code)]
    if declared.count(type_name) != 1:
        raise ValueError("Target cache type missing or ambiguous")
    allocations = []
    for category, pattern in ALLOC.items():
        for m in pattern.finditer(code):
            args, end = parse_original_args(source, m.end() - 1)
            formats = []
            for fm in FORMAT.finditer(code, m.end(), end):
                name = fm.group(1)
                formats.append({"public_enum": name if name in SAFE_FORMAT else None,
                                "other_member_sha256": None if name in SAFE_FORMAT else digest(name)})
            allocations.append({
                "category": category,
                "line": code.count("\n", 0, m.start()) + 1,
                "argument_count": len(args),
                "explicit_unity_format_tokens": formats,
            })
    allocations.sort(key=lambda a: (a["line"], a["category"]))
    # This lexical inventory intentionally does not attribute allocator sites
    # to a particular method/branch, or infer variable source/value.
    return {
        "type": type_name,
        "source_sha256": digest(source),
        "get_cache_call_count": len(re.findall(r"\bGetCache\s*\(", code)),
        "render_texture_allocations": allocations,
        "enable_random_write_assignment_count": len(re.findall(
            r"\.\s*enableRandomWrite\s*=(?!=)", code)),
        "render_texture_create_call_count": len(re.findall(r"\.\s*Create\s*\(", code)),
        "filter_mode_assignment_count": len(re.findall(r"\.\s*filterMode\s*=(?!=)", code)),
        "runtime_format_or_creation_proven": False,
        "original_identifiers_disclosed": False,
    }


def inspect_source_tree(root):
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Unsafe original CSharp source root")
    files = sorted(root.rglob("*.cs"))
    if len(files) > MAX_FILES:
        raise ValueError("Original CSharp source inventory exceeds bound")
    discovered = {name: [] for name in TARGETS}
    for path in files:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError("Unsafe original source")
        source = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        code = mask_csharp_noncode(source)
        targets = sorted(set(m.group(1) for m in DECL.finditer(code)))
        for target in targets:
            discovered[target].append((path, source))
    if len(discovered["RenderTexturesCache"]) != 1:
        raise ValueError("Original RenderTexturesCache type missing or ambiguous")
    reports = {}
    for name, found in discovered.items():
        if len(found) > 1:
            raise ValueError("Ambiguous original RenderTexturesSet identity")
        reports[name] = inspect_type(found[0][1], name) if found else None
    return {
        "source_files_examined": len(files),
        "type_reports": reports,
        "exact_render_texture_runtime_allocation_proven": False,
        "shader_or_original_game_source_modified": False,
        "unity_or_device_executed": False,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    result = inspect_source_tree(p.parse_args().source)
    print("RAFT_ORIGINAL_FFT_CACHE_IMPLEMENTATION " + json.dumps(result, sort_keys=True))
