"""Bounded original shader/engine identity comparison; no export-gate waiver."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from scripts.w1_stage_zip2_owners import PINS, fingerprint


def shader_key(tree):
    parsed = tree['m_ParsedForm']
    name = tree['m_Name']
    if not isinstance(name, str) or not name or name != parsed['m_Name']:
        raise ValueError('Original shader names require explicit reconciliation')
    props = parsed['m_PropInfo']['m_Props']
    names = tuple(p['m_Name'] for p in props)
    if not all(isinstance(n, str) for n in names):
        raise ValueError('Malformed original shader property names')
    # AssetRipper PredefinedAssetCache.ShaderKey hashes property names in order.
    return name, names


def classify(game, canonical):
    counts = Counter()
    for key in game:
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
    canonical = defaultdict(list)
    owner_rows = []
    for relative in PINS:
        if '/Resources/' not in relative:
            continue
        env = UnityPy.load(str(source / relative))
        total = 0
        for obj in env.objects:
            if obj.type.name == 'Shader':
                canonical[shader_key(obj.read_typetree())].append((relative, obj.path_id))
                total += 1
        owner_rows.append({'canonical_shader_objects': total})
    game_keys = []
    shader_objects = {}
    materials = []
    for relative in PINS:
        if '/Resources/' in relative:
            continue
        env = UnityPy.load(str(source / relative))
        for obj in env.objects:
            if obj.type.name == 'Shader':
                key = shader_key(obj.read_typetree())
                game_keys.append(key)
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
        elif len(canonical.get(key, [])) == 1:
            refs['local_material_refs_to_unique_engine_candidates'] += 1
        else:
            refs['local_material_refs_to_other_shaders'] += 1
    return {'original_owner_count': len(PINS), 'verified_bytes': sum(x[0] for x in PINS.values()),
            'engine_owners': owner_rows, **classify(game_keys, canonical), **refs,
            'matching_rule': 'exact_original_name_and_ordered_property_names',
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
