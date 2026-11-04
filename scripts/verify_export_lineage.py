"""Join private same-process export pointers to original PPtrs and actual YAML.

No names or object IDs are emitted. This proves assignments, not shader programs.
"""
import argparse
from collections import Counter
import json
import hashlib
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


def document_key(export_pointer):
    """Identity of an exported YAML document: anchor fileID and asset GUID.

    A document's reference type lives in the PPtrs that point at it, never in
    the document itself. Loose exported assets legitimately use Serialized (2)
    through YamlExporterBase (materials) or Meta (3) through binary exporters
    (shaders, fonts). Any other type is an engine/localization pointer and can
    never denote a loose exported material document.
    """
    file_id, guid, reference_type = export_pointer
    if reference_type not in ('2', '3'):
        raise ValueError('Unexpected exported material reference type')
    return file_id, guid


def check(trace, original_edges, original_shaders, actual, fonts=None, source_fonts=None):
    if trace.get('schema_version') != 1 or not re.fullmatch('[0-9a-f]{32}', trace.get('export_instance', '')):
        raise ValueError('Missing same-instance export trace')
    seen = set()
    exports = {}
    selected_materials = set()
    selected_shaders = set()
    shader_exports = {}
    custom_shader_pointers = set()
    material_shader_pointers = []
    redirects = 0
    implicit_fonts = 0
    actual_materials = {document_key(key): value for key, value in actual.items()}
    for row in trace['objects']:
        key = identity(row['source'])
        if key in seen:
            raise ValueError('Source object appears in multiple export collections')
        seen.add(key)
        target = pointer(row['export'])
        if row['class_id'] == 48:
            if key in original_shaders:
                selected_shaders.add(key)
            shader_exports[key] = target
            if target[1] not in ENGINE:
                if target in custom_shader_pointers:
                    raise ValueError('Distinct custom Shader objects collapsed into one export pointer')
                custom_shader_pointers.add(target)
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
        material_shader_pointers.append((identity(row['shader_source']), shader))
        if row.get('collection_type') == 'AssetRipper.Export.UnityProjects.Miscellaneous.FontAssetExportCollection':
            font = pointer(row['font_export'])
            font_source = identity(row['font_source'])
            sha = row['font_data_sha256']
            if (font != (12800000, target[1], '3') or target[0] != 2100000 or target[2] != '3' or
                    document_key(target) in actual_materials or not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{64}', sha) or
                    fonts is None or fonts.get(font) != sha or source_fonts is None or source_fonts.get(font_source) != sha):
                raise ValueError('Implicit font material lacks matching original font bytes and TrueType importer')
            implicit_fonts += 1
            continue
        material = document_key(target)
        if material in exports:
            raise ValueError('Two distinct original materials share one export pointer')
        exports[material] = shader
    if selected_materials != set(original_edges) or selected_shaders != set(original_shaders):
        raise ValueError('Original Material or Shader omitted from trace')
    if any(shader_exports.get(key) != target for key, target in material_shader_pointers):
        raise ValueError('Material export pointer does not target its traced source Shader')
    if not actual_materials or actual_materials != exports:
        print('RAFT_LINEAGE_MISMATCH ' + json.dumps({
            'traced_yaml_materials': len(exports), 'actual_yaml_materials': len(actual_materials),
            'missing_actual': len(exports.keys() - actual_materials.keys()),
            'unexpected_actual': len(actual_materials.keys() - exports.keys()),
            'different_shader_pointers': sum(exports[k] != actual_materials[k] for k in exports.keys() & actual_materials.keys()),
            'implicit_font_materials': implicit_fonts, 'engine_material_redirects': redirects}, sort_keys=True))
        raise ValueError('Actual YAML material pointers differ from same-instance export trace')
    return {'source_material_edges_verified': len(selected_materials),
            'source_shader_objects_traced': len(selected_shaders),
            'actual_material_documents_verified': len(actual),
            'predefined_material_redirects_observed': redirects,
            'original_font_importer_materials_verified': implicit_fonts,
            'font_importer_runtime_shader_assignment_verified': False,
            'original_exported_material_shader_assignments_verified': True,
            'predefined_material_runtime_equivalence_verified': False,
            'shader_program_equivalence_verified': False}


def source_graph(source, include_fonts=False):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    pins = {'Raft_Data/' + k: v for k, v in SHADER_OWNERS.items()}
    pins.update({k: v for k, v in PINS.items() if '/Resources/' in k})
    materials, shaders, fonts = {}, set(), {}
    for relative, pin in pins.items():
        path = source / relative
        if path.is_symlink() or fingerprint(path) != pin:
            raise ValueError('Original source provider changed')
        owner = path.name
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name == 'Shader':
                shaders.add((owner, obj.path_id))
            elif obj.type.name == 'Font':
                fonts[owner, obj.path_id] = hashlib.sha256(bytes(obj.read_typetree()['m_FontData'])).hexdigest()
            elif obj.type.name == 'Material' and '/Resources/' not in relative:
                external = [x.path for x in obj.assets_file.externals]
                materials[owner, obj.path_id] = resolve_pointer(owner, external, obj.read_typetree()['m_Shader'])
    if any(target not in shaders for target in materials.values()):
        raise ValueError('Original material graph has unresolved source shaders')
    return (materials, shaders, fonts) if include_fonts else (materials, shaders)


def font_importers(project):
    result = {}
    assets = project / 'Assets'
    for path in assets.rglob('*'):
        if path.suffix.lower() not in {'.ttf', '.otf'} or not path.is_file():
            continue
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError('Redirected font importer')
        meta = Path(str(path) + '.meta')
        if meta.is_symlink():
            raise ValueError('Redirected font metadata')
        text = meta.read_text(encoding='utf-8-sig')
        guids = GUID.findall(text)
        if len(guids) != 1 or len(re.findall(r'^TrueTypeFontImporter:\s*$', text, re.M)) != 1:
            raise ValueError('Original font lacks unique TrueType importer metadata')
        key = 12800000, guids[0].lower(), '3'
        if key in result:
            raise ValueError('Duplicate font importer GUID')
        raw = path.read_bytes()
        if raw[:4] not in (b'\x00\x01\x00\x00', b'OTTO', b'true', b'ttcf'):
            raise ValueError('Invalid original font container')
        result[key] = hashlib.sha256(raw).hexdigest()
    return result


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
    edges, shaders, fonts = source_graph(a.source, include_fonts=True)
    report = check(json.loads(a.private_trace.read_text()), edges, shaders, actual_graph(a.project), font_importers(a.project), fonts)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('RAFT_ORIGINAL_EXPORT_LINEAGE ' + json.dumps(report, sort_keys=True))
