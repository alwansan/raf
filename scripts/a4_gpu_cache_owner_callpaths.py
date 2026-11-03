"""A4 ZIP2-owned FFT GPU cache caller/lifetime mapping; private CSharp9, CPU only.

Only aggregate Unity API categories, known lifecycle names, file hashes and
method-name digests leave the private runner. Calls are lexical evidence, NOT
proof that Unity invokes a callback or that a resource leak is closed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_android_display_paths import mask_csharp_noncode
from scripts.a4_original_gpu_cache_lifecycle import HEADER, CONTROL, _closing_brace

# Names of known original rendering owners; not discovered private file names.
TARGETS = ("RenderTexturesCache", "RenderTexturesSet", "GpuFFT",
           "Dx11FFT", "WavesRendererFFT", "WindWaves")
PUBLIC_LIFECYCLE = frozenset(("OnDisable", "OnDestroy", "OnEnable",
                              "Dispose", "Release", "OnApplicationQuit"))
MAX_BYTES = 750000
MAX_METHODS = 300
CALLS = {
    "release": r"\.\s*Release\s*\(",
    "dispose": r"\.\s*Dispose\s*\(",
    "destroy": r"\b(?:Object\s*\.\s*)?Destroy(?:Immediate)?\s*\(",
    "get_cache": r"\bGetCache\s*\(",
    "get_temporary": r"\bGetTemporary\s*\(",
    "new_cache": r"\bnew\s+RenderTexturesCache\s*\(",
    "new_set": r"\bnew\s+RenderTexturesSet\s*\(",
    "new_render_target": r"\bnew\s+RenderTexture\s*\(",
    "finally": r"\bfinally\s*\{",
    "return": r"\breturn\b",
}
RX = {key: re.compile(pattern) for key, pattern in CALLS.items()}
TYPED_FIELD = re.compile(
    r"\b(?:RenderTexturesCache|RenderTexturesSet)\s+([A-Za-z_]\w*)\b"
)


def inspect_owner_source(source, type_name):
    if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Unbounded original rendering owner")
    if type_name not in TARGETS:
        raise ValueError("Unknown original rendering owner")
    code = mask_csharp_noncode(source)
    if len(re.findall(r"\b(?:class|struct)\s+" + re.escape(type_name) + r"\b", code)) != 1:
        raise ValueError("Missing or ambiguous original rendering owner type")
    typed_fields = set(TYPED_FIELD.findall(code))
    methods = []
    for match in HEADER.finditer(code):
        name = match.group("name")
        if name in CONTROL:
            continue
        end = _closing_brace(code, match.end() - 1)
        body = code[match.end():end]
        calls = {key: len(rx.findall(body)) for key, rx in RX.items()}
        matched_receivers = []
        for field in typed_fields:
            if re.search(r"\b" + re.escape(field) + r"\s*\.\s*(?:Dispose|Release)\s*\(", body):
                matched_receivers.append(field)
        relevant = any(calls.values()) or name in PUBLIC_LIFECYCLE or bool(matched_receivers)
        if relevant:
            methods.append({
                "name_category": name if name in PUBLIC_LIFECYCLE else "other",
                "name_digest": hashlib.sha256(name.encode("utf-8")).hexdigest()[:12],
                "line": code.count("\n", 0, match.start()) + 1,
                "calls": {k: v for k, v in calls.items() if v},
                "typed_cache_field_release_call": bool(matched_receivers),
                "typed_cache_field_release_receiver_hashes":
                    sorted(hashlib.sha256(v.encode()).hexdigest()[:12] for v in matched_receivers),
                "original_runtime_invocation_proven": False,
            })
    if len(methods) > MAX_METHODS:
        raise ValueError("Unbounded rendering owner method inventory")
    methods.sort(key=lambda m: m["line"])
    return {
        "original_owner": type_name,
        "decompiled_source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "typed_cache_fields_detected": len(typed_fields),
        "structural_relevant_methods": methods,
        "lifecycle_callback_declared": sorted(set(
            m["name_category"] for m in methods if m["name_category"] in PUBLIC_LIFECYCLE)),
        "resolved_cleanup_reachability": False,
        "original_runtime_or_android_gpu_executed": False,
        "original_source_text_disclosed": False,
    }


def inspect_root(root):
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Unsafe private original source root")
    results = []
    for stem in TARGETS:
        paths = list(root.rglob(stem + ".cs"))
        if len(paths) > 1:
            raise ValueError("Ambiguous original rendering owner file")
        if not paths:
            if stem in ("RenderTexturesCache", "GpuFFT", "Dx11FFT", "WavesRendererFFT"):
                raise ValueError("Required original rendering owner absent")
            continue
        path = paths[0]
        if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_BYTES:
            raise ValueError("Unsafe original rendering owner file")
        normalized = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        results.append(inspect_owner_source(normalized, stem))
    return {
        "source_files_checked": len(results),
        "owners": results,
        "source_assembly_authentication_required_before_probe": True,
        "ownership_or_release_reachability_proven": False,
        "build_ready": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    args = p.parse_args()
    print("RAFT_A4_FFT_CACHE_OWNER_CALLPATHS " +
          json.dumps(inspect_root(args.source_root), sort_keys=True))


if __name__ == "__main__":
    main()
