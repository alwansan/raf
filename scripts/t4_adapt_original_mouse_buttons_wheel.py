#!/usr/bin/env python3
"""T4: fail-closed original ZIP2 button/wheel call-site bridge (Android only).

By default the command only checks the immutable original DLL plus exact lexical
call cardinality. --apply requires a fresh, external backup directory and never
writes to the original DLL or repository asset metadata. The C# wrapper preserves
Unity native legacy values first; captured physical events supply missing values.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

from scripts.t4_original_mouse_routing import assert_original, LEXEMES

SHIM = "RaftAndroid.Platform.AndroidPhysicalMouseCapture"
BUTTON = re.compile(
    r"\b(?:UnityEngine\s*\.\s*)?Input\s*\.\s*"
    r"(?P<method>GetMouseButton(?:Down|Up)?)\s*\(\s*(?P<arg>[^()]*)\)"
)
WHEEL = re.compile(
    r'\b(?:UnityEngine\s*\.\s*)?Input\s*\.\s*(?P<method>GetAxis(?:Raw)?)'
    r'\s*\(\s*"Mouse ScrollWheel"\s*\)'
)
DELTA = re.compile(r"\b(?:UnityEngine\s*\.\s*)?Input\s*\.\s*mouseScrollDelta\b")
EXPECTED = {"down": 4, "held": 6, "up": 2, "wheel_axis": 6, "scroll_delta": 2}
MAX_FILES, MAX_TOTAL, MAX_FILE = 18000, 80 * 1024 * 1024, 2 * 1024 * 1024


def mask_comments_and_literals(text):
    """Maintain exact offsets/newlines for source position provenance."""
    return LEXEMES.sub(
        lambda m: "".join("\n" if c == "\n" else " " for c in m.group())
        if m.group().startswith(("/*", "//", '"', "'", '@"'))
        else m.group(), text
    )


def replacement_plan(root, *, project_assets=False, capture_originals=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Original source root invalid")
    candidates = sorted(root.rglob("*.cs"))
    if not 1 <= len(candidates) <= MAX_FILES:
        raise ValueError("Unbounded original source population")
    count = {k: 0 for k in EXPECTED}
    replacements = {}
    total = 0
    for path in candidates:
        if path.is_symlink() or not path.is_file():
            raise ValueError("Original source contains linked or missing CSharp file")
        size = path.stat().st_size
        total += size
        if size > MAX_FILE or total > MAX_TOTAL:
            raise ValueError("Original source exceeds scan budget")
        if project_assets and "Assembly-CSharp" not in path.relative_to(root).parts:
            continue
        raw = path.read_bytes()
        original = raw.decode("utf-8-sig")
        mask = mask_comments_and_literals(original)
        if len(mask) != len(original):
            raise ValueError("Original CSharp lexer position corruption")
        # Search original (to retain string parameters), but accept only when
        # the start of the expression is definitely live CSharp code.
        patches = []
        for match in BUTTON.finditer(original):
            if not mask[match.start()].strip():
                continue
            method = match["method"]
            category = "down" if method.endswith("Down") else (
                "up" if method.endswith("Up") else "held")
            count[category] += 1
            patches.append((match.start(), match.end(),
                SHIM + "." + method + "(" + match["arg"] + ")"))
        for match in WHEEL.finditer(original):
            if not mask[match.start()].strip():
                continue
            count["wheel_axis"] += 1
            patches.append((match.start(), match.end(),
                SHIM + "." + match["method"] + '("Mouse ScrollWheel")'))
        for match in DELTA.finditer(original):
            if not mask[match.start()].strip():
                continue
            count["scroll_delta"] += 1
            patches.append((match.start(), match.end(),
                SHIM + ".GetMouseScrollDelta()"))
        if not patches:
            continue
        if path.stat().st_nlink != 1:
            raise ValueError("Hardlinked original cannot be modified")
        parent = path.parent
        while parent != root:
            if parent.is_symlink() or parent == parent.parent:
                raise ValueError("Source path redirected")
            parent = parent.parent
        patches.sort(key=lambda item: item[0])
        if any(a[1] > b[0] for a, b in zip(patches, patches[1:])):
            raise ValueError("Overlapping original input expressions")
        patched = original
        for start, end, value in reversed(patches):
            patched = patched[:start] + value + patched[end:]
        replacements[path] = patched
        if capture_originals is not None:
            capture_originals[path] = raw
    if count != EXPECTED or not replacements:
        raise ValueError("Original mouse button/wheel cardinality drift")
    return replacements, count


def patch(source_root, original_dll, *, apply=False, project_assets=False, backup=None):
    assert_original(original_dll)
    originals_at_plan = {} if apply else None
    changes, count = replacement_plan(source_root,
        project_assets=project_assets, capture_originals=originals_at_plan)
    if apply:
        if backup is None or backup.exists() or backup.is_symlink() or any(
                x.is_symlink() for x in backup.parents):
            raise ValueError("Fresh nonlinked backup directory required")
        if (backup.resolve().is_relative_to(source_root.resolve()) or
                source_root.resolve().is_relative_to(backup.resolve())):
            raise ValueError("Private original backup must be outside source tree")
        originals = {p: p.read_bytes() for p in changes}
        if any(originals[p] != originals_at_plan[p] for p in changes):
            raise ValueError("Original changed after validated source plan")
        patched = {
            p: (b"\xef\xbb\xbf" if b.startswith(b"\xef\xbb\xbf") else b"")
            + changes[p].encode("utf-8")
            for p, b in originals.items()
        }
        backup.mkdir(parents=True, exist_ok=False)
        mutation_started = False
        try:
            for p, b in originals.items():
                dest = backup / p.relative_to(source_root)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(b)
                if dest.read_bytes() != b or p.read_bytes() != b:
                    raise ValueError("Backup/validated source not byte-identical")
            mutation_started = True
            for p, b in patched.items():
                if p.read_bytes() != originals[p] or p.stat().st_nlink != 1:
                    raise ValueError("Source mutated before verified install")
                p.write_bytes(b)
                if p.read_bytes() != b:
                    raise ValueError("Patched content readback mismatch")
        except BaseException as err:
            if mutation_started:
                for p, b in originals.items():
                    p.write_bytes(b)
                if any(p.read_bytes() != b for p, b in originals.items()):
                    raise ValueError("Rollback failed; original backups retained") from err
            shutil.rmtree(backup)
            raise
    return {
        "status": "AUTHENTIC_ORIGINAL_BUTTON_WHEEL_CAPTURED_FALLBACK_PATCH",
        "original_sha_verified": True,
        "matched": count,
        "modified_files": len(changes),
        "applied": bool(apply),
        "outside_android_legacy_input_preserved": True,
        "device_verified": False,
        "source_published": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original-dll", type=Path, required=True)
    sources = p.add_mutually_exclusive_group(required=True)
    sources.add_argument("--source-root", type=Path)
    sources.add_argument("--project", type=Path)
    p.add_argument("--backup", type=Path)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    try:
        root = args.source_root if args.source_root is not None else args.project / "Assets"
        result = patch(root, args.original_dll, apply=args.apply,
            project_assets=args.project is not None, backup=args.backup)
        code = 0
    except Exception:
        result = {"status": "ORIGINAL_BUTTON_WHEEL_INPUT_UNRESOLVED",
                  "source_published": False, "device_verified": False}
        code = 2
    print("T4_LEGACY_BUTTON_WHEEL " + json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
