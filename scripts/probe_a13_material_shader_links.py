"""Read-only original Material to Shader PPtr audit (two SHA-pinned owners).

Never guess cross-file PPtr resolution. Do not disclose original asset names,
per-object IDs, raw materials, shader source, textures or proprietary content.
"""
import argparse
from collections import Counter, defaultdict
import gc
import json
from pathlib import Path

OWNERS = ('resources.assets', 'sharedassets0.assets')


def pointer_kind(pointer):
    if not isinstance(pointer, dict) or set(pointer) != {'m_FileID', 'm_PathID'}:
        raise ValueError('Original Material shader PPtr schema differs')
    file_id, path_id = pointer['m_FileID'], pointer['m_PathID']
    if (type(file_id) is not int or type(path_id) is not int or
            file_id < 0 or path_id < 0):
        raise ValueError('Invalid original Material shader pointer')
    if not path_id:
        if file_id:
            raise ValueError('Malformed external file with null PathID')
        return 'null'
    return 'internal' if file_id == 0 else 'external_unresolved'


def summarize(shaders, materials):
    """Only same-owner links resolve; a reused PathID in another file is not proof."""
    by_owner = defaultdict(set)
    counts = Counter()
    per_owner = defaultdict(Counter)
    for owner, path_id in shaders:
        if owner not in OWNERS or type(path_id) is not int or path_id <= 0:
            raise ValueError('Invalid original Shader object identity')
        if path_id in by_owner[owner]:
            raise ValueError('Duplicate original Shader PathID within owner')
        by_owner[owner].add(path_id)
        counts['original_shader_objects'] += 1
        per_owner[owner]['shader_objects'] += 1
    if not counts['original_shader_objects']:
        raise ValueError('No original Shader objects')
    material_ids = set()
    hit_counts = Counter()
    for owner, material_id, ptr in materials:
        if owner not in OWNERS or type(material_id) is not int or material_id <= 0:
            raise ValueError('Invalid original Material object identity')
        key = (owner, material_id)
        if key in material_ids:
            raise ValueError('Duplicate original Material PathID within owner')
        material_ids.add(key)
        kind = pointer_kind(ptr)
        counts['original_material_objects'] += 1
        per_owner[owner]['material_objects'] += 1
        counts['shader_reference_' + kind] += 1
        per_owner[owner][kind] += 1
        if kind == 'internal':
            if ptr['m_PathID'] not in by_owner[owner]:
                counts['internal_unresolved'] += 1
                per_owner[owner]['internal_unresolved'] += 1
            else:
                counts['internal_resolved'] += 1
                per_owner[owner]['internal_resolved'] += 1
                hit_counts[(owner, ptr['m_PathID'])] += 1
    if not counts['original_material_objects']:
        raise ValueError('No original Material objects')
    if counts['shader_reference_internal'] != counts['internal_unresolved'] + counts['internal_resolved']:
        raise AssertionError('Inconsistent internal reference coverage')
    if counts['original_material_objects'] != sum(
        counts['shader_reference_' + tag] for tag in ('null', 'external_unresolved', 'internal')
    ):
        raise AssertionError('Inconsistent total Material reference coverage')
    result = dict(sorted(counts.items()))
    result['referenced_distinct_local_shader_objects'] = len(hit_counts)
    result['max_materials_per_local_shader'] = max(hit_counts.values(), default=0)
    result['by_owner'] = {owner: dict(sorted(per_owner[owner].items())) for owner in OWNERS}
    result.update(external_refs_not_inferred=True, two_owner_scope_only=True,
                  failed_native_full_export_examined=False, source_modified=False,
                  gpu_or_android_verified=False)
    return result


def original_records(root):
    import UnityPy
    shaders, materials = [], []
    for owner in OWNERS:
        env = UnityPy.load(str(root / owner))
        for obj in env.file.objects.values():
            kind = obj.type.name
            if kind == 'Shader':
                shaders.append((owner, int(obj.path_id)))
            elif kind == 'Material':
                fields = obj.read_typetree()
                if 'm_Shader' not in fields:
                    raise ValueError('Original Material lacks m_Shader field')
                materials.append((owner, int(obj.path_id), fields['m_Shader']))
        del env
        gc.collect()
    return shaders, materials


def audit(root, out):
    from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
    manifest = {owner: EXPECTED[owner] for owner in OWNERS}
    verified = verify_sources(root, expected=manifest)
    shaders, materials = original_records(root)
    result = summarize(shaders, materials)
    if result['original_shader_objects'] != 105:
        raise ValueError('Original 2-owner Shader inventory count drift from authenticated W1')
    report = {'source_sha': __import__('os').environ.get('GITHUB_SHA'),
              'original_owners': verified['sources'],
              'original_shader_material_reference_evidence': result,
              'original_names_or_assets_disclosed': False,
              'vendor_identity_intersection_measured': False,
              'full_140_shader_export_scope_verified': False}
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print('RAFT_A13_ORIGINAL_MATERIAL_SHADER_PPTR ' + json.dumps(report, sort_keys=True))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    audit(args.source, args.out)


if __name__ == '__main__':
    main()
