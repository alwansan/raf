"""Source-pinned CSharp9 WavesRendererFFT OnDestroy->Dispose callgraph.

A lexical bounded same-class method graph, not type-resolved control flow.
No original names other than public lifecycle callbacks or private source text
are emitted. The source binary has already been validated by the workflow.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from scripts.probe_original_android_display_paths import mask_csharp_noncode
from scripts.a4_original_gpu_cache_lifecycle import HEADER, CONTROL, _closing_brace

ORIGINAL_WAVES_SHA = "2db9943277431ae23930e7ef0753a4575466ab7d68f5df435871724c1270d276"
MAX_BYTES = 750000
SELF_CALL = re.compile(r"(?<![\w.])(?:this\s*\.\s*)?([A-Za-z_]\w*)\s*\(")
CLEANUP = re.compile(r"\.\s*(?:Dispose|Release|ReleaseTemporary|Destroy|DestroyImmediate)\s*\(")


def inspect_source(text, expected_sha=ORIGINAL_WAVES_SHA):
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Unbounded original FFT owner source")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if sha != expected_sha:
        raise ValueError("WavesRendererFFT CSharp9 source fingerprint mismatch")
    code = mask_csharp_noncode(text)
    if len(re.findall(r"\bclass\s+WavesRendererFFT\b", code)) != 1:
        raise ValueError("Original water renderer type ambiguous")
    methods = {}
    for header in HEADER.finditer(code):
        name = header.group("name")
        if name in CONTROL:
            continue
        start = header.end()
        end = _closing_brace(code, start - 1)
        methods.setdefault(name, []).append(code[start:end])
    if len(methods.get("OnDestroy", [])) != 1 or len(methods.get("Dispose", [])) != 1:
        raise ValueError("Original OnDestroy/Dispose method identity ambiguous")
    if len(methods) > 250:
        raise ValueError("Too many bounded methods")
    graph = {}
    for name, bodies in methods.items():
        graph[name] = set()
        for body in bodies:
            graph[name].update(value for value in SELF_CALL.findall(body)
                               if value in methods)
    seen, queue = set(), ["OnDestroy"]
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        queue.extend(sorted(graph[name] - seen))
        if len(seen) > 250:
            raise ValueError("Unbounded call graph")
    original_destroy = methods["OnDestroy"][0]
    # We know that the original class contains an explicit Dispose method;
    # a lexical edge is not a guarantee that any call is executed at runtime.
    return {
        "source_sha256": sha,
        "source_method_count": len(methods),
        "on_destroy_declared": True,
        "dispose_declared": True,
        "on_destroy_direct_self_dispose": "Dispose" in graph["OnDestroy"],
        "on_destroy_transitive_self_dispose_lexical": "Dispose" in seen,
        "on_destroy_direct_member_cleanup_calls": len(CLEANUP.findall(original_destroy)),
        "on_destroy_direct_self_call_count": len(graph["OnDestroy"]),
        "on_destroy_reachable_self_methods_count": len(seen),
        "source_ownership_type_or_runtime_dispatch_resolved": False,
        "dispose_is_idempotent_or_double_free_safe_proven": False,
        "on_device_lifetime_or_oom_verified": False,
        "leak_fixed": False,
        "build_ready": False,
    }


def inspect_root(root):
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Unsafe original source root")
    paths = list(root.rglob("WavesRendererFFT.cs"))
    if len(paths) != 1 or paths[0].is_symlink() or not paths[0].is_file():
        raise ValueError("Original WavesRendererFFT source missing or unsafe")
    text = paths[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return inspect_source(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    args = parser.parse_args()
    print("RAFT_A4_ONDESTROY_DISPOSE_CALLGRAPH " +
          json.dumps(inspect_root(args.source_root), sort_keys=True))
