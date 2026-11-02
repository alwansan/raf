"""Read-only bounded audit of display-mode writes in privately decompiled Raft C#.

Only file basenames, SHA256, call categories and line numbers leave CI.
No game source excerpts, strings or method bodies are printed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

MAX_FILES = 12000
MAX_FILE_BYTES = 3 * 1024 * 1024
MAX_SITES = 300

PATTERNS = {
    "screen_set_resolution": re.compile(r"\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*SetResolution\s*\("),
    "screen_fullscreen_assignment": re.compile(r"\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*fullScreen\s*(?<![=!<>])=(?!=)"),
    "screen_fullscreen_mode_assignment": re.compile(r"\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*fullScreenMode\s*(?<![=!<>])=(?!=)"),
    "screen_orientation_assignment": re.compile(r"\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*orientation\s*(?<![=!<>])=(?!=)"),
    "display_set_rendering_resolution": re.compile(r"\bDisplay\s*\.\s*main\s*\.\s*SetRenderingResolution\s*\("),
    "scalable_buffer_resize": re.compile(r"\bScalableBufferManager\s*\.\s*ResizeBuffers\s*\("),
}


def mask_csharp_noncode(source: str) -> str:
    """Mask comments and string/char literals while preserving line offsets."""
    chars = list(source)
    i = 0
    while i < len(chars):
        c = chars[i]
        if c == '/' and i + 1 < len(chars) and chars[i + 1] in ('/', '*'):
            block = chars[i + 1] == '*'
            start = i
            i += 2
            while i < len(chars):
                if not block and chars[i] == '\n':
                    break
                if block and chars[i] == '*' and i + 1 < len(chars) and chars[i + 1] == '/':
                    i += 2
                    break
                i += 1
            for k in range(start, i):
                if chars[k] != '\n':
                    chars[k] = ' '
            continue
        prefix = 0
        verbatim = False
        if c in ('"', "'"):
            quote = c
        elif c == '@' and i + 1 < len(chars) and chars[i + 1] == '"':
            quote, prefix, verbatim = '"', 1, True
        elif c == '$' and i + 1 < len(chars) and chars[i + 1] == '"':
            quote, prefix = '"', 1
        elif c in ('$', '@') and i + 2 < len(chars) and chars[i + 1] in ('$', '@') and chars[i + 2] == '"':
            quote, prefix, verbatim = '"', 2, '@' in chars[i:i + 2]
        else:
            i += 1
            continue
        start = i
        i += prefix + 1
        while i < len(chars):
            if not verbatim and chars[i] == '\\':
                i += 2
                continue
            if chars[i] == quote:
                if verbatim and i + 1 < len(chars) and chars[i + 1] == '"':
                    i += 2
                    continue
                i += 1
                break
            i += 1
        for k in range(start, min(i, len(chars))):
            if chars[k] != '\n':
                chars[k] = ' '
    return ''.join(chars)


def inspect_source(source: str):
    code = mask_csharp_noncode(source)
    sites = []
    for category, pattern in PATTERNS.items():
        for match in pattern.finditer(code):
            sites.append({"category": category,
                          "line": code.count('\n', 0, match.start()) + 1})
    return sorted(sites, key=lambda site: (site['line'], site['category']))


def probe(root: Path):
    if not root.is_dir() or root.is_symlink():
        raise ValueError('Original CSharp source root unavailable or unsafe')
    files = sorted(root.rglob('*.cs'))
    if len(files) > MAX_FILES:
        raise ValueError('Original CSharp source inventory exceeds bound')
    reports = []
    totals = Counter()
    for file in files:
        if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_FILE_BYTES:
            raise ValueError('Unsafe or unexpectedly large original CSharp source')
        raw = file.read_bytes()
        source = raw.decode('utf-8-sig').replace('\r\n', '\n')
        sites = inspect_source(source)
        if not sites:
            continue
        if len(sites) > MAX_SITES or sum(totals.values()) + len(sites) > MAX_SITES:
            raise ValueError('Original display mutation inventory exceeds bound')
        for site in sites:
            totals[site['category']] += 1
        reports.append({"source_basename": file.name,
                        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                        "sites": sites})
    return {"source_files_examined": len(files),
            "mutation_sites": sum(totals.values()),
            "mutation_categories": dict(sorted(totals.items())),
            "sources_with_mutations": reports,
            "graphics_settings_only_assumption_verified": (
                len(reports) == 1 and reports[0]['source_basename'] == 'GraphicsSettingsBox.cs'),
            "source_modified": False, "unity_or_device_tested": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    print('RAFT_ORIGINAL_ANDROID_DISPLAY_MUTATIONS ' + json.dumps(probe(args.source), sort_keys=True))


if __name__ == '__main__':
    main()
