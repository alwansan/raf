"""B05: original Material -> texture binding fidelity across ONE authenticated export.

Only same-owner internal original texture PPtrs can be matched to exact exported
texture objects using the same-instance export trace. External references never
become guessed matches. Reports contain aggregate counts, not game identifiers.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re

from scripts.b44_verify_material_colors import (
    ALL_HEADER, MATERIAL_HEADER, GUID, ENGINE, FONT_COLLECTION,
)

HEX32 = re.compile(r'[0-9a-fA-F]{32}\Z')
TEXTURE_TYPES = frozenset((28, 84, 89, 117, 187))


def _original_pointer(value):
    if not isinstance(value, dict) or set(value) != {'m_FileID', 'm_PathID'}:
        raise ValueError('Malformed original texture PPtr')
    file_id, path_id = value['m_FileID'], value['m_PathID']
    if type(file_id) is not int or type(path_id) is not int or file_id < 0 or path_id < 0:
        raise ValueError('Invalid original PPtr component')
    if not path_id and file_id:
        raise ValueError('Invalid original external pointer with no target')
    return file_id, path_id


def _export_pointer(value):
    if not isinstance(value, dict) or not {'fileID'} <= set(value) or set(value) - {'fileID', 'guid', 'type'}:
        raise ValueError('Malformed exported texture PPtr')
    fid = value['fileID']
    guid = value.get('guid', '0'*32)
    kind = value.get('type', 0)
    if type(fid) is not int or type(kind) is not int or fid < 0 or kind < 0 or not isinstance(guid, str) or not HEX32.fullmatch(guid):
        raise ValueError('Invalid exported texture PPtr component')
    if not fid and guid.lower() != '0'*32:
        raise ValueError('Ambiguous null exported texture PPtr')
    return fid, guid.lower(), kind



def _uv_transform(value):
    """Extract UV scale/offset; reject partial and nonfinite values."""
    names = {'m_Scale', 'm_Offset'} & set(value)
    if not names:
        return None
    if names != {'m_Scale', 'm_Offset'}:
        raise ValueError('Incomplete texture UV transform')
    values = []
    for key in ('m_Scale', 'm_Offset'):
        vec = value[key]
        if not isinstance(vec, dict) or set(vec) != {'x', 'y'}:
            raise ValueError('Malformed texture UV vector')
        for comp in ('x', 'y'):
            num = vec[comp]
            if type(num) not in (int, float) or not math.isfinite(num):
                raise ValueError('Nonfinite texture UV component')
            values.append(float(num))
    return tuple(values)


def _slot(value):
    """Support pointer-only synthetic fixtures but report missing UV evidence."""
    if not isinstance(value, tuple):
        raise ValueError('Invalid normalized Material texture slot')
    if len(value) == 2 and isinstance(value[0], tuple):
        return value
    if len(value) in (2, 3) and type(value[0]) is int:
        return value, None
    raise ValueError('Invalid original/export texture slot')


def normalize_texenvs(entries, *, exported=False):
    """Keep private property names only in-memory; reject duplicates and drift."""
    if not isinstance(entries, list):
        raise ValueError('Texture environment slots must be an array')
    slots = {}
    for entry in entries:
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            name, val = entry
        elif isinstance(entry, dict) and set(entry) == {'m_First', 'm_Second'}:
            name, val = entry['m_First'], entry['m_Second']
        elif exported and isinstance(entry, dict) and len(entry) == 1:
            name, val = next(iter(entry.items()))
        else:
            raise ValueError('Unsupported texture slot entry shape')
        if not isinstance(name, str) or not name or name in slots or not isinstance(val, dict) or 'm_Texture' not in val:
            raise ValueError('Malformed or duplicate Material texture slot')
        slots[name] = (_export_pointer(val['m_Texture']) if exported else _original_pointer(val['m_Texture']), _uv_transform(val))
    return slots


def original_texenvs(root: Path):
    """SHA/byte-authenticated original providers; use no speculative archive mapping."""
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    result = {}
    for name, expected in SHADER_OWNERS.items():
        path = root / 'Raft_Data' / name
        if path.is_symlink() or not path.is_file() or fingerprint(path) != expected:
            raise ValueError('Original Material owner size/SHA mismatch')
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name != 'Material':
                continue
            props = obj.read_typetree().get('m_SavedProperties')
            if not isinstance(props, dict) or 'm_TexEnvs' not in props:
                raise ValueError('Missing original Material TexEnvs')
            identity = (name, obj.path_id)
            if identity in result:
                raise ValueError('Duplicated original Material identity')
            result[identity] = normalize_texenvs(props['m_TexEnvs'])
    if not result:
        raise ValueError('No SHA-authenticated original Materials')
    return result


def exported_texenvs(project: Path):
    """Parse actual exported Material YAML documents, including embedded ones."""
    import yaml
    # Unity YAML may carry duplicate keys at any nesting level. PyYAML's
    # default safe_load silently keeps the last value, so a conflicting
    # texture/UV pointer could appear faithful to the original. Fail closed.
    class UniqueMappingSafeLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            mapping = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                try:
                    duplicate = key in mapping
                except TypeError:
                    raise ValueError('Unhashable exported Material YAML mapping key') from None
                if duplicate:
                    raise ValueError('Duplicate exported Material YAML mapping key')
                mapping[key] = self.construct_object(value_node, deep=deep)
            return mapping

    assets = project / 'Assets'
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError('Missing/redirected Unity Assets root')
    entries = sorted(assets.rglob('*'))
    if any(path.is_symlink() for path in entries):
        raise ValueError('Linked export path is unsafe')
    found = {}
    for path in entries:
        if not path.is_file() or path.suffix not in ('.mat', '.asset', '.unity', '.prefab'):
            continue
        if path.stat().st_size > 256*1024*1024:
            raise ValueError('Oversized Material YAML candidate')
        with path.open('rb') as stream:
            if not stream.read(16).lstrip(b'\xef\xbb\xbf').startswith(b'%YAML'):
                continue
        text = path.read_text(encoding='utf-8-sig')
        headers = list(ALL_HEADER.finditer(text))
        if not any(MATERIAL_HEADER.fullmatch(h.group(0)) for h in headers):
            continue
        meta = Path(str(path) + '.meta')
        if not meta.is_file() or meta.is_symlink():
            raise ValueError('Missing or linked Material metadata')
        guids = GUID.findall(meta.read_text(encoding='utf-8-sig'))
        if len(guids) != 1 or guids[0].lower() == '0'*32:
            raise ValueError('Invalid exported Material GUID')
        for i, header in enumerate(headers):
            match = MATERIAL_HEADER.fullmatch(header.group(0))
            if match is None:
                continue
            try:
                doc = yaml.load(text[header.end():headers[i+1].start() if i+1 < len(headers) else len(text)], Loader=UniqueMappingSafeLoader)
            except yaml.YAMLError:
                raise ValueError('Malformed private Material YAML') from None
            mat = doc.get('Material') if isinstance(doc, dict) else None
            saved = mat.get('m_SavedProperties') if isinstance(mat, dict) else None
            if not isinstance(saved, dict) or 'm_TexEnvs' not in saved:
                raise ValueError('Material texture data absent in export')
            ptr = (int(match.group(1)), guids[0].lower())
            if ptr in found:
                raise ValueError('Duplicated exported Material pointer')
            found[ptr] = normalize_texenvs(saved['m_TexEnvs'], exported=True)
    if not found:
        raise ValueError('No exported Material texture documents')
    return found


def _trace_source(row):
    src = row.get('source')
    if not isinstance(src, dict) or set(src) != {'owner', 'path_id'} or not isinstance(src['owner'], str) or type(src['path_id']) is not int or src['path_id'] <= 0:
        raise ValueError('Invalid original object trace')
    return Path(src['owner'].replace('\\', '/')).name, src['path_id']


def _trace_export(row):
    ptr = row.get('export')
    if not isinstance(ptr, dict) or set(ptr) != {'file_id', 'guid', 'type'}:
        raise ValueError('Invalid same-export object trace')
    return _export_pointer({'fileID':ptr['file_id'], 'guid':ptr['guid'], 'type':ptr['type']})


def compare(trace: dict, original: dict, exported: dict):
    if (trace.get('schema_version') != 1 or not isinstance(trace.get('export_instance'), str)
            or not HEX32.fullmatch(trace['export_instance']) or not isinstance(trace.get('objects'), list)):
        raise ValueError('Missing same-instance export trace')
    mapped_materials = {}
    mapped_textures = {}
    traced_sources = set()
    excluded_engine = excluded_font = 0
    for row in trace['objects']:
        if row.get('class_id') not in {21, *TEXTURE_TYPES}:
            continue
        src = _trace_source(row)
        if src in traced_sources:
            raise ValueError('Duplicated original object in trace')
        traced_sources.add(src)
        if row['class_id'] == 21:
            if src not in original:
                raise ValueError('Unverified traced original Material')
            dst = _trace_export(row)
            if dst[1] in ENGINE and dst[2] == 0 and row.get('exportable') is False:
                excluded_engine += 1
                continue
            if row.get('collection_type') == FONT_COLLECTION:
                excluded_font += 1
                continue
            if dst[2] not in (2, 3) or not dst[0]:
                raise ValueError('Unusable Material export pointer')
            if dst[:2] in mapped_materials:
                raise ValueError('Two original Materials map to same exported object')
            mapped_materials[dst[:2]] = src
        else:
            ptr = _trace_export(row)
            if src in mapped_textures or not ptr[0]:
                raise ValueError('Unusable duplicate Texture object trace')
            mapped_textures[src] = ptr
    covered = {s for s in traced_sources if s in original}
    if covered != set(original) or not mapped_materials or set(mapped_materials) != set(exported):
        raise ValueError('Original/export Material identities do not match same-instance trace')
    c = dict(materials_compared=0, source_texture_slots=0, slots_compared=0,
             missing_slots=0, extra_slots=0, null_to_bound=0, bound_to_null=0,
             exact_internal_targets_compared=0, wrong_internal_targets=0,
             unresolved_internal_targets=0, external_targets_not_proven=0,
             source_null_bindings=0, uv_transform_slots_compared=0,
             uv_transform_missing_or_unproven=0, uv_transform_value_mismatches=0)
    for dst, src in mapped_materials.items():
        before, after = original[src], exported[dst]
        c['materials_compared'] += 1
        c['source_texture_slots'] += len(before)
        c['missing_slots'] += len(before.keys() - after.keys())
        c['extra_slots'] += len(after.keys() - before.keys())
        for name in before.keys() & after.keys():
            c['slots_compared'] += 1
            original_pointer, src_uv = _slot(before[name])
            exported_pointer, dst_uv = _slot(after[name])
            src_file, src_path = original_pointer
            dst_file, _, _ = actual = exported_pointer
            if src_uv is None or dst_uv is None:
                c['uv_transform_missing_or_unproven'] += 1
            else:
                c['uv_transform_slots_compared'] += 1
                if any(not math.isclose(x, y, abs_tol=1e-6, rel_tol=1e-6) for x, y in zip(src_uv, dst_uv)):
                    c['uv_transform_value_mismatches'] += 1
            src_bound = src_path != 0
            dst_bound = dst_file != 0
            if not src_bound:
                c['source_null_bindings'] += 1
            if src_bound and not dst_bound:
                c['bound_to_null'] += 1
            elif dst_bound and not src_bound:
                c['null_to_bound'] += 1
            elif src_bound and dst_bound:
                if src_file > 0:
                    c['external_targets_not_proven'] += 1
                else:
                    expected = mapped_textures.get((src[0],src_path))
                    if expected is None:
                        c['unresolved_internal_targets'] += 1
                    else:
                        c['exact_internal_targets_compared'] += 1
                        c['wrong_internal_targets'] += expected != actual
    c['source_slots_faithful_with_resolved_scope'] = not any(c[k] for k in ('missing_slots','extra_slots','null_to_bound','bound_to_null','wrong_internal_targets','unresolved_internal_targets','uv_transform_value_mismatches'))
    c['all_uv_transforms_verified'] = (c['uv_transform_slots_compared'] == c['slots_compared'] and c['uv_transform_missing_or_unproven'] == 0 and c['missing_slots'] == 0 and c['extra_slots'] == 0 and c['uv_transform_value_mismatches'] == 0)
    c['all_texture_targets_proven'] = bool(c['exact_internal_targets_compared']) and c['external_targets_not_proven'] == 0 and c['source_slots_faithful_with_resolved_scope']
    c.update(schema_version=1,excluded_engine_materials=excluded_engine,excluded_font_materials=excluded_font,
             original_values_or_names_disclosed=False,unity_shader_or_android_pixels_proven=False)
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--original',required=True,type=Path,help='SHA-verified reconstructed ZIP2 root')
    ap.add_argument('--project',required=True,type=Path,help='same-instance Unity export')
    ap.add_argument('--trace',required=True,type=Path,help='private exporter trace from that same run')
    ap.add_argument('--out',required=True,type=Path,help='aggregate JSON outside exported assets')
    a=ap.parse_args(argv)
    if a.out.resolve().is_relative_to(a.project.resolve()):
        raise ValueError('Report must be outside export')
    result = compare(json.loads(a.trace.read_text(encoding='utf-8')),original_texenvs(a.original),exported_texenvs(a.project))
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('RAFT_B05_MATERIAL_TEXENV_FIDELITY '+json.dumps(result,sort_keys=True))
    if not result['source_slots_faithful_with_resolved_scope']:
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
