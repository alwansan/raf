"""Bounded original shader/engine identity comparison; no export-gate waiver."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from scripts.w1_stage_zip2_owners import PINS, fingerprint


def shader_key(tree, name_source='asset'):
    parsed = tree['m_ParsedForm']
    if name_source not in ('asset', 'declaration'):
        raise ValueError('Unsupported original name dimension')
    name = tree['m_Name'] if name_source == 'asset' else parsed['m_Name']
    # Never guess how the exporter's generated IShader.Name property maps a
    # stripped raw m_Name. Report both original fields independently.
    if not isinstance(name, str):
        raise ValueError('Malformed original shader name')
    if not name:
        return None
    props = parsed['m_PropInfo']['m_Props']
    names = tuple(p['m_Name'] for p in props)
    if not all(isinstance(n, str) for n in names):
        raise ValueError('Malformed original shader property names')
    # AssetRipper PredefinedAssetCache.ShaderKey hashes property names in order.
    return name, names


def classify(game, canonical):
    counts = Counter()
    for key in game:
        if key is None:
            counts['game_shaders'] += 1
            counts['unavailable_original_name_keys'] += 1
            continue
        choices = canonical.get(key, [])
        counts['game_shaders'] += 1
        counts['unique_engine_identity_candidates' if len(choices) == 1 else
               'ambiguous_engine_identity_candidates' if choices else 'not_in_engine_owners'] += 1
    return dict(counts)


def probe(source):
    import UnityPy
    for relative, pin in PINS.items():
        if fingerprint(source / relative) != pin:
            raise ValueError('Original owner pin mismatch')
    canonical = {'asset': defaultdict(list), 'declaration': defaultdict(list)}
    owner_rows = []
    for relative in PINS:
        if '/Resources/' not in relative:
            continue
        env = UnityPy.load(str(source / relative))
        total = 0
        for obj in env.objects:
            if obj.type.name == 'Shader':
                tree = obj.read_typetree()
                for dimension in canonical:
                    key = shader_key(tree, dimension)
                    if key is not None:
                        canonical[dimension][key].append((relative, obj.path_id))
                total += 1
        owner_rows.append({'canonical_shader_objects': total})
    game_keys = {'asset': [], 'declaration': []}
    shader_objects = {}
    materials = []
    for relative in PINS:
        if '/Resources/' in relative:
            continue
        env = UnityPy.load(str(source / relative))
        for obj in env.objects:
            if obj.type.name == 'Shader':
                tree = obj.read_typetree()
                for dimension in game_keys:
                    game_keys[dimension].append(shader_key(tree, dimension))
                key = shader_key(tree, 'declaration')
                shader_objects[(relative, obj.path_id)] = key
            elif obj.type.name == 'Material':
                tree = obj.read_typetree()
                materials.append((relative, tree['m_Shader']))
    refs = Counter()
    for relative, pointer in materials:
        if pointer['m_FileID'] != 0:
            refs['external_material_shader_refs_not_resolved'] += 1
            continue
        key = shader_objects.get((relative, pointer['m_PathID']))
        if key is None:
            refs['unresolved_local_material_shader_refs'] += 1
        elif len(canonical['declaration'].get(key, [])) == 1:
            refs['local_material_refs_to_unique_declaration_candidates'] += 1
        else:
            refs['local_material_refs_to_other_shaders'] += 1
    return {'original_owner_count': len(PINS), 'verified_bytes': sum(x[0] for x in PINS.values()),
            'engine_owners': owner_rows, 'dimensions': {
                d: classify(game_keys[d], canonical[d]) for d in game_keys}, **refs,
            'matching_rule': 'independent_raw_asset_and_parsed_declaration_names_plus_ordered_properties',
            'generated_IShader_Name_mapping_verified': False,
            'embedded_exporter_engine_database_verified': False,
            'actual_exported_engine_material_refs_verified': False,
            'zero_loose_builtin_gate_may_be_skipped': False,
            'original_programs_or_names_published': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    result = probe(a.source)
    a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_ENGINE_REDIRECT_CANDIDATES ' + json.dumps(result, sort_keys=True))
