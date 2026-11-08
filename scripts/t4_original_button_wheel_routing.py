#!/usr/bin/env python3
"""T4 original Raft input API call-site census (aggregate only, no raw source)."""
import argparse
import hashlib
import json
import re
from pathlib import Path

SIZE = 3211776
SHA = "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e"
TOKENS = re.compile(r'@"(?:[^"]|"")*"|"(?:\\.|[^"\\])*"|'
                    r"'(?:\\.|[^'\\])*'|/\*[\s\S]*?\*/|//[^\n]*")
BUTTONS = re.compile(r'\b(?P<api>MyInput|Input)\s*\.\s*'
                     r'GetMouseButton(?P<action>Down|Up)?\s*\(\s*(?P<arg>[^()]*)\)')
WHEEL = re.compile(r'\b(?P<api>MyInput|Input)\s*\.\s*GetAxis(?:Raw)?\s*'
                   r'\(\s*"Mouse ScrollWheel"\s*\)')
NEW_BUTTON = re.compile(r'\bMouse\s*\.\s*current\s*\??\s*\.\s*'
                        r'(?:leftButton|rightButton|middleButton)\b')
NEW_WHEEL = re.compile(r'\bMouse\s*\.\s*current\s*\??\s*\.\s*scroll\b')
LEGACY_DELTA = re.compile(r'\bInput\s*\.\s*mouseScrollDelta\b')
KEYS = ("legacy_down", "legacy_up", "legacy_held", "myinput_down",
        "myinput_up", "myinput_held", "button_dynamic_argument",
        "legacy_wheel", "myinput_wheel", "legacy_scroll_delta",
        "inputsystem_buttons", "inputsystem_scroll")


def assert_original(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size != SIZE:
        raise ValueError("Original DLL not verified")
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA:
        raise ValueError("Original DLL hash differs")


def count_text(text):
    mask = TOKENS.sub(lambda m: "".join("\n" if ch == "\n" else " " for ch in m.group()), text)
    in_code = lambda m: bool(mask[m.start()].strip())
    counts = dict.fromkeys(KEYS, 0)
    for m in BUTTONS.finditer(text):
        if not in_code(m):
            continue
        prefix = "myinput" if m["api"] == "MyInput" else "legacy"
        counts[prefix + "_" + (m["action"] or "held").lower()] += 1
        if not re.fullmatch(r"[012]", m["arg"].strip()):
            counts["button_dynamic_argument"] += 1
    for m in WHEEL.finditer(text):
        if in_code(m):
            counts[("myinput" if m["api"] == "MyInput" else "legacy") + "_wheel"] += 1
    for pat, key in ((NEW_BUTTON, "inputsystem_buttons"),
                     (NEW_WHEEL, "inputsystem_scroll"),
                     (LEGACY_DELTA, "legacy_scroll_delta")):
        counts[key] += sum(1 for m in pat.finditer(text) if in_code(m))
    return counts


def census(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Private source root invalid")
    files = sorted(root.rglob("*.cs"))
    if not 1 <= len(files) <= 18000:
        raise ValueError("Private source population invalid")
    counts = dict.fromkeys(KEYS, 0)
    nbytes = 0
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise ValueError("Linked original source refused")
        nbytes += path.stat().st_size
        if path.stat().st_size > 2 * 1024 * 1024 or nbytes > 80 * 1024 * 1024:
            raise ValueError("Source scan budget exceeded")
        for k, v in count_text(path.read_text(encoding="utf-8-sig")).items():
            counts[k] += v
    return dict(status="ORIGINAL_MOUSE_BUTTON_WHEEL_LEXICAL_ONLY",
                original_sha_verified=True, source_files=len(files),
                counts=counts, device_verified=False, original_source_published=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original-dll", required=True, type=Path)
    p.add_argument("--source-root", required=True, type=Path)
    args = p.parse_args()
    try:
        assert_original(args.original_dll)
        report = census(args.source_root)
        code = 0
    except (OSError, UnicodeError, ValueError):
        report = dict(status="ORIGINAL_INPUT_UNRESOLVED",
                      device_verified=False, original_source_published=False)
        code = 2
    print("T4_ORIGINAL_MOUSE_INPUT " + json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
