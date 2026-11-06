#!/usr/bin/env python3
"""Read-only fail-closed structural link gate; original provenance is NOT established here."""
import argparse
import json
import re
from pathlib import Path

HEX = re.compile(r'[0-9a-f]{32}\Z')
META = re.compile(r'(?m)^guid:\s*([0-9a-f]{32})\s*$')
PPTR = re.compile(r'(?m)^\s*m_Shader:\s*\{\s*fileID:\s*4800000\s*,\s*guid:\s*([0-9a-f]{32})\s*,\s*type:\s*3\s*\}\s*(?:\#.*)?

def check(root, manifest):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('invalid_root')
    if set(manifest) != {'source_sha256', 'source_shader_id', 'export_shader_guid', 'shader_path', 'material_paths'}:
        raise ValueError('manifest_schema')
    if not isinstance(manifest['source_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', manifest['source_sha256']):
        raise ValueError('unverified_source_pin')
    if not isinstance(manifest['source_shader_id'], int) or isinstance(manifest['source_shader_id'], bool) or manifest['source_shader_id'] < 0:
        raise ValueError('invalid_source_shader_id')
    guid = manifest['export_shader_guid']
    if not isinstance(guid, str) or not HEX.fullmatch(guid):
        raise ValueError('invalid_export_guid')
    def safe(rel):
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
            raise ValueError('unsafe_relative_path')
        p = root / rel
        if any(x.is_symlink() for x in (p, *p.parents)):
            raise ValueError('symlink_input')
        if not p.is_file() or not p.resolve().is_relative_to(root):
            raise ValueError('missing_or_escaped_input')
        if p.stat().st_size > 8 * 1024 * 1024:
            raise ValueError('oversized_input')
        return p
    shader = safe(manifest['shader_path'])
    if shader.suffix != '.shader':
        raise ValueError('not_shader')
    meta = safe(manifest['shader_path'] + '.meta')
    matches = META.findall(meta.read_text(encoding='utf-8-sig'))
    if matches != [guid]:
        raise ValueError('shader_guid_mismatch')
    shader_text = shader.read_text(encoding='utf-8-sig')
    if any(s in shader_text for s in ('DummyShaderTextExporter', 'No subprograms found', 'ShaderUnknownExporter')):
        raise ValueError('unresolved_exporter_placeholder')
    materials = manifest['material_paths']
    if not isinstance(materials, list) or not materials or not all(isinstance(x,str) for x in materials) or len(materials) != len(set(materials)):
        raise ValueError('invalid_material_scope')
    for rel in materials:
        mat = safe(rel)
        if mat.suffix != '.mat':
            raise ValueError('not_material')
        found = PPTR.findall(mat.read_text(encoding='utf-8-sig'))
        if found != [guid]:
            raise ValueError('material_shader_link_mismatch')
    return {'status': 'STRUCTURAL_LINK_ONLY', 'matched_materials': len(materials),
            'original_export_join_independently_verified': False,
            'shader_program_authenticity_verified': False, 'android_pixels_verified': False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--manifest', required=True)
    a = p.parse_args()
    print(json.dumps(check(a.root, json.loads(Path(a.manifest).read_text())), sort_keys=True))

if __name__ == '__main__':
    main()
)

def check(root, manifest):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('invalid_root')
    if set(manifest) != {'source_sha256', 'source_shader_id', 'export_shader_guid', 'shader_path', 'material_paths'}:
        raise ValueError('manifest_schema')
    if not isinstance(manifest['source_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', manifest['source_sha256']):
        raise ValueError('unverified_source_pin')
    if not isinstance(manifest['source_shader_id'], int) or isinstance(manifest['source_shader_id'], bool) or manifest['source_shader_id'] < 0:
        raise ValueError('invalid_source_shader_id')
    guid = manifest['export_shader_guid']
    if not isinstance(guid, str) or not HEX.fullmatch(guid):
        raise ValueError('invalid_export_guid')
    def safe(rel):
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
            raise ValueError('unsafe_relative_path')
        p = root / rel
        if any(x.is_symlink() for x in (p, *p.parents)):
            raise ValueError('symlink_input')
        if not p.is_file() or not p.resolve().is_relative_to(root):
            raise ValueError('missing_or_escaped_input')
        if p.stat().st_size > 8 * 1024 * 1024:
            raise ValueError('oversized_input')
        return p
    shader = safe(manifest['shader_path'])
    if shader.suffix != '.shader':
        raise ValueError('not_shader')
    meta = safe(manifest['shader_path'] + '.meta')
    matches = META.findall(meta.read_text(encoding='utf-8-sig'))
    if matches != [guid]:
        raise ValueError('shader_guid_mismatch')
    shader_text = shader.read_text(encoding='utf-8-sig')
    if any(s in shader_text for s in ('DummyShaderTextExporter', 'No subprograms found', 'ShaderUnknownExporter')):
        raise ValueError('unresolved_exporter_placeholder')
    materials = manifest['material_paths']
    if not isinstance(materials, list) or not materials or not all(isinstance(x,str) for x in materials) or len(materials) != len(set(materials)):
        raise ValueError('invalid_material_scope')
    for rel in materials:
        mat = safe(rel)
        if mat.suffix != '.mat':
            raise ValueError('not_material')
        found = PPTR.findall(mat.read_text(encoding='utf-8-sig'))
        if found != [guid]:
            raise ValueError('material_shader_link_mismatch')
    return {'status': 'STRUCTURAL_LINK_ONLY', 'matched_materials': len(materials),
            'original_export_join_independently_verified': False,
            'shader_program_authenticity_verified': False, 'android_pixels_verified': False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--manifest', required=True)
    a = p.parse_args()
    print(json.dumps(check(a.root, json.loads(Path(a.manifest).read_text())), sort_keys=True))

if __name__ == '__main__':
    main()
