"""Private original-CSharp reference audit for Android Settings/display suspicion.

This is lexical evidence, NOT a full call graph or runtime aspect proof.
Logs source file basenames, SHA hashes, line numbers, counts and booleans only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from scripts.probe_original_android_display_paths import mask_csharp_noncode

PINS = {
    'DynamicResolution.cs': '69f9ab873de44b167deb3d6d00182fd59b0147b27d8365fff64b2849069cedbc',
    'GraphicsSettingsBox.cs': 'e1854d74adbbe0565b586ec749f7de2cc73e3f97f59c388934a3faa0defc9300',
}
MAX_FILES = 12000
MAX_SIZE = 3 * 1024 * 1024
# Explicit class/member use only: an alias or reflection is NOT ruled out.
SITES = {
    'dynamic_resolution_class_reference': re.compile(r'\bDynamicResolution\b'),
    'qualified_horizontal_scale_write': re.compile(r'\bDynamicResolution\s*\.\s*m_widthScale\s*(?:\+\+|--|(?:[+*/%-]|<<|>>|&|\||\^)?=(?!=))'),
    'qualified_vertical_scale_write': re.compile(r'\bDynamicResolution\s*\.\s*m_heightScale\s*(?:\+\+|--|(?:[+*/%-]|<<|>>|&|\||\^)?=(?!=))'),
    'apply_settings_resolution_reference': re.compile(r'\bApplyCurrentResolutionAndFullscreenMode\s*\('),
    'dynamic_resize_call': re.compile(r'\bScalableBufferManager\s*\.\s*ResizeBuffers\s*\('),
}


def inspect(root, require_pins=True):
    if not root.is_dir() or root.is_symlink():
        raise ValueError('Missing or unsafe original source root')
    files = sorted(root.rglob('*.cs'))
    if len(files) > MAX_FILES:
        raise ValueError('Unbounded original source inventory')
    observed = {name: [] for name in PINS}
    references = []
    counts = {name: 0 for name in SITES}
    for path in files:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SIZE:
            raise ValueError('Unsafe original source file')
        source = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        sha = hashlib.sha256(source.encode()).hexdigest()
        if path.name in observed:
            observed[path.name].append(sha)
        code = mask_csharp_noncode(source)
        items = []
        for category, expression in SITES.items():
            for match in expression.finditer(code):
                items.append({'kind': category, 'line': code.count('\n', 0, match.start()) + 1})
                counts[category] += 1
        if items:
            references.append({'basename': path.name, 'sha256': sha,
                               'sites': sorted(items, key=lambda x: (x['line'], x['kind']))})
    if require_pins and any(observed[name] != [expected] for name, expected in PINS.items()):
        raise ValueError('Original Settings/DynamicResolution source SHA mismatch or duplicate')
    settings = [row for row in references if row['basename'] == 'GraphicsSettingsBox.cs']
    setting_direct_dynamic_reference = any(site['kind'] == 'dynamic_resolution_class_reference'
                                           for row in settings for site in row['sites'])
    external_scale_sites = [site for row in references if row['basename'] != 'DynamicResolution.cs'
                            for site in row['sites'] if site['kind'].startswith('qualified_')]
    return {
        'files_examined': len(files), 'pinned_sources_verified': bool(require_pins),
        'reference_counts': counts, 'reference_owners': references,
        'settings_has_explicit_dynamic_resolution_reference': setting_direct_dynamic_reference,
        'external_qualified_scale_writes': len(external_scale_sites),
        'full_call_graph_proven': False, 'indirect_alias_reflection_writes_excluded': False,
        'settings_aspect_cause_proven': False, 'source_modified': False, 'gpu_or_device_tested': False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    args = p.parse_args()
    print('RAFT_ORIGINAL_SETTINGS_DYNAMIC_REFERENCE_AUDIT ' + json.dumps(inspect(args.source), sort_keys=True))


if __name__ == '__main__':
    main()
