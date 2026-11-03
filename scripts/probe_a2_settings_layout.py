"""Bounded source-only Settings/UI layout inventory for privately recovered Raft CSharp9.

Logs only original source basenames, source SHA256, syntactic category counts and
line numbers. It cannot prove a Settings-caused aspect regression or Unity behavior.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_android_display_paths import mask_csharp_noncode

# Existing independent managed-source pins; fail closed if changed or ambiguous.
PINS = {
    'Settings.cs': '904c52b337fe951f711e2efc15bfafc4fc77f2a8d2cc9c5bee2f7d14075103ad',
    'GraphicsSettingsBox.cs': 'e1854d74adbbe0565b586ec749f7de2cc73e3f97f59c388934a3faa0defc9300',
    'DynamicResolution.cs': '69f9ab873de44b167deb3d6d00182fd59b0147b27d8365fff64b2849069cedbc',
}
MAX_FILES = 12000
MAX_SOURCE_BYTES = 3 * 1024 * 1024
MAX_SCOPED = 256
MAX_REPORTED_SITES = 1600

# Lexical references, not control-flow or runtime mutations. Assignment patterns
# intentionally distinguish ==, => and comparison reads from a direct setter.
CATEGORIES = {
    'screen_width_read': re.compile(r'\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*width\b'),
    'screen_height_read': re.compile(r'\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*height\b'),
    'screen_safe_area_read': re.compile(r'\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*safeArea\b'),
    'screen_resolution_read': re.compile(r'\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*(?:currentResolution|resolutions)\b'),
    'screen_set_resolution': re.compile(r'\b(?:UnityEngine\s*\.\s*)?Screen\s*\.\s*SetResolution\s*\('),
    'scalable_buffer_resize': re.compile(r'\bScalableBufferManager\s*\.\s*ResizeBuffers\s*\('),
    'canvas_scaler_type': re.compile(r'\bCanvasScaler\b'),
    'rect_transform_type': re.compile(r'\bRectTransform\b'),
    'reference_resolution_write': re.compile(r'\.\s*referenceResolution\s*=(?!=|>)'),
    'width_or_height_match_write': re.compile(r'\.\s*matchWidthOrHeight\s*=(?!=|>)'),
    'ui_scale_mode_write': re.compile(r'\.\s*uiScaleMode\s*=(?!=|>)'),
    'screen_match_mode_write': re.compile(r'\.\s*screenMatchMode\s*=(?!=|>)'),
    'size_delta_write': re.compile(r'\.\s*sizeDelta\s*=(?!=|>)'),
    'anchor_write': re.compile(r'\.\s*anchor(?:Min|Max)\s*=(?!=|>)'),
    'local_scale_write': re.compile(r'\.\s*localScale\s*=(?!=|>)'),
    'set_size_with_anchors': re.compile(r'\.\s*SetSizeWithCurrentAnchors\s*\('),
    'camera_aspect_write': re.compile(r'\.\s*aspect\s*=(?!=|>)'),
    'camera_reset_aspect': re.compile(r'\.\s*ResetAspect\s*\('),
}


def relevant(name: str) -> bool:
    """Include the menu and all setting boxes without widening to gameplay."""
    return name in PINS or name.endswith('SettingsBox.cs')


def source_sites(text: str):
    masked = mask_csharp_noncode(text)
    sites = []
    for kind, pattern in CATEGORIES.items():
        for match in pattern.finditer(masked):
            sites.append({'category': kind, 'line': masked.count('\n', 0, match.start()) + 1})
    return sorted(sites, key=lambda s: (s['line'], s['category']))


def inspect(root: Path, require_pins=True):
    if not root.is_dir() or root.is_symlink():
        raise ValueError('Unsafe original source root')
    all_sources = sorted(root.rglob('*.cs'))
    if len(all_sources) > MAX_FILES:
        raise ValueError('Original inventory is unbounded')
    pinned = {name: [] for name in PINS}
    scope = []
    for path in all_sources:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SOURCE_BYTES:
            raise ValueError('Unsafe or oversized original source')
        if relevant(path.name):
            scope.append(path)
    if len(scope) > MAX_SCOPED:
        raise ValueError('Original Settings source scope exceeds bound')
    owners = []
    totals = Counter()
    total_sites = 0
    for path in scope:
        normalized = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        digest = hashlib.sha256(normalized.encode()).hexdigest()
        if path.name in pinned:
            pinned[path.name].append(digest)
        sites = source_sites(normalized)
        total_sites += len(sites)
        if total_sites > MAX_REPORTED_SITES:
            raise ValueError('Original Settings source signal count exceeds bound')
        totals.update(s['category'] for s in sites)
        if sites:
            owners.append({'basename': path.name, 'sha256': digest, 'sites': sites})
    if require_pins and any(pinned[name] != [sha] for name, sha in PINS.items()):
        raise ValueError('Authenticated original Settings source missing, duplicated, or changed')
    return {
        'source_files_examined': len(all_sources),
        'settings_files_examined': len(scope),
        'original_sources_pinned': bool(require_pins),
        'site_count': total_sites,
        'category_counts': dict(sorted(totals.items())),
        'owners': owners,
        'call_graph_proven': False,
        'settings_aspect_cause_proven': False,
        'native_or_device_tested': False,
        'source_modified': False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    args = p.parse_args()
    print('RAFT_A2_SETTINGS_LAYOUT_SOURCE ' + json.dumps(inspect(args.source), sort_keys=True))


if __name__ == '__main__':
    main()
