"""Source-pinned lexical provenance of original RenderTexturesCache image format.

Reports only hashes, public Unity enum names and structural tests. A lexical
chain is not a type-resolved CSharp assignment or a real GPU allocation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from scripts.probe_original_android_display_paths import mask_csharp_noncode
from scripts.probe_original_fft_kernel_callsites import parse_original_args

ORIGINAL_SHA = "4157076c3e4bddc27ac5b24da768d29ff9e6c227c4da07a9e2f55ae9ff6b8245"
IMAGE_CTOR = re.compile(r"\bnew\s+RenderTexture\s*\(")
TYPED_FORMAT = re.compile(r"\bRenderTextureFormat\s+([A-Za-z_]\w*)\b")
ASSIGN = re.compile(r"(?<![\w.])(?:this\s*\.\s*)?([A-Za-z_]\w*)\s*=(?!=)\s*([A-Za-z_]\w*)\s*;")
RANDOM_WRITE = re.compile(r"\.\s*enableRandomWrite\s*=(?!=)\s*([^;]{1,256});")
READ_WRITE = re.compile(r"\bRenderTextureReadWrite\s*\.\s*(Linear|sRGB|Default)\b")


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def source_contract(source, expected_sha=ORIGINAL_SHA):
    if not isinstance(source, str) or len(source) > 750000 or _sha(source) != expected_sha:
        raise ValueError("Original FFT cache source fingerprint mismatch")
    code = mask_csharp_noncode(source)
    if len(re.findall(r"\bclass\s+RenderTexturesCache\b", code)) != 1:
        raise ValueError("Original FFT cache type ambiguous")
    matches = list(IMAGE_CTOR.finditer(code))
    if len(matches) != 1:
        raise ValueError("Expected one original RenderTexture constructor")
    call = matches[0]
    args, end = parse_original_args(source, call.end() - 1)
    if len(args) != 5:
        raise ValueError("Original RenderTexture constructor signature changed")
    expressions = [re.sub(r"\s+", "", arg) for arg in args]
    param_names = TYPED_FORMAT.findall(code)
    if len(param_names) > 50:
        raise ValueError("Unbounded RenderTextureFormat declarations")
    target = re.fullmatch(r"(?:this\.)?([A-Za-z_]\w*)", expressions[3])
    assigns = {}
    for assignment in ASSIGN.finditer(code):
        lhs, rhs = assignment.groups()
        assigns.setdefault(lhs, set()).add(rhs)
    if len(assigns) > 300:
        raise ValueError("Unbounded cache assignment candidates")
    hops = None
    if target is not None:
        field = target.group(1)
        if field in param_names:
            hops = 0
        else:
            frontier = {field}
            for distance in (1, 2):
                frontier = {r for v in frontier for r in assigns.get(v, [])}
                if any(value in param_names for value in frontier):
                    hops = distance
                    break
                if len(frontier) > 40:
                    raise ValueError("Unbounded cache format lineage")
    assignment = list(RANDOM_WRITE.finditer(code))
    if len(assignment) != 1:
        raise ValueError("Original random-write assignment changed")
    val = source[assignment[0].start(1):assignment[0].end(1)].strip()
    rw_mode = "true_literal" if val == "true" else "false_literal" if val == "false" else "reference" if re.fullmatch(r"(?:this\.)?[A-Za-z_]\w*", val) else "expression"
    read_write_modes = sorted(set(m.group(1) for m in READ_WRITE.finditer(code[call.start():end])))
    return {
        "source_sha256": expected_sha,
        "render_texture_constructor_calls": 1,
        "constructor_argument_count": 5,
        "fourth_argument_is_simple_reference": bool(target),
        "render_texture_format_typed_declaration_count": len(param_names),
        "format_reference_to_typed_declaration_lexical_hops": hops,
        "fifth_argument_public_readwrite_modes": read_write_modes,
        "random_write_value_category": rw_mode,
        "random_write_value_identifier_sha256": _sha(val) if rw_mode == "reference" else None,
        "original_gpu_resource_format_verified": False,
        "scope_resolved_or_active_branch_verified": False,
        "source_identifiers_or_expressions_disclosed": False,
        "unity_or_android_gpu_executed": False,
    }


def inspect(root):
    candidates = list(root.rglob("RenderTexturesCache.cs"))
    if len(candidates) != 1 or candidates[0].is_symlink() or not candidates[0].is_file():
        raise ValueError("Original FFT cache source missing or ambiguous")
    source = candidates[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return source_contract(source)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    print("RAFT_ORIGINAL_FFT_CACHE_FORMAT_LINEAGE " + json.dumps(inspect(p.parse_args().source), sort_keys=True))
