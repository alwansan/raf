"""Join private same-process export pointers to original PPtrs and actual YAML.

No names or object IDs are emitted. This proves assignments, not shader programs.
"""
import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re

from scripts.w1_audit_export_material_shaders import HEADER, SHADER, GUID, ENGINE, pptr
from scripts.w1_probe_original_shader_links import resolve_pointer
from scripts.w1_stage_zip2_owners import fingerprint, PINS


def identity(row):
    if not isinstance(row, dict) or set(row) != {'owner', 'path_id'}:
        raise ValueError('Invalid trace source identity')
    if not isinstance(row['owner'], str) or type(row['path_id']) is not int:
        raise ValueError('Invalid trace identity values')
    return PurePosixPath(row['owner'].replace('\\', '/')).name, row['path_id']


def pointer(row):
    if not isinstance(row, dict) or set(row) != {'file_id', 'guid', 'type'}:
        raise ValueError('Invalid trace pointer')
    if type(row['file_id']) is not int or type(row['type']) is not int or not isinstance(row['guid'], str):
        raise ValueError('Invalid trace pointer types')
    if not re.fullmatch('[0-9a-fA-F]{32}', row['guid']) or not row['file_id']:
        raise ValueError('Null or malformed trace export pointer')
    return row['file_id'], row['guid'].lower(), str(row['type'])


def check(trace, original_edges, original_shaders, actual):
    if trace.get('schema_version') != 1 or not re.fullmatch('[0-9a-f]{32}', trace.get('export_instance', '')):
        raise ValueError('Missing same-instance export trace')
    seen = set()
    exports = {}
    selected_materials = set()
    selected_shaders = set()
    redirects = 0
    for row in trace['objects']:
        key = identity(row['source'])
        if key in seen:
            raise ValueError('Source object appears in multiple export collections')
        seen.add(key)
        target = pointer(row['export'])
        if row['class_id'] == 48:
            if key in original_shaders:
                selected_shaders.add(key)
            continue
        if row['class_id'] != 21:
            raise ValueError('Unexpected trace class')
        if key in original_edges:
            selected_materials.add(key)
            if row.get('shader_source') is None or identity(row['shader_source']) != original_edges[key]:
                raise ValueError('Original material Shader PPtr changed during processing')
        if target[1] in ENGINE and target[2] == '0' and row['exportable'] is False:
            redirects += 1
            continue
        shader = pointer(row['shader_export'])
        if target in exports:
            raise ValueError('Two distinct original materials share one export pointer')
        exports[target] = shader
    if selected_materials != set(original_edges) or selected_shaders != set(original_shaders):
        raise ValueError('Original Material or Shader omitted from trace')
    if not actual or actual != exports:
        raise ValueError('Actual YAML material pointers differ from same-instance export trace')
    return {'source_material_edges_verified': len(selected_materials),
            'source_shader_objects_traced': len(selected_shaders),
            'actual_material_documents_verified': len(actual),
            'predefined_material_redirects_observed': redirects,
            'original_exported_material_shader_assignments_verified': True,
            'predefined_material_runtime_equivalence_verified': False,
            'shader_program_equivalence_verified': False}


def source_graph(source):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    pins = {'Raft_Data/' + k: v for k, v in SHADER_OWNERS.items()}
    pins.update({k: v for k, v in PINS.items() if '/Resources/' in k})
    materials, shaders = {}, set()
    for relative, pin in pins.items():
        path = source / relative
        if path.is_symlink() or fingerprint(path) != pin:
            raise ValueError('Original source provider changed')
        owner = path.name
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name == 'Shader':
                shaders.add((owner, obj.path_id))
            elif obj.type.name == 'Material' and '/Resources/' not in relative:
                external = [x.path for x in obj.assets_file.externals]
                materials[owner, obj.path_id] = resolve_pointer(owner, external, obj.read_typetree()['m_Shader'])
    if any(target not in shaders for target in materials.values()):
        raise ValueError('Original material graph has unresolved source shaders')
    return materials, shaders


def actual_graph(project):
    assets = project / 'Assets'
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError('Missing/unsafe actual export')
    entries = sorted(assets.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise ValueError('Redirected export path')
    result = {}
    for path in entries:
        if not path.is_file() or path.suffix not in {'.mat', '.asset', '.unity', '.prefab'}:
            continue
        if path.stat().st_size > 256 * 1024**2:
            raise ValueError('Oversized actual YAML')
        with path.open('rb') as stream:
            if not stream.read(16).lstrip(b'\xef\xbb\xbf').startswith(b'%YAML'):
                continue
        text = path.read_text(encoding='utf-8-sig')
        headers = list(HEADER.finditer(text))
        for i, header in enumerate(headers):
            if header[1] != '21':
                continue
            meta = Path(str(path) + '.meta')
            guids = GUID.findall(meta.read_text(encoding='utf-8-sig'))
            if len(guids) != 1:
                raise ValueError('Missing or ambiguous containing asset GUID')
            file_id = int(re.search(r'&(-?\d+)', header[0])[1])
            body = text[header.end():headers[i + 1].start() if i + 1 < len(headers) else len(text)]
            refs = SHADER.findall(body)
            if len(refs) != 1 or len(re.findall(r'^  m_Shader:', body, re.M)) != 1:
                raise ValueError('Missing or ambiguous actual Shader field')
            shader = pptr(refs[0])
            if not shader[1]:
                shader = shader[0], guids[0].lower(), '3'
            key = file_id, guids[0].lower(), '3'
            if key in result:
                raise ValueError('Duplicate actual material export pointer')
            result[key] = shader
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--private-trace', type=Path, required=True)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.resolve().is_relative_to(a.project.resolve()):
        raise ValueError('Report must stay outside export')
    edges, shaders = source_graph(a.source)
    report = check(json.loads(a.private_trace.read_text()), edges, shaders, actual_graph(a.project))
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('RAFT_ORIGINAL_EXPORT_LINEAGE ' + json.dumps(report, sort_keys=True))
