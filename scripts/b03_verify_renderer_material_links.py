#!/usr/bin/env python3
"""B03 read-only exported Renderer.m_Materials -> Material object identity guard.

This inspects serialized Unity YAML, not the original game or compiled shader.
Null and built-in slots are reported as unknown, never silently considered fixed.
Only aggregate counts escape the private/export workspace.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re

DOC = re.compile(r'^--- !u!(\d+) &(-?\d+)(?: stripped)?[ \t]*$', re.M)
GUID = re.compile(r'^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*$', re.M)
FIELD = re.compile(r'^  m_Materials:[ \t]*(.*)$', re.M)
POINTER = re.compile(r'^\{([^{}\r\n]*)\}$')
RENDERERS = {'23': 'MeshRenderer', '137': 'SkinnedMeshRenderer',
             '199': 'ParticleSystemRenderer', '96': 'TrailRenderer',
             '120': 'LineRenderer', '212': 'SpriteRenderer'}
BUILTIN = {'0000000000000000e000000000000000', '0000000000000000f000000000000000'}
ZERO = '0' * 32
YAML_EXT = {'.mat', '.unity', '.prefab', '.asset'}
MAX_YAML = 128 * 1024 * 1024


class LinkError(ValueError):
    """Invalid export, or an unresolved renderer->material edge."""


def source_guids(meta: Path) -> str:
    if meta.is_symlink() or not meta.is_file() or meta.stat().st_size > 65536:
        raise LinkError('missing_or_invalid_meta')
    names = GUID.findall(meta.read_text(encoding='utf-8-sig'))
    if len(names) != 1 or names[0].lower() == ZERO:
        raise LinkError('missing_or_ambiguous_meta_guid')
    return names[0].lower()


def documents(raw: str):
    headers = list(DOC.finditer(raw))
    seen = set()
    for i, header in enumerate(headers):
        kind, object_id = header.group(1), int(header.group(2))
        if object_id in seen or object_id == 0:
            raise LinkError('duplicate_or_null_yaml_anchor')
        seen.add(object_id)
        end = headers[i + 1].start() if i + 1 < len(headers) else len(raw)
        yield kind, object_id, raw[header.end():end]


def parse_pointer(raw: str):
    match = POINTER.fullmatch(raw.strip())
    if not match:
        raise LinkError('malformed_material_pointer')
    values = {}
    for part in match.group(1).split(','):
        kv = part.strip().split(':', 1)
        if len(kv) != 2 or kv[0] in values:
            raise LinkError('malformed_material_pointer')
        values[kv[0]] = kv[1].strip()
    if 'fileID' not in values or set(values) - {'fileID', 'guid', 'type'}:
        raise LinkError('malformed_material_pointer')
    if not re.fullmatch(r'-?\d+', values['fileID']):
        raise LinkError('malformed_material_file_id')
    fid = int(values['fileID'])
    guid = values.get('guid', '').lower()
    if guid and not re.fullmatch(r'[0-9a-f]{32}', guid):
        raise LinkError('malformed_material_guid')
    kind = values.get('type')
    if kind is not None and not re.fullmatch(r'\d+', kind):
        raise LinkError('malformed_material_pointer_type')
    return fid, guid, kind


def renderer_slots(kind: str, body: str):
    if kind not in RENDERERS:
        return None
    nonblank = [line for line in body.splitlines() if line.strip()]
    if not nonblank or nonblank[0].strip() != RENDERERS[kind] + ':':
        raise LinkError('renderer_type_name_mismatch')
    hits = list(FIELD.finditer(body))
    if len(hits) != 1:
        raise LinkError('missing_or_duplicate_renderer_materials')
    found = hits[0]
    if found.group(1) == '[]':
        return []
    if found.group(1):
        raise LinkError('unsupported_materials_field_form')
    slots = []
    rest = body[found.end():].splitlines()
    for line in rest:
        if line.startswith('  - '):
            slots.append(parse_pointer(line[4:]))
        elif line.strip():
            break
    return slots


def audit(project: Path) -> dict:
    project = Path(os.path.abspath(project))
    if any(p.is_symlink() for p in (project, *project.parents)):
        raise LinkError('symlinked_project_ancestor')
    assets = project / 'Assets'
    if not assets.is_dir() or assets.is_symlink():
        raise LinkError('missing_assets_root')
    entries = sorted(assets.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise LinkError('symlink_export_entry')
    parsed = []
    seen_guids = set()
    for file in entries:
        if not file.is_file() or file.suffix not in YAML_EXT:
            continue
        if file.stat().st_size > MAX_YAML:
            raise LinkError('oversized_export_yaml')
        with file.open('rb') as stream:
            header = stream.read(8).lstrip(b'\xef\xbb\xbf')
        if not header.startswith(b'%YAML'):
            if file.suffix == '.mat':
                raise LinkError('non_yaml_material_file')
            continue
        meta_guid = source_guids(Path(str(file) + '.meta'))
        if meta_guid in seen_guids:
            raise LinkError('duplicate_yaml_asset_guid')
        seen_guids.add(meta_guid)
        body = file.read_text(encoding='utf-8-sig')
        parsed.append((meta_guid, list(documents(body))))
    materials = set()
    for owner, docs in parsed:
        for kind, object_id, body in docs:
            if kind == '21':
                if not body.lstrip().startswith('Material:\n'):
                    raise LinkError('material_type_name_mismatch')
                key = (owner, object_id)
                if key in materials:
                    raise LinkError('duplicate_material_object')
                materials.add(key)
    counts = Counter()
    for owner, docs in parsed:
        for kind, _, body in docs:
            slots = renderer_slots(kind, body)
            if slots is None:
                continue
            counts['renderer_objects'] += 1
            counts['material_slots'] += len(slots)
            if not slots:
                counts['empty_material_arrays'] += 1
            for fid, guid, ptr_kind in slots:
                if fid == 0:
                    counts['null_slots_unverified'] += 1
                    continue
                if guid in BUILTIN or (guid == ZERO and ptr_kind == '0'):
                    counts['builtin_slots_unverified'] += 1
                    continue
                if ptr_kind is not None and ptr_kind not in {'2', '3'}:
                    counts['unexpected_pointer_type'] += 1
                    continue
                target = (guid or owner, fid)
                if target in materials:
                    counts['verified_local_material_references'] += 1
                else:
                    counts['unresolved_material_references'] += 1
    if not materials:
        raise LinkError('no_exported_material_objects')
    if not counts['renderer_objects']:
        raise LinkError('no_exported_renderers')
    errors = {key: counts[key] for key in ('unresolved_material_references', 'unexpected_pointer_type') if counts[key]}
    return {
        'schema_version': 1,
        'renderer_classes_checked': len(RENDERERS),
        'exported_material_objects': len(materials),
        'counts': dict(sorted(counts.items())),
        'errors': errors,
        'local_reference_structure_valid': not bool(errors),
        'all_material_slots_authenticated': bool(counts['material_slots']) and
            counts['verified_local_material_references'] == counts['material_slots'],
        'original_to_export_material_identity_verified': False,
        'shader_program_texture_color_equivalence_verified': False,
        'unity_or_android_pixels_verified': False,
        'changes_to_export': 0,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.resolve().is_relative_to(args.project.resolve()):
        raise LinkError('report_inside_export_refused')
    result = audit(args.project)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print('RAFT_B03_RENDERER_MATERIAL_REFERENCES ' + json.dumps(result, sort_keys=True))
    if not result['local_reference_structure_valid']:
        raise SystemExit('Exported renderer material PPtrs unresolved')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
