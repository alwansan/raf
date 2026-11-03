"""A4 bounded original GPU cache ownership survey, CPU-only.

Authenticates original CSharp9 RenderTexturesCache content before reporting
aggregate allocation/release categories. Never prints raw original code, field
names or method identifiers. This is NOT a leak, reachability or GPU runtime
proof: ownership can transfer beyond the allocating method.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_android_display_paths import mask_csharp_noncode

CACHE_SHA = "4157076c3e4bddc27ac5b24da768d29ff9e6c227c4da07a9e2f55ae9ff6b8245"
MAX_SOURCE_BYTES = 750_000
MAX_METHODS = 200
# Include constructors as well as regular CSharp9 instance/static methods.
HEADER = re.compile(
    r"(?m)^[ \t]*(?:(?:public|private|protected|internal|static|virtual|override|sealed|new|"
    r"async|extern|unsafe)\s+){0,8}"
    r"(?:[\w.<>,?\[\]]+\s+)?(?P<name>[A-Za-z_]\w*)\s*"
    r"\([^;{}]{0,420}\)\s*\{"
)
CONTROL = frozenset(("if", "else", "for", "while", "switch", "catch", "using",
                     "lock", "foreach", "return", "throw", "finally", "try"))
SAFE_CALLBACKS = frozenset(("OnDestroy", "OnDisable", "OnEnable", "Dispose",
                             "Release", "GetCache", "GetTemporary"))
PATTERNS = {
    "gpu_ctor": r"\bnew\s+(?:UnityEngine\s*\.\s*)?RenderTexture\s*\(",
    "gpu_create": r"\.\s*Create\s*\(",
    "gpu_release": r"\.\s*Release\s*\(",
    "gpu_get_temporary": r"\bRenderTexture\s*\.\s*GetTemporary\s*\(",
    "gpu_release_temporary": r"\bRenderTexture\s*\.\s*ReleaseTemporary\s*\(",
    "dispose": r"\.\s*Dispose\s*\(",
    "destroy": r"\b(?:Object\s*\.\s*)?Destroy(?:Immediate)?\s*\(",
    "get_cache": r"\bGetCache\s*\(",
    "clear": r"\.\s*Clear\s*\(",
    "remove": r"\.\s*Remove\s*\(",
    "returns": r"\breturn\b",
    "throws": r"\bthrow\b",
    "finally": r"\bfinally\s*\{",
}
RX = {k: re.compile(p) for k, p in PATTERNS.items()}


def _closing_brace(masked, opening):
    if opening >= len(masked) or masked[opening] != "{":
        raise ValueError("Invalid masked CSharp method brace")
    depth = 1
    for idx in range(opening + 1, len(masked)):
        if masked[idx] == "{":
            depth += 1
        elif masked[idx] == "}":
            depth -= 1
            if depth == 0:
                return idx
    raise ValueError("Unbalanced original CSharp method")


def _finally_has_release(body):
    for m in RX["finally"].finditer(body):
        opening = m.end() - 1
        end = _closing_brace(body, opening)
        span = body[opening + 1:end]
        if (RX["gpu_release"].search(span) or RX["gpu_release_temporary"].search(span)
                or RX["dispose"].search(span) or RX["destroy"].search(span)):
            return True
    return False


def inspect_source(source, expected_sha=CACHE_SHA):
    if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("Invalid/unbounded original cache source")
    sha = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if sha != expected_sha:
        raise ValueError("Original GPU cache source SHA mismatch")
    masked = mask_csharp_noncode(source)
    if len(re.findall(r"\bclass\s+RenderTexturesCache\b", masked)) != 1:
        raise ValueError("Original RenderTexturesCache identity missing/ambiguous")
    methods = []
    for match in HEADER.finditer(masked):
        name = match.group("name")
        if name in CONTROL:
            continue
        opening = match.end() - 1
        end = _closing_brace(masked, opening)
        body = masked[opening + 1:end]
        counts = {key: len(rx.findall(body)) for key, rx in RX.items()}
        # Keep only resource operations / known lifecycle callbacks; not the
        # source itself, variable names, private method names or raw strings.
        relevant = (sum(counts[key] for key in (
            "gpu_ctor", "gpu_create", "gpu_release", "gpu_get_temporary",
            "gpu_release_temporary", "dispose", "destroy", "get_cache",
            "clear", "remove")) > 0 or name in SAFE_CALLBACKS)
        if relevant:
            methods.append({
                "api": name if name in SAFE_CALLBACKS else "other",
                "method_fingerprint": hashlib.sha256(name.encode()).hexdigest()[:12],
                "start_line": masked.count("\n", 0, match.start()) + 1,
                "operations": {k: v for k, v in counts.items() if v},
                "release_inside_finally_seen": _finally_has_release(body),
                "exception_path_proven_safe": False,
                "ownership_transfer_resolved": False,
            })
    if len(methods) > MAX_METHODS:
        raise ValueError("Unbounded original GPU cache method matches")
    if not methods or not any(m["operations"].get("gpu_ctor", 0) for m in methods):
        raise ValueError("Original GPU cache allocator not found in method bodies")
    methods.sort(key=lambda m: m["start_line"])
    totals = {k: sum(m["operations"].get(k, 0) for m in methods) for k in RX}
    return {
        "original_cache_sha256": sha,
        "bounded_relevant_methods": methods,
        "aggregate_operations": totals,
        "definite_source_allocation_lexical_sites": totals["gpu_ctor"],
        "exception_safe_cleanup_or_leak_proven": False,
        "game_gpu_allocation_runtime_or_phone_verified": False,
        "original_source_text_disclosed": False,
        "build_ready": False,
    }


def inspect_root(root):
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Untrusted private original source root")
    candidates = list(root.rglob("RenderTexturesCache.cs"))
    if len(candidates) != 1:
        raise ValueError("Original cache file absent or ambiguous")
    path = candidates[0]
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("Unsafe original cache file")
    normalized = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return inspect_source(normalized)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_A4_ORIGINAL_GPU_CACHE_LIFETIME " +
          json.dumps(inspect_root(args.source_root), sort_keys=True))


if __name__ == "__main__":
    main()
