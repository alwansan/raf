"""T4 INPUT-005: fail-closed, Android-only replacement of original legacy mouse axes.

Never modify game assets, original compiled DLL, .meta, GUIs or original scene links.
The caller supplies the exact immutable ZIP2 original DLL and decompiled source.
On Windows the Android-only runtime shim is not imported into the output project.
"""
import argparse
import json
import re
from pathlib import Path

from scripts.t4_original_mouse_routing import assert_original, without_comments

# Anchored to the eight direct original axis sites, not all mouse/button input.
AXIS = re.compile(
    r"\b(?:UnityEngine\s*\.\s*)?Input\s*\.\s*(GetAxis(?:Raw)?)\s*"
    r'\(\s*("Mouse\s+[XY]")\s*\)'
)
LOCK = re.compile(
    r"\bCursor\s*\.\s*lockState\s*=\s*(?![=])"
    r"(?P<rhs>[^;\n]+);"
)
SHIM = "RaftAndroid.Platform.AndroidPhysicalMouseCapture"
EXPECTED = {"mouse_x": 4, "mouse_y": 4, "cursor_lock": 2}


def replacement_plan(root: Path, *, project_assets=False):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Regular source directory required")
    files = sorted(root.rglob("*.cs"))
    if not files or len(files) > 18000:
        raise ValueError("Source population missing or unbounded")
    changed = {}
    counts = {"mouse_x": 0, "mouse_y": 0, "cursor_lock": 0}
    for file in files:
        if file.is_symlink() or not file.is_file():
            raise ValueError("Linked original source refused")
        if project_assets and "Assembly-CSharp" not in file.relative_to(root).parts:
            continue
        if file.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Oversized original source refused")
        data = file.read_text(encoding="utf-8-sig")
        visible = without_comments(data)
        if len(visible) != len(data):
            raise ValueError("Lexical comments must preserve source positions")
        matches = []
        for m in AXIS.finditer(visible):
            axis = "mouse_x" if "X" in m.group(2) else "mouse_y"
            counts[axis] += 1
            # Preserve GetAxis vs GetAxisRaw behavior and the literal axis argument.
            matches.append((m.start(), m.end(), SHIM + "." + m.group(1) + "(" + m.group(2) + ")"))
        for m in LOCK.finditer(visible):
            counts["cursor_lock"] += 1
            matches.append((m.start(), m.end(), SHIM + ".ApplyCursorLock(" + data[m.start("rhs"):m.end("rhs")] + ");"))
        if not matches:
            continue
        matches.sort(key=lambda item: item[0])
        if any(a[1] > b[0] for a, b in zip(matches, matches[1:])):
            raise ValueError("Overlapping original input patch candidates")
        result = data
        for start, end, replacement in reversed(matches):
            result = result[:start] + replacement + result[end:]
        changed[file] = result
    if counts != EXPECTED:
        raise ValueError("Original mouse-call cardinality drift")
    if not changed:
        raise ValueError("No original input sites found")
    return changed, counts


def patch(source_root: Path, original_dll: Path, *, apply=False, project_assets=False, backup=None):
    assert_original(original_dll)
    sources, counts = replacement_plan(source_root, project_assets=project_assets)
    if apply:
        if backup is None or backup.is_symlink() or backup.exists():
            raise ValueError("New, nonlinked private backup directory is required")
        if backup.resolve().is_relative_to(source_root.resolve()) or source_root.resolve().is_relative_to(backup.resolve()):
            raise ValueError("Backup must be external to source root")
        backup.mkdir(parents=True, exist_ok=False)
        # Save every original input-site source before any mutation.
        for file in sources:
            destination = backup / file.relative_to(source_root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(file.read_bytes())
        for file, text in sources.items():
            file.write_text(text, encoding="utf-8")
    return {"status": "AUTHENTIC_LEGACY_MOUSE_BRIDGE_PLAN",
            "original_sha_verified": True,
            "matched": counts,
            "source_files_changed": len(sources),
            "applied": bool(apply),
            "original_source_published": False,
            "android_pointer_capture_device_verified": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-dll", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source-root", type=Path)
    group.add_argument("--project", type=Path)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        root = args.source_root if args.source_root is not None else args.project / "Assets"
        result = patch(root, args.original_dll, apply=args.apply,
                       project_assets=args.project is not None, backup=args.backup)
        code = 0
    except Exception:
        # Original path/type/exceptions and decompiled source must never leak to CI.
        result = {"status": "LEGACY_MOUSE_BRIDGE_UNRESOLVED",
                  "original_source_published": False}
        code = 2
    print("T4_LEGACY_MOUSE_BRIDGE " + json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
