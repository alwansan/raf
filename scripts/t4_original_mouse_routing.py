"""T4 INPUT-005: source-authenticated, private original mouse routing census.

The original compiled DLL and decompiler output remain inside the CI runner.
Only bounded call-site counts, not game code, types or file paths, leave CI.
This answers routing questions; it does NOT implement Android pointer capture.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ORIGINAL_SIZE = 3211776
ORIGINAL_SHA256 = "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e"

# Preserve string literals (including verbatim C#) while removing comments.
# This is a conservative lexical census, not a full C# compiler or call graph.
LEXEMES = re.compile(
    r'@"(?:[^"]|"")*"|"(?:\\.|[^"\\])*"|'
    r"'(?:\\.|[^'\\])*'|/\*[\s\S]*?\*/|//[^\n]*"
)
DIRECT = re.compile(
    r'\b(?:UnityEngine\s*\.\s*)?Input\s*\.\s*GetAxis(?:Raw)?\s*'
    r'\(\s*"Mouse\s+([XY])"\s*\)'
)
WRAPPED = re.compile(
    r'\bMyInput\s*\.\s*GetAxis(?:Raw)?\s*'
    r'\(\s*"Mouse\s+([XY])"\s*\)'
)
OTHER_AXIS = re.compile(r'\b(?:Input|MyInput)\s*\.\s*GetAxis(?:Raw)?\s*\(')
INPUT_SYSTEM = re.compile(r'\bMouse\s*\.\s*current\s*\.\s*delta\b')
CURSOR_LOCK = re.compile(r'\bCursor\s*\.\s*lockState\s*=')
LOOK_NAME = re.compile(r'camera|look|firstperson|thirdperson|player|person', re.I)
MAX_FILES = 18000
MAX_BYTES = 80 * 1024 * 1024
MAX_FILE_BYTES = 2 * 1024 * 1024


def without_comments(source):
    def substitute(match):
        token = match.group(0)
        if token.startswith("//") or token.startswith("/*"):
            return "".join("\n" if ch == "\n" else " " for ch in token)
        return token
    return LEXEMES.sub(substitute, source)


def assert_original(dll):
    if dll.is_symlink() or not dll.is_file() or dll.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("Unverified original binary")
    digest = hashlib.sha256(dll.read_bytes()).hexdigest()
    if digest != ORIGINAL_SHA256:
        raise ValueError("Unverified original binary")
    return True


def count_sources(source_root):
    if source_root.is_symlink() or not source_root.is_dir():
        raise ValueError("Private source directory must be a real directory")
    files = sorted(source_root.rglob("*.cs"))
    if not files or len(files) > MAX_FILES:
        raise ValueError("Private source population is absent or unbounded")
    counts = {
        "source_files": 0,
        "direct_mouse_x": 0, "direct_mouse_y": 0,
        "wrapped_mouse_x": 0, "wrapped_mouse_y": 0,
        "camera_named_direct_sites": 0,
        "camera_named_wrapped_sites": 0,
        "all_axis_call_syntax_sites": 0,
        "input_system_delta_syntax_sites": 0,
        "cursor_lock_assignment_syntax_sites": 0,
    }
    total = 0
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise ValueError("Symlink or nonregular private source refused")
        size = path.stat().st_size
        total += size
        if size > MAX_FILE_BYTES or total > MAX_BYTES:
            raise ValueError("Private source exceeds bounded scan budget")
        # Read only; all original source stays private.
        source = without_comments(path.read_text(encoding="utf-8-sig"))
        direct = DIRECT.findall(source)
        wrapped = WRAPPED.findall(source)
        counts["source_files"] += 1
        counts["direct_mouse_x"] += direct.count("X")
        counts["direct_mouse_y"] += direct.count("Y")
        counts["wrapped_mouse_x"] += wrapped.count("X")
        counts["wrapped_mouse_y"] += wrapped.count("Y")
        counts["all_axis_call_syntax_sites"] += len(OTHER_AXIS.findall(source))
        counts["input_system_delta_syntax_sites"] += len(INPUT_SYSTEM.findall(source))
        counts["cursor_lock_assignment_syntax_sites"] += len(CURSOR_LOCK.findall(source))
        if LOOK_NAME.search(path.stem):
            counts["camera_named_direct_sites"] += len(direct)
            counts["camera_named_wrapped_sites"] += len(wrapped)
    return counts


def report(dll, sources):
    assert_original(dll)
    counts = count_sources(sources)
    return {
        "status": "AUTHENTIC_ORIGINAL_MOUSE_ROUTING_CENSUS",
        "original_binary_verified": True,
        "source_commit": "15964ea8f246b6e076ce26b60931ee2e1a9a2385",
        "counts": counts,
        "classification": "lexical_only_no_runtime_proof",
        "pointer_capture_implemented": False,
        "camera_injection_path_proven": False,
        "unity_or_android_compiled": False,
        "device_tested": False,
        "original_source_published": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dll", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = report(args.dll, args.source)
        code = 0
    except Exception:
        # Never expose private source paths, symbol names, or decompiler exceptions.
        result = {"status": "ORIGINAL_MOUSE_ROUTING_UNRESOLVED",
                  "original_source_published": False, "device_tested": False}
        code = 2
    print("T4_ORIGINAL_MOUSE_ROUTING " + json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
